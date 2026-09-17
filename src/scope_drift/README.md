# Scope-drift further work

Journal-level RT/section probes and stakeholder PDF briefs, pulled in from
`scope_drift_outputs/further_work`. Run from the repository root with the
`scope_drift` conda environment.

Artifacts (CSV, JSON, PDF) still write to `scope_drift_outputs/further_work`.
Dashboards are read from `scope_drift_outputs/output`.

```powershell
python src/scope_drift/probe_sections_rts.py
python src/scope_drift/analyze_rts.py
python src/scope_drift/build_neurorobotics_brief_pdf.py

python src/scope_drift/build_all_journal_briefs.py
python src/scope_drift/build_all_journal_briefs.py --journal "Frontiers in Earth Science"
python src/scope_drift/build_all_journal_briefs.py --skip-bq
```

| File | Purpose |
|------|---------|
| `neuro_analysis.py` | Shared loaders for dashboard HTML |
| `journal_profile.py` | Per-journal gainer/loser communities |
| `probe_sections_rts.py` | Papers → RDM taxonomy + Research Topics |
| `probe_taxonomy_sections.py` | Neurorobotics taxonomy inventory probe |
| `analyze_rts.py` | RT vs spontaneous, keep/gate/remove/add |
| `build_neurorobotics_brief_pdf.py` | Neurorobotics stakeholder PDF |
| `build_journal_brief_pdf.py` | Same brief layout for other journals |
| `build_all_journal_briefs.py` | Probe + analyse + PDF for every test journal |
