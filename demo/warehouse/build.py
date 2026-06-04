"""Warehouse builder — orchestrates L1 → L2 → L3 → L4.

Materialises:
  Layer 2 — 10 conformed dimensions (demo/warehouse/dims.py)
  Layer 3 — 3 fact views (demo/warehouse/facts.py)
  Layer 4 — 8 aggregate tables that back every chart in the demo

Run once whenever the raw parquet inputs change:
    python -m demo.warehouse.build
"""
from __future__ import annotations

import logging
import time
from pathlib import Path

import duckdb

from . import dims, facts, validate as validate_mod

logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s")
log = logging.getLogger("warehouse.build")

_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
DB_PATH = _PROJECT_ROOT / "db" / "bus.duckdb"


def _ensure_views_present(con: duckdb.DuckDBPyConnection) -> None:
    """Register the L1 parquet views the L2 / L3 builders read from."""
    pq = _PROJECT_ROOT / "data" / "parquet"
    if not pq.exists():
        raise FileNotFoundError(f"Parquet inputs missing at {pq}")
    direct = {
        "stops":            pq / "stops.parquet",
        "ticket_trips":     pq / "ticket_trips.parquet",
        "ticket_routes":    pq / "ticket_routes.parquet",
        "ticket_stations":  pq / "ticket_stations.parquet",
        "ticket_companies": pq / "ticket_companies.parquet",
        "ticket_buses":     pq / "ticket_buses.parquet",
        "gps_trips":        pq / "gps_trips.parquet",
        "gps_stop_times":   pq / "gps_stop_times.parquet",
    }
    for view, p in direct.items():
        if p.exists():
            con.execute(f"CREATE OR REPLACE VIEW {view} AS SELECT * FROM read_parquet('{p}')")
    tickets_dir = pq / "tickets"
    if tickets_dir.exists():
        con.execute(
            "CREATE OR REPLACE VIEW tickets AS "
            f"SELECT * FROM read_parquet('{tickets_dir}/*.parquet')"
        )
    payments_dir = pq / "payments"
    if payments_dir.exists():
        con.execute(
            "CREATE OR REPLACE VIEW payments AS "
            f"SELECT * FROM read_parquet('{payments_dir}/*.parquet')"
        )


# ─── Layer 4 — aggregate tables that back the chart catalogue ──────────────
# Names align with CLAUDE.md §9 where possible. Every aggregate reads from
# the L3 fact view fact_boardings (which itself reads from L1 + L2).

def build_agg_network_day(con: duckdb.DuckDBPyConnection) -> None:
    log.info("  · agg_network_day")
    t0 = time.time()
    con.execute("""
        CREATE OR REPLACE TABLE agg_network_day AS
        SELECT day, fare_class, COUNT(*) AS boardings
        FROM fact_boardings
        GROUP BY day, fare_class
        ORDER BY day, fare_class
    """)
    n = con.execute("SELECT COUNT(*) FROM agg_network_day").fetchone()[0]
    log.info("     → %s rows in %.2fs", f"{n:,}", time.time() - t0)


def build_agg_route_hour(con: duckdb.DuckDBPyConnection) -> None:
    log.info("  · agg_route_hour")
    t0 = time.time()
    con.execute("""
        CREATE OR REPLACE TABLE agg_route_hour AS
        SELECT
          route_no,
          extract(dow FROM day)::INT AS dow,
          hour,
          fare_class,
          COUNT(*) AS boardings
        FROM fact_boardings
        WHERE route_no IS NOT NULL
        GROUP BY 1, 2, 3, 4
    """)
    n = con.execute("SELECT COUNT(*) FROM agg_route_hour").fetchone()[0]
    log.info("     → %s rows in %.2fs", f"{n:,}", time.time() - t0)


def build_agg_route_day(con: duckdb.DuckDBPyConnection) -> None:
    log.info("  · agg_route_day")
    t0 = time.time()
    con.execute("""
        CREATE OR REPLACE TABLE agg_route_day AS
        SELECT
          route_no,
          day,
          fare_class,
          COUNT(*) AS boardings
        FROM fact_boardings
        WHERE route_no IS NOT NULL
        GROUP BY 1, 2, 3
    """)
    n = con.execute("SELECT COUNT(*) FROM agg_route_day").fetchone()[0]
    log.info("     → %s rows in %.2fs", f"{n:,}", time.time() - t0)


def build_agg_stop_hour(con: duckdb.DuckDBPyConnection) -> None:
    """Per-stop × dow × hour × fare-class. Supports the weekly heatmap and
    any future stop-level hour drill-down."""
    log.info("  · agg_stop_hour")
    t0 = time.time()
    con.execute("""
        CREATE OR REPLACE TABLE agg_stop_hour AS
        SELECT
          stop_id,
          extract(dow FROM day)::INT AS dow,
          hour,
          fare_class,
          COUNT(*) AS boardings
        FROM fact_boardings
        WHERE stop_id IS NOT NULL
        GROUP BY 1, 2, 3, 4
    """)
    n = con.execute("SELECT COUNT(*) FROM agg_stop_hour").fetchone()[0]
    log.info("     → %s rows in %.2fs", f"{n:,}", time.time() - t0)


