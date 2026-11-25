"""Tests for etl.transform.clean_orders and order_totals."""

from etl.transform import clean_orders, order_totals


def test_clean_orders_dedupes_and_drops_bad_rows(raw_orders):
    clean = clean_orders(raw_orders)
    # 4 raw rows: 1 duplicate, 1 bad date, 1 zero quantity -> 1 clean row
    assert len(clean) == 1
    row = clean.iloc[0]
    assert row["order_id"] == "ORD-1"
    assert row["quantity"] == 2
    assert float(row["line_total"]) == 119.98
    assert row["status"] == "completed"
    assert row["currency"] == "USD"
    assert row["customer_email"] == "ana.sharma@example.com"
    assert row["region"] == "West"


def test_clean_orders_normalises_unknown_status(raw_orders):
    df = raw_orders.iloc[:1].copy()
    df.loc[0, "status"] = "weird-status"
    clean = clean_orders(df)
    assert clean.iloc[0]["status"] == "unknown"


def test_clean_orders_empty_frame():
    import pandas as pd

    assert clean_orders(pd.DataFrame()).empty


def test_order_totals_aggregates_lines(raw_orders):
    clean = clean_orders(raw_orders)
    totals = order_totals(clean)
    assert len(totals) == 1
    assert totals.iloc[0]["order_id"] == "ORD-1"
    assert float(totals.iloc[0]["total_amount"]) == 119.98
    assert int(totals.iloc[0]["item_count"]) == 1
