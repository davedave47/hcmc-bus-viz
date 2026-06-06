# HCMC Bus Analytics — Project Record

> Descriptive record of the current state, locked design, and future plan. Auto-loaded into
> every session. **Keep it descriptive and current:** update sections in place and delete
> outdated content; do **not** narrate before→after changes or keep a change-log. Treat
> conversation memory as transient — this file is the single durable record.
>
> Companion artifacts:
>
> - `backend/` — FastAPI JSON **data API** (the system's serving layer). 9 charts + kpis + filters.
> - `frontend/` — React + Vite + TS **SPA** that consumes the API.
> - `pipeline/` — the **data pipeline** (dbt + Dagster over BigQuery/DuckDB). Designed; build pending.
> - `demo/` — the Phase-1 prototype (FastAPI + Jinja + HTMX + Plotly). The reference the new
>   code ports from and the current source of `db/bus.duckdb`. Superseded once the new stack reaches parity.
> - `report/` — the Phase-1 report (LaTeX, xelatex + biber). See §9.
> - `deck/` — Phase-1 defence deck: `capstone_defence.pptx` (source of truth) + `.pdf` + assets.
> - `docs/specs/chart-catalogue.md` — the canonical 20-chart catalogue + interaction model
>   (**chart truth**; §5 summarises it). `docs/specs/bigquery-deployment.md` — GCP setup + env contract.
> - `docs/conventions/` — `report-writing.md` + `diagrams.md` (draw.io; sources in `docs/diagrams/`).
> - `notebooks/01–07_*.{ipynb,py}` — executed EDA + programmatic profiling (evidence base).

---

## 0 · Current state

**Phase 2 — re-architecting the delivered Phase-1 prototype into a production-grade analytics
platform.** Target: a clean **FastAPI JSON data API** + a **React/Vite/TypeScript SPA**, served
from a **dbt + Dagster** warehouse on **BigQuery** (with DuckDB for local sampling). The data API
returns **domain data + a computed action title**, never Plotly figures; the frontend builds the
charts. Monorepo of three independent packages (`pipeline/` · `backend/` · `frontend/`).

**Built so far (on `main`):**

- **Backend** — the full layered data API: `Warehouse` Protocol (DI), `repositories → services →
  schemas → routers`, a chart **registry** (open/closed), `Theme` enum. Serves all **9 charts**
  (Schools 2.1–2.4 · Spatial 3.1/3.2/3.4 · Network Health 5.1/5.2) + `/api/kpis` + `/api/filters`
  (parameterised filter bar) + `/api/healthz`. Hardened: TTL+LRU caching, structured logging +
  request middleware, global exception handlers. Tests: contract tests run in CI against a
  **synthetic fixture warehouse** (guards the schema seam); exact-number integration tests are
  data-gated. ruff + mypy `strict` clean.
- **Frontend** — foundation + first chart end-to-end: `api/` (typed client) → `hooks/` (TanStack
  Query) → `charts/` (pure Plotly builders + components) → `components/`. Network pulse (5.1) +
  KPI strip render live through the Vite `/api` proxy. typecheck + eslint + vitest clean.
- **Pipeline** — package scaffold only; the dbt/Dagster build is designed, not built.

The backend reads `db/bus.duckdb` (built by `demo/`) read-only **until the pipeline lands**.

**Run (dev):**

```
# backend (reads db/bus.duckdb)
cd backend && uv run uvicorn busanalytics_api.main:app --port 8000
# frontend (proxies /api -> :8000)
cd frontend && pnpm dev          # http://localhost:5173
```

To free a port use `fuser -k <port>/tcp` (NOT `pkill -f uvicorn` — self-match risk).

---

## 1 · Problem

> HCMC's bus network produces ~17.8 M AFC boarding events per quarter + ~50 days of GPS
> telemetry per release window, yet **no accessible tool turns either stream into operational
> insight** for the people the network serves. Existing apps (BusMap, GoBus!, MultiGo) do
> real-time passenger routing — they don't answer "how reliable is route 72?", "where is the
> network undersupplied?", or "what does the data say about us as riders?". This project builds
> an **analytical & visualisation platform** over the historical GPS + AFC record, for both the
> operations side (planners, operators) and the rider side (passengers, businesses).

**Big idea:** make the network's **performance, equity, and shocks** visible to planners,
operators, and passengers through 20 coordinated charts, with schools and students as the focus.

**Flagship differentiator:** school-aware ridership — leverages the ~36 % student-fare share
unique to HCMC's ticketing data; no global tool does this. **Proof-of-value case study:** the
Tết 2026 shock (see §4).

---

## 2 · Users (3 personas — internal design tool only, NOT shown in UI)

| Role | Decision the tool helps them make |
| --- | --- |
| 👤 **passenger** | Which route to commit to (reliability) · when to ride (crowding) · is my school served (student variant) |
| 🏢 **operating company** | Where to add/cut capacity · which routes are profitable (₫/trip, waste %) · rank vs peers · did the promo work |
| 🏛 **public-transport authority (MCPT)** | Where service ≠ riding · which routes need scrutiny (QoS) · network shock & recovery · coverage/equity gaps · bus↔metro integration |

**Driver is data, not a user** — driver records flow into the warehouse and surface inside
company/authority views; no driver-facing screen. The UI shows no role badges and no role
switcher; charts are role-agnostic and the date window is global. Personas drive **internal
feature prioritisation only**.

### 2.1 · 14 stakeholder questions (every chart traces to one)

| #    | Question (short)                                                  | Persona · tier               |
| ---- | ----------------------------------------------------------------- | ----------------------------- |
| P-Q1 | Is route X reliable enough to commit to?                          | passenger · Must             |
| P-Q2 | When is route X / stop Y least crowded?                           | passenger · Must             |
| P-Q3 | Does this route serve my school's commute window?                 | passenger 🌟 · Must          |
| C-Q1 | Which of my routes are over/under-served vs riding?               | company · Must               |
| C-Q2 | Route-level revenue picture (₫/trip, waste %)?                    | company · Must               |
| C-Q3 | How do I rank vs other operators on the same corridors?           | company · Must               |
| C-Q4 | Did my last promotion lift ridership (DiD)?                       | company · Should             |
| A-Q1 | Where does service ≠ riding across the network?                   | authority · Must             |
| A-Q2 | Which routes/operators have reliability problems (QoS-1/2/3)?     | authority · Must             |
| A-Q3 | How does the network absorb / recover from shocks (Tết, Apr 30)?  | authority · Must             |
| A-Q4 | Where are coverage / equity gaps (schools, districts)?            | authority · Must             |
| A-Q5 | How well does bus integrate with Metro Line 1 (transfer timing)?  | authority · Must             |
| A-Q6 | What is the market structure (operator concentration, HHI)?       | authority + company · Should |
| A-Q7 | What will ridership look like over the next 14 days (forecast)?   | authority + company · Should |

Requirements layer: **R1–R15** functional, **N1–N6** non-functional (N1 = warm re-render budget,
the latency gate). Full records in report Ch 4.1.

---

## 3 · Data invariants (NEVER VIOLATE)

1. **GPS window ≠ AFC window.** GPS = Mar 20 – May 10 2025 (local sample: 1 day, 2025-03-18).
   AFC = Jan 1 – Mar 31 2026 (~17.8 M rows). **No timestamp-level join.**
2. **Cross-source joins are at `route × hour-of-day × day-type`** ("B framing"). GPS gives
   *operations*; AFC gives *ridership*; combine only at the aggregate profile level.
3. **`user_id` is 0.1 % populated** (23,109 of 17,883,623). Individual-user features (loyalty,
   churn, journeys) are **out of scope** — data killed them.
4. **No alighting data.** AFC records boardings only. "Live occupancy" is not computable.
5. **Boardings are cumulative** — there is no "people on bus at time T".
6. **Plan as if A, demo as if B.** Plan = full 50-day GPS from Kaggle. Demo = 1-day local.
7. **Schedule data has ~91k `service_type='unknown'`** — adherence features need cleaning.
8. **GPS `speed` is ~50 % null** (358,156 of 720,088 on 2025-03-18). Any operating-regime feature
   must declare a null strategy (drop / impute / interpolate).
9. **GPS and AFC drivers are disjoint.** Overlap = 42 keys (2.4 % / 6.4 %). No driver-level
   cross-source join.
10. **`gps.schedules` has ~39 % full-row duplicates** (109,620 of 283,134); safe to `.unique()` at ingest.
11. **Cross-source route join is `route_no` ONLY.** `route_id` splits into two disjoint keyspaces
    (GPS vs AFC). Never join cross-source on `route_id`.
12. **Local GPS sample lacks 5 fields the full Kaggle dataset has** (`heading · ignition · aircon ·
    sos · working`). The **`working` flag is a per-vehicle school-bus marker** — cross-validates
    fare-level student inference. Pull full Kaggle GPS before any school-bus vehicle-identity analytics.
13. **GPS `extracted.hmm_state` is the SOURCE's segmentation, not ours.** The provider labels each
    ping **Travel / Dwell / Outage** by a Hidden Markov Model; it is the basis for trips and
    stop-visits. We consume it, we do not train it.
14. **The dataset is dynamic, not fixed.** The ~17.88 M AFC rows are the **current sample**;
    production ingests continuously-growing data (far larger). Invariants are **relative** —
    e.g. `Gold boardings == Bronze ticket count` (computed each run), never a hard-coded number.

---

## 4 · Measured data facts (these are MEASURED on the current sample)

| Discovery | Value | Note |
| --- | --- | --- |
| AFC volume | **17,883,623** boardings | Jan–Mar 2026 sample, lossless through Gold |
| AFC revenue | ~₫72 B (90 days) | |
| Student-fare share | **~36 %** | the flagship signal |
| Cash dominance | **96.2 %** of payments | |
| Fare-class mix | ~43 % regular cash · ~36 % student · ~16 % free | |
| Routes | **128 AFC** / 163 GPS / 121 shared | |
| Ridership concentration | 80 % of boardings on ~55 of 128 routes | heavy-tailed |
| Weekday twin peaks | ~22k/hr at ~6 AM and ~4–5 PM | |
| **Tết 2026 shock** | window **Feb 14–22**; **−57 % avg**, **−84 % trough Feb 16** (33,176); recovers ~**Feb 23** | the proof-of-value case |
| Anchor universities | 8 (HCMUS, HCMUT, UEH, GTVT, USSH/KHXH-NV, HCMUTE, UIT, SGU) | |
| Biggest school→route edge | Route 20 → KHXH-NV (~16k students, all-fare; ~8k student-fare) | |
| Stops | 4,710 with lat/lng | |
| GPS local sample | 1 day, 131 vehicles, 720,088 pings | full = ~32 M over 50 days |

> All chart action titles are **computed from the warehouse**, never hard-coded.

---

## 5 · Chart catalogue — 20 canvases, 6 themes (LOCKED)

Canonical spec: `docs/specs/chart-catalogue.md` (per-chart 10-field defence specs). Distribution
**4 / 4 / 3 / 4 / 2 / 3**. Charts ordered within a theme by **persona breadth** (front-door first).
Readability tiers: **A** instant front-door · **B** rewards a second pass · **C** drill-in depth.
**9 of 20 served by the backend data API** (Schools 4 · Spatial 3 · Health 2).

| Theme | # | Chart | Primitive | Tier |
| --- | --- | --- | --- | --- |
| **1 · Ridership & Crowding** (4) | 1.2 | Route × hour heatmap (hover→sparkline) | Heatmap | B |
| | 1.3 | Route constellation (mean × variance × peak × archetype) | Bubble scatter | A |
| | 1.1 | Ridership streamgraph (fare class × 90 days) | Streamgraph | A |
| | 1.4 | Bump chart — top-20 routes' rank over 12 weeks | Bump chart | B |
| **2 · Schools & Students 🌟** (4) | 2.1 | School constellation (vol × peak% × routes × equity) | Bubble scatter | A |
| | 2.2 | School→route treemap with drill | Treemap | A |
| | 2.4 | School proximity map with walking circles | Annotated map | A |
| | 2.3 | Weekly fare-class heatmap (live filter bar) | Calendar heatmap | A |
| **3 · Spatial & Connectivity** (3) | 3.1 | Multi-layer hex map (density · per-stop · ghost layers) | Hex bin map | A |
| | 3.2 | Bus↔Metro Sankey *(indicative — Metro schedule hard-coded)* | Sankey | A |
| | 3.4 | Accessibility isochrone from chosen origin | Isochrone map | A |
| **4 · Financial & Operations** (4) | 4.2 | Operator constellation (share × rev/trip × fleet × on-time) | Bubble scatter | A |
| | 4.1 | P&L quadrant (waste × rev/trip × volume × company) | Quadrant scatter | B |
| | 4.3 | Payment-channel streamgraph | Streamgraph | A |
| | 4.4 | Free-fare student-day lift waterfall + synthetic control | Waterfall | B |
| **5 · Network Health** (2) | 5.2 | QoS small-multiples scatter (QoS-1/2/3) | Small multiples | A |
| | 5.1 | Network pulse with anomaly bands + threshold slider | Timeline + bands | A |
| **6 · Routes** (3) | 6.4 | Per-stop arrival box plot along route | Box plot | A |
| | 6.3 | Stop-by-stop boardings + door-dwell dual axis | Dual-axis bar+line | B |
| | 6.2 | Marey time-distance diagram + dwell heatmap | Marey + heatmap | C |

**Banned primitives:** pie, donut, 3D, word cloud, dendrogram-as-primary, radar/radial, horizon,
ridgeline, chord, in-cell sparkline as primary. Two conditional extensions live outside the 20:
bus-as-traffic-sensor speed grid (needs full GPS) and speed-vs-posted-limit map (needs OSM road-speed).

**SDVF tiers:** 🌟 flagship = Schools & Students · ✅ Must = Network Health, Ridership, Financial,
Spatial, Tết case, Bus↔Metro · 🟦 Should = Reliability, route discovery, forecast, speed grid ·
🟥 Won't-yet = arrival-time bands, driver fingerprint (#9), user-level loyalty (#3), text-to-SQL,
rain/electric-bus analytics.

---

## 6 · UI & interaction model (LOCKED)

**Hierarchy:** `Hub → Theme (card) → Chart`. Light theme, full-bleed.

- **Hub** — editorial vertical scroll; 6 full-width teasers with real warehouse KPIs; each offers
  "Start exploring" + (where a Story exists) "Read the story".
- **Theme card** — left chart rail (the theme's 2–4 charts), top View Controls bar (date range +
  theme-specific filter), main canvas = one chart at ~70 % of viewport.
- **Chart** — interactive; action title in the caption header; click any entity → entity-detail panel.

**Coordination = click-to-entity-detail panel.** One chart per canvas, so simultaneous cross-chart
brushing would be structurally invisible. The single mechanism: **one click on any entity → A3
universal entity-detail panel** (≈40 % viewport, slides from right, ≤4 mini-views, tabs when needed)
— the Yi (2007) *Connect* category as a panel handoff. The other six Yi categories (Select · Explore
· Reconfigure · Encode · Abstract/Elaborate · Filter) stay first-class within each chart via the
View Controls bar. **Universal click contract:** one click = panel; drill/zoom/expand are separate
affordances; one click never has two meanings. Grounded in Yi 2007, Heer & Shneiderman 2012,
Shneiderman 1996. *(The backend serves the data for the panel + the filter bar; the React UI for both
is to be built — see §11.)*

**Chart invariants (durable):**

- **A2 · Action title + subtitle.** Title states the finding; subtitle gives the reading context.
  Muted defaults; one focal accent on the element the story points at. Titles computed from the warehouse.
- **A4 · Bar charts have a zero baseline.** (Line charts may use a non-zero baseline — flag it.)
- **A5 · 3–8 second story test.** Every chart surfaces its finding within 3–8 s.
- **A6 · One primitive per theme.** A repeat becomes a filter/toggle on the first (theme-scoped).
- **Multi-encoding bias.** No chart whose only data channel is bar length.

**Stories (scrollytelling) — sticky-graphic mechanic.** Each Story = Bing hero → 1–2 scroll sections
that each **pin one chart** (`position: sticky`) while step panels scroll past firing transitions
(highlight · annotation · filter · encode) → Bongo recap + CTA. A primitive change happens only at a
section boundary. **Two-tier sourcing:** Tier 1 = catalogue chart frozen in a story state; Tier 2 =
bespoke story-only chart. **4 stories, 26 scenes** (School / Spatial / Financial / Tết); only the Tết
story exists (in `demo/`). Scene inventories: report Appendix D.

---

## 7 · Architecture (Phase 2)

### 7.1 · Data engine — dbt + Dagster, BigQuery-primary

Production scale is **millions of trips/tickets per day**, so the engine must scale past one node.
The design **separates storage from compute** with **dbt** as the portability seam:

- **Storage** — source parquet staged to **GCS**; Bronze = BigQuery **external tables** over it.
  A local parquet copy backs the optional DuckDB sampling target.
- **Transform** — **dbt** models: Bronze sources → **Silver Kimball star** (`dim_*` tables +
  `fact_*` views) → **Gold** aggregates (`agg_*`, one per chart contract). Models are BigQuery-dialect
  first; dialect-specific SQL is macro-ized (`dbt_utils`) for the DuckDB local target. Fact/Gold are
  **partitioned by `day` + clustered by `route_no`/`fare_class`**; production path is **incremental**.
- **Compute** — BigQuery for both **`bq_dev`** (sampled dataset) and **`bq_prod`** (full); a DuckDB
  **`local`** target is an offline sampling convenience, not the source of truth.
- **Ingestion (micro-batch)** — new data lands in batches (daily/hourly exports) to GCS;
  **Dagster sensors** trigger an **incremental** dbt run that appends new `day` partitions.
  Dashboard freshness is hours, not seconds.
- **Orchestration** — **Dagster** (dagster-dbt software-defined assets, DuckDB resource, asset
  checks, freshness sensors).
- **Serving cube** — the filter-bar charts read a pre-aggregated **Gold cube** (date × route ×
  day-type × fare-class × hour), **not** the raw fact, so per-request BigQuery cost/latency stays
  bounded as the fact grows.
- **Integrity** — dbt tests (unique · not_null · relationships · accepted_values) + a singular
  **relative lossless** test (`Gold boardings == Bronze ticket count`).
- **No streaming-analytics engine** (Flink / Spark Streaming / Materialize): the product is
  **batch aggregate analytics over a growing record**, and the invariants (no alighting,
  cumulative boardings) preclude real-time occupancy. The stack scales to dynamic data via
  micro-batch ingestion + incremental partitioned models — no new paradigm. Deferred scale-ups
  (not built now): streaming ingest (Pub/Sub), dlt, Terraform/IaC, dbt contracts, Elementary,
  Iceberg/Delta, Spark/Databricks. GCP setup + env contract: `docs/specs/bigquery-deployment.md`.

**Silver star** (Kimball-dimensional): `dim_date` (tags `is_tet_2026` Feb 14–22 + trough + pre-Tết
baseline + Apr-30) · `dim_hour` · `dim_route` (1:1 on `route_no`) · `dim_stop` · `dim_school` +
`dim_school_stop` bridge · `dim_trip` · `dim_company` · `dim_fare_class` · `dim_payment_channel` ·
`dim_vehicle` · `dim_promotion`; facts `fact_boardings`, `fact_gps_trips`, `fact_stop_visits`.
Three source defects are fixed in Silver so the chain is arithmetically lossless: `ticket_trips`
trip-id dupes (dedup), `route_no` leading-zero variants (1:1), stops near two universities
(closest-school-wins bridge). **Gold:** `agg_network_day` · `agg_route_hour` · `agg_route_day` ·
`agg_stop_hour` · `agg_stop_total` · `agg_school_route` · `agg_hub_kpis`.

### 7.2 · Backend — FastAPI data API (layered + DI)

Clean layering, dependencies pointing one way:

- **`api/routers`** — HTTP only (parse, inject, call a service, return a schema). `Theme` enum →
  automatic 422. `deps.get_warehouse` injects the warehouse via `Depends`.
- **`services/charts`** — domain logic: compute the series + the A2 action title. Framework-agnostic
  (no FastAPI, no Plotly). `services/registry.py` maps `(Theme, slug) → service` (open/closed).
- **`repositories`** — warehouse SQL → typed rows. User input is **parameterised**; segment/day-type
  allow-listed.
- **`schemas`** — Pydantic `ChartResponse` DTO = the wire contract: `{theme, slug, title, subtitle,
  series, encoding, meta}`. **Domain data, not Plotly figures** — the frontend builds the figure.
- **`db.py`** — `Warehouse` Protocol (dependency-inversion seam) + `DuckDBWarehouse` impl. Swapping
  to BigQuery later = a `BigQueryWarehouse` impl + the provider in `deps.py`; the repositories'
  SQL dialect is the remaining swap work (documented in `db.py`).
- **`core`** — TTL+LRU `cache` (on charts/kpis/filters), `logging` (setup + request middleware),
  `errors` (global handlers: 503 warehouse-unavailable, 500 structured).
- **`domain`** — `Theme` enum, `ChartKey`.

Endpoints: `GET /api/charts/{theme}/{slug}` · `/api/kpis` · `/api/filters` · `/api/healthz`.
Tests: **contract tests run in CI** against a synthetic fixture warehouse (every endpoint's
SQL/service/schema, guarding the backend↔warehouse seam); exact-number **integration tests** are
data-gated. Reads `db/bus.duckdb` read-only today; points at BigQuery once the pipeline lands.

### 7.3 · Frontend — React SPA

React + Vite + TypeScript, feature-based: **`api/`** (typed client + contract types) → **`hooks/`**
(TanStack Query: `useChart`, `useKpis` — components never fetch) → **`charts/`** (presentational
components + **pure Plotly figure builders** in `lib`, testable without React; a registry maps
`chartId → component`) → **`maps/`** (MapLibre) · **`stories/`** (Scrollama) → **`components/`**
(shell, ChartCard, EntityPanel, FilterBar) → **`features/`** (hub, theme, story). react-plotly.js
(slim Plotly bundle). Dev: Vite proxies `/api` → backend. Types are hand-kept now; OpenAPI
generation is a follow-up.

---

## 8 · Repo layout

```
busanalytics/
  pipeline/   data: dbt project (Bronze sources → Silver star → Gold) + Dagster (assets, checks).
              BigQuery primary, DuckDB local sample. (Scaffold built; transforms pending GCP.)
  backend/    FastAPI JSON data API (layered, DI). src/busanalytics_api/{api,services,repositories,
              schemas,domain,core,db.py,config.py,main.py}; tests/ (contract + integration).
  frontend/   React + Vite + TS SPA. src/{api,hooks,charts,maps,stories,components,features,lib}.
  demo/       Phase-1 prototype (FastAPI+Jinja+HTMX+Plotly+DuckDB). Reference to port from +
              current source of db/bus.duckdb. Superseded at parity.
  src/        duckdb_loader.py — Bronze loader that registers the 24 raw views db/bus.duckdb sits on.
  notebooks/  EDA + programmatic profiling (evidence base).
  db/ data/   warehouse + raw inputs (gitignored).
  report/     Phase-1 report (LaTeX). deck/ — defence deck + assets.
  docs/       specs/ · diagrams/ (draw.io sources) · conventions/ · reference/ · project/ · design/.
```

---

## 9 · Report — Phase-1 deliverable (`report/`)

LaTeX (xelatex + biber), `\documentclass[12pt]{report}`, Times New Roman, ~174 pages. Front matter →
**Ch1** Introduction → **Ch2** Related Work → **Ch3** Theoretical Background (7 §) → **Ch4** Proposed
Solution (8 §, largest) → **Ch5** Prototype Implementation → **Ch6** Future Work → **Ch7** Conclusion
→ references → **Appendices A–E** (DDL + field inventories + data-quality observations · schedule +
risk register · benchmarks · story scenes · rejected primitives). Title *"Studying and Developing
Tools to Analyze and Visualize Bus Data"*; supervisor Assoc. Prof. Thoai Nam; student Huynh Thanh Duy
2252114. `\imageplaceholder{type}{what}{capture}` marks un-captured figures. The report describes the
Phase-1 Medallion prototype; the S2 revision (§11) re-aligns it to the Phase-2 architecture.

---

## 10 · Reference & competitive moats

**Techniques borrowed:** Knaflic (storytelling; forbidden pie/donut/3D) · Segel & Heer 2010
(narrative-viz taxonomy) · Liu 2022 (MCV) · Chawuthai/Srisakaokul 2023 (Bangkok QoS-1/2/3) ·
Derevitskiy 2016 (bus-as-sensor speed) · Lin & Zeng 2014 (Marey arrival prediction) · Cleveland &
McGill 1984 + Munzner 2014 (chart-selection rubric) · Yi 2007 + Heer & Shneiderman 2012 +
Shneiderman 1996 (interaction taxonomy) · Nguyen & Thoai (HCMC dataset doc).

**Competitive moats:** (1) school-aware ridership (unique to HCMC student-fare data); (2) AFC + GPS
integrated at `route × hour × day-type` (Swiftly is GPS-only, fare vendors AFC-only); (3) in-theme
Stories on a live dashboard; (4) one multi-stakeholder surface across 3 personas; (5) HCMC-specific
pre-tagged anomaly catalogue (Tết, Apr-30). Frame carefully: "no *accessible, multi-stakeholder,
analytical* dashboard for HCMC bus exists" — MCPT may have internal SCADA we can't see.
`bus.dev.tris.vn` (Tris research demo) = a single Gridify heatmap, ≈ our chart 3.1 only.

---

## 11 · Future plan / roadmap

**Pipeline (the data source of truth).** Build the dbt + Dagster warehouse on BigQuery — translate
the Silver star + Gold into **incremental, partitioned** dbt models, integrity as dbt tests + the
relative lossless test, wrapped as Dagster assets; the preprocess (exports → parquet → GCS) asset +
the validation gate (row-count regression · null-rate ceiling · referential · PK uniqueness) as
asset checks; a **Dagster sensor** that triggers the incremental run on new GCS partitions; and the
**filterable Gold cube** (date × route × day-type × fare-class × hour) the filter-bar endpoints read.
**Pending the user's GCP project / bucket / service-account env vars**
(`docs/specs/bigquery-deployment.md`). Add a contract test that the warehouse schema matches what the
backend reads.

**Frontend.** Build the 8 remaining charts (TS Plotly builders + components), the hub, theme cards +
routing, the A3 entity panel, the filter-bar UI, and the Tết story; add an **error boundary** and
**code-split Plotly** (the bundle is ~4.8 MB). Then decommission `demo/`.

**Backend should-fix.** OpenAPI-generated frontend types · request timeouts/limits · explicit
auth/CORS decision · build + smoke-test the Docker images in CI · coverage reporting + Dependabot ·
Playwright e2e.

**Catalogue completion.** Wire the remaining 11 charts end-to-end (Ridership 4 · Financial 4 ·
Routes 3) — backend services + frontend components; build the 3 unbuilt stories (School / Spatial /
Financial).

**Report (S2).** Slim to 50–70 pp (move material to appendices); rewrite §4.3.1 + §4.5 to the
dbt + Dagster + BigQuery architecture; fix the known inconsistencies (stale MCV glossary entry; Tết
recovery date should be Feb 23 everywhere; roadmap warehouse counts; a Ch7.1 typo).

**Diagrams (S3).** Migrate the legacy Mermaid sources (`dataset_erd`, `interaction_sequence`,
`foundations_layered`; deck `erd_afc`/`erd_gps`) to draw.io + a render/export step.

**Data.** Full 50-day Kaggle GPS pull (unlocks reliability scorecard, speed grid, Apr-30 study, the
`working` school-bus flag) · school geocoding · schedule cleaning (91k `unknown` service-types) ·
Metro Line 1 schedule · HCMC weather + OSM road-speed (Phase 2.5+).
