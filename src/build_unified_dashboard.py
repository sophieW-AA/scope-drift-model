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
    BQ_DATASET    : BigQuery dataset (default: raw_citation_network_data)
    PRIMARY_COVERAGE : fraction of journal papers defining primary clusters (default: 0.8)
    SCOPE_LLM_BORDERLINE_ENABLED : 1/0 — LLM judges OOS communities as borderline (default: 1)
    SCOPE_LLM_BORDERLINE_MODEL : OpenAI model (default: gpt-4o-mini)
    SCOPE_LLM_BORDERLINE_CACHE : cache path under cwts_output (default: scope_llm_borderline.json)
    SCOPE_HARD_NEGATIVES_ENABLED : 1/0 — title hard-negative rules force OOS (default: 1)
    SCOPE_HARD_NEGATIVES_PATH : config JSON path (default: config/journal_hard_negatives.json)
    SCOPE_PAPER_LLM_ENABLED : 1/0 — demote risky primary papers via title LLM (default: 1)
    SCOPE_PAPER_LLM_MODEL : OpenAI model for paper demotion (default: gpt-4o-mini)
    SCOPE_PAPER_LLM_BATCH : titles per API call (default: 20)
    SCOPE_PAPER_LLM_MAX_PER_JOURNAL : cap scored suspicious titles per journal (default: 60)
    SCOPE_DISTANCE_ENABLED : 1/0 — legacy layout-distance rescue (default: 0, off)
    SCOPE_DISTANCE_MODE : nearest_primary | journal_centroid (default: nearest_primary)
    SCOPE_DISTANCE_FACTOR : multiply primary radius for distance threshold (default: 1.25)
    SCOPE_DISTANCE_PERCENTILE : percentile of primary-paper radii used for threshold (default: 95)
    LAYOUT_SEED : seed for Fruchterman-Reingold + paper jitter (default: 42)
