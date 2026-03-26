#!/usr/bin/env python3
"""
Reverse-engineer indicator_id names using Qwen 235B API.

Two-round independent inference with cross-context consistency check.
"""

import argparse
import csv
import json
import os
import re
import sys
import time
from pathlib import Path

import yaml

from schemas import IndicatorInput, RoundResult, ReverseResult
from comparator import compare_rounds, compute_final_confidence

SCRIPT_DIR = Path(__file__).parent


# ---------------------------------------------------------------------------
# Data loading
# ---------------------------------------------------------------------------

def load_csv_metadata(csv_path: str) -> dict[str, dict]:
    """Load indicator metadata from CSV, skip comments and blank lines."""
    meta = {}
    with open(csv_path, "r", encoding="utf-8") as f:
        lines = [l for l in f if l.strip() and not l.strip().startswith("#")]
    reader = csv.DictReader(lines)
    for row in reader:
        code = row.get("indicator_id", "").strip()
        if code:
            meta[code] = {
                "indicator_name": row.get("indicator_name", "").strip(),
                "unit": row.get("unit", "").strip(),
                "adjustment": row.get("adjustment", "").strip(),
                "source": row.get("source", "").strip(),
                "data_type": row.get("data_type", "").strip(),
            }
    return meta


def load_supplemental(yaml_path: str) -> dict[str, dict]:
    """Load supplemental metadata from YAML."""
    with open(yaml_path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    return data.get("indicators", {})


def load_input_indicators(yaml_path: str) -> list[dict]:
    """Load input indicator list from YAML."""
    with open(yaml_path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    return data.get("indicators", [])


def enrich_indicator(
    raw: dict, csv_meta: dict, supplemental: dict
) -> IndicatorInput:
    """Build IndicatorInput by merging raw input with CSV / supplemental metadata."""
    code = raw["raw_indicator_code"]
    meaning = raw.get("current_meaning", "")
    remark = raw.get("remark", "")

    # Try CSV first, then supplemental
    meta = csv_meta.get(code, supplemental.get(code, {}))

    return IndicatorInput(
        raw_indicator_code=code,
        current_meaning=meaning,
        remark=remark,
        indicator_name=meta.get("indicator_name", meaning),
        unit=meta.get("unit", ""),
        adjustment=meta.get("adjustment", ""),
        source=meta.get("source", ""),
        data_type=meta.get("data_type", ""),
    )


# ---------------------------------------------------------------------------
# Prompt building
# ---------------------------------------------------------------------------

def load_prompt_template(filename: str) -> str:
    path = SCRIPT_DIR / filename
    return path.read_text(encoding="utf-8")


def build_user_message(ind: IndicatorInput) -> str:
    """Build user message for the model."""
    parts = [
        f"Raw indicator code: {ind.raw_indicator_code}",
        f"Chinese meaning: {ind.current_meaning}",
    ]
    if ind.indicator_name and ind.indicator_name != ind.current_meaning:
        parts.append(f"Indicator name: {ind.indicator_name}")
    if ind.unit:
        parts.append(f"Unit: {ind.unit}")
    if ind.adjustment:
        parts.append(f"Adjustment type: {ind.adjustment}")
    if ind.source:
        parts.append(f"Data source: {ind.source}")
    if ind.data_type:
        parts.append(f"Data category: {ind.data_type}")
    if ind.remark:
        parts.append(
            f"Note: This indicator is originally {ind.remark}. "
            "This is a frequency processing detail — do NOT encode it in the indicator_id."
        )
    return "\n".join(parts)


# ---------------------------------------------------------------------------
# Response parsing
# ---------------------------------------------------------------------------

def parse_json_response(text: str) -> dict:
    """Robustly parse JSON from model response."""
    # Strip markdown code fences
    cleaned = re.sub(r"```(?:json)?\s*", "", text)
    cleaned = re.sub(r"```", "", cleaned)
    cleaned = cleaned.strip()

    # Try direct parse
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        pass

    # Try to find JSON object in text
    match = re.search(r"\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}", cleaned, re.DOTALL)
    if match:
        try:
            return json.loads(match.group())
        except json.JSONDecodeError:
            pass

    # Return empty dict with raw text preserved
    return {"_parse_error": True, "_raw_text": text}


def extract_round_result(parsed: dict, is_round1: bool = True) -> RoundResult:
    """Extract RoundResult from parsed JSON."""
    r = RoundResult()
    r.recommended_indicator_id = parsed.get("recommended_indicator_id", "")
    r.alternative_indicator_ids = parsed.get("alternative_indicator_ids", [])
    r.confidence = parsed.get("confidence", "")

    if is_round1:
        r.display_name_cn = parsed.get("display_name_cn", "")
        r.naming_rationale_short = parsed.get("naming_rationale_short", "")

    return r


# ---------------------------------------------------------------------------
# Main processing
# ---------------------------------------------------------------------------

def process_one_indicator(
    ind: IndicatorInput,
    client,  # QwenClient or None for dry-run
    dry_run: bool = False,
) -> ReverseResult:
    """Run two-round reverse engineering for a single indicator."""
    result = ReverseResult(
        raw_indicator_code=ind.raw_indicator_code,
        current_meaning=ind.current_meaning,
        indicator_name=ind.indicator_name,
        unit=ind.unit,
        adjustment=ind.adjustment,
        source=ind.source,
        data_type=ind.data_type,
        remark=ind.remark,
    )

    user_msg = build_user_message(ind)
    prompt_r1 = load_prompt_template("prompt_round1.txt")
    prompt_r2 = load_prompt_template("prompt_round2.txt")

    if dry_run:
        print(f"  [DRY-RUN] Round 1 system prompt: {len(prompt_r1)} chars")
        print(f"  [DRY-RUN] User message:\n{user_msg}")
        print(f"  [DRY-RUN] Round 2 system prompt: {len(prompt_r2)} chars")
        result.notes = "dry-run, no API call"
        return result

    # --- Round 1 ---
    print(f"  Round 1...")
    try:
        raw_r1 = client.chat(system_prompt=prompt_r1, user_message=user_msg)
        result.round1_raw_response = raw_r1
        parsed_r1 = parse_json_response(raw_r1)
        r1 = extract_round_result(parsed_r1, is_round1=True)
        result.round1_indicator_id = r1.recommended_indicator_id
        result.round1_alternatives = r1.alternative_indicator_ids
        result.round1_confidence = r1.confidence
    except Exception as e:
        result.round1_raw_response = str(e)
        result.notes = f"Round 1 failed: {e}"
        r1 = RoundResult()

    # --- Round 2 (independent context) ---
    print(f"  Round 2...")
    try:
        raw_r2 = client.chat(system_prompt=prompt_r2, user_message=user_msg)
        result.round2_raw_response = raw_r2
        parsed_r2 = parse_json_response(raw_r2)
        r2 = extract_round_result(parsed_r2, is_round1=False)
        result.round2_indicator_id = r2.recommended_indicator_id
        result.round2_alternatives = r2.alternative_indicator_ids
        result.round2_confidence = r2.confidence
    except Exception as e:
        result.round2_raw_response = str(e)
        if result.notes:
            result.notes += f"; Round 2 failed: {e}"
        else:
            result.notes = f"Round 2 failed: {e}"
        r2 = RoundResult()

    # --- Compare ---
    consistency, final_id, notes = compare_rounds(r1, r2)
    result.consistency = consistency
    result.final_indicator_id = final_id
    result.final_confidence = compute_final_confidence(r1, r2, consistency)
    if notes:
        result.notes = (result.notes + "; " + notes) if result.notes else notes

    return result


# ---------------------------------------------------------------------------
# Output
# ---------------------------------------------------------------------------

def save_results(results: list[ReverseResult], output_dir: str):
    """Save results as JSON and CSV."""
    os.makedirs(output_dir, exist_ok=True)

    # JSON
    json_path = os.path.join(output_dir, "reverse_results.json")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(
            [r.to_json_dict() for r in results],
            f,
            ensure_ascii=False,
            indent=2,
        )
    print(f"\nJSON saved: {json_path}")

    # CSV
    csv_path = os.path.join(output_dir, "reverse_results.csv")
    if results:
        fieldnames = list(results[0].to_csv_dict().keys())
        with open(csv_path, "w", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for r in results:
                writer.writerow(r.to_csv_dict())
    print(f"CSV  saved: {csv_path}")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Reverse-engineer indicator_id using Qwen 235B"
    )
    parser.add_argument(
        "--input", default=str(SCRIPT_DIR / "input_indicators.yaml"),
        help="Path to input indicators YAML",
    )
    parser.add_argument(
        "--csv", default=str(SCRIPT_DIR.parent.parent / "data-type.csv"),
        help="Path to data-type.csv metadata",
    )
    parser.add_argument(
        "--supplemental", default=str(SCRIPT_DIR / "supplemental_metadata.yaml"),
        help="Path to supplemental metadata YAML",
    )
    parser.add_argument(
        "--output-dir", default=str(SCRIPT_DIR / "outputs"),
        help="Output directory",
    )
    parser.add_argument(
        "--only", type=str, default=None,
        help="Process only this indicator code (e.g. --only GDP_REAL_YOY)",
    )
    parser.add_argument(
        "--dry-run", action="store_true",
        help="Print prompts without calling API",
    )
    args = parser.parse_args()

    # Load data
    csv_meta = load_csv_metadata(args.csv) if os.path.exists(args.csv) else {}
    supplemental = load_supplemental(args.supplemental) if os.path.exists(args.supplemental) else {}
    raw_indicators = load_input_indicators(args.input)

    # Filter if --only
    if args.only:
        raw_indicators = [
            i for i in raw_indicators
            if i["raw_indicator_code"] == args.only
        ]
        if not raw_indicators:
            print(f"Indicator '{args.only}' not found in input file.")
            sys.exit(1)

    # Enrich with metadata
    indicators = [enrich_indicator(r, csv_meta, supplemental) for r in raw_indicators]

    # Init client
    client = None
    if not args.dry_run:
        from qwen_client import QwenClient
        client = QwenClient()

    # Process sequentially
    results: list[ReverseResult] = []
    total = len(indicators)
    for i, ind in enumerate(indicators, 1):
        print(f"\n[{i}/{total}] {ind.raw_indicator_code} — {ind.current_meaning}")
        try:
            result = process_one_indicator(ind, client, dry_run=args.dry_run)
            results.append(result)
            if not args.dry_run:
                print(
                    f"  -> final_indicator_id={result.final_indicator_id}  "
                    f"consistency={result.consistency}  "
                    f"confidence={result.final_confidence}"
                )
        except Exception as e:
            print(f"  [ERROR] {e}")
            # Create a failure result so we don't lose the indicator
            fail = ReverseResult(
                raw_indicator_code=ind.raw_indicator_code,
                current_meaning=ind.current_meaning,
                indicator_name=ind.indicator_name,
                notes=f"Processing failed: {e}",
            )
            results.append(fail)

    # Save
    save_results(results, args.output_dir)

    # Summary
    if not args.dry_run and results:
        print("\n--- Summary ---")
        for r in results:
            status = "✓" if r.consistency == "high" else "~" if r.consistency == "medium" else "✗"
            print(
                f"  {status} {r.raw_indicator_code:40s} -> {r.final_indicator_id:30s} "
                f"[{r.consistency}]"
            )


if __name__ == "__main__":
    main()
