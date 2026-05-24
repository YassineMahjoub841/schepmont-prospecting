"""Select and rename the ~25 columns we use from the DOL LCA workbook.

All rows are kept here. Geography / sector / visa-class filtering happens at
the dbt staging layer per CLAUDE.md.

Output is a snake_case-columned Parquet file suitable for an external
BigQuery table.
"""
import argparse
import sys
from pathlib import Path

import pandas as pd


# Source DOL column -> snake_case warehouse column.
# Confirm against the actual FY2025 workbook before first run; DOL renames
# a handful of columns between releases.
COLUMN_MAP: dict[str, str] = {
    "CASE_NUMBER":            "case_number",
    "CASE_STATUS":            "case_status",
    "RECEIVED_DATE":          "received_date",
    "DECISION_DATE":          "decision_date",
    "VISA_CLASS":             "visa_class",
    "JOB_TITLE":              "job_title",
    "SOC_CODE":               "soc_code",
    "SOC_TITLE":              "soc_title",
    "FULL_TIME_POSITION":     "full_time_position",
    "BEGIN_DATE":             "employment_begin_date",
    "END_DATE":               "employment_end_date",
    "EMPLOYER_NAME":          "employer_name",
    "EMPLOYER_CITY":          "employer_city",
    "EMPLOYER_STATE":         "employer_state",
    "NAICS_CODE":             "naics_code",
    "WORKSITE_CITY":          "worksite_city",
    "WORKSITE_COUNTY":        "worksite_county",
    "WORKSITE_STATE":         "worksite_state",
    "WORKSITE_POSTAL_CODE":   "worksite_postal_code",
    "WAGE_RATE_OF_PAY_FROM":  "wage_rate_of_pay_from",
    "WAGE_RATE_OF_PAY_TO":    "wage_rate_of_pay_to",
    "WAGE_UNIT_OF_PAY":       "wage_unit_of_pay",
    "PREVAILING_WAGE":        "prevailing_wage",
    "PW_UNIT_OF_PAY":         "prevailing_wage_unit_of_pay",
    "TOTAL_WORKER_POSITIONS": "total_worker_positions",
}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--in", dest="in_path", required=True)
    parser.add_argument("--out", dest="out_path", required=True)
    args = parser.parse_args()

    in_path = Path(args.in_path)
    out_path = Path(args.out_path)

    print(f"Reading {in_path}")
    df = pd.read_excel(in_path, dtype=str)
    print(f"Loaded {len(df):,} rows x {len(df.columns)} cols.")

    missing = [c for c in COLUMN_MAP if c not in df.columns]
    if missing:
        print(f"WARNING: {len(missing)} expected columns not found: {missing}", file=sys.stderr)

    keep = [c for c in COLUMN_MAP if c in df.columns]
    df = df[keep].rename(columns=COLUMN_MAP)

    out_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_parquet(out_path, index=False, compression="snappy")
    print(f"Wrote {len(df):,} rows x {len(df.columns)} cols -> {out_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
