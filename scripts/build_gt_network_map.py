"""
Build an independent ground-truth network-map dashboard.

Reads manual_scope_check_truth.ods and overlays those papers on the
citation-layout community map from an existing scope_dashboard.html
(same run / same geometry as the main dashboards).

Output:
    output/gt_network_map.html
"""

from __future__ import annotations

import json
import os
import re
import xml.etree.ElementTree as ET
import zipfile
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np
import pandas as pd

REPO = Path(__file__).resolve().parents[1]
DEFAULT_GT = Path(
    r"c:\Users\sophie.wilson\OneDrive - Frontiers Media SA\manual_scope_check_truth.ods"
)
DEFAULT_SCOPE_HTML = REPO / "output" / "scope_dashboard.html"
FALLBACK_SCOPE_HTML = REPO / "output" / "150948" / "scope_dashboard.html"
LABELS_CSV = REPO / "cwts_output" / "macro_labels.csv"
MESO_LABELS_CSV = REPO / "cwts_output" / "meso_labels.csv"
OUT_HTML = REPO / "output" / "gt_network_map.html"
BQ_PROJECT = "ocean-tech-adv-analytics-c-tfs"
BQ_DATASET = "raw_citation_network_data"
# Default matches the 50-macro EU run; override via RUN_TIMESTAMP env (notebook Step 4).
RUN_TIMESTAMP = os.environ.get("RUN_TIMESTAMP", "20260721_122750").strip() or "20260721_122750"

NS = {
    "office": "urn:oasis:names:tc:opendocument:xmlns:office:1.0",
    "table": "urn:oasis:names:tc:opendocument:xmlns:table:1.0",
    "text": "urn:oasis:names:tc:opendocument:xmlns:text:1.0",
}


def _cell_text(tc) -> str:
    texts = ["".join(p.itertext()) for p in tc.findall(".//text:p", NS)]
    val = " ".join(x for x in texts if x).strip()
    if not val:
        val = tc.get(f"{{{NS['office']}}}value") or ""
    return val


def read_ods_sheet(path: Path) -> pd.DataFrame:
    """Parse first sheet of an ODS without odfpy."""
    with zipfile.ZipFile(path) as z:
        root = ET.fromstring(z.read("content.xml"))
    table = root.find(".//table:table", NS)
    if table is None:
        raise ValueError(f"No table found in {path}")

    rows = []
    for tr in table.findall("table:table-row", NS):
        cells = []
        for tc in tr.findall("table:table-cell", NS):
            repeat = int(
                tc.get(f"{{{NS['table']}}}number-columns-repeated") or 1
            )
            val = _cell_text(tc)
            cells.extend([val] * min(repeat, 40))
        while cells and cells[-1] == "":
            cells.pop()
        if any(cells):
            rows.append(cells)

    if not rows:
        raise ValueError(f"Empty ODS: {path}")

    header = rows[0]
    n = len(header)
    body = []
    for r in rows[1:]:
        padded = (r + [""] * n)[:n]
        body.append(padded)
    return pd.DataFrame(body, columns=header)


def norm_scope(val: object) -> str | None:
    if val is None or (isinstance(val, float) and np.isnan(val)):
        return None
    s = str(val).strip().lower()
    if not s or s in {"nan", "none", "null"}:
        return None
    if s in {"in scope", "inscope", "in-scope", "in"}:
        return "In Scope"
    if s in {"out of scope", "oos", "out-of-scope", "out"}:
        return "Out of Scope"
    return str(val).strip()


def norm_journal(val: object) -> str:
    if val is None or (isinstance(val, float) and np.isnan(val)):
        return ""
    s = str(val).strip()
    if not s or s.lower() == "nan":
        return ""
    low = s.lower()
    if low.startswith("frontiers in "):
        rest = low[len("frontiers in ") :].strip()
        # Keep small words lowercase to match scope dashboard names
        parts = []
        for w in rest.split():
            if w in {"and", "of", "the"}:
                parts.append(w)
            elif w == "ai":
                parts.append("AI")
            else:
                parts.append(w.capitalize())
        return "Frontiers in " + " ".join(parts)
    return s


