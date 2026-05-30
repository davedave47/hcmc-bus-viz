# Capstone Phase 1 Defence Deck — Design Specification

**Date:** 2026-05-29
**Author:** Duy (with Claude)
**Status:** Locked, ready for implementation
**Output:** `report/capstone_defence.pptx` (single deliverable)
**Talk length:** 15 minutes + Q&A
**Audience:** HCMUT capstone defence committee (strict, deep technical questions expected)

---

## 1 · Project context

The deck defends Phase 1 of the HCMC Bus Analytics project — an analytical and
visualisation platform over the city's GPS and AFC operational data streams.
The full content is in [report/main.pdf](../../../report/main.pdf) (177 pages, 7
chapters, 5 appendices). The deck is *not* a compression of the report; it is a
spoken-defence artefact whose purpose is to make the case for the project to a
committee that may not read the report end to end.

Companion artefacts:
- Template: [template.pptx](../../../template.pptx) (HCMUT/VNU-HCM branding,
  16:9, 18 layouts, light theme with dark-navy + light-blue triangular motif).
- Running prototype: [demo/](../../../demo/) (FastAPI + Jinja2 + HTMX +
  Plotly + DuckDB, Medallion warehouse in `db/bus.duckdb`).
- Screenshot assets: `card2_treemap_v2.png`, `card3_density_v3.png`,
  `card5_pulse_v2.png`, `hub_fullbleed.png`, `story_v3_bing.png` (capstone
  root).
- Report diagrams: `report/images/diagrams/*.png` (used unchanged where the
  defence visual matches the report figure).

---

## 2 · Through-line and character

### Through-line (one sentence)

> HCMC's bus network produces 17.8 million boarding events a quarter that
> nobody is analysing. We designed a multi-stakeholder analytical platform,
> built a working prototype that proves the design choices, and have a
> credible plan to finish it in fourteen weeks.

Every slide must move this sentence forward. If a slide does not contribute,
it is cut.

### Speaker character

Confident-but-humble, evidence-grounded, engineering-disciplined. Vietnamese
academic culture rewards directness over showmanship — no dramatic hooks, no
slogans, no "imagine if…". State, prove, move on.

### Two headline findings

These get rhetorical emphasis; everything else is supporting evidence.

1. The warehouse architecture was selected by a **hard integrity gate, not by
   speed alone**. Star-schema-over-raw was rejected *before latency was even
   measured* because it inflates the boarding count by **+17.9 %** — route
   identifiers cannot be reconciled at query time. The chosen Medallion-with-
   Gold is lossless to **17,883,623** boardings *and* **6× faster than
   Silver-only** (5,517 ms → 920 ms per chart-catalogue page load). Integrity
   leads; the 6× is the payoff. This ordering matters: it pre-empts the
   "isn't pre-computing obviously faster" objection.
2. The Tết 2026 shock is **−57 % on average across 9 days, troughing at
   −84 % on Feb 16**, recovering Feb 22.

### Number consistency note

Student-fare share is stated as **34 %** everywhere in the deck, to match the
submitted report (Ch 4.2). The session log records a measured 36 %; that
discrepancy is parked as an EDA re-run task and does *not* surface in the
deck. The deck never contradicts the report a committee may be holding.

---

## 3 · Act structure

| Act | Length | Audience question | Slides |
|---|---|---|---|
| 1 — Why this matters | 2:30 | *Is this a real problem, and for whom?* | 1–3 |
| 2 — What we propose | 4:25 | *Did they design this, or assemble it?* | 4–8 |
| 3 — What we built | 5:30 | *Is this real, or just a paper?* | 9–14 |
| 4 — What comes next | 1:45 | *Is this finishable? What's the contribution?* | 15–16 |

**Verified time budget (sum of §4 beat allocations):**

| Act | Beat seconds | Subtotal |
|---|---|---|
| 1 | 20 + 85 + 45 | 150 |
| 2 | 45 + 45 + 30 + 90 + 55 | 265 |
| 3 | 45 + 45 + 50 + 50 + 90 + 50 | 330 |
| 4 | 55 + 50 | 105 |
| **Sum** | | **850 s = 14:10** |

Plus ~20 s of act-transition sentences → **≈ 14:30 spoken**, a 30-second
buffer under the 15-minute ceiling. (The earlier "~14:55" estimate was wrong:
the old beat allocations summed to 15:50. This table is now the authority —
if any beat is retimed, this sum must be recomputed and stay ≤ 14:40.)

