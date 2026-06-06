# Phase 2 · S1 — Codebase re-architecture (design)

**Date:** 2026-06-04
**Status:** Approved direction; spec under review
**Scope (S1):** scaffold + pipeline + backend + the 9 currently-wired charts at parity on
the new stack. The remaining 11 catalogue charts, the report slim-down (S2), and the
diagram migration (S3) are separate follow-on sub-projects.

## 1 · Context

Phase 1 shipped a working prototype in [demo/](../../demo/) — a server-rendered FastAPI +
Jinja2 + HTMX + Plotly app over a Medallion DuckDB warehouse (9 of 20 charts wired across
3 themes, plus the Tết scrollytelling story). It survived the Phase-1 defence.

Phase 2 turns the prototype into a professional application. The locked direction:

- **API backend + SPA frontend** (not server-rendered HTML).
- **React + Vite + TypeScript** SPA against a separate FastAPI **JSON data API**.
- **Clean data boundary:** the API returns domain *data*, not Plotly figures; charts are
  built client-side in TypeScript.
- **Flat 3-part monorepo:** `pipeline/` (data) · `backend/` (API) · `frontend/` (SPA).
- **Runway:** full semester.

Authority documents: [CLAUDE.md](../../CLAUDE.md) (locked decisions + the 12 data invariants
+ measured EDA numbers), [docs/specs/chart-catalogue.md](chart-catalogue.md) (the 20-chart
catalogue), and the warehouse contract described in [demo/README.md](../../demo/README.md).

## 2 · Goals / non-goals

**Goals (S1):**

1. Split the codebase into three independent, separately-runnable/testable packages.
2. Establish the clean data-API contract (Pydantic v2 schemas; OpenAPI → typed TS client).
3. Stand up the professional tooling baseline (Python: uv/ruff/mypy/pytest; JS:
   pnpm/Vite/TS/Tailwind/shadcn/eslint/prettier/vitest/Playwright; Docker Compose; CI).
4. Reach **parity with `demo/`** on the new stack: the 9 wired charts, the editorial hub,
   the A3 entity-detail panel, the filter bar (currently on chart 2.3), and the Tết story.
5. Decommission `demo/` once parity is verified.

**Non-goals (S1) — explicitly deferred:**

- Wiring the remaining 11 catalogue charts (follow-on after parity).
- Report slim-down to 50–70 pp (**S2**); diagram migration to draw.io (**S3**).
- New analytics or features beyond current `demo/` behaviour.
- Full 50-day Kaggle GPS pull and school geocoding (independent data tasks).

## 3 · Target structure

