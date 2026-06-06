# S1 · P1a — dbt + Dagster Warehouse (DuckDB dev / BigQuery prod) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the warehouse as a portable **dbt** project (Silver star + Gold) orchestrated by **Dagster**, running on **DuckDB** locally and **provably swappable to BigQuery**, with integrity encoded as dbt tests + a lossless asset check.

**Architecture:** `pipeline/dbt/` holds the dbt project: parquet **sources** at a configurable storage path, **Silver** models (`dim_*` tables + `fact_*` views = the Kimball star) and **Gold** models (`agg_*` tables), all written DuckDB-first with dialect-specific SQL macro-ized for portability. `pipeline/src/busanalytics_pipeline/` holds Dagster `definitions.py`/`assets.py` (dagster-dbt assets + DuckDB resource + a lossless asset check). dbt **targets**: `dev`=DuckDB→`db/bus.duckdb`, `prod`=BigQuery (config only; proven by `dbt compile --target prod`). **`demo/` is untouched.**

**Tech Stack:** Python 3.12 · dbt-core · dbt-duckdb · dbt-bigquery · dbt-utils · Dagster · dagster-dbt · dagster-duckdb · DuckDB · pytest.

**Reference (source SQL to translate, read but do not modify):** `demo/warehouse/dims.py` (9 SQL dims + 2 static + 1 placeholder), `demo/warehouse/facts.py` (3 fact views), `demo/warehouse/build.py` (7 Gold aggregates), `demo/warehouse/validate.py` (integrity checks → dbt tests). Spec: `docs/specs/2026-06-04-phase2-s1-rearchitecture-design.md` §3.2.

**Test/CI note:** building needs `data/parquet/` (gitignored, local-only). dbt-build / integration tests are guarded `@pytest.mark.skipif(not PARQUET_DIR.exists())` so the CI `pipeline` job stays green without data; unit tests (config, dbt parse) still run.

---

### Task 1: Pipeline dependencies + config

**Files:**
- Modify: `pipeline/pyproject.toml`
- Create: `pipeline/src/busanalytics_pipeline/config.py`
- Test: `pipeline/tests/test_config.py`

- [ ] **Step 1: Add data-engineering deps to `pipeline/pyproject.toml`**

Replace the `dependencies` + add a `dev` extra:
```toml
dependencies = [
  "duckdb>=1.1",
  "polars>=1.6",
  "pyarrow>=17",
  "dbt-core>=1.8",
  "dbt-duckdb>=1.8",
  "dagster>=1.8",
  "dagster-dbt>=0.24",
  "dagster-duckdb>=0.24",
]

[project.optional-dependencies]
dev = ["ruff>=0.6", "mypy>=1.11", "pytest>=8", "dbt-bigquery>=1.8"]
```
(dbt-bigquery is dev-only — needed to *compile* the prod target, not to run dev.)

- [ ] **Step 2: Write `config.py`**

```python
"""Pipeline paths + settings (12-factor: env-overridable)."""
from __future__ import annotations

import os
from pathlib import Path


def _repo_root() -> Path:
    env = os.environ.get("BUSPIPE_REPO_ROOT")
    return Path(env) if env else Path(__file__).resolve().parents[3]


REPO_ROOT = _repo_root()
DATA_DIR = Path(os.environ.get("BUSPIPE_DATA_DIR", REPO_ROOT / "data"))
PARQUET_DIR = DATA_DIR / "parquet"
DB_PATH = Path(os.environ.get("BUSPIPE_DB_PATH", REPO_ROOT / "db" / "bus.duckdb"))
DBT_DIR = Path(__file__).resolve().parents[2] / "dbt"
DBT_TARGET = os.environ.get("DBT_TARGET", "dev")
```

- [ ] **Step 3: Write the config test**

```python
from pathlib import Path

from busanalytics_pipeline import config


def test_paths() -> None:
    assert config.DB_PATH.name == "bus.duckdb"
    assert config.PARQUET_DIR.parent == config.DATA_DIR
    assert config.DBT_DIR.name == "dbt"
    assert config.DBT_TARGET in {"dev", "prod"}
```

- [ ] **Step 4: Sync + verify**

Run: `cd pipeline && uv sync --extra dev && uv run pytest tests/test_config.py -q && uv run ruff check . && uv run mypy`
Expected: deps resolve; tests pass; clean.

- [ ] **Step 5: Commit**

