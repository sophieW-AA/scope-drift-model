"""
Local dashboard for the author citation network.

Network tab: macro communities, then zoom to meso, micro, and authors.
Details tab: one author, their strongest links, and the strongest links of
those people. Line thickness is the connection weight. Blue is a citation
link. Teal means those authors also coauthored a paper in this run.

    python src/author_network_dashboard.py --timestamp 20261023_114612

Then open http://127.0.0.1:8765
"""

from __future__ import annotations

import argparse
import json
import re
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlparse

from google.cloud import bigquery

BQ_PROJECT = "ocean-tech-adv-analytics-c-tfs"
BQ_DATASET = "raw_citation_network_data_person"
AIRAK_PUBLICATION = "ocean-breeze-tier-1.airak.Publication"
DEFAULT_TIMESTAMP = "20261023_114612"
HOP1_LIMIT = 12
HOP2_LIMIT = 5
PAPER_LIMIT = 80
AUTHORS_IN_MICRO = 40

TIMESTAMP = DEFAULT_TIMESTAMP
CLIENT: bigquery.Client | None = None
CACHE: dict = {}
INFLIGHT: dict = {}
CACHE_LOCK = threading.Lock()


def table(name: str) -> str:
    if not re.fullmatch(r"\d{8}_\d{6}", TIMESTAMP):
        raise SystemExit(f"Timestamp must look like YYYYMMDD_HHMMSS, got {TIMESTAMP!r}")
    return f"`{BQ_PROJECT}.{BQ_DATASET}.{name}_person_{TIMESTAMP}`"


def client() -> bigquery.Client:
    global CLIENT
    if CLIENT is None:
        CLIENT = bigquery.Client(project=BQ_PROJECT, location="EU")
    return CLIENT


def clean(value):
    if value is None or isinstance(value, (str, bool)):
        return value
    if isinstance(value, int) and not isinstance(value, bool):
        return value
    if isinstance(value, float):
        return value
    try:
        number = float(value)
    except (TypeError, ValueError):
        return str(value)
    if number.is_integer():
        return int(number)
    return number


def query(sql: str, params: list | None = None) -> list[dict]:
    job = client().query(
        sql,
        job_config=bigquery.QueryJobConfig(query_parameters=params or []),
    )
    rows = []
    for row in job.result():
        item = {}
        for key, value in row.items():
            if key in ("author_id", "publication_id"):
                item[key] = None if value is None else str(value)
            else:
                item[key] = clean(value)
        rows.append(item)
    print(f"Query finished, {job.total_bytes_processed or 0:,} bytes", flush=True)
    return rows


def cached(key: str, build):
    with CACHE_LOCK:
        if key in CACHE:
            return CACHE[key]
        pending = INFLIGHT.get(key)
        if pending is None:
            pending = threading.Event()
            INFLIGHT[key] = pending
            owner = True
        else:
            owner = False
    if not owner:
        pending.wait()
        with CACHE_LOCK:
            if key in CACHE:
                return CACHE[key]
            error = INFLIGHT.get(key + ":error")
        if error:
            raise error
        raise RuntimeError(f"Cache build failed for {key}")
    try:
        value = build()
    except Exception as exc:
        with CACHE_LOCK:
            INFLIGHT[key + ":error"] = exc
            INFLIGHT.pop(key, None)
        pending.set()
        raise
    with CACHE_LOCK:
        CACHE[key] = value
        INFLIGHT.pop(key, None)
        INFLIGHT.pop(key + ":error", None)
    pending.set()
    return value


def marked_links_cte() -> str:
    """One row per author pair. Weight is split by coauthorship in this run."""
    return f"""
    link AS (
      SELECT int_id1 AS a, int_id2 AS b, weight
      FROM {table("cit_links_raw")}
      WHERE int_id1 < int_id2
    ),
    coauthor AS (
      SELECT pa.int_id AS a, pb.int_id AS b
      FROM {table("author_papers")} pa
      JOIN {table("author_papers")} pb
        ON pa.publication_id = pb.publication_id
       AND pa.int_id < pb.int_id
      GROUP BY 1, 2
    ),
    marked AS (
      SELECT
        link.a,
        link.b,
        IF(coauthor.a IS NULL, link.weight, 0) AS citation_only,
        IF(coauthor.a IS NULL, 0, link.weight) AS with_coauthor
      FROM link
      LEFT JOIN coauthor
        ON coauthor.a = link.a AND coauthor.b = link.b
    )
    """


def community_nodes(level: str, where_sql: str, params: list) -> list[dict]:
    sql = f"""
    SELECT
      {level} AS id,
      ANY_VALUE(macro) AS macro,
      ANY_VALUE(meso) AS meso,
      COUNT(*) AS n_authors
    FROM {table("classification_raw")}
    WHERE {level} IS NOT NULL
      {where_sql}
    GROUP BY id
    ORDER BY n_authors DESC
    """
    return query(sql, params)


def community_edges(group_col: str, where_sql: str, params: list) -> list[dict]:
    sql = f"""
    WITH {marked_links_cte()}
    SELECT
      LEAST(c1.{group_col}, c2.{group_col}) AS source,
      GREATEST(c1.{group_col}, c2.{group_col}) AS target,
      SUM(marked.citation_only) AS citation_only,
      SUM(marked.with_coauthor) AS with_coauthor
    FROM marked
    JOIN {table("classification_raw")} c1 ON c1.int_id = marked.a
    JOIN {table("classification_raw")} c2 ON c2.int_id = marked.b
    WHERE c1.{group_col} IS NOT NULL
      AND c2.{group_col} IS NOT NULL
      {where_sql}
    GROUP BY source, target
    """
    return query(sql, params)


def network_macro() -> dict:
    nodes = community_nodes("macro", "", [])
    edges = community_edges("macro", "", [])
    return {"level": "macro", "nodes": nodes, "edges": edges, "truncated": False}


