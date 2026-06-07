# HCMC Bus Analytics

An analytics and visualization platform for Ho Chi Minh City's bus network. It draws on the city's
automated fare-collection records and GPS vehicle telemetry — a stream that keeps growing as new
data arrives — and turns it into clear, operational insight for the people the network serves:
passengers, operators, and the city's transport authority. Schools and students are the analytical
focus, and the Tết 2026 network shock is the worked case study.

The platform surfaces patterns from the accumulated record rather than live positions, and is built
for data that keeps arriving rather than a one-off snapshot.

## What it answers

- **Passengers** — How reliable is a route? When is it least crowded? Does it serve my school's commute?
- **Operators** — Which routes are over- or under-served? Which are profitable? How do we compare with peers?
- **Authority** — Where does service not match ridership? Where are the coverage and equity gaps? How does the network absorb and recover from a shock?

## How it's built

Three independent parts move data from raw records to interactive charts:

- **`pipeline/`** — a data warehouse that cleans and aggregates incoming data in batches, organised in layers from raw to chart-ready.
- **`backend/`** — a service that serves chart-ready data over a simple web API.
- **`frontend/`** — a single-page web app that renders the charts and maps.

An earlier prototype lives in `demo/` and is being superseded by the three parts above.

## Repository layout

| Path | What |
| --- | --- |
| `pipeline/` | The data warehouse (ingestion and aggregation). |
| `backend/` | The data API. |
| `frontend/` | The web app. |
| `demo/` | The earlier prototype and the current local data source. |
| `notebooks/` | Exploratory data analysis. |
| `report/` | The project report. |
| `deck/` | The presentation deck. |
| `docs/` | Design specifications, conventions, and reference material. |
| `data/`, `db/` | Raw inputs and the local warehouse (not checked in). |

## Running it locally

```bash
# data API (port 8000)
cd backend && uv run uvicorn busanalytics_api.main:app --port 8000

# web app (port 5173, talks to the API)
cd frontend && pnpm dev
```

Open http://localhost:5173 in a browser.

## Learn more

- The full set of charts and what each one shows: `docs/specs/chart-catalogue.md`
- The project report: `report/main.pdf`
