"""
build_unified_dashboard.py
==========================
Generates all dashboards from BigQuery data and combines them.

Reads from BigQuery tables:
    - {BQ_DATASET}.classification_raw_{RUN_TIMESTAMP}
    - {BQ_DATASET}.pub_metadata_raw_{RUN_TIMESTAMP}
    - {BQ_DATASET}.cit_links_raw_{RUN_TIMESTAMP}

Output:
    - output/combined_dashboard.html

Usage:
    python scripts/build_unified_dashboard.py

Environment variables (required):
    RUN_TIMESTAMP : timestamp suffix for BigQuery tables (e.g. 20260714_151745)

Environment variables (optional):
    CLUSTER_LEVEL : micro, meso, or macro (default: macro)
    BQ_PROJECT    : BigQuery project (default: ocean-tech-adv-analytics-c-tfs)
    BQ_DATASET    : BigQuery dataset (default: scope_drift_raw)
"""

import json
import logging
import os
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.spatial.distance import jensenshannon
from scipy.stats import entropy

# ──────────────────────────────────────────────────────────────────────────────
# SHARED CONFIG
# ──────────────────────────────────────────────────────────────────────────────
BASE_DIR = Path(__file__).resolve().parent.parent
CWTS_DIR = BASE_DIR / "cwts_output"  # For GPT labels only
OUTPUT_DIR = BASE_DIR / "output"
RENDER_SCRIPT_PATH = BASE_DIR / "render_script.js"

# BigQuery config
BQ_PROJECT = os.environ.get("BQ_PROJECT", "ocean-tech-adv-analytics-c-tfs")
BQ_DATASET = os.environ.get("BQ_DATASET", "scope_drift_raw")
RUN_TIMESTAMP = os.environ.get("RUN_TIMESTAMP", "")
CLUSTER_LEVEL = os.environ.get("CLUSTER_LEVEL", "macro")

PRIMARY_COVERAGE = 0.8
BASELINE_YEARS = [2018, 2019, 2020]
MIN_PAPERS_PER_YEAR = 20
MAX_COMMUNITIES = {"macro": 50, "meso": 100, "micro": 200}

JOURNALS = [
    "Frontiers in Immunology",
    "Frontiers in Public Health",
    "Frontiers in Medicine",
    "Frontiers in Oncology",
    "Frontiers in Psychology",
]

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s  %(message)s", datefmt="%H:%M:%S"
)
log = logging.getLogger(__name__)

# Global GPT labels (loaded once, shared by all dashboards)
GPT_LABELS = {}
GPT_LABELS_ALL = {"macro": {}, "meso": {}, "micro": {}}


# ══════════════════════════════════════════════════════════════════════════════
# BIGQUERY DATA LOADING
# ══════════════════════════════════════════════════════════════════════════════
def load_merged_data() -> pd.DataFrame:
    """Load and merge classification + metadata from BigQuery, filtered to target journals."""
    from google.cloud import bigquery

    log.info(f"       Project: {BQ_PROJECT}")
    log.info(f"       Dataset: {BQ_DATASET}")
    log.info(f"       Timestamp: {RUN_TIMESTAMP}")

    tbl_classif = f"{BQ_PROJECT}.{BQ_DATASET}.classification_raw_{RUN_TIMESTAMP}"
    tbl_pub_meta = f"{BQ_PROJECT}.{BQ_DATASET}.pub_metadata_raw_{RUN_TIMESTAMP}"

    log.info(f"       Classification: {tbl_classif}")
    log.info(f"       Pub metadata: {tbl_pub_meta}")

    journals_str = ", ".join(f"'{j}'" for j in JOURNALS)

    client = bigquery.Client(project=BQ_PROJECT)

    query = f"""
    SELECT 
        c.int_id,
        c.micro,
        c.meso,
        c.macro,
        m.pub_id,
        m.is_frontiers,
        m.journal,
        m.date,
        m.title
    FROM `{tbl_classif}` c
    JOIN `{tbl_pub_meta}` m ON c.int_id = m.int_id
    WHERE m.journal IN ({journals_str})
    """

    df = client.query(query).to_dataframe()
    log.info(f"       Loaded {len(df):,} rows from BigQuery")

    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    df["pub_year"] = df["date"].dt.year
    df = df.dropna(subset=["pub_year"])
    df["pub_year"] = df["pub_year"].astype(int)

    return df


def load_citations() -> pd.DataFrame:
    """Load citation links from BigQuery, filtered to relevant papers only."""
    from google.cloud import bigquery

    tbl_cit_links = f"{BQ_PROJECT}.{BQ_DATASET}.cit_links_raw_{RUN_TIMESTAMP}"
    tbl_classif = f"{BQ_PROJECT}.{BQ_DATASET}.classification_raw_{RUN_TIMESTAMP}"
    tbl_pub_meta = f"{BQ_PROJECT}.{BQ_DATASET}.pub_metadata_raw_{RUN_TIMESTAMP}"

    log.info(f"       Citation links: {tbl_cit_links}")

    client = bigquery.Client(project=BQ_PROJECT)

    journals_str = ", ".join(f"'{j}'" for j in JOURNALS)

    query = f"""
    WITH journal_papers AS (
        SELECT c.int_id
        FROM `{tbl_classif}` c
        JOIN `{tbl_pub_meta}` m ON c.int_id = m.int_id
        WHERE m.journal IN ({journals_str})
    )
    SELECT cl.int_id1, cl.int_id2, cl.weight
    FROM `{tbl_cit_links}` cl
    WHERE cl.int_id1 IN (SELECT int_id FROM journal_papers)
      AND cl.int_id2 IN (SELECT int_id FROM journal_papers)
    """

    try:
        df = client.query(query).to_dataframe()
        log.info(f"       Loaded {len(df):,} citation edges")
    except Exception as e:
        log.warning(f"       Citation query failed: {e}")
        df = pd.DataFrame(columns=["int_id1", "int_id2", "weight"])

    return df


def load_run_metadata() -> dict:
    """Load run metadata from BigQuery."""
    if not RUN_TIMESTAMP:
        return {}

    try:
        import pandas_gbq

        table = f"{BQ_PROJECT}.{BQ_DATASET}.run_metadata_{RUN_TIMESTAMP}"
        query = f"SELECT * FROM `{table}` LIMIT 1"
        df = pandas_gbq.read_gbq(query, project_id=BQ_PROJECT)

        if df.empty:
            log.warning("No metadata found in %s", table)
            return {}

        row = df.iloc[0].to_dict()
        if "journal_ids" in row and isinstance(row["journal_ids"], str):
            row["journal_ids"] = json.loads(row["journal_ids"])

        log.info("       Loaded run metadata from BigQuery")
        return row
    except Exception as e:
        log.warning("Could not load metadata from BigQuery: %s", e)
        return {}


