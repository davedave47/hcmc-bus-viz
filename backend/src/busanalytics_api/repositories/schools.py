"""Schools & Students repository (Gold: agg_school_route, agg_route_hour;
Silver: dim_school, dim_stop; Fact: fact_boardings for the filtered heatmap)."""
from __future__ import annotations

from typing import Any

from ..db import Warehouse

# 500 m walking-catchment half-box (matches the dim_school_stop bridge).
_LAT_HALF = 0.0045
_LNG_HALF = 0.0046
_CITY_BBOX = (10.55, 11.05, 106.45, 106.95)  # lat_min, lat_max, lng_min, lng_max

_FARE_PREDICATE = {
    "student": "fare_class = 'student'",
    "non_student": "fare_class IN ('cash','other')",
    "free": "fare_class = 'free'",
    "all": "",
}


def constellation(wh: Warehouse) -> list[dict[str, Any]]:
    """2.1 — per-university student volume, morning-peak share, serving routes, equity."""
    return wh.query(
        """
        WITH a AS (
          SELECT uni_slug,
                 SUM(boardings) AS student_boardings,
                 SUM(CASE WHEN hour BETWEEN 6 AND 8 THEN boardings ELSE 0 END) * 1.0
                   / NULLIF(SUM(boardings), 0) AS morning_peak_share,
                 COUNT(DISTINCT route_no) AS serving_routes
          FROM agg_school_route
          WHERE fare_class = 'student'
          GROUP BY uni_slug
        ),
        p AS (
          SELECT sc.school_slug AS uni_slug, COUNT(st.stop_id) AS nearby_stops
          FROM dim_school sc
          LEFT JOIN dim_stop st
            ON ABS(st.lat - sc.lat) < 0.0045 AND ABS(st.lng - sc.lng) < 0.0046
          GROUP BY sc.school_slug
        )
        SELECT sc.school_slug AS slug, sc.display, sc.verified,
               COALESCE(a.student_boardings, 0)  AS student_boardings,
               COALESCE(a.morning_peak_share, 0) AS morning_peak_share,
               COALESCE(a.serving_routes, 0)     AS serving_routes,
               COALESCE(p.nearby_stops, 0)       AS nearby_stops
        FROM dim_school sc
        LEFT JOIN a ON a.uni_slug = sc.school_slug
        LEFT JOIN p ON p.uni_slug = sc.school_slug
        WHERE COALESCE(a.student_boardings, 0) > 0
        ORDER BY student_boardings DESC
        """
    )


def treemap(wh: Warehouse) -> list[dict[str, Any]]:
    """2.2 — (university → route) student-boarding edges."""
    return wh.query(
        """
        SELECT a.uni_slug, sc.display AS uni_display, a.route_no,
               SUM(a.boardings) AS student_boardings
        FROM agg_school_route a
        JOIN dim_school sc ON sc.school_slug = a.uni_slug
        WHERE a.fare_class = 'student' AND a.route_no IS NOT NULL
        GROUP BY a.uni_slug, sc.display, a.route_no
        HAVING SUM(a.boardings) >= 20
        ORDER BY student_boardings DESC
        """
    )


def weekly_heatmap(
    wh: Warehouse,
    segment: str = "student",
    date_from: str | None = None,
    date_to: str | None = None,
    route: str = "",
    day_type: str = "all",
) -> list[dict[str, Any]]:
    """2.3 — hour × day-of-week counts, filtered live (every field re-queries
    fact_boardings). route/date are parameterised; segment/day_type are allow-listed."""
    preds: list[str] = []
    params: list[Any] = []
    fare = _FARE_PREDICATE.get(segment, "fare_class = 'student'")
    if fare:
        preds.append(fare)
    if date_from:
        preds.append("day >= CAST(? AS DATE)")
        params.append(date_from)
    if date_to:
        preds.append("day <= CAST(? AS DATE)")
        params.append(date_to)
    if route:
        preds.append("route_no = ?")
        params.append(route)
    if day_type == "weekday":
        preds.append("dayofweek(day) BETWEEN 1 AND 5")
    elif day_type == "weekend":
        preds.append("dayofweek(day) IN (0, 6)")
    where = ("WHERE " + " AND ".join(preds)) if preds else ""
    rows = wh.query(
        f"""
        SELECT dayofweek(day) AS dow, hour, COUNT(*) AS boardings
        FROM fact_boardings
        {where}
        GROUP BY dow, hour
        ORDER BY dow, hour
        """,
        tuple(params) if params else None,
    )
    return [
        {"dow": int(r["dow"]), "hour": int(r["hour"]), "boardings": int(r["boardings"])}
        for r in rows
    ]


def proximity(wh: Warehouse) -> dict[str, list[dict[str, Any]]]:
    """2.4 — school points (+ equity count), the city stop base layer, and the
    500 m walking-catchment stops."""
    schools = wh.query(
        """
        WITH p AS (
          SELECT sc.school_slug, COUNT(st.stop_id) AS nearby_stops
          FROM dim_school sc
          LEFT JOIN dim_stop st
            ON ABS(st.lat - sc.lat) < 0.0045 AND ABS(st.lng - sc.lng) < 0.0046
          GROUP BY sc.school_slug
        )
        SELECT sc.school_slug AS slug, sc.display, sc.lat, sc.lng, sc.verified,
               COALESCE(p.nearby_stops, 0) AS nearby_stops
        FROM dim_school sc
        LEFT JOIN p ON p.school_slug = sc.school_slug
        ORDER BY nearby_stops DESC
        """
    )
    lo_lat, hi_lat, lo_lng, hi_lng = _CITY_BBOX
    city_stops = wh.query(
        f"""
        SELECT lat, lng FROM dim_stop
        WHERE lat BETWEEN {lo_lat} AND {hi_lat} AND lng BETWEEN {lo_lng} AND {hi_lng}
        """
    )
    catchment = wh.query(
        """
        SELECT st.lat, st.lng, sc.school_slug AS uni_slug
        FROM dim_school sc
        JOIN dim_stop st
          ON ABS(st.lat - sc.lat) < 0.0045 AND ABS(st.lng - sc.lng) < 0.0046
        """
    )
    return {"schools": schools, "city_stops": city_stops, "catchment": catchment}
