"""Extract: read raw e-commerce orders from CSV.

The expected columns are documented in README.md and in
``data/sample/orders.csv``. Extraction is deliberately strict about the
schema (missing columns fail fast) and lenient about individual rows
(bad rows are reported and dropped later, in transform).
"""

from __future__ import annotations

import logging
from pathlib import Path

import pandas as pd

logger = logging.getLogger(__name__)

REQUIRED_COLUMNS = {
    "order_id",
    "order_date",
    "customer_id",
    "customer_name",
    "customer_email",
    "product_id",
    "product_name",
    "category",
    "quantity",
    "unit_price",
    "currency",
    "status",
    "region",
}


def read_orders_csv(path: str | Path) -> pd.DataFrame:
    """Read an orders CSV into a DataFrame, preserving raw values.

    Raises:
        FileNotFoundError: if the file does not exist.
        ValueError: if required columns are missing.
    """
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"Orders file not found: {path}")
    df = pd.read_csv(path, dtype=str, keep_default_na=True)
    missing = REQUIRED_COLUMNS - set(df.columns)
    if missing:
        raise ValueError(f"Missing required columns in {path}: {sorted(missing)}")
    logger.info("Extracted %d rows from %s", len(df), path)
    return df


def discover_csvs(data_dir: str | Path) -> list[Path]:
    """Return all CSV files under a directory, sorted for determinism."""
    files = sorted(Path(data_dir).glob("*.csv"))
    logger.info("Discovered %d CSV file(s) in %s", len(files), data_dir)
    return files
