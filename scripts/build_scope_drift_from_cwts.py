"""
build_scope_drift_from_cwts.py
==============================
Visualises how the research focus of each cluster shifts over time using
Jensen-Shannon divergence on sub-cluster composition.

Data source : local cwts_output/ files
Output      : output/scope_drift.html

Usage:
    python scripts/build_scope_drift_from_cwts.py
    
Environment variables:
    SCOPE_LEVEL : macro or meso (default: macro)
                  - macro: shows drift within macro clusters (measured by meso composition)
                  - meso: shows drift within meso clusters (measured by micro composition)
"""

import json
import logging
import os
from pathlib import Path

import numpy as np
import pandas as pd
import plotly.graph_objects as go
from scipy.spatial.distance import jensenshannon

# ──────────────────────────────────────────────────────────────────────────────
# CONFIG
# ──────────────────────────────────────────────────────────────────────────────
CWTS_DIR = Path(__file__).resolve().parent.parent / "cwts_output"
OUTPUT_PATH = Path(__file__).resolve().parent.parent / "output" / "scope_drift.html"

# Which level to analyze (can override via env var)
SCOPE_LEVEL = os.environ.get("SCOPE_LEVEL", "macro")
CHILD_OF = {"macro": "meso", "meso": "micro"}

# Minimum papers per period to include
MIN_PAPERS = 30

PALETTE = [
    "#4e79a7", "#f28e2b", "#e15759", "#76b7b2", "#59a14f",
    "#edc948", "#b07aa1", "#ff9da7", "#9c755f", "#bab0ac",
    "#17becf", "#bcbd22", "#7f7f7f", "#8c564b", "#e377c2",
]

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s  %(message)s", datefmt="%H:%M:%S"
)
log = logging.getLogger(__name__)


# ──────────────────────────────────────────────────────────────────────────────
# LOAD DATA
# ──────────────────────────────────────────────────────────────────────────────
def load_data() -> pd.DataFrame:
    """Load classification + metadata from local files."""
    log.info("[1/4] Loading data from local files …")
    
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
    
    # Merge
    df = df_classif.merge(df_meta[["int_id", "date"]], on="int_id")
    
    # Parse date to year
    df["pub_year"] = pd.to_datetime(df["date"], errors="coerce").dt.year
    df = df.dropna(subset=["pub_year"])
    df["pub_year"] = df["pub_year"].astype(int)
    
    log.info(f"       Loaded {len(df):,} papers")
    log.info(f"       Years: {df['pub_year'].min()}–{df['pub_year'].max()}")
    
    return df


# ──────────────────────────────────────────────────────────────────────────────
# COMPUTE DRIFT
# ──────────────────────────────────────────────────────────────────────────────
def compute_drift(df: pd.DataFrame, parent_col: str, child_col: str) -> pd.DataFrame:
    """
    Compute Jensen-Shannon divergence for each parent cluster over time.
    
    For each parent cluster, we look at its distribution over child clusters
    in each year, and compute how much that distribution changes from year to year.
    """
    log.info(f"[2/4] Computing drift ({parent_col} → {child_col}) …")
    
    years = sorted(df["pub_year"].unique())
    parent_ids = sorted(df[parent_col].unique())
    
    results = []
    
    for pid in parent_ids:
        pdf = df[df[parent_col] == pid]
        
        # Build distribution per year
        year_dists = {}
        for year in years:
            ydf = pdf[pdf["pub_year"] == year]
            if len(ydf) >= MIN_PAPERS:
                counts = ydf[child_col].value_counts()
                dist = counts / counts.sum()
                year_dists[year] = dist
        
        if len(year_dists) < 2:
            continue
        
        # Compute year-over-year drift
        sorted_years = sorted(year_dists.keys())
        for i in range(1, len(sorted_years)):
            y1, y2 = sorted_years[i-1], sorted_years[i]
            d1, d2 = year_dists[y1], year_dists[y2]
            
            # Align distributions (fill missing with 0)
            all_children = set(d1.index) | set(d2.index)
            v1 = np.array([d1.get(c, 0) for c in all_children])
            v2 = np.array([d2.get(c, 0) for c in all_children])
            
            # Jensen-Shannon divergence
            jsd = jensenshannon(v1, v2)
            
            results.append({
                "cluster_id": pid,
                "year": y2,
                "jsd": jsd,
                "n_papers": len(pdf[pdf["pub_year"] == y2]),
            })
    
    df_drift = pd.DataFrame(results)
    log.info(f"       Computed {len(df_drift):,} drift measurements")
    
    return df_drift


