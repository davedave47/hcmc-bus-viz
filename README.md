# HCMC Bus Analytics

An analytical & visualisation platform over Ho Chi Minh City's historical bus data —
~17.9 M AFC boarding events per quarter plus GPS telemetry — turning the GPS + AFC
record into operational insight for planners, operators, and passengers. Schools and
students are the analytical focus; the Tết 2026 network shock is the proof-of-value case.

> **Status.** Phase 1 delivered: a running prototype ([demo/](demo/)) over a Medallion
> DuckDB warehouse, plus the Phase-1 report ([report/](report/)). **Phase 2 is underway** —
> re-architecting the prototype into a professional application: a FastAPI **data API** +
> a **React/Vite/TypeScript** SPA, with the data pipeline, backend, and frontend split into
> independent packages. See the design specs in [docs/specs/](docs/specs/).

## Repository layout

| Path | What |
| --- | --- |
| [demo/](demo/) | Phase-1 prototype — FastAPI + Jinja2 + HTMX + Plotly over the warehouse. See [demo/README.md](demo/README.md). *(Phase 2 replaces this with `pipeline/` + `backend/` + `frontend/`.)* |
| [src/](src/) | Bronze loader (`duckdb_loader.py`) — registers the 24 raw views in `db/bus.duckdb`. |
| [notebooks/](notebooks/) | Exploratory EDA + programmatic profiling (the evidence base). |
| [report/](report/) | Phase-1 report (LaTeX, xelatex + biber). |
| [deck/](deck/) | Phase-1 defence deck (`capstone_defence.pptx` is the source of truth) + assets. |
| [docs/](docs/) | `specs/` design specs · `diagrams/` draw.io sources · `conventions/` · `reference/` papers · `project/` brief/rubric/goals. |
| `data/`, `db/` | Raw inputs + the built DuckDB warehouse (gitignored; the pipeline↔app contract). |
| [CLAUDE.md](CLAUDE.md) | The durable project log — locked decisions, data invariants, current state. |

## Quick start (Phase-1 prototype)

Requires Python 3.12+. From the repo root:

```bash
make install      # create .venv and install demo dependencies
make build        # (re)build the Silver+Gold warehouse in db/bus.duckdb (~5s)
make run          # serve at http://localhost:8000
```

`db/bus.duckdb` is opened read-only at serve time; stop the server before rebuilding
(`make stop`). Full architecture, API surface, and benchmarks: [demo/README.md](demo/README.md).

## Documentation

- **Project log & decisions:** [CLAUDE.md](CLAUDE.md)
- **Chart catalogue (the chart truth):** [docs/specs/chart-catalogue.md](docs/specs/chart-catalogue.md)
- **Report:** [report/main.pdf](report/main.pdf)
- **Conventions:** [docs/conventions/](docs/conventions/) (report writing · diagrams)
