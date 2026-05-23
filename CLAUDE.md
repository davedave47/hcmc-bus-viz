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

**Step:** Phase 1 **running prototype DELIVERED** + report rebuilt to match (177 pages, [report/main.pdf](report/main.pdf)).
**Last locked:** Demo built from scratch under [demo/](demo/) (FastAPI + Jinja2 + HTMX + Plotly + DuckDB); full Medallion warehouse (Bronze→Silver→Gold) materialised in `db/bus.duckdb`; 11 wired chart canvases across Cards 2/3/5 + the Tết Story; report Ch3/4/5/6/7 + abstract rewritten from the Streamlit/4-layer framing to the FastAPI/Medallion framing, every architecture comparison backed by a measured benchmark.
**Current:** Demo serves hub + Card 2 (School-Aware Demand, 5 wired + 2 Phase-2 stubs) + Card 3 (Spatial, 3 wired + 2 stubs) + Card 5 (Network Health, 3 wired) + Story "Nine days without a network". Backend = Medallion: 24 Bronze views → 12 Silver dims + 3 fact views → 7 Gold aggregate tables. Bronze→Gold lossless (17,883,623 boardings exact). `/api/charts/{theme}/{slug}` + `/api/aggregates` + `/api/healthz` JSON surface. **Run:** `python -m demo.warehouse.build` then `uvicorn demo.main:app`. See [demo/README.md](demo/README.md).
**Next:** wire Card 1 (Demand & Crowding), Card 4 (Financial), Card 6 (Routes); implement A1 linked-brushing + A3 entity panel (slots present, behaviour deferred); re-render the 2 Mermaid architecture diagrams (`mmdc` needs a working Chrome).
**Tech stack (BUILT, replaces earlier Streamlit plan):** FastAPI + Jinja2 + HTMX (app shell + interactivity) + Plotly incl. MapLibre map traces (charts/maps) + Scrollama (story) + DuckDB (warehouse, in-process, read-only at serve time). Streamlit/pydeck dropped — the bespoke Atlas design needed full HTML control. Stack-switch rationale + measured architecture benchmarks live in report Ch3.6 + Ch4.5.

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

### 1.1 · Big Idea (one sentence — Knaflic Ch 1, added 2026-05-17)

> *HCMC's bus network generates **17.8 M boarding events + 50 days of GPS** that no
> current tool turns into operational insight — this platform makes the network's
> **performance, equity, and shocks** visible to planners, operators, and passengers
> through 22 coordinated charts and a school-aware demand flagship.*

### 1.2 · 3-minute story (Knaflic Ch 1, added 2026-05-17)

> HCMC has the data: 90 days of AFC fare events + 50 days of GPS pings across 184 routes.
> Existing apps (BusMap, GoBus!, MultiGo, MultiPass) cover real-time routing and
> e-ticketing; bus.dev.tris.vn is a single research demo. **None turn the historical
> record into operational insight.** Our platform fills the gap: a Streamlit + DuckDB
> tool with 22 charts answering 14 questions across 3 personas. The **flagship** is
> school-aware demand — leveraging the 34 % student-fare share that's unique to HCMC's
> ticketing data. **The Tết shock** (67 % daily-ridership drop, 9 days, full recovery
> Feb 12) is the case-study that proves retrospective analytics matter. Phase 2
> finishes the warehouse build, ingests the full 50-day Kaggle GPS (unlocking the
> `working` school-bus flag + city-wide speed grid via bus-as-traffic-sensor), and
> ships the Stories scrollytelling layer. Bus-as-sensor and weather-correlation
> analytics extend in Phase 2.5+.

---

## 2 · Users (3 personas, internal design only — not visible in UI)

> **Trimmed from 4 → 3 personas on 2026-05-17** after decision-orientation test: drivers
> don't make analytical decisions; they're data sources, not tool users.

| Role | Decision the tool helps them make |
|---|---|
| 👤 **passenger** | Which route to commit to (reliability) · when to ride (crowding) · whether their school is served (student variant) |
| 🏢 **company** | Where to add/cut capacity · which routes are profitable (₫/trip, ghost-run %) · how they rank vs peers · did the promo work |
| 🏛 **admin (MCPT)** | Where supply ≠ demand · which routes/operators need scrutiny (QoS) · network shock & recovery · coverage/equity gaps · bus↔metro integration |

Driver is **data, not user** — driver license + shift records flow into the warehouse
and surface inside company/admin views; no driver-facing screen.

Personas drive **internal feature prioritisation** only. The shipped UI shows no role
badges, no role switcher. Date range is global; charts are role-agnostic.

### 2.1 · 14 stakeholder questions (locked 2026-05-17)

Every chart in §7 traces to one of these 14 questions. Source of truth for the
requirements records (6-field: input · computation · output shape · MoSCoW · decision
type · success criterion) lives in [§12 brainstorm log], summarised here:

| # | Question (short form) | Persona · tier |
|---|---|---|
| P-Q1 | Is route X reliable enough to commit to? | passenger · Must |
| P-Q2 | When is route X / stop Y least crowded? | passenger · Must |
| P-Q3 | Does this route serve my school's commute window? | passenger 🌟 flagship · Must |
| C-Q1 | Which of my routes are over/under-supplied vs demand? | company · Must |
| C-Q2 | Route-level revenue picture (₫/trip, ghost-run %)? | company · Must |
| C-Q3 | How do I rank vs other operators on same corridors? | company · Must |
| C-Q4 | Did my last promotion lift ridership (DiD)? | company · Should |
| A-Q1 | Where does supply ≠ demand across the network? | admin · Must |
| A-Q2 | Which routes/operators have reliability problems (QoS-1/2/3)? | admin · Must |
| A-Q3 | How does the network absorb / recover from shocks (Tết, Apr 30)? | admin · Must |
| A-Q4 | Where are coverage / equity gaps (schools, districts)? | admin · Must |
| A-Q5 | How well does bus integrate with Metro Line 1 (transfer timing)? | admin · Must |
| A-Q6 | What's the market structure (operator concentration, HHI)? | admin + company · Should |
| A-Q7 | What will demand look like for the next 14 days (forecast)? | admin + company · Should |

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
8. **GPS `speed` is ~50 % null.** 358,156 of 720,088 pings on 2025-03-18 have no speed
   reading. Any operating-regime feature (stopped vs moving, dwell detection, speed grid)
   must declare a null strategy (drop / impute / time-interpolate from adjacent pings).
