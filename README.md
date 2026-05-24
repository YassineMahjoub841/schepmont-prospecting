# Ohio Manufacturing H-1B Sponsorship Intelligence

End-to-end data pipeline and Looker Studio dashboard ranking Ohio manufacturers
by their H-1B sponsorship activity in US fiscal year 2025.

See **[BUSINESS.md](BUSINESS.md)** for what the metrics mean and why they matter.

## Stack

Terraform · Kestra · Python · GCS · BigQuery · dbt · Looker Studio

## Week 1 — run the vertical slice

Provisions GCP infrastructure and ingests one quarter of LCA data into BigQuery
as a raw external table.

1. **Prerequisites**: GCP project with billing enabled, `gcloud` CLI,
   Terraform `>= 1.6`, Docker.

2. **Provision infra**

   ```bash
   cd terraform
   cp terraform.tfvars.example terraform.tfvars  # edit values
   terraform init
   terraform apply
   ```

3. **Create a key for the Kestra service account**

   ```bash
   gcloud iam service-accounts keys create kestra-ingestion-key.json \
     --iam-account=$(terraform -chdir=terraform output -raw kestra_service_account_email)
   ```

4. **Configure environment**

   ```bash
   cp .env.example .env  # edit values, including absolute path to the key JSON
   ```

5. **Start Kestra and trigger an ingest**

   ```bash
   docker compose -f kestra/docker-compose.yml --env-file .env up -d
   # Open http://localhost:8080, upload kestra/flows/ingest_lca_quarterly.yml,
   # upload the ingestion/ folder as namespace files for namespace `h1b`,
   # then trigger an execution with quarter=Q1.
   ```

6. **Verify in BigQuery**

   ```sql
   SELECT case_status, COUNT(*)
   FROM `<project>.h1b_ohio_mfg.raw_lca_disclosure`
   GROUP BY 1;
   ```

## Roadmap

| Week | Deliverable |
|------|-------------|
| 1 | Infra + one-quarter vertical slice |
| 2 | All four quarters + dbt staging/intermediate |
| 3 | dbt marts + Looker Studio dashboard |
| 4 | README polish + Loom walkthrough + case study |
