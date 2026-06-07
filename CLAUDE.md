# HCMC Bus Analytics — Project Record

> The always-loaded **map** of the project: what it is, the rules I work under, and **where
> everything lives**. This file points to the docs; it does not duplicate them — open the referenced
> doc when detail is needed. Keep it current; delete what is no longer true.

## 1 · What it is, and current state

An analytics & visualization platform over Ho Chi Minh City's bus network — a **dynamic,
continuously-growing** record of AFC fare transactions and GPS telemetry — serving passengers,
operators, and the public-transport authority **equally**. It surfaces accumulated patterns (not
live tracking), built for data that keeps arriving via micro-batch ingestion.

Monorepo of three packages:

- **`backend/`** — the FastAPI **data API is built**: 9 charts (Schools · Spatial · Health) + kpis +
  filters + healthz; layered + dependency-injected; returns domain data, never figures; tested;
  ruff/mypy clean. Reads `db/bus.duckdb` for now.
- **`frontend/`** — React/Vite/TS SPA: **foundation + the first chart** (network pulse) render live.
- **`pipeline/`** — **scaffold only**; the dbt + Dagster + BigQuery warehouse is designed (see
  `docs/specs/2026-06-04-phase2-s1-rearchitecture-design.md`), not built.

`demo/` is the Phase-1 prototype that currently builds `db/bus.duckdb`; superseded at parity.

**Run (dev):** `cd backend && uv run uvicorn busanalytics_api.main:app --port 8000` ·
`cd frontend && pnpm dev` · or `docker compose up`. `make help` lists tasks. Free a port with
`fuser -k <port>/tcp`.

## 2 · Rules I work under

- **Dynamic data**, never "historical/static"; the ~17.9 M AFC rows are the *current sample*, not a
  headline number → memory `feedback_dynamic_data_framing`.
- **All stakeholders equal** — no schools/students flagship; storytelling is generated from the
  current data window so it does not go stale → `feedback_equal_stakeholders_dynamic_story`.
- **Captions, titles, hero text are abstract** — the capability/question, never the data; the visual
  carries the specifics → `feedback_abstract_captions`.
- **No defensive over-explaining**; the report and deck are **low-context** for the council (no
  "Phase 1", no internal references) → `feedback_no_over_explaining`.
- **Feature decisions = impact × effort + three states** (perfect 100 / desirable 50 / fallback 10),
  with alternatives recorded → `feedback_feature_decision_framework`.
- **Stale content is deleted and rewritten fresh, never patched.** When a doc, section, deck, or
  diagram is outdated or superseded, remove it and write the current version from scratch. Appending
  updates onto stale material hides the staleness and compounds it.
- **Writing, figure, and table conventions (the report):** `docs/conventions/report-writing.md` is
  the single source of truth.
- **Doc writing.** Project docs (this file, the package READMEs, specs, scrum) are **descriptive
  records of the current state** — flowing prose, one clear job per doc, and they **reference other
  docs rather than duplicate them**. No AI-thought narration, no dumped content, no defensive asides.
- **Versioning.** A doc holds **no change-log or version history** — no "v4 → v5", no "previously X,
  now Y", no before→after narration. The doc *is* the current state; git holds the history. Change a
  doc by editing in place or deleting and rewriting it, never by appending onto stale material.
- **Engineering conventions.** Dependencies point one way (`api → services → repositories` in the
  backend; `api → hooks → components` in the frontend). The store sits behind a Protocol seam
  (dependency inversion). DRY · YAGNI · single responsibility · small focused files · typed contracts
  end-to-end. Extensibility is open/closed via **registries** — add a chart = add a module and
  register it, edit nothing. Tests guard the contracts. Changes are surgical and match the
  surrounding style; no unrelated refactors. Per-package detail lives in each package's `README.md`;
  the system design is `docs/specs/2026-06-04-phase2-s1-rearchitecture-design.md`.

## 3 · Way of working

**Scrum** in `docs/scrum/` — the backlog, the Definition of Done (four delivery tracks: code/tools ·
documents · report · deck), and the weekly sprint files — is the **plan of record**. The weekly deck
reports to the supervisor; the decks distill into the final defense deck.

**Graded** out of 100 by a reviewer (`docs/project/Rubric1.md`) and a council member
(`docs/project/Rubric2.md`); **delivered results (50) + product evaluation (10) dominate**, then
presentation, then report + references. Every backlog item ties to a criterion.

## 4 · Data: hard constraints vs current-sample observations

