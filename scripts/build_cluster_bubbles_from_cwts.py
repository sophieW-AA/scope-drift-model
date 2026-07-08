"""
build_cluster_bubbles_from_cwts.py
==================================
Creates an HTML dashboard with 5 bubble charts (one per Frontiers journal)
showing clusters as circles positioned by citation relationships.
Circle size reflects how many papers each journal has in each cluster.

Data source : local cwts_output/ files
Output      : output/cluster_bubbles.html

Usage:
    python scripts/build_cluster_bubbles_from_cwts.py
    
Environment variables:
    CLUSTER_LEVEL : micro, meso, or macro (default: macro)
"""

import json
import logging
import os
from pathlib import Path

import numpy as np
import pandas as pd
import igraph as ig

# ──────────────────────────────────────────────────────────────────────────────
# CONFIG
# ──────────────────────────────────────────────────────────────────────────────
CWTS_DIR = Path(__file__).resolve().parent.parent / "cwts_output"

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

# Cluster level to use (can override via env var)
CLUSTER_LEVEL = os.environ.get("CLUSTER_LEVEL", "macro")

# GPT labels directory
GPT_LABELS_PATH = Path(__file__).resolve().parent.parent / "cwts_output"

OUTPUT_PATH = Path(__file__).resolve().parent.parent / "output" / "cluster_bubbles.html"

# Global GPT labels
GPT_LABELS = {}

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s  %(message)s", datefmt="%H:%M:%S"
)
log = logging.getLogger(__name__)


def load_gpt_labels() -> dict:
    """Load GPT-generated labels mapping cluster_id -> short_label."""
    labels_file = GPT_LABELS_PATH / f"{CLUSTER_LEVEL}_labels.csv"
    if not labels_file.exists():
        log.warning("GPT labels not found at %s, using cluster IDs", labels_file)
        return {}
    
    df = pd.read_csv(labels_file)
    
    labels = {}
    for _, row in df.iterrows():
        cluster_id = int(row["cluster_id"])
        labels[cluster_id] = row["short_label"]
    
    log.info("       Loaded %d GPT labels", len(labels))
    return labels


# ──────────────────────────────────────────────────────────────────────────────
# STEP 1 — Load data from local files
# ──────────────────────────────────────────────────────────────────────────────
def load_papers() -> pd.DataFrame:
    """Load papers with cluster assignments for target journals."""
    log.info("[1/5] Loading papers from local files …")
    
    # Load classification
    classif_path = CWTS_DIR / "classification.txt"
    df_classif = pd.read_csv(
        classif_path, sep="\t", header=None,
        names=["int_id", "micro", "meso", "macro"]
    )
    
    # Load metadata
    meta_path = CWTS_DIR / "pub_metadata.txt"
    df_meta = pd.read_csv(
        meta_path, sep="\t", header=None,
        names=["int_id", "pub_id", "is_frontiers", "journal", "date", "title"]
    )
    
    # Merge and filter
    df = df_classif.merge(df_meta[["int_id", "journal", "title"]], on="int_id")
    df = df[df["journal"].isin(JOURNALS)].copy()
    df = df.rename(columns={CLUSTER_LEVEL: "cluster_id"})
    
    log.info(f"       Loaded {len(df):,} papers from {df['journal'].nunique()} journals")
    log.info(f"       Unique clusters: {df['cluster_id'].nunique()}")
    
    return df


