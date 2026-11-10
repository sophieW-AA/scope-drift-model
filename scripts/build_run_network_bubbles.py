"""Frontiers-journal bubble map for the opportunity mapper's source run.

One HTML file: each bubble is a Frontiers journal. Colour is the macro or
meso community that journal mostly publishes in. Journals that share
communities sit next to each other.

    python scripts/build_run_network_bubbles.py
    python scripts/build_run_network_bubbles.py --run 20260827_081311
"""

from __future__ import annotations

import argparse
import json
import random
from pathlib import Path

import numpy as np
import pandas as pd

RUN = "20260827_081311"
PROJECT = "ocean-tech-adv-analytics-c-tfs"
DATASET = "raw_citation_network_data"
LABELS = "taxonomy_labelling"
LAYOUT_SEED = 42
OUT_DIR = Path.home() / "Documents" / "scope_drift_outputs" / "dashboards"
CACHE_DIR = Path.home() / "Documents" / "scope_drift_outputs" / "cache"
# Closest journals kept for the layout and the detail panel.
LAYOUT_NEIGHBOURS = 6
# Journals below this many papers in the run are not offered as close matches.
MIN_CANDIDATE_PAPERS = 30

# Brand accents first, then extra distinct colours so 19 macros stay separable.
PALETTE = [
    "#003BDE",
    "#279F94",
    "#E7323B",
    "#FF953E",
    "#856DF0",
    "#00A0DC",
    "#287863",
    "#7D0022",
    "#822907",
    "#2D1D7F",
    "#046379",
    "#91CF7A",
    "#001991",
    "#C45C26",
    "#5B8DEF",
    "#1F8A4C",
    "#8E3A6B",
    "#3D6B8C",
    "#545454",
    "#B8860B",
]


def client():
    from google.cloud import bigquery

    return bigquery.Client(project=PROJECT, location="EU")


def query(cli, sql: str) -> pd.DataFrame:
    job = cli.query(sql)
    df = job.to_dataframe()
    print(
        f"  {job.total_bytes_processed / 1e9:.2f} GB scanned, {len(df):,} rows",
        flush=True,
    )
    return df


def cache_dir(run: str) -> Path:
    path = CACHE_DIR / f"network_bubbles_{run}"
    path.mkdir(parents=True, exist_ok=True)
    return path


def load(cli, run: str, refresh: bool) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    cached = cache_dir(run)
    names = ("communities", "edges", "journals_all", "labels")
    paths = [cached / f"{name}.parquet" for name in names]
    if not refresh and all(path.exists() for path in paths):
        print(f"reading cache {cached}", flush=True)
        return tuple(pd.read_parquet(path) for path in paths)  # type: ignore[return-value]
    raw = f"{PROJECT}.{DATASET}"
    lab = f"{PROJECT}.{LABELS}"
    print("communities", flush=True)
    communities = query(
        cli,
        f"""
        SELECT
          CAST(c.meso AS INT64) AS meso,
          CAST(c.macro AS INT64) AS macro,
          EXTRACT(YEAR FROM SAFE.PARSE_DATE('%Y-%m-%d', SUBSTR(m.date, 1, 10))) AS yr,
          COUNT(*) AS n,
          COUNTIF(m.is_frontiers = 1) AS n_fi
        FROM `{raw}.classification_raw_{run}` c
        JOIN `{raw}.pub_metadata_raw_{run}` m ON c.int_id = m.int_id
        WHERE c.meso IS NOT NULL AND c.macro IS NOT NULL
        GROUP BY 1, 2, 3
        """,
    )
    print("citation edges (meso to meso)", flush=True)
    edges = query(
        cli,
        f"""
        SELECT
          LEAST(a.meso, b.meso) AS src,
          GREATEST(a.meso, b.meso) AS tgt,
          SUM(cl.weight) AS w
        FROM `{raw}.cit_links_raw_{run}` cl
        JOIN `{raw}.classification_raw_{run}` a ON cl.int_id1 = a.int_id
        JOIN `{raw}.classification_raw_{run}` b ON cl.int_id2 = b.int_id
        WHERE a.meso IS NOT NULL AND b.meso IS NOT NULL
          AND a.meso != b.meso
        GROUP BY 1, 2
        """,
    )
    print("journals per community, all publishers", flush=True)
    journals = query(
        cli,
        f"""
        SELECT
          CAST(c.meso AS INT64) AS meso,
          m.journal,
          COUNT(*) AS n,
          MAX(CAST(m.is_frontiers AS INT64)) AS is_fi
        FROM `{raw}.classification_raw_{run}` c
        JOIN `{raw}.pub_metadata_raw_{run}` m ON c.int_id = m.int_id
        WHERE c.meso IS NOT NULL
          AND m.journal IS NOT NULL
          AND m.journal != ''
        GROUP BY 1, 2
        """,
    )
    print("labels", flush=True)
    labels = query(
        cli,
        f"""
        SELECT 'meso' AS level, cluster_id, short_label
        FROM `{lab}.cluster_labels_meso_{run}`
        UNION ALL
        SELECT 'macro' AS level, cluster_id, short_label
        FROM `{lab}.cluster_labels_macro_{run}`
        """,
    )
    for name, frame in zip(names, (communities, edges, journals, labels)):
        frame.to_parquet(cached / f"{name}.parquet", index=False)
    print(f"cached {cached}", flush=True)
    return communities, edges, journals, labels