def network_meso(macro_id: int) -> dict:
    params = [bigquery.ScalarQueryParameter("macro", "INT64", macro_id)]
    nodes = community_nodes("meso", "AND macro = @macro", params)
    edges = community_edges(
        "meso",
        "AND c1.macro = @macro AND c2.macro = @macro",
        params,
    )
    return {"level": "meso", "macro": macro_id, "nodes": nodes, "edges": edges, "truncated": False}


def network_micro(meso_id: int) -> dict:
    params = [bigquery.ScalarQueryParameter("meso", "INT64", meso_id)]
    nodes = community_nodes("micro", "AND meso = @meso", params)
    edges = community_edges(
        "micro",
        "AND c1.meso = @meso AND c2.meso = @meso",
        params,
    )
    parent = query(
        f"""
        SELECT macro, COUNT(*) AS n_authors
        FROM {table("classification_raw")}
        WHERE meso = @meso
        GROUP BY macro
        ORDER BY n_authors DESC
        LIMIT 1
        """,
        params,
    )
    return {
        "level": "micro",
        "meso": meso_id,
        "macro": parent[0]["macro"] if parent else None,
        "nodes": nodes,
        "edges": edges,
        "truncated": False,
    }


def network_authors(micro_id: int) -> dict:
    params = [bigquery.ScalarQueryParameter("micro", "INT64", micro_id)]
    counted = query(
        f"""
        SELECT COUNT(*) AS n_authors, ANY_VALUE(meso) AS meso, ANY_VALUE(macro) AS macro
        FROM {table("classification_raw")}
        WHERE micro = @micro
        """,
        params,
    )
    n_authors = int(counted[0]["n_authors"]) if counted else 0
    nodes = query(
        f"""
        WITH members AS (
          SELECT int_id
          FROM {table("classification_raw")}
          WHERE micro = @micro
        ),
        strength AS (
          SELECT l.int_id1 AS int_id, SUM(l.weight) AS strength
          FROM {table("cit_links_raw")} l
          JOIN members me ON me.int_id = l.int_id1
          JOIN members other ON other.int_id = l.int_id2
          GROUP BY int_id
        )
        SELECT
          m.int_id AS id,
          meta.name,
          meta.author_id,
          c.macro,
          c.meso,
          c.micro,
          IFNULL(strength.strength, 0) AS strength
        FROM members m
        JOIN {table("pub_metadata_raw")} meta USING (int_id)
        JOIN {table("classification_raw")} c USING (int_id)
        LEFT JOIN strength USING (int_id)
        ORDER BY strength DESC, m.int_id
        LIMIT {AUTHORS_IN_MICRO}
        """,
        params,
    )
    ids = [int(node["id"]) for node in nodes]
    edges = edges_among(ids) if ids else []
    return {
        "level": "author",
        "micro": micro_id,
        "meso": counted[0]["meso"] if counted else None,
        "macro": counted[0]["macro"] if counted else None,
        "nodes": nodes,
        "edges": edges,
        "n_authors": n_authors,
        "truncated": n_authors > len(nodes),
    }


def edges_among(ids: list[int]) -> list[dict]:
    params = [bigquery.ArrayQueryParameter("ids", "INT64", ids)]
    return query(
        f"""
        WITH link AS (
          SELECT int_id1 AS a, int_id2 AS b, weight
          FROM {table("cit_links_raw")}
          WHERE int_id1 < int_id2
            AND int_id1 IN UNNEST(@ids)
            AND int_id2 IN UNNEST(@ids)
        ),
        coauthor AS (
          SELECT pa.int_id AS a, pb.int_id AS b
          FROM {table("author_papers")} pa
          JOIN {table("author_papers")} pb
            ON pa.publication_id = pb.publication_id
           AND pa.int_id < pb.int_id
          WHERE pa.int_id IN UNNEST(@ids)
            AND pb.int_id IN UNNEST(@ids)
          GROUP BY 1, 2
        )
        SELECT
          link.a AS source,
          link.b AS target,
          IF(coauthor.a IS NULL, link.weight, 0) AS citation_only,
          IF(coauthor.a IS NULL, 0, link.weight) AS with_coauthor
        FROM link
        LEFT JOIN coauthor
          ON coauthor.a = link.a AND coauthor.b = link.b
        """,
        params,
    )


def search_authors(text: str) -> list[dict]:
    needle = text.strip()
    if len(needle) < 2:
        return []
    return query(
        f"""
        SELECT m.int_id, m.author_id, m.name, c.macro, c.meso, c.micro
        FROM {table("pub_metadata_raw")} m
        LEFT JOIN {table("classification_raw")} c USING (int_id)
        WHERE STRPOS(LOWER(m.name), LOWER(@q)) > 0
        ORDER BY m.name
        LIMIT 25
        """,
        [bigquery.ScalarQueryParameter("q", "STRING", needle)],
    )


