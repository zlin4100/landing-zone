-- ============================================================
-- Layer 1a: macro_monthly -- 宏观月频时序（窄表）
-- 覆盖：宏观核心16个（月均聚合值） + 宏观非核心14个 = 30个指标
-- 设计要点：data_version 支持统计局数据修订追踪
-- 注意：DR007/YIELD_30Y/T5YIE/CREDIT_SPREAD等日频指标的
--       月均聚合值也写入本表，日频原始保留在 macro_daily
-- ============================================================
USE robo_advisor;

CREATE TABLE IF NOT EXISTS macro_monthly (
    id               BIGINT        NOT NULL AUTO_INCREMENT,
    indicator_code   VARCHAR(60)   NOT NULL  COMMENT 'FK -> indicator_catalog',
    stat_month       CHAR(7)       NOT NULL  COMMENT '统计月份 YYYY-MM',
    value            DECIMAL(16,6) NULL      COMMENT '指标值（NULL=本月未发布）',
    is_preliminary   TINYINT(1)    DEFAULT 0 COMMENT '1=初值，可能被后续修订',
    data_version     TINYINT       DEFAULT 1 COMMENT '修订版本号，查询取MAX',
    source_tag       VARCHAR(40)   NULL      COMMENT '来源标识, 如 NBS_OFFICIAL / AGG_FROM_DAILY',
    created_at       TIMESTAMP     DEFAULT CURRENT_TIMESTAMP,
    updated_at       TIMESTAMP     DEFAULT CURRENT_TIMESTAMP
                                   ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    UNIQUE KEY uk_code_month_ver (indicator_code, stat_month, data_version),
    INDEX idx_stat_month         (stat_month),
    INDEX idx_indicator_code     (indicator_code),
    CONSTRAINT fk_macro_catalog
        FOREIGN KEY (indicator_code) REFERENCES indicator_catalog(indicator_code)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
  COMMENT='宏观月频时序数据 — Layer 1a（含日频指标的月均聚合值）';
