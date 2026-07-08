"""
build_scope_dashboard.py
=========================
Creates the full scope drift dashboard using CWTS data from BigQuery.
Replicates the render_script.js visualization with:
- KPI strip
- OOS by journal/year charts
- Community bar chart
- Scatter plots per journal (bubble = community)

Data source : scope_drift_raw BigQuery tables
Output      : output/scope_dashboard.html
"""

import json
import logging
import math
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np
import pandas as pd
import igraph as ig
from google.cloud import bigquery

# ──────────────────────────────────────────────────────────────────────────────
# CONFIG
# ──────────────────────────────────────────────────────────────────────────────
BQ_PROJECT = "ocean-tech-adv-analytics-c-tfs"
BQ_DATASET = "scope_drift_raw"

TBL_CLASSIF = f"{BQ_PROJECT}.{BQ_DATASET}.classification_raw_20260617_120737"
TBL_PUB_META = f"{BQ_PROJECT}.{BQ_DATASET}.pub_metadata_raw_20260617_122707"
TBL_CIT_LINKS = f"{BQ_PROJECT}.{BQ_DATASET}.cit_links_raw_20260617_122707"
# FROM `ocean-tech-adv-analytics-c-tfs.scope_drift_raw.classification_raw_20260617_120737` cit

# JOIN ocean-tech-adv-analytics-c-tfs.scope_drift_raw.pub_metadata_raw_20260617_122707 met
# ON cit.int_id = met.int_id

# --  JOIN ocean-tech-adv-analytics-c-tfs.scope_drift_raw.pubs_raw_20260617_122707 pubs
# --  ON met.int_id = pubs.int_id

# --   JOIN ocean-tech-adv-analytics-c-tfs.scope_drift_raw.cit_links_raw_20260617_122707 link
# --  ON link.int_id1 = pubs.int_id
# Target journals
JOURNALS = [
    "Frontiers in Immunology",
    "Frontiers in Public Health",
    "Frontiers in Oncology",
    "Frontiers in Psychology",
    "Frontiers in Pharmacology",
]

# Use meso clusters as "communities" (now has 53 clusters after tuning)
CLUSTER_LEVEL = "macro"
PRIMARY_COVERAGE = 0.8  # Primary clusters = smallest set covering 80% of papers

OUTPUT_PATH = Path(__file__).resolve().parent.parent / "output" / "scope_dashboard.html"

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s  %(message)s", datefmt="%H:%M:%S"
)
log = logging.getLogger(__name__)


# ──────────────────────────────────────────────────────────────────────────────
# DATA LOADING
# ──────────────────────────────────────────────────────────────────────────────
def load_papers(client) -> pd.DataFrame:
    """Load papers with cluster assignments."""
    log.info("[1/6] Loading papers from BigQuery …")

    journals_str = ", ".join(f"'{j}'" for j in JOURNALS)

    query = f"""
    SELECT 
        c.int_id,
        c.{CLUSTER_LEVEL} AS community,
        m.journal,
        m.title,
        EXTRACT(YEAR FROM PARSE_DATE('%Y-%m-%d', m.date)) AS pub_year
    FROM `{TBL_CLASSIF}` c
    JOIN `{TBL_PUB_META}` m ON c.int_id = m.int_id
    WHERE m.journal IN ({journals_str})
    """

    df = client.query(query).to_dataframe()
    df = df.dropna(subset=["pub_year"])
    df["pub_year"] = df["pub_year"].astype(int)

    log.info(f"       Loaded {len(df):,} papers")
    log.info(f"       Journals: {df['journal'].nunique()}")
    log.info(f"       Communities: {df['community'].nunique()}")
    log.info(f"       Years: {df['pub_year'].min()}–{df['pub_year'].max()}")

    return df


