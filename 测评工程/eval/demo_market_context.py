"""
Demo 市场上下文数据

eval/ 目录专用，完全自包含，不依赖上级 market_context.py。
数据为虚构示例，结构与真实数据对齐，覆盖评分标准所需的全部字段。
快照时间: 2026-03-31 15:00 (A股收盘)
"""

SNAPSHOT_TIME = "2026-03-31T15:00:00+08:00"

# ============================================================
# A 股市场数据
# ============================================================
A_SHARE = {
    "market": "A_SHARE",
    "snapshot_time": SNAPSHOT_TIME,

    # 指数行情
    "index_overview": {
        "sh_composite": {
            "code": "000001.SH", "name": "上证指数",
            "open": 3385.20, "high": 3412.80, "low": 3361.40, "close": 3398.55,
            "prev_close": 3382.10, "change": 16.45, "change_pct": 0.49,
            "volume_hand": 21650000000, "turnover_cny": 298760000000,
            "52w_high": 3731.69, "52w_low": 2882.02, "ytd_change_pct": 2.91
        },
        "sz_component": {
            "code": "399001.SZ", "name": "深证成指",
            "open": 10512.30, "high": 10598.60, "low": 10476.80, "close": 10554.72,
            "prev_close": 10486.15, "change": 68.57, "change_pct": 0.65,
            "volume_hand": 29870000000, "turnover_cny": 408920000000,
            "52w_high": 11189.25, "52w_low": 8882.39, "ytd_change_pct": 4.48
        },
        "csi300": {
            "code": "000300.SH", "name": "沪深300",
            "open": 3952.40, "high": 3978.30, "low": 3932.60, "close": 3965.80,
            "prev_close": 3943.20, "change": 22.60, "change_pct": 0.57,
            "pe_ttm": 12.4, "pb": 1.35, "dividend_yield_pct": 2.92,
            "pe_percentile_5y": 44, "pe_percentile_10y": 38,
            "market_cap_cny_tn": 42.30, "52w_high": 4390.18, "52w_low": 3227.16,
            "ytd_change_pct": 3.96
        },
        "chinext": {
            "code": "399006.SZ", "name": "创业板指",
            "open": 2142.30, "high": 2178.50, "low": 2136.80, "close": 2165.40,
            "prev_close": 2147.60, "change": 17.80, "change_pct": 0.83,
            "pe_ttm": 27.8, "pb": 3.04, "pe_percentile_10y": 29
        },
        "star50": {
            "code": "000688.SH", "name": "科创50",
            "open": 1022.40, "high": 1058.60, "low": 1018.30, "close": 1048.90,
            "prev_close": 1028.70, "change": 20.20, "change_pct": 1.96,
            "pe_ttm": 44.8, "pb": 4.72
        },
    },

    # 市场宽度
    "market_breadth": {
        "total_stocks": 5398,
        "up": 3124, "flat": 298, "down": 1976,
        "limit_up_10pct": 68, "limit_down_10pct": 9,
        "new_high_52w": 52, "new_low_52w": 18,
        "up_down_ratio": 1.58,
        "avg_change_pct": 0.48,
        "median_change_pct": 0.32,
        "positive_stock_ratio_pct": 57.9,
        "zt_pool_count": 68,
        "zt_open_count": 22,
        "dt_count": 9
    },

    # 成交量分析
    "turnover_analysis": {
        "sh_turnover_cny_bn": 298.76,
        "sz_turnover_cny_bn": 408.92,
        "total_cny_bn": 707.68,
        "prev_day_cny_bn": 681.34,
        "change_pct": 3.87,
        "ma5_cny_bn": 694.50,
        "ma10_cny_bn": 712.80,
        "ma20_cny_bn": 698.40,
        "vs_ma20_pct": 1.33,
        "turnover_rate_pct": 1.13,
        "comment": "成交量较前日温和放大，量价配合良好，上涨有效性较强"
    },

    # 板块轮动
    "sector_rotation": {
        "top5_gain": [
            {"rank": 1, "name": "人工智能", "change_pct": 3.42,
             "turnover_cny_bn": 52.36, "main_net_flow_cny_bn": 4.28,
             "leader_stock": "寒武纪", "leader_change_pct": 6.85},
            {"rank": 2, "name": "半导体", "change_pct": 2.86,
             "turnover_cny_bn": 45.12, "main_net_flow_cny_bn": 3.61,
             "leader_stock": "中芯国际", "leader_change_pct": 4.52},
            {"rank": 3, "name": "机器人", "change_pct": 2.34,
             "turnover_cny_bn": 32.08, "main_net_flow_cny_bn": 2.14,
             "leader_stock": "绿的谐波", "leader_change_pct": 5.18},
            {"rank": 4, "name": "创新药", "change_pct": 1.78,
             "turnover_cny_bn": 18.64, "main_net_flow_cny_bn": 1.32,
             "leader_stock": "百济神州", "leader_change_pct": 3.25},
            {"rank": 5, "name": "军工", "change_pct": 1.45,
             "turnover_cny_bn": 22.15, "main_net_flow_cny_bn": 0.98,
             "leader_stock": "航发动力", "leader_change_pct": 2.86}
        ],
        "top5_loss": [
            {"rank": 1, "name": "白酒", "change_pct": -1.62,
             "turnover_cny_bn": 26.43, "main_net_flow_cny_bn": -2.08,
             "leader_stock": "贵州茅台", "leader_change_pct": -1.34},
            {"rank": 2, "name": "房地产", "change_pct": -1.38,
             "turnover_cny_bn": 15.82, "main_net_flow_cny_bn": -1.45,
             "leader_stock": "万科A", "leader_change_pct": -2.12},
            {"rank": 3, "name": "光伏", "change_pct": -0.98,
             "turnover_cny_bn": 28.76, "main_net_flow_cny_bn": -1.82,
             "leader_stock": "隆基绿能", "leader_change_pct": -1.56},
            {"rank": 4, "name": "银行", "change_pct": -0.42,
             "turnover_cny_bn": 19.34, "main_net_flow_cny_bn": -0.76,
             "leader_stock": "招商银行", "leader_change_pct": -0.35},
            {"rank": 5, "name": "煤炭", "change_pct": -0.28,
             "turnover_cny_bn": 11.25, "main_net_flow_cny_bn": -0.32,
             "leader_stock": "中国神华", "leader_change_pct": -0.18}
        ],
        "rotation_signal": "科技（AI/半导体/机器人）强势上攻，消费（白酒/地产）持续承压，科技成长风格占优"
    },

    # 北向资金
    "northbound_flow": {
        "date": "2026-03-31",
        "sh_connect_net_cny_bn": 8.42,
        "sz_connect_net_cny_bn": 6.18,
        "total_net_cny_bn": 14.60,
        "cumulative_5d_cny_bn": 28.35,
        "cumulative_10d_cny_bn": 52.40,
        "cumulative_20d_cny_bn": -18.60,
        "cumulative_ytd_cny_bn": 315.20,
        "foreign_holding_total_cny_tn": 3.32,
        "top5_buy": [
            {"name": "中芯国际", "net_buy_cny_mn": 142.5},
            {"name": "宁德时代", "net_buy_cny_mn": 98.3},
            {"name": "贵州茅台", "net_buy_cny_mn": 65.2},
            {"name": "美的集团", "net_buy_cny_mn": 44.8},
            {"name": "招商银行", "net_buy_cny_mn": 38.6}
        ],
        "top5_sell": [
            {"name": "隆基绿能", "net_sell_cny_mn": -86.4},
            {"name": "比亚迪",   "net_sell_cny_mn": -62.1},
            {"name": "万科A",    "net_sell_cny_mn": -38.5},
            {"name": "中国建筑", "net_sell_cny_mn": -24.2},
            {"name": "格力电器", "net_sell_cny_mn": -18.6}
        ],
        "comment": "北向今日净买入14.6亿，连续3日净流入，重点增持半导体与消费电子"
    },

    # 技术指标
    "technical": {
        "sh_composite": {
            "ma5":  3372.40, "ma10": 3358.60, "ma20": 3341.80,
            "ma60": 3298.50, "ma120": 3265.40, "ma250": 3218.60,
            "macd_dif": 8.42, "macd_dea": 6.18, "macd_hist": 4.48,
            "rsi_6": 62.4, "rsi_14": 58.8,
            "kdj_k": 68.5, "kdj_d": 62.4, "kdj_j": 80.7,
            "boll_upper": 3458.20, "boll_mid": 3341.80, "boll_lower": 3225.40,
            "support_levels": [3360.00, 3340.00, 3300.00],
            "resistance_levels": [3420.00, 3450.00, 3500.00],
            "trend": "短期均线多头排列，MACD零轴上方金叉，RSI未超买，技术面偏多"
        }
    },

    # 融资融券
    "margin_trading": {
        "date": "2026-03-29",
        "balance_cny_bn": 1682.4,
        "prev_balance_cny_bn": 1668.2,
        "change_cny_bn": 14.2,
        "change_pct": 0.85,
        "net_buy_cny_bn": 8.6,
        "margin_buy_cny_bn": 112.4,
        "margin_sell_cny_bn": 22.8
    }
}