"""

import json
import logging
import os
import re
import sys
import time
import urllib.request
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
OUTPUT_DIR = Path(
    r"C:\Users\sophie.wilson\Documents\scope_drift_outputs\dashboards"
)
# LLM borderline / paper-demotion JSON caches (not taxonomy labels)
CACHE_DIR = Path(r"C:\Users\sophie.wilson\Documents\scope_drift_outputs\cache")
RENDER_SCRIPT_PATH = BASE_DIR / "assets" / "render_script.js"

# BigQuery config
BQ_PROJECT = os.environ.get("BQ_PROJECT", "ocean-tech-adv-analytics-c-tfs")
BQ_DATASET = os.environ.get("BQ_DATASET", "raw_citation_network_data")
RUN_TIMESTAMP = os.environ.get("RUN_TIMESTAMP", "")
CLUSTER_LEVEL = os.environ.get("CLUSTER_LEVEL", "macro")

PRIMARY_COVERAGE = float(os.environ.get("PRIMARY_COVERAGE", "0.8"))
BASELINE_YEARS = [2018, 2019, 2020]
MIN_PAPERS_PER_YEAR = 20
MAX_COMMUNITIES = {"macro": 50, "meso": 100, "micro": 200}

# LLM borderline: ask whether non-primary communities are borderline vs hard OOS
SCOPE_LLM_BORDERLINE_ENABLED = os.environ.get(
    "SCOPE_LLM_BORDERLINE_ENABLED", "1"
).strip() not in ("0", "false", "False", "no", "NO")
SCOPE_LLM_BORDERLINE_MODEL = os.environ.get(
    "SCOPE_LLM_BORDERLINE_MODEL", "gpt-4o-mini"
).strip()
SCOPE_LLM_BORDERLINE_CACHE = os.environ.get(
    "SCOPE_LLM_BORDERLINE_CACHE", "scope_llm_borderline.json"
).strip()
BORDERLINE_PROMPT_VERSION = os.environ.get("SCOPE_LLM_BORDERLINE_PROMPT_VERSION", "v2").strip()

def _env_flag(name: str, default: str = "1") -> bool:
    return os.environ.get(name, default).strip() not in ("0", "false", "False", "no", "NO")

SCOPE_HARD_NEGATIVES_ENABLED = _env_flag("SCOPE_HARD_NEGATIVES_ENABLED", "1")
SCOPE_HARD_NEGATIVES_PATH = os.environ.get(
    "SCOPE_HARD_NEGATIVES_PATH", "config/journal_hard_negatives.json"
).strip()

SCOPE_PAPER_LLM_ENABLED = _env_flag("SCOPE_PAPER_LLM_ENABLED", "1")
SCOPE_PAPER_LLM_MODEL = os.environ.get("SCOPE_PAPER_LLM_MODEL", "gpt-4o-mini").strip()
SCOPE_PAPER_LLM_BATCH = int(os.environ.get("SCOPE_PAPER_LLM_BATCH", "20"))
SCOPE_PAPER_LLM_MAX_PER_JOURNAL = int(os.environ.get("SCOPE_PAPER_LLM_MAX_PER_JOURNAL", "60"))
SCOPE_PAPER_LLM_CACHE = os.environ.get(
    "SCOPE_PAPER_LLM_CACHE", "scope_paper_llm.json"
).strip()

# Soft suspicion patterns: only send these titles to paper LLM (keeps API volume tractable)
_DEFAULT_PAPER_LLM_CANDIDATE_PATTERNS = [
    r"(?i)\b(yolo|cnn|transformer|deep learning|computer vision|image segmentation)\b",
    r"(?i)\b(defect|re[- ]?identif|traffic|vehicle|uav|drone)\b",
    r"(?i)\b(fintech|erp|startup|bibliometric|smart city)\b",
    r"(?i)\b(concrete|retaining wall|foundation pit|excavation|backfill)\b",
    r"(?i)\b(pneumonia|x[- ]?ray|endoscopy|table tennis|music performance)\b",
    r"(?i)\b(air conditioning|physical education|labor income)\b",
]

# Legacy secondary rule (layout distance). Off by default — replaced by LLM borderline.
SCOPE_DISTANCE_ENABLED = _env_flag("SCOPE_DISTANCE_ENABLED", "0")
SCOPE_DISTANCE_MODE = os.environ.get("SCOPE_DISTANCE_MODE", "nearest_primary").strip()
SCOPE_DISTANCE_FACTOR = float(os.environ.get("SCOPE_DISTANCE_FACTOR", "1.25"))
SCOPE_DISTANCE_PERCENTILE = float(os.environ.get("SCOPE_DISTANCE_PERCENTILE", "95"))
LAYOUT_SEED = int(os.environ.get("LAYOUT_SEED", "42"))

# Default journals (can be overridden via JOURNALS env var, comma-separated)
_DEFAULT_JOURNALS = [
    "Frontiers in Immunology",
    "Frontiers in Public Health",
    "Frontiers in Medicine",
    "Frontiers in Oncology",
    "Frontiers in Psychology",
]
_JOURNALS_OVERRIDE = os.environ.get("JOURNALS", "").strip()
JOURNALS = [j.strip() for j in _JOURNALS_OVERRIDE.split(",") if j.strip()] if _JOURNALS_OVERRIDE else _DEFAULT_JOURNALS

# Windows consoles / redirected pipes default to cp1252, which cannot encode the
# arrows and box characters used in log messages.
for _stream in (sys.stdout, sys.stderr):
    if hasattr(_stream, "reconfigure"):
        _stream.reconfigure(encoding="utf-8", errors="replace")

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

    client = bigquery.Client(project=BQ_PROJECT, location="EU")

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


def load_all_papers() -> pd.DataFrame:
    """Load ALL papers (including external) from BigQuery for community composition."""
    from google.cloud import bigquery

    tbl_classif = f"{BQ_PROJECT}.{BQ_DATASET}.classification_raw_{RUN_TIMESTAMP}"
    tbl_pub_meta = f"{BQ_PROJECT}.{BQ_DATASET}.pub_metadata_raw_{RUN_TIMESTAMP}"

    log.info(f"       Loading ALL papers for community composition...")

    client = bigquery.Client(project=BQ_PROJECT, location="EU")

    query = f"""
    SELECT 
        c.int_id,
        c.micro,
        c.meso,
        c.macro,
        m.is_frontiers,
        m.journal
    FROM `{tbl_classif}` c
    JOIN `{tbl_pub_meta}` m ON c.int_id = m.int_id
    """

    df = client.query(query).to_dataframe()
    log.info(f"       Loaded {len(df):,} total papers (Frontiers + external)")

    return df


def load_citations() -> pd.DataFrame:
    """Load citation links from BigQuery, filtered to relevant papers only."""
    from google.cloud import bigquery

    tbl_cit_links = f"{BQ_PROJECT}.{BQ_DATASET}.cit_links_raw_{RUN_TIMESTAMP}"
    tbl_classif = f"{BQ_PROJECT}.{BQ_DATASET}.classification_raw_{RUN_TIMESTAMP}"
    tbl_pub_meta = f"{BQ_PROJECT}.{BQ_DATASET}.pub_metadata_raw_{RUN_TIMESTAMP}"

    log.info(f"       Citation links: {tbl_cit_links}")

    client = bigquery.Client(project=BQ_PROJECT, location="EU")

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
        df = pandas_gbq.read_gbq(query, project_id=BQ_PROJECT, location="EU")

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
    """Load cluster short labels for one level from BigQuery taxonomy_labelling."""
    if not RUN_TIMESTAMP:
        log.warning("No RUN_TIMESTAMP — cannot load taxonomy labels from BigQuery")
        return {}

    table = (
        f"{BQ_PROJECT}.taxonomy_labelling.cluster_labels_{level}_{RUN_TIMESTAMP}"
    )
    try:
        client = bigquery.Client(project=BQ_PROJECT, location="EU")
        df = client.query(
            f"SELECT cluster_id, short_label FROM `{table}`"
        ).to_dataframe()
    except Exception as e:
        log.warning("Could not load labels from %s: %s", table, e)
        return {}

    labels = {}
    for _, row in df.iterrows():
        labels[int(row["cluster_id"])] = row["short_label"]
    log.info("       BigQuery %s: %s labels", table.split(".")[-1], len(labels))
    return labels


def load_gpt_labels_all() -> dict:
    """Load taxonomy labels for all levels with full info from BigQuery."""
    labels = {"macro": {}, "meso": {}, "micro": {}}
    if not RUN_TIMESTAMP:
        log.warning("No RUN_TIMESTAMP — cannot load taxonomy labels from BigQuery")
        return labels

    client = bigquery.Client(project=BQ_PROJECT, location="EU")
    for level in ["macro", "meso", "micro"]:
        table = (
            f"{BQ_PROJECT}.taxonomy_labelling.cluster_labels_{level}_{RUN_TIMESTAMP}"
        )
        try:
            df = client.query(
                f"""
                SELECT cluster_id, short_label, long_label, keywords, summary
                FROM `{table}`
                """
            ).to_dataframe()
        except Exception as e:
            log.warning("Could not load labels from %s: %s", table, e)
            continue

        for _, row in df.iterrows():
            cluster_id = int(row["cluster_id"])
            raw_kw = row["keywords"] if "keywords" in row.index else None
            try:
                keywords = eval(raw_kw) if pd.notna(raw_kw) else []
            except Exception:
                keywords = []
            if not isinstance(keywords, list):
                keywords = []
            labels[level][cluster_id] = {
                "short_label": row["short_label"],
                "long_label": row.get("long_label", row["short_label"]),
                "keywords": keywords,
                "summary": (
                    str(row["summary"])
                    if "summary" in row.index and pd.notna(row.get("summary"))
                    else ""
                ),
            }
        log.info(
            "       BigQuery cluster_labels_%s_%s: %s labels",
            level,
            RUN_TIMESTAMP,
            len(labels[level]),
        )
    return labels


# ══════════════════════════════════════════════════════════════════════════════
# SCOPE DASHBOARD
# ══════════════════════════════════════════════════════════════════════════════
def _circular_layout(n: int) -> np.ndarray:
    """Simple circular layout fallback."""
    angles = np.linspace(0, 2 * np.pi, n, endpoint=False)
    return np.column_stack([np.cos(angles), np.sin(angles)])


def compute_scatter_positions(df: pd.DataFrame, df_cit: pd.DataFrame) -> dict:
    """Compute x,y positions for papers using citation-based force-directed layout.

    Community order and Fruchterman-Reingold are seeded so distance-rescue
    (and thus OOS %) is stable across regenerations of the same run.
    """
    import random

    import igraph as ig

    # Stable community → node index mapping (BQ/pandas unique() order is not)
    communities = sorted(df[CLUSTER_LEVEL].dropna().unique(), key=lambda c: int(c))
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
        .sort_values(["src_cluster", "tgt_cluster"])
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
            # igraph FR uses Python's random module for initial placement
            random.seed(LAYOUT_SEED)
            np.random.seed(LAYOUT_SEED)
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
    # Deterministic paper iteration + jitter
    np.random.seed(LAYOUT_SEED)
    jdf_sorted = df.sort_values("int_id")
    for _, row in jdf_sorted.iterrows():
        cx, cy = comm_positions.get(row[CLUSTER_LEVEL], (0.5, 0.5))
        jitter = 0.06
        x = cx + np.random.uniform(-jitter, jitter)
        y = cy + np.random.uniform(-jitter, jitter)
        positions[row["int_id"]] = (float(x), float(y))

    return positions


def compute_primary_clusters(df: pd.DataFrame, journal: str) -> set:
    """Find smallest set of clusters covering PRIMARY_COVERAGE of papers."""
    jdf = df[df["journal"] == journal]
    return compute_primary_clusters_from_frame(jdf)


def compute_primary_clusters_from_frame(jdf: pd.DataFrame) -> set:
    """Primary clusters for an already-filtered journal frame."""
    if jdf.empty:
        return set()
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


def _primary_share_rows(jdf: pd.DataFrame, primary: set, top_n: int = 5) -> list[dict]:
    """Rank primary clusters by share within a year/journal slice."""
    if jdf.empty or not primary:
        return []
    counts = jdf[CLUSTER_LEVEL].value_counts()
    total = int(counts.sum()) or 1
    rows = []
    for comm in primary:
        n = int(counts.get(comm, 0))
        rows.append(
            {
                "comm_id": int(comm),
                "label": GPT_LABELS.get(int(comm), f"Cluster {comm}"),
                "papers": n,
                "share_of_year": round(n / total * 100, 1),
            }
        )
    rows.sort(key=lambda r: (-r["papers"], r["comm_id"]))
    return rows[:top_n]


def compute_primary_shift(
    jdf: pd.DataFrame,
    baseline_year: int = 2020,
    latest_year: int | None = None,
    min_papers: int = 10,
) -> dict:
    """
    Compare primary-cluster sets for baseline_year vs the latest year with enough papers.
    Used in PDF commentary (“have primary clusters changed since 2020?”).
    """
    years = sorted(int(y) for y in jdf["pub_year"].dropna().unique())
    if not years:
        return {}

    if latest_year is None:
        latest_year = years[-1]
    if latest_year not in years:
        latest_year = years[-1]

    base_year = baseline_year if baseline_year in years else years[0]
    base_df = jdf[jdf["pub_year"] == base_year]
    late_df = jdf[jdf["pub_year"] == latest_year]
    if len(base_df) < min_papers or len(late_df) < min_papers:
        return {
            "baseline_year": int(base_year),
            "latest_year": int(latest_year),
            "changed": None,
            "insufficient_data": True,
            "baseline_top": [],
            "latest_top": [],
            "gained_labels": [],
            "lost_labels": [],
        }

    base_primary = compute_primary_clusters_from_frame(base_df)
    late_primary = compute_primary_clusters_from_frame(late_df)
    base_top = _primary_share_rows(base_df, base_primary)
    late_top = _primary_share_rows(late_df, late_primary)

    base_ids = {r["comm_id"] for r in base_top}
    late_ids = {r["comm_id"] for r in late_top}
    # Also compare full primary sets (not only top_n rows)
    full_base = {int(c) for c in base_primary}
    full_late = {int(c) for c in late_primary}
    gained_ids = sorted(full_late - full_base)
    lost_ids = sorted(full_base - full_late)
    changed = full_base != full_late

    return {
        "baseline_year": int(base_year),
        "latest_year": int(latest_year),
        "changed": changed,
        "insufficient_data": False,
        "baseline_primary_ids": sorted(full_base),
        "latest_primary_ids": sorted(full_late),
        "baseline_top": base_top,
        "latest_top": late_top,
        "gained_labels": [
            GPT_LABELS.get(cid, f"Cluster {cid}") for cid in gained_ids
        ],
        "lost_labels": [
            GPT_LABELS.get(cid, f"Cluster {cid}") for cid in lost_ids
        ],
        # Convenience for light overlap checks
        "top_overlap": sorted(base_ids & late_ids),
    }


def _default_on_scope_title_patterns(journal: str) -> list[str]:
    """Heuristic title patterns that suggest a paper still belongs to the journal."""
    bare = re.sub(r"(?i)^frontiers\s+in\s+", "", journal or "").strip().lower()
    extras = {
        "surgery": [
            r"(?i)\b(surg(?:ery|ical|eon)?|operati(?:on|ve)|perioperati(?:ve)?|"
            r"postoperati(?:ve)?|intraoperati(?:ve)?|laparoscop\w*|laparotom\w*|"
            r"endoscop\w*|resect\w*|arthroscop\w*|anesthes\w*|thyroidectomy|"
            r"portoenterostom\w*|fasciotom\w*|fracture|ercp|orthop\w*|implant|"
            r"catheter|anastomosis|hernia|transplant|biopsy|incision|wound|"
            r"flap|graft|tka|osseointegr\w*|tumor|sarcoma|metastas\w*|"
            r"pseudotumor|reconstruct\w*|patellar|femoral|condyle|perforator|"
            r"mammary|clinical|patient|case\s+report|rhizotomy|cholecyst\w*|"
            r"neuromonitor\w*|carpal\s+tunnel|rotator\s+cuff|brachial\s+plexus|"
            r"glioma|corneal|abdominal|tubal|fertility|cadaveric|spasticity)\b"
        ],
        "neurorobotics": [
            r"(?i)\b(neuro(?:robotics?)?|robot(?:ic|ics)?|bci|eeg|emg|"
            r"prosthetic|motor\s+imagery|brain[- ]computer|sensorimotor)\b"
        ],
        "earth science": [
            r"(?i)\b(geolog\w*|seismic|earthquake|volcan\w*|tectonic|"
            r"sediment\w*|stratigraph\w*|paleoclim\w*|geophys\w*|geoinformatic)\b"
        ],
        "environmental science": [
            r"(?i)\b(environment\w*|ecolog\w*|pollut\w*|emission\w*|"
            r"biodiversity|ecosystem|wetland|watershed|air\s+quality|"
            r"water\s+quality|climate|carbon\s+sequestr\w*|invasive\s+species|"
            r"coastal|earth\s+observation|species\s+distribution|monitoring|"
            r"cadmium|soil|plantation|land\s+use|sustainab\w*|heritage|"
            r"geospatial|contamination|remediat\w*)\b"
        ],
        "aging neuroscience": [
            r"(?i)\b(aging|ageing|alzheimer|parkinson|neurodegener\w*|"
            r"dementia|cognitive|brain\s+aging)\b"
        ],
        "chemistry": [r"(?i)\b(chem(?:istry|ical)|synthesis|catalyst|molecule|polymer)\b"],
        "materials": [r"(?i)\b(material\w*|alloy|ceramic|composite|polymer|nano\w*)\b"],
        "robotics and ai": [
            r"(?i)\b(robot(?:ic|ics)?|reinforcement\s+learning|autonom(?:ous|y)|"
            r"manipulator|humanoid)\b"
        ],
    }
    pats = list(extras.get(bare, []))
    for tok in re.split(r"\W+", bare):
        if len(tok) >= 5:
            pats.append(rf"(?i)\b{re.escape(tok)}")
    return pats


def _on_scope_title_patterns(journal: str) -> list[re.Pattern]:
    cfg = load_hard_negative_config()
    jcfg = (cfg.get("journals") or {}).get(journal) or {}
    raw = jcfg.get("on_scope_title_patterns") or _default_on_scope_title_patterns(journal)
    compiled = []
    for p in raw:
        try:
            compiled.append(re.compile(p))
        except re.error:
            continue
    return compiled


def _title_suggests_on_scope(title: str, patterns: list[re.Pattern]) -> bool:
    if not title or not patterns:
        return False
    return any(p.search(title) for p in patterns)


def sample_example_papers(
    jdf: pd.DataFrame,
    n_each: int = 20,
    prefer_year: int = 2026,
    random_state: int = 42,
    journal: str | None = None,
) -> list[dict]:
    """
    Sample in-scope and out-of-scope example titles, preferring prefer_year
    (fallback to more recent years, then older).

    Out-of-scope examples prefer really-OOS papers in prefer_year:
    hard-negative / paper-LLM demotions first, then titles that do not look
    on-topic for the journal (avoids surgical papers falsely clustered OOS, etc.).
    """

    def _pick_by_year(pool: pd.DataFrame, n: int) -> pd.DataFrame:
        if pool.empty or n <= 0:
            return pool.iloc[0:0]
        preferred = pool[pool["pub_year"] == prefer_year]
        if len(preferred) >= n:
            return preferred.sample(n=n, random_state=random_state)
        parts = [preferred] if len(preferred) else []
        need = n - len(preferred)
        others = pool[pool["pub_year"] != prefer_year]
        for y in sorted(others["pub_year"].dropna().unique(), reverse=True):
            if need <= 0:
                break
            ydf = others[others["pub_year"] == y]
            take_n = min(need, len(ydf))
            parts.append(ydf.sample(n=take_n, random_state=random_state))
            need -= take_n
        return pd.concat(parts) if parts else pool.iloc[0:0]

    def _sample_n(pool: pd.DataFrame, n: int) -> pd.DataFrame:
        if pool.empty or n <= 0:
            return pool.iloc[0:0]
        take = min(n, len(pool))
        return pool.sample(n=take, random_state=random_state)

    def _pick_oos(pool: pd.DataFrame, n: int) -> pd.DataFrame:
        """Year-major: clear OOS, then off-topic titles, then remaining."""
        if pool.empty or n <= 0:
            return pool.iloc[0:0]
        jname = journal or (
            str(pool["journal"].iloc[0]) if "journal" in pool.columns and len(pool) else ""
        )
        on_scope_re = _on_scope_title_patterns(jname)
        hn = (
            pool["hard_negative"].fillna(False).astype(bool)
            if "hard_negative" in pool.columns
            else pd.Series(False, index=pool.index)
        )
        dem = (
            pool["paper_demoted"].fillna(False).astype(bool)
            if "paper_demoted" in pool.columns
            else pd.Series(False, index=pool.index)
        )
        clear_mask = hn | dem
        titles = pool["title"].fillna("").astype(str)
        on_scope_mask = titles.map(lambda t: _title_suggests_on_scope(t, on_scope_re))

        # Communities whose labels share tokens with in-scope communities are less
        # persuasive as "really OOS" examples.
        in_scope_ids = set(
            int(c)
            for c in jdf.loc[~jdf["is_oos"], CLUSTER_LEVEL].dropna().unique()
        )
        in_tokens: set[str] = set()
        for cid in in_scope_ids:
            lab = str(GPT_LABELS.get(int(cid), "")).lower()
            in_tokens.update(t for t in re.split(r"\W+", lab) if len(t) >= 4)

        def _foreign_comm(cid) -> bool:
            lab = str(GPT_LABELS.get(int(cid), "")).lower()
            tokens = {t for t in re.split(r"\W+", lab) if len(t) >= 4}
            return not (tokens & in_tokens)

        foreign_mask = pool[CLUSTER_LEVEL].map(_foreign_comm)

        years = []
        if (pool["pub_year"] == prefer_year).any():
            years.append(prefer_year)
        years.extend(
            int(y)
            for y in sorted(pool["pub_year"].dropna().unique(), reverse=True)
            if int(y) != prefer_year
        )

        parts: list[pd.DataFrame] = []
        need = n
        for y in years:
            if need <= 0:
                break
            ymask = pool["pub_year"] == y
            for tier_mask in (
                clear_mask,
                ~clear_mask & ~on_scope_mask & foreign_mask,
                ~clear_mask & ~on_scope_mask & ~foreign_mask,
                ~clear_mask & on_scope_mask,
            ):
                if need <= 0:
                    break
                pick = _sample_n(pool[ymask & tier_mask], need)
                if len(pick):
                    parts.append(pick)
                    need -= len(pick)
        return pd.concat(parts) if parts else pool.iloc[0:0]

    in_scope_df = _pick_by_year(jdf[~jdf["is_oos"]], n_each)
    out_scope_df = _pick_oos(jdf[jdf["is_oos"]], n_each)
    jname = journal or (
        str(jdf["journal"].iloc[0]) if "journal" in jdf.columns and len(jdf) else ""
    )
    on_scope_re = _on_scope_title_patterns(jname)
    in_scope_ids = set(
        int(c) for c in jdf.loc[~jdf["is_oos"], CLUSTER_LEVEL].dropna().unique()
    )
    in_tokens: set[str] = set()
    for cid in in_scope_ids:
        lab = str(GPT_LABELS.get(int(cid), "")).lower()
        in_tokens.update(t for t in re.split(r"\W+", lab) if len(t) >= 4)

    example_papers = []
    for _, row in in_scope_df.iterrows():
        comm_id = int(row[CLUSTER_LEVEL])
        example_papers.append(
            {
                "title": str(row["title"] or "Untitled"),
                "year": int(row["pub_year"]) if pd.notna(row["pub_year"]) else None,
                "is_in_scope": True,
                "is_borderline": bool(row["is_borderline"]),
                "community_id": comm_id,
                "community_label": GPT_LABELS.get(comm_id, f"Cluster {comm_id}"),
            }
        )
    for _, row in out_scope_df.iterrows():
        comm_id = int(row[CLUSTER_LEVEL])
        title = str(row["title"] or "Untitled")
        hn = bool(row.get("hard_negative"))
        dem = bool(row.get("paper_demoted"))
        lab = str(GPT_LABELS.get(comm_id, "")).lower()
        tokens = {t for t in re.split(r"\W+", lab) if len(t) >= 4}
        example_papers.append(
            {
                "title": title,
                "year": int(row["pub_year"]) if pd.notna(row["pub_year"]) else None,
                "is_in_scope": False,
                "is_borderline": False,
                "community_id": comm_id,
                "community_label": GPT_LABELS.get(comm_id, f"Cluster {comm_id}"),
                "hard_negative": hn,
                "paper_demoted": dem,
                "clear_oos": hn or dem,
                "title_on_scope": _title_suggests_on_scope(title, on_scope_re),
                "foreign_community": not (tokens & in_tokens),
            }
        )
    return example_papers


def _community_centroids(jdf: pd.DataFrame, positions: dict) -> dict:
    """Mean (x, y) per community for papers that have layout positions."""
    buckets = defaultdict(list)
    for _, row in jdf.iterrows():
        pos = positions.get(row["int_id"])
        if pos is None:
            continue
        buckets[row[CLUSTER_LEVEL]].append(pos)
    centroids = {}
    for comm, pts in buckets.items():
        arr = np.asarray(pts, dtype=float)
        centroids[comm] = (float(arr[:, 0].mean()), float(arr[:, 1].mean()))
    return centroids


def compute_distance_rescued_clusters(
    jdf: pd.DataFrame,
    positions: dict,
    primary_clusters: set,
) -> tuple[set, dict]:
    """
    Secondary in-scope rule: non-primary communities whose layout centroid is
    close enough to the journal / primary-cluster core are treated as in-scope
    (false-OOS rescue via outlier-distance framing).

    Returns (rescued_cluster_ids, debug_meta).
    """
    meta = {
        "enabled": SCOPE_DISTANCE_ENABLED,
        "mode": SCOPE_DISTANCE_MODE,
        "factor": SCOPE_DISTANCE_FACTOR,
        "percentile": SCOPE_DISTANCE_PERCENTILE,
        "threshold": None,
        "rescued": [],
    }
    if not SCOPE_DISTANCE_ENABLED or not primary_clusters:
        return set(), meta

    centroids = _community_centroids(jdf, positions)
    primary_centroids = {
        c: centroids[c] for c in primary_clusters if c in centroids
    }
    if not primary_centroids:
        return set(), meta

    # Paper-level distances to reference → set a radius that covers most of the core
    primary_paper_dists = []
    for _, row in jdf.iterrows():
        if row[CLUSTER_LEVEL] not in primary_clusters:
            continue
        pos = positions.get(row["int_id"])
        if pos is None:
            continue
        x, y = pos
        if SCOPE_DISTANCE_MODE == "journal_centroid":
            ref_pts = np.asarray(list(primary_centroids.values()), dtype=float)
            jx, jy = float(ref_pts[:, 0].mean()), float(ref_pts[:, 1].mean())
            primary_paper_dists.append(float(np.hypot(x - jx, y - jy)))
        else:
            # nearest_primary: distance to own / nearest primary community centroid
            dmin = min(
                float(np.hypot(x - cx, y - cy))
                for cx, cy in primary_centroids.values()
            )
            primary_paper_dists.append(dmin)

    if not primary_paper_dists:
        return set(), meta

    base_radius = float(
        np.percentile(primary_paper_dists, SCOPE_DISTANCE_PERCENTILE)
    )
    # Avoid a degenerate zero threshold when all primary papers sit on centroids
    if base_radius < 1e-6:
        base_radius = float(np.max(primary_paper_dists) or 0.05)
    threshold = base_radius * SCOPE_DISTANCE_FACTOR
    meta["threshold"] = round(threshold, 5)

    ref_pts = np.asarray(list(primary_centroids.values()), dtype=float)
    journal_xy = (float(ref_pts[:, 0].mean()), float(ref_pts[:, 1].mean()))
    if SCOPE_DISTANCE_MODE == "journal_centroid":
        meta["journal_centroid"] = {
            "x": round(journal_xy[0], 4),
            "y": round(journal_xy[1], 4),
        }

    rescued = set()
    for comm, (cx, cy) in centroids.items():
        if comm in primary_clusters:
            continue
        if SCOPE_DISTANCE_MODE == "journal_centroid":
            d = float(np.hypot(cx - journal_xy[0], cy - journal_xy[1]))
        else:
            d = min(
                float(np.hypot(cx - px, cy - py))
                for px, py in primary_centroids.values()
            )
        if d <= threshold:
            rescued.add(comm)
            meta["rescued"].append(
                {
                    "comm_id": int(comm),
                    "label": GPT_LABELS.get(int(comm), f"Cluster {comm}"),
                    "distance": round(d, 5),
                }
            )

    meta["rescued"].sort(key=lambda r: r["distance"])
    return rescued, meta


BORDERLINE_SYSTEM_PROMPT = """You are an editorial scope analyst for Frontiers journals.

