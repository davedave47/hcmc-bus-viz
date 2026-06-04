"""Layer 2 — Conformed Dimensions.

Ten dimension tables materialised once and shared across the L3 fact views
and the L4 aggregate tables. Pre-tags Vietnamese holidays (Tết Nguyên Đán,
April 30 / Labour Day window) so downstream code reads them as columns
instead of hard-coding date constants.

Every dimension is keyed by a stable primary identifier:
  dim_date            day            (DATE)
  dim_hour            hour           (INT 0..23)
  dim_route           route_no       (VARCHAR — canonical AFC route number)
  dim_stop            stop_id        (BIGINT — AFC stop id)
  dim_school          school_slug    (VARCHAR — 8 verified universities)
  dim_company         company_id     (BIGINT)
  dim_fare_class      fare_class     (VARCHAR — student/cash/free/other)
  dim_payment_channel channel_key    (VARCHAR — cash/smartcard/qr/emv/free)
  dim_vehicle         bus_id         (BIGINT)
  dim_promotion       promotion_code (VARCHAR — placeholder; mostly null)
"""
from __future__ import annotations

import logging
import time

import duckdb

log = logging.getLogger("warehouse.dims")

# Single-source-of-truth for the verified universities. The fact view and
# any per-school aggregate read from dim_school instead of importing this
# list at query time.
_UNIVERSITIES = [
    ("HCMUT",  "Bách Khoa",         506,  10.7726, 106.6577, True),
    ("HCMUS",  "KH Tự Nhiên",       474,  10.7623, 106.6831, True),
    ("UEH",    "Kinh Tế",           7701, 10.7062, 106.6394, True),
    ("GTVT",   "Giao Thông VT",     1405, 10.8066, 106.7160, True),
    ("USSH",   "KHXH & Nhân Văn",   1096, 10.7858, 106.7027, True),
    ("HCMUTE", "Sư Phạm Kỹ Thuật",  400,  10.8499, 106.7721, True),
    ("SGU",    "Sài Gòn",           467,  10.7607, 106.6823, True),
    ("UIT",    "CNTT (district)",   None, 10.8704, 106.8030, False),
]


def build_all(con: duckdb.DuckDBPyConnection) -> None:
    t0 = time.time()
    log.info("Layer 2 — conformed dimensions")
    build_dim_date(con)
    build_dim_hour(con)
    build_dim_route(con)
    build_dim_stop(con)
    build_dim_school(con)
    build_dim_school_stop(con)
    build_dim_trip(con)
    build_dim_company(con)
    build_dim_fare_class(con)
    build_dim_payment_channel(con)
    build_dim_vehicle(con)
    build_dim_promotion(con)
    log.info("L2 dims built in %.2fs", time.time() - t0)


def build_dim_date(con: duckdb.DuckDBPyConnection) -> None:
    """One row per day in the AFC window, with holiday and season tagging.

    Tết 2026 window (Feb 14–22) and the April 30–May 4 long-weekend window
    are flagged as boolean columns. The Tết window is computed empirically
    from the daily-volume profile in the AFC data."""
    log.info("  · dim_date")
    con.execute("""
        CREATE OR REPLACE TABLE dim_date AS
        WITH days AS (
          SELECT DISTINCT to_timestamp(time_created_ticket)::DATE AS day
          FROM tickets
        )
        SELECT
          day,
          extract(year   FROM day)::INT  AS year,
          extract(month  FROM day)::INT  AS month,
          extract(day    FROM day)::INT  AS day_of_month,
          extract(dow    FROM day)::INT  AS dow,
          extract(week   FROM day)::INT  AS iso_week,
          CASE WHEN extract(dow FROM day) IN (0, 6) THEN 'Weekend' ELSE 'Weekday' END
                                          AS day_type,
          -- Holidays / shock windows
          (day BETWEEN DATE '2026-02-14' AND DATE '2026-02-22')  AS is_tet_2026,
          (day = DATE '2026-02-16')                              AS is_tet_2026_trough,
          (day BETWEEN DATE '2026-01-08' AND DATE '2026-02-07')  AS is_pre_tet_baseline,
          (day BETWEEN DATE '2026-04-30' AND DATE '2026-05-04')  AS is_apr30_window,
          -- School term proxy: typical HCMC school year runs Sep–May with a
          -- short Tết break. The AFC window (Jan–Mar) sits entirely inside
          -- a school term, so this is mostly TRUE here; the column is added
          -- so Phase 2 multi-year analyses can flip it cleanly.
          TRUE                                                   AS is_school_term,
          -- Season label, mostly cosmetic
          CASE
            WHEN extract(month FROM day) IN (12, 1, 2) THEN 'Cool-dry'
            WHEN extract(month FROM day) IN (3, 4)     THEN 'Hot-dry'
            ELSE 'Wet'
          END                                                    AS season
        FROM days
        ORDER BY day
    """)
    n = con.execute("SELECT COUNT(*) FROM dim_date").fetchone()[0]
    nt = con.execute("SELECT COUNT(*) FROM dim_date WHERE is_tet_2026").fetchone()[0]
    log.info("     → %d days  (%d in Tết window)", n, nt)