def load_gpt_labels_single(level: str) -> dict:
    """Load GPT labels for a single cluster level."""
    labels_file = CWTS_DIR / f"{level}_labels.csv"
    if not labels_file.exists():
        return {}

    df = pd.read_csv(labels_file)
    labels = {}
    for _, row in df.iterrows():
        cluster_id = int(row["cluster_id"])
        labels[cluster_id] = row["short_label"]
    return labels


def load_gpt_labels_all() -> dict:
    """Load GPT labels for all levels with full info."""
    labels = {"macro": {}, "meso": {}, "micro": {}}

    for level in ["macro", "meso", "micro"]:
        labels_file = CWTS_DIR / f"{level}_labels.csv"
        if labels_file.exists():
            df = pd.read_csv(labels_file)
            for _, row in df.iterrows():
                cluster_id = int(row["cluster_id"])
                labels[level][cluster_id] = {
                    "short_label": row["short_label"],
                    "long_label": row.get("long_label", row["short_label"]),
                    "keywords": (
                        eval(row["keywords"]) if pd.notna(row.get("keywords")) else []
                    ),
                }
            log.info(f"       {level}_labels.csv: {len(labels[level])} labels")
    return labels


# ══════════════════════════════════════════════════════════════════════════════
# SCOPE DASHBOARD
# ══════════════════════════════════════════════════════════════════════════════
def _circular_layout(n: int) -> np.ndarray:
    """Simple circular layout fallback."""
    angles = np.linspace(0, 2 * np.pi, n, endpoint=False)
    return np.column_stack([np.cos(angles), np.sin(angles)])


def compute_scatter_positions(df: pd.DataFrame, df_cit: pd.DataFrame) -> dict:
    """Compute x,y positions for papers using citation-based force-directed layout."""
    import igraph as ig

    communities = df[CLUSTER_LEVEL].unique()
    n_comm = len(communities)
    cluster_to_idx = {c: i for i, c in enumerate(communities)}

    paper_to_cluster = df.set_index("int_id")[CLUSTER_LEVEL].to_dict()
    valid_ids = set(paper_to_cluster.keys())

    df_cit_filtered = df_cit[
        df_cit["int_id1"].isin(valid_ids) & df_cit["int_id2"].isin(valid_ids)
    ].copy()

    df_cit_filtered["src_cluster"] = df_cit_filtered["int_id1"].map(paper_to_cluster)
    df_cit_filtered["tgt_cluster"] = df_cit_filtered["int_id2"].map(paper_to_cluster)
    df_cit_filtered = df_cit_filtered[
        df_cit_filtered["src_cluster"] != df_cit_filtered["tgt_cluster"]
    ]

    df_edges = (
        df_cit_filtered.groupby(["src_cluster", "tgt_cluster"])
        .agg(total_weight=("weight", "sum"))
        .reset_index()
    )

    g = ig.Graph(n=n_comm)
    edges = []
    weights = []
    for _, row in df_edges.iterrows():
        src = cluster_to_idx.get(row["src_cluster"])
        tgt = cluster_to_idx.get(row["tgt_cluster"])
        if src is not None and tgt is not None and src != tgt:
            edges.append((src, tgt))
            weights.append(float(row["total_weight"]))

    if len(edges) > 10:
        g.add_edges(edges)
        g.es["weight"] = weights
        try:
            layout = g.layout_fruchterman_reingold(weights="weight", niter=500)
            coords = np.array(layout.coords)
        except Exception:
            coords = _circular_layout(n_comm)
    else:
        coords = _circular_layout(n_comm)

    if len(coords) > 0:
        mins = coords.min(axis=0)
        maxs = coords.max(axis=0)
        ranges = maxs - mins
        ranges[ranges == 0] = 1
        coords = (coords - mins) / ranges
        coords = coords * 0.8 + 0.1

    comm_positions = {
        c: (float(coords[i, 0]), float(coords[i, 1])) for c, i in cluster_to_idx.items()
    }

    positions = {}
    np.random.seed(42)
    for _, row in df.iterrows():
        cx, cy = comm_positions.get(row[CLUSTER_LEVEL], (0.5, 0.5))
        jitter = 0.06
        x = cx + np.random.uniform(-jitter, jitter)
        y = cy + np.random.uniform(-jitter, jitter)
        positions[row["int_id"]] = (float(x), float(y))

    return positions


def compute_primary_clusters(df: pd.DataFrame, journal: str) -> set:
    """Find smallest set of clusters covering PRIMARY_COVERAGE of papers."""
    jdf = df[df["journal"] == journal]
    counts = jdf[CLUSTER_LEVEL].value_counts()
    total = counts.sum()

    primary = set()
    cumsum = 0
    for comm, count in counts.items():
        primary.add(comm)
        cumsum += count
        if cumsum >= total * PRIMARY_COVERAGE:
            break
    return primary


def compute_journal_stats(df: pd.DataFrame, positions: dict) -> list:
    """Compute statistics for each journal."""
    journals_data = []
    years = sorted(df["pub_year"].unique())

    for journal in JOURNALS:
        jdf = df[df["journal"] == journal].copy()
        if jdf.empty:
            continue

        primary_clusters = compute_primary_clusters(df, journal)
        jdf["is_oos"] = ~jdf[CLUSTER_LEVEL].isin(primary_clusters)

        n_articles = len(jdf)
        n_oos = jdf["is_oos"].sum()
        oos_pct = (n_oos / n_articles * 100) if n_articles else 0

        oos_by_year = []
        for year in years:
            ydf = jdf[jdf["pub_year"] == year]
            if len(ydf) >= 10:
                y_oos = ydf["is_oos"].sum()
                oos_by_year.append({
                    "year": int(year),
                    "articles": int(len(ydf)),
                    "out_of_scope": int(y_oos),
                    "out_of_scope_pct": round(y_oos / len(ydf) * 100, 1) if len(ydf) else 0,
                })

        comm_counts = jdf[CLUSTER_LEVEL].value_counts()
        top_comms = []
        for comm, count in comm_counts.head(10).items():
            label = GPT_LABELS.get(int(comm), f"Cluster {comm}")
            top_comms.append({
                "comm_id": int(comm),
                "label": label,
                "is_primary": comm in primary_clusters,
                "papers_in_comm": int(count),
                "share_of_journal": round(count / n_articles * 100, 1),
            })

        scatter = []
        for _, row in jdf.iterrows():
            if row["int_id"] in positions:
                x, y = positions[row["int_id"]]
                scatter.append({
                    "x": round(x, 4),
                    "y": round(y, 4),
                    "c": int(row[CLUSTER_LEVEL]),
                    "t": str(row["title"] or "")[:50],
                })

        journals_data.append({
            "name": journal,
            "articles": n_articles,
            "out_of_scope": int(n_oos),
            "out_of_scope_pct": round(oos_pct, 1),
            "n_primary_clusters": len(primary_clusters),
            "primary_coverage_pct": round(PRIMARY_COVERAGE * 100, 1),
            "top_communities": top_comms,
            "oos_by_year": oos_by_year,
            "scatter": scatter,
        })

    return journals_data


