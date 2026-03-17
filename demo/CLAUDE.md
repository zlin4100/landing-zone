# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Purpose

This directory contains a standalone raw-data preview page for the landing-zone project. It is intentionally isolated from the main `src/` ETL pipeline to avoid polluting the project.

## Files

| File | Role |
|------|------|
| `extract_data.py` | Reads xlsx files from `../data/raw/` and writes `raw_data.js` |
| `raw_data.js` | Auto-generated — do not edit by hand |
| `raw_data.json` | Intermediate output from extraction (not used by the page) |
| `raw.html` | Self-contained demo page; loads `chart.umd.min.js` and `raw_data.js` |
| `chart.umd.min.js` | Local copy of Chart.js 4.4.0 — no CDN dependency |

## Regenerating data

Run from the **project root**:

```bash
python3 demo/extract_data.py
```

This re-reads all source xlsx files and overwrites `raw_data.js`. The page reloads automatically if a dev server is running.

## Serving the page

```bash
python3 -m http.server 7788 --directory .
# open http://localhost:7788/demo/raw.html
```

A `.claude/launch.json` entry named `demo` is already configured for `preview_start`.

## Architecture

**Data flow**: `data/raw/**/*.xlsx` → `extract_data.py` → `raw_data.js` → `raw.html`

**`extract_data.py`** has three reader functions matching Choice terminal export formats:
- `read_choice_monthly` / `read_choice_daily` — rows 0–2 are metadata headers; data starts at row 3; column index → indicator code mapping is passed as `col_map`
- `read_kline` — K-line exports use a different schema (`Sheet0`, `交易时间` / `收盘价` columns)
- `read_annual` — year-frequency files, same Choice header layout

**`raw.html`** is fully self-contained (no build step, no framework):
- `RAW_DATA` global from `raw_data.js` holds `{ section1, section2, section3, section4 }` each containing `{ [CODE]: { dates, values } }`
- `META` object maps every indicator code to display metadata (name, unit, freq, src, color)
- `SECTIONS` defines the four tabs and their ordered code lists
- `render()` is the single re-render entry point — called on load and after any filter/section/view change
- Chart instances are tracked in `chartInstances` and destroyed before re-creation to avoid Chart.js memory leaks

## Scope constraints

- Only sections 1–4 from `docs/数据采集进度.md` are included (sections 5–7 excluded by design)
- Time range is 2025–2026 only; the year filter in the UI further narrows to a single year
- All logic must stay in `demo/` — do not import from or write to `src/`