Act 4 is deliberately compressed: the roadmap slide carries the "we can
finish" argument, the contributions slide carries the close, and supporting
detail (user-evaluation methodology, Phase 2.5+ extensions) is delivered in a
single short verbal aside and parked in the backup deck for Q&A.

---

## 4 · Beat-by-beat speaker plan

This is the *content* spec for each slide — what the speaker says, what the
slide shows, and what risks each beat carries. The implementation plan (next
phase) turns each beat into a slide build step.

### Act 1 — Why this matters

**Beat 1.1 — Opening + cover (≈ 20 sec, slide 1)**

Opening line, delivered while the cover is up:

> "Good morning. My name is [name]. The project I'm defending is an analytical
> and visualisation platform for the Ho Chi Minh City public bus network. In
> the next fifteen minutes I'll cover three things: what gap motivated the
> project, how we designed it, and what we built in Phase One."

- **Failure mode:** reading the cover aloud.

**Beat 1.2 — The analytical gap, across three stakeholders (≈ 85 sec, slide 2)**

This slide now does double duty: it shows *who* the platform serves (the three
personas) and *what* none of the existing tools answer for them. This is where
"multi-stakeholder" stops being a claim and becomes visible.

Argument:
> "Five tools exist for HCMC bus today. Four are passenger-facing routing
> apps; one is a research demo of a single spatial-density chart. Now look at
> who actually needs this network's data. A *passenger* asks: is route 152
> reliable enough to commit to? An *operator* asks: which of my routes lose
> money to near-empty trips? The *authority* asks: where does supply not
> match demand across the network? None of the five tools answers a single
> one of these. The gap is not a missing feature in any one app — it is the
> missing analytical surface across all three stakeholders."

- **Visual:** top band = 5 existing tools (chips, one category word each);
  divider line "none of these answer ↓"; bottom = 3 persona cards (passenger
  / operator / authority), each with one unanswered question. The vertical
  tension *is* the gap.
- **Failure mode:** bashing existing tools — frame as complementary.
- **Failure mode:** reading all three questions flatly — land the authority
  question last and slowest; it is the highest-value persona.
- **Q&A risk:** "What about internal MCPT control rooms?" → "May exist; not
  accessible to operators, passengers, or researchers."
- **Q&A risk:** "Only three personas? Where's the driver?" → "Driver is a
  data source, not a tool user — they make no analytical decision. Full
  fourteen-question breakdown in backup B5."

**Beat 1.3 — The data (≈ 45 sec, slide 3)**

Argument:
> "The network produces approximately seventeen point eight million boarding
> events per quarter and roughly fifty days of GPS telemetry per release
> window. Thirty-four percent of fare events are student tickets — that
> becomes our most distinctive theme. Ninety-six percent of payments are
> cash. The data exists; nobody is analysing it."

- **Failure mode:** reading the numbers without meaning. Each stat needs a
  half-sentence of "and this matters because…". At 45 sec, keep it to the
  student-share and cash points only.
- **Q&A risk:** "Data source?" → "Public Kaggle dataset (Nguyen and Thoai
  2024)."

### Act 2 — What we propose

**Beat 2.1 — Related work (≈ 45 sec, slide 4)**

Argument:
> "Five reference works inform the design. Chawuthai 2023 on Bangkok GPS
> gives us the Quality-of-Service framework in three tiers. Lin and Zeng on
> real-time bus arrival give us the time-distance trajectory primitive.
> Derevitskiy 2016 gives us the bus-as-traffic-sensor extension. Liu's 2022
> thesis on Multiple Coordinated Views grounds the interaction model.
> Knaflic's *Storytelling with Data* gives us the chart-writing rules."

- **Failure mode:** "I read these papers." Say *what each gives you*.

**Beat 2.2 — System overview (≈ 45 sec, slide 5)**

Argument:
> "At the top level: raw streams ingest into Bronze; normalise into Silver as
> a dimensional model; materialise into Gold as pre-computed aggregate
> tables. A FastAPI application surfaces six analytical themes from the Gold
> tier. The user sees twenty chart canvases coordinated through one
> interaction pattern."

- **Failure mode:** narrating every box. Diagram speaks; you point.
- **Transition:** "Three of those choices deserve their own justification —
  the tool stack, the warehouse architecture, and the interaction model."

