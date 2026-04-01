"""
宏观指标月频加工
- 日度转月度：BRENT_CRUDE, XAUUSD, DR007, FX_CNY_MID, VIX,
              AA_CREDIT_YIELD_3Y -> CREDIT_YTM_AA_3Y, CGB_3Y -> CGB_3Y_YTM
- 专项债派生：SPECIAL_BOND_PROGRESS = SPECIAL_BOND_ISSUE_CUM / LOCAL_SPECIAL_BOND_TARGET_ANNUAL
时间范围：2024-11 起
"""

import warnings
import pandas as pd
from pathlib import Path

warnings.filterwarnings("ignore")

ROOT = Path(__file__).resolve().parents[1]  # landing-zone/
DAILY = ROOT / "data/raw/daily"
MONTHLY = ROOT / "data/raw/monthly"
OUTPUT = Path(__file__).parent / "output"
OUTPUT.mkdir(exist_ok=True)

START_MONTH = "2024-11"

# 输出精度规则：所有指标统一保留2位小数
DECIMAL_PLACES = 2  # 所有指标统一保留2位小数

# 指标元数据：unit, adjustment, source, data_type
INDICATOR_META = {
    "BRENT_CRUDE":          ("USD/bbl", "Level",   "ICE",        "Inflation"),
    "XAUUSD":               ("USD/oz",  "Level",   "COMEX",      "Risk_Sentiment"),
    "FX_CNY_MID":           ("USD/CNY", "Level",   "PBOC",       "FX"),
    "VIX":                  ("",        "Level",   "CBOE",       "Risk_Sentiment"),
    "DR007":                ("%",       "Level",   "CFETS",      "Rate"),
    "CREDIT_YTM_AA_3Y":    ("%",       "Level",   "CHINA_BOND", "Rate"),
    "CGB_3Y_YTM":          ("%",       "Level",   "CHINA_BOND", "Rate"),
    "SPECIAL_BOND_PROGRESS": ("%",     "Derived", "Derived",    "Fiscal"),
}



# ---------------------------------------------------------------------------
# 辅助函数
# ---------------------------------------------------------------------------

def load_excel_daily(path: Path, col_name: str) -> pd.Series:
    """读取日频 Excel，返回以日期为索引的 Series（跳过元数据行）。"""
    df = pd.read_excel(path, sheet_name="指标")
    df["日期"] = pd.to_datetime(df["日期"], errors="coerce")
    df = df.dropna(subset=["日期"])
    df = df.set_index("日期")[col_name]
    df = pd.to_numeric(df, errors="coerce")
    df = df.dropna()
    return df


def to_month_end(series: pd.Series) -> pd.DataFrame:
    """月末最后有效值。"""
    df = series.resample("ME").last().dropna()
    df.index = df.index.to_period("M").strftime("%Y-%m")
    return df.rename("value").reset_index().rename(columns={"index": "ref_month"})


def to_month_mean(series: pd.Series) -> pd.DataFrame:
    """月均值（跳过 NaN）。"""
    df = series.resample("ME").mean().dropna()
    df.index = df.index.to_period("M").strftime("%Y-%m")
    return df.rename("value").reset_index().rename(columns={"index": "ref_month"})


# ---------------------------------------------------------------------------
# 1. 日频 → 月频
# ---------------------------------------------------------------------------

results = []

# --- BRENT_CRUDE (月均值) ---
s_brent = load_excel_daily(DAILY / "cross_market.xlsx", "期货收盘价(连续):ICE布油")
s_brent = s_brent[s_brent.index >= "2024-11-01"]
df_brent = to_month_mean(s_brent)
df_brent.columns = ["ref_month", "value"]
df_brent.insert(0, "indicator_id", "BRENT_CRUDE")
results.append(df_brent)