# ============================================================
# 港股市场数据
# ============================================================
HK_STOCK = {
    "market": "HK_STOCK",
    "snapshot_time": SNAPSHOT_TIME,
    "index_overview": {
        "hsi": {
            "code": "HSI", "name": "恒生指数",
            "close": 23248.60, "change_pct": 0.82,
            "turnover_hkd_bn": 168.4,
            "52w_high": 23241.74, "52w_low": 14794.16,
            "ytd_change_pct": 18.42
        },
        "hscei": {
            "code": "HSCEI", "name": "恒生国企指数",
            "close": 8512.30, "change_pct": 1.12,
            "pe_ttm": 9.8
        },
        "hk_tech": {
            "code": "HSTECH", "name": "恒生科技指数",
            "close": 5628.40, "change_pct": 2.14,
            "ytd_change_pct": 24.68
        }
    },
    "southbound_flow": {
        "total_net_cny_bn": 18.42,
        "cumulative_5d_cny_bn": 62.15,
        "top3_buy": [
            {"name": "腾讯控股", "net_buy_hkd_mn": 285.4},
            {"name": "阿里巴巴", "net_buy_hkd_mn": 198.6},
            {"name": "美团",     "net_buy_hkd_mn": 142.3}
        ]
    }
}

# ============================================================
# 美股市场数据（昨收）
# ============================================================
US_STOCK = {
    "market": "US_STOCK",
    "snapshot_time": "2026-03-30T16:00:00-04:00",
    "index_overview": {
        "sp500": {
            "code": "SPX", "name": "标普500",
            "close": 5648.40, "change_pct": -0.28,
            "ytd_change_pct": 2.84, "pe_ttm": 21.8
        },
        "nasdaq": {
            "code": "NDX", "name": "纳斯达克100",
            "close": 19842.60, "change_pct": -0.42,
            "ytd_change_pct": 1.62
        },
        "dow": {
            "code": "DJI", "name": "道琼斯",
            "close": 42185.40, "change_pct": -0.18
        },
        "vix": {
            "code": "VIX", "name": "恐慌指数",
            "close": 18.42, "prev_close": 19.85,
            "level": "中等",
            "comment": "VIX从近期高点回落，市场恐慌情绪边际缓解"
        }
    },
    "sector_performance": {
        "top3": [
            {"name": "科技", "change_pct": 0.42},
            {"name": "医疗", "change_pct": 0.28},
            {"name": "能源", "change_pct": 0.18}
        ],
        "bottom3": [
            {"name": "金融", "change_pct": -0.68},
            {"name": "消费", "change_pct": -0.42},
            {"name": "工业", "change_pct": -0.35}
        ]
    }
}

