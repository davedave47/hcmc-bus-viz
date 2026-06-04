"""Card 3 — Spatial & Connectivity aggregates (L4-backed)."""
from __future__ import annotations

import functools

from .. import db

# Metro Line 1 stations — approximate centroids.
METRO_L1: list[dict] = [
    dict(slug="BTH", name="Bến Thành",          lat=10.7720, lng=106.6986),
    dict(slug="OPR", name="Nhà Hát Thành Phố",  lat=10.7765, lng=106.7029),
    dict(slug="BSO", name="Ba Son",             lat=10.7855, lng=106.7066),
    dict(slug="VTH", name="Văn Thánh",          lat=10.8004, lng=106.7158),
    dict(slug="TCG", name="Tân Cảng",           lat=10.7986, lng=106.7224),
    dict(slug="THD", name="Thảo Điền",          lat=10.8060, lng=106.7370),
    dict(slug="APH", name="An Phú",             lat=10.8076, lng=106.7475),
    dict(slug="RCH", name="Rạch Chiếc",         lat=10.8330, lng=106.7670),
    dict(slug="PLG", name="Phước Long",         lat=10.8480, lng=106.7707),
    dict(slug="BTI", name="Bình Thái",          lat=10.8519, lng=106.7733),
    dict(slug="TDC", name="Thủ Đức",            lat=10.8511, lng=106.7716),
    dict(slug="KCC", name="Khu Công Nghệ Cao",  lat=10.8568, lng=106.7901),
    dict(slug="DHQ", name="Đại Học Quốc Gia",   lat=10.8718, lng=106.8023),
    dict(slug="STI", name="Suối Tiên",          lat=10.8744, lng=106.8059),
]
_FEEDER_RADIUS_DEG = 0.005   # ~550 m


# 3.1 / 3.4 — boarding density per stop
@functools.lru_cache(maxsize=1)
def boarding_density_per_stop() -> list[dict]:
    rows = db.query("""
        SELECT stop_id, name, lat, lng, boardings
        FROM agg_stop_total
        WHERE boardings > 0
    """)
    return [dict(stop_id=int(r["stop_id"]), name=r["name"],
                 lat=float(r["lat"]), lng=float(r["lng"]),
                 boardings=int(r["boardings"])) for r in rows]


@functools.lru_cache(maxsize=1)
def top_hot_cells(n: int = 5) -> list[dict]:
    return sorted(boarding_density_per_stop(), key=lambda r: -r["boardings"])[:n]


# 3.2 — bus → metro feeder Sankey
@functools.lru_cache(maxsize=1)
def feeder_routes_to_metro() -> dict:
    out_links = []
    routes_seen = set()
    nodes = ["All bus boardings"]
    metro_node_index = {}
    for m in METRO_L1:
        metro_node_index[m["slug"]] = len(nodes)
        nodes.append(f"Metro · {m['name']}")
    route_node_index: dict[str, int] = {}

    for m in METRO_L1:
        rows = db.query(f"""
            SELECT s.stopId, s.routes, st.boardings
            FROM stops s
            JOIN agg_stop_total st ON st.stop_id = s.stopId
            WHERE s.lat BETWEEN {m['lat'] - _FEEDER_RADIUS_DEG} AND {m['lat'] + _FEEDER_RADIUS_DEG}
              AND s.lng BETWEEN {m['lng'] - _FEEDER_RADIUS_DEG} AND {m['lng'] + _FEEDER_RADIUS_DEG}
              AND s.routes IS NOT NULL
        """)
        agg: dict[str, int] = {}
        for r in rows:
            route_list = [x.strip() for x in (r["routes"] or "").split(",") if x.strip()]
            for rn in route_list:
                if not rn.isdigit() and len(rn) > 5:
                    continue
                agg[rn] = agg.get(rn, 0) + int(r["boardings"] or 0)
        for rn, v in sorted(agg.items(), key=lambda kv: -kv[1])[:4]:
            routes_seen.add(rn)
            if rn not in route_node_index:
                route_node_index[rn] = len(nodes)
                nodes.append(f"Route {rn}")
            out_links.append((0, route_node_index[rn], v, rn))
            out_links.append((route_node_index[rn], metro_node_index[m["slug"]], v, rn))

    return dict(nodes=nodes, links=out_links, feeder_count=len(routes_seen))


# 3.4 — stops for the voronoi tessellation (busy stops only) — retained
@functools.lru_cache(maxsize=1)
def stops_for_voronoi() -> list[dict]:
    return [r for r in boarding_density_per_stop() if r["boardings"] >= 1000]


# 3.4 (v5.5) — network-reachability isochrone from an origin stop.
# Phase-1 proxy: BFS over the route-sharing graph using the populated
# `stops.routes` field. Band 0 = origin; band 1 = stops sharing a route
# (≈ ≤ 15 min, no transfer); band 2 = one transfer away (≈ ≤ 30 min).
# True travel-time isochrone awaits the cleaned schedule (v5.5 §12, ⚙️).
DEFAULT_ISOCHRONE_ORIGIN = 35   # Bến xe buýt Sài Gòn (central, many routes)


@functools.lru_cache(maxsize=8)
def isochrone_from_origin(origin_stop_id: int = DEFAULT_ISOCHRONE_ORIGIN) -> dict:
    rows = db.query(
        """
        SELECT stopId, stop_name, lat, lng, routes
        FROM stops
        WHERE routes IS NOT NULL
          AND lat BETWEEN 10.5 AND 11.2 AND lng BETWEEN 106.4 AND 107.0
        """
    )
    def routeset(s: str | None) -> set[str]:
        return {x.strip() for x in (s or "").split(",") if x.strip()}

    stops = {int(r["stopId"]): dict(
        stop_id=int(r["stopId"]), name=r["stop_name"],
        lat=float(r["lat"]), lng=float(r["lng"]), routes=routeset(r["routes"]),
    ) for r in rows}

    origin = stops.get(origin_stop_id)
    if origin is None:
        return dict(origin=None, bands=[])

    origin_routes = origin["routes"]
    # Band 1: stops sharing any route with the origin
    band1_ids = {sid for sid, s in stops.items()
                 if sid != origin_stop_id and (s["routes"] & origin_routes)}
    # Expand the route set with band-1 stops' routes (one transfer)
    transfer_routes = set(origin_routes)
    for sid in band1_ids:
        transfer_routes |= stops[sid]["routes"]
    # Band 2: stops reachable via the expanded route set, not already in band 1
    band2_ids = {sid for sid, s in stops.items()
                 if sid != origin_stop_id and sid not in band1_ids
                 and (s["routes"] & transfer_routes)}

    def pack(ids: set[int]) -> list[dict]:
        return [dict(stop_id=stops[i]["stop_id"], name=stops[i]["name"],
                     lat=stops[i]["lat"], lng=stops[i]["lng"]) for i in ids]

    return dict(
        origin=dict(stop_id=origin["stop_id"], name=origin["name"],
                    lat=origin["lat"], lng=origin["lng"]),
        band1=pack(band1_ids),
        band2=pack(band2_ids),
        band1_n=len(band1_ids),
        band2_n=len(band2_ids),
    )
