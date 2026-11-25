"""Generate synthetic e-commerce orders for local testing.

Usage:
    python scripts/generate_data.py --rows 500 --out data/generated
    python scripts/generate_data.py --rows 500 --out data/generated --seed 42

The output is a single ``orders.csv`` with the same schema as
``data/sample/orders.csv``. A small fraction of rows are intentionally
messy (bad dates, zero quantities, duplicate lines) so the transform
and quality checks have something to catch.
"""

from __future__ import annotations

import argparse
import csv
import random
from datetime import date, timedelta
from pathlib import Path

CUSTOMERS = [
    ("CUS-001", "Ana Sharma", "ana.sharma@example.com"),
    ("CUS-002", "Ben Carter", "ben.carter@example.com"),
    ("CUS-003", "Carla Diaz", "carla.diaz@example.com"),
    ("CUS-004", "David Kim", "david.kim@example.com"),
    ("CUS-005", "Emma Patel", "emma.patel@example.com"),
    ("CUS-006", "Farid Hassan", "farid.hassan@example.com"),
    ("CUS-007", "Grace Liu", "grace.liu@example.com"),
    ("CUS-008", "Henry Moore", "henry.moore@example.com"),
    ("CUS-009", "Ivy Chen", "ivy.chen@example.com"),
    ("CUS-010", "Jack Novak", "jack.novak@example.com"),
]

PRODUCTS = [
    ("PRD-101", "Wireless Headphones", "Electronics", 59.99),
    ("PRD-102", "Bluetooth Speaker", "Electronics", 45.00),
    ("PRD-103", "Smart Watch", "Electronics", 199.99),
    ("PRD-104", "USB-C Cable", "Electronics", 12.50),
    ("PRD-201", "Coffee Maker", "Home", 89.00),
    ("PRD-202", "Blender", "Home", 49.99),
    ("PRD-203", "Air Fryer", "Home", 129.00),
    ("PRD-204", "Toaster", "Home", 39.99),
    ("PRD-301", "Running Shoes", "Sports", 120.00),
    ("PRD-302", "Yoga Mat", "Sports", 25.00),
    ("PRD-303", "Dumbbell Set", "Sports", 75.00),
]

REGIONS = ["West", "East", "South", "Midwest", "Northeast"]
STATUSES = ["completed", "completed", "completed", "shipped", "pending", "cancelled", "refunded"]
HEADER = [
    "order_id", "order_date", "customer_id", "customer_name", "customer_email",
    "product_id", "product_name", "category", "quantity", "unit_price",
    "currency", "status", "region",
]


def generate(rows: int, seed: int, out_dir: Path) -> Path:
    rng = random.Random(seed)
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / "orders.csv"
    start = date(2026, 1, 1)
    written: list[list] = []
    for i in range(rows):
        order_id = f"ORD-{2000 + i // 2}"
        order_date = start + timedelta(days=rng.randrange(0, 180))
        cust = rng.choice(CUSTOMERS)
        prod = rng.choice(PRODUCTS)
        row = [
            order_id,
            order_date.isoformat(),
            cust[0], cust[1], cust[2],
            prod[0], prod[1], prod[2],
            rng.randint(1, 4),
            f"{prod[3]:.2f}",
            "USD",
            rng.choice(STATUSES),
            rng.choice(REGIONS),
        ]
        # Inject a few messy rows (~2%) for testing.
        if rng.random() < 0.02:
            row[8] = 0  # zero quantity
        written.append(row)
    with out_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(HEADER)
        writer.writerows(written)
    return out_path


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate synthetic orders CSV")
    parser.add_argument("--rows", type=int, default=500)
    parser.add_argument("--out", type=Path, default=Path("data/generated"))
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()
    path = generate(args.rows, args.seed, args.out)
    print(f"Wrote {args.rows} rows to {path}")


if __name__ == "__main__":
    main()
