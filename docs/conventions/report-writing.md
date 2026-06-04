# Report Style Guide — HCMC Bus Analytics Report

The single source of truth for every writing, figure and table in the report.
When in doubt, match the three reference figures in `docs/` (the data-centre
workflow, the DIPLOEE model, the GTFS ERD).

## Section 1. Global conventions (applies to every section)

### 1.1 Voice and register

The report is a third-person academic document addressed to an external marker. It is not addressed to the student, the advisor, or to the assistant that wrote earlier drafts.

The following are forbidden in the body of the report:

1. Meta-commentary about the document. The sentence "This section presents the motivation, scope, and outline" is not allowed. The section title is the meta-commentary; nothing more is needed.
2. Forward references in the abstract or in chapter introductions of the form "Section 4 develops the dashboard". A single chapter-outline paragraph at the end of Chapter 1 is allowed; otherwise, forward references appear at the end of paragraphs only where they add value.
3. Product names. The word "BusLens" never appears. The word "card" in the sense of a dashboard tile never appears. The word "lens" never appears. The word "hub" in the sense of an overview index appears only as a generic noun.
4. Internal acronyms. The acronyms "SDVF", "A1", "A2", "A3" never appear. The underlying concepts are renamed: prioritisation among proposed modules is presented as a comparison table; the three interaction-design choices are presented under their academic names (Multiple Coordinated Views, visual storytelling, entity-detail interaction pattern).
5. File paths. The strings `src/duckdb_loader.py`, `docs/design/app-layouts.html`, `notebooks/01_*.ipynb`, and any other source-tree path do not appear in the body. They are confined to Appendix A.
6. Citations of internal documents. The bibliography entries `rubric`, `capstoneDescription`, and `thoai2025` are deleted. No section refers to the grading rubric in any form. The capstone topic is restated in the student's own words once in Chapter 1; the document is not cited.
7. Conversational phrasing. The phrases "wired into", "anchored to data narratives", "the differentiator", "table-stakes", "deliverables", "feature bundle" are removed. Replace with formal alternatives: "implemented as", "organised around", "the principal contribution", "essential capabilities", "outputs".

### 1.2 Typographic conventions

1. The em dash character "—" is forbidden. Replace with comma, semicolon, parentheses, or rewrite the sentence.
2. The `\paragraph{...}` command is forbidden. Replace with one of: a plain paragraph whose first sentence is the topic sentence; a plain paragraph followed by `\begin{itemize}` or `\begin{enumerate}`; a numbered subsection if the content justifies it.
3. Every abbreviation is expanded on first use: "Automated Fare Collection (AFC)", "Global Positioning System (GPS)", "Quality of Service (QoS)", "Multiple Coordinated Views (MCV)", "Uniform Manifold Approximation and Projection (UMAP)", "Hexagonal hierarchical geospatial indexing system (H3)". Subsequent uses are the abbreviation only.
4. Captions are one short clause. Never two sentences. The "What" details that earlier captions contained move into the paragraph that introduces the figure or table.
5. Float placement is `[!htbp]` for every figure and table. The `[H]` placement (from the `float` package) is removed. LaTeX is allowed to reorder floats to avoid large blank pages.
6. Section structure uses only `\section`, `\subsection`, and (sparingly) `\subsubsection`. No `\paragraph`.
7. Math is set with `\(...\)` or `\[...\]` or `equation` environments. Plain text variables are typeset as `\(T\)`, not `T`.

### 1.3 Figure and table policy

1. Every figure uses the `\imageplaceholder{Type}{What}{How to capture}` macro defined in `main.tex`. The student replaces placeholders with real assets before submission.
2. Large dump-style tables (the previous data-quality table, the 31-row chart catalogue) are split into smaller, page-friendly tables. No single table spans more than half a page. Long tables that genuinely need to be long are converted to `longtable` and labelled appropriately.
3. Every figure and table is introduced in the paragraph immediately before it, and the discussion that follows refers to it by `\ref{...}`. No floating tables without prose anchor.
4. Captions name the object, not the finding. "Volume of boardings per fare class" is a caption. "Student fares dominate the morning peak" is a finding and belongs in the prose.

### 1.4 Forbidden vocabulary

| Word or phrase | Replacement |
|---|---|
| BusLens | the proposed system; the proposed analytical platform; the system |
| card (as a UI element) | thematic view; analytical view; theme |
| lens | analytical view; theme |
| hub | overview index; home page (if a UI noun is required) |
| Atlas-style | reference-style (or drop the analogy) |
| editorial scroll | vertical reading order |
| flagship | principal; central |
| SDVF | (concept dropped; replace with a justification paragraph or a comparison table) |
| A1 / A2 / A3 | (concept kept; replace with named academic principles) |
| linked brushing invariant | Multiple Coordinated Views (MCV) interaction model |
| story-subtitled charts | annotated charts following visual storytelling principles |
| universal entity detail panel | entity-detail interaction pattern |
| sprint, deliverable, ship | phase, output, complete |
| advisor specification | (cite removed; restate the requirement in plain words) |

---

## Section 2 - Figures and Tables Convention

### 2.1 · Which tool? (decision rule)

| Content | Tool | Output |
|---|---|---|
| **UML** — sequence, class, component, activity, state, use-case | **Mermaid** (`.mmd`) | PNG via `render-mermaid.sh` |
| **Everything else visual** — block diagrams, flows, ERDs, star schema, swim-lanes, wireframes, pictograms, statistical sketches, KPI cards | **draw.io** (`.drawio`) | PNG via `drawio -x -f png -e` |
| **Tabular / matrix data** — comparisons, traceability, coverage, requirements, field lists | **LaTeX table** (`tabularx`) | inline |

