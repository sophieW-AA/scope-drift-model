# Scope-drift pipeline architecture

Technical schema for `main.py` — what each step runs, what it reads, what it writes, and how a run id ties it all together.

---

## The run id is the join key

Everything is keyed on a single run timestamp of the form `YYYYMMDD_HHMMSS`. `main.py` resolves it once and exports it as `RUN_TIMESTAMP` to every child process; each step then reads and writes `<table>_{timestamp}` in BigQuery. Reusing an existing run means passing `-t`, and only `--export` mints a new id (from `datetime.now()`) when you don't supply one.

```
main.py -t 20260818_090851
   │
   ├─ loads .env (override=True — .env beats a stale shell key)
   ├─ sets PYTHONUTF8=1, PYTHONIOENCODING=utf-8   (cp1252 breaks the log glyphs)
   ├─ sets RUN_TIMESTAMP, CLUSTER_LEVEL, JOURNALS, SCOPE_* defaults
   └─ runs each step as a subprocess, aborting on the first non-zero exit
```

---

## Pipeline at a glance

```text
1. EXPORT                                    src/cwts_export.py    [--export]
   IN    AIRAK: Publication, PublicationCitation, Journal
   DOES  pick journals + year window, build a weighted citation graph
   OUT   pubs_raw · pub_metadata_raw · cit_links_raw · run_metadata
                              │
                              ▼
2. LEIDEN                              src/subprocess_leiden.py  [--skip-leiden]
   IN    pubs_raw + cit_links_raw
   DOES  CWTS Java jar clusters the graph at three resolutions
   OUT   classification_raw          int_id → micro | meso | macro
                              │
                              ▼
3. TAXONOMY                           src/taxonomy_naming.py  [--skip-taxonomy]
   IN    classification_raw + pub_metadata_raw + Frontiers taxonomy
   DOES  sample 300 papers per cluster, GPT names it
   OUT   cluster_labels_{level}       cluster id → "Thermal Energy Management"
                              │
                              ▼
4. DASHBOARD                    src/build_unified_dashboard.py  [--skip-dashboard]
   IN    classification_raw + pub_metadata_raw + cit_links_raw
         + cluster_labels_{level}
   DOES  find each journal's core clusters, flag out-of-scope papers
   OUT   6 HTML dashboards + paper_scope
                              │
                              ▼
6. PDF                      src/build_scope_drift_report_pdf.py  [--skip-pdf]
   IN    scope_dashboard.html + drift_dashboard.html
   DOES  render the scope story as a report
   OUT   Scope_Drift_Report.pdf


   off to the side, optional:

5. GT MAP                          scripts/build_gt_network_map.py  [--gt]
   IN    classification_raw + pub_metadata_raw + manual truth .ods
   DOES  overlay manual scope labels on the community map
   OUT   output/gt_network_map.html
```

The opportunity mapper (`python src/opportunities/run.py`) is **not** part of `main.py`. It sits downstream and consumes `classification_raw`, `pub_metadata_raw`, `cluster_labels_meso` and `paper_scope`.

Its market phase is deliberately independent of the export corpus:

1. `world_market.py` sizes and grows all AIRAK level-1 fields across every publisher.
2. Market size and growth alone decide whether a field is an opportunity.
3. Non-Frontiers papers in the citation neighbourhood divide qualified fields into Leiden journal- and section-shaped scopes.
4. Frontiers volume and ownership are attached last to choose the action: greenfield launch, consolidation launch, grow, reroute or gate.

`cwts_export.py` remains Frontiers-seeded because Leiden needs a relevant citation neighbourhood for scope analysis. Counts from that ego network are never labelled or used as global market volume.

---

## Step reference

