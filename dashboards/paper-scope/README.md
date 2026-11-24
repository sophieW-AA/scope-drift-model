# Paper scope dashboard

A single HTML page showing how the topics of Frontiers journals are changing, built from the stored scope-drift tables in BigQuery.

Only the code lives here. The built page and the query results contain journal-level results and paper titles, and this repository is public, so they are git-ignored. Do not commit them.

## Files

- `build.py` runs the BigQuery queries, saves each result under `OUT/cache_<RUN>/`, works out the layouts and writes `OUT/network_bubbles_<RUN>.html`.
- `page_head.html` is the page's HTML and CSS, up to the opening of the data script.
- `page_script.js` is the page's JavaScript, plus the closing tags.
- `test_dashboard.js` is a smoke test for a built page.

## Build

```bash
pip install google-cloud-bigquery db-dtypes pandas pyarrow numpy scipy python-igraph scikit-learn
RUN=20260827_081311 OUT=./out python3 build.py            # reuses saved results in OUT/cache_<RUN>/
RUN=20260827_081311 OUT=./out python3 build.py --refresh  # re-runs every query
```

Queries run in project `ocean-tech-adv-analytics-c-tfs` (EU) and are billed to `gcp-innovation-hub`, using your Application Default Credentials. Each query has a 20 GB scan cap.

## Test

```bash
npm install jsdom
node test_dashboard.js out/network_bubbles_20260827_081311.html
```

This checks that every journal and tab renders, and that the headline and per-year figures equal the stored totals.

## Where the numbers come from

The page has a **Data & queries** tab that lists every query with its SQL, the tables it reads, the rows it returned and what it feeds.

- **Stored, read as is:** the share of papers outside the core, overall and by year; borderline and title-rule counts; topic mix change, change in focus and its rank; core broad fields gained and lost; example papers.
- **Worked out by `build.py` (estimates, not stored):**
  - topic positions on the journal map, laid out from citation links between topics
  - journal positions in Frontiers view, from a t-SNE layout of each journal's topic mix, then separated so bubbles don't overlap
  - similar journals
  - main topics by year, using the stored 80% threshold
  - bubble colour, the status most of a topic's papers carry

Both layouts use fixed seeds, so the same inputs give the same page.

## Notes

- Since 12 Nov 2026 the scope tables hold both broad-field (`macro`) and topic (`meso`) rows. The queries filter to `cluster_level = 'macro'`.
- The "Main topics by year" tab does not match the pipeline's stored core: it agrees for only 19 of 209 journals. It is labelled as an estimate on the page.
- Paper-level AI verdicts are enabled in the run config but none are stored, so none are shown.
