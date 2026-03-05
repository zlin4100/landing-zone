"""ETL: Load macro daily indicators from raw files into macro_daily table.

Covers daily-frequency macro indicators that need raw daily preservation:
  - DR007, YIELD_10Y, YIELD_30Y, T5YIE
  - CREDIT_SPREAD_AA, CREDIT_SPREAD_AA_AAA, FX_CNY_MID, SHIBOR_3M

Monthly averages are aggregated and written to macro_monthly with
source_tag='AGG_FROM_DAILY'.

Usage:
    python -m src.etl.load_macro_daily --file data/raw/chinabond/yield_30y_20260216.csv
    python -m src.etl.load_macro_daily --file data/raw/fred/t5yie_20260216.csv
"""

import argparse
import logging

import pandas as pd
from sqlalchemy import text

from src.utils.db import get_engine

logger = logging.getLogger(__name__)

DAILY_MACRO_INDICATORS = [
    "DR007", "YIELD_10Y", "YIELD_30Y", "T5YIE",
    "CREDIT_SPREAD_AA", "CREDIT_SPREAD_AA_AAA",
    "FX_CNY_MID", "SHIBOR_3M",
]


def load(file_path: str, engine=None):
    """Read a raw daily macro data file, clean, and insert into macro_daily."""
    engine = engine or get_engine()
    logger.info("Loading macro daily data from %s", file_path)

    # TODO: Implement file parsing logic per vendor format
    # - chinabond: yield curve CSV (YIELD_30Y, CREDIT_SPREAD_AA_AAA)
    # - fred: T5YIE CSV download
    # - cfets: DR007/SHIBOR daily
    # - Parse indicator_code, trade_date, value
    # - INSERT ... ON DUPLICATE KEY UPDATE value = VALUES(value)
    raise NotImplementedError("Implement per vendor file format")


def aggregate_monthly(month: str, engine=None):
    """Aggregate daily values to monthly average and write to macro_monthly.

    Args:
        month: Target month in 'YYYY-MM' format.
    """
    engine = engine or get_engine()
    logger.info("Aggregating macro_daily -> macro_monthly for %s", month)

    sql = text("""
        INSERT INTO macro_monthly (indicator_code, stat_month, value, data_version, source_tag)
        SELECT
            indicator_code,
            :month AS stat_month,
            AVG(value) AS value,
            1 AS data_version,
            'AGG_FROM_DAILY' AS source_tag
        FROM macro_daily
        WHERE indicator_code IN :codes
          AND trade_date >= CONCAT(:month, '-01')
          AND trade_date < DATE_ADD(CONCAT(:month, '-01'), INTERVAL 1 MONTH)
        GROUP BY indicator_code
        ON DUPLICATE KEY UPDATE
            value = VALUES(value),
            source_tag = VALUES(source_tag)
    """)

    with engine.connect() as conn:
        conn.execute(sql, {
            "month": month,
            "codes": tuple(DAILY_MACRO_INDICATORS),
        })
        conn.commit()

    logger.info("Monthly aggregation for %s complete", month)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    parser = argparse.ArgumentParser()
    parser.add_argument("--file", required=True, help="Path to raw data file")
    args = parser.parse_args()
    load(args.file)
