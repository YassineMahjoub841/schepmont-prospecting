# CLAUDE.md — Ohio Manufacturing H-1B Sponsorship Intelligence

## Project overview

A 4-week portfolio project that builds an end-to-end data pipeline and dashboard surfacing H-1B sponsorship activity among Ohio manufacturers. Designed to demonstrate data-engineering-adjacent analyst skills (Terraform, Kestra, dbt, BigQuery, Looker Studio) for a job application to **Schepmont Group**, a small Ohio-based manufacturing recruitment firm.

**Read `BUSINESS.md` before making any product decision.** It is the source of truth for what each metric means and why it matters. CLAUDE.md only covers *how* to build; BUSINESS.md covers *why*.

## Scope constraints (do not violate without explicit discussion)

- **Geography**: Ohio worksites only.
- **Sector**: Manufacturing NAICS codes `31`, `32`, `33` only.
- **Time**: US fiscal year 2025 (Oct 2024 – Sep 2025). Four quarters of LCA data.
- **Data source**: DOL LCA Disclosure Data only. Do NOT add USCIS Employer Data Hub, BLS OEWS, or scrape anything — they were deliberately cut from scope.
- **Case status**: Certified LCAs only (filter out withdrawn / denied at staging, except where needed for approval-rate calculation).
- **Visa class**: H-1B only (exclude H-1B1, E-3).
- **Timeline**: 4 weeks total. Cut features before slipping deadline.

## Tech stack

| Layer | Tool | Notes |
|-------|------|-------|
| IaC | Terraform | Provision GCS bucket + BigQuery dataset only |
| Orchestration | Kestra | Self-hosted via Docker Compose |
| Ingestion | Python 3.11 | Pandas + Requests; uses GCP Application Default Credentials |
| Storage (raw) | GCS | One prefix per quarter, Parquet format |
| Warehouse | BigQuery | Single dataset; schemas: `raw`, `staging`, `intermediate`, `marts` |
| Transform | dbt-bigquery | Three layers: staging → intermediate → marts |
| Viz | Looker Studio | Free tier, direct BigQuery connector |

## Repo layout

```
.
├── CLAUDE.md
├── BUSINESS.md
├── README.md
├── terraform/
│   ├── main.tf
│   ├── variables.tf
│   └── outputs.tf
├── kestra/
│   ├── docker-compose.yml
│   └── flows/
│       └── ingest_lca_quarterly.yml
├── ingestion/
│   ├── download_lca.py
│   ├── normalize_columns.py
│   └── upload_to_gcs.py
├── dbt/
│   ├── dbt_project.yml
│   ├── profiles.yml.example
│   ├── models/
│   │   ├── staging/
│   │   ├── intermediate/
│   │   └── marts/
│   ├── seeds/
│   │   ├── naics_manufacturing.csv
│   │   └── employer_aliases.csv
│   └── tests/
└── docs/
    ├── architecture.png
    └── case_study.md
```

## Data source

- **DOL LCA Disclosure Data**, quarterly Excel files from https://www.dol.gov/agencies/eta/foreign-labor/performance
- File pattern: `LCA_Disclosure_Data_FY2025_Q[1-4].xlsx`
- ~250 columns per file; we keep ~25. Mapping lives in `ingestion/normalize_columns.py`.
- Files are 100–300 MB. Download once, cache in GCS, never re-download.

## Filtering rules applied at the staging layer

1. `worksite_state = 'OH'`
2. `naics_code` starts with `31`, `32`, or `33`
3. `visa_class = 'H-1B'`
4. Drop rows with null `employer_name` or null `wage_rate_of_pay_from`
5. Keep `case_status` in (`Certified`, `Denied`, `Withdrawn`) — denied/withdrawn needed only for approval-rate calculation; certified-only filter happens at the marts layer

## Sponsorship likelihood score (core business logic)

The headline metric. Lives in `marts/mart_sponsorship_likelihood.sql`. Computed per employer:

```
score = 0.4 * frequency_norm + 0.3 * recency_norm + 0.3 * approval_rate_norm
```

- `frequency` = count of LCA filings in FY2025
- `recency` = quarters since most recent filing, inverted so recent = high
- `approval_rate` = certified ÷ total filings
- Each component min-max normalized to 0–1, final score rescaled to 0–100

DO NOT change the weights without also updating `BUSINESS.md` and `docs/case_study.md`. The weights are an explicit product decision, not a tunable hyperparameter.

## Naming conventions

- dbt models: `stg_`, `int_`, `dim_`, `fact_`, `mart_` prefixes
- Snake_case for all column and file names
- Employer-name normalization happens in `int_employers_normalized.sql`:
  - Strip suffixes: ` Inc`, ` LLC`, ` Corp`, ` Co`, ` Ltd`, `, Inc.`, ` Ltd.`
  - Title-case
  - Trim and collapse whitespace
  - Apply manual aliases from `seeds/employer_aliases.csv` (e.g., "Honda of America Mfg" → "Honda Manufacturing of America")

## Required dbt tests

At minimum, every mart model must have:
- `unique` and `not_null` tests on its primary key
- `not_null` on any FK column
- `accepted_values` test on `case_status` in staging
- `relationships` test from facts to dimensions

## Commands

```bash
# Terraform
cd terraform && terraform init && terraform plan && terraform apply

# Start Kestra
docker compose -f kestra/docker-compose.yml up -d

# Trigger an ingestion run manually (from Kestra UI at localhost:8080 or):
curl -X POST http://localhost:8080/api/v1/executions/h1b/ingest_lca_quarterly \
  -F "quarter=Q1" -F "fiscal_year=2025"

# Run dbt
cd dbt && dbt deps && dbt seed && dbt run && dbt test

# Run a single model
dbt run --select mart_sponsorship_likelihood
```

## Definition of done (per week)

- **Week 1**: One quarter ingested end-to-end via Kestra; raw table visible in BigQuery.
- **Week 2**: All 4 quarters ingested; staging + intermediate models built and passing tests.
- **Week 3**: Marts models built and tested; Looker Studio dashboard with 3 pages published and shared.
- **Week 4**: README, Loom walkthrough, one-page case study, public dashboard link — all committed.

## Things to actively avoid

- Re-downloading source files. Cache in GCS.
- Storing credentials in code. Use ADC or env vars only. `.env` is gitignored.
- Over-engineering. This is a 4-week portfolio project, not a production system.
- Adding new data sources. The narrative is intentionally focused on one.
- Custom Python or JS visualizations. Looker Studio only for the dashboard.
- Touching anything outside the Ohio + FY2025 + manufacturing slice without first updating CLAUDE.md and BUSINESS.md.

## Current status

- [ ] Week 1 — Infrastructure + ingestion vertical slice
- [ ] Week 2 — Full ingest + dbt staging/intermediate
- [ ] Week 3 — dbt marts + Looker Studio dashboard
- [ ] Week 4 — README + Loom + case study + public deployment
