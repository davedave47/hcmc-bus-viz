"""Network Health repository (Gold: agg_network_day, agg_route_hour; dim_date)."""
from __future__ import annotations

from typing import Any

from ..db import Warehouse


def daily_volume(wh: Warehouse) -> list[dict[str, Any]]:
    rows = wh.query(
        """
        SELECT day, SUM(boardings) AS boardings
        FROM agg_network_day
        GROUP BY day
        ORDER BY day
        """
    )
    return [{"day": str(r["day"]), "boardings": int(r["boardings"])} for r in rows]


def tet_window(wh: Warehouse) -> dict[str, Any]:
    """The locked Tết window, read from dim_date (source of truth, not hard-coded)."""
    row = wh.query_one(
        """
        SELECT
          MIN(CASE WHEN is_tet_2026         THEN day END) AS tet_start,
          MAX(CASE WHEN is_tet_2026         THEN day END) AS tet_end,
          MAX(CASE WHEN is_tet_2026_trough  THEN day END) AS tet_trough,
          MIN(CASE WHEN is_pre_tet_baseline THEN day END) AS pre_start,
          MAX(CASE WHEN is_pre_tet_baseline THEN day END) AS pre_end
        FROM dim_date
        """
    )
    if row is None:
        return {}
    return {k: (str(v) if v is not None else None) for k, v in row.items()}


def qos_small_multiples(wh: Warehouse, top_n: int = 60) -> list[dict[str, Any]]:
    """Three QoS proxy scores per route (Phase-1 fare-event proxies), scaled 0..100."""
    rows = wh.query(
        f"""
        WITH per_slot AS (
          SELECT route_no, dow, hour, SUM(boardings) AS n
          FROM agg_route_hour
          GROUP BY route_no, dow, hour
        ),
        per_route AS (
          SELECT route_no,
                 SUM(n)        AS total,
                 COUNT(*)      AS slots_served,
                 AVG(n)        AS hmean,
                 stddev_pop(n) AS hstd
          FROM per_slot
          GROUP BY route_no
          HAVING SUM(n) >= 1000
        )
        SELECT route_no,
               total,
               100.0 * slots_served / 168.0                        AS qos1,
               100.0 * (hmean / NULLIF(hmean + hstd, 0))           AS qos2,
               100.0 * (1.0 - LEAST(1.0, hstd / NULLIF(hmean, 0))) AS qos3
        FROM per_route
        ORDER BY total DESC
        LIMIT {int(top_n)}
        """
    )
    return [
        {
            "route_no": r["route_no"],
            "total": int(r["total"]),
            "qos1": float(r["qos1"] or 0),
            "qos2": float(r["qos2"] or 0),
            "qos3": float(r["qos3"] or 0),
        }
        for r in rows
    ]
