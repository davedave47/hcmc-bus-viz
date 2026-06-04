"""Card 2 — School-Aware Demand aggregates (L4-backed).

Per §4.6 of the report, school attribution is hand-verified for the eight
largest universities only. The remaining schools are geocoded at district
granularity. Every query in this module reads from L4 tables produced by
`demo.warehouse.build`:

  agg_school_route (uni_slug, route_no, fare_class, dow, hour, boardings)
  agg_route_hour (route_no, dow, hour, fare_class, boardings)
"""
from __future__ import annotations

import functools

from .. import db

# (slug, display, canonical stop_id, lat, lng, verified) — sync with
# demo/warehouse/build.py UNIVERSITIES.
UNIVERSITIES: list[dict] = [
    dict(slug="HCMUT",  display="Bách Khoa",         stop_id=506,  lat=10.7726, lng=106.6577, verified=True),
    dict(slug="HCMUS",  display="KH Tự Nhiên",       stop_id=474,  lat=10.7623, lng=106.6831, verified=True),
    dict(slug="UEH",    display="Kinh Tế",           stop_id=7701, lat=10.7062, lng=106.6394, verified=True),
    dict(slug="GTVT",   display="Giao Thông VT",     stop_id=1405, lat=10.8066, lng=106.7160, verified=True),
    dict(slug="USSH",   display="KHXH & Nhân Văn",   stop_id=1096, lat=10.7858, lng=106.7027, verified=True),
    dict(slug="HCMUTE", display="Sư Phạm Kỹ Thuật",  stop_id=400,  lat=10.8499, lng=106.7721, verified=True),
    dict(slug="SGU",    display="Sài Gòn",           stop_id=467,  lat=10.7607, lng=106.6823, verified=True),
    dict(slug="UIT",    display="CNTT (district)",   stop_id=None, lat=10.8704, lng=106.8030, verified=False),
]
_DISPLAY_BY_SLUG = {u["slug"]: u for u in UNIVERSITIES}

_BBOX_LAT_HALF = 0.0045
_BBOX_LNG_HALF = 0.0046


# ────────────────────────────────────────────────────────────────────────
# Chart 1.1 — top schools by student boardings
# ────────────────────────────────────────────────────────────────────────
@functools.lru_cache(maxsize=1)
def top_schools_by_student_boardings() -> list[dict]:
    rows = db.query(
        """
        SELECT uni_slug,
               SUM(boardings) AS boardings_total,
               SUM(CASE WHEN fare_class = 'student' THEN boardings ELSE 0 END) AS student_boardings
        FROM agg_school_route
        GROUP BY uni_slug
        """
    )
    by_slug = {r["uni_slug"]: r for r in rows}
    out = []
    for u in UNIVERSITIES:
        r = by_slug.get(u["slug"], {})
        out.append(dict(
            slug=u["slug"], display=u["display"], verified=u["verified"],
            boardings=int(r.get("boardings_total") or 0),
            student_boardings=int(r.get("student_boardings") or 0),
        ))
    out.sort(key=lambda r: r["student_boardings"], reverse=True)
    return out


# ────────────────────────────────────────────────────────────────────────
# Chart 2.1 — school constellation (bubble scatter)
#   X = total student boardings · Y = morning-peak share %
#   size = # serving routes · colour = equity (nearby stops, gradient)
# ────────────────────────────────────────────────────────────────────────
@functools.lru_cache(maxsize=1)
def school_constellation() -> list[dict]:
    rows = db.query(
        """
        SELECT uni_slug,
               SUM(boardings)                                              AS student_boardings,
               SUM(CASE WHEN hour BETWEEN 6 AND 8 THEN boardings ELSE 0 END) * 1.0
                 / NULLIF(SUM(boardings), 0)                               AS morning_peak_share,
               COUNT(DISTINCT route_no)                                    AS serving_routes
        FROM agg_school_route
        WHERE fare_class = 'student'
        GROUP BY uni_slug
        """
    )
    by_slug = {r["uni_slug"]: r for r in rows}
    prox = {u["slug"]: u for u in school_proximity_geo()}
    out = []
    for u in UNIVERSITIES:
        r = by_slug.get(u["slug"], {})
        p = prox.get(u["slug"], {})
        out.append(dict(
            slug=u["slug"], display=u["display"], verified=u["verified"],
            student_boardings=int(r.get("student_boardings") or 0),
            morning_peak_share=float(r.get("morning_peak_share") or 0),
            serving_routes=int(r.get("serving_routes") or 0),
            nearby_stops=int(p.get("nearby_stops") or 0),
        ))
    return [r for r in out if r["student_boardings"] > 0]