# --- XAUUSD (月均值) ---
s_xau = load_excel_daily(DAILY / "gold.xlsx", "期货收盘价(连续):COMEX黄金")
s_xau = s_xau[s_xau.index >= "2024-11-01"]
df_xau = to_month_mean(s_xau)
df_xau.columns = ["ref_month", "value"]
df_xau.insert(0, "indicator_id", "XAUUSD")
results.append(df_xau)

# --- FX_CNY_MID (月均值) ---
s_fx = load_excel_daily(DAILY / "cross_market.xlsx", "中间价:美元兑人民币")
s_fx = s_fx[s_fx.index >= "2024-11-01"]
df_fx = to_month_mean(s_fx)
df_fx.columns = ["ref_month", "value"]
df_fx.insert(0, "indicator_id", "FX_CNY_MID")
results.append(df_fx)

# --- VIX (月均值) ---
s_vix = load_excel_daily(DAILY / "cross_market.xlsx", "标准普尔500波动率指数(VIX)")
s_vix = s_vix[s_vix.index >= "2024-11-01"]
df_vix = to_month_mean(s_vix)
df_vix.columns = ["ref_month", "value"]
df_vix.insert(0, "indicator_id", "VIX")
results.append(df_vix)

# --- DR007 (月均值) ---
s_dr = load_excel_daily(DAILY / "cn_bond_credit_rates_daily.xlsx", "DR007")
s_dr = s_dr[s_dr.index >= "2024-11-01"]
df_dr = s_dr.resample("ME").mean().dropna()
df_dr.index = df_dr.index.to_period("M").strftime("%Y-%m")
df_dr = df_dr.reset_index()
df_dr.columns = ["ref_month", "value"]
df_dr.insert(0, "indicator_id", "DR007")
results.append(df_dr)

# --- AA_CREDIT_YIELD_3Y → CREDIT_YTM_AA_3Y (月末值) ---
s_aa = load_excel_daily(DAILY / "cn_bond_credit_rates_daily.xlsx", "中债企业债到期收益率(AA):3年")
s_aa = s_aa[s_aa.index >= "2024-11-01"]
df_aa = to_month_end(s_aa)
df_aa.columns = ["ref_month", "value"]
df_aa.insert(0, "indicator_id", "CREDIT_YTM_AA_3Y")
results.append(df_aa)

# --- CGB_3Y → CGB_3Y_YTM (月末值) ---
s_cgb = load_excel_daily(DAILY / "cn_bond_credit_rates_daily.xlsx", "中债国债到期收益率:3年")
s_cgb = s_cgb[s_cgb.index >= "2024-11-01"]
df_cgb = to_month_end(s_cgb)
df_cgb.columns = ["ref_month", "value"]
df_cgb.insert(0, "indicator_id", "CGB_3Y_YTM")
results.append(df_cgb)

# ---------------------------------------------------------------------------
# 2. 专项债派生：SPECIAL_BOND_PROGRESS
# ---------------------------------------------------------------------------

# 读取 SPECIAL_BOND_ISSUE_CUM（月频累计值，亿元）
df_bond = pd.read_excel(MONTHLY / "marco_0316.xlsx", sheet_name="指标")
df_bond["日期"] = pd.to_datetime(df_bond["日期"], errors="coerce")
df_bond = df_bond.dropna(subset=["日期"])
df_bond["ref_month"] = df_bond["日期"].dt.to_period("M").astype(str)
df_bond["cum"] = pd.to_numeric(
    df_bond["中国:发行地方政府债券:按用途划分:发行新增专项债券:累计值"], errors="coerce"
)
df_bond = df_bond[["ref_month", "cum"]].dropna(subset=["cum"])
df_bond = df_bond[df_bond["ref_month"] >= START_MONTH]

