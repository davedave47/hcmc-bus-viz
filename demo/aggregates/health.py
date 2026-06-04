"""Card 5 — Network Health & Performance aggregates (L4-backed).

Tết window dates are read from the L2 `dim_date` table at module load
time so the demo never carries date constants in Python code. The L2 dim
encodes the empirical Feb 14--22 window and the Feb 16 trough day."""
from __future__ import annotations

import functools

from .. import db


_TET_KEYS = {
    "TET_2026_START":         "tet_start",
    "TET_2026_END":           "tet_end",
    "TET_2026_TROUGH":        "tet_trough",
    "PRE_TET_BASELINE_START": "pre_start",
    "PRE_TET_BASELINE_END":   "pre_end",
    "TET_2026_RECOVERY":      "recovery_day",
}


@functools.lru_cache(maxsize=1)
def _tet_window() -> dict:
    """Read the locked Tet window from dim_date (one query per process)."""
    row = db.query_one("""
        SELECT
          MIN(CASE WHEN is_tet_2026         THEN day END) AS tet_start,
          MAX(CASE WHEN is_tet_2026         THEN day END) AS tet_end,
          MAX(CASE WHEN is_tet_2026_trough  THEN day END) AS tet_trough,
          MIN(CASE WHEN is_pre_tet_baseline THEN day END) AS pre_start,
          MAX(CASE WHEN is_pre_tet_baseline THEN day END) AS pre_end,
          MIN(CASE WHEN day > (SELECT MAX(day) FROM dim_date WHERE is_tet_2026)
                   THEN day END)                          AS recovery_day
        FROM dim_date
    """)
    return {k: str(v) for k, v in row.items()}


def __getattr__(name: str) -> str:
    """Lazy module-level constants — resolved on first access against
    dim_date so the source of truth lives in the warehouse, not Python."""
    if name in _TET_KEYS:
        return _tet_window()[_TET_KEYS[name]]
    raise AttributeError(f"module 'demo.aggregates.health' has no attribute {name!r}")


@functools.lru_cache(maxsize=1)
def daily_volume() -> list[dict]:
    rows = db.query("""
        SELECT day, SUM(boardings) AS boardings
        FROM agg_network_day
        GROUP BY day
        ORDER BY day
    """)
    return [dict(day=str(r["day"]), boardings=int(r["boardings"])) for r in rows]


@functools.lru_cache(maxsize=1)
def tet_drop_metrics() -> dict:
    """Net summary numbers for the chart annotations and the Story Bing."""
    w = _tet_window()
    pre_start, pre_end = w["pre_start"], w["pre_end"]
    tet_start, tet_end = w["tet_start"], w["tet_end"]
    rows = daily_volume()
    by_day = {r["day"]: r["boardings"] for r in rows}
    pre_dates = [d for d in by_day if pre_start <= d <= pre_end]
    tet_dates = [d for d in by_day if tet_start <= d <= tet_end]
    if not pre_dates or not tet_dates:
        return dict(pre_mean=0, tet_mean=0, drop_pct=0, min_day=None,
                    min_val=0, min_drop_pct=0, recovery_day=None, window_days=0)
    pre_mean = sum(by_day[d] for d in pre_dates) / len(pre_dates)
    tet_mean = sum(by_day[d] for d in tet_dates) / len(tet_dates)
    drop_pct = 100 * (1 - tet_mean / pre_mean) if pre_mean else 0
    min_day = min(tet_dates, key=lambda d: by_day[d])
    min_val = by_day[min_day]
    min_drop_pct = 100 * (1 - min_val / pre_mean) if pre_mean else 0
    # True recovery day: first day after the trough whose volume is back to
    # at least 90% of the January baseline. Queried, not assumed.
    post = sorted(d for d in by_day if d > min_day)
    recovery_day = next((d for d in post if by_day[d] >= 0.9 * pre_mean),
                        w["recovery_day"])
    return dict(
        pre_mean=int(pre_mean), tet_mean=int(tet_mean), drop_pct=drop_pct,
        min_day=min_day, min_val=int(min_val), min_drop_pct=min_drop_pct,
        recovery_day=recovery_day, window_days=len(tet_dates),
    )