def load_labels(path: Path | None = None) -> dict[int, str]:
    """Load short labels from local CSV if present, else BigQuery taxonomy_labelling."""
    labels_file = path or LABELS_CSV
    if labels_file.exists():
        df = pd.read_csv(labels_file)
        out = {}
        for _, row in df.iterrows():
            out[int(row["cluster_id"])] = str(row["short_label"])
        return out

    _load_dotenv()
    import os

    from google.cloud import bigquery

    ts = os.environ.get("RUN_TIMESTAMP", RUN_TIMESTAMP).strip()
    if not ts:
        return {}
    level = "macro" if labels_file == LABELS_CSV else "meso"
    table = (
        f"ocean-tech-adv-analytics-c-tfs.taxonomy_labelling.cluster_labels_{level}_{ts}"
    )
    try:
        client = bigquery.Client(
            project="ocean-tech-adv-analytics-c-tfs", location="EU"
        )
        df = client.query(
            f"SELECT cluster_id, short_label FROM `{table}`"
        ).to_dataframe()
    except Exception as e:
        print(f"Could not load labels from {table}: {e}")
        return {}
    return {int(r["cluster_id"]): str(r["short_label"]) for _, r in df.iterrows()}


def _load_dotenv() -> None:
    env_path = REPO / ".env"
    if not env_path.exists():
        return
    for line in env_path.read_text(encoding="utf-8").splitlines():
        if "=" in line and not line.strip().startswith("#"):
            k, v = line.split("=", 1)
            import os

            os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))


def fetch_layout_clusters(
    int_ids: list[int], run_timestamp: str = RUN_TIMESTAMP
) -> dict[int, dict]:
    """Map int_id → {macro, meso} for the layout run."""
    if not int_ids:
        return {}
    _load_dotenv()
    from google.cloud import bigquery

    client = bigquery.Client(project=BQ_PROJECT, location="EU")
    sql = f"""
    SELECT c.int_id, c.macro, c.meso
    FROM `{BQ_PROJECT}.{BQ_DATASET}.classification_raw_{run_timestamp}` c
    WHERE c.int_id IN UNNEST(@ids)
    """
    job_config = bigquery.QueryJobConfig(
        query_parameters=[
            bigquery.ArrayQueryParameter("ids", "INT64", list(map(int, int_ids)))
        ]
    )
    df = client.query(sql, job_config=job_config).to_dataframe()
    out = {}
    for r in df.itertuples(index=False):
        out[int(r.int_id)] = {"macro": int(r.macro), "meso": int(r.meso)}
    return out


def fetch_layout_clusters_by_title(
    journals: list[str],
    run_timestamp: str = RUN_TIMESTAMP,
) -> dict[str, dict]:
    """Fallback: title_key → {int_id, macro, meso} within target journals."""
    if not journals:
        return {}
    _load_dotenv()
    from google.cloud import bigquery

    client = bigquery.Client(project=BQ_PROJECT, location="EU")
    journals = sorted({j for j in journals if j})
    journals_str = ", ".join(f"'{j}'" for j in journals)
    sql = f"""
    SELECT c.int_id, c.macro, c.meso, m.title, m.journal
    FROM `{BQ_PROJECT}.{BQ_DATASET}.classification_raw_{run_timestamp}` c
    JOIN `{BQ_PROJECT}.{BQ_DATASET}.pub_metadata_raw_{run_timestamp}` m
      ON c.int_id = m.int_id
    WHERE m.journal IN ({journals_str})
    """
    df = client.query(sql).to_dataframe()
    by_title: dict[str, dict] = {}
    for r in df.itertuples(index=False):
        tk = title_key(r.title, 80)
        if tk and tk not in by_title:
            by_title[tk] = {
                "int_id": int(r.int_id),
                "macro": int(r.macro),
                "meso": int(r.meso),
            }
    return by_title


def load_scope_data(path: Path) -> dict:
    text = path.read_text(encoding="utf-8")
    start = text.find("const DATA = ")
    if start < 0:
        raise ValueError(f"No DATA blob in {path}")
    start += len("const DATA = ")
    data, _ = json.JSONDecoder().raw_decode(text, start)
    return data


def title_key(title: object, max_chars: int = 60) -> str:
    if title is None or (isinstance(title, float) and np.isnan(title)):
        return ""
    t = str(title).lower()
    t = re.sub(r"[^a-z0-9\s]", " ", t)
    t = re.sub(r"\s+", " ", t).strip()
    return t[:max_chars]


def community_centroids(scatter: list[dict]) -> dict[int, tuple[float, float, int]]:
    buckets: dict[int, list[tuple[float, float]]] = defaultdict(list)
    for p in scatter:
        buckets[int(p["c"])].append((float(p["x"]), float(p["y"])))
    out = {}
    for cid, pts in buckets.items():
        arr = np.asarray(pts, dtype=float)
        out[cid] = (float(arr[:, 0].mean()), float(arr[:, 1].mean()), len(pts))
    return out


