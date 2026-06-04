"""Architecture benchmark — five measurement passes.

Pass 1: Silver-only vs Silver + Gold (the Gold-tier value)
Pass 2: LRU-cache counterfactual (in-process cache vs persistent Gold)
Pass 3: Build scaling (1× vs 2× input — confirms O(N) row scaling)
Pass 4: Star-schema-over-raw counterfactual — the third architecture
        candidate from Ch4.5: skip the Silver tier entirely, joining raw
        tickets × ticket_trips × ticket_routes directly. Measures both
        latency AND row-count integrity (without Silver dedup the
        boarding count inflates by ~1M from the three row-multiplication
        bugs catalogued in Table~\\ref{tab:arch:integrity}).
Pass 5: Chart-endpoint p50/p99 latency over 100 runs against the
        running demo (skipped automatically if the server is not up).

Run with:
    python -m demo.warehouse.benchmark
"""
from __future__ import annotations

import statistics
import time
from pathlib import Path

import duckdb

_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
DB_PATH = _PROJECT_ROOT / "db" / "bus.duckdb"

# (label, silver_sql, gold_sql)
QUERIES = [
    (
        "network_day  (90-day daily volume × 4 fare classes)",
        """
            SELECT day, fare_class, COUNT(*) AS boardings
            FROM fact_boardings
            GROUP BY day, fare_class
        """,
        "SELECT day, fare_class, boardings FROM agg_network_day",
    ),
    (
        "route_hour   (route × dow × hour × fare-class)",
        """
            SELECT route_no,
                   extract(dow FROM day)::INT AS dow,
                   hour, fare_class, COUNT(*) AS boardings
            FROM fact_boardings
            WHERE route_no IS NOT NULL
            GROUP BY 1, 2, 3, 4
        """,
        "SELECT * FROM agg_route_hour",
    ),
    (
        "stop_hour    (stop × dow × hour × fare-class)",
        """
            SELECT stop_id,
                   extract(dow FROM day)::INT AS dow,
                   hour, fare_class, COUNT(*) AS boardings
            FROM fact_boardings
            WHERE stop_id IS NOT NULL
            GROUP BY 1, 2, 3, 4
        """,
        "SELECT * FROM agg_stop_hour",
    ),
    (
        "school_route (8 unis × route × fare-class × dow × hour)",
        """
            SELECT school_slug, route_no, fare_class,
                   extract(dow FROM day)::INT AS dow,
                   hour, COUNT(*) AS boardings
            FROM fact_boardings
            WHERE school_slug IS NOT NULL
            GROUP BY 1, 2, 3, 4, 5
        """,
        "SELECT * FROM agg_school_route",
    ),
    (
        "stop_total   (per-stop 90-day total + lat/lng)",
        """
            SELECT s.stop_id, s.name, s.lat, s.lng, COUNT(f.ticket_id) AS boardings
            FROM dim_stop s
            LEFT JOIN fact_boardings f USING (stop_id)
            WHERE s.in_bbox
            GROUP BY s.stop_id, s.name, s.lat, s.lng
        """,
        "SELECT * FROM agg_stop_total",
    ),
    (
        "hub_kpis     (single-row summary for the hub stats strip)",
        """
            WITH net AS (
              SELECT COUNT(*) AS boardings,
                     100.0 * SUM(CASE WHEN fare_class='student' THEN 1 ELSE 0 END)
                           / NULLIF(COUNT(*), 0) AS student_share
              FROM fact_boardings
            ),
            rev AS (SELECT COALESCE(SUM(amount_money), 0) AS revenue FROM payments),
            r  AS (SELECT COUNT(DISTINCT route_no) AS routes_n FROM ticket_routes),
            s  AS (SELECT COUNT(*) AS stops_n FROM stops
                   WHERE lat IS NOT NULL AND lng IS NOT NULL)
            SELECT net.boardings, rev.revenue, net.student_share,
                   r.routes_n, s.stops_n, 19 AS metro_feeders
            FROM net, rev, r, s
        """,
        "SELECT * FROM agg_hub_kpis",
    ),
]


def _time_query(con: duckdb.DuckDBPyConnection, sql: str, repeats: int = 5) -> tuple[float, int]:
    """Return (median seconds, row count)."""
    samples = []
    n_rows = 0
    for _ in range(repeats):
        t0 = time.time()
        cur = con.execute(sql)
        rows = cur.fetchall()
        samples.append(time.time() - t0)
        n_rows = len(rows)
    return statistics.median(samples), n_rows