def layout(
    edges: pd.DataFrame, ids: list[int], sizes: dict[int, int]
) -> dict[int, tuple[float, float]]:
    """Place communities by citation affinity, not raw citation volume.

    Affinity is shared citation weight divided by the geometric mean of the
    two community sizes, so a large field is not pulled toward everything it
    touches. Only the strongest links are kept; a near-complete graph collapses
    to one blob under force-directed layout.
    """
    import igraph as ig

    index = {cid: i for i, cid in enumerate(ids)}
    usable = edges.copy()
    usable["src"] = usable["src"].astype(int)
    usable["tgt"] = usable["tgt"].astype(int)
    usable = usable[
        usable["src"].isin(index) & usable["tgt"].isin(index) & (usable["src"] != usable["tgt"])
    ]
    src_n = usable["src"].map(sizes).astype(float).clip(lower=1)
    tgt_n = usable["tgt"].map(sizes).astype(float).clip(lower=1)
    usable["aff"] = usable["w"].astype(float) / np.sqrt(src_n * tgt_n)

    ranked = pd.concat(
        [
            usable.sort_values(["src", "aff"], ascending=[True, False])
            .groupby("src", sort=False)
            .head(LAYOUT_NEIGHBOURS),
            usable.sort_values(["tgt", "aff"], ascending=[True, False])
            .groupby("tgt", sort=False)
            .head(LAYOUT_NEIGHBOURS),
        ],
        ignore_index=True,
    ).drop_duplicates(["src", "tgt"])

    pairs = [(index[int(r.src)], index[int(r.tgt)]) for r in ranked.itertuples(index=False)]
    weights = np.array([float(r.aff) for r in ranked.itertuples(index=False)], dtype=float)
    graph = ig.Graph(n=len(ids))
    if len(pairs) > 10:
        median = float(np.median(weights)) or 1.0
        graph.add_edges(pairs)
        graph.es["weight"] = (weights / median).tolist()
        random.seed(LAYOUT_SEED)
        np.random.seed(LAYOUT_SEED)
        coords = np.array(
            graph.layout_fruchterman_reingold(weights="weight", niter=800).coords
        )
        print(f"layout edges kept: {len(pairs):,}", flush=True)
    else:
        angles = np.linspace(0, 2 * np.pi, len(ids), endpoint=False)
        coords = np.column_stack([np.cos(angles), np.sin(angles)])
    # Percentiles, not the raw min and max: a few distant communities would
    # otherwise squash the rest of the map into the middle.
    low = np.percentile(coords, 3, axis=0)
    high = np.percentile(coords, 97, axis=0)
    span = np.maximum(high - low, 1e-9)
    coords = np.clip((coords - low) / span, 0, 1)
    coords = coords * 0.8 + 0.1
    return {cid: (float(coords[i, 0]), float(coords[i, 1])) for cid, i in index.items()}


def _load_borderline_cache(run: str) -> dict:
    """LLM borderline calls already stored for this run, keyed by journal."""
    path = CACHE_DIR / f"scope_llm_borderline_{run}_meso.json"
    if not path.is_file():
        return {}
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    return payload if isinstance(payload, dict) else {}