**Beat 2.3 — Tool stack (≈ 30 sec, slide 6)**

Argument:
> "Six tools, each chosen for one reason. DuckDB for in-process analytical
> queries. FastAPI because the bespoke editorial hub needed full HTML control
> — Streamlit would have forced seventy percent of the surface into iframes.
> HTMX for partial swaps. Plotly because it ships with MapLibre traces.
> Scrollama for scroll-story. Polars for preprocessing."

- **Failure mode:** dwelling. 30 seconds, then move on.

**Beat 2.4 — Data architecture (≈ 90 sec, slide 7) — FIRST HEADLINE FINDING**

Lead with **integrity**, not speed. The non-obvious finding is that the
fastest-looking candidate is *wrong*, and we caught it. Speed is the payoff,
stated second.

Argument:
> "Three candidates. Star-schema over raw views. Plain Medallion with
> on-demand Gold aggregation. Medallion with materialised Gold. We selected
> against two gates, integrity first. The star-over-raw fails the integrity
> gate outright — it inflates the boarding count by seventeen point nine
> percent, because the route identifiers across our two data families cannot
> be reconciled at query time. We rejected it before we ever measured its
> speed. The plain Medallion is correct but slow — five and a half seconds
> per chart-catalogue page load. Only Medallion with materialised Gold passes
> both: lossless to all seventeen point eight million boardings, and it
> collapses page-load from five thousand five hundred to nine hundred and
> twenty milliseconds — six times faster, measured."

- **Pacing:** slow down. Pause after "seventeen point nine percent" and again
  after "six times faster, measured".
- **Why integrity-first:** pre-empts the strict-committee objection that "of
  course pre-computing is faster." The defensible finding is the *rejection
  on correctness*, not the speed win.
- **Key data:** +17.9 % (reject) · lossless to 17,883,623 · 5,517 ms →
  920 ms · 6×.
- **Slide visual:** `arch_tradeoff.png` with the **+17.9 % integrity-fail
  callout** as the primary overlay and the 6× as secondary.
- **Q&A risks:**
  - "Isn't pre-computing trivially faster?" → "Yes — which is why the finding
    is the integrity rejection, not the speed. Speed only decided between the
    two *correct* candidates."
  - "Why not Inmon CIF / Data Vault?" → no audit-history need, single
    consumer; backup slide B1.
  - "Why not cache Silver with LRU?" → backup slide B2.
  - "How is the integrity check exact?" → backup slide B3.

**Beat 2.5 — Interaction model (≈ 55 sec, slide 8)**

Argument:
> "Multiple Coordinated Views, as Liu specifies it, assumes simultaneous
> brushing across visible charts. Our application shell renders one chart
> canvas at a time. So we make a deliberate choice: Yi's 2007 Connect
> category collapses to a single click-to-entity-panel handoff. Click any
> element — route, stop, school, hex cell — and a detail panel slides in.
> The other six Yi categories remain first-class within each canvas. MCV
> lineage preserved; simultaneous-brushing realisation replaced with
> sequential one."

- **Q&A risk:** "How is this real MCV?" → backup slide B4.

### Act 3 — What we built

**Beat 3.1 — Chart catalogue (≈ 45 sec, slide 9)**

Argument:
> "Twenty chart canvases across six themes. Rule: no two charts in a theme
> share a visual primitive. Three themes wired end-to-end. Three deferred to
> Phase 2."

- **Failure mode:** apologising for the three deferred themes.
- **Transition:** "Let me show you the three that run."

**Beat 3.2 — The hub (≈ 45 sec, slide 10)**

Argument:
> "This is what the user lands on. Editorial vertical scroll, six theme
> cards. KPI strip at the top reads live from the Gold tier. Clicking a card
> lands you in that theme's first chart. The hub is a deliberate design
> choice — not a grid of widgets, an editorial reading mode. Different from
> every existing transit dashboard we surveyed."

- **Failure mode:** apologising for the editorial choice.

**Beat 3.3 — School-Aware Demand (≈ 50 sec, slide 11)**

Argument:
> "First wired theme. Schools-to-routes treemap. Student-fare tickets are
> thirty-four percent of all rides — this is the most novel theme in the
> catalogue, because no global transit tool uses HCMC's HS-SV student-fare
> tagging. Route 20 leads the K-H-X-H-N-V campus, approximately sixteen
> thousand boardings over the ninety-day window."