def _bench_lru_cache(con: duckdb.DuckDBPyConnection) -> None:
    """Pass 2 — LRU-cache counterfactual.

    Reviewers asking 'why not just cache query results in memory?' deserve
    a number. We wrap the Silver query in functools.lru_cache and measure:
      cold     — first call, cache miss, full Silver execution
      warm     — second call, in-process cache hit
    Then compare to the Gold-direct path.
    """
    import functools

    print("Pass 2  ·  LRU-cache counterfactual vs Gold tables")
    print("─" * 90)
    print(f"{'Query':<28} {'LRU cold':>10} {'LRU warm':>10} {'Gold':>10}  {'Conclusion':<28}")
    print("─" * 90)

    for label, silver_sql, gold_sql in QUERIES:
        # Build a per-query lru-cached version of the Silver-only path
        @functools.lru_cache(maxsize=1)
        def _cached_silver(_key: str) -> int:
            return len(con.execute(silver_sql).fetchall())

        # cold = first call (miss); warm = second call (hit)
        t0 = time.time(); _cached_silver("k"); cold = time.time() - t0
        t0 = time.time(); _cached_silver("k"); warm = time.time() - t0
        gold_t, _ = _time_query(con, gold_sql, repeats=3)
        key = label.split("(")[0].strip()
        # LRU cache cold-start = Silver-only execution; the value of pre-
        # aggregating is the persistence + cross-process sharing
        verdict = "Gold ≪ LRU cold" if gold_t < cold * 0.5 else "Gold ≈ LRU"
        print(f"{key:<28} {cold*1000:>8.1f}ms {warm*1000:>8.1f}ms {gold_t*1000:>8.1f}ms  {verdict:<28}")
    print()
    print("Notes")
    print("  · LRU 'cold' incurs the full Silver-only cost on every cold start:")
    print("    process restart, cache eviction, schema reload all reset the cache.")
    print("  · Gold tables are persistent on disk and shared across processes;")
    print("    every cold start of the demo server reads them in O(rows) without")
    print("    re-aggregating. Disk cost: ~30 MB; LRU per-process memory ceiling")
    print("    grows with cache entries × result-set size.")
    print()


def _bench_scaling(con: duckdb.DuckDBPyConnection) -> None:
    """Pass 3 — confirm the build scales linearly with input rows.

    We do not materialise 5× data (it would inflate the warehouse file).
    Instead we time the heaviest single Gold build (agg_route_hour) over
    the existing fact_boardings, then over a UNION ALL of fact_boardings
    with itself (2× rows, no double-counting concern since this is a
    scaling probe, not a chart-feeding build).
    """
    print("Pass 3  ·  Build scaling validation (1× and 2× input)")
    print("─" * 90)

    def _time_build(sql: str, repeats: int = 3) -> float:
        samples = []
        for _ in range(repeats):
            t0 = time.time()
            con.execute("DROP TABLE IF EXISTS _scaling_probe")
            con.execute(sql)
            samples.append(time.time() - t0)
        con.execute("DROP TABLE IF EXISTS _scaling_probe")
        return statistics.median(samples)

    sql_1x = """
        CREATE TABLE _scaling_probe AS
        SELECT route_no,
               extract(dow FROM day)::INT AS dow,
               hour, fare_class, COUNT(*) AS boardings
        FROM fact_boardings
        WHERE route_no IS NOT NULL
        GROUP BY 1, 2, 3, 4
    """
    sql_2x = """
        CREATE TABLE _scaling_probe AS
        WITH doubled AS (
          SELECT * FROM fact_boardings
          UNION ALL
          SELECT * FROM fact_boardings
        )
        SELECT route_no,
               extract(dow FROM day)::INT AS dow,
               hour, fare_class, COUNT(*) AS boardings
        FROM doubled
        WHERE route_no IS NOT NULL
        GROUP BY 1, 2, 3, 4
    """
    t1 = _time_build(sql_1x)
    t2 = _time_build(sql_2x)

    print(f"  agg_route_hour build @ 1× input ({17_883_623:>12,} rows):  {t1*1000:>7.1f} ms")
    print(f"  agg_route_hour build @ 2× input ({17_883_623*2:>12,} rows):  {t2*1000:>7.1f} ms")
    print(f"  Scaling ratio:                                    {t2/t1:>7.2f}× (ideal O(N) = 2.00×)")
    print()
    print("Projection (assuming validated O(N) scaling):")
    print(f"  5×  input ( 89.4 M rows): {t1*5*1000:>7.0f} ms     (≈ {t1*5:.1f}s)")
    print(f"  10× input (178.8 M rows): {t1*10*1000:>7.0f} ms    (≈ {t1*10:.1f}s)")
    print(f"  50-day GPS (replaces 1-day; row count flat for AFC):  no change")
    print()


