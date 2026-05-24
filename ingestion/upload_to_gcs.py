"""Upload a normalized Parquet to gs://{bucket}/raw/fy={fy}/q={q}/data.parquet.

The fy=/q= path layout is Hive-style so BigQuery picks them up as partition
columns on the external table (see register_raw_table.py).
"""
import argparse
import os
import sys
from pathlib import Path

from google.cloud import storage


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--in", dest="in_path", required=True)
    parser.add_argument("--fiscal-year", required=True)
    parser.add_argument("--quarter", required=True, choices=["Q1", "Q2", "Q3", "Q4"])
    args = parser.parse_args()

    bucket_name = os.environ.get("GCS_BUCKET")
    if not bucket_name:
        print("GCS_BUCKET env var is not set.", file=sys.stderr)
        return 1

    in_path = Path(args.in_path)
    blob_path = f"raw/fy={args.fiscal_year}/q={args.quarter}/data.parquet"

    client = storage.Client()
    bucket = client.bucket(bucket_name)
    blob = bucket.blob(blob_path)
    blob.upload_from_filename(str(in_path))

    print(f"Uploaded {in_path} -> gs://{bucket_name}/{blob_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