def author_view(int_id: int) -> dict:
    profiles = query(
        f"""
        SELECT m.int_id, m.author_id, m.name, c.macro, c.meso, c.micro
        FROM {table("pub_metadata_raw")} m
        LEFT JOIN {table("classification_raw")} c USING (int_id)
        WHERE m.int_id = @int_id
        """,
        [bigquery.ScalarQueryParameter("int_id", "INT64", int_id)],
    )
    if not profiles:
        return {}
    first = query(
        f"""
        SELECT
          l.int_id2 AS int_id,
          l.weight,
          (SELECT COUNT(*) FROM {table("cit_links_raw")} WHERE int_id1 = @int_id) AS n_neighbors
        FROM {table("cit_links_raw")} l
        WHERE l.int_id1 = @int_id
        ORDER BY l.weight DESC
        LIMIT {HOP1_LIMIT}
        """,
        [bigquery.ScalarQueryParameter("int_id", "INT64", int_id)],
    )
    n_neighbors = int(first[0]["n_neighbors"]) if first else 0
    hop1_ids = [int(row["int_id"]) for row in first]
    second = []
    if hop1_ids:
        second = query(
            f"""
            SELECT int_id1, int_id2, weight
            FROM {table("cit_links_raw")}
            WHERE int_id1 IN UNNEST(@ids)
            QUALIFY ROW_NUMBER() OVER (PARTITION BY int_id1 ORDER BY weight DESC) <= {HOP2_LIMIT}
            """,
            [bigquery.ArrayQueryParameter("ids", "INT64", hop1_ids)],
        )
    node_ids = {int_id, *hop1_ids}
    for row in second:
        node_ids.add(int(row["int_id2"]))
    people = query(
        f"""
        SELECT m.int_id, m.author_id, m.name, c.macro, c.meso, c.micro
        FROM {table("pub_metadata_raw")} m
        LEFT JOIN {table("classification_raw")} c USING (int_id)
        WHERE m.int_id IN UNNEST(@ids)
        """,
        [bigquery.ArrayQueryParameter("ids", "INT64", sorted(node_ids))],
    )
    by_id = {int(row["int_id"]): row for row in people}
    nodes = []
    center = dict(by_id.get(int_id, profiles[0]))
    center["hop"] = 0
    nodes.append(center)
    for author_id in hop1_ids:
        row = dict(by_id.get(author_id, {"int_id": author_id, "name": None}))
        row["hop"] = 1
        nodes.append(row)
    for row in second:
        other = int(row["int_id2"])
        if other == int_id or other in hop1_ids:
            continue
        if any(int(node["int_id"]) == other for node in nodes):
            continue
        person = dict(by_id.get(other, {"int_id": other, "name": None}))
        person["hop"] = 2
        nodes.append(person)
    edge_map: dict[tuple[int, int], float] = {}
    for row in first:
        pair = tuple(sorted((int_id, int(row["int_id"]))))
        edge_map[pair] = float(row["weight"])
    shown = {int(node["int_id"]) for node in nodes}
    for row in second:
        source = int(row["int_id1"])
        target = int(row["int_id2"])
        if target not in shown or source not in shown:
            continue
        pair = tuple(sorted((source, target)))
        edge_map[pair] = max(edge_map.get(pair, 0), float(row["weight"]))
    coauthored = set()
    if len(shown) > 1:
        pairs = query(
            f"""
            SELECT pa.int_id AS a, pb.int_id AS b
            FROM {table("author_papers")} pa
            JOIN {table("author_papers")} pb
              ON pa.publication_id = pb.publication_id
             AND pa.int_id < pb.int_id
            WHERE pa.int_id IN UNNEST(@ids)
              AND pb.int_id IN UNNEST(@ids)
            GROUP BY 1, 2
            """,
            [bigquery.ArrayQueryParameter("ids", "INT64", sorted(shown))],
        )
        coauthored = {(int(row["a"]), int(row["b"])) for row in pairs}
    edges = []
    for (source, target), weight in edge_map.items():
        shared = (source, target) in coauthored
        edges.append(
            {
                "source": source,
                "target": target,
                "citation_only": 0 if shared else weight,
                "with_coauthor": weight if shared else 0,
            }
        )
    papers = query(
        f"""
        SELECT publication_id, MAX(role_weight) AS role_weight
        FROM {table("author_papers")}
        WHERE int_id = @int_id
        GROUP BY publication_id
        """,
        [bigquery.ScalarQueryParameter("int_id", "INT64", int_id)],
    )
    titles = paper_titles()
    for row in papers:
        info = titles.get(row["publication_id"], {})
        row["title"] = info.get("title")
        row["year"] = info.get("year")
        row["doi"] = info.get("doi")
    papers.sort(key=lambda row: (row["year"] is None, -(row["year"] or 0), int(row["publication_id"])))
    n_papers = len(papers)
    papers = papers[:PAPER_LIMIT]
    return {
        "author": profiles[0],
        "nodes": nodes,
        "edges": edges,
        "n_neighbors": n_neighbors,
        "shown_neighbors": len(hop1_ids),
        "papers": papers,
        "n_papers": n_papers,
    }


def load_paper_titles() -> dict:
    """One read of publication titles. Later author clicks reuse this."""
    rows = query(
        f"""
        SELECT
          p.PublicationId AS publication_id,
          p.Title AS title,
          p.PublishedYear AS year,
          p.Doi AS doi
        FROM `{AIRAK_PUBLICATION}` p
        WHERE p.PublicationId IN (
          SELECT DISTINCT publication_id
          FROM {table("author_papers")}
        )
        """
    )
    found = {
        row["publication_id"]: {"title": row["title"], "year": row["year"], "doi": row["doi"]}
        for row in rows
    }
    print(f"Paper titles loaded: {len(found):,}", flush=True)
    return found


def paper_titles() -> dict:
    try:
        return cached("paper-titles", load_paper_titles)
    except Exception as exc:
        print(f"Paper titles unavailable: {exc}", flush=True)
        return {}


def communities(level: str, macro_id: int | None, meso_id: int | None) -> list[dict]:
    where = []
    params = []
    if macro_id is not None and level != "macro":
        where.append("AND macro = @macro")
        params.append(bigquery.ScalarQueryParameter("macro", "INT64", macro_id))
    if meso_id is not None and level == "micro":
        where.append("AND meso = @meso")
        params.append(bigquery.ScalarQueryParameter("meso", "INT64", meso_id))
    return community_nodes(level, " ".join(where), params)


def build_network(level: str, macro_id: int | None, meso_id: int | None, micro_id: int | None) -> dict:
    if level == "macro":
        return cached("network-macro", network_macro)
    if level == "meso":
        if macro_id is None:
            raise ValueError("meso network needs a macro id")
        return cached(f"network-meso-{macro_id}", lambda: network_meso(macro_id))
    if level == "micro":
        if meso_id is None:
            raise ValueError("micro network needs a meso id")
        return cached(f"network-micro-{meso_id}", lambda: network_micro(meso_id))
    if level == "author":
        if micro_id is None:
            raise ValueError("author network needs a micro id")
        return cached(f"network-author-{micro_id}", lambda: network_authors(micro_id))
    raise ValueError(f"Unknown level {level}")


PAGE = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Author citation network</title>
<style>
  :root {
    --blue: #003BDE;
    --blue-dark: #001991;
    --teal: #279F94;
    --ink: #282828;
    --muted: #545454;
    --faint: #6B6B6B;
    --line: #F0F0F0;
    --paper: #F7F7F7;
    --white: #FFFFFF;
  }
  * { box-sizing: border-box; }
  body {
    margin: 0;
    color: var(--ink);
    background: var(--white);
    font-family: "Museo Sans 300", Calibri, Arial, "Helvetica Neue", Helvetica, sans-serif;
  }
  header { padding: 18px 28px 8px; }
  h1 {
    margin: 0 0 4px;
    font-size: 22px;
    color: var(--blue);
    font-family: "Museo Sans 500", Calibri, Arial, "Helvetica Neue", Helvetica, sans-serif;
  }
  header p { margin: 0; color: var(--muted); font-size: 14px; }
  .tabs { display: flex; gap: 8px; padding: 12px 28px 0; }
  .tabs button, .crumb button, .filters button, .linkish {
    font: inherit;
    cursor: pointer;
  }
  .tabs button {
    background: var(--paper);
    color: var(--muted);
    border: 1px solid var(--line);
    border-bottom: 0;
    border-radius: 4px 4px 0 0;
    padding: 8px 14px;
  }
  .tabs button.active { background: var(--white); color: var(--blue-dark); font-weight: 600; }
  .panel { display: none; border-top: 1px solid var(--line); }
  .panel.active { display: block; }
  .crumb { display: flex; gap: 6px; align-items: center; padding: 12px 28px; color: var(--faint); flex-wrap: wrap; }
  .crumb button { background: transparent; border: 0; color: var(--blue); padding: 0; }
  .network-layout, .details-layout { display: grid; min-height: calc(100vh - 150px); }
  .network-layout { grid-template-columns: 320px 1fr; }
  .details-layout { grid-template-columns: 1fr 360px; }
  .side, .detail { border-left: 1px solid var(--line); overflow: auto; }
  .network-layout .side { border-left: 0; border-right: 1px solid var(--line); }
  .filters { display: flex; flex-direction: column; gap: 8px; padding: 12px 16px; background: var(--paper); }
  select, input {
    border: 1px solid #ACACAC;
    border-radius: 4px;
    padding: 8px 10px;
    font: inherit;
    color: var(--ink);
    background: var(--white);
  }
  .search { display: flex; gap: 8px; padding: 14px 28px; background: var(--paper); }
  .search input { flex: 1; }
  button.primary { background: var(--blue); color: white; border: 0; border-radius: 4px; padding: 8px 14px; }
  button.primary:hover { background: var(--blue-dark); }
  .graph { position: relative; }
  svg { width: 100%; height: calc(100vh - 190px); min-height: 560px; display: block; }
  .status { position: absolute; left: 16px; top: 12px; color: var(--muted); font-size: 14px; max-width: 420px; }
  .legend { position: absolute; right: 16px; bottom: 16px; background: var(--white); border: 1px solid var(--line); padding: 8px 10px; font-size: 12px; color: var(--muted); }
  .swatch { display: inline-block; width: 18px; height: 3px; margin-right: 6px; vertical-align: middle; }
  ul { list-style: none; margin: 0; padding: 0 8px 20px; }
  li button.linkish, .paper button.linkish {
    width: 100%;
    text-align: left;
    background: transparent;
    color: var(--ink);
    border: 0;
    border-radius: 4px;
    padding: 8px 10px;
  }
  li button.linkish:hover, .paper button.linkish:hover { background: var(--paper); color: var(--blue-dark); }
  .meta { display: block; color: var(--faint); font-size: 12px; }
  .bar { height: 4px; background: var(--line); margin-top: 4px; }
  .bar span { display: block; height: 4px; background: var(--blue); }
  .person { padding: 8px 16px 24px; }
  .person h2 { margin: 0 0 6px; font-size: 20px; color: var(--blue-dark); }
  .chips { display: flex; gap: 6px; flex-wrap: wrap; margin: 8px 0 12px; }
  .chip { background: var(--paper); border: 1px solid var(--line); border-radius: 99px; padding: 3px 8px; font-size: 12px; color: var(--muted); }
  .paper { padding: 8px 0; border-top: 1px solid var(--line); }
  .paper strong { display: block; }
  .paper span, .empty { color: var(--faint); font-size: 13px; }
  h3 { margin: 16px 0 8px; font-size: 13px; letter-spacing: 0.04em; text-transform: uppercase; color: var(--faint); }
  a { color: var(--blue); }
</style>
</head>
<body>
<header>
  <h1>Author citation network</h1>
  <p>Run __TIMESTAMP__. Line thickness is the connection weight. Blue is a citation. Teal means the authors also coauthored a paper in this run.</p>
</header>
<nav class="tabs">
  <button type="button" id="tab-network" class="active">Network</button>
  <button type="button" id="tab-details">Details</button>
</nav>
<section id="network" class="panel active">
  <div class="crumb" id="crumb"></div>
  <div class="network-layout">
    <aside class="side">
      <div class="filters">
        <select id="list-level">
          <option value="macro">Macro communities</option>
          <option value="meso">Meso communities</option>
          <option value="micro">Micro communities</option>
        </select>
        <select id="list-macro" hidden></select>
        <select id="list-meso" hidden></select>
        <select id="list-sort">
          <option value="size-desc">Largest first</option>
          <option value="size-asc">Smallest first</option>
          <option value="id">Community number</option>
        </select>
      </div>
      <ul id="community-list"></ul>
    </aside>
    <div class="graph">
      <div class="status" id="network-status">Loading the macro map. The first query can take a few minutes.</div>
      <svg id="network-svg" viewBox="0 0 900 700"></svg>
      <div class="legend">
        <div><span class="swatch" style="background:#003BDE"></span>Citation only</div>
        <div><span class="swatch" style="background:#279F94"></span>Citation and coauthorship</div>
        <div>Circle size is the number of authors. A ring is links inside the community.</div>
      </div>
    </div>
  </div>
</section>
<section id="details" class="panel">
  <form class="search" id="search-form">
    <input id="q" type="search" placeholder="Search an author name" autocomplete="off">
    <button class="primary" type="submit">Search</button>
  </form>
  <div class="details-layout">
    <div class="graph">
      <div class="status" id="details-status">Search for an author. The view shows their links, and the links of those people.</div>
      <svg id="details-svg" viewBox="0 0 900 700"></svg>
      <div class="legend">
        <div><span class="swatch" style="background:#003BDE"></span>Citation only</div>
        <div><span class="swatch" style="background:#279F94"></span>Citation and coauthorship</div>
        <div>Inner ring: their links. Outer ring: links of those people. Thickness is connection weight.</div>
      </div>
    </div>
    <aside class="detail" id="detail"><p class="empty">No author selected.</p></aside>
  </div>
</section>
<script>
const COLORS = ["#003BDE", "#279F94", "#856DF0", "#E7323B", "#FF953E", "#00A0DC", "#91CF7A", "#001991", "#31C7D1", "#046379"];
const netState = { level: "macro", macro: null, meso: null, micro: null };
let macroOptions = [];
let mesoOptions = [];

function clear(node) { while (node.firstChild) node.removeChild(node.firstChild); }
function el(tag, text, className) {
  const node = document.createElement(tag);
  if (className) node.className = className;
  if (text !== undefined && text !== null) node.textContent = String(text);
  return node;
}
function colorFor(macro) {
  if (macro === null || macro === undefined) return "#ACACAC";
  return COLORS[Number(macro) % COLORS.length];
}
function communityText(row) {
  if (row.macro === null || row.macro === undefined) return "Outside the largest component";
  return "Macro " + row.macro + " · Meso " + row.meso + " · Micro " + row.micro;
}
function weightWidth(value, maxWeight) {
  if (!value || !maxWeight) return 0;
  return 1 + 12 * Math.sqrt(value / maxWeight);
}

document.getElementById("tab-network").addEventListener("click", () => showTab("network"));
document.getElementById("tab-details").addEventListener("click", () => showTab("details"));
function showTab(name) {
  document.getElementById("tab-network").classList.toggle("active", name === "network");
  document.getElementById("tab-details").classList.toggle("active", name === "details");
  document.getElementById("network").classList.toggle("active", name === "network");
  document.getElementById("details").classList.toggle("active", name === "details");
}

function drawEdges(svg, nodes, edges) {
  const byId = new Map(nodes.map((node) => [Number(node.id), node]));
  const totals = edges.map((edge) => Number(edge.citation_only) + Number(edge.with_coauthor));
  const maxWeight = Math.max(...totals, 0);
  edges.forEach((edge) => {
    const only = Number(edge.citation_only) || 0;
    const shared = Number(edge.with_coauthor) || 0;
    const total = only + shared;
    if (!total) return;
    const source = byId.get(Number(edge.source));
    const target = byId.get(Number(edge.target));
    if (!source || !target) return;
    const title = "Weight " + total.toLocaleString("en-GB", { maximumFractionDigits: 2 })
      + " · citation " + only.toLocaleString("en-GB", { maximumFractionDigits: 2 })
      + " · also coauthors " + shared.toLocaleString("en-GB", { maximumFractionDigits: 2 });
    if (Number(edge.source) === Number(edge.target)) {
      const ring = document.createElementNS("http://www.w3.org/2000/svg", "circle");
      ring.setAttribute("cx", source.x);
      ring.setAttribute("cy", source.y);
      ring.setAttribute("r", String(source.r + 8));
      ring.setAttribute("fill", "none");
      ring.setAttribute("stroke", shared >= only ? "#279F94" : "#003BDE");
      ring.setAttribute("stroke-width", String(weightWidth(total, maxWeight)));
      const tip = document.createElementNS("http://www.w3.org/2000/svg", "title");
      tip.textContent = "Inside this community. " + title;
      ring.appendChild(tip);
      svg.appendChild(ring);
      return;
    }
    const outer = weightWidth(total, maxWeight);
    const inner = outer * (shared / total);
    addLine(svg, source, target, "#003BDE", outer, title);
    if (inner > 0.4) addLine(svg, source, target, "#279F94", inner, title);
  });
}
function addLine(svg, source, target, color, width, title) {
  const line = document.createElementNS("http://www.w3.org/2000/svg", "line");
  line.setAttribute("x1", source.x);
  line.setAttribute("y1", source.y);
  line.setAttribute("x2", target.x);
  line.setAttribute("y2", target.y);
  line.setAttribute("stroke", color);
  line.setAttribute("stroke-width", String(width));
  const tip = document.createElementNS("http://www.w3.org/2000/svg", "title");
  tip.textContent = title;
  line.appendChild(tip);
  svg.appendChild(line);
}