```
busanalytics/
├── pipeline/                       # DATA — dbt (transforms) + Dagster (orchestration) over DuckDB
│   ├── dbt/                        # dbt-duckdb project: the warehouse transforms + data tests
│   │   ├── dbt_project.yml
│   │   ├── profiles.yml            # duckdb target → db/bus.duckdb
│   │   └── models/
│   │       ├── bronze/sources.yml  # raw parquet as dbt sources (report §4.3 step 6)
│   │       ├── silver/             # dim_*.sql + fact_*.sql — the Kimball star (L2/L3 = dims tables, fact views)
│   │       ├── gold/               # agg_*.sql — chart-serving aggregates (L4)
│   │       └── schema.yml          # dbt tests: unique · not_null · relationships · accepted_values
│   ├── src/busanalytics_pipeline/
│   │   ├── config.py               # paths (env-overridable)
│   │   ├── definitions.py          # Dagster Definitions: dbt assets, DuckDB resource, asset checks, schedule
│   │   ├── assets.py               # @dbt_assets (the star+gold) + the lossless asset check + (P1b) preprocess asset
│   │   ├── preprocess/             # report §4.3: raw CSV → parquet (six steps)            (P1b)
│   │   └── validate/               # lossless + §4.3.1 gate, surfaced as Dagster asset checks
│   ├── notebooks/                  # 01–04 .ipynb — exploratory record, import from src (no copy-paste)
│   ├── tests/                      # pytest: dbt build + asset-check + lossless integration
│   └── pyproject.toml              # + dbt-duckdb · dagster · dagster-dbt · dagster-duckdb
├── backend/                        # API — FastAPI JSON data API, read-only over the warehouse
│   ├── src/busanalytics_api/
│   │   ├── main.py                 # app factory + lifespan, wiring only
│   │   ├── config.py               # env/settings (pydantic-settings)
│   │   ├── db.py                   # read-only DuckDB connector        (was demo/db.py)
│   │   ├── api/                    # HTTP layer — thin
│   │   │   ├── routers/            # charts, kpis, filters, health
│   │   │   └── deps.py             # FastAPI dependencies (inject db, settings)
│   │   ├── services/               # domain logic — framework-agnostic (no fastapi import)
│   │   │   ├── charts/             # per-theme chart services (compute series + A2 action title)
│   │   │   └── registry.py         # chart registry: slug → service (open/closed)
│   │   ├── repositories/           # data access — warehouse SQL reads  (was demo/aggregates/)
│   │   ├── schemas/                # Pydantic v2 DTOs = the API contract
│   │   └── domain/                 # internal types/enums (Theme, ChartId)
│   ├── tests/                      # pytest + httpx: contract + service unit tests
│   └── pyproject.toml
├── frontend/                       # SPA — React + Vite + TypeScript (feature-based)
│   ├── src/
│   │   ├── app/                    # App root + providers (QueryClient, router, theme)
│   │   ├── api/                    # generated types + typed fetch client (one source of truth)
│   │   ├── hooks/                  # server-state hooks (TanStack Query): useChart, useKpis, useFilters
│   │   ├── charts/                 # presentational chart components + registry (chartId → component)
│   │   ├── maps/                   # MapLibre via react-map-gl
│   │   ├── stories/                # Scrollama scrollytelling (Tết)
│   │   ├── components/             # reusable presentational UI (shell, EntityPanel, FilterBar, ThemeCard)
│   │   ├── features/               # composition per area (hub, theme, story)
│   │   └── lib/                    # pure helpers (formatting, Plotly figure builders)
│   ├── tests/                      # vitest (unit) + Playwright (e2e)
│   └── package.json
├── db/  data/                      # warehouse + raw inputs (gitignored) — the pipeline↔backend contract
├── report/  deck/  docs/           # unchanged (already cleaned)
├── README.md                       # repo front door
├── docker-compose.yml              # local: db volume · backend · frontend
└── .github/workflows/ci.yml        # per-package lint + typecheck + test
```

`demo/` remains runnable until the new stack reaches parity, then it is deleted — there is
never a window without a working app. P0 scaffolds minimal skeletons; the layers below are
created with their content by the P2 (backend) and P3 (frontend) plans.

## 3.1 · Architecture principles (backend + frontend)

Both apps use a layered design with dependencies pointing **one way**, so each layer is
independently understandable, testable, and replaceable.

**Backend — clean layering (`api → services → repositories`):**

- **`api/`** (routers) handle HTTP only: parse params, call a service, return a schema. No SQL,
  no business logic. The db connection and settings are **injected** via `deps.py`
  (FastAPI `Depends`) rather than imported globally.
- **`services/`** hold domain logic (compute the chart series, derive the A2 action title,
  apply filters). They are **framework-agnostic** — never import FastAPI — so they unit-test
  in isolation.
- **`repositories/`** own data access (warehouse SQL → typed rows) and contain no business
  logic. Services depend on a **repository interface**, not on DuckDB directly, so the store
  can be swapped later (ties to §11 cloud/streaming).
- **`schemas/`** are the Pydantic DTOs at the boundary (the wire contract); **`domain/`** holds
  internal types. Separating them lets the wire format evolve without churning internals.
- **Extensibility:** a chart **registry** maps `slug → service`. Adding a chart = add a service
  module + register it; **no existing code is edited** (open/closed principle).

