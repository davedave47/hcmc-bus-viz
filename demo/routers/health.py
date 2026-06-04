"""Card 5 — Network Health & Performance routes."""
from __future__ import annotations

import datetime
import functools

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse

from .. import db
from ..aggregates import health as health_agg
from ..charts import health as chart
from ..charts import style

router = APIRouter(prefix="/cards/health")


@functools.lru_cache(maxsize=1)
def _indexed_days() -> int:
    return int(db.query_scalar("SELECT COUNT(DISTINCT day) FROM agg_network_day") or 0)


def _fmt_day(iso: str | None) -> str:
    if not iso:
        return ""
    try:
        return datetime.date.fromisoformat(iso).strftime("%b %-d")
    except ValueError:
        return iso


@functools.lru_cache(maxsize=1)
def _pulse_subtitle() -> str:
    """Tết shock numbers for the 5.1 subtitle, read from the warehouse so the
    caption can never drift from the chart it sits above."""
    m = health_agg.tet_drop_metrics()
    n = _indexed_days()
    return (f"Daily network ridership over {n} days · "
            f"−{round(m['drop_pct'])}% average across the Tết window, "
            f"−{round(m['min_drop_pct'])}% on the trough day ({_fmt_day(m['min_day'])})")


# Catalogue v5.5 · Theme 5 · QoS front door (3/3 breadth), pulse second
CHARTS = {
    "5.2": dict(slug="5.2", label=("QoS", "multiples"), icon="multiples",
                title="QoS small-multiples (Phase 1 proxy)",
                sub="Three QoS dimensions per route · true QoS-1/2/3 (Chawuthai 2023) awaits the full 50-day GPS window",
                finding="Reliability decomposes into three dimensions, and the weakest one differs by route.",
                builder=chart.chart_5_2_qos_small_multiples),
    "5.1": dict(slug="5.1", label=("Pulse",), icon="pulse",
                title="Network pulse with Tết anomaly",
                sub="Daily network ridership over 90 days · −57% average across the Tết window, −84% on the trough day (Feb 16)",
                finding="Ridership collapses across the Tết window, then recovers.",
                builder=chart.chart_5_1_pulse),
}


def _icon_svg(name: str) -> str:
    return {
        "pulse":     '<path d="M2 13 L7 13 L9 6 L13 20 L17 10 L19 13 L24 13" stroke="currentColor" fill="none" stroke-width="1.7" stroke-linejoin="round" stroke-linecap="round"/>',
        "multiples": '<rect x="2" y="3" width="6" height="20" rx="1" fill="none" stroke="currentColor" stroke-width="1.2"/><rect x="10" y="3" width="6" height="20" rx="1" fill="none" stroke="currentColor" stroke-width="1.2"/><rect x="18" y="3" width="6" height="20" rx="1" fill="none" stroke="currentColor" stroke-width="1.2"/><circle cx="5" cy="9" r="1.2" fill="currentColor"/><circle cx="5" cy="16" r="1.2" fill="currentColor"/><circle cx="13" cy="12" r="1.2" fill="currentColor"/><circle cx="13" cy="18" r="1.2" fill="currentColor"/><circle cx="21" cy="8" r="1.2" fill="currentColor"/><circle cx="21" cy="15" r="1.2" fill="currentColor"/>',
    }.get(name, "")


def _build(slug: str, scene: str | None = None) -> tuple[str, dict]:
    spec = CHARTS[slug]
    if slug == "5.1":
        fig = chart.chart_5_1_pulse(scene)
    else:
        fig = spec["builder"]()
    active = {**spec, "finding": style.action_title(fig, spec["finding"])}
    if slug == "5.1":
        active["sub"] = _pulse_subtitle()
    return fig.to_json(), active


@router.get("", response_class=HTMLResponse)
async def card_health(request: Request, c: str = "5.2"):
    if c not in CHARTS: c = "5.2"
    plotly_json, spec = _build(c)
    return request.app.state.templates.TemplateResponse(
        request, "card_health.html",
        {"card_index": 5, "leaf": spec["title"],
         "charts": CHARTS, "active_slug": c, "active": spec,
         "plotly_json": plotly_json, "icon_svg": _icon_svg,
         "indexed_days": _indexed_days()},
    )


@router.get("/chart/{slug}", response_class=HTMLResponse)
async def chart_partial(slug: str, request: Request, scene: str | None = None):
    if slug not in CHARTS: slug = "5.2"
    plotly_json, spec = _build(slug, scene)
    return request.app.state.templates.TemplateResponse(
        request, "partials/health_canvas.html",
        {"active_slug": slug, "active": spec, "plotly_json": plotly_json,
         "indexed_days": _indexed_days()},
    )