def compute_community_stats_scope(df: pd.DataFrame) -> list:
    """Compute statistics for each community (scope dashboard version)."""
    communities = []
    comm_counts = df.groupby(CLUSTER_LEVEL).agg(size=("int_id", "count")).reset_index()

    for _, row in comm_counts.nlargest(100, "size").iterrows():
        comm_id = row[CLUSTER_LEVEL]
        cdf = df[df[CLUSTER_LEVEL] == comm_id]

        journal_counts = cdf["journal"].value_counts()
        dominant_journal = journal_counts.index[0] if len(journal_counts) else "Unknown"
        dominant_pct = round(journal_counts.iloc[0] / len(cdf) * 100, 1) if len(journal_counts) else 0

        top_journals = [
            {"name": j, "count": int(c), "pct": round(c / len(cdf) * 100, 1)}
            for j, c in journal_counts.head(3).items()
        ]

        label = GPT_LABELS.get(int(comm_id), f"Cluster {comm_id}")
        communities.append({
            "id": int(comm_id),
            "label": label,
            "size": int(row["size"]),
            "frontiers_pct": 100.0,
            "dominant_journal": dominant_journal,
            "dominant_pct": dominant_pct,
            "top_journals": top_journals,
        })

    return communities


SCOPE_HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Journal Scope Dashboard</title>
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

#scatterGrid { margin-top: 16px; }

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
  <h1>Journal Scope Dashboard</h1>
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
      <h2>Out-of-scope % by Year</h2>
      <div id="barOOSYear" class="plot tall"></div>
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
    Each bubble = community centroid. <span style="color: var(--green);">Green = in-scope (primary clusters)</span>, 
    <span style="color: var(--red);">Red = out-of-scope</span>. Size = paper count.
  </p>
  <div id="scatterGrid" class="grid"></div>
</div>

<footer>
  <div style="margin-bottom: 8px;">
    <span id="ftYears"></span> · <span id="ftCov"></span>% primary coverage · 
    <span id="ftJournals"></span> journals · <span id="ftPapers"></span> papers · 
    <span id="ftComms"></span> communities
  </div>
  <div id="ftSource" style="color: #8899a6; font-size: 0.75rem;"></div>
</footer>

