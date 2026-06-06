"""Liveness + warehouse-readiness endpoint."""
from __future__ import annotations

from typing import Any

from fastapi import APIRouter

from ..deps import get_warehouse

router = APIRouter(prefix="/api")


@router.get("/healthz")
def healthz() -> dict[str, Any]:
    """Always 200 (the API is live); reports whether the warehouse is reachable
    so a missing/locked DB shows up as `warehouse_ready: false`, not a crash."""
    try:
        get_warehouse().query_one("SELECT 1")
        return {"status": "ok", "warehouse_ready": True}
    except Exception as exc:  # noqa: BLE001 — readiness probe must not raise
        return {"status": "ok", "warehouse_ready": False, "detail": str(exc)}
