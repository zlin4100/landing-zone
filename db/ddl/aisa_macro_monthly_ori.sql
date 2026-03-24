CREATE TABLE `aisa_macro_monthly_ori` (
  `id` bigint NOT NULL AUTO_INCREMENT COMMENT '自增主键',
  `indicator_code` varchar(60) COLLATE utf8mb4_bin DEFAULT NULL COMMENT '指标代码',
  `stat_month` date DEFAULT NULL COMMENT '统计月份',
  `indicator_value` decimal(18,6) DEFAULT NULL COMMENT '指标数值',
  `is_preliminary` tinyint DEFAULT NULL COMMENT '初值标志',
  `data_version` varchar(50) COLLATE utf8mb4_bin DEFAULT NULL COMMENT '数据修订版本号',
  `source_tag` varchar(50) COLLATE utf8mb4_bin DEFAULT NULL COMMENT '来源标志',
  `created_by` varchar(50) COLLATE utf8mb4_bin DEFAULT NULL COMMENT '创建人',
  `created_time` datetime DEFAULT NULL COMMENT '创建时间',
  `updated_by` varchar(50) COLLATE utf8mb4_bin DEFAULT NULL COMMENT '修改人',
  `updated_time` datetime DEFAULT NULL COMMENT '修改时间',
  PRIMARY KEY (`id`),
  UNIQUE KEY `uidx_aisa_macro_monthly_ori_5` (`indicator_code`,`stat_month`,`data_version`),
  KEY `idx_stat_month` (`stat_month`),
  KEY `idx_indicator_code` (`indicator_code`)
) ENGINE=InnoDB AUTO_INCREMENT=1878164 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_bin COMMENT='aisa宏观月频时序表';