```bash
git add pipeline/pyproject.toml pipeline/uv.lock pipeline/src/busanalytics_pipeline/config.py pipeline/tests/test_config.py
git commit -m "feat(s1-p1a): pipeline deps (dbt/dagster) + config (paths, dbt target)"
```

---

### Task 2: dbt project scaffold (dev/prod targets + parquet sources)

**Files:**
- Create: `pipeline/dbt/dbt_project.yml`, `pipeline/dbt/profiles.yml`, `pipeline/dbt/packages.yml`, `pipeline/dbt/models/bronze/sources.yml`

- [ ] **Step 1: `dbt_project.yml`**

```yaml
name: busanalytics
version: "1.0.0"
config-version: 2
profile: busanalytics

model-paths: ["models"]
seed-paths: ["seeds"]
test-paths: ["tests"]
macro-paths: ["macros"]

models:
  busanalytics:
    silver:
      dims:
        +materialized: table
      facts:
        +materialized: view
    gold:
      +materialized: table
```

- [ ] **Step 2: `profiles.yml` (dev=DuckDB, prod=BigQuery)**

```yaml
busanalytics:
  target: "{{ env_var('DBT_TARGET', 'dev') }}"
  outputs:
    dev:
      type: duckdb
      path: "{{ env_var('BUSPIPE_DB_PATH', '../../db/bus.duckdb') }}"
      threads: 4
    prod:
      type: bigquery
      method: service-account
      project: "{{ env_var('BQ_PROJECT', 'unset') }}"
      dataset: "{{ env_var('BQ_DATASET', 'busanalytics') }}"
      keyfile: "{{ env_var('BQ_KEYFILE', '') }}"
      location: "{{ env_var('BQ_LOCATION', 'US') }}"
      threads: 4
```

- [ ] **Step 3: `packages.yml` (dbt_utils for cross-db macros)**

```yaml
packages:
  - package: dbt-labs/dbt_utils
    version: [">=1.1.0", "<2.0.0"]
```

- [ ] **Step 4: `models/bronze/sources.yml` (parquet at a configurable path, dev target)**

```yaml
version: 2

sources:
  - name: bronze
    meta:
      external_location: "{{ env_var('BUSPIPE_PARQUET_DIR', '../../data/parquet') }}/{name}.parquet"
    tables:
      - name: tickets
        meta:
          external_location: "{{ env_var('BUSPIPE_PARQUET_DIR', '../../data/parquet') }}/tickets/*.parquet"
      - name: payments
        meta:
          external_location: "{{ env_var('BUSPIPE_PARQUET_DIR', '../../data/parquet') }}/payments/*.parquet"
      - name: stops
      - name: ticket_routes
      - name: ticket_trips
      - name: ticket_companies
      - name: ticket_buses
      - name: gps_trips
      - name: gps_stop_times
```
(The `external_location` meta is a dbt-duckdb feature — it binds each source to its parquet. For the `prod`/BigQuery target these sources become BigQuery external tables over GCS-staged parquet; that binding is the documented step in Task 9, not built now.)

- [ ] **Step 5: Verify dbt parses (dev)**

Run:
```bash
cd pipeline/dbt && unset VIRTUAL_ENV
DBT_TARGET=dev uv run --project .. dbt deps
DBT_TARGET=dev uv run --project .. dbt parse
DBT_TARGET=dev uv run --project .. dbt debug
```
Expected: `dbt deps` installs dbt_utils; `parse` succeeds; `debug` reports the duckdb connection OK.

- [ ] **Step 6: Commit**

```bash
git add pipeline/dbt/dbt_project.yml pipeline/dbt/profiles.yml pipeline/dbt/packages.yml \
        pipeline/dbt/models/bronze/sources.yml pipeline/dbt/package-lock.yml
git commit -m "feat(s1-p1a): dbt project scaffold (dev=duckdb/prod=bigquery, parquet sources)"
```

---

### Task 3: Seeds (static dims) + placeholder

**Files:**
- Create: `pipeline/dbt/seeds/dim_school.csv`, `pipeline/dbt/seeds/dim_fare_class.csv`, `pipeline/dbt/models/silver/dims/dim_promotion.sql`

- [ ] **Step 1: `seeds/dim_school.csv`** (the 8 universities from `dims.py::_UNIVERSITIES`)