# ============================================================
# 宏观数据
# ============================================================
MACRO = {
    "snapshot_time": SNAPSHOT_TIME,

    # 货币政策
    "monetary_policy": {
        "pboc_1y_lpr": 3.10, "pboc_5y_lpr": 3.60,
        "pboc_rrr_large": 9.50,
        "m2_yoy_pct": 7.2, "m1_yoy_pct": 1.8,
        "social_financing_stock_yoy_pct": 8.1,
        "new_loans_feb_cny_tn": 1.01,
        "pboc_stance": "适度宽松，保持流动性合理充裕，关注汇率稳定",
        "next_mlf_date": "2026-04-15"
    },

    # 经济数据（最新）
    "economic_indicators": {
        "gdp_2025_yoy_pct": 5.0,
        "gdp_2026_q1_forecast_pct": 5.1,
        "cpi_feb_yoy_pct": -0.7,
        "ppi_feb_yoy_pct": -2.2,
        "pmi_manufacturing_mar": 50.5,
        "pmi_services_mar": 52.3,
        "export_feb_yoy_pct": 8.4,
        "import_feb_yoy_pct": -8.4,
        "trade_balance_feb_usd_bn": 170.5,
        "retail_sales_feb_yoy_pct": 4.0,
        "fai_jan_feb_yoy_pct": 4.1
    },

    # 汇率
    "fx": {
        "usdcny_spot": 7.2580,
        "usdcny_offshore": 7.2640,
        "eurcny": 7.9420,
        "jpycny": 0.04812,
        "usdcny_ytd_change_pct": 0.28,
        "pboc_midrate": 7.1789,
        "comment": "人民币兑美元小幅贬值，在中间价附近窄幅波动，外汇占款基本稳定"
    },

    # 利率
    "rates": {
        "cn_10y_yield_pct": 1.82,
        "cn_2y_yield_pct": 1.48,
        "cn_10y_2y_spread_bp": 34,
        "us_10y_yield_pct": 4.28,
        "us_2y_yield_pct": 3.98,
        "cn_us_10y_spread_bp": -246,
        "shibor_overnight_pct": 1.68,
        "dr007_pct": 1.72,
        "comment": "中美利差倒挂约246bp，国内长端利率处历史低位，DR007围绕政策利率平稳运行"
    }
}