# ────────────────────────────────────────────────────────────────────────
# Chart 2.2 — schools → routes treemap
# ────────────────────────────────────────────────────────────────────────
@functools.lru_cache(maxsize=1)
def school_serving_routes(top_n: int = 6) -> dict:
    """slug → list of the top serving routes (route_no, student_boardings),
    used to populate the school entity panel (spec §11.2 click action:
    'serving routes + walking distances')."""
    out: dict[str, list[dict]] = {}
    for r in schools_to_routes_treemap():
        out.setdefault(r["uni_slug"], []).append(
            dict(route_no=r["route_no"], student_boardings=r["student_boardings"]))
    for slug in out:
        out[slug] = sorted(out[slug], key=lambda e: -e["student_boardings"])[:top_n]
    return out


@functools.lru_cache(maxsize=1)
def schools_to_routes_treemap() -> list[dict]:
    rows = db.query(
        """
        SELECT uni_slug, route_no, SUM(boardings) AS student_boardings
        FROM agg_school_route
        WHERE fare_class = 'student'
          AND route_no IS NOT NULL
        GROUP BY uni_slug, route_no
        HAVING SUM(boardings) >= 20
        ORDER BY student_boardings DESC
        """
    )
    return [
        dict(uni_slug=r["uni_slug"], route_no=r["route_no"],
             student_boardings=int(r["student_boardings"]))
        for r in rows
    ]


# ────────────────────────────────────────────────────────────────────────
# Chart 1.3 — weekly fare-class heatmap (network-wide hour × dow)
# ────────────────────────────────────────────────────────────────────────
@functools.lru_cache(maxsize=4)
def weekly_heatmap(segment: str = "student", date_from: str | None = None,
                   date_to: str | None = None, route: str = "",
                   day_type: str = "all") -> list[dict]:
    """Hour × day-of-week boarding counts, filtered live on every field.

    `segment` ∈ {'student','non_student','all','free'}; `date_from`/`date_to`
    are ISO dates inside the AFC window; `route` is a single route_no or ''
    (all); `day_type` ∈ {'all','weekday','weekend'}. Queries the full
    fact_boardings record so every filter re-queries the warehouse."""
    preds: list[str] = []
    if segment == "student":
        preds.append("fare_class = 'student'")
    elif segment == "non_student":
        preds.append("fare_class IN ('cash','other')")
    elif segment == "free":
        preds.append("fare_class = 'free'")
    if date_from:
        preds.append(f"day >= DATE '{date_from}'")
    if date_to:
        preds.append(f"day <= DATE '{date_to}'")
    if route:
        preds.append(f"route_no = '{route}'")
    if day_type == "weekday":
        preds.append("dayofweek(day) BETWEEN 1 AND 5")
    elif day_type == "weekend":
        preds.append("dayofweek(day) IN (0, 6)")
    where = ("WHERE " + " AND ".join(preds)) if preds else ""
    rows = db.query(f"""
        SELECT dayofweek(day) AS dow, hour, COUNT(*) AS boardings
        FROM fact_boardings
        {where}
        GROUP BY dow, hour
        ORDER BY dow, hour
    """)
    return [dict(dow=int(r["dow"]), hour=int(r["hour"]),
                 boardings=int(r["boardings"])) for r in rows]


@functools.lru_cache(maxsize=1)
def route_list() -> list[str]:
    """Reconciled routes, busiest first — the options for the route filter."""
    rows = db.query("""
        SELECT route_no, SUM(boardings) AS b FROM agg_route_hour
        GROUP BY route_no ORDER BY b DESC
    """)
    return [r["route_no"] for r in rows]