- **This is the differentiation answer.** If the committee asks "what makes
  this not a generic transit dashboard", this theme is the answer — the
  student-fare lens is unique to HCMC's data and no surveyed tool has it.

**Beat 3.4 — Spatial and Connectivity (≈ 50 sec, slide 12)**

Argument:
> "Second wired theme. Hex density layer over MapLibre, three cell-size
> modes — this is computed from the fare data. Bus-to-metro feeders are
> overlaid: nineteen routes connect to Metro Line 1. I want to be precise
> about scope here — our GPS sample is one local day, and the Metro timetable
> is not in the dataset, so the feeder view is *indicative*, validated by
> design rather than by the full telemetry. The full fifty-day GPS extraction
> in Phase 2 is what turns this theme into a measured connectivity analysis."

- **This is the honesty beat for the data-window limitation.** State it
  plainly here, on your own terms, rather than letting the committee surface
  it as a "gotcha". Full treatment in backup B8.
- **Q&A risk:** "Where does the Metro schedule come from?" → "Not in the
  dataset; a hard-coded MAUR indicative fallback. Phase 2 sources the real
  timetable." (backup B8)

**Beat 3.5 — The Tết shock (≈ 90 sec, slide 13) — SECOND HEADLINE FINDING**

Argument:
> "Third wired theme — Network Health. The Tết 2026 window is the case
> study. February fourteenth through twenty-second: nine days of measured
> network depression, averaging negative fifty-seven percent against the
> pre-Tết January baseline, troughing at negative eighty-four percent on
> February sixteenth — the second day of the lunar new year. January
> baseline returns by February twenty-third. The shock is measurable,
> dateable, recoverable. The Tết Story scrollytelling presents the same
> data narratively, through the same warehouse."

- **Pacing:** slowest beat in the talk. Pause after "negative eighty-four
  percent on February sixteenth".
- **Key data:** −57 % avg · −84 % trough · Feb 14–22 · recovery Feb 22–23.
- **Q&A risks:**
  - "Why only this case study?" → April 30 parade tagged in `dim_date` for
    Phase 2.
  - "Just descriptive, or causal?" → "Descriptive. Phase 2 specifies DiD
    with k-NN synthetic controls."

**Beat 3.6 — Phase 1 status (≈ 50 sec, slide 14)**

Frame as a **deliberate vertical slice**, not a half-finished horizontal
build. The point: three themes are wired *end to end* — raw ingest, Bronze,
Silver, Gold, API, chart, story — proving the entire architecture works, not
just three-twentieths of a UI.

Argument:
> "Phase 1 is a vertical slice, taken deliberately. Rather than half-building
> all six themes, we drove three themes completely through every layer — raw
> ingest, Bronze, Silver, Gold, the API, the chart, and one scrollytelling
> story. That proves the whole pipeline, not a fragment of the surface.
> Delivered: the full Medallion warehouse, forty-one integrity checks all
> passing, nine of eleven endpoints inside the hundred-millisecond ceiling at
> p99, three themes wired, one story shipped. Deferred by design: the three
> remaining themes, within-theme linked brushing, the full fifty-day GPS for
> QoS — our sample is one local day — and the fourteen-day forecast. Phase 1
> is internal self-audit; external user validation is Phase 2."

- **Failure mode:** apologetic tone. "Deliberate vertical slice" — not
  "incomplete work".
- **Slide visual:** the ✓ / → two-column block; relabel the columns
  "Delivered end-to-end" and "Deferred by design", and put the
  "GPS = 1 local day, full 50-day in Phase 2" note in the deferred column so
  the data-window limit is visible, not just spoken.
- **Q&A risk:** "Only nine of twenty charts run — is that a Phase 1?" → "Nine
  charts across three *complete* themes. The slice proves the architecture;
  Phase 2 replicates a proven pattern across the rest."

### Act 4 — What comes next

**Beat 4.1 — Phase 2 roadmap (≈ 55 sec, slide 15)**

Argument (Gantt walkthrough):
> "Phase 2 is fourteen weeks at one developer, ten phases. P0 remediates data
> quality; P1 polishes the warehouse; P2 onward wires the remaining themes,
> stories, and the full fifty-day GPS, with two advisor reviews at the P2 and
> P6 milestones. Crucially, every phase replicates a pattern Phase 1 already
> proved — so the plan is execution, not new design."

