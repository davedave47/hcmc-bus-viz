"""FastAPI dependencies.

The single place that constructs the concrete `Warehouse`. Routers receive it via
`Depends(get_warehouse)` and pass it down — repositories and services never import a
global connection. Swapping the engine = changing the implementation built here.
Tests can override with `app.dependency_overrides[get_warehouse]`.
"""
from __future__ import annotations

from ..config import settings
from ..db import DuckDBWarehouse, Warehouse

_warehouse: Warehouse | None = None


def get_warehouse() -> Warehouse:
    """Provider for the read-only warehouse (lazy singleton)."""
    global _warehouse
    if _warehouse is None:
        _warehouse = DuckDBWarehouse(settings.db_path)
    return _warehouse


def close_warehouse() -> None:
    global _warehouse
    if _warehouse is not None:
        _warehouse.close()
        _warehouse = None