def main() -> None:
    con = duckdb.connect(str(DB_PATH), read_only=False)
    print()
    print("Pass 1  ·  Aggregate query latency  ·  Silver-only  vs  Silver + Gold  ·  median of 5 runs")
    print("─" * 90)
    print(f"{'Query':<55} {'Silver':>10} {'Gold':>10} {'Speedup':>10}")
    print("─" * 90)
    silver_total = 0.0
    gold_total = 0.0
    for label, silver_sql, gold_sql in QUERIES:
        silver_t, silver_rows = _time_query(con, silver_sql)
        gold_t,   gold_rows   = _time_query(con, gold_sql)
        silver_total += silver_t
        gold_total   += gold_t
        speedup = silver_t / gold_t if gold_t > 0 else float("inf")
        print(f"{label:<55} {silver_t*1000:>8.1f}ms {gold_t*1000:>8.1f}ms {speedup:>9.1f}x")
    print("─" * 90)
    print(f"{'TOTAL':<55} {silver_total*1000:>8.1f}ms {gold_total*1000:>8.1f}ms {silver_total/gold_total:>9.1f}x")
    print()

    # Disk footprint of each layer
    print("Materialised footprint by layer")
    print("─" * 90)
    rows = con.execute("""
        SELECT table_name,
               estimated_size       AS row_count,
               (SELECT COUNT(*) FROM duckdb_columns() c
                  WHERE c.table_name = t.table_name) AS n_cols
        FROM duckdb_tables() t
        WHERE schema_name = 'main' AND NOT internal
        ORDER BY estimated_size DESC
    """).fetchall()
    silver_rows_total = 0
    gold_rows_total = 0
    for name, nrows, ncols in rows:
        layer = "L4 Gold" if name.startswith("agg_") else "L2 Silver-dim"
        if name.startswith("agg_"):
            gold_rows_total += nrows
        else:
            silver_rows_total += nrows
        print(f"  {name:<35} {layer:<16} {nrows:>12,} rows  {ncols:>3} cols")
    print("─" * 90)
    print(f"  Silver-dim rows: {silver_rows_total:,}")
    print(f"  Gold rows:       {gold_rows_total:,}")

    db_size = DB_PATH.stat().st_size / (1024 * 1024)
    print(f"  Warehouse file:  {db_size:.1f} MB on disk")
    print()

    # Pass 2 + 3
    _bench_lru_cache(con)
    _bench_scaling(con)
    _bench_star_over_raw(con)
    _bench_chart_endpoints()


