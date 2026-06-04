"""JSON API surface for the demo.

Routes:
  GET /api/healthz                       — liveness + L4 table presence
  GET /api/kpis                          — hub stats strip
  GET /api/charts/{theme}/{slug}         — Plotly figure JSON for one chart
  GET /api/aggregates/{name}             — raw aggregate rows (read-only)
                                           name ∈ {network_day, stop_total,
                                                   route_hour_fc, school_route}

The page-rendering routers reuse the same chart builders, so /api/charts and
the inline-embedded chart JSON return identical payloads.
"""
from __future__ import annotations

import datetime as _dt
import decimal
import json
from typing import Any, Callable

from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse, PlainTextResponse


def _json_safe(v: Any) -> Any:
    """Coerce DuckDB column values that the stdlib JSON encoder rejects."""
    if isinstance(v, (_dt.date, _dt.datetime)):
        return v.isoformat()
    if isinstance(v, decimal.Decimal):
        return float(v)
    if isinstance(v, dict):
        return {k: _json_safe(x) for k, x in v.items()}
    if isinstance(v, list):
        return [_json_safe(x) for x in v]
    return v

from .. import db
from ..charts import health as health_charts
from ..charts import schools as school_charts
from ..charts import spatial as spatial_charts

router = APIRouter(prefix="/api")


_CHART_BUILDERS: dict[str, dict[str, Callable]] = {
    "schools": {
        "2.1": school_charts.chart_2_1_constellation,
        "2.2": school_charts.chart_2_2_treemap,
        "2.3": lambda: school_charts.chart_2_3_weekly("student"),
        "2.4": school_charts.chart_2_4_proximity,
    },
    "spatial": {
        "3.1": spatial_charts.chart_3_1_density,
        "3.2": spatial_charts.chart_3_2_metro_sankey,
        "3.4": spatial_charts.chart_3_4_isochrone,
    },
    "health": {
        "5.1": health_charts.chart_5_1_pulse,
        "5.2": health_charts.chart_5_2_qos_small_multiples,
    },
}


_REQUIRED_L4_TABLES = (
    "agg_network_day", "agg_route_hour", "agg_route_day",
    "agg_stop_hour", "agg_stop_total", "agg_school_route",
    "agg_hub_kpis",
)
_REQUIRED_L2_DIMS = (
    "dim_date", "dim_hour", "dim_route", "dim_stop",
    "dim_school", "dim_school_stop", "dim_trip",
    "dim_company", "dim_fare_class", "dim_payment_channel",
    "dim_vehicle", "dim_promotion",
)


def _l4_status() -> dict:
    rows = db.query("""
        SELECT table_name FROM information_schema.tables
        WHERE table_schema = 'main' AND table_type = 'BASE TABLE'
    """)
    present = {r["table_name"] for r in rows}
    required = set(_REQUIRED_L4_TABLES) | set(_REQUIRED_L2_DIMS)
    missing = sorted(required - present)
    return dict(
        l2_dims_present=sorted(set(_REQUIRED_L2_DIMS) & present),
        l4_aggs_present=sorted(set(_REQUIRED_L4_TABLES) & present),
        missing=missing,
        healthy=not missing,
    )


@router.get("/healthz")
async def healthz():
    s = _l4_status()
    body = dict(ok=s["healthy"], **s,
                hint=("All L4 aggregates present" if s["healthy"]
                      else "Run `python -m demo.warehouse.build` to materialise "
                           "the missing aggregate tables."))
    return JSONResponse(content=body, status_code=200 if s["healthy"] else 503)


@router.get("/kpis")
async def kpis():
    return JSONResponse(content=_json_safe(db.query_one("SELECT * FROM agg_hub_kpis")))


@router.get("/charts/{theme}/{slug}")
async def chart_json(theme: str, slug: str):
    if theme not in _CHART_BUILDERS:
        raise HTTPException(status_code=404, detail=f"unknown theme '{theme}'")
    if slug not in _CHART_BUILDERS[theme]:
        raise HTTPException(status_code=404, detail=f"unknown chart '{slug}' in theme '{theme}'")
    fig = _CHART_BUILDERS[theme][slug]()
    return PlainTextResponse(content=fig.to_json(), media_type="application/json")


@router.get("/aggregates/{name}")
async def aggregate_rows(name: str, limit: int = 10000):
    name_map = {
        "network_day":   "agg_network_day",
        "stop_total":    "agg_stop_total",
        "stop_dow_hour": "agg_stop_dow_hour",
        "route_hour_fc": "agg_route_hour_fc",
        "school_route":  "agg_school_route",
    }
    if name not in name_map:
        raise HTTPException(status_code=404, detail=f"unknown aggregate '{name}'")
    if limit < 1 or limit > 100000:
        raise HTTPException(status_code=400, detail="limit must be in [1, 100000]")
    rows = db.query(f"SELECT * FROM {name_map[name]} LIMIT {int(limit)}")
    return JSONResponse(content=_json_safe(rows))