<script>
const DATA = __DATA_JSON__;
__RENDER_SCRIPT__
</script>
</body>
</html>
"""


def build_scope_dashboard(df: pd.DataFrame, df_cit: pd.DataFrame, run_metadata: dict = None) -> None:
    """Build scope_dashboard.html"""
    log.info("=" * 60)
    log.info("Building Scope Dashboard")
    log.info("=" * 60)

    log.info("[1/4] Computing scatter positions …")
    positions = compute_scatter_positions(df, df_cit)
    log.info(f"       Positioned {len(positions):,} papers")

    log.info("[2/4] Computing journal statistics …")
    journals = compute_journal_stats(df, positions)
    for j in journals:
        log.info(f"       {j['name']}: {j['articles']:,} papers, {j['out_of_scope_pct']:.1f}% OOS")

    log.info("[3/4] Computing community statistics …")
    communities = compute_community_stats_scope(df)

    years = sorted(df["pub_year"].unique())
    data = {
        "meta": {
            "year_range": [int(years[0]), int(years[-1])] if years else [],
            "primary_cluster_coverage": PRIMARY_COVERAGE,
            "primary_cluster_level": CLUSTER_LEVEL,
            "oos_per_year_years": [int(y) for y in years],
        },
        "run_metadata": run_metadata or {},
        "journals": journals,
        "communities": communities,
    }

    log.info("[4/4] Writing HTML …")
    if RENDER_SCRIPT_PATH.exists():
        render_script = RENDER_SCRIPT_PATH.read_text(encoding="utf-8")
    else:
        log.error(f"       render_script.js not found at {RENDER_SCRIPT_PATH}")
        return

    data_json = json.dumps(data, separators=(",", ":"))
    html = SCOPE_HTML_TEMPLATE.replace("__DATA_JSON__", data_json)
    html = html.replace("__RENDER_SCRIPT__", render_script)

    output_path = OUTPUT_DIR / "scope_dashboard.html"
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    output_path.write_text(html, encoding="utf-8")

    log.info(f"       Written to {output_path}")
    log.info(f"       File size: {output_path.stat().st_size / 1024:.1f} KB")


# ══════════════════════════════════════════════════════════════════════════════
# DRIFT DASHBOARD
# ══════════════════════════════════════════════════════════════════════════════
def get_cluster_distribution(df: pd.DataFrame) -> pd.Series:
    """Get normalized distribution over clusters."""
    counts = df[CLUSTER_LEVEL].value_counts()
    return counts / counts.sum()


def compute_jsd(dist1: pd.Series, dist2: pd.Series) -> float:
    """Compute Jensen-Shannon divergence between two distributions."""
    all_clusters = set(dist1.index) | set(dist2.index)
    v1 = np.array([dist1.get(c, 0) for c in all_clusters])
    v2 = np.array([dist2.get(c, 0) for c in all_clusters])
    return float(jensenshannon(v1, v2))


def compute_entropy_val(dist: pd.Series) -> float:
    """Compute Shannon entropy of a distribution."""
    return float(entropy(dist.values, base=2))


def compute_new_community_fraction(current_dist: pd.Series, baseline_clusters: set) -> float:
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
    years = [int(y) for y in sorted(df["pub_year"].unique())]

    available_baseline = [int(y) for y in BASELINE_YEARS if y in years]
    if not available_baseline:
        available_baseline = years[:3]

    log.info(f"       Baseline years: {available_baseline}")

    jsd_trends = {}
    summary = []
    heatmap = []

    for journal in JOURNALS:
        jdf = df[df["journal"] == journal]
        if jdf.empty:
            continue

        baseline_df = jdf[jdf["pub_year"].isin(available_baseline)]
        if len(baseline_df) < MIN_PAPERS_PER_YEAR:
            continue

        baseline_dist = get_cluster_distribution(baseline_df)
        baseline_clusters = set(baseline_dist.index)
        baseline_entropy = compute_entropy_val(baseline_dist)

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
            year_entropy = compute_entropy_val(year_dist)
            entropy_delta = year_entropy - baseline_entropy

            yearly_years.append(int(year))
            yearly_jsd.append(round(jsd, 4))
            yearly_new_comm.append(round(new_comm * 100, 2))
            yearly_entropy_delta.append(round(entropy_delta, 4))
            yearly_articles.append(int(len(ydf)))

            heatmap.append({"Journal": journal, "Year": int(year), "JSD": round(jsd, 4)})

        if not yearly_years:
            continue

        jsd_trends[journal] = {
            "years": yearly_years,
            "jsd": yearly_jsd,
            "new_comm": yearly_new_comm,
            "entropy_delta": yearly_entropy_delta,
            "articles": yearly_articles,
        }

        latest_year = max(yearly_years)
        latest_idx = yearly_years.index(latest_year)
        latest_df = jdf[jdf["pub_year"] == latest_year]
        latest_dist = get_cluster_distribution(latest_df)

        summary.append({
            "Journal": journal,
            "Year": latest_year,
            "JSD": yearly_jsd[latest_idx],
            "NewCommunityFrac": round(yearly_new_comm[latest_idx] / 100, 4),
            "Top5Jaccard": round(compute_top5_jaccard(baseline_dist, latest_dist), 4),
            "Entropy": round(compute_entropy_val(latest_dist), 4),
            "EntropyDelta": yearly_entropy_delta[latest_idx],
            "ArticleCount": yearly_articles[latest_idx],
        })

        log.info(f"       {journal}: JSD={yearly_jsd[-1]:.3f}")

    summary.sort(key=lambda x: x["JSD"], reverse=True)

    return {
        "jsd_trends": jsd_trends,
        "summary": summary,
        "heatmap": heatmap,
        "baseline_years": available_baseline,
        "all_years": years,
    }


def compute_community_stats_drift(df: pd.DataFrame) -> list:
    """Compute statistics for top communities (drift dashboard version)."""
    communities = []
    cluster_counts = df.groupby(CLUSTER_LEVEL).size().sort_values(ascending=False)

    for cluster_id in cluster_counts.head(30).index:
        cdf = df[df[CLUSTER_LEVEL] == cluster_id]
        size = len(cdf)

        journal_counts = cdf["journal"].value_counts()
        journal_pcts = (journal_counts / size * 100).round(1)

        journals_dict = {}
        for j in journal_pcts.head(5).index:
            journals_dict[j] = float(journal_pcts[j])

        label = GPT_LABELS.get(int(cluster_id), f"Cluster {cluster_id}")
        communities.append({
            "id": int(cluster_id),
            "label": label,
            "size": int(size),
            "journals": journals_dict,
            "dominant": journal_counts.index[0] if len(journal_counts) > 0 else "",
        })

    return communities


def build_drift_dashboard(df: pd.DataFrame, run_metadata: dict = None) -> None:
    """Build drift_dashboard.html"""
    log.info("=" * 60)
    log.info("Building Drift Dashboard")
    log.info("=" * 60)

    log.info("[1/3] Computing drift metrics …")
    metrics = compute_drift_metrics(df)

    log.info("[2/3] Computing community statistics …")
    communities = compute_community_stats_drift(df)

    log.info("[3/3] Building HTML …")
    heatmap_journals = sorted(set(h["Journal"] for h in metrics["heatmap"]))
    heatmap_years = [int(y) for y in sorted(set(h["Year"] for h in metrics["heatmap"]))]
    latest_year = int(max(heatmap_years)) if heatmap_years else 0

    data = {
        "run_metadata": run_metadata or {},
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
            "n_edges": 0,
            "year_range": f"{min(heatmap_years)}–{max(heatmap_years)}" if heatmap_years else "",
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

<div class="foot">
  <div>Data: CWTS clustering · Leiden algorithm · {CLUSTER_LEVEL} level</div>
</div>

<script>
const D={json.dumps(data)};
const COLORS=['#4338ca','#dc2626','#d97706','#059669','#0891b2','#7c3aed','#db2777','#ea580c',
              '#16a34a','#2563eb','#9333ea','#c026d3','#0d9488','#ca8a04','#64748b'];

document.getElementById('meta-badge').textContent=
  `Leiden · {CLUSTER_LEVEL} · ${{D.stats.n_nodes.toLocaleString()}} papers · ${{D.stats.year_range}}`;
document.getElementById('latest-yr').textContent=D.latest_year;
document.getElementById('bl-yrs').textContent=D.baseline_years.join('–');

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

    output_path = OUTPUT_DIR / "drift_dashboard.html"
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    output_path.write_text(html, encoding="utf-8")

    log.info(f"       Written to {output_path}")
    log.info(f"       File size: {output_path.stat().st_size / 1024:.1f} KB")


# ══════════════════════════════════════════════════════════════════════════════
# CLUSTERS DASHBOARD
# ══════════════════════════════════════════════════════════════════════════════
def build_cluster_profiles(df: pd.DataFrame) -> dict:
    """Build cluster profiles for each level."""
    profiles = {"macro": [], "meso": [], "micro": []}

    for level in ["macro", "meso", "micro"]:
        cluster_counts = df.groupby(level).size().sort_values(ascending=False)
        max_clusters = MAX_COMMUNITIES[level]

        for cluster_id in cluster_counts.head(max_clusters).index:
            cdf = df[df[level] == cluster_id]
            size = len(cdf)

            journal_counts = cdf["journal"].value_counts()
            dominant = journal_counts.index[0] if len(journal_counts) > 0 else "Unknown"
            dominant_pct = round(journal_counts.iloc[0] / size * 100, 1) if len(journal_counts) > 0 else 0

            journals_dict = {}
            for j, c in journal_counts.items():
                journals_dict[j.replace("Frontiers in ", "")] = round(c / size * 100, 1)

            year_counts = cdf["pub_year"].value_counts().sort_index()
            years_dict = {int(y): int(c) for y, c in year_counts.items()}

            label_info = GPT_LABELS_ALL[level].get(int(cluster_id), {})
            label = label_info.get("short_label", f"Cluster {cluster_id}")
            keywords = label_info.get("keywords", [])

            profile = {
                "id": int(cluster_id),
                "label": label,
                "size": size,
                "dominant": dominant.replace("Frontiers in ", ""),
                "dominant_pct": dominant_pct,
                "journals": journals_dict,
                "years": years_dict,
                "fos": keywords[:5] if keywords else [],
                "fos_specific": keywords[5:10] if len(keywords) > 5 else [],
            }

            if level == "meso":
                macro_counts = cdf["macro"].value_counts()
                if len(macro_counts) > 0:
                    profile["parent_macro"] = int(macro_counts.index[0])
            elif level == "micro":
                meso_counts = cdf["meso"].value_counts()
                if len(meso_counts) > 0:
                    profile["parent_meso"] = int(meso_counts.index[0])

            profiles[level].append(profile)

    return profiles


def build_fos_global(df: pd.DataFrame) -> dict:
    """Build global field of study distribution from labels."""
    fos_global = {"macro": {}, "meso": {}, "micro": {}}

    for level in ["macro", "meso", "micro"]:
        keyword_counts = Counter()
        cluster_counts = df.groupby(level).size()

        for cluster_id, size in cluster_counts.items():
            label_info = GPT_LABELS_ALL[level].get(int(cluster_id), {})
            keywords = label_info.get("keywords", [])
            for kw in keywords[:3]:
                keyword_counts[kw] += size

        fos_global[level] = dict(keyword_counts.most_common(30))

    return fos_global


CLUSTERS_HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Frontiers Citation Cluster Hierarchy</title>
<script src="https://cdn.plot.ly/plotly-2.35.2.min.js"></script>
<style>
:root{--bg:#f8fafc;--card:#fff;--bdr:#e2e8f0;--tx:#0f172a;--tx2:#64748b;--blue:#3b82f6;--pink:#ec4899;--amber:#f59e0b;--green:#10b981;--indigo:#6366f1}
*{box-sizing:border-box;margin:0;padding:0}
body{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif;background:var(--bg);color:var(--tx);padding:16px 20px;max-width:1400px;margin:0 auto}
.hdr{text-align:center;margin-bottom:20px}
.hdr h1{font-size:22px;font-weight:700}.hdr p{font-size:13px;color:var(--tx2);margin-top:2px}
.pills{display:flex;justify-content:center;gap:8px;margin-top:10px;flex-wrap:wrap}
.pill{padding:4px 12px;border-radius:12px;font-size:11px;font-weight:600}
.pill-ma{background:#dbeafe;color:#1e40af}.pill-me{background:#fce7f3;color:#9d174d}
.pill-mi{background:#d1fae5;color:#065f46}.pill-g{background:#f1f5f9;color:#475569}
.kpis{display:flex;gap:10px;margin-bottom:16px;flex-wrap:wrap}
.kpi{background:var(--card);border-radius:10px;padding:10px 14px;box-shadow:0 1px 2px rgba(0,0,0,.06);flex:1;min-width:120px}
.kpi .l{font-size:10px;color:#94a3b8;text-transform:uppercase;letter-spacing:.5px}
.kpi .v{font-size:22px;font-weight:700;margin-top:1px}.kpi .d{font-size:11px;color:var(--tx2)}
.tabs{display:flex;gap:4px;margin-bottom:14px;flex-wrap:wrap}
.tab{padding:8px 16px;border:none;background:#e2e8f0;border-radius:6px;cursor:pointer;font-size:13px;font-weight:500}
.tab.on{background:var(--blue);color:#fff}
.pan{display:none}.pan.on{display:block}
.row{display:grid;gap:14px}.r1{grid-template-columns:1fr}.r2{grid-template-columns:340px 1fr}.r3{grid-template-columns:repeat(3,1fr)}
@media(max-width:900px){.r2,.r3{grid-template-columns:1fr}}
.card{background:var(--card);border-radius:10px;padding:14px;box-shadow:0 1px 2px rgba(0,0,0,.06)}
.card h3{font-size:14px;font-weight:600}.card .sub{font-size:11px;color:#94a3b8;margin-bottom:10px}
.cl{max-height:500px;overflow-y:auto}
.ci{padding:10px;border-radius:6px;cursor:pointer;margin-bottom:6px;border:1px solid var(--bdr)}
.ci:hover{background:#f8fafc}.ci.sel{background:#eff6ff;border-color:var(--blue)}
.ci-h{display:flex;justify-content:space-between;align-items:center}
.ci-n{font-weight:600;font-size:13px}.ci-s{font-size:12px;color:var(--tx2)}
.ci-f{font-size:11px;color:var(--tx2);margin-top:4px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.ci-j{margin-top:4px;display:flex;gap:4px;flex-wrap:wrap}
.ci-j span{font-size:10px;padding:2px 6px;border-radius:4px}
.det{min-height:400px}
.dt{font-size:16px;font-weight:700;margin-bottom:4px}
.dm{font-size:12px;color:var(--tx2);margin-bottom:12px}
.ds{margin-bottom:12px}.ds h4{font-size:12px;font-weight:600;margin-bottom:6px;color:var(--tx2)}
.br{display:flex;align-items:center;margin-bottom:4px}
.bl{width:100px;font-size:11px;flex-shrink:0}.bt{flex:1;background:#f1f5f9;border-radius:3px;height:18px}
.bf{height:100%;border-radius:3px;font-size:10px;color:#fff;padding:0 6px;display:flex;align-items:center}
.chi{display:flex;justify-content:space-between;font-size:12px;padding:4px 0;border-bottom:1px solid #f1f5f9}
.cn{color:var(--tx)}.cs{color:var(--tx2)}
.sb{height:500px}.tree{max-height:600px;overflow-y:auto;font-size:13px;line-height:1.6}
.ma{margin-bottom:16px;padding-left:8px;border-left:3px solid var(--blue)}
.me{margin-left:20px;margin-top:6px;padding-left:8px;border-left:2px solid var(--pink)}
.mi{margin-left:20px;font-size:12px;color:var(--tx2)}
.j-im{background:#dbeafe;color:#1e40af}.j-ps{background:#fce7f3;color:#9d174d}
.j-on{background:#fef3c7;color:#92400e}.j-ph{background:#d1fae5;color:#065f46}
.j-pu{background:#e0e7ff;color:#3730a3}.j-o{background:#f1f5f9;color:#475569}
.foot{text-align:center;margin-top:24px;font-size:11px;color:#94a3b8}
</style>
</head>
<body>

<div class="hdr">
<h1>Frontiers Citation Cluster Hierarchy</h1>
<p>CWTS Leiden clustering on citation network</p>
<div class="pills">
<span class="pill pill-ma" id="pill-ma"></span>
<span class="pill pill-me" id="pill-me"></span>
<span class="pill pill-mi" id="pill-mi"></span>
<span class="pill pill-g" id="pill-g"></span>
</div>
</div>

<div class="kpis" id="kpis"></div>

<div class="tabs" id="tabs">
<button class="tab on" data-t="macro">Macro</button>
<button class="tab" data-t="meso">Meso</button>
<button class="tab" data-t="micro">Micro</button>
<button class="tab" data-t="hier">Hierarchy</button>
<button class="tab" data-t="fos">Keywords</button>
</div>

<!-- MACRO -->
<div id="pan-macro" class="pan on">
<div class="row r2"><div class="card"><h3>Macro Clusters</h3><div class="sub">Broad domains · CWTS Leiden</div><div class="cl" id="ma-list"></div></div>
<div class="card det" id="ma-det"><div style="color:#94a3b8;text-align:center;padding-top:120px">← Select a cluster</div></div></div>
<div class="row r1" style="margin-top:14px"><div class="card"><h3>Macro Size Distribution</h3><div class="sub">Articles per cluster, coloured by dominant journal</div><div id="ma-chart" style="height:300px"></div></div></div>
</div>

<!-- MESO -->
<div id="pan-meso" class="pan">
<div class="row r2"><div class="card"><h3>Meso Clusters</h3><div class="sub">Thematic areas · CWTS Leiden</div><div class="cl" id="me-list"></div></div>
<div class="card det" id="me-det"><div style="color:#94a3b8;text-align:center;padding-top:120px">← Select a cluster</div></div></div>
<div class="row r1" style="margin-top:14px"><div class="card"><h3>Meso Size Distribution</h3><div class="sub">Top clusters</div><div id="me-chart" style="height:300px"></div></div></div>
</div>

<!-- MICRO -->
<div id="pan-micro" class="pan">
<div class="row r2"><div class="card"><h3>Micro Clusters</h3><div class="sub">Fine-grained topics · CWTS Leiden</div><div class="cl" id="mi-list"></div></div>
<div class="card det" id="mi-det"><div style="color:#94a3b8;text-align:center;padding-top:120px">← Select a cluster</div></div></div>
<div class="row r1" style="margin-top:14px"><div class="card"><h3>Micro Size Distribution</h3><div class="sub">Top clusters</div><div id="mi-chart" style="height:300px"></div></div></div>
</div>

<!-- HIERARCHY -->
<div id="pan-hier" class="pan">
<div class="row r1"><div class="card"><h3>Sunburst — Macro → Meso → Micro</h3><div class="sub">Click to drill down</div><div class="sb" id="sunburst"></div></div></div>
<div class="row r1" style="margin-top:14px"><div class="card"><h3>Hierarchy Tree</h3><div class="sub">Full nesting</div><div class="tree" id="tree"></div></div></div>
</div>

<!-- KEYWORDS -->
<div id="pan-fos" class="pan">
<div class="row r3">
<div class="card"><h3>Macro Keywords</h3><div class="sub">Top keywords from GPT labels</div><div id="fos0" style="height:460px"></div></div>
<div class="card"><h3>Meso Keywords</h3><div class="sub">Top 30</div><div id="fos1" style="height:460px"></div></div>
<div class="card"><h3>Micro Keywords</h3><div class="sub">Top 30</div><div id="fos2" style="height:460px"></div></div>
</div>
</div>

<div class="foot">Data: Local CWTS output · Leiden algorithm · GPT labels</div>

<script>
const D=/*DATA_PLACEHOLDER*/null;
const JC={}; D.journals.forEach((j,i)=>{
  const cols=['#3b82f6','#ec4899','#f59e0b','#10b981','#6366f1','#8b5cf6','#ef4444','#0ea5e9','#d946ef','#f97316','#14b8a6','#a855f7','#64748b','#06b6d4','#84cc16'];
  JC[j]=cols[i%cols.length];
});
function jc(j){return JC[j]||'#94a3b8'}
const JCL={};D.journals.forEach((j,i)=>{
  const cls=['j-im','j-ps','j-on','j-ph','j-pu','j-o','j-o','j-o','j-o','j-o'];
  JCL[j]=cls[i%cls.length];
});
function jcl(j){return JCL[j]||'j-o'}

document.getElementById('pill-ma').textContent=D.stats.n_macro+' Macro';
document.getElementById('pill-me').textContent=D.stats.n_meso+' Meso';
document.getElementById('pill-mi').textContent=D.stats.n_micro+' Micro';
document.getElementById('pill-g').textContent=D.stats.nodes.toLocaleString()+' nodes · '+D.stats.edges.toLocaleString()+' edges · '+D.stats.years;

document.getElementById('kpis').innerHTML=`
<div class="kpi"><div class="l">Macro</div><div class="v" style="color:#1d4ed8">${D.stats.n_macro}</div><div class="d">Broad domains</div></div>
<div class="kpi"><div class="l">Meso</div><div class="v" style="color:#be185d">${D.stats.n_meso}</div><div class="d">Thematic areas</div></div>
<div class="kpi"><div class="l">Micro</div><div class="v" style="color:#065f46">${D.stats.n_micro}</div><div class="d">Research topics</div></div>
<div class="kpi"><div class="l">Journals</div><div class="v">${D.journals.length}</div><div class="d">${D.journals.join(', ')}</div></div>
<div class="kpi"><div class="l">Citation Edges</div><div class="v">${D.stats.edges.toLocaleString()}</div><div class="d">Article-to-article</div></div>`;

document.getElementById('tabs').addEventListener('click',e=>{
  if(!e.target.dataset.t)return;
  document.querySelectorAll('.tab').forEach(t=>t.classList.remove('on'));
  document.querySelectorAll('.pan').forEach(p=>p.classList.remove('on'));
  e.target.classList.add('on');
  document.getElementById('pan-'+e.target.dataset.t).classList.add('on');
});

function rList(data,elId,detId,level,childLevel){
  const el=document.getElementById(elId);
  let h='';
  data.forEach((c,i)=>{
    const fos=(c.fos||[]).join(' · ');
    const jt=Object.entries(c.journals||{}).slice(0,4).map(([j,p])=>
      `<span class="${jcl(j)}">${j} ${p}%</span>`).join('');
    h+=`<div class="ci" data-i="${i}" onclick="showDet('${level}',${i},'${detId}','${childLevel}')">
      <div class="ci-h"><span class="ci-n">C${c.id} — ${c.label}</span><span class="ci-s">${c.size.toLocaleString()}</span></div>
      <div class="ci-f">${fos}</div><div class="ci-j">${jt}</div></div>`;
  });
  el.innerHTML=h;
}

function showDet(level,idx,detId,childLevel){
  const data={macro:D.macro,meso:D.meso,micro:D.micro}[level];
  const c=data[idx];
  const el=document.getElementById(detId);
  const entries=Object.entries(c.journals||{}).sort((a,b)=>b[1]-a[1]);
  const mx=entries.length?entries[0][1]:100;
  const bars=entries.map(([j,p])=>`<div class="br"><div class="bl">${j}</div>
    <div class="bt"><div class="bf" style="width:${p/mx*100}%;background:${jc(j)}">${p}%</div></div></div>`).join('');
  const fosH=(c.fos||[]).map(f=>`<span class="pill pill-me">${f}</span>`).join(' ');
  const fosS=(c.fos_specific||[]).map(f=>`<span class="pill pill-mi">${f}</span>`).join(' ');
  let chH='';
  if(childLevel&&childLevel!=='null'){
    const cData={macro:D.meso,meso:D.micro}[level]||[];
    const pKey={macro:'parent_macro',meso:'parent_meso'}[level];
    if(pKey){
      const kids=cData.filter(m=>m[pKey]===c.id).sort((a,b)=>b.size-a.size).slice(0,12);
      if(kids.length) chH=`<div class="ds"><h4>${childLevel} Children (${kids.length})</h4>`+
        kids.map(k=>`<div class="chi"><span class="cn">C${k.id} — ${k.label}</span><span class="cs">${k.size.toLocaleString()}</span></div>`).join('')+'</div>';
    }
  }
  const yrs=Object.keys(c.years||{}).sort();
  const yvals=yrs.map(y=>c.years[y]);
  el.innerHTML=`<div class="dt">C${c.id} — ${c.label}</div>
    <div class="dm">${c.size.toLocaleString()} articles · ${c.dominant} (${c.dominant_pct}%)</div>
    <div class="ds"><h4>Keywords</h4>${fosH} ${fosS}</div>
    <div class="ds"><h4>Journal Mix</h4>${bars}</div>${chH}
    <div class="ds"><h4>Year Distribution</h4><div id="yc-${level}" style="height:140px"></div></div>`;
  if(yrs.length)Plotly.newPlot('yc-'+level,[{x:yrs,y:yvals,type:'bar',marker:{color:jc(c.dominant)}}],
    {template:'plotly_white',margin:{l:35,r:10,t:5,b:25},xaxis:{dtick:1},autosize:true},{responsive:true});
  el.closest('.r2').querySelector('.cl').querySelectorAll('.ci').forEach(ci=>ci.classList.toggle('sel',+ci.dataset.i===idx));
}

rList(D.macro,'ma-list','ma-det','macro','meso');
rList(D.meso,'me-list','me-det','meso','micro');
rList(D.micro,'mi-list','mi-det','micro','null');

function sChart(data,id,n){
  const d=data.slice(0,n||50);
  Plotly.newPlot(id,[{x:d.map(c=>'C'+c.id),y:d.map(c=>c.size),type:'bar',
    marker:{color:d.map(c=>jc(c.dominant))},text:d.map(c=>c.label),
    hovertemplate:'%{x}<br>%{y} articles<br>%{text}<extra></extra>'}],
    {template:'plotly_white',autosize:true,margin:{l:45,r:15,t:5,b:50},
     xaxis:{tickangle:-45,tickfont:{size:9}},yaxis:{title:'Articles'}},{responsive:true});
}
sChart(D.macro,'ma-chart',25);sChart(D.meso,'me-chart',50);sChart(D.micro,'mi-chart',50);

(function(){
  const ids=[],labels=[],parents=[],values=[],colors=[];
  D.macro.forEach(m=>{ids.push('MA'+m.id);labels.push(m.label);parents.push('');values.push(m.size);colors.push(jc(m.dominant))});
  D.meso.forEach(m=>{if(D.macro.find(ma=>ma.id===m.parent_macro)){
    ids.push('ME'+m.id);labels.push(m.label);
    parents.push('MA'+m.parent_macro);values.push(m.size);colors.push(jc(m.dominant))}});
  D.micro.forEach(m=>{if(D.meso.find(me=>me.id===m.parent_meso)){
    ids.push('MI'+m.id);labels.push(m.label);parents.push('ME'+m.parent_meso);
    values.push(m.size);colors.push(jc(m.dominant))}});
  Plotly.newPlot('sunburst',[{type:'sunburst',ids,labels,parents,values,
    marker:{colors},branchvalues:'total',maxdepth:2,
    hovertemplate:'<b>%{label}</b><br>%{value} articles<extra></extra>',
    textinfo:'label',insidetextorientation:'radial'}],
    {template:'plotly_white',margin:{l:5,r:5,t:5,b:5},autosize:true,font:{size:11}},{responsive:true});
})();

(function(){
  let h='';
  D.macro.slice(0,15).forEach(ma=>{
    const meK=D.meso.filter(m=>m.parent_macro===ma.id).sort((a,b)=>b.size-a.size).slice(0,6);
    let mh='';
    meK.forEach(me=>{
      const miK=D.micro.filter(m=>m.parent_meso===me.id).sort((a,b)=>b.size-a.size).slice(0,4);
      const mih=miK.map(mi=>`<div class="mi">⬡ <strong>C${mi.id}</strong> ${mi.label} <span style="color:#94a3b8">(${mi.size})</span></div>`).join('');
      mh+=`<div class="me">◆ <strong>C${me.id}</strong> ${me.label} <span style="color:#94a3b8">(${me.size} articles)</span>${mih}</div>`;
    });
    h+=`<div class="ma"><span style="color:${jc(ma.dominant)};font-size:16px">●</span>
      <strong style="font-size:14px">C${ma.id}</strong> ${ma.label}
      <span style="color:#94a3b8">(${ma.size.toLocaleString()} articles · ${ma.dominant} ${ma.dominant_pct}%)</span>${mh}</div>`;
  });
  document.getElementById('tree').innerHTML=h;
})();

function fChart(data,id){
  const e=Object.entries(data).sort((a,b)=>b[1]-a[1]).slice(0,25);
  Plotly.newPlot(id,[{y:e.map(x=>x[0]),x:e.map(x=>x[1]),type:'bar',orientation:'h',
    marker:{color:'#6366f1'},hovertemplate:'%{y}: %{x:,}<extra></extra>'}],
    {template:'plotly_white',autosize:true,margin:{l:140,r:15,t:5,b:35},
     yaxis:{autorange:'reversed',tickfont:{size:11}},xaxis:{title:'Articles'}},{responsive:true});
}
fChart(D.fos_global.macro,'fos0');fChart(D.fos_global.meso,'fos1');fChart(D.fos_global.micro,'fos2');

setTimeout(()=>{showDet('macro',0,'ma-det','meso')},100);
</script>
</body>
</html>"""