def build_agg_stop_total(con: duckdb.DuckDBPyConnection) -> None:
    """Per-stop 90-day total with lat/lng denormalised — backs the spatial
    canvas density layer and the voronoi tessellation."""
    log.info("  · agg_stop_total")
    t0 = time.time()
    con.execute("""
        CREATE OR REPLACE TABLE agg_stop_total AS
        SELECT
          s.stop_id,
          s.name,
          s.lat,
          s.lng,
          COUNT(f.ticket_id) AS boardings
        FROM dim_stop s
        LEFT JOIN fact_boardings f USING (stop_id)
        WHERE s.in_bbox
        GROUP BY s.stop_id, s.name, s.lat, s.lng
    """)
    n = con.execute("SELECT COUNT(*) FROM agg_stop_total").fetchone()[0]
    log.info("     → %s rows in %.2fs", f"{n:,}", time.time() - t0)


def build_agg_school_route(con: duckdb.DuckDBPyConnection) -> None:
    log.info("  · agg_school_route")
    t0 = time.time()
    con.execute("""
        CREATE OR REPLACE TABLE agg_school_route AS
        SELECT
          school_slug AS uni_slug,
          route_no,
          fare_class,
          extract(dow FROM day)::INT AS dow,
          hour,
          COUNT(*) AS boardings
        FROM fact_boardings
        WHERE school_slug IS NOT NULL
        GROUP BY 1, 2, 3, 4, 5
    """)
    n = con.execute("SELECT COUNT(*) FROM agg_school_route").fetchone()[0]
    log.info("     → %s rows in %.2fs", f"{n:,}", time.time() - t0)


def build_agg_hub_kpis(con: duckdb.DuckDBPyConnection) -> None:
    """Single-row KPI aggregate for the hub stats strip."""
    log.info("  · agg_hub_kpis")
    t0 = time.time()
    con.execute("""
        CREATE OR REPLACE TABLE agg_hub_kpis AS
        WITH net AS (
          SELECT SUM(boardings) AS boardings,
                 100.0 * SUM(CASE WHEN fare_class='student' THEN boardings END)
                       / NULLIF(SUM(boardings), 0) AS student_share
          FROM agg_network_day
        ),
        rev AS (
          SELECT COALESCE(SUM(amount_money), 0) AS revenue FROM payments
        ),
        -- route_no is the canonical route identity (invariant #11); count the
        -- distinct AFC route numbers (128), not the 131 route_id rows that
        -- include leading-zero variants.
        r AS (SELECT COUNT(DISTINCT route_no) AS routes_n FROM ticket_routes),
        -- all stops with a coordinate (matches the EDA stop count), not just
        -- the AFC-active subset.
        s AS (SELECT COUNT(*) AS stops_n FROM stops
              WHERE lat IS NOT NULL AND lng IS NOT NULL)
        SELECT
          net.boardings, rev.revenue, net.student_share,
          r.routes_n, s.stops_n, 19 AS metro_feeders
        FROM net, rev, r, s
    """)
    row = con.execute("SELECT * FROM agg_hub_kpis").fetchone()
    log.info("     → boardings=%s revenue=%s share=%.1f%% routes=%d stops=%d in %.2fs",
             f"{int(row[0]):,}", f"{int(row[1]):,}", row[2], row[3], row[4],
             time.time() - t0)


def build_layer_4(con: duckdb.DuckDBPyConnection) -> None:
    t0 = time.time()
    log.info("Layer 4 — aggregate tables")
    build_agg_network_day(con)
    build_agg_route_hour(con)
    build_agg_route_day(con)
    build_agg_stop_hour(con)
    build_agg_stop_total(con)
    build_agg_school_route(con)
    build_agg_hub_kpis(con)
    log.info("L4 aggregates built in %.2fs", time.time() - t0)


def main() -> None:
    if not DB_PATH.exists():
        raise FileNotFoundError(f"Warehouse missing at {DB_PATH}")
    log.info("Opening %s read-write …", DB_PATH)
    con = duckdb.connect(str(DB_PATH))
    try:
        _ensure_views_present(con)
        dims.build_all(con)
        facts.build_all(con)
        build_layer_4(con)
        con.execute("CHECKPOINT")
        log.info("Warehouse build complete. Running validation harness …")
        log.info("─" * 72)
        validate_mod.validate(con, strict=True)
        log.info("Validation passed — warehouse is consistent.")
    finally:
        con.close()


if __name__ == "__main__":
    main()
