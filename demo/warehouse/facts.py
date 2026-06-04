"""Layer 3 — Fact Views.

Three views that re-shape the raw operational streams through L2 dimensions.
Defined as VIEWS (not materialised) because:

  * DuckDB pushes predicate filters down through views, so an aggregate
    that filters on `fare_class = 'student'` reads only the matching
    partition of the underlying parquet — no fact-table copy needed.
  * Materialising fact_boardings would duplicate the 17.88M-row ticket
    stream (~200 MB) on disk for no behaviour change; the L4 aggregates
    already cover the read-hot paths.

The three views establish the dimensional surface contract:

  fact_boardings    one row per boarding event, joined to dim_date,
                    dim_hour, dim_route, dim_stop, dim_fare_class.
  fact_gps_trips    one row per GPS-extracted trip (Phase-2 wiring).
  fact_stop_visits  one row per GPS visit at a stop (Phase-2 wiring;
                    awaits the full 50-day GPS pull).
"""
from __future__ import annotations

import logging
import time

import duckdb

log = logging.getLogger("warehouse.facts")


def build_all(con: duckdb.DuckDBPyConnection) -> None:
    t0 = time.time()
    log.info("Layer 3 — fact views")
    build_fact_boardings(con)
    build_fact_gps_trips(con)
    build_fact_stop_visits(con)
    log.info("L3 facts built in %.2fs", time.time() - t0)


def build_fact_boardings(con: duckdb.DuckDBPyConnection) -> None:
    """Single row per boarding event with foreign keys to L2 dims.

    Joins are done through the deduplicated dim_trip (raw ticket_trips has
    4,051 multi-row trip_ids) and the dim_school_stop bridge (replaces a
    correlated subquery that was ~100× slower). One row per ticket.
    """
    log.info("  · fact_boardings (view)")
    con.execute("""
        CREATE OR REPLACE VIEW fact_boardings AS
        SELECT
          t.ticket_id,
          to_timestamp(t.time_created_ticket)::DATE       AS day,
          extract(hour FROM to_timestamp(t.time_created_ticket))::INT
                                                          AS hour,
          r.route_no,
          t.station_id                                    AS stop_id,
          CASE
            WHEN t.ticket_type LIKE '%HS-SV%'           THEN 'student'
            WHEN t.ticket_type LIKE '%miễn phí%'        THEN 'free'
            WHEN t.ticket_type LIKE '%TM%'              THEN 'cash'
            ELSE                                              'other'
          END                                             AS fare_class,
          dt.bus_id                                       AS bus_id,
          ss.school_slug                                  AS school_slug
        FROM tickets       t
        LEFT JOIN dim_trip dt ON dt.trip_id = t.trip_id
        LEFT JOIN dim_route r ON r.route_id  = dt.route_id
        LEFT JOIN dim_school_stop ss ON ss.stop_id = t.station_id
    """)


def build_fact_gps_trips(con: duckdb.DuckDBPyConnection) -> None:
    """One row per GPS-extracted trip. Phase 1 uses the locally available
    single-day extract; Phase 2 ingests the full 50-day Kaggle GPS. The
    view also resolves the GPS-side route_id to the canonical route_no
    via dim_route, so Phase-2 cross-source aggregates can join cleanly."""
    log.info("  · fact_gps_trips (view)")
    con.execute("""
        CREATE OR REPLACE VIEW fact_gps_trips AS
        SELECT
          g.trip_id,
          g.route_id        AS gps_route_id,
          r.route_no        AS route_no,
          g.direction,
          g.vehicle_id,
          g.driver_id,
          g.date            AS day,
          g.start_time,
          g.end_time,
          g.travel_time
        FROM gps_trips g
        LEFT JOIN dim_route r ON r.route_id = g.route_id
    """)


def build_fact_stop_visits(con: duckdb.DuckDBPyConnection) -> None:
    """One row per GPS visit at a stop. The underlying gps_stop_times view
    is registered; the empirical visit detection (dwell ≥ 10 s + door-open
    proxy) is Phase 2 work."""
    log.info("  · fact_stop_visits (view)")
    con.execute("""
        CREATE OR REPLACE VIEW fact_stop_visits AS
        SELECT
          trip_id,
          station_id       AS stop_id,
          "order"          AS stop_order,
          arrival_time,
          departure_time,
          dwell_time       AS dwell_seconds
        FROM gps_stop_times
    """)
