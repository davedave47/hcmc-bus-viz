# HCMC Bus Analytics — Project Log

> Durable record of the locked decisions, data invariants, and current state of the
> project. Auto-loaded into every Claude session.
> **Edit-in-place** for status and specs (§0–§11); **append one line** to the decision
> log (§12) for each new locked decision. CLAUDE.md is the single durable record —
> treat conversation memory as transient.
>
> Companion artifacts:
>
> - `demo/` — the running FastAPI prototype (the system). See [demo/README.md](demo/README.md).
> - `report/` — the Phase 1 report (LaTeX, xelatex + biber). See §9.
> - `docs/specs/` — centralised design specs:
>   - `chart-catalogue.md` — the canonical chart catalogue v5.5 (20 charts) + interaction
>     model. **This spec is the chart truth; §5 below summarises it.**
>   - `defence-deck.md` — the defence-deck design spec.
> - `notebooks/01–05_*.{ipynb,py}` — executed EDA + programmatic profiling (evidence base).
> - `docs/conventions/` — `report-writing.md` (critical report writing convention) +
>   `diagrams.md` (draw.io convention; sources in `docs/diagrams/`, renders in the consumer).
> - `docs/diagrams/{report,deck}/` — editable diagram **sources** (draw.io); renders live in
>   `report/images/diagrams/` (report) and `deck/assets/` (deck) — kept as independent sets.
> - `deck/` — Phase-1 defence deck: `capstone_defence.pptx` (source of truth) + `.pdf`.
>   (`build_deck.py` there is a stale, non-runnable historical generator.)

---

## 0 · Current state

**Phase:** Phase 1 DELIVERED — running prototype + report both built and aligned.

**Stack (BUILT):** FastAPI + Jinja2 + HTMX (server-rendered app shell + partial swaps) ·
Plotly incl. MapLibre map traces (`Densitymap`/`Scattermap`/`Choroplethmap`, CartoDB
Positron, no token) · Scrollama (scrollytelling) · DuckDB (in-process warehouse,
read-only at serve time) · Polars + H3 + UMAP + statsforecast (AutoETS) for analytics.
**Streamlit + pydeck were dropped** — the bespoke Atlas design needed full HTML control.

**Warehouse (BUILT):** full Medallion in `db/bus.duckdb` — Bronze (24 raw views) →
Silver (12 dimension tables + 3 fact views, Kimball-dimensional) → Gold (7 materialised
aggregate tables). Bronze→Gold lossless (`agg_hub_kpis.boardings = 17,883,623` exact).
Full build ≈ 5 s; 41-check validation harness in `demo/warehouse/validate.py`.

**Demo coverage:** 9 of 20 v5.5 canvases wired, across 3 of 6 themes —
**Schools & Students (4/4)**, **Spatial & Connectivity (3/3)**, **Network Health (2/2)**
— plus the standalone Tết Story "Nine days without a network" (Scrollama, Bing-Bang-Bongo).
Ridership & Crowding, Financial & Operations, and Routes are **hub teasers only (0 wired)**.

**Run:**

```
python -m demo.warehouse.build      # (re)build db/bus.duckdb from raw inputs (~5 s)
uvicorn demo.main:app --reload --port 8000
```

To free the port, use `fuser -k 8000/tcp` (NOT `pkill -f uvicorn` — self-match risk).

**Next:** wire Ridership (4), Financial (4), Routes (3); build the flexible filter bar
(date range · route · day-type, re-querying every chart); load full 50-day Kaggle GPS;
geocode schools; fix the report inconsistencies in §9.

---

## 1 · Problem

> HCMC's bus network produces ~17.8 M AFC boarding events per quarter + ~50 days of GPS
> telemetry per release window, yet **no accessible tool turns either stream into
> operational insight** for the people the network serves. Existing apps (BusMap, GoBus!,
> MultiGo) do real-time passenger routing — they don't answer "how reliable is route 72?",
> "where is the network undersupplied?", or "what does the data say about us as riders?".
> This project builds an **analytical & visualisation platform** over the historical
> GPS + AFC record, for both the operations side (planners, operators) and the rider side
> (passengers, businesses).

**Big idea:** make the network's **performance, equity, and shocks** visible to planners,
operators, and passengers through 20 coordinated charts, with schools and students as the focus.

**Flagship differentiator:** school-aware ridership — leverages the ~36 % student-fare share
unique to HCMC's ticketing data; no global tool does this. **Proof-of-value case study:**
the Tết 2026 shock (see §4).

---

## 2 · Users (3 personas — internal design tool only, NOT shown in UI)

| Role                                          | Decision the tool helps them make                                                                                                        |
| --------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------- |
| 👤**passenger**                         | Which route to commit to (reliability) · when to ride (crowding) · is my school served (student variant)                               |
| 🏢**operating company**                 | Where to add/cut capacity · which routes are profitable (₫/trip, waste %) · rank vs peers · did the promo work                       |
| 🏛**public-transport authority (MCPT)** | Where service ≠ riding · which routes need scrutiny (QoS) · network shock & recovery · coverage/equity gaps · bus↔metro integration |

**Driver is data, not a user** — driver records flow into the warehouse and surface inside
company/authority views; no driver-facing screen. The shipped UI shows no role badges and
no role switcher; charts are role-agnostic and the date window is global. Personas drive
**internal feature prioritisation only**.

