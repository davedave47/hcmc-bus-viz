"""DuckDB connector for the demo surface.

Opens the project warehouse read-only and exposes a tiny query helper. The
existing 24 raw views registered by `src.duckdb_loader.BusDuckDB` are
available directly through the `query()` function.
"""
from __future__ import annotations

import functools
import logging
import threading
from pathlib import Path

import duckdb

logger = logging.getLogger("demo.db")

_PROJECT_ROOT = Path(__file__).resolve().parent.parent
_DB_PATH = _PROJECT_ROOT / "db" / "bus.duckdb"

_lock = threading.Lock()
_conn: duckdb.DuckDBPyConnection | None = None


def get_conn() -> duckdb.DuckDBPyConnection:
    global _conn
    with _lock:
        if _conn is None:
            if not _DB_PATH.exists():
                raise FileNotFoundError(
                    f"Warehouse not found at {_DB_PATH}. "
                    "Run src/duckdb_loader.py first to build it."
                )
            _conn = duckdb.connect(str(_DB_PATH), read_only=True)
            logger.info("Opened warehouse %s (read-only)", _DB_PATH)
        return _conn


def query(sql: str, params: tuple | dict | None = None) -> list[dict]:
    """Run SQL, return list of dicts (one per row). DuckDB query is serialised
    by the global lock — DuckDB read-only connections are thread-safe for
    reads, but the cursor returned by execute() is not."""
    with _lock:
        conn = _conn if _conn is not None else get_conn()
        cur = conn.execute(sql, params) if params is not None else conn.execute(sql)
        cols = [c[0] for c in cur.description]
        return [dict(zip(cols, row)) for row in cur.fetchall()]


def query_one(sql: str, params: tuple | dict | None = None) -> dict | None:
    rows = query(sql, params)
    return rows[0] if rows else None


def query_scalar(sql: str, params: tuple | dict | None = None):
    row = query_one(sql, params)
    return next(iter(row.values())) if row else None


@functools.lru_cache(maxsize=256)
def cached_query(sql: str) -> tuple[dict, ...]:
    """Memoised query for static aggregates. Returns a tuple so the result is
    hashable and safely reusable across requests."""
    return tuple(query(sql))


def close():
    global _conn
    with _lock:
        if _conn is not None:
            _conn.close()
            _conn = None
