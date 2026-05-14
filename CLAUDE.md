# HCMC Bus Analytics — Project Log

> This file is the durable record of all locked decisions, data invariants, and the
> running brainstorm. It is auto-loaded into every Claude session.
> Keep it **append-only for new decisions** and **edit-in-place for status / current step**.
> Companion artifacts:
> - `notebooks/01–04_*.ipynb` — executed EDA with embedded charts (report material)
> - `.superpowers/brainstorm/*/content/*.html` — UI mockups pushed during this session
> - `docs/superpowers/specs/` — formal design specs (to be written at end of brainstorm)

---

## 0 · Current state

**Step:** Phase 1 report **DELIVERED** (49 pages, [report/main.pdf](report/main.pdf)).
**Last locked:** Phase 1 report final — 6 chapters + 3 appendixes; ~33 commits; built with xelatex + biber; all `\imageplaceholder` macros pending real image capture per Appendix~C.
**Current:** Awaiting user review of report PDF.
**After review:** Phase 2 implementation begins — P1 warehouse build (Layers 2–4) is the critical-path entry point per the roadmap in report Ch 5.
**Tech stack confirmed:** Streamlit (shell + state) + Plotly (charts) + pydeck (maps) + DuckDB (warehouse, in-process). Complex charts (Marey, GroupSet, Stories) via `st.components.v1.html`.

**Logging discipline:** Every locked decision from this conversation forward is appended to
**§ 12 — Running brainstorm log** at the end of this file, with a one-line summary so the
log is scannable. CLAUDE.md is the single durable record; treat conversation memory as
transient.

---

## 1 · Problem

> HCMC's bus network generates large GPS + AFC data. Planners, operators, AND passengers
> have no good way to *see* it. Existing apps (BusMap, GoBus!, MultiGo) serve passengers
> with real-time routing — they don't answer "how reliable is route 72?", "where is the
> network undersupplied?", or "what does the data say about us as riders?".
>
> This project builds an **analytical & visualization platform** over historical GPS + AFC
> data for both supply (planners, operators) and demand (passengers, businesses) sides.

---

## 2 · Users (4 roles, internal design only — not visible in UI)

| Role | Concern |
|---|---|
| 👤 **passenger** | crowding, reliability, beginner-friendly routes |
| 🚍 **driver** | own shift, route detail |
| 🏢 **company** | fleet performance, revenue, scorecard vs network |
| 🏛 **admin (MCPT)** | network performance, anomalies, equity, capacity |

Roles drive **internal feature prioritisation** only. The shipped UI shows no role badges,
no role switcher. Date range is global; charts are role-agnostic.

---

## 3 · Data invariants (NEVER VIOLATE)

1. **GPS window ≠ AFC window.** GPS = Mar 20 – May 10 2025 (locally: 1 day, 2025-03-18).
   AFC = Jan 1 – Mar 31 2026 (complete, ~17.8M rows). **No timestamp-level join.**
2. **Cross-source joins must be at `route × hour-of-day × day-type`** (the "B framing").
   GPS gives *operations*; AFC gives *demand*; we combine at the aggregate profile level.
3. **`user_id` is 0.1 % populated** in `tickets` (23,109 of 17,883,623). Individual-user
   features (loyalty, churn, journey patterns) are **out of scope** — data killed them.
4. **No alighting data.** AFC records boardings only. "Live occupancy" is not computable.
5. **Boardings are cumulative** — there is no "people on bus at time T".
6. **Plan as if A, demo as if B.** Plan = full 50-day GPS from Kaggle. Demo = 1-day local.
7. **Schedule data has 91k `service_type='unknown'`** — adherence features need cleaning.

---

## 4 · EDA headline numbers (from `notebooks/`)

| Discovery | Value | Source |
|---|---|---|
| AFC volume | 17,883,623 boardings | nb 01 |
| AFC revenue | ₫72.4B (Jan–Mar 2026) | nb 03 |
| Student-fare share | **34 %** (6.16M HS-SV tickets) | nb 03 |
| Cash dominance | 96.2 % of payments | nb 03 |
| Top schools = universities | HCMUS, HCMUT, UEH, GTVT, USSH, HCMUTE, UIT, SGU | nb 03 |
| Routes shared GPS↔AFC | 121 of 163 | nb 01 |
| Metro feeders | 19 routes (per dataset doc) | nb 04 |
| Stops | 4,710 with lat/lng + parsed routes list | nb 04 |
| GPS sample | 1 day, 131 vehicles, 720,088 pings | nb 02 |
| Tết signature | Visible dip 2026-01-28 → 2026-02-05 | nb 03 |
| 9 routes processed in extracted GPS | 29, 41, 57, 61, 84, 99, 102, 141, 151 | nb 02 |

