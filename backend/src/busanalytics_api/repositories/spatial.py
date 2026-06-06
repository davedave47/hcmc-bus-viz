"""Spatial & Connectivity repository (Gold: agg_stop_total; Silver: dim_stop)."""
from __future__ import annotations

from typing import Any

from ..db import Warehouse


def boarding_density(wh: Warehouse) -> list[dict[str, Any]]:
    """3.1 — per-stop 90-day boarding totals with coordinates."""
    rows = wh.query(
        "SELECT stop_id, name, lat, lng, boardings FROM agg_stop_total WHERE boardings > 0"
    )
    return [
        {
            "stop_id": int(r["stop_id"]),
            "name": r["name"],
            "lat": float(r["lat"]),
            "lng": float(r["lng"]),
            "boardings": int(r["boardings"]),
        }
        for r in rows
    ]


def stops_with_routes(wh: Warehouse) -> list[dict[str, Any]]:
    """In-bbox stops with their route membership + boardings — backs the metro
    Sankey (3.2) and the reachability isochrone (3.4)."""
    rows = wh.query(
        """
        SELECT s.stop_id, s.name, s.lat, s.lng, s.routes_csv,
               COALESCE(t.boardings, 0) AS boardings
        FROM dim_stop s
        LEFT JOIN agg_stop_total t ON t.stop_id = s.stop_id
        WHERE s.in_bbox AND s.lat IS NOT NULL AND s.lng IS NOT NULL
        """
    )
    return [
        {
            "stop_id": int(r["stop_id"]),
            "name": r["name"],
            "lat": float(r["lat"]),
            "lng": float(r["lng"]),
            "routes_csv": r["routes_csv"] or "",
            "boardings": int(r["boardings"]),
        }
        for r in rows
    ]
