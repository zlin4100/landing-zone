"""四大类资产 Benchmark Profile

读取已计算好的月收益率和 CGB_1Y 无风险利率，
输出 1Y/3Y/5Y 窗口的年化收益、年化波动率、Sharpe Ratio。

Usage:
    python3 建模数据/asset_benchmark_profile.py
"""

from pathlib import Path

import numpy as np
import pandas as pd

DIR = Path(__file__).resolve().parent
RETURNS_CSV = DIR / "plan_a_returns.csv"
RAW_CSV = DIR / "建模月频序列.csv"
OUT_CSV = DIR / "asset_benchmark_profile.csv"

RETURN_COLS = ["r_cash", "r_bond", "r_equity", "r_alt"]
ASSET_CLASSES = ["CASH", "BOND", "EQUITY", "ALT"]
WINDOWS = {"1y": 12, "3y": 36, "5y": 60}


def main():
    returns = pd.read_csv(RETURNS_CSV, index_col="month")
    rf_raw = pd.read_csv(RAW_CSV, index_col="month", usecols=["month", "CGB_1Y"])
    rf_monthly = rf_raw["CGB_1Y"] / 100 / 12

    # 对齐
    common = returns.index.intersection(rf_monthly.dropna().index)
    returns = returns.loc[common, RETURN_COLS]
    rf_monthly = rf_monthly.loc[common]

    rows = []
    for asset, col in zip(ASSET_CLASSES, RETURN_COLS):
        row = {"asset_class": asset}
        for label, w in WINDOWS.items():
            r = returns[col].iloc[-w:]
            rf = rf_monthly.iloc[-w:]
            excess = r - rf

            row[f"ann_return_{label}"] = r.mean() * 12
            row[f"ann_vol_{label}"] = r.std() * np.sqrt(12)
            row[f"sharpe_ratio_{label}"] = excess.mean() / excess.std() * np.sqrt(12)
        rows.append(row)

    col_order = [
        "asset_class",
        "ann_return_1y", "ann_return_3y", "ann_return_5y",
        "ann_vol_1y", "ann_vol_3y", "ann_vol_5y",
        "sharpe_ratio_1y", "sharpe_ratio_3y", "sharpe_ratio_5y",
    ]
    df = pd.DataFrame(rows, columns=col_order).round(4)
    df.to_csv(OUT_CSV, index=False)
    print(f"✓ {OUT_CSV}")
    print(df.to_string(index=False))


if __name__ == "__main__":
    main()
