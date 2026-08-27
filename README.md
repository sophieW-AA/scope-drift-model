# Scope Drift Model

Detection of scope drift in Frontiers journals using Leiden community detection on AIRAK citation networks.

## Project Structure

```
scope-drift-model/
├── src/                     # Main source code
│   └── scope_drift.py       # Primary analysis script
├── scripts/                 # Utility scripts
│   ├── test_edge_weight_configs.py
│   ├── build_drift_dashboard.py
│   └── build_cluster_dashboard.py
├── output/                  # Generated outputs
├── data/                    # Data files
│   ├── cwts_synthetic_test/ # Test fixtures
│   └── cwts_work/           # Working data
├── archive/                 # Old/research code
└── requirements.txt
```

## Quick Start

```powershell
# Install dependencies
pip install -r requirements.txt

# Set credentials
$env:GOOGLE_APPLICATION_CREDENTIALS = "C:\path\to\creds.json"

# Run the analysis
python src/scope_drift.py
```

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `GOOGLE_APPLICATION_CREDENTIALS` | — | Path to GCP service account JSON |
| `PRIMARY_CLUSTER_COVERAGE` | `0.80` | Fraction of papers defining "in scope" clusters |
| `ENABLE_EDGE_WEIGHTS` | `true` | Enable all edge weight features |
| `ENABLE_BC_EDGES` | `true` | Bibliographic coupling edges |
| `TEMPORAL_DECAY_TAU` | `5` | Decay half-life in years for citation weighting |
| `SELF_CITE_JOURNAL_WEIGHT` | `0.5` | Discount factor for within-journal citations |

## Scripts

| Script | Description |
|--------|-------------|
| `src/scope_drift.py` | Main analysis with Phase 2 edge weights |
| `scripts/test_edge_weight_configs.py` | Compare edge weight configurations |
| `scripts/build_drift_dashboard.py` | Build drift dashboard |
| `scripts/build_cluster_dashboard.py` | Build cluster dashboard |

## Outputs

Results are written to `output/`:

- `scope_global_dashboard.html` — Interactive dashboard
- `scope_global_network.json` — Network data for visualization
- `config_comparison.txt` — Edge weight config comparison



#### 

How to run efficiently

Full run is run_pipeline in the notebook - data gather, cwts cluster, taxonomy naming, pdf/html output

PARTIAL RUN 
cwts_export - runs data gathering, cwts export and upload all output to bigquery, 
run_pipeline - manually change dattime to the same as above for taxonomy naming, pdf/html output 

Individual runs are:
1. cwts_export run classification = FALSE - this just gets the data and ciation weights
1. subprocess_leiden - you need to make sure your resolution and timestamp is right
2. taxonomy_naming.py - names the files
3. files come from run_pipeline