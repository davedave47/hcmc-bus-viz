"""Chart + KPI endpoints (HTTP layer — thin)."""
from __future__ import annotations

from typing import Any

from fastapi import APIRouter, HTTPException

from ...repositories import hub
from ...schemas import ChartResponse
from ...services.registry import CHART_SERVICES

router = APIRouter(prefix="/api")


@router.get("/charts/{theme}/{slug}", response_model=ChartResponse)
def chart(theme: str, slug: str) -> ChartResponse:
    service = CHART_SERVICES.get((theme, slug))
    if service is None:
        raise HTTPException(status_code=404, detail=f"unknown chart {theme}/{slug}")
    return service()


@router.get("/kpis")
def kpis() -> dict[str, Any]:
    data = hub.hub_kpis()
    if not data:
        raise HTTPException(status_code=503, detail="kpis unavailable")
    return data