def paper_xy(
    int_id: object,
    macro: int,
    centroids: dict[int, tuple[float, float, int]],
    title_pos: dict[str, tuple[float, float, int]],
    title: object,
) -> tuple[float, float, str] | None:
    """Return (x, y, source) for a GT paper.

    Placement is driven by the paper's community (macro). Title matching is
    only accepted when the matched scatter point is in the *same* community —
    short-title collisions were previously putting papers in the wrong bubble.
    """
    if macro is None:
        return None

    candidates = []
    raw = str(title or "")
    for cand in (title_key(raw), title_key(raw[:50]), title_key(raw[:45])):
        if cand and cand not in candidates:
            candidates.append(cand)

    # Exact layout coords only if title hits a point in the same community
    for tk in candidates:
        if tk in title_pos:
            x, y, c = title_pos[tk]
            if int(c) == int(macro):
                return float(x), float(y), "title_match"

    if macro not in centroids:
        return None

    cx, cy, _ = centroids[macro]
    seed_key = candidates[0] if candidates else f"c{macro}"
    try:
        seed = int(int_id)
    except (TypeError, ValueError):
        seed = abs(hash(seed_key)) % (2**31)
    if pd.isna(int_id) or str(int_id).strip() in {"", "nan"}:
        seed = abs(hash(seed_key)) % (2**31)

    rng = np.random.default_rng(seed)
    # Keep jitter inside the community bubble (smaller than bubble radius)
    x = float(cx + rng.uniform(-0.035, 0.035))
    y = float(cy + rng.uniform(-0.035, 0.035))
    return x, y, "community_jitter"


def global_community_centroids(scope: dict) -> dict[int, tuple[float, float, int]]:
    """Community centroids from all journals (shared FR layout)."""
    buckets: dict[int, list[tuple[float, float]]] = defaultdict(list)
    for j in scope.get("journals", []):
        for p in j.get("scatter") or []:
            buckets[int(p["c"])].append((float(p["x"]), float(p["y"])))
    out = {}
    for cid, pts in buckets.items():
        arr = np.asarray(pts, dtype=float)
        out[cid] = (float(arr[:, 0].mean()), float(arr[:, 1].mean()), len(pts))
    return out


