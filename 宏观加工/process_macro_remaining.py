"""
剩余月频宏观指标加工
- 从原始 Excel 中提取月频指标，统一格式输出 CSV
- 时间范围：2024-11 起
- 所有数值保留小数点后两位
"""

import warnings
import pandas as pd
from pathlib import Path

warnings.filterwarnings("ignore")

ROOT = Path(__file__).resolve().parents[1]
MONTHLY = ROOT / "data/raw/monthly"
NEW_DATA = ROOT / "data/raw/2026-4-2"
OUTPUT = Path(__file__).parent / "output"
OUTPUT.mkdir(exist_ok=True)

START_MONTH = "2024-11"
DECIMAL_PLACES = 2

# ---------------------------------------------------------------------------
# 指标定义：indicator_id -> (excel_col, indicator_name, unit, adjustment, source, data_type, file)
# ---------------------------------------------------------------------------

INDICATORS = {
    # --- nbs_macro_core_20260305.xlsx ---
    "CPI_YOY": (
        "中国:CPI:同比", "CPI:同比",
        "%", "YoY", "NBS", "Inflation",
        "nbs_macro_core_20260305.xlsx",
    ),
    "PPI_YOY": (
        "中国:PPI:全部工业品:同比", "PPI:同比",
        "%", "YoY", "NBS", "Inflation",
        "nbs_macro_core_20260305.xlsx",
    ),
    "PMI_MANU": (
        "中国:PMI", "中国:PMI",
        "", "Level", "NBS", "Sentiment",
        NEW_DATA / "中国-PMI.xlsx",
    ),
    "PMI_SERV": (
        "中国:非制造业PMI:商务活动", "中国:非制造业PMI",
        "", "Level", "NBS", "Sentiment",
        NEW_DATA / "中国-非制造业PMI.xlsx",
    ),
    "INDUSTRY_YOY": (
        "中国:工业增加值:同比", "工业增加值:同比",
        "%", "YoY", "NBS", "Growth",
        "nbs_macro_core_20260305.xlsx",
    ),
    # --- macro_20260310.xlsx ---
    "TSF_STOCK_YOY": (
        "中国:社会融资规模存量:同比", "社融存量:同比",
        "%", "YoY", "PBOC", "Credit",
        "macro_20260310.xlsx",
    ),
    "LPR_1Y": (
        "贷款市场报价利率(LPR):1年", "LPR:1年期",
        "%", "Level", "CFETS", "Rate",
        "macro_20260310.xlsx",
    ),
    "GOV_EXPEND_CUM_YOY": (
        "中国:财政预算支出:累计同比", "财政支出累计同比",
        "%", "YoY", "MOF", "Fiscal",
        "macro_20260310.xlsx",
    ),
    # --- marco_meeting_318.xlsx ---
    "M1_YOY": (
        "中国:M1:同比", "中国:M1:同比",
        "%", "YoY", "PBOC", "Credit",
        "marco_meeting_318.xlsx",
    ),
    "M2_YOY": (
        "中国:M2:同比", "M2:同比",
        "%", "YoY", "PBOC", "Credit",
        "marco_meeting_318.xlsx",
    ),
    "URBAN_SURVEYED_UNEMPLOYMENT_RATE": (
        "中国:城镇调查失业率", "城镇调查失业率",
        "%", "Level", "NBS", "Labor",
        "marco_meeting_318.xlsx",
    ),
    # --- growth.xlsx ---
    "RETAIL_SALES_YOY": (
        "中国:社会消费品零售总额:累计同比", "社会消费品零售总额",
        "%", "YoY", "NBS", "Growth",
        "growth.xlsx",
    ),
    "CONSUMER_CONFIDENCE": (
        "中国:消费者信心指数", "中国:消费者信心指数",
        "", "Level", "NBS", "Sentiment",
        NEW_DATA / "中国-消费者信心指数.xlsx",
    ),
    "MANU_INVEST_CUM_YOY": (
        "中国:固定资产投资完成额:制造业:累计同比", "制造业投资:累计同比",
        "%", "YoY", "NBS", "Investment",
        "growth.xlsx",
    ),
    "REAL_ESTATE_INVEST_CUM_YOY": (
        "中国:房地产开发投资完成额:累计同比", "房地产开发投资完成额:累计同比",
        "%", "YoY", "NBS", "Real_Estate",
        "growth.xlsx",
    ),
    "INFRA_INVEST_CUM_YOY": (
        "中国:城镇固定资产投资完成额:基础设施(不含电力):累计同比", "基础设施投资:累计同比",
        "%", "YoY", "NBS", "Investment",
        "growth.xlsx",
    ),
    "RESID_HOUSE_SALES_CUM_YOY": (
        "商品房销售额:住宅:累计同比", "商品房销售额(住宅)",
        "%", "YoY", "NBS", "Real_Estate",
        "growth.xlsx",
    ),
    "PMI_NEW_EXPORT_ORDERS": (
        "中国:PMI:新出口订单", "中国:PMI:新出口订单",
        "", "Level", "NBS", "Sentiment",
        NEW_DATA / "中国-PMI-新出口订单.xlsx",
    ),
    # --- import_export.xlsx ---
    "EXPORT_AMOUNT_CNY_YOY": (
        "中国:出口金额:同比", "中国:出口金额:同比",
        "%", "YoY", "GACC", "Trade",
        "import_export.xlsx",
    ),
    "IMPORT_AMOUNT_CNY_YOY": (
        "中国:进口金额:同比", "中国:进口金额:同比",
        "%", "YoY", "GACC", "Trade",
        "import_export.xlsx",
    ),
    # --- GDP.xlsx ---
    "GDP_REAL_YOY": (
        "中国:GDP:不变价:同比", "中国:GDP:不变价:当季同比",
        "%", "YoY", "NBS", "Growth",
        "GDP.xlsx",
    ),
    # --- marco_0316.xlsx ---
    "SPECIAL_BOND_ISSUE_CUM": (
        "中国:发行地方政府债券:按用途划分:发行新增专项债券:累计值",
        "中国:发行地方政府债券:按用途划分:发行新增专项债券:累计值",
        "CNY_100M", "", "MOF", "Fiscal",
        "marco_0316.xlsx",
    ),
}


# ---------------------------------------------------------------------------
# 提取函数
# ---------------------------------------------------------------------------

def load_monthly_indicator(file_ref: "str | Path", excel_col: str) -> pd.DataFrame:
    """从月频 Excel 提取单列，返回 (ref_month, value) DataFrame。"""
    path = file_ref if isinstance(file_ref, Path) else MONTHLY / file_ref
    df = pd.read_excel(path, sheet_name="指标", engine="openpyxl")
    df["日期"] = pd.to_datetime(df["日期"], errors="coerce")
    df = df.dropna(subset=["日期"])
    df["ref_month"] = df["日期"].dt.to_period("M").astype(str)
    df["value"] = pd.to_numeric(df[excel_col], errors="coerce")
    df = df[["ref_month", "value"]].dropna(subset=["value"])
    df = df[df["ref_month"] >= START_MONTH]
    return df


# ---------------------------------------------------------------------------
# 主流程
# ---------------------------------------------------------------------------

results = []

for ind_id, (excel_col, ind_name, unit, adj, source, dtype, file_name) in INDICATORS.items():
    df = load_monthly_indicator(file_name, excel_col)
    df.insert(0, "indicator_id", ind_id)
    df["unit"] = unit
    df["adjustment"] = adj
    df["source"] = source
    df["data_type"] = dtype
    results.append(df)

final = pd.concat(results, ignore_index=True)
final = final.sort_values(["indicator_id", "ref_month"]).reset_index(drop=True)
final["value"] = final["value"].apply(lambda v: f"{float(v):.{DECIMAL_PLACES}f}")

final = final[["indicator_id", "ref_month", "value", "unit", "adjustment", "source", "data_type"]]

out_path = OUTPUT / "processed_macro_remaining_2024_11_latest.csv"
final.to_csv(out_path, index=False)

# ---------------------------------------------------------------------------
# 终端汇总
# ---------------------------------------------------------------------------

print("=" * 60)
print("剩余月频宏观指标加工完成")
print("=" * 60)

print(f"\n输出文件：{out_path}")
print(f"总行数：{len(final)}")

print("\n各指标最新月份：")
for ind, grp in final.groupby("indicator_id"):
    latest = grp["ref_month"].max()
    count = len(grp)
    print(f"  {ind:<35} 最新={latest}  共{count}行")
