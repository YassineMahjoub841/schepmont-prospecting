provider "google" {
  project = var.project_id
  region  = var.region
}

# Raw landing zone for quarterly LCA Parquet. Versioning is on as cheap
# insurance against accidental delete; CLAUDE.md says "download once, cache
# forever", so no lifecycle rules.
resource "google_storage_bucket" "raw" {
  name                        = var.bucket_name
  location                    = var.region
  uniform_bucket_level_access = true
  force_destroy               = false

  versioning {
    enabled = true
  }
}

# Single dataset containing raw + (later) staging/intermediate/marts.
# Tables inside the dataset are owned by ingestion code and dbt, not Terraform.
resource "google_bigquery_dataset" "warehouse" {
  dataset_id                 = var.dataset_id
  location                   = var.region
  delete_contents_on_destroy = false
}

# Dedicated identity for Kestra to authenticate to GCP. Least privilege via
# the IAM bindings below.
resource "google_service_account" "kestra_ingestion" {
  account_id   = var.kestra_sa_name
  display_name = "Kestra LCA ingestion"
  description  = "Writes raw LCA Parquet to GCS and registers external tables in BigQuery."
}

resource "google_storage_bucket_iam_member" "kestra_bucket_writer" {
  bucket = google_storage_bucket.raw.name
  role   = "roles/storage.objectAdmin"
  member = "serviceAccount:${google_service_account.kestra_ingestion.email}"
}

resource "google_bigquery_dataset_iam_member" "kestra_dataset_editor" {
  dataset_id = google_bigquery_dataset.warehouse.dataset_id
  role       = "roles/bigquery.dataEditor"
  member     = "serviceAccount:${google_service_account.kestra_ingestion.email}"
}

# jobUser is a project-level role; dataEditor alone cannot run jobs.
resource "google_project_iam_member" "kestra_job_user" {
  project = var.project_id
  role    = "roles/bigquery.jobUser"
  member  = "serviceAccount:${google_service_account.kestra_ingestion.email}"
}