def build_dim_hour(con: duckdb.DuckDBPyConnection) -> None:
    """0–23 with peak-window flags."""
    log.info("  · dim_hour")
    con.execute("""
        CREATE OR REPLACE TABLE dim_hour AS
        SELECT
          h AS hour,
          (h BETWEEN 6  AND 8)  AS is_morning_peak,
          (h BETWEEN 16 AND 18) AS is_evening_peak,
          (h BETWEEN 6  AND 8 OR h BETWEEN 16 AND 18) AS is_peak,
          CASE
            WHEN h BETWEEN 5  AND 11 THEN 'Morning'
            WHEN h BETWEEN 12 AND 13 THEN 'Midday'
            WHEN h BETWEEN 14 AND 18 THEN 'Afternoon'
            WHEN h BETWEEN 19 AND 22 THEN 'Evening'
            ELSE 'Late night'
          END                                       AS period
        FROM range(0, 24) AS t(h)
    """)


def build_dim_route(con: duckdb.DuckDBPyConnection) -> None:
    """Canonical AFC route catalogue, 1:1 on route_id (the JOIN key from
    dim_trip). Three route_ids in the raw table carry leading-zero variants
    of the same number (e.g. route_id=5 → '03' and '3'); we pick the
    no-leading-zero variant as canonical so the dim is unique on route_id.
    """
    log.info("  · dim_route")
    con.execute("""
        CREATE OR REPLACE TABLE dim_route AS
        WITH ranked AS (
          SELECT
            route_id,
            route_no,
            route_name,
            company_id,
            ROW_NUMBER() OVER (
              PARTITION BY route_id
              -- prefer the shortest (no-leading-zero) variant
              ORDER BY LENGTH(route_no), route_no
            ) AS rk
          FROM ticket_routes
          WHERE route_id IS NOT NULL AND route_no IS NOT NULL
        )
        SELECT route_id, route_no, route_name, company_id
        FROM ranked
        WHERE rk = 1
    """)
    n = con.execute("SELECT COUNT(*) FROM dim_route").fetchone()[0]
    log.info("     → %d routes (1-to-1 on route_id)", n)


def build_dim_stop(con: duckdb.DuckDBPyConnection) -> None:
    """Stop master keyed by stop_id."""
    log.info("  · dim_stop")
    con.execute("""
        CREATE OR REPLACE TABLE dim_stop AS
        SELECT
          stopId                  AS stop_id,
          stop_name               AS name,
          lat,
          lng,
          zone,
          ward,
          street,
          routes                  AS routes_csv,
          (lat BETWEEN 10.5 AND 11.2 AND lng BETWEEN 106.4 AND 107.0) AS in_bbox
        FROM stops
    """)
    n = con.execute("SELECT COUNT(*) FROM dim_stop").fetchone()[0]
    log.info("     → %d stops", n)


def build_dim_school(con: duckdb.DuckDBPyConnection) -> None:
    """Eight verified universities. Carries the verified flag so every
    school-aware chart can surface district-level stubs explicitly."""
    log.info("  · dim_school")
    con.execute("""
        CREATE OR REPLACE TABLE dim_school (
          school_slug VARCHAR,
          display     VARCHAR,
          stop_id     BIGINT,
          lat         DOUBLE,
          lng         DOUBLE,
          verified    BOOLEAN
        )
    """)
    con.execute("DELETE FROM dim_school")
    con.executemany(
        "INSERT INTO dim_school VALUES (?, ?, ?, ?, ?, ?)",
        _UNIVERSITIES,
    )