```csv
school_slug,display,stop_id,lat,lng,verified
HCMUT,Bách Khoa,506,10.7726,106.6577,true
HCMUS,KH Tự Nhiên,474,10.7623,106.6831,true
UEH,Kinh Tế,7701,10.7062,106.6394,true
GTVT,Giao Thông VT,1405,10.8066,106.7160,true
USSH,KHXH & Nhân Văn,1096,10.7858,106.7027,true
HCMUTE,Sư Phạm Kỹ Thuật,400,10.8499,106.7721,true
SGU,Sài Gòn,467,10.7607,106.6823,true
UIT,CNTT (district),,10.8704,106.8030,false
```

- [ ] **Step 2: `seeds/dim_fare_class.csv`** (the 4 classes from `dims.py::build_dim_fare_class`)

```csv
fare_class,description,is_subsidised
student,HS-SV student-fare ticket,true
cash,Cash / smartcard standard fare,false
free,Free or fully subsidised ticket,true
other,Other / unclassified ticket type,false
```

- [ ] **Step 3: `models/silver/dims/dim_promotion.sql`** (empty placeholder, typed)

```sql
-- Phase-2 placeholder: the four payment promo fields are >=99% null in the
-- Phase-1 release. Materialised empty so downstream joins stay valid.
select
  cast(null as varchar) as promotion_code,
  cast(null as varchar) as promotion_description
where false
```

- [ ] **Step 4: Verify seeds load**

Run: `cd pipeline/dbt && DBT_TARGET=dev uv run --project .. dbt seed`
Expected: `dim_school` (8 rows) + `dim_fare_class` (4 rows) loaded into `db/bus.duckdb`.

- [ ] **Step 5: Commit**

```bash
git add pipeline/dbt/seeds pipeline/dbt/models/silver/dims/dim_promotion.sql
git commit -m "feat(s1-p1a): dbt seeds (dim_school, dim_fare_class) + dim_promotion placeholder"
```

---

### Task 4: Silver dimension models

**Files:**
- Create: `pipeline/dbt/models/silver/dims/{dim_date,dim_hour,dim_route,dim_stop,dim_school_stop,dim_trip,dim_company,dim_payment_channel,dim_vehicle}.sql`

Translate each from the matching `build_dim_*` function in `demo/warehouse/dims.py`: take the `SELECT` body, replace raw Bronze table names with `{{ source('bronze', '<name>') }}`, replace dim references with `{{ ref('<dim>') }}`, and drop the `CREATE OR REPLACE TABLE ... AS` wrapper (dbt handles materialization). Write DuckDB SQL now; portability macro-izing happens in Task 9.

- [ ] **Step 1: Representative model — `dim_route.sql`** (shows the exact pattern)

```sql
with ranked as (
  select
    route_id,
    route_no,
    route_name,
    company_id,
    row_number() over (
      partition by route_id
      order by length(route_no), route_no
    ) as rk
  from {{ source('bronze', 'ticket_routes') }}
  where route_id is not null and route_no is not null
)
select route_id, route_no, route_name, company_id
from ranked
where rk = 1
```

- [ ] **Step 2: Translate the remaining 8 dims by the same pattern**

- `dim_date.sql` ← `build_dim_date` (`from {{ source('bronze','tickets') }}`).
- `dim_hour.sql` ← `build_dim_hour` (`from range(0,24) as t(h)` — DuckDB-specific; flagged for Task 9 macro).
- `dim_stop.sql` ← `build_dim_stop` (`from {{ source('bronze','stops') }}`).
- `dim_school_stop.sql` ← `build_dim_school_stop` (`from {{ ref('dim_school') }}` join `{{ ref('dim_stop') }}`).
- `dim_trip.sql` ← `build_dim_trip` (`from {{ source('bronze','ticket_trips') }}`).
- `dim_company.sql` ← `build_dim_company` (`select * from {{ source('bronze','ticket_companies') }}`).
- `dim_payment_channel.sql` ← `build_dim_payment_channel` — **replace the hardcoded `read_parquet('data/parquet/payments/*.parquet')` with `{{ source('bronze','payments') }}`**.
- `dim_vehicle.sql` ← `build_dim_vehicle` (`from {{ source('bronze','ticket_buses') }}`).

- [ ] **Step 3: Verify Silver dims build**

Run: `cd pipeline/dbt && DBT_TARGET=dev uv run --project .. dbt run --select silver.dims`
Expected: all `dim_*` build green against `db/bus.duckdb`.

- [ ] **Step 4: Commit**

