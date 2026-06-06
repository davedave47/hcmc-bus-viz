"""Filter-bar option lists (routes, day-types, fare segments, date range)."""
from __future__ import annotations

from typing import Any

from ..db import Warehouse

_DAY_TYPES = ["all", "weekday", "weekend"]
_SEGMENTS = ["student", "non_student", "free", "all"]


def filter_options(wh: Warehouse) -> dict[str, Any]:
    routes = [
        r["route_no"]
        for r in wh.query(
            "SELECT route_no, SUM(boardings) AS b FROM agg_route_hour "
            "GROUP BY route_no ORDER BY b DESC"
        )
    ]
    span = wh.query_one("SELECT MIN(day) AS lo, MAX(day) AS hi FROM agg_network_day")
    return {
        "routes": routes,
        "day_types": _DAY_TYPES,
        "segments": _SEGMENTS,
        "date_range": {
            "min": str(span["lo"]) if span and span["lo"] is not None else None,
            "max": str(span["hi"]) if span and span["hi"] is not None else None,
        },
    }
