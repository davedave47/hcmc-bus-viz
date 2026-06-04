"""Hub route — editorial vertical scroll with 6 card teasers + story affordances.

The hero KPIs are computed once at boot (lru_cache on the query strings)."""
from __future__ import annotations

import datetime
import functools

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse

from .. import db
from ..aggregates import health as health_agg
from ..aggregates import schools as schools_agg
from ..aggregates import spatial as spatial_agg

router = APIRouter()


@functools.lru_cache(maxsize=1)
def hero_kpis() -> dict:
    """6 KPIs shown in the hub stats strip. Reads from the L4 agg_hub_kpis
    table — a single-row aggregate produced by demo.warehouse.build."""
    row = db.query_one("SELECT * FROM agg_hub_kpis")
    return {
        "boardings": int(row["boardings"]),
        "revenue": int(row["revenue"]),
        "student_share": float(row["student_share"]),
        "routes_n": int(row["routes_n"]),
        "stops_n": int(row["stops_n"]),
        "metro_feeders": int(row["metro_feeders"]),
    }


def _fmt_day(iso: str | None) -> str:
    """'2026-02-23' → 'Feb 23'. Empty string if missing."""
    if not iso:
        return ""
    try:
        return datetime.date.fromisoformat(iso).strftime("%b %-d")
    except ValueError:
        return iso


def _fmt_hour(h: int | None) -> str:
    """0..23 → '7am' / '5pm' / '12pm'."""
    if h is None:
        return ""
    suffix = "am" if h < 12 else "pm"
    h12 = h % 12 or 12
    return f"{h12}{suffix}"


@functools.lru_cache(maxsize=1)
def hub_facts() -> dict:
    """Headline numbers the hub teasers quote — every one queried, never static.

    Every value is computed from the same warehouse path the corresponding
    card uses, so the hub can never drift from what a reviewer sees on drill-in:
    the Tết shock is the Network Health / Tết Story metric set; the flagship
    quote is the top edge of the Schools→Routes treemap; demand concentration
    and the twin peaks are read off agg_route_hour."""
    m = health_agg.tet_drop_metrics()
    rows = spatial_agg.boarding_density_per_stop()
    hot = spatial_agg.top_hot_cells(5)
    total = sum(r["boardings"] for r in rows) or 1
    hot_share = 100 * sum(h["boardings"] for h in hot) / total

    # Flagship: the single biggest (route → university) student edge, and how
    # many times larger it is than the next three edges into the same school.
    treemap = schools_agg.schools_to_routes_treemap()
    disp = {u["slug"]: u["display"] for u in schools_agg.UNIVERSITIES}
    if treemap:
        top = treemap[0]
        same_uni = [e for e in treemap if e["uni_slug"] == top["uni_slug"]]
        uni_total = sum(e["student_boardings"] for e in same_uni) or 1
        flagship_route = top["route_no"]
        flagship_school = disp.get(top["uni_slug"], top["uni_slug"])
        flagship_share = round(100 * top["student_boardings"] / uni_total)
        flagship_routes_n = len(same_uni)
    else:
        flagship_route = flagship_school = ""
        flagship_share = 0
        flagship_routes_n = 0

    # School-only routes: routes whose student-fare share is a clear majority.
    routeness = schools_agg.school_routeness()
    n_school_routes = sum(1 for r in routeness if r["student_share"] >= 0.6)

    # Demand concentration + the twin peaks, straight off agg_route_hour.
    route_rows = db.query("""
        SELECT route_no, SUM(boardings) AS b
        FROM agg_route_hour
        GROUP BY route_no
        ORDER BY b DESC
    """)
    grand = sum(r["b"] for r in route_rows) or 1
    cum = 0
    routes_for_80 = len(route_rows)
    for i, r in enumerate(route_rows, 1):
        cum += r["b"]
        if cum / grand >= 0.80:
            routes_for_80 = i
            break

    hour_rows = db.query("""
        SELECT hour, SUM(boardings) AS b FROM agg_route_hour GROUP BY hour
    """)
    by_hour = {int(r["hour"]): r["b"] for r in hour_rows}
    am_peak = max((h for h in by_hour if 5 <= h <= 11), key=lambda h: by_hour[h], default=None)
    pm_peak = max((h for h in by_hour if 14 <= h <= 20), key=lambda h: by_hour[h], default=None)

    cash_share = db.query_scalar("""
        SELECT 100.0 * SUM(CASE WHEN payment_method = 'Tiền mặt' THEN 1 ELSE 0 END)
                     / NULLIF(COUNT(*), 0)
        FROM payments
    """) or 0

    return {
        "tet_drop_pct": round(m["drop_pct"]),
        "tet_trough_pct": round(m["min_drop_pct"]),
        "tet_window_days": m["window_days"],
        "tet_recovery": _fmt_day(m["recovery_day"]),
        "hot_cells": len(hot),
        "hot_share_pct": round(hot_share),
        "flagship_route": flagship_route,
        "flagship_school": flagship_school,
        "flagship_share": flagship_share,
        "flagship_routes_n": flagship_routes_n,
        "n_universities": len(schools_agg.UNIVERSITIES),
        "n_school_routes": n_school_routes,
        "routes_for_80": routes_for_80,
        "am_peak": _fmt_hour(am_peak),
        "pm_peak": _fmt_hour(pm_peak),
        "cash_share": round(cash_share),
    }


@router.get("/", response_class=HTMLResponse)
async def hub(request: Request):
    templates = request.app.state.templates
    return templates.TemplateResponse(
        request,
        "hub.html",
        {"kpis": hero_kpis(), "facts": hub_facts(), "card_index": 0},
    )
