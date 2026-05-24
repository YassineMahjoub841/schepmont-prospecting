variable "project_id" {
  description = "GCP project ID."
  type        = string
}

variable "region" {
  description = "Region for the GCS bucket and BigQuery dataset. Must match across both or BigQuery refuses to read the GCS files."
  type        = string
  default     = "europe-west9"
}

variable "bucket_name" {
  description = "Globally unique GCS bucket name for raw LCA Parquet."
  type        = string
}

variable "dataset_id" {
  description = "BigQuery dataset ID. dbt creates schema-suffixed children inside this dataset in later weeks."
  type        = string
  default     = "h1b_ohio_mfg"
}

variable "kestra_sa_name" {
  description = "Account ID for the Kestra ingestion service account."
  type        = string
  default     = "kestra-ingestion"
}
