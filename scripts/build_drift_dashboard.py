"""
build_drift_dashboard.py
=========================
Pulls citation data from AIRAK BigQuery, runs Leiden community detection,
computes scope-drift metrics per journal against a historical baseline,
and writes an interactive HTML dashboard.

Data source : ocean-breeze-tier-1.airak
Algorithm   : Leiden (Traag et al., 2019) — Modularity partition
Output      : drift_dashboard.html

Requirements:
    pip install leidenalg python-igraph google-cloud-bigquery pandas scipy

Usage:
    export GOOGLE_APPLICATION_CREDENTIALS=/path/to/credentials.json
    python build_drift_dashboard.py
"""

import os
import gc
import json
import random
import logging
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.spatial.distance import jensenshannon
from scipy.stats import entropy as sp_entropy
import igraph as ig
import leidenalg
from google.cloud import bigquery

# ──────────────────────────────────────────────────────────────────────────────
# CONFIG
# ──────────────────────────────────────────────────────────────────────────────
BQ_PROJECT = "ocean-breeze-tier-1"
AIRAK = "ocean-breeze-tier-1.airak"
FRONTIERS_PUBLISHER_ID = 1563368095744

TOP_N_JOURNALS = 15  # journals to include in the citation graph
YEAR_START = 2018  # earliest year in the graph
YEAR_END = 2025  # latest year
BASELINE_YEARS = [2018, 2019, 2020]  # years that define "normal" scope
TARGET_YEARS = [2021, 2022, 2023, 2024, 2025]  # years to measure drift

OUTPUT_PATH = Path(__file__).resolve().parent.parent / "output" / "drift_dashboard.html"

random.seed(42)
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s  %(message)s", datefmt="%H:%M:%S"
)
log = logging.getLogger(__name__)


# ──────────────────────────────────────────────────────────────────────────────
# STEP 1 — Top journals
# ──────────────────────────────────────────────────────────────────────────────
def get_top_journals(client):
    log.info(f"[1/6] Finding top {TOP_N_JOURNALS} Frontiers journals …")
    q = f"""
    SELECT j.JournalId, j.DisplayName, COUNT(*) AS pubs
    FROM `{AIRAK}.Publication` p
    JOIN `{AIRAK}.Journal` j ON p.JournalId = j.JournalId
    WHERE j.PublisherId = {FRONTIERS_PUBLISHER_ID}
      AND p.PublishedYear BETWEEN {YEAR_START} AND {YEAR_END}
    GROUP BY 1, 2
    ORDER BY 3 DESC
    LIMIT {TOP_N_JOURNALS}
    """
    df = client.query(q).to_dataframe()
    for _, r in df.iterrows():
        log.info(f"       {r['DisplayName']:<45} {r['pubs']:>6,}")
    return df


# ──────────────────────────────────────────────────────────────────────────────
# STEP 2 — Citation edges + node metadata
# ──────────────────────────────────────────────────────────────────────────────
def get_citation_data(client, journal_ids):
    ids = ",".join(str(x) for x in journal_ids)
    log.info("[2/6] Pulling citation edges …")
    q_edges = f"""
    WITH pubs AS (
      SELECT PublicationId
      FROM `{AIRAK}.Publication`
      WHERE JournalId IN ({ids})
        AND PublishedYear BETWEEN {YEAR_START} AND {YEAR_END}
    )
    SELECT pc.PublicationId AS src, pc.CitedPublicationId AS tgt
    FROM `{AIRAK}.PublicationCitation` pc
    WHERE pc.PublicationId    IN (SELECT PublicationId FROM pubs)
      AND pc.CitedPublicationId IN (SELECT PublicationId FROM pubs)
    """
    df_edges = client.query(q_edges).to_dataframe()
    log.info(f"       {len(df_edges):,} edges")

    log.info("       Pulling node metadata …")
    q_nodes = f"""
    SELECT p.PublicationId, p.PublishedYear,
           j.DisplayName AS JournalName
    FROM `{AIRAK}.Publication` p
    JOIN `{AIRAK}.Journal` j ON p.JournalId = j.JournalId
    WHERE j.JournalId IN ({ids})
      AND p.PublishedYear BETWEEN {YEAR_START} AND {YEAR_END}
    """
    df_nodes = client.query(q_nodes).to_dataframe()
    log.info(f"       {len(df_nodes):,} articles")

    meta = df_nodes.set_index("PublicationId").to_dict("index")
    del df_nodes
    gc.collect()
    return df_edges, meta


