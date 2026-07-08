"""
build_cluster_network_dashboard.py
===================================
Creates an HTML dashboard with 5 bubble charts (one per Frontiers journal)
showing clusters as circles positioned by citation relationships.
Circle size reflects how many papers each journal has in each cluster.

Data source : scope_drift_raw BigQuery tables
Output      : output/journal_cluster_bubbles.html

Usage:
    python scripts/build_cluster_network_dashboard.py
"""

import json
import logging
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

# Table timestamps
TBL_CLASSIF = f"{BQ_PROJECT}.{BQ_DATASET}.classification_raw_20260617_120737"
TBL_PUB_META = f"{BQ_PROJECT}.{BQ_DATASET}.pub_metadata_raw_20260617_135005"
TBL_CIT_LINKS = f"{BQ_PROJECT}.{BQ_DATASET}.cit_links_raw_20260617_135005"

# Target journals
JOURNALS = [
    "Frontiers in Immunology",
    "Frontiers in Public Health",
    "Frontiers in Medicine",
    "Frontiers in Oncology",
    "Frontiers in Psychology",
]

# Journal display colors (light mode friendly)
JOURNAL_COLORS = {
    "Frontiers in Immunology": "#2563eb",      # blue
    "Frontiers in Public Health": "#059669",   # green
    "Frontiers in Medicine": "#d97706",        # amber
    "Frontiers in Oncology": "#dc2626",        # red
    "Frontiers in Psychology": "#7c3aed",      # purple
}

# Cluster level to use
CLUSTER_LEVEL = "micro"

OUTPUT_PATH = Path(__file__).resolve().parent.parent / "output" / "journal_cluster_bubbles.html"

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s  %(message)s", datefmt="%H:%M:%S"
)
log = logging.getLogger(__name__)


# ──────────────────────────────────────────────────────────────────────────────
# STEP 1 — Load data from BigQuery
# ──────────────────────────────────────────────────────────────────────────────
def load_papers(client) -> pd.DataFrame:
    """Load papers with cluster assignments for target journals."""
    log.info("[1/5] Loading papers from BigQuery …")
    
    journals_str = ", ".join(f"'{j}'" for j in JOURNALS)
    
    query = f"""
    SELECT 
        c.int_id,
        c.{CLUSTER_LEVEL} AS cluster_id,
        m.journal,
        m.title
    FROM `{TBL_CLASSIF}` c
    JOIN `{TBL_PUB_META}` m ON c.int_id = m.int_id
    WHERE m.journal IN ({journals_str})
    """
    
    df = client.query(query).to_dataframe()
    log.info(f"       Loaded {len(df):,} papers from {df['journal'].nunique()} journals")
    log.info(f"       Unique clusters: {df['cluster_id'].nunique()}")
    
    return df


def load_citations_aggregated(client, journals_str: str) -> pd.DataFrame:
    """Load citation links aggregated by cluster pair (much more efficient)."""
    log.info("[2/5] Loading aggregated citation links from BigQuery …")
    
    # Aggregate citations at cluster level directly in BigQuery
    query = f"""
    WITH journal_papers AS (
        SELECT c.int_id, c.{CLUSTER_LEVEL} AS cluster_id
        FROM `{TBL_CLASSIF}` c
        JOIN `{TBL_PUB_META}` m ON c.int_id = m.int_id
        WHERE m.journal IN ({journals_str})
    )
    SELECT 
        jp1.cluster_id AS src_cluster,
        jp2.cluster_id AS tgt_cluster,
        SUM(cl.weight) AS total_weight,
        COUNT(*) AS edge_count
    FROM `{TBL_CIT_LINKS}` cl
    JOIN journal_papers jp1 ON cl.int_id1 = jp1.int_id
    JOIN journal_papers jp2 ON cl.int_id2 = jp2.int_id
    WHERE jp1.cluster_id != jp2.cluster_id
    GROUP BY jp1.cluster_id, jp2.cluster_id
    """
    
    try:
        job = client.query(query)
        df_edges = job.result(timeout=180).to_dataframe()  # 3 minute timeout
        log.info(f"       Loaded {len(df_edges):,} cluster-cluster citation pairs")
    except Exception as e:
        log.warning(f"       Citation query failed: {e}")
        log.info("       Using simple circular layout instead")
        df_edges = pd.DataFrame(columns=["src_cluster", "tgt_cluster", "total_weight"])
    
    return df_edges


# ──────────────────────────────────────────────────────────────────────────────
# STEP 2 — Aggregate by cluster
# ──────────────────────────────────────────────────────────────────────────────
def aggregate_papers_by_cluster(df_papers: pd.DataFrame) -> pd.DataFrame:
    """Count papers per journal x cluster."""
    log.info("[3/5] Aggregating papers by journal × cluster …")
    
    df_agg = (
        df_papers
        .groupby(["journal", "cluster_id"])
        .size()
        .reset_index(name="paper_count")
    )
    
    log.info(f"       {len(df_agg):,} journal-cluster combinations")
    
    return df_agg


