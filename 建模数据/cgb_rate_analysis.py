"""CGB 利率汇总分析

读取 建模月频序列.csv，输出季末 CGB_1Y / CGB_10Y / term_spread 序列。

Usage:
    python 建模数据/cgb_rate_analysis.py
"""

from pathlib import Path

import pandas as pd

BASE_DIR = Path(__file__).resolve().parent
CSV_IN = BASE_DIR / "建模月频序列.csv"
OUT_CSV = BASE_DIR / "cgb_summary_metrics.csv"


def main():
    df = pd.read_csv(CSV_IN, index_col=0, parse_dates=True)
    df.index.name = "date"
    df = df.sort_index()

    # 季末重采样（取月末值）
    quarterly = df[["CGB_1Y", "CGB_10Y"]].resample("QE").last().dropna()

    # 从 2021Q1 开始
    quarterly = quarterly[quarterly.index >= "2021-01-01"].copy()

    quarterly["term_spread"] = quarterly["CGB_10Y"] - quarterly["CGB_1Y"]

    # 季度标签
    quarterly["quarter_label"] = quarterly.index.map(
        lambda dt: f"{dt.year}Q{(dt.month - 1) // 3 + 1}"
    )

    out = (
        quarterly[["quarter_label", "CGB_1Y", "CGB_10Y", "term_spread"]]
        .rename(columns={"CGB_1Y": "CGB_1Y_YTM", "CGB_10Y": "CGB_10Y_YTM"})
        .round(2)
        .reset_index()
    )
    out["date"] = out["date"].dt.strftime("%Y-%m-%d")

    out.to_csv(OUT_CSV, index=False)
    print(f"✓ {OUT_CSV}")
    print(out.to_string(index=False))


if __name__ == "__main__":
    main()