# ──────────────────────────────────────────────────────────────────────────────
# STEP 3 — Build graph + Leiden
# ──────────────────────────────────────────────────────────────────────────────
def build_graph_and_cluster(df_edges):
    log.info("[3/6] Building graph & running Leiden (modularity) …")
    node_ids = sorted(set(df_edges["src"]) | set(df_edges["tgt"]))
    id_map = {p: i for i, p in enumerate(node_ids)}
    n_edges = len(df_edges)

    edges = [
        (id_map[r["src"]], id_map[r["tgt"]])
        for _, r in df_edges.iterrows()
        if r["src"] in id_map and r["tgt"] in id_map
    ]
    del df_edges
    gc.collect()

    G = ig.Graph(n=len(node_ids), edges=edges, directed=False)
    G.simplify()
    log.info(f"       {G.vcount():,} nodes, {G.ecount():,} edges")

    partition = leidenalg.find_partition(
        G,
        leidenalg.ModularityVertexPartition,
        n_iterations=10,
        seed=42,
    )
    membership = partition.membership
    n_comms = len(set(membership))
    sizes = sorted(Counter(membership).values(), reverse=True)
    log.info(f"       {n_comms:,} communities, top 10 sizes: {sizes[:10]}")

    del G, edges
    gc.collect()
    return node_ids, membership, n_edges


# ──────────────────────────────────────────────────────────────────────────────
# STEP 4 — Community profiles + scope drift metrics
# ──────────────────────────────────────────────────────────────────────────────
def compute_drift(node_ids, membership, meta):
    log.info("[4/6] Computing scope drift metrics …")

    # Build per-journal, per-year community distribution
    journal_year_comm = {}
    for idx in range(len(membership)):
        pub_id = node_ids[idx]
        comm = membership[idx]
        m = meta.get(pub_id)
        if m and m["PublishedYear"] and YEAR_START <= m["PublishedYear"] <= YEAR_END:
            journal = m["JournalName"].replace("Frontiers in ", "")
            year = m["PublishedYear"]
            journal_year_comm.setdefault((journal, year), Counter())[comm] += 1

    # All community IDs for consistent vector length
    all_comms = sorted(set(membership))
    comm_idx = {c: i for i, c in enumerate(all_comms)}
    n_comms = len(all_comms)

    def dist_vec(counter):
        v = np.zeros(n_comms)
        total = sum(counter.values())
        for c, cnt in counter.items():
            v[comm_idx[c]] = cnt / total
        return v

    journals = sorted({j for j, _ in journal_year_comm.keys()})
    all_years = sorted({y for _, y in journal_year_comm.keys()})

    drift_rows = []
    for journal in journals:
        # Aggregate baseline
        baseline = Counter()
        for y in BASELINE_YEARS:
            if (journal, y) in journal_year_comm:
                baseline += journal_year_comm[(journal, y)]
        if not baseline:
            continue

        baseline_vec = dist_vec(baseline)
        baseline_entropy = float(sp_entropy(baseline_vec[baseline_vec > 0]))
        baseline_comms = set(c for c, cnt in baseline.items())

        for year in all_years:
            key = (journal, year)
            if key not in journal_year_comm:
                continue
            yc = journal_year_comm[key]
            total_year = sum(yc.values())

            year_vec = dist_vec(yc)
            year_entropy = float(sp_entropy(year_vec[year_vec > 0]))

            # JSD
            jsd = float(jensenshannon(baseline_vec, year_vec))

            # New community fraction
            new_articles = sum(cnt for c, cnt in yc.items() if c not in baseline_comms)
            new_frac = new_articles / total_year if total_year else 0

            # Top-5 Jaccard
            top5_b = set(c for c, _ in baseline.most_common(5))
            top5_y = set(c for c, _ in yc.most_common(5))
            jaccard = (
                len(top5_b & top5_y) / len(top5_b | top5_y) if top5_b | top5_y else 0
            )

            drift_rows.append(
                {
                    "Journal": journal,
                    "Year": int(year),
                    "JSD": round(jsd, 4),
                    "NewCommunityFrac": round(new_frac, 4),
                    "Top5Jaccard": round(jaccard, 4),
                    "Entropy": round(year_entropy, 4),
                    "EntropyDelta": round(year_entropy - baseline_entropy, 4),
                    "ArticleCount": int(total_year),
                }
            )

    # Community profiles (top 30 by size)
    comm_journal_dist = defaultdict(Counter)
    for idx in range(len(membership)):
        m = meta.get(node_ids[idx])
        if m:
            j = m["JournalName"].replace("Frontiers in ", "")
            comm_journal_dist[membership[idx]][j] += 1

    comm_sizes = Counter(membership)
    top_comms = []
    for comm_id, size in comm_sizes.most_common(30):
        jd = comm_journal_dist[comm_id]
        total = sum(jd.values())
        top_j = jd.most_common(5)
        top_comms.append(
            {
                "id": int(comm_id),
                "size": int(size),
                "journals": {j: round(c / total * 100, 1) for j, c in top_j},
                "dominant": top_j[0][0] if top_j else "?",
            }
        )

    log.info(
        f"       {len(drift_rows)} drift data points across {len(journals)} journals"
    )
    return pd.DataFrame(drift_rows), top_comms


