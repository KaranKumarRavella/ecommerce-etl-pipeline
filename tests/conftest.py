"""Shared fixtures for the ETL tests."""

from pathlib import Path

import pandas as pd
import pytest


@pytest.fixture
def raw_orders() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "order_id": "ORD-1",
                "order_date": "2026-01-05",
                "customer_id": "CUS-001",
                "customer_name": " Ana Sharma ",
                "customer_email": "ANA.SHARMA@EXAMPLE.COM",
                "product_id": "PRD-101",
                "product_name": "Wireless Headphones",
                "category": "Electronics",
                "quantity": "2",
                "unit_price": "59.99",
                "currency": "usd",
                "status": "Completed",
                "region": "west",
            },
            {
                "order_id": "ORD-1",
                "order_date": "2026-01-05",
                "customer_id": "CUS-001",
                "customer_name": "Ana Sharma",
                "customer_email": "ana.sharma@example.com",
                "product_id": "PRD-101",
                "product_name": "Wireless Headphones",
                "category": "Electronics",
                "quantity": "2",
                "unit_price": "59.99",
                "currency": "USD",
                "status": "completed",
                "region": "West",
            },
            {
                "order_id": "ORD-2",
                "order_date": "not-a-date",
                "customer_id": "CUS-002",
                "customer_name": "Ben Carter",
                "customer_email": "ben.carter@example.com",
                "product_id": "PRD-201",
                "product_name": "Coffee Maker",
                "category": "Home",
                "quantity": "1",
                "unit_price": "89.00",
                "currency": "USD",
                "status": "shipped",
                "region": "East",
            },
            {
                "order_id": "ORD-3",
                "order_date": "2026-01-07",
                "customer_id": "CUS-003",
                "customer_name": "Carla Diaz",
                "customer_email": "carla.diaz@example.com",
                "product_id": "PRD-102",
                "product_name": "Bluetooth Speaker",
                "category": "Electronics",
                "quantity": "0",
                "unit_price": "45.00",
                "currency": "USD",
                "status": "completed",
                "region": "South",
            },
        ]
    )


@pytest.fixture
def sample_csv() -> Path:
    return Path(__file__).resolve().parents[1] / "data" / "sample" / "orders.csv"