def load_citations_for_layout(client) -> pd.DataFrame:
    """Load citation edges for computing scatter positions."""
    log.info("[2/6] Loading citations for layout …")

    journals_str = ", ".join(f"'{j}'" for j in JOURNALS)

    query = f"""
    WITH journal_papers AS (
        SELECT c.int_id, c.{CLUSTER_LEVEL} AS community
        FROM `{TBL_CLASSIF}` c
        JOIN `{TBL_PUB_META}` m ON c.int_id = m.int_id
        WHERE m.journal IN ({journals_str})
    )
    SELECT 
        jp1.int_id AS src,
        jp2.int_id AS tgt,
        jp1.community AS src_comm,
        jp2.community AS tgt_comm,
        cl.weight
    FROM `{TBL_CIT_LINKS}` cl
    JOIN journal_papers jp1 ON cl.int_id1 = jp1.int_id
    JOIN journal_papers jp2 ON cl.int_id2 = jp2.int_id
    """

    try:
        job = client.query(query)
        df = job.result(timeout=300).to_dataframe()
        log.info(f"       Loaded {len(df):,} citation edges")
    except Exception as e:
        log.warning(f"       Citation query failed: {e}")
        df = pd.DataFrame(columns=["src", "tgt", "src_comm", "tgt_comm", "weight"])

    return df


# ──────────────────────────────────────────────────────────────────────────────
# COMPUTE METRICS
# ──────────────────────────────────────────────────────────────────────────────
def compute_primary_clusters(df: pd.DataFrame, journal: str) -> set:
    """Find smallest set of clusters covering PRIMARY_COVERAGE of papers."""
    jdf = df[df["journal"] == journal]
    counts = jdf["community"].value_counts()
    total = counts.sum()

    primary = set()
    cumsum = 0
    for comm, count in counts.items():
        primary.add(comm)
        cumsum += count
        if cumsum >= total * PRIMARY_COVERAGE:
            break

    return primary


def compute_scatter_positions(df: pd.DataFrame, df_edges: pd.DataFrame) -> dict:
    """Compute x,y positions for each paper using community-based layout."""
    log.info("[3/6] Computing scatter positions …")

    # For large datasets, use community-based positioning instead of full graph layout
    # This is much faster and still shows meaningful structure

    paper_ids = df["int_id"].unique()
    n_papers = len(paper_ids)

    if df_edges.empty or n_papers > 50000:
        log.info("       Using community-based layout (faster for large datasets)")

        # Group papers by community, position communities in a circle
        communities = df["community"].unique()
        n_comm = len(communities)

        # Assign each community a position on a circle
        comm_positions = {}
        for i, comm in enumerate(communities):
            angle = 2 * np.pi * i / max(n_comm, 1)
            comm_positions[comm] = (
                0.5 + 0.35 * np.cos(angle),
                0.5 + 0.35 * np.sin(angle),
            )

        # Position papers with jitter around their community center
        positions = {}
        np.random.seed(42)
        for _, row in df.iterrows():
            cx, cy = comm_positions.get(row["community"], (0.5, 0.5))
            jitter = 0.08
            x = cx + np.random.uniform(-jitter, jitter)
            y = cy + np.random.uniform(-jitter, jitter)
            positions[row["int_id"]] = (float(x), float(y))

        log.info(
            f"       Positioned {len(positions):,} papers in {n_comm} community clusters"
        )
        return positions

    # For smaller datasets, use actual graph layout
    log.info(f"       Building graph with {n_papers:,} nodes")

    id_to_idx = {pid: i for i, pid in enumerate(paper_ids)}
    idx_to_id = {i: pid for pid, i in id_to_idx.items()}

    # Sample edges if too many
    max_edges = 500000
    if len(df_edges) > max_edges:
        log.info(f"       Sampling {max_edges:,} edges from {len(df_edges):,}")
        df_edges = df_edges.sample(n=max_edges, random_state=42)

    edges = []
    weights = []
    for _, row in df_edges.iterrows():
        src_idx = id_to_idx.get(row["src"])
        tgt_idx = id_to_idx.get(row["tgt"])
        if src_idx is not None and tgt_idx is not None:
            edges.append((src_idx, tgt_idx))
            weights.append(row["weight"])

    if not edges:
        log.info("       No valid edges, using random positions")
        positions = {}
        for _, row in df.iterrows():
            positions[row["int_id"]] = (np.random.random(), np.random.random())
        return positions

    log.info(f"       {len(edges):,} edges, computing layout …")

    g = ig.Graph(n=n_papers, edges=edges, directed=False)
    g.es["weight"] = weights

    layout = g.layout_drl(weights="weight")

    # Normalize to [0, 1]
    coords = np.array(layout.coords)
    coords_min = coords.min(axis=0)
    coords_max = coords.max(axis=0)
    coords_range = coords_max - coords_min
    coords_range[coords_range == 0] = 1
    coords_norm = (coords - coords_min) / coords_range

    positions = {
        idx_to_id[i]: (float(coords_norm[i, 0]), float(coords_norm[i, 1]))
        for i in range(n_papers)
    }

    log.info("       Layout complete")
    return positions


