"""ETL: Compute and load internal derived features into derived_daily table.

Computes from Layer 1 raw data:
  - TERM_SPREAD_10Y_1Y  = YIELD_10Y - CGB_1Y (from macro_daily)
  - TERM_SPREAD_30Y_10Y = YIELD_30Y - YIELD_10Y (from macro_daily)
  - DR007_FUNDING_COST_DAILY (passthrough from macro_daily DR007)

Usage:
    python -m src.etl.load_derived_daily --month 2026-02
"""

import argparse
import logging

import pandas as pd
from sqlalchemy import text

from src.utils.db import get_engine

logger = logging.getLogger(__name__)


def compute_and_load(month: str, engine=None):
    """Compute derived features for a given month and insert into derived_daily."""
    engine = engine or get_engine()
    logger.info("Computing derived features for %s", month)

    month_start = f"{month}-01"

    with engine.connect() as conn:
        # Read daily macro data for the month
        df = pd.read_sql(text("""
            SELECT indicator_code, trade_date, value
            FROM macro_daily
            WHERE indicator_code IN ('YIELD_10Y', 'YIELD_30Y', 'SHIBOR_1W', 'DR007')
              AND trade_date >= :start
              AND trade_date < DATE_ADD(:start, INTERVAL 1 MONTH)
            ORDER BY trade_date
        """), conn, params={"start": month_start})

    if df.empty:
        logger.warning("No macro_daily data found for %s, skipping", month)
        return

    wide = df.pivot(index="trade_date", columns="indicator_code", values="value")

    rows = []

    # TERM_SPREAD_10Y_1Y (bp): using SHIBOR_1W as short-end proxy
    if "YIELD_10Y" in wide.columns and "SHIBOR_1W" in wide.columns:
        spread = (wide["YIELD_10Y"] - wide["SHIBOR_1W"]) * 100  # to bp
        for dt, val in spread.dropna().items():
            rows.append(("TERM_SPREAD_10Y_1Y", dt, float(val)))

    # TERM_SPREAD_30Y_10Y (bp)
    if "YIELD_30Y" in wide.columns and "YIELD_10Y" in wide.columns:
        spread = (wide["YIELD_30Y"] - wide["YIELD_10Y"]) * 100  # to bp
        for dt, val in spread.dropna().items():
            rows.append(("TERM_SPREAD_30Y_10Y", dt, float(val)))

    # DR007_FUNDING_COST_DAILY (passthrough)
    if "DR007" in wide.columns:
        for dt, val in wide["DR007"].dropna().items():
            rows.append(("DR007_FUNDING_COST_DAILY", dt, float(val)))

    if not rows:
        logger.warning("No derived features computed for %s", month)
        return

    insert_sql = text("""
        INSERT INTO derived_daily (indicator_code, trade_date, value)
        VALUES (:code, :dt, :val)
        ON DUPLICATE KEY UPDATE value = VALUES(value)
    """)

    with engine.connect() as conn:
        for code, dt, val in rows:
            conn.execute(insert_sql, {"code": code, "dt": dt, "val": val})
        conn.commit()

    logger.info("Inserted %d derived feature rows for %s", len(rows), month)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    parser = argparse.ArgumentParser()
    parser.add_argument("--month", required=True, help="Target month YYYY-MM")
    args = parser.parse_args()
    compute_and_load(args.month)
