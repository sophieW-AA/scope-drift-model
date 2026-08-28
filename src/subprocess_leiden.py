"""
CWTS Leiden classification: read pubs/cit_links from BigQuery, run the Java jar,
upload classification_raw_{timestamp}.

Timestamp resolution (first match wins):
  1. env RUN_TIMESTAMP  — set by main.py (-t / --export / --leiden)
  2. DATA_TIMESTAMP below — edit this to cluster a specific existing export
     when running the script directly

    python src/subprocess_leiden.py
    python main.py --leiden -t 20260818_090851
"""

from __future__ import annotations

import logging
import os
import shutil
import subprocess
import sys
from pathlib import Path

import pandas as pd
import pandas_gbq
from google.cloud import bigquery

# Edit this when running Leiden alone on a specific export (ignored if
# RUN_TIMESTAMP is set in the environment / by main).
DATA_TIMESTAMP = "20260818_090851"  # global run 2023-2026

# --- Parameters ---
params = {
    "largest_component_only": "true",
    "iterations": "1000",
    "micro_resolution": "1e-5",
    "micro_min_cluster_size": "500",
    "meso_resolution": "2e-6",
    "meso_min_cluster_size": "5000",
    "macro_resolution": "2e-7",
    "macro_min_cluster_size": "100000",
}

run_timestamp = (os.environ.get("RUN_TIMESTAMP") or "").strip() or DATA_TIMESTAMP

# -- logging setup --
LOG_DIR = Path(
    r"C:\Users\sophie.wilson\Documents\scope_drift_outputs\logs\subprocess_leiden"
)
LOG_DIR.mkdir(parents=True, exist_ok=True)

# Windows consoles / redirected pipes default to cp1252, which cannot encode the
# arrows and box characters used in log messages.
for _stream in (sys.stdout, sys.stderr):
    if hasattr(_stream, "reconfigure"):
        _stream.reconfigure(encoding="utf-8", errors="replace")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(
            LOG_DIR / f"subprocess_leiden_{run_timestamp}.log",
            mode="w",
            encoding="utf-8",
        ),
        logging.StreamHandler(),
    ],
)
log = logging.getLogger(__name__)
log.info("CWTS Publication Classification Run")
log.info("=" * 50)
log.info("Timestamp : %s", run_timestamp)
log.info("Parameters")
log.info("-" * 30)
for k, v in params.items():
    log.info("  %-26s: %s", k, v)

# --- Source: BigQuery tables written by cwts_export.py ---
BQ_PROJECT = os.environ.get("BQ_PROJECT", "ocean-tech-adv-analytics-c-tfs")
BQ_DATASET = os.environ.get("BQ_DATASET", "raw_citation_network_data")

log.info("  BQ_PROJECT              : %s", BQ_PROJECT)
log.info("  BQ_DATASET              : %s", BQ_DATASET)

client = bigquery.Client(project=BQ_PROJECT)

pubs_df = client.query(
    f"SELECT int_id, core_pub FROM `{BQ_PROJECT}.{BQ_DATASET}.pubs_raw_{run_timestamp}` "
    f"ORDER BY int_id"
).to_dataframe()

log.info("pubs_df loaded successfully")

cit_links_df = client.query(
    f"SELECT int_id1, int_id2, weight FROM `{BQ_PROJECT}.{BQ_DATASET}.cit_links_raw_{run_timestamp}` "
    f"ORDER BY int_id1, int_id2"
).to_dataframe()

log.info("cit_links_df loaded successfully")

# --- Plain text files for the CWTS jar (cleaned up after upload) ---
os.makedirs("leiden_input", exist_ok=True)
pubs_path = os.path.join("leiden_input", "pubs.txt")
cit_links_path = os.path.join("leiden_input", "cit_links.txt")
classification_path = os.path.join("leiden_input", "classification.txt")

pubs_df.to_csv(pubs_path, sep="\t", index=False, header=False)
cit_links_df.to_csv(
    cit_links_path, sep="\t", index=False, header=False, float_format="%.6f"
)

log.info("temp files created for leiden")

jar_path = Path(__file__).resolve().parent / "publicationclassification.jar"
if not jar_path.exists():
    raise SystemExit(f"Missing CWTS jar: {jar_path}")

result = subprocess.run(
    [
        "java",
        "-Xmx350g",
        "-cp",
        str(jar_path),
        "nl.cwts.publicationclassification.run.PublicationClassificationCreator",
        pubs_path,
        cit_links_path,
        classification_path,
        params["largest_component_only"],
        params["iterations"],
        params["micro_resolution"],
        params["micro_min_cluster_size"],
        params["meso_resolution"],
        params["meso_min_cluster_size"],
        params["macro_resolution"],
        params["macro_min_cluster_size"],
    ],
    capture_output=True,
    text=True,
)
log.info("Leiden jar finished (return code %s)", result.returncode)

if result.stdout:
    log.info("stdout: %s", result.stdout)
if result.stderr:
    log.error("stderr: %s", result.stderr)
if result.returncode != 0:
    shutil.rmtree("leiden_input", ignore_errors=True)
    raise SystemExit(f"Leiden failed with return code {result.returncode}")

classification = pd.read_csv(
    classification_path,
    sep="\t",
    header=None,
    names=["int_id", "micro", "meso", "macro"],
)

print(f"Log written to: {LOG_DIR}")

pandas_gbq.to_gbq(
    classification,
    f"{BQ_DATASET}.classification_raw_{run_timestamp}",
    project_id=BQ_PROJECT,
    if_exists="replace",
)
print(f"  → BigQuery: {BQ_DATASET}.classification_raw_{run_timestamp}")

shutil.rmtree("leiden_input", ignore_errors=True)
log.info("leiden_input files removed")
log.info("Script finished successfully")
