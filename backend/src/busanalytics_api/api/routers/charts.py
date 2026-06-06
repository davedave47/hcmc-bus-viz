"""Chart + KPI + filter endpoints (HTTP layer — thin: parse, inject, call a service)."""
from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Request

from ...core.cache import TTLCache
from ...db import Warehouse
from ...domain import Theme
from ...repositories import filters as filters_repo
from ...repositories import hub
from ...schemas import ChartResponse
from ...services.registry import CHART_SERVICES
from ..deps import get_warehouse

router = APIRouter(prefix="/api")

# Read-only warehouse → cache computed payloads by their inputs.
_chart_cache: TTLCache[ChartResponse] = TTLCache(maxsize=256, ttl=300)
_kpis_cache: TTLCache[dict[str, Any]] = TTLCache(maxsize=1, ttl=300)
_filters_cache: TTLCache[dict[str, Any]] = TTLCache(maxsize=1, ttl=300)


@router.get("/charts/{theme}/{slug}", response_model=ChartResponse)
def chart(
    theme: Theme,
    slug: str,
    request: Request,
    wh: Warehouse = Depends(get_warehouse),
) -> ChartResponse:
    service = CHART_SERVICES.get((theme, slug))
    if service is None:
        raise HTTPException(status_code=404, detail=f"unknown chart {theme.value}/{slug}")
    filters = dict(request.query_params)
    key = (theme.value, slug, tuple(sorted(filters.items())))
    return _chart_cache.get_or_compute(key, lambda: service(wh, filters))


@router.get("/kpis")
def kpis(wh: Warehouse = Depends(get_warehouse)) -> dict[str, Any]:
    data = _kpis_cache.get_or_compute("kpis", lambda: hub.hub_kpis(wh))
    if not data:
        raise HTTPException(status_code=503, detail="kpis unavailable")
    return data


@router.get("/filters")
def filter_options(wh: Warehouse = Depends(get_warehouse)) -> dict[str, Any]:
    """Option lists for the filter bar (routes, day-types, fare segments, date range)."""
    return _filters_cache.get_or_compute("filters", lambda: filters_repo.filter_options(wh))
