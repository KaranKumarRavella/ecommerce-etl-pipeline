"""End-to-end dry-run test: no database required."""

from etl.config import Settings
from etl.pipeline import run_pipeline


def test_pipeline_dry_run_sample(sample_csv, tmp_path):
    settings = Settings(
        orders_file=sample_csv,
        max_order_age_days=10000,  # sample dates are Jan 2026; be lenient in tests
    )
    summary = run_pipeline(settings, dry_run=True)
    assert summary["rows_extracted"] == 20
    assert summary["rows_cleaned"] == 20
    assert summary["orders"] == 19
    assert summary["dry_run"] is True
    assert summary["rows_loaded"] == 0
