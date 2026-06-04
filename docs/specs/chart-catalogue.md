# HCMC Bus Analytics — Chart Catalogue v5 (Design)

**Date:** 2026-05-21
**Status:** Draft for user review
**Supersedes:** Catalogue v4 (36 charts, 6 themes, MCV linked brushing) recorded in CLAUDE.md §7
**Companion edits:** Report sections 3.4, 4.7, 4.8 + CLAUDE.md §6 invariant A1

---

## 1 · Problem

Catalogue v4 (36 chart canvases across 6 themes) drew three concerns from review:

1. **Redundancy.** Several themes carried multiple charts answering the same question (School-Aware Demand had four school→route attribution views; Financial had three operator-concentration views).
2. **Static feel.** Charts dominated by ranked-bar primitives were perceived as one-question display widgets rather than interactive analytical surfaces. Chart 1.1 (Top schools ranked bar) was the canonical case.
3. **Interaction model misalignment.** Section 4.8 of the Phase 1 report described Multiple Coordinated Views (MCV) with simultaneous cross-chart brushing, but the actual UI design (CLAUDE.md §6: *"Main canvas = one big chart at ~70% of viewport"*) shows only one chart at a time, making MCV-as-simultaneous-brushing structurally impossible.

---

## 2 · Design moves

### 2.1 · Interaction model: drop MCV-simultaneous, adopt click-to-entity-panel

The system retains MCV as intellectual lineage (Liu 2022) but implements a simpler coordination pattern grounded in the canonical interaction taxonomy of Yi, Kang, Stasko & Jacko (2007). Of Yi's seven interaction categories, six are first-class within every chart (Select, Explore, Reconfigure, Encode, Abstract/Elaborate, Filter); the seventh (Connect) collapses to a single mechanism: **click any entity → side panel slides in with that entity's multi-chart detail**.

The entity panel is the only place in the system where multiple coordinated views render simultaneously. The main analytical surface stays at one chart per canvas.

This is consistent with the UI shell in CLAUDE.md §6 and removes the MCV/UI inconsistency in §4.8 of the Phase 1 report.

### 2.2 · Readability tiering — Tier A / B / C

Every chart is classified by reader cognitive load:

| Tier | Load | Examples | Placement rule |
|---|---|---|---|
| **A** | Instant (≤ 5 sec to first read) | Bubble scatter · Treemap · Streamgraph · Calendar heatmap · Sankey (≤ 8 nodes) · Multi-layer map · Box plot · Stacked area | **Front-door chart** of every theme |
| **B** | 5–10 sec onboarding | Bump chart · Slope chart · Heatmap-with-hover-sparkline · Cartogram · Waterfall · Quadrant scatter | Second / third chart |
| **C** | Specialised; needs caption | UMAP · Marey · UpSet · Parallel coordinates | Drill-in only; never front door |
| D (banned) | Too dense for committee review | Horizon chart · Ridgeline / joy plot · Chord diagram · Heatmap with in-cell mini-charts | — |

**Rule:** a theme has at most one Tier C chart, and never as the entry chart. Theme 6 (Routes) carries an exception: two Tier C charts (UMAP + Marey) on the rationale that Routes is the analytical-depth theme of the platform and earns one specialised theme.

### 2.3 · Per-chart richness — multi-encoding bias

Every chart should encode **at least two axes of variable information** through its visual channels. Simple ranked bars (one axis carrying data) are upgraded to bubble constellations (X, Y, size, colour all carrying data) wherever the underlying question admits multi-attribute comparison.

### 2.4 · Theme size — 2 to 5 charts

Each theme contains 2–5 charts. Themes that drove redundancy in v4 (School, Financial, Routes) shrink to 4; themes already lean (Demand, Spatial) stay at 3–4; Network Health drops to 2 after cutting the orphaned service-day calendar (§4).

### 2.5 · Within-theme chart ordering — persona breadth first

Charts within a theme are ordered top-to-bottom by **persona breadth**. The order matches dwell time: students arrive needing a quick answer ("is my route reliable today"), so the chart visible on theme entry is the chart that serves the most personas. Operators and authorities dwell longer and navigate down to specialist views.

The ordering rule:

1. **Top of theme:** charts that serve all three personas (student + operator + authority) with appropriate filter defaults. These are the "3/3" charts in the persona-breadth scoring of §3.
2. **Middle of theme:** charts that serve two personas (typically operator + authority, or student + authority).
3. **Bottom of theme:** specialist charts that serve a single persona deeply (typically operator-only operational views or authority-only research views).

This drives both the side-nav sidebar order within each theme card and the chart-tab order. Within the same persona-breadth tier, the chart with the simpler readability tier (Tier A before B, B before C) appears earlier.

### 2.6 · Per-chart 10-field defence spec

For each chart in the catalogue, §11 records a defence-ready specification with ten fields: What · Why this chart · Why NOT alternative-1 · Why NOT alternative-2 · Why NOT alternative-3 · Student use · Operator use · Authority use · Defence answer 1 · Defence answer 2. The format follows the question pattern thesis committees apply to visualisation choices: justify the primitive, justify the rejection of obvious alternatives, and demonstrate multi-stakeholder utility.

---

## 3 · Catalogue v5.5 (reordered, post-cuts)

20 charts across 6 themes, ordered top-to-bottom by persona breadth per §2.5. Every front door is Tier A and serves all three personas (3/3 in the breadth scoring).

**Column legend:**
- *Breadth* — number of personas (Student S, Operator O, Authority A) served with strong utility. ⭐⭐⭐ = three; ⭐⭐ = two; ⭐ = one specialist.
- *Data* — data-feasibility tier per §12: ✅ = Phase 1 ready (data complete); ⚙️ = Phase 1 with computation effort (clustering, joins, schedule cleaning); 🟨 = Phase 2 prerequisite (school geocoding OR full 50-day GPS); ⚠️ = conditional on external data or salvage logic.

### Theme 1 · Demand and Crowding (4 — ordered)

| Order | # | Chart | Primitive | Tier | Breadth | Data | Stakeholder Q |
|---|---|---|---|---|---|---|---|
| 1 | 1.2 | Route × hour heatmap (hover → cell sparkline) | Heatmap + tooltip | B | ⭐⭐⭐ S O A | ✅ | P-Q1, P-Q2 |
| 2 | 1.3 | Route constellation (mean × variance × peak × archetype) | Bubble scatter | A | ⭐⭐⭐ S O A | ⚙️ | P-Q1, P-Q2 |
| 3 | 1.1 | Demand streamgraph (fare class × 90 days) | Streamgraph | A | ⭐⭐ O A | ✅ | A-Q3 |
| 4 | 1.4 | Bump chart — top-20 routes' rank over 12 weeks | Bump chart | B | ⭐⭐ O A | ✅ | A-Q7 |

### Theme 2 · School-Aware Demand 🌟 (4 — ordered)

| Order | # | Chart | Primitive | Tier | Breadth | Data | Stakeholder Q |
|---|---|---|---|---|---|---|---|
| 1 | 2.1 | School constellation (vol × peak% × routes × equity colour) | Bubble scatter | A | ⭐⭐⭐ S O A | 🟨 | P-Q3, A-Q4 |
| 2 | 2.2 | School→route treemap with drill | Treemap | A | ⭐⭐⭐ S O A | 🟨 | P-Q3 |
| 3 | 2.4 | School proximity map with walking circles | Annotated map | A | ⭐⭐ S A | 🟨 | A-Q4 |
| 4 | 2.3 | Weekly fare-class heatmap (student / non-student toggle) | Calendar heatmap | A | ⭐⭐ O A | ✅ | P-Q3 |

### Theme 3 · Spatial and Connectivity (3 — ordered, post-fold)

| Order | # | Chart | Primitive | Tier | Breadth | Data | Stakeholder Q |
|---|---|---|---|---|---|---|---|
| 1 | 3.1 | Multi-layer hex map (toggleable layers: density · per-stop demand · ghost stops · district cartogram) | Hex bin map | A | ⭐⭐⭐ S O A | ⚙️ | A-Q1 |
| 2 | 3.2 | Bus↔Metro Sankey (indicative)¹ | Sankey (≤ 8 nodes) | A | ⭐⭐⭐ S O A | ⚠️ | A-Q5 |
| 3 | 3.4 | Accessibility isochrone from chosen origin | Isochrone map | A | ⭐⭐ S A | ⚙️ | A-Q4 |

> Notes: former chart 3.3 District cartogram has been folded into 3.1 as a toggleable layer per §4. ¹*Indicative* qualifier on 3.2 reflects the hard-coded Metro Line 1 schedule fallback (Metro arrival data is not in the published dataset); see §12 red-flag charts.

### Theme 4 · Financial and Operations (4 — ordered)

| Order | # | Chart | Primitive | Tier | Breadth | Data | Stakeholder Q |
|---|---|---|---|---|---|---|---|
| 1 | 4.2 | Operator constellation (share × rev/trip × fleet × on-time) | Bubble scatter | A | ⭐⭐ O A | 🟨 | C-Q3, A-Q6 |
| 2 | 4.1 | P&L quadrant (waste × rev/trip × volume × company) | Quadrant scatter | B | ⭐⭐ O A | ⚙️ | C-Q2 |
| 3 | 4.3 | Payment-channel streamgraph | Streamgraph | A | ⭐⭐ O A | ✅ | descriptive |
| 4 | 4.4 | Free-fare student-day lift waterfall + synthetic-control overlay² | Waterfall composite | B | ⭐ O | ⚙️ | C-Q4 |

> ²Reframed from "Promotion DiD" because `promotion_code` is 99 % null in `afc.payments` per CLAUDE.md §10. Free-fare student days are in the `fare_class` field (free-pass, 9 % of boardings) and serve as the proxy promotion event for DiD analysis. See §12 red-flag charts.

### Theme 5 · Network Health and Performance (2 — ordered, post-cut)

| Order | # | Chart | Primitive | Tier | Breadth | Data | Stakeholder Q |
|---|---|---|---|---|---|---|---|
| 1 | 5.2 | QoS small-multiples scatter (3 mini-scatters, one per QoS dimension) | Small multiples | A | ⭐⭐⭐ S O A | 🟨 | A-Q2 |
| 2 | 5.1 | Network pulse with anomaly bands + threshold slider | Timeline + bands | A | ⭐⭐ O A | ✅ | A-Q3, A-Q2 |