You judge whether citation-network communities that fall outside a journal's
primary scope core are HARD out-of-scope, or BORDERLINE (plausibly adjacent /
interdisciplinary / occasionally acceptable, but not core).

Definitions:
- primary / in-scope: the journal's core topical communities (already given; do not reclassify them).
- borderline: not core, but the community's methods or topics are applied TO THIS JOURNAL'S
  DOMAIN. Examples that SHOULD be borderline:
  • AI / remote sensing / control methods used for wetlands, coastal monitoring, geology
  • VR / mixed reality used for surgical education or clinical training
  • Adjacent clinical/biological phenomena clearly relevant to the journal's mission
- out_of_scope: methods-only or buzzword overlap WITHOUT the journal's domain. Examples:
  • Generic deep learning / computer vision / robotics with no neuro/rehab/BCI link
  • Civil/structural construction engineering without geoscience
  • Fintech, management, PE curriculum, or "sustainability" business topics without
    environmental measurement or ecological substance
  • Superficial keyword overlap only

Be conservative with borderline: most non-primary communities should stay out_of_scope.
Rescue interdisciplinary *domain applications*; reject opportunistic method dumping.

Respond with ONLY a JSON object:
{
  "decisions": [
    {
      "comm_id": 12,
      "verdict": "borderline" | "out_of_scope",
      "reason": "one short sentence"
    }
  ]
}
Include every candidate community exactly once. No markdown fences."""


PAPER_SCOPE_SYSTEM_PROMPT = """You are an editorial scope analyst for a Frontiers journal.

You review paper TITLES that currently sit in a broad primary (core) citation community.
Some of those communities are method-broad and contain opportunistic out-of-scope papers.

For each paper, decide:
- in_scope: title clearly fits the journal's scholarly mission / domain
- out_of_scope: title is methods-only drift, wrong field, or only superficial keyword overlap

Be strict on method dumping (generic CV/DL, civil engineering, fintech/management) when
there is no clear link to the journal domain. When unsure but domain cues are present,
prefer in_scope.

