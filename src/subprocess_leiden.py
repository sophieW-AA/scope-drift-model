import subprocess
import datetime
import os
import pandas as pd
import pandas_gbq

run_timestamp = "20260714_151745"

# --- Parameters ---
params = {
    "largest_component_only": "true",
    "iterations": "100",
    "micro_resolution": "4e-4",
    "micro_min_cluster_size": "200",
    "meso_resolution": "1e-6",
    "meso_min_cluster_size": "1000",
    "macro_resolution": "5e-7",
    "macro_min_cluster_size": "50000",
}

input_files = {
    "pubs": "cwts_output/pubs.txt",
    "cit_links": "cwts_output/cit_links.txt",
    "output": "cwts_output/classification.txt",
    "jar": "publicationclassification.jar",
}


result = subprocess.run(
    [
        "java",
        "-Xmx350g",
        "-cp",
        input_files["jar"],
        "nl.cwts.publicationclassification.run.PublicationClassificationCreator",
        input_files["pubs"],
        input_files["cit_links"],
        input_files["output"],
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

# --- Log ---
os.makedirs("logs", exist_ok=True)
log_path = f"logs/cwts_run_{run_timestamp}.log"

with open(log_path, "w") as f:
    f.write(f"CWTS Publication Classification Run\n")
    f.write(f"{'='*50}\n")
    f.write(f"Timestamp : {run_timestamp}\n\n")

    f.write(f"Input Files\n{'-'*30}\n")
    for k, v in input_files.items():
        f.write(f"  {k:<20}: {v}\n")

    f.write(f"\nParameters\n{'-'*30}\n")
    for k, v in params.items():
        f.write(f"  {k:<26}: {v}\n")

    f.write(f"\nReturn Code: {result.returncode}\n")

    f.write(f"\nSTDOUT\n{'-'*30}\n")
    f.write(result.stdout or "(empty)\n")

    f.write(f"\nSTDERR\n{'-'*30}\n")
    f.write(result.stderr or "(empty)\n")

print(f"Log written to: {log_path}")
print(result.stdout)
if result.stderr:
    print(result.stderr)

# Load classification.txt
classification = pd.read_csv(
    "cwts_output/classification.txt",
    sep="\t",
    header=None,
    names=["int_id", "micro", "meso", "macro"],
)

# Upload to BigQuery
BQ_DEST_PROJECT = "ocean-tech-adv-analytics-c-tfs"
BQ_DEST_DATASET = "scope_drift_raw"


# classification.to_gbq(
#     f"{dataset}.classification_raw_{run_timestamp}",
#     project_id=project,
#     if_exists="replace",
# )

# Upload to BigQuery

pandas_gbq.to_gbq(
    classification,
    f"{BQ_DEST_DATASET}.classification_raw_{run_timestamp}",
    project_id=BQ_DEST_PROJECT,
    if_exists="replace",
)
print(f"  → BigQuery: {BQ_DEST_DATASET}.classification_raw_{run_timestamp}")