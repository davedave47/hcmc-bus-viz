"""Chart + KPI endpoints (HTTP layer — thin: parse, inject, call a service)."""
from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, HTTPException

from ...db import Warehouse
from ...domain import Theme
from ...repositories import hub
from ...schemas import ChartResponse
from ...services.registry import CHART_SERVICES
from ..deps import get_warehouse

router = APIRouter(prefix="/api")


@router.get("/charts/{theme}/{slug}", response_model=ChartResponse)
def chart(
    theme: Theme,
    slug: str,
    wh: Warehouse = Depends(get_warehouse),
) -> ChartResponse:
    service = CHART_SERVICES.get((theme, slug))
    if service is None:
        raise HTTPException(status_code=404, detail=f"unknown chart {theme.value}/{slug}")
    return service(wh)


@router.get("/kpis")
def kpis(wh: Warehouse = Depends(get_warehouse)) -> dict[str, Any]:
    data = hub.hub_kpis(wh)
    if not data:
        raise HTTPException(status_code=503, detail="kpis unavailable")
    return data
