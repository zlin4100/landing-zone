-- ============================================================
-- Layer 1a-daily: macro_daily -- 宏观日频时序（窄表）
-- 覆盖：需要保留日频原始的宏观指标
--   - DR007（央行流动性锚定）
--   - YIELD_10Y（10年国债日频）
--   - YIELD_30Y（30年国债日频，全天候P0）
--   - T5YIE（美国5年通胀预期日频）
--   - CREDIT_SPREAD_AA（AA信用利差日频）
--   - CREDIT_SPREAD_AA_AAA（AA-AAA等级利差日频）
--   - FX_CNY_MID（人民币中间价日频）
-- 设计要点：
--   ① 日频原始保留，支持审计/复算溯源
--   ② 月均聚合由 ETL 写入 macro_monthly，source_tag='AGG_FROM_DAILY'
--   ③ 与 market_daily 区分：本表存宏观利率/汇率类，
--      market_daily 存股指/波动率/资金流/大宗
-- ============================================================
USE robo_advisor;

CREATE TABLE IF NOT EXISTS macro_daily (
    id               BIGINT        NOT NULL AUTO_INCREMENT,
    indicator_code   VARCHAR(60)   NOT NULL  COMMENT 'FK -> indicator_catalog',
    trade_date       DATE          NOT NULL  COMMENT '交易日/发布日',
    value            DECIMAL(16,6) NULL      COMMENT '指标值',
    created_at       TIMESTAMP     DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    UNIQUE KEY uk_code_date (indicator_code, trade_date),
    INDEX idx_trade_date      (trade_date),
    INDEX idx_indicator_code  (indicator_code),
    CONSTRAINT fk_macro_daily_catalog
        FOREIGN KEY (indicator_code) REFERENCES indicator_catalog(indicator_code)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
  COMMENT='宏观日频时序数据 — Layer 1a-daily（v1.3新增，保留日频原始）';
