"""
Scope Drift Detection — AIRAK BigQuery Edition
================================================
Builds a citation network from AIRAK data, runs Leiden community detection
at macro/meso/micro resolutions, writes cluster_data.json (includes journal_drift metrics) and output/scope_journal_dashboard.html
(Plotly: journal drift vs out-of-scope, OOS % by publication year, macro cluster scatter).

Data source : ocean-breeze-tier-1.airak (BigQuery)
Algorithm   : Leiden community detection (Traag et al., 2019)
Target      : Top N Frontiers journals by publication volume

Community labels : sampled titles + abstracts from BigQuery, then OpenAI Chat Completions.
Set OPENAI_API_KEY in the shell, or put it in a ``.env`` file (repo root or next to this script);
the script loads ``.env`` on startup so it behaves like notebooks that call ``load_dotenv()``.
Optional: OPENAI_MODEL, LLM_SAMPLE_PER_COMM, LLM_MAX_TITLE_CHARS, LLM_MAX_ABS_CHARS,
LLM_SLEEP_SEC, JOURNAL_DRIFT_LEVEL (macro|meso|micro; default macro for the journal dashboard).
If the key is still missing, labels fall back to the dominant journal name.

Requirements:
    pip install leidenalg python-igraph google-cloud-bigquery pandas plotly

Usage:
    export GOOGLE_APPLICATION_CREDENTIALS=/path/to/creds.json
    export OPENAI_API_KEY=...
    python scope_drift_airak.py
"""

import math
import os
import json
import re
import time
import random
import logging
import urllib.error
import urllib.request
from collections import Counter, defaultdict
from pathlib import Path

import pandas as pd
from google.cloud import bigquery
import igraph as ig
import leidenalg


def _merge_dotenv_file(path: Path) -> None:
    """Set os.environ from KEY=value lines; does not override variables already set."""
    try:
        raw = path.read_text(encoding="utf-8")
    except OSError:
        return
    for line in raw.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if line.lower().startswith("export "):
            line = line[7:].strip()
        if "=" not in line:
            continue
        key, _, val = line.partition("=")
        key = key.strip()
        if not key:
            continue
        val = val.strip()
        if len(val) >= 2 and val[0] == val[-1] and val[0] in "\"'":
            val = val[1:-1]
        if key not in os.environ:
            os.environ[key] = val


def _bootstrap_env_from_dotenv() -> None:
    """Load `.env` from cwd, script directory, and parents (matches typical notebook + .env setup)."""
    try:
        from dotenv import load_dotenv  # type: ignore[import-not-found]

        load_dotenv(override=False)
    except ImportError:
        pass

    candidates: list[Path] = []
    here = Path(__file__).resolve()
    for i in range(8):
        candidates.append(here.parents[i] / ".env")
    candidates.append(Path.cwd() / ".env")

    seen = set()
    for p in candidates:
        try:
            rp = p.resolve()
        except OSError:
            continue
        if rp in seen or not rp.is_file():
            continue
        seen.add(rp)
        _merge_dotenv_file(rp)


_bootstrap_env_from_dotenv()

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------
BQ_PROJECT = "ocean-breeze-tier-1"
AIRAK_DATASET = "ocean-breeze-tier-1.airak"
FRONTIERS_PUBLISHER_ID = 1563368095744

TOP_N_JOURNALS = 5  # number of journals to include in citation graph
YEAR_RANGE = (2020, 2025)  # publication year window

# OpenAI labelling (titles + abstracts → short labels). Override via environment.
OPENAI_MODEL = os.environ.get("OPENAI_MODEL", "gpt-4o-mini")
LLM_SAMPLE_PER_COMM = int(os.environ.get("LLM_SAMPLE_PER_COMM", "18"))
LLM_MAX_TITLE_CHARS = int(os.environ.get("LLM_MAX_TITLE_CHARS", "240"))
LLM_MAX_ABS_CHARS = int(os.environ.get("LLM_MAX_ABS_CHARS", "1200"))
LLM_SLEEP_SEC = float(os.environ.get("LLM_SLEEP_SEC", "0.35"))

# Journal scope / drift dashboard: article is "out of scope" if its journal's share
# in its **macro** citation community is below this threshold (community led by other journals).
_jdl = os.environ.get("JOURNAL_DRIFT_LEVEL", "macro").strip().lower()
JOURNAL_DRIFT_LEVEL = (
    _jdl if _jdl in ("macro", "meso", "micro") else "macro"
)  # OOS %, drift L1, cluster scatter
OUT_OF_SCOPE_COMMUNITY_SHARE = float(
    os.environ.get("OUT_OF_SCOPE_COMMUNITY_SHARE", "0.35")
)

LEIDEN_RESOLUTIONS = {
    "macro": 0.00005,  # ~10-30 broad domains
    "meso": 0.0005,  # ~100-700 thematic areas
    "micro": 0.005,  # ~500-8000 fine-grained topics
}

OUTPUT_DIR = "./output"
random.seed(42)

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s"
)
log = logging.getLogger(__name__)
os.makedirs(OUTPUT_DIR, exist_ok=True)

# ---------------------------------------------------------------------------
# BigQuery helpers
# ---------------------------------------------------------------------------


def bq_client():
    return bigquery.Client(project=BQ_PROJECT)


