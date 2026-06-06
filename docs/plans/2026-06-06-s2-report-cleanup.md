# S2 · Report cleanup for Phase 2 — plan

**Goal:** slim the report **body (Ch1–7) from ~130 pp to 50–70 pp** by moving detail to
appendices and compressing; **realign** the architecture + implementation to the Phase-2 stack
(dbt + Dagster + BigQuery, monorepo, data API + React); **fix** the 4 known inconsistencies.
174 pp → target ~90–110 pp total (60–70 body + grown appendices). xelatex + biber are available
here, so I rebuild the PDF and confirm it compiles.

**Method:** edit `.tex` in place; move (don't delete) detail into appendices; rewrite the
Phase-1-specific architecture/impl sections; **consolidate over-fragmented subsections**. Frame
Phase 2 honestly — *what is built* (backend data API + re-architecture) + *the design* (pipeline,
frontend) — not a finished system.

---

## Consolidate subsections (primary slimming lever)

The body has **73 subsections + 10 subsubsections** — far too many; most are 1–2 paragraphs that
should be flowing prose under their section, not separate headed stubs. **Rule:** a subsection
must earn its heading (a distinct sub-argument, ~≥ half a page); anything shorter is merged into
the parent as prose, optionally with a **bold lead-in** instead of a heading. This tightens the
prose, shrinks the TOC, and recovers whitespace.

| Chapter | Subsections now | Target | Example |
| --- | --- | --- | --- |
| Ch2 | 6 | ~3 | merge the per-tool stubs into the comparison |
| Ch3 | 17 (+4 subsub) | ~8, 0 subsub | one subsection per concept, not per sub-point |
| Ch4 | 35 (+6 subsub) | ~14, ≤2 subsub | **§4.5: 7 subsections → 2** ("Candidate comparison" + "Selected architecture", with integrity/refresh/Gold folded as prose) |
| Ch5 | 5 | ~3 | |
| Ch6 | 10 | ~4 | |
| **Total** | **73 sub / 10 subsub** | **~32 sub / ~2 subsub** | |

This runs *alongside* the move-to-appendix + compress work below (the per-chapter line-count
targets already assume it).

### Depth rule (hard): chapter → section → subsection, and stop

Maximum heading depth is **`\subsection`**. All **10 `\subsubsection`s are flattened** — folded
into their subsection as flowing prose (bold lead-in if a label helps) or promoted to a real
subsection only if they earn it. No deeper nesting is introduced anywhere.

### Ranked restructuring (rank → verify → dispose)

Every element is ranked **Core** (carries the thesis/Phase-2 narrative), **Support** (useful but
compressible), or **Cut/Move**; then verified (accurate? non-redundant? needed for Phase 2?) and
given a disposition. Section-level dispositions:

| § | Section | Rank | Disposition |
| --- | --- | --- | --- |
| 1.1–1.3 | Motivation / Objectives / Scope | Core | Keep; add the Phase-2 objective + scope |
| 1.4 | Outline | Support | Keep, trim |
| 2.1 | Existing tools | Core | Keep; merge per-tool subsections → one comparison |
| 2.2/2.3 | Ops / Viz research | Support | Trim |
| 2.4 | Gap | Core | Keep |
| 3.1 | Layered architecture | Support | Trim, flatten subs |
| 3.2 | QoS (Bangkok) | Core | Keep (moat) |
| 3.3 | Visualisation primitives | Support | Compress; catalogue → **App E**; flatten 2 subsubs |
| 3.4 | MCV | Support | Trim (lineage only) |
| 3.5 | Storytelling | Support | Trim |
| 3.6 | Tools | Support | Compress (Phase-1 list superseded by Ch5) |
| 3.7 | Analytical methods | Support | Trim |
| 4.1 | Problem analysis | Core | Keep; R/N as a table, trim prose |
| 4.2 | Dataset & EDA | Core | Keep headlines; profiling tables → **App A** |
| 4.3 | Preprocessing | Core | **Rewrite P2** (dbt/Dagster micro-batch) |
| 4.4 | Solution overview | Core | **Rewrite P2** (monorepo) |
| 4.5 | Data architecture | Core | **Rewrite P2** + 7 subs → 2 + benchmarks → **App C** |
| 4.6 | Analytical themes | Support | Compress to the catalogue summary |
| 4.7 | Visualisation selection | Support | Compress; per-chart rationale → **App E** |
| 4.8 | Interaction model | Core | Keep, trim, flatten subs, P2 status |
| 5.1 | Pipeline status | Core | **Rewrite P2** (backend built + frontend + pipeline design) |
| 5.2 | Interface mockup | Support | Keep relevant captures, trim |
| 5.3 | Evaluation | Core | Keep what holds; fix Tết date |
| 6.1 | Roadmap | Core | **Rewrite P2** roadmap; fix warehouse counts |
| 6.2 | Deployment | Support | **Rewrite P2** (BigQuery deploy) |
| 6.3/6.4 | User eval / Extensions | Support | Trim |
| 7.1–7.3 | Summary / Contributions / Limitations | Core | Keep, P2-update; fix typo + Tết date |

**Writing-quality pass** (from the skill's anti-patterns), applied during every rewrite/compress:
≤ 2 em-dashes per page, no AI-typical fillers ("delve", "crucial", "it is important to note"), no
throat-clearing openers ("In this section we discuss…"), varied paragraph length.

---

## Per-chapter actions

### Front matter
- **`table-of-glossary.tex`** — **FIX**: the MCV entry still says "a selection in one chart
  propagates to every sibling chart"; rewrite to the click-to-entity-panel model (matches
  Ch3.4/4.8). **`abstract.tex`** — light Phase-2 reframe (analytics platform, the re-architecture).

### Ch1 Introduction (~156 ln, ~6 pp) → keep, light update
- **1.2 Objectives / 1.3 Scope** — add the Phase-2 objective (production-grade re-architecture:
  data API + SPA + dbt/Dagster/BigQuery pipeline). 1.1/1.4 unchanged. Target ~5–6 pp.

### Ch2 Related Work (~306 ln, ~12 pp) → keep, light trim
- Trim prose; keep the 6-tool comparison + the gap. Target ~9–10 pp.

### Ch3 Theoretical Background (~900 ln, ~30 pp) → **compress hard** (biggest theory cut)
- **3.3 VisualisationPrimitives (278)** — keep the Cleveland–McGill / Munzner rubric + the
  chosen primitives; **MOVE** the full primitive catalogue → **Appendix E**. ~278→~90 ln.
- **3.6 Tools (164)** — compress to the chosen stack rationale; the Phase-1 tool list is
  superseded (see Ch5). ~164→~70 ln.
- **3.1 LayeredArchitecture / 3.7 AnalyticalMethods** — trim ~20–30%.
- Keep 3.2 QoS, 3.4 MCV, 3.5 Storytelling (trim lightly). Target Ch3 ~12–14 pp.

### Ch4 Proposed Solution (~2,262 ln, ~55 pp) → **the main slim + realign**
- **4.1 ProblemAnalysis (207)** — keep R1–R15/N1–N6 as a compact table; move long rationale
  prose to text/appendix. ~207→~120 ln.
- **4.2 DatasetAndEDA (341)** — keep the headline EDA + the dynamic-data framing; **MOVE** the
  detailed profiling tables → **Appendix A**. ~341→~150 ln.
- **4.3 Preprocessing (75)** — **REWRITE**: remove the dbt-rejection; describe the dbt + Dagster
  micro-batch ingestion (exports → parquet → GCS → Dagster sensor → incremental dbt) + the
  §4.3.1 validation gate as Dagster asset checks.
- **4.4 SolutionOverview (37)** — update the one-page system overview to the monorepo
  (pipeline · backend data API · React SPA).
- **4.5 DataArchitecture (479)** — **REWRITE + slim**: keep the Medallion lineage (vs Inmon/Data
  Vault), the Bronze→Silver-star→Gold tiers, the integrity argument (relative lossless), and
  Gold-as-serving-contract; reframe the implementation as **dbt models on BigQuery** (dev/prod
  datasets, DuckDB local), **incremental + partitioned**, **filterable Gold cube**, Dagster
  orchestration. **MOVE** the Phase-1 DuckDB benchmark tables (latency, endpoint p50/p99,
  LRU/scaling) → **Appendix C**, cited as the Phase-1 measurements that motivate materialised Gold.
  ~479→~180 ln.
- **4.6 AnalyticalThemes (330)** — keep the 6-theme framing + the catalogue summary table;
  compress per-theme prose (the catalogue spec is the source). ~330→~160 ln.
- **4.7 VisualisationSelection (495)** — keep the selection rubric + the 20-chart summary table;
  **MOVE** the per-chart 10-field rationale → **Appendix E** (or cite the catalogue). ~495→~170 ln.
- **4.8 InteractionModel (298)** — keep the click-to-entity-panel design; trim; update "built"
  references to the Phase-2 split (backend serves the data; React builds the UI). ~298→~170 ln.
- Target Ch4 ~24–28 pp.

### Ch5 Implementation (~462 ln) → **REWRITE to Phase 2**
- **5.1** — the monorepo + the **backend data API** that is built: layered architecture (Warehouse
  Protocol/DI, repositories→services→schemas→routers, chart registry), domain-data contract,
  caching/logging/error-handling, **contract tests in CI** (synthetic fixture warehouse). The
  **frontend foundation** (React+Vite+TS, TanStack Query, react-plotly.js, one chart end-to-end).
  The **pipeline** as designed (dbt/Dagster/BigQuery), not yet built.
- **5.2 InterfaceMockup** — keep the UI captures relevant to the new SPA; note the demo as the
  reference prototype.
- **5.3 Evaluation** — keep what still holds (the lossless integrity, the latency motivation);
  **FIX** the Tết recovery date → Feb 23. Target Ch5 ~8–10 pp.

### Ch6 Future Work (~302 ln) → **REWRITE to the Phase-2 roadmap**
- **6.1 Roadmap** — the actual remaining plan: build the dbt/Dagster pipeline on BigQuery
  (incremental + cube + sensors), finish the 8 remaining charts + hub/panel/filter UI, the
  should-fix list. **FIX** the warehouse counts (12 dims + 3 facts + 7 Gold). 6.2 Deployment →
  the BigQuery deployment (cite `docs/specs/bigquery-deployment.md`). 6.3/6.4 trim. Target ~6–8 pp.

### Ch7 Conclusion (~273 ln) → light update
- Contributions/limitations reflect Phase 2; **FIX** the Ch7.1 typo and the Tết recovery date.
  Target ~6–7 pp.

### Appendices (receive the moved detail)
- **A** ← EDA profiling tables. **C** ← the Phase-1 benchmark tables. **E** ← the primitive
  catalogue + per-chart viz rationale. **DELETE** the empty `AppendixD_SolutionDetails.tex`.

---

## Inconsistency fixes (the 4 + cleanup)
1. Glossary MCV entry → click-to-entity-panel model.
2. Tết recovery date → **Feb 23** everywhere (Ch5.3, Ch7.1, Appendix D StoryScenes).
3. Roadmap warehouse counts → **12 dims + 3 facts + 7 Gold** (Ch6.1, Appendix B).
4. Ch7.1 typo ("the a running prototype").
5. Remove the empty `AppendixD_SolutionDetails.tex` from disk.

## Build + verify
- After edits: `cd report && xelatex main && biber main && xelatex main && xelatex main`.
- Confirm it compiles clean; check `pdfinfo main.pdf` body pages land in 50–70 (excl. appendices).
- Spot-check the rewritten architecture + impl chapters read coherently.

## Execution order
1. Inconsistency fixes (small, safe). 2. Ch5 + Ch6 rewrite (Phase-2 impl/roadmap). 3. Ch4.3 +
4.5 + 4.4 rewrite (architecture realign). 4. Slimming moves (Ch3, 4.2, 4.6, 4.7 → appendices).
5. Front matter + Ch1/Ch7 updates. 6. Build + verify.
