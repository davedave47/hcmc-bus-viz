"""Schools & Students chart services — series + A2 action title (no Plotly, no FastAPI)."""
from __future__ import annotations

from collections.abc import Mapping

from ...db import Warehouse
from ...repositories import schools as repo
from ...schemas import ChartResponse

_WEEKLY_TITLE = {
    "student": "Student boardings concentrate in weekday peak hours.",
    "non_student": "Non-student boardings are spread across the day.",
    "all": "The network pulses with a sharp morning and evening peak.",
    "free": "Free-fare rides cluster on weekend afternoons.",
}


def constellation(wh: Warehouse, filters: Mapping[str, str]) -> ChartResponse:
    """2.1 — school constellation (bubble scatter)."""
    return ChartResponse(
        theme="schools",
        slug="2.1",
        title="Boarding volume and morning-peak share, by university.",
        subtitle="X = 90-day student-fare boardings · Y = share in the 6–8 AM peak · "
        "bubble size = serving routes · colour = stops within 500 m (equity)",
        series=repo.constellation(wh),
        encoding={
            "x": "student_boardings",
            "y": "morning_peak_share",
            "size": "serving_routes",
            "color": "nearby_stops",
            "label": "display",
            "kind": "bubble",
        },
    )


def treemap(wh: Warehouse, filters: Mapping[str, str]) -> ChartResponse:
    """2.2 — schools → routes treemap."""
    return ChartResponse(
        theme="schools",
        slug="2.2",
        title="Each university's student ridership concentrates on a few routes.",
        subtitle="Sized by 90-day student-fare boardings in the 500 m walking catchment of each campus",
        series=repo.treemap(wh),
        encoding={"hierarchy": ["uni_display", "route_no"], "value": "student_boardings", "kind": "treemap"},
    )


def weekly_heatmap(wh: Warehouse, filters: Mapping[str, str]) -> ChartResponse:
    """2.3 — weekly fare-class heatmap (live filter bar)."""
    segment = filters.get("segment", "student")
    date_from = filters.get("date_from") or None
    date_to = filters.get("date_to") or None
    route = filters.get("route", "")
    day_type = filters.get("day_type", "all")
    rows = repo.weekly_heatmap(wh, segment, date_from, date_to, route, day_type)
    return ChartResponse(
        theme="schools",
        slug="2.3",
        title=_WEEKLY_TITLE.get(segment, "Weekly ridership by hour"),
        subtitle=f"Boardings by hour-of-day × day-of-week · {segment.replace('_', ' ')} fare · Jan–Mar 2026",
        series=rows,
        encoding={"x": "hour", "y": "dow", "z": "boardings", "kind": "heatmap"},
        meta={
            "applied": {
                "segment": segment,
                "date_from": date_from,
                "date_to": date_to,
                "route": route or None,
                "day_type": day_type,
            }
        },
    )


def proximity(wh: Warehouse, filters: Mapping[str, str]) -> ChartResponse:
    """2.4 — school proximity & equity map."""
    data = repo.proximity(wh)
    return ChartResponse(
        theme="schools",
        slug="2.4",
        title="Most universities sit on a dense stop cluster — but coverage is uneven.",
        subtitle="Every city stop (grey), the 500 m walking catchment of each campus (gold), "
        "and the eight universities",
        series=data["schools"],
        encoding={"lat": "lat", "lng": "lng", "label": "display", "kind": "map"},
        meta={"city_stops": data["city_stops"], "catchment": data["catchment"]},
    )