def query_df(sql: str) -> pd.DataFrame:
    return bq_client().query(sql).to_dataframe()


# ---------------------------------------------------------------------------
# Step 1: Identify top journals
# ---------------------------------------------------------------------------


def get_top_journals(n: int) -> pd.DataFrame:
    log.info(f"Getting top {n} Frontiers journals by publication count...")
    q = f"""
    SELECT j.JournalId, j.DisplayName, COUNT(*) as pubs
    FROM `{AIRAK_DATASET}.Publication` p
    JOIN `{AIRAK_DATASET}.Journal` j ON p.JournalId = j.JournalId
    WHERE j.PublisherId = {FRONTIERS_PUBLISHER_ID}
      AND p.PublishedYear BETWEEN {YEAR_RANGE[0]} AND {YEAR_RANGE[1]}
    GROUP BY j.JournalId, j.DisplayName
    ORDER BY pubs DESC
    LIMIT {n}
    """
    df = query_df(q)
    log.info(f"Top journals:\n{df.to_string(index=False)}")
    return df


# ---------------------------------------------------------------------------
# Step 2: Extract citation edges
# ---------------------------------------------------------------------------


def get_citation_edges(journal_ids: list[int]) -> pd.DataFrame:
    ids_str = ",".join(str(x) for x in journal_ids)
    log.info(f"Extracting citation edges for {len(journal_ids)} journals...")
    q = f"""
    WITH pubs AS (
      SELECT PublicationId FROM `{AIRAK_DATASET}.Publication`
      WHERE JournalId IN ({ids_str})
        AND PublishedYear BETWEEN {YEAR_RANGE[0]} AND {YEAR_RANGE[1]}
    )
    SELECT pc.PublicationId as src, pc.CitedPublicationId as tgt
    FROM `{AIRAK_DATASET}.PublicationCitation` pc
    WHERE pc.PublicationId IN (SELECT PublicationId FROM pubs)
      AND pc.CitedPublicationId IN (SELECT PublicationId FROM pubs)
    """
    df = query_df(q)
    log.info(f"Citation edges: {len(df):,}")
    return df


# ---------------------------------------------------------------------------
# Step 3: Get node metadata
# ---------------------------------------------------------------------------


def get_node_metadata(journal_ids: list[int]) -> pd.DataFrame:
    ids_str = ",".join(str(x) for x in journal_ids)
    log.info("Fetching node metadata...")
    q = f"""
    SELECT
      p.PublicationId,
      p.PublishedYear,
      j.DisplayName AS JournalName,
      COALESCE(p.Title, '') AS Title,
      COALESCE(pa.Abstract, '') AS AbstractText
    FROM `{AIRAK_DATASET}.Publication` p
    JOIN `{AIRAK_DATASET}.Journal` j ON p.JournalId = j.JournalId
    LEFT JOIN `{AIRAK_DATASET}.PublicationAbstract` pa
      ON p.PublicationId = pa.PublicationId
    WHERE j.JournalId IN ({ids_str})
      AND p.PublishedYear BETWEEN {YEAR_RANGE[0]} AND {YEAR_RANGE[1]}
    """
    df = query_df(q)
    log.info(f"Nodes: {len(df):,}")
    return df


# ---------------------------------------------------------------------------
# Step 4: Build graph & run Leiden
# ---------------------------------------------------------------------------


def build_graph(df_edges: pd.DataFrame):
    node_ids = sorted(set(df_edges["src"]) | set(df_edges["tgt"]))
    id_map = {pid: i for i, pid in enumerate(node_ids)}

    edges = [
        (id_map[r["src"]], id_map[r["tgt"]])
        for _, r in df_edges.iterrows()
        if r["src"] in id_map and r["tgt"] in id_map
    ]

    log.info(f"Building graph: {len(node_ids):,} nodes, {len(edges):,} edges")
    G = ig.Graph(n=len(node_ids), edges=edges, directed=False)
    G.simplify()
    log.info(f"After simplify: {G.vcount():,} nodes, {G.ecount():,} edges")
    return G, node_ids


def run_leiden_hierarchy(G: ig.Graph, resolutions: dict) -> dict:
    memberships = {}
    for level, res in resolutions.items():
        log.info(f"Leiden {level} (res={res})...")
        partition = leidenalg.find_partition(
            G,
            leidenalg.CPMVertexPartition,
            resolution_parameter=res,
            n_iterations=10,
            seed=42,
        )
        mem = partition.membership
        sizes = sorted(Counter(mem).values(), reverse=True)
        n_big = sum(1 for s in sizes if s >= 50)
        log.info(f"  {len(set(mem)):,} communities, {n_big} with 50+ members")
        memberships[level] = mem
    return memberships


# ---------------------------------------------------------------------------
# Step 5: Profile communities
# ---------------------------------------------------------------------------


