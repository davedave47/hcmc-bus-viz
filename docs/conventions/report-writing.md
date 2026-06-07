# Report Style Guide: HCMC Bus Analytics Report

The single source of truth for every writing, figure, and table decision in the
report.

## Section 1. Global conventions (applies to every section)

### 1.1 Voice and register

The report is a third-person academic document addressed to an external marker. It is not addressed to the student, the advisor, or to the assistant that wrote earlier drafts.

The following are forbidden in the body of the report:

1. Meta-commentary about the document. The sentence "This section presents the motivation, scope, and outline" is not allowed. The section title is the meta-commentary; nothing more is needed.
2. Forward references in the abstract or in chapter introductions of the form "Section 4 develops the dashboard". A single chapter-outline paragraph at the end of Chapter 1 is allowed; otherwise, forward references appear at the end of paragraphs only where they add value.
3. Product names. The word "BusLens" never appears. The word "card" in the sense of a dashboard tile never appears. The word "lens" never appears. The word "hub" in the sense of an overview index appears only as a generic noun.
4. Internal acronyms. The acronyms "SDVF", "A1", "A2", "A3" never appear. The underlying concepts are renamed: prioritization among proposed modules is presented as a comparison table; the three interaction-design choices are presented under their academic names (Multiple Coordinated Views, visual storytelling, entity-detail interaction pattern).
5. File paths. The strings `src/duckdb_loader.py`, `docs/design/app-layouts.html`, `notebooks/01_*.ipynb`, and any other source-tree path do not appear in the body. They are confined to Appendix A.
6. Citations of internal documents. The bibliography entries `rubric`, `capstoneDescription`, and `thoai2025` are deleted. No section refers to the grading rubric in any form. The capstone topic is restated in the student's own words once in Chapter 1; the document is not cited.
7. Conversational phrasing. The phrases "wired into", "anchored to data narratives", "the differentiator", "table-stakes", "deliverables", "feature bundle" are removed. Replace with formal alternatives: "implemented as", "organized around", "the principal contribution", "essential capabilities", "outputs". No phrasal verbs.
8. Never dump your thoughts like "the data is **dynamic / continuously-growing**, neve"historical/static". The ~17.9 M AFC rows are the **current dev sample**, not a fixed or headline number — all counts are relative and recomputed each run (invariant #14). See memory `feedback_dynamic_data_framing`.". This is AI thoughts narrative and should never be written.
9. Phrasing like ""Column widths and spacing (the anti-"stupid-table" rules)" is banned because the reader does not care about additional names that is only mentioned once like "(the anti-"stupid-table" rules)". Do not write things if it adds no impact or meaningful value
10. No defensive over-explaining like non-choice defense if it has no impact to stop raising questions, just explain why you choose something and non-choice only appears in numbered evaluation and metrics.
11. Be as low context as possible, the audience are council with zero context of our discussion nor transit knowledge, don't mention Phase 1 or our internal discussions.

### 1.2 Typographic conventions

1. The em dash character "—" is forbidden. Replace with comma, semicolon, parentheses, or rewrite the sentence.
2. The `\paragraph{...}` command is forbidden. Replace with one of: a plain paragraph whose first sentence is the topic sentence; a plain paragraph followed by `\begin{itemize}` or `\begin{enumerate}`; a numbered subsection if the content justifies it.
3. Every abbreviation is expanded on first use: "Automated Fare Collection (AFC)", "Global Positioning System (GPS)", "Quality of Service (QoS)", "Multiple Coordinated Views (MCV)", "Uniform Manifold Approximation and Projection (UMAP)", "Hexagonal hierarchical geospatial indexing system (H3)". Subsequent uses are the abbreviation only.
4. Captions follow §2.5 (one sentence; name the object, not the finding).
5. Float placement is `[!htbp]` for every figure and table. The `[H]` placement (from the `float` package) is removed. LaTeX is allowed to reorder floats to avoid large blank pages.
6. Heading depth is capped at `\subsection`. The structure is **chapter → section → subsection and stops there**, with no `\subsubsection` and no `\paragraph`. A subsection must earn its heading (a distinct sub-argument, roughly half a page or more); shorter points become flowing prose under the section, with a **bold lead-in** if a label helps.
7. Math is set with `\(...\)` or `\[...\]` or `equation` environments. Plain text variables are typeset as `\(T\)`, not `T`.