def build_clusters_dashboard(df: pd.DataFrame, n_edges: int) -> None:
    """Build clusters.html"""
    log.info("=" * 60)
    log.info("Building Clusters Dashboard")
    log.info("=" * 60)

    log.info("[1/3] Building cluster profiles …")
    profiles = build_cluster_profiles(df)
    for level in ["macro", "meso", "micro"]:
        log.info(f"       {level}: {len(profiles[level])} clusters")

    log.info("[2/3] Building keyword distributions …")
    fos_global = build_fos_global(df)

    years = sorted(df["pub_year"].unique())
    year_range = f"{min(years)}–{max(years)}" if years else ""
    journal_names = [j.replace("Frontiers in ", "") for j in JOURNALS]

    dashboard_data = {
        "macro": profiles["macro"],
        "meso": profiles["meso"],
        "micro": profiles["micro"],
        "fos_global": fos_global,
        "journals": journal_names,
        "stats": {
            "nodes": len(df),
            "edges": n_edges,
            "years": year_range,
            "n_macro": len(profiles["macro"]),
            "n_meso": len(profiles["meso"]),
            "n_micro": len(profiles["micro"]),
        },
    }

    log.info("[3/3] Writing HTML …")
    data_json = json.dumps(dashboard_data, default=str)
    html = CLUSTERS_HTML_TEMPLATE.replace(
        "const D=/*DATA_PLACEHOLDER*/null;", f"const D={data_json};"
    )

    output_path = OUTPUT_DIR / "clusters.html"
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    output_path.write_text(html, encoding="utf-8")

    log.info(f"       Written to {output_path}")
    log.info(f"       File size: {output_path.stat().st_size / 1024:.1f} KB")