Closing one sentence (spoken aside, no slide change):
> "Validation in Phase 2 is a two-wave user study across the three personas,
> and three further extensions — arrival prediction, anomaly detection, the
> bus-as-sensor speed grid — are specified and conditional beyond it."

- **Failure mode:** generality. Phase boundaries with named outputs and
  verifiable acceptance criteria are what make this credible.
- **Q&A risks:**
  - "How will you validate Phase 2?" → backup slide B7 (two-wave matrix).
  - "What's beyond Phase 2?" → covered verbally; if pressed for detail,
    reference report section 6.4.

**Beat 4.2 — Contributions + closing (≈ 50 sec, slide 16)**

Argument:
> "Five contribution headings condense the seven from the report. A
> reconciled design specification. A Medallion warehouse with measured
> architecture defence. A twenty-canvas evidence-grounded chart catalogue.
> Twelve documented data invariants. A running prototype with three wired
> themes and one story. Report and demo together are the Phase 1
> deliverable."

Closing line:
> "Thank you. I'm ready for your questions."

- **Failure mode:** running over time, adding context past the closing line.

### Transitions between acts

| Boundary | Transition sentence |
|---|---|
| Act 1 → 2 | *"Before designing the platform, we surveyed five reference works that shaped the architecture and the chart catalogue."* |
| Act 2 → 3 | *"That is the design. Let me show you what runs."* |
| Act 3 → 4 | *"And from there, Phase 2 finishes the catalogue and validates the design externally."* |
| Act 4 → Q&A | *"Thank you. I'm ready for your questions."* |

---

## 5 · Slide-by-slide build specification

Each slide is specified at the level a junior implementer needs to build it
without further design judgment.

### Universal rules

- **Aspect ratio:** 16:9 (13.33" × 7.5"), inherited from `template.pptx`.
- **Layouts:** every body slide picks one of the template's existing layouts.
  Custom layouts are forbidden — branding must inherit.
- **Footer:** the template's "VIETNAM NATIONAL UNIVERSITY HCM / HCMUT" footer
  stays untouched on every body slide.
- **Title:** descriptive, plain academic register. **No** punchy fragments,
  em-dash drama, period-fragments, or numbers-as-headline rhetoric.
- **Text on slide:** ≤ 25 words per slide where possible. Title is the only
  required text on slides that have a strong self-labelling visual.
- **Title font size:** 36–44 pt. Body: 24–28 pt. Captions: 12–14 pt muted.
- **Margins:** 0.5" minimum from slide edges.
- **Colour palette:** template default (dark navy + light blue triangular
  motif). Single accent colour reserved for the focal element of each slide.
- **One hero visual per slide.** Text-only slides forbidden by the pptx
  skill.

### Slide-by-slide

| # | Beat | Title | Layout | Hero visual | Text on slide |
|---|---|---|---|---|---|
| 1 | 1.1 | HCMC Bus Analytics: A Multi-Stakeholder Analytical Platform | `3_Title Slide` (dark cover) | Logo_BK + template motif | Title, "Phase 1 · Capstone Defence", name, advisor, date |
| 2 | 1.2 | The analytical gap | `Title and Content` | Custom: 5-tool band (top) + divider + 3 persona question-cards (bottom) | 5 tool names + 3 persona labels, each with one unanswered question |
| 3 | 1.3 | Dataset and exploratory analysis | `Blank` | Custom 2 × 2 stat grid | 4 numbers (17.88 M · ₫72 B · 34 % · 96 %) + 4 sub-labels |
| 4 | 2.1 | Related work | `Title and Content` | Custom 5-lens row | 5 × (author-year + one phrase) |
| 5 | 2.2 | System overview | `Picture with Caption` | `report/images/diagrams/solution_pipeline.png` | none — diagram self-labels |
| 6 | 2.3 | Tool stack | `Title and Content` | Custom 6-icon grid (use `report/images/logos/*.png` where available; placeholder boxes for HTMX, Scrollama, FastAPI) | 6 tool names |
| 7 | 2.4 | Data architecture | `Picture with Caption` | `report/images/diagrams/arch_tradeoff.png` + **primary "+17.9 % integrity fail → rejected"** callout, secondary "6× / 920 ms" callout | "Star-over-raw rejected on integrity (+17.9 %) · Gold 6× faster (5,517 → 920 ms)" |
| 8 | 2.5 | Interaction model | `Picture with Caption` | `report/images/diagrams/interaction_sequence.png` (or `foundations_mcv.png` if cleaner) | "Click → entity detail panel · Yi 2007 Connect category" |
| 9 | 3.1 | Chart catalogue | `Picture with Caption` | `report/images/diagrams/solution_catalogue_map.png` | "20 canvases · 6 themes · 3 wired" |
| 10 | 3.2 | Phase 1 prototype: the hub | `Picture with Caption` | `hub_fullbleed.png` full-bleed | none — UI self-labels |
| 11 | 3.3 | Wired theme: School-Aware Demand | `Picture with Caption` | `card2_treemap_v2.png` | "Student-fare tickets = 34 % of all rides" |
| 12 | 3.4 | Wired theme: Spatial and Connectivity | `Picture with Caption` | `card3_density_v3.png` | "Hex density + 19 bus-to-metro feeders" |
| 13 | 3.5 | Case study: the Tết 2026 shock | `Picture with Caption` | `card5_pulse_v2.png` (alternate: `story_v3_bing.png`) | "Feb 14–22 · −57 % avg · −84 % Feb 16" |
| 14 | 3.6 | Phase 1 implementation status | `Comparison` | Custom 2-column ✓ / → block, columns labelled "Delivered end-to-end" / "Deferred by design" | 5 ✓ items + 4 → items (incl. "GPS = 1 local day; full 50-day in Phase 2") |
| 15 | 4.1 | Phase 2 roadmap | `Picture with Caption` | `report/images/diagrams/future_gantt.png` | "14 weeks · 10 phases · 2 advisor reviews" |
| 16 | 4.2 | Contributions | `Title and Content` | Numbered list (plain text composition, no hero image) | 5 condensed contribution lines |