def compute_journal_stats(df: pd.DataFrame, positions: dict) -> list:
    """Compute statistics for each journal."""
    log.info("[4/6] Computing journal statistics …")

    journals_data = []
    years = sorted(df["pub_year"].unique())

    for journal in JOURNALS:
        jdf = df[df["journal"] == journal].copy()
        if jdf.empty:
            continue

        primary_clusters = compute_primary_clusters(df, journal)
        jdf["is_oos"] = ~jdf["community"].isin(primary_clusters)

        n_articles = len(jdf)
        n_oos = jdf["is_oos"].sum()
        oos_pct = (n_oos / n_articles * 100) if n_articles else 0

        # OOS by year
        oos_by_year = []
        for year in years:
            ydf = jdf[jdf["pub_year"] == year]
            if len(ydf) >= 10:
                y_oos = ydf["is_oos"].sum()
                oos_by_year.append(
                    {
                        "year": int(year),
                        "articles": int(len(ydf)),
                        "out_of_scope": int(y_oos),
                        "out_of_scope_pct": float(y_oos / len(ydf) * 100),
                    }
                )

        # Top communities for this journal
        comm_counts = jdf["community"].value_counts()
        top_comms = []
        for comm, count in comm_counts.head(10).items():
            top_comms.append(
                {
                    "comm_id": int(comm),
                    "label": f"Cluster {comm}",
                    "is_primary": comm in primary_clusters,
                    "papers_in_comm": int(count),
                    "share_of_journal": round(count / n_articles * 100, 1),
                }
            )

        # Scatter data (paper positions)
        scatter = []
        for _, row in jdf.iterrows():
            if row["int_id"] in positions:
                x, y = positions[row["int_id"]]
                scatter.append(
                    {
                        "x": x,
                        "y": y,
                        "c": int(row["community"]),
                        "t": (row["title"] or "")[:60],
                    }
                )

        journals_data.append(
            {
                "name": journal,
                "articles": n_articles,
                "out_of_scope": int(n_oos),
                "out_of_scope_pct": round(oos_pct, 1),
                "n_primary_clusters": len(primary_clusters),
                "primary_coverage_pct": round(PRIMARY_COVERAGE * 100, 1),
                "top_communities": top_comms,
                "oos_by_year": oos_by_year,
                "scatter": scatter,
            }
        )

        log.info(f"       {journal}: {n_articles:,} papers, {oos_pct:.1f}% OOS")

    return journals_data


def compute_community_stats(df: pd.DataFrame) -> list:
    """Compute statistics for each community."""
    log.info("[5/6] Computing community statistics …")

    communities = []

    comm_counts = (
        df.groupby("community")
        .agg(
            size=("int_id", "count"),
        )
        .reset_index()
    )

    for _, row in comm_counts.nlargest(50, "size").iterrows():
        comm_id = row["community"]
        cdf = df[df["community"] == comm_id]

        # Journal breakdown
        journal_counts = cdf["journal"].value_counts()
        frontiers_count = journal_counts.sum()  # All are Frontiers in our data

        dominant_journal = journal_counts.index[0] if len(journal_counts) else "Unknown"
        dominant_pct = (
            round(journal_counts.iloc[0] / len(cdf) * 100, 1)
            if len(journal_counts)
            else 0
        )

        top_journals = [
            {"name": j, "count": int(c), "pct": round(c / len(cdf) * 100, 1)}
            for j, c in journal_counts.head(3).items()
        ]

        communities.append(
            {
                "id": int(comm_id),
                "label": f"Cluster {comm_id}",
                "size": int(row["size"]),
                "frontiers_pct": 100.0,  # All papers are from Frontiers journals
                "dominant_journal": dominant_journal,
                "dominant_pct": dominant_pct,
                "top_journals": top_journals,
            }
        )

    return communities