| Step | Flag | File | Reads | Writes |
|---|---|---|---|---|
| **1 Export** | `--export` (off by default) | `src/cwts_export.py` | `ocean-breeze-tier-1.airak` Publication, PublicationCitation, Journal | `pubs_raw_{ts}`, `pub_metadata_raw_{ts}`, `cit_links_raw_{ts}`, `run_metadata_{ts}` |
| **2 Leiden** | on by default, `--skip-leiden` | `src/subprocess_leiden.py` + `publicationclassification.jar` | `pubs_raw_{ts}`, `cit_links_raw_{ts}` | `classification_raw_{ts}` |
| **3 Taxonomy** | on by default, `--skip-taxonomy` | `src/taxonomy_naming.py` | `classification_raw_{ts}` ⋈ `pub_metadata_raw_{ts}`, Frontiers taxonomy, OpenAI | `cluster_labels_{level}_{ts}`, `cluster_taxonomy_labels_{level}_{ts}` |
| **4 Dashboard** | on by default, `--skip-dashboard` | `src/build_unified_dashboard.py` | `classification_raw`, `pub_metadata_raw`, `cit_links_raw`, `run_metadata`, labels, OpenAI | 6 HTML dashboards, `paper_scope_{ts}` |
| **5 GT map** | `--gt` (off by default) | `scripts/build_gt_network_map.py` | `manual_scope_check_truth.ods`, `classification_raw`, `pub_metadata_raw` | `output/gt_network_map.html` |
| **6 PDF** | on by default, `--skip-pdf` | `src/build_scope_drift_report_pdf.py` | `scope_dashboard.html` + `drift_dashboard.html` (embedded JS constants) | `Scope_Drift_Report.pdf` |

All BigQuery tables live in project `ocean-tech-adv-analytics-c-tfs`, location EU. HTML and PDF land in `C:\Users\sophie.wilson\Documents\scope_drift_outputs\dashboards`.

---

## Step detail

### 1. Export — `src/cwts_export.py`

Builds the citation network from AIRAK. It picks the journal set (`TOP_N_JOURNALS` or `JOURNAL_IDS_OVERRIDE`), pulls publications in the year window, then expands outward according to `NETWORK_MODE`:

| Mode | Meaning |
|---|---|
| `ego` | Frontiers papers plus their immediate citation neighbours |
| `full` | Frontiers core plus external papers up to `MAX_EXTERNAL_PAPERS` |
| `global` | The whole citation graph for the window (default) |

Edges are then weighted rather than left binary: temporal decay with `TEMPORAL_DECAY_TAU` (default 5 years), a self-citation discount via `SELF_CITE_JOURNAL_WEIGHT` (0.5), and optional bibliographic-coupling edges requiring `BC_MIN_SHARED_REFS` shared references.

Key environment variables: `START_YEAR` (2023), `END_YEAR` (2026), `NETWORK_MODE` (global), `MAX_EXTERNAL_PAPERS` (50000), `ENABLE_EDGE_WEIGHTS`, `ENABLE_BC_EDGES`.

> **Note:** the year window is fixed into the network here and cannot be widened downstream. A run built with `START_YEAR=2023` can never support a 2020 drift baseline.

### 2. Leiden — `src/subprocess_leiden.py`

Pulls `pubs_raw` and `cit_links_raw` out of BigQuery, writes them as tab-separated files into a temporary `leiden_input/`, and shells out to the CWTS Java jar (`nl.cwts.publicationclassification.run.PublicationClassificationCreator`) with `java -Xmx350g`. The result is parsed back as `int_id, micro, meso, macro` and uploaded as `classification_raw_{ts}`, then the temp directory is removed.

Current resolution parameters:

```text
largest_component_only  true
iterations              1000
micro   resolution 1e-5   min cluster size 500
meso    resolution 2e-6   min cluster size 5000
macro   resolution 2e-7   min cluster size 100000
```

Journal is **not** an input — clusters are formed from citation structure alone, which is what makes the downstream scope analysis independent of our own labelling.

> **Note:** `largest_component_only=true` drops papers disconnected from the main component. On run `20260818_090851` that is ~453k of 17.1M rows (2.6%).

### 3. Taxonomy naming — `src/taxonomy_naming.py`

Turns numeric cluster ids into readable labels. It joins classification to metadata, samples up to `SAMPLE_SIZE_PER_CLUSTER` (300) papers per cluster, builds a per-cluster brief, and asks GPT to assign each cluster to `core` and `bleed` categories from the Frontiers taxonomy. `export_dashboard_labels` then takes the top-ranked core category as `short_label`.

Levels come from the module constant `CLUSTER_LEVELS = ("micro", "meso", "macro")` — there is no CLI or environment override, and no checkpoint/resume. Both output tables are written with `if_exists="replace"`.

Requires `OPENAI_API_KEY` (or `GPT4_OPENAI_KEY`); the script calls `load_dotenv(override=True)` itself, so running it directly is fine as long as the working directory is the repo root.

