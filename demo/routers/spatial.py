"""Card 3 — Spatial & Connectivity routes."""
from __future__ import annotations

import functools

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse

from .. import db
from ..aggregates import spatial as spatial_agg
from ..charts import spatial as chart
from ..charts import style

router = APIRouter(prefix="/cards/spatial")


@functools.lru_cache(maxsize=1)
def _stops_n() -> int:
    return int(db.query_scalar("SELECT stops_n FROM agg_hub_kpis") or 0)


def _metro_stations() -> int:
    return len(spatial_agg.METRO_L1)


# Catalogue v5.5 · Theme 3 · hex front door, sankey, isochrone (cartogram folded into 3.1)
CHARTS = {
    "3.1": dict(slug="3.1", label=("Hex", "density"), icon="hex",
                title="Multi-layer hex density map",
                sub="Stop-level boardings as a continuous density · cartogram + ghost-stop layers fold in here (Phase 2) · top-5 stops labelled",
                finding="A handful of central stops drive the densest peaks in the boarding map.",
                builder=chart.chart_3_1_density),
    "3.2": dict(slug="3.2", label=("Bus", "→ Metro"), icon="sankey",
                title="Bus → Metro feeder Sankey (indicative)",
                sub="Boardings at bus stops within 550 m of each Metro Line 1 station, expanded to feeder routes",
                finding="Dozens of bus routes feed every Metro station — the corridor is multi-modal at every stop.",
                builder=chart.chart_3_2_metro_sankey),
    "3.4": dict(slug="3.4", label=("Iso", "chrone"), icon="iso",
                title="Accessibility isochrone",
                sub="Network-reachability from a chosen origin (Phase-1 proxy over the route-sharing graph)",
                finding="From the central hub, one transfer multiplies the reachable-stop count.",
                builder=chart.chart_3_4_isochrone),
}


def _icon_svg(name: str) -> str:
    return {
        "hex":    '<circle cx="13" cy="13" r="5" opacity=".9"/><circle cx="8" cy="9" r="3" opacity=".6"/><circle cx="17" cy="9" r="3" opacity=".55"/><circle cx="8" cy="18" r="3" opacity=".5"/><circle cx="17" cy="18" r="2.5" opacity=".4"/>',
        "sankey": '<path d="M3 5 C 10 5, 16 7, 23 8" stroke="currentColor" fill="none" stroke-width="3" opacity=".7"/><path d="M3 12 C 10 12, 16 14, 23 15" stroke="currentColor" fill="none" stroke-width="4" opacity=".55"/><path d="M3 20 C 10 20, 16 21, 23 22" stroke="currentColor" fill="none" stroke-width="2" opacity=".4"/>',
        "cart":   '<rect x="2" y="3" width="9" height="8" rx="1" opacity=".75"/><rect x="13" y="3" width="11" height="11" rx="1"/><rect x="2" y="13" width="13" height="11" rx="1" opacity=".55"/><rect x="17" y="16" width="7" height="8" rx="1" opacity=".4"/>',
        "vor":    '<path d="M3 6 L11 4 L15 9 L13 15 L7 16 Z" fill="none" stroke="currentColor" stroke-width="1.2"/><path d="M15 9 L21 8 L23 14 L19 19 L13 15 Z" fill="none" stroke="currentColor" stroke-width="1.2"/><path d="M7 16 L13 15 L19 19 L15 23 L8 22 Z" fill="none" stroke="currentColor" stroke-width="1.2"/><circle cx="8" cy="10" r="1.5" fill="currentColor"/><circle cx="17" cy="13" r="1.5" fill="currentColor"/><circle cx="12" cy="19" r="1.5" fill="currentColor"/>',
        "iso":    '<circle cx="13" cy="13" r="3" fill="currentColor"/><circle cx="13" cy="13" r="6" fill="none" stroke="currentColor" stroke-width="1" opacity=".65"/><circle cx="13" cy="13" r="10" fill="none" stroke="currentColor" stroke-width="1" opacity=".4"/>',
    }.get(name, "")


def _build(slug: str) -> tuple[str, dict]:
    spec = CHARTS[slug]
    if spec["builder"] is None:
        return "", spec
    fig = spec["builder"]()
    active = {**spec, "finding": style.action_title(fig, spec["finding"])}
    return fig.to_json(), active


@router.get("", response_class=HTMLResponse)
async def card_spatial(request: Request, c: str = "3.1"):
    if c not in CHARTS: c = "3.1"
    plotly_json, spec = _build(c)
    return request.app.state.templates.TemplateResponse(
        request, "card_spatial.html",
        {"card_index": 3, "leaf": spec["title"],
         "charts": CHARTS, "active_slug": c, "active": spec,
         "plotly_json": plotly_json, "icon_svg": _icon_svg,
         "stops_n": _stops_n(), "metro_stations": _metro_stations()},
    )


@router.get("/chart/{slug}", response_class=HTMLResponse)
async def chart_partial(slug: str, request: Request):
    if slug not in CHARTS: slug = "3.1"
    plotly_json, spec = _build(slug)
    return request.app.state.templates.TemplateResponse(
        request, "partials/spatial_canvas.html",
        {"active_slug": slug, "active": spec, "plotly_json": plotly_json,
         "stops_n": _stops_n(), "metro_stations": _metro_stations()},
    )