def load_citations(df_papers: pd.DataFrame) -> pd.DataFrame:
    """Load citation links and aggregate by cluster pair."""
    log.info("[2/5] Loading citation links …")
    
    # Load citation links
    cit_path = CWTS_DIR / "cit_links.txt"
    df_cit = pd.read_csv(
        cit_path, sep="\t", header=None,
        names=["int_id1", "int_id2", "weight"]
    )
    
    log.info(f"       Raw edges: {len(df_cit):,}")
    
    # Map paper IDs to cluster IDs
    paper_to_cluster = df_papers.set_index("int_id")["cluster_id"].to_dict()
    
    # Filter to papers in our set
    valid_ids = set(paper_to_cluster.keys())
    df_cit = df_cit[
        df_cit["int_id1"].isin(valid_ids) & 
        df_cit["int_id2"].isin(valid_ids)
    ].copy()
    
    # Map to clusters
    df_cit["src_cluster"] = df_cit["int_id1"].map(paper_to_cluster)
    df_cit["tgt_cluster"] = df_cit["int_id2"].map(paper_to_cluster)
    
    # Remove self-loops and aggregate
    df_cit = df_cit[df_cit["src_cluster"] != df_cit["tgt_cluster"]]
    
    df_edges = (
        df_cit
        .groupby(["src_cluster", "tgt_cluster"])
        .agg(total_weight=("weight", "sum"), edge_count=("weight", "count"))
        .reset_index()
    )
    
    log.info(f"       Cluster-cluster pairs: {len(df_edges):,}")
    
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
    df_edges: pd.DataFrame
) -> dict:
    """Compute 2D positions for clusters using force-directed layout."""
    log.info("[4/5] Computing cluster layout …")
    
    clusters = df_papers["cluster_id"].unique()
    n_clusters = len(clusters)
    cluster_to_idx = {c: i for i, c in enumerate(clusters)}
    
    # Build graph
    g = ig.Graph(n=n_clusters)
    
    edges = []
    weights = []
    for _, row in df_edges.iterrows():
        src = cluster_to_idx.get(row["src_cluster"])
        tgt = cluster_to_idx.get(row["tgt_cluster"])
        if src is not None and tgt is not None and src != tgt:
            edges.append((src, tgt))
            weights.append(float(row["total_weight"]))
    
    if len(edges) > 100:
        g.add_edges(edges)
        g.es["weight"] = weights
        
        log.info(f"       Graph: {g.vcount()} nodes, {g.ecount()} edges")
        
        # Force-directed layout
        try:
            layout = g.layout_fruchterman_reingold(weights="weight", niter=500)
            coords = np.array(layout.coords)
        except Exception as e:
            log.warning(f"       Layout failed: {e}, using circular")
            coords = _circular_layout(n_clusters)
    else:
        log.info(f"       Not enough edges ({len(edges)}), using circular layout")
        coords = _circular_layout(n_clusters)
    
    # Normalize to [0, 1]
    if len(coords) > 0:
        coords = (coords - coords.min(axis=0)) / (coords.max(axis=0) - coords.min(axis=0) + 1e-6)
        # Add padding
        coords = coords * 0.8 + 0.1
    
    positions = {c: (float(coords[i, 0]), float(coords[i, 1])) for c, i in cluster_to_idx.items()}
    
    log.info(f"       Positioned {len(positions)} clusters")
    
    return positions


def _circular_layout(n: int) -> np.ndarray:
    """Simple circular layout fallback."""
    angles = np.linspace(0, 2 * np.pi, n, endpoint=False)
    return np.column_stack([np.cos(angles), np.sin(angles)])


# ──────────────────────────────────────────────────────────────────────────────
# STEP 4 — Build dashboard data
# ──────────────────────────────────────────────────────────────────────────────
def build_dashboard_data(
    df_agg: pd.DataFrame,
    positions: dict
) -> dict:
    """Build JSON data structure for dashboard."""
    
    data = {"journals": {}, "positions": {}}
    
    # Store positions
    for cluster_id, (x, y) in positions.items():
        data["positions"][int(cluster_id)] = {"x": round(x, 4), "y": round(y, 4)}
    
    # Per-journal bubble data
    for journal in JOURNALS:
        jdf = df_agg[df_agg["journal"] == journal]
        
        bubbles = []
        for _, row in jdf.iterrows():
            cid = int(row["cluster_id"])
            pos = positions.get(cid, (0.5, 0.5))
            label = GPT_LABELS.get(cid, f"Cluster {cid}")
            bubbles.append({
                "cluster_id": cid,
                "label": label,
                "count": int(row["paper_count"]),
                "x": round(pos[0], 4),
                "y": round(pos[1], 4),
            })
        
        data["journals"][journal] = {
            "color": JOURNAL_COLORS.get(journal, "#666666"),
            "total_papers": int(jdf["paper_count"].sum()),
            "bubbles": bubbles,
        }
    
    return data


