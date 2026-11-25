"""Postgres helpers. Imported lazily by the loader so the rest of the
pipeline (extract / transform / quality) can run without a database.
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


def get_connection(settings: Any):
    """Return a psycopg2 connection using settings.database_url."""
    import psycopg2

    conn = psycopg2.connect(settings.database_url)
    conn.autocommit = False
    return conn


def execute_sql_file(conn, path: str | Path) -> None:
    """Execute a .sql file, splitting on semicolons at statement level."""
    sql_text = Path(path).read_text(encoding="utf-8")
    statements = [s.strip() for s in sql_text.split(";") if s.strip()]
    with conn.cursor() as cur:
        for statement in statements:
            logger.debug("Executing SQL: %s...", statement[:80].replace("\n", " "))
            cur.execute(statement)
    conn.commit()