### 1.3 Figure and table policy

1. **Every figure must be viewable.** A figure is a real image, rendered to PNG (draw.io) or produced by the analysis code, embedded with `\includegraphics` and confirmed to display by opening the compiled PDF. The report can carry **`\imageplaceholder` boxes** with desccription and capture guide for displaying a figure that is planned but not yet existing.
2. Large dump-style tables (the previous data-quality table, the 31-row chart catalog) are split into smaller, page-friendly tables. No single table spans more than half a page.
3. Every figure and table is introduced in the paragraph immediately before it, and the discussion that follows refers to it by `\ref{...}`. No floating tables without prose anchor.

### 1.4 Forbidden vocabulary

| Word or phrase                | Replacement                                                                     |
| ----------------------------- | ------------------------------------------------------------------------------- |
| BusLens                       | the proposed system; the proposed analytical platform; the system               |
| card (as a UI element)        | thematic view; analytical view; theme                                           |
| lens                          | analytical view; theme                                                          |
| hub                           | overview index; home page (if a UI noun is required)                            |
| Atlas-style                   | reference-style (or drop the analogy)                                           |
| editorial scroll              | vertical reading order                                                          |
| flagship                      | principal; central                                                              |
| SDVF                          | (concept dropped; replace with a justification paragraph or a comparison table) |
| A1 / A2 / A3                  | (concept kept; replace with named academic principles)                          |
| linked brushing invariant     | Multiple Coordinated Views (MCV) interaction model                              |
| story-subtitled charts        | annotated charts following visual storytelling principles                       |
| universal entity detail panel | entity-detail interaction pattern                                               |
| sprint, deliverable, ship     | phase, output, complete                                                         |
| advisor specification         | (cite removed; restate the requirement in plain words)                          |

### 1.5 Writing quality

1. No AI-typical filler: "delve into", "crucial", "it is important to note", "plays a vital role", "in today's world". Use precise, discipline-specific phrasing.
2. No throat-clearing openers. A paragraph or section opens with its claim or finding, not "In this section we discuss…".
3. Vary paragraph and sentence length. Avoid uniform four-to-five-sentence paragraphs; mix short and long.
4. Every claim is cited or supported by the project's own measured data. No unsupported assertion.
5. **No marketing or hype wording or narrative.** The report describes and evaluates; it does not sell. Banned adjectives: "powerful", "seamless", "robust", "comprehensive", "cutting-edge", "state-of-the-art", "world-class", "best-in-class", "next-generation", "revolutionary", "game-changing", "innovative", "advanced", "sophisticated", "intuitive", "effortless", "unparalleled", "industry-leading", "enterprise-grade", "holistic". Banned verbs: "leverage", "unlock", "empower", "streamline", "harness", "supercharge", "elevate", "revolutionize". State the concrete property instead: not "a powerful, scalable engine" but "serves each chart from one pre-aggregated table".
6. **Say it once (DRY).** Each definition, fact, or argument lives in exactly one place, the section that owns it, and is reached from elsewhere by `\ref`, never restated or paraphrased. A value measured once is not re-derived later in prose. When content moves to an appendix, the body keeps a one-line pointer, not a second copy. Two paragraphs that make the same point are a sign one of them is redundant.
7. **Claim strength (hedging).** Match every claim to its evidence. Use strong verbs (shows, demonstrates, establishes) only for the project's directly measured facts; moderate verbs (suggests, indicates, points to) for patterns inferred across the aggregate route-by-hour grain; weak hedges (may, might, could) for anything resting on the partial sample, the non-overlapping GPS and AFC windows, or a proxy measure. Do not hedge a measured number ("the student-fare share is 36%", not "appears to be about 36%"). Reserve causal verbs (causes, drives) for the difference-in-differences design; elsewhere write "is associated with".
8. **One term per concept.** Pick one word for each concept and repeat it; do not cycle synonyms to look varied. A chart is not also a visualization, a graphic, and a view in the same passage. Where the project gives words distinct meanings, hold them: a primitive is a chart type, a canvas is the slot it occupies, a chart is the instance. Consistent terminology is clarity, not monotony.
9. **Concision and clear reference.** Prefer the short form: "to" over "in order to", "because" over "due to the fact that", "many" over "a large number of", "can" over "has the ability to". Every "this" or "it" has an unmistakable antecedent; if a sentence opens with a bare "This", name the noun ("This mismatch", "This aggregate").

