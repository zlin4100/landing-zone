# CLAUDE.md

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
data/raw/       # Raw data files (committed to git, organized by source)
  nbs/          # 统计局
  wind/         # Wind
  chinabond/    # 中债数据 (YIELD_30Y etc.)
  fred/         # FRED free data (T5YIE etc.)
  market/       # Market data
  policy/       # Policy/EPU data
config/         # Settings (settings.toml is gitignored, use settings.example.toml)
docs/           # Design docs and procurement lists
logs/           # Log files (gitignored)
```

## Database Architecture (3 layers)

- **Layer 0**: `indicator_catalog` — all indicator metadata (single source of truth)
- **Layer 1**: Narrow tables by frequency/type
  - `macro_monthly` — monthly macro (30 indicators, incl. daily→monthly aggregates)
  - `macro_daily` — daily macro (DR007, YIELD_30Y, T5YIE, etc.)
  - `market_daily` — daily market (16 tickers)
  - `quant_daily` — quant modeling (6 tickers)
  - `central_bank_events` — event-driven policy data
  - `news_raw` — raw news text for RAG
  - `derived_daily` — internal computed features (term spreads, funding cost)
- **Layer 2**: `macro_snapshot_monthly` — wide table (~35 columns, 1 row = 1 month snapshot for LLM consumption)

## Key Conventions

- All indicator codes must exist in `indicator_catalog` (foreign key enforced)
- Internal derived features use `category='internal_derived'`, `data_source='INTERNAL_CALC'`
- Daily indicators aggregated to monthly: `source_tag='AGG_FROM_DAILY'`
- Data revisions: append new `data_version` row, never overwrite; query with `MAX(data_version)`
- Raw files stay in filesystem (`data/raw/`), naming: `{source}_{content}_{date}.{ext}`
- NULL means "not yet published" — never fill with 0 or mean

## Common Commands

```bash
# Initialize database
bash db/init.sh

# Run ETL
python -m src.etl.load_macro_monthly --file data/raw/nbs/统计局_20260211.xlsx
python -m src.etl.load_macro_daily --file data/raw/chinabond/yield_30y_20260216.csv
python -m src.etl.load_derived_daily --month 2026-02

# Build monthly snapshot
python -m src.aggregation.build_snapshot --month 2026-02

# Compute covariance matrix
python -m src.aggregation.cov_matrix --start 2016-01-01 --end 2026-01-01

# Lint
ruff check src/ tests/

# Test
pytest
```

## Environment

- DB connection: `DATABASE_URL` env var or `config/settings.toml`
- Default: `mysql+pymysql://root:@localhost:3306/robo_advisor?charset=utf8mb4`
