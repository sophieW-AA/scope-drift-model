"""
Scope Drift Detection Prototype
================================
Replicates the InCites/CWTS approach: build a citation network from
Frontiers in Environmental Science (2025) articles, run Leiden community
detection, and compute scope-drift metrics against a historical baseline.

Data source : OpenAlex API (free, no key required)
Algorithm   : Leiden community detection (Traag et al., 2019)
Target      : Frontiers in Environmental Science — ISSN 2296-665X
              OpenAlex source ID: S2596204836

Usage:
    python scope_drift_prototype.py

Outputs (saved to ./output/):
    - articles.csv           : all fetched articles with metadata
    - citation_network.graphml : the citation graph
    - communities.csv        : article → community assignments
    - drift_report.csv       : per-quarter drift metrics
    - drift_dashboard.html   : interactive Plotly dashboard
    - community_summary.csv  : top keywords per community
"""

import os
import json
import time
import logging
from collections import Counter, defaultdict
from itertools import combinations

import requests
import pandas as pd
import numpy as np
from scipy.spatial.distance import jensenshannon
from scipy.stats import entropy as sp_entropy

import igraph as ig
import leidenalg

import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.express as px

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------
OPENALEX_SOURCE_ID = "S2596204836"  # Frontiers in Environmental Science
BASELINE_YEARS = [2021, 2022, 2023]  # historical baseline period
TARGET_YEAR = 2025                    # year we're checking for drift
COMPARISON_YEAR = 2024                # intermediate comparison
EMAIL = "sophie.wilson@frontiersin.org"  # polite-pool for OpenAlex
OUTPUT_DIR = "./output"
LOG_LEVEL = logging.INFO

# Leiden resolution parameters (multi-scale)
RESOLUTIONS = {
    "macro": 0.0005,
    "meso":  0.005,
    "micro": 0.05,
}