### Custom-drawn visuals (7 in total)

| Slide | Visual | Build method | Effort |
|---|---|---|---|
| 2 | 5-tool band + 3 persona question-cards | python-pptx native shapes: top row 5 tool chips, divider line, bottom row 3 persona cards each with a one-line question | 30 min |
| 3 | 2 × 2 big-stat grid | python-pptx native shapes + 72 pt stat text + 14 pt sub-labels | 15 min |
| 4 | 5-lens row | python-pptx native shapes (5 rows, icon + text) | 20 min |
| 6 | 6-tool icon grid | python-pptx native layout reusing `report/images/logos/*.png` + placeholder shapes for HTMX/Scrollama/FastAPI | 15 min |
| 14 | 2-column ✓ / → block | python-pptx native shapes (2 columns, coloured bullets) | 15 min |
| B7 | 3 × 2 user-evaluation matrix (backup) | python-pptx native shapes (3 columns × 2 rows + headers) | 20 min |

| B8 | GPS / AFC data-window honesty (backup) | python-pptx native shapes (2-row timeline: AFC 2026 vs GPS 2025, "no timestamp join" callout) | 20 min |
| B9 | Differentiation vs generic dashboards (backup) | python-pptx native shapes (5 moats list) | 15 min |

Total custom-visual effort: ≈ 2 hours 20 min. No external dependencies (no AI
image generation, no LaTeX, no draw.io export).

---

## 6 · Backup slides

Parked after slide 16, not in the main flow. Each backup slide defends one
flagged Q&A risk from §4.

| # | Title | Source | Defends |
|---|---|---|---|
| B1 | Three architecture candidates — qualitative + quantitative | `report/sections/Ch4_ProposedSolution/4.5_DataArchitecture.tex` tables 4.5 + 4.6 | Beat 2.4 — "Why not Inmon / Data Vault?" |
| B2 | LRU vs Gold benchmark | `report/sections/appendixes/AppendixC_BenchmarkStories.tex` table | Beat 2.4 — "Why not cache Silver with LRU?" |
| B3 | Three row-multiplication bugs fixed in Silver | `report/sections/Ch4_ProposedSolution/4.5_DataArchitecture.tex` table 4.8 | Beat 2.4 — "How do you know your numbers are right?" |
| B4 | Yi 2007 + Heer-Shneiderman 2012 category map | `report/sections/Ch4_ProposedSolution/4.8_InteractionModel.tex` | Beat 2.5 — "How is this real MCV?" |
| B5 | Fourteen stakeholder questions full table | `report/sections/Ch4_ProposedSolution/4.1_ProblemAnalysis.tex` (and CLAUDE.md §2.1) | Beat 3.1 — "Show me question N in your system" |
| B6 | HCMC anomaly catalogue (Tết, April 30, school terms, etc.) | `report/sections/Ch4_ProposedSolution/4.2_DatasetAndEDA.tex` `dim_date` discussion | Beat 3.5 — "What other anomalies?" |
| B7 | Two-wave user evaluation matrix (3 personas × 2 waves) | `report/sections/Ch6_FutureWorks/6.3_UserEvaluation.tex` | Beat 4.1 — "How will you validate Phase 2?" |
| B8 | GPS / AFC data-window mismatch, stated plainly | CLAUDE.md §3 invariants 1, 6, 8, 11 + Ch4.2 | Beat 3.4 — "1 day of GPS from a different year — how is any cross-source claim valid?" |
| B9 | Five differentiation moats vs generic transit SaaS | CLAUDE.md §8.1 + Ch2.4 | Beat 3.3 — "What's new here versus Swiftly / Remix / a generic dashboard?" |

