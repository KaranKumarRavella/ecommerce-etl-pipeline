"""Tests for etl.quality."""

import pandas as pd
import pytest

from etl.quality import QualityCheckFailed, run_quality_checks
from etl.transform import clean_orders


def test_quality_passes_on_clean_data(raw_orders):
    clean = clean_orders(raw_orders)
    report = run_quality_checks(
        clean, reference_date=pd.Timestamp("2026-02-01", tz="UTC")
    )
    assert report.passed


def test_quality_fails_on_empty_frame():
    with pytest.raises(QualityCheckFailed):
        run_quality_checks(pd.DataFrame(), reference_date=pd.Timestamp("2026-02-01", tz="UTC"))


def test_quality_fails_on_duplicate_lines(raw_orders):
    # Bypass transform de-duplication by checking the raw frame directly.
    with pytest.raises(QualityCheckFailed):
        run_quality_checks(
            raw_orders.assign(line_total=10.0),
            reference_date=pd.Timestamp("2026-02-01", tz="UTC"),
        )


def test_quality_fails_on_stale_data(raw_orders):
    clean = clean_orders(raw_orders)
    with pytest.raises(QualityCheckFailed):
        run_quality_checks(
            clean,
            max_order_age_days=1,
            reference_date=pd.Timestamp("2027-01-01", tz="UTC"),
        )
