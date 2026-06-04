"""Card 2 — School-Aware Demand routes.

  GET /cards/schools                  → full card shell (defaults to chart 1.2)
  GET /cards/schools/chart/{slug}     → HTMX partial: canvas + caption + chart JSON
"""
from __future__ import annotations

import functools
import json

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse

from .. import db
from ..aggregates import schools as agg
from ..charts import schools as chart
from ..charts import style

router = APIRouter(prefix="/cards/schools")


@functools.lru_cache(maxsize=1)
def _student_peak_share() -> int:
    """Share of student-fare boardings that fall in the weekday commute peaks
    (Mon–Fri, 06:00–08:59 and 16:00–18:59). Computed off agg_route_hour so the
    2.3 subtitle stays in lock-step with the heatmap it labels."""
    row = db.query_one("""
        SELECT
          SUM(CASE WHEN dow BETWEEN 1 AND 5
                    AND (hour BETWEEN 6 AND 8 OR hour BETWEEN 16 AND 18)
                   THEN boardings ELSE 0 END) AS peak,
          SUM(boardings) AS total
        FROM agg_route_hour
        WHERE fare_class = 'student'
    """)
    if not row or not row["total"]:
        return 0
    return round(100 * row["peak"] / row["total"])


@functools.lru_cache(maxsize=1)
def _total_boardings() -> int:
    return int(db.query_scalar("SELECT boardings FROM agg_hub_kpis") or 0)


# Catalogue v5.5 · Theme 2 · ordered by persona breadth (constellation front door)
CHARTS = {
    "2.1": dict(
        slug="2.1", label=("School", "constel."), icon="bubble",
        title="School constellation",
        sub="X = student-fare boardings · Y = morning-peak share · size = serving routes · colour = stops within 500 m",
        finding="Boarding volume and morning-peak share, by university.",
        builder=chart.chart_2_1_constellation,
    ),
    "2.2": dict(
        slug="2.2", label=("Schools", "→ Routes"), icon="treemap",
        title="Schools → Routes treemap",
        sub="Sized by student-fare boardings in each university's 500 m walking catchment · click a cell to drill in",
        finding="Each university's student ridership concentrates on a few routes.",
        builder=chart.chart_2_2_treemap,
    ),
    "2.4": dict(
        slug="2.4", label=("Prox", "imity"), icon="pin",
        title="School proximity & equity",
        sub="Eight verified universities and the stops within 500 m walking distance",
        finding="University stop-coverage is uneven across the city.",
        builder=chart.chart_2_4_proximity,
    ),
    "2.3": dict(
        slug="2.3", label=("Weekly", "heatmap"), icon="cal",
        title="Weekly fare-class heatmap",
        sub="Boardings by hour-of-day × day-of-week · ~60% of student rides fall in the weekday peaks · toggle the fare class above",
        finding="Student boardings concentrate in weekday peak hours.",
        builder=chart.chart_2_3_weekly,
    ),
}


def _icon_svg(name: str) -> str:
    return {
        "rank":     '<rect x="2" y="4" width="22" height="4" rx="1"/><rect x="2" y="11" width="17" height="4" rx="1" opacity=".75"/><rect x="2" y="18" width="11" height="4" rx="1" opacity=".55"/>',
        "treemap":  '<rect x="1" y="1" width="13" height="24" rx="1"/><rect x="15" y="1" width="10" height="14" rx="1" opacity=".7"/><rect x="15" y="16" width="5" height="9" rx="1" opacity=".5"/><rect x="21" y="16" width="4" height="9" rx="1" opacity=".35"/>',
        "cal":      '<rect x="2" y="2" width="4" height="4" rx=".5" opacity=".4"/><rect x="8" y="2" width="4" height="4" rx=".5" opacity=".9"/><rect x="14" y="2" width="4" height="4" rx=".5" opacity=".55"/><rect x="20" y="2" width="4" height="4" rx=".5" opacity=".25"/><rect x="2" y="8" width="4" height="4" rx=".5" opacity=".6"/><rect x="8" y="8" width="4" height="4" rx=".5" opacity=".85"/><rect x="14" y="8" width="4" height="4" rx=".5" opacity=".3"/><rect x="20" y="8" width="4" height="4" rx=".5" opacity=".2"/><rect x="2" y="14" width="4" height="4" rx=".5" opacity=".4"/><rect x="8" y="14" width="4" height="4" rx=".5" opacity=".7"/><rect x="14" y="14" width="4" height="4" rx=".5" opacity=".25"/><rect x="20" y="14" width="4" height="4" rx=".5" opacity=".15"/><rect x="2" y="20" width="4" height="4" rx=".5" opacity=".15"/><rect x="8" y="20" width="4" height="4" rx=".5" opacity=".4"/>',
        "bubble":   '<circle cx="9" cy="10" r="5" fill="currentColor" opacity=".85"/><circle cx="18" cy="7" r="3" fill="currentColor" opacity=".6"/><circle cx="17" cy="17" r="4" fill="currentColor" opacity=".5"/><circle cx="6" cy="19" r="2.5" fill="currentColor" opacity=".4"/>',
        "pin":      '<path d="M13 3 C 8 3, 4 7, 4 12 C 4 18, 13 24, 13 24 C 13 24, 22 18, 22 12 C 22 7, 18 3, 13 3 Z" fill="none" stroke="currentColor" stroke-width="1.5"/><circle cx="13" cy="12" r="3" fill="currentColor"/>',
    }.get(name, "")