def _journal_communities(
    group: pd.DataFrame,
    meso_pos: dict[int, tuple[float, float]],
    cached: dict | None,
) -> tuple[list[dict], float, int]:
    """Scope colours for one journal, matching the scope dashboard.

    Green is the smallest set of communities covering 80% of the journal's
    papers. Amber is only a stored borderline call. Every other community
    the journal publishes in is out of scope. Proximity is not used: a broad
    journal's core already spans the map, so a distance rule turned the
    out-of-scope tail amber.
    """
    ordered = group.sort_values("n", ascending=False)
    total = int(ordered["n"].sum()) or 1
    primary: list[int] = []
    covered = 0
    for row in ordered.itertuples(index=False):
        primary.append(int(row.meso))
        covered += int(row.n)
        if covered >= total * 0.80:
            break
    primary_set = set(primary)
    cached_border: set[int] = set()
    if cached:
        stored_primary = {int(v) for v in cached.get("primary_ids") or []}
        if stored_primary:
            primary_set = stored_primary
        cached_border = {int(v) for v in cached.get("borderline_ids") or []}

    comms = []
    oos_papers = 0
    for row in ordered.itertuples(index=False):
        meso = int(row.meso)
        count = int(row.n)
        if meso not in meso_pos:
            continue
        if meso in primary_set:
            key = "p"
        elif meso in cached_border:
            key = "b"
        else:
            key = "o"
        if key == "o":
            oos_papers += count
        comms.append({"id": meso, "n": count, "k": key})
    oos_pct = round(100 * oos_papers / total, 1)
    n_border = sum(1 for item in comms if item["k"] == "b")
    return comms, oos_pct, n_border


def short_journal(name: str) -> str:
    """Full journal name, including the "Frontiers in" prefix."""
    return name


def meso_palette(rank: int) -> str:
    import colorsys

    hue = (rank * 137.508) % 360
    red, green, blue = colorsys.hls_to_rgb(hue / 360.0, 0.42, 0.62)
    return f"#{int(red * 255):02X}{int(green * 255):02X}{int(blue * 255):02X}"


