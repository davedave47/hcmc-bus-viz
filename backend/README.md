# backend — data API

A FastAPI JSON **data API** over the analytics warehouse. Each endpoint returns the **domain data**
a chart needs plus an abstract title; it never returns Plotly figures — the frontend builds the
visuals. It reads `db/bus.duckdb` read-only today and swaps to BigQuery behind one seam when the
pipeline lands.

**Status: built.** Serves 9 charts (Schools 2.1–2.4 · Spatial 3.1/3.2/3.4 · Health 5.1/5.2) plus
`/api/kpis`, `/api/filters`, and `/api/healthz`. Contract + service tests; ruff and mypy (strict) clean.

## Stack and tooling

- Python 3.12 · **FastAPI** + Uvicorn · **Pydantic v2** (+ pydantic-settings) · **DuckDB** (read-only).
- **uv** for dependencies and build · **ruff** (lint + format) · **mypy** (strict) · **pytest** +
  httpx for tests · a `Dockerfile` for the container.

## Design principles

Clean layering with dependencies pointing **one way** (`api → services → repositories`), so each
layer is understandable, testable, and replaceable on its own.

- **`api/`** — HTTP only. Routers parse params, call a service, return a schema; no SQL, no business
  logic. The db connection and settings are injected through `api/deps.py` (FastAPI `Depends`),
  never imported globally.
- **`services/`** — domain logic: compute the chart series, derive the abstract title, apply filters.
  **Framework-agnostic** (never imports FastAPI), so it unit-tests in isolation. `services/charts/`
  holds the per-theme services; `services/registry.py` maps `(theme, slug) → service`. Adding a
  chart is adding a service module and registering it — no existing code is edited (open/closed).
- **`repositories/`** — data access only: warehouse SQL to typed rows, every input parameterized.
  Services depend on this interface, not on DuckDB directly, so the store can be swapped.
- **`schemas/`** — the Pydantic v2 DTOs at the boundary. They **are** the wire contract and drive
  the OpenAPI that generates the frontend's types.
- **`domain/`** — internal types and enums (`Theme`, `ChartKey`). **`db.py`** — a `Warehouse`
  Protocol (the dependency-inversion seam) plus a `DuckDBWarehouse` implementation. **`core/`** —
  TTL+LRU cache, structured logging + request middleware, global exception handlers.
  **`config.py`** — 12-factor settings.

## Directory

```
backend/
├── src/busanalytics_api/
│   ├── main.py            # app factory + lifespan (wiring only)
│   ├── config.py          # settings (pydantic-settings)
│   ├── db.py              # Warehouse Protocol + DuckDBWarehouse
│   ├── api/
│   │   ├── routers/       # charts · kpis · filters · health
│   │   └── deps.py        # inject db + settings
│   ├── services/
│   │   ├── charts/        # per-theme services (series + abstract title)
│   │   └── registry.py    # (theme, slug) → service
│   ├── repositories/      # warehouse SQL reads
│   ├── schemas/           # Pydantic DTOs = the API contract
│   ├── domain/            # Theme, ChartKey
│   └── core/              # cache · logging+middleware · errors
├── tests/                 # pytest + httpx (contract + service unit)
├── Dockerfile
└── pyproject.toml
```

## The data-API contract

Every chart endpoint returns `{theme, slug, title, subtitle, series, encoding, meta}` — domain data,
not figures. Titles are abstract (the capability or question), not derived from the data, so nothing
goes stale as the data grows. Endpoints: `GET /api/charts/{theme}/{slug}` · `GET /api/kpis` ·
`GET /api/filters` · `GET /api/healthz`.

## Run, test, lint

```bash
uv sync                                              # install
uv run uvicorn busanalytics_api.main:app --reload --port 8000
uv run pytest -q                                     # tests (exact-number tests are data-gated)
uv run ruff check . && uv run mypy src               # lint + types
```

## Swapping DuckDB → BigQuery

Add a `BigQueryWarehouse` implementation of the `Warehouse` Protocol and switch the provider in
`api/deps.py`; the repositories' SQL dialect is the remaining work. Nothing above `repositories/`
changes.
