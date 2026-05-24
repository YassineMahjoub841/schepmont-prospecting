"""Download a single quarter of DOL LCA Disclosure Data to a local path.

Idempotent: if the destination exists and is non-empty, the download is
skipped. This mirrors the CLAUDE.md rule "download once, cache forever".
"""
import argparse
import os
import sys
from pathlib import Path

import requests


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--quarter", required=True, choices=["Q1", "Q2", "Q3", "Q4"])
    parser.add_argument("--fiscal-year", required=True)
    parser.add_argument("--out", required=True, help="Local output path for the .xlsx file.")
    args = parser.parse_args()

    template = os.environ.get("LCA_SOURCE_URL_TEMPLATE")
    if not template:
        print("LCA_SOURCE_URL_TEMPLATE env var is not set.", file=sys.stderr)
        return 1

    url = template.format(quarter=args.quarter, fiscal_year=args.fiscal_year)
    out = Path(args.out)

    if out.exists() and out.stat().st_size > 0:
        print(f"{out} already exists ({out.stat().st_size:,} bytes); skipping download.")
        return 0

    out.parent.mkdir(parents=True, exist_ok=True)
    print(f"Downloading {url} -> {out}")

    with requests.get(url, stream=True, timeout=300) as r:
        r.raise_for_status()
        with open(out, "wb") as f:
            for chunk in r.iter_content(chunk_size=1 << 20):
                f.write(chunk)

    print(f"Downloaded {out.stat().st_size:,} bytes.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