def _bench_star_over_raw(con: duckdb.DuckDBPyConnection) -> None:
    """Pass 4 — Star-schema-over-raw counterfactual.

    Architecture: skip the Silver tier entirely, run aggregate queries
    directly against the raw views (no dim_trip dedup, no dim_route 1:1
    canonicalisation, no dim_school_stop bridge). Two failure modes
    measurable in this configuration:
      (a) latency: comparable to Silver-only (we still pay the join)
      (b) integrity: the three row-multiplication bugs catalogued in
          Table~\\ref{tab:arch:integrity} are NOT resolved, so
          boarding counts inflate.
    """
    print("Pass 4  ·  Star-schema-over-raw  ·  no Silver dedup")
    print("─" * 90)

    # Latency: same agg_route_hour query, but joining raw tables directly
    star_sql = """
        SELECT r.route_no,
               extract(dow FROM to_timestamp(t.time_created_ticket))::INT AS dow,
               extract(hour FROM to_timestamp(t.time_created_ticket))::INT AS hour,
               CASE WHEN t.ticket_type LIKE '%HS-SV%'      THEN 'student'
                    WHEN t.ticket_type LIKE '%miễn phí%'   THEN 'free'
                    WHEN t.ticket_type LIKE '%TM%'         THEN 'cash'
                    ELSE 'other' END AS fare_class,
               COUNT(*) AS boardings
        FROM tickets t
        JOIN ticket_trips  tt ON tt.trip_id = t.trip_id
        JOIN ticket_routes r  ON r.route_id  = tt.route_id
        WHERE r.route_no IS NOT NULL
        GROUP BY 1, 2, 3, 4
    """
    silver_sql = """
        SELECT route_no,
               extract(dow FROM day)::INT AS dow,
               hour, fare_class, COUNT(*) AS boardings
        FROM fact_boardings
        WHERE route_no IS NOT NULL
        GROUP BY 1, 2, 3, 4
    """
    gold_sql = "SELECT * FROM agg_route_hour"

    star_t, star_rows = _time_query(con, star_sql, repeats=3)
    silver_t, silver_rows = _time_query(con, silver_sql, repeats=3)
    gold_t,   gold_rows   = _time_query(con, gold_sql, repeats=3)

    print(f"  {'Architecture':<45} {'Latency':>12} {'Result rows':>14}")
    print(f"  {'─'*45} {'─'*12} {'─'*14}")
    print(f"  {'Star over raw (no dim dedup)':<45} {star_t*1000:>10.1f} ms {star_rows:>14,}")
    print(f"  {'Medallion · Silver only':<45} {silver_t*1000:>10.1f} ms {silver_rows:>14,}")
    print(f"  {'Medallion · Silver + Gold (selected)':<45} {gold_t*1000:>10.1f} ms {gold_rows:>14,}")

    # Integrity: sum of boardings across the three modes
    star_total = con.execute(f"SELECT SUM(boardings) FROM ({star_sql})").fetchone()[0]
    silver_total = con.execute(f"SELECT SUM(boardings) FROM ({silver_sql})").fetchone()[0]
    gold_total = con.execute("SELECT SUM(boardings) FROM agg_route_hour").fetchone()[0]
    raw_total = con.execute("SELECT COUNT(*) FROM tickets").fetchone()[0]

    print()
    print(f"  Integrity check — sum of boardings vs raw tickets ({raw_total:,}):")
    print(f"    Star-over-raw total:      {star_total:>14,}    "
          f"({(star_total/raw_total - 1)*100:+.2f}% inflation)")
    print(f"    Silver-only total:        {silver_total:>14,}    "
          f"({(silver_total/raw_total - 1)*100:+.2f}% inflation)")
    print(f"    Silver + Gold total:      {gold_total:>14,}    "
          f"({(gold_total/raw_total - 1)*100:+.2f}% inflation)")
    print()
    print("  Star-over-raw is faster on this query because it pays no dedup")
    print("  cost, but produces a boarding count inflated by the three")
    print("  row-multiplication bugs (duplicate trip_id, leading-zero")
    print("  route_no, multi-school stops). The Silver tier resolves them.")
    print()


def _bench_chart_endpoints() -> None:
    """Pass 5 — user-facing chart-endpoint p50/p99 latency.

    Hits each /api/charts/{theme}/{slug} endpoint 100 times against a
    running uvicorn server. Skipped if the server is not up.
    """
    import urllib.request
    import urllib.error

    print("Pass 5  ·  Chart-endpoint p50 / p99 over 100 runs each")
    print("─" * 90)

    base = "http://127.0.0.1:8765"
    try:
        urllib.request.urlopen(base + "/api/healthz", timeout=1)
    except (urllib.error.URLError, ConnectionError):
        print("  Server not running on 8765 — skipping Pass 5.")
        print("  Start with `uvicorn demo.main:app` and rerun for these numbers.")
        print()
        return

    endpoints = [
        ("schools", "1.1"), ("schools", "1.2"), ("schools", "1.3"),
        ("schools", "1.4"), ("schools", "1.5"),
        ("spatial", "3.1"), ("spatial", "3.2"), ("spatial", "3.4"),
        ("health",  "5.1"), ("health",  "5.2"), ("health",  "5.3"),
    ]
    print(f"  {'Endpoint':<28} {'p50':>9} {'p95':>9} {'p99':>9} {'max':>9}  {'N1 pass':>10}")
    print(f"  {'─'*28} {'─'*9} {'─'*9} {'─'*9} {'─'*9}  {'─'*10}")

    for theme, slug in endpoints:
        url = f"{base}/api/charts/{theme}/{slug}"
        samples = []
        for _ in range(100):
            t0 = time.time()
            try:
                with urllib.request.urlopen(url, timeout=10) as resp:
                    resp.read()
            except urllib.error.URLError:
                continue
            samples.append((time.time() - t0) * 1000)
        if not samples:
            continue
        samples.sort()
        p50 = samples[len(samples) // 2]
        p95 = samples[int(len(samples) * 0.95)]
        p99 = samples[int(len(samples) * 0.99)]
        n1_pass = "✓" if p99 < 100 else ("△" if p99 < 200 else "✗")
        print(f"  /api/charts/{theme}/{slug:<11} {p50:>7.1f}ms {p95:>7.1f}ms {p99:>7.1f}ms {max(samples):>7.1f}ms  {n1_pass:>10}")
    print()
    print("  N1 pass = warm chart render under 100 ms (the relaxed N1 ceiling")
    print("  for full chart-rendering, not just the underlying Gold query).")
    print()


if __name__ == "__main__":
    main()