# ──────────────────────────────────────────────────────────────────────────────
# HTML TEMPLATE
# ──────────────────────────────────────────────────────────────────────────────
HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Scope Drift Dashboard</title>
<script src="https://cdn.plot.ly/plotly-2.35.2.min.js"></script>
<style>
:root {
  --bg: #f6f8fa;
  --card: #ffffff;
  --text: #1a1f36;
  --muted: #5f6b7c;
  --border: #e3e7ee;
  --green: #1f8a4c;
  --red: #c93030;
  --amber: #d4a300;
  --blue: #2c5fa3;
}
* { box-sizing: border-box; margin: 0; padding: 0; }
body {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  background: var(--bg);
  color: var(--text);
  line-height: 1.5;
}
header {
  background: var(--card);
  padding: 20px 24px;
  border-bottom: 1px solid var(--border);
}
header h1 { font-size: 1.4rem; font-weight: 700; margin-bottom: 4px; }
header p { color: var(--muted); font-size: 0.85rem; }
#scopeDesc { font-weight: 500; }

.kpi-row {
  display: flex;
  gap: 12px;
  padding: 16px 24px;
  background: var(--card);
  border-bottom: 1px solid var(--border);
  flex-wrap: wrap;
}
.kpi {
  flex: 1;
  min-width: 140px;
  padding: 12px 16px;
  background: var(--bg);
  border-radius: 8px;
}
.kpi-label { font-size: 0.75rem; color: var(--muted); text-transform: uppercase; letter-spacing: 0.5px; }
.kpi-value { font-size: 1.5rem; font-weight: 700; margin: 4px 0; }
.kpi-sub { font-size: 0.8rem; color: var(--muted); }

.tab-nav {
  display: flex;
  gap: 4px;
  padding: 12px 24px 0;
  background: var(--card);
}
.tab-btn {
  padding: 10px 20px;
  border: none;
  background: transparent;
  color: var(--muted);
  cursor: pointer;
  font-size: 0.9rem;
  border-bottom: 2px solid transparent;
  transition: all 0.2s;
}
.tab-btn:hover { color: var(--text); }
.tab-btn.active { color: var(--blue); border-bottom-color: var(--blue); font-weight: 600; }

.tab-content { display: none; padding: 20px 24px; }
.tab-content.active { display: block; }

.grid { display: grid; gap: 16px; grid-template-columns: repeat(auto-fit, minmax(500px, 1fr)); }
.card {
  background: var(--card);
  border-radius: 10px;
  padding: 16px;
  border: 1px solid var(--border);
}
.card h2 { font-size: 0.95rem; font-weight: 600; margin-bottom: 12px; }
.plot { height: 350px; }
.plot.tall { height: 420px; }
.plot.scatter { height: 450px; }

table { width: 100%; border-collapse: collapse; font-size: 0.85rem; }
th, td { text-align: left; padding: 10px 12px; border-bottom: 1px solid var(--border); }
th { color: var(--muted); font-weight: 600; font-size: 0.75rem; text-transform: uppercase; }
.num { text-align: right; font-variant-numeric: tabular-nums; }
.hi { color: var(--red); font-weight: 600; }
.lo { color: var(--green); }
.muted { color: var(--muted); font-size: 0.8rem; }

footer {
  padding: 16px 24px;
  text-align: center;
  font-size: 0.8rem;
  color: var(--muted);
  border-top: 1px solid var(--border);
  background: var(--card);
}
</style>
</head>
<body>

<header>
  <h1>Scope Drift Dashboard</h1>
  <p>Generated <span id="snapStamp"></span> · <span id="scopeDesc"></span></p>
</header>

<div class="kpi-row" id="kpiRow"></div>

<nav class="tab-nav">
  <button class="tab-btn active" data-tab="overview">Overview</button>
  <button class="tab-btn" data-tab="scatter">Network Maps</button>
</nav>