# ══════════════════════════════════════════════════════════════════════════════
# COMBINE DASHBOARDS
# ══════════════════════════════════════════════════════════════════════════════
COMBINE_HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Scope Drift Analysis Dashboard</title>
<style>
:root {
  --bg: #f6f8fa;
  --card: #ffffff;
  --text: #1a1f36;
  --muted: #5f6b7c;
  --border: #e3e7ee;
  --blue: #2c5fa3;
  --blue-light: #e8f0fe;
}
* { box-sizing: border-box; margin: 0; padding: 0; }
html, body { height: 100%; overflow: hidden; }
body {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  background: var(--bg);
  color: var(--text);
  display: flex;
  flex-direction: column;
}
.header {
  background: var(--card);
  padding: 16px 24px;
  border-bottom: 1px solid var(--border);
  display: flex;
  align-items: center;
  justify-content: space-between;
  flex-shrink: 0;
}
.header h1 { font-size: 1.3rem; font-weight: 700; }
.header .meta { color: var(--muted); font-size: 0.85rem; }
.tab-nav {
  display: flex;
  gap: 0;
  background: var(--card);
  border-bottom: 1px solid var(--border);
  padding: 0 24px;
  flex-shrink: 0;
}
.tab-btn {
  padding: 14px 24px;
  border: none;
  background: transparent;
  color: var(--muted);
  cursor: pointer;
  font-size: 0.95rem;
  font-weight: 500;
  border-bottom: 3px solid transparent;
  transition: all 0.2s;
}
.tab-btn:hover { color: var(--text); background: var(--bg); }
.tab-btn.active { color: var(--blue); border-bottom-color: var(--blue); background: var(--blue-light); }
.tab-content { flex: 1; display: none; overflow: hidden; }
.tab-content.active { display: block; }
.tab-content iframe { width: 100%; height: 100%; border: none; }
</style>
</head>
<body>
<div class="header">
  <h1>Scope Drift Analysis</h1>
  <div class="meta">__META_INFO__</div>