```bash
git add pipeline/dbt/models/silver/dims
git commit -m "feat(s1-p1a): Silver dimension models (the Kimball star dims)"
```

---

### Task 5: Silver fact models (views = the star's facts)

**Files:**
- Create: `pipeline/dbt/models/silver/facts/{fact_boardings,fact_gps_trips,fact_stop_visits}.sql`

- [ ] **Step 1: `fact_boardings.sql`** (the central fact; ported from `facts.py::build_fact_boardings`)

```sql
select
  t.ticket_id,
  to_timestamp(t.time_created_ticket)::date as day,
  extract(hour from to_timestamp(t.time_created_ticket))::int as hour,
  r.route_no,
  t.station_id as stop_id,
  case
    when t.ticket_type like '%HS-SV%'    then 'student'
    when t.ticket_type like '%miễn phí%' then 'free'
    when t.ticket_type like '%TM%'       then 'cash'
    else 'other'
  end as fare_class,
  dt.bus_id as bus_id,
  ss.school_slug as school_slug
from {{ source('bronze', 'tickets') }} t
left join {{ ref('dim_trip') }}        dt on dt.trip_id = t.trip_id
left join {{ ref('dim_route') }}       r  on r.route_id  = dt.route_id
left join {{ ref('dim_school_stop') }} ss on ss.stop_id  = t.station_id
```

- [ ] **Step 2: Translate `fact_gps_trips.sql` + `fact_stop_visits.sql`** from `facts.py` by the same pattern (`{{ source('bronze','gps_trips') }}`, `{{ ref('dim_route') }}`, `{{ source('bronze','gps_stop_times') }}`).

- [ ] **Step 3: Verify facts build (as views)**

Run: `cd pipeline/dbt && DBT_TARGET=dev uv run --project .. dbt run --select silver.facts`
Expected: the three `fact_*` views build green.

- [ ] **Step 4: Commit**

```bash
git add pipeline/dbt/models/silver/facts
git commit -m "feat(s1-p1a): Silver fact views (fact_boardings + gps facts)"
```

---

### Task 6: Gold aggregate models

**Files:**
- Create: `pipeline/dbt/models/gold/{agg_network_day,agg_route_hour,agg_route_day,agg_stop_hour,agg_stop_total,agg_school_route,agg_hub_kpis}.sql`

Translate each from the matching `build_agg_*` function in `demo/warehouse/build.py`: take the `SELECT` body, replace `fact_boardings` with `{{ ref('fact_boardings') }}`, `dim_stop` with `{{ ref('dim_stop') }}`, and the raw `ticket_routes`/`stops`/`payments` references in `agg_hub_kpis` with `{{ source('bronze', ...) }}`.

- [ ] **Step 1: Representative — `agg_hub_kpis.sql`** (the one the lossless test reads)

```sql
with net as (
  select
    sum(boardings) as boardings,
    100.0 * sum(case when fare_class = 'student' then boardings end)
          / nullif(sum(boardings), 0) as student_share
  from {{ ref('agg_network_day') }}
),
rev as (select coalesce(sum(amount_money), 0) as revenue from {{ source('bronze', 'payments') }}),
r   as (select count(distinct route_no) as routes_n from {{ source('bronze', 'ticket_routes') }}),
s   as (select count(*) as stops_n from {{ source('bronze', 'stops') }}
        where lat is not null and lng is not null)
select net.boardings, rev.revenue, net.student_share,
       r.routes_n, s.stops_n, 19 as metro_feeders
from net, rev, r, s
```

- [ ] **Step 2: Translate the other 6 Gold models** from `build.py` by the same pattern (`agg_network_day` etc. read `{{ ref('fact_boardings') }}`; `agg_stop_total` joins `{{ ref('dim_stop') }}`).

- [ ] **Step 3: Full build → warehouse**

Run: `cd pipeline/dbt && DBT_TARGET=dev uv run --project .. dbt build`
Expected: every model + seed builds; `db/bus.duckdb` now holds the star + Gold; build summary shows PASS.

- [ ] **Step 4: Commit**

```bash
git add pipeline/dbt/models/gold
git commit -m "feat(s1-p1a): Gold aggregate models (chart-serving L4)"
```

---

### Task 7: dbt tests (integrity) + lossless singular test

**Files:**
- Create: `pipeline/dbt/models/silver/schema.yml`, `pipeline/dbt/models/gold/schema.yml`, `pipeline/dbt/tests/assert_lossless_boardings.sql`

