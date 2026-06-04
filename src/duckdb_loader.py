import logging
from pathlib import Path

import duckdb
import polars as pl

logging.basicConfig(level=logging.INFO, format="%(levelname)s | %(message)s")
logger = logging.getLogger(__name__)


class BusDuckDB:
    """
    Loads HCMC bus GPS + AFC ticket data into DuckDB views backed by Parquet.

    Expected layout under data_dir/raw/:
      gps/
        raw_gps/YYYY-MM-DD.csv          raw GPS pings
        trips.csv                        GPS-extracted trip records
        stop_times.csv                   per-stop timing (arrival, dwell, departure)
        schedules.csv                    planned timetable
        routes.csv                       route metadata (headway, distance, company)
        companies.csv                    GPS-side bus operators
        vehicles.csv                     vehicle_id → license plate
        drivers.csv                      driver_id → name
        stations.csv                     stop/station master (GPS side)
        extracted_trips_buffer_50m/
          {route_no}/{trip_id}.csv       HMM-filtered GPS points per trip
      tickets/
        {mon_yyyy}/
          tickets/DD-MM-YYYY.csv         AFC boarding events
          payments/DD-MM-YYYY.csv        payment records (linked by ticket_id)
          trips.csv                      AFC trip metadata
        buses.csv                        bus_id → vehicle_number
        routes.csv                       AFC route metadata
        companies.csv                    AFC operators
        stations.csv                     AFC station master
        route_stops.csv                  route → stop sequence
        drivers.csv                      AFC driver_license_number → name
        users.csv                        user_id → student_id link
        students.csv                     student_id → school_id, name
        schools.csv                      school_id → name, address
      hcmc_stops_agu_2025.csv            master stop list (HCMC-wide)
      vehicle_route_mapping.csv          anonymised vehicle hash → route

    Views registered after normalize() / register_views():
      GPS side  : gps_raw, gps_trips, gps_stop_times, gps_schedules,
                  gps_routes, gps_companies, gps_vehicles, gps_drivers,
                  gps_stations, gps_extracted
      AFC side  : tickets, payments, ticket_trips, ticket_routes,
                  ticket_companies, ticket_buses, ticket_stations,
                  ticket_route_stops, ticket_drivers, ticket_users,
                  ticket_students, ticket_schools
      Shared    : stops, mapping

    Notes:
      - AFC tickets record boarding station only; no alighting data exists.
        "Boardings per stop/trip" is valid; live occupancy is not computable.
      - GPS raw data available locally is a single-day sample (2025-03-18).
        Full 50-day dataset must be loaded for temporal pattern analysis.
      - GPS (2025) and AFC (2026) cover different periods — they cannot be
        joined by timestamp. Analyse as complementary sources.
    """

    _GPS_DIMS = [
        "trips", "stop_times", "schedules", "routes",
        "companies", "vehicles", "drivers", "stations",
    ]

    _TICKET_REFS = {
        "buses":       "ticket_buses",
        "routes":      "ticket_routes",
        "companies":   "ticket_companies",
        "stations":    "ticket_stations",
        "route_stops": "ticket_route_stops",
        "drivers":     "ticket_drivers",
        "users":       "ticket_users",
        "students":    "ticket_students",
        "schools":     "ticket_schools",
    }

    # tickets and payments use a glob over a subdirectory (written per-day)
    _GLOB_VIEWS = {
        "tickets":  "tickets/*.parquet",
        "payments": "payments/*.parquet",
    }

    _VIEWS = {
        "gps_raw":           "gps_raw.parquet",
        "gps_trips":         "gps_trips.parquet",
        "gps_stop_times":    "gps_stop_times.parquet",
        "gps_schedules":     "gps_schedules.parquet",
        "gps_routes":        "gps_routes.parquet",
        "gps_companies":     "gps_companies.parquet",
        "gps_vehicles":      "gps_vehicles.parquet",
        "gps_drivers":       "gps_drivers.parquet",
        "gps_stations":      "gps_stations.parquet",
        "gps_extracted":     "gps_extracted.parquet",
        "ticket_trips":      "ticket_trips.parquet",
        "ticket_routes":     "ticket_routes.parquet",
        "ticket_companies":  "ticket_companies.parquet",
        "ticket_buses":      "ticket_buses.parquet",
        "ticket_stations":   "ticket_stations.parquet",
        "ticket_route_stops":"ticket_route_stops.parquet",
        "ticket_drivers":    "ticket_drivers.parquet",
        "ticket_users":      "ticket_users.parquet",
        "ticket_students":   "ticket_students.parquet",
        "ticket_schools":    "ticket_schools.parquet",
        "stops":             "stops.parquet",
        "mapping":           "mapping.parquet",
    }

    def __init__(self, data_dir: str, db_path: str = ":memory:"):
        """
        Args:
            data_dir: project data root (contains raw/ and parquet/ subdirs)
            db_path:  ":memory:" for in-process, or a path like "db/bus.duckdb"
        """
        self.data_dir    = Path(data_dir)
        self.raw_dir     = self.data_dir / "raw"
        self.pq_dir      = self.data_dir / "parquet"
        self.gps_dir     = self.raw_dir / "gps"
        self.tickets_dir = self.raw_dir / "tickets"

        try:
            self.con = duckdb.connect(db_path)
        except duckdb.IOException:
            logger.warning(f"Cannot lock {db_path} — falling back to :memory:")
            self.con = duckdb.connect(":memory:")

        logger.info("DuckDB ready")

    # ------------------------------------------------------------------ #
    # Public API                                                           #
    # ------------------------------------------------------------------ #

    def normalize(self, force: bool = False):
        """Convert all raw CSV files to Parquet, then register views."""
        self.pq_dir.mkdir(parents=True, exist_ok=True)

        self._norm_gps_raw(force)
        for dim in self._GPS_DIMS:
            self._norm_gps_dim(dim, force)
        self._norm_gps_extracted(force)

        self._norm_ticket_events("tickets",  force)
        self._norm_ticket_events("payments", force)
        self._norm_ticket_trips(force)
        for src, view in self._TICKET_REFS.items():
            self._norm_ticket_ref(src, view, force)

        self._norm_single("hcmc_stops_agu_2025.csv", "stops.parquet",   force)
        self._norm_single("vehicle_route_mapping.csv", "mapping.parquet", force)

        logger.info("Normalization complete")
        self._register_views()

    def register_views(self):
        """Register views from existing Parquet (no re-normalisation)."""
        self._register_views()

    def query(self, sql: str) -> pl.DataFrame:
        return pl.from_arrow(self.con.execute(sql).arrow())

    def sample(self, view: str, n: int = 10_000, method: str = "reservoir") -> pl.DataFrame:
        return self.query(f"SELECT * FROM {view} USING SAMPLE {n} ROWS ({method})")

    def preview(self, view: str, n: int = 5) -> pl.DataFrame:
        return self.query(f"SELECT * FROM {view} LIMIT {n}")

    def schema(self, view: str) -> pl.DataFrame:
        return self.query(f"DESCRIBE {view}")

    def row_count(self, view: str) -> int:
        return self.query(f"SELECT COUNT(*) AS n FROM {view}")["n"][0]

    def show_views(self) -> pl.DataFrame:
        return self.query("""
            SELECT table_name, table_type
            FROM information_schema.tables
            WHERE table_schema = 'main'
            ORDER BY table_name
        """)

    def close(self):
        self.con.close()
        logger.info("DuckDB connection closed")

    def __enter__(self):
        return self

    def __exit__(self, *_):
        self.close()

    # ------------------------------------------------------------------ #
    # Normalisation helpers                                                #
    # ------------------------------------------------------------------ #

    def _norm_gps_raw(self, force: bool):
        """Union all raw_gps/YYYY-MM-DD.csv → gps_raw.parquet."""
        out = self.pq_dir / "gps_raw.parquet"
        if out.exists() and not force:
            logger.info("Skip (exists): gps_raw.parquet")
            return

        raw_dir = self.gps_dir / "raw_gps"
        files = sorted(raw_dir.glob("*.csv"))
        if not files:
            logger.warning("No GPS raw CSV files found in gps/raw_gps/")
            return

        glob = str(raw_dir / "*.csv")
        self.con.execute(f"""
            COPY (
                SELECT
                    TRY_CAST(datetime  AS TIMESTAMP) AS datetime,
                    TRY_CAST(date      AS DATE)      AS date,
                    CAST(vehicle       AS VARCHAR)   AS vehicle,
                    TRY_CAST(lng       AS DOUBLE)    AS lng,
                    TRY_CAST(lat       AS DOUBLE)    AS lat,
                    CAST(driver        AS VARCHAR)   AS driver,
                    TRY_CAST(speed     AS DOUBLE)    AS speed,
                    TRY_CAST(door_up   AS BOOLEAN)   AS door_up,
                    TRY_CAST(door_down AS BOOLEAN)   AS door_down
                FROM read_csv_auto('{glob}', union_by_name=True, ignore_errors=True)
            ) TO '{out}' (FORMAT PARQUET, COMPRESSION ZSTD)
        """)
        logger.info(f"gps_raw → {out.name} ({len(files)} file(s))")

    def _norm_gps_dim(self, table: str, force: bool):
        """Convert a single GPS dimension CSV → gps_{table}.parquet."""
        src = self.gps_dir / f"{table}.csv"
        out = self.pq_dir / f"gps_{table}.parquet"
        if not src.exists():
            logger.warning(f"GPS dim not found: gps/{table}.csv")
            return
        if out.exists() and not force:
            logger.info(f"Skip (exists): gps_{table}.parquet")
            return
        self.con.execute(f"""
            COPY (SELECT * FROM read_csv_auto('{src}', ignore_errors=True))
            TO '{out}' (FORMAT PARQUET, COMPRESSION ZSTD)
        """)
        logger.info(f"gps_{table} → {out.name}")

    def _norm_gps_extracted(self, force: bool):
        """
        Union all extracted_trips_buffer_50m/{route_no}/*.csv → gps_extracted.parquet.
        Adds a route_no column derived from the parent directory name.
        """
        out = self.pq_dir / "gps_extracted.parquet"
        if out.exists() and not force:
            logger.info("Skip (exists): gps_extracted.parquet")
            return

        buf_dir = self.gps_dir / "extracted_trips_buffer_50m"
        files = [f for f in buf_dir.rglob("*.csv") if not f.name.startswith(".")]
        if not files:
            logger.warning("No extracted trip CSVs found in extracted_trips_buffer_50m/")
            return

        glob = str(buf_dir / "*" / "*.csv")
        self.con.execute(f"""
            COPY (
                SELECT
                    * EXCLUDE (filename),
                    regexp_extract(filename, '/([^/]+)/[^/]+\\.csv$', 1) AS route_no
                FROM read_csv_auto(
                    '{glob}',
                    union_by_name=True,
                    ignore_errors=True,
                    filename=True
                )
            ) TO '{out}' (FORMAT PARQUET, COMPRESSION ZSTD)
        """)
        logger.info(f"gps_extracted → {out.name} ({len(files)} file(s))")

    def _norm_ticket_events(self, kind: str, force: bool):
        """
        Convert tickets/{mon_yyyy}/{kind}/DD-MM-YYYY.csv → parquet/{kind}/ one file at a time.
        Processing daily keeps peak memory to ~30 MB per file (raw CSVs are up to 32 MB each).
        """
        out_dir = self.pq_dir / kind
        out_dir.mkdir(parents=True, exist_ok=True)

        files = sorted(self.tickets_dir.glob(f"*/{kind}/*.csv"))
        if not files:
            logger.warning(f"No {kind} CSV files found under tickets/")
            return

        written = 0
        for src in files:
            month = src.parent.parent.name   # e.g. "jan_2026"
            out   = out_dir / f"{month}_{src.stem}.parquet"
            if out.exists() and not force:
                continue
            self.con.execute(f"""
                COPY (
                    SELECT *, '{month}' AS month
                    FROM read_csv_auto('{src}', ignore_errors=True)
                ) TO '{out}' (FORMAT PARQUET, COMPRESSION ZSTD)
            """)
            written += 1

        total = len(files)
        skipped = total - written
        logger.info(f"{kind} → parquet/{kind}/ ({written} written, {skipped} skipped of {total})")

    def _norm_ticket_trips(self, force: bool):
        """Union tickets/{mon_yyyy}/trips.csv across months → ticket_trips.parquet."""
        out = self.pq_dir / "ticket_trips.parquet"
        if out.exists() and not force:
            logger.info("Skip (exists): ticket_trips.parquet")
            return

        files = sorted(self.tickets_dir.glob("*/trips.csv"))
        if not files:
            logger.warning("No ticket trips.csv files found under tickets/")
            return

        parts = [
            f"SELECT *, '{f.parent.name}' AS month FROM read_csv_auto('{f}', ignore_errors=True)"
            for f in files
        ]
        sql = " UNION ALL ".join(parts)
        self.con.execute(f"COPY ({sql}) TO '{out}' (FORMAT PARQUET, COMPRESSION ZSTD)")
        logger.info(f"ticket_trips → {out.name} ({len(files)} file(s))")

    def _norm_ticket_ref(self, src_name: str, view_name: str, force: bool):
        """Convert a shared ticket reference CSV → {view_name}.parquet."""
        src = self.tickets_dir / f"{src_name}.csv"
        out = self.pq_dir / f"{view_name}.parquet"
        if not src.exists():
            logger.warning(f"Ticket ref not found: tickets/{src_name}.csv")
            return
        if out.exists() and not force:
            logger.info(f"Skip (exists): {view_name}.parquet")
            return
        self.con.execute(f"""
            COPY (SELECT * FROM read_csv_auto('{src}', ignore_errors=True))
            TO '{out}' (FORMAT PARQUET, COMPRESSION ZSTD)
        """)
        logger.info(f"{view_name} → {out.name}")

    def _norm_single(self, src_name: str, out_name: str, force: bool):
        """Convert a single raw CSV in raw/ → parquet/{out_name}."""
        src = self.raw_dir / src_name
        out = self.pq_dir / out_name
        if not src.exists():
            logger.warning(f"File not found: raw/{src_name}")
            return
        if out.exists() and not force:
            logger.info(f"Skip (exists): {out_name}")
            return
        self.con.execute(f"""
            COPY (SELECT * FROM read_csv_auto('{src}', ignore_errors=True))
            TO '{out}' (FORMAT PARQUET, COMPRESSION ZSTD)
        """)
        logger.info(f"{out_name} ← raw/{src_name}")

    def _register_views(self):
        for view_name, glob_pattern in self._GLOB_VIEWS.items():
            files = sorted((self.pq_dir).glob(glob_pattern))
            if files:
                path = str(self.pq_dir / glob_pattern)
                self.con.execute(f"""
                    CREATE OR REPLACE VIEW {view_name} AS
                    SELECT * FROM read_parquet('{path}', union_by_name=True)
                """)
                logger.info(f"View '{view_name}' registered ({len(files)} file(s))")
            else:
                logger.warning(f"No parquet for view '{view_name}' — skipped (run normalize() first)")

        for view_name, pq_file in self._VIEWS.items():
            path = self.pq_dir / pq_file
            if path.exists():
                self.con.execute(f"""
                    CREATE OR REPLACE VIEW {view_name} AS
                    SELECT * FROM read_parquet('{path}')
                """)
                logger.info(f"View '{view_name}' registered")
            else:
                logger.warning(f"Parquet not found for view '{view_name}' — skipped (run normalize() first)")


if __name__ == "__main__":
    db = BusDuckDB("data", "db/bus.duckdb")
    db.normalize()
