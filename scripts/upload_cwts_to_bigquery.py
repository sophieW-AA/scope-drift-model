"""
upload_cwts_to_bigquery.py
===========================
Uploads CWTS output files to BigQuery with timestamped table names.

Files uploaded:
    cwts_output/classification.txt  → classification_raw_{timestamp}
    cwts_output/pub_metadata.txt    → pub_metadata_raw_{timestamp}
    cwts_output/pubs.txt            → pubs_raw_{timestamp}
    cwts_output/cit_links.txt       → cit_links_raw_{timestamp}

Usage:
    python scripts/upload_cwts_to_bigquery.py
"""

import logging
from datetime import datetime
from pathlib import Path

import pandas as pd
from google.cloud import bigquery

# ──────────────────────────────────────────────────────────────────────────────
# CONFIG
# ──────────────────────────────────────────────────────────────────────────────
BQ_PROJECT = "ocean-tech-adv-analytics-c-tfs"
BQ_DATASET = "scope_drift_test_set"

CWTS_OUTPUT_DIR = Path(__file__).resolve().parent.parent / "cwts_output"

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s  %(message)s", datefmt="%H:%M:%S"
)
log = logging.getLogger(__name__)


# ──────────────────────────────────────────────────────────────────────────────
# File definitions
# ──────────────────────────────────────────────────────────────────────────────
FILES = {
    "classification": {
        "filename": "classification.txt",
        "columns": ["int_id", "micro", "meso", "macro"],
        "dtypes": {"int_id": int, "micro": int, "meso": int, "macro": int},
    },
    "pub_metadata": {
        "filename": "pub_metadata.txt",
        "columns": ["int_id", "pub_id", "is_frontiers", "journal", "date", "title"],
        "dtypes": {"int_id": int, "pub_id": int, "is_frontiers": int},
    },
    "pubs": {
        "filename": "pubs.txt",
        "columns": ["int_id", "core_pub"],
        "dtypes": {"int_id": int, "core_pub": int},
    },
    "cit_links": {
        "filename": "cit_links.txt",
        "columns": ["int_id1", "int_id2", "weight"],
        "dtypes": {"int_id1": int, "int_id2": int, "weight": float},
    },
}


def load_file(name: str, config: dict) -> pd.DataFrame:
    """Load a CWTS output file into a DataFrame."""
    path = CWTS_OUTPUT_DIR / config["filename"]

    if not path.exists():
        log.warning(f"  File not found: {path}")
        return None

    df = pd.read_csv(
        path,
        sep="\t",
        header=None,
        names=config["columns"],
        dtype=config.get("dtypes"),
        on_bad_lines="warn",
    )

    log.info(f"  Loaded {name}: {len(df):,} rows")
    return df


def upload_to_bigquery(df: pd.DataFrame, table_name: str, client: bigquery.Client):
    """Upload a DataFrame to BigQuery."""
    full_table = f"{BQ_PROJECT}.{BQ_DATASET}.{table_name}"

    job_config = bigquery.LoadJobConfig(
        write_disposition=bigquery.WriteDisposition.WRITE_TRUNCATE,
    )

    job = client.load_table_from_dataframe(df, full_table, job_config=job_config)
    job.result()  # Wait for completion

    log.info(f"  Uploaded → {full_table} ({len(df):,} rows)")


def main():
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    log.info("=" * 60)
    log.info("  CWTS Output → BigQuery Uploader")
    log.info("=" * 60)
    log.info(f"  Project:   {BQ_PROJECT}")
    log.info(f"  Dataset:   {BQ_DATASET}")
    log.info(f"  Timestamp: {timestamp}")
    log.info(f"  Source:    {CWTS_OUTPUT_DIR}")
    log.info("=" * 60)

    client = bigquery.Client(project=BQ_PROJECT)

    # Ensure dataset exists
    dataset_ref = f"{BQ_PROJECT}.{BQ_DATASET}"
    try:
        client.get_dataset(dataset_ref)
        log.info(f"  Dataset {BQ_DATASET} exists")
    except Exception:
        log.info(f"  Creating dataset {BQ_DATASET}...")
        dataset = bigquery.Dataset(dataset_ref)
        dataset.location = "US"
        client.create_dataset(dataset)

    log.info("")
    log.info("[1/4] Loading files...")

    uploaded = []

    for name, config in FILES.items():
        df = load_file(name, config)

        if df is not None and not df.empty:
            table_name = f"{name}_raw_{timestamp}"
            upload_to_bigquery(df, table_name, client)
            uploaded.append((name, table_name, len(df)))

    log.info("")
    log.info("=" * 60)
    log.info("  Upload complete!")
    log.info("=" * 60)
    log.info("")
    log.info("  Tables created:")
    for name, table_name, rows in uploaded:
        log.info(f"    {BQ_DATASET}.{table_name} ({rows:,} rows)")

    log.info("")
    log.info("  To use in build_drift_dashboard.py, update:")
    log.info(f'    TBL_CLASSIF = "{BQ_DATASET}.classification_raw_{timestamp}"')
    log.info(f'    TBL_PUB_META = "{BQ_DATASET}.pub_metadata_raw_{timestamp}"')
    log.info("")


if __name__ == "__main__":
    main()