- [ ] **Step 1: `models/silver/schema.yml`** (key uniqueness + domain, from `validate.py` C/F)

```yaml
version: 2
models:
  - name: dim_route
    columns:
      - name: route_id
        data_tests: [unique, not_null]
  - name: dim_trip
    columns:
      - name: trip_id
        data_tests: [unique, not_null]
  - name: dim_school_stop
    columns:
      - name: stop_id
        data_tests: [unique, not_null]
  - name: dim_date
    columns:
      - name: day
        data_tests: [unique, not_null]
  - name: fact_boardings
    columns:
      - name: fare_class
        data_tests:
          - accepted_values:
              values: [student, cash, free, other]
```

- [ ] **Step 2: `models/gold/schema.yml`** (referential, from `validate.py` E)

```yaml
version: 2
models:
  - name: agg_route_hour
    columns:
      - name: route_no
        data_tests:
          - relationships:
              to: ref('dim_route')
              field: route_no
  - name: agg_school_route
    columns:
      - name: uni_slug
        data_tests:
          - relationships:
              to: ref('dim_school')
              field: school_slug
```

- [ ] **Step 3: `tests/assert_lossless_boardings.sql`** (the headline guarantee — singular test; passes when it returns 0 rows)

```sql
-- Bronze->Gold must be arithmetically lossless: the Gold KPI boarding count
-- equals the raw ticket count (17,883,623). This query returns a row only on mismatch.
select boardings
from {{ ref('agg_hub_kpis') }}
where boardings <> 17883623
```

- [ ] **Step 4: Run the test suite**

Run: `cd pipeline/dbt && DBT_TARGET=dev uv run --project .. dbt test`
Expected: all data tests + `assert_lossless_boardings` PASS.

- [ ] **Step 5: Commit**

```bash
git add pipeline/dbt/models/silver/schema.yml pipeline/dbt/models/gold/schema.yml \
        pipeline/dbt/tests/assert_lossless_boardings.sql
git commit -m "test(s1-p1a): dbt integrity tests + lossless singular test"
```

---

### Task 8: Dagster — dbt assets + DuckDB resource + lossless asset check

**Files:**
- Create: `pipeline/src/busanalytics_pipeline/assets.py`, `pipeline/src/busanalytics_pipeline/definitions.py`
- Create: `pipeline/dbt/.gitignore` (ignore `target/`, `dbt_packages/`, `logs/`)

- [ ] **Step 1: `pipeline/dbt/.gitignore`**

```gitignore
target/
dbt_packages/
logs/
```

- [ ] **Step 2: `assets.py` (dagster-dbt assets + lossless asset check)**

```python
"""Dagster assets: the dbt warehouse + a lossless asset check."""
from __future__ import annotations

from pathlib import Path

import duckdb
from dagster import AssetCheckResult, asset_check
from dagster_dbt import DbtCliResource, DbtProject, dbt_assets

from .config import DB_PATH, DBT_DIR

dbt_project = DbtProject(project_dir=Path(DBT_DIR))
dbt_project.prepare_if_dev()


@dbt_assets(manifest=dbt_project.manifest_path)
def busanalytics_dbt_assets(context, dbt: DbtCliResource):  # type: ignore[no-untyped-def]
    yield from dbt.cli(["build"], context=context).stream()


@asset_check(asset="agg_hub_kpis")
def lossless_boardings() -> AssetCheckResult:
    con = duckdb.connect(str(DB_PATH), read_only=True)
    try:
        boardings = con.execute("SELECT boardings FROM agg_hub_kpis").fetchone()[0]
    finally:
        con.close()
    return AssetCheckResult(
        passed=boardings == 17_883_623,
        metadata={"boardings": int(boardings)},
    )
```

- [ ] **Step 3: `definitions.py`**

```python
"""Dagster Definitions — wires the dbt assets, the DuckDB resource, and checks."""
from __future__ import annotations

from dagster import Definitions
from dagster_dbt import DbtCliResource

from .assets import busanalytics_dbt_assets, dbt_project, lossless_boardings

defs = Definitions(
    assets=[busanalytics_dbt_assets],
    asset_checks=[lossless_boardings],
    resources={"dbt": DbtCliResource(project_dir=dbt_project)},
)
```

- [ ] **Step 4: Verify Dagster loads + materializes**

