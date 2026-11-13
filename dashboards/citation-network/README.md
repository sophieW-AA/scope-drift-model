# Frontiers author citation network dashboard

Static, self-contained HTML dashboard of the person citation network, run `20261016_150236`
(Frontiers journals only, papers published 2023–2026; 817,257 authors, 27 macro / 250 meso / 777 micro communities).

Tabs: **Community map** (27 macro communities, MDS layout from macro-to-macro links; solid lines > 0.9×,
dotted lines = each macro's 3 strongest neighbours), **Network** (macro → meso → micro drill-down),
**Details** (author pages with their 50 strongest links), **Data** (every query used, with bytes scanned).

## Files

| File | What it does |
|---|---|
| `export.py` | Runs all BigQuery queries and writes the data to `/home/user/cn/` (about 35 GB billed, 1–2 minutes). Records each query in `cn/queries.json` for the Data tab. |
| `template.html` | The dashboard page (HTML, CSS, D3 code) with placeholders for the data. |
| `build.py` | Gzips the data, embeds it in the template and writes `artifacts/citation-network/index.html` (~25 MB). |
| `test_dashboard.js` | Runs every view against the real data in jsdom (`npm install jsdom@24 d3@7`, then `node test_dashboard.js`). |

## Rebuild

```bash
python3 export.py      # needs GOOGLE_APPLICATION_CREDENTIALS; billing project gcp-innovation-hub
python3 build.py
node --max-old-space-size=650 test_dashboard.js
```

Run each step as its own process, not inside a long-lived notebook kernel: a 1 GB workspace runs out of
memory if the data stays loaded between steps.

## Not in this repo

This repo is public. The built page and the exported data contain researcher names, AIRAK IDs and
citation links, so they are git-ignored. Rebuild them with the steps above, or use the private copy
exported from FrontiersOS.
