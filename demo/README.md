# HCMC Bus Analytics — Phase 1 Demo

A running prototype of the analytical surface specified in the capstone
report (`report/main.pdf`). Server-rendered FastAPI application over a
Medallion DuckDB warehouse, serving an editorial hub, three analytical
cards, and one scrollytelling story.

> Built from scratch under `demo/`. The older `app/` directory is unrelated
> and is not used by this demo.

---

## Quick start

```bash
# 1. install deps (from repo root)
pip install -r demo/requirements.txt

# 2. build the Silver + Gold warehouse tiers (one-time, ~5s)
#    Bronze (raw views) already exists in db/bus.duckdb
python -m demo.warehouse.build

# 3. run the server
uvicorn demo.main:app --port 8765 --reload

# 4. open
#    http://127.0.0.1:8765/            hub
#    http://127.0.0.1:8765/cards/schools   Card 2 (School-Aware Demand)
#    http://127.0.0.1:8765/cards/spatial   Card 3 (Spatial & Connectivity)
#    http://127.0.0.1:8765/cards/health    Card 5 (Network Health)
#    http://127.0.0.1:8765/cards/health/story/tet   Tết story
```

`db/bus.duckdb` must exist (it holds the Bronze raw views built by
`src/duckdb_loader.py`). The server opens it **read-only**; the build
script opens it read-write, so stop the server before rebuilding.

---

## Architecture — Medallion (Bronze / Silver / Gold)

```
Bronze   24 raw parquet views (src/duckdb_loader.py)         immutable input
   │     register · no copy
Silver   12 dimension tables + 3 fact views                  conformed, deduped
   │     build · 5.4s · O(N)
Gold     7 pre-computed aggregate tables                     chart-ready
   │     one SELECT per chart
Surface  FastAPI + Jinja2 + HTMX + Plotly                    11 charts + 1 story
```

### Silver tier (12 dims + 3 facts) — built by `demo/warehouse/dims.py`, `facts.py`

Dimensions: `dim_date` (with `is_tet_2026` / `is_apr30_window` tagging),
`dim_hour`, `dim_route` (1:1 on route_id), `dim_stop`, `dim_school`,
`dim_school_stop` (closest-uni bridge), `dim_trip` (dedup), `dim_company`,
`dim_fare_class`, `dim_payment_channel`, `dim_vehicle`, `dim_promotion`.

Fact views (not materialised — DuckDB pushes predicates through):
`fact_boardings`, `fact_gps_trips`, `fact_stop_visits`.

Three raw-data row-multiplication bugs are resolved here so the
Bronze→Gold chain is **arithmetically lossless** (`agg_hub_kpis.boardings
= 17,883,623`, exact match with raw `tickets`):

| Raw defect | Silver fix |
|---|---|
| `ticket_trips.trip_id` has 4,051 duplicate ids | `dim_trip` (one row per trip_id) |
| 3 route_ids carry leading-zero variants ("03"/"3") | `dim_route` (1:1 on route_id) |
| 19 stops within 500 m of two universities | `dim_school_stop` (closest-uni-wins) |

### Gold tier (7 tables) — built by `demo/warehouse/build.py`

`agg_network_day`, `agg_route_hour`, `agg_route_day`, `agg_stop_hour`,
`agg_stop_total`, `agg_school_route`, `agg_hub_kpis`. Every chart reads
exactly one Gold table.

---

## API surface

| Route | Returns |
|---|---|
| `GET /` | hub page (HTML) |
| `GET /cards/{schools,spatial,health}` | card interior (HTML) |
| `GET /cards/{theme}/chart/{slug}` | HTMX chart fragment |
| `GET /cards/health/story/tet` | Tết scrollytelling story |
| `GET /api/charts/{theme}/{slug}` | Plotly figure JSON |
| `GET /api/aggregates/{name}` | raw aggregate rows (JSON) |
| `GET /api/kpis` | hub stats strip (JSON) |
| `GET /api/healthz` | liveness + Silver/Gold table presence |

`{theme}` ∈ `schools` (1.1–1.5), `spatial` (3.1, 3.2, 3.4), `health` (5.1–5.3).

---

## Coverage

| Card | Wired | Phase-2 stubs |
|---|---|---|
| 2 · School-Aware Demand | 1.1 top schools · 1.2 schools→routes treemap · 1.3 weekly fare-class heatmap · 1.4 school-routeness parcoords · 1.5 proximity map | 1.6 bipartite · 1.7 student-flow sankey |
| 3 · Spatial & Connectivity | 3.1 hex density (MapLibre) · 3.2 bus→metro sankey · 3.4 stop-catchment voronoi | 3.3 cartogram · 3.5 isochrone |
| 5 · Network Health | 5.1 Tết pulse · 5.2 service calendar · 5.3 QoS-proxy scorecard | — |
| Story | "Nine days without a network" (Tết, 6 Bing-Bang-Bongo scenes) | — |

Cards 1 (Demand), 4 (Financial), 6 (Routes) are hub teasers only.

Not yet wired: A1 within-card linked brushing and A3 entity-detail panel
(the chrome slots exist; the behaviour is Phase-2 work).

---

## Benchmarks

```bash
python -m demo.warehouse.benchmark   # stop the server first (needs RW for Pass 3)
```

Five measured passes (against the running warehouse, this workstation):

1. **Silver-only vs Silver+Gold** — 6.1× total chart-catalogue speedup
   (5.5 s → 0.9 s per page load); up to 2,139× per aggregate.
2. **LRU-cache counterfactual** — cold-LRU equals the Silver-only cost
   and resets on every process restart; Gold persists on disk (~30 MB),
   shared across workers.
3. **Build scaling** — 2× input → 1.95× build time, confirming O(N).
4. **Star-schema-over-raw** — +17.90 % boarding-count inflation (the
   three row-multiplication bugs unresolved); rejected on integrity.
5. **Chart-endpoint p50/p99** — median p50 = 31 ms; 9/11 endpoints pass
   the 100 ms p99 budget (spatial/3.1 marginal at 102 ms; spatial/3.4
   voronoi 311 ms, CPU-bound on `scipy.spatial.Voronoi`).

---

## Data invariants (do not violate)

- AFC `tickets` = Jan 1 – Mar 31 2026, 17,883,623 rows. **No timestamp join
  to GPS** (GPS is a different window).
- `tickets_clean` is a stale 16-day Dec-2025 snapshot — **do not use it**.
- Student-fare proxy is `ticket_type LIKE '%HS-SV%'` (≈ 36 %).
- Tết 2026 window = **Feb 14–22**, trough Feb 16, recovery Feb 23 (sourced
  from `dim_date`, not hard-coded).
- School attribution is hand-verified for 8 universities; UIT is a
  district-level stub (`verified = false`).