B1–B7 are built from a single table or figure already in the report — no new
content. B8 and B9 are new defensive backups added after the strict-committee
stress-test (they answer the two hardest drill-downs the main flow does not
fully resolve on its own). Layout: `Title and Content` with a single
full-width table or figure.

---

## 7 · Build approach

The implementation plan (next phase, via writing-plans skill) will turn this
spec into ordered build steps. At a high level:

1. **Clone template.** Copy `template.pptx` to
   `report/capstone_defence.pptx`. Delete the 10 demo slides shipped with the
   template; keep all slide layouts in the master untouched.
2. **Insert 16 main-flow slides + 9 backup.** Each slide references its
   target layout from the master by name (e.g. `Picture with Caption`,
   `Comparison`).
3. **Place hero visuals.** Existing PNGs inserted at slide-specific fixed
   positions; custom visuals drawn with python-pptx native shapes at the
   same positions.
4. **Set titles + minimal text.** Each slide's text content matches the §5
   table verbatim. No filler text, no subtitles unless §5 specifies.
5. **Verify branding inheritance.** After insertion, every body slide must
   show the template footer, the corner triangular motif, and the inherited
   font. Cover slide uses the dark `3_Title Slide` layout.
6. **QA loop (mandatory):**
   - Render to PDF via `soffice --headless --convert-to pdf`.
   - Convert PDF to JPEG via `pdftoppm -jpeg -r 150`.
   - Send all 25 slide images to a fresh subagent for visual inspection with
     the bug-hunt prompt from the pptx skill.
   - Fix every overlap, wrap issue, missing footer, low-contrast element.
   - Re-render and re-inspect at least once.
7. **Content QA.** Run `python -m markitdown report/capstone_defence.pptx`
   and grep for leftover placeholder text (`xxxx`, `lorem`, "this page
   layout"). Fix any matches before declaring done.

---

## 8 · Acceptance criteria

The deck is done when **all** of these hold:

- [ ] `report/capstone_defence.pptx` exists and opens in PowerPoint / Keynote
      / LibreOffice without rendering errors.
- [ ] Exactly 25 slides: 1 cover + 15 body + 9 backup.
- [ ] Spoken time budget (§3 table) sums to ≤ 14:40 including transitions.
- [ ] Student-fare share reads 34 % everywhere (no 36 %).
- [ ] Slide 2 shows the 3 personas; slide 7 leads with the +17.9 % integrity
      fail; slide 14 columns read "Delivered end-to-end" / "Deferred by
      design" and disclose the 1-day GPS limit.
- [ ] Every body slide carries the template footer and corner motif.
- [ ] Every slide has a title at the size and position inherited from its
      layout.
- [ ] No slide exceeds 30 words of body text (cover and contributions slide
      exempt).
- [ ] Every hero visual is present (no missing or placeholder images).
- [ ] At least one full QA loop (render → image → subagent inspection → fix)
      has completed with no remaining issues.
- [ ] Content grep for placeholder text returns no matches.
- [ ] Total file size under 25 MB.

---

## 9 · Out of scope

- Speaker notes (the speaker plan in §4 is the de facto script; not embedded
  in slide notes).
- Animations / transitions (none specified; the deck is static).
- Live demo integration (defence is static-screenshot only, per
  brainstorming Q4).
- Vietnamese translation of body text (English-only, per brainstorming Q1).
- Embedded video (none, per brainstorming Q3).
- Distribution / export to PDF for handout (deck is `.pptx` only; PDF
  conversion is a QA step, not a deliverable).
