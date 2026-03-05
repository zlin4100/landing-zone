-- ============================================================
-- 存储过程：构建月度宽表快照
-- 调用方式：CALL proc_build_monthly_snapshot('2026-02');
-- 执行时机：每月16日 ETL Step 4
-- v1.3 变更：新增 macro_daily / derived_daily 聚合来源
-- ============================================================
USE robo_advisor;

DELIMITER $$

CREATE PROCEDURE proc_build_monthly_snapshot(IN p_month CHAR(7))
BEGIN
    -- 月份起止日期（复用变量避免重复 CONCAT）
    DECLARE v_month_start DATE;
    DECLARE v_month_end DATE;
    SET v_month_start = CONCAT(p_month, '-01');
    SET v_month_end = DATE_ADD(v_month_start, INTERVAL 1 MONTH);

    -- 删除已有的当月快照（幂等）
    DELETE FROM macro_snapshot_monthly WHERE snap_month = p_month;

    INSERT INTO macro_snapshot_monthly (
        snap_month,
        cpi_yoy, ppi_yoy, m2_yoy, tsf_stock_yoy,
        lpr_1y, yield_10y, yield_30y_avg, t5yie_avg,
        dr007, credit_spread_aa, credit_spread_aa_aaa,
        pmi_manu, pmi_serv, industry_yoy, gov_expend_cum_yoy, fx_cny_mid,
        retail_sales_yoy, export_yoy, urban_unemployment, xauusd_avg,
        spx_eom, hs300_eom, vix_avg,
        northbound_net_sum, southbound_net_sum,
        brent_avg, iron_ore_dce_avg,
        pboc_rate_event, fomc_rate_event,
        epu_cn, epu_us, epu_global, gpr, gpr_threats, gpr_acts,
        term_spread_10y_1y_eom
    )
    SELECT
        p_month AS snap_month,

        -- ========== 宏观核心 (从 macro_monthly 窄表 pivot) ==========
        MAX(CASE WHEN m.indicator_code = 'CPI_YOY'          THEN m.value END) AS cpi_yoy,
        MAX(CASE WHEN m.indicator_code = 'PPI_YOY'          THEN m.value END) AS ppi_yoy,
        MAX(CASE WHEN m.indicator_code = 'M2_YOY'           THEN m.value END) AS m2_yoy,
        MAX(CASE WHEN m.indicator_code = 'TSF_STOCK_YOY'    THEN m.value END) AS tsf_stock_yoy,
        MAX(CASE WHEN m.indicator_code = 'LPR_1Y'           THEN m.value END) AS lpr_1y,

        -- 日频指标月均（优先从 macro_monthly 取 AGG_FROM_DAILY 值，兜底从 macro_daily 实时聚合）
        COALESCE(
            MAX(CASE WHEN m.indicator_code = 'YIELD_10Y' THEN m.value END),
            (SELECT AVG(md.value) FROM macro_daily md
             WHERE md.indicator_code = 'YIELD_10Y'
               AND md.trade_date >= v_month_start AND md.trade_date < v_month_end)
        ) AS yield_10y,

        -- v1.3 新增: 30Y国债月均
        COALESCE(
            MAX(CASE WHEN m.indicator_code = 'YIELD_30Y' THEN m.value END),
            (SELECT AVG(md.value) FROM macro_daily md
             WHERE md.indicator_code = 'YIELD_30Y'
               AND md.trade_date >= v_month_start AND md.trade_date < v_month_end)
        ) AS yield_30y_avg,

        -- v1.3 新增: T5YIE月均
        COALESCE(
            MAX(CASE WHEN m.indicator_code = 'T5YIE' THEN m.value END),
            (SELECT AVG(md.value) FROM macro_daily md
             WHERE md.indicator_code = 'T5YIE'
               AND md.trade_date >= v_month_start AND md.trade_date < v_month_end)
        ) AS t5yie_avg,

        COALESCE(
            MAX(CASE WHEN m.indicator_code = 'DR007' THEN m.value END),
            (SELECT AVG(md.value) FROM macro_daily md
             WHERE md.indicator_code = 'DR007'
               AND md.trade_date >= v_month_start AND md.trade_date < v_month_end)
        ) AS dr007,

        COALESCE(
            MAX(CASE WHEN m.indicator_code = 'CREDIT_SPREAD_AA' THEN m.value END),
            (SELECT AVG(md.value) FROM macro_daily md
             WHERE md.indicator_code = 'CREDIT_SPREAD_AA'
               AND md.trade_date >= v_month_start AND md.trade_date < v_month_end)
        ) AS credit_spread_aa,

        -- v1.3 新增: AA-AAA等级利差月均
        COALESCE(
            MAX(CASE WHEN m.indicator_code = 'CREDIT_SPREAD_AA_AAA' THEN m.value END),
            (SELECT AVG(md.value) FROM macro_daily md
             WHERE md.indicator_code = 'CREDIT_SPREAD_AA_AAA'
               AND md.trade_date >= v_month_start AND md.trade_date < v_month_end)
        ) AS credit_spread_aa_aaa,

        MAX(CASE WHEN m.indicator_code = 'PMI_MANU'         THEN m.value END) AS pmi_manu,
        MAX(CASE WHEN m.indicator_code = 'PMI_SERV'         THEN m.value END) AS pmi_serv,
        MAX(CASE WHEN m.indicator_code = 'INDUSTRY_YOY'     THEN m.value END) AS industry_yoy,

        -- v1.3 新增: 财政支出累计同比
        MAX(CASE WHEN m.indicator_code = 'GOV_EXPEND_CUMULATIVE_YOY' THEN m.value END) AS gov_expend_cum_yoy,

        COALESCE(
            MAX(CASE WHEN m.indicator_code = 'FX_CNY_MID' THEN m.value END),
            (SELECT AVG(md.value) FROM macro_daily md
             WHERE md.indicator_code = 'FX_CNY_MID'
               AND md.trade_date >= v_month_start AND md.trade_date < v_month_end)
        ) AS fx_cny_mid,

        -- ========== 宏观非核心 ==========
        MAX(CASE WHEN m.indicator_code = 'RETAIL_SALES_YOY'  THEN m.value END) AS retail_sales_yoy,
        MAX(CASE WHEN m.indicator_code = 'EXPORT_YOY'        THEN m.value END) AS export_yoy,
        MAX(CASE WHEN m.indicator_code = 'URBAN_UNEMPLOYMENT' THEN m.value END) AS urban_unemployment,

        -- ========== 行情月度聚合 (从 market_daily 聚合) ==========
        -- 黄金月均价
        (SELECT AVG(mk.close_price) FROM market_daily mk
         WHERE mk.ticker = 'XAUUSD'
           AND mk.trade_date >= v_month_start AND mk.trade_date < v_month_end
        ) AS xauusd_avg,

        -- 标普500月末收盘
        (SELECT mk.close_price FROM market_daily mk
         WHERE mk.ticker = 'SPX'
           AND mk.trade_date >= v_month_start AND mk.trade_date < v_month_end
         ORDER BY mk.trade_date DESC LIMIT 1
        ) AS spx_eom,

        -- 沪深300月末收盘
        (SELECT mk.close_price FROM market_daily mk
         WHERE mk.ticker = '000300.SH'
           AND mk.trade_date >= v_month_start AND mk.trade_date < v_month_end
         ORDER BY mk.trade_date DESC LIMIT 1
        ) AS hs300_eom,

        -- VIX月均
        (SELECT AVG(mk.close_price) FROM market_daily mk
         WHERE mk.ticker = 'VIX'
           AND mk.trade_date >= v_month_start AND mk.trade_date < v_month_end
        ) AS vix_avg,

        -- 北向资金月度净流入
        (SELECT SUM(mk.net_flow) FROM market_daily mk
         WHERE mk.ticker = 'NORTHBOUND_NET'
           AND mk.trade_date >= v_month_start AND mk.trade_date < v_month_end
        ) AS northbound_net_sum,

        -- v1.3 新增: 南向资金月度净流入
        (SELECT SUM(mk.net_flow) FROM market_daily mk
         WHERE mk.ticker = 'SOUTHBOUND_NET'
           AND mk.trade_date >= v_month_start AND mk.trade_date < v_month_end
        ) AS southbound_net_sum,

        -- 布伦特原油月均
        (SELECT AVG(mk.close_price) FROM market_daily mk
         WHERE mk.ticker = 'BRENT_CRUDE'
           AND mk.trade_date >= v_month_start AND mk.trade_date < v_month_end
        ) AS brent_avg,

        -- v1.3 新增: 铁矿石月均
        (SELECT AVG(mk.close_price) FROM market_daily mk
         WHERE mk.ticker = 'IRON_ORE_DCE'
           AND mk.trade_date >= v_month_start AND mk.trade_date < v_month_end
        ) AS iron_ore_dce_avg,

        -- ========== 央行事件文本拼接 ==========
        (SELECT GROUP_CONCAT(CONCAT(cb.event_type, '(', cb.change_bp, 'bp)') SEPARATOR '; ')
         FROM central_bank_events cb
         WHERE cb.institution = 'PBOC'
           AND cb.event_date >= v_month_start AND cb.event_date < v_month_end
        ) AS pboc_rate_event,

        (SELECT GROUP_CONCAT(CONCAT(cb.event_type, '(', cb.change_bp, 'bp)') SEPARATOR '; ')
         FROM central_bank_events cb
         WHERE cb.institution = 'FOMC'
           AND cb.event_date >= v_month_start AND cb.event_date < v_month_end
        ) AS fomc_rate_event,

        -- ========== 新闻政策指数 ==========
        MAX(CASE WHEN m.indicator_code = 'EPU_CN'     THEN m.value END) AS epu_cn,
        MAX(CASE WHEN m.indicator_code = 'EPU_US'     THEN m.value END) AS epu_us,
        MAX(CASE WHEN m.indicator_code = 'EPU_GLOBAL' THEN m.value END) AS epu_global,
        MAX(CASE WHEN m.indicator_code = 'GPR'        THEN m.value END) AS gpr,
        MAX(CASE WHEN m.indicator_code = 'GPR_THREATS' THEN m.value END) AS gpr_threats,
        MAX(CASE WHEN m.indicator_code = 'GPR_ACTS'    THEN m.value END) AS gpr_acts,

        -- ========== 内部合成特征月末值 (从 derived_daily 取月末) ==========
        (SELECT dd.value FROM derived_daily dd
         WHERE dd.indicator_code = 'TERM_SPREAD_10Y_1Y'
           AND dd.trade_date >= v_month_start AND dd.trade_date < v_month_end
         ORDER BY dd.trade_date DESC LIMIT 1
        ) AS term_spread_10y_1y_eom

    FROM macro_monthly m
    WHERE m.stat_month = p_month
      AND m.data_version = (
          SELECT MAX(m2.data_version)
          FROM macro_monthly m2
          WHERE m2.indicator_code = m.indicator_code
            AND m2.stat_month = m.stat_month
      );
END$$

DELIMITER ;