Run:
```bash
cd pipeline && unset VIRTUAL_ENV
uv run dagster definitions validate -m busanalytics_pipeline.definitions
uv run dagster asset materialize --select '*' -m busanalytics_pipeline.definitions
```
Expected: definitions validate; assets materialize (runs `dbt build`); the `lossless_boardings` check passes with `boardings=17883623`.

- [ ] **Step 5: Commit**

```bash
git add pipeline/src/busanalytics_pipeline/assets.py \
        pipeline/src/busanalytics_pipeline/definitions.py pipeline/dbt/.gitignore
git commit -m "feat(s1-p1a): Dagster dbt assets + DuckDB resource + lossless asset check"
```

---

### Task 9: Integration test + BigQuery portability proof

**Files:**
- Create: `pipeline/tests/test_warehouse_integration.py`
- Create: `pipeline/dbt/macros/` portability macros (only the dialect spots `dbt compile --target prod` flags)
- Create: `docs/specs/bigquery-deployment.md` (the documented prod binding)

- [ ] **Step 1: Integration test (builds via dbt, asserts lossless), skipif no data**

```python
import subprocess

import duckdb
import pytest

from busanalytics_pipeline.config import DB_PATH, DBT_DIR, PARQUET_DIR

pytestmark = pytest.mark.skipif(
    not PARQUET_DIR.exists(), reason="data/parquet not present (CI / fresh checkout)"
)


def test_dbt_build_is_lossless() -> None:
    subprocess.run(
        ["dbt", "build", "--target", "dev"], cwd=DBT_DIR, check=True
    )
    con = duckdb.connect(str(DB_PATH), read_only=True)
    try:
        boardings = con.execute("SELECT boardings FROM agg_hub_kpis").fetchone()[0]
    finally:
        con.close()
    assert boardings == 17_883_623
```

- [ ] **Step 2: Run it locally**

Run: `cd pipeline && unset VIRTUAL_ENV && uv run pytest -q`
Expected: integration test runs (data present), `dbt build` green, lossless asserted; unit tests pass.

- [ ] **Step 3: Prove BigQuery portability (compile against prod)**

Run: `cd pipeline/dbt && DBT_TARGET=prod uv run --project .. dbt compile --target prod`
Expected: compilation surfaces any DuckDB-only SQL (e.g. `range(0,24)`, `to_timestamp`, `::date` casts, `ILIKE`). For each, add a macro under `pipeline/dbt/macros/` (or use `dbt_utils` / `{{ dbt.date_trunc }}` / `{{ dbt.type_timestamp() }}`) and re-run until `dbt compile --target prod` succeeds. Record the macro list + the GCS-external-table source binding in `docs/specs/bigquery-deployment.md`.

> If BigQuery credentials are not configured locally, `dbt compile --target prod` will still
> parse/compile the SQL without a live connection (compile does not require a warehouse round-trip
> for most models); the credential-bound `dbt build --target prod` against a sample dataset is the
> documented manual deployment step, not a CI gate.

- [ ] **Step 4: Confirm CI-safe (no data) path**

Run: `cd pipeline && BUSPIPE_DATA_DIR=/tmp/nodata uv run pytest -q`
Expected: integration test SKIPS; config + any unit tests PASS.

- [ ] **Step 5: Commit**

```bash
git add pipeline/tests/test_warehouse_integration.py pipeline/dbt/macros docs/specs/bigquery-deployment.md
git commit -m "test(s1-p1a): warehouse integration test + BigQuery portability proof + docs"
```

---

## Done criteria (P1a)

- `dbt build --target dev` builds the star + Gold into `db/bus.duckdb`; all dbt tests pass incl. `assert_lossless_boardings`.
- Dagster materializes the dbt assets; the `lossless_boardings` asset check passes.
- `cd pipeline && uv run pytest -q && uv run ruff check . && uv run mypy` green locally; the `pipeline` CI job stays green with no data (integration tests skip).
- `dbt compile --target prod` (BigQuery) succeeds; portability macros + the GCS source binding documented in `docs/specs/bigquery-deployment.md`.
- `demo/` untouched and still runnable.

## Next

P1b · Preprocess + gate: port `src/duckdb_loader.py`'s CSV→parquet (report §4.3 six steps) as an upstream Dagster asset, and implement the §4.3.1 gate (row-count regression · null-rate ceiling · referential · PK uniqueness) as Dagster **asset checks** that block the dbt build. Then P2 (backend) reads the warehouse via the data API.