### 2.1 · 14 stakeholder questions (every chart traces to one)

| #    | Question (short)                                                  | Persona · tier               |
| ---- | ----------------------------------------------------------------- | ----------------------------- |
| P-Q1 | Is route X reliable enough to commit to?                          | passenger · Must             |
| P-Q2 | When is route X / stop Y least crowded?                           | passenger · Must             |
| P-Q3 | Does this route serve my school's commute window?                 | passenger 🌟 · Must          |
| C-Q1 | Which of my routes are over/under-served vs riding?             | company · Must               |
| C-Q2 | Route-level revenue picture (₫/trip, waste %)?                   | company · Must               |
| C-Q3 | How do I rank vs other operators on the same corridors?           | company · Must               |
| C-Q4 | Did my last promotion lift ridership (DiD)?                       | company · Should             |
| A-Q1 | Where does service ≠ riding across the network?                   | authority · Must             |
| A-Q2 | Which routes/operators have reliability problems (QoS-1/2/3)?     | authority · Must             |
| A-Q3 | How does the network absorb / recover from shocks (Tết, Apr 30)? | authority · Must             |
| A-Q4 | Where are coverage / equity gaps (schools, districts)?            | authority · Must             |
| A-Q5 | How well does bus integrate with Metro Line 1 (transfer timing)?  | authority · Must             |
| A-Q6 | What is the market structure (operator concentration, HHI)?       | authority + company · Should |
| A-Q7 | What will ridership look like over the next 14 days (forecast)?      | authority + company · Should |

Requirements layer: **R1–R15** functional, **N1–N6** non-functional (N1 = warm re-render
budget, the latency gate the architecture is benchmarked against). Full records in report
Ch 4.1.

---

## 3 · Data invariants (NEVER VIOLATE)

1. **GPS window ≠ AFC window.** GPS = Mar 20 – May 10 2025 (local sample: 1 day, 2025-03-18).
   AFC = Jan 1 – Mar 31 2026 (~17.8 M rows). **No timestamp-level join.**
2. **Cross-source joins are at `route × hour-of-day × day-type`** ("B framing"). GPS gives
   *operations*; AFC gives *ridership*; combine only at the aggregate profile level.
3. **`user_id` is 0.1 % populated** (23,109 of 17,883,623). Individual-user features
   (loyalty, churn, journeys) are **out of scope** — data killed them.
4. **No alighting data.** AFC records boardings only. "Live occupancy" is not computable.
5. **Boardings are cumulative** — there is no "people on bus at time T".
6. **Plan as if A, demo as if B.** Plan = full 50-day GPS from Kaggle. Demo = 1-day local.
7. **Schedule data has ~91k `service_type='unknown'`** — adherence features need cleaning.
8. **GPS `speed` is ~50 % null** (358,156 of 720,088 on 2025-03-18). Any operating-regime
   feature must declare a null strategy (drop / impute / interpolate).
9. **GPS and AFC drivers are disjoint.** Overlap = 42 keys (2.4 % / 6.4 %). No driver-level
   cross-source join.
10. **`gps.schedules` has ~39 % full-row duplicates** (109,620 of 283,134). `direction`
    column already exists; these are literal full-row dupes (source-side snapshot UNION).
    Safe to `.unique()` at ingest.
11. **Cross-source route join is `route_no` ONLY.** `route_id` appears in 7 tables but
    splits into two disjoint keyspaces (GPS vs AFC). Never join cross-source on `route_id`.
12. **Local GPS sample lacks 5 fields the full Kaggle dataset has** (`heading · ignition · aircon · sos · working`). The **`working` flag is a per-vehicle school-bus marker** —
    cross-validates fare-level student inference. Pull full Kaggle GPS before any
    school-bus vehicle-identity analytics.
13. **GPS `extracted.hmm_state` is the SOURCE's segmentation, not ours.** The provider
    ships an `extracted` table (subset of routes) where each ping is labelled
    **Travel / Dwell / Outage** by a Hidden Markov Model; it is the basis for trips and
    stop-visits (dwell, arrival timing). We consume it, we do not train it. (Deck GPS ERD
    simplifies the values to `Travel | At_Stop`.) Q&A: "that HMM is the provider's; I use
    its labelled output."

---

## 4 · EDA headline numbers (corrected against the warehouse — these are MEASURED)

| Discovery                  | Value                                                                                                                               | Note                                                 |
| -------------------------- | ----------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------- |
| AFC volume                 | **17,883,623** boardings                                                                                                      | Jan–Mar 2026, lossless through Gold                 |
| AFC revenue                | ~₫72 B (90 days)                                                                                                                   |                                                      |
| Student-fare share         | **~36 %**                                                                                                                     | the flagship signal (NOT 34 — see §9)              |
| Cash dominance             | **96.2 %** of payments                                                                                                        |                                                      |
| Fare-class mix             | ~43 % regular cash · ~36 % student · ~16 % free                                                                                   |                                                      |
| Routes                     | **128 AFC** / 163 GPS / 121 shared                                                                                            | (NOT 163/184 — old placeholders)                    |
| Ridership concentration       | 80 % of boardings on ~55 of 128 routes                                                                                              | heavy-tailed                                         |
| Weekday twin peaks         | ~22k/hr at ~6 AM and ~4–5 PM                                                                                                       |                                                      |
| **Tết 2026 shock**  | window**Feb 14–22**; **−57 % avg**, **−84 % trough day Feb 16** (33,176 boardings); recovers ~**Feb 23** | the proof-of-value case                              |
| Anchor universities        | 8 (HCMUS, HCMUT, UEH, GTVT, USSH/KHXH-NV, HCMUTE, UIT, SGU)                                                                         |                                                      |
| Biggest school→route edge | Route 20 → KHXH-NV, ~16k students                                                                                                  | (NOT the old illustrative "Route 152 → HCMUT 482k") |
| Stops                      | 4,710 with lat/lng                                                                                                                  |                                                      |
| GPS local sample           | 1 day, 131 vehicles, 720,088 pings                                                                                                  | full = ~32 M over 50 days                            |