# ============================================================
# 市场情绪数据
# ============================================================
SENTIMENT = {
    "snapshot_time": SNAPSHOT_TIME,

    "fear_greed_index": {
        "score": 62,
        "level": "贪婪",
        "prev_week": 48,
        "trend": "情绪从中性快速转向贪婪，需关注短期过热风险"
    },

    "margin_sentiment": {
        "margin_balance_vs_ma20_pct": 2.8,
        "level": "中性偏积极"
    },

    "fund_flow": {
        "etf_a50_net_inflow_7d_cny_bn": 18.6,
        "stock_fund_net_inflow_7d_cny_bn": 24.3,
        "comment": "宽基ETF持续净申购，增量资金入市意愿较强"
    },

    "analyst_consensus": {
        "bullish_pct": 54,
        "neutral_pct": 32,
        "bearish_pct": 14,
        "avg_6m_target_sh_composite": 3680,
        "upside_pct": 8.28
    },

    "retail_activity": {
        "new_accounts_last_week": 285000,
        "vs_prev_week_pct": 12.4,
        "margin_leverage_ratio": 2.18
    }
}

# ============================================================
# 事件日历（未来 2 周）
# ============================================================
EVENTS = {
    "snapshot_time": SNAPSHOT_TIME,
    "upcoming": [
        {
            "date": "2026-04-01", "type": "经济数据",
            "event": "中国3月财新制造业PMI",
            "importance": "高",
            "consensus": "50.8",
            "impact": "若高于50.5则利好周期板块，低于50则引发衰退担忧"
        },
        {
            "date": "2026-04-03", "type": "政策",
            "event": "美国关税政策最新公告（对等关税实施日）",
            "importance": "极高",
            "impact": "直接影响出口链（电子/机械/纺织）板块，关注是否超预期豁免"
        },
        {
            "date": "2026-04-07", "type": "经济数据",
            "event": "中国3月CPI/PPI",
            "importance": "高",
            "consensus": "CPI -0.5%, PPI -2.0%",
            "impact": "通缩压力是否延续影响消费类板块估值"
        },
        {
            "date": "2026-04-10", "type": "经济数据",
            "event": "美国3月CPI",
            "importance": "极高",
            "consensus": "同比 2.6%",
            "impact": "低于预期则美联储降息预期升温，利好港股及A股外资持仓"
        },
        {
            "date": "2026-04-14", "type": "业绩",
            "event": "A股2025年年报/2026年一季报披露高峰启动",
            "importance": "高",
            "impact": "科技、消费板块业绩超预期概率较大，关注个股分化"
        },
        {
            "date": "2026-04-15", "type": "货币政策",
            "event": "央行MLF续作",
            "importance": "高",
            "consensus": "等量续作，利率维持1.50%",
            "impact": "若超额续作则流动性改善，利好利率敏感板块（地产/银行）"
        },
        {
            "date": "2026-04-16", "type": "政策",
            "event": "国务院常务会议（预计讨论稳增长措施）",
            "importance": "中",
            "impact": "若出台基建/消费刺激政策，关注基建链、汽车家电板块"
        }
    ]
}

