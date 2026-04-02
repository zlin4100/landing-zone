#!/usr/bin/env python3
"""
build_macro_prompt.py
自动拼接宏观指标 CSV 片段，生成「市场分析-提示词模板-宏观.md」。

用法（项目根目录下执行）：
    python 提示词模板/build_macro_prompt.py

自定义路径：
    python 提示词模板/build_macro_prompt.py \\
        --data1  宏观加工/output/processed_macro_2024_11_latest.csv \\
        --data2  宏观加工/output/processed_macro_remaining_2024_11_latest.csv \\
        --schema 提示词模板/data-type.csv \\
        --output 提示词模板/市场分析-提示词模板-宏观.md
"""

import argparse
from pathlib import Path

import pandas as pd

# ── 默认路径（相对于本脚本所在目录的上一级，即项目根） ──────────────────────────
_HERE = Path(__file__).parent
BASE  = _HERE.parent

DEFAULT_DATA1  = BASE / "宏观加工/output/processed_macro_2024_11_latest.csv"
DEFAULT_DATA2  = BASE / "宏观加工/output/processed_macro_remaining_2024_11_latest.csv"
DEFAULT_SCHEMA = _HERE / "data-type.csv"
DEFAULT_OUTPUT = _HERE / "市场分析-提示词模板-宏观.md"

CSV_HEADER = "indicator_id,ref_month,value,unit,adjustment,source,data_type"


# ── 解析 data-type.csv：保留 section 顺序及各 section 内的指标顺序 ─────────────
def parse_schema(path: Path) -> list[dict]:
    """
    返回:
        [{"section": "Growth（经济增长）", "indicators": ["GDP_REAL_YOY", ...]}, ...]
    section 顺序与 csv 中 `# Xxx` 注释行的出现顺序一致。
    """
    sections: list[dict] = []
    current: dict | None = None
    with path.open(encoding="utf-8") as f:
        for raw in f:
            line = raw.strip()
            if not line:
                continue
            if line.startswith("#"):
                label = line.lstrip("# ").strip()
                current = {"section": label, "indicators": []}
                sections.append(current)
            elif current and not line.startswith("indicator_id"):
                iid = line.split(",")[0].strip()
                if iid:
                    current["indicators"].append(iid)
    return sections


# ── 数值格式化：去除不必要的尾部零（39977.00→39977，7.10→7.1） ─────────────────
def fmt_value(v) -> str:
    """
    value 字段的“输出格式化 API”。

    作用：把上游 CSV 里可能出现的 NaN/空值/字符串数字统一规整成适合写入 Markdown
    ```csv``` 代码块的文本格式，避免出现 `nan`、`39977.0` 这类对阅读/复制不友好的输出。
    """
    if pd.isna(v):
        return ""
    try:
        f = float(v)
        return str(int(f)) if f == int(f) else str(f)
    except (ValueError, TypeError):
        return str(v)


# ── 主逻辑 ────────────────────────────────────────────────────────────────────
def build(data1: Path, data2: Path, schema: Path, output: Path) -> None:
    sections = parse_schema(schema)

    # 合并两个数据文件
    df = pd.concat(
        [pd.read_csv(data1, dtype=str), pd.read_csv(data2, dtype=str)],
        ignore_index=True,
    )

    # 按时间升序排列
    df["_dt"] = pd.to_datetime(df["ref_month"], errors="coerce")
    df = df.sort_values(["indicator_id", "_dt"]).drop(columns="_dt")
    df["ref_month"] = pd.to_datetime(df["ref_month"]).dt.strftime("%Y-%m")

    # 格式化数值列，其余 NaN → ""
    df["value"] = df["value"].apply(fmt_value)
    df = df.fillna("")

    blocks: list[str] = []

    for sec in sections:
        label       = sec["section"]
        ind_ordered = sec["indicators"]

        # 按 data-type.csv 中的指标顺序拼接
        chunks = [df[df["indicator_id"] == iid] for iid in ind_ordered]
        sec_df = pd.concat(chunks, ignore_index=True)
        if sec_df.empty:
            continue

        rows = [f"## {label}", "```csv", CSV_HEADER]
        for _, r in sec_df.iterrows():
            rows.append(
                f"{r['indicator_id']},{r['ref_month']},{r['value']},"
                f"{r['unit']},{r['adjustment']},{r['source']},{r['data_type']}"
            )
        rows.append("```")
        rows.append("")
        blocks.extend(rows)

    output.write_text("\n".join(blocks), encoding="utf-8")
    n_data = sum(1 for b in blocks if b and not b.startswith(("##", "```", "indicator")))
    print(f"✅  写入完成：{output}")
    print(f"    {len(sections)} 个板块，{n_data} 条数据行")


# ── CLI ───────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="构建宏观提示词模板 Markdown")
    parser.add_argument("--data1",  type=Path, default=DEFAULT_DATA1,
                        help="第一个 CSV（processed_macro_...）")
    parser.add_argument("--data2",  type=Path, default=DEFAULT_DATA2,
                        help="第二个 CSV（processed_macro_remaining_...）")
    parser.add_argument("--schema", type=Path, default=DEFAULT_SCHEMA,
                        help="data-type.csv（定义 section 与指标顺序）")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT,
                        help="输出 Markdown 文件路径")
    args = parser.parse_args()
    build(args.data1, args.data2, args.schema, args.output)
