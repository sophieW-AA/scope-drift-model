# Scope Drift Model

Detect scope drift in Frontiers journals from AIRAK citation networks: CWTS clustering, taxonomy labels, HTML dashboards, and a PDF report.

## Project structure

```
scope-drift-model/
├── main.py                      # Pipeline orchestrator (preferred entrypoint)
├── run_pipeline.ipynb           # Same steps, notebook form (optional)
├── src/
│   ├── cwts_export.py           # Fetch network, write CWTS files, upload to BigQuery
│   ├── taxonomy_naming.py       # Map clusters -> taxonomy labels (macro_labels.csv)
│   ├── build_unified_dashboard.py
│   ├── build_scope_drift_report_pdf.py
│   ├── subprocess_leiden.py     # CWTS Java clustering -> classification_raw_*
│   └── opportunities/           # Market-first journal-opportunity pipeline
├── scripts/
│   └── build_gt_network_map.py  # Optional ground-truth overlay map
├── output/                      # HTML dashboards + PDF
├── cwts_output/                 # Optional caches / legacy artefacts (not required by taxonomy)
├── .env                         # Secrets (e.g. OPENAI_API_KEY) — not committed
└── requirements.txt
```

## Quick start

```powershell
pip install -r requirements.txt

# GCP auth (ADC or service account)
$env:GOOGLE_APPLICATION_CREDENTIALS = "C:\path\to\creds.json"

# Reuse an existing BigQuery run (skips cwts_export) — usual path
python main.py --timestamp 20260721_122750

# Or create a new network, then Leiden + the rest (Leiden is on by default)
python main.py --export --start-year 2023 --end-year 2026
```

`main.py` loads `.env` from the repo root (e.g. `OPENAI_API_KEY` for borderline / paper LLM / taxonomy).

## How to run (`main.py`)

Default path runs **Leiden** (unless `--skip-leiden`). Pass a timestamp to reuse an existing export; add `--export` for a new network.

| Mode | Command |
|------|---------|
| Reuse export + existing clusters | `python main.py -t 20260721_122750 --skip-leiden` |
| Re-cluster existing export + pipeline | `python main.py --timestamp 20260721_122750` |
| + GT overlay map | `python main.py -t 20260721_122750 --skip-leiden --gt` |
| New export + Leiden + pipeline | `python main.py --export --start-year 2023 --end-year 2026` |
| Export with fixed timestamp | `python main.py --export -t 20260828_120000 --start-year 2023 --end-year 2026` |
| Skip some steps | `python main.py -t 20260721_122750 --skip-leiden --skip-taxonomy --skip-pdf` |

```text
[--export]  ->  [leiden]  ->  taxonomy_naming  ->  build_unified_dashboard  ->  read_model  ->  [--gt]  ->  PDF
```

- **`--export`**: runs `src/cwts_export.py` (network + weights → BigQuery).
- **Leiden** (default): runs `src/subprocess_leiden.py` → `classification_raw_{timestamp}`. Skip with `--skip-leiden`.
- **taxonomy**: `src/taxonomy_naming.py` uploads cluster labels to BigQuery (`taxonomy_labelling`).
- **dashboard**: `src/build_unified_dashboard.py` (scope / drift / network maps; LLM borderline, hard-negatives, paper demotion on by default). Also writes `journal_summary_{timestamp}` next to `paper_scope_{timestamp}` in `raw_citation_network_data`.
- **read model**: `src/read_model.py` adds `leiden_output.papers`, `communities`, and `journals`. Skip with `--skip-read-model`.
- **`--gt`**: optional `scripts/build_gt_network_map.py` (needs local truth ODS).
- **PDF**: `src/build_scope_drift_report_pdf.py` → `scope_drift_outputs/dashboards/Scope_Drift_Report.pdf`.

Useful flags: `--cluster-level {micro,meso,macro}`, `--journals "..."`, `--skip-leiden`, `--skip-taxonomy`, `--skip-dashboard`, `--skip-read-model`, `--skip-pdf`. See `python main.py --help`.

### Partial / manual steps

If you prefer running pieces yourself:

1. **Data gather** (`cwts_export` — network + weights → BigQuery only):

   ```powershell
   $env:START_YEAR="2023"; $env:END_YEAR="2026"; $env:NETWORK_MODE="full"
   $env:RUN_TIMESTAMP="20260828_120000"
   python src/cwts_export.py
   ```

2. **Clusters** — `python main.py -t 20260828_120000 --skip-taxonomy --skip-dashboard --skip-pdf` (or reuse an existing `classification_raw_{timestamp}` with `--skip-leiden`).

3. **Labels + dashboards + PDF** off that timestamp:

   ```powershell
   python main.py --timestamp 20260828_120000 --skip-leiden
   ```

## Journal opportunities

The opportunity mapper is downstream of the citation-network pipeline. Its
supported default combines all-publisher OpenAlex market sizing with Leiden
scope validation and Frontiers portfolio routing:

```powershell
# Discover the latest complete scope-drift run and create the readable Excel
python src/opportunities/run.py

# Or pin the Leiden run
python src/opportunities/run.py --run 20260827_081311
```

Opportunity artifacts are deliberately outside the repository:

```text
C:\Users\sophie.wilson\Documents\scope_drift_outputs\opportunities\
├── output\   # final JSON, manifest, readable Excel
└── logs\     # timestamped run logs
```

Set `OPPORTUNITIES_OUTPUT_ROOT` to override that directory. See
`src/opportunities/README.md` for the method, thresholds, output columns, legacy
phases and re-export commands.

## Outputs

### Local (`output/`)

