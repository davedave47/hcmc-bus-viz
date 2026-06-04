"""
Measured warm-render latency benchmark on Layer 1 (raw parquet views).

Question: For the worst-case chart query in the catalogue --- the
route-by-hour heatmap of the Demand and Crowding theme, which aggregates
the full 17.9 M-row AFC boarding stream by route x hour x day-type ---
what is the actual per-chart warm-render latency on the locally
available Layer-1 build?

Method: Open a persistent DuckDB connection, register the parquet view
layer, warm the engine with one throwaway scan, then issue the
chart-driving query 30 times. Report p50, p90, p99 in milliseconds.
This stands in for the projected numbers reported in Table 4.11 of the
capstone report.

This benchmark is Phase-1 evidence. The four-layer architecture
selection is justified if its measured Layer-1 latency already lies
beyond the N1 budget, since the Layer-4 aggregate path it specifies
will only be faster.
"""

from __future__ import annotations

import statistics
import time
from pathlib import Path

import duckdb

ROOT = Path(__file__).resolve().parents[1]
PARQUET_DIR = ROOT / "data" / "parquet"


def setup_views(con: duckdb.DuckDBPyConnection) -> None:
    """Register the Layer-1 raw views from the parquet directory."""
    for path in sorted(PARQUET_DIR.glob("*.parquet")):
        view_name = path.stem
        con.execute(
            f"CREATE OR REPLACE VIEW {view_name} AS "
            f"SELECT * FROM read_parquet('{path}')"
        )
    # tickets is stored as month-partitioned parquet to bound peak memory
    tickets_glob = str(PARQUET_DIR / "tickets_partitioned" / "*.parquet")
    con.execute(
        f"CREATE OR REPLACE VIEW tickets AS "
        f"SELECT * FROM read_parquet('{tickets_glob}', union_by_name=true)"
    )


def warm_engine(con: duckdb.DuckDBPyConnection) -> None:
    """One throwaway scan so cold-start cost is not attributed to the query."""
    con.execute("SELECT COUNT(*) FROM tickets").fetchone()
    con.execute("SELECT COUNT(*) FROM payments").fetchone()


def time_query(con: duckdb.DuckDBPyConnection, sql: str, repeats: int = 30) -> list[float]:
    samples_ms: list[float] = []
    for _ in range(repeats):
        t0 = time.perf_counter()
        con.execute(sql).fetchall()
        samples_ms.append((time.perf_counter() - t0) * 1000.0)
    return samples_ms


def percentile(samples: list[float], p: float) -> float:
    if not samples:
        return float("nan")
    s = sorted(samples)
    k = max(0, min(len(s) - 1, int(round(p * (len(s) - 1)))))
    return s[k]


def summary(name: str, samples: list[float]) -> dict:
    return {
        "query": name,
        "n": len(samples),
        "p50_ms": round(percentile(samples, 0.50), 2),
        "p90_ms": round(percentile(samples, 0.90), 2),
        "p99_ms": round(percentile(samples, 0.99), 2),
        "min_ms": round(min(samples), 2),
        "max_ms": round(max(samples), 2),
        "mean_ms": round(statistics.mean(samples), 2),
    }


# --- Queries ----------------------------------------------------------------

Q_ROUTE_HOUR = """
SELECT
  tt.route_id,
  EXTRACT(hour FROM TO_TIMESTAMP(t.time_created_ticket)) AS hour,
  CASE WHEN EXTRACT(dow FROM TO_TIMESTAMP(t.time_created_ticket)) IN (0, 6)
       THEN 'weekend' ELSE 'weekday' END AS day_type,
  COUNT(*) AS boardings
FROM tickets t
JOIN ticket_trips tt ON tt.trip_id = t.trip_id
GROUP BY 1, 2, 3
"""

# Same query restricted to a single day --- closer to a warm chart re-render
# with a date predicate filter, which is the actual N1-budget pattern.
Q_ROUTE_HOUR_ONE_DAY = """
SELECT
  tt.route_id,
  EXTRACT(hour FROM TO_TIMESTAMP(t.time_created_ticket)) AS hour,
  COUNT(*) AS boardings
FROM tickets t
JOIN ticket_trips tt ON tt.trip_id = t.trip_id
WHERE CAST(TO_TIMESTAMP(t.time_created_ticket) AS DATE) = DATE '2026-01-15'
GROUP BY 1, 2
"""

# A simpler aggregate close to what a Layer-4 pre-computed aggregate
# would deliver: just count boardings per route over the full window.
Q_ROUTE_TOTAL = """
SELECT
  tt.route_id,
  COUNT(*) AS boardings
FROM tickets t
JOIN ticket_trips tt ON tt.trip_id = t.trip_id
GROUP BY 1
"""


def main() -> None:
    print(f"Connecting to in-process DuckDB; reading from {PARQUET_DIR}")
    con = duckdb.connect()
    setup_views(con)
    warm_engine(con)

    print("\nRow counts:")
    print(f"  tickets:        {con.execute('SELECT COUNT(*) FROM tickets').fetchone()[0]:>12,}")
    print(f"  payments:       {con.execute('SELECT COUNT(*) FROM payments').fetchone()[0]:>12,}")
    print(f"  ticket_trips:   {con.execute('SELECT COUNT(*) FROM ticket_trips').fetchone()[0]:>12,}")

    print("\nLayer-1 raw-view query latencies (in-process DuckDB, locally available data):")
    rows = []
    for name, sql in [
        ("Q_ROUTE_HOUR (90-day route x hour x day-type)", Q_ROUTE_HOUR),
        ("Q_ROUTE_HOUR_ONE_DAY (single-day filter)", Q_ROUTE_HOUR_ONE_DAY),
        ("Q_ROUTE_TOTAL (per-route lifetime count)", Q_ROUTE_TOTAL),
    ]:
        samples = time_query(con, sql, repeats=30)
        rows.append(summary(name, samples))

    print()
    print(f"{'query':<55}  {'n':>3}  {'p50':>8}  {'p90':>8}  {'p99':>8}  {'min':>7}  {'max':>8}")
    for r in rows:
        print(
            f"{r['query']:<55}  "
            f"{r['n']:>3}  "
            f"{r['p50_ms']:>7.2f}ms  "
            f"{r['p90_ms']:>7.2f}ms  "
            f"{r['p99_ms']:>7.2f}ms  "
            f"{r['min_ms']:>6.2f}ms  "
            f"{r['max_ms']:>7.2f}ms"
        )

    # Persist as machine-readable record for the report appendix
    import json
    out_path = Path(__file__).resolve().parent / "06_latency_benchmark.json"
    record = {
        "duckdb_version": duckdb.__version__,
        "host": "single workstation, no GPU; in-process",
        "rows": rows,
    }
    out_path.write_text(json.dumps(record, indent=2))
    print(f"\nSaved record to {out_path}")


if __name__ == "__main__":
    main()
