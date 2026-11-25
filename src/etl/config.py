"""Configuration loaded from environment variables.

All settings have sensible local defaults so the pipeline can be run
with ``--dry-run`` without a database. Production values come from
``.env`` (loaded with python-dotenv when available) or the environment.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

try:
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:  # dotenv is optional for tests
    pass


@dataclass(frozen=True)
class Settings:
    postgres_host: str = "localhost"
    postgres_port: int = 5432
    postgres_db: str = "etl_db"
    postgres_user: str = "etl_user"
    postgres_password: str = "change_me"
    data_dir: Path = Path("data/sample")
    orders_file: Path = Path("data/sample/orders.csv")
    max_order_age_days: int = 365
    min_rows_expected: int = 1
    log_level: str = "INFO"

    @classmethod
    def from_env(cls) -> "Settings":
        return cls(
            postgres_host=os.getenv("POSTGRES_HOST", "localhost"),
            postgres_port=int(os.getenv("POSTGRES_PORT", "5432")),
            postgres_db=os.getenv("POSTGRES_DB", "etl_db"),
            postgres_user=os.getenv("POSTGRES_USER", "etl_user"),
            postgres_password=os.getenv("POSTGRES_PASSWORD", "change_me"),
            data_dir=Path(os.getenv("DATA_DIR", "data/sample")),
            orders_file=Path(os.getenv("ORDERS_FILE", "data/sample/orders.csv")),
            max_order_age_days=int(os.getenv("MAX_ORDER_AGE_DAYS", "365")),
            min_rows_expected=int(os.getenv("MIN_ROWS_EXPECTED", "1")),
            log_level=os.getenv("LOG_LEVEL", "INFO"),
        )

    @property
    def database_url(self) -> str:
        url = os.getenv("DATABASE_URL")
        if url:
            return url
        return (
            f"postgresql://{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )
