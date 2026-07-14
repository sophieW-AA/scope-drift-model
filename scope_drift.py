"""
scope_drift.py
==============
Visualises how the research focus of each cluster shifts over time using
Jensen-Shannon divergence on sub-cluster composition.

Loads data from BigQuery (joined classification + pub_metadata tables).

Output:
    cwts_output/scope_drift_Y.html   (yearly, default)
    cwts_output/scope_drift_Q.html   (quarterly, with --quarterly flag)

Usage:
    python scope_drift.py                        # yearly, macro → meso
    python scope_drift.py --quarterly            # quarterly, macro → meso
    python scope_drift.py --level meso           # yearly, meso → micro
    python scope_drift.py --quarterly --level meso
    python scope_drift.py --min-papers 50        # stricter sparse-period filter
"""

import argparse
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import plotly.graph_objects as go
from scipy.spatial.distance import jensenshannon
from google.cloud import bigquery

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------
OUTPUT_DIR = Path("cwts_output")
MIN_PAPERS = 30
CHILD_OF   = {"macro": "meso", "meso": "micro"}

# BigQuery configuration
BQ_PROJECT = "ocean-tech-adv-analytics-c-tfs"
BQ_DATASET = "scope_drift_raw"
TBL_CLASSIF = f"{BQ_DATASET}.classification_raw_20260617_081903"
TBL_PUB_META = f"{BQ_DATASET}.pub_metadata_raw_20260617_081904"

PALETTE = [
    "#4e79a7", "#f28e2b", "#e15759", "#76b7b2", "#59a14f",
    "#edc948", "#b07aa1", "#ff9da7", "#9c755f", "#bab0ac",
    "#17becf", "#bcbd22", "#7f7f7f", "#8c564b", "#e377c2",
]

# ---------------------------------------------------------------------------
# Args
# ---------------------------------------------------------------------------
def parse_args():
    p = argparse.ArgumentParser(description="Scope drift visualiser")
    p.add_argument("--quarterly", action="store_true",
                   help="Quarterly granularity (default: yearly)")
    p.add_argument("--level", default="macro", choices=["macro", "meso"],
                   help="Parent cluster level (default: macro)")
    p.add_argument("--min-papers", type=int, default=MIN_PAPERS,
                   help=f"Min papers per period (default: {MIN_PAPERS})")
    return p.parse_args()

# ---------------------------------------------------------------------------
# Data loading
# ---------------------------------------------------------------------------
def load_data() -> pd.DataFrame:
    """Load classification + metadata from BigQuery with a single JOIN."""
    bq = bigquery.Client(project=BQ_PROJECT)
    
    query = f"""
    SELECT 
        c.int_id,
        c.micro,
        c.meso,
        c.macro,
        m.pub_id,
        m.is_frontiers,
        m.journal,
        m.date AS pub_date,
        m.title
    FROM `{TBL_CLASSIF}` c
    JOIN `{TBL_PUB_META}` m
    ON c.int_id = m.int_id
    """
    
    print(f"Loading from BigQuery: {TBL_CLASSIF} + {TBL_PUB_META}...")
    merged = bq.query(query).to_dataframe()
    print(f"Loaded: {len(merged):,} publications")
    return merged


def add_period(df: pd.DataFrame, quarterly: bool) -> pd.DataFrame:
    df = df.copy()
    df["pub_date"] = pd.to_datetime(df["pub_date"], errors="coerce")

    n_missing = df["pub_date"].isna().sum()
    if n_missing:
        print(f"  Dropped {n_missing:,} rows with no date")
    df = df.dropna(subset=["pub_date"])

    df["pub_year"] = df["pub_date"].dt.year
    if quarterly:
        df["period"] = (
            df["pub_year"].astype(str)
            + "-Q"
            + df["pub_date"].dt.quarter.astype(str)
        )
    else:
        df["period"] = df["pub_year"].astype(str)

    return df

# ---------------------------------------------------------------------------
# Labels
# ---------------------------------------------------------------------------
def load_labels(level: str) -> dict[int, str]:
    path = OUTPUT_DIR / f"{level}_labels.csv"
    if not path.exists():
        return {}
    df = pd.read_csv(path)
    if "cluster_id" not in df.columns or "short_label" not in df.columns:
        return {}
    return dict(zip(df["cluster_id"].astype(int), df["short_label"].astype(str)))


def cluster_name(cluster_id: int, labels: dict) -> str:
    label = labels.get(cluster_id, "")
    return f"{cluster_id}: {label}" if label else str(cluster_id)

# ---------------------------------------------------------------------------
# Drift calculation
# ---------------------------------------------------------------------------
def js_div(p: np.ndarray, q: np.ndarray) -> float:
    """Jensen-Shannon divergence in [0, 1] (squared JS distance)."""
    p = np.asarray(p, dtype=float)
    q = np.asarray(q, dtype=float)
    if p.sum() == 0 or q.sum() == 0:
        return np.nan
    p /= p.sum()
    q /= q.sum()
    return float(jensenshannon(p, q, base=2) ** 2)


def compute_drift_for_cluster(
    group: pd.DataFrame,
    child_level: str,
    min_papers: int,
) -> dict | None:
    ct = (
        group.groupby(["period", child_level])
        .size()
        .reset_index(name="n")
    )
    period_totals = ct.groupby("period")["n"].sum()
    valid = period_totals[period_totals >= min_papers].index
    ct = ct[ct["period"].isin(valid)]

    if ct.empty or ct["period"].nunique() < 2:
        return None

    pivot = ct.pivot_table(index="period", columns=child_level, values="n", fill_value=0)
    pivot = pivot.sort_index()
    proportions = pivot.div(pivot.sum(axis=1), axis=0)

    baseline = pivot.index[0]
    base_vec = proportions.loc[baseline].values
    drift = proportions.apply(lambda row: js_div(base_vec, row.values), axis=1)

    return {
        "periods":      list(pivot.index),
        "children":     list(pivot.columns),
        "proportions":  proportions,
        "drift":        drift,
        "counts":       period_totals.reindex(pivot.index),
        "baseline":     baseline,
    }


def build_drift_data(
    df: pd.DataFrame,
    parent_level: str,
    child_level: str,
    min_papers: int,
) -> dict[int, dict]:
    results = {}
    for parent_id, group in df.groupby(parent_level):
        d = compute_drift_for_cluster(group, child_level, min_papers)
        if d is not None:
            results[int(parent_id)] = d
    return results

# ---------------------------------------------------------------------------
# Plotly figure
# ---------------------------------------------------------------------------
def build_figure(
    drift_data: dict[int, dict],
    parent_labels: dict,
    child_labels: dict,
    parent_level: str,
    child_level: str,
    quarterly: bool,
) -> go.Figure:
    cluster_ids = sorted(drift_data.keys())
    gran_label  = "Quarterly" if quarterly else "Yearly"
    fig = go.Figure()

    cluster_trace_ranges: dict[int, list[int]] = {}

    # --- Per-cluster traces (hidden by default) ---
    for cid in cluster_ids:
        d = drift_data[cid]
        start = len(fig.data)

        for ci, child_id in enumerate(d["children"]):
            fig.add_trace(go.Bar(
                x=d["periods"],
                y=d["proportions"][child_id].tolist(),
                name=cluster_name(int(child_id), child_labels),
                marker_color=PALETTE[ci % len(PALETTE)],
                legendgroup=f"c{cid}",
                showlegend=True,
                visible=False,
                yaxis="y",
                hovertemplate=(
                    f"<b>{cluster_name(int(child_id), child_labels)}</b>"
                    "<br>Period: %{x}<br>Share: %{y:.1%}<extra></extra>"
                ),
            ))

        fig.add_trace(go.Scatter(
            x=d["periods"],
            y=d["drift"].tolist(),
            name="Drift score (JS div.)",
            line=dict(color="#d62728", width=2, dash="dot"),
            mode="lines+markers",
            marker=dict(size=6),
            legendgroup=f"c{cid}",
            showlegend=True,
            visible=False,
            yaxis="y2",
            hovertemplate="Period: %{x}<br>Drift: %{y:.3f}<extra></extra>",
        ))

        cluster_trace_ranges[cid] = list(range(start, len(fig.data)))

    # --- Overview bar (peak drift per cluster) ---
    summary_x = [cluster_name(cid, parent_labels) for cid in cluster_ids]
    summary_y = [drift_data[cid]["drift"].max() for cid in cluster_ids]
    summary_n = [drift_data[cid]["counts"].sum() for cid in cluster_ids]
    max_y     = max(summary_y) if summary_y else 1
    max_y     = max_y if max_y > 0 else 1  # guard against division by zero

    summary_start = len(fig.data)
    fig.add_trace(go.Bar(
        x=summary_x,
        y=summary_y,
        name="Peak drift",
        marker_color=[
            f"rgba(78,121,167,{0.4 + 0.6 * v / max_y})" for v in summary_y
        ],
        visible=True,
        yaxis="y",
        customdata=list(zip(summary_n, summary_y)),
        hovertemplate=(
            "<b>%{x}</b><br>Papers: %{customdata[0]:,.0f}"
            "<br>Peak drift: %{customdata[1]:.3f}<extra></extra>"
        ),
    ))
    summary_traces = list(range(summary_start, len(fig.data)))

    # --- Dropdown buttons ---
    def visibility(show_traces: list[int]) -> list[bool]:
        v = [False] * len(fig.data)
        for ti in show_traces:
            v[ti] = True
        return v

    overview_btn = dict(
        label="▶ Overview — Peak Drift by Cluster",
        method="update",
        args=[
            {"visible": visibility(summary_traces)},
            {
                "title.text": (
                    f"<b>Scope Drift Overview — {parent_level.title()} Clusters</b><br>"
                    f"<sup>{gran_label} · JS divergence from baseline period</sup>"
                ),
                "barmode": "group",
            },
        ],
    )

    cluster_btns = []
    for cid in cluster_ids:
        d   = drift_data[cid]
        lbl = cluster_name(cid, parent_labels)
        cluster_btns.append(dict(
            label=f"{lbl}  (peak {d['drift'].max():.2f})",
            method="update",
            args=[
                {"visible": visibility(cluster_trace_ranges[cid])},
                {
                    "title.text": (
                        f"<b>Scope Drift — {parent_level.title()} cluster {lbl}</b><br>"
                        f"<sup>{gran_label} · {len(d['periods'])} periods"
                        f" · baseline: {d['baseline']}</sup>"
                    ),
                    "barmode": "stack",
                },
            ],
        ))

    fig.update_layout(
        title=dict(
            text=(
                f"<b>Scope Drift Overview — {parent_level.title()} Clusters</b><br>"
                f"<sup>{gran_label} · JS divergence from baseline period</sup>"
            ),
            font=dict(size=16),
        ),
        updatemenus=[dict(
            buttons=[overview_btn] + cluster_btns,
            direction="down",
            showactive=True,
            x=0.01, xanchor="left",
            y=1.18, yanchor="top",
            bgcolor="white",
            bordercolor="#cccccc",
            font=dict(size=12),
        )],
        barmode="group",
        yaxis=dict(
            title="Sub-cluster share",
            tickformat=".0%",
            range=[0, 1.05],
        ),
        yaxis2=dict(
            title="Drift score (JS divergence)",
            overlaying="y",
            side="right",
            range=[0, 1.05],
            showgrid=False,
            tickformat=".2f",
        ),
        legend=dict(
            x=1.08, y=1,
            bgcolor="rgba(255,255,255,0.8)",
            bordercolor="#cccccc",
            borderwidth=1,
        ),
        plot_bgcolor="white",
        paper_bgcolor="#f9fafb",
        hovermode="x unified",
        margin=dict(l=60, r=180, t=130, b=80),
        font=dict(
            family="-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif",
            size=13,
        ),
        height=560,
    )
    fig.update_xaxes(showgrid=True, gridcolor="#e5e7eb", tickangle=-30, automargin=True)

    return fig

# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    args         = parse_args()
    quarterly    = args.quarterly
    parent_level = args.level
    child_level  = CHILD_OF[parent_level]
    min_papers   = args.min_papers
    gran         = "Q" if quarterly else "Y"

    # Load
    df = load_data()
    df = add_period(df, quarterly)
    print(f"Date coverage: {df['pub_year'].min()}–{df['pub_year'].max()}  |  "
          f"{df['period'].nunique()} periods")

    # Labels
    parent_labels = load_labels(parent_level)
    child_labels  = load_labels(child_level)
    if parent_labels:
        print(f"Labels loaded: {len(parent_labels)} {parent_level}, {len(child_labels)} {child_level}")

    # Drift
    print(f"\nComputing drift: {parent_level} → {child_level} ({gran}, min {min_papers} papers/period)…")
    drift_data = build_drift_data(df, parent_level, child_level, min_papers)
    print(f"Clusters with sufficient data: {len(drift_data)}")

    if not drift_data:
        sys.exit(f"No clusters passed min-papers={min_papers}. Try a lower value.")

    # Summary table
    print(f"\n{'Cluster':>10}  {'Label':35}  {'Periods':>7}  {'Peak Drift':>10}  {'Baseline':>10}")
    print("-" * 80)
    for cid in sorted(drift_data, key=lambda c: -drift_data[c]["drift"].max()):
        d   = drift_data[cid]
        lbl = parent_labels.get(cid, "")[:35]
        print(f"{cid:>10}  {lbl:35}  {len(d['periods']):>7}  "
              f"{d['drift'].max():>10.3f}  {d['baseline']:>10}")

    # Figure
    print("\nBuilding figure…")
    fig = build_figure(drift_data, parent_labels, child_labels,
                       parent_level, child_level, quarterly)

    out = OUTPUT_DIR / f"scope_drift_{gran}.html"
    fig.write_html(str(out), include_plotlyjs="cdn")
    print(f"Saved → {out}")


if __name__ == "__main__":
    main()
