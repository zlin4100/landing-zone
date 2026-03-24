CREATE TABLE `aisa_indicator` (
  `id` bigint NOT NULL AUTO_INCREMENT COMMENT '自增主键',
  `indicator_code` varchar(60) COLLATE utf8mb4_bin DEFAULT NULL COMMENT '指标代码',
  `indicator_name` varchar(120) COLLATE utf8mb4_bin DEFAULT NULL COMMENT '指标中文名',
  `category` enum('macro_core','macro_secondary','market','quant','news_policy') COLLATE utf8mb4_bin DEFAULT NULL COMMENT '指标类型枚举',
  `data_source` varchar(80) COLLATE utf8mb4_bin DEFAULT NULL COMMENT '数据来源',
  `frequency` enum('daily','weekly','monthly','quarterly','event') COLLATE utf8mb4_bin DEFAULT NULL COMMENT '更新频率枚举',
  `value_type` enum('yoy','mom','qoq','level','cumulative_yoy','index','rate') COLLATE utf8mb4_bin DEFAULT NULL COMMENT '数值类型枚举',
  `created_by` varchar(50) COLLATE utf8mb4_bin DEFAULT NULL COMMENT '创建人',
  `created_time` datetime DEFAULT NULL COMMENT '创建时间',
  `updated_by` varchar(50) COLLATE utf8mb4_bin DEFAULT NULL COMMENT '修改人',
  `updated_time` datetime DEFAULT NULL COMMENT '修改时间',
  PRIMARY KEY (`id`),
  KEY `idx_indicator_code` (`indicator_code`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_bin COMMENT='aisa指标目录表';
