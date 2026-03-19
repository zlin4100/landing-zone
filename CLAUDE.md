# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

智能投顾 3.0 数据落库管道（landing-zone）。MySQL 数据库 + Python ETL，负责外部数据采购入库、月频聚合、为 LLM 月报和量化建模提供数据。

## Tech Stack

- **Python 3.11+** with pandas, numpy, sqlalchemy, pymysql, openpyxl
- **MySQL 8.0+** (database: `robo_advisor`)
- **Linter**: ruff (line-length=100)
- **Tests**: pytest (testpaths: `tests/`)
- **Package management**: pip with pyproject.toml (editable install)

## Project Structure

```
db/
  ddl/          # DDL scripts (numbered 00-09, executed in order)
  seed/         # Seed data (indicator_catalog_seed.sql)
  procedures/   # Stored procedures
  init.sh       # One-shot DB initialization script
src/
  etl/          # ETL loaders per data source/frequency
  aggregation/  # Snapshot builder, covariance matrix
  quality/      # Data quality checks (completeness, outliers)
  utils/        # DB connection helpers
  models/       # (reserved for ORM models)
data/raw/       # Raw data files (committed to git, organized by frequency)
  monthly/      # 月频/季频原始文件（宏观核心、非核心、基准序列、金价）
  daily/        # 日频原始文件（利率、汇率、信用利差、行情、量化建模）
  event/        # 事件驱动数据（央行事件日历，不定期更新）
  news/         # 新闻文本与情绪指数（日频/实时）
  deprecated/   # ⛔ 废弃文件，不参与任何 ETL 处理
config/         # Settings (settings.toml is gitignored, use settings.example.toml)
docs/           # Design docs and procurement lists
logs/           # Log files (gitignored)
```

## Database Architecture (3 layers)

- **Layer 0**: `indicator_catalog` — all indicator metadata (single source of truth)
- **Layer 1**: Narrow tables by frequency/type
  - `macro_monthly` — monthly macro (30 indicators, incl. daily→monthly aggregates)
  - `macro_daily` — daily macro (DR007, CGB_10Y, FX, BRENT, etc.)
  - `market_daily` — daily market (VIX and display indices)
  - `quant_daily` — quant modeling (CSI300, CSI300_TR, AU9999, NHCI)
  - `central_bank_events` — event-driven policy data
  - `news_raw` — raw news text for RAG
  - `derived_daily` — internal computed features (term spreads, funding cost)
- **Layer 2**: `macro_snapshot_monthly` — wide table (~35 columns, 1 row = 1 month snapshot for LLM consumption)

## Raw Data File Index

指标代码 → 文件、Choice ID、数据范围的完整对照表见 **[data/raw/CLAUDE.md](data/raw/CLAUDE.md)**。

## Key Conventions

- All indicator codes must exist in `indicator_catalog` (foreign key enforced)
- Internal derived features use `category='internal_derived'`, `data_source='INTERNAL_CALC'`
- Daily indicators aggregated to monthly: `source_tag='AGG_FROM_DAILY'`
- Data revisions: append new `data_version` row, never overwrite; query with `MAX(data_version)`
- File naming: `{batch}_{YYYYMMDD}.xlsx`（`YYYYMMDD` 为导出日期，非数据截止日期）
- 所有原始数据均通过 **Choice 终端**导出；指标与文件的对应关系见 `docs/数据采集进度.md`
- NULL means "not yet published" — never fill with 0 or mean

## Common Commands

```bash
# Initialize database
bash db/init.sh

# Run ETL — monthly
python -m src.etl.load_macro_monthly --file data/raw/monthly/nbs_macro_core_20260305.xlsx
python -m src.etl.load_macro_monthly --file data/raw/monthly/macro_20260310.xlsx
python -m src.etl.load_macro_monthly --file data/raw/monthly/marco_meeting_318.xlsx
python -m src.etl.load_macro_monthly --file data/raw/monthly/marco_0316.xlsx
python -m src.etl.load_macro_monthly --file data/raw/monthly/growth.xlsx
python -m src.etl.load_macro_monthly --file data/raw/monthly/GDP.xlsx
python -m src.etl.load_macro_monthly --file data/raw/monthly/housing_318.xlsx
python -m src.etl.load_macro_monthly --file data/raw/monthly/cash_mmf_yld.xlsx
python -m src.etl.load_macro_monthly --file data/raw/monthly/special_bonds_annual.xlsx

# Run ETL — daily
python -m src.etl.load_macro_daily   --file data/raw/daily/cn_bond_credit_rates_daily.xlsx
python -m src.etl.load_macro_daily   --file data/raw/daily/bond_CGB_1y.xlsx
python -m src.etl.load_macro_daily   --file data/raw/daily/cross_market.xlsx
python -m src.etl.load_macro_daily   --file data/raw/daily/gold.xlsx
python -m src.etl.load_market_daily  --file data/raw/daily/cross_market.xlsx
python -m src.etl.load_quant_daily   --file data/raw/daily/K线导出_H00300_日线数据.xlsx
python -m src.etl.load_quant_daily   --file data/raw/daily/K线导出_000300_日线数据.xlsx
python -m src.etl.load_quant_daily   --file data/raw/daily/K线导出_AU9999_日线数据.xlsx
python -m src.etl.load_quant_daily   --file data/raw/daily/K线导出_NHCI_日线数据.xlsx

# Run ETL — derived
python -m src.etl.load_derived_daily --month 2026-02

# Build monthly snapshot
python -m src.aggregation.build_snapshot --month 2026-02

# Compute covariance matrix
python -m src.aggregation.cov_matrix --start 2016-01-01 --end 2026-01-01

# Lint
ruff check src/ tests/

# Test
pytest
pytest tests/test_foo.py::test_bar   # single test
```

## Monthly SOP

```
1. 统计局数据发布后（通常次月15日前）
2. Choice 导出 → monthly/nbs_macro_core_YYYYMMDD.xlsx（NBS 5指标）
                → monthly/macro_YYYYMMDD.xlsx（PBOC/MOF 3指标）
                → monthly/marco_YYYYMMDD.xlsx（PBOC/NBS/海关 5指标）
3. Choice 导出 → monthly/growth.xlsx（8指标，更新至月末）
4. Choice 导出 → daily/cn_bond_credit_rates_daily.xlsx（5指标，更新至月末）
                → daily/bond_CGB_1y.xlsx · cross_market.xlsx · gold.xlsx · K线导出_*.xlsx
5. 运行全部 ETL → load_derived_daily → build_snapshot --month YYYY-MM
```

## Environment

- DB connection: `DATABASE_URL` env var or `config/settings.toml`
- Default: `mysql+pymysql://root:@localhost:3306/robo_advisor?charset=utf8mb4`
