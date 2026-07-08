"""
build_drift_dashboard_from_cwts.py
==================================
Creates a comprehensive scope drift dashboard matching drift_dashboard.html format.

Metrics computed:
- JSD (Jensen-Shannon Divergence) vs baseline period
- New Community Fraction (papers in clusters absent from baseline)
- Entropy Delta (change in cluster distribution spread)
- Top-5 Jaccard (similarity of top clusters vs baseline)

Data source : local cwts_output/ files
Output      : output/drift_dashboard.html

Usage:
    python scripts/build_drift_dashboard_from_cwts.py

Environment variables:
    CLUSTER_LEVEL : micro, meso, or macro (default: macro)
"""

import json
import logging
import os
from pathlib import Path
from collections import defaultdict

import numpy as np
import pandas as pd
from scipy.spatial.distance import jensenshannon
from scipy.stats import entropy

# ──────────────────────────────────────────────────────────────────────────────
# CONFIG
# ──────────────────────────────────────────────────────────────────────────────
CWTS_DIR = Path(__file__).resolve().parent.parent / "cwts_output"
OUTPUT_PATH = Path(__file__).resolve().parent.parent / "output" / "drift_dashboard.html"

# Target journals
JOURNALS = [
    "Frontiers in Immunology",
    "Frontiers in Public Health",
    "Frontiers in Medicine",
    "Frontiers in Oncology",
    "Frontiers in Psychology",
]

# Cluster level (can override via env var)
CLUSTER_LEVEL = os.environ.get("CLUSTER_LEVEL", "macro")

# GPT labels directory
GPT_LABELS_PATH = Path(__file__).resolve().parent.parent / "cwts_output"
GPT_LABELS = {}

# Baseline years for comparison
BASELINE_YEARS = [2018, 2019, 2020]

# Minimum papers per year to include in calculations
MIN_PAPERS_PER_YEAR = 20

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
# LOAD DATA
# ──────────────────────────────────────────────────────────────────────────────
def load_data() -> pd.DataFrame:
    """Load classification + metadata from local files."""
    log.info("[1/4] Loading data from local files …")

    # Load classification
    classif_path = CWTS_DIR / "classification.txt"
    df_classif = pd.read_csv(
        classif_path,
        sep="\t",
        header=None,
        names=["int_id", "micro", "meso", "macro"],
    )

    # Load metadata
    meta_path = CWTS_DIR / "pub_metadata.txt"
    df_meta = pd.read_csv(
        meta_path,
        sep="\t",
        header=None,
        names=["int_id", "pub_id", "is_frontiers", "journal", "date", "title"],
    )

    # Merge
    df = df_classif.merge(df_meta[["int_id", "journal", "date"]], on="int_id")

    # Parse date to year
    df["pub_year"] = pd.to_datetime(df["date"], errors="coerce").dt.year
    df = df.dropna(subset=["pub_year"])
    df["pub_year"] = df["pub_year"].astype(int)

    # Filter to target journals
    df = df[df["journal"].isin(JOURNALS)].copy()

    log.info(f"       Loaded {len(df):,} papers")
    log.info(f"       Journals: {df['journal'].nunique()}")
    log.info(f"       Years: {df['pub_year'].min()}–{df['pub_year'].max()}")

    return df


# ──────────────────────────────────────────────────────────────────────────────
# COMPUTE METRICS
# ──────────────────────────────────────────────────────────────────────────────
def get_cluster_distribution(df: pd.DataFrame) -> pd.Series:
    """Get normalized distribution over clusters."""
    counts = df[CLUSTER_LEVEL].value_counts()
    return counts / counts.sum()


def compute_jsd(dist1: pd.Series, dist2: pd.Series) -> float:
    """Compute Jensen-Shannon divergence between two distributions."""
    # Align distributions
    all_clusters = set(dist1.index) | set(dist2.index)
    v1 = np.array([dist1.get(c, 0) for c in all_clusters])
    v2 = np.array([dist2.get(c, 0) for c in all_clusters])
    return float(jensenshannon(v1, v2))


def compute_entropy(dist: pd.Series) -> float:
    """Compute Shannon entropy of a distribution."""
    return float(entropy(dist.values, base=2))


def compute_new_community_fraction(
    current_dist: pd.Series, baseline_clusters: set
) -> float:
    """Fraction of papers in clusters not present in baseline."""
    new_clusters = set(current_dist.index) - baseline_clusters
    return float(sum(current_dist.get(c, 0) for c in new_clusters))


def compute_top5_jaccard(dist1: pd.Series, dist2: pd.Series) -> float:
    """Jaccard similarity between top-5 clusters of two distributions."""
    top5_1 = set(dist1.nlargest(5).index)
    top5_2 = set(dist2.nlargest(5).index)
    if not top5_1 or not top5_2:
        return 0.0
    return len(top5_1 & top5_2) / len(top5_1 | top5_2)


def compute_drift_metrics(df: pd.DataFrame) -> dict:
    """Compute all drift metrics for all journals."""
    log.info("[2/4] Computing drift metrics …")

    years = [int(y) for y in sorted(df["pub_year"].unique())]

    # Adjust baseline years to what's available
    available_baseline = [int(y) for y in BASELINE_YEARS if y in years]
    if not available_baseline:
        # Use first 3 years as baseline
        available_baseline = years[:3]

    log.info(f"       Baseline years: {available_baseline}")
    log.info(f"       All years: {years}")

    jsd_trends = {}
    summary = []
    heatmap = []

    for journal in JOURNALS:
        jdf = df[df["journal"] == journal]
        if jdf.empty:
            continue

        # Baseline distribution
        baseline_df = jdf[jdf["pub_year"].isin(available_baseline)]
        if len(baseline_df) < MIN_PAPERS_PER_YEAR:
            log.warning(f"       {journal}: insufficient baseline data, skipping")
            continue

        baseline_dist = get_cluster_distribution(baseline_df)
        baseline_clusters = set(baseline_dist.index)
        baseline_entropy = compute_entropy(baseline_dist)

        # Per-year metrics
        yearly_jsd = []
        yearly_new_comm = []
        yearly_entropy_delta = []
        yearly_articles = []
        yearly_years = []

        for year in years:
            ydf = jdf[jdf["pub_year"] == year]
            if len(ydf) < MIN_PAPERS_PER_YEAR:
                continue

            year_dist = get_cluster_distribution(ydf)

            jsd = compute_jsd(baseline_dist, year_dist)
            new_comm = compute_new_community_fraction(year_dist, baseline_clusters)
            year_entropy = compute_entropy(year_dist)
            entropy_delta = year_entropy - baseline_entropy

            yearly_years.append(int(year))
            yearly_jsd.append(round(jsd, 4))
            yearly_new_comm.append(round(new_comm * 100, 2))
            yearly_entropy_delta.append(round(entropy_delta, 4))
            yearly_articles.append(int(len(ydf)))

            # Heatmap entry
            heatmap.append(
                {"Journal": journal, "Year": int(year), "JSD": round(jsd, 4)}
            )

        if not yearly_years:
            continue

        # Store trends
        jsd_trends[journal] = {
            "years": yearly_years,
            "jsd": yearly_jsd,
            "new_comm": yearly_new_comm,
            "entropy_delta": yearly_entropy_delta,
            "articles": yearly_articles,
        }

        # Latest year summary
        latest_year = max(yearly_years)
        latest_idx = yearly_years.index(latest_year)
        latest_df = jdf[jdf["pub_year"] == latest_year]
        latest_dist = get_cluster_distribution(latest_df)

        summary.append(
            {
                "Journal": journal,
                "Year": latest_year,
                "JSD": yearly_jsd[latest_idx],
                "NewCommunityFrac": round(yearly_new_comm[latest_idx] / 100, 4),
                "Top5Jaccard": round(
                    compute_top5_jaccard(baseline_dist, latest_dist), 4
                ),
                "Entropy": round(compute_entropy(latest_dist), 4),
                "EntropyDelta": yearly_entropy_delta[latest_idx],
                "ArticleCount": yearly_articles[latest_idx],
            }
        )

        log.info(
            f"       {journal}: JSD={yearly_jsd[-1]:.3f}, years={len(yearly_years)}"
        )

    # Sort summary by JSD descending
    summary.sort(key=lambda x: x["JSD"], reverse=True)

    return {
        "jsd_trends": jsd_trends,
        "summary": summary,
        "heatmap": heatmap,
        "baseline_years": available_baseline,
        "all_years": years,
    }