def profile_communities(node_ids, memberships, node_lookup, min_sizes, max_per_level):
    profiles = {}
    for level in ["macro", "meso", "micro"]:
        mem = memberships[level]
        min_sz = min_sizes.get(level, 50)
        max_n = max_per_level.get(level, 60)

        comm_counter = Counter(mem)
        big_comms = [(c, sz) for c, sz in comm_counter.most_common() if sz >= min_sz][
            :max_n
        ]

        level_profiles = []
        for comm_id, size in big_comms:
            journal_counts = Counter()
            year_counts = Counter()
            for idx in range(len(mem)):
                if mem[idx] == comm_id:
                    pub_id = node_ids[idx]
                    meta = node_lookup.get(pub_id, {})
                    if meta:
                        j = meta.get("JournalName", "Unknown").replace(
                            "Frontiers in ", ""
                        )
                        journal_counts[j] += 1
                        year_counts[meta.get("PublishedYear", 0)] += 1

            total = sum(journal_counts.values())
            top_j = journal_counts.most_common(5)

            level_profiles.append(
                {
                    "id": int(comm_id),
                    "size": int(size),
                    "journals": {j: round(c / total * 100, 1) for j, c in top_j},
                    "dominant": top_j[0][0] if top_j else "Unknown",
                    "dominant_pct": round(top_j[0][1] / total * 100, 1) if top_j else 0,
                    "n_journals": len(journal_counts),
                    "years": dict(sorted(year_counts.items())),
                }
            )

        profiles[level] = level_profiles
        log.info(f"  {level}: {len(level_profiles)} communities profiled")

    return profiles


# ---------------------------------------------------------------------------
# Step 6: Build hierarchy
# ---------------------------------------------------------------------------


def build_hierarchy(memberships):
    n = len(memberships["macro"])

    meso_to_macro = {}
    meso_macro_map = {}
    for i in range(n):
        mid = memberships["meso"][i]
        maid = memberships["macro"][i]
        meso_macro_map.setdefault(mid, Counter())[maid] += 1
    for mid, c in meso_macro_map.items():
        meso_to_macro[mid] = c.most_common(1)[0][0]

    micro_to_meso = {}
    micro_meso_map = {}
    for i in range(n):
        mid = memberships["micro"][i]
        meid = memberships["meso"][i]
        micro_meso_map.setdefault(mid, Counter())[meid] += 1
    for mid, c in micro_meso_map.items():
        micro_to_meso[mid] = c.most_common(1)[0][0]

    return meso_to_macro, micro_to_meso


# ---------------------------------------------------------------------------
# Step 7: OpenAI labelling (title + abstract samples)
# ---------------------------------------------------------------------------

LLM_SYSTEM = """You label scientific publication clusters for an analytics dashboard.
Use UK English. Respond with ONLY a single JSON object, no markdown fences.
Schema:
{
  "label": "2–6 words, main research theme for this cluster",
  "keywords": ["3–5 short noun phrases"],
  "label_specific": "narrower sub-theme OR empty string if not applicable",
  "keywords_specific": ["2–4 narrower phrases OR empty array"]
}
For resolution "meso", fill label_specific and keywords_specific when a clear sub-theme exists.
For "macro" or "micro", set label_specific to "" and keywords_specific to []."""


def _truncate(s: str, max_len: int) -> str:
    s = (s or "").strip()
    if len(s) <= max_len:
        return s
    return s[: max_len - 1] + "…"


def _extract_json_object(text: str) -> dict:
    """Parse first JSON object from model output (handles optional ```json fences)."""
    text = text.strip()
    m = re.search(r"```(?:json)?\s*([\s\S]*?)```", text, re.IGNORECASE)
    if m:
        text = m.group(1).strip()
    start = text.find("{")
    end = text.rfind("}")
    if start == -1 or end <= start:
        raise ValueError("No JSON object in model response")
    return json.loads(text[start : end + 1])


def _call_openai(user_prompt: str) -> str:
    key = os.environ.get("OPENAI_API_KEY")
    if not key:
        raise RuntimeError("OPENAI_API_KEY is not set")
    body = {
        "model": OPENAI_MODEL,
        "max_tokens": 500,
        "messages": [
            {"role": "system", "content": LLM_SYSTEM},
            {"role": "user", "content": user_prompt},
        ],
    }
    req = urllib.request.Request(
        "https://api.openai.com/v1/chat/completions",
        data=json.dumps(body).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {key}",
            "content-type": "application/json",
        },
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=180) as resp:
        data = json.loads(resp.read().decode("utf-8"))
    choices = data.get("choices") or []
    if not choices:
        raise RuntimeError(f"Unexpected OpenAI response: {data!r:.500}")
    return choices[0]["message"]["content"]


def _openai_configured() -> bool:
    return bool(os.environ.get("OPENAI_API_KEY"))


def _build_sample_prompt(
    level: str, comm_id: int, size: int, articles: list[dict]
) -> str:
    lines = [
        f"Resolution level: {level}",
        f"Community id: {comm_id} (approx. {size} articles in full graph; below is a random sample).",
        "Publications (title + abstract excerpt):",
        "",
    ]
    for i, a in enumerate(articles, 1):
        lines.append(f"--- Paper {i} ---")
        lines.append(f"Title: {a['title']}")
        lines.append(f"Abstract: {a['abstract']}")
        lines.append("")
    lines.append("Return the JSON object as specified in the system message.")
    return "\n".join(lines)


def _apply_fallback_labels(profiles):
    """When OpenAI is not configured or a call fails."""
    for level in profiles:
        for p in profiles[level]:
            p["label"] = p.get("dominant", "Unknown")
            p["fos"] = []
            if level == "meso":
                p["label_specific"] = ""
                p["fos_specific"] = []
    return profiles


