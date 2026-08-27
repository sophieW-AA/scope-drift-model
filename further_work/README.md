# Further work — Neurorobotics scope drift

Analysis pack for run `20260721_122750` focused on **Frontiers in Neurorobotics**.

## Contents

| File | Purpose |
|------|---------|
| `neurorobotics_scope_drift_deep_dive.ipynb` | Walkthrough notebook (onset, mix shift, OOS audit, sections/RTs, recommendations) |
| `neuro_analysis.py` | Shared loaders/helpers used by notebook + PDF |
| `probe_sections_rts.py` | Joins run papers → RDM taxonomy + RTs |
| `analyze_rts.py` | RT vs spontaneous, OOS/drift contributors, keep/gate/remove/add |
| `neurorobotics_rt_deep_dive.csv` | Per-RT metrics + recommendations |
| `neurorobotics_rt_analysis_summary.json` | Verdict + lists for PDF |
| `neurorobotics_section_rt_summary.json` | Verdict + counts from the section probe |
| `neurorobotics_rt_*.csv` | RT launch cohorts / OOS-by-topic / year×RT tables |
| `build_neurorobotics_brief_pdf.py` | Builds the stakeholder PDF |
| `Neurorobotics_Scope_Drift_Brief.pdf` | Branded brief (generate via script or last notebook cell) |
| `figures/` | Charts written by notebook/PDF |

## How to run

From repo root (conda env `scope_drift`):

```powershell
# Section / Research Topic join (needs BigQuery)
python further_work/probe_sections_rts.py

# RT deep-dive: OOS, drift, keep/cut/add (needs BigQuery)
python further_work/analyze_rts.py

# PDF only
python further_work/build_neurorobotics_brief_pdf.py
```

Requires existing dashboards in `output/` from the pipeline run.

**Section finding:** Neurorobotics has **no** journal sections in RDM/SF — use Research Topics as the launch unit for drift attribution.