**Frontend — feature-based + unidirectional layering:**

- **`api/`** is the single source of truth for types (generated from the backend's OpenAPI) +
  the fetch client. Types are never hand-duplicated.
- **`hooks/`** own all server-state (TanStack Query); **components never fetch directly**.
- **`charts/`** are presentational; figure construction is **pure functions in `lib/`**
  (testable without React). A chart **registry** maps `chartId → component` (open/closed).
- **`components/`** are reusable and presentational; **`features/`** compose them into pages.
  UI state stays local/contextual, server state stays in hooks — clear data-flow, no tangle.

**Cross-cutting principles:** single responsibility · separation of concerns · dependency
inversion · DRY · small, focused files (one clear responsibility each) · typed contracts
end-to-end. The P2 and P3 plans create exactly these layers and are reviewed against these
principles.

## 3.2 · Data engine strategy (portable, cloud-scale)

The production target is **millions of trips/tickets per day**, so the engine must scale beyond
a single node while staying free to run + demonstrate locally. The design **separates storage
from compute, with dbt as the portability seam**:

- **Storage:** source parquet staged to **GCS** (the bucket is the data home); Bronze = BigQuery
  **external tables** over that parquet (query-in-place, no load step). A local parquet copy backs
  the optional DuckDB sampling target.
- **Transform:** **dbt** models (one definition of the Silver star + Gold), written
  **BigQuery-dialect first**, with `dbt_utils` / cross-db macros where the optional DuckDB local
  target needs them. BigQuery is authoritative.
- **Compute (primary = BigQuery):** BigQuery is the real engine for **both dev and prod** — the
  standard *develop-on-the-production-engine* pattern, promoted by dbt **target/dataset**
  (`bq_dev` = sampled dataset · `bq_prod` = full dataset). What you test is what you ship; the
  free tier covers capstone scale.
- **Local sampling (optional):** a **DuckDB** `local` target over local parquet for fast, offline
  scratch iteration — convenience only, **not the source of truth** (correctness + CI run on
  BigQuery).
- **Orchestration:** **Dagster** (engine-agnostic — assets, checks, schedules, cloud-deployable).

**Operated now:** a GCP project + GCS bucket + BigQuery `dev`/`prod` datasets, all within the
free tier. **Deliberately deferred (clean scale-up paths, not over-engineered now):**
Iceberg/Delta table format (multi-engine ACID / time-travel — adds a catalog); Spark/Databricks
(for 100s-of-TB / heavy ML); Kafka streaming ingest (no live source yet — design stays
streaming-ready, §11); paid BigQuery slots / dedicated clusters (free on-demand pricing suffices).
GCP setup + env contract: `docs/specs/bigquery-deployment.md`.

## 4 · The data-API contract

The backend returns **domain data** plus the computed action title; the frontend constructs
the Plotly figure. Example for chart 2.1 (school constellation):

```
GET /api/charts/schools/2.1
→ {
    "title":    "<computed from warehouse, A2 invariant>",
    "subtitle": "Reading context",
    "series":   [ { "school": "...", "volume": 0, "peak_pct": 0.0,
                    "routes": 0, "equity": 0.0 }, ... ],
    "encoding": { "x": "volume", "y": "peak_pct", "size": "routes", "color": "equity" },
    "meta":     { "unit": "boardings", "n": 0 }
  }
```

- Every chart endpoint has a Pydantic v2 response model in `backend/schemas/`; these models
  ARE the contract and drive OpenAPI, which generates the frontend's TS types.
- Action titles (A2) and all numbers are **computed from the warehouse**, never hard-coded
  (carries the CLAUDE.md invariant across the new boundary).
- `/api/filters` supplies filter-bar option lists (routes, day-types, fare classes, date
  range); the filter bar re-queries chart endpoints with query params.
- `/api/healthz` keeps the Silver/Gold table-presence check.

## 5 · Tooling baseline

| Concern | Choice |
| --- | --- |
| Python deps/build | uv + `pyproject.toml` per package |
| Python quality | ruff (lint+format) · mypy · pytest |
| Data engineering | **dbt** (Silver/Gold transforms + tests) on **BigQuery** (`bq_dev` sampled / `bq_prod` full — primary), optional **dbt-duckdb** `local` sampling target · **Dagster** + dagster-dbt (orchestration, lineage, checks, schedules) · source parquet on **GCS**, Bronze = BigQuery external tables |
| JS deps | pnpm |
| Frontend | Vite · React · TypeScript · Tailwind · shadcn/ui |
| Charts/maps/story | react-plotly.js · react-map-gl (MapLibre) · react-scrollama |
| Server-state | TanStack Query (caching, re-fetch on filter change) |
| JS quality | eslint · prettier · vitest · Playwright (e2e) |
| Containers | Dockerfile per service + docker-compose for local dev |
| CI | GitHub Actions: lint + typecheck + test, per package |

## 6 · Migration plan (each step has a verify gate)

1. **Scaffold** the three packages + tooling + root README + `docker-compose.yml` + CI.
   *Verify:* CI green on the empty skeleton; `docker compose up` serves a backend health
   endpoint and the Vite dev server.
2. **Pipeline (dbt + Dagster).** Split into two sub-phases:
   - **P1a — dbt warehouse + Dagster (BigQuery-primary):** GCP setup (project + GCS bucket +
     `bq_dev`/`bq_prod` datasets + service account, per `docs/specs/bigquery-deployment.md`);
     stage source parquet to GCS and define Bronze as **BigQuery external tables**; translate the
     Silver star (`dim_*`/`fact_*`) + Gold (`agg_*`) into **BigQuery-dialect dbt models** (optional
     DuckDB `local` sampling target via `dbt_utils` macros), **partitioned by `day` + clustered by
     `route_no`/`fare_class`** (BigQuery scale/cost), full-refresh on the sample (incremental is
     the documented production pattern); integrity as dbt tests (unique · not_null · relationships ·
     accepted_values) + a singular **relative lossless** test (`Gold boardings == Bronze ticket
     count`, computed — **not** a fixed number, since data is dynamic); wrap as Dagster assets
     (dagster-dbt) + a lossless asset check. *Verify:* `dbt build --target bq_dev` builds the star +
     Gold in BigQuery with all tests green; the relative lossless check passes; a pytest integration
     asserts `Gold boardings == Bronze count` against BigQuery. **Unblocks P2.**

   Data is **dynamic / continuously-growing**; the 17.9 M-row figure is the current dev sample,
   not a fixed total. All counts/invariants are relative, and `bq_dev` builds against a sampled
   subset while `bq_prod` builds the full (growing) dataset.
   - **P1b — preprocess + gate:** port `preprocess` (CSV → parquet, report §4.3 six steps) as an
     upstream Dagster asset, and implement the §4.3.1 gate (row-count regression · null-rate
     ceiling · referential · PK uniqueness) as Dagster **asset checks** that block the dbt build.
     *Verify:* the preprocess asset reproduces `data/parquet`; the gate check fails on a seeded
     violation and blocks the downstream assets.
3. **Backend port.** Lift the warehouse queries from `demo/aggregates/` into `backend/queries/`,
   wrap them in Pydantic-typed data endpoints, drop all Plotly figure construction.
   *Verify:* httpx contract tests pass for the 9 chart endpoints + kpis + healthz; returned
   numbers match `demo/` for the same charts.
4. **Frontend port, theme by theme** (Schools → Spatial → Health). Build each chart in TS
   from the data API, then the hub, the A3 entity panel, the filter bar, and the Tết story.
   *Verify:* visual parity with `demo/` per theme; Playwright e2e covers hub load, one chart
   render, the entity panel, a filter re-query, and the Tết story scenes.
5. **Decommission `demo/`.** *Verify:* the new stack serves all 9 charts + hub + panel +
   filter + story; then delete `demo/` and the stale `app`-era references.

## 7 · Testing strategy

- **pipeline:** pytest for warehouse integrity (lossless chain, the 41 checks) and profiling
  unit tests; the warehouse build is the contract, so it is the most heavily tested.
- **backend:** httpx contract tests per endpoint — response schema validates + a few key
  numbers asserted (boardings = 17,883,623; student-fare ≈ 36 %; Tết trough −84 %).
- **frontend:** vitest for pure chart-builder functions and components; Playwright e2e for
  the critical paths (hub → chart → entity panel → filter re-query → Tết story).

## 8 · Risks & mitigations

| Risk | Mitigation |
| --- | --- |
| Rebuilding charts in TS is the biggest effort | Port theme-by-theme; keep `demo/` running until parity; only 9 charts in S1. |
| MapLibre + scrollytelling porting | Use maintained React bindings (react-map-gl, react-scrollama), already proven libraries. |
| Data parity drift across the new boundary | Contract tests assert the key warehouse numbers; the warehouse itself is unchanged. |
| DuckDB read-only vs build concurrency | Backend opens read-only; pipeline build runs offline (stop backend, or build to a temp file then swap). |

## 9 · Done criteria (S1)

- Three packages scaffolded, tooled, CI green.
- `pipeline` builds the warehouse via CLI; integrity tests pass (lossless).
- `backend` serves data endpoints for the 9 charts + kpis + filters + healthz; contract
  tests pass.
- `frontend` renders the 9 charts + hub + A3 entity panel + filter bar + Tết story at parity
  with `demo/`.
- `demo/` deleted.

## 10 · Follow-ons (out of scope for S1)

- **S1.x:** wire the remaining 11 catalogue charts (Ridership, Financial, Routes).
- **S2:** report slim-down to 50–70 pp (move material to appendices), realign to the deck, and
  **rewrite §4.3.1 + §4.5** to describe the adopted dbt + Dagster architecture (the current text
  rejects dbt and describes a hand-built Medallion).
- **S3:** diagram migration to draw.io + the render/export pipeline.
- **Data:** full 50-day GPS pull, school geocoding.

## 11 · Forward compatibility / extension points

The package seams (data / API / UI) are chosen so later capabilities slot in without a
rewrite. **None of these are built in S1** — the goal is only to not preclude them.

| Future capability | Fit | What evolves (and where) |
| --- | --- | --- |
| CI/CD | already in baseline | CD = the same `.github/workflows` pushing Docker images. |
| Orchestrator | **adopted in S1 (Dagster)** | dbt models are already orchestrated as software-defined assets with checks; scheduled refresh / new sources = new assets + schedules. |
| Cloud migration | designed for it | containers + 12-factor config deploy anywhere; `db/bus.duckdb` (local file) moves to object storage or a cloud warehouse — swap localised to `backend/db.py` + `queries/`. |
| AI models for analysis | two homes | batch ML in `pipeline/` writes results to Gold; heavy/real-time inference becomes a 4th package (`ml/`/`inference/`) behind the same API. |
| Streaming + streaming analysis | fits, real addition | streaming ingest in `pipeline/` + a broker (Kafka/Redpanda); backend gains WebSocket/SSE push; a hot store (ClickHouse/Timescale/Materialize) joins DuckDB. **No data source today** (data is batch/historical per CLAUDE.md invariants #1, #5) — speculative until then. |

**Cheap-now refinements that keep these doors open (done in S1 because they are good practice anyway):**

1. **Granular pipeline tasks** — `ingest`, `silver`, `gold`, `validate` as independently
   callable functions, not one `build()` monolith (orchestrator-ready).
2. **DB access behind a thin layer** (`db.py` + `queries/`) so the store can be swapped.
3. **12-factor config** (`config.py` / pydantic-settings) from day one.

**Explicit YAGNI:** no broker, no separate ML service, no Kubernetes, no hot store in S1.
The monorepo absorbs a 4th/5th package when a real need arrives.