# ────────────────────────────────────────────────────────────────────────
# Chart 1.4 — school-routeness classifier
# ────────────────────────────────────────────────────────────────────────
@functools.lru_cache(maxsize=1)
def school_routeness() -> list[dict]:
    """Per-route metrics, computed entirely on agg_route_hour.
    uni_hits comes from agg_school_route (count of (uni, route) edges)."""
    rows = db.query("""
        WITH per_route AS (
          SELECT route_no,
                 SUM(boardings) AS total_boardings,
                 SUM(CASE WHEN fare_class = 'student' THEN boardings ELSE 0 END) * 1.0
                   / NULLIF(SUM(boardings), 0) AS student_share,
                 SUM(CASE WHEN hour BETWEEN 6 AND 8 THEN boardings ELSE 0 END) * 1.0
                   / NULLIF(SUM(boardings), 0) AS morning_peak_share,
                 SUM(CASE WHEN dow BETWEEN 1 AND 5 THEN boardings ELSE 0 END) * 1.0
                   / NULLIF(SUM(CASE WHEN dow IN (0,6) THEN boardings ELSE 0 END), 0)
                   AS weekday_ratio
          FROM agg_route_hour
          GROUP BY route_no
          HAVING SUM(boardings) >= 5000
        ),
        per_route_uni AS (
          SELECT route_no, COUNT(DISTINCT uni_slug) AS uni_hits
          FROM agg_school_route
          GROUP BY route_no
        )
        SELECT p.route_no,
               p.total_boardings,
               p.student_share,
               p.morning_peak_share,
               COALESCE(p.weekday_ratio, 0) AS weekday_ratio,
               COALESCE(u.uni_hits, 0)      AS uni_hits
        FROM per_route p
        LEFT JOIN per_route_uni u USING (route_no)
        ORDER BY p.student_share DESC
    """)
    return [
        dict(
            route_no=r["route_no"],
            total_boardings=int(r["total_boardings"] or 0),
            student_share=float(r["student_share"] or 0),
            morning_peak_share=float(r["morning_peak_share"] or 0),
            weekday_ratio=float(r["weekday_ratio"] or 0),
            uni_hits=int(r["uni_hits"] or 0),
        )
        for r in rows
    ]


# ────────────────────────────────────────────────────────────────────────
# Chart 1.5 — school proximity & equity (point map)
# ────────────────────────────────────────────────────────────────────────
def school_proximity_geo() -> list[dict]:
    out = []
    for u in UNIVERSITIES:
        n = db.query_scalar(f"""
            SELECT COUNT(*) FROM stops
            WHERE ABS(lat - {u['lat']}) < {_BBOX_LAT_HALF}
              AND ABS(lng - {u['lng']}) < {_BBOX_LNG_HALF}
              AND lat IS NOT NULL AND lng IS NOT NULL
        """)
        out.append(dict(**u, nearby_stops=int(n or 0)))
    return out


# HCMC core bounding box — drops the handful of out-of-bbox/stale stop rows
# (invariant: 77 stops sit outside the city extent).
_CITY_BBOX = dict(lat_min=10.55, lat_max=11.05, lng_min=106.45, lng_max=106.95)


@functools.lru_cache(maxsize=1)
def all_stops_geo() -> list[dict]:
    """Every AFC stop with a valid coordinate inside the city box — the faint
    base layer that gives the proximity map its city shape."""
    b = _CITY_BBOX
    rows = db.query(f"""
        SELECT lat, lng FROM stops
        WHERE lat BETWEEN {b['lat_min']} AND {b['lat_max']}
          AND lng BETWEEN {b['lng_min']} AND {b['lng_max']}
    """)
    return [dict(lat=float(r["lat"]), lng=float(r["lng"])) for r in rows]


@functools.lru_cache(maxsize=1)
def catchment_stops_geo() -> list[dict]:
    """Stops inside the 500 m walking catchment of any verified university —
    the highlighted layer that shows where the schools are actually served."""
    out: list[dict] = []
    for u in UNIVERSITIES:
        rows = db.query(f"""
            SELECT lat, lng FROM stops
            WHERE ABS(lat - {u['lat']}) < {_BBOX_LAT_HALF}
              AND ABS(lng - {u['lng']}) < {_BBOX_LNG_HALF}
              AND lat IS NOT NULL AND lng IS NOT NULL
        """)
        for r in rows:
            out.append(dict(lat=float(r["lat"]), lng=float(r["lng"]), uni_slug=u["slug"]))
    return out
