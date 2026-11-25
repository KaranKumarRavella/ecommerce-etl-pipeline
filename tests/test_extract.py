"""Tests for etl.extract."""

import pytest

from etl.extract import discover_csvs, read_orders_csv


def test_read_sample_csv(sample_csv):
    df = read_orders_csv(sample_csv)
    assert len(df) == 20
    assert "order_id" in df.columns
    assert "line_total" not in df.columns  # computed in transform, not raw


def test_read_missing_file_raises():
    with pytest.raises(FileNotFoundError):
        read_orders_csv("data/does-not-exist.csv")


def test_read_missing_columns_raises(tmp_path):
    bad = tmp_path / "bad.csv"
    bad.write_text("order_id,order_date\nORD-1,2026-01-01\n", encoding="utf-8")
    with pytest.raises(ValueError, match="Missing required columns"):
        read_orders_csv(bad)


def test_discover_csvs(sample_csv):
    files = discover_csvs(sample_csv.parent)
    assert files == [sample_csv]