Rule of thumb: if the content is a *grid of values or ✓/✗ cells*, it is a **table**, not a figure. Don't draw a matrix as boxes.

Every source file is checked into `report/images/diagrams/` and listed in Appendix C.

---

### 2.2 · Visual house style (shared by Mermaid + draw.io)

| Element | Value |
|---|---|
| Font | Helvetica / Arial (sans-serif) |
| Font sizes | 12–13 pt node titles · 11 pt body/attributes · 10 pt edge labels & legends |
| Fills | **White** everywhere. One pastel band (`#E1E0F2`) is allowed **only** for ERD / star-schema entity headers |
| Strokes | Thin black (`#000000`, ~1 px), **uniform weight** — hierarchy comes from nesting, not line weight |
| Corners | **Slightly rounded** (`rounded=1`, arcSize 6–10). Never sharp, never bubbly |
| Colour | **None.** No accent fills, no coloured arrows. Monochrome only |
| Secondary text | Italic, mid-grey (`#666666`) — date ranges, sizes, §-refs, qualifiers |
| Containers / groups | Thin **dashed** black rectangle, no fill, italic label at **top-left** |
| Arrows | Open arrowhead (`endArrow=open;endFill=0`), thin black; dashed for events/returns/secondary flows |
| Edge labels | Italic, 10 pt, white background (`labelBackgroundColor=#FFFFFF`) to avoid line collisions |
| Legend | One short italic-grey strip at the bottom, only if a convention isn't obvious |

**Forbidden:** colour fills, drop shadows, 3-D, gradients, icons/clip-art, UML stereotypes in non-UML diagrams (`«component»` etc. — those belong only inside actual UML).

---

### 2.3 · Figure rules

1. **One focal point.** The reader's eye should land on the protagonist first (heavier *border*, not colour; or position; or a small black event dot).
2. **Horizontal, not vertical.** Target aspect ratio **≈ 2:1 to 3:1 wide**. The report column is wide; tall figures fit weirdly and waste vertical space. If a flow has many steps, lay it left-to-right; wrap to a second row before going tall.
3. **Zero overlap — verify every render.** No box may touch another box; no line may cross through a box. Re-open the PNG and check before moving on. Leave ≥40 px between major elements and ≥20 px inside a container edge.
4. **Cap complexity.** ≤12 boxes and ≤16 edges per figure. Beyond that, group into sub-containers or split into two figures (passes the 3–8 second readability gate).
5. **Scope down.** Show the spine of the story, not the whole universe. (ERD shows the 8 join-spine tables, not all 24 — the rest lives in Appendix A.)
6. **`\includegraphics[width=0.7–0.95\linewidth]`** centred. Wider figures use a larger fraction; never exceed `\linewidth`.

---

### 2.4 · Table rules

1. **`booktabs` discipline:** horizontal rules only (`\hline` / `\toprule`-style). **No vertical rules ever.**
2. **Column count:** keep to ≤6 content columns. If a matrix needs 14 columns, **transpose it** (questions as rows, themes as columns) or rotate headers with `\rotatebox{60}{...}`.
3. **Density:** `\footnotesize` + `\renewcommand{\arraystretch}{1.2–1.3}`. If a table runs >½ page of dense reference rows, **move it to an appendix** and leave a one-line cross-reference in the body.
4. **Width:** `\begin{tabularx}{\linewidth}{...}` with one `X` column absorbing the free text; fixed `p{}` widths for short columns.
5. **No duplicate data:** a value lives in exactly one table. If two tables share a column, drop it from the secondary one and cross-reference.
6. **Emphasis:** bold the selected/winning row; never use colour to highlight.
7. **Merge over split:** prefer one table with a `\multicolumn` sub-header (e.g. *Functional* / *Non-functional*) over two near-identical tables.

---

### 2.5 · Captions

| | Figures | Tables |
|---|---|---|
| Position | **Below** the figure | **Above** the table |
| Length | **One sentence.** State what it shows, not how it's drawn | One sentence |
| Forbidden | Step-by-step narration, line-style legends ("solid arrows are…"), colour keys — put those *inside* the figure or in body text | Same |
| Cross-ref | Every figure/table is referenced by `\ref` in the prose before it appears | Same |

Good: *"Source-schema relationships across the AFC family, the GPS family, and the shared masters."*
Bad: *"…Solid arrows are foreign keys; the red dashed link is the canonical cross-source join on route\_no; thin dashed lines join the two families…"* (→ move to the diagram legend / body).

---

### 2.6 · Workflow

```bash
cd report/images/diagrams

# draw.io  →  PNG (keeps the .drawio editable)
drawio -x -f png -e -b 10 -o NAME.png NAME.drawio

# Mermaid  →  PNG (monochrome theme, system Chrome)
mmdc -i NAME.mmd -o NAME.png -p ~/.puppeteer-config.json -b transparent -s 2
./render-mermaid.sh        # renders every .mmd at once
```

After every render: **open the PNG and visually confirm zero overlaps** before
embedding. Update Appendix C (`AppendixC_ImageInventory.tex`) when a figure's
source format changes (drawio ↔ mermaid).

---

### 2.7 · Quick checklist (before committing a figure/table)

- [ ] Right tool (UML→mermaid · visual→drawio · grid→LaTeX table)
- [ ] White fills, thin uniform black strokes, slight rounding, **no colour**
- [ ] Wider than tall (≈2:1+)
- [ ] **Zero overlapping** — verified on the rendered PNG
- [ ] ≤12 boxes / ≤16 edges; scoped to the story
- [ ] Caption is one sentence (below figure / above table)
- [ ] Tables: no vertical rules, ≤6 columns, `\footnotesize`
- [ ] Referenced by `\ref` in the prose
- [ ] Source checked in + Appendix C updated
