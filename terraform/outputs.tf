output "raw_bucket_name" {
  description = "GCS bucket for raw LCA Parquet."
  value       = google_storage_bucket.raw.name
}

output "dataset_id" {
  description = "BigQuery dataset ID."
  value       = google_bigquery_dataset.warehouse.dataset_id
}

output "kestra_service_account_email" {
  description = "Generate a JSON key for this account and mount it into the Kestra container."
  value       = google_service_account.kestra_ingestion.email
}

output "project_id" {
  value = var.project_id
}
