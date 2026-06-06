"""Spatial & Connectivity chart services — series + A2 title + graph logic
(Sankey/isochrone). Framework-agnostic (no FastAPI, no Plotly)."""
from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from ...db import Warehouse
from ...repositories import spatial as repo
from ...schemas import ChartResponse

# Metro Line 1 stations (approximate centroids) — domain reference data.
METRO_L1: list[dict[str, Any]] = [
    {"slug": "BTH", "name": "Bến Thành", "lat": 10.7720, "lng": 106.6986},
    {"slug": "OPR", "name": "Nhà Hát Thành Phố", "lat": 10.7765, "lng": 106.7029},
    {"slug": "BSO", "name": "Ba Son", "lat": 10.7855, "lng": 106.7066},
    {"slug": "VTH", "name": "Văn Thánh", "lat": 10.8004, "lng": 106.7158},
    {"slug": "TCG", "name": "Tân Cảng", "lat": 10.7986, "lng": 106.7224},
    {"slug": "THD", "name": "Thảo Điền", "lat": 10.8060, "lng": 106.7370},
    {"slug": "APH", "name": "An Phú", "lat": 10.8076, "lng": 106.7475},
    {"slug": "RCH", "name": "Rạch Chiếc", "lat": 10.8330, "lng": 106.7670},
    {"slug": "PLG", "name": "Phước Long", "lat": 10.8480, "lng": 106.7707},
    {"slug": "BTI", "name": "Bình Thái", "lat": 10.8519, "lng": 106.7733},
    {"slug": "TDC", "name": "Thủ Đức", "lat": 10.8511, "lng": 106.7716},
    {"slug": "KCC", "name": "Khu Công Nghệ Cao", "lat": 10.8568, "lng": 106.7901},
    {"slug": "DHQ", "name": "Đại Học Quốc Gia", "lat": 10.8718, "lng": 106.8023},
    {"slug": "STI", "name": "Suối Tiên", "lat": 10.8744, "lng": 106.8059},
]
_FEEDER_RADIUS = 0.005  # ~550 m
_DEFAULT_ORIGIN = 35  # Bến xe buýt Sài Gòn (central, many routes)


def _route_set(csv: str) -> set[str]:
    return {x.strip() for x in csv.split(",") if x.strip()}


def density(wh: Warehouse, filters: Mapping[str, str]) -> ChartResponse:
    """3.1 — boarding-density map (hexbin in the frontend)."""
    rows = repo.boarding_density(wh)
    total = sum(r["boardings"] for r in rows) or 1
    hot = sorted(rows, key=lambda r: -r["boardings"])[:5]
    top_share = 100 * sum(h["boardings"] for h in hot) / total
    return ChartResponse(
        theme="spatial",
        slug="3.1",
        title="A few central stops dominate the boarding map.",
        subtitle=f"Boarding density at every AFC-active stop, Jan–Mar 2026 · "
        f"top-5 stops carry {top_share:.0f}% of all boardings",
        series=rows,
        encoding={"lat": "lat", "lng": "lng", "weight": "boardings", "kind": "hexmap"},
        meta={"hot": hot, "top_share": round(top_share, 1)},
    )


def metro_sankey(wh: Warehouse, filters: Mapping[str, str]) -> ChartResponse:
    """3.2 — bus → Metro Line 1 feeder Sankey."""
    stops = repo.stops_with_routes(wh)
    nodes: list[str] = ["All bus boardings"]
    metro_idx: dict[str, int] = {}
    for m in METRO_L1:
        metro_idx[m["slug"]] = len(nodes)
        nodes.append(f"Metro · {m['name']}")
    route_idx: dict[str, int] = {}
    links: list[dict[str, Any]] = []
    routes_seen: set[str] = set()

    for m in METRO_L1:
        agg: dict[str, int] = {}
        for s in stops:
            if abs(s["lat"] - m["lat"]) >= _FEEDER_RADIUS or abs(s["lng"] - m["lng"]) >= _FEEDER_RADIUS:
                continue
            for rn in _route_set(s["routes_csv"]):
                if not rn.isdigit() and len(rn) > 5:
                    continue
                agg[rn] = agg.get(rn, 0) + s["boardings"]
        for rn, value in sorted(agg.items(), key=lambda kv: -kv[1])[:4]:
            routes_seen.add(rn)
            if rn not in route_idx:
                route_idx[rn] = len(nodes)
                nodes.append(f"Route {rn}")
            links.append({"source": 0, "target": route_idx[rn], "value": value, "route": rn})
            links.append({"source": route_idx[rn], "target": metro_idx[m["slug"]], "value": value, "route": rn})

    return ChartResponse(
        theme="spatial",
        slug="3.2",
        title="Many bus routes feed the Metro Line 1 corridor.",
        subtitle=f"Boardings at stops within 550 m of each Metro station, expanded to feeder "
        f"routes · {len(routes_seen)} feeder routes",
        series=links,
        encoding={"kind": "sankey", "source": "source", "target": "target", "value": "value"},
        meta={"nodes": nodes, "feeder_count": len(routes_seen)},
    )


def isochrone(wh: Warehouse, filters: Mapping[str, str]) -> ChartResponse:
    """3.4 — network-reachability isochrone (BFS over the route-sharing graph)."""
    try:
        origin_id = int(filters.get("origin", _DEFAULT_ORIGIN))
    except ValueError:
        origin_id = _DEFAULT_ORIGIN

    stops = {r["stop_id"]: {**r, "routes": _route_set(r["routes_csv"])} for r in repo.stops_with_routes(wh)}
    origin = stops.get(origin_id)
    if origin is None:
        return ChartResponse(
            theme="spatial", slug="3.4",
            title="Origin stop not found.", subtitle="",
            series=[], encoding={"kind": "map"}, meta={"origin": None},
        )

    origin_routes: set[str] = origin["routes"]
    band1 = {sid for sid, s in stops.items() if sid != origin_id and (s["routes"] & origin_routes)}
    transfer_routes = set(origin_routes)
    for sid in band1:
        transfer_routes |= stops[sid]["routes"]
    band2 = {
        sid
        for sid, s in stops.items()
        if sid != origin_id and sid not in band1 and (s["routes"] & transfer_routes)
    }

    def point(sid: int, band: int) -> dict[str, Any]:
        s = stops[sid]
        return {"stop_id": sid, "name": s["name"], "lat": s["lat"], "lng": s["lng"], "band": band}

    series = [point(origin_id, 0)] + [point(i, 1) for i in band1] + [point(i, 2) for i in band2]
    return ChartResponse(
        theme="spatial",
        slug="3.4",
        title="One transfer multiplies the reachable-stop count.",
        subtitle=f"Network-reachability isochrone from {str(origin['name'])[:30]} "
        f"(Phase-1 proxy over the route-sharing graph) · one transfer adds {len(band2):,} stops",
        series=series,
        encoding={"lat": "lat", "lng": "lng", "band": "band", "kind": "map"},
        meta={
            "origin": {"stop_id": origin_id, "name": origin["name"], "lat": origin["lat"], "lng": origin["lng"]},
            "band1_n": len(band1),
            "band2_n": len(band2),
        },
    )