| File | Description |
|------|-------------|
| `combined_dashboard.html` | Combined views |
| `scope_dashboard.html` | Scope / OOS / borderline |
| `drift_dashboard.html` | Drift trends |
| `network_maps.html` | Community maps + year slider |
| `gt_network_map.html` | Ground-truth overlay (with `--gt`) |
| `Scope_Drift_Report.pdf` | Journal Scope Drift Report |

### BigQuery uploads

Project: `ocean-tech-adv-analytics-c-tfs` (EU).

#### From `cwts_export` (`--export`)

Uploads to dataset `raw_citation_network_data` (no lasting local network data files):

| BigQuery table | When |
|----------------|------|
| `raw_citation_network_data.pubs_raw_{timestamp}` | Always on export |
| `raw_citation_network_data.pub_metadata_raw_{timestamp}` | Always on export |
| `raw_citation_network_data.cit_links_raw_{timestamp}` | Always on export |
| `raw_citation_network_data.run_metadata_{timestamp}` | Always on export (run config row) |

Logs only: `C:\Users\sophie.wilson\Documents\scope_drift_outputs\logs\cwts_export*.log`.

#### From `subprocess_leiden`

Reads `pubs_raw_*` + `cit_links_raw_*`, runs the CWTS Java classifier, uploads:

| BigQuery table |
|----------------|
| `raw_citation_network_data.classification_raw_{timestamp}` |

Dashboards / taxonomy expect this table (or an older run’s equivalent) before labelling.

#### From `taxonomy_naming`

Reads `classification_raw_*` + `pub_metadata_raw_*`, then uploads labels to dataset `taxonomy_labelling` (per level: macro / meso / micro). No local CSV outputs.

| BigQuery table |
|----------------|
| `taxonomy_labelling.cluster_labels_{level}_{timestamp}` |
| `taxonomy_labelling.cluster_taxonomy_labels_{level}_{timestamp}` |

Dashboards load labels from these BigQuery tables.

`taxonomy_naming` also writes `taxonomy_labelling.cluster_l2_topics_{level}_{timestamp}` (top L2 topics and the L1 rollup name). The read model uses that for community names.

#### From the dashboard

Writes into `raw_citation_network_data`:

| BigQuery table |
|----------------|
| `raw_citation_network_data.paper_scope_{timestamp}` |
| `raw_citation_network_data.journal_summary_{timestamp}` |

#### Read model (`src/read_model.py`)

Adds three stable tables in `leiden_output`. The network tables stay in `raw_citation_network_data`. `run_timestamp` is a column, so a run is one filter rather than a new table name. Republishing a run replaces only that run's rows in `leiden_output`.

| Table | Grain | What it holds |
|-------|-------|----------------|
| `leiden_output.papers` | one row per paper | `int_id`, `pub_id`, `title`, `journal`, `is_frontiers`, `pub_year`, `macro_id`, `meso_id`, `micro_id`. Scope columns are filled only for journals the dashboard scored. |
| `leiden_output.communities` | one row per community per level | `level` (`macro` / `meso` / `micro`), `community_id`, `name` (`unit_name`, else `short_label`), `n_papers`, `parent_name`, `topics`, `taxonomy_key` |
| `leiden_output.journals` | one row per scored journal | `n_articles`, `n_out_of_scope`, `out_of_scope_pct`, `primary_communities`, `borderline_communities` (semicolon-separated names), `oos_by_year` (JSON), plus borderline / hard-negative / paper-LLM counts |

`papers.scope` is `in_scope`, `borderline`, or `out_of_scope`. `papers.scope_reason` is `primary`, `borderline_community`, `hard_negative`, `paper_llm`, or `outside_primary`. `papers.scope_level` is the dashboard cluster level. Those three columns are null for papers the dashboard did not score.

Network inputs are read from `raw_citation_network_data`: `classification_raw_{timestamp}`, `pub_metadata_raw_{timestamp}`, `paper_scope_{timestamp}`, and `journal_summary_{timestamp}`. `journals` is filled only when `journal_summary_{timestamp}` is in that dataset. A missing label level is skipped; `papers` and `communities` still publish when `--skip-dashboard` is set.

Backfill a finished run without re-clustering:

```powershell
python src/read_model.py --timestamp 20260721_122750
```

## Key environment variables

| Variable | Default | Description |
|----------|---------|-------------|
| `RUN_TIMESTAMP` | — | BigQuery run id (or pass `-t`) |
| `CLUSTER_LEVEL` | `macro` | Cluster level for dashboards |
| `JOURNALS` | (8 test journals in `main.py`) | Comma-separated journal names |
| `START_YEAR` / `END_YEAR` | `2023` / `2026` | Export year window |
| `NETWORK_MODE` | `full` | `ego` / `full` / `global` |
| `PRIMARY_COVERAGE` | `0.8` | Share of papers defining primary clusters |
| `SCOPE_LLM_BORDERLINE_ENABLED` | `1` | LLM borderline communities |
| `SCOPE_HARD_NEGATIVES_ENABLED` | `1` | Title hard-negative OOS rules |
| `SCOPE_PAPER_LLM_ENABLED` | `1` | Paper-level demotion in risky primaries |
| `OPENAI_API_KEY` | — | Taxonomy + scope LLM steps |
| `GOOGLE_APPLICATION_CREDENTIALS` | — | GCP auth if not using ADC |

## Run on a VM (long export)

```bash
nohup env START_YEAR=2020 END_YEAR=2026 NETWORK_MODE=full ENABLE_BC_EDGES=false \
  python src/cwts_export.py > cwts_output.log 2>&1 &

# Still running?
ps aux | grep cwts_export.py

# Live stdout
tail -f cwts_output.log

# Structured step log
tail -f /c/Users/sophie.wilson/Documents/scope_drift_outputs/logs/cwts_export*.log
```

Then on the same timestamp:

```bash
python main.py --timestamp <that_RUN_TIMESTAMP>
```