### 1.6 Mechanics: spelling, numbers, citations, tense

1. **Spelling.** American throughout: `-ize` / `-ization` (organize, visualization, prioritize, analyze), "behavior", "color", "modeling", "center", "meter", "catalog", "labeled". Never the British `-ise` / `-isation` / `-our` / `-re`.
2. **Phase framing.** Always "Phase 2", with a capital P, an Arabic digit, and a normal space. Never "Phase Two", "phase 2", or "Phase~2".
3. **Numbers.** Tables carry exact figures with thousands separators (17,883,623; ₫72,041,500,000). Prose rounds for readability ("approximately 17.9 million boardings", "about ₫72 billion", "a 36% student-fare share"). Spell out a quantity that opens a sentence, or rewrite so it does not. A measured value appears once as an exact figure; later mentions round.
4. **Citations.** Numeric biblatex style: `\cite{key}` renders as `[n]`. Place the marker at the end of the clause it supports, before the punctuation. Merge multiple keys into one marker (`[3, 5]`), never `[3][5]`. Every claim that is not the project's own measured data carries a citation.
5. **Tense.** Present tense for the system's design and the data's standing properties ("the warehouse materializes seven aggregates"; "the AFC stream records boardings only").

### 1.7 Choosing the content form: prose, list, table, figure

Prose is the default and the connective tissue; lists, tables, and figures are punctuation that prose introduces and then reads aloud. Pick the lightest form that carries the structure of the content. Once the form is a diagram or a grid, §2.1 picks the tool.

- **Paragraph (prose).** The default. Use it whenever items are joined by reasoning: cause, contrast, sequence-with-justification, qualification. Two items are a sentence ("the stream covers January and February"), never a two-row table. If dropping the connectives would lose meaning, it is prose.
- **Bulleted list (`itemize`).** Three to seven short, parallel, unordered items that need no reasoning between them: options, criteria, components, constraints. Not for two items (prose), not for items that each need a paragraph (prose with bold lead-ins), not for more than about eight (regroup or tabulate).
- **Numbered list (`enumerate`).** As above, but when order matters (steps, a procedure) or the items are referenced by number later (R1–R15, the five findings).
- **Table.** A grid: several entities (rows) described by the *same* attributes (columns). It earns its place only when the reader gains from scanning rows against columns: comparison, traceability, coverage, a field inventory. A one-column table is a list; a two-cell table is a sentence; label-then-description pairs that read fine in order are prose. This is the cure for too-many-tables: most tables in a first draft are lists or prose wearing rules.
- **Figure / diagram.** Structure that position, connection, or shape conveys better than words (architecture, sequence, schema, geography), or a quantitative pattern (a chart). Use one when the equivalent paragraph would be longer and less clear than the picture.

Two tests settle most cases:

- **Dimensions.** One set of things → a list. Things × attributes → a table. Things connected in space → a figure. Reasoning among things → prose.
- **Read or scan?** Content followed as an argument is prose; content looked up, compared, or scanned is a table or figure.

A chapter that is mostly tables, or mostly unbroken prose, is a smell: vary the form to fit the content. The §1.3.3 rule (introduce a float in the sentence before it and read its point in the sentence after) applies to lists as well.

---

## Section 2 - Figures and Tables Convention

### 2.1 · Which tool? (decision rule)

| Content                                                                                                           | Tool                                 | Output                          |
| ----------------------------------------------------------------------------------------------------------------- | ------------------------------------ | ------------------------------- |
| **All diagrams** (flows, ERDs, star schema, architecture, swim-lanes, wireframes, sequence/UML, pictograms) | **draw.io** (`.drawio`)      | PNG via `drawio -x -f png -e` |
| **Tabular / matrix data** (comparisons, traceability, coverage, requirements, field lists)                  | **LaTeX table** (`tabularx`) | inline                          |

Rule of thumb: if the content is a *grid of values or ✓/✗ cells*, it is a **table**, not a figure. Don't draw a matrix as boxes.

Diagram **sources** live in `docs/diagrams/{report,deck}/`; rendered `.png` go in
`report/images/diagrams/`. Full convention: `docs/conventions/diagrams.md`. Mermaid is legacy; migrate any remaining `.mmd` to `.drawio`.

---

### 2.2 · Visual house style (draw.io)

