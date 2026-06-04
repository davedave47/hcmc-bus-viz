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
├── pipeline/                       # DATA — builds db/bus.duckdb from raw inputs
│   ├── src/busanalytics_pipeline/
│   │   ├── ingest/                 # Bronze: register 24 raw views   (was src/duckdb_loader.py)
│   │   ├── warehouse/              # Silver+Gold: dims, facts, build, validate (was demo/warehouse/)
│   │   ├── profiling/              # programmatic EDA, importable     (was notebooks/05_programmatic_eda.py)
│   │   ├── figures/                # report-figure generation         (was notebooks/06,07_*.py)
│   │   └── cli.py                  # `busanalytics-pipeline build|validate`
│   ├── notebooks/                  # 01–04 .ipynb — exploratory record, import from src (no copy-paste)
│   ├── tests/                      # pytest: warehouse integrity (41 checks) + lossless assert
│   └── pyproject.toml
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
2. **Pipeline port.** Move the Bronze loader + Silver/Gold build into `pipeline/`; expose a
   `build` / `validate` CLI; port the 41-check validation harness into pytest.
   *Verify:* `busanalytics-pipeline build` produces `db/bus.duckdb`; the lossless assert
   (`agg_hub_kpis.boardings == 17_883_623`) and all integrity tests pass.
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
- **S2:** report slim-down to 50–70 pp (move material to appendices), realign to the deck.
- **S3:** diagram migration to draw.io + the render/export pipeline.
- **Data:** full 50-day GPS pull, school geocoding.

## 11 · Forward compatibility / extension points

The package seams (data / API / UI) are chosen so later capabilities slot in without a
rewrite. **None of these are built in S1** — the goal is only to not preclude them.

| Future capability | Fit | What evolves (and where) |
| --- | --- | --- |
| CI/CD | already in baseline | CD = the same `.github/workflows` pushing Docker images. |
| Orchestrator (Dagster/Prefect/Airflow) | clean | wraps `pipeline/` tasks as a DAG; needs granular task functions (see below). |
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