def build_payload(
    communities: pd.DataFrame,
    edges: pd.DataFrame,
    journals: pd.DataFrame,
    labels: pd.DataFrame,
    run: str,
) -> dict:
    """One bubble per Frontiers journal, compared against every publisher.

    A journal's profile is its share of papers in each meso community, using
    all journals in the run. Similarity is cosine between those profiles, so
    100 means an identical community mix. Bubble positions come from the
    nearest Frontiers journals only; each journal's closest-journals list can
    name any publisher.
    """
    meso_labels = {
        int(row.cluster_id): str(row.short_label)
        for row in labels[labels["level"] == "meso"].itertuples(index=False)
        if pd.notna(row.short_label)
    }
    macro_labels = {
        int(row.cluster_id): str(row.short_label)
        for row in labels[labels["level"] == "macro"].itertuples(index=False)
        if pd.notna(row.short_label)
    }

    parent = (
        communities.assign(
            meso=communities["meso"].astype(int),
            macro=communities["macro"].astype(int),
        )
        .groupby(["meso", "macro"], as_index=False)["n"]
        .sum()
        .sort_values(["meso", "n"], ascending=[True, False])
        .drop_duplicates("meso")
    )
    meso_macro = dict(zip(parent["meso"], parent["macro"]))

    meso_sizes = (
        communities.assign(meso=communities["meso"].astype(int))
        .groupby("meso")["n"]
        .sum()
        .astype(int)
        .to_dict()
    )
    meso_ids = sorted(meso_macro)
    print(f"community layout: {len(meso_ids)} meso communities", flush=True)
    meso_pos = layout(edges, meso_ids, {m: int(meso_sizes.get(m, 1)) for m in meso_ids})
    borderline_cache = _load_borderline_cache(run)

    jr = journals.copy()
    jr["meso"] = jr["meso"].astype(int)
    jr["n"] = jr["n"].astype(int)
    jr["is_fi"] = jr["is_fi"].fillna(0).astype(int) == 1
    jr = jr[jr["meso"].isin(list(meso_macro.keys()))].copy()
    jr["macro"] = jr["meso"].map(meso_macro).astype(int)

    matrix = jr.pivot_table(
        index="journal", columns="meso", values="n", aggfunc="sum", fill_value=0
    )
    totals = matrix.sum(axis=1)
    all_names = list(matrix.index)
    shares = matrix.div(totals.where(totals > 0, 1), axis=0).to_numpy(dtype=float)
    norms = np.sqrt((shares ** 2).sum(axis=1))
    norms[norms == 0] = 1
    unit = shares / norms[:, None]

    fi_names = sorted(jr.loc[jr["is_fi"], "journal"].unique())
    pos = {name: i for i, name in enumerate(all_names)}
    fi_pos = {name: k for k, name in enumerate(fi_names)}
    fi_rows = np.array([pos[name] for name in fi_names])
    candidate = totals.to_numpy() >= MIN_CANDIDATE_PAPERS

    similarity = unit[fi_rows] @ unit.T
    similarity[np.arange(len(fi_rows)), fi_rows] = 0
    similarity[:, ~candidate] = 0

    nearest_all: dict[int, list[int]] = {}
    for f in range(len(fi_names)):
        order = np.argsort(-similarity[f])[:LAYOUT_NEIGHBOURS]
        nearest_all[f] = [int(a) for a in order if similarity[f, a] > 0]

    # Placement uses Frontiers-to-Frontiers overlap only, so bubbles sit near
    # the Frontiers journals they actually share communities with.
    fi_sim = similarity[:, fi_rows]
    link_rows = []
    for f in range(len(fi_names)):
        for g in np.argsort(-fi_sim[f])[:LAYOUT_NEIGHBOURS]:
            g = int(g)
            if g != f and fi_sim[f, g] > 0:
                src, tgt = (f, g) if f < g else (g, f)
                link_rows.append((src, tgt, float(fi_sim[f, g])))
    link_edges = (
        pd.DataFrame(link_rows, columns=["src", "tgt", "w"])
        .groupby(["src", "tgt"], as_index=False)["w"]
        .max()
    )
    ids = list(range(len(fi_names)))
    print(
        f"layout: {len(ids)} Frontiers journals, {len(link_edges):,} overlap edges",
        flush=True,
    )
    positions = layout(link_edges, ids, {i: 1 for i in ids})
    xs = np.array([positions[i][0] for i in ids])
    ys = np.array([positions[i][1] for i in ids])
    print(
        f"layout spread x {xs.min():.3f}-{xs.max():.3f} (std {xs.std():.3f})"
        f"  y {ys.min():.3f}-{ys.max():.3f} (std {ys.std():.3f})",
        flush=True,
    )

    papers = jr[jr["is_fi"]].copy()
    by_journal = {
        name: group.sort_values("n", ascending=False)
        for name, group in papers.groupby("journal")
    }
    dominant_meso = {}
    for name in fi_names:
        group = by_journal[name]
        top = group.iloc[0]
        total = int(totals[name])
        macro_counts = group.groupby("macro")["n"].sum().sort_values(ascending=False)
        dominant_meso[name] = {
            "n": total,
            "meso": int(top["meso"]),
            "meso_share": round(100 * int(top["n"]) / total, 1) if total else 0,
            "macro": int(macro_counts.index[0]),
            "top": [
                {
                    "label": meso_labels.get(int(row.meso), f"Community {int(row.meso)}"),
                    "n": int(row.n),
                    "share": round(100 * int(row.n) / total, 1) if total else 0,
                }
                for row in group.head(3).itertuples(index=False)
            ],
        }

    meso_rank = pd.Series(
        {name: info["meso"] for name, info in dominant_meso.items()}
    ).value_counts()
    meso_color = {
        int(meso): meso_palette(rank) for rank, meso in enumerate(meso_rank.index)
    }
    macro_papers = papers.groupby("macro")["n"].sum().sort_values(ascending=False)
    macros = []
    macro_color = {}
    for rank, (macro_id, n) in enumerate(macro_papers.items()):
        color = PALETTE[rank % len(PALETTE)]
        macro_color[int(macro_id)] = color
        macros.append(
            {
                "id": int(macro_id),
                "label": macro_labels.get(int(macro_id), f"Macro {int(macro_id)}"),
                "n": int(n),
                "color": color,
            }
        )

    bubbles = []
    for i, name in enumerate(fi_names):
        info = dominant_meso[name]
        near = [
            {
                "id": fi_pos.get(other),
                "name": other,
                "sim": round(100 * float(similarity[i, a]), 1),
            }
            for a in nearest_all[i]
            for other in [all_names[a]]
        ]
        comms, oos_pct, n_border = _journal_communities(
            by_journal[name], meso_pos, borderline_cache.get(name)
        )
        bubbles.append(
            {
                "id": i,
                "name": name,
                "short": name,
                "n": info["n"],
                "macro": info["macro"],
                "meso": info["meso"],
                "macroLabel": macro_labels.get(info["macro"], f"Macro {info['macro']}"),
                "mesoLabel": meso_labels.get(info["meso"], f"Community {info['meso']}"),
                "mesoShare": info["meso_share"],
                "mesoColor": meso_color[info["meso"]],
                "x": positions[i][0],
                "y": positions[i][1],
                "top": info["top"],
                "near": near,
                "comms": comms,
                "oosPct": oos_pct,
                "nBorder": n_border,
            }
        )

    for sample in (
        "Frontiers in Immunology",
        "Frontiers in Neurorobotics",
        "Frontiers in Chemistry",
    ):
        hit = next((bubble for bubble in bubbles if bubble["name"] == sample), None)
        if hit:
            close = ", ".join(
                f"{item['name']} ({item['sim']})" for item in hit["near"][:4]
            )
            print(
                f"  {hit['name']}: {hit['mesoLabel']} ({hit['mesoShare']}%)"
                f" / {hit['macroLabel']} | near {close}",
                flush=True,
            )

    return {
        "run": run,
        "macros": macros,
        "macroColor": {str(key): value for key, value in macro_color.items()},
        "journals": bubbles,
        "papers": int(papers["n"].sum()),
        "comms": [
            {
                "id": meso,
                "label": meso_labels.get(meso, f"Community {meso}"),
                "x": meso_pos[meso][0],
                "y": meso_pos[meso][1],
            }
            for meso in meso_ids
            if meso in meso_pos
        ],
    }


