"""Airflow DAG: daily batch ETL for e-commerce orders.

Tasks:
    extract -> transform -> load -> quality checks -> build marts

The Python callables import the same ``etl`` package used by the CLI,
so the DAG and ``python -m etl.pipeline`` always run the same logic.
Set ``ETL_ORDERS_FILE`` in the Airflow environment to point at the
day's input file, or let the default in ``etl.config.Settings`` apply.

To run locally, see README.md "Running with Airflow".
"""

from __future__ import annotations

from datetime import datetime, timedelta

from airflow import DAG
from airflow.operators.python import PythonOperator

from etl.config import Settings
from etl.extract import read_orders_csv
from etl.quality import run_quality_checks
from etl.transform import clean_orders

default_args = {
    "owner": "karan",
    "retries": 2,
    "retry_delay": timedelta(minutes=5),
    "depends_on_past": False,
}


def _extract(**context):
    settings = Settings.from_env()
    df = read_orders_csv(settings.orders_file)
    context["ti"].xcom_push(key="rows_extracted", value=len(df))
    # Pass the raw frame path, not the frame itself, to keep XCom small.
    context["ti"].xcom_push(key="orders_file", value=str(settings.orders_file))


def _transform(**context):
    settings = Settings.from_env()
    df = read_orders_csv(settings.orders_file)
    clean = clean_orders(df)
    clean.to_parquet("/tmp/clean_orders.parquet", index=False)
    context["ti"].xcom_push(key="rows_cleaned", value=len(clean))


def _load(**context):
    import pandas as pd

    from etl.db import execute_sql_file, get_connection
    from etl.load import SQL_DIR, build_marts, load_staging

    settings = Settings.from_env()
    clean = pd.read_parquet("/tmp/clean_orders.parquet")
    conn = get_connection(settings)
    try:
        execute_sql_file(conn, SQL_DIR / "schema.sql")
        loaded = load_staging(conn, clean)
        context["ti"].xcom_push(key="rows_loaded", value=loaded)
    finally:
        conn.close()


def _quality(**context):
    import pandas as pd

    from etl.quality import run_quality_checks

    settings = Settings.from_env()
    clean = pd.read_parquet("/tmp/clean_orders.parquet")
    run_quality_checks(
        clean,
        min_rows_expected=settings.min_rows_expected,
        max_order_age_days=settings.max_order_age_days,
    )


def _build_marts(**context):
    from etl.db import get_connection
    from etl.load import build_marts

    settings = Settings.from_env()
    conn = get_connection(settings)
    try:
        build_marts(conn)
    finally:
        conn.close()


with DAG(
    dag_id="etl_pipeline",
    default_args=default_args,
    description="Daily batch ETL: e-commerce orders CSV to Postgres marts",
    schedule_interval="@daily",
    start_date=datetime(2026, 1, 1),
    catchup=False,
    tags=["etl", "ecommerce", "postgres"],
) as dag:
    extract = PythonOperator(task_id="extract", python_callable=_extract)
    transform = PythonOperator(task_id="transform", python_callable=_transform)
    load = PythonOperator(task_id="load", python_callable=_load)
    quality = PythonOperator(task_id="quality_checks", python_callable=_quality)
    build_marts_task = PythonOperator(task_id="build_marts", python_callable=_build_marts)

    extract >> transform >> load >> quality >> build_marts_task