> All chart action titles are **computed from the warehouse**, never hard-coded.

---

## 5 · Chart catalogue v5.5 — 20 canvases, 6 themes (LOCKED)

Canonical spec: `docs/specs/chart-catalogue.md`
(13 sections, per-chart 10-field defence specs). Distribution **4 / 4 / 3 / 4 / 2 / 3**.
Charts are ordered within a theme by **persona breadth** (3/3 front-door first, specialist
last). Readability tiers: **A** = instant front-door · **B** = rewards a second pass ·
**C** = drill-in depth only (banned: horizon, ridgeline, chord, in-cell sparkline as
primary). Front door of every theme is Tier A and serves all three personas.

| Theme                                     | #   | Chart                                                                                                                     | Primitive          | Tier | Data |
| ----------------------------------------- | --- | ------------------------------------------------------------------------------------------------------------------------- | ------------------ | ---- | ---- |
| **1 · Ridership & Crowding** (4)      | 1.2 | Route × hour heatmap (hover→sparkline)                                                                                  | Heatmap            | B    | ✅   |
|                                           | 1.3 | Route constellation (mean × variance × peak × archetype)                                                               | Bubble scatter     | A    | ⚙️ |
|                                           | 1.1 | Ridership streamgraph (fare class × 90 days)                                                                                | Streamgraph        | A    | ✅   |
|                                           | 1.4 | Bump chart — top-20 routes' rank over 12 weeks                                                                           | Bump chart         | B    | ✅   |
| **2 · Schools & Students 🌟** (4) | 2.1 | School constellation (vol × peak% × routes × equity)                                                                   | Bubble scatter     | A    | 🟨   |
|                                           | 2.2 | School→route treemap with drill                                                                                          | Treemap            | A    | 🟨   |
|                                           | 2.4 | School proximity map with walking circles                                                                                 | Annotated map      | A    | 🟨   |
|                                           | 2.3 | Weekly fare-class heatmap (student/non-student toggle)                                                                    | Calendar heatmap   | A    | ✅   |
| **3 · Spatial & Connectivity** (3) | 3.1 | Multi-layer hex map (density · per-stop · ghost · district cartogram layers)                                           | Hex bin map        | A    | ⚙️ |
|                                           | 3.2 | Bus↔Metro Sankey*(indicative — Metro schedule hard-coded)*                                                            | Sankey             | A    | ⚠️ |
|                                           | 3.4 | Accessibility isochrone from chosen origin                                                                                | Isochrone map      | A    | ⚙️ |
| **4 · Financial & Operations** (4) | 4.2 | Operator constellation (share × rev/trip × fleet × on-time)                                                            | Bubble scatter     | A    | 🟨   |
|                                           | 4.1 | P&L quadrant (waste × rev/trip × volume × company)                                                                     | Quadrant scatter   | B    | ⚙️ |
|                                           | 4.3 | Payment-channel streamgraph                                                                                               | Streamgraph        | A    | ✅   |
|                                           | 4.4 | Free-fare student-day lift waterfall + synthetic control*(reframed from Promotion DiD — `promotion_code` 99 % null)* | Waterfall          | B    | ⚙️ |
| **5 · Network Health** (2)         | 5.2 | QoS small-multiples scatter (one mini-scatter per QoS-1/2/3)                                                              | Small multiples    | A    | 🟨   |
|                                           | 5.1 | Network pulse with anomaly bands + threshold slider                                                                       | Timeline + bands   | A    | ✅   |
| **6 · Routes** (3)                 | 6.4 | Per-stop arrival box plot along route                                                                                     | Box plot           | A    | 🟨   |
|                                           | 6.3 | Stop-by-stop boardings + door-dwell dual axis                                                                             | Dual-axis bar+line | B    | 🟨   |
|                                           | 6.2 | Marey time-distance diagram + dwell heatmap                                                                               | Marey + heatmap    | C    | 🟨   |

Data tier: ✅ Phase-1 ready · ⚙️ Phase-1 with compute effort · 🟨 needs school geocoding
OR full 50-day GPS · ⚠️ conditional on external data. **13/20 demoable now.**

**Cut from v4 (36 charts):** UMAP route constellation → research appendix; service-day
calendar → cut (overlaps 5.1); district cartogram → folded into 3.1 as a layer. Two
conditional extensions live outside the 20: bus-as-traffic-sensor speed grid (Derevitskiy,
needs full GPS) and speed-vs-posted-limit map (needs OSM road-speed).

