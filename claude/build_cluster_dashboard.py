"""
build_cluster_dashboard.py
===========================
Pulls citation data from AIRAK BigQuery, runs Leiden community detection
at macro/meso/micro resolutions, labels clusters via FieldOfStudy, and
writes an interactive HTML dashboard.

Data source : ocean-breeze-tier-1.airak
Algorithm   : Leiden (Traag et al., 2019) — CPM partition
Output      : clusters.html

Requirements:
    pip install leidenalg python-igraph google-cloud-bigquery pandas psutil

Usage:
    export GOOGLE_APPLICATION_CREDENTIALS=/path/to/credentials.json
    python build_cluster_dashboard.py

Config:
    Edit the constants below to change journals, years, resolutions, etc.
"""

import os
import gc
import json
import random
import logging
from collections import Counter

import pandas as pd
import igraph as ig
import leidenalg
from google.cloud import bigquery

# ──────────────────────────────────────────────────────────────────────────────
# CONFIG — tweak these to taste
# ──────────────────────────────────────────────────────────────────────────────
BQ_PROJECT = "ocean-breeze-tier-1"
AIRAK = "ocean-breeze-tier-1.airak"
FRONTIERS_PUBLISHER_ID = 1563368095744

TOP_N_JOURNALS = 5  # how many journals to include
YEAR_START = 2020  # citation graph window
YEAR_END = 2025
FOS_SIMILARITY_MIN = 0.25  # minimum similarity for FoS assignments
FOS_SAMPLE_PER_COMMUNITY = 150  # articles sampled per community for labelling
FOS_BATCH_SIZE = 5000  # BQ query batch size

LEIDEN_RESOLUTIONS = {
    "macro": 0.00005,  # few broad domains
    "meso": 0.0005,  # thematic areas
    "micro": 0.003,  # fine-grained topics
}

# Minimum community size to include in the dashboard at each level
MIN_COMMUNITY_SIZE = {"macro": 300, "meso": 50, "micro": 50}
# Max communities shown per level
MAX_COMMUNITIES = {"macro": 25, "meso": 80, "micro": 80}

OUTPUT_PATH = "clusters.html"

random.seed(42)
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s  %(message)s", datefmt="%H:%M:%S"
)
log = logging.getLogger(__name__)


# ──────────────────────────────────────────────────────────────────────────────
# STEP 1 — Identify top journals
# ──────────────────────────────────────────────────────────────────────────────
def get_top_journals(client):
    log.info(f"[1/7] Finding top {TOP_N_JOURNALS} Frontiers journals …")
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
        log.info(f"       {r['DisplayName']:<40} {r['pubs']:>6,} articles")
    return df


# ──────────────────────────────────────────────────────────────────────────────
# STEP 2 — Pull citation edges
# ──────────────────────────────────────────────────────────────────────────────
def get_edges(client, journal_ids):
    ids = ",".join(str(x) for x in journal_ids)
    log.info("[2/7] Pulling citation edges from AIRAK …")
    q = f"""
    WITH pubs AS (
      SELECT PublicationId
      FROM `{AIRAK}.Publication`
      WHERE JournalId IN ({ids})
        AND PublishedYear BETWEEN {YEAR_START} AND {YEAR_END}
    )
    SELECT pc.PublicationId AS s, pc.CitedPublicationId AS t
    FROM `{AIRAK}.PublicationCitation` pc
    WHERE pc.PublicationId    IN (SELECT PublicationId FROM pubs)
      AND pc.CitedPublicationId IN (SELECT PublicationId FROM pubs)
    """
    df = client.query(q).to_dataframe()
    log.info(f"       {len(df):,} edges")
    return df


# ──────────────────────────────────────────────────────────────────────────────
# STEP 3 — Pull node metadata
# ──────────────────────────────────────────────────────────────────────────────
def get_nodes(client, journal_ids):
    ids = ",".join(str(x) for x in journal_ids)
    log.info("[3/7] Pulling node metadata …")
    q = f"""
    SELECT p.PublicationId, p.PublishedYear, j.DisplayName AS JournalName
    FROM `{AIRAK}.Publication` p
    JOIN `{AIRAK}.Journal` j ON p.JournalId = j.JournalId
    WHERE j.JournalId IN ({ids})
      AND p.PublishedYear BETWEEN {YEAR_START} AND {YEAR_END}
    """
    df = client.query(q).to_dataframe()
    log.info(f"       {len(df):,} articles")
    return df.set_index("PublicationId").to_dict("index")


