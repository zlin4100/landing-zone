"""Demo: 大类资产建模数据加工

从 data/raw/ 读取原始 Excel，加工为月频序列，输出 CSV。
覆盖 10 个建模核心指标（见《大类资产建模数据》采购表）。

Usage:
    python3 docs/建模数据/demo_modeling_data.py
"""

from pathlib import Path

import numpy as np
import pandas as pd

RAW_DIR = Path(__file__).resolve().parents[2] / "data" / "raw"
OUT_DIR = Path(__file__).resolve().parent


# ---------------------------------------------------------------------------
# 读取函数
# ---------------------------------------------------------------------------

def read_choice_indicator(filepath, col_index: int = 2) -> pd.Series:
    """Choice 导出格式（序号/日期/值，前 10 行元数据）。"""
    df = pd.read_excel(filepath, header=None)
    data = df.iloc[10:, [1, col_index]].copy()
    data.columns = ["date", "value"]
    data["date"] = pd.to_datetime(data["date"], errors="coerce")
    data["value"] = pd.to_numeric(data["value"], errors="coerce")
    return data.dropna(subset=["date", "value"]).set_index("date").sort_index()["value"]


def read_kline_close(filepath) -> pd.Series:
    """Choice K线导出格式，提取收盘价（col 6）。"""
    df = pd.read_excel(filepath, header=None)
    data = df.iloc[1:, [2, 6]].copy()
    data.columns = ["date", "close"]
    data["date"] = pd.to_datetime(data["date"], errors="coerce")
    data["close"] = pd.to_numeric(data["close"], errors="coerce")
    return data.dropna(subset=["date", "close"]).set_index("date").sort_index()["close"]


def read_cba02201(filepath) -> pd.Series:
    """Choice 行情导出格式（CBA02201.CS），取收盘价 col 4。"""
    df = pd.read_excel(filepath, header=None)
    data = df.iloc[1:, [0, 4]].copy()
    data.columns = ["date", "close"]
    data["date"] = pd.to_datetime(data["date"], errors="coerce")
    data["close"] = pd.to_numeric(data["close"], errors="coerce")
    return data.dropna(subset=["date", "close"]).set_index("date").sort_index()["close"]


def to_month_end(s: pd.Series) -> pd.Series:
    """日频 → 月频（每月最后一个有效交易日）。"""
    return s.resample("ME").last().dropna()


# ---------------------------------------------------------------------------
# 指标配置：指标代码 → (读取方式, 文件, 列索引)
# ---------------------------------------------------------------------------

INDICATORS = {
    # 无风险利率
    "CGB_1Y":  ("choice", "daily/bond_CGB_1y.xlsx", 2),
    # 固收类
    "CGB_3Y":  ("choice", "daily/cn_bond_credit_rates_daily.xlsx", 3),
    "CGB_10Y": ("choice", "daily/cn_bond_credit_rates_daily.xlsx", 4),
    "AA_CREDIT_YIELD_3Y": ("choice", "daily/cn_bond_credit_rates_daily.xlsx", 5),
    "CBOND_NEW_COMPOSITE_WEALTH": ("choice", "daily/cn_bond_credit_rates_daily.xlsx", 2),
    # 现金类
    "CBA02201.CS": ("cba02201", "daily/CBA02201.CS行情数据统计明细.xls", None),
    # 股票类
    "CSI300_TR": ("kline", "daily/K线导出_H00300_日线数据.xlsx", None),
    "CSI300":    ("kline", "daily/K线导出_000300_日线数据.xlsx", None),
    # 另类资产
    "AU9999": ("kline", "daily/K线导出_AU9999_日线数据.xlsx", None),
    "NHCI":   ("kline", "daily/K线导出_NHCI_日线数据.xlsx", None),
}


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    print("=" * 60)
    print("大类资产建模数据加工 Demo — 10 指标")
    print("=" * 60)

    monthly = {}

    for code, (fmt, relpath, col) in INDICATORS.items():
        fpath = RAW_DIR / relpath
        if fmt == "choice":
            daily = read_choice_indicator(fpath, col)
        elif fmt == "kline":
            daily = read_kline_close(fpath)
        elif fmt == "cba02201":
            daily = read_cba02201(fpath)

        m = to_month_end(daily)
        monthly[code] = m
        print(f"  [{code}] 日频 {len(daily):,} → 月频 {len(m):,}  "
              f"({m.index[0]:%Y-%m} ~ {m.index[-1]:%Y-%m})")

    # 合并
    df = pd.DataFrame(monthly)
    df.index.name = "month"
    df.index = df.index.strftime("%Y-%m")

    # 保存
    out = OUT_DIR / "建模月频序列.csv"
    df.to_csv(out)
    print(f"\n✓ 已保存 {out}")
    print(f"  {len(df)} 行 × {len(df.columns)} 列")
    print(f"  列: {', '.join(df.columns)}")


if __name__ == "__main__":
    main()