> **Assumption to watch:** a cluster only gets a label if some taxonomy category clears `SCOPE_PCT_FLOOR` / `L1_ARTICLE_SHARE_FLOOR` on its 300-paper sample. Broad, heterogeneous clusters spread thin and yield no `core` row, so they silently end up unlabelled — coverage on `20260818_090851` is 89% micro, 53% meso, 29% macro.

### 4. Unified dashboard — `src/build_unified_dashboard.py`

The analytical heart of the pipeline. For each journal in `JOURNALS` it determines primary clusters by `PRIMARY_COVERAGE` (0.8) coverage, flags out-of-scope papers, and layers on several LLM passes: borderline community judging, hard negatives, and paper-level demotion inside method-broad primary communities. LLM results are cached to `cwts_output/scope_llm_borderline_*.json` and `scope_paper_llm_*.json`.

It consumes step 3's labels via `load_gpt_labels_single` / `load_gpt_labels_all`, which read `cluster_id`, `short_label`, `long_label`, `keywords` and `summary` from `taxonomy_labelling.cluster_labels_{level}_{ts}`. This is a soft dependency — missing labels fall back to `Cluster {id}` placeholders — but it is not only cosmetic: the hard-negative pass compares label tokens between in-scope and candidate communities, so unlabelled clusters weaken the scope classification itself, not just the display.

Outputs six HTML files — `scope_dashboard`, `drift_dashboard`, `clusters`, `network_maps`, `paper_examples` and the `combined_dashboard` wrapper — plus the one BigQuery table the mapper depends on, `paper_scope_{ts}` (`int_id`, `journal`, `scope_code`, `is_oos`, `is_borderline`). Set `PAPER_SCOPE_TO_BQ=0` to suppress that write.

> **Note:** `paper_scope` only covers journals passed in `JOURNALS`, because the write happens inside the per-journal loop. `main.py` defaults to eight titles.

### 5. GT network map — `scripts/build_gt_network_map.py`

Optional validation step behind `--gt`. Overlays a manually labelled ground-truth spreadsheet (`manual_scope_check_truth.ods`, read from OneDrive) onto the community map so scope calls can be checked against human judgement. Writes `output/gt_network_map.html`.

### 6. PDF report — `src/build_scope_drift_report_pdf.py`

Parses the JavaScript constants embedded in `scope_dashboard.html` and `drift_dashboard.html` and renders `Scope_Drift_Report.pdf`. It reads no BigQuery at all, so it hard-depends on step 4 having produced both files — it exits with `Missing <path>` if either is absent.

From the scope page it takes `journals[]` (name, article count, out-of-scope count, example papers) plus `run_metadata` and `meta` for the run id, year range and cluster level. From the drift page it takes `summary[]` (journal, JSD, entropy delta), which sets the journal ordering and the High/Medium/Low drift bands. Paths are overridable with `--scope-html`, `--drift-html` and `--out-pdf`.

---

## Typical invocations

```powershell
# Rebuild outputs from an existing export and clustering
python main.py -t 20260818_090851 --skip-leiden

# Re-cluster an existing export, then rebuild everything
python main.py -t 20260818_090851

# Brand new network for a wider baseline, then the full pipeline
python main.py --export --start-year 2020 --end-year 2026 --network-mode full

# Dashboard only (the step that writes paper_scope)
python main.py -t 20260818_090851 --skip-leiden --skip-taxonomy --skip-pdf
```

---

## Risks and notes

- **Steps fail closed.** `run_step` raises `SystemExit` on any non-zero exit code, so a failure aborts the remaining steps rather than producing partial output silently.
- **Two steps cost real money.** Taxonomy naming and the dashboard both call OpenAI per cluster or per paper batch. Taxonomy has no resume, so a re-run pays for every cluster again.
- **Step 6 depends on step 4's files, not on BigQuery.** Skipping the dashboard while keeping the PDF will fail on a missing `scope_dashboard.html`.
- **`subprocess_leiden.py` has a hardcoded `DATA_TIMESTAMP` fallback.** Running it directly without `RUN_TIMESTAMP` set will silently cluster whatever run that constant points at.
- **`java -Xmx350g`** means step 2 is only viable on the large-memory host.

Disclaimer: This page was created with AI assistance.
