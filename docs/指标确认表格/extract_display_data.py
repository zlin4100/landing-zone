"""
extract_display_data.py
-----------------------
从 data/raw/ 原始文件提取指标展示表格所需数据。
- 月频指标：直接取当月值
- 日频指标：取月末最后交易日值（方案A）
输出范围：2025-02 ~ 2026-02（13个月）

运行方式（从项目根目录）：
    python docs/指标确认表格/extract_display_data.py
"""

import pandas as pd
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]  # 项目根目录
RAW = ROOT / "data" / "raw"

MONTHS = pd.date_range("2025-02-01", "2026-02-01", freq="MS")
MONTH_LABELS = [m.strftime("%y-%m") for m in MONTHS]  # ['25-02', ..., '26-02']


# ──────────────────────────────────────────────
# 工具函数
# ──────────────────────────────────────────────

def read_choice_monthly(path: Path, skip_rows: int = 5) -> pd.DataFrame:
    """
    读取 Choice 导出的月频 Excel。
    格式：前5行为元数据（指标名、ID、频率、单位、时间区间），
    第6行起为数据，第2列为日期，第3列起为指标值。
    返回：以月份（period M）为索引的 DataFrame。
    """
    df = pd.read_excel(path, sheet_name=0, skiprows=skip_rows, header=0)
    df = df.iloc[:, 1:]  # 去掉序号列
    df.columns = ["date"] + [f"col{i}" for i in range(len(df.columns) - 1)]
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    df = df.dropna(subset=["date"]).set_index("date").sort_index()
    return df


def read_choice_daily_monthend(path: Path, skip_rows: int = 7) -> pd.DataFrame:
    """
    读取 Choice 导出的日频 Excel，聚合为月末最后交易日值。
    格式：前7行为元数据，第8行起为数据。
    返回：以月末日期（period M）为索引的 DataFrame。
    """
    df = pd.read_excel(path, sheet_name=0, skiprows=skip_rows, header=0)
    df = df.iloc[:, 1:]
    df.columns = ["date"] + [f"col{i}" for i in range(len(df.columns) - 1)]
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    df = df.dropna(subset=["date"]).set_index("date").sort_index()
    # 取月末最后交易日值
    monthly = df.resample("ME").last()
    monthly.index = monthly.index.to_period("M")
    return monthly


def filter_range(df: pd.DataFrame) -> pd.DataFrame:
    """截取 2025-02 ~ 2026-02。"""
    idx = pd.period_range("2025-02", "2026-02", freq="M")
    return df.reindex(idx)


def fmt(val, decimals: int = 1) -> str:
    """将数值格式化为字符串，NaN 输出 '—'。"""
    if pd.isna(val):
        return "—"
    if decimals == 0:
        return f"{int(val):,}"
    return f"{val:.{decimals}f}"


# ──────────────────────────────────────────────
# 1. 月频数据提取
# ──────────────────────────────────────────────

def load_nbs_core() -> dict:
    """nbs_macro_core_20260305.xlsx → CPI_YOY PPI_YOY PMI_MANU PMI_SERV INDUSTRY_YOY"""
    path = RAW / "monthly" / "nbs_macro_core_20260305.xlsx"
    df = read_choice_monthly(path)
    df.index = df.index.to_period("M")
    df = filter_range(df)
    return {
        "CPI_YOY":       df["col0"],  # EMM00072301
        "PPI_YOY":       df["col1"],  # EMM00073348
        "PMI_MANU":      df["col2"],  # EMM00121996
        "PMI_SERV":      df["col3"],  # EMM00122009
        "INDUSTRY_YOY":  df["col4"],  # EMM00008445
    }


def load_macro() -> dict:
    """macro_20260310.xlsx → TSF_STOCK_YOY M2_YOY LPR_1Y GOV_EXPEND_CUMULATIVE_YOY"""
    path = RAW / "monthly" / "macro_20260310.xlsx"
    df = read_choice_monthly(path)
    df.index = df.index.to_period("M")
    df = filter_range(df)
    return {
        "TSF_STOCK_YOY":            df["col0"],  # EMM00634721
        "M2_YOY":                   df["col1"],  # EMM00087086
        "LPR_1Y":                   df["col2"],  # EMM02326278
        # col3 = LPR_5Y（跳过，非采购项）
        "GOV_EXPEND_CUMULATIVE_YOY": df["col4"],  # EMM00058496
    }


