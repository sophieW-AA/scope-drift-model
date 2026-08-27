import subprocess
from datetime import datetime
import os
import pandas as pd
import pandas_gbq
from google.cloud import bigquery
from pathlib import Path
import logging
import tempfile
import shutil

    # python subprocess_leiden.py
    # OR nohup python subprocess_leiden.py &
    # OR nohup python subprocess_leiden.py > nohup_out.log 2>&1 & AND tail -f nohup_out.log
# ps -p <PID>

run_timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")


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

# -- logging setup --
LOG_DIR = Path("../cwts_logs")
LOG_DIR.mkdir(parents=True, exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(
            LOG_DIR / f"subprocess_leidgen{run_timestamp}.log",
            mode="w",
        ),
        logging.StreamHandler(),
    ],
)
log = logging.getLogger(__name__)
log.info(f"CWTS Publication Classification Run\n")
log.info(f"{'='*50}\n")
log.info(f"Timestamp : {run_timestamp}\n\n")
log.info(f"\nParameters\n{'-'*30}\n")
for k, v in params.items():
    log.info(f"  {k:<26}: {v}\n")

# --- Source: BigQuery tables written by cwts_export.py ---
BQ_PROJECT = "ocean-tech-adv-analytics-c-tfs"
BQ_DATASET = "raw_citation_network_data"

log.info(f"  BQ_PROJECT              : {BQ_PROJECT}")
log.info(f"  AIRAK_DATASET           : {BQ_DATASET}")

client = bigquery.Client(project=BQ_PROJECT)

data_timestamp = "20260818_090851" #-- this is global run 2023-2026

pubs_df = client.query(
    f"SELECT int_id, core_pub FROM `{BQ_PROJECT}.{BQ_DATASET}.pubs_raw_{data_timestamp}` "
    f"ORDER BY int_id"
).to_dataframe()

log.info("pubs_df loaded successfully")

cit_links_df = client.query(
    f"SELECT int_id1, int_id2, weight FROM `{BQ_PROJECT}.{BQ_DATASET}.cit_links_raw_{data_timestamp}` "
    f"ORDER BY int_id1, int_id2"
).to_dataframe()

log.info("cit_links_df loaded successfully")

# --- Write back out as the plain text files the CWTS jar reads ---
os.makedirs("leiden_input", exist_ok=True)

# Everything — pubs.txt, cit_links.txt AND classification.txt — lives inside a
# TemporaryDirectory now. It's deleted the moment the `with` block exits, so
# cwts_output/ is never created and nothing survives the run.
pubs_path = os.path.join("leiden_input", "pubs.txt")
cit_links_path = os.path.join("leiden_input", "cit_links.txt")
classification_path = os.path.join("leiden_input", "classification.txt")

pubs_df.to_csv(pubs_path, sep="\t", index=False, header=False)
cit_links_df.to_csv(cit_links_path, sep="\t", index=False, header=False, float_format="%.6f")

log.info("temp files created for leiden")


result = subprocess.run(
    [
        "java",
        "-Xmx350g",
        "-cp",
        "publicationclassification.jar",
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
log.info("LEIDEN HAS RUN!1")
    
if result.stdout:
    log.info(f"stdout: {result.stdout}")
if result.stderr:
    log.error(f"stderr: {result.stderr}")
if result.returncode != 0:
    log.error(f"Leiden failed with return code {result.returncode} (signal {-result.returncode if result.returncode < 0 else 'n/a'})")

# Read classification.txt into memory WHILE it still exists in tmp_dir
classification = pd.read_csv(
    classification_path,
    sep="\t",
    header=None,
    names=["int_id", "micro", "meso", "macro"],
)
# <- tmp_dir (pubs.txt, cit_links.txt, classification.txt) is deleted here


log.info(f"\nReturn Code: {result.returncode}\n")

log.info(f"\nSTDOUT\n{'-'*30}\n")
log.info(result.stdout or "(empty)\n")

log.info(f"\nSTDERR\n{'-'*30}\n")
log.info(result.stderr or "(empty)\n")

print(f"Log written to: {LOG_DIR}")
log.info(result.stdout)
if result.stderr:
    print(result.stderr)

# Upload to BigQuery

pandas_gbq.to_gbq(
    classification,
    f"{BQ_DATASET}.classification_raw_{run_timestamp}",
    project_id=BQ_PROJECT,
    if_exists="replace",
)
print(f"  → BigQuery: {BQ_DATASET}.classification_raw_{run_timestamp}")


shutil.rmtree("leiden_input")

log.info('leiden_input files removed')
log.info("Script finished success!!")