# ──────────────────────────────────────────────────────────────────────────────
# STEP 4 — Build graph & run Leiden
# ──────────────────────────────────────────────────────────────────────────────
def build_graph_and_cluster(df_edges):
    log.info("[4/7] Building graph & running Leiden …")
    n_edges_total = len(df_edges)
    node_ids = sorted(set(df_edges["s"]) | set(df_edges["t"]))
    id_map = {p: i for i, p in enumerate(node_ids)}

    edges = [
        (id_map[r["s"]], id_map[r["t"]])
        for _, r in df_edges.iterrows()
        if r["s"] in id_map and r["t"] in id_map
    ]
    del df_edges
    gc.collect()

    G = ig.Graph(n=len(node_ids), edges=edges, directed=False)
    G.simplify()
    log.info(f"       graph: {G.vcount():,} nodes, {G.ecount():,} edges")

    memberships = {}
    for level, res in LEIDEN_RESOLUTIONS.items():
        part = leidenalg.find_partition(
            G,
            leidenalg.CPMVertexPartition,
            resolution_parameter=res,
            n_iterations=10,
            seed=42,
        )
        memberships[level] = part.membership
        sizes = sorted(Counter(part.membership).values(), reverse=True)
        n_big = sum(1 for s in sizes if s >= 50)
        log.info(
            f"       {level:6s} res={res}: {len(set(part.membership)):,} communities, "
            f"{n_big} with ≥50 members, top: {sizes[:5]}"
        )

    del G, edges
    gc.collect()
    return node_ids, memberships, n_edges_total


# ──────────────────────────────────────────────────────────────────────────────
# STEP 5 — Profile communities
# ──────────────────────────────────────────────────────────────────────────────
def profile_communities(node_ids, memberships, meta):
    log.info("[5/7] Profiling communities …")
    profiles = {}
    for level in ("macro", "meso", "micro"):
        mem = memberships[level]
        min_sz = MIN_COMMUNITY_SIZE[level]
        max_n = MAX_COMMUNITIES[level]
        cc = Counter(mem)
        big = [(c, s) for c, s in cc.most_common() if s >= min_sz][:max_n]

        out = []
        for cid, sz in big:
            jc, yc = Counter(), Counter()
            for i in range(len(mem)):
                if mem[i] == cid:
                    m = meta.get(node_ids[i])
                    if m:
                        jc[m["JournalName"].replace("Frontiers in ", "")] += 1
                        yc[m["PublishedYear"]] += 1
            tot = sum(jc.values()) or 1
            tj = jc.most_common(5)
            out.append(
                {
                    "id": int(cid),
                    "size": int(sz),
                    "journals": {j: round(c / tot * 100, 1) for j, c in tj},
                    "dominant": tj[0][0] if tj else "?",
                    "dominant_pct": round(tj[0][1] / tot * 100, 1) if tj else 0,
                    "years": {int(k): int(v) for k, v in sorted(yc.items())},
                }
            )
        profiles[level] = out
        log.info(f"       {level}: {len(out)} communities")

    # hierarchy links
    n = len(memberships["macro"])
    t1, t2 = {}, {}
    for i in range(n):
        t1.setdefault(memberships["meso"][i], Counter())[memberships["macro"][i]] += 1
        t2.setdefault(memberships["micro"][i], Counter())[memberships["meso"][i]] += 1
    me2ma = {k: v.most_common(1)[0][0] for k, v in t1.items()}
    mi2me = {k: v.most_common(1)[0][0] for k, v in t2.items()}
    for p in profiles["meso"]:
        p["parent_macro"] = int(me2ma.get(p["id"], -1))
    for p in profiles["micro"]:
        p["parent_meso"] = int(mi2me.get(p["id"], -1))

    return profiles