# ──────────────────────────────────────────────────────────────────────────────
# STEP 3 — Build graph and compute layout
# ──────────────────────────────────────────────────────────────────────────────
def compute_cluster_layout(
    df_papers: pd.DataFrame,
    df_cluster_edges: pd.DataFrame
) -> dict:
    """Compute cluster positions using citation graph or circular layout."""
    log.info("[4/5] Computing cluster layout …")
    
    # Get all unique clusters
    all_clusters = sorted(df_papers["cluster_id"].unique())
    n_clusters = len(all_clusters)
    
    log.info(f"       {n_clusters} unique clusters")
    
    # If we have enough citation edges, use force-directed layout
    if len(df_cluster_edges) >= n_clusters:
        cluster_to_idx = {c: i for i, c in enumerate(all_clusters)}
        idx_to_cluster = {i: c for c, i in cluster_to_idx.items()}
        
        # Build edge list
        edges = []
        weights = []
        
        for _, row in df_cluster_edges.iterrows():
            src = cluster_to_idx.get(row["src_cluster"])
            tgt = cluster_to_idx.get(row["tgt_cluster"])
            if src is not None and tgt is not None:
                edges.append((src, tgt))
                weights.append(row["total_weight"])
        
        log.info(f"       {len(edges):,} edges in cluster graph")
        
        if edges:
            # Create graph and compute layout
            g = ig.Graph(n=n_clusters, edges=edges, directed=False)
            g.es["weight"] = weights
            
            log.info("       Computing Fruchterman-Reingold layout …")
            layout = g.layout_fruchterman_reingold(weights="weight", niter=500)
            
            # Normalize layout to [0, 1]
            coords = np.array(layout.coords)
            coords_min = coords.min(axis=0)
            coords_max = coords.max(axis=0)
            coords_range = coords_max - coords_min
            coords_range[coords_range == 0] = 1
            coords_norm = (coords - coords_min) / coords_range
            
            positions = {
                idx_to_cluster[i]: (float(coords_norm[i, 0]), float(coords_norm[i, 1]))
                for i in range(n_clusters)
            }
            
            log.info("       Force-directed layout complete")
            return positions
    
    # Fallback: circular layout
    log.info("       Using circular layout (insufficient citation data)")
    positions = {}
    for i, cluster_id in enumerate(all_clusters):
        angle = 2 * np.pi * i / n_clusters
        x = 0.5 + 0.4 * np.cos(angle)
        y = 0.5 + 0.4 * np.sin(angle)
        positions[cluster_id] = (float(x), float(y))
    
    return positions


# ──────────────────────────────────────────────────────────────────────────────
# STEP 4 — Build HTML dashboard
# ──────────────────────────────────────────────────────────────────────────────
def build_dashboard_data(
    df_agg: pd.DataFrame,
    positions: dict
) -> dict:
    """Prepare data structure for the HTML template."""
    
    data = {
        "journals": [],
        "cluster_positions": {str(k): v for k, v in positions.items()},
    }
    
    for journal in JOURNALS:
        journal_data = df_agg[df_agg["journal"] == journal].copy()
        
        clusters = []
        for _, row in journal_data.iterrows():
            cluster_id = row["cluster_id"]
            if cluster_id in positions:
                clusters.append({
                    "id": int(cluster_id),
                    "count": int(row["paper_count"]),
                    "x": positions[cluster_id][0],
                    "y": positions[cluster_id][1],
                })
        
        # Sort by count descending
        clusters.sort(key=lambda x: x["count"], reverse=True)
        
        data["journals"].append({
            "name": journal,
            "color": JOURNAL_COLORS.get(journal, "#6b7280"),
            "total_papers": int(journal_data["paper_count"].sum()),
            "cluster_count": len(clusters),
            "clusters": clusters,
        })
    
    return data


HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Journal Scope — Cluster Bubble Charts</title>
<script src="https://cdn.plot.ly/plotly-2.35.2.min.js"></script>
<style>
:root {
  --bg: #f8fafc;
  --card: #ffffff;
  --text: #0f172a;
  --muted: #64748b;
  --border: #e2e8f0;
}
* { box-sizing: border-box; margin: 0; padding: 0; }
body {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  background: var(--bg);
  color: var(--text);
  padding: 20px 24px;
  max-width: 1600px;
  margin: 0 auto;
}
header {
  text-align: center;
  margin-bottom: 24px;
  padding-bottom: 16px;
  border-bottom: 1px solid var(--border);
}
header h1 { font-size: 1.5rem; font-weight: 700; margin-bottom: 6px; }
header p { color: var(--muted); font-size: 0.9rem; }
.grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 20px;
}
@media (max-width: 1000px) { .grid { grid-template-columns: 1fr; } }
.card {
  background: var(--card);
  border-radius: 12px;
  padding: 16px;
  box-shadow: 0 1px 3px rgba(0,0,0,0.08);
  border: 1px solid var(--border);
}
.card:last-child:nth-child(odd) {
  grid-column: 1 / -1;
  max-width: 50%;
  justify-self: center;
}
@media (max-width: 1000px) { .card:last-child:nth-child(odd) { max-width: 100%; } }
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}
.card-header h2 { font-size: 1rem; font-weight: 600; }
.card-header .stats { font-size: 0.8rem; color: var(--muted); }
.plot { height: 400px; }
.legend {
  text-align: center;
  margin-top: 20px;
  padding: 12px;
  background: var(--card);
  border-radius: 8px;
  border: 1px solid var(--border);
  font-size: 0.85rem;
  color: var(--muted);
}
</style>
</head>
<body>

<header>
  <h1>Journal Scope — Cluster Distribution</h1>
  <p>Each bubble represents a micro cluster. Size = number of papers from that journal in the cluster.<br>
  Clusters positioned by citation relationships (nearby clusters cite each other).</p>
</header>

<div class="grid" id="chartGrid"></div>

<div class="legend">
  <strong>Reading the charts:</strong> Larger bubbles = more papers in that cluster. 
  Same cluster appears in the same position across all charts — overlapping bubbles indicate shared scope.
</div>

<script>
const DATA = __DATA_JSON__;

const grid = document.getElementById("chartGrid");

DATA.journals.forEach((j, idx) => {
  const card = document.createElement("div");
  card.className = "card";
  card.innerHTML = `
    <div class="card-header">
      <h2 style="color: ${j.color}">${j.name}</h2>
      <span class="stats">${j.total_papers.toLocaleString()} papers · ${j.cluster_count} clusters</span>
    </div>
    <div id="plot${idx}" class="plot"></div>
  `;
  grid.appendChild(card);
  
  // Prepare trace data
  const x = j.clusters.map(c => c.x);
  const y = j.clusters.map(c => c.y);
  const sizes = j.clusters.map(c => Math.max(6, Math.sqrt(c.count) * 3));
  const text = j.clusters.map(c => 
    `Cluster ${c.id}<br>Papers: ${c.count}<br>${(c.count / j.total_papers * 100).toFixed(1)}% of journal`
  );
  
  Plotly.newPlot("plot" + idx, [{
    type: "scatter",
    mode: "markers",
    x: x,
    y: y,
    marker: {
      size: sizes,
      color: j.color,
      opacity: 0.7,
      line: { color: j.color, width: 1 }
    },
    text: text,
    hovertemplate: "%{text}<extra></extra>"
  }], {
    paper_bgcolor: "white",
    plot_bgcolor: "#fafafa",
    xaxis: { 
      showgrid: false, 
      zeroline: false, 
      showticklabels: false,
      range: [-0.05, 1.05]
    },
    yaxis: { 
      showgrid: false, 
      zeroline: false, 
      showticklabels: false,
      range: [-0.05, 1.05]
    },
    margin: { t: 10, l: 10, r: 10, b: 10 },
    hovermode: "closest"
  }, { responsive: true });
});
</script>
</body>
</html>
"""


def build_html(data: dict):
    """Write the HTML dashboard file."""
    log.info("[5/5] Writing HTML dashboard …")
    
    # Embed data as JSON
    data_json = json.dumps(data, separators=(",", ":"))
    html = HTML_TEMPLATE.replace("__DATA_JSON__", data_json)
    
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(html, encoding="utf-8")
    
    log.info(f"       Written to {OUTPUT_PATH}")
    log.info(f"       File size: {OUTPUT_PATH.stat().st_size / 1024:.1f} KB")


# ──────────────────────────────────────────────────────────────────────────────
# MAIN
# ──────────────────────────────────────────────────────────────────────────────
def main():
    log.info("=" * 60)
    log.info("Building Journal Cluster Bubble Dashboard")
    log.info("=" * 60)
    
    client = bigquery.Client(project=BQ_PROJECT)
    
    # Load data
    journals_str = ", ".join(f"'{j}'" for j in JOURNALS)
    df_papers = load_papers(client)
    df_cluster_edges = load_citations_aggregated(client, journals_str)
    
    # Aggregate papers by cluster
    df_agg = aggregate_papers_by_cluster(df_papers)
    
    # Compute layout
    positions = compute_cluster_layout(df_papers, df_cluster_edges)
    
    # Build dashboard
    data = build_dashboard_data(df_agg, positions)
    build_html(data)
    
    log.info("=" * 60)
    log.info("Done!")
    log.info("=" * 60)


if __name__ == "__main__":
    main()