logging.basicConfig(
    level=LOG_LEVEL,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger(__name__)
os.makedirs(OUTPUT_DIR, exist_ok=True)

# ---------------------------------------------------------------------------
# 1. Data Acquisition — fetch articles from OpenAlex
# ---------------------------------------------------------------------------

def fetch_works(source_id: str, years: list[int], email: str) -> list[dict]:
    """Fetch all works for a source across the given years using cursor pagination."""
    all_works = []
    base_url = "https://api.openalex.org/works"
    year_filter = "|".join(str(y) for y in years)

    params = {
        "filter": f"primary_location.source.id:{source_id},publication_year:{year_filter},type:article",
        "select": "id,doi,title,publication_year,publication_date,referenced_works,topics,cited_by_count",
        "per_page": 200,
        "cursor": "*",
        "mailto": email,
    }

    page = 0
    while True:
        page += 1
        resp = requests.get(base_url, params=params, timeout=30)
        resp.raise_for_status()
        data = resp.json()

        results = data.get("results", [])
        if not results:
            break

        all_works.extend(results)
        next_cursor = data["meta"].get("next_cursor")
        if not next_cursor:
            break

        params["cursor"] = next_cursor

        if page % 5 == 0:
            log.info(f"  ... fetched {len(all_works)} works so far (page {page})")
        time.sleep(0.15)  # respect rate limits

    log.info(f"Fetched {len(all_works)} works for years {years}")
    return all_works


def works_to_dataframe(works: list[dict]) -> pd.DataFrame:
    """Convert raw OpenAlex works to a clean DataFrame."""
    rows = []
    for w in works:
        openalex_id = w["id"].replace("https://openalex.org/", "")
        doi = (w.get("doi") or "").replace("https://doi.org/", "")
        primary_topic = None
        primary_topic_field = None
        primary_topic_domain = None
        if w.get("topics"):
            t = w["topics"][0]
            primary_topic = t.get("display_name", "")
            primary_topic_field = t.get("field", {}).get("display_name", "")
            primary_topic_domain = t.get("domain", {}).get("display_name", "")

        rows.append({
            "openalex_id": openalex_id,
            "doi": doi,
            "title": w.get("title", ""),
            "publication_year": w.get("publication_year"),
            "publication_date": w.get("publication_date"),
            "cited_by_count": w.get("cited_by_count", 0),
            "n_references": len(w.get("referenced_works", [])),
            "primary_topic": primary_topic,
            "primary_topic_field": primary_topic_field,
            "primary_topic_domain": primary_topic_domain,
            "referenced_works": json.dumps(
                [r.replace("https://openalex.org/", "") for r in w.get("referenced_works", [])]
            ),
        })
    return pd.DataFrame(rows)


# ---------------------------------------------------------------------------
# 2. Citation Network Construction
# ---------------------------------------------------------------------------

def build_citation_graph(df: pd.DataFrame) -> ig.Graph:
    """Build an undirected citation co-reference graph.

    Nodes  = articles in our dataset
    Edges  = shared references (bibliographic coupling) — two articles that
             cite the same work get an edge, weighted by the number of shared refs.

    We use bibliographic coupling because we only have outgoing references
    for *our* articles (not the full forward citation graph). This is standard
    in bibliometric clustering when you don't have the global citation index.
    """
    log.info("Building citation network via bibliographic coupling ...")

    node_ids = list(df["openalex_id"])
    node_index = {nid: i for i, nid in enumerate(node_ids)}

    # Parse references
    ref_map = {}  # openalex_id -> set of referenced work IDs
    for _, row in df.iterrows():
        refs = set(json.loads(row["referenced_works"]))
        if refs:
            ref_map[row["openalex_id"]] = refs

    # Inverted index: reference -> list of articles citing it
    ref_to_articles = defaultdict(list)
    for article_id, refs in ref_map.items():
        for ref in refs:
            ref_to_articles[ref].append(article_id)

    # Build edges via shared references
    edge_weights = Counter()
    for ref, articles in ref_to_articles.items():
        if len(articles) < 2 or len(articles) > 200:
            # skip very common refs (noise) and singletons
            continue
        for a, b in combinations(articles, 2):
            pair = tuple(sorted([a, b]))
            edge_weights[pair] += 1

    # Filter: keep edges with >= 3 shared references for signal quality
    MIN_SHARED_REFS = 3
    edges = []
    weights = []
    for (a, b), w in edge_weights.items():
        if w >= MIN_SHARED_REFS and a in node_index and b in node_index:
            edges.append((node_index[a], node_index[b]))
            weights.append(w)

    log.info(f"  Nodes: {len(node_ids)}, Edges: {len(edges)} "
             f"(min shared refs = {MIN_SHARED_REFS})")

    G = ig.Graph(n=len(node_ids), edges=edges, directed=False)
    G.vs["name"] = node_ids
    G.vs["year"] = list(df["publication_year"])
    G.vs["title"] = list(df["title"])
    G.vs["primary_topic"] = list(df["primary_topic"])
    G.es["weight"] = weights

    return G


# ---------------------------------------------------------------------------
# 3. Community Detection (Leiden)
# ---------------------------------------------------------------------------

def run_leiden(G: ig.Graph, resolution: float, label: str) -> list[int]:
    """Run Leiden community detection at a given resolution."""
    log.info(f"Running Leiden ({label}) at resolution={resolution} ...")

    partition = leidenalg.find_partition(
        G,
        leidenalg.CPMVertexPartition,
        resolution_parameter=resolution,
        weights="weight",
        n_iterations=10,
        seed=42,
    )

    membership = partition.membership
    n_communities = len(set(membership))
    modularity = partition.quality()
    log.info(f"  {label}: {n_communities} communities, quality={modularity:.4f}")
    return membership


def assign_communities(G: ig.Graph, resolutions: dict) -> pd.DataFrame:
    """Run Leiden at multiple resolutions and return a DataFrame of assignments."""
    results = {"openalex_id": G.vs["name"]}
    for label, res in resolutions.items():
        results[f"community_{label}"] = run_leiden(G, res, label)
    return pd.DataFrame(results)


# ---------------------------------------------------------------------------
# 4. Community Labelling
# ---------------------------------------------------------------------------

def label_communities(df_articles: pd.DataFrame, df_communities: pd.DataFrame,
                      level: str = "meso") -> pd.DataFrame:
    """Label each community by its most frequent OpenAlex topics."""
    col = f"community_{level}"
    merged = df_articles.merge(df_communities[["openalex_id", col]], on="openalex_id")

    rows = []
    for comm_id, group in merged.groupby(col):
        top_topics = (
            group["primary_topic"]
            .dropna()
            .value_counts()
            .head(3)
        )
        label = " | ".join(top_topics.index.tolist()) if len(top_topics) > 0 else "Unlabelled"
        rows.append({
            "community": comm_id,
            "level": level,
            "size": len(group),
            "top_topics": label,
            "top_fields": " | ".join(
                group["primary_topic_field"].dropna().value_counts().head(2).index.tolist()
            ),
        })

    return pd.DataFrame(rows).sort_values("size", ascending=False)


# ---------------------------------------------------------------------------
# 5. Scope Drift Metrics
# ---------------------------------------------------------------------------

def compute_community_distribution(df: pd.DataFrame, community_col: str,
                                   year: int = None) -> pd.Series:
    """Compute the proportion of articles in each community for a given year."""
    subset = df[df["publication_year"] == year] if year else df
    counts = subset[community_col].value_counts()
    return counts / counts.sum()


def compute_drift_metrics(
    df: pd.DataFrame,
    community_col: str,
    baseline_years: list[int],
    target_years: list[int],
) -> list[dict]:
    """Compute scope drift metrics comparing each target year to the baseline."""

    # Baseline distribution
    baseline_mask = df["publication_year"].isin(baseline_years)
    baseline_dist = df.loc[baseline_mask, community_col].value_counts(normalize=True)

    all_communities = sorted(df[community_col].unique())
    baseline_vec = np.array([baseline_dist.get(c, 0.0) for c in all_communities])

    results = []
    for year in target_years:
        year_mask = df["publication_year"] == year
        year_count = year_mask.sum()
        if year_count == 0:
            continue

        year_dist = df.loc[year_mask, community_col].value_counts(normalize=True)
        year_vec = np.array([year_dist.get(c, 0.0) for c in all_communities])

        # Jensen-Shannon Divergence (0 = identical, 1 = completely different)
        jsd = float(jensenshannon(baseline_vec, year_vec) ** 2)  # squared = actual JSD

        # New community fraction — articles in communities absent from baseline
        baseline_communities = set(baseline_dist.index)
        year_communities = set(year_dist.index)
        new_communities = year_communities - baseline_communities
        new_frac = float(year_dist[year_dist.index.isin(new_communities)].sum()) \
            if new_communities else 0.0

        # Entropy
        baseline_entropy = float(sp_entropy(baseline_vec[baseline_vec > 0]))
        year_entropy = float(sp_entropy(year_vec[year_vec > 0]))

        # Top-5 community stability (Jaccard)
        top5_baseline = set(baseline_dist.head(5).index)
        top5_year = set(year_dist.head(5).index)
        jaccard = len(top5_baseline & top5_year) / len(top5_baseline | top5_year) \
            if (top5_baseline | top5_year) else 0.0

        results.append({
            "year": year,
            "n_articles": year_count,
            "jsd": round(jsd, 4),
            "new_community_fraction": round(new_frac, 4),
            "baseline_entropy": round(baseline_entropy, 4),
            "year_entropy": round(year_entropy, 4),
            "entropy_change": round(year_entropy - baseline_entropy, 4),
            "top5_jaccard": round(jaccard, 4),
            "n_communities_year": len(year_communities),
            "n_new_communities": len(new_communities),
        })

    return results


# ---------------------------------------------------------------------------
# 6. Article-Level Outlier Flagging
# ---------------------------------------------------------------------------

def flag_outlier_articles(
    df: pd.DataFrame,
    community_col: str,
    baseline_years: list[int],
    target_year: int,
    threshold: float = 0.01,
) -> pd.DataFrame:
    """Flag individual articles that fall in communities rare in the baseline."""
    baseline_mask = df["publication_year"].isin(baseline_years)
    baseline_dist = df.loc[baseline_mask, community_col].value_counts(normalize=True)

    target_mask = df["publication_year"] == target_year
    target_df = df.loc[target_mask].copy()
    target_df["baseline_community_share"] = target_df[community_col].map(
        lambda c: baseline_dist.get(c, 0.0)
    )
    target_df["is_scope_outlier"] = target_df["baseline_community_share"] < threshold

    return target_df.sort_values("baseline_community_share")


# ---------------------------------------------------------------------------
# 7. Dashboard Generation
# ---------------------------------------------------------------------------

def build_dashboard(
    drift_metrics: list[dict],
    community_summary: pd.DataFrame,
    df_with_communities: pd.DataFrame,
    community_col: str,
    baseline_years: list[int],
    outliers: pd.DataFrame,
) -> str:
    """Build an interactive HTML dashboard using Plotly."""

    drift_df = pd.DataFrame(drift_metrics)

    fig = make_subplots(
        rows=3, cols=2,
        subplot_titles=(
            "Jensen-Shannon Divergence vs Baseline",
            "New Community Fraction",
            "Entropy Change from Baseline",
            "Top-5 Community Jaccard Stability",
            "Community Size Distribution (meso)",
            "Outlier Articles by Community",
        ),
        vertical_spacing=0.12,
        horizontal_spacing=0.10,
    )

    # 1. JSD over time
    fig.add_trace(
        go.Bar(x=drift_df["year"].astype(str), y=drift_df["jsd"],
               marker_color="#e74c3c", name="JSD"),
        row=1, col=1
    )
    fig.update_yaxes(title_text="JSD", row=1, col=1)

    # 2. New community fraction
    fig.add_trace(
        go.Bar(x=drift_df["year"].astype(str), y=drift_df["new_community_fraction"],
               marker_color="#f39c12", name="New Comm. Frac."),
        row=1, col=2
    )
    fig.update_yaxes(title_text="Fraction", row=1, col=2)

    # 3. Entropy change
    colors = ["#27ae60" if v <= 0 else "#e74c3c" for v in drift_df["entropy_change"]]
    fig.add_trace(
        go.Bar(x=drift_df["year"].astype(str), y=drift_df["entropy_change"],
               marker_color=colors, name="ΔEntropy"),
        row=2, col=1
    )
    fig.update_yaxes(title_text="ΔH", row=2, col=1)

    # 4. Top-5 Jaccard
    fig.add_trace(
        go.Bar(x=drift_df["year"].astype(str), y=drift_df["top5_jaccard"],
               marker_color="#3498db", name="Jaccard"),
        row=2, col=2
    )
    fig.update_yaxes(title_text="Jaccard", range=[0, 1], row=2, col=2)

    # 5. Community size distribution for top 15 communities
    top_comms = community_summary.head(15)
    fig.add_trace(
        go.Bar(
            x=[f"C{c}" for c in top_comms["community"]],
            y=top_comms["size"],
            text=top_comms["top_topics"].str[:40],
            textposition="none",
            marker_color="#8e44ad",
            name="Community Size",
            hovertemplate="%{x}<br>Size: %{y}<br>Topics: %{text}<extra></extra>",
        ),
        row=3, col=1
    )
    fig.update_yaxes(title_text="Articles", row=3, col=1)

    # 6. Outlier articles by community
    if not outliers.empty:
        outlier_comm_counts = (
            outliers[outliers["is_scope_outlier"]]
            [community_col]
            .value_counts()
            .head(10)
        )
        fig.add_trace(
            go.Bar(
                x=[f"C{c}" for c in outlier_comm_counts.index],
                y=outlier_comm_counts.values,
                marker_color="#c0392b",
                name="Outlier Articles",
            ),
            row=3, col=2
        )
    fig.update_yaxes(title_text="Flagged Articles", row=3, col=2)

    fig.update_layout(
        title_text=(
            f"Scope Drift Dashboard — Frontiers in Environmental Science<br>"
            f"<sub>Baseline: {baseline_years} | Leiden community detection (meso)</sub>"
        ),
        template="plotly_white",
        height=1000,
        showlegend=False,
        font=dict(family="Segoe UI, Roboto, sans-serif", size=12),
        margin=dict(l=50, r=50, t=100, b=50),
    )

    return fig.to_html(include_plotlyjs="cdn", full_html=True)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    log.info("=" * 60)
    log.info("SCOPE DRIFT PROTOTYPE — Frontiers in Environmental Science")
    log.info("=" * 60)

    # ---- Step 1: Fetch articles ----
    all_years = sorted(set(BASELINE_YEARS + [COMPARISON_YEAR, TARGET_YEAR]))
    log.info(f"\n▶ Step 1: Fetching articles for years {all_years} ...")
    works = fetch_works(OPENALEX_SOURCE_ID, all_years, EMAIL)
    df_articles = works_to_dataframe(works)
    df_articles.to_csv(os.path.join(OUTPUT_DIR, "articles.csv"), index=False)
    log.info(f"  Saved {len(df_articles)} articles to articles.csv")
    log.info(f"  Year breakdown:\n{df_articles['publication_year'].value_counts().sort_index().to_string()}")

    # ---- Step 2: Build citation network ----
    log.info(f"\n▶ Step 2: Building citation network ...")
    G = build_citation_graph(df_articles)

    # Remove isolates for cleaner clustering
    isolates = [v.index for v in G.vs if G.degree(v) == 0]
    log.info(f"  Removing {len(isolates)} isolated nodes ...")
    G.delete_vertices(isolates)
    log.info(f"  Final graph: {G.vcount()} nodes, {G.ecount()} edges")

    G.write_graphml(os.path.join(OUTPUT_DIR, "citation_network.graphml"))
    log.info(f"  Saved citation_network.graphml")

    # ---- Step 3: Leiden community detection ----
    log.info(f"\n▶ Step 3: Running Leiden community detection ...")
    df_communities = assign_communities(G, RESOLUTIONS)

    # Merge year info back
    year_map = dict(zip(df_articles["openalex_id"], df_articles["publication_year"]))
    df_communities["publication_year"] = df_communities["openalex_id"].map(year_map)

    df_communities.to_csv(os.path.join(OUTPUT_DIR, "communities.csv"), index=False)
    log.info(f"  Saved communities.csv ({len(df_communities)} articles)")

    # ---- Step 4: Label communities ----
    log.info(f"\n▶ Step 4: Labelling communities ...")
    community_summary = label_communities(df_articles, df_communities, level="meso")
    community_summary.to_csv(os.path.join(OUTPUT_DIR, "community_summary.csv"), index=False)
    log.info(f"  Top 10 communities (meso):")
    for _, row in community_summary.head(10).iterrows():
        log.info(f"    C{row['community']:>3d}  ({row['size']:>4d} articles)  {row['top_topics'][:80]}")

    # ---- Step 5: Compute drift metrics ----
    log.info(f"\n▶ Step 5: Computing drift metrics ...")
    community_col = "community_meso"
    merged = df_communities.dropna(subset=["publication_year"]).copy()
    merged["publication_year"] = merged["publication_year"].astype(int)

    target_years = sorted(set([COMPARISON_YEAR, TARGET_YEAR]) - set(BASELINE_YEARS))
    drift_metrics = compute_drift_metrics(
        merged, community_col, BASELINE_YEARS, target_years
    )
    drift_df = pd.DataFrame(drift_metrics)
    drift_df.to_csv(os.path.join(OUTPUT_DIR, "drift_report.csv"), index=False)
    log.info(f"  Drift report:\n{drift_df.to_string(index=False)}")

    # ---- Step 6: Flag outlier articles ----
    log.info(f"\n▶ Step 6: Flagging outlier articles in {TARGET_YEAR} ...")
    merged_with_topics = merged.merge(
        df_articles[["openalex_id", "title", "doi", "primary_topic", "primary_topic_field"]],
        on="openalex_id",
        how="left",
    )
    outliers = flag_outlier_articles(
        merged_with_topics, community_col, BASELINE_YEARS, TARGET_YEAR
    )
    n_outliers = outliers["is_scope_outlier"].sum()
    n_target = len(outliers)
    log.info(f"  {n_outliers} / {n_target} articles flagged as potential scope outliers")
    outliers.to_csv(os.path.join(OUTPUT_DIR, "outlier_articles.csv"), index=False)

    if n_outliers > 0:
        log.info(f"  Sample outliers:")
        for _, row in outliers[outliers["is_scope_outlier"]].head(5).iterrows():
            log.info(
                f"    • {row.get('title', 'N/A')[:70]}... "
                f"(topic: {row.get('primary_topic', 'N/A')}, "
                f"baseline share: {row['baseline_community_share']:.4f})"
            )

    # ---- Step 7: Build dashboard ----
    log.info(f"\n▶ Step 7: Building dashboard ...")
    html = build_dashboard(
        drift_metrics, community_summary, merged_with_topics,
        community_col, BASELINE_YEARS, outliers,
    )
    dashboard_path = os.path.join(OUTPUT_DIR, "drift_dashboard.html")
    with open(dashboard_path, "w") as f:
        f.write(html)
    log.info(f"  Saved drift_dashboard.html")

    # ---- Summary ----
    log.info(f"\n{'=' * 60}")
    log.info(f"DONE — All outputs saved to {OUTPUT_DIR}/")
    log.info(f"  articles.csv            — {len(df_articles)} articles")
    log.info(f"  citation_network.graphml — {G.vcount()} nodes, {G.ecount()} edges")
    log.info(f"  communities.csv         — community assignments at 3 scales")
    log.info(f"  community_summary.csv   — community labels & sizes")
    log.info(f"  drift_report.csv        — JSD, entropy, Jaccard metrics")
    log.info(f"  outlier_articles.csv    — {n_outliers} flagged articles")
    log.info(f"  drift_dashboard.html    — interactive Plotly dashboard")
    log.info(f"{'=' * 60}")


if __name__ == "__main__":
    main()