9. **GPS and AFC drivers are disjoint populations.** `driver_license_number` overlap
   between `gps.drivers` (1,763 unique) and `afc.drivers` (660 unique) is **42 keys —
   2.4 % / 6.4 %**. No driver-level cross-source join is feasible.
10. **`gps.schedules` has ~39 % full-row duplicates** (109,620 of 283,134 rows). Verified
    2026-05-17: `direction` column (0/1) already exists; duplicates are **literal full-row
    duplicates across all 13 columns**, not inbound/outbound or path variants. 38,713 rows
    have `route_id = NULL`. Safe to `df.unique()` at ingest; root cause likely source-side
    snapshot UNION.
11. **Cross-source route join is `route_no` ONLY.** Column name `route_id` appears in 7
    tables but splits into two disjoint keyspaces (GPS family vs AFC family).
    `vehicle_route_mapping.route_id` ↔ `afc.routes.route_id` overlap is **25.8 % / 6.1 %**.
    Always join cross-source on `route_no` per §9 decision 5 — never on `route_id`.

12. **Local GPS sample lacks 5 fields the full Kaggle dataset has.** Per
    [HCMC dataset paper](docs/HCMC_BUS_GPS_DATASET_ver_1.md) Table 3, the full GPS feed
    has `heading · ignition · aircon · sos · working`. Local `raw_gps/2025-03-18.csv`
    has none. The **`working` flag is a per-vehicle school-bus marker** —
    cross-validates fare-level student inference for the flagship card. Pull full Kaggle
    GPS before any school-bus vehicle-identity analytics.