function drawNetwork(data) {
  const svg = document.getElementById("network-svg");
  clear(svg);
  const nodes = data.nodes.map((node) => ({ ...node, id: node.id }));
  const maxAuthors = Math.max(...nodes.map((node) => Number(node.n_authors || node.strength || 1)), 1);
  nodes.forEach((node, index) => {
    const angle = -Math.PI / 2 + (index / Math.max(nodes.length, 1)) * Math.PI * 2;
    const orbit = nodes.length > 18 ? 270 : 220;
    node.x = 450 + Math.cos(angle) * orbit;
    node.y = 340 + Math.sin(angle) * orbit;
    const size = Number(node.n_authors || node.strength || 1);
    node.r = 10 + 22 * Math.sqrt(size / maxAuthors);
  });
  drawEdges(svg, nodes, data.edges || []);
  nodes.forEach((node) => {
    const group = document.createElementNS("http://www.w3.org/2000/svg", "g");
    group.style.cursor = "pointer";
    const circle = document.createElementNS("http://www.w3.org/2000/svg", "circle");
    circle.setAttribute("cx", node.x);
    circle.setAttribute("cy", node.y);
    circle.setAttribute("r", node.r);
    circle.setAttribute("fill", data.level === "author" ? colorFor(node.macro) : colorFor(node.id));
    const label = document.createElementNS("http://www.w3.org/2000/svg", "text");
    label.setAttribute("x", node.x);
    label.setAttribute("y", node.y + node.r + 14);
    label.setAttribute("text-anchor", "middle");
    label.setAttribute("font-size", "11");
    label.setAttribute("fill", "#282828");
    label.textContent = data.level === "author"
      ? (node.name || "Author")
      : data.level.charAt(0).toUpperCase() + data.level.slice(1) + " " + node.id;
    group.appendChild(circle);
    group.appendChild(label);
    group.addEventListener("click", () => zoomFrom(data, node));
    svg.appendChild(group);
  });
}

function zoomFrom(data, node) {
  if (data.level === "macro") {
    netState.level = "meso";
    netState.macro = Number(node.id);
    netState.meso = null;
    netState.micro = null;
  } else if (data.level === "meso") {
    netState.level = "micro";
    netState.meso = Number(node.id);
    netState.macro = data.macro;
    netState.micro = null;
  } else if (data.level === "micro") {
    netState.level = "author";
    netState.micro = Number(node.id);
    netState.meso = data.meso;
    netState.macro = data.macro;
  } else {
    showTab("details");
    loadAuthor(node.id);
    return;
  }
  loadNetwork();
}

function renderCrumb() {
  const crumb = document.getElementById("crumb");
  clear(crumb);
  const steps = [{ label: "All macros", state: { level: "macro", macro: null, meso: null, micro: null } }];
  if (netState.macro !== null && netState.level !== "macro") {
    steps.push({ label: "Macro " + netState.macro, state: { level: "meso", macro: netState.macro, meso: null, micro: null } });
  }
  if (netState.meso !== null && (netState.level === "micro" || netState.level === "author")) {
    steps.push({ label: "Meso " + netState.meso, state: { level: "micro", macro: netState.macro, meso: netState.meso, micro: null } });
  }
  if (netState.micro !== null && netState.level === "author") {
    steps.push({ label: "Micro " + netState.micro, state: netState });
  }
  steps.forEach((step, index) => {
    if (index) crumb.appendChild(el("span", "/"));
    const button = document.createElement("button");
    button.type = "button";
    button.textContent = step.label;
    button.addEventListener("click", () => {
      Object.assign(netState, step.state);
      loadNetwork();
    });
    crumb.appendChild(button);
  });
}

async function loadNetwork() {
  renderCrumb();
  const status = document.getElementById("network-status");
  status.textContent = "Loading this map…";
  const params = new URLSearchParams({ level: netState.level });
  if (netState.macro !== null) params.set("macro", netState.macro);
  if (netState.meso !== null) params.set("meso", netState.meso);
  if (netState.micro !== null) params.set("micro", netState.micro);
  const response = await fetch("/api/network?" + params.toString());
  const data = await response.json();
  if (!response.ok) {
    status.textContent = data.error || "The map could not be loaded.";
    return;
  }
  if (data.macro !== undefined && data.macro !== null) netState.macro = data.macro;
  if (data.meso !== undefined && data.meso !== null && netState.level !== "meso") netState.meso = data.meso;
  renderCrumb();
  drawNetwork(data);
  const noun = data.level === "author" ? "authors" : data.level + " communities";
  let message = data.nodes.length + " " + noun + ".";
  if (data.truncated) message += " Showing the " + data.nodes.length + " strongest of " + Number(data.n_authors).toLocaleString("en-GB") + " authors.";
  status.textContent = message;
}

function fillSelect(select, rows, allLabel, selected) {
  clear(select);
  const all = document.createElement("option");
  all.value = "";
  all.textContent = allLabel;
  select.appendChild(all);
  rows.forEach((row) => {
    const option = document.createElement("option");
    option.value = row.id;
    option.textContent = row.label;
    select.appendChild(option);
  });
  select.value = selected || "";
}

let communityRows = [];
let communityLevel = "macro";

async function loadCommunityList() {
  const level = document.getElementById("list-level").value;
  const macroSelect = document.getElementById("list-macro");
  const mesoSelect = document.getElementById("list-meso");
  macroSelect.hidden = level === "macro";
  mesoSelect.hidden = level !== "micro";
  const params = new URLSearchParams({ level });
  if (level !== "macro" && macroSelect.value) params.set("macro", macroSelect.value);
  if (level === "micro" && mesoSelect.value) params.set("meso", mesoSelect.value);
  const response = await fetch("/api/communities?" + params.toString());
  const rows = await response.json();
  const list = document.getElementById("community-list");
  clear(list);
  if (!response.ok || !Array.isArray(rows)) {
    list.appendChild(el("li", (rows && rows.error) || "Communities could not be loaded."));
    return;
  }
  communityRows = rows;
  communityLevel = level;
  renderCommunityList();
}

function renderCommunityList() {
  const rows = communityRows.slice();
  const level = communityLevel;
  const list = document.getElementById("community-list");
  clear(list);
  const sort = document.getElementById("list-sort").value;
  rows.sort((a, b) => {
    if (sort === "id") return Number(a.id) - Number(b.id);
    if (sort === "size-asc") return Number(a.n_authors) - Number(b.n_authors);
    return Number(b.n_authors) - Number(a.n_authors);
  });
  const maxCount = Math.max(...rows.map((row) => Number(row.n_authors)), 1);
  const total = rows.reduce((sum, row) => sum + Number(row.n_authors), 0);
  rows.forEach((row) => {
    const li = document.createElement("li");
    const button = document.createElement("button");
    button.type = "button";
    button.className = "linkish";
    const name = level.charAt(0).toUpperCase() + level.slice(1) + " " + row.id;
    button.appendChild(el("span", name));
    const share = total ? (100 * Number(row.n_authors) / total) : 0;
    button.appendChild(el("span", Number(row.n_authors).toLocaleString("en-GB") + " authors · " + share.toFixed(1) + "%", "meta"));
    const bar = el("div", null, "bar");
    const fill = document.createElement("span");
    fill.style.width = (100 * Number(row.n_authors) / maxCount) + "%";
    bar.appendChild(fill);
    button.appendChild(bar);
    button.addEventListener("click", () => openCommunity(level, row));
    li.appendChild(button);
    list.appendChild(li);
  });
}