# ──────────────────────────────────────────────────────────────────────────────
# STEP 5 — Assemble dashboard data
# ──────────────────────────────────────────────────────────────────────────────
def assemble_data(df_drift, top_comms, journal_names, n_nodes, n_edges):
    log.info("[5/6] Assembling dashboard data …")

    # JSD trend data per journal
    jsd_trends = {}
    for _, row in df_drift.iterrows():
        j = row["Journal"]
        if j not in jsd_trends:
            jsd_trends[j] = {
                "years": [],
                "jsd": [],
                "new_comm": [],
                "entropy_delta": [],
                "articles": [],
            }
        jsd_trends[j]["years"].append(row["Year"])
        jsd_trends[j]["jsd"].append(row["JSD"])
        jsd_trends[j]["new_comm"].append(round(row["NewCommunityFrac"] * 100, 2))
        jsd_trends[j]["entropy_delta"].append(row["EntropyDelta"])
        jsd_trends[j]["articles"].append(row["ArticleCount"])

    # Summary (latest target year)
    latest_year = max(TARGET_YEARS)
    summary = (
        df_drift[df_drift["Year"] == latest_year]
        .sort_values("JSD", ascending=False)
        .to_dict("records")
    )

    # Heatmap
    heatmap = df_drift[["Journal", "Year", "JSD"]].to_dict("records")
    heatmap_journals = sorted(df_drift["Journal"].unique())
    heatmap_years = sorted(df_drift["Year"].unique())

    return {
        "jsd_trends": jsd_trends,
        "summary": summary,
        "heatmap": heatmap,
        "heatmap_journals": heatmap_journals,
        "heatmap_years": [int(y) for y in heatmap_years],
        "communities": top_comms,
        "baseline_years": BASELINE_YEARS,
        "latest_year": latest_year,
        "stats": {
            "n_journals": len(journal_names),
            "n_nodes": n_nodes,
            "n_edges": n_edges,
            "year_range": f"{YEAR_START}–{YEAR_END}",
        },
    }


