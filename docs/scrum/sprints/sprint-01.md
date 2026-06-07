# Sprint 1 — Justified end-to-end architecture + core-tool selection

**Window:** 2026-06-08 → 2026-06-14 (1 week) · **Epic:** E1 · **Goal 1**

## Sprint goal

A justified end-to-end system architecture and core-tool selection, diagrammed and written into the
report and deck - the foundation the build and evaluation depend on.

## Committed stories / tasks

| Task | Done when | Rubric |
|---|---|---|
| T1 · End-to-end architecture diagram (context + data flow), draw.io house style | PNG renders, legible at embedded size, in report Ch6 + deck assets | Câu 5 · Part II Câu 3 |
| T2 · Core-tool selection matrix — storage · transform · orchestration · serving · frontend: candidates, chosen, **why-not-the-alternatives** | table + prose, one row per layer, each with a rejected option and the reason | Câu 3 · Part II Câu 4 |
| T3 · Capture T1/T2 into report Ch6 (Architecture Overview) + §3.6 tech stack | sections compile clean, follow `report-writing.md` | Câu 5 |

**Evaluation for this sprint (Câu 4):** the design is checked against its requirements — the warm
re-render / latency budget (N1), the scale target (millions of trips/day), and portability
(DuckDB ↔ BigQuery). The architecture-pattern-vs-alternatives discussion is the design's evaluation.

**Out of scope (→ Sprint 2):** monitoring/observability, CI/CD, testing strategy, deployment/IaC,
security. Building the pipeline (E1-3) starts Sprint 2.

## Deliverables (the four tracks)

| Track | This sprint |
|---|---|
| **Code / tools** | render the architecture diagram (draw.io → PNG) into `report/images/diagrams/`; confirm the `pipeline/` package config reflects the chosen stack |
| **Documents** | tool-selection matrix as a decision record in `docs/design/` (candidates · choice · why-not) |
| **Report** | Ch6 Architecture Overview + §3.6 Technology Stack written |
| **Deck** | Sprint-1 progress deck for the supervisor: the architecture + the tool choices + next sprint |

## Daily log

- Mon (06-08):
- Tue (06-09):
- Wed (06-10):
- Thu (06-11):
- Fri (06-12):

## Review (Fri — what shipped, demo)

-

## Retro (keep / drop / try)

- Keep:
- Drop:
- Try:

## Supervisor check-in

- Date / notes:
