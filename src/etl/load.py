"""Load: write cleaned orders to Postgres (staging, then marts).

Staging is a full refresh per run (``TRUNCATE`` + insert) which keeps
the pipeline idempotent for a batch job: re-running the same day
produces the same staging table. Marts are rebuilt from staging with
the SQL in ``models/marts/`` so the warehouse stays the single source
of truth for downstream reporting.
"""

from __future__ import annotations

import logging
from pathlib import Path

import pandas as pd

logger = logging.getLogger(__name__)

STAGING_COLUMNS = [
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
    "line_total",
]

SQL_DIR = Path(__file__).resolve().parents[2] / "sql"
MODELS_DIR = Path(__file__).resolve().parents[2] / "models"


def load_staging(conn, df: pd.DataFrame) -> int:
    """Truncate staging.orders and insert the cleaned frame. Returns rows."""
    if df.empty:
        logger.warning("No rows to load into staging")
        return 0
    cols = [c for c in STAGING_COLUMNS if c in df.columns]
    rows = [
        tuple(None if pd.isna(v) else v for v in row)
        for row in df[cols].itertuples(index=False, name=None)
    ]
    placeholders = ", ".join(["%s"] * len(cols))
    with conn.cursor() as cur:
        cur.execute("TRUNCATE TABLE staging.orders")
        cur.executemany(
            f"INSERT INTO staging.orders ({', '.join(cols)}) "
            f"VALUES ({placeholders})",
            rows,
        )
    conn.commit()
    logger.info("Loaded %d row(s) into staging.orders", len(rows))
    return len(rows)


def build_marts(conn) -> None:
    """Rebuild marts from staging.

    Runs ``sql/marts_build.sql`` (plain Postgres). The files in
    ``models/marts/`` are the same logic in dbt form, using ref(),
    and are intended for ``dbt build`` rather than this loader.
    """
    from etl.db import execute_sql_file

    logger.info("Building marts from sql/marts_build.sql")
    execute_sql_file(conn, SQL_DIR / "marts_build.sql")