| Element             | Value                                                                                                                                                                                                                                                     |
| ------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Font                | Helvetica / Arial (sans-serif)                                                                                                                                                                                                                            |
| Font sizes          | 12–13 pt node titles · 11 pt body/attributes · 10 pt edge labels & legends                                                                                                                                                                             |
| Fills               | **White** by default. An accent fill is spent only to encode a layer/category (e.g. Bronze/Silver/Gold tiers) or to mark the focal node; flat and pale, never saturated                                                                             |
| Strokes             | Thin black (`#000000`, ~1 px), **uniform weight** (hierarchy comes from nesting, not line weight)                                                                                                                                                 |
| Corners             | **Slightly rounded** (`rounded=1`, arcSize 6–10). Never sharp, never bubbly                                                                                                                                                                      |
| Color               | **Limited functional palette**: grayscale base plus at most three accent hues, each encoding meaning (focal element, or a layer/category). The same category keeps the same hue across figures. Never decorative, no per-node rainbow, no gradients |
| Secondary text      | Italic, mid-gray (`#666666`) for date ranges, sizes, §-refs, qualifiers                                                                                                                                                                                |
| Containers / groups | Thin**dashed** black rectangle, no fill, italic label at **top-left**                                                                                                                                                                         |
| Arrows              | Open arrowhead (`endArrow=open;endFill=0`), thin black; dashed for events/returns/secondary flows                                                                                                                                                       |
| Edge labels         | Italic, 10 pt, white background (`labelBackgroundColor=#FFFFFF`) to avoid line collisions                                                                                                                                                               |
| Legend              | One short italic-gray strip at the bottom, only if a convention isn't obvious                                                                                                                                                                             |

