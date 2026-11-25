"""Data quality checks.

Checks run on the cleaned DataFrame (and, when a connection is
available, against the warehouse with ``sql/quality_checks.sql``).
A failed check does not silently pass: ``run_quality_checks`` raises
``QualityCheckFailed`` so Airflow / the CLI can mark the run failed.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field

import pandas as pd

logger = logging.getLogger(__name__)


class QualityCheckFailed(Exception):
    """Raised when one or more quality checks fail."""


@dataclass
class QualityCheckResult:
    name: str
    passed: bool
    detail: str


@dataclass
class QualityReport:
    results: list[QualityCheckResult] = field(default_factory=list)

    @property
    def passed(self) -> bool:
        return all(r.passed for r in self.results)

    def failures(self) -> list[QualityCheckResult]:
        return [r for r in self.results if not r.passed]


def run_quality_checks(
    df: pd.DataFrame,
    *,
    min_rows_expected: int = 1,
    max_order_age_days: int = 365,
    reference_date: pd.Timestamp | None = None,
) -> QualityReport:
    """Run the standard checks on a cleaned orders frame."""
    results: list[QualityCheckResult] = []
    now = reference_date or pd.Timestamp.now(tz="UTC")
    if now.tzinfo is None:
        now = now.tz_localize("UTC")

    results.append(
        QualityCheckResult(
            "row_count",
            len(df) >= min_rows_expected,
            f"{len(df)} row(s), expected at least {min_rows_expected}",
        )
    )

    for col in ["order_id", "customer_id", "product_id", "order_date"]:
        nulls = int(df[col].isna().sum()) if col in df.columns else -1
        results.append(
            QualityCheckResult(
                f"not_null_{col}",
                nulls == 0,
                f"{nulls} null(s) in {col}",
            )
        )

    dupes = 0
    if not df.empty and {"order_id", "product_id"}.issubset(df.columns):
        dupes = int(df.duplicated(subset=["order_id", "product_id"]).sum())
    results.append(
        QualityCheckResult(
            "unique_order_product",
            dupes == 0,
            f"{dupes} duplicate (order_id, product_id) pair(s)",
        )
    )

    negative = 0
    if not df.empty and "line_total" in df.columns:
        negative = int((df["line_total"] < 0).sum())
    results.append(
        QualityCheckResult(
            "non_negative_line_total",
            negative == 0,
            f"{negative} negative line_total(s)",
        )
    )

    if not df.empty and "order_date" in df.columns:
        dates = pd.to_datetime(df["order_date"], utc=True, errors="coerce")
        max_age = (now - dates.max()).days
        results.append(
            QualityCheckResult(
                "freshness",
                max_age <= max_order_age_days,
                f"latest order is {max_age} day(s) old, limit is {max_order_age_days}",
            )
        )
    else:
        results.append(QualityCheckResult("freshness", False, "no order dates to check"))

    report = QualityReport(results)
    for r in results:
        level = logging.INFO if r.passed else logging.ERROR
        logger.log(level, "Quality check %s: %s — %s", r.name, "PASS" if r.passed else "FAIL", r.detail)
    if not report.passed:
        raise QualityCheckFailed(
            "Quality checks failed: "
            + ", ".join(f"{f.name} ({f.detail})" for f in report.failures())
        )
    return report