</div>
<nav class="tab-nav">
__TAB_BUTTONS__
</nav>
__TAB_CONTENTS__
<script>
document.querySelectorAll('.tab-btn').forEach(btn => {
  btn.addEventListener('click', () => {
    document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
    btn.classList.add('active');
    const tabId = btn.dataset.tab;
    document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));
    document.getElementById('tab-' + tabId).classList.add('active');
  });
});
document.querySelectorAll('.tab-btn').forEach(btn => {
  btn.addEventListener('click', () => {
    const tabId = btn.dataset.tab;
    const iframe = document.querySelector('#tab-' + tabId + ' iframe');
    if (iframe && !iframe.src && iframe.dataset.src) {
      iframe.src = iframe.dataset.src;
    }
  });
});
const firstIframe = document.querySelector('.tab-content.active iframe');
if (firstIframe && firstIframe.dataset.src) {
  firstIframe.src = firstIframe.dataset.src;
}
</script>
</body>
</html>
"""


def combine_dashboards() -> None:
    """Combine all dashboards into a single tabbed HTML file."""
    log.info("=" * 60)
    log.info("Combining Dashboards")
    log.info("=" * 60)

    dashboards = [
        ("scope_dashboard", "Scope Analysis"),
        ("drift_dashboard", "Drift Analysis"),
        ("clusters", "Cluster Map"),
    ]

    existing = []
    for filename, label in dashboards:
        path = OUTPUT_DIR / f"{filename}.html"
        if path.exists():
            existing.append((filename, label, path))
            log.info(f"    [OK] {filename}.html")
        else:
            log.info(f"    [--] {filename}.html (not found)")

    if not existing:
        log.warning("No dashboards found to combine!")
        return

    tab_buttons = []
    for i, (filename, label, _) in enumerate(existing):
        active = "active" if i == 0 else ""
        tab_buttons.append(
            f'  <button class="tab-btn {active}" data-tab="{filename}">{label}</button>'
        )

    tab_contents = []
    for i, (filename, label, path) in enumerate(existing):
        active = "active" if i == 0 else ""
        relative_path = f"{filename}.html"
        tab_contents.append(f'''
<div id="tab-{filename}" class="tab-content {active}">
  <iframe data-src="{relative_path}" title="{label}"></iframe>
</div>''')

    meta_parts = []
    if RUN_TIMESTAMP:
        meta_parts.append(f"Run: {RUN_TIMESTAMP}")
    meta_parts.append(f"Generated: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}")
    meta_parts.append(f"{len(existing)} dashboards")
    meta_info = " · ".join(meta_parts)

    html = COMBINE_HTML_TEMPLATE
    html = html.replace("__TAB_BUTTONS__", "\n".join(tab_buttons))
    html = html.replace("__TAB_CONTENTS__", "\n".join(tab_contents))
    html = html.replace("__META_INFO__", meta_info)

    output_path = OUTPUT_DIR / "combined_dashboard.html"
    output_path.write_text(html, encoding="utf-8")

    log.info(f"       Written to {output_path}")
    log.info(f"       File size: {output_path.stat().st_size / 1024:.1f} KB")


# ══════════════════════════════════════════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════════════════════════════════════════
def main():
    global GPT_LABELS, GPT_LABELS_ALL

    log.info("=" * 60)
    log.info("Unified Dashboard Builder (BigQuery)")
    log.info("=" * 60)

    if not RUN_TIMESTAMP:
        log.error("RUN_TIMESTAMP environment variable is required!")
        log.error("Example: RUN_TIMESTAMP=20260714_151745")
        return

    log.info(f"RUN_TIMESTAMP: {RUN_TIMESTAMP}")
    log.info(f"Cluster level: {CLUSTER_LEVEL}")
    log.info(f"Output dir: {OUTPUT_DIR}")

    # Load data from BigQuery
    log.info("\n[LOAD] Loading data from BigQuery …")
    df = load_merged_data()
    log.info(f"       {len(df):,} papers")
    log.info(f"       Journals: {df['journal'].nunique()}")
    log.info(f"       Years: {df['pub_year'].min()}–{df['pub_year'].max()}")

    log.info("\n[LOAD] Loading citations from BigQuery …")
    df_cit = load_citations()

    # Load run metadata
    run_metadata = load_run_metadata()

    # Load GPT labels (from local files)
    log.info("\n[LOAD] Loading GPT labels …")
    GPT_LABELS = load_gpt_labels_single(CLUSTER_LEVEL)
    log.info(f"       {len(GPT_LABELS)} labels for {CLUSTER_LEVEL} level")
    GPT_LABELS_ALL = load_gpt_labels_all()

    # Build all dashboards
    print()
    build_scope_dashboard(df, df_cit, run_metadata)
    print()
    build_drift_dashboard(df, run_metadata)
    print()
    build_clusters_dashboard(df, len(df_cit))

    # Combine dashboards
    print()
    combine_dashboards()

    log.info("\n" + "=" * 60)
    log.info("Done!")
    log.info("=" * 60)


if __name__ == "__main__":
    main()