Respond with ONLY a JSON object:
{
  "decisions": [
    {
      "int_id": 123,
      "verdict": "in_scope" | "out_of_scope",
      "reason": "one short sentence"
    }
  ]
}
Include every paper exactly once. No markdown fences."""


def _load_dotenv_openai() -> None:
    env_path = BASE_DIR / ".env"
    if not env_path.exists():
        return
    for line in env_path.read_text(encoding="utf-8").splitlines():
        if "=" in line and not line.strip().startswith("#"):
            k, v = line.split("=", 1)
            os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))


def _borderline_cache_path() -> Path:
    name = SCOPE_LLM_BORDERLINE_CACHE
    path = Path(name)
    if not path.is_absolute():
        path = CACHE_DIR / name
    # Namespace by run + cluster level so caches don't cross runs
    if RUN_TIMESTAMP and "scope_llm_borderline" in path.name:
        stem = path.stem
        path = path.with_name(f"{stem}_{RUN_TIMESTAMP}_{CLUSTER_LEVEL}{path.suffix}")
    return path


def _call_openai_borderline(user_prompt: str) -> str:
    _load_dotenv_openai()
    key = os.environ.get("OPENAI_API_KEY")
    if not key:
        raise RuntimeError("OPENAI_API_KEY is not set (needed for LLM borderline scope)")

    body = json.dumps(
        {
            "model": SCOPE_LLM_BORDERLINE_MODEL,
            "max_tokens": 1200,
            "temperature": 0.1,
            "messages": [
                {"role": "system", "content": BORDERLINE_SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt},
            ],
        }
    ).encode("utf-8")
    req = urllib.request.Request(
        "https://api.openai.com/v1/chat/completions",
        data=body,
        headers={
            "Authorization": f"Bearer {key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    last_err = None
    for attempt in range(1, 4):
        try:
            with urllib.request.urlopen(req, timeout=60) as resp:
                data = json.loads(resp.read().decode("utf-8"))
            return data["choices"][0]["message"]["content"].strip()
        except Exception as e:
            last_err = e
            log.warning("LLM borderline call attempt %s failed: %s", attempt, e)
            time.sleep(3 * attempt)
    raise RuntimeError(f"LLM borderline call failed: {last_err}")


def _parse_borderline_json(raw: str) -> list[dict]:
    text = raw.strip()
    if text.startswith("```"):
        text = text.strip("`")
        if text.startswith("json"):
            text = text[4:].strip()
    data = json.loads(text)
    decisions = data.get("decisions") if isinstance(data, dict) else data
    if not isinstance(decisions, list):
        raise ValueError("LLM response missing decisions list")
    return decisions


def compute_llm_borderline_clusters(
    journal: str,
    jdf: pd.DataFrame,
    primary_clusters: set,
) -> tuple[set, dict]:
    """
    Ask an LLM which non-primary communities in this journal are borderline
    (vs hard out-of-scope). Results are cached under cwts_output/.
    """
    meta = {
        "enabled": SCOPE_LLM_BORDERLINE_ENABLED,
        "model": SCOPE_LLM_BORDERLINE_MODEL,
        "source": "llm",
        "decisions": [],
        "cached": False,
    }
    if not SCOPE_LLM_BORDERLINE_ENABLED or not primary_clusters:
        return set(), meta

    n_articles = len(jdf)
    counts = jdf[CLUSTER_LEVEL].value_counts()
    candidates = []
    for comm, count in counts.items():
        if comm in primary_clusters:
            continue
        cid = int(comm)
        label = GPT_LABELS.get(cid, f"Cluster {cid}")
        info = GPT_LABELS_ALL.get(CLUSTER_LEVEL, {}).get(cid, {})
        candidates.append(
            {
                "comm_id": cid,
                "label": label,
                "long_label": info.get("long_label", label) if isinstance(info, dict) else label,
                "papers_in_journal": int(count),
                "share_of_journal_pct": round(100.0 * count / n_articles, 2) if n_articles else 0.0,
            }
        )

    if not candidates:
        return set(), meta

    # Only send communities with a meaningful share (avoid tiny noise)
    candidates_for_llm = [
        c for c in candidates if c["papers_in_journal"] >= 3 or c["share_of_journal_pct"] >= 0.3
    ]
    if not candidates_for_llm:
        candidates_for_llm = candidates[:15]

    primary_payload = []
    for comm in sorted(primary_clusters, key=lambda x: int(x)):
        cid = int(comm)
        primary_payload.append(
            {
                "comm_id": cid,
                "label": GPT_LABELS.get(cid, f"Cluster {cid}"),
                "papers_in_journal": int(counts.get(comm, 0)),
                "share_of_journal_pct": round(
                    100.0 * counts.get(comm, 0) / n_articles, 2
                )
                if n_articles
                else 0.0,
            }
        )

    cache_path = _borderline_cache_path()
    cache: dict = {}
    if cache_path.exists():
        try:
            cache = json.loads(cache_path.read_text(encoding="utf-8"))
        except Exception:
            cache = {}

    cache_key = journal
    # Invalidate if candidate set changed
    cand_sig = sorted(c["comm_id"] for c in candidates_for_llm)
    primary_sig = sorted(int(c) for c in primary_clusters)
    cached_entry = cache.get(cache_key) if isinstance(cache, dict) else None
    if (
        isinstance(cached_entry, dict)
        and cached_entry.get("candidate_ids") == cand_sig
        and cached_entry.get("primary_ids") == primary_sig
        and cached_entry.get("model") == SCOPE_LLM_BORDERLINE_MODEL
        and cached_entry.get("prompt_version") == BORDERLINE_PROMPT_VERSION
    ):
        borderline = {int(x) for x in cached_entry.get("borderline_ids", [])}
        meta["decisions"] = cached_entry.get("decisions", [])
        meta["cached"] = True
        meta["prompt_version"] = BORDERLINE_PROMPT_VERSION
        return borderline, meta

    user_prompt = (
        f"Journal: {journal}\n\n"
        f"Primary (in-scope) communities for this journal "
        f"(~{PRIMARY_COVERAGE*100:.0f}% coverage core):\n"
        f"{json.dumps(primary_payload, indent=2)}\n\n"
        f"Candidate non-primary communities to classify "
        f"(borderline vs out_of_scope):\n"
        f"{json.dumps(candidates_for_llm, indent=2)}\n"
    )

    try:
        raw = _call_openai_borderline(user_prompt)
        decisions = _parse_borderline_json(raw)
    except Exception as e:
        log.warning("LLM borderline failed for %s: %s — no borderline applied", journal, e)
        meta["error"] = str(e)
        return set(), meta

    borderline = set()
    cleaned = []
    valid_ids = {c["comm_id"] for c in candidates_for_llm}
    for d in decisions:
        try:
            cid = int(d.get("comm_id"))
        except (TypeError, ValueError):
            continue
        if cid not in valid_ids:
            continue
        verdict = str(d.get("verdict", "")).strip().lower().replace(" ", "_")
        if verdict in {"borderline", "border_line", "border-line"}:
            borderline.add(cid)
            verdict = "borderline"
        else:
            verdict = "out_of_scope"
        cleaned.append(
            {
                "comm_id": cid,
                "label": GPT_LABELS.get(cid, f"Cluster {cid}"),
                "verdict": verdict,
                "reason": str(d.get("reason") or "")[:240],
            }
        )

    meta["decisions"] = cleaned
    meta["prompt_version"] = BORDERLINE_PROMPT_VERSION
    cache[cache_key] = {
        "model": SCOPE_LLM_BORDERLINE_MODEL,
        "prompt_version": BORDERLINE_PROMPT_VERSION,
        "primary_ids": primary_sig,
        "candidate_ids": cand_sig,
        "borderline_ids": sorted(borderline),
        "decisions": cleaned,
    }
    try:
        cache_path.parent.mkdir(parents=True, exist_ok=True)
        cache_path.write_text(json.dumps(cache, indent=2), encoding="utf-8")
    except Exception as e:
        log.warning("Could not write borderline cache %s: %s", cache_path, e)

    return borderline, meta


# ══════════════════════════════════════════════════════════════════════════════
# HARD-NEGATIVES + PAPER-LEVEL LLM DEMOTION
# ══════════════════════════════════════════════════════════════════════════════

_HARD_NEG_CONFIG_CACHE: dict | None = None


def _hard_neg_config_path() -> Path:
    path = Path(SCOPE_HARD_NEGATIVES_PATH)
    if not path.is_absolute():
        path = BASE_DIR / path
    return path


def load_hard_negative_config() -> dict:
    global _HARD_NEG_CONFIG_CACHE
    if _HARD_NEG_CONFIG_CACHE is not None:
        return _HARD_NEG_CONFIG_CACHE
    path = _hard_neg_config_path()
    if not path.exists():
        _HARD_NEG_CONFIG_CACHE = {}
        return _HARD_NEG_CONFIG_CACHE
    try:
        _HARD_NEG_CONFIG_CACHE = json.loads(path.read_text(encoding="utf-8"))
    except Exception as e:
        log.warning("Could not load hard-negatives config %s: %s", path, e)
        _HARD_NEG_CONFIG_CACHE = {}
    return _HARD_NEG_CONFIG_CACHE


def apply_hard_negatives(journal: str, jdf: pd.DataFrame) -> tuple[pd.Series, dict]:
    """
    Return boolean mask (index-aligned with jdf) of papers forced OOS by title rules.
    """
    meta = {
        "enabled": SCOPE_HARD_NEGATIVES_ENABLED,
        "n_flagged": 0,
        "examples": [],
    }
    mask = pd.Series(False, index=jdf.index)
    if not SCOPE_HARD_NEGATIVES_ENABLED or jdf.empty:
        return mask, meta

    cfg = load_hard_negative_config()
    jcfg = (cfg.get("journals") or {}).get(journal) or {}
    force_pats = jcfg.get("force_oos_patterns") or []
    unless_pats = jcfg.get("unless_patterns") or []
    if not force_pats:
        return mask, meta

    force_re = [re.compile(p) for p in force_pats]
    unless_re = [re.compile(p) for p in unless_pats]

    examples = []
    for idx, row in jdf.iterrows():
        title = str(row.get("title") or "")
        if not title:
            continue
        if not any(r.search(title) for r in force_re):
            continue
        if unless_re and any(r.search(title) for r in unless_re):
            continue
        mask.at[idx] = True
        if len(examples) < 8:
            examples.append(
                {
                    "int_id": int(row["int_id"]),
                    "title": title[:140],
                    "source": "hard_negative",
                }
            )

    meta["n_flagged"] = int(mask.sum())
    meta["examples"] = examples
    if meta["n_flagged"]:
        log.info(
            "       %s: hard-negatives flagged %s paper(s)",
            journal,
            meta["n_flagged"],
        )
    return mask, meta


def _risky_primary_ids(journal: str, primary_clusters: set) -> set[int]:
    cfg = load_hard_negative_config()
    jcfg = (cfg.get("journals") or {}).get(journal) or {}
    labels = jcfg.get("risky_primary_labels") or cfg.get("default_risky_primary_labels") or []
    label_set = {str(x).strip().lower() for x in labels}
    risky = set()
    for comm in primary_clusters:
        cid = int(comm)
        lab = str(GPT_LABELS.get(cid, "")).strip().lower()
        if lab in label_set:
            risky.add(cid)
    return risky


def _paper_llm_cache_path() -> Path:
    name = SCOPE_PAPER_LLM_CACHE
    path = Path(name)
    if not path.is_absolute():
        path = CACHE_DIR / name
    if RUN_TIMESTAMP and "scope_paper_llm" in path.name:
        stem = path.stem
        path = path.with_name(f"{stem}_{RUN_TIMESTAMP}_{CLUSTER_LEVEL}{path.suffix}")
    return path


def _call_openai_chat(system_prompt: str, user_prompt: str, model: str, max_tokens: int = 2000) -> str:
    _load_dotenv_openai()
    key = os.environ.get("OPENAI_API_KEY")
    if not key:
        raise RuntimeError("OPENAI_API_KEY is not set")
    body = json.dumps(
        {
            "model": model,
            "max_tokens": max_tokens,
            "temperature": 0.1,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
        }
    ).encode("utf-8")
    req = urllib.request.Request(
        "https://api.openai.com/v1/chat/completions",
        data=body,
        headers={
            "Authorization": f"Bearer {key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    last_err = None
    for attempt in range(1, 4):
        try:
            with urllib.request.urlopen(req, timeout=90) as resp:
                data = json.loads(resp.read().decode("utf-8"))
            return data["choices"][0]["message"]["content"].strip()
        except Exception as e:
            last_err = e
            log.warning("OpenAI chat attempt %s failed: %s", attempt, e)
            time.sleep(3 * attempt)
    raise RuntimeError(f"OpenAI chat failed: {last_err}")


def _parse_paper_scope_json(raw: str) -> list[dict]:
    text = raw.strip()
    if text.startswith("```"):
        text = text.strip("`")
        if text.startswith("json"):
            text = text[4:].strip()
    data = json.loads(text)
    decisions = data.get("decisions") if isinstance(data, dict) else data
    if not isinstance(decisions, list):
        raise ValueError("paper LLM response missing decisions list")
    return decisions


def compute_paper_scope_overrides(
    journal: str,
    jdf: pd.DataFrame,
    primary_clusters: set,
    already_oos_mask: pd.Series | None = None,
) -> tuple[dict[int, dict], dict]:
    """
    Demote risky-primary papers to OOS via title LLM.
    Returns {int_id: {verdict, reason, source, community_id}} for demotions only,
    plus meta.
    """
    meta = {
        "enabled": SCOPE_PAPER_LLM_ENABLED,
        "model": SCOPE_PAPER_LLM_MODEL,
        "n_scored": 0,
        "n_demoted": 0,
        "n_cached": 0,
        "risky_primary_ids": [],
        "decisions": [],
    }
    if not SCOPE_PAPER_LLM_ENABLED or jdf.empty or not primary_clusters:
        return {}, meta

    risky = _risky_primary_ids(journal, primary_clusters)
    meta["risky_primary_ids"] = sorted(risky)
    if not risky:
        return {}, meta

    candidates = jdf[jdf[CLUSTER_LEVEL].isin(risky)].copy()
    if already_oos_mask is not None:
        candidates = candidates[~already_oos_mask.reindex(candidates.index).fillna(False)]
    # Only demote papers that would otherwise be treated as in-scope via primary
    candidates = candidates[candidates[CLUSTER_LEVEL].isin(primary_clusters)]
    if candidates.empty:
        return {}, meta

    # Prefer suspicious titles so we don't score entire primary communities
    cfg = load_hard_negative_config()
    jcfg = (cfg.get("journals") or {}).get(journal) or {}
    cand_pats = (
        jcfg.get("paper_llm_candidate_patterns")
        or cfg.get("paper_llm_candidate_patterns")
        or _DEFAULT_PAPER_LLM_CANDIDATE_PATTERNS
    )
    cand_re = [re.compile(p) for p in cand_pats]
    if cand_re:
        sus_mask = candidates["title"].fillna("").astype(str).apply(
            lambda t: any(r.search(t) for r in cand_re)
        )
        suspicious = candidates[sus_mask]
        if not suspicious.empty:
            candidates = suspicious
    if len(candidates) > SCOPE_PAPER_LLM_MAX_PER_JOURNAL:
        candidates = candidates.sample(
            n=SCOPE_PAPER_LLM_MAX_PER_JOURNAL, random_state=42
        )
    meta["n_candidates"] = int(len(candidates))

    cache_path = _paper_llm_cache_path()
    cache: dict = {}
    if cache_path.exists():
        try:
            cache = json.loads(cache_path.read_text(encoding="utf-8"))
        except Exception:
            cache = {}
    journal_cache = cache.get(journal) if isinstance(cache.get(journal), dict) else {}
    if not isinstance(journal_cache, dict):
        journal_cache = {}

    to_score = []
    demotions: dict[int, dict] = {}
    decisions_out = []

    for _, row in candidates.iterrows():
        iid = int(row["int_id"])
        title = str(row.get("title") or "").strip()
        cid = int(row[CLUSTER_LEVEL])
        cached = journal_cache.get(str(iid))
        if (
            isinstance(cached, dict)
            and cached.get("model") == SCOPE_PAPER_LLM_MODEL
            and cached.get("title") == title
        ):
            meta["n_cached"] += 1
            verdict = str(cached.get("verdict", "in_scope")).lower()
            entry = {
                "int_id": iid,
                "verdict": "out_of_scope" if verdict == "out_of_scope" else "in_scope",
                "reason": str(cached.get("reason") or "")[:240],
                "source": "paper_llm",
                "community_id": cid,
                "community_label": GPT_LABELS.get(cid, f"Cluster {cid}"),
                "title": title[:140],
            }
            decisions_out.append(entry)
            if entry["verdict"] == "out_of_scope":
                demotions[iid] = entry
            continue
        if title:
            to_score.append({"int_id": iid, "title": title, "community_id": cid})

    batch_size = max(1, SCOPE_PAPER_LLM_BATCH)
    for i in range(0, len(to_score), batch_size):
        batch = to_score[i : i + batch_size]
        payload = [
            {
                "int_id": p["int_id"],
                "title": p["title"][:300],
                "community_label": GPT_LABELS.get(
                    p["community_id"], f"Cluster {p['community_id']}"
                ),
            }
            for p in batch
        ]
        user_prompt = (
            f"Journal: {journal}\n\n"
            f"These papers sit in broad PRIMARY communities. Classify each title.\n"
            f"{json.dumps(payload, indent=2)}\n"
        )
        try:
            raw = _call_openai_chat(
                PAPER_SCOPE_SYSTEM_PROMPT,
                user_prompt,
                SCOPE_PAPER_LLM_MODEL,
                max_tokens=2500,
            )
            parsed = _parse_paper_scope_json(raw)
        except Exception as e:
            log.warning("Paper LLM failed for %s batch: %s", journal, e)
            meta["error"] = str(e)
            break

        by_id = {}
        for d in parsed:
            try:
                by_id[int(d.get("int_id"))] = d
            except (TypeError, ValueError):
                continue

        for p in batch:
            iid = p["int_id"]
            d = by_id.get(iid, {})
            verdict = str(d.get("verdict", "in_scope")).strip().lower().replace(" ", "_")
            if verdict not in {"in_scope", "out_of_scope"}:
                verdict = "in_scope"
            reason = str(d.get("reason") or "")[:240]
            entry = {
                "int_id": iid,
                "verdict": verdict,
                "reason": reason,
                "source": "paper_llm",
                "community_id": p["community_id"],
                "community_label": GPT_LABELS.get(
                    p["community_id"], f"Cluster {p['community_id']}"
                ),
                "title": p["title"][:140],
            }
            decisions_out.append(entry)
            journal_cache[str(iid)] = {
                "model": SCOPE_PAPER_LLM_MODEL,
                "title": p["title"],
                "verdict": verdict,
                "reason": reason,
                "community_id": p["community_id"],
            }
            if verdict == "out_of_scope":
                demotions[iid] = entry

    meta["n_scored"] = len(to_score)
    meta["n_demoted"] = len(demotions)
    meta["decisions"] = [
        d for d in decisions_out if d.get("verdict") == "out_of_scope"
    ][:40]

    cache[journal] = journal_cache
    try:
        cache_path.parent.mkdir(parents=True, exist_ok=True)
        cache_path.write_text(json.dumps(cache, indent=2), encoding="utf-8")
    except Exception as e:
        log.warning("Could not write paper LLM cache %s: %s", cache_path, e)

    if meta["n_demoted"]:
        log.info(
            "       %s: paper LLM demoted %s / scored %s (cached hits %s) in risky primaries %s",
            journal,
            meta["n_demoted"],
            meta["n_scored"],
            meta["n_cached"],
            meta["risky_primary_ids"],
        )
    return demotions, meta


def compute_journal_stats(df: pd.DataFrame, positions: dict) -> list:
    """Compute statistics for each journal."""
    journals_data = []
    years = sorted(df["pub_year"].unique())

    for journal in JOURNALS:
        jdf = df[df["journal"] == journal].copy()
        if jdf.empty:
            continue

        primary_clusters = compute_primary_clusters(df, journal)

        # Prefer LLM borderline; optional legacy distance rescue if explicitly enabled
        borderline_clusters, border_meta = compute_llm_borderline_clusters(
            journal, jdf, primary_clusters
        )
        dist_meta = {"enabled": False}
        if SCOPE_DISTANCE_ENABLED:
            dist_rescued, dist_meta = compute_distance_rescued_clusters(
                jdf, positions, primary_clusters
            )
            # Distance only adds clusters not already decided by LLM path when LLM off
            if not SCOPE_LLM_BORDERLINE_ENABLED:
                borderline_clusters = set(dist_rescued)
                border_meta = {
                    "enabled": True,
                    "source": "distance",
                    "decisions": dist_meta.get("rescued", []),
                    **{k: dist_meta.get(k) for k in ("mode", "factor", "percentile", "threshold")},
                }

        # Soft in-scope set for OOS%: primary ∪ borderline (borderline is not hard OOS)
        soft_in_scope = set(primary_clusters) | set(borderline_clusters)
        jdf["is_oos"] = ~jdf[CLUSTER_LEVEL].isin(soft_in_scope)
        jdf["is_borderline"] = jdf[CLUSTER_LEVEL].isin(borderline_clusters)
        jdf["hard_negative"] = False
        jdf["paper_demoted"] = False

        # Title hard-negatives: force OOS even inside primary/borderline communities
        hn_mask, hn_meta = apply_hard_negatives(journal, jdf)
        if hn_mask.any():
            jdf.loc[hn_mask, "is_oos"] = True
            jdf.loc[hn_mask, "is_borderline"] = False
            jdf.loc[hn_mask, "hard_negative"] = True

        # Paper-level LLM demotion inside risky primary communities
        paper_demotions, paper_meta = compute_paper_scope_overrides(
            journal, jdf, primary_clusters, already_oos_mask=jdf["is_oos"]
        )
        if paper_demotions:
            demote_ids = set(paper_demotions.keys())
            demote_mask = jdf["int_id"].isin(demote_ids)
            jdf.loc[demote_mask, "is_oos"] = True
            jdf.loc[demote_mask, "is_borderline"] = False
            jdf.loc[demote_mask, "paper_demoted"] = True

        # Combined per-paper overrides for GT map / apply scripts
        paper_overrides: dict[str, dict] = {}
        for idx in jdf.index[jdf["hard_negative"]]:
            iid = int(jdf.at[idx, "int_id"])
            paper_overrides[str(iid)] = {
                "verdict": "out_of_scope",
                "reason": "hard_negative title rule",
                "source": "hard_negative",
                "community_id": int(jdf.at[idx, CLUSTER_LEVEL]),
            }
        for iid, entry in paper_demotions.items():
            paper_overrides[str(iid)] = {
                "verdict": "out_of_scope",
                "reason": entry.get("reason") or "",
                "source": "paper_llm",
                "community_id": entry.get("community_id"),
            }

        n_articles = len(jdf)
        n_oos = int(jdf["is_oos"].sum())
        oos_pct = (n_oos / n_articles * 100) if n_articles else 0
        n_borderline_papers = int(jdf["is_borderline"].sum())
        n_hard_neg = int(jdf["hard_negative"].sum())
        n_paper_demoted = int(jdf["paper_demoted"].sum())

        if borderline_clusters:
            labels = ", ".join(
                f"C{int(c)}:{GPT_LABELS.get(int(c), str(c))}"
                for c in sorted(borderline_clusters, key=lambda x: int(x))
            )
            src = border_meta.get("source", "llm")
            cached = " (cached)" if border_meta.get("cached") else ""
            log.info(
                f"       {journal}: borderline [{src}]{cached} "
                f"{len(borderline_clusters)} cluster(s) "
                f"({n_borderline_papers} papers) → {labels}"
            )

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
        for comm, count in comm_counts.head(15).items():
            label = GPT_LABELS.get(int(comm), f"Cluster {comm}")
            top_comms.append({
                "comm_id": int(comm),
                "label": label,
                "is_primary": comm in primary_clusters,
                "is_distance_rescued": comm in borderline_clusters,  # legacy alias
                "is_borderline": comm in borderline_clusters,
                "is_in_scope": comm in soft_in_scope,
                "papers_in_comm": int(count),
                "share_of_journal": round(count / n_articles * 100, 1),
            })

        scatter = []
        for _, row in jdf.iterrows():
            if row["int_id"] in positions:
                x, y = positions[row["int_id"]]
                # s: 2=primary-ish in-scope, 1=borderline, 0=oos (after demotions)
                if row["is_oos"]:
                    s = 0
                elif row["is_borderline"]:
                    s = 1
                else:
                    s = 2
                scatter.append({
                    "x": round(x, 4),
                    "y": round(y, 4),
                    "c": int(row[CLUSTER_LEVEL]),
                    "t": str(row["title"] or "")[:50],
                    "i": int(row["int_id"]),
                    "s": s,
                    "yr": int(row["pub_year"]) if pd.notna(row["pub_year"]) else None,
                })

        # Prefer 2026 titles when available; fall back to more recent years.
        # OOS examples prefer clear/hard-negative demotions, then off-topic titles.
        example_papers = sample_example_papers(
            jdf, n_each=20, prefer_year=2026, random_state=42, journal=journal
        )
        primary_shift = compute_primary_shift(jdf, baseline_year=2020)

        borderline_ids = [int(c) for c in sorted(borderline_clusters, key=int)]
        journals_data.append({
            "name": journal,
            "articles": n_articles,
            "out_of_scope": int(n_oos),
            "out_of_scope_pct": round(oos_pct, 1),
            "n_primary_clusters": len(primary_clusters),
            "n_borderline_clusters": len(borderline_clusters),
            "n_borderline_papers": n_borderline_papers,
            "n_hard_negative_papers": n_hard_neg,
            "n_paper_demoted": n_paper_demoted,
            "n_distance_rescued_clusters": len(borderline_clusters),  # legacy
            "n_distance_rescued_papers": n_borderline_papers,  # legacy
            "primary_coverage_pct": round(PRIMARY_COVERAGE * 100, 1),
            "in_scope_cluster_ids": [int(c) for c in sorted(soft_in_scope, key=int)],
            "borderline_cluster_ids": borderline_ids,
            "distance_rescued_cluster_ids": borderline_ids,  # legacy alias for GT map
            "scope_borderline": border_meta,
            "scope_distance": dist_meta,
            "scope_hard_negatives": hn_meta,
            "scope_paper_llm": paper_meta,
            "paper_scope_overrides": paper_overrides,
            "top_communities": top_comms,
            "oos_by_year": oos_by_year,
            "primary_shift": primary_shift,
            "example_papers": example_papers,
            "scatter": scatter,
        })

    return journals_data


def compute_community_stats_scope(df: pd.DataFrame, df_all: pd.DataFrame = None) -> list:
    """Compute statistics for each community (scope dashboard version).
    
    Args:
        df: DataFrame with only target Frontiers journals
        df_all: DataFrame with ALL papers (including external) for true cluster sizes
    """
    communities = []
    
    # Get clusters that have papers from our target journals
    target_clusters = df[CLUSTER_LEVEL].unique()
    
    # Use all papers if available, otherwise just use df
    if df_all is not None:
        # Get total size of each cluster (all papers)
        all_comm_counts = df_all.groupby(CLUSTER_LEVEL).agg(
            total_size=("int_id", "count"),
            frontiers_count=("is_frontiers", "sum")
        ).reset_index()
        all_comm_counts = all_comm_counts[all_comm_counts[CLUSTER_LEVEL].isin(target_clusters)]
    else:
        all_comm_counts = None

    # Get Frontiers journal breakdown per cluster
    frontiers_comm_counts = df.groupby(CLUSTER_LEVEL).agg(size=("int_id", "count")).reset_index()

    for _, row in frontiers_comm_counts.nlargest(100, "size").iterrows():
        comm_id = row[CLUSTER_LEVEL]
        cdf = df[df[CLUSTER_LEVEL] == comm_id]
        frontiers_size = int(row["size"])

        # Get total cluster size and Frontiers % from all papers
        if all_comm_counts is not None:
            cluster_row = all_comm_counts[all_comm_counts[CLUSTER_LEVEL] == comm_id]
            if not cluster_row.empty:
                total_size = int(cluster_row["total_size"].iloc[0])
                frontiers_pct = round(frontiers_size / total_size * 100, 1)
            else:
                total_size = frontiers_size
                frontiers_pct = 100.0
        else:
            total_size = frontiers_size
            frontiers_pct = 100.0

        # Get TRUE dominant journal from ALL papers in cluster
        true_dominant_journal = "Unknown"
        true_dominant_pct = 0.0
        if df_all is not None:
            cluster_all = df_all[df_all[CLUSTER_LEVEL] == comm_id]
            if len(cluster_all) > 0:
                all_journal_counts = cluster_all["journal"].value_counts()
                true_dominant_journal = all_journal_counts.index[0] if len(all_journal_counts) else "Unknown"
                true_dominant_pct = round(all_journal_counts.iloc[0] / total_size * 100, 1) if len(all_journal_counts) else 0

        # Top Frontiers journal (among our target journals)
        journal_counts = cdf["journal"].value_counts()
        top_frontiers_journal = journal_counts.index[0] if len(journal_counts) else "Unknown"
        # Calculate percentages relative to TOTAL cluster size, not just Frontiers subset
        top_frontiers_pct = round(journal_counts.iloc[0] / total_size * 100, 2) if len(journal_counts) else 0

        top_journals = [
            {"name": j, "count": int(c), "pct": round(c / total_size * 100, 2)}
            for j, c in journal_counts.head(3).items()
        ]

        label = GPT_LABELS.get(int(comm_id), f"Cluster {comm_id}")
        info = GPT_LABELS_ALL.get(CLUSTER_LEVEL, {}).get(int(comm_id), {}) or {}
        long_label = info.get("long_label") or label
        keywords = info.get("keywords") or []
        if not isinstance(keywords, list):
            keywords = []
        summary = str(info.get("summary") or "").strip()
        communities.append({
            "id": int(comm_id),
            "label": label,
            "long_label": long_label,
            "keywords": [str(k) for k in keywords],
            "summary": summary,
            "description": summary or long_label,
            "size": int(total_size),  # Total cluster size
            "frontiers_size": frontiers_size,  # Just our target journals
            "frontiers_pct": frontiers_pct,
            "true_dominant_journal": true_dominant_journal,
            "true_dominant_pct": true_dominant_pct,
            "top_frontiers_journal": top_frontiers_journal,
            "top_frontiers_pct": top_frontiers_pct,
            "top_journals": top_journals,
        })

    # Sort by total size descending
    communities.sort(key=lambda x: x["size"], reverse=True)
    return communities[:100]


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

.main { padding: 20px 24px; }

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

<div class="main">
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
        <th>Theme</th><th class="num">Size</th><th>Description</th>
      </tr></thead>
      <tbody></tbody>
    </table>
  </div>
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


def build_scope_dashboard(df: pd.DataFrame, df_cit: pd.DataFrame, run_metadata: dict = None, df_all: pd.DataFrame = None) -> dict:
    """Build scope_dashboard.html. Returns scope data for Network Maps / Paper Examples."""
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
    communities = compute_community_stats_scope(df, df_all)

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
        return data

    data_json = json.dumps(data, separators=(",", ":"))
    html = SCOPE_HTML_TEMPLATE.replace("__DATA_JSON__", data_json)
    html = html.replace("__RENDER_SCRIPT__", render_script)

    output_path = OUTPUT_DIR / "scope_dashboard.html"
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    output_path.write_text(html, encoding="utf-8")

    log.info(f"       Written to {output_path}")
    log.info(f"       File size: {output_path.stat().st_size / 1024:.1f} KB")

    return data


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

            # Sample example papers for this cluster
            sample_size = min(5, len(cdf))
            sample_df = cdf.sample(n=sample_size, random_state=42) if sample_size > 0 else cdf.head(0)
            example_papers = []
            for _, paper in sample_df.iterrows():
                example_papers.append({
                    "title": str(paper["title"] or "Untitled")[:150],
                    "year": int(paper["pub_year"]) if pd.notna(paper["pub_year"]) else None,
                    "journal": str(paper["journal"]).replace("Frontiers in ", ""),
                })

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
                "examples": example_papers,
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

<div style="margin-bottom:14px;background:var(--card);border-radius:10px;padding:12px 14px;box-shadow:0 1px 2px rgba(0,0,0,.06)">
<label style="font-weight:600;font-size:13px;margin-right:10px">🔍 Search clusters:</label>
<input type="text" id="clusterSearch" placeholder="e.g. surgical innovation, cancer, robotics..." style="padding:8px 12px;border:1px solid var(--bdr);border-radius:6px;font-size:13px;width:350px">
<span id="searchResults" style="margin-left:12px;font-size:12px;color:var(--tx2)"></span>
</div>

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
  // Example papers section
  let exH='';
  if(c.examples&&c.examples.length){
    exH='<div class="ds"><h4>📄 Example Papers</h4><div style="max-height:200px;overflow-y:auto">';
    c.examples.forEach(p=>{
      exH+=`<div style="padding:6px 0;border-bottom:1px solid #f1f5f9;font-size:12px">
        <div style="color:var(--tx);line-height:1.4">${p.title}</div>
        <div style="color:var(--tx2);font-size:11px;margin-top:2px">${p.journal} · ${p.year||'—'}</div></div>`;
    });
    exH+='</div></div>';
  }
  const yrs=Object.keys(c.years||{}).sort();
  const yvals=yrs.map(y=>c.years[y]);
  el.innerHTML=`<div class="dt">C${c.id} — ${c.label}</div>
    <div class="dm">${c.size.toLocaleString()} articles · ${c.dominant} (${c.dominant_pct}%)</div>
    <div class="ds"><h4>Keywords</h4>${fosH} ${fosS}</div>
    <div class="ds"><h4>Journal Mix</h4>${bars}</div>${chH}${exH}
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

// Search functionality
const searchInput=document.getElementById('clusterSearch');
const searchResults=document.getElementById('searchResults');
let allClusters=[];
['macro','meso','micro'].forEach(level=>{
  (D[level]||[]).forEach((c,idx)=>{
    allClusters.push({level,idx,id:c.id,label:c.label,fos:(c.fos||[]).concat(c.fos_specific||[]),size:c.size,examples:c.examples||[]});
  });
});

searchInput.addEventListener('input',function(){
  const q=this.value.toLowerCase().trim();
  if(!q){searchResults.innerHTML='';return;}
  const matches=allClusters.filter(c=>
    c.label.toLowerCase().includes(q)||c.fos.some(f=>f.toLowerCase().includes(q))
  ).sort((a,b)=>b.size-a.size).slice(0,20);
  if(!matches.length){searchResults.innerHTML='<span style="color:#c93030">No matches</span>';return;}
  let h=`<strong>${matches.length} matches:</strong> `;
  matches.slice(0,8).forEach(m=>{
    const col={macro:'#1d4ed8',meso:'#be185d',micro:'#065f46'}[m.level];
    h+=`<span style="cursor:pointer;margin-right:8px;padding:2px 8px;background:#f1f5f9;border-radius:4px;font-size:11px" 
      onclick="jumpTo('${m.level}',${m.idx})">
      <span style="color:${col}">${m.level[0].toUpperCase()}</span> C${m.id} ${m.label.slice(0,25)}</span>`;
  });
  if(matches.length>8) h+=`<span style="color:var(--tx2)">+${matches.length-8} more</span>`;
  searchResults.innerHTML=h;
});

function jumpTo(level,idx){
  document.querySelectorAll('.tab').forEach(t=>t.classList.remove('on'));
  document.querySelectorAll('.pan').forEach(p=>p.classList.remove('on'));
  document.querySelector(`.tab[data-t="${level}"]`).classList.add('on');
  document.getElementById('pan-'+level).classList.add('on');
  const detId={macro:'ma-det',meso:'me-det',micro:'mi-det'}[level];
  const childLevel={macro:'meso',meso:'micro',micro:'null'}[level];
  showDet(level,idx,detId,childLevel);
  const listEl=document.getElementById({macro:'ma-list',meso:'me-list',micro:'mi-list'}[level]);
  const targetItem=listEl.querySelector(`[data-i="${idx}"]`);
  if(targetItem) targetItem.scrollIntoView({behavior:'smooth',block:'center'});
}

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
.tab-content { flex: 1; display: none; overflow: hidden; min-height: 0; }
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
function notifyIframeResize(iframe) {
  if (!iframe || !iframe.contentWindow) return;
  try {
    const w = iframe.contentWindow;
    if (typeof w.resizeNetworkMaps === 'function') w.resizeNetworkMaps();
    if (w.Plotly && w.Plotly.Plots && typeof w.Plotly.Plots.resize === 'function') {
      w.document.querySelectorAll('.js-plotly-plot').forEach(el => {
        try { w.Plotly.Plots.resize(el); } catch (e) {}
      });
    }
    w.dispatchEvent(new Event('resize'));
  } catch (e) {}
}

function activateTab(tabId) {
  document.querySelectorAll('.tab-btn').forEach(b => {
    b.classList.toggle('active', b.dataset.tab === tabId);
  });
  document.querySelectorAll('.tab-content').forEach(c => {
    c.classList.toggle('active', c.id === 'tab-' + tabId);
  });
  const iframe = document.querySelector('#tab-' + tabId + ' iframe');
  if (iframe && !iframe.src && iframe.dataset.src) {
    iframe.src = iframe.dataset.src;
    iframe.addEventListener('load', () => {
      notifyIframeResize(iframe);
      setTimeout(() => notifyIframeResize(iframe), 200);
    }, { once: true });
  } else {
    notifyIframeResize(iframe);
    setTimeout(() => notifyIframeResize(iframe), 50);
    setTimeout(() => notifyIframeResize(iframe), 250);
  }
}

document.querySelectorAll('.tab-btn').forEach(btn => {
  btn.addEventListener('click', () => activateTab(btn.dataset.tab));
});

const firstActive = document.querySelector('.tab-btn.active') || document.querySelector('.tab-btn');
if (firstActive) activateTab(firstActive.dataset.tab);

window.addEventListener('resize', () => {
  document.querySelectorAll('.tab-content.active iframe').forEach(notifyIframeResize);
});
document.addEventListener('fullscreenchange', () => {
  document.querySelectorAll('.tab-content.active iframe').forEach(notifyIframeResize);
});
</script>
</body>
</html>
"""


