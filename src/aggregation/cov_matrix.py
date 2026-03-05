"""Compute annualized covariance matrix from quant_daily narrow table.

Usage:
    python -m src.aggregation.cov_matrix --start 2016-01-01 --end 2026-01-01
"""

import argparse
import logging

import numpy as np
import pandas as pd

from src.utils.db import get_engine

logger = logging.getLogger(__name__)

DEFAULT_TICKERS = ["510300", "518880", "NHCI", "SHIBOR_1W", "CN_BOND_10Y", "CN_BOND_30Y"]


def get_cov_matrix(
    tickers: list[str] | None = None,
    start: str = "2016-01-01",
    end: str = "2026-01-01",
    engine=None,
) -> pd.DataFrame:
    """
    Read quant_daily narrow table, pivot to wide format, compute annualized cov matrix.
    Transparent to caller -- no need to know underlying table is narrow.
    """
    tickers = tickers or DEFAULT_TICKERS
    engine = engine or get_engine()

    placeholders = ",".join([f":t{i}" for i in range(len(tickers))])
    sql = f"""
        SELECT ticker, trade_date, close_price
        FROM quant_daily
        WHERE ticker IN ({placeholders})
          AND trade_date BETWEEN :start AND :end
        ORDER BY trade_date
    """
    params = {f"t{i}": t for i, t in enumerate(tickers)}
    params["start"] = start
    params["end"] = end

    df = pd.read_sql(sql, engine, params=params)

    wide = df.pivot(index="trade_date", columns="ticker", values="close_price")
    returns = wide.pct_change().dropna()
    cov_matrix = returns.cov() * 252  # annualize

    return cov_matrix


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    parser = argparse.ArgumentParser()
    parser.add_argument("--start", default="2016-01-01")
    parser.add_argument("--end", default="2026-01-01")
    args = parser.parse_args()

    cov = get_cov_matrix(start=args.start, end=args.end)
    print(cov.round(4))