def label_communities_llm(node_ids, memberships, profiles, node_lookup):
    """Label each profiled community using sampled titles+abstracts and OpenAI."""
    comm_pub_map = {}
    for level in ["macro", "meso", "micro"]:
        for idx in range(len(memberships[level])):
            key = f"{level}_{memberships[level][idx]}"
            comm_pub_map.setdefault(key, []).append(node_ids[idx])

    comm_samples = {}
    relevant = {f"{level}_{p['id']}" for level in profiles for p in profiles[level]}
    for ck in relevant:
        pubs = comm_pub_map.get(ck, [])
        k = min(LLM_SAMPLE_PER_COMM, len(pubs))
        comm_samples[ck] = random.sample(pubs, k) if k else []

    if not _openai_configured():
        log.warning(
            "OPENAI_API_KEY is not set (shell env and .env files were loaded) — "
            "using dominant journal as community label."
        )
        return _apply_fallback_labels(profiles)

    n_sample_slots = sum(len(comm_samples[k]) for k in comm_samples)
    log.info(
        "Labelling communities via OpenAI (%s); %s sampled article slots across communities",
        OPENAI_MODEL,
        f"{n_sample_slots:,}",
    )

    n_calls = 0
    for level in profiles:
        for p in profiles[level]:
            key = f"{level}_{p['id']}"
            pubs = comm_samples.get(key, [])
            articles = []
            for pid in pubs:
                meta = node_lookup.get(pid)
                if meta is None:
                    meta = node_lookup.get(int(pid))
                if not meta:
                    continue
                title = _truncate(str(meta.get("Title", "")), LLM_MAX_TITLE_CHARS)
                abstract = _truncate(
                    str(meta.get("AbstractText", "")), LLM_MAX_ABS_CHARS
                )
                if not title and not abstract:
                    continue
                articles.append({"title": title or "(no title)", "abstract": abstract})

            if not articles:
                p["label"] = p["dominant"]
                p["fos"] = []
                if level == "meso":
                    p["label_specific"] = ""
                    p["fos_specific"] = []
                continue

            user_prompt = _build_sample_prompt(
                level, int(p["id"]), int(p["size"]), articles
            )
            raw = ""
            try:
                raw = _call_openai(user_prompt)
                out = _extract_json_object(raw)
            except (urllib.error.HTTPError, urllib.error.URLError, TimeoutError) as e:
                log.error("OpenAI HTTP error for %s: %s", key, e)
                p["label"] = p["dominant"]
                p["fos"] = []
                if level == "meso":
                    p["label_specific"] = ""
                    p["fos_specific"] = []
                continue
            except (json.JSONDecodeError, ValueError, KeyError, RuntimeError) as e:
                snippet = (raw[:400] + "…") if len(raw) > 400 else raw
                log.error("OpenAI parse error for %s: %s; raw=%r", key, e, snippet)
                p["label"] = p["dominant"]
                p["fos"] = []
                if level == "meso":
                    p["label_specific"] = ""
                    p["fos_specific"] = []
                continue

            n_calls += 1
            label = (out.get("label") or "").strip() or p["dominant"]
            kws = out.get("keywords") or []
            if isinstance(kws, str):
                kws = [kws]
            kws = [str(x).strip() for x in kws if str(x).strip()][:5]
            p["label"] = label
            p["fos"] = kws[:3] if kws else []

            if level == "meso":
                ls = (out.get("label_specific") or "").strip()
                kws_s = out.get("keywords_specific") or []
                if isinstance(kws_s, str):
                    kws_s = [kws_s]
                kws_s = [str(x).strip() for x in kws_s if str(x).strip()][:4]
                p["label_specific"] = ls
                p["fos_specific"] = kws_s[:3]
            else:
                p["label_specific"] = ""
                p["fos_specific"] = []

            time.sleep(LLM_SLEEP_SEC)

    log.info("OpenAI community labelling finished (%d API calls).", n_calls)
    return profiles


# ---------------------------------------------------------------------------
# Journal scope + drift dashboard (HTML)
# ---------------------------------------------------------------------------


def _journal_short(meta: dict) -> str:
    return (meta.get("JournalName") or "Unknown").replace("Frontiers in ", "")


def _meta_for_pub(node_lookup, pub_id):
    m = node_lookup.get(pub_id)
    if m is None:
        m = node_lookup.get(int(pub_id))
    return m or {}


def compute_journal_shares_for_level(
    node_ids, memberships, node_lookup, level: str
) -> dict:
    """community_id -> {journal_short: fraction within that community} for Leiden `level`."""
    mem = memberships[level]
    comm_j = defaultdict(Counter)
    for idx, pid in enumerate(node_ids):
        meta = _meta_for_pub(node_lookup, pid)
        if not meta:
            continue
        j = _journal_short(meta)
        comm_j[int(mem[idx])][j] += 1
    out = {}
    for cid, ctr in comm_j.items():
        tot = sum(ctr.values())
        if tot <= 0:
            continue
        out[cid] = {jn: ctr[jn] / tot for jn in ctr}
    return out


def _l1_divergence(p: dict, q: dict) -> float:
    """Half L1 distance between two sparse distributions on the same keys (0–1 scale)."""
    keys = set(p) | set(q)
    if not keys:
        return 0.0
    return 0.5 * sum(abs(p.get(k, 0.0) - q.get(k, 0.0)) for k in keys)