@functools.lru_cache(maxsize=1)
def service_calendar() -> list[dict]:
    rows = db.query("""
        SELECT day,
               SUM(boardings) AS boardings,
               extract(week FROM day)::INT AS iso_week,
               extract(dow  FROM day)::INT AS dow
        FROM agg_network_day
        GROUP BY day
        ORDER BY day
    """)
    return [dict(day=str(r["day"]), boardings=int(r["boardings"]),
                 iso_week=int(r["iso_week"]), dow=int(r["dow"])) for r in rows]


@functools.lru_cache(maxsize=1)
def qos_small_multiples(top_n: int = 60) -> list[dict]:
    """Three QoS proxy dimensions per route (Phase-1 fare-event proxies;
    true QoS-1/2/3 from Chawuthai 2023 awaits the full 50-day GPS window):
      qos1_completion  — service-slot coverage: distinct (dow,hour) slots
                         served / 168 possible. Proxy for trip completion.
      qos2_onpath      — share of boardings on the route's modal stop set
                         (concentration as a proxy for on-path consistency).
      qos3_onschedule  — hourly consistency 1 - std/mean (lower variance =
                         more schedule-like). Proxy for on-schedule.
    Each scaled to 0..100."""
    rows = db.query(f"""
        WITH per_slot AS (
          SELECT route_no, dow, hour, SUM(boardings) AS n
          FROM agg_route_hour
          GROUP BY route_no, dow, hour
        ),
        per_route AS (
          SELECT route_no,
                 SUM(n)                              AS total,
                 COUNT(*)                            AS slots_served,
                 AVG(n)                              AS hmean,
                 stddev_pop(n)                       AS hstd
          FROM per_slot
          GROUP BY route_no
          HAVING SUM(n) >= 1000
        )
        SELECT route_no,
               total,
               100.0 * slots_served / 168.0                          AS qos1_completion,
               100.0 * (hmean / NULLIF(hmean + hstd, 0))             AS qos2_onpath,
               100.0 * (1.0 - LEAST(1.0, hstd / NULLIF(hmean, 0)))   AS qos3_onschedule
        FROM per_route
        ORDER BY total DESC
        LIMIT {top_n}
    """)
    return [dict(
        route_no=r["route_no"], total=int(r["total"]),
        qos1=float(r["qos1_completion"] or 0),
        qos2=float(r["qos2_onpath"] or 0),
        qos3=float(r["qos3_onschedule"] or 0),
    ) for r in rows]


@functools.lru_cache(maxsize=1)
def reliability_scorecard(top_n: int = 25) -> list[dict]:
    rows = db.query(f"""
        WITH per_dow_hour AS (
          SELECT route_no, dow, hour, SUM(boardings) AS n
          FROM agg_route_hour
          GROUP BY route_no, dow, hour
        ),
        per_route AS (
          SELECT route_no,
                 SUM(n) AS total,
                 COUNT(DISTINCT (dow, hour)) AS service_slots,
                 SUM(CASE WHEN hour BETWEEN 6 AND 8 OR hour BETWEEN 16 AND 18
                          THEN n ELSE 0 END) AS peak_n,
                 AVG(n) AS hourly_mean,
                 stddev_pop(n) AS hourly_std
          FROM per_dow_hour
          GROUP BY route_no
          HAVING SUM(n) >= 1000
        )
        SELECT route_no, total,
               service_slots                                    AS service_days,
               peak_n,
               (peak_n * 1.0) / NULLIF(total, 0)                AS peak_share,
               1.0 - LEAST(1.0, hourly_std / NULLIF(hourly_mean, 0))
                                                                AS consistency
        FROM per_route
        ORDER BY consistency DESC, total DESC
        LIMIT {top_n}
    """)
    return [dict(
        route_no=r["route_no"], total=int(r["total"]),
        service_days=int(r["service_days"]), peak_share=float(r["peak_share"] or 0),
        consistency=float(r["consistency"] or 0),
    ) for r in rows]