function openCommunity(level, row) {
  if (level === "macro") {
    Object.assign(netState, { level: "meso", macro: Number(row.id), meso: null, micro: null });
  } else if (level === "meso") {
    Object.assign(netState, { level: "micro", macro: row.macro, meso: Number(row.id), micro: null });
  } else {
    Object.assign(netState, { level: "author", macro: row.macro, meso: row.meso, micro: Number(row.id) });
  }
  loadNetwork();
}

document.getElementById("list-level").addEventListener("change", async () => {
  await refreshFilters();
  loadCommunityList();
});
document.getElementById("list-macro").addEventListener("change", async () => {
  await refreshMesoFilter();
  loadCommunityList();
});
document.getElementById("list-meso").addEventListener("change", () => loadCommunityList());
document.getElementById("list-sort").addEventListener("change", () => renderCommunityList());

async function refreshFilters() {
  if (!macroOptions.length) {
    const response = await fetch("/api/communities?level=macro");
    const rows = await response.json();
    if (Array.isArray(rows)) {
      macroOptions = rows.map((row) => ({ id: row.id, label: "Macro " + row.id }));
    }
  }
  fillSelect(document.getElementById("list-macro"), macroOptions, "All macros");
  await refreshMesoFilter();
}
async function refreshMesoFilter() {
  const macro = document.getElementById("list-macro").value;
  const params = new URLSearchParams({ level: "meso" });
  if (macro) params.set("macro", macro);
  const response = await fetch("/api/communities?" + params.toString());
  const rows = await response.json();
  mesoOptions = Array.isArray(rows)
    ? rows.map((row) => ({ id: row.id, label: "Meso " + row.id }))
    : [];
  fillSelect(document.getElementById("list-meso"), mesoOptions, "All mesos");
}

document.getElementById("search-form").addEventListener("submit", async (event) => {
  event.preventDefault();
  const q = document.getElementById("q").value.trim();
  document.getElementById("details-status").textContent = "Searching…";
  const response = await fetch("/api/search?q=" + encodeURIComponent(q));
  const rows = await response.json();
  const detail = document.getElementById("detail");
  clear(detail);
  detail.className = "person";
  if (!rows.length) {
    detail.appendChild(el("p", "No matching authors.", "empty"));
    return;
  }
  detail.appendChild(el("h3", "Search results"));
  rows.forEach((row) => {
    const block = el("div", null, "paper");
    const button = document.createElement("button");
    button.type = "button";
    button.className = "linkish";
    button.appendChild(el("strong", row.name || "Unnamed author"));
    button.appendChild(el("span", communityText(row)));
    button.addEventListener("click", () => loadAuthor(row.int_id));
    block.appendChild(button);
    detail.appendChild(block);
  });
});

async function loadAuthor(intId) {
  showTab("details");
  document.getElementById("details-status").textContent = "Loading two steps of links…";
  const response = await fetch("/api/author/" + intId);
  const data = await response.json();
  if (!response.ok) {
    document.getElementById("details-status").textContent = data.error || "Author not found.";
    return;
  }
  drawDetails(data);
  showAuthorDetail(data);
  document.getElementById("details-status").textContent = data.author.name
    + " · showing " + data.shown_neighbors + " of " + Number(data.n_neighbors).toLocaleString("en-GB") + " links, then their strongest links";
}

function drawDetails(data) {
  const svg = document.getElementById("details-svg");
  clear(svg);
  const nodes = data.nodes.map((node) => ({ ...node, id: node.int_id }));
  const rings = { 0: [], 1: [], 2: [] };
  nodes.forEach((node) => rings[node.hop || 0].push(node));
  rings[0].forEach((node) => { node.x = 450; node.y = 330; node.r = 16; });
  placeRing(rings[1], 170, 11);
  placeRing(rings[2], 285, 8);
  drawEdges(svg, nodes, data.edges || []);
  nodes.forEach((node) => {
    const group = document.createElementNS("http://www.w3.org/2000/svg", "g");
    group.style.cursor = "pointer";
    const circle = document.createElementNS("http://www.w3.org/2000/svg", "circle");
    circle.setAttribute("cx", node.x);
    circle.setAttribute("cy", node.y);
    circle.setAttribute("r", node.r);
    circle.setAttribute("fill", colorFor(node.macro));
    if (node.hop === 0) {
      circle.setAttribute("stroke", "#001991");
      circle.setAttribute("stroke-width", "3");
    }
    const label = document.createElementNS("http://www.w3.org/2000/svg", "text");
    label.setAttribute("x", node.x + (node.hop === 0 ? 0 : 10));
    label.setAttribute("y", node.y + (node.hop === 0 ? -22 : 4));
    label.setAttribute("text-anchor", node.hop === 0 ? "middle" : "start");
    label.setAttribute("font-size", node.hop === 2 ? "10" : "12");
    label.setAttribute("fill", "#282828");
    label.textContent = node.name || "Author";
    group.appendChild(circle);
    group.appendChild(label);
    group.addEventListener("click", () => loadAuthor(node.id));
    svg.appendChild(group);
  });
}
function placeRing(nodes, radius, r) {
  nodes.forEach((node, index) => {
    const angle = -Math.PI / 2 + (index / Math.max(nodes.length, 1)) * Math.PI * 2;
    node.x = 450 + Math.cos(angle) * radius;
    node.y = 330 + Math.sin(angle) * radius;
    node.r = r;
  });
}

