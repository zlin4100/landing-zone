-- ============================================================
-- Layer 0: indicator_catalog -- 指标目录/数据字典
-- 作用：① 防脏数据写入（外键约束）
--       ② 给 LLM 提供语义上下文（联表查询）
--       ③ 管理指标生命周期（is_active 字段）
--       ④ 登记内部合成特征（data_source='INTERNAL_CALC'）
-- ============================================================
USE robo_advisor;

CREATE TABLE IF NOT EXISTS indicator_catalog (
    indicator_code   VARCHAR(60)   NOT NULL  COMMENT '指标代码, 如 CPI_YOY',
    indicator_name   VARCHAR(120)  NOT NULL  COMMENT '中文名称',
    category         ENUM(
                       'macro_core',
                       'macro_secondary',
                       'market',
                       'quant',
                       'news_policy',
                       'internal_derived'
                     )             NOT NULL,
    data_source      VARCHAR(80)   NOT NULL  COMMENT '数据来源, 如 NBS/PBOC/Wind/INTERNAL_CALC',
    frequency        ENUM('daily','weekly','monthly','quarterly','event')
                                   NOT NULL,
    value_type       ENUM('yoy','mom','qoq','qoq_sa','level','cumulative_yoy','index','rate','spread')
                                   NOT NULL  COMMENT '调整方式',
    unit             VARCHAR(40)   NULL      COMMENT '单位, 如 %/点/USD/bp',
    history_window   VARCHAR(40)   NULL      COMMENT '近10年/近5年 等',
    target_table     VARCHAR(60)   NOT NULL  COMMENT '实际存储的 Layer 1 表名',
    is_active        TINYINT(1)    DEFAULT 1 COMMENT '0=已停用，历史数据保留',
    notes            TEXT          NULL      COMMENT '业务含义/公式说明（供LLM读取）',
    updated_at       TIMESTAMP     DEFAULT CURRENT_TIMESTAMP
                                   ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (indicator_code)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
  COMMENT='指标目录/数据字典 — Layer 0';