def _top_k_dist(dist: dict, k: int, label_map: dict) -> list:
    items = sorted(dist.items(), key=lambda x: -x[1])[:k]
    return [
        {
            "comm_id": int(cid),
            "share": round(v, 4),
            "label": label_map.get(int(cid), f"Community {cid}"),
        }
        for cid, v in items
    ]


def compute_journal_scope_dashboard_payload(
    node_ids,
    memberships,
    node_lookup,
    profiles: dict,
    year_range: tuple,
) -> dict:
    """
    Per-journal: out-of-scope rate (community share below threshold), drift (L1
    between community distributions, baseline vs recent years), and OOS % split
    by publication year (same rule; counts per calendar year).
    """
    level = JOURNAL_DRIFT_LEVEL
    yr_lo, yr_hi = int(year_range[0]), int(year_range[1])
    mid = (yr_lo + yr_hi) // 2
    baseline_years = list(range(yr_lo, mid + 1))
    recent_years = list(range(mid + 1, yr_hi + 1))
    baseline_set = set(baseline_years)
    recent_set = set(recent_years)

    shares = compute_journal_shares_for_level(node_ids, memberships, node_lookup, level)
    comm_labels = {int(p["id"]): p.get("label", str(p["id"])) for p in profiles[level]}

    journal_set = set()
    for pid in node_ids:
        journal_set.add(_journal_short(_meta_for_pub(node_lookup, pid)))

    mem = memberships[level]
    rows = []
    for jname in sorted(journal_set):
        baseline = Counter()
        recent = Counter()
        per_year_total: Counter = Counter()
        per_year_oos: Counter = Counter()
        total = 0
        oos = 0
        for idx, pid in enumerate(node_ids):
            meta = _meta_for_pub(node_lookup, pid)
            if not meta:
                continue
            if _journal_short(meta) != jname:
                continue
            y = int(meta.get("PublishedYear") or 0)
            cid = int(mem[idx])
            total += 1
            per_year_total[y] += 1
            frac = shares.get(cid, {}).get(jname, 0.0)
            is_oos = frac < OUT_OF_SCOPE_COMMUNITY_SHARE
            if is_oos:
                oos += 1
                per_year_oos[y] += 1
            if y in baseline_set:
                baseline[cid] += 1
            elif y in recent_set:
                recent[cid] += 1

        sb = sum(baseline.values())
        sr = sum(recent.values())
        if sb > 0 and sr > 0:
            p = {c: baseline[c] / sb for c in baseline}
            q = {c: recent[c] / sr for c in recent}
            drift = _l1_divergence(p, q)
        else:
            p, q, drift = {}, {}, 0.0
        oos_pct = round(100.0 * oos / total, 2) if total else 0.0

        oos_by_year = []
        for y in range(yr_lo, yr_hi + 1):
            tot_y = int(per_year_total[y])
            oos_y = int(per_year_oos[y])
            pct_y = round(100.0 * oos_y / tot_y, 2) if tot_y else None
            oos_by_year.append(
                {
                    "year": y,
                    "articles": tot_y,
                    "out_of_scope": oos_y,
                    "out_of_scope_pct": pct_y,
                }
            )

        rows.append(
            {
                "name": jname,
                "articles": int(total),
                "out_of_scope": int(oos),
                "out_of_scope_pct": oos_pct,
                "drift_l1": round(drift, 4),
                "risk": round((oos_pct / 100.0) * drift, 4),
                "oos_by_year": oos_by_year,
                "baseline_top": _top_k_dist(p, 5, comm_labels),
                "recent_top": _top_k_dist(q, 5, comm_labels),
            }
        )

    scatter_rows = []
    for p in profiles[level]:
        jm = p.get("journals") or {}
        entropy = 0.0
        for pct in jm.values():
            x = float(pct) / 100.0
            if x > 0:
                entropy -= x * math.log(x)
        scatter_rows.append(
            {
                "id": int(p["id"]),
                "label": p.get("label", ""),
                "size": int(p["size"]),
                "dominant": p.get("dominant", ""),
                "dominant_pct": float(p.get("dominant_pct", 0)),
                "mix_index": round(100.0 - float(p.get("dominant_pct", 0)), 2),
                "entropy": round(entropy, 3),
                "n_journals": int(p.get("n_journals", 0)),
            }
        )

    scatter_key = f"{level}_communities"
    meta = {
        "leiden_level": level,
        "scatter_series_key": scatter_key,
        "year_range": [yr_lo, yr_hi],
        "baseline_years": baseline_years,
        "recent_years": recent_years,
        "out_of_scope_threshold": OUT_OF_SCOPE_COMMUNITY_SHARE,
        "out_of_scope_rule": (
            f"An article counts as out-of-scope if its own journal represents "
            f"less than {OUT_OF_SCOPE_COMMUNITY_SHARE:.0%} of nodes in its {level} "
            "citation community (it clusters with other journals' literature)."
        ),
        "drift_rule": (
            f"Drift is half the L1 distance between {level}-community distributions "
            "for the same journal: baseline years vs recent years (0 = no change, "
            "up to ~1 = large shift)."
        ),
        "oos_per_year_years": list(range(yr_lo, yr_hi + 1)),
        "oos_by_year_rule": (
            "Per calendar year: same OOS rule as overall (own-journal share in "
            f"{level} community vs threshold); percentages use only articles "
            "published in that year."
        ),
    }
    out = {"meta": meta, "journals": sorted(rows, key=lambda r: -r["risk"])}
    out[scatter_key] = scatter_rows
    return out