> Invariants 8–12 added 2026-05-17 from programmatic EDA + HCMC dataset paper read.

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
| 🟦 **SHOULD** | Reliability · Discovery (clustering) · Demand prediction · **Bus-as-traffic-sensor city-wide speed grid** *(Derevitskiy method, promoted from WON'T on 2026-05-17 — gated on full 50-day Kaggle GPS pull; chart #23 in v3 catalogue)* |
| 🟨 **COULD** | Adoption & Promo (cash-vs-digital, promotion lift) · Speed-vs-posted-limit map *(gated on OSM road-speed ingest; chart #24 in v3 catalogue)* |
| 🟥 **WON'T (yet)** | Arrival-time bands · Driver fingerprint *(GPS↔AFC drivers disjoint per invariant #9 — dead in both directions)* · User-level loyalty *(data killed it — invariant #3)* · Text-to-SQL *(external team)* · Rain-factor / traffic-jam / electric-bus analytics *(teacher's checklist Section 5/7; need external data — backlog in §10)* |

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
- **A1 · Click-to-entity-panel (revised 2026-05-22).** Every clickable entity (route, cell,
  stop, school, company, hex cell, vehicle) opens the A3 Universal Entity Detail Panel for
  that entity — that is the *single* coordination mechanism between a chart and the rest
  of the analytical surface. The earlier framing ("clicking highlights the selection in
  all sibling charts simultaneously") is retired because the UI shell renders one chart
  per canvas at any time, making MCV-as-simultaneous-brushing structurally invisible.
  Grounded in Yi 2007's seven interaction categories: Connect collapses to the panel-handoff;
  the other six categories (Select · Explore · Reconfigure · Encode · Abstract/Elaborate ·
  Filter) remain first-class within each chart. Cross-chart state within a theme persists
  via the theme-wide filter bar and the panel's "open in Route Detail" deep-links; nothing
  is simultaneous, everything is sequential and explicit. See
  [docs/superpowers/specs/2026-05-21-bus-analytics-chart-catalogue-v5-design.md](docs/superpowers/specs/2026-05-21-bus-analytics-chart-catalogue-v5-design.md)
  §2.1 + §5.
- **A2 · Action title + supporting subtitle (sharpened 2026-05-17 post-Knaflic re-read).** Every
  chart shows an *action title* that **states the finding** ("Route 152 carries 4× the median
  in morning peak") AND a *supporting subtitle* that **gives the chart-reading context**
  ("Boardings per hour, top 30 routes, weekdays Jan–Mar 2026"). Title carries the punch;
  subtitle does the labelling. Annotations on the chart underline the same finding.
  Default colours are muted; bright colour is reserved for the element the story is pointing
  at. *(Knaflic Ch 1, 5, 7 — chart title should be the conclusion, not the variable.)*
- **A3 · Universal Entity Detail Panel.** Every clickable entity (stop, route, company,
  school, day, hour, hex cell, driver, vehicle) opens a **rich side panel** (≈ 40% of
  viewport, slides from right) — multi-chart mini-dashboard about that entity. Hover stays
  light (tooltip); click is always the full panel. Panels have tabs when needed
  (Overview / Demand / Reliability / Network / Context).
- **A4 · Bar charts have a zero baseline (added 2026-05-17).** Any chart whose visual
  encoding is bar **length** (categorical bars, ranked bars, stacked bars, ranking
  scorecards) must start the value axis at zero. Truncated baselines visually exaggerate
  small differences. Line charts may have a non-zero baseline (the encoding is relative
  position, not length) — but flag the choice if you use it. *(Knaflic Ch 2.)*
- **A5 · 3–8 second story test (added 2026-05-17).** Every chart must surface its finding
  (the action title from A2) within 3–8 seconds of looking at it. QA protocol: glance at
  chart for 5 seconds, look away, articulate the finding. If the finding doesn't come,
  the chart fails — re-design (typically: stronger action title, more aggressive
  de-emphasis of context, one focal accent colour, direct labelling instead of legend).
  *(Knaflic Ch 4 — audience decides whether to keep looking within 3–8 sec.)*
- **A6 · One primitive per theme (added 2026-05-18).** Within any single analytical theme,
  no two chart canvases use the same visual primitive from the Chart Selection Rubric
  (Ch3.3 §Rubric, rows T1–T18). If the same primitive is needed for two different data
  subsets, the second instance becomes a *filter* on the first canvas (or a *mode toggle*
  / *paired-comparison overlay*), not a separate canvas. Rationale: a theme is one
  analytical question; the reader has already chosen the primitive lens by entering the
  theme; further canvases must answer with a *different* lens. The constraint is
  theme-scoped, not catalogue-scoped — same primitive freely reused across themes
  (Liu MCV consistency); duplicated within a theme is the violation. Drove the v3 → v4
  catalogue consolidation that merged 2.1+2.5, 2.2+2.3, 3.1–3.4, 5.1+5.5 and removed
  paired heatmaps.

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

**Role-anchored internally; no role labels in UI.**
**Chart catalogue v4** (locked 2026-05-18 after A6 + 8-chart backfill) = **36 canvases + 2 conditional**.
Distribution: 7+5+5+7+3+9 across the six themes. Every canvas inside a theme uses a
different primitive from the Ch3.3 rubric (rows T1–T18) per invariant A6. The catalogue
gained 8 net new chart types (cartogram T15, voronoi T16, isochrone T17, marimekko T18,
headway box plot T5, demand-variance quadrant T6, schools-routes bipartite, student-flow
sankey T10) and collapsed several duplicate-primitive entries (paired heatmaps,
historical+forecast timelines, 4-map spatial canvas, KPI+anomaly timelines, market
treemap that lived in two cards). See §12 brainstorm log for the full catalogue lineage.

| # | Card | Description (shown under name on hub) | Internal anchor | Charts |
|---|---|---|---|---|
| 1 | 🎓 **School-Aware Demand** 🌟 | *How HCMC's universities and schools shape network demand* | passenger + admin (flagship, cross-cutting) | 7 |
| 2 | 📈 **Demand & Crowding** | *When and where people ride — peak times, quiet windows, demand forecast, route reliability variance* | **passenger** | 5 |
| 3 | 🗺 **Spatial & Connectivity** | *The network as a map: density, catchment, accessibility, cartogram, metro feeders* | passenger + admin (cross-cutting) | 5 |
| 4 | 💰 **Financial & Operations** | *Route P&L, operator scorecard, payment adoption, promotion impact, market structure, operator-route marimekko* | **company** | 7 |
| 5 | 🌐 **Network Health & Performance** | *Network pulse with anomaly overlay, service-day calendar, QoS-1/2/3 scorecard* | **admin (MCPT)** | 3 |
| 6 | 🔍 **Routes** | *Per-route deep-dive + cross-route discovery (clustering, archetypes, compare, box-plot, pairwise-delay)* | all (drill-down spine — driver-data hub, not driver-user) | 9 |
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
| 4.5 | Promotion lift (DiD) | Before/after bars + lift line + **waterfall sub-view** (#26, baseline → +promo → +rebound → final) | *"Free-fare student days lift route ridership by ~12% weekdays, ~3% weekends"* | Click promo → affected routes overlaid on 4.1 |
| 4.6 | **Market structure** (A-Q6) | Treemap (Company → Route → Trip volume) + HHI concentration callout | *"Two companies operate 60% of network volume — they don't compete on the same routes"* | Click company → filters 4.1, 4.3 *(Note: same data shape as 5.2; can render in either card depending on context)* |

Card filters: metric anchor, include-free-tickets toggle, ghost-run threshold slider, company multi-select.
**Note:** "ghost-run %" is a proxy. UI language uses *"high waste, low revenue per trip"*, never *"losing money"*.
**DiD controls:** k-NN in UMAP archetype (k=5 same-archetype routes as synthetic control set per §9 gap-3 decision).

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
| 6.5 | **Marey time–distance diagram** 🌟 (U1, Lin & Zeng) | Time (x) × distance-along-route (y), trips as polylines + **time-check-stop bands** behind + **auto-detected bunching** annotations | *"Bunching gap visible mid-morning — 3 trips arrive within 4 min after a 22-min wait"* | Detail |
| 6.6 | Stop-by-stop boardings + door dwell (U6) | Dual-axis bar (boardings) + line (door-open %) per stop along route | *"Stop 4127 sees 18% of route boardings but door-opens 6% of the time — a bottleneck"* | Detail |
| 6.7 | **Per-stop arrival-time box plot** (teacher's checklist §1, added v2 — chart #22) | Box plot per stop along route, filterable by date / dow / peak vs off-peak | *"Stop 4127 has the widest arrival-time spread on this route — 9-min IQR vs 3-min network median"* | Detail |
| 6.8 | **Pairwise stop-delay scatter** (Lin & Zeng, added v2 — chart #20) | Small-multiples per consecutive stop-pair; each shows delay-at-A vs delay-at-B with R² | *"Segments A→B and C→D compound delay (R²=0.78); B→C self-corrects (R²=0.21) — drivers recover here"* | Detail |
| 6.9 | **Compare slopegraph** (added v3 — chart #25) | Slopegraph: 2 time periods (e.g., Jan vs Mar 2026) across selected routes, one metric at a time | *"Route 152 reliability fell 9pp Jan→Mar; Route 30 improved 4pp — the rest stayed flat"* | Discovery (alternative to 6.3 parcoords) |

Card filters: route picker (always-visible; multi-select in Discovery, single in Detail), date range, direction (inbound/outbound).
**Entry:** clicking any route anywhere in the app lands here in Detail mode for that route.
**Card 6 Detail mode hosts the heaviest A3 entity-panel pattern** — Marey + box plot + pairwise delay + door dwell are tabs in one route-detail surface.

### 7.7 · 📖 Stories — second reading mode INSIDE each source card (REVISED 2026-05-17)

> **SUPERSEDED 2026-05-22 by chart catalogue v5.5 spec §13** —
> [docs/superpowers/specs/2026-05-21-bus-analytics-chart-catalogue-v5-design.md](docs/superpowers/specs/2026-05-21-bus-analytics-chart-catalogue-v5-design.md)
> §13 is the current Stories truth. Changes since this section was written:
> (1) **Sticky-graphic scrollytelling** is the locked mechanic — each Story = Bing hero →
> one or two scroll sections that each *pin one chart* (`position: sticky`) while step
> panels scroll past and fire transitions (highlight · annotation · filter · encode) →
> Bongo recap+CTA. A chart-type change happens only at a section boundary, never mid-scroll.
> Studied from the VnExpress labour-market piece via Playwright 2026-05-22 (sticky-chart +
> scrolling steps, d3/ECharts/Flourish, bespoke-per-beat charts).
> (2) **Two-tier chart sourcing** — Tier 1 = catalogue chart (v5.5 numbering) in a frozen
> story state; Tier 2 = bespoke *simple* story-only chart that never enters the 20-chart tool
> catalogue (free-fare lift slope in Story 3; resilience sparkline grid in Story 4). This
> retires the earlier "Stories add no new canvases" claim.
> (3) **Chart references renumbered to v5.5** — old scene charts (1.1 ranked bar, 1.7 Sankey,
> 1.4 parcoords, 3.3 cartogram, 3.4 voronoi, 4.6 market treemap, 4.7 marimekko, 4.3 scorecard)
> are cut/folded; the 4 stories now use 2.1/2.3, 3.1/3.2, 4.1/4.2, 5.1 + 2 Tier-2 charts.
> (4) **26 scenes** (was 29), still 4 stories (School, Spatial, Financial, Tết).
> The detail below is kept as historical record (v4 numbering).

> **Design change 2026-05-17:** Stories are **NOT a separate top-level destination.** They
> live INSIDE each source card as a second reading mode. Each card with a Story shows a
> "Read the story" affordance next to "Start exploring"; the same chart canvases scroll
> through a curated sequence. No `/stories` hub page, no separate top-nav entry, no
> standalone landing. This keeps the cards as the single unit of navigation and avoids
> the hub becoming a mini-CMS.

Each Story is a curated scroll-locked sequence of chart states (filters / highlights /
annotations) on the same chart canvases that card uses for free exploration. Inspired by
**VnExpress** data-journalism (*"Dữ liệu LinkedIn tiết lộ gì…"*) and Knaflic ch. 7
storytelling. Implemented with a scrolly-trigger framework (Scrollama or equivalent)
+ authored scene JSON, mounted as a tab/mode within the card route.

**Card-story mapping (4 of 6 cards have a Story; cards 1 and 6 do not):**

| Lives inside | Story title | Scenes | Reading time |
|---|---|---|---|
| **Card 2 School-Aware Demand** | *The school commute, in numbers* | 8 (1 Bing + 6 Bang + 1 Bongo) | ~6 min |
| **Card 3 Spatial & Connectivity** | *Where the city actually rides* | 7 (1 + 5 + 1) | ~5 min |
| **Card 4 Financial & Operations** | *Who runs Saigon's buses* | 8 (1 + 6 + 1) | ~5 min |
| **Card 5 Network Health & Performance** | *Nine days without a network* (Tết) | 6 (1 + 4 + 1) | ~4 min |

**Cards 1 (Demand & Crowding) and 6 (Routes) have no Story** in v1 — they're tool-mode only. Could add later if a clear narrative emerges.

Within each card, users can break out of Story mode at any scroll position into free exploration (same chart components, same data, just a curated vs free path). The "Read the story" affordance and "Start exploring" CTA sit next to each other in the hub-level card teaser.

**Story structure (Bing-Bang-Bongo, Knaflic Ch 7 — added 2026-05-17).** Every Story must
follow a 3-act spine:
1. **Bing** (opening scene) — *"Here's what you're about to see"*: a one-screen hero KPI
   that sets the dramatic question (e.g., "What does HCMC ride during Tết?").
2. **Bang** (middle scenes) — the chart-by-chart unfolding of the answer. This is where
   the existing scene tables above live.
3. **Bongo** (closing scene) — *"Here's what you saw"*: a recap with the call to action /
   open question (e.g., "9 days of flatline → 9 routes need contingency planning →
   here's the Anomaly Lab to start").
Repetition cements memory; the recap + call-to-action turns passive scrolling into
something the reader can act on or remember.

**Scroll-trigger state transitions (4 types, added 2026-05-18):**
1. **Highlight overlay** — one element to focal accent, rest fade to grey
2. **Annotation overlay** — label / reference line / named-event flag appears
3. **Filter change** — chart re-renders against different subset (fare class, window)
4. **Primitive change** — canvas swaps to a different chart type at a narrative pivot

**Storytelling techniques (added 2026-05-18 from VnExpress 2025 data-journalism review):**
- **Statistical-sentence scene opener** — each Bang scene leads with a finding-sentence; chart appears as proof
- **Connecting prose between scenes** — 1-2 lines carry narrative argument scene N → N+1
- **In-chart date annotation** — named events (Tết 2026, April 30 2025) flagged inline on temporal axes
- **Expert pull-quote** (Phase 2 ingestion) — < 125 chars, attributed; placeholders in design
- **Comparative framing** — close Bongo with comparison to known benchmark (Bangkok QoS, Singapore intermodal, Tokyo holiday plans)
- **Methodology footnote per story** — one-line link to Method Card (chart #21) for most algorithmic chart in the story

**Chart categories across tool/story boundary (added 2026-05-18):**
- **Category A · story-strong** — works in both modes; comes alive with narrative. Charts: 5.1 network pulse · 3.3 cartogram · 3.5 isochrone · 1.7 student sankey · 1.2 schools treemap · 4.6 market treemap
- **Category B · tool-strong** — needs reader interaction; use sparingly in stories. Charts: 6.1 UMAP · 6.3 multi-route parcoords · 6.2 UpSet · 2.5 variance quadrant
- **Category C · story-exclusive frames** — only as story scenes, NOT in tool-mode catalogue. Frames: Bing hero KPI · Bongo recap card · side-by-side juxtaposition

**Per-story scene inventory (29 scenes across 4 stories; full tables in [Ch4.6 §Stories](report/sections/Ch4_ProposedSolution/4.6_AnalyticalThemes.tex)):**

| Story | # scenes | Reading | Bing → Bang → Bongo |
|---|---:|---|---|
| **Story 1 · The school commute, in numbers** (Card 2) | 8 | ~6 min | KPI "34%" → top schools bar → schools-routes treemap → weekly heatmap (student filter) → student-flow sankey → school-routeness parcoords → school-proximity map → recap "3 schools without a stop, 7 routes without a summer" → CTA |
| **Story 2 · Where the city actually rides** (Card 3) | 7 | ~5 min | KPI "5 hex cells = 20%" → hex density layer → cartogram → voronoi catchment → isochrone from Bến Thành → bus-metro sankey → recap "city you ride ≠ city on the map" → CTA |
| **Story 3 · Who runs Saigon's buses** (Card 4) | 8 | ~5 min | KPI "₫72B, 2 ops take 60%" → market treemap → operator-route marimekko → P&L quadrant → operator scorecard → promo waterfall → payment adoption → recap "12 bleeding routes, slow digital, ₫72B" → CTA |
| **Story 4 · Nine days without a network** (Card 5, Tết) | 6 | ~4 min | KPI "−67%" → timeline+Tết highlight → timeline+recovery marker → timeline+per-route deviation → spatial canvas resilience view → recap "9 days flatline, 9 routes need contingency" → CTA |

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
| **Goals.MD** | 5-persona Q&A from earlier ideation (3 personas now per §2; driver dropped as user, user-level feature dropped). |
| **Rubric.md** | Grading rubric (10 pts each: objectives, requirements, research, solutions, plan, report, presentation; 30 pts: solution). Solution depth is the highest-weight item. |

### 8.1 · Existing products surveyed (locked 2026-05-17 — competitive analysis)

| Tool | What it actually is | Coverage vs our 14 Qs | Relationship to our tool |
|---|---|---|---|
| **BusMap / GoMo by BusMap** (HCMC, [busmap.vn](https://busmap.vn)) | Passenger routing + ETA + student-fare verification + TPBank GoMo e-payment | △ routing/ETA only — none of our 14 Qs | Not a competitor; complementary upstream |
| **Go!Bus TPHCM** (FPT, [gobus.vn](https://gobus.vn)) | Real-time passenger ETA + journey planning | △ routing/ETA only | Not a competitor |
| **MultiGo / MultiPass** (Go Labs, [multigo.golabs.vn](https://multigo.golabs.vn/en/)) | Multi-modal (bus + Metro + river + bike) + MultiPass e-ticketing | △ routing + ticketing | **Upstream data source** (MultiPass payments → afc.payments — explains 99% null promo/EMV/QR fields per invariant #11 era) |
| **bus.dev.tris.vn** (Tris research) | **Single research demo** — Gridify spatial intensity heatmap only (λ/β params, sigmoid/tanh, 200–2000 m cells) | △ **just 1 of our 24** charts (= chart #7 hex layer) | Inspiration for chart #7 spatial canvas; cite + credit |
| **VinBus** ([maps.vinbus.vn](https://maps.vinbus.vn)) | Vingroup electric-bus operator routing app — VinBus routes only | △ operator-specific routing | Future data source (electric-bus analytics in WON'T tier) |
| **Swiftly** (foreign SaaS) | Commercial transit-ops platform | ✓ company ops + reliability + scorecard (no HCMC, generic) | Generic-SaaS competitor; we differentiate via HCMC context + multi-stakeholder |
| **Remix / Via** (foreign SaaS) | Network-planning tool | ✓ network/equity/scenario (no HCMC) | Generic-SaaS competitor in admin lane |
| **TfL Open Data dashboards** (London) | Public-transit KPI + reliability | ✓ admin lane (London only) | Reference pattern; "public-transit data API" worth borrowing |
| **Citymapper Pulse** | Foreign multi-city + "city pulse" KPI hero | △ A-Q3 shock view inspiration | Borrowable pattern only |

**Differentiation moats (locked):**
1. **School-aware demand (P-Q3, A-Q4)** — unique to HCMC's HS-SV student-fare data; no global tool does this.
2. **AFC + GPS integrated** at `route × hour × day-type` — Swiftly is GPS-only, fare vendors are AFC-only.
3. **Stories scrollytelling** on a live dashboard — rare; news outlets do one-off, ops tools don't.
4. **Multi-stakeholder unified surface** — operator tools serve operators, passenger apps serve passengers; one tool across 3 personas is uncommon.
5. **HCMC-specific anomaly catalogue** (Tết, Apr-30 parade, school terms) pre-tagged in `dim_date`.

**Frame our claim carefully:** "no *accessible, multi-stakeholder, analytical* dashboard for HCMC bus exists." MCPT may have internal SCADA control-room screens we can't see; those aren't exposed to operators / passengers / researchers — which is exactly our space.

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

### 9.1 · Architecture — the "how" (LOCKED 2026-05-17, step 9 of brainstorm v2)

**7-tier architecture.** Each tier has one job + a load-bearing decision:

| # | Tier | Job | Key decision |
|---|---|---|---|
| 1 | **Data** | L1 raw → L2 dims → L3 facts → L4 aggregates (already locked §9) | Every chart reads exactly one L4 table — hard contract |
| 2 | **Query** | DuckDB → pandas/polars | One persistent connection per session via `st.cache_resource`; `@st.cache_data(ttl=3600)` on each L4 read |
| 3 | **Render** | Plotly + pydeck + `st.components.v1.html` | Library decision tree: Plotly ~85% · pydeck for spatial · HTML components for Marey / GroupSet / Stories / A3 panel |
| 4 | **App shell** | Streamlit pages + topbar + entity panel | Linked brushing (A1) via `st.session_state` + `st.rerun()` on Plotly click events; URL state via `st.query_params` |
| 5 | **Stories engine** | Scrollama + scene JSON | Bing-Bang-Bongo (§7.7) — `content/stories/{school,tet,money,network}.json` with `bing`/`bang`/`bongo` scene types |
| 6 | **Analytical methods** | Prophet · HDBSCAN · STL · QoS-1/2/3 · DiD synthetic-control · Aggregate-Based traffic estimation | Each method has a Method Card (chart #21) exposing model + inputs + MAPE/silhouette/accuracy |
| 7 | **Deploy** | Local Streamlit + 2-min screen recording | No production server (locked §9 decision 8) |

**File layout (proposed for P1):**
```
src/
  warehouse/  # L2 dims + L3 facts + L4 aggregates (SQL + Python builders)
  chart_style.py  # Knaflic defaults helper (A2/A4/A5 codified)
  charts/  # one module per chart type (heatmap, treemap, scatter, ...)
  maps/  # pydeck_base + hex_grid + transfer_heatmap
  components/  # entity_panel, topbar, linked_state, url_state
  methods/  # qos, did_synthetic_control, anomaly_stl, prophet_holiday
app/
  Hub.py
  pages/01_Demand.py..06_Routes.py + 10_Methodology.py + 20_Story.py
content/stories/*.json  # Bing-Bang-Bongo authored scenes
db/bus.duckdb  # persistent warehouse
```

**Refreshed roadmap P0–P9 (28 days, replaces earlier ~21-day estimate):**
| Phase | Goal | Charts | Days |
|---|---|---|---|
| P0 | EDA backlog fixes (gps.schedules dedup · bbox stations · payments policy) | — | 1 |
| P1 | Warehouse skeleton + `chart_style.py` + first end-to-end chart (2.4) | 1 | 3 |
| P2 | Card 2 Demand + linked brushing A1 + URL state | 5 | 3 |
| P3 | Card 3 Spatial canvas (pydeck + hex grid + stop explorer) | 5 | 3 |
| P4 | 🌟 Card 1 School flagship | 5 | 2 |
| P5 | Card 4 Financial + Card 5 Network Health | 11 | 4 |
| P6 | Card 6 Routes (Discovery + Detail w/ Marey + box plot + pairwise delay) | 9 | 4 |
| P7 | Hub editorial scroll + cross-card deep-linking + Method Cards (#21) | — | 2 |
| P8 | Stories (Scrollama + Bing-Bang-Bongo, 4 stories) | — | 3 |
| P9 | Full GPS pull + Phase 2 acceptance gates + screen recording | — | 3 |

**Critical path:** P0 → P1 → P2 → P4 (school flagship in week 2 = highest-impact demo).
**Conditional charts (#23 speed grid, #24 speed-vs-limit) sit in P9.5+** — outside the 28-day plan, gated on full GPS + OSM ingest.

---

## 10 · Backlog / open work (not yet started)

- Geocode 64 school addresses (Nominatim) → unlock 0.1, 0.2, 0.5 verified joins.
- Download full 50-day GPS from Kaggle → unlock Reliability Watch full power, Spatial Map speed grid, Anomaly Lab April-30 study.
- Build station-proximity heuristic for `student_fare → route` linking when user_id is null.
- Schedule data cleaning: classify the 91k `service_type='unknown'` rows.
- Star-schema design (warehouse, in Solution Design phase).
- Final design spec → `docs/superpowers/specs/YYYY-MM-DD-bus-analytics-design.md`.
- **Build `src/chart_style.py` (added 2026-05-17 from Knaflic Ch 2–5).** Single helper enforcing
  Knaflic defaults across every chart: no top/right spines, no gridlines (or alpha=0.15
  grey only), single accent colour per chart, dark grey title (larger) + light grey
  footnote, action-title + supporting-subtitle layout (per A2), zero baseline forced on
  bar charts (per A4), no trailing zeros on numeric labels, no diagonal axis text, direct
  data labels when ≤5 categories, forecast = dotted line + light shaded background.
  Use in P1.
- **Investigate `gps.schedules` "duplicates" hypothesis** (1 h) — verified `direction`
  column already exists (invariant #10 amended). True full-row duplicates remain; root
  cause may be source-side snapshot UNION. Decide dedup vs reach out to MCPT for source
  fix.
- **Triage 77 out-of-bbox `afc.stations`** — likely swapped lat/lng or stale rows. Drop
  vs fix.
- **Decide policy for 4 ≥ 99 % null `afc.payments` fields** (`promotion_code`,
  `promotion_description`, `verification_qr`, `emv_card_id`) — keep as sparse signal vs
  drop from `fact_payments`.
- **Source HCMC weather/rain API** (teacher's Section 5 ask) — half a day.
- **Source OSM road-speed extraction** (teacher's Section 9 ask) — 1 day.
- **Source MAUR Metro Line 1 indicative schedule** (or finalise the hard-coded fallback
  per gap-2 decision).
- **Phase 2 acceptance criteria (Knaflic-derived, added 2026-05-17):**
  - **Horizontal logic** — chart titles, read in order through the dashboard or the
    report, tell the meta-story.
  - **Vertical logic** — within any chart card / report page, title + subtitle + chart +
    annotations all reinforce a single point.
  - **Reverse storyboarding** — write down main point of each page in the report v2; the
    list must match the intended storyboard.
  - **Fresh perspective** — at least one classmate or advisor walks through the tool,
    talking aloud about what they see first, what's confusing, what they want — apply
    fixes before deeming "done."
  - **3–8 second story test** (A5 invariant) — every chart in the catalogue must pass.

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
- **Programmatic EDA (24 tables, no solution context)** — script [notebooks/05_programmatic_eda.py](notebooks/05_programmatic_eda.py) drives /programmatic-eda + /schema-mapper end-to-end. Outputs: per-table profile, 9 figures in `notebooks/figures/eda_*.png`, schema map (32 shared columns, 83 joins computed). 4 new invariants added to §3 (#8 GPS speed half-null · #9 GPS↔AFC drivers disjoint · #10 gps.schedules 39 % dup · #11 cross-source route join is `route_no` only). Other surfaced issues parked: 77 out-of-bbox `afc.stations`, 4 ≥99 % null payment fields, gps.drivers.driver_name 59 % null.
- **Stakeholder requirements LOCKED (14 questions, 6-field records)** — applied /stakeholder-requirements-gathering. Personas trimmed to 3 (passenger / company / admin — driver dropped as a *user*, kept as data). 5 requirement gaps resolved: (1c) boardings/km² for equity v1, (2b) hard-coded metro schedule, (3b) k-NN in UMAP archetype for DiD controls, (4) per-shock baseline split (Tết now / April-30 gated on full GPS), (5b) manual top-8 university geocode then Nominatim. Chart catalogue consolidated 31 → **19 charts** (10 primary canvases + 6 drill-downs + 3 discovery tools), with 2 new questions added: A-Q6 market structure treemap, A-Q7 14-day demand forecast.
- **Chart catalogue v2 LOCKED at 22 + 2 conditional** — applied papers (Chawuthai 2023 Bangkok QoS, Lin & Zeng arrival prediction, Derevitskiy 2016 bus-as-sensor, Liu 2022 MCV thesis, Nguyen & Thoai HCMC dataset, teacher checklist `Bus system analytics_students.md`) + viz-builder skill. Added: **#20 pairwise stop-delay scatter** (Lin & Zeng correlation diagnostic) · **#21 Method Cards meta-view** (algorithm transparency) · **#22 per-stop arrival-time box plot** (teacher's explicit ask). Conditional on full Kaggle GPS pull: **#23 city-wide speed grid** (Derevitskiy bus-as-sensor — promote WON'T→SHOULD) · **#24 speed-vs-posted-limit map** (gated on OSM ingest). Existing-chart refinements: chart #2 gets polar layout option (Liu §2.4.1) · #7 hex grid via Chawuthai rounding-box + bus.dev.tris.vn-style λ/β/cell-size params · #11 path-variants sub-view · #12 Marey gets time-check-stop bands + bunching auto-detect · A-Q5 gets transfer-time trend line · `dim_date` extends holiday tagging beyond Tết+April-30 to school year start, mid-autumn, Hung Kings, Workers Day, Reunification.
- **Chart catalogue v3 LOCKED at 24 + 2 conditional (Knaflic Ch 1-7 re-read 2026-05-17)** — added **#25 slopegraph** (year-over-year or period-A-vs-period-B route comparison, used as sub-view of A-Q7 forecast / A-Q2 reliability) · **#26 waterfall chart** (Tết shock decomposition: pre-baseline → -drop → +recovery → post; and C-Q4 promo lift breakdown — replaces simple before/after bars). NEW invariants: **A2 sharpened to action-title + supporting-subtitle** (title is the finding, subtitle is the labelling — was "descriptive title + story subtitle") · **A4 bar charts have zero baseline** · **A5 3-8 second story test as QA gate**. NEW §1.1 Big Idea + §1.2 3-minute story added. NEW §7.7 Stories follow Bing-Bang-Bongo (opening hero → middle scenes → recap+CTA). NEW Phase 2 acceptance criteria (§10): horizontal logic + vertical logic + reverse storyboarding + fresh perspective walkthrough. NEW backlog: `src/chart_style.py` helper enforcing Knaflic defaults across every chart.

---

### Session 2026-05-20→22 · Built running prototype + stack switch + Medallion warehouse + report rebuild

- **Stack switched Streamlit → FastAPI + Jinja2 + HTMX + Plotly (LOCKED 2026-05-20).** The bespoke Atlas design (`docs/design/app-layouts.html` — custom Funnel Display/Geist fonts, editorial hub, per-card rails, slide-in entity panel, scrollytelling) would have lived ~70 % inside `st.components.v1.html` iframes under Streamlit. Switched to server-rendered FastAPI + Jinja2, HTMX for partial swaps, Plotly (incl. MapLibre `Densitymap`/`Scattermap` traces, no token) for charts, Scrollama for the story. DuckDB stays as the in-process engine. Streamlit + pydeck dropped. Rationale in report Ch3.6.
- **Demo built from scratch under [demo/](demo/) (NOT the old `app/` — user said ignore it).** Layout: `demo/main.py` (FastAPI) · `demo/db.py` (read-only DuckDB connector) · `demo/aggregates/{schools,spatial,health}.py` · `demo/charts/{style,schools,spatial,health}.py` · `demo/routers/{hub,schools,spatial,health,story_tet,api}.py` · `demo/warehouse/{dims,facts,build,benchmark}.py` · `demo/templates/` + `demo/static/css|js`. Run: `python -m demo.warehouse.build` then `uvicorn demo.main:app`. See [demo/README.md](demo/README.md).
- **Scope shipped:** Hub (editorial scroll, 6 teasers, real KPIs) + Card 2 School-Aware Demand (5 wired: top-schools bar, schools→routes treemap, weekly fare-class heatmap, school-routeness parcoords, proximity map; +2 Phase-2 stubs bipartite/sankey) + Card 3 Spatial (3 wired: hex density MapLibre, bus→metro sankey, stop-catchment voronoi; +2 stubs cartogram/isochrone) + Card 5 Network Health (3 wired: Tết pulse, service calendar, QoS-proxy scorecard) + Story "Nine days without a network" (Scrollama, 6 Bing-Bang-Bongo scenes). Cards 1/4/6 are hub teasers only.
- **5 UX fixes after first walkthrough (LOCKED):** chart autosizes to fill canvas (was fixed-height with dead space) · action title moved to caption header, de-duplicated from Plotly title · HTMX active-rail feedback on swap · fake/non-functional filter chips removed · rail labels split intentionally (2-line). Also: page made full-bleed (dropped the mockup's 1180px framed-card look); CSS cache-bust via `?v=` query.
- **Full Medallion warehouse built + rewired (LOCKED 2026-05-21).** The earlier "L1-only, query raw views directly" approach lagged (cold chart queries 0.4–1.4 s, joining 17.88 M rows each). Built the full architecture into `db/bus.duckdb`: **Bronze** = 24 raw views; **Silver** = 12 dim tables (`dim_date` with `is_tet_2026`/`is_apr30_window` tagging, `dim_route` 1:1 on route_id, `dim_stop`, `dim_school` + `dim_school_stop` bridge, `dim_trip` dedup, `dim_fare_class`, `dim_hour`, `dim_company`, `dim_payment_channel`, `dim_vehicle`, `dim_promotion`) + 3 fact views (`fact_boardings`, `fact_gps_trips`, `fact_stop_visits`, non-materialised); **Gold** = 7 aggregate tables (`agg_network_day`, `agg_route_hour`, `agg_route_day`, `agg_stop_hour`, `agg_stop_total`, `agg_school_route`, `agg_hub_kpis`). Full build = 5.4 s. Hard-coded Tết constants removed — `aggregates/health.py` reads the window from `dim_date` via lazy `__getattr__`.
- **3 row-multiplication integrity bugs found + fixed in Silver:** (1) `ticket_trips.trip_id` has 4,051 dupes → `dim_trip` GROUP BY; (2) 3 `route_id`s carry leading-zero `route_no` variants ("03"/"3") → `dim_route` 1:1 ROW_NUMBER; (3) 19 stops sit within 500 m of 2 universities (HCMUS/SGU adjacent) → `dim_school_stop` closest-uni-wins. Bronze→Gold now arithmetically lossless: `agg_hub_kpis.boardings = 17,883,623` exact.
- **`/api` JSON surface added:** `/api/charts/{theme}/{slug}` (Plotly JSON), `/api/aggregates/{name}`, `/api/kpis`, `/api/healthz` (L2/L4 table presence check). Page routes + API share the chart builders.
- **Architecture re-framed Medallion (not "4-layer") + 5 measured benchmarks (LOCKED 2026-05-22).** `demo/warehouse/benchmark.py` produces: (1) Silver-only vs Silver+Gold = **6.1× total**, up to 2,139× per aggregate; (2) LRU-cache counterfactual = cold-LRU equals Silver cost + dies on restart; (3) build scaling **1.95× ≈ O(N)** at 2× input; (4) star-over-raw = **+17.90 % boarding-count inflation** (rejected on integrity before latency); (5) chart-endpoint p50/p99 = **median 31 ms, 9/11 pass N1 100 ms** (spatial/3.1 marginal 102 ms, spatial/3.4 voronoi 311 ms scipy-bound). Decision: present as "Medallion with materialised Gold + dimensional Silver", not "4-layer" — industry-standard taxonomy, less reviewer pushback.
- **Report rebuilt to match (177 pages, was 49→168→170→177).** Stack switch propagated to Ch3.6 (Tools: FastAPI/Jinja2/HTMX/Scrollama replace Streamlit/pydeck) + Ch3.1 (Layered: Medallion is the canonical pattern, Silver internally dimensional). Ch4.5 rewritten: candidate table + measured Table 4.6 (3 architectures) + integrity table (3 bugs) + 4 new measured subsections (LRU, scaling, chart-endpoint p50/p99, Medallion-vs-Inmon-CIF-vs-Data-Vault lineage). Ch5 = running prototype (was "mockup + L1-only"); coverage table + visual-invariant audit (A1/A3 deferred) + data-grounded findings table. Ch6.1 roadmap status note. Vocabulary swept "four-layer"→"Medallion" across abstract + Ch1.3 + Ch7.1/7.2/7.3 + AppC (35 hits). New bib: fastapi, jinja2, htmx, scrollama, inmon2008cif, linstedt2015dv.
- **Report-vs-data corrections (data now wins, applied across Ch4/5):** Tết window **Feb 14–22** (not Jan 28–Feb 12); shock **−57 % avg / −84 % trough day Feb 16** (not −67 %); recovery **Feb 23**; biggest school-route edge **Route 20 → KHXH-NV ~16K** (not illustrative "Route 152 → HCMUT 482K"); routes **128–131** (not 163); student share **36 %** (not 34 %); "5 hex cells = 20 %" softened (real top-5 stops = 7 %, needs H3 binning to validate). All chart action titles are computed from the warehouse, not hard-coded.
- **Diagrams:** `arch_tradeoff` redrawn as inline TikZ (measured numbers, no external dep). `foundations_layered.mmd` + `arch_medallion.mmd` written as Mermaid sources but `mmdc` can't launch Chrome in this env — figures use `\imageplaceholder` with the exact render command pending a working Puppeteer/Chrome. `solution_star_schema` re-captioned as the Silver-tier star.
- **Known gaps / next:** A1 within-card linked brushing + A3 entity panel (slots present, behaviour deferred to Phase 2); Cards 1/4/6 not wired; 2 Mermaid diagrams await render; voronoi (3.4) is CPU-bound at 311 ms p99 — figure-level cache candidate.

### Session 2026-05-22→23 · Chart catalogue v5.5 + interaction-model rewrite + Stories re-alignment

- **Chart catalogue v5.5 LOCKED (36 → 20 charts).** Reworked the catalogue from "what the data supports" to "what each persona needs", under brainstorming + visualization-builder skills. Two-pass prune: v4 (36) → v5 (23, redundancy cuts) → v5.5 (20, persona-breadth cuts). Spec: [docs/superpowers/specs/2026-05-21-bus-analytics-chart-catalogue-v5-design.md](docs/superpowers/specs/2026-05-21-bus-analytics-chart-catalogue-v5-design.md) (13 sections, ~970 lines). Distribution 4/4/3/4/2/3. Each chart carries a 10-field defence spec (What · Why this · Why-NOT ×3 · 3-persona use · 2 defence answers). Committed `61ea825` (spec) + `9596d76` (report propagation).
- **Interaction model: dropped MCV-simultaneous, installed click-to-entity-panel.** The one-chart-per-canvas UI shell makes simultaneous cross-chart brushing structurally invisible, so MCV is kept as *lineage* only; the Yi (2007) Connect category is realised as a single click→side-panel handoff. Grounded in Yi 2007 + Heer-Shneiderman 2012 (both added to ref.bib). Report Ch 3.4 re-scoped, Ch 4.8 rewritten, CLAUDE.md §6 invariant A1 updated. Universal click contract: one click = panel; drill is a separate affordance.
- **Persona-breadth ordering + readability tiers (LOCKED).** Charts ordered top-to-bottom within a theme by how many of {Student, Operator, Authority} they serve (3/3 front-door, specialist last). Tier A/B/C readability gate (A = front door, C = drill-in only, D banned: horizon/ridgeline/chord/in-cell-sparkline). "Multi-encoding bias": no chart whose only data channel is bar length — ranked bars upgraded to constellation bubble scatters (route, school, operator constellations).
- **Two red-flag chart reframes (data-driven):** 3.2 Bus↔Metro Sankey → "(indicative)" (Metro schedule not in dataset, hard-coded MAUR fallback); 4.4 Promotion DiD → "Free-fare student-day lift waterfall" (`promotion_code` 99% null; free-pass fare class is the proxy intervention). §12 Data Feasibility Audit per chart (✅ Phase-1-ready / ⚙️ effort / 🟨 Phase-2 prerequisite / ⚠️ conditional): 13/20 demoable now, all 20 feasible after geocoding + full GPS + schedule cleaning.
- **Routes → Route Detail (renamed).** Theme reframed as the single-route deep-dive destination (other themes use routes as comparison units); cross-theme drill-in lands here via the panel deep-link.
- **Stories re-aligned to v5.5 + sticky-graphic mechanic (LOCKED 2026-05-23).** Studied VnExpress labour-market piece via Playwright (sticky-chart + scrolling steps, d3/ECharts/Flourish, bespoke-per-beat charts) + app-layouts LAYOUT 4 dark scrolly shell. Mechanic: Bing hero → 1-2 scroll sections each *pinning one chart* while step panels scroll past firing highlight/annotation/filter/encode transitions → Bongo recap+CTA; primitive change only at section boundary. **Two-tier chart sourcing:** Tier 1 = catalogue chart in story state; Tier 2 = bespoke *simple* story-only chart (free-fare lift slope, resilience sparkline grid) — retires the old "Stories add no canvases" rule. 4 stories (School/Spatial/Financial/Tết), 26 scenes. Spec §13; report Ch 4.6 story tables + prose rewritten following the report v2 plan §1 conventions (no em dash, no "card"/"hub"/"flagship", abbreviations expanded). CLAUDE.md §7.7 marked superseded.
- **OPEN — 34 vs 36% student share:** report EDA Ch 4.2 + theme intro Ch 4.6 say **34%**; this session log (2026-05-22) + earlier correction say measured value is **36%**. Stories aligned to **34%** to keep the report internally consistent for now. Needs a decision: re-run the EDA number and update Ch 4.2 to 36%, or confirm 34% is correct.