---

## 5 · SDVF tiers (locked)

| Tier | Themes |
|---|---|
| 🌟 **FLAGSHIP** | School-aware demand (the differentiator) |
| ✅ **MUST** | Network Health · Demand · Financial · Spatial · Anomalies (Tết case) · Bus↔Metro (teacher's named feature) |
| 🟦 **SHOULD** | Reliability · Discovery (clustering) · Demand prediction |
| 🟨 **COULD** | Adoption & Promo (cash-vs-digital, promotion lift) |
| 🟥 **WON'T (yet)** | Arrival-time bands · Driver fingerprint · Bus-as-traffic-sensor map *(all unlock with full 50-day GPS)* · User-level loyalty *(data killed it)* · Text-to-SQL *(external team)* |

---

## 6 · UI architecture (locked)

**Hierarchy:** `Hub → Card (theme) → Chart (one big interactive viz)`

**Canonical data window:** AFC = Jan 1 – Mar 31, 2026 (full 90 days). GPS = Mar 20 – May 10 2025 (local demo: 1 day). Date pill always shows the AFC window. **Never show "Mar 1–31" — that was a placeholder error.**

- **Hub** — Editorial scroll layout (not a grid): each card is a full-width alternating text↔SVG section with unique accent color. Light theme.
- **Card** — Atlas-style. Left **chart sidebar** (3–6 chart options for that theme).
  Top **filter bar** (chart-specific). Main canvas = one big chart at ~70 % of viewport.
- **Chart** — fully interactive. **Click any element → popover with details + drill-down
  deep-links** ("Open Route Detail", "See same hour, weekend", etc.). One canonical chart
  type per card-sidebar item; no crammed grids.

**Canonical viz vocabulary** (teacher's slides + reference docs):
- treemap · parallel coordinates · calendar heatmap · spatial grid heatmap (`bus.dev.tris.vn`)
- ranked bars · scatter quadrant with bubbles · sankey · UMAP scatter · deck.gl map
- **Marey time–distance diagram** (Lin & Zeng) — trips on a route, time × distance-along-route
- **GroupSet / UpSet matrix** (Liu 2022) — set-intersection partitioning of routes by archetype

**Forbidden:** pie charts, donut charts, 3D anything (Knaflic ch. 2).

**Per-chart conventions (invariants):**
- **A1 · Linked brushing (MCV).** Within a card, clicking a route / cell / company in one
  chart highlights that selection in **all** other charts of the same card — no navigation
  needed. Cross-card navigation is reserved for explicit drill-down deep-links.
- **A2 · Story subtitle.** Every chart shows a *descriptive title* AND a one-sentence
  *story subtitle* that tells the viewer what to notice (Knaflic ch. 1, 4, 6). Annotations
  on the chart underline the same finding. Default colours are muted; bright colour is
  reserved for the element the story is pointing at.
- **A3 · Universal Entity Detail Panel.** Every clickable entity (stop, route, company,
  school, day, hour, hex cell, driver, vehicle) opens a **rich side panel** (≈ 40% of
  viewport, slides from right) — multi-chart mini-dashboard about that entity. Hover stays
  light (tooltip); click is always the full panel. Panels have tabs when needed
  (Overview / Demand / Reliability / Network / Context).

**App-wide features (locked, in addition to invariants):**
- **🎯 Global highlight set** — a selection (e.g., "school routes" archetype) persists across
  card navigation until cleared.
- **🔖 Bookmarkable URL state** — full app state (card + chart + filters + selection) lives
  in the URL; share / re-land workflow.
- **📥 Export anywhere** — every chart + every entity panel → PNG / PDF / CSV / link, one-click.
- **⚖️ Comparison drawer** — select 2–4 entities of the same type → side-by-side mini-charts.
- **📝 Annotations + auto-callouts** — user-pinned and auto-detected callouts (Tết, parade,
  major anomalies).
- **🏅 "Routes like this one"** — on any route, UMAP nearest neighbours with distance scores.
- **📖 Stories (scrollytelling)** — see § 7.7 below. Inspired by VnExpress data journalism
  + Knaflic ch. 7 storytelling. Sits as a *separate top-level section* on the hub alongside
  the 6 cards.

---

## 7 · The 6 cards (all LOCKED — consolidation from prior 11-card structure)

**Role-anchored internally; no role labels in UI.** 31 charts total.

| # | Card | Description (shown under name on hub) | Internal anchor | Charts |
|---|---|---|---|---|
| 1 | 🎓 **School-Aware Demand** 🌟 | *How HCMC's universities and schools shape network demand* | passenger + admin (flagship, cross-cutting) | 5 |
| 2 | 📈 **Demand & Crowding** | *When and where people ride — peak times, quiet windows, demand forecast* | **passenger** | 5 |
| 3 | 🗺 **Spatial & Connectivity** | *The network as a map: density, hubs, ghost stops, metro feeders* | passenger + admin (cross-cutting) | 5 |
| 4 | 💰 **Financial & Operations** | *Route P&L, operator scorecard, payment adoption, promotion impact* | **company** | 5 |
| 5 | 🌐 **Network Health & Performance** | *Network-wide vitals, reliability (QoS-1/2/3), anomalies, daily pulse* | **admin (MCPT)** | 5 |
| 6 | 🔍 **Routes** | *Per-route deep-dive and cross-route discovery (clustering, archetypes, compare)* | **driver** + all (drill-down spine) | 6 |
| – | 💬 **Ask the Data** | *(upcoming — external team's Text-to-SQL)* | — | — |

### 7.1 · 🎓 School-Aware Demand 🌟 (LOCKED)

| # | Sidebar label | Chart type | Story subtitle | Linked brushing (A1) |
|---|---|---|---|---|
| 1.1 | Top schools by bus dependency | Ranked horizontal bar | *"5 universities drive half of all student-fare rides"* | Click school → highlight in 1.2, 1.4 |
| 1.2 | **Schools → Routes treemap** 🌟 | Treemap (Atlas) | *"Route 152 alone moves more HCMUT students than the next 3 routes combined"* | Click route → Card 6 Routes (Detail) |
| 1.3 | Student vs non-student week | Two calendar heatmaps (hour × dow) | *"Students compress 60% of their rides into 4 hours of the weekday"* | Click cell → route breakdown popover |
| 1.4 | "School-routeness" classifier | Parallel coordinates | *"7 routes are pure 'school routes' — they would vanish in summer break"* | Click line → Card 6 Routes (Detail) |
| 1.5 | School proximity & equity | Scatter map (schools as labelled stars) | *"3 large schools sit > 800 m from any stop — an equity gap"* | Click school → zoom + highlight serving routes |

Card filters: school-type, compare-to-baseline.
Backlog: geocode 64 school addresses; station-proximity heuristic.

### 7.2 · 📈 Demand & Crowding (LOCKED)

| # | Sidebar label | Chart type | Story subtitle | Linked brushing (A1) |
|---|---|---|---|---|
| 2.1 | Hourly demand curve | Stacked area (24 h, student vs non-student) | *"Two sharp peaks — 7 AM and 5 PM — student-fare drives 60% of the morning peak"* | Click hour → column highlight in 2.2, 2.3 |
| 2.2 | **Route × Hour heatmap** 🌟 | Categorical heatmap (routes × 24 h) | *"30 routes carry 80% of crowding — they all peak at the same hour"* | Click route row → highlights in 2.4, 2.5 |
| 2.3 | Weekly rhythm | Heatmap (7 dow × 24 h) | *"Saturdays look nothing like Sundays — leisure pattern only emerges Sunday afternoon"* | Click dow → profile re-projected onto 2.1, 2.2 |
| 2.4 | Top routes by demand | Ranked horizontal bar (top 20) | *"Route 152 alone is 4× the network median"* | Click route → highlights in 2.2, 2.3, 2.5 |
| 2.5 | Demand forecast | Multi-line forecast + 80/95% bands | *"Next 14 days: 3 routes projected to exceed historical peak by Friday"* | Click point → model-details popover |

Card filters: metric (boardings / # trips), day-type, segment (all / student-only / non-student), compare vs prior period, route multi-select.
"Quietest window" is a toggle on 2.2.

### 7.3 · 🗺 Spatial & Connectivity (LOCKED)

| # | Sidebar label | Chart type | Story subtitle | Linked brushing / drill |
|---|---|---|---|---|
| 3.1 | Network overview | pydeck base map: route polylines + stop dots | *"184 routes, 4,710 stops — one corridor on Hwy 1A carries 23"* | Click route → Card 6 (Detail); click stop → 3.3 |
| 3.2 | **Boarding density grid** 🌟 | deck.gl HexagonLayer (Gridify), 200 m / 500 m / 1 km cells | *"5 hex cells in District 1 capture 20% of city boardings"* | Click hex → top routes & stops popover |
| 3.3 | **Stop Demand Explorer** 🌟 | Stops on map, **red → yellow → green** by demand; hover = quick stats; click = hourly demand decomposed by route + per-route peak-hour table | *"Bến Thành takes 4× more boardings at 7 AM than its 3 PM low — every stop has its own rhythm"* | Click stop → highlights serving routes on 3.1; click route inside popover → Card 6 (Detail) |
| 3.4 | Effective vs ghost stops (U6) | Stop map coloured by door-open ratio (from GPS) | *"~12% of stops are 'ghost stops' — buses pass but doors open < 20% of the time"* | Click stop → dwell-distribution popover |
| 3.5 | **Bus ↔ Metro connectivity** (teacher's named feature) | Map of 19 feeder routes + Metro Line 1 + transfer stops; toggle to time-matching matrix | *"19 feeder routes connect to Metro 1 — only 8 get a bus within 5 min of metro arrival"* | Click transfer stop → Sankey of bus↔metro flow timing |

Card filters: hour-of-day chips, day-type, company multi-select, layer-specific (cell size, radius, etc.).

### 7.4 · 💰 Financial & Operations (LOCKED — Finance standalone, Adoption & Promo folded in)

| # | Sidebar label | Chart type | Story subtitle | Linked brushing (A1) |
|---|---|---|---|---|
| 4.1 | **P&L Quadrant** 🌟 | Scatter quadrant (X = ghost-run %, Y = ₫/trip, size = # trips, colour = company) | *"12 routes sit in the 'bleeding' quadrant — high waste, low ₫/trip"* | Click bubble → highlight in 4.2, 4.3 |
| 4.2 | Financial signatures | Parallel coordinates | *"Two companies stand out — their routes trace a distinct shape across all financial dimensions"* | Click line → highlight in 4.1, 4.3; brush axis → re-filter 4.1 |
| 4.3 | Operator P&L scorecard | Ranked table (volume + revenue toggle) | *"One company captures 31% of network revenue with 18% of routes operated"* | Click company → filters 4.1, 4.2 |
| 4.4 | Payment adoption curve | Stacked-area + small-multiples per channel | *"Cash is 96% — digital channels grew 0.4 pp/month over the 3-month window"* | Click channel → company-breakdown popover |
| 4.5 | Promotion lift | Before/after bars + lift line per promo type | *"Free-fare student days lift route ridership by ~12% weekdays, ~3% weekends"* | Click promo → affected routes overlaid on 4.1 |

Card filters: metric anchor, include-free-tickets toggle, ghost-run threshold slider, company multi-select.
**Note:** "ghost-run %" is a proxy. UI language uses *"high waste, low revenue per trip"*, never *"losing money"*.

### 7.5 · 🌐 Network Health & Performance (LOCKED — Pulse + Anomaly + Reliability merged)

| # | Sidebar label | Chart type | Story subtitle | Linked brushing (A1) |
|---|---|---|---|---|
| 5.1 | Network at a glance | KPI strip + daily-volume timeline | *"Tết drops daily ridership by 67% for 9 days — recovery completes by Feb 12"* | Click day → 5.5 drilldown |
| 5.2 | **Volume composition treemap** 🌟 | Treemap (Company → Route → Trip) | *"Two companies operate 60% of network volume — they don't compete on the same routes"* | Click company → filters 5.3, 5.4 |
| 5.3 | Service-day calendar | Calendar heatmap (3 mo × 7 dow) | *"Sundays are the quietest day-of-week — except afternoons, when leisure rides spike"* | Click day → 5.5 |
| 5.4 | **Reliability scorecard (QoS-1/2/3)** (U2) | Multi-metric ranked bars + small-multiples per route | *"QoS-3 (on-schedule) is the weakest — 14 routes below 60% on-time"* | Click route → Card 6 (Detail) |
| 5.5 | **Anomaly Lab + threshold T slider** (U3) | Date timeline with anomaly bands + drilldown popover | *"April 30 parade week disrupts 31 routes; recovery by May 4 — at threshold T = +5 min"* | Click anomaly → affected-routes list + Card 6 (Detail) |

Card filters: metric, day-type, company, QoS metric selector (in 5.4), threshold slider T (in 5.5).

### 7.6 · 🔍 Routes (LOCKED — Discovery + Detail with mode toggle)

**Mode toggle at top of card:** Discovery (cross-route) ↔ Detail (single route).

| # | Sidebar label | Chart type | Story subtitle | Mode |
|---|---|---|---|---|
| 6.1 | **Route constellation** 🌟 | UMAP scatter, coloured by archetype | *"184 routes cluster into 4 archetypes: commuter / all-day / school / weekend-leisure"* | Discovery |
| 6.2 | **Archetype intersection matrix** (U5) | UpSet / GroupSet matrix | *"7 routes are 'school + commuter' — they need both peaks AND summer-break planning"* | Discovery |
| 6.3 | **Multi-route compare** (U4) | Parallel coordinates + small-multiples per metric | *"Pick 2–4 routes — see how their demand, reliability, and ₫/trip stack up side-by-side"* | Discovery |
| 6.4 | Route summary page | KPI strip + stops list + schedule + sparklines | *"Route 152: 1.2M boardings, ₫48M revenue, 65% student share, on-time 71%"* | Detail |
| 6.5 | **Marey time–distance diagram** 🌟 (U1) | Time (x) × distance-along-route (y), trips as polylines | *"Bunching gap visible mid-morning — 3 trips arrive within 4 min after a 22-min wait"* | Detail |
| 6.6 | Stop-by-stop boardings + door dwell (U6) | Dual-axis bar (boardings) + line (door-open %) per stop along route | *"Stop 4127 sees 18% of route boardings but door-opens 6% of the time — a bottleneck"* | Detail |

Card filters: route picker (always-visible; multi-select in Discovery, single in Detail), date range, direction (inbound/outbound).
**Entry:** clicking any route anywhere in the app lands here in Detail mode for that route.

### 7.7 · 📖 Stories — scrollytelling layer (LOCKED, separate from cards)

Stories live in their own hub section. Each Story is a curated scroll-locked sequence of
chart states (filters / highlights / annotations) on the same chart canvases the cards use.
Inspired by **VnExpress** data-journalism (*"Dữ liệu LinkedIn tiết lộ gì…"*) and Knaflic
ch. 7 storytelling. Implemented with a scrolly-trigger framework (Scrollama or equivalent)
+ authored scene JSON.

| Story | Source card | Scenes |
|---|---|---|
| 🎓 **The School Story** (flagship) | Card 1 | (1) "34% of HCMC bus rides are students" KPI hero · (2) "5 schools generate half" top-schools bar · (3) "Each school anchors a route family" treemap · (4) weekday heatmap · (5) "7 routes are school-only — what happens in June?" parcoords · (6) "3 schools sit > 800m from any stop — the equity gap" proximity map |
| 🧧 **The Tết Story** | Card 5 | (1) "Daily ridership flatline for 9 days" timeline · (2) "Recovery completes Feb 12" zoom · (3) "Some routes drop 90%, others only 30%" top deviations · (4) "Holiday-resilient routes share airport corridors" subset map highlight |
| 💰 **The Money Story** | Card 4 | (1) "₫72B in 90 days" KPI hero · (2) "Two companies dominate" treemap · (3) "₫/trip varies 4×" P&L quadrant · (4) "12 routes bleeding" filtered view · (5) "Free fares lift ridership +12%" promo bar · (6) "Cash is 96% — digital just starting" adoption curve |
| 🗺 **The Network Map** | Card 3 | (1) "184 routes on one map" overview · (2) "5 hex cells = 20% of boardings" density grid · (3) "Bến Thành is 4× peak vs trough" stop demand · (4) "12% of stops are ghost stops" door dwell · (5) "19 metro feeders — only 8 arrive in time" connectivity |

Stories are read-only narratives; users can break out into Cards at any scroll position
(every chart state is a deep-link). Same chart components, same data — just a curated path
through them.

---

## 8 · Reference docs — techniques to borrow

| Doc | Contribution |
|---|---|
| **Knaflic — Storytelling with Data** | 6 lessons: context → visual → de-clutter → focus attention → design thinking → story. Forbidden: pie, donut, 3D. Use color sparingly to direct attention. Subtitles tell the story. |
| **Liu 2022 (PhD)** | Multiple Coordinated Visualization (MCV); `Gridify` (decoupling data & visual grid abstractions — used by `bus.dev.tris.vn`); `GroupSet` (set-based temporal exploration via UpSet matrix); `FuzzyCut` (interactive categorisation). Faceted small multiples for compare-by-route. |
| **Chawuthai 2023 (Bangkok GPS QoS)** | QoS-1 (complete trips), QoS-2 (on-path driving), QoS-3 (on-schedule). GPS coordinate rounding for trajectory matching. Pattern: input → preprocess → score → output. Maps to our **Reliability Watch** card. |
| **Derevitskiy 2016 (bus-as-traffic-sensor)** | Aggregate-Based Method to estimate road-graph edge speeds from bus GPS. Step-by-step propagation to unsensed edges. Macroscopic travel-time models incorporating traffic lights + peak hours. MAPE ~20 % at ≤ 15 km. Documents the *full* version of our (currently WON'T-tier) traffic-sensor map. |
| **Lin & Zeng (real-time arrival prediction)** | Link-node route representation. Project GPS pings onto a 1-D bus path. Construct time-distance trajectories. Dwell at time-check stops is the dominant predictor. Documents the *full* version of our (currently WON'T-tier) arrival-time-bands feature. |
| **HCMC dataset doc (Nguyen & Thoai)** | Schema, 31 routes, 50-day window, 19 metro feeders, April 30 parade as natural experiment. |
| **`Bus system analytics_students.md`** | Teacher's checklist of features per scope (1 route → many routes → realtime → AFC → environmental → electric). Source of all themed cards. |
| **Goals.MD** | 5-persona Q&A from earlier ideation (4 personas now; user-level feature dropped). |
| **Rubric.md** | Grading rubric (10 pts each: objectives, requirements, research, solutions, plan, report, presentation; 30 pts: solution). Solution depth is the highest-weight item. |

---

## 9 · Tooling & Solution Design (LOCKED)

**Warehouse — 4-layer architecture:**
- **Layer 1 — Raw views (existing):** 24 views from [src/duckdb_loader.py](src/duckdb_loader.py:1) — immutable input.
- **Layer 2 — Conformed dimensions (NEW):** `dim_date` · `dim_hour` · `dim_route` · `dim_stop` · `dim_school` · `dim_company` · `dim_fare_class` · `dim_payment_channel` · `dim_vehicle` · `dim_promotion`. Materialised as `CREATE OR REPLACE TABLE`. Pre-tags Tết + April-30 windows. Reconciles GPS↔AFC route IDs.
- **Layer 3 — Fact views (NEW):** `fact_boardings` · `fact_gps_trips` · `fact_stop_visits`.
- **Layer 4 — Aggregate tables (NEW, chart-ready):** `agg_route_hour` · `agg_route_day` · `agg_stop_hour` · `agg_school_route` · `agg_company_route` · `agg_payment_day` · `agg_network_day` · `agg_route_profile`. **Every chart in the 31-chart catalogue maps to exactly one of these.**

**Storage:** parquet partitioned daily for tickets/payments; `data/raw/` and `data/parquet/`. Persistent `db/bus.duckdb` warehouse file (NOT `:memory:`).

**DataFrames:** polars + pandas.

**Static charts (report):** matplotlib + seaborn; plotly for interactivity in notebooks.

**Interactive web app — confirmed architecture:**
- **Streamlit** as shell + session state manager + Python query engine
- **Plotly** for ~85% of charts (heatmaps, scatter, parallel coords, treemaps, stacked area, forecast)
- **pydeck / st.pydeck_chart** for all deck.gl maps
- **`st.components.v1.html()`** for: Hub landing page, Marey diagram, GroupSet/UpSet matrix, Stories scrollytelling, A3 entity panel
- Linked brushing (A1) via `st.session_state` + `st.rerun()` on Plotly selection events
- **No separate API server** — DuckDB queries run directly in Python process
- **`@st.cache_data`** for aggregated query results (TTL configurable)

**Locked open-question decisions:**
1. **DuckDB persistence:** persistent `db/bus.duckdb` file (fast cold start; rebuilt only when raw data changes).
2. **Forecast model (Chart 2.5):** statsforecast's ETS as the primary model; ship a "model card" page explaining accuracy.
3. **UMAP clustering (Chart 6.1):** runs at warehouse-build time (frozen), version-stamped.
4. **Anomaly threshold T (Chart 5.5):** pre-compute 5 levels (T = 1, 2, 5, 10, 15 min); slider snaps between them.
5. **GPS↔AFC route reconciliation:** AFC `route_no` is canonical `route_id`; GPS `route_no` stored as join field on `dim_route`. Routes flagged as GPS-only / AFC-only.
6. **School geocoding backfill:** stub with district-level approximation; replace as geocoding completes; "verified ✓" badge per school.
7. **Stories deep-link:** opens card in side panel (≈40% viewport), preserving scroll context.
8. **Streamlit deployment:** local-only for the demo + 2-min screen recording for the report.

**Notebooks:** `notebooks/01–04_*.ipynb` executed via `jupyter nbconvert --execute --inplace`.
**Test pipeline on 1-day GPS first; switch to full 50-day when Kaggle pull is done.**

---

## 10 · Backlog / open work (not yet started)

- Geocode 64 school addresses (Nominatim) → unlock 0.1, 0.2, 0.5 verified joins.
- Download full 50-day GPS from Kaggle → unlock Reliability Watch full power, Spatial Map speed grid, Anomaly Lab April-30 study.
- Build station-proximity heuristic for `student_fare → route` linking when user_id is null.
- Schedule data cleaning: classify the 91k `service_type='unknown'` rows.
- Star-schema design (warehouse, in Solution Design phase).
- Final design spec → `docs/superpowers/specs/YYYY-MM-DD-bus-analytics-design.md`.

---

## 11 · Where the brainstorm decisions live

- **CLAUDE.md** (this file) — durable, project-specific, auto-loaded every session.
- **`~/.claude/projects/-home-duyhuynh-Desktop-capstone/memory/`** — Claude's auto-memory
  (cross-project preferences: viz style, interactivity bias, AFC boarding invariant).
- **`.superpowers/brainstorm/.../content/*.html`** — UI mockups from this session (kept for review).
- **`notebooks/01–04_*.ipynb`** — empirical evidence (the foundation of SDVF).
- **`docs/superpowers/specs/`** — formal design spec (written at end of brainstorm).

---

## 12 · Running brainstorm log

> Append one bullet per locked decision. Newest at the bottom. Keep entries short — link
> to sections above for detail.

- **Problem framing** — analytics & visualisation platform over historical GPS + AFC for HCMC bus, serving supply AND demand sides. *(§1)*
- **4 personas** kept internally as design tool only; **no role UI**. *(§2)*
- **Framing B** — cross-source join only at `route × hour × day-type`. *(§3)*
- **Demo scope = local 1-day GPS + 90-day AFC**; **design scope = full 50-day GPS** (downloaded later). *(§3)*
- **🌟 FLAGSHIP = School-Aware Demand**; SDVF tiers approved. *(§5)*
- **Hub → Card → Chart** UI architecture, Atlas-style; **light theme**; **no role badges in UI**. *(§6)*
- **Card list = 11 active + 1 upcoming** ("Ask the Data" by external team). *(§7)*
- **Card 0 LOCKED** — 5 charts (top schools / treemap / week heatmap / parcoords / equity map). *(§7.0)*
- **Card 1 LOCKED** — 4 charts (KPI+timeline / treemap / scorecard / calendar). *(§7.1)*
- **CLAUDE.md established** as the durable project log; logging discipline adopted from this point forward.
- **6 doc-driven adjustments LOCKED:** A1 linked brushing · A2 story subtitles · U1 Marey · U2 QoS-1/2/3 · U3 anomaly threshold T · U4 multi-route compare · U5 GroupSet · U6 door-open dwell. *(§6 invariants + §7.3+ pre-commitments)*
- **Card 2 LOCKED** — 5 charts (hourly curve / route×hour heatmap / weekly rhythm / top routes / forecast). *(§7.2)*
- **Card 3 LOCKED** — 3 charts (P&L quadrant / parallel-coords signatures / operator P&L scorecard). Ghost-run language stays as "high waste" never "losing money" because no cost data. *(§7.3)*
- **Card 4 (old Spatial Map) brainstorm done** — added Stop Demand Explorer per user request (gradient red→yellow→green, click for hourly demand-by-route popover); folded Bus↔Metro into Spatial.
- **CONSOLIDATION to 6 cards LOCKED:** role-anchored internally (passenger / driver / company / admin), Finance kept standalone with Adoption & Promo folded in, no role labels in UI. Final cards: (1) School-Aware Demand 🌟, (2) Demand & Crowding, (3) Spatial & Connectivity, (4) Financial & Operations, (5) Network Health & Performance, (6) Routes. 31 charts total. All chart-level details locked. *(§7.1–7.6)*
- **App-wide feature bundle LOCKED (Option A):** A3 Universal Entity Detail Panel · 🎯 Global highlight set · 🔖 Bookmarkable URL state · 📥 Export anywhere · ⚖️ Comparison drawer · 📝 Annotations + auto-callouts · 🏅 "Routes like this one". (Multi-language deferred.)
- **Stories (scrollytelling) layer LOCKED:** 4 curated stories inspired by VnExpress data-journalism technique — School Story (flagship), Tết Story, Money Story, Network Map. Sits as a separate top-level hub section alongside the 6 cards. *(§7.7)*
- **Hub design v8 locked** — editorial vertical scroll with alternating text↔SVG cards; unique accent color per card (orange → gold → green → red → purple → slate); cross-card nav menu in topbar; hover glossary tooltips for technical terms. File: `docs/design/app-layouts.html`.
- **Date window bug fixed** — AFC data is Jan 1 – Mar 31, 2026 (90 days). "Mar 1–31" was a placeholder; corrected everywhere. Invariant added to §6.
- **Streamlit hybrid architecture LOCKED** — Streamlit shell + Plotly charts + pydeck maps + DuckDB in-process. `st.components.v1.html()` for Hub page, Marey, GroupSet, Stories. Linked brushing via session_state + rerun. No separate API server. *(§9)*
- **Solution Design phase started** — star schema, aggregation layer, data flow next. *(§0)*
- **Solution Design LOCKED** — 4-layer warehouse (raw → dims → facts → aggregates); 8 aggregate views map to 31 charts as a hard data contract; Streamlit + Plotly + pydeck + `st.components.v1.html` for Marey/GroupSet/Stories; persistent `db/bus.duckdb`; statsforecast ETS for forecast; UMAP at build time; pre-computed anomaly thresholds (T=1,2,5,10,15 min); AFC route_no canonical; geocoding stubbed at district level with "verified ✓" badges; Stories deep-link to side panel; local-only Streamlit deploy + screen recording. Solution design report shared inline; spec to be written at `docs/superpowers/specs/2026-05-14-bus-analytics-design.md`. *(§9)*
- **Phase 1 deliverable = report** — submitted at end of Phase 1; rubric at `docs/Rubric.md` (Câu 1–7, max 100 pts). Teacher-mandated structural changes: add Problem Statement section to Chapter 4; add Current Prototype chapter before Conclusion; split Future Work into its own chapter before Conclusion; Contributions section is short and written last (phase 1 = solutioning + prototyping only).
- **Implementation roadmap LOCKED (P1–P9)** — P1 warehouse skeleton · P2 first end-to-end card (Demand) · P3 Spatial+pydeck · P4 School flagship · P5 Financial+Network Health · P6 Routes+Marey · P7 Hub+nav+entity panel · P8 Stories · P9 polish+full GPS. Total est ~21 days, P1→P2 critical path. *(§10)*
- **Phase 1 report DELIVERED** — 49-page PDF at [report/main.pdf](report/main.pdf), built with xelatex + biber. Structure: 6 chapters (Intro · Background+Related Work · Proposed Solution · Current Prototype · Future Work · Conclusion) + 3 appendixes (Warehouse DDL · Phase 2 Plan · Image Inventory). All figures are `\imageplaceholder{type}{what}{how}` placeholders cataloged in Appendix C — student fills in real photos/screenshots before submission. Rubric coverage: Câu 1 (objectives) · Câu 2 (problem statement) · Câu 3 (related work, 4 problems + 9 refs) · Câu 4 (proposed solutions with 3 alternatives-considered subsections covering warehouse, modules, dashboard) · Câu 5 (Phase 2 roadmap + Appendix B with content/time/personnel/outcomes) · Câu 6 (TOC, section structure, no undefined refs).
- **Plan amendments applied:** Related Works folded into Background (Ch 2); Contributions moved from intro to Conclusion (Ch 6); all diagrams replaced with image placeholders + master inventory in Appendix C.