def load_growth() -> dict:
    """growth.xlsx → RETAIL_SALES_YOY CONSUMER_CONFIDENCE 投资三分法 EXPORT PMI_NEW_EXPORT_ORDERS"""
    path = RAW / "monthly" / "growth.xlsx"
    df = read_choice_monthly(path)
    df.index = df.index.to_period("M")
    df = filter_range(df)
    return {
        "RETAIL_SALES_YOY":                df["col0"],  # EMM00063225
        "CONSUMER_CONFIDENCE":             df["col1"],  # EMM00122031
        "MANUFACTURING_INVEST_CUM_YOY":    df["col2"],  # EMM00027220
        "REAL_ESTATE_INVEST_CUM_YOY":      df["col3"],  # EMI00120220
        "INFRA_INVEST_CUM_YOY":            df["col4"],  # EMM00597116
        "RESID_HOUSE_SALES_CUMULATIVE_YOY": df["col5"], # EMM00877640
        "EXPORT_CUMULATIVE_YOY":           df["col6"],  # EMM00183416
        "PMI_NEW_EXPORT_ORDERS":           df["col7"],  # EMM00121999
    }


def load_marco_0316() -> dict:
    """marco_0316.xlsx → SPECIAL_BOND_ISSUE_CUM RRR_LARGE_FIN_INST"""
    path = RAW / "monthly" / "marco_0316.xlsx"
    df = read_choice_monthly(path)
    df.index = df.index.to_period("M")
    df = filter_range(df)
    return {
        "SPECIAL_BOND_ISSUE_CUM":  df["col0"],  # EMM01259587
        "RRR_LARGE_FIN_INST":      df["col1"],  # EMM01280574
    }


# ──────────────────────────────────────────────
# 2. 日频数据提取（月末值）
# ──────────────────────────────────────────────

def load_cn_bond_daily() -> dict:
    """cn_bond_credit_rates_daily.xlsx → CGB_3Y CGB_10Y AA_CREDIT_YIELD_3Y DR007（月末值）"""
    path = RAW / "daily" / "cn_bond_credit_rates_daily.xlsx"
    df = read_choice_daily_monthend(path)
    df = filter_range(df)
    return {
        # col0 = CBOND_NEW_COMPOSITE_WEALTH（建模用，不在展示表）
        "CGB_3Y":               df["col1"],  # E1000174
        "CGB_10Y":              df["col2"],  # E1000180
        "AA_CREDIT_YIELD_3Y":   df["col3"],  # E1000469
        "DR007":                df["col4"],  # E1300004
    }


def load_cross_market_daily() -> dict:
    """cross_market.xlsx → BRENT_CRUDE VIX XAUUSD FX_CNY_MID（月末值）"""
    path = RAW / "daily" / "cross_market.xlsx"
    df = read_choice_daily_monthend(path)
    df = filter_range(df)
    return {
        "BRENT_CRUDE": df["col0"],  # EMM01588169
        "VIX":         df["col1"],  # EMG00002651
        "XAUUSD":      df["col2"],  # EMI01630991
        "FX_CNY_MID":  df["col3"],  # EMM00058124
    }


# ──────────────────────────────────────────────
# 3. 汇总输出
# ──────────────────────────────────────────────

