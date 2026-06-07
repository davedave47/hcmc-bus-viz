# Product Backlog — HCMC Bus Analytics (Phase 2)

**Stakeholders:** supervisor = product-owner proxy + immediate reviewer · council = final acceptance
at the defense. **Grading targets:** CLAUDE.md §0 (delivery 50 + evaluation 10 dominate). **Cadence:**
1-week sprints, ~full semester (~14 sprints). **Definition of Done:** `definition-of-done.md`.

Priority is MoSCoW (**M**ust / **S**hould / **C**ould / **W**on't-yet). Each story names the rubric
criterion it advances. Because ~60% of the grade is *deliver + evaluate the system* (Câu 1 + Câu 4),
the release plan front-loads a finishable core and evaluates as it goes — breadth is traded for a
task that is ≥95% done and proven.

**Every sprint delivers across four tracks** — code/tools · documents · report · **deck** — per the
Sprint Definition of Done (`definition-of-done.md`). The weekly **deck reports to the supervisor**;
those decks distill into the **final defense deck for the council and reviewer**.

## Epics

| # | Epic | From | Realizes |
|---|---|---|---|
| **E1** | System & tools (end-to-end) — architecture, tool selection (core + monitoring + ops), build the platform | Goal 1 | Câu 1 · Câu 3 · Part II |
| **E2** | Chart selection — refine the 20-chart catalogue step by step, then build the remaining charts + UI | Goal 2 | Câu 1 · Câu 3 |
| **E3** | Living storytelling — keep narrative fresh as the data grows (a story computed once goes stale) | Goal 3 | Câu 1 · Câu 2 · bonus |
| **E4** | Report, deck & defense — documentation, slides, Q&A prep | Goal 4 | Câu 5/6 · council Câu 5/6/7 |
| **E5** | Evaluation & validation — test/experiment the product against its requirements | rubric | Câu 4 · Câu 2 |
| **E6** | Project management *(continuous)* — weekly sprints, supervisor check-ins | this setup | steady Câu 1 |

## Stories (initial — the backlog grows each sprint)

| ID | Epic | Story | Pri | Rubric |
|---|---|---|---|---|
| E1-1 | E1 | End-to-end architecture + core-tool selection (storage · transform · orchestration · serving · frontend), with justified alternatives | M | Câu 3 / Part II |
| E1-2 | E1 | Monitoring, observability & ops design — CI/CD, testing strategy, deployment/IaC, security — selection + rationale | M | Câu 3 |
| E1-3 | E1 | Build the dbt + Dagster pipeline (Bronze → Silver star → Gold) on BigQuery (DuckDB local) | M | Câu 1 |
| E1-4 | E1 | Filterable Gold cube + serving contract the API reads | M | Câu 1 |
| E1-5 | E1 | Deploy the stack (cloud) end-to-end | S | Câu 1 |
| E2-1 | E2 | Rewrite the chart docs fresh as two clean files — `chart-catalogue.md` (the catalogue) + `chart-rationale.md` (justified choice per chart by impact × effort) — re-validated step by step against the data + the 14 questions; drop the old flagship/change-log/Phase-1 framing | M | Câu 3 |
| E2-2 | E2 | Build the remaining 11 backend chart services | M | Câu 1 |
| E2-3 | E2 | Build the remaining frontend chart builders + components | M | Câu 1 |
| E2-4 | E2 | Hub + theme cards + entity-detail panel + filter-bar UI | M | Câu 1 |
| E3-1 | E3 | Design a "living story" mechanism — parametrize each story over the current data window and recompute, so narratives stay current | S | Câu 2/3 |
| E3-2 | E3 | Build it for one rolling story end-to-end | S | Câu 1 · bonus |
| E4-1 | E4 | Write Ch6 Data Architecture · Ch7 Implementation · Ch8 Evaluation · Ch9 | M | Câu 5 |
| E4-2 | E4 | Keep ≥5 properly-cited references; all figures in house style | M | Câu 6 |
| E4-3 | E4 | Build the Phase-2 defense deck | M | council Câu 5 |
| E4-4 | E4 | Defense Q&A preparation (anticipated questions + evidence) | S | Câu 7/9 |
| E5-1 | E5 | Functional coverage evaluation — charts vs the 20-catalogue + 14 questions | M | Câu 4 |
| E5-2 | E5 | Performance/latency evaluation — cube reads + warm re-render budget (N1) | M | Câu 4 |
| E5-3 | E5 | Data-integrity evaluation — relative lossless + contract tests | M | Câu 4 |
| E6-1 | E6 | Run weekly planning / review / retro; log supervisor check-ins | M | steady Câu 1 |

## Release plan (sprint map, ~14 weekly sprints)

| Sprint | Focus |
|---|---|
| **S1** | E1-1 end-to-end architecture + core-tool selection *(current)* |
| S2 | E1-2 monitoring/ops design + start E1-3 pipeline |
| S3–S4 | E1-3/E1-4 build pipeline + Gold cube; E1-5 deploy |
| S5 | E2-1 catalogue re-validation + E2-2 backend charts |
| S6–S7 | E2-3 frontend charts + E2-4 UI shell |
| S8 | E3 living storytelling |
| S9 | E5 evaluation pass (coverage · performance · integrity) |
| S10–S11 | finish remaining + E4-1 report writing |
| S12 | E4-3 deck |
| S13 | E4-4 defense rehearsal + buffer |
| S14 | hardening before defense |

E4 (report/deck) and E6 (PM) run **continuously** every sprint, not only in their dedicated slots.
