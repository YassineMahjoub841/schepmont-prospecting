# Week 1 — design decisions and open items

## Decisions locked in scaffolding

- **Region**: `europe-west9` (Paris) for both GCS bucket and BigQuery dataset.
  They must match or BQ refuses to read GCS.
- **Raw layer storage**: external BigQuery table over Hive-partitioned Parquet
  in GCS (`raw/fy=YYYY/q=QN/data.parquet`). Cheap, immutable, easy to refresh
  by dropping a new file. Staging/marts in Week 2 will be native tables.
- **Auth**: dedicated `kestra-ingestion` service account, least-privilege IAM:
  - `roles/storage.objectAdmin` on the raw bucket only
  - `roles/bigquery.dataEditor` on the dataset only
  - `roles/bigquery.jobUser` at project level (needed to run any BQ job)
  - SA key JSON mounted into the Kestra container read-only. The key file is
    gitignored; the SA email is a Terraform output.
- **Terraform owns** bucket, dataset, SA, IAM bindings. **Not** tables —
  ingestion code owns raw, dbt owns everything downstream.
- **Python scripts** are the executors; Kestra is the orchestrator. Scripts
  are independently runnable (`python ingestion/download_lca.py ...`) for
  local debugging.

## Open items to resolve during the build

- **Exact DOL URL pattern.** `.env.example` has a best-guess template; confirm
  against https://www.dol.gov/agencies/eta/foreign-labor/performance on
  first run and update if wrong.
- **Column map in `normalize_columns.py`.** The 25-column list is based on
  prior-year DOL schemas. Inspect the actual FY2025 Q1 file and adjust if
  DOL renamed anything. Missing columns produce a warning, not a failure.
- **Kestra namespace files upload.** The flow expects `ingestion/` to be
  uploaded as namespace files for `h1b`. Either do this through the Kestra
  UI on first run or add a one-shot CLI step to the README.
- **BigQuery cost**: external table reads scan the full Parquet on every
  query. With ~4 quarters at ~50MB Parquet each that's negligible, but watch
  it if the dashboard ends up issuing many concurrent queries.

## Cuts considered and rejected for Week 1

- Remote Terraform state in GCS — local state is fine for a solo project;
  revisit only if multi-machine work becomes necessary.
- Workload Identity Federation instead of SA key — overkill for local Docker.
- Inline Python in the Kestra YAML — harder to test and debug than separate
  scripts; the marginal YAML complexity isn't worth it.
