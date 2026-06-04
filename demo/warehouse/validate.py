"""Warehouse validation harness.

Asserts the integrity guarantees the report claims for the Medallion
warehouse. Run standalone (raises on first hard failure):

    python -m demo.warehouse.validate

Or call validate(con, strict=False) from the build to log warnings without
halting. Checks are grouped:

  A. Presence        — every L2 dim and L4 aggregate table exists
  B. Row counts      — dims have the expected cardinality
  C. Key uniqueness  — the 1:1 dims really are 1:1 on their join key
  D. Lossless chain  — Bronze ticket count == Gold boarding count (exact)
  E. Referential     — Gold foreign keys resolve into the dims
  F. Domain / null   — fare_class domain, stop bbox, no null calendar days
"""
from __future__ import annotations

import logging
import sys
from dataclasses import dataclass, field
from pathlib import Path

import duckdb

logging.basicConfig(level=logging.INFO, format="%(levelname)s | %(message)s")
log = logging.getLogger("warehouse.validate")

_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
DB_PATH = _PROJECT_ROOT / "db" / "bus.duckdb"

RAW_TICKETS = 17_883_623   # the locked Bronze baseline

L2_DIMS = ["dim_date", "dim_hour", "dim_route", "dim_stop", "dim_school",
           "dim_school_stop", "dim_trip", "dim_company", "dim_fare_class",
           "dim_payment_channel", "dim_vehicle", "dim_promotion"]
L3_FACTS = ["fact_boardings", "fact_gps_trips", "fact_stop_visits"]
L4_AGGS = ["agg_network_day", "agg_route_hour", "agg_route_day",
           "agg_stop_hour", "agg_stop_total", "agg_school_route", "agg_hub_kpis"]


@dataclass
class Result:
    checks: list[tuple[str, bool, str]] = field(default_factory=list)

    def add(self, name: str, ok: bool, detail: str = "") -> None:
        self.checks.append((name, ok, detail))

    @property
    def failures(self) -> list[tuple[str, bool, str]]:
        return [c for c in self.checks if not c[1]]

    def report(self) -> None:
        for name, ok, detail in self.checks:
            mark = "PASS" if ok else "FAIL"
            log.info("  [%s] %-46s %s", mark, name, detail)
        n_fail = len(self.failures)
        log.info("─" * 72)
        log.info("  %d checks · %d passed · %d failed",
                 len(self.checks), len(self.checks) - n_fail, n_fail)


def _scalar(con, sql):
    return con.execute(sql).fetchone()[0]


def validate(con: duckdb.DuckDBPyConnection, strict: bool = True) -> Result:
    r = Result()
    present = {row[0] for row in con.execute(
        "SELECT table_name FROM information_schema.tables WHERE table_schema='main'"
    ).fetchall()}

    # A. Presence
    for t in L2_DIMS + L3_FACTS + L4_AGGS:
        r.add(f"presence · {t}", t in present, "" if t in present else "MISSING")

    # B. Row counts (exact for fixed dims, lower-bound for data-driven)
    expected_exact = {"dim_hour": 24, "dim_fare_class": 4}
    expected_min = {"dim_date": 88, "dim_route": 120, "dim_stop": 4000,
                    "dim_school": 8, "dim_company": 1}
    for t, exp in expected_exact.items():
        if t in present:
            n = _scalar(con, f"SELECT COUNT(*) FROM {t}")
            r.add(f"rowcount · {t} == {exp}", n == exp, f"got {n:,}")
    for t, lo in expected_min.items():
        if t in present:
            n = _scalar(con, f"SELECT COUNT(*) FROM {t}")
            r.add(f"rowcount · {t} >= {lo}", n >= lo, f"got {n:,}")

    # C. Key uniqueness (the 1:1 dims)
    uniq = {
        "dim_route": "route_id",
        "dim_trip": "trip_id",
        "dim_school_stop": "stop_id",
        "dim_date": "day",
    }
    for t, key in uniq.items():
        if t in present:
            dup = _scalar(con, f"""
                SELECT COUNT(*) FROM (
                  SELECT {key} FROM {t} GROUP BY {key} HAVING COUNT(*) > 1
                )""")
            r.add(f"unique · {t}.{key}", dup == 0, f"{dup} duplicate keys")

    # D. Lossless Bronze→Gold chain (the headline guarantee)
    hub = _scalar(con, "SELECT boardings FROM agg_hub_kpis") if "agg_hub_kpis" in present else -1
    r.add("lossless · agg_hub_kpis.boardings == raw 17,883,623",
          hub == RAW_TICKETS, f"got {hub:,}")
    if "agg_network_day" in present:
        net = _scalar(con, "SELECT SUM(boardings) FROM agg_network_day")
        r.add("lossless · sum(agg_network_day) == raw 17,883,623",
              net == RAW_TICKETS, f"got {net:,}")

    # E. Referential integrity (Gold FKs resolve into dims)
    if {"agg_school_route", "dim_school"} <= present:
        orphan = _scalar(con, """
            SELECT COUNT(*) FROM (
              SELECT DISTINCT uni_slug FROM agg_school_route
              WHERE uni_slug NOT IN (SELECT school_slug FROM dim_school))""")
        r.add("ref · agg_school_route.uni_slug ⊆ dim_school", orphan == 0,
              f"{orphan} orphan school slugs")
    if {"agg_route_hour", "dim_route"} <= present:
        orphan = _scalar(con, """
            SELECT COUNT(*) FROM (
              SELECT DISTINCT route_no FROM agg_route_hour
              WHERE route_no NOT IN (SELECT route_no FROM dim_route))""")
        r.add("ref · agg_route_hour.route_no ⊆ dim_route", orphan == 0,
              f"{orphan} orphan route numbers")

    # F. Domain + null checks
    if "agg_network_day" in present:
        bad = _scalar(con, """
            SELECT COUNT(*) FROM agg_network_day
            WHERE fare_class NOT IN ('student','cash','free','other')""")
        r.add("domain · fare_class ∈ {student,cash,free,other}", bad == 0,
              f"{bad} out-of-domain rows")
    if "dim_stop" in present:
        bad = _scalar(con, """
            SELECT COUNT(*) FROM dim_stop
            WHERE in_bbox AND (lat NOT BETWEEN 10.5 AND 11.2
                            OR lng NOT BETWEEN 106.4 AND 107.0)""")
        r.add("bbox · in_bbox stops within HCMC bounds", bad == 0,
              f"{bad} stops out of bounds")
    if "dim_date" in present:
        nulls = _scalar(con, "SELECT COUNT(*) FROM dim_date WHERE day IS NULL")
        r.add("null · dim_date.day not null", nulls == 0, f"{nulls} null days")
        tet = _scalar(con, "SELECT COUNT(*) FROM dim_date WHERE is_tet_2026")
        r.add("tag · dim_date Tết window == 9 days", tet == 9, f"got {tet}")

    r.report()
    if strict and r.failures:
        raise SystemExit(f"VALIDATION FAILED: {len(r.failures)} check(s) failed")
    return r


def main() -> None:
    if not DB_PATH.exists():
        raise FileNotFoundError(f"Warehouse missing at {DB_PATH}")
    con = duckdb.connect(str(DB_PATH), read_only=True)
    try:
        log.info("Validating warehouse at %s", DB_PATH)
        log.info("─" * 72)
        validate(con, strict=True)
        log.info("All validation checks passed.")
    finally:
        con.close()


if __name__ == "__main__":
    main()
