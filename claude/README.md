# Scope Drift Analysis — Claude Scripts

Scripts for detecting scope drift in Frontiers journals using Leiden community detection on AIRAK citation networks.

---

## Which script to run

| Script | Status | Description |
|--------|--------|-------------|
| `scope_drift_airak_global_1.py` | **Current** | Active test version with Phase 2 edge weight improvements (bibliographic coupling, temporal decay, self-citation discounting) |
| `scope_drift_airak_global.py` | Legacy | Older version without citation works / edge weight enhancements |
| `test_edge_weight_configs.py` | Testing | Runs analysis with 3 different edge configs for comparison (baseline, decay-only, full Phase 2) |
| `build_drift_dashboard.py` | Utility | Builds drift dashboard comparing journals against historical baseline |
| `build_cluster_dashboard.py` | Utility | Builds cluster dashboard with macro/meso/micro Leiden resolutions |

---

## Quick start

```powershell
# Set credentials
$env:GOOGLE_APPLICATION_CREDENTIALS = "C:\path\to\creds.json"

# Run the current analysis
python scope_drift_airak_global_1.py
```

---

## Environment variables

| Variable | Default | Description |
|----------|---------|-------------|
| `GOOGLE_APPLICATION_CREDENTIALS` | — | Path to GCP service account JSON |
| `PRIMARY_CLUSTER_COVERAGE` | `0.80` | Fraction of papers defining "in scope" clusters |
| `ENABLE_EDGE_WEIGHTS` | `true` | Enable all edge weight features |
| `ENABLE_BC_EDGES` | `true` | Bibliographic coupling edges |
| `TEMPORAL_DECAY_TAU` | `5` | Decay half-life in years for citation weighting |
| `SELF_CITE_JOURNAL_WEIGHT` | `0.5` | Discount factor for within-journal citations |

---

## Outputs

Results are written to `output/`:

- `scope_global_dashboard.html` — Interactive dashboard
- `scope_global_network.json` — Network data for visualization
- `config_comparison.txt` — Edge weight config comparison (from `test_edge_weight_configs.py`)

---

## Dependencies

```
pip install leidenalg python-igraph google-cloud-bigquery pandas plotly numpy scipy
```
