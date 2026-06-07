# Definition of Done

A backlog item is **Done** only when every point below holds. The bar is written to the Phase-2
grading targets (CLAUDE.md §0): *deliver, evaluate, justify, document.*

1. **Works.** Implemented and, if code, it builds and its tests pass (CI green). The result is real,
   not a stub — it contributes to ≥95% delivery of the committed task (Câu 1, 50 pts).
2. **Evaluated.** The item carries at least one evaluation appropriate to it: a test, a measurement,
   an experiment, or a validation against its requirement (Câu 4, 10 pts). "It runs" is not an
   evaluation.
3. **Justified.** Any significant tool, chart, or architecture decision records its **alternatives
   and the reason for the choice** (Câu 3, 5 pts; reviewer Part II rewards an architecture pattern
   justified against other patterns).
4. **Documented.** The report and/or deck are updated for the change, following
   `docs/conventions/report-writing.md` — diagrams in the draw.io house style, ≥5 properly-cited
   references maintained (reviewer Câu 5/6).
5. **Demoable.** There is something to show at sprint review: a screenshot, a live run, a figure, or
   a passing test. It is what proves the real-world benefit, with evidence (Câu 2, 5 pts).
6. **Tracked.** The backlog and the current sprint file reflect the new state.

A story that cannot meet points 1–3 is too big or ill-defined — split it or send it back to the
backlog.

## Sprint Definition of Done — four deliverable tracks

A sprint is not Done on code alone. **Every sprint delivers across all four tracks**, weighted to
that sprint's focus (a design sprint is doc/report/deck-heavy; a build sprint is code-heavy), but
none is ever zero:

| Track                  | What ships each sprint                                                      | Serves                     |
| ---------------------- | --------------------------------------------------------------------------- | -------------------------- |
| **Code / tools** | the implementation or tool setup advanced this sprint                       | Câu 1 (delivered results) |
| **Documents**    | design notes / decision records in `docs/` (e.g. a tool-selection matrix) | Câu 3 · Part II          |
| **Report**       | the LaTeX report sections updated for the sprint's work                     | Câu 5/6                   |
| **Deck**         | a short**weekly progress deck for the supervisor** check-in           | reporting + council Câu 5 |

**Deck cadence.** The weekly deck reports progress to the **supervisor**. The decks accumulate and
are distilled into the **final defense deck for the council and reviewer** (council Câu 5/6/7,
reviewer Câu 7/8/9). Keep weekly decks short (a few slides: done · in-progress · next · blockers).

**The deck, report and final product are used for grading at the end.**