# 读取 LOCAL_SPECIAL_BOND_TARGET_ANNUAL（年频目标，万亿元 → 亿元 * 10000）
df_target = pd.read_excel(MONTHLY / "special_bonds_annual.xlsx", sheet_name="指标")
# 跳过元数据行（序号为 NaN 且 日期 为非数字字符串的行）
df_target = df_target[pd.to_numeric(df_target["序号"], errors="coerce").notna()].copy()
df_target["year"] = df_target["日期"].astype(str).str.strip()
df_target["target_yi"] = (
    pd.to_numeric(df_target["中国:政府预期目标:地方专项债"], errors="coerce") * 10000
)  # 万亿元 → 亿元
df_target = df_target[["year", "target_yi"]].dropna()
# 构建 {year_str: target_yi} 映射
target_map = dict(zip(df_target["year"], df_target["target_yi"]))

# 派生
skipped = []
progress_rows = []
for _, row in df_bond.iterrows():
    ref_month = row["ref_month"]
    year = ref_month[:4]
    cum = row["cum"]
    if year not in target_map:
        skipped.append((ref_month, f"年度目标缺失: year={year}"))
        continue
    target = target_map[year]
    if pd.isna(target) or target == 0:
        skipped.append((ref_month, f"年度目标为0或NaN: year={year}"))
        continue
    # SPECIAL_BOND_PROGRESS 统一保存为百分数值（如 90.99），unit 在输出中标记为 %
    progress_rows.append(
        {
            "indicator_id": "SPECIAL_BOND_PROGRESS",
            "ref_month": ref_month,
            "value": (cum / target) * 100,
        }
    )

df_progress = pd.DataFrame(progress_rows)
results.append(df_progress)

# ---------------------------------------------------------------------------
# 3. 合并并输出
# ---------------------------------------------------------------------------

final = pd.concat(results, ignore_index=True)
final = final.sort_values(["indicator_id", "ref_month"]).reset_index(drop=True)
final["value"] = final["value"].apply(lambda v: f"{float(v):.{DECIMAL_PLACES}f}")

# 补充 unit, adjustment, source, data_type
for col, idx in [("unit", 0), ("adjustment", 1), ("source", 2), ("data_type", 3)]:
    final[col] = final["indicator_id"].map(lambda x, i=idx: INDICATOR_META.get(x, ("", "", "", ""))[i])

final = final[["indicator_id", "ref_month", "value", "unit", "adjustment", "source", "data_type"]]

out_path = OUTPUT / "processed_macro_2024_11_latest.csv"
final.to_csv(out_path, index=False)

# ---------------------------------------------------------------------------
# 4. 终端汇总
# ---------------------------------------------------------------------------

print("=" * 60)
print("加工完成")
print("=" * 60)

sources = {
    "BRENT_CRUDE": "data/raw/daily/cross_market.xlsx",
    "XAUUSD": "data/raw/daily/gold.xlsx",
    "FX_CNY_MID": "data/raw/daily/cross_market.xlsx",
    "VIX": "data/raw/daily/cross_market.xlsx",
    "DR007": "data/raw/daily/cn_bond_credit_rates_daily.xlsx",
    "CREDIT_YTM_AA_3Y": "data/raw/daily/cn_bond_credit_rates_daily.xlsx",
    "CGB_3Y_YTM": "data/raw/daily/cn_bond_credit_rates_daily.xlsx",
    "SPECIAL_BOND_PROGRESS": (
        "data/raw/monthly/marco_0316.xlsx + data/raw/monthly/special_bonds_annual.xlsx"
    ),
}
print("\n原始文件来源：")
for ind, src in sources.items():
    print(f"  {ind:<25} <- {src}")

print(f"\n输出文件：{out_path.relative_to(ROOT.parent)}")
print(f"总行数：{len(final)}")

print("\n各指标最新月份：")
for ind, grp in final.groupby("indicator_id"):
    latest = grp["ref_month"].max()
    count = len(grp)
    print(f"  {ind:<25} 最新={latest}  共{count}行")

if skipped:
    print("\n跳过记录（SPECIAL_BOND_PROGRESS）：")
    for ref_month, reason in skipped:
        print(f"  {ref_month}: {reason}")
else:
    print("\n无跳过记录。")
