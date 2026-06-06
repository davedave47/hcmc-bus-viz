"""Read-only warehouse connector — the data-engine seam.

The backend queries the warehouse read-only. This module is the single place
that knows the engine, so swapping DuckDB for BigQuery later (spec §3.2) is
localised here + in the repositories.
"""
from __future__ import annotations

import threading
from pathlib import Path
from typing import Any

import duckdb

from .config import settings

_lock = threading.Lock()
_conn: duckdb.DuckDBPyConnection | None = None


def _ensure_conn() -> duckdb.DuckDBPyConnection:
    """Open the read-only connection once. Caller must hold ``_lock``."""
    global _conn
    if _conn is None:
        path = Path(settings.db_path)
        if not path.exists():
            raise FileNotFoundError(f"Warehouse not found at {path}")
        _conn = duckdb.connect(str(path), read_only=True)
    return _conn


def get_conn() -> duckdb.DuckDBPyConnection:
    with _lock:
        return _ensure_conn()


def query(
    sql: str, params: tuple[Any, ...] | dict[str, Any] | None = None
) -> list[dict[str, Any]]:
    """Run SQL and return one dict per row. Serialised by the global lock —
    DuckDB read connections are thread-safe but the cursor is not."""
    with _lock:
        conn = _ensure_conn()
        cur = conn.execute(sql, params) if params is not None else conn.execute(sql)
        cols = [c[0] for c in cur.description]
        return [dict(zip(cols, row, strict=True)) for row in cur.fetchall()]


def query_one(
    sql: str, params: tuple[Any, ...] | dict[str, Any] | None = None
) -> dict[str, Any] | None:
    rows = query(sql, params)
    return rows[0] if rows else None


def close() -> None:
    global _conn
    with _lock:
        if _conn is not None:
            _conn.close()
            _conn = None
