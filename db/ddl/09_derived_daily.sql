-- ============================================================
-- Layer 1f: derived_daily -- 内部合成特征日频（窄表）
-- 覆盖：由已采购原始序列计算生成的衍生指标
--   - TERM_SPREAD_10Y_1Y = YIELD_10Y - CGB_1Y
--   - TERM_SPREAD_30Y_10Y = YIELD_30Y - YIELD_10Y（可选）
--   - DR007_FUNDING_COST_DAILY（杠杆资金成本逐日计提）
-- 设计要点：
--   ① 非采购项，由 ETL 脚本在 Layer 1 原始数据基础上计算
--   ② 在 indicator_catalog 中登记（category='internal_derived'）
--   ③ 独立建表，与采购原始数据隔离
-- ============================================================
USE robo_advisor;

CREATE TABLE IF NOT EXISTS derived_daily (
    id               BIGINT        NOT NULL AUTO_INCREMENT,
    indicator_code   VARCHAR(60)   NOT NULL  COMMENT 'FK -> indicator_catalog',
    trade_date       DATE          NOT NULL,
    value            DECIMAL(16,6) NULL      COMMENT '合成指标值',
    created_at       TIMESTAMP     DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    UNIQUE KEY uk_code_date (indicator_code, trade_date),
    INDEX idx_trade_date      (trade_date),
    INDEX idx_indicator_code  (indicator_code),
    CONSTRAINT fk_derived_catalog
        FOREIGN KEY (indicator_code) REFERENCES indicator_catalog(indicator_code)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
  COMMENT='内部合成特征日频 — Layer 1f（v1.3新增，非采购项）';
