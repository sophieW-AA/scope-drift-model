# Opportunity mapper

The supported opportunity workflow produces the graded 252-row journal-market
assessment and the readable Excel used for presentations.

The code lives in ``src/opportunities``. From the repository root:

```powershell
python src/opportunities/run.py --run 20260827_081311
```

The core rule is:

1. **OpenAlex sizes the world market.**
2. **Leiden tests whether that market has a coherent citation-community scope.**
3. **Frontiers presence selects the action only after the market qualifies.**

This prevents Frontiers volume from making its existing publishing communities
look like market opportunities.

---

## Quick start

From the repository root, using the `scope_drift` conda environment:

```powershell
python src/opportunities/run.py
```

That one command:

1. discovers the latest complete, taxonomy-labelled scope-drift run;
2. evaluates all 252 OpenAlex subfields;
3. maps qualified markets to Leiden meso and micro communities by DOI;
4. grades and routes every field;
5. writes the result and manifest to BigQuery;
6. creates local JSON, manifest and readable Excel files; and
7. writes a timestamped run log.

Pin the citation-network run when reproducibility matters:

```powershell
python src/opportunities/run.py --run 20260827_081311
```

Generate deterministic template scopes without GPT:

```powershell
python src/opportunities/run.py --run 20260827_081311 --skip-llm
```

Run locally without replacing the BigQuery final tables:

```powershell
python src/opportunities/run.py --run 20260827_081311 --no-write-bq
```

---

## Local files

No generated opportunity files are written into this repository. The default
location is:

```text
C:\Users\sophie.wilson\Documents\scope_drift_outputs\opportunities\
├── output\
│   ├── final_journal_opportunities_YYYYMMDD.json
│   ├── final_journal_opportunities_YYYYMMDD.manifest.json
│   └── leiden_journal_opportunities_readable_YYYYMMDD.csv.xlsx
└── logs\
    └── opportunities_YYYYMMDD_HHMMSS.log
```

Override the root for another machine:

```powershell
$env:OPPORTUNITIES_OUTPUT_ROOT = "D:\analytics\opportunities"
python src/opportunities/run.py
```

The Excel contains the same analytical rows as the JSON. It adds readable
labels plus two narrative columns:

- **Community market (Leiden)** — deterministic evidence about mapped
  non-Frontiers papers, 80% coverage, meso communities and micro themes.
- **Journal scope** — concise scope wording grounded in those community names.
  GPT-4o writes it by default; `--skip-llm` uses a deterministic template.

---

## How the final method works

### 1. Select a complete scope-drift run

`final_opportunities.discover_latest_complete_run()` requires classification,
publication metadata, paper-scope flags, and both meso and micro taxonomy
labels. Small probe runs are rejected.

### 2. Qualify markets independently

`fetch_live_market()` counts all-publisher English-language journal articles
in OpenAlex. A subfield qualifies when it has:

- at least **10,000 world articles in 2025**; and
- at least **5% CAGR from 2022 to 2025**.

Frontiers counts cannot change this result or its market score.

### 3. Validate the citation scope

Qualified OpenAlex papers join to AIRAK/Leiden papers by normalized DOI.
Non-Frontiers papers are ranked across meso communities. The smallest sibling
set covering **80%** becomes the proposed journal market; the leading micro
communities become candidate section themes.

Scope confidence is:

- **high** — at least 300 mapped papers, 80% coverage, no more than 30 meso
  communities;
- **medium** — at least 100 papers, 70% coverage, no more than 45 communities;
- **low** — anything weaker, including poor taxonomy-label coverage.

Low confidence blocks a launch.

### 4. Assess Frontiers ownership and coverage

Only now are Frontiers titles attached. The mapper asks whether a dedicated
title names the market, whether one title owns at least 40% of Frontiers
output, and whether Frontiers is below or above its global portfolio share.

### 5. Route the action

```text
market failed                         -> pass_market
scope confidence is low               -> validate_scope
dedicated Frontiers title exists      -> grow_existing
fewer than 30 FI papers in three years -> launch_greenfield
otherwise                             -> launch_consolidation
```

### 6. Export

`opportunities.export_workbook` converts the final DataFrame into the branded,
filtered Excel. It does not recalculate the analytics.

---

## Commands

| Goal | Command |
|---|---|
| Full supported run + Excel | `python src/opportunities/run.py` |
| Pin Leiden run | `python src/opportunities/run.py --run <timestamp>` |
| Avoid GPT calls | `python src/opportunities/run.py --skip-llm` |
| Avoid BigQuery writes | `python src/opportunities/run.py --no-write-bq` |
| Analysis only, no local files | `python src/opportunities/run.py --skip-excel` |
| Re-export an existing JSON | `python src/opportunities/export_workbook.py --json <file>` |
| Re-export to a chosen file | `python src/opportunities/export_workbook.py --json <file> --out <file.xlsx>` |
| Direct final-module run | `python src/opportunities/final_opportunities.py --excel` |

---

## BigQuery outputs

Project: `ocean-tech-adv-analytics-c-tfs`, dataset:
`opportunity_mapping`, location: EU.

The supported final run writes:

- `final_journal_opportunities_{scope_run}`
- `final_journal_opportunities_manifest_{scope_run}`

The manifest records source-table timestamps, the selected Leiden run and all
decision thresholds.

---

## Module map

| Module | Responsibility |
|---|---|
| `run.py` / `__main__.py` | One-command orchestration, file logging and local artifacts |
| `final_opportunities.py` | Market facts, DOI overlap, Leiden scope, scoring and routing |
| `export_workbook.py` | Readable Excel and narrative columns |
| `paths.py` | External output/log directories |
| `bq.py` | BigQuery reads and writes |
| `config.py` | Governed thresholds and table names |
| `seed_jd.py` | One-off load of the governed JD reference |

---

## Legacy diagnostic phases

The older P0-P5 community mapper and launch-unit experiments remain available
for diagnostics:

```powershell
python src/opportunities/run.py --phase all --run 20260827_081311
python src/opportunities/run.py --phase p0 --run 20260827_081311
python src/opportunities/run.py --phase units --run 20260827_081311
```

These phases write their versioned tables to BigQuery. They are **not** the
source of the presentation Excel; the default `final` phase is.

---

## Requirements and costs

- Google Application Default Credentials with BigQuery access
- `OPENAI_API_KEY` for GPT-written journal scopes
- `pandas`, `pandas-gbq`, `google-cloud-bigquery`, `openpyxl`, `openai`

The final run executes large OpenAlex and DOI-overlap queries. GPT is used only
for the human-readable **Journal scope** column, not for market qualification,
scoring or routing.
