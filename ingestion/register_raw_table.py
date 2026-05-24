"""Create-or-replace the BigQuery external table over raw GCS Parquet.

Idempotent and cheap. Reads all Parquet under raw/fy=*/q=*/ with Hive
partitioning, so new quarters drop in without further action — we re-run
this anyway after every ingest for clarity.
"""
import os
import sys

from google.cloud import bigquery


def main() -> int:
    project_id = os.environ.get("GCP_PROJECT_ID")
    dataset_id = os.environ.get("BQ_DATASET")
    bucket = os.environ.get("GCS_BUCKET")

    if not all([project_id, dataset_id, bucket]):
        print("GCP_PROJECT_ID, BQ_DATASET, GCS_BUCKET must all be set.", file=sys.stderr)
        return 1

    table_id = f"{project_id}.{dataset_id}.raw_lca_disclosure"
    client = bigquery.Client(project=project_id)

    external_config = bigquery.ExternalConfig("PARQUET")
    external_config.source_uris = [f"gs://{bucket}/raw/fy=*/q=*/*.parquet"]
    external_config.autodetect = True

    hive_opts = bigquery.HivePartitioningOptions()
    hive_opts.mode = "AUTO"
    hive_opts.source_uri_prefix = f"gs://{bucket}/raw/"
    external_config.hive_partitioning = hive_opts

    table = bigquery.Table(table_id)
    table.external_data_configuration = external_config

    client.delete_table(table_id, not_found_ok=True)
    client.create_table(table)
    print(f"Registered external table {table_id} over gs://{bucket}/raw/")
    return 0


if __name__ == "__main__":
    sys.exit(main())