TEMPLATE = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Ground Truth Network Map</title>
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
header h1 { font-size: 1.35rem; font-weight: 700; margin-bottom: 4px; }
header p { color: var(--muted); font-size: 0.85rem; max-width: 980px; }
.main { padding: 20px 24px; }
.stats {
  display: flex; gap: 12px; flex-wrap: wrap; margin: 16px 0 8px;
}
.stat {
  background: var(--card);
  border: 1px solid var(--border);
  border-radius: 8px;
  padding: 10px 14px;
  min-width: 140px;
}
.stat .n { font-size: 1.25rem; font-weight: 700; }
.stat .l { font-size: 0.75rem; color: var(--muted); text-transform: uppercase; letter-spacing: .03em; }
.controls {
  display: flex; gap: 12px; flex-wrap: wrap; align-items: center;
  margin: 12px 0 16px;
}
select, .filter-btn {
  padding: 8px 12px;
  border: 1px solid var(--border);
  border-radius: 6px;
  background: var(--card);
  font-size: 0.9rem;
}
.filter-btn { cursor: pointer; }
.filter-btn.active { background: var(--text); color: #fff; border-color: var(--text); }
.grid { display: grid; gap: 16px; grid-template-columns: 1.4fr 1fr; }
@media (max-width: 1100px) { .grid { grid-template-columns: 1fr; } }
.card {
  background: var(--card);
  border: 1px solid var(--border);
  border-radius: 10px;
  padding: 16px;
}
.card h2 { font-size: 0.95rem; font-weight: 600; margin-bottom: 10px; }
.plot { height: 560px; }
table { width: 100%; border-collapse: collapse; font-size: 0.82rem; }
th {
  text-align: left; padding: 8px; border-bottom: 2px solid var(--border);
  color: var(--muted); font-size: 0.7rem; text-transform: uppercase;
  position: sticky; top: 0; background: var(--card);
}
td { padding: 8px; border-bottom: 1px solid var(--border); vertical-align: top; }
tr:hover { background: #f8fafc; }
.title { max-width: 280px; }
.in { color: var(--green); font-weight: 600; }
.out { color: var(--red); font-weight: 600; }
.borderline { color: var(--amber); font-weight: 600; }
.miss { color: var(--muted); font-weight: 600; }
.table-wrap { max-height: 560px; overflow: auto; }
.legend span { margin-right: 14px; font-size: 0.82rem; }
.dot { display:inline-block; width:10px; height:10px; border-radius:50%; margin-right:4px; }
</style>
</head>
<body>
<header>
  <h1>Ground Truth Network Map</h1>
  <p>
    Manual scope-check papers plotted on the citation-community layout
    (run layout from scope dashboard). Bubbles and labels use <b>macro</b>
    communities. Marker colour =
    <span style="color:var(--green);font-weight:600;">In Scope</span> /
    <span style="color:var(--red);font-weight:600;">Out of Scope</span>
    from the ground-truth file. Bubble colour = model scope
    (green = in scope / amber = borderline via LLM / red = out of scope).
  </p>
</header>
<div class="main">
  <div class="stats" id="stats"></div>
  <div class="controls">
    <select id="journalSelect"></select>
    <button class="filter-btn active" data-filter="all">All GT</button>
    <button class="filter-btn" data-filter="in">In Scope</button>
    <button class="filter-btn" data-filter="out">Out of Scope</button>
    <button class="filter-btn" data-filter="missing">Not in network</button>
    <span class="legend">
      <span><i class="dot" style="background:#1f8a4c"></i>GT In</span>
      <span><i class="dot" style="background:#c93030"></i>GT Out</span>
      <span><i class="dot" style="background:#9aa3b2"></i>Not in network</span>
    </span>
  </div>
  <div class="grid">
    <div class="card">
      <h2 id="plotTitle">Network map</h2>
      <div id="plot" class="plot"></div>
    </div>
    <div class="card">
      <h2>Papers in view</h2>
      <div class="table-wrap">
        <table>
          <thead>
            <tr>
              <th>Title</th>
              <th>GT</th>
              <th>Model</th>
              <th>Macro community</th>
            </tr>
          </thead>
          <tbody id="tbody"></tbody>
        </table>
      </div>
    </div>
  </div>
</div>
<script>
const DATA = __DATA_JSON__;
const FONT = { family:'-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,sans-serif', color:"#1a1f36", size:12 };
const CFG = { responsive:true, displayModeBar:false };
const sel = document.getElementById("journalSelect");
const tbody = document.getElementById("tbody");
const statsEl = document.getElementById("stats");
let filter = "all";

DATA.journals.forEach((j, i) => {
  const opt = document.createElement("option");
  opt.value = i;
  const n = j.papers.length;
  const oos = j.papers.filter(p => p.gt_scope === "Out of Scope").length;
  opt.textContent = j.name + " — " + n + " GT papers (" + oos + " OOS)";
  sel.appendChild(opt);
});

function esc(s) {
  return String(s || "").replace(/[&<>"']/g, c => ({
    "&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"
  }[c]));
}

function renderStats() {
  const all = DATA.journals.flatMap(j => j.papers);
  const inN = all.filter(p => p.gt_scope === "In Scope").length;
  const outN = all.filter(p => p.gt_scope === "Out of Scope").length;
  const miss = all.filter(p => !p.on_map).length;
  const agreeExact = all.filter(p => p.model_scope && p.gt_scope && p.model_scope === p.gt_scope).length;
  const comparable = all.filter(p =>
    p.model_scope && p.gt_scope && p.model_scope !== "Borderline"
  ).length;
  const borderline = all.filter(p => p.model_scope === "Borderline").length;
  statsEl.innerHTML = [
    ["GT papers", all.length],
    ["In Scope", inN],
    ["Out of Scope", outN],
    ["Model borderline", borderline],
    ["Not in network", miss],
    ["Model↔GT agree", comparable ? (agreeExact + " / " + comparable) : "—"]
  ].map(([l,n]) => '<div class="stat"><div class="n">'+n+'</div><div class="l">'+l+'</div></div>').join("");
}

function filteredPapers(j) {
  return j.papers.filter(p => {
    if (filter === "in") return p.gt_scope === "In Scope";
    if (filter === "out") return p.gt_scope === "Out of Scope";
    if (filter === "missing") return !p.on_map;
    return true;
  });
}

function render() {
  const j = DATA.journals[parseInt(sel.value, 10)];
  if (!j) return;
  const papers = filteredPapers(j);
  document.getElementById("plotTitle").textContent =
    j.name + " — " + papers.length + " papers in view";

  // Community background bubbles (model colour)
  const comm = j.communities || [];
  const maxN = Math.max(...comm.map(c => c.n), 1);
  const mkComm = (subset, color, name) => ({
    type: "scatter", mode: "markers", name,
    x: subset.map(c => c.x),
    y: subset.map(c => c.y),
    text: subset.map(c => c.label),
    customdata: subset.map(c => c.n),
    marker: {
      size: subset.map(c => Math.max(28, Math.sqrt(c.n / maxN) * 110)),
      sizemode: "diameter",
      color, opacity: 0.18,
      line: { color: "rgba(255,255,255,0.5)", width: 1 }
    },
    hovertemplate: "<b>%{text}</b><br>Journal papers in community: %{customdata:,}<br>"+name+"<extra></extra>",
    showlegend: true
  });
  const primary = comm.filter(c => c.model_status === "primary");
  const borderline = comm.filter(c => c.model_status === "borderline" || c.model_status === "rescued");
  const oosC = comm.filter(c => c.model_status === "oos");
  const traces = [];
  if (primary.length) traces.push(mkComm(primary, "#1f8a4c", "Model: in scope"));
  if (borderline.length) traces.push(mkComm(borderline, "#d4a300", "Model: borderline"));
  if (oosC.length) traces.push(mkComm(oosC, "#c93030", "Model: out of scope"));

  const groups = {
    "In Scope": papers.filter(p => p.on_map && p.gt_scope === "In Scope"),
    "Out of Scope": papers.filter(p => p.on_map && p.gt_scope === "Out of Scope"),
  };
  const colors = { "In Scope": "#1f8a4c", "Out of Scope": "#c93030" };
  Object.keys(groups).forEach(name => {
    const pts = groups[name];
    if (!pts.length) return;
    traces.push({
      type: "scatter", mode: "markers", name: "GT " + name,
      x: pts.map(p => p.x),
      y: pts.map(p => p.y),
      text: pts.map(p => p.title),
      customdata: pts.map(p => [
        p.community_label || ("Macro " + p.macro),
        p.gt_scope,
        p.model_scope || "—",
        p.article_code || p.article_id_original || p.int_id || ""
      ]),
      marker: {
        size: 11,
        color: colors[name],
        opacity: 0.92,
        line: { color: "#ffffff", width: 1.4 },
        symbol: "circle"
      },
      hovertemplate:
        "<b>%{text}</b><br>" +
        "Macro: %{customdata[0]}<br>" +
        "GT: %{customdata[1]} · Model: %{customdata[2]}<br>" +
        "ID: %{customdata[3]}<extra></extra>"
    });
  });

  // Off-map papers: no geometric trace; listed in table only
  Plotly.newPlot("plot", traces, {
    paper_bgcolor: "#ffffff",
    plot_bgcolor: "#ffffff",
    font: FONT,
    xaxis: { showgrid:false, zeroline:false, showticklabels:false, showline:false },
    yaxis: { showgrid:false, zeroline:false, showticklabels:false, showline:false, scaleanchor:"x" },
    legend: { orientation:"h", y:-0.06, font:{size:11} },
    margin: { l:10, r:10, t:10, b:60 },
    hovermode: "closest"
  }, CFG);

  tbody.innerHTML = "";
  papers
    .slice()
    .sort((a,b) => (a.gt_scope||"").localeCompare(b.gt_scope||"") || (a.title||"").localeCompare(b.title||""))
    .forEach(p => {
      const tr = document.createElement("tr");
      const gtCls = p.gt_scope === "In Scope" ? "in" : (p.gt_scope === "Out of Scope" ? "out" : "miss");
      const modelCls = p.model_scope === "In Scope" ? "in"
        : (p.model_scope === "Out of Scope" ? "out"
        : (p.model_scope === "Borderline" ? "borderline" : "miss"));
      tr.innerHTML =
        '<td class="title">' + esc(p.title) + '</td>' +
        '<td class="'+gtCls+'">' + esc(p.gt_scope || "—") + '</td>' +
        '<td class="'+modelCls+'">' + esc(p.model_scope || (p.on_map ? "—" : "Not in network")) + '</td>' +
        '<td>' + esc(p.community_label || (p.macro != null ? ("Macro "+p.macro) : "—")) + '</td>';
      tbody.appendChild(tr);
    });
}

sel.addEventListener("change", render);
document.querySelectorAll(".filter-btn").forEach(btn => {
  btn.addEventListener("click", () => {
    document.querySelectorAll(".filter-btn").forEach(b => b.classList.remove("active"));
    btn.classList.add("active");
    filter = btn.dataset.filter;
    render();
  });
});

renderStats();
if (DATA.journals.length) render();
</script>
</body>
</html>
"""


def build(
    gt_path: Path = DEFAULT_GT,
    scope_html: Path | None = None,
    out_path: Path = OUT_HTML,
) -> Path:
    scope_html = scope_html or (
        DEFAULT_SCOPE_HTML if DEFAULT_SCOPE_HTML.exists() else FALLBACK_SCOPE_HTML
    )
    if not gt_path.exists():
        raise FileNotFoundError(gt_path)
    if not scope_html.exists():
        raise FileNotFoundError(scope_html)

    print(f"GT file:     {gt_path}")
    print(f"Layout from: {scope_html}")

    gt = read_ods_sheet(gt_path)
    macro_labels = load_labels(LABELS_CSV)
    scope = load_scope_data(scope_html)

    scope_by_name = {j["name"]: j for j in scope.get("journals", [])}
    scope_by_lower = {j["name"].lower(): j for j in scope.get("journals", [])}
    macro_label_from_scope = {
        int(c["id"]): c.get("label") or f"Macro {c['id']}"
        for c in scope.get("communities", [])
    }
    for k, v in macro_labels.items():
        macro_label_from_scope.setdefault(k, v)

    gt = gt.copy()
    gt["gt_scope"] = gt["manual_scope_class"].map(norm_scope)
    gt["journal_use"] = gt.apply(
        lambda r: norm_journal(r.get("matched_journal"))
        or norm_journal(r.get("journal")),
        axis=1,
    )
    gt["int_id_num"] = pd.to_numeric(gt.get("int_id"), errors="coerce")
    gt["macro_ods"] = pd.to_numeric(gt.get("macro"), errors="coerce")
    gt["title_norm"] = gt["title"].map(lambda t: title_key(t, 120))

    # Drop empty titles / blank journals
    gt = gt[gt["title"].astype(str).str.strip().ne("")]
    gt = gt[gt["title"].astype(str).str.lower().ne("nan")]
    gt = gt[gt["journal_use"].astype(str).str.strip().ne("")]

    # Deduplicate ODS rows (same paper listed twice → duplicate dropdown counts)
    before = len(gt)
    gt = gt.sort_values(
        by=["int_id_num", "manual_scope_score"],
        ascending=[True, False],
        na_position="last",
    )
    # Deduplicate only within a journal (same paper may appear in multiple packs)
    gt = gt.drop_duplicates(subset=["journal_use", "title_norm"], keep="first")
    has_id = gt["int_id_num"].notna()
    gt = pd.concat(
        [
            gt.loc[has_id].drop_duplicates(
                subset=["journal_use", "int_id_num"], keep="first"
            ),
            gt.loc[~has_id],
        ],
        ignore_index=True,
    )
    print(f"Deduped GT rows: {before} -> {len(gt)}")

    int_ids = gt["int_id_num"].dropna().astype(int).unique().tolist()
    print(f"Resolving layout macros for {len(int_ids)} int_ids ({RUN_TIMESTAMP})…")
    try:
        layout_by_id = fetch_layout_clusters(int_ids)
        print(f"  BQ int_id matches: {len(layout_by_id)}")
    except Exception as e:
        print(f"  BQ int_id lookup failed: {e}")
        layout_by_id = {}

    need_title_mask = []
    matched_ids = set(layout_by_id)
    for _, row in gt.iterrows():
        if pd.isna(row["int_id_num"]):
            need_title_mask.append(True)
        else:
            need_title_mask.append(int(row["int_id_num"]) not in matched_ids)
    need_title = gt.loc[need_title_mask]
    layout_by_title: dict[str, dict] = {}
    if len(need_title):
        journals_for_lookup = sorted(scope_by_name.keys())
        print(
            f"  Title fallback for {len(need_title)} rows against "
            f"{len(journals_for_lookup)} journals…"
        )
        try:
            layout_by_title = fetch_layout_clusters_by_title(journals_for_lookup)
            print(f"  Title index size: {len(layout_by_title)}")
        except Exception as e:
            print(f"  BQ title lookup failed: {e}")
            layout_by_title = {}

    layout_comm_ids = set(global_community_centroids(scope).keys())
    print(f"Macro communities in layout: {len(layout_comm_ids)} -> {sorted(layout_comm_ids)}")

    def resolve_layout(row) -> dict:
        iid = int(row["int_id_num"]) if pd.notna(row["int_id_num"]) else None
        if iid is not None and iid in layout_by_id:
            d = layout_by_id[iid]
            return {
                "macro_layout": d["macro"],
                "meso_layout": d["meso"],
                "int_id_layout": iid,
                "cluster_source": "bq_int_id",
            }
        raw = str(row.get("title") or "")
        for cand in (title_key(raw, 80), title_key(raw, 60), title_key(raw[:50])):
            if cand in layout_by_title:
                d = layout_by_title[cand]
                return {
                    "macro_layout": d["macro"],
                    "meso_layout": d["meso"],
                    "int_id_layout": d["int_id"],
                    "cluster_source": "bq_title",
                }
        if pd.notna(row["macro_ods"]) and int(row["macro_ods"]) in layout_comm_ids:
            return {
                "macro_layout": int(row["macro_ods"]),
                "meso_layout": None,
                "int_id_layout": iid,
                "cluster_source": "ods_macro",
            }
        return {
            "macro_layout": None,
            "meso_layout": None,
            "int_id_layout": iid,
            "cluster_source": "none",
        }

    resolved = [resolve_layout(row) for _, row in gt.iterrows()]
    gt = pd.concat([gt.reset_index(drop=True), pd.DataFrame(resolved)], axis=1)
    print(
        "  Cluster sources:",
        dict(Counter(gt["cluster_source"])),
        "| macro found:",
        int(gt["macro_layout"].notna().sum()),
    )

    journals_out = []
    unmatched = 0
    pos_sources: Counter = Counter()
    global_centroids = global_community_centroids(scope)

    groups: dict[str, pd.DataFrame] = {}
    for journal, jdf in gt.groupby("journal_use", dropna=False):
        if not journal or not str(journal).strip():
            continue
        sj = scope_by_name.get(journal) or scope_by_lower.get(str(journal).lower())
        canon = sj["name"] if sj else journal
        groups[canon] = (
            jdf
            if canon not in groups
            else pd.concat([groups[canon], jdf], ignore_index=True)
        )

    for journal, jdf in groups.items():
        jdf = jdf.drop_duplicates(subset=["title_norm"], keep="first")
        if jdf["int_id_layout"].notna().any():
            with_id = jdf[jdf["int_id_layout"].notna()].drop_duplicates(
                subset=["int_id_layout"], keep="first"
            )
            without = jdf[jdf["int_id_layout"].isna()]
            jdf = pd.concat([with_id, without], ignore_index=True)

        sj = scope_by_name.get(journal) or scope_by_lower.get(journal.lower())
        scatter = (sj or {}).get("scatter") or []
        journal_counts = {
            cid: n for cid, (_x, _y, n) in community_centroids(scatter).items()
        }

        title_pos: dict[str, tuple[float, float, int]] = {}
        for p in scatter:
            tk = title_key(p.get("t"))
            if tk and tk not in title_pos:
                title_pos[tk] = (float(p["x"]), float(p["y"]), int(p["c"]))

        in_ids = set((sj or {}).get("in_scope_cluster_ids") or [])
        rescued = set(
            (sj or {}).get("borderline_cluster_ids")
            or (sj or {}).get("distance_rescued_cluster_ids")
            or []
        )
        primary_only = set()
        for c in (sj or {}).get("top_communities") or []:
            if c.get("is_primary"):
                primary_only.add(int(c["comm_id"]))
        if not primary_only and in_ids:
            primary_only = set(in_ids) - rescued

        bubble_ids = set(journal_counts) | {
            int(m)
            for m in jdf["macro_layout"].dropna().astype(int).tolist()
            if int(m) in global_centroids
        }
        communities = []
        for cid in sorted(bubble_ids, key=lambda c: -journal_counts.get(c, 0)):
            if cid not in global_centroids:
                continue
            x, y, _ = global_centroids[cid]
            n = int(journal_counts.get(cid, 0))
            if cid in primary_only:
                status = "primary"
            elif cid in rescued:
                status = "borderline"
            elif cid in in_ids:
                status = "primary"
            else:
                status = "oos"
            communities.append(
                {
                    "id": int(cid),
                    "label": macro_label_from_scope.get(int(cid), f"Macro {cid}"),
                    "x": round(x, 4),
                    "y": round(y, 4),
                    "n": n if n > 0 else 1,
                    "model_status": status,
                }
            )

        papers = []
        for _, row in jdf.iterrows():
            macro = int(row["macro_layout"]) if pd.notna(row["macro_layout"]) else None
            meso = int(row["meso_layout"]) if pd.notna(row["meso_layout"]) else None
            int_id = (
                int(row["int_id_layout"])
                if pd.notna(row.get("int_id_layout"))
                else (
                    int(row["int_id_num"]) if pd.notna(row["int_id_num"]) else None
                )
            )
            pos = None
            if macro is not None:
                pos = paper_xy(
                    int_id, macro, global_centroids, title_pos, row.get("title")
                )
            on_map = pos is not None
            if not on_map:
                unmatched += 1
            else:
                pos_sources[pos[2]] += 1

            model_scope = None
            overrides = (sj or {}).get("paper_scope_overrides") or {}
            ov = None
            if int_id is not None and overrides:
                ov = overrides.get(str(int_id)) or overrides.get(int_id)
            if ov and str(ov.get("verdict", "")).lower().replace(" ", "_") == "out_of_scope":
                model_scope = "Out of Scope"
            elif macro is not None and sj is not None:
                if macro in primary_only:
                    model_scope = "In Scope"
                elif macro in rescued:
                    model_scope = "Borderline"
                elif macro in in_ids:
                    # in_scope but not listed as primary/rescued → treat as in scope
                    model_scope = "In Scope"
                else:
                    model_scope = "Out of Scope"

            papers.append(
                {
                    "title": str(row.get("title") or ""),
                    "article_code": str(row.get("article_code") or "") or None,
                    "article_id_original": str(row.get("article_id_original") or "")
                    or None,
                    "int_id": int_id,
                    "macro": macro,
                    "meso": meso,
                    "community_label": (
                        macro_label_from_scope.get(macro, f"Macro {macro}")
                        if macro is not None
                        else None
                    ),
                    "cluster_source": row.get("cluster_source"),
                    "gt_scope": row.get("gt_scope"),
                    "model_scope": model_scope,
                    "gt_score": str(row.get("manual_scope_score") or "") or None,
                    "source_file": str(row.get("source_file") or ""),
                    "on_map": on_map,
                    "x": round(pos[0], 4) if pos else None,
                    "y": round(pos[1], 4) if pos else None,
                    "pos_source": pos[2] if pos else None,
                }
            )

        journals_out.append(
            {
                "name": journal,
                "in_scope_dashboard": sj is not None,
                "communities": communities,
                "papers": papers,
            }
        )

    journals_out.sort(key=lambda j: (-len(j["papers"]), j["name"]))
    seen = set()
    uniq = []
    for j in journals_out:
        if j["name"] in seen:
            continue
        seen.add(j["name"])
        uniq.append(j)
    journals_out = uniq

    payload = {
        "source_gt": str(gt_path),
        "layout_source": str(scope_html),
        "cluster_level": "macro",
        "n_macro_communities": len(layout_comm_ids),
        "n_gt_rows": int(len(gt)),
        "n_unmapped": int(unmatched),
        "gt_scope_counts": dict(Counter(gt["gt_scope"].dropna())),
        "journals": journals_out,
    }

    out_path.parent.mkdir(parents=True, exist_ok=True)
    html = TEMPLATE.replace(
        "__DATA_JSON__", json.dumps(payload, separators=(",", ":"), ensure_ascii=False)
    )
    out_path.write_text(html, encoding="utf-8")

    print(f"GT rows:     {len(gt)}")
    print(f"Journals:    {len(journals_out)}")
    print(f"Unmapped:    {unmatched}")
    print(f"Pos sources: {dict(pos_sources)}")
    for j in journals_out:
        nin = sum(1 for p in j["papers"] if p["gt_scope"] == "In Scope")
        nout = sum(1 for p in j["papers"] if p["gt_scope"] == "Out of Scope")
        nmap = sum(1 for p in j["papers"] if p["on_map"])
        macros = Counter(
            p.get("community_label") for p in j["papers"] if p.get("on_map")
        )
        print(
            f"  {j['name']}: {len(j['papers'])} GT "
            f"(in={nin}, out={nout}, on_map={nmap})"
        )
        print(f"    macro top: {macros.most_common(5)}")
    print(f"Written:     {out_path} ({out_path.stat().st_size/1024:.1f} KB)")
    return out_path


if __name__ == "__main__":
    import argparse

    ap = argparse.ArgumentParser(description="Build GT network map dashboard")
    ap.add_argument("--gt", type=Path, default=DEFAULT_GT)
    ap.add_argument("--scope-html", type=Path, default=None)
    ap.add_argument("--out", type=Path, default=OUT_HTML)
    args = ap.parse_args()
    build(gt_path=args.gt, scope_html=args.scope_html, out_path=args.out)