DATE_LO, DATE_HI = "2026-01-01", "2026-03-31"


def _build_canvas_json(slug: str, segment: str = "student", date_from: str = "",
                       date_to: str = "", route: str = "",
                       day_type: str = "all") -> tuple[str, dict]:
    """Return (plotly_json, chart_meta)."""
    spec = CHARTS[slug]
    if spec["builder"] is None:
        return "", spec
    if slug == "2.3":
        fig = chart.chart_2_3_weekly(segment, date_from or None,
                                     date_to or None, route, day_type)
    else:
        fig = spec["builder"]()
    active = {**spec, "finding": style.action_title(fig, spec["finding"])}
    if slug == "2.3":
        bits = []
        if route:
            bits.append(f"Route {route}")
        if day_type == "weekday":
            bits.append("weekdays only")
        elif day_type == "weekend":
            bits.append("weekends only")
        if (date_from and date_from != DATE_LO) or (date_to and date_to != DATE_HI):
            bits.append(f"{date_from or DATE_LO} to {date_to or DATE_HI}")
        flt = (" · " + " · ".join(bits)) if bits else ""
        active["sub"] = (
            f"Boardings by hour-of-day × day-of-week{flt} · every field "
            "re-queries the warehouse live")
    return fig.to_json(), active


def _filter_ctx(segment: str, date_from: str, date_to: str, route: str,
                day_type: str) -> dict:
    return {
        "segment": segment, "date_from": date_from or DATE_LO,
        "date_to": date_to or DATE_HI, "route": route,
        "day_type": day_type, "routes": agg.route_list(),
    }


@router.get("", response_class=HTMLResponse)
async def card_schools(request: Request, c: str = "2.1", segment: str = "student",
                       date_from: str = "", date_to: str = "", route: str = "",
                       day_type: str = "all"):
    if c not in CHARTS:
        c = "2.1"
    plotly_json, spec = _build_canvas_json(c, segment, date_from, date_to,
                                           route, day_type)
    ctx = {
        "card_index": 2, "leaf": spec["title"], "charts": CHARTS,
        "active_slug": c, "active": spec, "plotly_json": plotly_json,
        "icon_svg": _icon_svg, "total_boardings": _total_boardings(),
    }
    ctx.update(_filter_ctx(segment, date_from, date_to, route, day_type))
    return request.app.state.templates.TemplateResponse(
        request, "card_school.html", ctx)


@router.get("/chart/{slug}", response_class=HTMLResponse)
async def chart_partial(slug: str, request: Request, segment: str = "student",
                        date_from: str = "", date_to: str = "", route: str = "",
                        day_type: str = "all"):
    if slug not in CHARTS:
        slug = "2.1"
    plotly_json, spec = _build_canvas_json(slug, segment, date_from, date_to,
                                           route, day_type)
    ctx = {
        "active_slug": slug, "active": spec, "plotly_json": plotly_json,
        "total_boardings": _total_boardings(),
    }
    ctx.update(_filter_ctx(segment, date_from, date_to, route, day_type))
    return request.app.state.templates.TemplateResponse(
        request, "partials/school_canvas.html", ctx)
