"""Pipeline runner: extract -> transform -> load -> quality checks.

Usage:
    python -m etl.pipeline --dry-run            # no database needed
    python -m etl.pipeline --orders data/sample/orders.csv
    python -m etl.pipeline                      # full load to Postgres

``--dry-run`` runs extract, transform and quality checks only, and is
the recommended first step after checkout. The full run also creates
the schema, loads staging, and rebuilds the marts.
"""

from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path

from etl.config import Settings
from etl.extract import read_orders_csv
from etl.quality import run_quality_checks
from etl.transform import clean_orders, order_totals

logger = logging.getLogger(__name__)


def setup_logging(level: str = "INFO") -> None:
    logging.basicConfig(
        level=getattr(logging, level.upper(), logging.INFO),
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )


def run_pipeline(settings: Settings | None = None, *, dry_run: bool = False) -> dict:
    """Run the full pipeline and return a summary dict."""
    settings = settings or Settings.from_env()
    setup_logging(settings.log_level)

    raw = read_orders_csv(settings.orders_file)
    clean = clean_orders(raw)
    totals = order_totals(clean)
    logger.info(
        "Cleaned %d line(s) across %d order(s), total revenue %.2f",
        len(clean),
        len(totals),
        float(totals["total_amount"].sum()) if not totals.empty else 0.0,
    )

    # Quality checks run on the cleaned frame in every mode.
    run_quality_checks(
        clean,
        min_rows_expected=settings.min_rows_expected,
        max_order_age_days=settings.max_order_age_days,
    )

    loaded = 0
    if not dry_run:
        from etl.db import execute_sql_file, get_connection
        from etl.load import SQL_DIR, build_marts, load_staging

        conn = get_connection(settings)
        try:
            logger.info("Creating schema from %s", SQL_DIR / "schema.sql")
            execute_sql_file(conn, SQL_DIR / "schema.sql")
            loaded = load_staging(conn, clean)
            build_marts(conn)
        finally:
            conn.close()
        logger.info("Load complete: %d row(s) staged, marts rebuilt", loaded)

    return {
        "rows_extracted": len(raw),
        "rows_cleaned": len(clean),
        "orders": len(totals),
        "rows_loaded": loaded,
        "dry_run": dry_run,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run the e-commerce ETL pipeline")
    parser.add_argument("--orders", type=Path, default=None, help="Orders CSV to load")
    parser.add_argument("--dry-run", action="store_true", help="Skip database load")
    args = parser.parse_args(argv)

    settings = Settings.from_env()
    if args.orders:
        settings = Settings(
            **{**settings.__dict__, "orders_file": args.orders}
        )
    try:
        summary = run_pipeline(settings, dry_run=args.dry_run)
    except Exception as exc:  # noqa: BLE001 - surface the failure and exit non-zero
        logger.exception("Pipeline failed: %s", exc)
        return 1
    logger.info("Pipeline succeeded: %s", summary)
    return 0


if __name__ == "__main__":
    sys.exit(main())