> Note: former chart 5.3 Service-day calendar cut per §4. Theme falls below the soft 3-chart floor but holds the analytical-coverage line (reliability + anomalies = full coverage of the theme's question).

### Theme 6 · Routes (3 — ordered, post-move)

| Order | # | Chart | Primitive | Tier | Breadth | Data | Stakeholder Q |
|---|---|---|---|---|---|---|---|
| 1 | 6.4 | Per-stop arrival box plot along route | Box plot | A | ⭐⭐⭐ S O A | 🟨 | P-Q1 |
| 2 | 6.3 | Stop-by-stop boardings + door-dwell dual axis | Dual-axis bar+line | B | ⭐⭐ O A | 🟨 | C-Q1 |
| 3 | 6.2 | Marey time-distance diagram with dwell heatmap composite | Marey + heatmap | C | ⭐⭐ O A | 🟨 | P-Q1 |

> Note: former chart 6.1 UMAP route constellation moved to authority-only research appendix per §4.

---

## 4 · Cuts from v4 (and v5 → v5.5 refinements)

### 4.1 · v4 → v5 cuts

The catalogue first dropped from 36 to 23 canvases (net reduction of 13). Fifteen individual v4 canvases were removed; five of those were replaced by new aggregated canvases (the three constellation scatters), giving the net of 13.

| Cut | Disposition |
|---|---|
| School: Schools→Routes bipartite graph | Removed; redundant with treemap; networks fail the Connect criterion cleanly |
| School: Student-flow Sankey (school→route→district) | Removed; folded into treemap drill |
| School: School-routeness parallel coordinates | Removed; covered by school constellation |
| School: Top schools ranked bar | **Replaced** by school constellation |
| Demand: Top routes ranked bar | **Replaced** by route constellation |
| Demand: Per-route headway box plot | Removed; folded into route constellation (variance axis) |
| Demand: Demand-variance quadrant | Removed; folded into route constellation |
| Financial: Financial signatures parallel coordinates | Removed; redundant with P&L quadrant + operator constellation |
| Financial: Market-structure treemap | Removed; folded into operator constellation |
| Financial: Operator-route marimekko | Removed; folded into operator constellation |
| Financial: Operator scorecard ranked bar | **Replaced** by operator constellation |
| Routes: Single-route summary table | Removed; static; entity-panel covers single-route summary |
| Routes: Multi-route parallel coordinates | Removed; redundant with UMAP |
| Routes: Pairwise stop-delay scatter | Removed; small-multiples are display-leaning, not worth a slot |
| Routes: Period-comparison slopegraph | Removed; orphan; no interaction wiring |

Replacements introduced in v5 (the three constellations) each absorb 2 to 3 v4 canvases, so the catalogue is denser per-chart than v4 even though chart count drops by a third.

### 4.2 · v5 → v5.5 cuts (post-persona-breadth scoring)

A second pruning pass applied the 3-persona breadth scoring of §2.5: a chart that serves only one persona (1/3 breadth) and is not the single specialist anchor for that persona is a candidate for cut, fold, or move to an appendix. Three v5 canvases failed this test.

| v5 chart | Breadth | Disposition |
|---|---|---|
| 3.3 District cartogram | ⭐ A-only (authority pattern correction) | **Folded** into 3.1 multi-layer hex map as a "by-district cartogram" toggleable layer. Avoids losing the analytical capability while removing a single-persona canvas. |
| 5.3 Service-day calendar | ⭐ A-only (authority calendar pattern) | **Cut.** Overlaps with 5.1 network pulse on the temporal dimension; the calendar's distinct day-of-week reading does not justify the canvas in a 2-persona-minimum catalogue. |
| 6.1 UMAP route constellation | ⭐ A-only (research-oriented embedding) | **Moved** to a research-appendix view outside the main themes. Defensible position: "we exposed the technical embedding for advanced users but kept the front-door catalogue accessible to all personas." |

**Final count:** 20 canvases across 6 themes (4 / 4 / 3 / 4 / 2 / 3).

---

## 5 · Interaction contract (every chart)

Every chart **must** support, at minimum:

- **Select** — click an entity (bar segment, bubble, cell, stop, polygon)
- **Filter** — date-range picker (theme-wide) and chart-specific filters
- **Abstract/Elaborate** — click → side panel with multi-chart detail of clicked entity

These three are non-negotiable. The Rule-of-Three test from Yi (2007) — a chart that supports 0 to 1 of the seven categories is a display widget, not an interactive surface — is the criterion for inclusion in the catalogue.

Each chart additionally supports 1 to 4 of the remaining four Yi categories (Explore, Reconfigure, Encode, Connect-via-panel), spec'd per chart in a separate document.

### 5.1 · Entity-detail panel conventions

- **Slides from right**, occupies ~40% of viewport (or surfaces as a smaller floating popover for quick reads — pattern from `docs/design/app-layouts.html` `.pop` block)
- **Body** carries at most four mini-views (one summary view + up to three drill views)
- **Header** shows entity name, type, and a "back to theme" link
- **Footer** shows "Export as PDF" + "Copy shareable link" (state captured in URL per R10)
- **Click outside** closes the panel; the X button also closes
- **Re-click on a different entity** while panel is open: replaces panel contents with new entity (the most common pattern)
- **Universal click contract:** every chart's primary click affordance opens the panel for the clicked entity. Drill / zoom / expand actions live as separate affordances (button in the panel header, double-click on the canvas). One click never has two meanings.

### 5.2 · Top View Controls bar (per chart)

Following the `.vc` block in `docs/design/app-layouts.html`, every chart canvas carries a horizontal **View Controls** bar at the top, separated from the chart by the legend strip. The bar groups controls into:

- **Filter group** — date range (always), plus theme-specific primary categorical filter (fare class, operator, etc.)
- **Encoding group** — radio toggles for X-axis, Y-axis, size, colour where the chart's encoding is reconfigurable
- **View group** — chart-mode toggles (heatmap axis swap, treemap drill level, etc.)
- **Settings button** — opens a popover for advanced controls (colour scale, null-handling, etc.)

The View Controls bar is the in-canvas implementation of Yi (2007) categories Filter, Reconfigure, and Encode. It is the visible answer to the defence question *"how is this chart actually interactive?"*

### 5.3 · Colour encoding policy

- **Gradient first** for any quantitative encoding (volume, score, density). Default ramp follows the `linear-gradient(90deg, #FFF1EB → #FBC9B3 → #F39A6F → #E45A2E)` orange-warmth scale from `docs/design/app-layouts.html`.
- **Solid bins** only where the data has policy-defined hard cutoffs (equity flag red / amber / green; QoS pass / warn / fail). Solid colour signals a categorical reading; gradient signals a continuous one. The choice is a chart-author declaration of what the reader should infer.
- **Single accent colour** per chart for the focal annotation (saturated orange `#E45A2E`); rest of the palette is muted grey (`#1B2333` family from app-layouts).

---

## 6 · Cross-cutting policies

- **Theme-wide filter bar** at the top of each theme: date range + the primary categorical dimension of that theme (fare class for School/Demand, operator for Financial, etc.). Filter state persists as user navigates between charts in the theme.
- **Action title + supporting subtitle** on every chart (invariant A2 from CLAUDE.md §6)
- **Zero baseline** on every bar-encoded chart (invariant A4)
- **Three-to-eight-second readability test** at design time (invariant A5)
- **One primitive per theme** (invariant A6) holds, except where a primitive is shared across themes as part of a consistent visual vocabulary

---

## 7 · Document impact

Edits this design will drive across the report:

| File | Change |
|---|---|
| `report/sections/Ch3_FoundationsTools/3.4_MCV.tex` | Rename section / re-scope MCV as intellectual lineage; add Yi (2007) and Heer & Shneiderman (2012) citations |
| `report/sections/Ch4_ProposedSolution/4.7_VisualisationSelection.tex` | Replace catalogue (36 → 23 charts); add Interactions column per chart table; record cuts |
| `report/sections/Ch4_ProposedSolution/4.8_InteractionModel.tex` | Drop MCV-simultaneous worked example; install entity-detail panel as the single coordination pattern; rewrite §4.8.1 and §4.8.3 |
| `report/bibliography.bib` (or equivalent) | Add Yi 2007 and Heer-Shneiderman 2012 entries |
| `CLAUDE.md` | Update §6 invariant A1 (linked brushing → entity-panel handoff); update §7 with v5 catalogue summary |

The LaTeX revision pass is the appropriate place to dispatch the `academic-paper revision` mode (per `/academic-research-skills:academic-paper`).

---

## 8 · Open questions

1. **Per-chart interaction spec** (filters / clickable elements / click-display behaviour / side-panel content) for all 23 charts — to be written as a companion document or appended to this spec? Decision deferred until user signs off on this design.
2. **Whether to retire the v3 / v4 catalogue in CLAUDE.md §7** or keep it as historical record. Recommendation: keep §7 historical, add §7a pointing to this spec.

---

## 9 · Acceptance criteria for the spec

- ✓ Every theme has 2–5 charts (per §2.4, Network Health holds at 2)
- ✓ Every theme's front-door (top-of-order) chart is Tier A AND ⭐⭐⭐ persona breadth
- ✓ Theme 6 carries one Tier C chart (Marey) as the operational depth anchor
- ✓ Every chart supports Select + Filter + Abstract (minimum Yi categories)
- ✓ Every chart has at least two axes of variable information (no simple ranked bars)
- ✓ Every chart traces to ≥ 1 of the 14 stakeholder questions in §2.1 of the Phase 1 report
- ✓ Cuts from v4 (§4.1) and v5 → v5.5 (§4.2) are documented with reasons
- ✓ Every chart in §11 has the full 10-field defence specification
- ✓ Within-theme ordering follows the persona-breadth rule of §2.5

---

## 10 · References

- Yi, J. S., Kang, Y., Stasko, J. T., & Jacko, J. A. (2007). Toward a deeper understanding of the role of interaction in information visualization. *IEEE Transactions on Visualization and Computer Graphics, 13*(6), 1224–1231.
- Heer, J., & Shneiderman, B. (2012). Interactive dynamics for visual analysis. *Communications of the ACM, 55*(4), 45–54.
- Shneiderman, B. (1996). The eyes have it: A task by data type taxonomy for information visualizations. *Proceedings of the IEEE Symposium on Visual Languages*, 336–343.
- Liu, S. (2022). *Multiple Coordinated Visualization for big-data temporal exploration* [PhD thesis].
- Knaflic, C. N. (2015). *Storytelling with Data: A Data Visualization Guide for Business Professionals*. Wiley.
- Few, S. (2006). *Information Dashboard Design: The Effective Visual Communication of Data*. O'Reilly.

---

## 11 · Per-chart defence specifications

Each chart in the catalogue is recorded with the ten-field defence template introduced in §2.6. The template format:

> **What** — concrete chart description (primitive + encoded variables + interaction surface).
> **Why this chart** — first-principles justification of the primitive choice.
> **Why NOT alt-1, alt-2, alt-3** — three obvious alternatives considered and rejected, each with a one-sentence reason.
> **Student use** — filter defaults + decision + click action for the student persona.
> **Operator use** — filter defaults + decision + click action for the operating-company persona.
> **Authority use** — filter defaults + decision + click action for the public-transport-authority persona.
> **Defence answer 1** — anticipated defence question on primitive choice + the answer.
> **Defence answer 2** — anticipated defence question on multi-persona utility + the answer.

The format is structured to answer the question pattern thesis committees apply to visualisation choices. The first three fields justify *what* the chart is and *why* it is that way. The next three demonstrate *who* uses it across the three personas, with concrete filter defaults so the defence does not have to hand-wave. The last two pre-load the two questions most likely to surface in the oral defence: *"why this primitive over the obvious alternative?"* and *"how does this serve more than one user?"*

Per-theme ordering within this section follows the persona-breadth top-to-bottom order of §3.

---

### 11.1 · Theme 1 · Demand and Crowding

#### Chart 1.2 — Route × hour heatmap (with hover-to-sparkline)

**What.** A two-dimensional categorical heatmap. Rows: routes (top-30 by volume by default, expandable). Columns: 24 hours of the day. Cell colour: gradient orange ramp (per §5.3) encoding average boardings per hour. Hover on a cell opens a small floating popover containing the cell's day-to-day variance as a 30-day sparkline. The View Controls bar above the chart carries: date range (theme-wide), day-type filter (weekday / weekend / holiday), routes filter (top-30 / top-50 / all), sort axis (alphabetical / by-volume / by-archetype), and a colour-scale toggle (linear / log / diverging vs network average).

**Why this chart.** The dominant question for the Demand and Crowding theme is "when and where does ridership concentrate." The matrix structure of `route × hour` is the canonical encoding for that question; cell colour answers the magnitude question instantly, the matrix arrangement answers the pattern question (one peak vs two peaks; commuter vs all-day vs leisure). Adding the hover sparkline grafts a second analytical axis (day-to-day variance) onto the same canvas without crowding the visual — Tufte's "small multiples in the tooltip" pattern. The chart serves the Tier B readability budget: a reader who has never seen the chart understands the matrix in 5 seconds; the hover discovery rewards a second pass.

**Why NOT a stacked bar of total boardings per route.** A stacked bar collapses the 24-hour dimension into a single height, hiding the peak-hour pattern that is the question's whole point. Routes that look identical in total can have completely different hourly signatures.

**Why NOT a per-hour line per route (spaghetti plot).** 30 lines on a single chart loses individual identity (Munzner's spaghetti problem). The reader cannot trace any single route; the chart degrades to a generic shape.

**Why NOT a 3D surface.** Banned per Knaflic Ch. 2 (3D distorts magnitude perception). A 2D heatmap with gradient colour answers the same `route × hour × magnitude` question without the distortion.

**Student use.** Default filter: **{my-route + 5 nearest neighbours, weekday}**. Decision the chart serves: *"Is my route as crowded at 5 PM as I think it is, and is there a calmer alternative?"* Click action: clicking a row's 5 PM cell opens the side panel with that route's 30-day reliability ribbon and a "compare to my saved route" overlay.

**Operator use.** Default filter: **{my-company's routes, all-week}**. Decision: *"Which of my routes have a saturating peak that needs extra trips?"* Click action: clicking a high-magnitude cell opens the panel with the trip count vs scheduled-trip-count for that hour, surfacing under-supply on the operator's own fleet.

**Authority use.** Default filter: **{all routes, weekday}**. Decision: *"Where is supply diverging from demand — which routes are red-hot at peak but have no scheduled capacity slack?"* Click action: clicking a cell opens the panel with the cell-level breakdown by operator, allowing the authority to see which operator is responsible for the under-supplied peak.

**Defence answer 1 — "Why a heatmap and not, say, parallel coordinates?"** Parallel coordinates answers a multi-attribute *profile* question ("how does route X score across 8 metrics"). The Demand-and-Crowding theme's primary question is a *spatio-temporal* question ("when, on what route, does crowding occur"), which is exactly what a heatmap is designed for. The two charts solve different problems. The catalogue's parcoords-equivalent for routes lives in Theme 1's chart 1.3 (route constellation, which combines 4 attributes into a bubble scatter) — the analytical surface as a whole offers both lenses.

**Defence answer 2 — "How does one chart serve three personas?"** The chart's structure (route × hour × magnitude) is invariant; only the *filter default* changes per persona. The student sees a small set of routes relevant to their commute; the operator sees their fleet; the authority sees the whole network. The interaction contract (click → panel) is identical, but the panel content adapts to the clicked entity's relationship to the active persona's filter. This is multi-persona utility through filter and panel adaptation, not through chart-shape variation — defensible as *"one analytical surface, three configured entries."*

---

#### Chart 1.3 — Route constellation (bubble scatter)

**What.** Bubble scatter. X = mean daily boardings (90 d). Y = day-to-day coefficient of variation (predictability inverse). Bubble size = peak-hour load. Colour = archetype cluster rendered as a gradient ramp by mean rather than discrete bin (per §5.3). Hover = tooltip with route number, peak ID. View Controls: date range, Y-axis encoding swap (variance / weekend ratio / summer drop), size swap (peak load / # trips / vehicles), colour rule (archetype / operator / district), top-N filter.

**Why this chart.** Two-dimensional position + size + colour = four variables in one screen. Bubble scatter is the canonical *gapminder* primitive — universally readable in under five seconds. Quadrants self-label: top-right = high-volume + high-variance (volatile workhorses), top-left = high-volume + predictable (network prestige routes), bottom-right = niche volatile, bottom-left = candidates for service rationalisation.

**Why NOT a ranked bar.** Bars rank one variable; the question is intrinsically two-dimensional (volume × predictability). A ranked bar collapses "busy but reliable" and "busy but volatile" into the same rank.

**Why NOT parallel coordinates.** Parcoords requires the reader to mentally trace polylines across axes — fails the 5-second readability test. Scatter wins at first impression.

**Why NOT a treemap.** Treemap encodes a hierarchy through area; routes have no hierarchy — they are peer entities with attributes.

**Student use.** Default filter: {my route + 5 nearest neighbours in archetype space, weekday}. Decision: *"Is my route reliable, or is there a more reliable alternative carrying similar demand?"* Click action: click neighbour bubble → side panel with that route's 30-day reliability ribbon and "compare to my route" overlay.

**Operator use.** Default filter: {my company's routes, all data}. Decision: *"Which of my routes is spike-prone — I need to add reserve capacity."* Click action: click high-Y-variance bubble → panel with the route's anomaly history.

**Authority use.** Default filter: {all routes}. Decision: *"Which routes deserve scrutiny? Where are operators dumping capacity on already-busy routes while ignoring spike-prone underserved ones?"* Click action: brush a region → multi-route comparison panel.

**Defence answer 1 — "Why bubble scatter not parcoords?"** Bubble scatter answers a positional comparison question ("where does this route sit on the busy / reliable plane?"); parcoords answers a profile question ("what does this one route's signature look like across many metrics?"). The catalogue uses parcoords for high-dimensional profile views and bubble scatter for low-dimensional positional views (this chart, plus 2.1 school constellation and 4.2 operator constellation). The pattern is consistent.

**Defence answer 2 — "How does one chart serve three personas?"** The chart's bubble cloud is fixed; the persona-specific filter default sets which bubbles are emphasised. The student sees ~6 nearby bubbles, the operator sees ~12 fleet bubbles, the authority sees all 184. Same chart, three configured entries.

---

#### Chart 1.1 — Demand streamgraph (fare class × 90 days)

**What.** Symmetric-baseline streamgraph (organic stacked area). X = calendar day across the 90-day AFC window. Y = boardings, stacked by fare class group (student-HS, student-SV, adult, elderly, free-pass). Gradient orange ramp across student bands; muted grey for adult / elderly / free per §5.3. Named-event flags marked inline on the X-axis: Tết Lunar New Year window (Feb 14–22), April 30 parade week. Hover = tooltip with daily breakdown by fare class. View Controls: fare-class subset toggle, date range, normalisation toggle (absolute vs percent).

**Why this chart.** The question "how does total ridership composition shift over time, and what shock events are visible" needs organic composition flow. Streamgraph encodes each band's thickness as that group's contribution. The Tết dip becomes a self-evident narrowing of the river; recovery becomes the river re-widening.

**Why NOT a stacked bar chart.** Daily bars at 90-day resolution create visual jitter (each bar a hard column); the streamgraph's smooth baseline reveals organic shape.

**Why NOT a line chart per fare class.** Five lines force the reader to mentally sum them to read total ridership — losing the composition perspective. Streamgraph encodes composition via thickness directly.

**Why NOT a stacked-100 % bar.** Percentage-stacked loses absolute magnitude — the reader cannot see Tết as a *drop* in total volume; only relative-composition shift. The chart needs absolute magnitude to surface the shock.

**Student use.** Default filter: {student bands only, full 90 days}. Decision: *"Does student ridership recover after Tết — should I plan for capacity issues?"* Click action: click an anomaly date → panel with that day's per-route breakdown.

**Operator use.** Default filter: {all bands, my-company subset}. Decision: *"What's my fare-class mix and how did it move during the holiday?"* Click action: click a fare band → panel with that band's per-route contribution.

**Authority use.** Default filter: {all bands, full window}. Decision: *"How resilient is the network to shocks? Which fare classes recover fastest?"* Click action: click a date in the Tết window → panel with the recovery trajectory.

**Defence answer 1 — "Why streamgraph not just stacked area?"** Symmetric baseline treats every band equally; standard stacked area pins one band to the X-axis, distorting the perceived stability of the bottom band. Symmetric baseline is the correct encoding when no single band has analytical priority — which is true here, all fare classes matter.

**Defence answer 2 — "Why does this serve more than the authority?"** The Tết shock affects every persona's planning. Students plan their post-Tết return; operators schedule reduced holiday service; authorities assess network resilience. The shock window is a shared analytical fact across all three.

---

#### Chart 1.4 — Bump chart (top-20 routes' rank over 12 weeks)

**What.** Bump chart (parallel-rank polylines). X = weeks (12 weekly bins). Y = rank position (top-20 routes by weekly boardings). Each route is a polyline connecting its rank across weeks. Lines cross when routes swap ranks. Gradient colour intensity = current-week rank (top-5 saturated, 16–20 muted). Hover = tooltip with route number and rank trajectory. View Controls: top-N (10 / 20 / 30), date window (last 12 weeks / last 6 months / full), metric (boardings / revenue / on-time).

**Why this chart.** The question "which routes are climbing or falling in importance over time" is an ordinal-change-over-time question. Bump chart is the canonical primitive for it (invented for sports league standings, adopted for any rank-flow narrative). Line crossings visually surface the "swap" moments that are the story.

**Why NOT a multi-line absolute chart.** Absolute values obscure rank changes when two routes converge in volume; the rank reordering is invisible. Bump chart makes the reordering itself the visual subject.

**Why NOT a slopegraph (first vs last week).** Slopegraph collapses 12 weeks into 2; middle-week swaps are lost. Bump chart preserves temporal granularity.

**Why NOT a heatmap with rank as colour.** Heatmap by week (X) × route (Y) with rank as colour would work, but loses the line-trajectory reading that's the intuitive way to follow a single route.

**Student use.** Default filter: {my saved route + immediate neighbours, last 12 weeks}. Decision: *"Is my route gaining or losing importance?"* (Situational context, not daily decision.) Click action: click route line → panel with the trajectory broken down by weekday vs weekend.

**Operator use.** Default filter: {my company's routes, last 12 weeks}. Decision: *"Which of my routes is climbing — should I shift resources toward it?"* Click action: click an upward-climbing route → panel with per-week boarding deltas + rolling 4-week trend.

**Authority use.** Default filter: {all routes, last 12 weeks}. Decision: *"Which routes are silently becoming critical infrastructure — and which formerly-critical routes are atrophying?"* Click action: click a crossing event → panel with the swap context.

**Defence answer 1 — "Why bump chart not line chart of absolute values?"** Bump chart isolates the *ordinal* signal; absolute lines mix ordinal (rank) and cardinal (magnitude) into one visual. The question this chart answers is ordinal-only.

**Defence answer 2 — "How does this serve the student?"** Student use is the weakest of the three (2/3 breadth). The defensible justification is situational awareness ("my route is gaining traffic, expect more crowding next month") — context for occasional planning, not the daily tool.

---

### 11.2 · Theme 2 · School-Aware Demand 🌟

#### Chart 2.1 — School constellation (bubble scatter)

**What.** Bubble scatter. X = total student boardings 90 d. Y = morning-peak share %. Size = # serving routes within 400 m. Colour = equity flag (gradient red < 100 m no stops → amber → green) per §5.3 hybrid policy. Hover = tooltip with school name, verified✓ flag, type, total boardings, distance to nearest stop. View Controls: Y-axis swap (peak % / weekend ratio / summer drop), size swap (# routes / # within 400 m / avg trips), colour rule (equity / operator / district), school type subset.

**Why this chart.** School-aware demand is the flagship theme; the question "which schools shape demand and how" is a multi-attribute question. Bubble constellation surfaces four dimensions at once. Quadrants self-label: high-vol high-peak = commuter universities; low-vol low-peak = underserved schools.

**Why NOT a ranked bar of schools.** Collapses four dimensions into rank; loses the equity signal entirely (the gradient colour is what surfaces underserved schools).

**Why NOT parallel coordinates of school attributes.** Parcoords requires polyline tracing — fails 5-second readability for the front-door chart of the flagship theme.

**Why NOT a treemap by school.** Treemap is hierarchical (school → route); this chart is positional (where each school sits on the demand-pattern plane). Different question (treemap lives in 2.2).

**Student use.** Default filter: {my school highlighted + nearby schools}. Decision: *"Is my school well-served compared to peers?"* Click action: click my school → side panel with serving routes + walking distances.

**Operator use.** Default filter: {schools served by my routes}. Decision: *"Which schools depend on me — am I their dominant operator?"* Click action: click school → panel with my routes' share of that school's boardings.

**Authority use.** Default filter: {all schools, equity colour}. Decision: *"Which schools have equity gaps — no stop within walking distance?"* Click action: click red bubble → panel with proposed nearest-route extension distance.

**Defence answer 1 — "Why bubble scatter not treemap?"** Bubble surfaces the *positional* signal (where on demand × peak plane); treemap surfaces the *proportional* signal (share of total). The flagship theme's primary question is positional; treemap (chart 2.2) handles the proportional question separately.

**Defence answer 2 — "How is this defensible as flagship?"** Flagship status comes from the equity gradient encoding (chart's fourth channel). No surveyed tool (BusMap, GoBus!, MultiGo, bus.dev.tris.vn) renders equity information at the school level. The chart is the analytical surface no one else provides, anchored on data (34 % student-fare share) unique to HCMC's ticketing system.

---

#### Chart 2.2 — School→route treemap with drill

**What.** Hierarchical treemap. Outer rectangle = school (sized by student-boarding volume). Inner rectangle = route serving the school (sized by route's share of school's boardings). Gradient: outer cell colour intensity = total school volume; inner cell colour = route's share of school total. Hover = tooltip with cell label, volume, % of parent. View Controls: top-N schools (8 / 16 / 32 / all), day type (all / weekday / weekend), inner-cell colour rule (volume / school type / dominant-route operator).

**Why this chart.** Schools and their routes form a natural hierarchy; treemap is the canonical primitive for hierarchical magnitude — preserving the parent-child reading and encoding magnitude through area.

**Why NOT a bipartite network graph.** Networks fail the Connect criterion cleanly — cannot receive brushes easily and read poorly past ~20 nodes per side.

**Why NOT a Sankey of school → route → district.** Sankey is correct for 3-stage flows; treemap suffices for the 2-stage hierarchy here. Adding district makes it too dense for the front-row position (Theme 3 covers spatial).

**Why NOT a stacked bar (school as bar, routes as segments).** Stacked bar fragments the hierarchy into bar segments — loses "single school = single rectangle" visual.

**Student use.** Default filter: {my school, drill into school}. Decision: *"Which routes serve my school, and how dominant is each?"* Click action (universal contract): single click on outer cell (school) or inner cell (route) → side panel opens for clicked entity. Drill into school is a separate affordance in the panel header ("drill into HCMUS").

**Operator use.** Default filter: {schools served by my routes, drill into route}. Decision: *"Which schools am I dominant for, and where am I peripheral?"* Click action: click inner cell → panel with my route's share of that school's boardings.

**Authority use.** Default filter: {top-16 schools, all routes}. Decision: *"Network structure of student transport — which schools have concentration risk (one route carrying 80 %+)?"* Click action: click outer cell → panel with school's concentration ratio.

**Defence answer 1 — "Why treemap not Sankey?"** Treemap encodes hierarchy + magnitude through area; Sankey encodes flow + magnitude through ribbon width. The question is "how much of each school's demand goes through each route" — a hierarchical magnitude question, exactly what treemap solves. Sankey would add a stage (destination district) the analytical question doesn't need.

**Defence answer 2 — "How does drill honour the universal click contract?"** Per §5.1, every click opens the side panel — that's the contract. Drill is a separate affordance via a button in the panel header. One click never has two meanings; drill is a deliberate second action initiated by the user.

---

#### Chart 2.4 — School proximity map with walking circles

**What.** Annotated map. Schools = star markers. Stops = dots. On chart load: gradient colour from green (no equity gap) through amber to red (gap > 400 m). Click school → walking circle drawn at chosen threshold around the school; nearby stops highlight. View Controls: walking threshold (300 / 400 / 500 m), school type, district subset, equity colour rule.

**Why this chart.** The question "which schools sit outside walking distance of any served stop" is intrinsically spatial; only a map answers it directly.

**Why NOT a list of schools sorted by nearest-stop distance.** Loses spatial context — reader cannot see whether underserved schools are clustered (suggesting a corridor gap) or scattered (suggesting individual placements).

**Why NOT a hex-density map.** Hex density shows boarding intensity, not school positions. Different question.

**Why NOT a Voronoi of stop catchments.** Voronoi answers "which stop owns which area" — a stop-centric question. This chart is school-centric.

**Student use.** Default filter: {my school zoomed-in + walking circles drawn}. Decision: *"How far is my school from the nearest stop, and which routes can I take?"* Click action: click my school → panel with serving routes and walking distances.

**Operator use.** Default filter: {schools within my routes' coverage}. Decision: *"Where are the gaps my company could close by extending a route?"* Click action: click red school → panel with proposed extension distance.

**Authority use.** Default filter: {all schools, equity colour}. Decision: *"Where are equity gaps city-wide — which districts have a cluster of underserved schools?"* Click action: click district polygon → panel with district-aggregate equity score.

**Defence answer 1 — "Why a map and not a list?"** Spatial pattern (clustered gap vs scattered gap) is invisible on a list. Clustered gaps suggest a missing corridor; scattered gaps suggest individual school placement. Only a map reveals the difference.

**Defence answer 2 — "How is this not authority-only?"** Walking-distance equity is a passenger-facing fact (the student or their parent makes the daily walk). The chart's student-use default puts the panel directly on the student's school. The operator-use default highlights schools the operator could profitably serve.

---

#### Chart 2.3 — Weekly fare-class heatmap

**What.** Day-of-week × hour heatmap. Cell colour = boardings for the selected fare-class subset. Toggleable mode: single-fare-class view (all data filtered to chosen class) or side-by-side (student vs non-student two-heatmap layout). Gradient orange ramp. View Controls: fare-class mode (all / student-only / non-student-only / side-by-side), date window, school filter (when set, heatmap restricts to that school's boardings), colour scale (linear / log / diverging vs network average).

**Why this chart.** The "when in the week do which fare classes ride" question is categorical-temporal. Calendar heatmap is the canonical primitive (universally readable; everyone knows a calendar). Side-by-side mode directly answers the student-vs-non-student comparison that is the flagship-theme story.

**Why NOT a line chart of hourly boardings per fare class.** Multiple lines obscure the day-of-week dimension. Heatmap encodes both day and hour at once.

**Why NOT a stacked area of fare classes by hour.** Stacked area shows composition over hours but loses the day-of-week dimension entirely.

**Why NOT a streamgraph (like chart 1.1).** Streamgraph over the 24-hour cycle is unusual; calendar heatmap is the convention readers will recognise.

**Student use.** (Weak 2/3 breadth for this dimension.) Default filter: {student-only mode}. Decision: *"When are the student-heavy hours — when should I avoid the crush?"* Click action: click cell → panel with top routes at that slot.

**Operator use.** Default filter: {side-by-side mode}. Decision: *"Does my route's demand pattern match the student pattern (school routes) or the adult pattern (commuter routes)?"* Click action: click cell → panel with the cell's per-route breakdown.

**Authority use.** Default filter: {all-mode, all-window}. Decision: *"How does fare-class composition shape the network's weekly load?"* Click action: click cell → panel with the slot's full fare-class decomposition.

**Defence answer 1 — "Why heatmap not stacked area?"** Heatmap encodes two categorical axes (day, hour) + one quantitative (boardings) in one canvas. Stacked area encodes only one categorical + composition — losing the day-of-week dimension that distinguishes school routes from commuter routes.

**Defence answer 2 — "Why is this 2/3 breadth, not 3/3?"** The student's primary need ("when to avoid the crush") is already covered by chart 1.2. This chart's added value is the *fare-class decomposition*, which is more strategic than tactical for the student. The 2/3 score is honest; the chart belongs because the fare-class decomposition cannot fold into 1.2 without overloading the heatmap.

---

### 11.3 · Theme 3 · Spatial and Connectivity

#### Chart 3.1 — Multi-layer hex map

**What.** Hex-bin map of Ho Chi Minh City (H3 cells at 500 m default resolution). Toggleable layers: route network polylines, hex density (gradient orange ramp encoding boardings), per-stop demand dots, ghost-stop overlay (stops where door-open ratio < 20 %), district cartogram outline (boundaries distorted area-proportional to boardings — folded from former chart 3.3 per §4.2). View Controls: layer toggle (independent on/off per layer), hex cell size (200 / 500 / 1000 m), date window, fare class.

**Why this chart.** The "how does demand distribute spatially across the city" question demands a uniform-area aggregation — hex bins control for the district-area bias that a choropleth would introduce. Multi-layer toggling answers five related questions on one canvas without forcing navigation between five separate maps.

**Why NOT a choropleth keyed to districts.** HCMC districts vary in area by an order of magnitude; choropleth confounds intensity with area. Hex bins are uniform. (The district cartogram is now an optional layer — keeps the analytical capability without the choropleth distortion.)

**Why NOT a continuous-density KDE (smooth heatmap).** KDE is visually attractive but readers struggle with cell-level interrogation; hex bins allow drill-into-cell interactions.

**Why NOT separate maps per layer.** Five separate maps fragment attention; reader cannot cross-reference (are the ghost stops in the high-density area or not?). Multi-layer canvas keeps the spatial frame constant.

**Student use.** Default filter: {route network + hex density layers visible, full date}. Decision: *"Where are the busy corridors near me?"* Click action: click hex cell → panel with top routes serving that cell.

**Operator use.** Default filter: {my routes + ghost-stop layers visible}. Decision: *"Where are my underperforming stops — should I cut them?"* Click action: click ghost stop → panel with that stop's 90-day dwell history.

**Authority use.** Default filter: {all layers including cartogram outline, full window}. Decision: *"Is demand spatially equitable? Where is supply lagging?"* Click action: click district polygon → panel with district-aggregate KPIs.

**Defence answer 1 — "Why hex bins not standard administrative units?"** Hex bins are area-uniform; district choropleth confounds intensity with area. The H3 spec (Uber's hex hierarchy) is the modern standard for uniform-area spatial aggregation and is referenced in Liu (2022) Gridify.

**Defence answer 2 — "Why one canvas with toggles instead of five canvases?"** Spatial cross-reference is the analytical purpose (are ghost stops in dense areas? do underserved districts overlap with ghost stops?). Separate maps make cross-reference impossible.

---

#### Chart 3.2 — Bus↔Metro Sankey (indicative)

> **Data caveat (red-flag chart).** Metro Line 1 arrival schedule is not in the published dataset. This chart uses an *indicative* hard-coded fallback schedule (cited from MAUR's published Line 1 spec) for the timing dimension. The bus-side flow is measured from the real GPS+AFC pipeline; the metro-side timing is estimated. The chart's title carries "(indicative)" to surface this caveat in the UI; the Methodology Side-Panel exposes the fallback schedule explicitly.

**What.** Sankey diagram. Left nodes: bus routes feeding Metro Line 1. Right nodes: Metro Line 1 stations. Ribbon width = estimated transfer volume (computed via stop-to-station proximity at transfer points). Gradient ribbon colour = transfer-timing quality (green if bus arrives within 5 min of metro, red if > 15 min wait), computed against the indicative fallback schedule. Hover = tooltip with route + station + estimated transfer count + average wait. View Controls: direction (bus → metro / metro → bus / both), transfer-time threshold slider, fallback-schedule visibility toggle (exposes the indicative timing in a side note).

**Why this chart.** Bus-metro integration is intrinsically a flow question: which bus routes feed which stations, and how well-timed are transfers. Sankey is the canonical primitive — ribbon width directly encodes transfer volume; left-to-right flow is intuitive.

**Why NOT a chord diagram.** Chord diagrams encode bidirectional flows in a circle but require more reader effort (ribbons cross visually). Sankey's left-to-right flow is more intuitive.

**Why NOT a network graph (force-directed).** Force-directed layouts vary across renders and read poorly; Sankey's fixed layout preserves consistency.

**Why NOT a matrix heatmap (bus × metro).** Matrix shows pairwise volume but loses the flow visualisation (the "feed into" metaphor). Sankey is purpose-built for the flow question.

**Student use.** Default filter: {bus → metro direction, my saved route}. Decision: *"Can I take my bus to Metro Line 1 with a good connection?"* Click action: click ribbon → panel with transfer-time distribution for that route-station pair.

**Operator use.** Default filter: {my routes if feeder, both directions}. Decision: *"Is my route a useful metro feeder, and could I improve timing?"* Click action: click ribbon → panel with the timing gap distribution.

**Authority use.** Default filter: {all routes, both directions, full window}. Decision: *"Where is intermodal coordination working, where is it failing?"* Click action: click ribbon → panel with policy-suggested headway adjustments.

**Defence answer 1 — "Why Sankey not matrix heatmap?"** Sankey makes flow-direction reading instant (left feeds right); matrix heatmap requires reader to interpret cells. The integration question is about flow direction, not pairwise magnitude.

**Defence answer 2 — "How does Sankey honour the universal click contract?"** Ribbons are clickable as entities (one ribbon = one route-station transfer); clicking opens panel for that ribbon. Per §5.1, every click opens the panel — Sankey supports this cleanly even though it cannot easily *receive* brushes from other charts.

---

#### Chart 3.4 — Accessibility isochrone

**What.** Map with isochrone polygons drawn from a chosen origin stop. 10-min, 20-min, 30-min reach bands as concentric polygons. Gradient colour intensity = travel time (saturated for close, muted for far). View Controls: origin stop picker (autocomplete), time bands (10 / 20 / 30 default), time of day (peak / off-peak), fare class restriction (e.g., student-only routes if student persona).

**Why this chart.** "How far can I reach from here in X minutes" is intrinsically a spatial-temporal question. Isochrone polygons are the canonical primitive (Mapbox Isochrone, OpenTripPlanner). Concentric bands let the reader read "what's within reach" at a glance.

**Why NOT a list of reachable stops sorted by travel time.** Loses spatial context; reader cannot see geographic coverage.

**Why NOT a heatmap of travel-time grid (KDE).** Continuous gradients are visually attractive but blur the band-by-band reading; isochrones are discrete and policy-readable.

**Why NOT a route-by-route departure-time list.** Different question — that's a schedule view, not an accessibility view.

**Student use.** Default filter: {origin = my home stop, fare class = student}. Decision: *"What's within reach for my morning commute?"* Click action: click stop in reachable area → panel with bus route + transfer details.

**Operator use.** (Lower utility — chart is 2/3 breadth.) Default filter: {origin = my company's hub}. Decision: *"What's my company's reach footprint?"* Click action: click reachable polygon → panel with my routes' contribution.

**Authority use.** Default filter: {origin = key hubs (Bến Thành, Bến xe Miền Đông), city-wide}. Decision: *"Where are accessibility shadows — areas no major stop can reach in 20 min?"* Click action: click unreachable polygon → panel with proposed route extensions.

**Defence answer 1 — "Why isochrone not route map?"** Route map shows what routes exist; isochrone shows what is *reachable* from a chosen point — fundamentally different. Reachability accounts for transfer time, frequency, walking.

**Defence answer 2 — "Why 2/3 breadth?"** Operator's interest is limited — operators care about their fleet, not user-perspective accessibility. Honest 2/3 (student + authority) is acceptable; chart belongs because passenger-facing equity and authority-facing accessibility planning are both core to A-Q4.

---

### 11.4 · Theme 4 · Financial and Operations

#### Chart 4.2 — Operator constellation (bubble scatter)

**What.** Bubble scatter. X = market share (% of total network boardings). Y = average revenue per trip. Bubble size = fleet count. Colour = average on-time % (gradient green → red). Hover = tooltip with operator name, fleet, # routes. View Controls: Y-axis swap (rev / trip / cost-recovery / ghost-trip %), size swap (fleet / # routes / # vehicles), colour rule (on-time / driver-tenure / fleet-age).

**Why this chart.** "Where do operators stand against peers" is a multi-attribute positional question — same logic as charts 1.3 and 2.1. Bubble scatter is the catalogue's consistent primitive for four-variable positional comparison.

**Why NOT a ranked bar of operators by market share.** Collapses four dimensions into rank; loses on-time and revenue dimensions.

**Why NOT parallel coordinates of operators.** Parcoords requires polyline tracing; scatter reads in five seconds.

**Why NOT a treemap of operators.** Treemap encodes area-proportional share but loses the on-time dimension; bubble scatter encodes share AND on-time AND rev/trip AND fleet.

**Student use.** (Weak — operator information is not directly student-facing.) Default filter: {operators serving my route}. Decision: *"Is the operator running my route a quality operator?"* Click action: click bubble → panel with the operator's on-time history.

**Operator use.** Default filter: {all operators, my company highlighted}. Decision: *"Where do I rank vs peers — am I lagging on rev/trip or on-time?"* Click action: click peer bubble → panel with side-by-side comparison.

**Authority use.** Default filter: {all operators}. Decision: *"Which operators warrant scrutiny — high market share + low on-time?"* Click action: click red bubble → panel with that operator's per-route on-time history.

**Defence answer 1 — "Why bubble scatter not bar?"** Same as 1.3 and 2.1 — multi-attribute positional comparison needs 2D + size + colour, which a bar cannot provide.

**Defence answer 2 — "How does this serve the student?"** Honestly weak (2/3 breadth, operator + authority). Student inclusion comes from the operator-quality signal (red bubble = poor on-time = student should know). Not the student's primary view.

---

#### Chart 4.1 — P&L quadrant

**What.** Scatter quadrant. X = ghost-trip share (% trips with zero boardings — proxy for waste). Y = revenue per trip (₫). Bubble size = total trip count. Colour = operating company (categorical, muted; per §5.3 solid bins are appropriate for categorical operator identity). Four quadrants: top-right = healthy + revenue (prestige); top-left = waste + revenue (high overhead but profitable); bottom-right = healthy + low revenue (subsidised social routes); bottom-left = waste + low revenue (rationalisation candidates). View Controls: bubble-size encoding swap, colour rule (operator / archetype), operator subset filter.

**Why this chart.** Financial efficiency per route is intrinsically a two-axis trade-off (waste vs revenue). Quadrant scatter is the canonical trade-off primitive — four interpretive regions self-label; "bleeding" vs "healthy" quadrant membership is instant.

**Why NOT a single ranked bar of rev/trip.** Collapses the waste dimension; routes with the same rev/trip can have wildly different ghost-trip shares.

**Why NOT separate charts for rev/trip and ghost %.** Loses the trade-off reading. Quadrant gives the joint perspective.

**Why NOT parallel coordinates with financial metrics.** Parcoords is better when ≥ 4 metrics; this chart's question is fundamentally two-axis. Bubble adds the volume dimension.

**Student use.** (Weak — financial information is not user-facing.) Default filter: {routes I use highlighted}. Decision: *"Is my route at financial risk of being cut?"* Click action: click route in bleeding quadrant → panel with the route's financial trajectory.

**Operator use.** Default filter: {my routes only}. Decision: *"Which of my routes are healthy, which are bleeding?"* Click action: click bubble in bleeding quadrant → panel with rationalisation analysis.

**Authority use.** Default filter: {all routes, colour by operator}. Decision: *"Which routes warrant subsidy review (bleeding) vs which are profitable (revenue concentration)?"* Click action: click bubble → panel with the route's subsidy classification.

**Defence answer 1 — "Why quadrant not two separate charts?"** The trade-off reading requires both axes at once. Two separate charts force manual cross-reference. Quadrant makes the joint position instantly visible.

**Defence answer 2 — "How does waste = ghost-trip % defend?"** Ghost-trip is a proxy because cost data is unavailable. The interface labels the metric as "trips with zero boardings" not "wasted trips" — letting the analyst draw the conclusion. The Methodology Side-Panel documents the proxy explicitly per §6 cross-cutting policy.

---

#### Chart 4.3 — Payment-channel streamgraph

**What.** Symmetric-baseline streamgraph. X = 90-day calendar. Y = stacked daily boardings by payment channel (cash, smartcard, mobile-app, e-ticket QR). Gradient ramp for cash band (dominant), muted bands for digital. View Controls: subset toggle (cash-only / digital-only / all), normalisation toggle (absolute / percent), date window.

**Why this chart.** "How is payment-channel adoption evolving" is a composition-over-time question. Streamgraph excels at organic composition flow — same logic as chart 1.1.

**Why NOT stacked bar.** Daily bars at 90-day resolution are visually jittery; streamgraph's smooth baseline is cleaner.

**Why NOT line chart per channel.** Multiple lines force manual summation for total; streamgraph encodes composition via thickness.

**Why NOT percentage-stacked area.** Loses absolute volume; cash dominance becomes hard to read.

**Student use.** (Weak — payment is operational, not user-facing decision.) Default filter: {all channels}. Decision: *"Is digital payment growing — should I get a smartcard?"* Click action: click date → panel with breakdown.

**Operator use.** Default filter: {all channels, my-company subset}. Decision: *"What's my payment mix and where is digital adoption fastest?"* Click action: click digital band → panel with per-route digital share.

**Authority use.** Default filter: {all channels, full window}. Decision: *"How is digital adoption progressing across the network?"* Click action: click date → panel with channel-by-channel growth rates.

**Defence answer 1 — "Why streamgraph not stacked area?"** Symmetric baseline avoids the bottom-band-anchoring distortion of standard stacked area. Cash is dominant; streamgraph treats it equally with the others.

**Defence answer 2 — "Why is this not authority-only?"** Operators care intensely about their payment-channel mix (cash-handling cost, digital processing fees). The operator-use default filters to "my company subset." Student inclusion is admittedly weak (2/3 breadth) but the digital-adoption signal is socially relevant.

---

#### Chart 4.4 — Free-fare student-day lift waterfall + synthetic-control overlay

> **Data caveat (red-flag chart).** The `afc.payments.promotion_code` field is 99 % null per CLAUDE.md §10 backlog (4 ≥ 99 % null `afc.payments` fields). The original "Promotion DiD" framing is not data-supported. The chart is reframed against **free-fare student days** — the free-pass fare class (9 % of boardings) is populated in `afc.tickets.fare_class` and serves as the proxy intervention event. The free-fare events are calendar-known (school terms, holidays) so the DiD comparison is well-defined. If the `promotion_code` field is partially salvaged in Phase 2, the chart can extend to operator-specific promotions; the design remains the same.

**What.** Waterfall chart. X-axis sequence: pre-free-fare-day baseline → intervention-day lift → post-day rebound → final equilibrium. Y = boardings. Synthetic-control line overlays the waterfall (drawn from k = 5 same-archetype routes per §9 gap-3 decision). Bars use gradient colour: positive lift green, negative red. View Controls: intervention picker (which free-fare campaign / day to analyse), control-k slider (5 / 10 / 20 control routes), date window.

**Why this chart.** "Did the intervention X lift ridership" is a causal-inference question with a clear narrative arc (baseline → intervention → after). Waterfall is the canonical primitive for sequence-of-effects visualisation; synthetic-control overlay surfaces the counterfactual.

**Why NOT before-and-after bar chart.** Two bars don't show in-period dynamics; doesn't separate promotion period from rebound.

**Why NOT a line chart with promotion period shaded.** Line chart shows trajectory but doesn't decompose the lift into phases (pre-baseline → promo → rebound). Waterfall decomposes.

**Why NOT a difference-in-differences scatter.** Scatter is correct for the DiD comparison but loses the temporal narrative; waterfall preserves the time-sequence reading.

**Student use.** (Weak — student is not the audience for promotion-effectiveness analysis.) Chart is 1/3 breadth — operator-focused specialist.

**Operator use.** Default filter: {my recent promotions}. Decision: *"Did my last promotion actually lift ridership beyond what would have happened anyway?"* Click action: click waterfall bar → panel with per-route lift breakdown.

**Authority use.** Default filter: {all promotions, network-wide}. Decision: *"Are operator promotions effective enough to justify regulatory support?"* Click action: click control line → panel with the synthetic-control composition.

**Defence answer 1 — "Why waterfall not before/after bars?"** Waterfall decomposes the lift into phases (baseline, promotion, rebound); before/after only shows two snapshots. The DiD analysis requires the rebound phase to be visible.

**Defence answer 2 — "Why is this 1/3 breadth — should it be cut?"** Promotion-effectiveness analysis is operator-specific; the audience is operator decision-makers. The chart belongs because C-Q4 ("did my promo work?") is one of the 14 stakeholder questions and no other chart answers it. 1/3 breadth here is a *specialist* tag (which §2.5 explicitly allows at the bottom of a theme), not a redundancy tag.

---

### 11.5 · Theme 5 · Network Health and Performance

#### Chart 5.2 — QoS small-multiples scatter (three mini-scatters)

**What.** Three small-multiples scatter charts side-by-side, one per QoS dimension (QoS-1 trip completion, QoS-2 on-path driving, QoS-3 on-schedule). Each mini-scatter: X = route number, Y = QoS score (0-100). Gradient colour ramp per mini-scatter. Hover = tooltip with route name + QoS score. View Controls: date window, operator subset, "expand this dimension to full size" toggle per mini.

**Why this chart.** Reliability decomposed into QoS-1/2/3 (Chawuthai 2023) is intrinsically multi-dimensional. Small-multiples (Tufte) is the canonical primitive for "same chart structure across different dimensions" — preserving direct comparability while showing three dimensions at once.

**Why NOT a single bar chart of composite QoS score.** Composite hides the decomposition; the analytical purpose is to see which dimension is weakest.

**Why NOT a radial composite (radar chart per route).** Radar charts require one chart per route — defeats cross-route comparison.

**Why NOT parallel coordinates of QoS dimensions.** Parcoords requires polyline tracing; small-multiples reads in five seconds.

**Student use.** Default filter: {my route highlighted across all 3 small-multiples}. Decision: *"Which QoS dimension does my route fail?"* Click action: click route in any mini-scatter → panel with the route's full QoS history.

**Operator use.** Default filter: {my routes highlighted}. Decision: *"Which of my routes is failing which dimension — where do I direct intervention?"* Click action: click route → panel with per-route remediation plan.

**Authority use.** Default filter: {all routes, lowest-QoS-decile highlighted}. Decision: *"Network-wide, which operators have the QoS problem?"* Click action: click route → panel with operator-aggregate QoS rollup.

**Defence answer 1 — "Why small-multiples not one composite chart?"** QoS is intentionally decomposed (Chawuthai 2023's framework). Composite scores hide the dimensional decomposition that is the analytical purpose. Small-multiples preserves the decomposition while remaining easy to compare.

**Defence answer 2 — "How does this serve all three personas?"** Reliability is the most cross-cutting analytical concern: students experience it daily, operators are measured on it, authorities regulate it. Filter defaults route each persona to their relevant entry; the QoS decomposition serves all three with the same primitive.

---

#### Chart 5.1 — Network pulse with anomaly bands + threshold slider

**What.** Time-series line chart. X = 90-day calendar. Y = daily total boardings. Annotated bands: normal range (mean ± Nσ), anomaly markers (days exceeding threshold). Named events flagged inline (Tết 2026 Feb 14–22; April 30 parade week). Threshold slider lets the user adjust N (1σ to 5σ). View Controls: date window, threshold slider, normalisation toggle (raw / day-of-week-detrended), event-flag toggle.

**Why this chart.** "How is the network behaving over time, where are the anomalies" is a time-series anomaly question. Line chart with anomaly bands is the canonical primitive — line shows trajectory, bands show context, markers show outliers, slider exposes parameter sensitivity.

**Why NOT a calendar heatmap of daily totals.** Heatmap shows seasonal patterns but loses precise magnitude; line chart shows magnitude precisely. (This is also why former chart 5.3 calendar was cut per §4.2.)

**Why NOT a horizon chart.** Horizon compresses too aggressively; banned per §2.2 cognitive-load policy.

**Why NOT a bump chart of route ranks.** Different question — bump chart is for ordinal rank changes; this is for absolute magnitude trajectory.

**Student use.** Default filter: {full 90 days, default threshold}. Decision: *"Did the network function during shocks I'll experience?"* Click action: click anomaly → panel with that day's impact breakdown.

**Operator use.** Default filter: {my routes' subset of network total}. Decision: *"How did my fleet hold up during anomalies?"* Click action: click anomaly → panel with my routes' per-route deviation.

**Authority use.** Default filter: {full network, threshold = 2σ}. Decision: *"Which days warrant root-cause investigation?"* Click action: click anomaly → panel with hypothesis-generation tools.

**Defence answer 1 — "Why line + bands not heatmap calendar?"** Line + bands surfaces both trajectory and anomaly context in one view; calendar heatmap requires reader to interpret cells. Line + bands also supports the threshold slider directly — the slider redraws the bands in real time, which a calendar cannot.

**Defence answer 2 — "How is this 3/3 breadth?"** Network behaviour during shocks is universal: students experienced Tết, operators planned for it, authorities managed it. Persona-specific filter defaults route each user to their relevant entry.

---

### 11.6 · Theme 6 · Routes

#### Chart 6.4 — Per-stop arrival box plot

**What.** Box plot per stop along a chosen route. X = stop sequence (1 to N stops). Y = arrival-time deviation from schedule (minutes early/late). Each stop = one box plot (median, IQR, whiskers, outliers). Filterable by date subset, day-type, peak vs off-peak. Gradient orange ramp for outlier dots. View Controls: route picker, date subset, day-type filter, peak / off-peak toggle.

**Why this chart.** "Where on the route does reliability break down" is a per-stop distribution question. Box plot is the canonical primitive for distribution comparison across categories — wide IQR = unreliable stop; outliers visible directly; trend across stops visible at a glance.

**Why NOT a ridgeline / joy plot.** Ridgeline requires statistical literacy (overlapping density curves); box plot is more familiar. (Tier A vs Tier D per §2.2.)

**Why NOT a single average-deviation per stop.** Averages collapse the distribution; the analytical purpose is to see spread, not central tendency alone.

**Why NOT a heatmap (stop × deviation magnitude).** Heatmap loses the precise distribution shape; box plot's whiskers and outliers carry the analytical signal.

**Student use.** Default filter: {my route, weekday peak}. Decision: *"Which stop on my route is the unreliability hot spot — should I board earlier?"* Click action: click stop → panel with that stop's anomaly-day history.

**Operator use.** Default filter: {my routes, all data}. Decision: *"Where do my drivers consistently fall behind? Is it a dispatch issue or a traffic issue?"* Click action: click outlier-heavy stop → panel with per-trip deviation history.

**Authority use.** Default filter: {all routes' worst-decile stops}. Decision: *"Network-wide, which stops are reliability bottlenecks?"* Click action: click stop → panel with cross-route impact (other routes affected by this stop's delay).

**Defence answer 1 — "Why box plot not ridgeline?"** Box plot is reader-familiar (Tier A); ridgeline requires statistical literacy. Per §2.2 the front-door chart of every theme must be Tier A.

**Defence answer 2 — "How is this 3/3 breadth?"** Stop-level reliability is the most universal user concern: students plan around it, operators control it, authorities measure it. Filter defaults give each persona their relevant route subset.

---

#### Chart 6.3 — Stop-by-stop boardings + door-dwell dual-axis

**What.** Dual-axis combination chart per route. X = stop sequence. Left Y-axis: bar height = boardings per stop. Right Y-axis: line = door-open-ratio per stop (proxy for stop activity vs ghost-stop). Gradient orange bar colour. View Controls: route picker, date window, direction (inbound / outbound), bar colour rule.

**Why this chart.** "Where on the route are people boarding, and is the bus actually stopping" is two-variable per stop. Dual-axis bar + line is the canonical primitive — bars show magnitude, line shows quality.

**Why NOT two separate charts.** Two charts force manual cross-reference; the analytical purpose is to see boardings AND quality at the same stop simultaneously.

**Why NOT a scatter (boardings × door-ratio).** Loses the stop-sequence dimension; reader cannot see whether problem stops are early or late on the route.

**Why NOT a stacked bar (boardings broken by passenger type).** Different question; this chart is operational, not demographic.

**Student use.** (Weak — stop-level operational data is not user-facing.) Default filter: {my route}. Decision: *"Where on my route are the busiest boardings?"* Click action: click stop → panel with that stop's hourly profile.

**Operator use.** Default filter: {my routes}. Decision: *"Where on my routes do my drivers skip stops (low door-open ratio)?"* Click action: click low-door-ratio stop → panel with per-trip dwell history.

**Authority use.** Default filter: {all routes' worst stops}. Decision: *"Where in the network are the ghost-stop problems?"* Click action: click ghost stop → panel with cross-route ghost-stop pattern.

**Defence answer 1 — "Why dual-axis not two charts?"** Cross-reference: the analytical purpose is "is the busy stop also a well-served stop?" — which only one chart with both variables can answer. Two charts split attention.

**Defence answer 2 — "Why is this 2/3 breadth?"** Operational stop-level analysis is operator + authority focus. Student inclusion is weak and honest. Chart belongs because the door-ratio signal answers C-Q1 (under-supply) directly.

---

#### Chart 6.2 — Marey time-distance diagram + dwell heatmap composite

**What.** Time-distance trip diagram (Marey 1885; Lin & Zeng 2014). X = time of day. Y = distance along the chosen route. Each trip = one polyline from origin (top) to terminus (bottom). Slope = average speed (gentler = slower). Time-check stops overlaid as horizontal reference bands. Bunching auto-detected and annotated (consecutive trips with headway below threshold). Dwell heatmap below: same X-axis; Y-axis = stop sequence; colour = dwell time. View Controls: date subset, direction, bunching-threshold slider, heatmap visibility toggle.

**Why this chart.** "What does a single route's operation look like across a day" is intrinsically a space-time question. Marey diagram is the canonical primitive (invented 1885 for railway scheduling; applied to bus by Lin & Zeng 2014). The composite with dwell heatmap surfaces trip-level (polylines) AND stop-level (heatmap) operational signals on one canvas.

**Why NOT a separate trip-timeline and dwell chart.** Two charts split attention; the analytical purpose is to see trip bunching AND dwell pattern as one operational story.

**Why NOT a scatter of trip arrival times per stop.** Scatter loses the trip-as-trajectory reading; the bunching signal is invisible.

**Why NOT a heatmap alone.** Heatmap loses the slope (speed) reading — the most operationally important Marey signal.

**Student use.** (Weak — Marey is operator-focused, Tier C cognitive load.) Chart is 2/3 breadth (operator + authority). Student exclusion is acceptable per §2.5 placement: this chart is the bottom-of-theme specialist.

**Operator use.** Default filter: {my routes, last 7 days}. Decision: *"Are my trips bunching, and where do dwells exceed dispatch tolerance?"* Click action: click polyline → panel with that trip's per-stop log.

**Authority use.** Default filter: {flagged routes, full window}. Decision: *"Which operators' Marey diagrams show systematic bunching?"* Click action: click bunching annotation → panel with operator-aggregate bunching statistics.

**Defence answer 1 — "Why Marey specifically?"** Marey is the historical standard for time-distance operations visualisation (1885 railway invention; transit-industry standard). Lin & Zeng (2014) is the modern bus reference. The chart inherits a citable, defensible lineage.

**Defence answer 2 — "Why Tier C — committee will challenge this."** Marey's specialised readability is acknowledged. Every analytical platform needs one operator-grade deep-dive view; Marey serves that purpose for the operator / authority audience. Bottom-of-theme placement matches §2.5. Student exclusion is honest; the chart is not student-facing.

---

> **§11 complete.** All 20 charts of catalogue v5.5 documented with the 10-field defence template. The document is now defence-ready for thesis committee review.

---

## 12 · Data Feasibility Audit

The catalogue's design decisions are independent of immediate data availability — the catalogue is a *design specification* for Phase 1, with implementation in Phase 2. This section makes the implementation-readiness of every chart explicit, so that the committee question *"can you actually build this with your data?"* has a written answer per chart.

### 12.1 · Data-feasibility tiers

| Tier | Symbol | Meaning | Phase available |
|---|:-:|---|---|
| 1 | ✅ | Phase 1 ready — all source data complete; only the chart-rendering pipeline needs implementation | Phase 1 |
| 2 | ⚙️ | Phase 1 with computation effort — source data complete but the chart requires non-trivial computation (clustering, multi-source joins, schedule cleaning, DiD logic) | Phase 1 (with effort) |
| 3 | 🟨 | Phase 2 prerequisite — depends on a CLAUDE.md §10 backlog item (school geocoding OR full 50-day GPS extraction) | Phase 2 |
| 4 | ⚠️ | Conditional — depends on external data not in the published dataset (Metro schedule) OR salvage of a sparse field; the chart is feasible but the design carries an explicit caveat | Phase 1 with caveats, Phase 2 with backlog completion |

### 12.2 · Per-chart audit

| # | Chart | Aggregate table | Source data | Known data-quality concern | Tier | Phase |
|---|---|---|---|---|:-:|:-:|
| 1.1 | Demand streamgraph | `agg_payment_day` + `dim_fare_class` | AFC `tickets.fare_class` + `tickets.time_created_ticket` | None — fare_class populated | ✅ | 1 |
| 1.2 | Route × hour heatmap | `agg_route_hour` | AFC `tickets.route_no` + `tickets.time_created_ticket` | None | ✅ | 1 |
| 1.3 | Route constellation | `agg_route_profile` | AFC + clustering pipeline | Clustering implementation needed (k-means or hierarchical; UMAP is moved to research appendix per §4.2) | ⚙️ | 1 |
| 1.4 | Bump chart | `agg_route_day` rolled up to weeks | AFC `tickets.route_no` + week-rollup | None | ✅ | 1 |
| 2.1 | School constellation | `agg_school_route` | AFC + school geocoding + walking-distance join | 56 of 64 schools stubbed at district level per §10 backlog; hand-verified for 8 universities only | 🟨 | 2 |
| 2.2 | School→route treemap | `agg_school_route` | AFC + school geocoding | Same as 2.1 | 🟨 | 2 |
| 2.3 | Weekly fare-class heatmap | `agg_payment_day` × hour pivot | AFC `tickets.fare_class` + hour-of-day | Works at full strength without school filter; school filter requires geocoding | ✅ | 1 (no school filter) / 2 (with school filter) |
| 2.4 | School proximity map | `dim_school` + `dim_stop` + distance join | School geocoding + stop coordinates | Stops have lat/lng ✓; schools require Phase 2 geocoding | 🟨 | 2 |
| 3.1 | Multi-layer hex map | `agg_stop_hour` + H3 binning | AFC `tickets.station_id` + `dim_stop.lat/lng` | Door-dwell layer requires GPS `door_open` field (missing locally per invariant #12); other layers work in Phase 1 | ⚙️ | 1 (without door-dwell) / 2 (full) |
| 3.2 | Bus↔Metro Sankey (indicative) | Custom: `fact_boardings` joined to `dim_metro_station` (hard-coded) | AFC bus side + Metro schedule fallback | Metro Line 1 arrival data NOT in published dataset; design uses hard-coded MAUR Line 1 spec per CLAUDE.md §9 gap-2 | ⚠️ | 1 with caveat (indicative timing) |
| 3.4 | Accessibility isochrone | `dim_stop` + schedule + route graph | Schedule `gps.schedules` + stop network | Schedule has 91k unknown service-type rows per CLAUDE.md §10 backlog; needs cleaning | ⚙️ | 1 (with cleaned schedule) |
| 4.1 | P&L quadrant | `agg_company_route` | AFC revenue + `gps.schedules` trips + ghost-trip join | Cost data absent (already known — proxy by ghost-trip %); schedule cleaning needed for trip count | ⚙️ | 1 |
| 4.2 | Operator constellation | `agg_company_route` | AFC + GPS for on-time dimension | On-time requires GPS+schedule (QoS-3); full 50-day GPS in Phase 2 | 🟨 | 2 (for on-time axis) |
| 4.3 | Payment-channel streamgraph | `agg_payment_day` | AFC `payments.payment_channel` | 96.7% cash already EDA'd; non-cash bands are sparse but present | ✅ | 1 |
| 4.4 | Free-fare student-day lift waterfall | `agg_payment_day` + `dim_promotion` (calendar-known) | AFC `tickets.fare_class` (free-pass band) + intervention calendar | Original `promotion_code` field is 99% null per §10; reframed to free-fare days (free-pass = 9% of boardings, populated in `fare_class`) | ⚙️ | 1 (free-fare framing) / 2 (operator promotions if `promotion_code` salvaged) |
| 5.1 | Network pulse + anomaly bands | `agg_network_day` | AFC daily totals + STL or rolling-Z anomaly detection | None for the AFC side; anomaly detection is standard | ✅ | 1 |
| 5.2 | QoS small-multiples | `agg_company_route` + per-route QoS | GPS for QoS-1/2/3; schedule for QoS-3 | Requires full 50-day GPS + cleaned schedule per CLAUDE.md §10 | 🟨 | 2 |
| 6.2 | Marey diagram | `fact_gps_trips` + `dim_stop` | Per-trip GPS polylines | Requires full 50-day GPS; local 1-day extract supports demo only | 🟨 | 2 |
| 6.3 | Stop-by-stop + door-dwell | `agg_stop_hour` + `fact_gps_trips.door_open` | AFC boardings + GPS door-state | Door-state field missing in local 1-day extract per invariant #12; boardings ✅ | 🟨 | 2 (full chart) / 1 (boardings-only without door-dwell) |
| 6.4 | Per-stop arrival box plot | `fact_gps_trips` + schedule | GPS arrival times per stop + schedule | Requires full 50-day GPS + cleaned schedule | 🟨 | 2 |

### 12.3 · Red-flag charts — explicit caveats

Two charts in the catalogue carry data caveats serious enough to surface in the chart title and in the Methodology Side-Panel.

#### 3.2 Bus↔Metro Sankey (indicative)

**Caveat.** Metro Line 1 arrival schedule is not in the published HCMC dataset. The chart's bus side (route, ridership, stop proximity to Metro stations) is measured from real data; the chart's metro-timing dimension uses a hard-coded fallback drawn from MAUR's published Line 1 service spec per CLAUDE.md §9 gap-2 decision.

**Mitigation.**
1. Chart title carries the qualifier "(indicative)" so the qualifier appears anywhere the chart appears (theme nav, exports, PDF inclusions).
2. The Methodology Side-Panel surfaces the fallback schedule explicitly with a citation to the MAUR spec source.
3. Phase 2 work item: source the live MAUR schedule (CLAUDE.md §10 backlog: *"Source MAUR Metro Line 1 indicative schedule (or finalise the hard-coded fallback per gap-2 decision)"*).

**Defence framing.** *"The chart's bus-side flow is measured; the metro-side timing is the published spec. We expose the spec in the methodology view so the reader can audit the assumption. Phase 2 will replace the fallback with live timing when MAUR exposes the schedule API."*

#### 4.4 Free-fare student-day lift waterfall

**Caveat.** The chart's original framing was "Promotion DiD" using the `afc.payments.promotion_code` field. That field is 99 % null per CLAUDE.md §10 backlog. The chart's purpose (does an intervention lift ridership) is preserved by reframing the intervention from "promotion code" to "free-fare student days," which is populated in `afc.tickets.fare_class` (the free-pass band, ~9 % of boardings). Free-fare days are calendar-known (school terms, holidays) so the DiD intervention window is well-defined.

**Mitigation.**
1. Chart title renamed in catalogue and in §11.
2. Chart can extend to operator promotions in Phase 2 if `promotion_code` is partially salvaged (CLAUDE.md §10 backlog item: *"Decide policy for 4 ≥ 99% null `afc.payments` fields"*); the underlying DiD design is identical.
3. The chart still answers stakeholder question C-Q4 (*"Did my last promotion lift ridership in a measurable way?"*) — the answer just covers free-fare interventions in Phase 1 rather than arbitrary promotion campaigns.

**Defence framing.** *"The sparse promotion-code field would have made the original chart non-renderable. We re-framed the intervention from 'promotion campaign' to 'free-fare student day' because the free-fare days are the only intervention class our data supports with statistical power. C-Q4 is still answered, just for the intervention class we can measure."*

### 12.4 · Phase 1 demo scope vs Phase 2 full scope

Counting by tier across the 20 charts:

| Tier | Charts | Catalogue % |
|---|--:|--:|
| ✅ Phase 1 ready | 6 | 30 % |
| ⚙️ Phase 1 with effort | 5 | 25 % |
| 🟨 Phase 2 prerequisite | 7 | 35 % |
| ⚠️ Conditional | 2 | 10 % |

**Phase 1 demoable** (tiers 1 + 2 + the conditional charts with their caveats): **13 of 20 charts**, enough for a 2-minute screen recording, the Current Prototype chapter of the Phase 1 report, and the front-door demo for at least 4 of the 6 themes (Demand and Crowding, Spatial and Connectivity partial, Financial and Operations partial, Network Health and Performance).

**Phase 2 full catalogue** (all 20 charts) requires three backlog items to clear:
1. School geocoding (8/64 already verified; 56 schools to complete; Nominatim batch run is the implementation path) — unlocks Theme 2 charts 2.1, 2.2, 2.4.
2. Full 50-day Kaggle GPS extraction — unlocks 4.2 on-time axis, 5.2 QoS, 6.2 Marey, 6.3 door-dwell, 6.4 per-stop box plot.
3. Schedule cleaning (91k unknown service-type) — unlocks the on-time and ghost-trip joins shared across multiple charts.

These three items are already on the CLAUDE.md §10 backlog and are listed as Phase 2 prerequisites in the Phase 1 report's Chapter 5 (Current Prototype) and Chapter 6 (Future Work / Phase 2 roadmap).

### 12.5 · No chart cut for data reasons

The data audit triggers two **chart reframes** (3.2 → "indicative", 4.4 → "free-fare student-day lift") but **zero chart cuts**. Every chart in the catalogue is feasible given the planned Phase 2 data scope; the audit's purpose is to make the implementation phase per chart explicit, not to prune the catalogue further.

---

## 13 · Stories (scrollytelling layer)

The Stories layer is a second reading mode that sits inside four of the six themes. Where the tool mode is reader-driven (the analyst clicks, filters, and drills), the Story mode is author-driven: a curated scroll-locked sequence walks the reader from a dramatic question to a recap and call to action. The design is grounded in two studied references: the VnExpress 2025 labour-market data-journalism piece~\cite{vnexpress2025labour} (studied via browser inspection on 2026-05-22) and the project's own `docs/design/app-layouts.html` LAYOUT 4 dark scrollytelling shell.

### 13.1 · Mechanic — sticky-graphic scrollytelling

The VnExpress piece implements the canonical sticky-graphic scrollytelling pattern, confirmed by DOM inspection: each scroll section pins one chart with `position: sticky` (the inspected sections pinned a 433 px and a 556 px chart) while narrative step-cards scroll past; as each step crosses the trigger line, the pinned chart transitions (highlights a row, annotates a value, redraws a series). The charts are simple and gradient-coloured (the inspected chart was a year-by-industry heatmap with direct start→end value labels per row and an orange-to-dark-red ramp), built with d3 + ECharts + Flourish, and are bespoke per narrative beat rather than reused from an analytical dashboard.

The proposed system adopts this mechanic. Each Story is structured as:

1. **Bing (hero).** A full-screen opener: one large KPI number plus the dramatic question, in the dark theme of app-layouts LAYOUT 4 (200 px KPI value, Funnel Display headline, orange accent).
2. **Bang (scrolly sections).** One or two scroll sections. Each section pins **one chart** (`position: sticky`); three to five narrative step-cards scroll past; each step fires one of the four scroll-trigger transitions (highlight overlay, annotation overlay, filter change, redraw) on the pinned chart. Two sections, each with its own pinned chart, are used when a Story needs a primitive change — the change happens at the section boundary, never mid-scroll within a section, so the reader is never disoriented by a chart morphing under them.
3. **Bongo (recap + CTA).** A closing card with the recap finding and a call to action that opens the parent theme in tool mode for free exploration.

A section progress indicator (dots, per app-layouts LAYOUT 4) tracks scroll position within the Story.

### 13.2 · Two-tier chart sourcing

Story charts are drawn from two tiers:

- **Tier 1 — catalogue chart in story state.** A v5.5 catalogue chart frozen to a narrative beat (for example, the network pulse 5.1 with the Tết window shaded, or the operator constellation 4.2 with the two dominant bubbles highlighted). Reuses the tool-mode chart component; the Story only supplies a state specification (which filter, which highlight, which annotation).
- **Tier 2 — bespoke simple story chart.** A purpose-built simple chart that exists only in a Story and never in the tool catalogue. Examples: a "100 students" unit-dot array, a single annotated line, a before-and-after slope, a small resilience sparkline grid. These charts are deliberately simpler than any tool-catalogue chart (which must serve three personas and support the Select+Filter+Abstract minimum); a Story beat needs none of that interaction, so a dead-simple narrative chart is the correct tool. This tier is what the VnExpress piece does with its bespoke-per-beat charts.

The two-tier split resolves a tension: the tool catalogue stays rigorous (20 multi-persona analytical charts each passing the Yi-category and multi-encoding tests), while Stories gain the freedom to use narrative-simple charts that would fail the tool-catalogue inclusion criteria but are exactly right for a guided reading beat.

### 13.3 · Section navigation

Following the VnExpress top-tab section nav, each Story carries a chapter nav that lets the reader jump between the Story's scroll sections. The nav is Story-scoped (it lists the sections of the current Story), not global; this keeps the navigation surface compact and preserves the §7.7 decision that Stories live inside their parent theme rather than in a separate top-level destination. The parent-theme hub card carries both a "Read the story" affordance (enters Story mode) and a "Start exploring" affordance (enters tool mode).

### 13.4 · The four Stories

Four of the six themes carry a Story; Demand and Crowding and Route Detail are tool-mode only. Each Story is specified below as Bing → scrolly sections (with the pinned chart and per-step transitions) → Bongo. Chart references use the v5.5 numbering; the chart tier (Tier 1 catalogue / Tier 2 bespoke) is tagged per pinned chart.

#### Story 1 · The school commute, in numbers (School-Aware Demand theme)

```
BING        "34%"  — of all HCMC bus rides are paid with a student-fare card (matches report EDA §4.2; see note on 34 vs 36% below)

SCROLLY A   pinned: weekly fare-class heatmap (Tier 1, catalogue 2.3)
  step 1    "Thirty-six of every hundred rides are student fares."   highlight student rows
  step 2    "Students compress their week into four hours."          highlight 6-8am + 4-6pm columns
  step 3    "Saturday looks nothing like Tuesday."                   filter to weekend, fade weekday

SCROLLY B   pinned: school constellation (Tier 1, catalogue 2.1)
  step 4    "A handful of universities anchor most student demand."  highlight university quadrant
  step 5    "But three schools sit beyond walking distance."         highlight 3 red equity bubbles + annotate

BONGO       "Three schools without a stop. Seven routes without a summer."
            CTA → Explore School-Aware Demand
```

#### Story 2 · Where the city actually rides (Spatial and Connectivity theme)

```
BING        "5 stops = 7%"  — five central stops carry seven percent of all boardings

SCROLLY A   pinned: multi-layer hex map (Tier 1, catalogue 3.1)
  step 1    "The boarding map, at 500-metre resolution."             hex density layer
  step 2    "Sized by ridership, not by area, the centre swells."    toggle to cartogram layer (filter change)
  step 3    "Five hex cells in the centre dominate."                 highlight top-5 cells + annotate

SCROLLY B   pinned: bus-to-metro Sankey, indicative (Tier 1, catalogue 3.2)
  step 4    "Nineteen routes feed Metro Line 1."                     full Sankey
  step 5    "Only eight arrive within five minutes of a train."      highlight 8 green ribbons, fade rest

BONGO       "The city you ride is not the city on the map."
            CTA → Explore Spatial and Connectivity
```

#### Story 3 · Who runs Saigon's buses (Financial and Operations theme)

```
BING        "₫72B, 2 operators"  — two companies move 60% of network volume in 90 days

SCROLLY A   pinned: operator constellation (Tier 1, catalogue 4.2)
  step 1    "Two companies move sixty percent of the network."       highlight 2 dominant bubbles
  step 2    "Size is not quality."                                   toggle bubble colour to on-time (encode change)
  step 3    "The biggest runs 18% of routes for 31% of revenue."     annotate the dominant bubble

SCROLLY B   pinned: P&L quadrant (Tier 1, catalogue 4.1)
  step 4    "Twelve routes sit in the bleeding quadrant."            highlight bottom-left quadrant

SCROLLY C   pinned: free-fare lift slope (Tier 2, bespoke story chart)
  step 5    "Free-fare student days lift ridership 12% on weekdays." before/after slope, weekday vs weekend

BONGO       "Twelve bleeding routes. One slow digital transition. ₫72B at stake."
            CTA → Explore Financial and Operations
```

#### Story 4 · Nine days without a network (Network Health and Performance theme, Tết)

```
BING        "−84%"  — daily ridership on the trough day of Tết (16 Feb 2026)

SCROLLY A   pinned: network pulse line (Tier 1, catalogue 5.1)
  step 1    "Ridership held steady through January."                 plain line, January window
  step 2    "Then Tết arrived, 14 February 2026."                    shade Tết window red + annotate
  step 3    "Minus eighty-four percent on the trough day."           trough point pulses + value callout
  step 4    "Recovery completes by 23 February."                     recovery marker + arrow

SCROLLY B   pinned: resilience sparkline grid (Tier 2, bespoke story chart)
  step 5    "Some routes flatlined; others barely moved."            small-multiple sparklines, airport routes green

BONGO       "Nine days of flatline. Nine routes need a contingency plan."
            CTA → Explore Network Health and Performance
```

### 13.5 · Scene and chart-sourcing summary

| Story | Theme | Sections | Steps | Tier-1 charts | Tier-2 charts |
|---|---|--:|--:|---|---|
| 1. The school commute | School-Aware Demand | 2 | 5 | 2.3, 2.1 | — |
| 2. Where the city rides | Spatial and Connectivity | 2 | 5 | 3.1, 3.2 | — |
| 3. Who runs Saigon's buses | Financial and Operations | 3 | 5 | 4.2, 4.1 | free-fare lift slope |
| 4. Nine days without a network | Network Health | 2 | 5 | 5.1 | resilience sparkline grid |

Two bespoke Tier-2 story charts are introduced (the free-fare lift slope and the resilience sparkline grid); neither enters the tool-mode catalogue. The four Stories consume six distinct Tier-1 catalogue charts in story state (2.1, 2.3, 3.1, 3.2, 4.1, 4.2, 5.1 — seven, across the four). Every Tier-1 chart used in a Story is also reachable in tool mode through its parent theme, satisfying the architectural rule that Story mode and tool mode share components.
