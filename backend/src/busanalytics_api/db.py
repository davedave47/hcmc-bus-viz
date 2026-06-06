"""Warehouse access — the data-engine seam (dependency-inversion boundary).

`Warehouse` is the abstraction repositories depend on; `DuckDBWarehouse` is the
read-only DuckDB implementation used today. A `BigQueryWarehouse` implementing the
same Protocol is the documented prod swap (spec §3.2) — change the provider in
`api/deps.py`, not the repositories.

Honest caveat: the repositories still hold DuckDB-dialect SQL (`stddev_pop`,
`extract`, `LEAST`, `NULLIF`), so a real BigQuery swap also touches their SQL —
this Protocol isolates the *connection*, not the dialect.
"""
from __future__ import annotations

import threading
from pathlib import Path
from typing import Any, Protocol, runtime_checkable

import duckdb

Params = tuple[Any, ...] | dict[str, Any] | None


@runtime_checkable
class Warehouse(Protocol):
    """Read gateway the repositories depend on (not a concrete engine)."""

    def query(self, sql: str, params: Params = None) -> list[dict[str, Any]]: ...

    def query_one(self, sql: str, params: Params = None) -> dict[str, Any] | None: ...

    def close(self) -> None: ...


class DuckDBWarehouse:
    """Read-only DuckDB implementation of `Warehouse`."""

    def __init__(self, db_path: str) -> None:
        path = Path(db_path)
        if not path.exists():
            raise FileNotFoundError(f"Warehouse not found at {path}")
        self._conn = duckdb.connect(str(path), read_only=True)
        self._lock = threading.Lock()

    def query(self, sql: str, params: Params = None) -> list[dict[str, Any]]:
        with self._lock:
            cur = self._conn.execute(sql, params) if params is not None else self._conn.execute(sql)
            cols = [c[0] for c in cur.description]
            return [dict(zip(cols, row, strict=True)) for row in cur.fetchall()]

    def query_one(self, sql: str, params: Params = None) -> dict[str, Any] | None:
        rows = self.query(sql, params)
        return rows[0] if rows else None

    def close(self) -> None:
        self._conn.close()
