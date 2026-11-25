"""Transform: clean, validate and enrich raw orders.

Rules (each is covered by tests in ``tests/test_transform.py``):
- Trim whitespace and normalise case for status, currency and region.
- ``order_date`` must parse as a date; unparseable rows are dropped.
- ``quantity`` must be a positive integer; ``unit_price`` must be >= 0.
- ``order_id``, ``customer_id`` and ``product_id`` must be present.
- Duplicate (order_id, product_id) lines are dropped, keeping the first.
- ``line_total`` is computed as quantity * unit_price, rounded to 2dp.
- ``customer_email`` is lower-cased; rows with a missing or malformed
  email are kept but flagged, because an order can still be valid.
- ``status`` is restricted to a known set; anything else becomes
  ``unknown`` and is logged.
"""

from __future__ import annotations

import logging
import re

import pandas as pd

logger = logging.getLogger(__name__)

VALID_STATUSES = {"completed", "shipped", "pending", "cancelled", "refunded"}
EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def clean_orders(df: pd.DataFrame) -> pd.DataFrame:
    """Clean a raw orders DataFrame and return the cleaned frame."""
    if df.empty:
        return df.copy()

    out = df.copy()
    # Normalise text columns.
    for col in ["customer_name", "product_name", "category", "region"]:
        out[col] = out[col].astype(str).str.strip()
    out["status"] = out["status"].astype(str).str.strip().str.lower()
    out["currency"] = out["currency"].astype(str).str.strip().str.upper()
    out["region"] = out["region"].str.title()
    out["customer_email"] = out["customer_email"].astype(str).str.strip().str.lower()

    before = len(out)
    # Drop rows missing a business key.
    out = out.dropna(subset=["order_id", "customer_id", "product_id"])
    out = out[(out["order_id"].astype(str).str.strip() != "")]
    out = out[(out["customer_id"].astype(str).str.strip() != "")]
    out = out[(out["product_id"].astype(str).str.strip() != "")]

    # Parse dates; drop unparseable rows.
    out["order_date"] = pd.to_datetime(out["order_date"], errors="coerce")
    out = out.dropna(subset=["order_date"])

    # Numeric fields.
    out["quantity"] = pd.to_numeric(out["quantity"], errors="coerce")
    out["unit_price"] = pd.to_numeric(out["unit_price"], errors="coerce")
    out = out.dropna(subset=["quantity", "unit_price"])
    out = out[(out["quantity"] > 0) & (out["unit_price"] >= 0)]
    out["quantity"] = out["quantity"].astype(int)
    out["unit_price"] = out["unit_price"].round(2)

    # De-duplicate line items.
    out = out.drop_duplicates(subset=["order_id", "product_id"], keep="first")

    # Status normalisation.
    unknown = ~out["status"].isin(VALID_STATUSES)
    if unknown.any():
        logger.warning("Found %d row(s) with unknown status; marking as 'unknown'", int(unknown.sum()))
        out.loc[unknown, "status"] = "unknown"

    # Enrichment.
    out["line_total"] = (out["quantity"] * out["unit_price"]).round(2)
    out["email_valid"] = out["customer_email"].apply(
        lambda v: bool(EMAIL_RE.match(v)) if isinstance(v, str) else False
    )
    out["order_year"] = out["order_date"].dt.year
    out["order_month"] = out["order_date"].dt.month

    dropped = before - len(out)
    if dropped:
        logger.info("Transform dropped %d invalid row(s) out of %d", dropped, before)
    logger.info("Transform produced %d clean row(s)", len(out))
    return out.reset_index(drop=True)


def order_totals(clean_df: pd.DataFrame) -> pd.DataFrame:
    """Aggregate cleaned line items to one row per order."""
    if clean_df.empty:
        return pd.DataFrame(
            columns=["order_id", "order_date", "customer_id", "total_amount", "item_count"]
        )
    grouped = (
        clean_df.groupby(["order_id", "order_date", "customer_id"], as_index=False)
        .agg(total_amount=("line_total", "sum"), item_count=("product_id", "count"))
    )
    grouped["total_amount"] = grouped["total_amount"].round(2)
    return grouped