# ──────────────────────────────────────────────────────────────────────────────
# BUILD VISUALIZATION
# ──────────────────────────────────────────────────────────────────────────────
def build_visualization(df: pd.DataFrame, df_drift: pd.DataFrame) -> str:
    """Build Plotly HTML visualization."""
    log.info("[3/4] Building visualization …")
    
    if len(df_drift) == 0:
        log.warning("       No drift data to visualize!")
        return "<html><body><h1>No drift data available</h1></body></html>"
    
    # Get top clusters by total papers
    cluster_sizes = df.groupby(SCOPE_LEVEL).size().sort_values(ascending=False)
    top_clusters = cluster_sizes.head(15).index.tolist()
    
    df_drift = df_drift[df_drift["cluster_id"].isin(top_clusters)]
    
    # Create figure
    fig = go.Figure()
    
    for i, cid in enumerate(top_clusters):
        cdf = df_drift[df_drift["cluster_id"] == cid].sort_values("year")
        if len(cdf) == 0:
            continue
        
        color = PALETTE[i % len(PALETTE)]
        
        fig.add_trace(go.Scatter(
            x=cdf["year"],
            y=cdf["jsd"],
            mode="lines+markers",
            name=f"Cluster {cid}",
            line=dict(color=color, width=2),
            marker=dict(size=8),
            hovertemplate=(
                f"<b>Cluster {cid}</b><br>"
                "Year: %{x}<br>"
                "JSD: %{y:.3f}<br>"
                "<extra></extra>"
            )
        ))
    
    # Layout
    child_level = CHILD_OF[SCOPE_LEVEL]
    fig.update_layout(
        title=dict(
            text=f"Scope Drift: {SCOPE_LEVEL.title()} Clusters → {child_level.title()} Composition",
            font=dict(size=20)
        ),
        xaxis=dict(
            title="Year",
            tickmode="linear",
            dtick=1,
            gridcolor="#e2e8f0"
        ),
        yaxis=dict(
            title="Jensen-Shannon Divergence (year-over-year)",
            range=[0, max(0.5, df_drift["jsd"].max() * 1.1)],
            gridcolor="#e2e8f0"
        ),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="center",
            x=0.5
        ),
        template="plotly_white",
        hovermode="x unified",
        height=600,
        margin=dict(l=60, r=40, t=100, b=60)
    )
    
    return fig.to_html(include_plotlyjs="cdn", full_html=True)


# ──────────────────────────────────────────────────────────────────────────────
# MAIN
# ──────────────────────────────────────────────────────────────────────────────
def main():
    log.info("=" * 60)
    log.info("Building Scope Drift Visualization from CWTS Output")
    log.info(f"Scope level: {SCOPE_LEVEL}")
    log.info("=" * 60)
    
    # Load data
    df = load_data()
    
    # Compute drift
    child_col = CHILD_OF.get(SCOPE_LEVEL)
    if child_col is None:
        log.error(f"Invalid SCOPE_LEVEL: {SCOPE_LEVEL}. Use 'macro' or 'meso'.")
        return
    
    df_drift = compute_drift(df, SCOPE_LEVEL, child_col)
    
    # Build visualization
    html = build_visualization(df, df_drift)
    
    # Write output
    log.info("[4/4] Writing HTML …")
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(html, encoding="utf-8")
    
    log.info(f"       Written to {OUTPUT_PATH}")
    log.info(f"       File size: {OUTPUT_PATH.stat().st_size / 1024:.1f} KB")
    
    log.info("=" * 60)
    log.info("Done!")
    log.info("=" * 60)


if __name__ == "__main__":
    main()