def write_scope_journal_dashboard_html(path: str, payload: dict) -> None:
    """Self-contained Plotly dashboard; open locally in a browser."""
    blob = json.dumps(payload, indent=2, ensure_ascii=True).replace("</", "<\\/")
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8" />
<meta name="viewport" content="width=device-width, initial-scale=1" />
<title>Journal scope clusters & drift</title>
<script src="https://cdn.plot.ly/plotly-2.35.2.min.js"></script>
<style>
  body {{ font-family: system-ui, sans-serif; margin: 0; background: #0f172a; color: #e2e8f0; }}
  header {{ padding: 20px 24px; border-bottom: 1px solid #334155; }}
  h1 {{ font-size: 1.35rem; margin: 0 0 6px; }}
  .sub {{ color: #94a3b8; font-size: 0.85rem; max-width: 900px; line-height: 1.45; }}
  main {{ padding: 16px 24px 40px; }}
  .grid {{ display: grid; gap: 18px; grid-template-columns: 1fr 1fr; max-width: 1400px; }}
  @media (max-width: 1000px) {{ .grid {{ grid-template-columns: 1fr; }} }}
  .card {{ background: #1e293b; border-radius: 10px; padding: 14px 16px; border: 1px solid #334155; }}
  .card h2 {{ font-size: 0.95rem; margin: 0 0 10px; color: #f8fafc; }}
  .plot {{ height: 420px; }}
  .plot.tall {{ height: 480px; }}
  table {{ width: 100%; border-collapse: collapse; font-size: 0.8rem; margin-top: 10px; }}
  th, td {{ text-align: left; padding: 6px 8px; border-bottom: 1px solid #334155; }}
  th {{ color: #94a3b8; font-weight: 600; }}
  .pill {{ display: inline-block; background: #334155; padding: 2px 8px; border-radius: 6px; font-size: 0.75rem; }}
</style>
</head>
<body>
<header>
  <h1>Journal scope clusters & drift</h1>
  <p class="sub" id="metaLine"></p>
  <p class="sub" id="ruleLine"></p>
</header>
<main>
  <div class="grid">
    <div class="card">
      <h2>Which journals drift vs carry out-of-scope articles?</h2>
      <div id="scatterDrift" class="plot"></div>
    </div>
    <div class="card">
      <h2 id="h2ClusterScatter">Macro citation communities (mix vs size)</h2>
      <div id="scatterMacro" class="plot"></div>
    </div>
    <div class="card" style="grid-column: 1 / -1;">
      <h2>Out-of-scope rate by journal</h2>
      <div id="barOOS" class="plot tall"></div>
    </div>
    <div class="card" style="grid-column: 1 / -1;">
      <h2>Out-of-scope % by publication year</h2>
      <p class="sub" id="oosYearRule" style="margin:0 0 8px;"></p>
      <div id="barOOSYear" class="plot tall"></div>
    </div>
    <div class="card" style="grid-column: 1 / -1;">
      <h2>Drift (L1) by journal</h2>
      <div id="barDrift" class="plot tall"></div>
    </div>
  </div>
  <div class="card" style="max-width:1400px;margin-top:18px;">
    <h2>OOS % by publication year <span class="pill">hover for OOS count / articles</span></h2>
    <div style="overflow:auto;"><table id="tblYear"><thead id="tblYearHead"></thead><tbody id="tblYearBody"></tbody></table></div>
  </div>
  <div class="card" style="max-width:1400px;margin-top:18px;">
    <h2>Summary table <span class="pill">sorted by risk = OOS% × drift</span></h2>
    <div style="overflow:auto;"><table id="tbl"><thead><tr>
      <th>Journal</th><th>Articles</th><th>Out-of-scope</th><th>OOS %</th><th>Drift L1</th><th>Risk</th>
      <th>Top macro (baseline)</th><th>Top macro (recent)</th>
    </tr></thead><tbody></tbody></table></div>
  </div>
</main>
<script>
const DATA = {blob};
(function () {{
  const M = DATA.meta || {{}};
  document.getElementById("metaLine").textContent =
    "Years " + (M.year_range || []).join("–") +
    " · baseline " + (M.baseline_years || []).join(", ") +
    " · recent " + (M.recent_years || []).join(", ");
  document.getElementById("ruleLine").textContent =
    (M.out_of_scope_rule || "") + " " + (M.drift_rule || "");
  const oosYrEl = document.getElementById("oosYearRule");
  if (oosYrEl) oosYrEl.textContent = (M.oos_by_year_rule || "");
  const lvl = (M.leiden_level || "macro");
  const h2 = document.getElementById("h2ClusterScatter");
  if (h2) h2.textContent = lvl.charAt(0).toUpperCase() + lvl.slice(1) + " citation communities (mix vs size)";

  const J = DATA.journals || [];
  const sk = (M.scatter_series_key || "macro_communities");
  const C = (DATA[sk] || DATA.macro_communities || DATA.meso_communities || []);

  const jNames = J.map(r => r.name);
  const oosPct = J.map(r => r.out_of_scope_pct);
  const drift = J.map(r => r.drift_l1);
  const risk = J.map(r => r.risk);
  const nArt = J.map(r => r.articles);

  Plotly.newPlot("scatterDrift", [{{
    type: "scatter", mode: "markers", x: drift, y: oosPct,
    text: jNames,
    customdata: nArt,
    marker: {{
      size: nArt.map(a => 12 + Math.min(28, Math.sqrt(a) * 1.2)),
      color: risk, colorscale: "Reds", showscale: true,
      colorbar: {{ title: "Risk" }}, line: {{ width: 0.5, color: "#0f172a" }}
    }},
    hovertemplate:
      "<b>%{{text}}</b><br>Drift (L1): %{{x:.3f}}<br>Out-of-scope %: %{{y:.1f}}<br>Articles: %{{customdata}}<extra></extra>"
  }}], {{
    paper_bgcolor: "#1e293b", plot_bgcolor: "#0f172a",
    font: {{ color: "#e2e8f0" }},
    xaxis: {{ title: "Scope drift (L1, baseline vs recent Leiden mix)", gridcolor: "#334155" }},
    yaxis: {{ title: "Out-of-scope articles %", gridcolor: "#334155" }},
    margin: {{ t: 28, l: 56, r: 20, b: 48 }}
  }}, {{ responsive: true }});

  const lab = C.map(c => "C" + c.id + " — " + (c.label || "").slice(0, 42));
  Plotly.newPlot("scatterMacro", [{{
    type: "scatter", mode: "markers",
    x: C.map(c => c.mix_index), y: C.map(c => c.size),
    text: lab,
    customdata: C.map(c => c.dominant),
    marker: {{
      size: C.map(c => 10 + Math.min(36, Math.sqrt(c.size) * 0.35)),
      color: C.map(c => c.entropy), colorscale: "Viridis", showscale: true,
      colorbar: {{ title: "Entropy (journal mix)" }}
    }},
    hovertemplate:
      "<b>%{{text}}</b><br>Cross-journal mix %: %{{x:.1f}}<br>Size: %{{y}}<br>Dominant: %{{customdata}}<extra></extra>"
  }}], {{
    paper_bgcolor: "#1e293b", plot_bgcolor: "#0f172a",
    font: {{ color: "#e2e8f0" }},
    xaxis: {{ title: "Cross-journal mix (100 − dominant journal %)", gridcolor: "#334155" }},
    yaxis: {{ title: "Community size (articles, log)", gridcolor: "#334155", type: "log" }},
    margin: {{ t: 28, l: 56, r: 20, b: 48 }}
  }}, {{ responsive: true }});

  const jSort = [...J].sort((a,b) => b.out_of_scope_pct - a.out_of_scope_pct);
  Plotly.newPlot("barOOS", [{{
    type: "bar",
    x: jSort.map(r => r.name),
    y: jSort.map(r => r.out_of_scope_pct),
    marker: {{ color: "#f97316" }},
    hovertemplate: "%{{x}}<br>OOS %: %{{y:.1f}}<extra></extra>"
  }}], {{
    paper_bgcolor: "#1e293b", plot_bgcolor: "#0f172a",
    font: {{ color: "#e2e8f0" }},
    xaxis: {{ tickangle: -35 }},
    yaxis: {{ title: "Out-of-scope %", gridcolor: "#334155" }},
    margin: {{ t: 20, l: 48, r: 16, b: 120 }}
  }}, {{ responsive: true }});

  const years = M.oos_per_year_years || [];
  if (years.length && document.getElementById("barOOSYear")) {{
    const yearTraces = J.map(r => ({{
      type: "bar",
      name: r.name,
      x: years,
      y: years.map(y => {{
        const row = (r.oos_by_year || []).find(o => o.year === y);
        return row && row.articles ? row.out_of_scope_pct : null;
      }}),
      marker: {{ line: {{ width: 0.3, color: "#0f172a" }} }},
      hovertemplate:
        "<b>%{{fullData.name}}</b><br>Year %{{x}}<br>OOS %: %{{y:.1f}}<br>Articles: %{{customdata}}<extra></extra>",
      customdata: years.map(y => {{
        const row = (r.oos_by_year || []).find(o => o.year === y);
        return row && row.articles ? row.articles : "";
      }})
    }}));
    Plotly.newPlot("barOOSYear", yearTraces, {{
      paper_bgcolor: "#1e293b", plot_bgcolor: "#0f172a",
      font: {{ color: "#e2e8f0" }},
      barmode: "group",
      xaxis: {{ title: "Publication year", gridcolor: "#334155", dtick: 1 }},
      yaxis: {{ title: "Out-of-scope %", gridcolor: "#334155", range: [0, 100] }},
      legend: {{ orientation: "h", yanchor: "top", y: -0.2, x: 0 }},
      margin: {{ t: 20, l: 48, r: 16, b: 140 }}
    }}, {{ responsive: true }});
  }}

  const yh = document.getElementById("tblYearHead");
  const yb = document.getElementById("tblYearBody");
  if (years.length && yh && yb) {{
    const hr = document.createElement("tr");
    hr.innerHTML = "<th>Journal</th>" + years.map(y => "<th>" + y + "</th>").join("");
    yh.appendChild(hr);
    J.forEach(r => {{
      const map = new Map((r.oos_by_year || []).map(o => [o.year, o]));
      const cells = years.map(y => {{
        const o = map.get(y);
        if (!o || !o.articles) return "<td>—</td>";
        const pct = o.out_of_scope_pct;
        const tip = o.out_of_scope + " / " + o.articles + " OOS";
        const txt = pct != null ? pct.toFixed(1) + "%" : "—";
        return "<td title='" + tip + "'>" + txt + "</td>";
      }}).join("");
      const tr = document.createElement("tr");
      tr.innerHTML = "<td>" + r.name + "</td>" + cells;
      yb.appendChild(tr);
    }});
  }}

  const jD = [...J].sort((a,b) => b.drift_l1 - a.drift_l1);
  Plotly.newPlot("barDrift", [{{
    type: "bar",
    x: jD.map(r => r.name),
    y: jD.map(r => r.drift_l1),
    marker: {{ color: "#38bdf8" }},
    hovertemplate: "%{{x}}<br>Drift L1: %{{y:.3f}}<extra></extra>"s
  }}], {{
    paper_bgcolor: "#1e293b", plot_bgcolor: "#0f172a",
    font: {{ color: "#e2e8f0" }},
    xaxis: {{ tickangle: -35 }},
    yaxis: {{ title: "Drift (L1)", gridcolor: "#334155" }},
    margin: {{ t: 20, l: 48, r: 16, b: 120 }}
  }}, {{ responsive: true }});

  const tb = document.querySelector("#tbl tbody");
  J.forEach(r => {{
    const b = (r.baseline_top || []).map(x => x.label + " (" + (100*x.share).toFixed(0) + "%)").join("; ");
    const rc = (r.recent_top || []).map(x => x.label + " (" + (100*x.share).toFixed(0) + "%)").join("; ");
    const tr = document.createElement("tr");
    tr.innerHTML = "<td>" + r.name + "</td><td>" + r.articles + "</td><td>" + r.out_of_scope +
      "</td><td>" + r.out_of_scope_pct.toFixed(1) + "</td><td>" + r.drift_l1.toFixed(3) +
      "</td><td>" + r.risk.toFixed(3) + "</td><td>" + b + "</td><td>" + rc + "</td>";
    tb.appendChild(tr);
  }});
}})();
</script>
</body>
</html>"""
    with open(path, "w", encoding="utf-8") as f:
        f.write(html)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main():
    log.info("=" * 60)
    log.info("SCOPE DRIFT — AIRAK Citation Cluster Analysis")
    log.info("=" * 60)

    # Step 1
    df_journals = get_top_journals(TOP_N_JOURNALS)
    journal_ids = df_journals["JournalId"].tolist()

    # Step 2
    df_edges = get_citation_edges(journal_ids)

    # Step 3
    df_nodes = get_node_metadata(journal_ids)
    node_lookup = df_nodes.set_index("PublicationId").to_dict("index")

    # Step 4
    G, node_ids = build_graph(df_edges)
    del df_edges  # free memory

    memberships = run_leiden_hierarchy(G, LEIDEN_RESOLUTIONS)
    del G  # free memory

    # Step 5
    profiles = profile_communities(
        node_ids,
        memberships,
        node_lookup,
        min_sizes={"macro": 200, "meso": 50, "micro": 50},
        max_per_level={"macro": 30, "meso": 60, "micro": 60},
    )

    # Step 6
    meso_to_macro, micro_to_meso = build_hierarchy(memberships)
    for p in profiles["meso"]:
        p["parent_macro"] = int(meso_to_macro.get(p["id"], -1))
    for p in profiles["micro"]:
        p["parent_meso"] = int(micro_to_meso.get(p["id"], -1))

    # Step 7
    profiles = label_communities_llm(node_ids, memberships, profiles, node_lookup)

    # Save results (fos_global left empty — FoS tab unused when labelling via OpenAI)
    output = {
        "macro": profiles["macro"],
        "meso": profiles["meso"],
        "micro": profiles["micro"],
        "fos_global": {"macro": {}, "meso": {}, "micro": {}},
        "hierarchy": {
            "meso_to_macro": {
                str(p["id"]): p.get("parent_macro", -1) for p in profiles["meso"]
            },
            "micro_to_meso": {
                str(p["id"]): p.get("parent_meso", -1) for p in profiles["micro"]
            },
        },
        "journal_names": [
            j.replace("Frontiers in ", "") for j in df_journals["DisplayName"]
        ],
    }

    dash_payload = compute_journal_scope_dashboard_payload(
        node_ids, memberships, node_lookup, profiles, YEAR_RANGE
    )
    output["journal_drift"] = dash_payload

    with open(os.path.join(OUTPUT_DIR, "cluster_data.json"), "w") as f:
        json.dump(output, f, indent=2, default=str)

    dash_path = os.path.join(OUTPUT_DIR, "scope_journal_dashboard.html")
    write_scope_journal_dashboard_html(dash_path, dash_payload)

    log.info(f"\nSaved cluster_data.json to {OUTPUT_DIR}/")
    log.info(f"  Macro: {len(profiles['macro'])} communities")
    log.info(f"  Meso:  {len(profiles['meso'])} communities")
    log.info(f"  Micro: {len(profiles['micro'])} communities")
    log.info(f"  Journal drift dashboard: {dash_path}")
    log.info("Done!")


if __name__ == "__main__":
    main()