**Hard constraints — true of the data always; these bound what the product can claim:**

- **No alighting data** — AFC records boardings only; live occupancy and origin→destination journeys
  are not computable.
- **Boardings are cumulative** — there is no "people on bus at time T".
- **The data is dynamic / continuously-growing** — every count is relative, recomputed each run
  (`Gold boardings == Bronze ticket count`, never a hard-coded number); the ~17.9 M sample is not a total.
- Cross-source route join is **`route_no`** — the AFC and GPS systems assign `route_id` in separate spaces.
- GPS `hmm_state` (Travel/Dwell/Outage) is the data provider's segmentation — consumed, not trained.

**Current-sample observations — do NOT generalize to production.** The pipeline's validation gate
(row-count regression · null-rate · referential · PK uniqueness) checks every incoming batch and
assumes production data is clean; it does not assume this sample's defects persist. In the current
sample: the GPS window (2025) and AFC window (2026) do not overlap, so cross-source analysis is done
at the aggregate **route × hour × day-type** grain; `user_id` is ~0.1% populated; the GPS and AFC
driver sets are disjoint; GPS `speed` is ~50% null; `gps.schedules` is ~39% duplicated; ~91k schedule
rows are `service_type='unknown'`; and the local GPS extract lacks five fields the full set has
(including the per-vehicle school-bus `working` flag). Measured numbers: report Ch4 + `notebooks/`.

## 5 · Where everything lives

**`docs/`**

- **`scrum/`** — backlog, Definition of Done, weekly sprints. The plan of record.
- **`conventions/`** — `report-writing.md` (every writing/figure/table rule, the SoT) ·
  `diagrams.md` (draw.io house style + the render step).
- **`specs/`** — `chart-catalogue.md` (the 20-chart catalogue + interaction model; **stale** —
  flagship/change-log/historical framing) · `2026-06-04-phase2-s1-rearchitecture-design.md` (the
  system design: backend/frontend layering, the dbt+Dagster+BigQuery data engine, monitoring,
  extension points) · `bigquery-deployment.md` (the GCP env contract). **Epic E2 rewrites the chart
  catalogue fresh as two clean files: the catalogue (the 20 charts) + a per-chart rationale (the
  justified choice for every chart, by impact × effort).**
- **`project/`** — the assignment brief (`.docx`) and the two grading rubrics (`Rubric1.md` reviewer,
  `Rubric2.md` council).
- **`reference/`** — summaries of the cited papers (Knaflic, Bangkok QoS, Marey, MCV, and the rest).
- **`plans/`** — point-in-time implementation plans; `…-s1-p1a-dbt-dagster-warehouse.md` is the live
  warehouse build plan.
- **`diagrams/`** — draw.io sources (`report/`, `deck/`); renders go to `report/images/diagrams/`
  and `deck/assets/`. *(A few sources still show the Phase-1 stack — refresh when redrawn.)*
- **`design/`** — `app-layouts.html`, a dated UI mockup.

**Other**

- **`report/`** — the LaTeX report (Ch1–5 foundation + Ch6–9 Phase-2 scaffold), compiles to ~124 pp.
  *Ch1–5 carry pre-decision framing; each chapter is rewritten fresh to §2's rules as the report
  track reaches it, not patched in place.*
- **`deck/`** — `capstone_defence.pptx` is the Phase-1 deck. *The Phase-2 deck is built fresh, not
  edited from this one.*
- **`notebooks/`** — the EDA + profiling that produced the data facts.
- **memories** (`feedback_*`) — the §2 rules, recalled per session.

## 6 · Repo layout

Each package carries its own **`README.md`** — purpose, stack, directory, design principles, and
how to build/run/test it.

```
pipeline/  dbt + Dagster warehouse — scaffold (CLI + duckdb/polars/pyarrow); build pending GCP. (README)
backend/   FastAPI data API (built). src/busanalytics_api/{api,services,repositories,schemas,domain,core,db.py,config.py}. (README)
frontend/  React + Vite + TS SPA (foundation). src/{api,hooks,charts,components,lib,types}. (README)
demo/      Phase-1 prototype (FastAPI+Jinja+HTMX+Plotly+DuckDB); current source of db/bus.duckdb.
src/       duckdb_loader.py — Bronze loader for the 24 raw views.
db/ data/  warehouse + raw inputs (gitignored).
report/ deck/ docs/ notebooks/   + docker-compose.yml (backend :8000 + frontend :5173).
```
