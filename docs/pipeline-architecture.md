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

A person run is a separate path. `--network-entity person` builds an author citation network, runs Leiden, and stops. It does not name clusters, build dashboards, or write the read model. See [Person network](#person-network).

---

## Step reference

| Step | Flag | File | Reads | Writes |
|---|---|---|---|---|
| **1 Export** | `--export` (off by default) | `src/cwts_export.py` | `ocean-breeze-tier-1.airak` Publication, PublicationCitation, Journal | `pubs_raw_{ts}`, `pub_metadata_raw_{ts}`, `cit_links_raw_{ts}`, `run_metadata_{ts}` |
| **2 Leiden** | on by default, `--skip-leiden` | `src/subprocess_leiden.py` + `publicationclassification.jar` | `pubs_raw_{ts}`, `cit_links_raw_{ts}` | `classification_raw_{ts}` |
| **2b Taxonomy assignment** | `--taxonomy-enrichment` (off by default) | `src/taxonomy_assignment.py` | `classification_raw_{ts}`, `pub_metadata_raw_{ts}`, AIRAK, `fw_taxonomy` v6 | rows appended to `classification_raw_{ts}` with `assignment_method` |
| **3 Taxonomy** | on by default, `--skip-taxonomy` | `src/taxonomy_naming.py` | Leiden rows of `classification_raw_{ts}` ⋈ `pub_metadata_raw_{ts}`, Frontiers taxonomy, OpenAI | `cluster_labels_{level}_{ts}`, `cluster_taxonomy_labels_{level}_{ts}` |
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

> **Note:** `largest_component_only=true` drops papers disconnected from the main component. On run `20260818_090851` that is ~453k of 17.1M rows (2.6%). The export still writes Frontiers papers that have no citation edges into `pubs_raw` and `pub_metadata_raw`, without adding edges.

### 2b. Taxonomy assignment — `src/taxonomy_assignment.py`

Optional. Run it with `python main.py --timestamp <ts> --skip-leiden --taxonomy-enrichment` after Leiden. It does not run unless that flag is set.

Frontiers papers in the run's journal and year window that Leiden did not classify — no citations, or outside the largest component — are scored against the Leiden clusters with taxonomy v6 (`fw_taxonomy`, CORE_TOPIC, score level 3). Profiles are fit on Leiden papers only. A paper is written back into `classification_raw_{ts}` at micro, then meso, then macro, and only as deep as the similarity and margin thresholds allow.

`assignment_method` on that table is `leiden`, `taxonomy`, or `unassigned`. Leiden rows keep their cluster ids. Cluster names stay based on the Leiden rows. The network view still draws citation edges only; community coverage can show the extra taxonomy count beside the Leiden size.

On the `20260827_081311` holdout, macro placement at similarity 0.15 and margin 0.02 was right about 78% of the time. Meso and micro stayed below 41% and 36%, so those levels are closed and a taxonomy row only receives a macro id.

A dry run prints acceptance counts and writes nothing:

```text
python src/taxonomy_assignment.py --timestamp 20260827_081311 --audit
python src/taxonomy_assignment.py --timestamp 20260827_081311 --calibrate
python src/taxonomy_assignment.py --timestamp 20260827_081311
```

### 3. Taxonomy naming — `src/taxonomy_naming.py`

Turns numeric cluster ids into readable labels. It joins classification to metadata, samples papers per cluster, builds a per-cluster brief, and asks GPT to assign each cluster to `core` and `bleed` categories from the Frontiers taxonomy. `export_dashboard_labels` then takes the top-ranked core category as `short_label`. When `assignment_method` is present, only `leiden` rows are sampled, so taxonomy-assigned papers do not change the names.

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

# Author citation network, then Leiden, then stop
python main.py --network-entity person --export --start-year 2023 --end-year 2026

# Global author citation network: no journal filter, then Leiden
python main.py --network-entity person --export --network-mode global --start-year 2020 --end-year 2026

# Global author network, 2024-2026, first and last authors only
python main.py --network-entity person --export --network-mode global --first-last-only --start-year 2024 --end-year 2026

# One citation step around four authors, every paper of theirs, every author.
python main.py --network-entity person --export --person-seed-all-years --end-year 2026 --person-seed-author-ids "34360390519,1374390108942,34360385232,94489924562" --person-citation-hops 1

# One citation step around authors affiliated in Belgium, Spain, and Italy,
# 2023-2026. First and last authors only. A sole author counts as both.
python main.py --network-entity person --export --first-last-only --start-year 2023 --end-year 2026 --person-seed-countries "BEL,ESP,ITA" --person-citation-hops 1

# Re-cluster an existing person export
python main.py --network-entity person -t 20261016_120000
```

---

## Risks and notes

- **Steps fail closed.** `run_step` raises `SystemExit` on any non-zero exit code, so a failure aborts the remaining steps rather than producing partial output silently.
- **Two steps cost real money.** Taxonomy naming and the dashboard both call OpenAI per cluster or per paper batch. Taxonomy has no resume, so a re-run pays for every cluster again.
- **Step 6 depends on step 4's files, not on BigQuery.** Skipping the dashboard while keeping the PDF will fail on a missing `scope_dashboard.html`.
- **`subprocess_leiden.py` has a hardcoded `DATA_TIMESTAMP` fallback.** Running it directly without `RUN_TIMESTAMP` set will silently cluster whatever run that constant points at.
- **`java -Xmx350g`** means step 2 is only viable on the large-memory host.
- **A person Leiden run loads every author-author edge into memory.** One paper citation becomes a pair for every citing author and cited author. Leiden logs the author and edge counts before the jar starts. The person block uses macro resolution `2e-6` and a macro minimum of 5,000.

---

## Person network

`--network-entity person` on `main.py` runs [src/person_network_export.py](../src/person_network_export.py) and then Leiden. Taxonomy naming, the dashboard, the read model, the PDF, and the opportunities scripts stay on the paper dataset and are not called.

Nodes are AIRAK authors (`Author.AuthorId`). Papers are not nodes. An edge exists when a paper by author A cites a paper by author B. Both papers have to be published in `START_YEAR`–`END_YEAR`.

| `NETWORK_MODE` | Who gets in |
|---|---|
| `journal_window` | Both papers are also in `JOURNAL_IDS`. This is the person default when `--network-mode` is omitted. |
| `global` | No journal filter. Every citation whose two papers fall in the year window. Pass `--network-mode global`. |
| `seed` | An induced citation neighbourhood around papers by `PERSON_SEED_AUTHOR_IDS`, expanded by `PERSON_CITATION_HOPS`. `main.py` selects this mode when `--person-seed-author-ids` is passed. `--person-seed-all-years` keeps every paper by those authors and does not apply the year window to the hops. |
| `country` | Same hop expansion, starting from papers whose `PublicationAuthor.OrganizationId` is in a country listed by `--person-seed-countries` (ISO alpha-3, for example `BEL,USA,ESP,ITA`). Each hop adds papers cited by the current set and papers that cite it. |

Authors who are not on one of those citing or cited papers are left out. Paper modes `ego` and `full` are not person networks.

The edge weight is the paper export's temporal decay, `exp(-(end_year - cited_paper_year) / TEMPORAL_DECAY_TAU)`, tau 5, floored at 0.01. That decay is multiplied by the citing author's role weight and the cited author's role weight, then summed over citations. The same weight is stored in both directions. Pairs where both ends are the same `AuthorId` are dropped.

| Role | Weight |
|---|---|
| Sole author | 1 |
| First author (`IsFirstAuthor`, or `AuthorSequenceNumber = 1`) | 1 |
| Last author (`IsLastAuthor`, or the highest `AuthorSequenceNumber` on that paper) | 1 |
| Middle author | 0.25 |

`PublicationAuthor` has `AuthorSequenceNumber`, `IsFirstAuthor`, and `IsLastAuthor`. Those are the order columns. There is no guessed position.

Writes go only to `ocean-tech-adv-analytics-c-tfs.raw_citation_network_data_person`. Every table ends in `_person_{timestamp}`.

| Table | Grain | Columns |
|---|---|---|
| `pubs_raw_person_{ts}` | author | `int_id`, `core_pub` |
| `pub_metadata_raw_person_{ts}` | author | `int_id`, `author_id`, `name` |
| `cit_links_raw_person_{ts}` | author pair | `int_id1`, `int_id2`, `weight` |
| `classification_raw_person_{ts}` | author | `int_id`, `micro`, `meso`, `macro` |
| `run_metadata_person_{ts}` | run | config, including `network_entity = person` |
| `author_papers_person_{ts}` | author on a paper | `publication_id`, `author_id`, `int_id`, `role_weight` |

`author_papers_person_{ts}` records which papers produced the edges. It does not assign a cluster to a paper. Join `pub_metadata_raw_person_{ts}.author_id` to `classification_raw_person_{ts}` on `int_id` to see which macro, meso, and micro an author landed in.

`largest_component_only` is false for `seed` and `country` runs, so a separate component around the requested authors is kept. Other person runs keep the largest component only.

Disclaimer: This page was created with AI assistance.