def build_dim_school_stop(con: duckdb.DuckDBPyConnection) -> None:
    """Bridge table: every stop within 500m walking-bbox of a verified
    university, deduplicated so each stop maps to AT MOST ONE school
    (the closest one by Euclidean distance). One-to-many on the school
    side; one-to-one on the stop side — critical for the fact_boardings
    LEFT JOIN to avoid row multiplication for stops near multiple
    universities (e.g. HCMUS and SGU sit ~300 m apart)."""
    log.info("  · dim_school_stop")
    con.execute("""
        CREATE OR REPLACE TABLE dim_school_stop AS
        WITH proximal AS (
          SELECT
            st.stop_id,
            sc.school_slug,
            POWER(st.lat - sc.lat, 2) + POWER(st.lng - sc.lng, 2) AS dist_sq,
            ROW_NUMBER() OVER (
              PARTITION BY st.stop_id
              ORDER BY POWER(st.lat - sc.lat, 2) + POWER(st.lng - sc.lng, 2)
            ) AS rk
          FROM dim_school sc
          JOIN dim_stop   st
            ON ABS(st.lat - sc.lat) < 0.0045
           AND ABS(st.lng - sc.lng) < 0.0046
        )
        SELECT school_slug, stop_id
        FROM proximal
        WHERE rk = 1
    """)
    n = con.execute("SELECT COUNT(*) FROM dim_school_stop").fetchone()[0]
    log.info("     → %d (school, stop) pairs (1-to-1 on stop)", n)


def build_dim_trip(con: duckdb.DuckDBPyConnection) -> None:
    """Trip dimension. ticket_trips has 4,051 trip_ids with > 1 row
    (verified) which would multiply the boarding join; this dim picks one
    canonical row per trip_id so fact_boardings stays at one row per
    ticket."""
    log.info("  · dim_trip (dedup)")
    con.execute("""
        CREATE OR REPLACE TABLE dim_trip AS
        SELECT
          trip_id,
          MIN(route_id)            AS route_id,
          MIN(bus_id)              AS bus_id,
          MIN(driver_license_number) AS driver_license_number
        FROM ticket_trips
        WHERE trip_id IS NOT NULL
        GROUP BY trip_id
    """)
    n = con.execute("SELECT COUNT(*) FROM dim_trip").fetchone()[0]
    log.info("     → %d trips", n)


def build_dim_company(con: duckdb.DuckDBPyConnection) -> None:
    log.info("  · dim_company")
    con.execute("""
        CREATE OR REPLACE TABLE dim_company AS
        SELECT * FROM ticket_companies
    """)


def build_dim_fare_class(con: duckdb.DuckDBPyConnection) -> None:
    """Canonical fare-class taxonomy. Every per-ticket query maps the raw
    `tickets.ticket_type` string into one of these four classes via
    fact_boardings.fare_class."""
    log.info("  · dim_fare_class")
    con.execute("""
        CREATE OR REPLACE TABLE dim_fare_class (
          fare_class    VARCHAR PRIMARY KEY,
          description   VARCHAR,
          is_subsidised BOOLEAN
        )
    """)
    con.execute("DELETE FROM dim_fare_class")
    con.executemany(
        "INSERT INTO dim_fare_class VALUES (?, ?, ?)",
        [
            ("student", "HS-SV student-fare ticket",        True),
            ("cash",    "Cash / smartcard standard fare",    False),
            ("free",    "Free or fully subsidised ticket",   True),
            ("other",   "Other / unclassified ticket type",  False),
        ],
    )


def build_dim_payment_channel(con: duckdb.DuckDBPyConnection) -> None:
    """Payment-method dimension, deduplicated from the raw payments
    stream. The four ≥99-percent-null payment fields (promotion_code,
    promotion_description, verification_qr, emv_card_id) are not surfaced
    here — they live on dim_promotion as a Phase-2 placeholder."""
    log.info("  · dim_payment_channel")
    con.execute("""
        CREATE OR REPLACE TABLE dim_payment_channel AS
        SELECT DISTINCT
          payment_method AS channel_key,
          payment_method AS description,
          (payment_method ILIKE '%miễn phí%') AS is_free
        FROM read_parquet('data/parquet/payments/*.parquet')
        WHERE payment_method IS NOT NULL
    """)
    n = con.execute("SELECT COUNT(*) FROM dim_payment_channel").fetchone()[0]
    log.info("     → %d channels", n)


def build_dim_vehicle(con: duckdb.DuckDBPyConnection) -> None:
    log.info("  · dim_vehicle")
    con.execute("""
        CREATE OR REPLACE TABLE dim_vehicle AS
        SELECT
          bus_id,
          vehicle_number,
          capacity,
          category
        FROM ticket_buses
    """)


def build_dim_promotion(con: duckdb.DuckDBPyConnection) -> None:
    """Phase-2 placeholder. The four payment-fields are ≥99% null in the
    Phase-1 release; the dimension is materialised empty so downstream
    joins remain valid."""
    log.info("  · dim_promotion (placeholder)")
    con.execute("""
        CREATE OR REPLACE TABLE dim_promotion (
          promotion_code        VARCHAR PRIMARY KEY,
          promotion_description VARCHAR
        )
    """)