# ──────────────────────────────────────────────────────────────────────────────
# STEP 5 — Build HTML
# ──────────────────────────────────────────────────────────────────────────────
def build_html(data: dict) -> None:
    """Generate HTML dashboard with embedded Plotly."""
    log.info("[5/5] Building HTML dashboard …")
    
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Cluster Bubble Dashboard</title>
    <script src="https://cdn.plot.ly/plotly-2.27.0.min.js"></script>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: #f8fafc;
            color: #1e293b;
            padding: 20px;
        }}
        h1 {{
            text-align: center;
            margin-bottom: 10px;
            font-size: 1.8rem;
        }}
        .subtitle {{
            text-align: center;
            color: #64748b;
            margin-bottom: 30px;
        }}
        .grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(450px, 1fr));
            gap: 20px;
            max-width: 1600px;
            margin: 0 auto;
        }}
        .card {{
            background: white;
            border-radius: 12px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
            padding: 20px;
        }}
        .card h2 {{
            font-size: 1.1rem;
            margin-bottom: 5px;
        }}
        .card .stats {{
            font-size: 0.85rem;
            color: #64748b;
            margin-bottom: 10px;
        }}
        .plot {{
            width: 100%;
            height: 350px;
        }}
    </style>
</head>
<body>
    <h1>Cluster Bubble Dashboard</h1>
    <p class="subtitle">Cluster level: {CLUSTER_LEVEL} | Circle size = paper count</p>
    <div class="grid" id="grid"></div>

    <script>
    const DATA = {json.dumps(data)};
    
    const grid = document.getElementById('grid');
    
    Object.entries(DATA.journals).forEach(([journal, jdata]) => {{
        const card = document.createElement('div');
        card.className = 'card';
        
        const nClusters = jdata.bubbles.length;
        card.innerHTML = `
            <h2 style="color: ${{jdata.color}}">${{journal}}</h2>
            <div class="stats">${{jdata.total_papers.toLocaleString()}} papers · ${{nClusters}} clusters</div>
            <div class="plot" id="plot-${{journal.replace(/\\s+/g, '-')}}"></div>
        `;
        grid.appendChild(card);
        
        const plotId = 'plot-' + journal.replace(/\\s+/g, '-');
        
        const bubbles = jdata.bubbles;
        const maxCount = Math.max(...bubbles.map(b => b.count));
        
        const trace = {{
            x: bubbles.map(b => b.x),
            y: bubbles.map(b => b.y),
            mode: 'markers',
            marker: {{
                size: bubbles.map(b => Math.sqrt(b.count / maxCount) * 50 + 5),
                color: jdata.color,
                opacity: 0.6,
                line: {{ color: jdata.color, width: 1 }}
            }},
            text: bubbles.map(b => `${{b.label}}<br>${{b.count}} papers`),
            hoverinfo: 'text'
        }};
        
        const layout = {{
            showlegend: false,
            xaxis: {{ visible: false, range: [0, 1] }},
            yaxis: {{ visible: false, range: [0, 1], scaleanchor: 'x' }},
            margin: {{ l: 10, r: 10, t: 10, b: 10 }},
            paper_bgcolor: 'rgba(0,0,0,0)',
            plot_bgcolor: 'rgba(0,0,0,0)',
            hovermode: 'closest'
        }};
        
        Plotly.newPlot(plotId, [trace], layout, {{ responsive: true }});
    }});
    </script>
</body>
</html>
"""
    
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(html, encoding="utf-8")
    
    log.info(f"       Written to {OUTPUT_PATH}")
    log.info(f"       File size: {OUTPUT_PATH.stat().st_size / 1024:.1f} KB")


# ──────────────────────────────────────────────────────────────────────────────
# MAIN
# ──────────────────────────────────────────────────────────────────────────────
def main():
    global GPT_LABELS
    
    log.info("=" * 60)
    log.info("Building Cluster Bubble Dashboard from CWTS Output")
    log.info(f"Cluster level: {CLUSTER_LEVEL}")
    log.info("=" * 60)
    
    # Load GPT labels
    GPT_LABELS = load_gpt_labels()
    
    # Load data
    df_papers = load_papers()
    df_edges = load_citations(df_papers)
    
    # Aggregate
    df_agg = aggregate_papers_by_cluster(df_papers)
    
    # Compute layout
    positions = compute_cluster_layout(df_papers, df_edges)
    
    # Build dashboard
    data = build_dashboard_data(df_agg, positions)
    build_html(data)
    
    log.info("=" * 60)
    log.info("Done!")
    log.info("=" * 60)


if __name__ == "__main__":
    main()