def compute_community_stats(df: pd.DataFrame) -> list:
    """Compute statistics for top communities."""
    log.info("[3/4] Computing community statistics …")

    communities = []
    cluster_counts = df.groupby(CLUSTER_LEVEL).size().sort_values(ascending=False)

    for cluster_id in cluster_counts.head(30).index:
        cdf = df[df[CLUSTER_LEVEL] == cluster_id]
        size = len(cdf)

        # Journal breakdown
        journal_counts = cdf["journal"].value_counts()
        journal_pcts = (journal_counts / size * 100).round(1)

        journals_dict = {}
        for j in journal_pcts.head(5).index:
            journals_dict[j] = float(journal_pcts[j])

        label = GPT_LABELS.get(int(cluster_id), f"Cluster {cluster_id}")
        communities.append(
            {
                "id": int(cluster_id),
                "label": label,
                "size": int(size),
                "journals": journals_dict,
                "dominant": journal_counts.index[0] if len(journal_counts) > 0 else "",
            }
        )

    return communities


# ──────────────────────────────────────────────────────────────────────────────
# BUILD HTML
# ──────────────────────────────────────────────────────────────────────────────
def build_html(metrics: dict, communities: list, df: pd.DataFrame) -> str:
    """Generate the drift dashboard HTML."""
    log.info("[4/4] Building HTML dashboard …")

    # Build data object
    heatmap_journals = sorted(set(h["Journal"] for h in metrics["heatmap"]))
    heatmap_years = [int(y) for y in sorted(set(h["Year"] for h in metrics["heatmap"]))]
    latest_year = int(max(heatmap_years)) if heatmap_years else 0

    data = {
        "jsd_trends": metrics["jsd_trends"],
        "summary": metrics["summary"],
        "heatmap": metrics["heatmap"],
        "heatmap_journals": heatmap_journals,
        "heatmap_years": heatmap_years,
        "communities": communities,
        "baseline_years": metrics["baseline_years"],
        "latest_year": latest_year,
        "stats": {
            "n_journals": len(JOURNALS),
            "n_nodes": int(len(df)),
            "n_edges": 0,  # Not computing edges here
            "year_range": (
                f"{min(heatmap_years)}–{max(heatmap_years)}" if heatmap_years else ""
            ),
        },
    }

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Frontiers Scope Drift Dashboard</title>
<script src="https://cdn.plot.ly/plotly-2.35.2.min.js"></script>
<style>
:root{{--red:#dc2626;--amber:#d97706;--green:#059669;--blue:#3b82f6;--purple:#8b5cf6;--slate:#64748b;--bg:#f8fafc;--card:#fff}}
*{{box-sizing:border-box;margin:0;padding:0}}
body{{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif;background:var(--bg);color:#0f172a;padding:16px 20px;max-width:1440px;margin:0 auto}}
.hdr{{text-align:center;margin-bottom:20px}}
.hdr h1{{font-size:22px;font-weight:700}}.hdr p{{font-size:13px;color:var(--slate);margin-top:2px}}
.badge{{display:inline-block;padding:3px 10px;border-radius:10px;font-size:11px;font-weight:600;margin:4px 2px;background:#f1f5f9;color:#475569}}

.kpis{{display:flex;gap:10px;margin-bottom:16px;flex-wrap:wrap}}
.kpi{{background:var(--card);border-radius:10px;padding:10px 14px;box-shadow:0 1px 2px rgba(0,0,0,.06);flex:1;min-width:130px}}
.kpi .l{{font-size:10px;color:#94a3b8;text-transform:uppercase;letter-spacing:.5px}}
.kpi .v{{font-size:22px;font-weight:700;margin-top:1px}}
.kpi .d{{font-size:11px;color:var(--slate)}}

.grid{{display:grid;gap:14px;margin-bottom:14px}}
.g1{{grid-template-columns:1fr}}.g2{{grid-template-columns:1fr 1fr}}
@media(max-width:900px){{.g2{{grid-template-columns:1fr}}}}

.card{{background:var(--card);border-radius:10px;padding:14px;box-shadow:0 1px 2px rgba(0,0,0,.06)}}
.card h3{{font-size:14px;font-weight:600}}.card .sub{{font-size:11px;color:#94a3b8;margin-bottom:10px}}

table{{width:100%;border-collapse:collapse;font-size:13px}}
th{{text-align:left;padding:7px 8px;border-bottom:2px solid #e5e7eb;font-weight:600;color:var(--slate);font-size:11px;text-transform:uppercase;letter-spacing:.4px}}
td{{padding:7px 8px;border-bottom:1px solid #f3f4f6}}
tr:hover{{background:#f9fafb}}
.drift-h{{color:var(--red);font-weight:700}}
.drift-m{{color:var(--amber);font-weight:600}}
.drift-l{{color:var(--green);font-weight:500}}
.bar-bg{{height:6px;background:#f3f4f6;border-radius:3px;position:relative}}
.bar-f{{height:6px;border-radius:3px;position:absolute;top:0;left:0}}


.foot{{text-align:center;margin-top:24px;font-size:11px;color:#94a3b8}}
</style>
</head>
<body>

<div class="hdr">
<h1>Frontiers Scope Drift Detection</h1>
<p>CWTS Leiden clustering — {CLUSTER_LEVEL} level communities</p>
<span class="badge" id="meta-badge"></span>
</div>

<div class="kpis" id="kpis"></div>

<div class="grid g1">
<div class="card">
<h3>Scope Drift Rankings — <span id="latest-yr"></span> vs Baseline (<span id="bl-yrs"></span>)</h3>
<div class="sub">Jensen-Shannon Divergence measures how much each journal's cluster distribution has shifted</div>
<table id="tbl"><thead><tr>
<th>Journal</th><th>JSD</th><th style="width:100px">JSD</th><th>Entropy Δ</th><th>Articles</th>
</tr></thead><tbody id="tbl-body"></tbody></table>
</div>
</div>

<div class="grid g2">
<div class="card"><h3>Drift Trajectory Over Time</h3><div class="sub">JSD trend per journal — rising = increasing scope drift</div><div id="jsd-trend" style="height:420px"></div></div>
<div class="card"><h3>Entropy Change</h3><div class="sub">Positive = spreading across more communities; Negative = concentrating</div><div id="entropy" style="height:420px"></div></div>
</div>

<div class="foot">Data: CWTS clustering · Leiden algorithm · {CLUSTER_LEVEL} level</div>

<script>
const D={json.dumps(data)};
const COLORS=['#4338ca','#dc2626','#d97706','#059669','#0891b2','#7c3aed','#db2777','#ea580c',
              '#16a34a','#2563eb','#9333ea','#c026d3','#0d9488','#ca8a04','#64748b'];

// Header
document.getElementById('meta-badge').textContent=
  `Leiden · {CLUSTER_LEVEL} · ${{D.stats.n_nodes.toLocaleString()}} papers · ${{D.stats.year_range}}`;
document.getElementById('latest-yr').textContent=D.latest_year;
document.getElementById('bl-yrs').textContent=D.baseline_years.join('–');

// KPIs
const highD=D.summary.filter(d=>d.JSD>0.30).length;
const medD=D.summary.filter(d=>d.JSD>0.20&&d.JSD<=0.30).length;
const avgJSD=D.summary.length?(D.summary.reduce((s,d)=>s+d.JSD,0)/D.summary.length).toFixed(3):'—';
const maxD=D.summary[0]||{{}};
document.getElementById('kpis').innerHTML=`
<div class="kpi"><div class="l">Journals</div><div class="v">${{D.stats.n_journals}}</div><div class="d">Frontiers journals</div></div>
<div class="kpi"><div class="l">High Drift (JSD>0.30)</div><div class="v" style="color:var(--red)">${{highD}}</div><div class="d">above threshold</div></div>
<div class="kpi"><div class="l">Medium Drift (0.20–0.30)</div><div class="v" style="color:var(--amber)">${{medD}}</div><div class="d">caution zone</div></div>
<div class="kpi"><div class="l">Average JSD (${{D.latest_year}})</div><div class="v">${{avgJSD}}</div><div class="d">across all journals</div></div>
<div class="kpi"><div class="l">Highest Drift</div><div class="v" style="color:var(--red)">${{maxD.JSD||'—'}}</div><div class="d">${{maxD.Journal||''}}</div></div>`;

// Summary table
const tb=document.getElementById('tbl-body');
let th='';
D.summary.forEach(d=>{{
  const cls=d.JSD>0.30?'drift-h':d.JSD>0.20?'drift-m':'drift-l';
  const pct=Math.min(d.JSD/0.40*100,100);
  const bc=d.JSD>0.30?'var(--red)':d.JSD>0.20?'var(--amber)':'var(--green)';
  const ed=d.EntropyDelta;
  th+=`<tr><td><strong>${{d.Journal}}</strong></td>
    <td class="${{cls}}">${{d.JSD.toFixed(3)}}</td>
    <td><div class="bar-bg"><div class="bar-f" style="width:${{pct}}%;background:${{bc}}"></div></div></td>
    <td style="color:${{ed>0?'var(--red)':'var(--green)'}}">${{ed>0?'+':''}}${{ed.toFixed(3)}}</td>
    <td>${{d.ArticleCount.toLocaleString()}}</td></tr>`;
}});
tb.innerHTML=th;

// JSD Trend
const tTraces=[];let ci=0;
for(const[j,d]of Object.entries(D.jsd_trends)){{
  tTraces.push({{x:d.years,y:d.jsd,name:j,type:'scatter',mode:'lines+markers',
    line:{{color:COLORS[ci%COLORS.length],width:2}},marker:{{size:5}}}});ci++;
}}
Plotly.newPlot('jsd-trend',tTraces,{{
  template:'plotly_white',autosize:true,margin:{{l:50,r:20,t:20,b:80}},
  xaxis:{{title:'Year',dtick:1}},yaxis:{{title:'Jensen-Shannon Divergence',rangemode:'tozero'}},
  legend:{{font:{{size:10}},orientation:'h',x:0.5,y:-0.25,xanchor:'center'}},hovermode:'x unified'
}},{{responsive:true}});

// Entropy chart
ci=0;
const eT=[];ci=0;
for(const[j,d]of Object.entries(D.jsd_trends)){{
  eT.push({{x:d.years,y:d.entropy_delta,name:j,type:'scatter',mode:'lines+markers',
    line:{{color:COLORS[ci%COLORS.length],width:2}},marker:{{size:5}}}});ci++;
}}
Plotly.newPlot('entropy',eT,{{
  template:'plotly_white',autosize:true,margin:{{l:50,r:20,t:20,b:80}},
  xaxis:{{title:'Year',dtick:1}},yaxis:{{title:'Entropy Δ vs Baseline'}},
  legend:{{font:{{size:10}},orientation:'h',x:0.5,y:-0.25,xanchor:'center'}},hovermode:'x unified',
  shapes:[{{type:'line',y0:0,y1:0,xref:'paper',x0:0,x1:1,
           line:{{color:'#d1d5db',width:1,dash:'dot'}}}}]
}},{{responsive:true}});

</script>
</body>
</html>"""

    return html


# ──────────────────────────────────────────────────────────────────────────────
# MAIN
# ──────────────────────────────────────────────────────────────────────────────
def main():
    global GPT_LABELS

    log.info("=" * 60)
    log.info("Building Drift Dashboard from CWTS Output")
    log.info(f"Cluster level: {CLUSTER_LEVEL}")
    log.info("=" * 60)

    # Load GPT labels
    GPT_LABELS = load_gpt_labels()

    # Load data
    df = load_data()

    # Compute metrics
    metrics = compute_drift_metrics(df)
    communities = compute_community_stats(df)

    # Build HTML
    html = build_html(metrics, communities, df)

    # Write output
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(html, encoding="utf-8")

    log.info(f"       Written to {OUTPUT_PATH}")
    log.info(f"       File size: {OUTPUT_PATH.stat().st_size / 1024:.1f} KB")

    log.info("=" * 60)
    log.info("Done!")
    log.info("=" * 60)


if __name__ == "__main__":
    main()