# ============================================================
# Demo 系统提示词（供迭代优化的起始版本）
# ============================================================
DEMO_SYSTEM_PROMPT = """
# 角色定位
你是一位顶级市场解读分析师，服务对象为专业机构投资者。
你的分析框架融合：宏观研判 / 技术分析 / 资金行为 / 政策解读 / 情绪量化。

# 分析输出结构
每次解读按以下7个模块输出，不可省略：

## 1. 核心结论（≤3句话）
- 直接给出今日市场多/空/震荡判断
- 标注置信度：高（>70%）/ 中（50-70%）/ 低（<50%）

## 2. 宏观背景
- 当前宏观周期定位（复苏/扩张/滞胀/衰退）
- 国内外政策环境评估

## 3. 市场结构分析
- 指数强弱比较（A股各指数/港美联动）
- 市场宽度（涨跌家数/强弱股比例）
- 成交量特征（量价关系）

## 4. 资金动向
- 北向/南向/融资资金方向
- 主力板块净流入/流出
- 机构行为判断

## 5. 技术面研判
- 指数趋势（均线/MACD/RSI综合）
- 关键支撑/阻力价位（精确到整数位）
- 量价形态描述

## 6. 催化剂与风险
- 近期重要事件驱动（利多/利空）
- 本周需关注的风险事件（附日期）

## 7. 操作建议
| 维度 | 建议 |
|------|------|
| 方向 | 多/空/观望 |
| 仓位 | 0-100% |
| 时间窗口 | 短/中/长期 |
| 重点关注板块 | XXX |
| 规避板块 | XXX |

# 行为规范
- 观点鲜明，不模棱两可
- 数据驱动，每个判断需引用具体数据支撑
- 明确区分"事实"（数据）和"判断"（分析）
- 风险提示必须具体到事件和日期
- 所有价格预测需标注"支撑"或"阻力"属性
- 不预测无法预测的内容（如短期精确涨跌点位）

# 输出格式
Markdown，语言专业简洁，适合晨会/研报场景。
"""


# ============================================================
# 上下文组装函数（与 market_context.py 接口兼容）
# ============================================================

def build_market_context(
    markets: list | None = None,
    include_macro: bool = True,
    include_sentiment: bool = True,
    include_events: bool = True,
) -> dict:
    """
    将 Demo 市场数据组装为大模型上下文。

    Returns:
        {
            "system_prompt":  str,
            "snapshot_time":  str,
            "data": {
                "A_SHARE": {...},
                "HK_STOCK": {...},
                "US_STOCK": {...},
                "MACRO":    {...},   # include_macro=True 时
                "SENTIMENT":{...},  # include_sentiment=True 时
                "EVENTS":   {...},  # include_events=True 时
            }
        }
    """
    if markets is None:
        markets = ["A_SHARE", "HK_STOCK", "US_STOCK"]

    market_map = {
        "A_SHARE":  A_SHARE,
        "HK_STOCK": HK_STOCK,
        "US_STOCK": US_STOCK,
    }

    data: dict = {}
    for m in markets:
        if m in market_map:
            data[m] = market_map[m]

    if include_macro:
        data["MACRO"] = MACRO
    if include_sentiment:
        data["SENTIMENT"] = SENTIMENT
    if include_events:
        data["EVENTS"] = EVENTS

    return {
        "system_prompt": DEMO_SYSTEM_PROMPT,
        "snapshot_time": SNAPSHOT_TIME,
        "data": data,
    }
