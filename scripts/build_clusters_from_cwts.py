"""
build_clusters_from_cwts.py
===========================
Generates the clusters.html dashboard from local CWTS output files.
Shows macro/meso/micro cluster hierarchy with GPT labels.

Data source : cwts_output/ (local files)
Output      : output/clusters.html

Usage:
    python scripts/build_clusters_from_cwts.py
"""

import json
import logging
from collections import Counter
from pathlib import Path

import pandas as pd

# ──────────────────────────────────────────────────────────────────────────────
# CONFIG
# ──────────────────────────────────────────────────────────────────────────────
CWTS_DIR = Path(__file__).resolve().parent.parent / "cwts_output"
OUTPUT_PATH = Path(__file__).resolve().parent.parent / "output" / "clusters.html"

# Max clusters shown per level
MAX_COMMUNITIES = {"macro": 50, "meso": 100, "micro": 200}

# Target journals
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


# ──────────────────────────────────────────────────────────────────────────────
# LOAD DATA
# ──────────────────────────────────────────────────────────────────────────────
def load_data():
    """Load CWTS output files."""
    log.info("[1/4] Loading CWTS data …")

    # Classification
    df_class = pd.read_csv(
        CWTS_DIR / "classification.txt",
        sep="\t",
        header=None,
        names=["int_id", "micro", "meso", "macro"],
    )
    log.info(f"       classification.txt: {len(df_class):,} rows")

    # Metadata
    df_meta = pd.read_csv(
        CWTS_DIR / "pub_metadata.txt",
        sep="\t",
        header=None,
        names=["int_id", "pub_id", "is_frontiers", "journal", "date", "title"],
    )
    log.info(f"       pub_metadata.txt: {len(df_meta):,} rows")

    # Merge
    df = df_class.merge(df_meta, on="int_id", how="inner")

    # Extract year from date
    df["year"] = pd.to_datetime(df["date"], errors="coerce").dt.year
    df = df.dropna(subset=["year"])
    df["year"] = df["year"].astype(int)

    # Filter to target journals
    df = df[df["journal"].isin(JOURNALS)]
    log.info(f"       Filtered to {len(df):,} papers in {df['journal'].nunique()} journals")

    return df


def load_citations():
    """Load citation links and count edges."""
    log.info("[2/4] Loading citations …")
    cit_path = CWTS_DIR / "cit_links.txt"

    # Just count lines for edge count
    n_edges = sum(1 for _ in open(cit_path, "r"))
    log.info(f"       cit_links.txt: {n_edges:,} edges")

    return n_edges


def load_gpt_labels():
    """Load GPT labels for all levels."""
    labels = {"macro": {}, "meso": {}, "micro": {}}

    for level in ["macro", "meso", "micro"]:
        labels_file = CWTS_DIR / f"{level}_labels.csv"
        if labels_file.exists():
            df = pd.read_csv(labels_file)
            for _, row in df.iterrows():
                labels[level][int(row["cluster_id"])] = {
                    "short_label": row["short_label"],
                    "long_label": row.get("long_label", row["short_label"]),
                    "keywords": eval(row["keywords"]) if pd.notna(row.get("keywords")) else [],
                }
            log.info(f"       {level}_labels.csv: {len(labels[level])} labels")
        else:
            log.warning(f"       {level}_labels.csv not found")

    return labels


# ──────────────────────────────────────────────────────────────────────────────
# BUILD PROFILES
# ──────────────────────────────────────────────────────────────────────────────
def build_profiles(df, labels):
    """Build cluster profiles for each level."""
    log.info("[3/4] Building cluster profiles …")

    profiles = {"macro": [], "meso": [], "micro": []}

    for level in ["macro", "meso", "micro"]:
        cluster_counts = df.groupby(level).size().sort_values(ascending=False)
        max_clusters = MAX_COMMUNITIES[level]

        for cluster_id in cluster_counts.head(max_clusters).index:
            cdf = df[df[level] == cluster_id]
            size = len(cdf)

            # Journal breakdown
            journal_counts = cdf["journal"].value_counts()
            dominant = journal_counts.index[0] if len(journal_counts) > 0 else "Unknown"
            dominant_pct = round(journal_counts.iloc[0] / size * 100, 1) if len(journal_counts) > 0 else 0

            journals_dict = {}
            for j, c in journal_counts.items():
                journals_dict[j.replace("Frontiers in ", "")] = round(c / size * 100, 1)

            # Year distribution
            year_counts = cdf["year"].value_counts().sort_index()
            years_dict = {int(y): int(c) for y, c in year_counts.items()}

            # Get label from GPT labels
            label_info = labels[level].get(int(cluster_id), {})
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

            # Add parent relationships for hierarchy
            if level == "meso":
                # Find dominant macro cluster for this meso
                macro_counts = cdf["macro"].value_counts()
                if len(macro_counts) > 0:
                    profile["parent_macro"] = int(macro_counts.index[0])
            elif level == "micro":
                # Find dominant meso cluster for this micro
                meso_counts = cdf["meso"].value_counts()
                if len(meso_counts) > 0:
                    profile["parent_meso"] = int(meso_counts.index[0])

            profiles[level].append(profile)

        log.info(f"       {level}: {len(profiles[level])} clusters")

    return profiles


def build_fos_global(df, labels):
    """Build global field of study distribution from labels."""
    fos_global = {"macro": {}, "meso": {}, "micro": {}}

    for level in ["macro", "meso", "micro"]:
        keyword_counts = Counter()
        cluster_counts = df.groupby(level).size()

        for cluster_id, size in cluster_counts.items():
            label_info = labels[level].get(int(cluster_id), {})
            keywords = label_info.get("keywords", [])
            for kw in keywords[:3]:  # Top 3 keywords per cluster
                keyword_counts[kw] += size

        fos_global[level] = dict(keyword_counts.most_common(30))

    return fos_global


# ──────────────────────────────────────────────────────────────────────────────
# HTML TEMPLATE
# ──────────────────────────────────────────────────────────────────────────────
HTML_TEMPLATE = """<!DOCTYPE html>
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


# ──────────────────────────────────────────────────────────────────────────────
# BUILD HTML
# ──────────────────────────────────────────────────────────────────────────────
def build_html(dashboard_data):
    """Write HTML dashboard."""
    log.info("[4/4] Writing HTML dashboard …")

    data_json = json.dumps(dashboard_data, default=str)
    html = HTML_TEMPLATE.replace(
        "const D=/*DATA_PLACEHOLDER*/null;", f"const D={data_json};"
    )

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(html, encoding="utf-8")

    log.info(f"       Written to {OUTPUT_PATH}")
    log.info(f"       File size: {OUTPUT_PATH.stat().st_size / 1024:.1f} KB")


# ──────────────────────────────────────────────────────────────────────────────
# MAIN
# ──────────────────────────────────────────────────────────────────────────────
def main():
    log.info("=" * 60)
    log.info("Building Clusters Dashboard from CWTS Output")
    log.info("=" * 60)

    # Load data
    df = load_data()
    n_edges = load_citations()
    labels = load_gpt_labels()

    # Build profiles
    profiles = build_profiles(df, labels)
    fos_global = build_fos_global(df, labels)

    # Get year range
    years = sorted(df["year"].unique())
    year_range = f"{min(years)}–{max(years)}" if years else ""

    # Build dashboard data
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

    build_html(dashboard_data)

    log.info("=" * 60)
    log.info("Done!")
    log.info("=" * 60)


if __name__ == "__main__":
    main()