# ──────────────────────────────────────────────────────────────────────────────
# STEP 6 — Label communities via FieldOfStudy
# ──────────────────────────────────────────────────────────────────────────────
def label_communities(client, node_ids, memberships, profiles):
    log.info("[6/7] Labelling communities via FieldOfStudy …")

    # build community → pub_id map
    comm_pubs = {}
    for level, mem in memberships.items():
        for i in range(len(mem)):
            comm_pubs.setdefault(f"{level}_{mem[i]}", []).append(node_ids[i])

    # sample
    sample_ids = set()
    comm_samples = {}
    for level in profiles:
        for p in profiles[level]:
            key = f"{level}_{p['id']}"
            pubs = comm_pubs.get(key, [])
            s = random.sample(pubs, min(FOS_SAMPLE_PER_COMMUNITY, len(pubs)))
            comm_samples[key] = s
            sample_ids.update(s)

    del comm_pubs
    gc.collect()
    log.info(f"       sampling {len(sample_ids):,} articles")

    # query BQ in batches
    sample_list = list(sample_ids)
    pub_fos = {}
    for i in range(0, len(sample_list), FOS_BATCH_SIZE):
        batch = sample_list[i : i + FOS_BATCH_SIZE]
        ids_str = ",".join(str(x) for x in batch)
        q = f"""
        SELECT pf.PublicationId, fos.DisplayName, fos.Level, pf.Similarity
        FROM `{AIRAK}.PublicationFieldOfStudy` pf
        JOIN `{AIRAK}.FieldOfStudy` fos ON pf.FieldOfStudyId = fos.FieldOfStudyId
        WHERE pf.PublicationId IN ({ids_str})
          AND fos.Level IN (1, 2)
          AND pf.Similarity >= {FOS_SIMILARITY_MIN}
        """
        df = client.query(q).to_dataframe()
        for _, r in df.iterrows():
            pub_fos.setdefault(r["PublicationId"], []).append(
                (r["DisplayName"], int(r["Level"]), float(r["Similarity"]))
            )
        log.info(f"       batch {i // FOS_BATCH_SIZE + 1}: {len(df):,} links")

    # assign labels
    def _top(key, fos_level):
        fc = Counter()
        for pid in comm_samples.get(key, []):
            for name, lv, _ in pub_fos.get(pid, []):
                if lv == fos_level:
                    fc[name] += 1
        return fc.most_common(5)

    for p in profiles["macro"]:
        top = _top(f"macro_{p['id']}", 1)
        p["fos"] = [n for n, _ in top[:3]]
        p["label"] = top[0][0] if top else p["dominant"]

    for p in profiles["meso"]:
        top1 = _top(f"meso_{p['id']}", 1)
        top2 = _top(f"meso_{p['id']}", 2)
        p["fos"] = [n for n, _ in top1[:3]]
        p["fos_specific"] = [n for n, _ in top2[:3]]
        p["label"] = top1[0][0] if top1 else p["dominant"]
        p["label_specific"] = top2[0][0] if top2 else ""

    for p in profiles["micro"]:
        top = _top(f"micro_{p['id']}", 2)
        p["fos"] = [n for n, _ in top[:3]]
        p["label"] = top[0][0] if top else p["dominant"]

    # global FoS across ALL Frontiers journals (for context tab)
    log.info("       querying global FoS distribution …")
    q_global = f"""
    SELECT fos.Level, fos.DisplayName AS field_name,
           COUNT(DISTINCT pf.PublicationId) AS articles
    FROM `{AIRAK}.PublicationFieldOfStudy` pf
    JOIN `{AIRAK}.FieldOfStudy` fos ON pf.FieldOfStudyId = fos.FieldOfStudyId
    JOIN `{AIRAK}.Publication` p ON pf.PublicationId = p.PublicationId
    JOIN `{AIRAK}.Journal` j ON p.JournalId = j.JournalId
    WHERE j.PublisherId = {FRONTIERS_PUBLISHER_ID}
      AND p.PublishedYear BETWEEN {YEAR_START} AND {YEAR_END}
      AND fos.Level IN (0, 1, 2)
      AND pf.Similarity >= 0.2
    GROUP BY 1, 2
    HAVING articles >= 100
    ORDER BY 1, 3 DESC
    """
    df_g = client.query(q_global).to_dataframe()
    fos_global = {"macro": {}, "meso": {}, "micro": {}}
    level_map = {0: "macro", 1: "meso", 2: "micro"}
    for _, r in df_g.iterrows():
        fos_global[level_map[r["Level"]]][r["field_name"]] = int(r["articles"])
    for k in fos_global:
        fos_global[k] = dict(sorted(fos_global[k].items(), key=lambda x: -x[1])[:30])

    return profiles, fos_global