HTML = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Frontiers journals · __RUN__</title>
<script src="https://cdn.plot.ly/plotly-2.35.2.min.js"></script>
<style>
:root {
  --bg: #f6f8fa;
  --card: #ffffff;
  --text: #1a1f36;
  --muted: #5f6b7c;
  --border: #e3e7ee;
}
* { box-sizing: border-box; margin: 0; padding: 0; }
html, body { height: 100%; }
body {
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
  background: var(--bg);
  color: var(--text);
  display: flex;
  flex-direction: column;
  min-height: 100%;
}
header {
  background: var(--card);
  padding: 14px 20px 10px;
  border-bottom: 1px solid var(--border);
}
header h1 { font-size: 1.3rem; font-weight: 700; margin-bottom: 4px; }
header p { color: var(--muted); font-size: 0.84rem; max-width: 980px; }
.toolbar, .macro-toolbar {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 8px;
  margin-top: 10px;
}
.label { font-size: 0.75rem; color: var(--muted); font-weight: 600; }
.filter-btn, .search input {
  border: 1px solid var(--border);
  background: #fff;
  color: var(--text);
  border-radius: 999px;
  padding: 4px 10px;
  font-size: 0.75rem;
  cursor: pointer;
}
.search input { border-radius: 8px; min-width: 220px; cursor: text; padding: 6px 10px; }
.filter-btn.active { background: #1a1f36; color: #fff; border-color: #1a1f36; }
.swatch { display: inline-block; width: 8px; height: 8px; border-radius: 50%; margin-right: 6px; }
.hint { color: var(--muted); font-size: 0.75rem; }
.main { flex: 1; min-height: 0; display: flex; gap: 12px; padding: 12px; }
.card {
  background: var(--card);
  border: 1px solid var(--border);
  border-radius: 10px;
  min-height: 0;
  display: flex;
  flex-direction: column;
}
.plot-card { flex: 1; padding: 6px; }
.plot-wrap { flex: 1; min-height: 520px; position: relative; }
#plot { position: absolute; inset: 0; }
.detail {
  width: 340px;
  flex-shrink: 0;
  padding: 16px 16px 12px;
  overflow: auto;
}
.detail h2 { font-size: 1rem; line-height: 1.3; margin-bottom: 4px; }
.detail .meta { color: var(--muted); font-size: 0.8rem; margin-bottom: 12px; }
.detail h3 { font-size: 0.72rem; text-transform: uppercase; letter-spacing: 0.04em; color: var(--muted); margin: 14px 0 6px; }
.detail ul { list-style: none; }
.detail li, .near-btn {
  font-size: 0.84rem;
  padding: 4px 0;
  border-bottom: 1px solid var(--border);
}
.near-btn {
  display: flex;
  justify-content: space-between;
  gap: 8px;
  width: 100%;
  text-align: left;
  background: none;
  border: 0;
  border-bottom: 1px solid var(--border);
  color: var(--text);
  cursor: pointer;
  padding: 6px 0;
}
.near-btn:hover { color: #003BDE; }
.share { color: var(--muted); font-variant-numeric: tabular-nums; }
.tag { color: var(--muted); font-size: 0.7rem; margin-left: 4px; }
.near-btn:disabled { cursor: default; }
.near-btn:disabled:hover { color: var(--text); }
.empty { color: var(--muted); font-size: 0.86rem; }
</style>
</head>
<body>
<header>
  <h1>Frontiers journals in the scope-drift network</h1>
  <p>
    Run <strong>__RUN__</strong>, the snapshot behind the opportunity mapper.
    Each bubble is one Frontiers journal. Colour is the community it mostly publishes in.
    Click a journal to open its communities. Green is the core that holds 80% of its papers. Red is everything else it publishes in. Amber is a stored borderline call, which this run only has for a few journals.
    __N_JOURNALS__ journals · __PAPERS__ Frontiers papers.
  </p>
  <div class="toolbar">
    <span class="label">Colour:</span>
    <button type="button" class="filter-btn" id="backBtn" hidden>All journals</button>
    <button type="button" class="filter-btn active" id="colorMacro">Macro</button>
    <button type="button" class="filter-btn" id="colorMeso">Meso</button>
    <span class="label">Find:</span>
    <input id="search" class="search" type="search" placeholder="Journal or community" aria-label="Find a journal or community" />
    <span class="hint" id="stats"></span>
  </div>
  <div class="macro-toolbar" id="macroFilters">
    <span class="label">Macros:</span>
    <button type="button" class="filter-btn active" id="allMacrosBtn">All</button>
  </div>
</header>
<div class="main">
  <div class="card plot-card"><div class="plot-wrap"><div id="plot"></div></div></div>
  <aside class="card detail" id="detail">
    <p class="empty">Click a journal to see its communities on the map, coloured in-scope, borderline and out of scope.</p>
  </aside>
</div>
<script>
const DATA = __DATA_JSON__;
const J = DATA.journals;
const MACROS = DATA.macros;
const macroColor = DATA.macroColor;
const shown = {};
MACROS.forEach(m => { shown[m.id] = true; });
let colorMode = "macro";
let query = "";
let selected = null;

const statsEl = document.getElementById("stats");
const detail = document.getElementById("detail");
const macroFilters = document.getElementById("macroFilters");
const allMacrosBtn = document.getElementById("allMacrosBtn");

function sizePx(n, maxN) {
  if (n <= 0) return 0;
  return Math.max(9, Math.sqrt(n / Math.max(maxN, 1)) * 86);
}

function matches(j) {
  if (!query) return true;
  return j.short.toLowerCase().indexOf(query) >= 0
    || j.name.toLowerCase().indexOf(query) >= 0
    || j.mesoLabel.toLowerCase().indexOf(query) >= 0
    || j.macroLabel.toLowerCase().indexOf(query) >= 0;
}

function frame() {
  const near = new Set();
  if (selected != null) {
    near.add(selected);
    (J[selected].near || []).forEach(item => { if (item.id != null) near.add(item.id); });
  }
  let maxN = 1;
  const visible = [];
  J.forEach(j => {
    if (!shown[j.macro]) return;
    if (j.n > maxN) maxN = j.n;
    visible.push(j.n);
  });
  visible.sort((a, b) => b - a);
  const labelCut = visible[28] || 0;
  const x = [], y = [], sizes = [], colors = [], text = [], opacity = [], line = [], custom = [];
  let shownCount = 0;
  J.forEach(j => {
    const on = !!shown[j.macro] && matches(j);
    const focus = selected == null || near.has(j.id);
    if (on) shownCount += 1;
    x.push(j.y);
    y.push(-j.x);
    sizes.push(on ? sizePx(j.n, maxN) : 0);
    colors.push(colorMode === "meso" ? j.mesoColor : macroColor[String(j.macro)]);
    const named = on && (j.n >= labelCut || near.has(j.id));
    text.push(named ? j.short : "");
    opacity.push(!on ? 0 : (focus ? 0.8 : 0.1));
    line.push(j.id === selected ? 2.4 : 1);
    custom.push(j.id);
  });
  return {
    shownCount,
    trace: {
      type: "scatter",
      mode: "markers+text",
      x, y, text,
      customdata: custom,
      textposition: "top center",
      textfont: { size: 10, color: "#1a1f36" },
      hovertext: J.map(j => "<b>" + j.short + "</b><br>Community: " + j.mesoLabel
        + " (" + j.mesoShare + "% of its papers)<br>Macro: " + j.macroLabel
        + "<br>" + j.n.toLocaleString() + " papers<br>Closest: "
        + (j.near || []).slice(0, 3).map(n => n.name).join(", ")),
      hoverinfo: "text",
      marker: {
        size: sizes,
        sizemode: "diameter",
        color: colors,
        opacity,
        line: { color: "rgba(255,255,255,0.9)", width: line }
      }
    }
  };
}

const layout = {
  paper_bgcolor: "#ffffff",
  plot_bgcolor: "#ffffff",
  font: { family: '-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,sans-serif', color: "#1a1f36", size: 11 },
  autosize: true,
  xaxis: { showgrid: false, zeroline: false, showticklabels: false, showline: false },
  yaxis: { showgrid: false, zeroline: false, showticklabels: false, showline: false, scaleanchor: "x", scaleratio: 1 },
  margin: { l: 8, r: 8, t: 8, b: 8 },
  hovermode: "closest",
  showlegend: false
};
const config = { responsive: true, displayModeBar: false };

function draw() {
  const f = frame();
  Plotly.react("plot", [f.trace], layout, config);
  const mode = colorMode === "meso" ? "meso" : "macro";
  statsEl.textContent = f.shownCount.toLocaleString() + " journals · colour is main " + mode;
}

const COMM = {};
(DATA.comms || []).forEach(c => { COMM[c.id] = c; });
const SCOPE = {
  p: { color: "#1f8a4c", name: "Primary in-scope" },
  b: { color: "#d4a300", name: "Borderline" },
  o: { color: "#c93030", name: "Out of scope" }
};

function drawCommunities(j) {
  const rows = j.comms || [];
  const maxN = Math.max.apply(null, rows.map(c => c.n).concat([1]));
  const traces = ["p", "b", "o"].map(key => {
    const subset = rows.filter(c => c.k === key && COMM[c.id]);
    return {
      type: "scatter",
      mode: "markers+text",
      name: SCOPE[key].name,
      x: subset.map(c => COMM[c.id].y),
      y: subset.map(c => -COMM[c.id].x),
      text: subset.map(c => c.n >= maxN * 0.16 ? COMM[c.id].label : ""),
      textposition: "top center",
      textfont: { size: 11, color: "#1a1f36" },
      hovertext: subset.map(c => "<b>" + COMM[c.id].label + "</b><br>"
        + c.n.toLocaleString() + " papers<br>" + SCOPE[key].name),
      hoverinfo: "text",
      marker: {
        size: subset.map(c => Math.max(12, Math.sqrt(c.n / maxN) * 120)),
        sizemode: "diameter",
        color: SCOPE[key].color,
        opacity: 0.58,
        line: { color: "rgba(255,255,255,0.85)", width: 1.4 }
      }
    };
  });
  Plotly.react("plot", traces, {
    paper_bgcolor: "#ffffff",
    plot_bgcolor: "#ffffff",
    font: layout.font,
    autosize: true,
    showlegend: true,
    legend: { orientation: "h", y: -0.06, font: { size: 12 } },
    margin: { l: 16, r: 16, t: 12, b: 48 },
    hovermode: "closest",
    xaxis: layout.xaxis,
    yaxis: layout.yaxis
  }, config);
}

function renderDetail(id) {
  const j = J[id];
  const communities = (j.top || []).map(c =>
    "<li><span>" + c.label + "</span> <span class='share'>" + c.share + "%</span></li>"
  ).join("");
  const near = (j.near || []).map(n => {
    const other = n.id == null;
    const tag = other ? " <span class='tag'>other publisher</span>" : "";
    return "<button type='button' class='near-btn' data-id='" + (other ? "" : n.id) + "'"
      + (other ? " disabled" : "") + "><span>" + n.name + tag + "</span><span class='share'>" + n.sim + "</span></button>";
  }).join("");
  detail.innerHTML =
    "<h2>" + j.short + "</h2>"
    + "<p class='meta'>" + j.n.toLocaleString() + " papers · "
    + j.oosPct + "% out of scope · " + j.nBorder + " borderline</p>"
    + "<h3>Main community</h3>"
    + "<p>" + j.mesoLabel + " <span class='share'>(" + j.mesoShare + "%)</span></p>"
    + "<p class='meta'>Macro: " + j.macroLabel + "</p>"
    + "<h3>Where its papers sit</h3><ul>" + communities + "</ul>"
    + "<h3>Closest journals</h3>" + near
    + "<p class='meta' style='margin-top:10px'>Across every publisher in the run. 100 = identical community mix.</p>";
  detail.querySelectorAll(".near-btn").forEach(btn => {
    btn.addEventListener("click", () => select(Number(btn.dataset.id)));
  });
}

function select(id) {
  selected = id;
  document.getElementById("backBtn").hidden = false;
  renderDetail(id);
  drawCommunities(J[id]);
  statsEl.textContent = J[id].name;
}

function clearSelection() {
  selected = null;
  document.getElementById("backBtn").hidden = true;
  detail.innerHTML = "<p class='empty'>Click a journal to see its communities on the map, coloured in-scope, borderline and out of scope.</p>";
  draw();
}

MACROS.forEach(m => {
  const btn = document.createElement("button");
  btn.type = "button";
  btn.className = "filter-btn active";
  btn.dataset.macro = String(m.id);
  btn.innerHTML = '<span class="swatch" style="background:' + m.color + '"></span>' + m.label;
  btn.title = "Double-click to keep only this macro";
  macroFilters.appendChild(btn);
  btn.addEventListener("click", () => {
    shown[m.id] = !shown[m.id];
    syncMacros();
    draw();
  });
  btn.addEventListener("dblclick", (ev) => {
    ev.preventDefault();
    MACROS.forEach(other => { shown[other.id] = other.id === m.id; });
    syncMacros();
    draw();
  });
});

function syncMacros() {
  macroFilters.querySelectorAll("button[data-macro]").forEach(btn => {
    btn.classList.toggle("active", !!shown[btn.dataset.macro]);
  });
  allMacrosBtn.classList.toggle("active", MACROS.every(m => shown[m.id]));
}

document.getElementById("backBtn").addEventListener("click", () => clearSelection());
allMacrosBtn.addEventListener("click", () => {
  MACROS.forEach(m => { shown[m.id] = true; });
  syncMacros();
  draw();
});
document.getElementById("colorMacro").addEventListener("click", () => {
  colorMode = "macro";
  document.getElementById("colorMacro").classList.add("active");
  document.getElementById("colorMeso").classList.remove("active");
  draw();
});
document.getElementById("colorMeso").addEventListener("click", () => {
  colorMode = "meso";
  document.getElementById("colorMeso").classList.add("active");
  document.getElementById("colorMacro").classList.remove("active");
  draw();
});
document.getElementById("search").addEventListener("input", (ev) => {
  query = ev.target.value.trim().toLowerCase();
  draw();
});
window.addEventListener("resize", () => Plotly.Plots.resize("plot"));

Plotly.newPlot("plot", [frame().trace], layout, config).then(gd => {
  gd.on("plotly_click", ev => {
    if (selected != null) return;
    if (!ev.points || !ev.points.length || ev.points[0].customdata == null) return;
    select(ev.points[0].customdata);
  });
  gd.on("plotly_doubleclick", () => clearSelection());
  draw();
});
</script>
</body>
</html>
"""


def write_html(payload: dict, path: Path) -> None:
    html = HTML.replace("__RUN__", payload["run"])
    html = html.replace("__PAPERS__", f"{payload['papers']:,}")
    html = html.replace("__N_JOURNALS__", f"{len(payload['journals']):,}")
    html = html.replace("__DATA_JSON__", json.dumps(payload, separators=(",", ":")))
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(html, encoding="utf-8")
    print(f"wrote {path} ({path.stat().st_size / 1024:.0f} KB)", flush=True)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run", default=RUN)
    parser.add_argument("--out", default="")
    parser.add_argument("--refresh", action="store_true")
    args = parser.parse_args()
    out = (
        Path(args.out)
        if args.out
        else OUT_DIR / f"network_bubbles_{args.run}.html"
    )
    communities, edges, journals, labels = load(client(), args.run, args.refresh)
    payload = build_payload(communities, edges, journals, labels, args.run)
    write_html(payload, out)


if __name__ == "__main__":
    main()