NETWORK_MAPS_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Network Maps</title>
<script src="https://cdn.plot.ly/plotly-2.35.2.min.js"></script>
<style>
:root {
  --bg: #f6f8fa;
  --card: #ffffff;
  --text: #1a1f36;
  --muted: #5f6b7c;
  --border: #e3e7ee;
  --green: #1f8a4c;
  --amber: #d4a300;
  --red: #c93030;
}
* { box-sizing: border-box; margin: 0; padding: 0; }
html, body { height: 100%; }
body {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  background: var(--bg);
  color: var(--text);
  line-height: 1.5;
  display: flex;
  flex-direction: column;
  min-height: 100%;
}
header {
  background: var(--card);
  padding: 16px 24px;
  border-bottom: 1px solid var(--border);
  flex-shrink: 0;
}
header h1 { font-size: 1.4rem; font-weight: 700; margin-bottom: 4px; }
header p { color: var(--muted); font-size: 0.85rem; }
.toolbar {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  align-items: center;
  margin-top: 12px;
}
.toolbar .label { color: var(--muted); font-size: 0.8rem; margin-right: 4px; }
.filter-btn {
  padding: 6px 12px;
  border: 1px solid var(--border);
  background: var(--card);
  border-radius: 999px;
  cursor: pointer;
  font-size: 0.82rem;
  color: var(--text);
}
.filter-btn.active { color: #fff; border-color: transparent; }
.filter-btn[data-scope="primary"].active { background: var(--green); }
.filter-btn[data-scope="borderline"].active { background: var(--amber); }
.filter-btn[data-scope="oos"].active { background: var(--red); }
.filter-btn:not(.active) { opacity: 0.55; }
.year-toolbar {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  align-items: center;
  margin-top: 12px;
  padding-top: 12px;
  border-top: 1px solid var(--border);
}
.year-toolbar .year-label {
  font-weight: 600;
  font-variant-numeric: tabular-nums;
  min-width: 4.5rem;
}
.year-toolbar input[type="range"] {
  flex: 1;
  min-width: 160px;
  max-width: 420px;
  accent-color: #1a1f36;
}
.play-btn {
  padding: 6px 14px;
  border: 1px solid var(--border);
  background: var(--card);
  border-radius: 999px;
  cursor: pointer;
  font-size: 0.82rem;
  color: var(--text);
  font-weight: 600;
}
.play-btn.playing { background: #1a1f36; color: #fff; border-color: #1a1f36; }
.play-btn:disabled { opacity: 0.45; cursor: not-allowed; }
.year-ticks {
  display: flex;
  justify-content: space-between;
  max-width: 420px;
  width: 100%;
  flex: 1;
  min-width: 160px;
  color: var(--muted);
  font-size: 0.72rem;
  margin-top: -4px;
}
.card .year-stats { color: #8893a6; font-weight: 400; font-size: 13px; }
.journal-toolbar {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  align-items: center;
  margin-top: 12px;
  padding-top: 12px;
  border-top: 1px solid var(--border);
}
.journal-toolbar .filter-btn.active {
  background: #1a1f36;
  color: #fff;
  border-color: #1a1f36;
  opacity: 1;
}
.journal-toolbar .hint {
  color: var(--muted);
  font-size: 0.75rem;
  margin-left: 4px;
}
.main {
  padding: 16px 24px 24px;
  flex: 1;
  min-height: 0;
  overflow: auto;
}
.grid {
  display: grid;
  gap: 16px;
  grid-template-columns: repeat(auto-fit, minmax(min(100%, 520px), 1fr));
  align-items: stretch;
}
.grid.focus-one {
  grid-template-columns: 1fr;
}
.grid.focus-one .plot-wrap {
  height: clamp(480px, 70vh, 820px);
  min-height: 480px;
}
.grid.focus-few {
  grid-template-columns: repeat(auto-fit, minmax(min(100%, 640px), 1fr));
}
.grid.focus-few .plot-wrap {
  height: clamp(420px, 55vh, 720px);
  min-height: 420px;
}
.card {
  background: var(--card);
  border-radius: 10px;
  padding: 16px;
  border: 1px solid var(--border);
  display: flex;
  flex-direction: column;
  min-width: 0;
  min-height: 0;
}
.card.hidden { display: none; }
.card h2 {
  font-size: 0.95rem;
  font-weight: 600;
  margin-bottom: 12px;
  flex-shrink: 0;
}
.plot-wrap {
  flex: 1;
  min-height: 420px;
  height: clamp(420px, 48vh, 680px);
  width: 100%;
  position: relative;
  overflow: hidden;
}
.plot.scatter {
  position: absolute;
  inset: 0;
  width: 100% !important;
  height: 100% !important;
}
.plot.scatter .js-plotly-plot,
.plot.scatter .plot-container,
.plot.scatter .svg-container {
  width: 100% !important;
  height: 100% !important;
}
</style>
</head>
<body>
<header>
  <h1>Network Maps</h1>
  <p>
    Each bubble = community centroid from the citation network layout
    (closer ≈ more citation links; map rotated so spread reads left–right).
    <span style="color: var(--green);">Green = primary in-scope</span>,
    <span style="color: var(--amber);">Amber = borderline</span>,
    <span style="color: var(--red);">Red = out-of-scope</span>.
    Size = paper count in the selected year.
  </p>
  <div class="toolbar" id="scopeFilters" aria-label="Scope visibility filters">
    <span class="label">Show:</span>
    <button type="button" class="filter-btn active" data-scope="primary">Primary in-scope</button>
    <button type="button" class="filter-btn active" data-scope="borderline">Borderline</button>
    <button type="button" class="filter-btn active" data-scope="oos">Out of scope</button>
  </div>
  <div class="year-toolbar" id="yearControls" aria-label="Year animation controls">
    <span class="label">Year:</span>
    <span class="year-label" id="yearLabel">All</span>
    <button type="button" class="play-btn" id="playBtn" title="Play years">Play</button>
    <button type="button" class="filter-btn active" id="allYearsBtn">All years</button>
    <input type="range" id="yearSlider" min="0" max="0" value="0" step="1" aria-label="Publication year" />
  </div>
  <div class="journal-toolbar" id="journalFilters" aria-label="Journal visibility filters">
    <span class="label">Journals:</span>
    <button type="button" class="filter-btn active" id="allJournalsBtn">All</button>
    <span class="hint">click to toggle · double-click for only</span>
  </div>
</header>
<div class="main">
  <div id="scatterGrid" class="grid"></div>
</div>
<script>
const DATA = __DATA_JSON__;
const J = DATA.journals || [];
const C = DATA.communities || [];
const FONT = { family:'-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,sans-serif', color:"#1a1f36", size:12 };
const BASE = { paper_bgcolor:"#ffffff", plot_bgcolor:"#ffffff", font:FONT, autosize:true };
const CFG  = { responsive:true, displayModeBar:false };
const ext  = (a,b)=>Object.assign({},a,b);
const grid = document.getElementById("scatterGrid");
const commLabels = {};
C.forEach(c => { commLabels[c.id] = c.label || ("Community " + c.id); });

const visibility = { primary: true, borderline: true, oos: true };
const plotIds = [];
const journalBundles = [];
const SCOPE_META = {
  primary: { color:"#1f8a4c", name:"Primary in-scope" },
  borderline: { color:"#d4a300", name:"Borderline" },
  oos: { color:"#c93030", name:"Out of scope" },
};
const SCOPE_ORDER = ["primary", "borderline", "oos"];

function collectYears() {
  const fromMeta = (DATA.meta && DATA.meta.years) || [];
  if (fromMeta.length) return fromMeta.map(Number).sort((a,b)=>a-b);
  const set = new Set();
  J.forEach(j => (j.scatter || []).forEach(p => {
    if (p.yr != null) set.add(Number(p.yr));
  }));
  return Array.from(set).sort((a,b)=>a-b);
}

const YEARS = collectYears();
let selectedYear = null; // null = all years
let playTimer = null;
const PLAY_MS = 900;

const yearSlider = document.getElementById("yearSlider");
const yearLabel = document.getElementById("yearLabel");
const playBtn = document.getElementById("playBtn");
const allYearsBtn = document.getElementById("allYearsBtn");

if (YEARS.length) {
  yearSlider.min = 0;
  yearSlider.max = YEARS.length - 1;
  yearSlider.value = 0;
  yearSlider.disabled = false;
  playBtn.disabled = false;
} else {
  yearSlider.disabled = true;
  playBtn.disabled = true;
}

function sizePx(n, maxN) {
  if (n <= 0) return 0;
  return Math.max(18, Math.sqrt(n / Math.max(maxN, 1)) * 110);
}

function buildBundle(j) {
  const scatter = j.scatter || [];
  if (!scatter.length) return null;
  const primaryIds = new Set((j.top_communities || []).filter(c => c.is_primary).map(c => c.comm_id));
  const borderlineIds = new Set(j.borderline_cluster_ids || j.distance_rescued_cluster_ids || []);
  const inScopeIds = new Set(j.in_scope_cluster_ids || [...primaryIds, ...borderlineIds]);

  const byCom = {};
  scatter.forEach(p => { (byCom[p.c] = byCom[p.c] || []).push(p); });

  const communities = [];
  Object.keys(byCom).forEach(cid => {
    const pts = byCom[cid];
    const n = pts.length;
    const cx = pts.reduce((s,p)=>s+p.x,0)/n;
    const cy = pts.reduce((s,p)=>s+p.y,0)/n;
    const id = parseInt(cid, 10);
    let key = "oos";
    if (primaryIds.has(id)) key = "primary";
    else if (borderlineIds.has(id) || inScopeIds.has(id)) key = "borderline";
    const countsByYear = {};
    pts.forEach(p => {
      if (p.yr == null) return;
      const y = Number(p.yr);
      countsByYear[y] = (countsByYear[y] || 0) + 1;
    });
    communities.push({
      id, key,
      label: commLabels[cid] || ("Community " + cid),
      cx, cy,
      total: n,
      countsByYear,
    });
  });

  const maxAll = Math.max(...communities.map(c => c.total), 1);

  function framesForYear(year) {
    const buckets = {
      primary: { x:[], y:[], sizes:[], labels:[], counts:[] },
      borderline: { x:[], y:[], sizes:[], labels:[], counts:[] },
      oos: { x:[], y:[], sizes:[], labels:[], counts:[] },
    };
    let paperN = 0;
    let oosN = 0;
    let yearMax = 1;
    communities.forEach(c => {
      const n = year == null ? c.total : (c.countsByYear[year] || 0);
      if (n > yearMax) yearMax = n;
    });
    // Always plot every community at its citation-layout centroid.
    // Rotate 90° (swap axes) so the tall citation spread runs left–right
    // and fills the wide card better.
    communities.forEach(c => {
      const n = year == null ? c.total : (c.countsByYear[year] || 0);
      paperN += n;
      if (c.key === "oos") oosN += n;
      const b = buckets[c.key];
      b.x.push(c.cy);
      b.y.push(-c.cx);
      b.sizes.push(n);
      b.labels.push(c.label);
      b.counts.push(n);
    });
    const traces = [];
    const traceKeys = [];
    SCOPE_ORDER.forEach(key => {
      const b = buckets[key];
      if (!b.x.length) return;
      const m = SCOPE_META[key];
      traces.push({
        type:"scatter", mode:"markers", name:m.name,
        x:b.x, y:b.y, text:b.labels, customdata:b.counts,
        visible: visibility[key],
        marker:{
          size: b.sizes.map(n => sizePx(n, year == null ? maxAll : yearMax)),
          sizemode:"diameter",
          color:m.color,
          opacity: b.sizes.map(n => n > 0 ? 0.55 : 0),
          line:{ color:"rgba(255,255,255,0.7)", width:1.5 }
        },
        hovertemplate:"<b>%{text}</b><br>Articles: %{customdata:,}<br>"+m.name+"<extra></extra>"
      });
      traceKeys.push(key);
    });
    const oosPct = paperN ? (oosN / paperN * 100) : 0;
    return { traces, traceKeys, paperN, oosPct, yearMax };
  }

  const initial = framesForYear(null);
  return {
    j, scatter, communities, maxAll,
    traces: initial.traces,
    traceKeys: initial.traceKeys,
    framesForYear,
    statsEl: null,
    card: null,
    gd: null,
  };
}

function layoutOpts() {
  return ext(BASE, {
    font: ext(FONT, {size:11}),
    autosize: true,
    xaxis:{ showgrid:false, zeroline:false, showticklabels:false, showline:false },
    yaxis:{ showgrid:false, zeroline:false, showticklabels:false, showline:false, scaleanchor:"x", scaleratio:1 },
    legend:{ orientation:"h", y:-0.08, yanchor:"top", font:{size:11} },
    margin:{ l:12, r:12, t:12, b:56 },
    hovermode:"closest"
  });
}

function resizeAllPlots() {
  plotIds.forEach(id => {
    const el = document.getElementById(id);
    if (el) {
      try { Plotly.Plots.resize(el); } catch (e) {}
    }
  });
  clearTimeout(resizeAllPlots._t);
  resizeAllPlots._t = setTimeout(() => {
    journalBundles.forEach(bundle => {
      if (bundle && bundle.gd) restyleBundle(bundle, selectedYear);
    });
  }, 120);
}

function formatStats(bundle, year) {
  const frame = bundle.framesForYear(year);
  const rescuedN = bundle.j.n_borderline_clusters || bundle.j.n_distance_rescued_clusters || 0;
  const yearBit = year == null ? "all years" : String(year);
  return yearBit + " · "
    + frame.paperN.toLocaleString() + " papers · "
    + frame.oosPct.toFixed(1) + "% out of scope"
    + (rescuedN ? (" · " + rescuedN + " borderline communities") : "");
}

function restyleBundle(bundle, year) {
  if (!bundle || !bundle.gd) return;
  const frame = bundle.framesForYear(year);
  bundle.traceKeys = frame.traceKeys;
  Plotly.react(bundle.gd, frame.traces, layoutOpts(), CFG);
  if (bundle.statsEl) bundle.statsEl.textContent = "— " + formatStats(bundle, year);
}

function applyYear(year) {
  selectedYear = year;
  if (year == null) {
    yearLabel.textContent = "All";
    allYearsBtn.classList.add("active");
  } else {
    yearLabel.textContent = String(year);
    allYearsBtn.classList.remove("active");
    const idx = YEARS.indexOf(year);
    if (idx >= 0) yearSlider.value = String(idx);
  }
  journalBundles.forEach(bundle => restyleBundle(bundle, year));
}

function applyVisibility() {
  journalBundles.forEach(bundle => restyleBundle(bundle, selectedYear));
}

function stopPlay() {
  if (playTimer) {
    clearInterval(playTimer);
    playTimer = null;
  }
  playBtn.classList.remove("playing");
  playBtn.textContent = "Play";
}

function startPlay() {
  if (!YEARS.length) return;
  stopPlay();
  // Start from beginning if on All or at last year
  let idx = selectedYear == null ? 0 : YEARS.indexOf(selectedYear);
  if (idx < 0 || idx >= YEARS.length - 1) idx = 0;
  applyYear(YEARS[idx]);
  playBtn.classList.add("playing");
  playBtn.textContent = "Pause";
  playTimer = setInterval(() => {
    idx += 1;
    if (idx >= YEARS.length) {
      stopPlay();
      return;
    }
    applyYear(YEARS[idx]);
  }, PLAY_MS);
}

function shortJournalName(name) {
  return String(name || "").replace(/^Frontiers in\s+/i, "");
}

const journalFiltersEl = document.getElementById("journalFilters");
const allJournalsBtn = document.getElementById("allJournalsBtn");
const journalShown = {};

J.forEach((j, jIdx) => {
  const bundle = buildBundle(j);
  if (!bundle) return;
  journalShown[jIdx] = true;
  const plotId = "scatter" + jIdx;
  const card = document.createElement("div");
  card.className = "card";
  card.dataset.journalIdx = String(jIdx);
  card.innerHTML = '<h2>' + j.name
    + ' <span class="year-stats" id="stats' + jIdx + '"></span></h2>'
    + '<div class="plot-wrap"><div id="' + plotId + '" class="plot scatter"></div></div>';
  grid.appendChild(card);
  bundle.card = card;
  bundle.jIdx = jIdx;
  bundle.statsEl = document.getElementById("stats" + jIdx);
  bundle.statsEl.textContent = "— " + formatStats(bundle, null);
  plotIds.push(plotId);
  journalBundles.push(bundle);

  const btn = document.createElement("button");
  btn.type = "button";
  btn.className = "filter-btn active";
  btn.dataset.journalIdx = String(jIdx);
  btn.textContent = shortJournalName(j.name);
  btn.title = j.name + " (double-click for only this journal)";
  // Insert before the hint span
  const hint = journalFiltersEl.querySelector(".hint");
  journalFiltersEl.insertBefore(btn, hint);

  Plotly.newPlot(plotId, bundle.traces, layoutOpts(), CFG).then(gd => {
    bundle.gd = gd;
    restyleBundle(bundle, selectedYear);
  });
});

function visibleJournalCount() {
  return Object.keys(journalShown).filter(k => journalShown[k]).length;
}

function syncJournalButtons() {
  journalFiltersEl.querySelectorAll("button[data-journal-idx]").forEach(btn => {
    const idx = btn.dataset.journalIdx;
    btn.classList.toggle("active", !!journalShown[idx]);
  });
  const n = visibleJournalCount();
  const total = journalBundles.length;
  allJournalsBtn.classList.toggle("active", n === total && total > 0);
  grid.classList.toggle("focus-one", n === 1);
  grid.classList.toggle("focus-few", n === 2 || n === 3);
}

function applyJournalVisibility() {
  if (visibleJournalCount() === 0 && journalBundles.length) {
    const first = journalBundles[0].jIdx;
    journalShown[first] = true;
  }
  journalBundles.forEach(bundle => {
    const on = !!journalShown[bundle.jIdx];
    if (bundle.card) bundle.card.classList.toggle("hidden", !on);
  });
  syncJournalButtons();
  setTimeout(resizeAllPlots, 30);
  setTimeout(resizeAllPlots, 200);
}

allJournalsBtn.addEventListener("click", () => {
  journalBundles.forEach(b => { journalShown[b.jIdx] = true; });
  applyJournalVisibility();
});

let journalClickTimer = null;
journalFiltersEl.addEventListener("click", (e) => {
  const t = e.target;
  if (!(t instanceof HTMLElement) || t.dataset.journalIdx == null) return;
  const idx = parseInt(t.dataset.journalIdx, 10);
  clearTimeout(journalClickTimer);
  journalClickTimer = setTimeout(() => {
    journalShown[idx] = !journalShown[idx];
    applyJournalVisibility();
  }, 220);
});

journalFiltersEl.addEventListener("dblclick", (e) => {
  const t = e.target;
  if (!(t instanceof HTMLElement) || t.dataset.journalIdx == null) return;
  e.preventDefault();
  clearTimeout(journalClickTimer);
  const idx = parseInt(t.dataset.journalIdx, 10);
  journalBundles.forEach(b => { journalShown[b.jIdx] = (b.jIdx === idx); });
  applyJournalVisibility();
});

syncJournalButtons();

yearSlider.addEventListener("input", () => {
  stopPlay();
  if (!YEARS.length) return;
  applyYear(YEARS[parseInt(yearSlider.value, 10)]);
});

allYearsBtn.addEventListener("click", () => {
  stopPlay();
  applyYear(null);
});

playBtn.addEventListener("click", () => {
  if (playTimer) stopPlay();
  else startPlay();
});

document.querySelectorAll("#scopeFilters .filter-btn").forEach(btn => {
  btn.addEventListener("click", () => {
    const key = btn.dataset.scope;
    visibility[key] = !visibility[key];
    btn.classList.toggle("active", visibility[key]);
    if (!visibility.primary && !visibility.borderline && !visibility.oos) {
      visibility[key] = true;
      btn.classList.add("active");
      return;
    }
    applyVisibility();
  });
});

window.addEventListener("resize", resizeAllPlots);
document.addEventListener("visibilitychange", () => {
  if (!document.hidden) resizeAllPlots();
});
if (window.ResizeObserver) {
  const ro = new ResizeObserver(() => resizeAllPlots());
  document.querySelectorAll(".plot-wrap").forEach(el => ro.observe(el));
  ro.observe(document.body);
}
window.resizeNetworkMaps = resizeAllPlots;
setTimeout(resizeAllPlots, 50);
setTimeout(resizeAllPlots, 300);
</script>
</body>
</html>"""


PAPER_EXAMPLES_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Paper Examples</title>
<style>
:root {
  --bg: #f6f8fa;
  --card: #ffffff;
  --text: #1a1f36;
  --muted: #5f6b7c;
  --border: #e3e7ee;
  --green: #1f8a4c;
  --red: #c93030;
}
* { box-sizing: border-box; margin: 0; padding: 0; }
body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: var(--bg); color: var(--text); padding: 20px; }
.card { background: var(--card); border-radius: 10px; padding: 20px; box-shadow: 0 1px 3px rgba(0,0,0,.08); max-width: 1200px; margin: 0 auto; }
h1 { font-size: 1.3rem; margin-bottom: 8px; }
.sub { color: var(--muted); font-size: 0.9rem; margin-bottom: 20px; }
select { padding: 10px 14px; border: 1px solid var(--border); border-radius: 6px; font-size: 1rem; min-width: 350px; margin-bottom: 20px; }
table { width: 100%; border-collapse: collapse; font-size: 0.9rem; }
th { text-align: left; padding: 12px; border-bottom: 2px solid var(--border); color: var(--muted); font-weight: 600; font-size: 0.75rem; text-transform: uppercase; }
td { padding: 12px; border-bottom: 1px solid var(--border); vertical-align: top; }
tr:hover { background: #f8fafc; }
.title-cell { max-width: 450px; line-height: 1.5; }
.in-scope { color: var(--green); font-weight: 600; }
.out-scope { color: var(--red); font-weight: 600; }
.comm-cell { font-size: 0.85rem; max-width: 250px; }
.year-cell { text-align: center; }
.filter-row { margin-bottom: 16px; display: flex; gap: 16px; align-items: center; flex-wrap: wrap; }
.filter-btn { padding: 6px 14px; border: 1px solid var(--border); background: var(--card); border-radius: 6px; cursor: pointer; font-size: 0.85rem; }
.filter-btn.active { background: var(--text); color: white; border-color: var(--text); }
</style>
</head>
<body>
<div class="card">
  <h1>📄 Paper Examples by Journal</h1>
  <p class="sub">Sample papers showing their scope classification and community assignment. 20 in-scope + 20 out-of-scope per journal.</p>
  
  <div class="filter-row">
    <select id="journalSelect"></select>
    <button class="filter-btn active" data-filter="all">All</button>
    <button class="filter-btn" data-filter="in">In-scope only</button>
    <button class="filter-btn" data-filter="out">Out-of-scope only</button>
  </div>
  
  <table>
    <thead>
      <tr>
        <th style="width:45%">Paper Title</th>
        <th style="width:8%" class="year-cell">Year</th>
        <th style="width:12%">Scope</th>
        <th style="width:35%">Community</th>
      </tr>
    </thead>
    <tbody id="paperBody"></tbody>
  </table>
</div>

<script>
const DATA = __DATA_JSON__;
const J = DATA.journals || [];
const sel = document.getElementById('journalSelect');
const tbody = document.getElementById('paperBody');
let currentFilter = 'all';

J.forEach((j, i) => {
  const opt = document.createElement('option');
  opt.value = i;
  opt.textContent = j.name + ' (' + j.articles.toLocaleString() + ' papers, ' + j.out_of_scope_pct.toFixed(1) + '% OOS)';
  sel.appendChild(opt);
});

function render(jIdx) {
  tbody.innerHTML = '';
  const journal = J[jIdx];
  if (!journal || !journal.example_papers) return;
  
  let papers = journal.example_papers.slice();
  if (currentFilter === 'in') papers = papers.filter(p => p.is_in_scope);
  else if (currentFilter === 'out') papers = papers.filter(p => !p.is_in_scope);
  
  papers.sort((a, b) => a.is_in_scope === b.is_in_scope ? 0 : a.is_in_scope ? -1 : 1);
  
  papers.forEach(p => {
    const tr = document.createElement('tr');
    const scopeCls = p.is_in_scope ? 'in-scope' : 'out-scope';
    const scopeTxt = p.is_in_scope ? '✓ In scope' : '✗ Out of scope';
    tr.innerHTML = 
      '<td class="title-cell">' + (p.title || 'Untitled') + '</td>' +
      '<td class="year-cell">' + (p.year || '—') + '</td>' +
      '<td class="' + scopeCls + '">' + scopeTxt + '</td>' +
      '<td class="comm-cell">' + (p.community_label || 'Unknown') + '</td>';
    tbody.appendChild(tr);
  });
}

sel.addEventListener('change', () => render(parseInt(sel.value)));
document.querySelectorAll('.filter-btn').forEach(btn => {
  btn.addEventListener('click', () => {
    document.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
    btn.classList.add('active');
    currentFilter = btn.dataset.filter;
    render(parseInt(sel.value));
  });
});

if (J.length) render(0);
</script>
</body>
</html>"""


def build_network_maps_dashboard(scope_data: dict) -> None:
    """Build network_maps.html standalone dashboard (community centroid scatter)."""
    log.info("=" * 60)
    log.info("Building Network Maps Dashboard")
    log.info("=" * 60)

    meta = scope_data.get("meta") or {}
    years = meta.get("oos_per_year_years") or []
    if not years:
        yr_range = meta.get("year_range") or []
        if len(yr_range) == 2:
            years = list(range(int(yr_range[0]), int(yr_range[1]) + 1))

    data_json = json.dumps(
        {
            "journals": scope_data.get("journals", []),
            "communities": scope_data.get("communities", []),
            "meta": {
                "years": [int(y) for y in years],
                "year_range": meta.get("year_range") or [],
            },
        },
        separators=(",", ":"),
    )
    html = NETWORK_MAPS_TEMPLATE.replace("__DATA_JSON__", data_json)

    output_path = OUTPUT_DIR / "network_maps.html"
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    output_path.write_text(html, encoding="utf-8")

    log.info(f"       Written to {output_path}")
    log.info(f"       File size: {output_path.stat().st_size / 1024:.1f} KB")


def build_paper_examples_dashboard(journals_data: list) -> None:
    """Build paper_examples.html standalone dashboard."""
    log.info("=" * 60)
    log.info("Building Paper Examples Dashboard")
    log.info("=" * 60)

    data = {"journals": journals_data}
    data_json = json.dumps(data, separators=(",", ":"))
    html = PAPER_EXAMPLES_TEMPLATE.replace("__DATA_JSON__", data_json)

    output_path = OUTPUT_DIR / "paper_examples.html"
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    output_path.write_text(html, encoding="utf-8")

    log.info(f"       Written to {output_path}")
    log.info(f"       File size: {output_path.stat().st_size / 1024:.1f} KB")


def combine_dashboards() -> None:
    """Combine all dashboards into a single tabbed HTML file."""
    log.info("=" * 60)
    log.info("Combining Dashboards")
    log.info("=" * 60)

    # Order: analysis tabs first; Network Maps near end; Paper Examples far right
    dashboards = [
        ("scope_dashboard", "Scope Analysis"),
        ("drift_dashboard", "Drift Analysis"),
        ("clusters", "Cluster Map"),
        ("network_maps", "Network Maps"),
        ("paper_examples", "Paper Examples"),
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
    log.info(f"Primary coverage: {PRIMARY_COVERAGE}")
    log.info(
        f"LLM borderline: enabled={SCOPE_LLM_BORDERLINE_ENABLED} "
        f"model={SCOPE_LLM_BORDERLINE_MODEL} prompt={BORDERLINE_PROMPT_VERSION}"
    )
    log.info(
        f"Hard-negatives: enabled={SCOPE_HARD_NEGATIVES_ENABLED} "
        f"path={SCOPE_HARD_NEGATIVES_PATH}"
    )
    log.info(
        f"Paper LLM demotion: enabled={SCOPE_PAPER_LLM_ENABLED} "
        f"model={SCOPE_PAPER_LLM_MODEL} batch={SCOPE_PAPER_LLM_BATCH}"
    )
    log.info(
        f"Distance rescue (legacy): enabled={SCOPE_DISTANCE_ENABLED} "
        f"mode={SCOPE_DISTANCE_MODE} factor={SCOPE_DISTANCE_FACTOR} "
        f"percentile={SCOPE_DISTANCE_PERCENTILE}"
    )
    log.info(f"Layout seed: {LAYOUT_SEED}")
    log.info(f"Output dir: {OUTPUT_DIR}")

    # Load data from BigQuery
    log.info("\n[LOAD] Loading data from BigQuery …")
    df = load_merged_data()
    log.info(f"       {len(df):,} papers")
    log.info(f"       Journals: {df['journal'].nunique()}")
    log.info(f"       Years: {df['pub_year'].min()}–{df['pub_year'].max()}")

    log.info("\n[LOAD] Loading ALL papers for community composition …")
    df_all = load_all_papers()
    log.info(f"       {len(df_all):,} total papers in network")
    log.info(f"       {df_all['is_frontiers'].sum():,} Frontiers papers ({df_all['is_frontiers'].mean()*100:.1f}%)")

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
    scope_data = build_scope_dashboard(df, df_cit, run_metadata, df_all)
    print()
    build_network_maps_dashboard(scope_data)
    print()
    build_paper_examples_dashboard(scope_data.get("journals", []))
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