# ──────────────────────────────────────────────────────────────────────────────
# STEP 6 — Write HTML
# ──────────────────────────────────────────────────────────────────────────────
HTML_TEMPLATE = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Frontiers Scope Drift Dashboard</title>
<script src="https://cdn.plot.ly/plotly-2.35.2.min.js"></script>
<style>
:root{--red:#dc2626;--amber:#d97706;--green:#059669;--blue:#3b82f6;--purple:#8b5cf6;--slate:#64748b;--bg:#f8fafc;--card:#fff}
*{box-sizing:border-box;margin:0;padding:0}
body{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif;background:var(--bg);color:#0f172a;padding:16px 20px;max-width:1440px;margin:0 auto}
.hdr{text-align:center;margin-bottom:20px}
.hdr h1{font-size:22px;font-weight:700}.hdr p{font-size:13px;color:var(--slate);margin-top:2px}
.badge{display:inline-block;padding:3px 10px;border-radius:10px;font-size:11px;font-weight:600;margin:4px 2px;background:#f1f5f9;color:#475569}

.kpis{display:flex;gap:10px;margin-bottom:16px;flex-wrap:wrap}
.kpi{background:var(--card);border-radius:10px;padding:10px 14px;box-shadow:0 1px 2px rgba(0,0,0,.06);flex:1;min-width:130px}
.kpi .l{font-size:10px;color:#94a3b8;text-transform:uppercase;letter-spacing:.5px}
.kpi .v{font-size:22px;font-weight:700;margin-top:1px}
.kpi .d{font-size:11px;color:var(--slate)}

.grid{display:grid;gap:14px;margin-bottom:14px}
.g1{grid-template-columns:1fr}.g2{grid-template-columns:1fr 1fr}
@media(max-width:900px){.g2{grid-template-columns:1fr}}

.card{background:var(--card);border-radius:10px;padding:14px;box-shadow:0 1px 2px rgba(0,0,0,.06)}
.card h3{font-size:14px;font-weight:600}.card .sub{font-size:11px;color:#94a3b8;margin-bottom:10px}

table{width:100%;border-collapse:collapse;font-size:13px}
th{text-align:left;padding:7px 8px;border-bottom:2px solid #e5e7eb;font-weight:600;color:var(--slate);font-size:11px;text-transform:uppercase;letter-spacing:.4px}
td{padding:7px 8px;border-bottom:1px solid #f3f4f6}
tr:hover{background:#f9fafb}
.drift-h{color:var(--red);font-weight:700}
.drift-m{color:var(--amber);font-weight:600}
.drift-l{color:var(--green);font-weight:500}
.bar-bg{height:6px;background:#f3f4f6;border-radius:3px;position:relative}
.bar-f{height:6px;border-radius:3px;position:absolute;top:0;left:0}

.comm-list{max-height:400px;overflow-y:auto;font-size:13px}
.comm-item{padding:6px 0;border-bottom:1px solid #f3f4f6}
.comm-id{font-weight:700;color:#4338ca}.comm-sz{color:var(--slate);font-size:12px}
.comm-j{margin-top:3px}.comm-j span{display:inline-block;background:#f3f4f6;padding:1px 7px;border-radius:4px;font-size:11px;margin:1px}

.foot{text-align:center;margin-top:24px;font-size:11px;color:#94a3b8}
</style>
</head>
<body>

<div class="hdr">
<h1>Frontiers Scope Drift Detection</h1>
<p>Citation network community detection — Leiden algorithm on AIRAK data</p>
<span class="badge" id="meta-badge"></span>
</div>

<div class="kpis" id="kpis"></div>

<div class="grid g1">
<div class="card">
<h3>Scope Drift Rankings — <span id="latest-yr"></span> vs Baseline (<span id="bl-yrs"></span>)</h3>
<div class="sub">Jensen-Shannon Divergence measures how much each journal's citation-community distribution has shifted</div>
<table id="tbl"><thead><tr>
<th>Journal</th><th>JSD</th><th style="width:100px">JSD</th><th>New Comm %</th><th>Top-5 Jaccard</th><th>Entropy Δ</th><th>Articles</th>
</tr></thead><tbody id="tbl-body"></tbody></table>
</div>
</div>

<div class="grid g2">
<div class="card"><h3>Drift Trajectory Over Time</h3><div class="sub">JSD trend per journal — rising = increasing scope drift</div><div id="jsd-trend" style="height:420px"></div></div>
<div class="card"><h3>Drift Heatmap — All Journals × Years</h3><div class="sub">Darker = greater divergence from baseline scope</div><div id="heatmap" style="height:420px"></div></div>
</div>

<div class="grid g2">
<div class="card"><h3>New Community Fraction</h3><div class="sub">% of articles in communities absent from the journal's baseline</div><div id="new-comm" style="height:380px"></div></div>
<div class="card"><h3>Entropy Change</h3><div class="sub">Positive = spreading across more communities; Negative = concentrating</div><div id="entropy" style="height:380px"></div></div>
</div>

<div class="grid g1">
<div class="card">
<h3>Top 30 Citation Communities</h3>
<div class="sub">Leiden-detected communities — these form the "topics" against which drift is measured</div>
<div class="comm-list" id="comm-list"></div>
</div>
</div>

<div class="foot">Data: <code>ocean-breeze-tier-1.airak</code> · Leiden algorithm (Traag et al. 2019) · Modularity partition</div>

<script>
const D=/*DATA_PLACEHOLDER*/null;
const COLORS=['#4338ca','#dc2626','#d97706','#059669','#0891b2','#7c3aed','#db2777','#ea580c',
              '#16a34a','#2563eb','#9333ea','#c026d3','#0d9488','#ca8a04','#64748b'];

// Header
document.getElementById('meta-badge').textContent=
  `Leiden · Modularity · ${D.stats.n_nodes.toLocaleString()} nodes · ${D.stats.n_edges.toLocaleString()} edges · ${D.stats.year_range}`;
document.getElementById('latest-yr').textContent=D.latest_year;
document.getElementById('bl-yrs').textContent=D.baseline_years.join('–');

// KPIs
const highD=D.summary.filter(d=>d.JSD>0.30).length;
const medD=D.summary.filter(d=>d.JSD>0.20&&d.JSD<=0.30).length;
const avgJSD=D.summary.length?(D.summary.reduce((s,d)=>s+d.JSD,0)/D.summary.length).toFixed(3):'—';
const maxD=D.summary[0]||{};
document.getElementById('kpis').innerHTML=`
<div class="kpi"><div class="l">Journals</div><div class="v">${D.stats.n_journals}</div><div class="d">Top by volume</div></div>
<div class="kpi"><div class="l">High Drift (JSD>0.30)</div><div class="v" style="color:var(--red)">${highD}</div><div class="d">above threshold</div></div>
<div class="kpi"><div class="l">Medium Drift (0.20–0.30)</div><div class="v" style="color:var(--amber)">${medD}</div><div class="d">caution zone</div></div>
<div class="kpi"><div class="l">Average JSD (${D.latest_year})</div><div class="v">${avgJSD}</div><div class="d">across all journals</div></div>
<div class="kpi"><div class="l">Highest Drift</div><div class="v" style="color:var(--red)">${maxD.JSD||'—'}</div><div class="d">${maxD.Journal||''}</div></div>`;

// Summary table
const tb=document.getElementById('tbl-body');
let th='';
D.summary.forEach(d=>{
  const cls=d.JSD>0.30?'drift-h':d.JSD>0.20?'drift-m':'drift-l';
  const pct=Math.min(d.JSD/0.40*100,100);
  const bc=d.JSD>0.30?'var(--red)':d.JSD>0.20?'var(--amber)':'var(--green)';
  const ed=d.EntropyDelta;
  th+=`<tr><td><strong>${d.Journal}</strong></td>
    <td class="${cls}">${d.JSD.toFixed(3)}</td>
    <td><div class="bar-bg"><div class="bar-f" style="width:${pct}%;background:${bc}"></div></div></td>
    <td>${(d.NewCommunityFrac*100).toFixed(1)}%</td>
    <td>${d.Top5Jaccard.toFixed(2)}</td>
    <td style="color:${ed>0?'var(--red)':'var(--green)'}">${ed>0?'+':''}${ed.toFixed(3)}</td>
    <td>${d.ArticleCount.toLocaleString()}</td></tr>`;
});
tb.innerHTML=th;

// JSD Trend
const tTraces=[];let ci=0;
for(const[j,d]of Object.entries(D.jsd_trends)){
  tTraces.push({x:d.years,y:d.jsd,name:j,type:'scatter',mode:'lines+markers',
    line:{color:COLORS[ci%COLORS.length],width:2},marker:{size:5}});ci++;
}
Plotly.newPlot('jsd-trend',tTraces,{
  template:'plotly_white',autosize:true,margin:{l:50,r:20,t:20,b:40},
  xaxis:{title:'Year',dtick:1},yaxis:{title:'Jensen-Shannon Divergence',rangemode:'tozero'},
  legend:{font:{size:10},orientation:'v',x:1.02,y:1},hovermode:'x unified'
},{responsive:true});

// Heatmap
const hj=D.heatmap_journals,hy=D.heatmap_years;
const z=hj.map(j=>hy.map(y=>{const c=D.heatmap.find(d=>d.Journal===j&&d.Year===y);return c?c.JSD:null}));
Plotly.newPlot('heatmap',[{z,x:hy.map(String),y:hj,type:'heatmap',
  colorscale:[[0,'#f0fdf4'],[0.3,'#fef9c3'],[0.6,'#fed7aa'],[1,'#fca5a5']],
  colorbar:{title:'JSD',thickness:15},
  hovertemplate:'%{y}<br>%{x}: JSD=%{z:.3f}<extra></extra>'}],{
  template:'plotly_white',autosize:true,margin:{l:160,r:20,t:10,b:40},
  yaxis:{automargin:true,tickfont:{size:11}},xaxis:{dtick:1}
},{responsive:true});

// New community fraction
const ncT=[];ci=0;
for(const[j,d]of Object.entries(D.jsd_trends)){
  ncT.push({x:d.years,y:d.new_comm,name:j,type:'scatter',mode:'lines+markers',
    line:{color:COLORS[ci%COLORS.length],width:2},marker:{size:5}});ci++;
}
Plotly.newPlot('new-comm',ncT,{
  template:'plotly_white',autosize:true,margin:{l:50,r:20,t:20,b:40},
  xaxis:{title:'Year',dtick:1},yaxis:{title:'New Community %',rangemode:'tozero'},
  legend:{font:{size:10},orientation:'v',x:1.02,y:1},hovermode:'x unified'
},{responsive:true});

// Entropy chart
const eT=[];ci=0;
for(const[j,d]of Object.entries(D.jsd_trends)){
  eT.push({x:d.years,y:d.entropy_delta,name:j,type:'scatter',mode:'lines+markers',
    line:{color:COLORS[ci%COLORS.length],width:2},marker:{size:5}});ci++;
}
Plotly.newPlot('entropy',eT,{
  template:'plotly_white',autosize:true,margin:{l:50,r:20,t:20,b:40},
  xaxis:{title:'Year',dtick:1},yaxis:{title:'Entropy Δ vs Baseline'},
  legend:{font:{size:10},orientation:'v',x:1.02,y:1},hovermode:'x unified',
  shapes:[{type:'line',y0:0,y1:0,x0:D.heatmap_years[0],x1:D.heatmap_years.at(-1),
           line:{color:'#d1d5db',width:1,dash:'dot'}}]
},{responsive:true});

// Community list
const cl=document.getElementById('comm-list');
cl.innerHTML=D.communities.map(c=>{
  const tags=Object.entries(c.journals).map(([j,p])=>`<span>${j} (${p}%)</span>`).join('');
  return `<div class="comm-item"><span class="comm-id">Community ${c.id}</span>
    <span class="comm-sz"> · ${c.size.toLocaleString()} articles</span>
    <div class="comm-j">${tags}</div></div>`;
}).join('');
</script>
</body>
</html>"""


def build_html(dashboard_data):
    log.info("[6/6] Writing HTML dashboard …")
    data_json = json.dumps(dashboard_data, default=str)
    html = HTML_TEMPLATE.replace(
        "const D=/*DATA_PLACEHOLDER*/null;",
        f"const D={data_json};",
    )
    # Windows defaults to cp1252; embedded JSON can include Greek (e.g. Δ) and other Unicode.
    with open(OUTPUT_PATH, "w", encoding="utf-8", newline="\n") as f:
        f.write(html)
    log.info(f"       -> {OUTPUT_PATH} ({len(html):,} chars)")


# ──────────────────────────────────────────────────────────────────────────────
# MAIN
# ──────────────────────────────────────────────────────────────────────────────
def main():
    log.info("=" * 60)
    log.info("  Frontiers Scope Drift Dashboard Builder")
    log.info("=" * 60)

    client = bigquery.Client(project=BQ_PROJECT)

    # 1. Journals
    df_j = get_top_journals(client)
    journal_ids = df_j["JournalId"].tolist()
    journal_names = [j.replace("Frontiers in ", "") for j in df_j["DisplayName"]]

    # 2. Citation data
    df_edges, meta = get_citation_data(client, journal_ids)

    # 3. Graph + Leiden
    node_ids, membership, n_edges = build_graph_and_cluster(df_edges)

    # 4. Drift metrics
    df_drift, top_comms = compute_drift(node_ids, membership, meta)

    # 5. Assemble
    dashboard_data = assemble_data(
        df_drift,
        top_comms,
        journal_names,
        n_nodes=len(node_ids),
        n_edges=n_edges,
    )

    # 6. Write
    build_html(dashboard_data)

    log.info("")
    log.info("Done! Open %s in a browser.", OUTPUT_PATH)
    log.info("=" * 60)


if __name__ == "__main__":
    main()