# ──────────────────────────────────────────────────────────────────────────────
# STEP 7 — Build HTML dashboard
# ──────────────────────────────────────────────────────────────────────────────
HTML_TEMPLATE = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Frontiers Citation Clusters — Macro · Meso · Micro</title>
<script src="https://cdn.plot.ly/plotly-2.35.2.min.js"></script>
<style>
:root{--blue:#3b82f6;--pink:#ec4899;--amber:#f59e0b;--emerald:#10b981;--violet:#8b5cf6;--slate:#64748b;--bg:#f8fafc;--card:#fff;--border:#e2e8f0}
*{box-sizing:border-box;margin:0;padding:0}
body{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif;background:var(--bg);color:#0f172a;padding:16px 20px}
.hdr{text-align:center;margin-bottom:20px}
.hdr h1{font-size:22px;font-weight:700;letter-spacing:-.3px}
.hdr p{font-size:13px;color:var(--slate);margin-top:2px}
.pills{display:flex;gap:6px;justify-content:center;margin-top:8px;flex-wrap:wrap}
.pill{display:inline-block;padding:3px 10px;border-radius:10px;font-size:11px;font-weight:600}
.pill-ma{background:#dbeafe;color:#1d4ed8}.pill-me{background:#fce7f3;color:#be185d}
.pill-mi{background:#d1fae5;color:#065f46}.pill-g{background:#f1f5f9;color:#475569}

.kpis{display:flex;gap:10px;margin-bottom:16px;flex-wrap:wrap}
.kpi{background:var(--card);border-radius:10px;padding:10px 14px;box-shadow:0 1px 2px rgba(0,0,0,.06);flex:1;min-width:120px}
.kpi .l{font-size:10px;color:#94a3b8;text-transform:uppercase;letter-spacing:.5px}
.kpi .v{font-size:22px;font-weight:700;margin-top:1px}
.kpi .d{font-size:11px;color:var(--slate)}

.tabs{display:flex;gap:0;background:var(--border);border-radius:10px;padding:3px;margin-bottom:16px}
.tab{flex:1;text-align:center;padding:9px 0;border-radius:8px;font-size:13px;font-weight:600;
     cursor:pointer;border:none;background:transparent;color:var(--slate);transition:all .15s}
.tab.on{background:var(--card);color:#0f172a;box-shadow:0 1px 3px rgba(0,0,0,.08)}

.pan{display:none}.pan.on{display:block}

.row{display:grid;gap:14px}.r2{grid-template-columns:340px 1fr}.r1{grid-template-columns:1fr}
.r3{grid-template-columns:1fr 1fr 1fr}
@media(max-width:900px){.r2,.r3{grid-template-columns:1fr}}

.card{background:var(--card);border-radius:10px;padding:14px;box-shadow:0 1px 2px rgba(0,0,0,.06)}
.card h3{font-size:14px;font-weight:600}.card .sub{font-size:11px;color:#94a3b8;margin-bottom:10px}

.cl{max-height:620px;overflow-y:auto}
.ci{padding:8px 10px;border-bottom:1px solid #f1f5f9;cursor:pointer;transition:background .1s;border-left:3px solid transparent}
.ci:hover{background:#f8fafc}.ci.sel{background:#eff6ff;border-left-color:var(--blue)}
.ci-h{display:flex;justify-content:space-between;align-items:center}
.ci-n{font-weight:600;font-size:12px}.ci-s{font-size:11px;color:var(--slate);background:#f1f5f9;padding:1px 7px;border-radius:5px}
.ci-f{font-size:11px;color:#94a3b8;margin-top:2px}
.ci-j{margin-top:3px;display:flex;flex-wrap:wrap;gap:2px}
.ci-j span{font-size:10px;padding:1px 6px;border-radius:3px;font-weight:500}

.det{min-height:400px}
.dt{font-size:17px;font-weight:700}.dm{font-size:12px;color:var(--slate);margin-bottom:14px}
.ds{margin-bottom:14px}
.ds h4{font-size:11px;font-weight:600;color:#475569;text-transform:uppercase;letter-spacing:.4px;margin-bottom:6px}
.br{display:flex;align-items:center;margin-bottom:4px;font-size:12px}
.bl{width:100px;text-align:right;padding-right:8px;color:#475569;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
.bt{flex:1;height:16px;background:#f1f5f9;border-radius:3px;overflow:hidden}
.bf{height:100%;border-radius:3px;display:flex;align-items:center;padding-left:5px;font-size:10px;font-weight:600;color:#fff;min-width:20px}
.chi{font-size:12px;padding:4px 8px;background:#f8fafc;border-radius:4px;margin-bottom:3px;
     display:flex;justify-content:space-between;cursor:pointer;transition:background .1s}
.chi:hover{background:#eff6ff}
.chi .cn{font-weight:500}.chi .cs{color:#94a3b8}

.sb{height:520px}
.tree{max-height:600px;overflow-y:auto;font-size:13px;line-height:1.6}
.tree .ma{padding:6px 0;border-bottom:1px solid #f1f5f9}
.tree .me{margin-left:20px;padding:2px 0}.tree .mi{margin-left:40px;color:var(--slate)}

.j-im{background:#dbeafe;color:#1e40af}.j-ps{background:#fce7f3;color:#9d174d}
.j-on{background:#fef3c7;color:#92400e}.j-ph{background:#d1fae5;color:#065f46}
.j-pu{background:#e0e7ff;color:#3730a3}.j-o{background:#f1f5f9;color:#475569}

.foot{text-align:center;margin-top:24px;font-size:11px;color:#94a3b8}
</style>
</head>
<body>

<div class="hdr">
<h1>Frontiers Citation Cluster Hierarchy</h1>
<p>Leiden community detection on AIRAK citation network</p>
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
<button class="tab" data-t="fos">Field of Study</button>
</div>

<!-- MACRO -->
<div id="pan-macro" class="pan on">
<div class="row r2"><div class="card"><h3>Macro Clusters</h3><div class="sub">Broad domains · Leiden CPM</div><div class="cl" id="ma-list"></div></div>
<div class="card det" id="ma-det"><div style="color:#94a3b8;text-align:center;padding-top:120px">← Select a cluster</div></div></div>
<div class="row r1" style="margin-top:14px"><div class="card"><h3>Macro Size Distribution</h3><div class="sub">Articles per cluster, coloured by dominant journal</div><div id="ma-chart" style="height:300px"></div></div></div>
</div>

<!-- MESO -->
<div id="pan-meso" class="pan">
<div class="row r2"><div class="card"><h3>Meso Clusters</h3><div class="sub">Thematic areas · Leiden CPM</div><div class="cl" id="me-list"></div></div>
<div class="card det" id="me-det"><div style="color:#94a3b8;text-align:center;padding-top:120px">← Select a cluster</div></div></div>
<div class="row r1" style="margin-top:14px"><div class="card"><h3>Meso Size Distribution</h3><div class="sub">Top clusters</div><div id="me-chart" style="height:300px"></div></div></div>
</div>

<!-- MICRO -->
<div id="pan-micro" class="pan">
<div class="row r2"><div class="card"><h3>Micro Clusters</h3><div class="sub">Fine-grained topics · Leiden CPM</div><div class="cl" id="mi-list"></div></div>
<div class="card det" id="mi-det"><div style="color:#94a3b8;text-align:center;padding-top:120px">← Select a cluster</div></div></div>
<div class="row r1" style="margin-top:14px"><div class="card"><h3>Micro Size Distribution</h3><div class="sub">Top clusters</div><div id="mi-chart" style="height:300px"></div></div></div>
</div>

<!-- HIERARCHY -->
<div id="pan-hier" class="pan">
<div class="row r1"><div class="card"><h3>Sunburst — Macro → Meso → Micro</h3><div class="sub">Click to drill down</div><div class="sb" id="sunburst"></div></div></div>
<div class="row r1" style="margin-top:14px"><div class="card"><h3>Hierarchy Tree</h3><div class="sub">Full nesting</div><div class="tree" id="tree"></div></div></div>
</div>

<!-- FOS -->
<div id="pan-fos" class="pan">
<div class="row r3">
<div class="card"><h3>Level 0 — Domains</h3><div class="sub">All Frontiers journals</div><div id="fos0" style="height:460px"></div></div>
<div class="card"><h3>Level 1 — Disciplines</h3><div class="sub">Top 30</div><div id="fos1" style="height:460px"></div></div>
<div class="card"><h3>Level 2 — Sub-disciplines</h3><div class="sub">Top 30</div><div id="fos2" style="height:460px"></div></div>
</div>
</div>

<div class="foot">Data: <code>ocean-breeze-tier-1.airak</code> · Leiden algorithm (Traag et al. 2019) · CPM partition</div>

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
    <div class="ds"><h4>Fields of Study</h4>${fosH} ${fosS}</div>
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
    ids.push('ME'+m.id);labels.push(m.label+(m.label_specific?' · '+m.label_specific:''));
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


def build_html(dashboard_data):
    log.info("[7/7] Writing HTML dashboard …")
    data_json = json.dumps(dashboard_data, default=str)
    html = HTML_TEMPLATE.replace(
        "const D=/*DATA_PLACEHOLDER*/null;", f"const D={data_json};"
    )
    # Windows defaults to cp1252 for text files; HTML/JSON often contains Unicode (e.g. arrows, FoS names).
    with open(OUTPUT_PATH, "w", encoding="utf-8", newline="\n") as f:
        f.write(html)
    log.info(f"       -> {OUTPUT_PATH} ({len(html):,} chars)")


# ──────────────────────────────────────────────────────────────────────────────
# MAIN
# ──────────────────────────────────────────────────────────────────────────────
def main():
    log.info("=" * 60)
    log.info("  Frontiers Citation Cluster Dashboard Builder")
    log.info("=" * 60)

    client = bigquery.Client(project=BQ_PROJECT)

    # 1. Journals
    df_j = get_top_journals(client)
    journal_ids = df_j["JournalId"].tolist()
    journal_names = [j.replace("Frontiers in ", "") for j in df_j["DisplayName"]]

    # 2. Edges
    df_e = get_edges(client, journal_ids)

    # 3. Nodes
    meta = get_nodes(client, journal_ids)

    # 4. Graph + Leiden
    node_ids, memberships, n_edges = build_graph_and_cluster(df_e)

    # 5. Profile
    profiles = profile_communities(node_ids, memberships, meta)

    # 6. Label
    profiles, fos_global = label_communities(client, node_ids, memberships, profiles)

    # 7. Build dashboard
    dashboard_data = {
        "macro": profiles["macro"],
        "meso": profiles["meso"],
        "micro": profiles["micro"],
        "fos_global": fos_global,
        "journals": journal_names,
        "stats": {
            "nodes": len(node_ids),
            "edges": n_edges,
            "years": f"{YEAR_START}–{YEAR_END}",
            "n_macro": len(profiles["macro"]),
            "n_meso": len(profiles["meso"]),
            "n_micro": len(profiles["micro"]),
        },
    }
    # fix edge count — we lost it after del; re-count from memberships
    dashboard_data["stats"]["edges"] = n_edges

    build_html(dashboard_data)

    log.info("")
    log.info("Done! Open %s in a browser.", OUTPUT_PATH)
    log.info("=" * 60)


if __name__ == "__main__":
    main()