function addChip(parent, label, onClick) {
  const chip = el("span", label, "chip");
  chip.style.cursor = "pointer";
  chip.style.color = "#003BDE";
  chip.addEventListener("click", () => {
    showTab("network");
    onClick();
  });
  parent.appendChild(chip);
}

function showAuthorDetail(data) {
  const detail = document.getElementById("detail");
  clear(detail);
  detail.className = "person";
  const author = data.author;
  detail.appendChild(el("h2", author.name || "Unnamed author"));
  detail.appendChild(el("div", "AIRAK AuthorId " + author.author_id));
  const chips = el("div", null, "chips");
  if (author.macro !== null && author.macro !== undefined) {
    addChip(chips, "Macro " + author.macro, () => openCommunity("macro", { id: author.macro }));
    addChip(chips, "Meso " + author.meso, () => openCommunity("meso", { id: author.meso, macro: author.macro }));
    addChip(chips, "Micro " + author.micro, () => openCommunity("micro", { id: author.micro, macro: author.macro, meso: author.meso }));
  } else {
    chips.appendChild(el("span", "Outside the largest component", "chip"));
  }
  chips.appendChild(el("span", Number(data.n_neighbors).toLocaleString("en-GB") + " links", "chip"));
  chips.appendChild(el("span", Number(data.n_papers).toLocaleString("en-GB") + " papers", "chip"));
  detail.appendChild(chips);
  detail.appendChild(el("h3", "Papers"));
  if (!data.papers.length) detail.appendChild(el("p", "No papers were recorded for this author in the network export.", "empty"));
  data.papers.forEach((paper) => {
    const block = el("div", null, "paper");
    block.appendChild(el("strong", paper.title || ("Publication " + paper.publication_id)));
    block.appendChild(el("span", [paper.year, "role weight " + Number(paper.role_weight).toFixed(2)].filter(Boolean).join(" · ")));
    if (paper.doi) {
      const link = document.createElement("a");
      link.href = "https://doi.org/" + paper.doi;
      link.target = "_blank";
      link.rel = "noreferrer";
      link.textContent = paper.doi;
      block.appendChild(link);
    }
    detail.appendChild(block);
  });
  if (data.n_papers > data.papers.length) {
    detail.appendChild(el("p", "Showing " + data.papers.length + " of " + Number(data.n_papers).toLocaleString("en-GB") + " papers.", "empty"));
  }
}

refreshFilters().then(loadCommunityList);
loadNetwork();
</script>
</body>
</html>
"""


class Handler(BaseHTTPRequestHandler):
    def _send(self, code: int, body: bytes, content_type: str) -> None:
        self.send_response(code)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _json(self, payload, code: int = 200) -> None:
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self._send(code, body, "application/json; charset=utf-8")

    def do_GET(self) -> None:  # noqa: N802
        parsed = urlparse(self.path)
        params = parse_qs(parsed.query)
        try:
            if parsed.path == "/":
                page = PAGE.replace("__TIMESTAMP__", TIMESTAMP)
                self._send(200, page.encode("utf-8"), "text/html; charset=utf-8")
                return
            if parsed.path == "/api/search":
                self._json(search_authors(params.get("q", [""])[0]))
                return
            if parsed.path == "/api/communities":
                level = params.get("level", ["macro"])[0]
                if level not in ("macro", "meso", "micro"):
                    self._json({"error": "level must be macro, meso, or micro"}, 400)
                    return
                macro_id = _optional_int(params, "macro")
                meso_id = _optional_int(params, "meso")
                self._json(communities(level, macro_id, meso_id))
                return
            if parsed.path == "/api/network":
                level = params.get("level", ["macro"])[0]
                payload = build_network(
                    level,
                    _optional_int(params, "macro"),
                    _optional_int(params, "meso"),
                    _optional_int(params, "micro"),
                )
                self._json(payload)
                return
            prefix = "/api/author/"
            if parsed.path.startswith(prefix):
                raw = parsed.path[len(prefix) :]
                if not raw.isdigit():
                    self._json({"error": "int_id must be an integer"}, 400)
                    return
                payload = author_view(int(raw))
                if not payload:
                    self._json({"error": "author not found"}, 404)
                    return
                self._json(payload)
                return
            self._json({"error": "not found"}, 404)
        except Exception as exc:
            print(f"Request failed: {exc}", flush=True)
            self._json({"error": str(exc)}, 500)

    def log_message(self, fmt: str, *args) -> None:
        print("[%s] %s" % (self.log_date_time_string(), fmt % args), flush=True)


def _optional_int(params: dict, name: str) -> int | None:
    raw = params.get(name, [""])[0].strip()
    if not raw:
        return None
    if not re.fullmatch(r"-?\d+", raw):
        raise ValueError(f"{name} must be an integer")
    return int(raw)


def main() -> None:
    global TIMESTAMP
    parser = argparse.ArgumentParser(description="Browse the author citation network.")
    parser.add_argument("--timestamp", default=DEFAULT_TIMESTAMP)
    parser.add_argument("--port", type=int, default=8765)
    args = parser.parse_args()
    TIMESTAMP = args.timestamp
    table("pub_metadata_raw")

    def warm_macro() -> None:
        try:
            print("Warming the macro map...", flush=True)
            cached("network-macro", network_macro)
            print("Macro map is ready.", flush=True)
        except Exception as exc:
            print(f"Macro map warm-up failed: {exc}", flush=True)

    server = ThreadingHTTPServer(("127.0.0.1", args.port), Handler)
    threading.Thread(target=warm_macro, daemon=True).start()
    threading.Thread(target=paper_titles, daemon=True).start()
    print(f"Author network dashboard: http://127.0.0.1:{args.port}", flush=True)
    print(f"Run timestamp: {TIMESTAMP}", flush=True)
    server.serve_forever()


if __name__ == "__main__":
    main()