**SDVF tiers:** 🌟 flagship = Schools & Students · ✅ Must = Network Health, Ridership,
Financial, Spatial, Tết anomaly case, Bus↔Metro · 🟦 Should = Reliability, route discovery,
forecast, speed grid · 🟥 Won't-yet = arrival-time bands, driver fingerprint (invariant #9),
user-level loyalty (invariant #3), text-to-SQL (external team), rain/electric-bus analytics.

---

## 6 · UI & interaction model (LOCKED)

**Hierarchy:** `Hub → Theme (card) → Chart`. Light theme. Full-bleed (no framed-card look).

- **Hub** — editorial vertical scroll; 6 full-width teasers with real warehouse KPIs;
  each teaser offers "Start exploring" + (where a Story exists) "Read the story".
- **Theme card** — Atlas-style: left chart rail (the theme's 2–4 charts), top View Controls
  bar (date range + theme-specific filter), main canvas = one chart at ~70 % of viewport.
  Charts autosize to fill the canvas.
- **Chart** — interactive; action title in the caption header (de-duplicated from Plotly's
  own title); click any entity → entity-detail panel (see below).

**Interaction model — click-to-entity-detail panel (revised, MCV-simultaneous retired).**
The shell renders **one chart per canvas**, so simultaneous cross-chart brushing would be
structurally invisible. MCV is kept as intellectual *lineage* only. The single coordination
mechanism is: **one click on any entity → A3 universal entity-detail panel** for that
entity (≈40 % viewport, slides from right, ≤4 mini-views, tabs when needed). This is the
Yi (2007) *Connect* category realised as a panel handoff. The other six Yi categories
(Select · Explore · Reconfigure · Encode · Abstract/Elaborate · Filter) stay first-class
within each chart via the View Controls bar. Cross-theme state travels via the theme-wide
filter bar + the panel's "open in Route Detail" deep-link. **Universal click contract:**
one click = panel; drill/zoom/expand are separate affordances; one click never has two
meanings. Grounded in Yi 2007, Heer & Shneiderman 2012, Shneiderman 1996.
*(Status: BUILT — clicking an entity slides in the A3 detail panel with its fields, a
ranked sub-list, and export/share. The **flexible filter bar is now BUILT** on the school
weekly heatmap (chart 2.3): four live fields — **date range · route · day-type · fare class**
— each re-querying the warehouse. The date filter sidesteps the date-grain-Gold gap by
querying `fact_boardings` directly (date/hour/route_no/fare_class columns), deriving dow via
`dayofweek(day)`; the dow-aggregated Gold tables are bypassed for this chart. Remaining Phase
2 item: roll the same filter bar out to the other charts.)*

**Chart invariants (durable — referenced across report + spec):**

- **A2 · Action title + supporting subtitle.** Title states the finding ("Route 152 carries
  4× the median in morning peak"); subtitle gives the reading context ("Boardings/hour,
  top 30 routes, weekdays"). Muted defaults; one focal accent colour on the element the
  story points at.
- **A4 · Bar charts have a zero baseline.** Any bar-length encoding starts the value axis
  at zero. (Line charts may use a non-zero baseline — flag it.)
- **A5 · 3–8 second story test.** Every chart must surface its finding within 3–8 s. QA:
  glance 5 s, look away, articulate the finding; if it doesn't come, redesign.
- **A6 · One primitive per theme.** No two canvases in a theme use the same rubric
  primitive; a repeat becomes a filter/toggle on the first. Theme-scoped, not
  catalogue-scoped (same primitive reused freely across themes).
- **Multi-encoding bias.** No chart whose only data channel is bar length — ranked bars
  were upgraded to constellation bubble scatters (route/school/operator constellations).

**Forbidden:** pie, donut, 3D, word cloud, dendrogram-as-primary, radar/radial.

**Stories (scrollytelling) — sticky-graphic mechanic (LOCKED).** Each Story = Bing hero →
1–2 scroll sections that each **pin one chart** (`position: sticky`) while step panels
scroll past firing transitions (highlight · annotation · filter · encode) → Bongo recap +
CTA. A primitive change happens only at a section boundary, never mid-scroll. Modelled on
the VnExpress 2025 labour-market data piece. **Two-tier chart sourcing:** Tier 1 = catalogue
chart frozen in a story state; Tier 2 = bespoke *simple* story-only chart that never enters
the 20-chart catalogue (e.g. free-fare lift slope, resilience sparkline grid). **4 stories,
26 scenes** (School / Spatial / Financial / Tết). Only the Tết Story is built so far. Full
scene inventories: report Appendix D.

---

## 7 · Architecture — Medallion warehouse (LOCKED, BUILT)

Three tiers in `db/bus.duckdb`, built by `demo/warehouse/build.py`:

- **Bronze** — 24 raw views over the parquet/CSV inputs (immutable).
- **Silver** — 12 dimension tables + 3 fact views (Kimball-dimensional):
  `dim_date` (tags `is_tet` Feb 14–22 + Apr-30 window) · `dim_hour` · `dim_route` (1:1,
  reconciles GPS↔AFC `route_no`) · `dim_stop` · `dim_school` + `dim_school_stop` bridge ·
  `dim_trip` (dedup) · `dim_company` · `dim_fare_class` · `dim_payment_channel` ·
  `dim_vehicle` · `dim_promotion`; facts `fact_boardings`, `fact_gps_trips`,
  `fact_stop_visits` (non-materialised).
- **Gold** — 7 materialised aggregate tables, each a hard chart contract:
  `agg_network_day` · `agg_route_hour` · `agg_route_day` · `agg_stop_hour` ·
  `agg_stop_total` · `agg_school_route` · `agg_hub_kpis`.

**3 Silver integrity bugs found + fixed** (row-multiplication): (1) `ticket_trips.trip_id`
4,051 dupes → `dim_trip` GROUP BY; (2) `route_no` leading-zero variants "03"/"3" →
`dim_route` ROW_NUMBER 1:1; (3) 19 stops within 500 m of 2 universities (HCMUS/SGU) →
`dim_school_stop` closest-school-wins. Result: Bronze→Gold arithmetically lossless.

**Architecture selected from 3 candidates** (report Ch 4.5, measured benchmark vs N1):
plain Medallion (on-demand Gold) · star-schema-over-raw (**rejected: +17.90 % boarding-count
inflation**, fails on integrity before latency) · **Medallion with materialised Gold +
dimensional Silver (chosen)**. Measured: Gold cuts total chart-catalogue serving cost
**~6×** (≈5.5 s → ≈0.9 s per page), up to 2,139× on a single aggregate; build is **O(N)**
(1.95× for 2× input); chart-endpoint median ~31 ms, 9/11 pass the N1 100 ms gate
(spatial/3.1 marginal ~102 ms; spatial/3.4 Voronoi ~311 ms, scipy-bound — figure-cache
candidate). LRU-cache counterfactual rejected (cold cost = Silver cost, dies on restart,
no cross-process sharing). Lineage framed Medallion vs Inmon CIF vs Data Vault 2.0.

`/api` JSON surface: `/api/charts/{theme}/{slug}` (Plotly JSON) · `/api/aggregates/{name}` ·
`/api/kpis` · `/api/healthz` (L2/L4 table-presence check). Page routes and `/api` share the
same chart builders.

---

## 8 · Demo file layout (BUILT under `demo/`)

> Built from scratch under `demo/`. (The dead Streamlit-era `app/` was deleted 2026-06-04;
> `src/duckdb_loader.py` remains — it builds the 24 Bronze raw views the warehouse sits on.)

```
demo/
  main.py                       # FastAPI entrypoint + lifespan (opens DuckDB, sets afc_window)
  db.py                         # read-only DuckDB connector (query / query_one / query_scalar)
  aggregates/{schools,spatial,health}.py   # warehouse-query layer (Gold reads)
  charts/{schools,spatial,health}.py       # Plotly figure builders (chart_<n>_<m>_*)
  charts/style.py               # Knaflic defaults (A2/A4/A5 codified)
  routers/{hub,schools,spatial,health,story_tet,api}.py
  warehouse/{dims,facts,build,benchmark,validate}.py
  templates/ (base, hub, card_{school,spatial,health}, story_tet, partials/)
  static/css|js
```

**Wired chart builders** (the 9 of 20): schools 2.1/2.2/2.3/2.4 · spatial 3.1/3.2/3.4 ·
health 5.1/5.2. Registry in `demo/routers/api.py::_CHART_BUILDERS`.

---

## 9 · Report — Phase 1 deliverable (`report/`, submitted)

LaTeX (xelatex + biber), `\documentclass[12pt]{report}`, Times New Roman. ~174 pages.
Structure: front matter (cover · signature · declaration · acknowledgement · abstract ·
glossary · TOC/LoT/LoF) → **Ch1** Introduction → **Ch2** Related Work (6 tools + research)
→ **Ch3** Theoretical Background (7 sections) → **Ch4** Proposed Solution (8 sections,
largest) → **Ch5** Phase 1 Implementation (3 sections) → **Ch6** Future Work (4 sections)
→ **Ch7** Conclusion (summary · 7 contributions · 6 limitations) → references →
**Appendices A–E** (A DDL + field inventories + 11 data-quality observations · B schedule +
risk register · C LRU + scaling benchmarks · D story scene inventories · E rejected
primitives + interaction patterns). Title: *"Studying and Developing Tools to Analyze and
Visualize Bus Data"*; supervisor Assoc. Prof. Thoai Nam; student Huynh Thanh Duy 2252114;
defence June 2026. `\imageplaceholder{type}{what}{capture}` macro marks un-captured figures.

**Known inconsistencies to fix (found 2026-05-30 on a full read):**

1. **Glossary MCV entry is stale** — `table-of-glossary.tex` still defines MCV as "a
   selection in one chart propagates to every sibling chart," contradicting the retired
   simultaneous-brushing model in Ch3.4 / Ch4.8 / Appendix E.2.
2. **Tết recovery date disagrees** — Ch5.3 + Ch7.1 say "by 23 February"; Appendix D
   Story 4 scene says "Recovery completes by 2 March". Pick one (Feb 23 is the measured value).
3. **Roadmap counts vs built warehouse** — Ch6.1 + Appendix B.1 P1 acceptance say "10 dim
   tables, 3 fact views, 8 aggregates"; the built warehouse is **12 dims + 3 facts + 7 Gold**.
4. **Typo Ch7.1 line 94** — "...the programmatic profiling script, the a running prototype".
   Non-issues checked & cleared: 34 % vs 36 % student share (report uses 36 % consistently in
   Ch4.2/4.6/7.1); leftover `streamlit`/`pydeck` bib entries are uncited (biblatex won't print).

---

## 10 · Reference docs & competitive analysis

**Techniques borrowed:** Knaflic (storytelling: declutter, focus, annotate, narrative;
forbidden pie/donut/3D) · Segel & Heer 2010 (narrative-viz taxonomy) · Liu 2022 (MCV,
Gridify, GroupSet/UpSet) · Chawuthai/Srisakaokul 2023 (Bangkok QoS-1/2/3) · Derevitskiy
2016 (bus-as-sensor speed estimation) · Lin & Zeng 2014 (time-distance arrival prediction,
Marey) · Cleveland & McGill 1984 + Munzner 2014 (chart-selection rubric) · Yi 2007 +
Heer & Shneiderman 2012 + Shneiderman 1996 (interaction taxonomy) · Nguyen & Thoai
(HCMC dataset doc).

**Competitive moats (locked):** (1) school-aware ridership (unique to HCMC student-fare data);
(2) AFC + GPS integrated at `route × hour × day-type` (Swiftly is GPS-only, fare vendors
AFC-only); (3) in-theme Stories on a live dashboard; (4) one multi-stakeholder surface
across 3 personas; (5) HCMC-specific pre-tagged anomaly catalogue (Tết, Apr-30). Frame the
claim carefully: "no *accessible, multi-stakeholder, analytical* dashboard for HCMC bus
exists" — MCPT may have internal SCADA screens we can't see; those aren't our space.
`bus.dev.tris.vn` (Tris research demo) = a single Gridify heatmap, ≈ our chart 3.1 only.

---

## 11 · Backlog / open work

- **Report fixes** — the 4 inconsistencies in §9.
- **Wire the remaining 11 canvases** — Ridership (4), Financial (4), Routes (3).
- **Flexible filter bar** — date range · route · day-type, re-querying every chart.
  (Entity-detail panel is BUILT; the date filter needs date-grain Gold for the
  day-of-week-aggregated tables: `agg_route_hour`, `agg_stop_hour`, `agg_school_route`.)
- **Geocode schools** — manual top-8 universities then Nominatim for the rest (unlocks the
  🟨 School + isochrone charts).
- **Full 50-day Kaggle GPS pull** — unlocks reliability scorecard, speed grid, Apr-30 study,
  the `working` school-bus flag.
- **Re-render 2 Mermaid architecture diagrams** — `mmdc` needs a working Chrome/Puppeteer in
  this env; figures currently use `\imageplaceholder`.
- Schedule cleaning (91k `unknown` service-types) · triage 77 out-of-bbox `afc.stations` ·
  null policy for 4 ≥99 %-null `afc.payments` fields · source Metro Line 1 schedule (or
  finalise hard-coded fallback) · source HCMC weather + OSM road-speed (Phase 2.5+).
- **Stories** — build the 3 unbuilt stories (School, Spatial, Financial); only Tết is wired.

---

---

## 12 · Decision log (condensed — append one line per locked decision, newest last)

- Problem = analytics & visualisation platform over historical GPS + AFC, operations + rider sides.
- 3 personas as internal design tool only; **no role UI**. Driver = data, not user.
- Framing B: cross-source join only at `route × hour × day-type`.
- Demo scope = local 1-day GPS + 90-day AFC; design scope = full 50-day GPS.
- 🌟 Flagship = Schools & Students. Hub → Theme → Chart, Atlas-style, light theme.
- 14 stakeholder questions locked; requirements as 6-field records (R1–R15, N1–N6).
- 12 data invariants locked (6 from exploratory EDA + 5 from programmatic profiling + the
  school-bus `working`-flag invariant).
- Chart invariants A2 (action title + subtitle) · A4 (zero baseline) · A5 (3–8 s test) ·
  A6 (one primitive per theme) locked.
- **Stack switched Streamlit → FastAPI + Jinja2 + HTMX + Plotly + DuckDB + Scrollama**
  (2026-05-20) — the bespoke Atlas design needed full HTML control.
- **Medallion warehouse built** (2026-05-21) — Bronze (24 views) → Silver (12 dims + 3
  facts) → Gold (7 agg tables); Bronze→Gold lossless; 3 Silver integrity bugs fixed.
- **Architecture re-framed Medallion + 5 measured benchmarks** (2026-05-22) — Gold ~6×,
  build O(N), star-over-raw rejected (+17.9 % count inflation), chart p50 ~31 ms.
- **Chart catalogue v5.5 locked (36 → 20 charts)** (2026-05-22) — persona-breadth ordering,
  readability tiers A/B/C, multi-encoding bias, two red-flag reframes (3.2 indicative,
  4.4 free-fare waterfall). Spec at `docs/specs/chart-catalogue.md`.
- **Interaction model: MCV-simultaneous dropped, click-to-entity-panel installed** (2026-05-22)
  — grounded in Yi 2007 + Heer-Shneiderman 2012. Report Ch3.4/4.8 + this file updated.
- **Stories re-aligned to v5.5 + sticky-graphic mechanic** (2026-05-23) — Bing→pinned-chart
  sections→Bongo; two-tier sourcing; 4 stories / 26 scenes.
- **Report rebuilt to match** — stack switch + Medallion + corrected numbers (Tết Feb 14–22
  −57 %/−84 %, 128 routes, 36 % student, Route 20→KHXH-NV) propagated through Ch3–7 + abstract.
- **CLAUDE.md rewritten to current state** (2026-05-30) — collapsed the v1–v4 brainstorm
  history into this log; body (§0–§11) now reflects the built system, not the design path.
  Report inconsistencies catalogued in §9.
- **Entity-detail panel confirmed BUILT** (2026-06-01) — `demo/static/js/charts.js` implements
  click→A3 panel (fields + ranked list + export/share); doc was stale. The remaining Phase 2
  interaction is the **flexible filter bar** (date range · route · day-type); the date filter
  needs date-grain Gold for the dow-aggregated tables. Added a `Makefile` (`make run`).
- **Defence deck Part 5 reframed to proof-by-demo** (2026-06-01) — dropped the number-strip
  engine slide + the limitations slide (limits already in scope + §data "what it can't tell");
  now: running system (hub) · the interaction (real filter/hover/panel captures) · the Tết
  story · a native low-context Phase-2 Gantt. Slide 19 kept as the *designed* interaction model.
- **Defence deck advisor reorg** (2026-06-02) — per advisor: the four interaction/technique
  slides after the 3 stakeholder slides (chart-choice · perceptual ladder · interaction model ·
  stories) moved out of the main flow into backup (redundant B12/B18 pruned); the Tết
  scrollytelling story re-themed dark→**light** to match the hub/cards (`story.css` + chart
  `dark=False`, frames re-captured); a **Phase-1 "objectives met" summary slide** added before
  the Phase-2 Gantt. Deck now 50 slides (27 main + close + backups).
- **"demand"/"supply" purged + two themes renamed** (2026-06-02) — per a hard user rule, the
  words "demand"/"supply" are scrubbed from everything presented. **Theme renames (locked):
  "Demand & Crowding" → "Ridership & Crowding"; "School-Aware Demand" → "Schools & Students"**
  (the latter also drops the "flagship ★" framing). Swept: deck (main + backup slides), demo UI
  (hub, card rail, nav titles, chart titles/subtitles/findings, the Tết story), and this file.
  Hub + entity-panel screenshots re-captured. Note: the submitted report (Ch3–7) still uses the
  old names + "demand" as a generic noun — a separate pass if it is ever revised. Internal code
  identifiers (`flagship_*`, `/cards/demand` placeholder route) are non-visible and left as-is.
- **Flexible filter bar BUILT on the school weekly heatmap (2.3)** (2026-06-03) — four live
  fields (date range · route · day-type · fare class), each re-querying. Solved the date-grain
  gap by querying `fact_boardings` directly instead of the dow-aggregated Gold; dow via
  `dayofweek(day)` (Sun=0, matches the heatmap). Demo files: `aggregates/schools.py`
  (`weekly_heatmap` + `route_list`), `charts/schools.py`, `routers/schools.py`,
  `partials/school_canvas.html` (form `hx-trigger=change`), `card.css`. Deck filter slide +
  Gantt task reworded ("roll the filter bar out to every chart"); filter screenshot re-captured.
  **Defence-deck work has moved well past the 50-slide spec — the live deck is now 44 slides**
  (32 main + 12 backup); many changes (story → 3 proof slides, multi-card slide, rejected-chart
  ladder, general Gantt, hover zoom, the global-`SW`-clobber bugfix) are deck-only and not
  re-catalogued here.
- **Repo cleanup + spec centralisation** (2026-06-04) — deleted the dead Streamlit-era `app/`,
  ~30 root/`report/` scratch captures (`card*`/`hub*`/`story*` PNGs, `probe2.pdf`, `template.pdf`,
  `thy-*`/`cards-23`), LaTeX build artifacts, and stray `__pycache__`. Kept build inputs
  (`template.pptx`, `dashboard_export.pdf`) and the live `src/duckdb_loader.py` (Bronze loader).
  Specs centralised under `docs/specs/` (`chart-catalogue.md` + merged `defence-deck.md`);
  superseded report plans under `docs/superpowers/plans/` deleted, empty tree removed; CLAUDE.md
  spec paths updated.
- **Defence deck Q&A-hardening + QoS↔report alignment + defence prep** (2026-06-04) — (1)
  **QoS backup slide corrected to match report §3.2**: the three axes are **completion ·
  on-path (50 m route adherence) · on-schedule**, NOT the deck's earlier wrong
  "regularity/headway"; deck and report now agree. (2) **Part 3 personas now carry the
  visualization inline** — each want/lens resolves to a "view chip" (chart-shape glyph +
  plain "what you'd see" label), all chart jargon stripped (P&L/QoS/streamgraph/constellation
  gone); passenger "knowable-before" labelled routing-app territory; a standalone
  catalogue+interaction bridge slide was tried then removed in favour of the in-persona
  treatment (Part 3 stays exactly 3 persona slides). (3) **Theory backups** rebuilt to teach
  why+how with bottom-right source cites, all Greek removed (σ/μ/Σ/Δ); recipe regained chart
  examples. (4) **New backup slide 45: the full 12-dimension Silver star** (boardings fact +
  all dims, for the "draw your dimensional model" ask). (5) lone "on-demand" → "Gold built on
  read". **Live deck now 45 slides (32 main + 13 backup).** Defence-prep artifacts written:
  `report/defense_script.md` + `report/defense_qa.md`. New data fact: GPS `extracted.hmm_state`
  is the source provider's HMM output (§3 #13).
- **Report/deck split + leftover-crap purge** (2026-06-04, post-defence) — `report/` is now
  LaTeX-only; the slide deck moved to a top-level `deck/` (`capstone_defence.pptx` = source of
  truth, `.pdf`, `template.pptx`, and the now-stale/broken `build_deck.py`). `report/CONVENTION.md`
  → `docs/conventions/report-writing.md`. Defence over → `defense_script.md` + `defense_qa.md`
  deleted; also removed `dashboard_export.pdf`, `export_pdf.py` (Playwright export), `.playwright-mcp/`,
  `.superpowers/`. `docs/` reorganised into `specs/ · reference/ · project/ · design/ · conventions/`.
  `report/images/` de-messed (149→clean): 57 deck-only assets → `deck/assets/`, 20 dead
  orphan captures deleted, only the 41 report-used figures + EDA figures kept. Diagram
  **sources** centralised under `docs/diagrams/{report,deck}/` (draw.io convention,
  `docs/conventions/diagrams.md`); renders stay with the consumer; report/deck image sets made
  independent. Stale root `requirements.txt` (Streamlit-era) deleted — `demo/requirements.txt`
  is the only one until S1 introduces per-package `pyproject.toml`.
- **Phase 2 direction locked: API backend + React SPA** (2026-06-04) — moving off the
  prototype. Target = clean FastAPI **JSON data API** (returns domain data, not Plotly figures)
  + **React + Vite + TypeScript** SPA that builds charts client-side (react-plotly.js + MapLibre
  + Scrollama). Full-semester runway. Re-architecture spec to be written (S1); report slim-down
  to 50–70pp (S2) + diagram convention → excalidraw/draw.io (S3) follow. *(design in progress)*
- **P0 scaffold merged** (2026-06-05) — monorepo `pipeline/` + `backend/` + `frontend/` on `main`:
  uv/ruff/mypy/pytest · Vite/React19/TS/Tailwind4/vitest · docker-compose · GitHub Actions CI.
  Backend boots `/api/healthz`; frontend builds; `demo/` untouched until parity (P4).
- **Pipeline tooling: dbt + Dagster adopted** (2026-06-05) — Phase-2 data layer = **dbt-duckdb**
  transforms (Silver star + Gold as dbt models; integrity as dbt tests + a singular lossless
  test `boardings == 17,883,623`) orchestrated by **Dagster** (dagster-dbt software-defined
  assets, DuckDB resource, asset checks, schedule-ready). **Supersedes** the report's §4.3.1
  rejection of dbt + §4.5 hand-built Medallion (report rewrite tracked in S2). P1 split: **P1a** =
  dbt warehouse + Dagster; **P1b** = preprocess Dagster asset + §4.3.1 gate as asset checks.
  The old SQL-in-Python P1a plan was replaced.
- **Engine strategy: portable, cloud-scale (DuckDB dev / BigQuery prod)** (2026-06-05) — the real
  production target is **millions of trips/tickets per day**, so the engine must scale past one
  node. Design **separates storage from compute** with dbt as the portability seam: parquet on
  **object storage** · dbt models written DuckDB-first, **dialect-specific SQL macro-ized**
  (`dbt_utils`) · compute = a dbt **target** (`dev`=DuckDB, `prod`=**BigQuery** serverless) ·
  **Dagster** orchestration. Phase 2 **builds+runs locally on DuckDB and PROVES the BigQuery swap
  on a sample** (`dbt compile --target prod`) — no paid cloud operated. **Deferred (not over-
  engineered):** Iceberg/Delta, Spark/Databricks, Kafka streaming, live cloud infra — each a
  documented scale-up path. Chosen via explicit trade-off analysis (BigQuery = lowest-ops path to
  real scale; ClickHouse = best event-perf but more ops; Spark = overkill for SQL at this scale).
- **Engine orientation flipped to BigQuery-primary** (2026-06-06) — per the user (the standard
  *develop-on-the-production-engine* pattern): **BigQuery is the real engine for dev AND prod**
  (`bq_dev` sampled dataset · `bq_prod` full, same engine); source parquet staged to **GCS**,
  Bronze = BigQuery **external tables**; **DuckDB demoted to an optional `local` sampling target**
  (not the source of truth — correctness + CI run on BigQuery). dbt models written
  **BigQuery-dialect first** (DuckDB local via `dbt_utils` macros). Free tier covers capstone
  scale (~$0). GCP setup + env contract: `docs/specs/bigquery-deployment.md`. The BigQuery-primary
  **P1a plan rewrite is pending the user's GCP project/bucket/service-account details**.
- **Dynamic-data reframe + core-only platform scope** (2026-06-06) — the 17.9 M rows are the
  **current dev sample**, NOT a fixed total; production ingests **dynamic, continuously-growing**
  data (far larger). Consequences baked into the design: (1) the lossless invariant is **relative**
  — `Gold boardings == Bronze ticket count` (computed), never `== 17,883,623`; (2) BigQuery
  fact/Gold tables **partitioned by `day` + clustered by `route_no`/`fare_class`**; (3) production
  path is **incremental** dbt models (full-refresh on the sample now, incremental documented).
  **Platform scope = CORE ONLY**: dbt + Dagster + BigQuery + dbt tests + Dagster checks. **Deferred
  until the pipeline + app work end-to-end:** Terraform/IaC, dlt ingestion, dbt contracts,
  Elementary observability, Dagster schedules/alerts (all evaluated, right-sized — not over-built
  now). GCP provisioned **manually** (checklist) for now; Terraform-ize later.
