-- Postgres schema for the e-commerce ETL pipeline.
-- Run via the loader (etl.db.execute_sql_file) or psql -f sql/schema.sql

CREATE SCHEMA IF NOT EXISTS staging;
CREATE SCHEMA IF NOT EXISTS marts;

CREATE TABLE IF NOT EXISTS staging.orders (
    order_id       TEXT NOT NULL,
    order_date     DATE NOT NULL,
    customer_id    TEXT NOT NULL,
    customer_name  TEXT NOT NULL,
    customer_email TEXT NOT NULL,
    product_id     TEXT NOT NULL,
    product_name   TEXT NOT NULL,
    category       TEXT NOT NULL,
    quantity       INTEGER NOT NULL CHECK (quantity > 0),
    unit_price     NUMERIC(10, 2) NOT NULL CHECK (unit_price >= 0),
    currency       TEXT NOT NULL,
    status         TEXT NOT NULL,
    region         TEXT NOT NULL,
    line_total     NUMERIC(12, 2) NOT NULL CHECK (line_total >= 0),
    loaded_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS marts.dim_customers (
    customer_id    TEXT PRIMARY KEY,
    customer_name  TEXT NOT NULL,
    customer_email TEXT NOT NULL,
    first_order_date DATE,
    last_order_date  DATE,
    total_orders   INTEGER NOT NULL DEFAULT 0,
    total_spent    NUMERIC(12, 2) NOT NULL DEFAULT 0
);

CREATE TABLE IF NOT EXISTS marts.dim_products (
    product_id   TEXT PRIMARY KEY,
    product_name TEXT NOT NULL,
    category     TEXT NOT NULL,
    total_quantity INTEGER NOT NULL DEFAULT 0,
    total_revenue  NUMERIC(12, 2) NOT NULL DEFAULT 0
);

CREATE TABLE IF NOT EXISTS marts.fact_orders (
    order_id     TEXT NOT NULL,
    order_date   DATE NOT NULL,
    customer_id  TEXT NOT NULL,
    product_id   TEXT NOT NULL,
    quantity     INTEGER NOT NULL,
    unit_price   NUMERIC(10, 2) NOT NULL,
    line_total   NUMERIC(12, 2) NOT NULL,
    status       TEXT NOT NULL,
    region       TEXT NOT NULL,
    PRIMARY KEY (order_id, product_id)
);

CREATE TABLE IF NOT EXISTS marts.daily_sales (
    order_date     DATE PRIMARY KEY,
    orders_count   INTEGER NOT NULL,
    items_sold     INTEGER NOT NULL,
    total_revenue  NUMERIC(12, 2) NOT NULL
);
