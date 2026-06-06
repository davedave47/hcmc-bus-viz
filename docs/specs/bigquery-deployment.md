# BigQuery deployment — GCP setup + env contract

The pipeline runs **BigQuery-primary**: BigQuery is the real engine for both `dev` (sampled
dataset) and `prod` (full dataset). DuckDB stays only as an optional offline `local` sampling
target. This doc is the **setup checklist** + the **environment-variable contract** the pipeline
reads. Everything here fits inside BigQuery's free tier at capstone scale (~$0).

> **Security:** the service-account key is a secret. It is **gitignored** (`*-sa-key.json`,
> `secrets/`, `.env`). Never commit it. Hand the values to the pipeline via `.env` (gitignored)
> or exported env vars — never in code or the repo.

## What to create in GCP

1. **Project** — create a GCP project (note the **project ID**, e.g. `hcmc-bus-analytics`).
   Link a **billing account** (required even for free tier; it will not charge under the limits).
2. **APIs** — enable **BigQuery API** and **Cloud Storage API**.
3. **Region** — pick one region and use it for *both* the bucket and the datasets (co-location is
   required for external tables and avoids egress). **`asia-southeast1`** (Singapore) is closest
   to Vietnam; `US` multi-region also works. Keep the bucket and datasets in the *same* location.
4. **GCS bucket** — create a bucket (note the **name**, e.g. `hcmc-bus-analytics-data`) in the
   chosen region. This is where source parquet is staged; Bronze reads it as external tables.
5. **BigQuery datasets** — create two, in the same region:
   - `busanalytics_dev` (sampled dev)
   - `busanalytics_prod` (full prod)
6. **Service account** — create one (e.g. `dbt-runner`) with these roles:
   - **BigQuery Data Editor** (create/replace tables in the datasets)
   - **BigQuery Job User** (run queries/loads)
   - **BigQuery User**
   - **Storage Object Admin** (read/write the bucket)

   Create a **JSON key** for it and download it. Put it somewhere gitignored, e.g.
   `secrets/dbt-sa-key.json` at the repo root.

## Env contract (what to hand me)

Create `.env` at the repo root (gitignored) with:

```dotenv
# GCP / BigQuery
GOOGLE_APPLICATION_CREDENTIALS=secrets/dbt-sa-key.json   # path to the SA JSON key
BQ_PROJECT=hcmc-bus-analytics            # your project ID
BQ_LOCATION=asia-southeast1              # bucket + dataset region (must match)
BQ_DATASET_DEV=busanalytics_dev
BQ_DATASET_PROD=busanalytics_prod

# GCS staging
GCS_BUCKET=hcmc-bus-analytics-data       # bucket name (no gs:// prefix)
GCS_PARQUET_PREFIX=parquet               # object prefix the parquet is staged under

# dbt target selector: bq_dev (default) | bq_prod | local
DBT_TARGET=bq_dev
```

Replace the example values with your real ones and send them over (or just fill in `.env`).
The only true secret is the **key file**; the rest are non-sensitive identifiers.

## How the pipeline uses these (built in P1a)

- **Stage parquet → GCS:** a Dagster/CLI step uploads `data/parquet/**` to
  `gs://$GCS_BUCKET/$GCS_PARQUET_PREFIX/...` (one-time / on change).
- **Bronze = external tables:** dbt sources are BigQuery external tables over the GCS parquet
  (`format = PARQUET`, `uris = gs://.../*.parquet`) — query-in-place, no load.
- **dbt targets** (`profiles.yml`): `bq_dev` → dataset `$BQ_DATASET_DEV`, `bq_prod` → `$BQ_DATASET_PROD`,
  both `type: bigquery`, `method: service-account`, `keyfile: $GOOGLE_APPLICATION_CREDENTIALS`,
  `location: $BQ_LOCATION`. Optional `local` → duckdb over local parquet (offline scratch).
- **dev sampling:** `bq_dev` builds against a sampled subset (a dbt var limiting the date range)
  so dev runs are fast/cheap; `bq_prod` builds the full dataset; the lossless test
  (`boardings == 17,883,623`) runs against the full dataset.
- **CI:** the GitHub Actions `pipeline` job needs the SA key as a repo secret to build against
  `bq_dev`; model-parse/unit tests run without it.

## Cost note

At ~17.9 M rows (sub-GB) the free tier (10 GB storage + 1 TB query/month) covers everything;
external tables over GCS incur no storage duplication. Expect ~$0 for the capstone.