<div id="tab-overview" class="tab-content active">
  <div class="grid">
    <div class="card" style="grid-column: 1 / -1;">
      <h2>Out-of-scope % by Journal</h2>
      <div id="barOOS" class="plot"></div>
    </div>
    <div class="card" style="grid-column: 1 / -1;">
      <h2>Out-of-scope % by Year</h2>
      <div id="barOOSYear" class="plot tall"></div>
    </div>
    <div class="card" style="grid-column: 1 / -1;">
      <h2>Top Communities (by size)</h2>
      <div id="barComm" class="plot tall"></div>
    </div>
  </div>
  <div class="card" style="margin-top: 16px;">
    <h2>Journal Summary</h2>
    <table id="tblJournal">
      <thead><tr>
        <th>Journal</th><th class="num">Articles</th><th class="num">Primary Clusters</th>
        <th class="num">Out of Scope</th><th class="num">OOS %</th><th>Top Community</th>
      </tr></thead>
      <tbody></tbody>
    </table>
  </div>
  <div class="card" style="margin-top: 16px;">
    <h2>Community Composition</h2>
    <table id="tblComm">
      <thead><tr>
        <th>Theme</th><th class="num">Size</th><th class="num">Frontiers %</th>
        <th>Dominant Journal</th><th>Top Journals</th>
      </tr></thead>
      <tbody></tbody>
    </table>
  </div>
</div>

<div id="tab-scatter" class="tab-content">
  <p style="margin-bottom: 16px; color: var(--muted);">
    Each bubble = community. <span style="color: var(--green);">Green = in-scope (primary clusters)</span>, 
    <span style="color: var(--red);">Red = out-of-scope</span>. Size = paper count. Position = citation network layout.
  </p>
  <div id="scatterGrid" class="grid"></div>
</div>

<footer>
  <span id="ftYears"></span> · <span id="ftCov"></span>% primary coverage · 
  <span id="ftJournals"></span> journals · <span id="ftPapers"></span> papers · 
  <span id="ftComms"></span> communities
</footer>

<script>
const DATA = __DATA_JSON__;
__RENDER_SCRIPT__
</script>
</body>
</html>
"""


def build_html(data: dict):
    """Write the HTML dashboard."""
    log.info("[6/6] Writing HTML dashboard …")

    # Read render_script.js
    render_script_path = Path(__file__).resolve().parent.parent / "render_script.js"
    if render_script_path.exists():
        render_script = render_script_path.read_text(encoding="utf-8")
    else:
        log.warning("       render_script.js not found, using embedded version")
        render_script = "(function(){console.log('render_script.js not found')})();"

    # Build HTML
    data_json = json.dumps(data, separators=(",", ":"))
    html = HTML_TEMPLATE.replace("__DATA_JSON__", data_json)
    html = html.replace("__RENDER_SCRIPT__", render_script)

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(html, encoding="utf-8")

    log.info(f"       Written to {OUTPUT_PATH}")
    log.info(f"       File size: {OUTPUT_PATH.stat().st_size / 1024:.1f} KB")


# ──────────────────────────────────────────────────────────────────────────────
# MAIN
# ──────────────────────────────────────────────────────────────────────────────
def main():
    log.info("=" * 60)
    log.info("Building Scope Dashboard")
    log.info("=" * 60)

    client = bigquery.Client(project=BQ_PROJECT)

    # Load data
    df = load_papers(client)

    # Skip citation loading for large datasets (use community-based layout)
    if len(df) > 50000:
        log.info(
            "[2/6] Skipping citation loading (using community-based layout for speed)"
        )
        df_edges = pd.DataFrame()
    else:
        df_edges = load_citations_for_layout(client)

    # Compute positions
    positions = compute_scatter_positions(df, df_edges)

    # Compute stats
    journals = compute_journal_stats(df, positions)
    communities = compute_community_stats(df)

    # Build data structure
    years = sorted(df["pub_year"].unique())
    data = {
        "meta": {
            "year_range": [int(years[0]), int(years[-1])] if years else [],
            "primary_cluster_coverage": PRIMARY_COVERAGE,
            "primary_cluster_level": CLUSTER_LEVEL,
            "oos_per_year_years": [int(y) for y in years],
        },
        "journals": journals,
        "communities": communities,
    }

    # Write HTML
    build_html(data)

    log.info("=" * 60)
    log.info("Done!")
    log.info("=" * 60)


if __name__ == "__main__":
    main()