INDICATOR_FMT = {
    # 指标代码: (显示名称, 小数位数)
    "PMI_MANU":                        ("中国:PMI",                              1),
    "PMI_SERV":                        ("中国:非制造业PMI:商务活动",              1),
    "INDUSTRY_YOY":                    ("中国:工业增加值:同比",                   1),
    "PMI_NEW_EXPORT_ORDERS":           ("中国:PMI:新出口订单",                   1),
    "CPI_YOY":                         ("中国:CPI:同比",                         1),
    "PPI_YOY":                         ("中国:PPI:全部工业品:同比",              1),
    "RETAIL_SALES_YOY":                ("社会消费品零售总额:累计同比",            1),
    "CONSUMER_CONFIDENCE":             ("中国:消费者信心指数",                    1),
    "INFRA_INVEST_CUM_YOY":            ("基础设施投资(不含电力):累计同比",       1),
    "MANUFACTURING_INVEST_CUM_YOY":    ("制造业投资:累计同比",                   1),
    "REAL_ESTATE_INVEST_CUM_YOY":      ("房地产开发投资:累计同比",               1),
    "RESID_HOUSE_SALES_CUMULATIVE_YOY": ("住宅销售额:累计同比",                  1),
    "EXPORT_CUMULATIVE_YOY":           ("出口金额:累计同比",                     1),
    "FX_CNY_MID":                      ("中间价:美元兑人民币（月末值）",         4),
    "M2_YOY":                          ("中国:M2:同比",                          1),
    "DR007":                           ("DR007（月末值）",                       4),
    "TSF_STOCK_YOY":                   ("社会融资规模存量:同比",                 1),
    "AA_CREDIT_YIELD_3Y":              ("AA级信用债收益率:3年（月末值）",        4),
    "CGB_10Y":                         ("中债国债到期收益率:10年（月末值）",     4),
    "CGB_3Y":                          ("中债国债到期收益率:3年（月末值）",      4),
    "GOV_EXPEND_CUMULATIVE_YOY":       ("财政预算支出:累计同比",                 1),
    "SPECIAL_BOND_ISSUE_CUM":          ("新增专项债券:累计值（亿元）",           0),
    "LPR_1Y":                          ("LPR:1年",                               1),
    "RRR_LARGE_FIN_INST":              ("存款准备金率:大型金融机构",              1),
    "BRENT_CRUDE":                     ("ICE布油收盘价（月末值，USD/桶）",       2),
    "XAUUSD":                          ("COMEX黄金结算价（月末值，USD/盎司）",  1),
    "VIX":                             ("VIX（月末值）",                         2),
}

DISPLAY_ORDER = [
    # 1. 经济总量与景气度
    "PMI_MANU", "PMI_SERV", "INDUSTRY_YOY", "PMI_NEW_EXPORT_ORDERS",
    # 2. 价格与通胀
    "CPI_YOY", "PPI_YOY",
    # 3. 消费
    "RETAIL_SALES_YOY", "CONSUMER_CONFIDENCE",
    # 4. 投资与房地产
    "INFRA_INVEST_CUM_YOY", "MANUFACTURING_INVEST_CUM_YOY",
    "REAL_ESTATE_INVEST_CUM_YOY", "RESID_HOUSE_SALES_CUMULATIVE_YOY",
    # 5. 进出口与外需
    "EXPORT_CUMULATIVE_YOY", "FX_CNY_MID",
    # 6. 货币与信用
    "M2_YOY", "DR007", "TSF_STOCK_YOY", "AA_CREDIT_YIELD_3Y", "CGB_10Y", "CGB_3Y",
    # 7. 财政与政策工具
    "GOV_EXPEND_CUMULATIVE_YOY", "SPECIAL_BOND_ISSUE_CUM", "LPR_1Y", "RRR_LARGE_FIN_INST",
    # 8. 国际环境与风险偏好
    "BRENT_CRUDE", "XAUUSD", "VIX",
]


def main():
    print("读取原始文件...")
    data: dict[str, pd.Series] = {}
    data.update(load_nbs_core())
    data.update(load_macro())
    data.update(load_growth())
    data.update(load_marco_0316())
    data.update(load_cn_bond_daily())
    data.update(load_cross_market_daily())

    # 构建宽表（行=指标，列=月份，newest→oldest）
    periods = pd.period_range("2025-02", "2026-02", freq="M")[::-1]  # 26-02 → 25-02
    col_labels = [p.strftime("%y-%m") for p in periods]

    rows = []
    for code in DISPLAY_ORDER:
        series = data.get(code)
        if series is None:
            continue
        name, decimals = INDICATOR_FMT[code]
        row = {"指标代码": code, "指标名称": name}
        for p, label in zip(periods, col_labels):
            val = series.get(p)
            row[label] = fmt(val, decimals)
        rows.append(row)

    result = pd.DataFrame(rows).set_index("指标代码")

    # 打印到控制台
    pd.set_option("display.max_columns", None)
    pd.set_option("display.width", 300)
    pd.set_option("display.max_colwidth", 40)
    print("\n" + "=" * 80)
    print(f"指标展示表格数据  {col_labels[-1]} ~ {col_labels[0]}")
    print("=" * 80)
    print(result.to_string())
    return result


if __name__ == "__main__":
    main()
