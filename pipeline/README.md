# pipeline — data warehouse

The data warehouse: it cleans and aggregates the incoming AFC and GPS data into chart-ready tables.
The data is dynamic and continuously growing, so the warehouse is built to ingest new batches and
extend, not to process a fixed snapshot.

**Status: scaffold only.** Currently a CLI stub plus `duckdb`/`polars`/`pyarrow`. The dbt + Dagster
design below is not built yet; the deps are not added. Full design:
`docs/specs/2026-06-04-phase2-s1-rearchitecture-design.md`; GCP setup: `docs/specs/bigquery-deployment.md`.

## Stack and tooling

- **dbt** for the transforms (the warehouse models + data tests) · **Dagster** + dagster-dbt for
  orchestration (software-defined assets, asset checks, freshness sensors, lineage).
- **BigQuery** is the primary engine (`bq_dev` sampled · `bq_prod` full); **DuckDB** is an offline
  local sampling target. Source parquet is staged to **GCS**; Bronze is BigQuery external tables.
- **uv** for deps/build · **ruff** · **mypy** · **pytest** (warehouse integrity + asset-check tests).

## Design principles

Storage is separated from compute, with **dbt as the portability seam** — the same models run on
BigQuery and on the local DuckDB target.

- **Medallion model:** Bronze sources → **Silver Kimball star** (`dim_*` tables + `fact_*` views) →
  **Gold** aggregates (`agg_*`, one per chart contract). Fact and Gold are partitioned by `day` and
  clustered by `route_no`/`fare_class`; the production path is incremental.
- **Micro-batch ingestion:** new data lands in GCS, a Dagster **sensor** triggers an incremental dbt
  run, and new `day` partitions are appended. Dashboard freshness is hours, not seconds.
- **Integrity as checks that block the build:** dbt tests (unique · not_null · relationships ·
  accepted_values), a **relative lossless** test (`Gold boardings == Bronze ticket count`, computed
  each run, never a fixed number), and a **validation gate** (row-count regression · null-rate
  ceiling · referential integrity · PK uniqueness) surfaced as Dagster asset checks.
- **Granular, orchestrator-ready tasks:** `ingest`, `silver`, `gold`, `validate` are independently
  callable, not one monolith.

## Directory (target)

```
pipeline/
├── dbt/                         # dbt project: the warehouse transforms + data tests
│   ├── dbt_project.yml
│   ├── profiles.yml             # bq_dev / bq_prod targets + a duckdb local target
│   └── models/{bronze,silver,gold}/   # sources.yml · dim_*/fact_*.sql · agg_*.sql · schema.yml (tests)
├── src/busanalytics_pipeline/
│   ├── config.py                # paths + env
│   ├── definitions.py           # Dagster: dbt assets, resources, asset checks, sensors
│   ├── assets.py                # @dbt_assets + lossless check + preprocess asset
│   ├── preprocess/              # raw CSV → parquet
│   └── validate/                # lossless + the validation gate
├── tests/                       # pytest: dbt build + asset-check + lossless integration
└── pyproject.toml               # + dbt · dagster · dagster-dbt
```

Current scaffold: `src/busanalytics_pipeline/cli.py` + `tests/test_cli.py`.

## Build (once GCP is configured)

```bash
uv sync
dbt build --target bq_dev        # builds the star + Gold in BigQuery, runs all tests
uv run pytest -q                 # warehouse integrity (lossless chain + asset checks)
```

Until then the backend reads `db/bus.duckdb`, built by `demo/` (`make warehouse`).