**Forbidden:** decorative or saturated color, per-node rainbow, gradients, drop shadows, 3-D, icons/clip-art, UML notation in non-UML diagrams (crow's-feet, lifelines, `«component»` stereotypes belong only inside actual UML).

**Color and meaning.** Color is a data channel, not decoration. The grayscale base carries everything structural; an accent hue is spent only where it carries a reading. One accent marks the protagonist the figure is about, and a small categorical set (at most three hues) distinguishes families the reader must tell apart, such as the Bronze, Silver, and Gold tiers, or the GPS and AFC source families. The same category keeps the same hue in every figure. Fills stay pale and flat: no saturation, no gradient, no hue that means nothing.

**Shapes.** Shape is also a channel, so keep it consistent. A rounded rectangle is a process, service, or component; a square-cornered rectangle is a data store or table; a cylinder is a database or file store; a diamond is a decision or branch; a pill or stadium is an external actor or system boundary. One shape means one kind of thing throughout the report, and shape never varies for visual interest.

**Arrows.** A solid line with an open arrowhead is the primary data or control flow, drawn in the dominant reading direction. A dashed line is a secondary, asynchronous, or return path (an event, a sensor trigger, a fallback). Label an edge only when the relationship is not obvious, on a white background so the text does not collide with the line. Avoid double-headed arrows unless the relation is genuinely symmetric. An arrow points the way data or control actually moves.

**Sizing and readability.** Size for the printed page, not the canvas. A figure is embedded at 0.7 to 0.95 of the line width, so design the canvas so that at that scale node titles land near 11 to 12 pt on paper and the smallest label stays at or above about 9 pt. If the figure must shrink below that to fit, it holds too much: split it or raise its abstraction level. Leave generous whitespace (at least 40 px between major elements at canvas scale), since crowding is the main readability killer. Open the embedded figure in the compiled PDF and confirm every label is comfortably legible before committing.

**UML.** Where a UML type fits the content (class, sequence, component, state, entity-relationship), use its standard notation correctly: compartmented class boxes (name, attributes, operations), sequence lifelines with activation bars and solid-call and dashed-return messages, component sockets and lollipops, ER entities with crow's-foot multiplicity. Render that notation in the house rules above, the limited palette and the sizing budget included. Do not import textbook UML coloring or decorative stereotypes; a stereotype such as «interface» appears only when it carries information. UML notation never leaks into a non-UML diagram.

---

### 2.3 · Figure rules

1. **One focal point.** The reader's eye should land on the protagonist first (heavier *border*, not color; or position; or a small black event dot).
2. **Horizontal, not vertical.** Target aspect ratio **≈ 2:1 to 3:1 wide**. The report column is wide; tall figures fit weirdly and waste vertical space. If a flow has many steps, lay it left-to-right; wrap to a second row before going tall.
3. **Zero overlap: verify every render.** No box may touch another box; no line may cross through a box. Re-open the PNG and check before moving on. Leave ≥40 px between major elements and ≥20 px inside a container edge.
4. **Cap complexity.** ≤12 boxes and ≤16 edges per figure. Beyond that, group into sub-containers or split into two figures (passes the 3–8 second readability gate).
5. **Scope down.** Show the spine of the story, not the whole universe. (ERD shows the 8 join-spine tables, not all 24; the rest lives in Appendix A.)
6. **`\includegraphics[width=0.7–0.95\linewidth]`** centered. Wider figures use a larger fraction; never exceed `\linewidth`.
7. **Labels match the diagram's abstraction level, consistently.** Pick one level of detail and hold every node to it. A context diagram may say "Serving API" and "Warehouse"; a component diagram names the concrete artifacts (`agg_route_hour`, `Dagster sensor`). What is banned is a *placeholder* that carries no information at the chosen level (a box called only "Process", "Data", or "Module" when the diagram is about something more specific), and mixing one vague box in among otherwise concrete ones.
8. **One reading direction.** The eye follows a single dominant flow, left-to-right or top-to-bottom. No hub-and-spoke layout where everything radiates from a center box; no hairball where most nodes connect to most others. If the relationships are genuinely that dense, the figure does too much; split it.
9. **No decoration.** Nothing on the canvas is ornamental: no clip-art or skeuomorphic icons (a drawn database-can, a gear, a cloud picture), no emoji, no logos, no background art, no duplicate "summary" boxes. A plain geometric cylinder used as the datastore *shape* per §2.2 is fine; a picture of a database is not. This extends the §2.2 color rule (color encodes, never decorates). Test: remove a mark; if the diagram loses no information, it should not have been there.

---

### 2.4 · Table rules

1. **`booktabs` rules:** load `\usepackage{booktabs}`; use `\toprule` (top), `\midrule` (after the header row), and `\bottomrule` (bottom), never `\hline`. **No vertical rules ever.** Use `\cmidrule(lr){...}` only to underline a `\multicolumn` sub-header.
2. **Column count:** keep to ≤6 content columns. If a matrix needs 14 columns, **transpose it** (questions as rows, themes as columns) or rotate headers with `\rotatebox{60}{...}`.
3. **Density:** `\footnotesize` + `\renewcommand{\arraystretch}{1.2–1.3}`. If a table runs >½ page of dense reference rows, **move it to an appendix** and leave a one-line cross-reference in the body.
4. **Width:** the table spans `\linewidth` via `tabularx`; how the columns divide that width is the difference between a clean table and a broken one; see *Column widths and spacing* below.
5. **No duplicate data:** a value lives in exactly one table. If two tables share a column, drop it from the secondary one and cross-reference.
6. **Emphasis:** bold the selected/winning row; never use color to highlight.
7. **Merge over split:** prefer one table with a `\multicolumn` sub-header (e.g. *Functional* / *Non-functional*) over two near-identical tables.
8. **No decorative cells.** No emoji, no status-light dots (🟢/🟡/🔴), no checkmark spam. A tick (✓) appears only in a genuine coverage or traceability matrix, at the same weight in every cell. Header names are specific ("Records", "Window", "Reason for rejection"), never catch-alls like "Details", "Notes", "Information", "Other".
9. **No filler or hype in cells.** A cell states one concrete value. It does not dodge with "Various", "Multiple", "N/A", or "TBD", and it carries no marketing adjectives. If one value repeats down every row, the column is removed and the fact is stated once in the prose (this is §1.5.6 applied to tables).
10. If a table gets too dense, normalize it into paragraph and smaller tables, never put a long and dense.

#### Column widths and spacing

The common failure is a `tabularx` where a short column eats the slack and a prose column is starved to one word per line. Width is allocated, not left to chance:

1. **Fix the bounded columns, flex only the prose.** Any column whose content is bounded (a code, a count, a tick, a date, one or two words) gets a fixed natural width (`c`, `r`, or `p{2.2cm}`). Only a genuinely free-flowing text column is `X`. This alone fixes most lopsided tables.
2. **Two or more prose columns → weight the `X`s.** Equal `X` columns split the free space evenly, which starves the denser column. Weight them so the denser gets more: a broad column is `>{\hsize=1.4\hsize}X`, a slim one `>{\hsize=0.6\hsize}X`, and the weights must sum to the number of `X` columns (here 1.4 + 0.6 = 2).
3. **Ragged-right in every flexible column.** Justified text in a narrow column opens ugly inter-word gaps; set `\raggedright` on each `X`/`p` column.
4. **Numbers are `r` (or siunitx `S`), never `X`.** Right-align numeric columns and align on the thousands separator; a number column is bounded, so it is never flexible.
5. **Row height and grouping.** `\renewcommand{\arraystretch}{1.25}` for breathing room; because booktabs has no interior lines, separate logical row groups with `\addlinespace` (and a `\cmidrule(lr){…}` only under a `\multicolumn` sub-header). Nudge `\tabcolsep` up on dense tables.
6. **A cell is a phrase, not a paragraph.** If a column truly needs a full sentence and cannot widen without starving its neighbors, the table is the wrong container: move that content to prose or a list, or split the table.
7. **Check the render.** No sparse column may sit wider than its content while a prose column wraps every word. If it does, the column spec is wrong, not the data.

Define the reusable column types once in the preamble (`tabularx` already loads `array`):

```latex
\newcolumntype{P}[1]{>{\raggedright\arraybackslash}p{#1}}             % fixed-width ragged text
\newcolumntype{Y}[1]{>{\hsize=#1\hsize\raggedright\arraybackslash}X}  % weighted flexible
% usage: \begin{tabularx}{\linewidth}{P{1.2cm} r Y{1.4} Y{0.6}} … (the two Y weights sum to 2)
```

---

### 2.5 · Captions

|           | Figures                                                                                                                        | Tables                    |
| --------- | ------------------------------------------------------------------------------------------------------------------------------ | ------------------------- |
| Position  | **Below** the figure                                                                                                     | **Above** the table |
| Length    | **One sentence.** State what it shows, not how it's drawn                                                                | One sentence              |
| Content   | **Names the object, not the finding** ("Boardings per fare class", not "Student fares dominate the morning peak")        | Same                      |
| Forbidden | Step-by-step narration, line-style legends ("solid arrows are…"), color keys (put those*inside* the figure or in body text) | Same                      |
| Cross-ref | Every figure/table is referenced by `\ref` in the prose before it appears                                                    | Same                      |

Good: *"Source-schema relationships across the AFC family, the GPS family, and the shared masters."*
Bad: *"…Solid arrows are foreign keys; the red dashed link is the canonical cross-source join on route\_no; thin dashed lines join the two families…"* (move to the diagram legend / body).

**Captions, chart titles, and hero text are abstract — no data specifics.** State the capability,
object, or question (e.g. "Boardings per fare class over the window"), never a data finding or a
concrete value (no route numbers, dates, or counts). The data is dynamic and continuously growing:
a caption that describes the data goes stale the moment the data changes, and rewriting captions
dynamically is high-effort, low-impact. The visual carries the specifics; the caption stays general.

---

### 2.6 · Workflow

```bash
# draw.io source (docs/diagrams/...)  ->  PNG render (report/images/diagrams/)
drawio -x -f png -e -b 10 -o report/images/diagrams/NAME.png docs/diagrams/report/NAME.drawio
```

After every render: **open the PNG and visually confirm zero overlaps** before embedding.

---

### 2.7 · Quick checklist (before committing a figure/table)

- [ ] Right tool (diagram → draw.io · grid of values → LaTeX table)
- [ ] White/gray base + limited palette (≤3 hues, each meaningful); thin uniform strokes; slight rounding; consistent shapes & arrows
- [ ] Wider than tall (≈2:1+)
- [ ] **Zero overlapping**, verified on the rendered PNG
- [ ] Legible at embedded size: smallest label ≥ ~9 pt on the page, checked in the compiled PDF
- [ ] ≤12 boxes / ≤16 edges; scoped to the story
- [ ] Labels at one abstraction level (no placeholder boxes); one reading direction; no icons/emoji/decoration
- [ ] Caption is one sentence (below figure / above table)
- [ ] Tables: booktabs rules (`\toprule`/`\midrule`/`\bottomrule`), no vertical rules, ≤6 columns, `\footnotesize`; no emoji/status-lights; specific headers (no Details/Notes/Other)
- [ ] Referenced by `\ref` in the prose
- [ ] `.drawio` source checked in to `docs/diagrams/`
