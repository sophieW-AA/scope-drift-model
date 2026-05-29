"""
Scope Drift Detection — Global Citation Network Edition
=========================================================
Builds an ego-network: Frontiers target journals + all papers they cite + all
papers that cite them. Runs Leiden on this broader scholarly context, then
evaluates whether Frontiers articles cluster with their journal's core literature.

Data source : ocean-breeze-tier-1.airak (BigQuery / OpenAlex)
Algorithm   : Leiden community detection (Traag et al., 2019)

Key difference from scope_drift_airak.py:
  - The original script builds a network of *only* the 5 Frontiers journals,
    forcing them to cluster together.
  - This script embeds Frontiers papers in the broader scholarly network.

OOS definition (primary cluster method):
  1. For each journal, identify "primary clusters" — the smallest set of
     communities that together contain PRIMARY_CLUSTER_COVERAGE (default 80%)
     of the journal's papers.
  2. Papers that fall OUTSIDE those primary clusters are "out of scope" —
     they don't cluster with the journal's core literature.

Phase 2 edge weight improvements (toggleable via env vars):
  2.1 Bibliographic coupling with association strength (ENABLE_BC_EDGES)
  2.2 Temporal decay on direct citations       (TEMPORAL_DECAY_TAU, default 5)
  2.3 Journal self-citation discounting         (SELF_CITE_JOURNAL_WEIGHT, default 0.5)
  Set ENABLE_EDGE_WEIGHTS=false to disable all and run unweighted (original behaviour).

Requirements:
    pip install leidenalg python-igraph google-cloud-bigquery pandas plotly numpy

Usage:
    export GOOGLE_APPLICATION_CREDENTIALS=/path/to/creds.json
    export PRIMARY_CLUSTER_COVERAGE=0.80   # optional, default 80%
    python scope_drift_airak_global.py
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

import numpy as np
import pandas as pd
from google.cloud import bigquery
import igraph as ig
import leidenalg
import importlib.util

# Get the directory where this notebook is located (works on Windows & Linux)
notebook_dir = Path().absolute()
module_path = notebook_dir / "src" / "create_html_output.py"

print(f"Loading module from: {module_path}")

# Load scope_drift module
spec = importlib.util.spec_from_file_location("create_html_output", module_path)
create_html_output = importlib.util.module_from_spec(spec)
spec.loader.exec_module(create_html_output)

def _merge_dotenv_file(path: Path) -> None:
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
    try:
        from dotenv import load_dotenv

        load_dotenv(override=False)
    except ImportError:
        pass
    candidates: list[Path] = []
    here = Path(__file__).resolve()
    for i in range(min(8, len(here.parents))):
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
BQ_PROJECT = "ocean-tech-adv-analytics-p-usr"
AIRAK_DATASET = "ocean-breeze-tier-1.airak"
FRONTIERS_PUBLISHER_ID = 1563368095744

TOP_N_JOURNALS = int(os.environ.get("TOP_N_JOURNALS", "5"))
# Optionally specify exact journal IDs (comma-separated) instead of top N
# e.g. JOURNAL_IDS=2405181685761,123456789
JOURNAL_IDS_OVERRIDE = os.environ.get("JOURNAL_IDS", "").strip()

# Configurable year range for network construction
# e.g. START_YEAR=2020 END_YEAR=2025 for 5 years
START_YEAR = int(os.environ.get("START_YEAR", "2021"))
END_YEAR = int(os.environ.get("END_YEAR", "2025"))
YEAR_RANGE = (START_YEAR, END_YEAR)

# Network mode:
#   "ego"    - Frontiers papers + their direct citations
#   "full"   - Frontiers + related journals (journals that cite/are cited by Frontiers)
#   "global" - ALL publications from ALL publishers in year range (requires significant resources)
NETWORK_MODE = os.environ.get("NETWORK_MODE", "full").strip().lower()
if NETWORK_MODE not in ("ego", "full", "global"):
    print(f"[WARNING] Unknown NETWORK_MODE '{NETWORK_MODE}', defaulting to 'full'")
    NETWORK_MODE = "full"

# For the global network, we compute OOS based on primary cluster membership:
# 1. Identify each journal's "primary clusters" — the smallest set of communities
#    that together contain PRIMARY_CLUSTER_COVERAGE % of the journal's papers.
# 2. Papers outside those primary clusters are "out of scope" (they don't cluster
#    with the journal's core literature).
PRIMARY_CLUSTER_COVERAGE = float(os.environ.get("PRIMARY_CLUSTER_COVERAGE", "0.80"))

LEIDEN_RESOLUTIONS = {
    # Targets aligned to Clarivate citation topics: 10 macro, 326 meso, 2478 micro
    "macro": 0.00000008,  # Target ~10 communities (Clarivate: 10)
    "meso": 0.000006,  # Target ~326 communities (Clarivate: 326)
    "micro": 0.00007,  # Target ~2478 communities (Clarivate: 2478)
}
# Run all three resolutions by default; set MULTI_RESOLUTION=false for single-level
MULTI_RESOLUTION = os.environ.get("MULTI_RESOLUTION", "true").strip().lower() in (
    "1",
    "true",
    "yes",
)
# Level used for OOS calculation and dashboard display
# "macro" is too coarse (10 communities), "meso" (326) provides better separation
JOURNAL_DRIFT_LEVEL = os.environ.get("JOURNAL_DRIFT_LEVEL", "meso").strip().lower()
if JOURNAL_DRIFT_LEVEL not in LEIDEN_RESOLUTIONS:
    JOURNAL_DRIFT_LEVEL = "meso"

# Use Clarivate citation topics instead of Leiden clustering
# Set USE_CLARIVATE_TOPICS=true to assign papers directly to Clarivate's 10/326/2478 topic hierarchy
USE_CLARIVATE_TOPICS = os.environ.get(
    "USE_CLARIVATE_TOPICS", "false"
).strip().lower() in ("1", "true", "yes")

MIN_COMMUNITY_SIZE = int(os.environ.get("MIN_COMMUNITY_SIZE", "100"))
# Per-level min sizes (micro needs smaller threshold)
MIN_COMMUNITY_SIZES = {
    "macro": MIN_COMMUNITY_SIZE,
    "meso": max(50, MIN_COMMUNITY_SIZE // 2),
    "micro": max(25, MIN_COMMUNITY_SIZE // 4),
}

OUTPUT_DIR = Path(__file__).resolve().parent.parent / "output"
random.seed(42)

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s"
)
log = logging.getLogger(__name__)
os.makedirs(OUTPUT_DIR, exist_ok=True)

# OpenAI labelling config
OPENAI_MODEL = os.environ.get("OPENAI_MODEL", "gpt-4o-mini")
LLM_SAMPLE_PER_COMM = int(os.environ.get("LLM_SAMPLE_PER_COMM", "12"))
LLM_MAX_TITLE_CHARS = int(os.environ.get("LLM_MAX_TITLE_CHARS", "200"))
LLM_SLEEP_SEC = float(os.environ.get("LLM_SLEEP_SEC", "0.35"))

# ---------------------------------------------------------------------------
# Phase 2: Edge weight config
# ---------------------------------------------------------------------------
# Master toggle — set ENABLE_EDGE_WEIGHTS=false to run unweighted (original behaviour)
ENABLE_EDGE_WEIGHTS = os.environ.get("ENABLE_EDGE_WEIGHTS", "true").strip().lower() in (
    "1",
    "true",
    "yes",
)
# 2.1 Bibliographic coupling toggle
ENABLE_BC_EDGES = os.environ.get("ENABLE_BC_EDGES", "true").strip().lower() in (
    "1",
    "true",
    "yes",
)
# 2.2 Temporal decay: weight = exp(-(end_year - cited_year) / TAU)
#     tau=5 → a citation 5 yrs old has weight ≈ 0.37; 15 yrs old ≈ 0.05
TEMPORAL_DECAY_TAU = float(os.environ.get("TEMPORAL_DECAY_TAU", "5.0"))
# 2.1 Minimum shared references for a bibliographic coupling edge
BC_MIN_SHARED_REFS = int(os.environ.get("BC_MIN_SHARED_REFS", "3"))
# 2.3 Weight multiplier for same-journal citations (journal self-citation discount)
SELF_CITE_JOURNAL_WEIGHT = float(os.environ.get("SELF_CITE_JOURNAL_WEIGHT", "0.5"))

LLM_SYSTEM = """You label scientific publication clusters for an analytics dashboard.
Use UK English. Respond with ONLY a single JSON object, no markdown fences.
Schema:
{
  "label": "2–6 words, main research theme for this cluster"
}"""


# ---------------------------------------------------------------------------
# OpenAI community labelling
# ---------------------------------------------------------------------------
def _truncate(s: str, max_len: int) -> str:
    s = (s or "").strip()
    if len(s) <= max_len:
        return s
    return s[: max_len - 1] + "…"


def _extract_json_object(text: str) -> dict:
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
        "max_tokens": 200,
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
    with urllib.request.urlopen(req, timeout=120) as resp:
        data = json.loads(resp.read().decode("utf-8"))
    choices = data.get("choices") or []
    if not choices:
        raise RuntimeError(f"Unexpected OpenAI response: {data!r:.500}")
    return choices[0]["message"]["content"]


def _openai_configured() -> bool:
    return bool(os.environ.get("OPENAI_API_KEY"))


def load_clarivate_topics(csv_path: Path = None) -> pd.DataFrame:
    """
    Load Clarivate citation topics from CSV.
    Returns DataFrame with columns for macro/meso/micro topics and descriptions.
    """
    if csv_path is None:
        csv_path = (
            Path(__file__).resolve().parent.parent
            / "data"
            / "clarivate_citation_topics_2025.csv"
        )

    if not csv_path.exists():
        log.warning(f"Clarivate topics file not found: {csv_path}")
        return pd.DataFrame()

    df = pd.read_csv(csv_path)
    log.info(f"Loaded {len(df)} Clarivate citation topics from {csv_path.name}")
    return df


def _build_topic_matcher(topics_df: pd.DataFrame, level: str = "micro"):
    """
    Build a TF-IDF matcher for Clarivate topics at a specific level.

    Args:
        topics_df: DataFrame with Clarivate citation topics
        level: "macro", "meso", or "micro" - determines which level to match against

    Returns matcher dict or None if sklearn unavailable.
    """
    if topics_df.empty:
        return None

    try:
        from sklearn.feature_extraction.text import TfidfVectorizer
        from sklearn.metrics.pairwise import cosine_similarity
    except ImportError:
        log.warning("sklearn not available — falling back to dominant journal labels")
        return None

    # Get unique topics at the specified level
    if level == "macro":
        # Get unique macro topics
        unique_topics = topics_df.drop_duplicates(subset=["Macro ID"])
        topic_texts = []
        topic_labels = []
        topic_ids = []

        for _, row in unique_topics.iterrows():
            # For macro, aggregate all micro descriptions under this macro
            macro_id = row["Macro ID"]
            macro_rows = topics_df[topics_df["Macro ID"] == macro_id]
            descriptions = " ".join(
                macro_rows["Micro Description"].dropna().astype(str).tolist()[:20]
            )
            text_parts = [str(row.get("Macro Topic", "")), descriptions]
            topic_texts.append(" ".join(text_parts))
            topic_labels.append(str(row.get("Macro Topic", f"Macro {macro_id}")))
            topic_ids.append(
                {"macro_id": macro_id, "macro_topic": row.get("Macro Topic")}
            )

    elif level == "meso":
        # Get unique meso topics
        unique_topics = topics_df.drop_duplicates(subset=["Meso ID"])
        topic_texts = []
        topic_labels = []
        topic_ids = []

        for _, row in unique_topics.iterrows():
            # For meso, aggregate micro descriptions under this meso
            meso_id = row["Meso ID"]
            meso_rows = topics_df[topics_df["Meso ID"] == meso_id]
            descriptions = " ".join(
                meso_rows["Micro Description"].dropna().astype(str).tolist()[:15]
            )
            text_parts = [
                str(row.get("Meso Topic", "")),
                str(row.get("Macro Topic", "")),
                descriptions,
            ]
            topic_texts.append(" ".join(text_parts))
            topic_labels.append(str(row.get("Meso Topic", f"Meso {meso_id}")))
            topic_ids.append(
                {
                    "meso_id": meso_id,
                    "macro_id": row.get("Macro ID"),
                    "meso_topic": row.get("Meso Topic"),
                    "macro_topic": row.get("Macro Topic"),
                }
            )

    else:  # micro
        topic_texts = []
        topic_labels = []
        topic_ids = []

        for _, row in topics_df.iterrows():
            text_parts = [
                str(row.get("Micro Topic", "")),
                str(row.get("Micro Longer Label", "")),
                str(row.get("Micro Description", "")),
            ]
            topic_texts.append(" ".join(text_parts))
            topic_labels.append(
                str(row.get("Micro Topic", f"Micro {row.get('Micro ID', '')}"))
            )
            topic_ids.append(
                {
                    "micro_id": row.get("Micro ID"),
                    "meso_id": row.get("Meso ID"),
                    "macro_id": row.get("Macro ID"),
                    "full_id": row.get("Full ID"),
                    "micro_topic": row.get("Micro Topic"),
                    "meso_topic": row.get("Meso Topic"),
                    "macro_topic": row.get("Macro Topic"),
                }
            )

    log.info(f"Built {level} matcher with {len(topic_texts)} topics")

    vectorizer = TfidfVectorizer(
        stop_words="english",
        ngram_range=(1, 2),
        max_features=10000,
        min_df=1,
    )
    topic_vectors = vectorizer.fit_transform(topic_texts)

    return {
        "vectorizer": vectorizer,
        "topic_vectors": topic_vectors,
        "topic_labels": topic_labels,
        "topic_ids": topic_ids,
        "cosine_similarity": cosine_similarity,
        "level": level,
    }


def _match_to_clarivate_topic(
    titles: list[str], matcher: dict
) -> tuple[str, dict, float]:
    """
    Match a list of paper titles to the nearest Clarivate topic.
    Returns (label, topic_info, similarity_score).
    """
    if not matcher or not titles:
        return None, None, 0.0

    # Combine all titles into one document
    combined_text = " ".join(titles)

    # Transform to TF-IDF vector
    query_vector = matcher["vectorizer"].transform([combined_text])

    # Compute similarities
    similarities = matcher["cosine_similarity"](query_vector, matcher["topic_vectors"])[
        0
    ]

    # Get best match
    best_idx = similarities.argmax()
    best_score = similarities[best_idx]

    return (
        matcher["topic_labels"][best_idx],
        matcher["topic_ids"][best_idx],
        float(best_score),
    )


def assign_papers_to_clarivate_topics(
    node_ids: list[int],
    node_lookup: dict,
) -> dict:
    """
    Assign each paper to a Clarivate citation topic based on title matching.
    Returns dict with membership arrays for macro, meso, and micro levels,
    plus lookup tables for topic info.
    """
    log.info("Assigning papers to Clarivate citation topics...")

    # Load topics and build matcher
    topics_df = load_clarivate_topics()
    matcher = _build_topic_matcher(topics_df)

    if matcher is None:
        log.error("Cannot assign to Clarivate topics — sklearn not available")
        return None

    # Build unique ID mappings for each level
    macro_to_idx = {}
    meso_to_idx = {}
    micro_to_idx = {}

    for topic_info in matcher["topic_ids"]:
        macro_id = topic_info["macro_id"]
        meso_id = topic_info["meso_id"]
        micro_id = topic_info["micro_id"]

        if macro_id not in macro_to_idx:
            macro_to_idx[macro_id] = len(macro_to_idx)
        if meso_id not in meso_to_idx:
            meso_to_idx[meso_id] = len(meso_to_idx)
        if micro_id not in micro_to_idx:
            micro_to_idx[micro_id] = len(micro_to_idx)

    log.info(
        f"Clarivate taxonomy: {len(macro_to_idx)} macro, {len(meso_to_idx)} meso, {len(micro_to_idx)} micro topics"
    )

    # Assign each paper
    macro_membership = []
    meso_membership = []
    micro_membership = []
    paper_topics = []  # Store full topic info per paper

    n_matched = 0
    n_low_confidence = 0

    for pid in node_ids:
        meta = node_lookup.get(pid, {})
        title = str(meta.get("Title", "")).strip()

        if not title:
            # No title - assign to "Unknown" cluster (index -1, will remap later)
            macro_membership.append(-1)
            meso_membership.append(-1)
            micro_membership.append(-1)
            paper_topics.append(None)
            continue

        # Match title to Clarivate topic
        label, topic_info, score = _match_to_clarivate_topic([title], matcher)

        if (
            topic_info and score >= 0.01
        ):  # Very low threshold since single titles have sparse vectors
            macro_membership.append(macro_to_idx[topic_info["macro_id"]])
            meso_membership.append(meso_to_idx[topic_info["meso_id"]])
            micro_membership.append(micro_to_idx[topic_info["micro_id"]])
            paper_topics.append(
                {
                    "macro_id": topic_info["macro_id"],
                    "meso_id": topic_info["meso_id"],
                    "micro_id": topic_info["micro_id"],
                    "macro_topic": topic_info["macro_topic"],
                    "meso_topic": topic_info["meso_topic"],
                    "micro_topic": topic_info["micro_topic"],
                    "similarity": round(score, 4),
                }
            )
            n_matched += 1
            if score < 0.05:
                n_low_confidence += 1
        else:
            macro_membership.append(-1)
            meso_membership.append(-1)
            micro_membership.append(-1)
            paper_topics.append(None)

    # Remap -1 (unmatched) to a dedicated "Unclassified" cluster
    unclassified_macro = len(macro_to_idx)
    unclassified_meso = len(meso_to_idx)
    unclassified_micro = len(micro_to_idx)

    macro_membership = [unclassified_macro if x == -1 else x for x in macro_membership]
    meso_membership = [unclassified_meso if x == -1 else x for x in meso_membership]
    micro_membership = [unclassified_micro if x == -1 else x for x in micro_membership]

    n_unmatched = len(node_ids) - n_matched
    log.info(
        f"Assigned {n_matched:,} papers to Clarivate topics ({n_low_confidence:,} low confidence)"
    )
    log.info(
        f"Unmatched papers: {n_unmatched:,} ({100*n_unmatched/len(node_ids):.1f}%)"
    )

    # Build reverse lookup: idx -> topic info
    idx_to_macro = {v: k for k, v in macro_to_idx.items()}
    idx_to_meso = {v: k for k, v in meso_to_idx.items()}
    idx_to_micro = {v: k for k, v in micro_to_idx.items()}

    # Add "Unclassified" entries
    idx_to_macro[unclassified_macro] = "Unclassified"
    idx_to_meso[unclassified_meso] = "Unclassified"
    idx_to_micro[unclassified_micro] = "Unclassified"

    # Build topic name lookups from the topics dataframe
    macro_names = {
        row["Macro ID"]: row["Macro Topic"] for _, row in topics_df.iterrows()
    }
    meso_names = {row["Meso ID"]: row["Meso Topic"] for _, row in topics_df.iterrows()}
    micro_names = {
        row["Micro ID"]: row["Micro Topic"] for _, row in topics_df.iterrows()
    }
    macro_names["Unclassified"] = "Unclassified"
    meso_names["Unclassified"] = "Unclassified"
    micro_names["Unclassified"] = "Unclassified"

    return {
        "macro_membership": macro_membership,
        "meso_membership": meso_membership,
        "micro_membership": micro_membership,
        "paper_topics": paper_topics,
        "macro_to_idx": macro_to_idx,
        "meso_to_idx": meso_to_idx,
        "micro_to_idx": micro_to_idx,
        "idx_to_macro": idx_to_macro,
        "idx_to_meso": idx_to_meso,
        "idx_to_micro": idx_to_micro,
        "macro_names": macro_names,
        "meso_names": meso_names,
        "micro_names": micro_names,
        "n_matched": n_matched,
        "n_unmatched": n_unmatched,
    }


def label_communities(
    comm_profiles: dict,
    node_ids: list,
    membership: list,
    node_lookup: dict,
    level: str = "micro",
    topics_df: pd.DataFrame = None,
) -> dict:
    """
    Label each community by matching sampled paper titles to Clarivate citation topics.
    Uses TF-IDF similarity to find the nearest topic at the specified level.

    Args:
        comm_profiles: Dict of community profiles
        node_ids: List of node IDs
        membership: List of community assignments
        node_lookup: Dict mapping node ID to metadata
        level: "macro", "meso", or "micro" - match to Clarivate topics at this level
        topics_df: Pre-loaded Clarivate topics DataFrame (optional, loads if not provided)

    Returns dict: comm_id -> label string
    """
    labels = {}
    topic_matches = {}  # Store full match info for later analysis

    # Load Clarivate topics and build matcher for the specified level
    if topics_df is None:
        topics_df = load_clarivate_topics()
    matcher = _build_topic_matcher(topics_df, level=level)

    if matcher is None:
        log.warning(
            f"Topic matcher unavailable for {level} — using dominant journal as community label"
        )
        for cid, profile in comm_profiles.items():
            labels[cid] = profile.get("dominant_journal", f"Community {cid}")
        return labels

    # Build mapping: comm_id -> list of pub_ids
    comm_pubs = defaultdict(list)
    for idx, pid in enumerate(node_ids):
        cid = membership[idx]
        comm_pubs[cid].append(pid)

    # Label communities with 50+ members (or 10+ for macro level)
    min_size = 10 if level == "macro" else 50
    candidates = [
        (cid, profile["total"])
        for cid, profile in comm_profiles.items()
        if profile["total"] >= min_size
    ]
    candidates.sort(key=lambda x: -x[1])
    to_label = [cid for cid, _ in candidates[:200]]  # Allow more for finer levels
    log.info(f"Matching {len(to_label)} communities to Clarivate {level} topics...")

    n_matched = 0
    for cid in to_label:
        pubs = comm_pubs.get(cid, [])
        k = min(
            LLM_SAMPLE_PER_COMM * 2, len(pubs)
        )  # Sample more titles for better matching
        sample_pubs = random.sample(pubs, k) if k else []

        # Collect titles from sampled papers
        titles = []
        for pid in sample_pubs:
            meta = node_lookup.get(pid)
            if not meta:
                continue
            title = _truncate(str(meta.get("Title", "")), LLM_MAX_TITLE_CHARS)
            if title:
                titles.append(title)

        if not titles:
            labels[cid] = comm_profiles[cid].get("dominant_journal", f"Community {cid}")
            continue

        # Match to Clarivate topic at the specified level
        label, topic_info, score = _match_to_clarivate_topic(titles, matcher)

        if label and score >= 0.03:  # Lower threshold for broader topics
            labels[cid] = label
            topic_matches[cid] = {
                "label": label,
                "topic_info": topic_info,
                "similarity": round(score, 4),
            }
            n_matched += 1
        else:
            labels[cid] = comm_profiles[cid].get("dominant_journal", f"Community {cid}")

    # Fill in unlabelled communities with dominant journal
    for cid in comm_profiles:
        if cid not in labels:
            labels[cid] = comm_profiles[cid].get("dominant_journal", f"Community {cid}")

    log.info(f"Matched {n_matched}/{len(to_label)} communities to Clarivate topics")

    return labels


def bq_client():
    return bigquery.Client(project=BQ_PROJECT)


def query_df(sql: str) -> pd.DataFrame:
    return bq_client().query(sql).to_dataframe()


# ---------------------------------------------------------------------------
# Step 1: Identify top Frontiers journals
# ---------------------------------------------------------------------------
def get_top_frontiers_journals(n: int) -> pd.DataFrame:
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
    log.info(f"Top Frontiers journals:\n{df.to_string(index=False)}")
    return df


# ---------------------------------------------------------------------------
# Step 2: Get Frontiers publication IDs
# ---------------------------------------------------------------------------
def get_frontiers_publication_ids(journal_ids: list[int]) -> set[int]:
    ids_str = ",".join(str(x) for x in journal_ids)
    log.info("Fetching Frontiers publication IDs...")
    q = f"""
    SELECT PublicationId
    FROM `{AIRAK_DATASET}.Publication`
    WHERE JournalId IN ({ids_str})
      AND PublishedYear BETWEEN {YEAR_RANGE[0]} AND {YEAR_RANGE[1]}
    """
    df = query_df(q)
    pub_ids = set(df["PublicationId"].tolist())
    log.info(f"Frontiers publications: {len(pub_ids):,}")
    return pub_ids


# Maximum external papers to keep (most connected to Frontiers) - for ego mode
MAX_EXTERNAL_PAPERS = int(os.environ.get("MAX_EXTERNAL_PAPERS", "50000"))

# Maximum publications for full network mode (safety limit)
MAX_FULL_NETWORK_PUBS = int(os.environ.get("MAX_FULL_NETWORK_PUBS", "2000000"))


# ---------------------------------------------------------------------------
# Step 3: Build focused ego-network (keep most connected external papers)
# ---------------------------------------------------------------------------
def get_ego_network_edges(frontiers_pub_ids: set[int]) -> tuple[pd.DataFrame, set[int]]:
    """
    Build a focused ego-network:
    1. Get all citations to/from Frontiers papers
    2. Count connections per external paper
    3. Keep only top MAX_EXTERNAL_PAPERS most-connected external papers
    4. Return edges within this reduced network
    """
    log.info("Building focused ego-network...")
    log.info(f"  Will keep top {MAX_EXTERNAL_PAPERS:,} most-connected external papers")

    ids_list = list(frontiers_pub_ids)
    batch_size = 50000
    all_edges = []

    for i in range(0, len(ids_list), batch_size):
        batch = ids_list[i : i + batch_size]
        ids_str = ",".join(str(x) for x in batch)

        q_out = f"""
        SELECT pc.PublicationId as src, pc.CitedPublicationId as tgt
        FROM `{AIRAK_DATASET}.PublicationCitation` pc
        WHERE pc.PublicationId IN ({ids_str})
        """

        q_in = f"""
        SELECT pc.PublicationId as src, pc.CitedPublicationId as tgt
        FROM `{AIRAK_DATASET}.PublicationCitation` pc
        WHERE pc.CitedPublicationId IN ({ids_str})
        """

        log.info(f"  Batch {i // batch_size + 1}: fetching outgoing citations...")
        df_out = query_df(q_out)
        all_edges.append(df_out)

        log.info(f"  Batch {i // batch_size + 1}: fetching incoming citations...")
        df_in = query_df(q_in)
        all_edges.append(df_in)

    df_edges = pd.concat(all_edges, ignore_index=True).drop_duplicates()
    log.info(f"Raw ego-network edges: {len(df_edges):,}")

    # Count connections per external paper (using pandas, not loops)
    all_nodes = set(df_edges["src"].unique()) | set(df_edges["tgt"].unique())
    external_nodes = all_nodes - frontiers_pub_ids
    log.info(f"External nodes (before filtering): {len(external_nodes):,}")

    log.info("  Counting connections per external paper...")
    # Count appearances in src and tgt columns
    src_counts = df_edges["src"].value_counts()
    tgt_counts = df_edges["tgt"].value_counts()

    # Combine counts (only for external nodes)
    external_counts = pd.Series(dtype=int)
    ext_src = src_counts[src_counts.index.isin(external_nodes)]
    ext_tgt = tgt_counts[tgt_counts.index.isin(external_nodes)]
    external_counts = ext_src.add(ext_tgt, fill_value=0).astype(int)

    # Keep top N most-connected external papers
    top_external = set(external_counts.nlargest(MAX_EXTERNAL_PAPERS).index)
    log.info(f"Keeping top {len(top_external):,} external papers by connection count")

    # Filter edges: keep only edges where both endpoints are in (Frontiers OR top_external)
    keep_nodes = frontiers_pub_ids | top_external
    df_filtered = df_edges[
        df_edges["src"].isin(keep_nodes) & df_edges["tgt"].isin(keep_nodes)
    ].copy()

    final_nodes = set(df_filtered["src"]) | set(df_filtered["tgt"])
    log.info(
        f"Filtered network: {len(df_filtered):,} edges, {len(final_nodes):,} nodes"
    )
    log.info(
        f"  Frontiers: {len(final_nodes & frontiers_pub_ids):,}, External: {len(final_nodes - frontiers_pub_ids):,}"
    )

    return df_filtered, final_nodes


# ---------------------------------------------------------------------------
# Step 3b: Build extended network (Frontiers + related journals)
# ---------------------------------------------------------------------------
def get_full_network_edges(
    frontiers_pub_ids: set[int], journal_ids: list[int]
) -> tuple[pd.DataFrame, set[int]]:
    """
    Build a network of Frontiers papers + papers from journals that interact with them.
    This creates a connected network by including all papers from "related" journals.

    Approach:
    1. Find journals that frequently cite or are cited by Frontiers
    2. Include ALL papers from those journals (in year range)
    3. Build citation network among them
    """
    log.info(
        f"Building EXTENDED citation network for {YEAR_RANGE[0]}-{YEAR_RANGE[1]}..."
    )
    log.info(f"  Starting with {len(frontiers_pub_ids):,} Frontiers papers")

    frontiers_ids_str = ",".join(str(x) for x in journal_ids)

    # Step 1: Find journals that frequently interact with Frontiers
    # Count citations TO Frontiers journals (who cites them)
    log.info("  Finding journals that cite Frontiers...")
    q_citing = f"""
    SELECT j.JournalId, j.DisplayName, COUNT(*) as citations
    FROM `{AIRAK_DATASET}.PublicationCitation` pc
    JOIN `{AIRAK_DATASET}.Publication` p1 ON pc.PublicationId = p1.PublicationId
    JOIN `{AIRAK_DATASET}.Publication` p2 ON pc.CitedPublicationId = p2.PublicationId
    JOIN `{AIRAK_DATASET}.Journal` j ON p1.JournalId = j.JournalId
    WHERE p2.JournalId IN ({frontiers_ids_str})
      AND p1.PublishedYear BETWEEN {YEAR_RANGE[0]} AND {YEAR_RANGE[1]}
      AND p2.PublishedYear BETWEEN {YEAR_RANGE[0]} AND {YEAR_RANGE[1]}
      AND p1.JournalId NOT IN ({frontiers_ids_str})
    GROUP BY j.JournalId, j.DisplayName
    HAVING citations >= 500
    ORDER BY citations DESC
    LIMIT 150
    """
    df_citing = query_df(q_citing)
    log.info(f"  Found {len(df_citing)} journals citing Frontiers (>=500 citations)")

    # Count citations FROM Frontiers journals (who they cite)
    log.info("  Finding journals cited by Frontiers...")
    q_cited = f"""
    SELECT j.JournalId, j.DisplayName, COUNT(*) as citations
    FROM `{AIRAK_DATASET}.PublicationCitation` pc
    JOIN `{AIRAK_DATASET}.Publication` p1 ON pc.PublicationId = p1.PublicationId
    JOIN `{AIRAK_DATASET}.Publication` p2 ON pc.CitedPublicationId = p2.PublicationId
    JOIN `{AIRAK_DATASET}.Journal` j ON p2.JournalId = j.JournalId
    WHERE p1.JournalId IN ({frontiers_ids_str})
      AND p1.PublishedYear BETWEEN {YEAR_RANGE[0]} AND {YEAR_RANGE[1]}
      AND p2.PublishedYear BETWEEN {YEAR_RANGE[0]} AND {YEAR_RANGE[1]}
      AND p2.JournalId NOT IN ({frontiers_ids_str})
    GROUP BY j.JournalId, j.DisplayName
    HAVING citations >= 500
    ORDER BY citations DESC
    LIMIT 150
    """
    df_cited = query_df(q_cited)
    log.info(f"  Found {len(df_cited)} journals cited by Frontiers (>=500 citations)")

    # Combine into set of related journals
    related_journal_ids = set(df_citing["JournalId"].tolist()) | set(
        df_cited["JournalId"].tolist()
    )
    all_journal_ids = related_journal_ids | set(journal_ids)
    log.info(
        f"  Total journals in network: {len(all_journal_ids)} (Frontiers + {len(related_journal_ids)} related)"
    )

    # Step 2: Get ALL publications from these journals in the year range
    all_journal_ids_str = ",".join(str(x) for x in all_journal_ids)
    log.info("  Fetching all papers from these journals...")
    q_pubs = f"""
    SELECT PublicationId
    FROM `{AIRAK_DATASET}.Publication`
    WHERE JournalId IN ({all_journal_ids_str})
      AND PublishedYear BETWEEN {YEAR_RANGE[0]} AND {YEAR_RANGE[1]}
    """
    df_pubs = query_df(q_pubs)
    all_pub_ids = set(df_pubs["PublicationId"].tolist())
    log.info(f"  Papers in network: {len(all_pub_ids):,}")

    # Step 3: Get citations between these papers
    log.info("  Fetching citations between papers...")
    pub_ids_list = list(all_pub_ids)
    batch_size = 50000
    all_edges = []

    for i in range(0, len(pub_ids_list), batch_size):
        batch = pub_ids_list[i : i + batch_size]
        batch_str = ",".join(str(x) for x in batch)
        batch_num = i // batch_size + 1
        n_batches = (len(pub_ids_list) + batch_size - 1) // batch_size

        log.info(f"    Citation batch {batch_num}/{n_batches}...")

        # Outgoing citations from this batch (to any paper in network)
        q_out = f"""
        SELECT pc.PublicationId as src, pc.CitedPublicationId as tgt
        FROM `{AIRAK_DATASET}.PublicationCitation` pc
        JOIN `{AIRAK_DATASET}.Publication` p ON pc.CitedPublicationId = p.PublicationId
        WHERE pc.PublicationId IN ({batch_str})
          AND p.JournalId IN ({all_journal_ids_str})
          AND p.PublishedYear BETWEEN {YEAR_RANGE[0]} AND {YEAR_RANGE[1]}
        """
        df_out = query_df(q_out)
        all_edges.append(df_out)

    df_edges = pd.concat(all_edges, ignore_index=True).drop_duplicates()
    log.info(f"  Total edges in network: {len(df_edges):,}")

    # Get final node set
    final_nodes = set(df_edges["src"]) | set(df_edges["tgt"])
    log.info(f"  Final network: {len(final_nodes):,} nodes, {len(df_edges):,} edges")

    return df_edges, final_nodes, all_journal_ids


def get_global_network_edges() -> tuple[pd.DataFrame, set[int]]:
    """
    Build a global citation network including ALL publications from ALL publishers
    within the configured year range.

    WARNING: This can be extremely large. Depending on the year range:
    - 1 year: ~3-5M papers, ~50M+ edges
    - 3 years: ~10-15M papers, ~200M+ edges
    - 5 years: ~15-25M papers, ~500M+ edges

    Consider running on a VM with sufficient memory (64GB+ recommended).
    """
    log.info("=" * 60)
    log.info("Building GLOBAL citation network (ALL publishers)")
    log.info(f"  Year range: {YEAR_RANGE[0]} - {YEAR_RANGE[1]}")
    log.info("=" * 60)

    # Step 1: Count total publications to estimate scale
    q_count = f"""
    SELECT COUNT(*) as cnt
    FROM `{AIRAK_DATASET}.Publication`
    WHERE PublishedYear BETWEEN {YEAR_RANGE[0]} AND {YEAR_RANGE[1]}
      AND JournalId IS NOT NULL
    """
    df_count = query_df(q_count)
    total_pubs = df_count["cnt"].iloc[0]
    log.info(f"  Total publications in range: {total_pubs:,}")

    if total_pubs > 50_000_000:
        log.warning(
            f"  WARNING: {total_pubs:,} publications is very large. "
            "Consider narrowing the year range."
        )

    # Step 2: Fetch all publication IDs in batches by year
    log.info("  Fetching publication IDs by year...")
    all_pub_ids = set()

    for year in range(YEAR_RANGE[0], YEAR_RANGE[1] + 1):
        q_year = f"""
        SELECT PublicationId
        FROM `{AIRAK_DATASET}.Publication`
        WHERE PublishedYear = {year}
          AND JournalId IS NOT NULL
        """
        df_year = query_df(q_year)
        year_count = len(df_year)
        all_pub_ids.update(df_year["PublicationId"].tolist())
        log.info(f"    {year}: {year_count:,} papers (total so far: {len(all_pub_ids):,})")
        del df_year

    log.info(f"  Total papers: {len(all_pub_ids):,}")

    # Step 3: Fetch citations in batches
    log.info("  Fetching citations (this may take a while)...")
    pub_ids_list = list(all_pub_ids)
    batch_size = 100000  # Larger batches for efficiency
    all_edges = []

    n_batches = (len(pub_ids_list) + batch_size - 1) // batch_size
    log.info(f"  Processing {n_batches} batches of {batch_size:,} papers each...")

    for i in range(0, len(pub_ids_list), batch_size):
        batch = pub_ids_list[i : i + batch_size]
        batch_str = ",".join(str(x) for x in batch)
        batch_num = i // batch_size + 1

        if batch_num % 10 == 1 or batch_num == n_batches:
            log.info(f"    Batch {batch_num}/{n_batches}...")

        # Get citations where source is in batch and target is in year range
        q_edges = f"""
        SELECT pc.PublicationId as src, pc.CitedPublicationId as tgt
        FROM `{AIRAK_DATASET}.PublicationCitation` pc
        JOIN `{AIRAK_DATASET}.Publication` p ON pc.CitedPublicationId = p.PublicationId
        WHERE pc.PublicationId IN ({batch_str})
          AND p.PublishedYear BETWEEN {YEAR_RANGE[0]} AND {YEAR_RANGE[1]}
          AND p.JournalId IS NOT NULL
        """
        df_batch = query_df(q_edges)
        if len(df_batch) > 0:
            all_edges.append(df_batch)
        del df_batch

    # Combine all edges
    log.info("  Combining edge batches...")
    if all_edges:
        df_edges = pd.concat(all_edges, ignore_index=True).drop_duplicates()
    else:
        df_edges = pd.DataFrame(columns=["src", "tgt"])
    del all_edges

    log.info(f"  Total edges: {len(df_edges):,}")

    # Get final node set (nodes that actually have edges)
    final_nodes = set(df_edges["src"]) | set(df_edges["tgt"])
    log.info(f"  Connected nodes: {len(final_nodes):,}")

    # Collect all journal IDs present in the network
    log.info("  Identifying journals in network...")
    nodes_str = ",".join(str(x) for x in list(final_nodes)[:100000])  # Sample for journal IDs
    q_journals = f"""
    SELECT DISTINCT JournalId
    FROM `{AIRAK_DATASET}.Publication`
    WHERE PublicationId IN ({nodes_str})
    """
    df_journals = query_df(q_journals)
    all_journal_ids = set(df_journals["JournalId"].dropna().astype(int).tolist())
    log.info(f"  Journals in network: {len(all_journal_ids):,}")

    log.info("=" * 60)
    log.info(f"GLOBAL NETWORK: {len(final_nodes):,} nodes, {len(df_edges):,} edges")
    log.info("=" * 60)

    return df_edges, final_nodes, all_journal_ids


# ---------------------------------------------------------------------------
# Step 3c: Bibliographic coupling edges (Phase 2.1)
# ---------------------------------------------------------------------------
def get_bibliographic_coupling_edges(
    frontiers_pub_ids: set[int],
    all_journal_ids: set[int],
) -> pd.DataFrame:
    """
    Bibliographic coupling (BC): two papers are linked if they share >= BC_MIN_SHARED_REFS
    references. Edge weight = association strength = shared_refs / sqrt(refs_i * refs_j).

    Only computed where at least one endpoint is a Frontiers paper (tractable subset).
    The network side is filtered by journal IDs to avoid huge IN clauses.
    """
    if not ENABLE_BC_EDGES:
        log.info("Bibliographic coupling disabled (ENABLE_BC_EDGES=false)")
        return pd.DataFrame(columns=["src", "tgt", "weight"])

    log.info(
        f"Computing bibliographic coupling edges (min shared refs: {BC_MIN_SHARED_REFS})..."
    )

    frontiers_list = list(frontiers_pub_ids)
    journal_ids_str = ",".join(str(x) for x in all_journal_ids)
    batch_size = 20000
    all_bc: list[pd.DataFrame] = []
    n_batches = (len(frontiers_list) + batch_size - 1) // batch_size

    for i in range(0, len(frontiers_list), batch_size):
        batch = frontiers_list[i : i + batch_size]
        frontiers_str = ",".join(str(x) for x in batch)
        batch_num = i // batch_size + 1
        log.info(f"  BC batch {batch_num}/{n_batches}...")

        q = f"""
        WITH frontiers_refs AS (
          -- All references made BY Frontiers papers in this batch
          SELECT PublicationId, CitedPublicationId
          FROM `{AIRAK_DATASET}.PublicationCitation`
          WHERE PublicationId IN ({frontiers_str})
        ),
        network_refs AS (
          -- All references made BY papers from related journals
          SELECT pc.PublicationId, pc.CitedPublicationId
          FROM `{AIRAK_DATASET}.PublicationCitation` pc
          JOIN `{AIRAK_DATASET}.Publication` p ON pc.PublicationId = p.PublicationId
          WHERE p.JournalId IN ({journal_ids_str})
            AND p.PublishedYear BETWEEN {YEAR_RANGE[0]} AND {YEAR_RANGE[1]}
        ),
        ref_counts_fr AS (
          SELECT PublicationId, COUNT(*) AS ref_count
          FROM `{AIRAK_DATASET}.PublicationCitation`
          WHERE PublicationId IN ({frontiers_str})
          GROUP BY PublicationId
        ),
        ref_counts_net AS (
          SELECT pc.PublicationId, COUNT(*) AS ref_count
          FROM `{AIRAK_DATASET}.PublicationCitation` pc
          JOIN `{AIRAK_DATASET}.Publication` p ON pc.PublicationId = p.PublicationId
          WHERE p.JournalId IN ({journal_ids_str})
            AND p.PublishedYear BETWEEN {YEAR_RANGE[0]} AND {YEAR_RANGE[1]}
          GROUP BY pc.PublicationId
        )
        SELECT
          fr.PublicationId AS src,
          nr.PublicationId AS tgt,
          COUNT(*) AS shared_refs,
          SAFE_DIVIDE(
            CAST(COUNT(*) AS FLOAT64),
            SQRT(CAST(rc_src.ref_count AS FLOAT64) * CAST(rc_tgt.ref_count AS FLOAT64))
          ) AS assoc_strength
        FROM frontiers_refs fr
        JOIN network_refs nr
          ON fr.CitedPublicationId = nr.CitedPublicationId
         AND fr.PublicationId != nr.PublicationId
        JOIN ref_counts_fr  rc_src ON rc_src.PublicationId = fr.PublicationId
        JOIN ref_counts_net rc_tgt ON rc_tgt.PublicationId = nr.PublicationId
        GROUP BY fr.PublicationId, nr.PublicationId, rc_src.ref_count, rc_tgt.ref_count
        HAVING COUNT(*) >= {BC_MIN_SHARED_REFS}
        """

        df_bc = query_df(q)
        if len(df_bc) > 0:
            all_bc.append(df_bc)
        log.info(f"    Batch {batch_num}: {len(df_bc):,} BC edges")

    if not all_bc:
        log.info("  No bibliographic coupling edges found")
        return pd.DataFrame(columns=["src", "tgt", "weight"])

    df_result = pd.concat(all_bc, ignore_index=True).drop_duplicates(
        subset=["src", "tgt"]
    )
    df_result["weight"] = df_result["assoc_strength"].fillna(0).clip(upper=1.0)
    n_strong = (df_result["weight"] >= 0.1).sum()
    log.info(
        f"  BC edges: {len(df_result):,} total, {n_strong:,} with association strength >= 0.1"
    )
    return df_result[["src", "tgt", "weight"]]


# ---------------------------------------------------------------------------
# Step 3d: Apply temporal decay + self-citation discounting (Phase 2.2 + 2.3)
# ---------------------------------------------------------------------------
def apply_edge_weights(df_edges: pd.DataFrame, node_lookup: dict) -> pd.DataFrame:
    """
    Apply two weight adjustments to direct citation edges:

    2.2 Temporal decay
        weight = exp(-(end_year - cited_year) / TEMPORAL_DECAY_TAU)
        A recent citation (same year) has weight ≈ 1.0.
        An old citation (15 yrs) has weight ≈ 0.05 with tau=5.
        This down-weights hub papers (1990s textbooks everyone cites)
        without removing them entirely.

    2.3 Journal self-citation discount
        Citations where src and tgt are in the same journal are multiplied
        by SELF_CITE_JOURNAL_WEIGHT (default 0.5). This reduces the
        inflated within-journal cohesion from journal self-promotion.
    """
    log.info(
        "Applying edge weights (2.2 temporal decay + 2.3 self-citation discount)..."
    )
    end_year = YEAR_RANGE[1]

    # Build fast lookup Series for year and journal
    pub_years = {
        pid: (meta.get("PublishedYear") or end_year)
        for pid, meta in node_lookup.items()
    }
    pub_journals = {pid: meta.get("JournalId") for pid, meta in node_lookup.items()}

    df = df_edges.copy()
    df["tgt_year"] = df["tgt"].map(pub_years).fillna(end_year)
    df["src_journal"] = df["src"].map(pub_journals)
    df["tgt_journal"] = df["tgt"].map(pub_journals)

    # 2.2 Temporal decay on the cited paper (tgt)
    df["decay"] = np.exp(-(end_year - df["tgt_year"]) / TEMPORAL_DECAY_TAU).clip(
        lower=0.01
    )

    # 2.3 Journal self-citation
    same_journal = (
        df["src_journal"].notna()
        & df["tgt_journal"].notna()
        & (df["src_journal"] == df["tgt_journal"])
    )
    df["self_factor"] = np.where(same_journal, SELF_CITE_JOURNAL_WEIGHT, 1.0)

    df["weight"] = (df["decay"] * df["self_factor"]).clip(lower=0.01)

    n_self = int(same_journal.sum())
    log.info(
        f"  Temporal decay  : mean={df['decay'].mean():.3f}, min={df['decay'].min():.4f}"
    )
    log.info(
        f"  Self-citations  : {n_self:,} ({100*n_self/max(len(df),1):.1f}%) discounted to ×{SELF_CITE_JOURNAL_WEIGHT}"
    )
    log.info(f"  Combined weight : mean={df['weight'].mean():.3f}")

    return df[["src", "tgt", "weight"]]


def merge_edge_lists(df_direct: pd.DataFrame, df_bc: pd.DataFrame) -> pd.DataFrame:
    """
    Combine weighted direct-citation edges with bibliographic coupling edges.

    For pairs that appear in both lists (direct citation + BC), weights are
    summed — rewarding paper pairs that both directly cite each other AND
    share a reference list. Total weight is capped at 2.0.
    """
    log.info("Merging direct citation and BC edges...")

    def _normalise_direction(df: pd.DataFrame) -> pd.DataFrame:
        """Ensure src <= tgt so (A,B) and (B,A) deduplicate correctly."""
        mask = df["src"] > df["tgt"]
        out = df.copy()
        out.loc[mask, ["src", "tgt"]] = out.loc[mask, ["tgt", "src"]].values
        return out

    d = _normalise_direction(df_direct[["src", "tgt", "weight"]])
    b = _normalise_direction(df_bc[["src", "tgt", "weight"]])

    merged = (
        pd.concat([d, b], ignore_index=True)
        .groupby(["src", "tgt"], as_index=False)["weight"]
        .sum()
    )
    merged["weight"] = merged["weight"].clip(upper=2.0)

    log.info(
        f"  Direct: {len(df_direct):,}  BC: {len(df_bc):,}  "
        f"Merged: {len(merged):,}  "
        f"Weight mean={merged['weight'].mean():.3f} max={merged['weight'].max():.3f}"
    )
    return merged


# ---------------------------------------------------------------------------
# Step 4: Get node metadata
# ---------------------------------------------------------------------------
def get_node_metadata(
    node_ids: set[int], frontiers_journal_ids: list[int]
) -> pd.DataFrame:
    """
    Get metadata for all nodes in the network.
    For non-Frontiers papers, we still get journal name to understand the community composition.
    """
    log.info(f"Fetching metadata for {len(node_ids):,} nodes...")

    ids_list = list(node_ids)
    # Use smaller batches to stay under BigQuery query size limit
    batch_size = 20000
    all_meta = []

    frontiers_ids_str = ",".join(str(x) for x in frontiers_journal_ids)
    n_batches = (len(ids_list) + batch_size - 1) // batch_size

    for i in range(0, len(ids_list), batch_size):
        batch = ids_list[i : i + batch_size]
        ids_str = ",".join(str(x) for x in batch)

        q = f"""
        SELECT
          p.PublicationId,
          p.PublishedYear,
          j.JournalId,
          j.DisplayName AS JournalName,
          j.PublisherId,
          CASE WHEN j.JournalId IN ({frontiers_ids_str}) THEN TRUE ELSE FALSE END AS IsFrontiers,
          COALESCE(p.Title, '') AS Title
        FROM `{AIRAK_DATASET}.Publication` p
        LEFT JOIN `{AIRAK_DATASET}.Journal` j ON p.JournalId = j.JournalId
        WHERE p.PublicationId IN ({ids_str})
        """

        batch_num = i // batch_size + 1
        log.info(f"  Metadata batch {batch_num}/{n_batches}...")
        df = query_df(q)
        all_meta.append(df)

    df_meta = pd.concat(all_meta, ignore_index=True)

    n_frontiers = df_meta["IsFrontiers"].sum()
    log.info(f"Nodes with metadata: {len(df_meta):,} ({n_frontiers:,} Frontiers)")

    return df_meta


# ---------------------------------------------------------------------------
# Step 5: Build graph & run Leiden
# ---------------------------------------------------------------------------
def build_graph(df_edges: pd.DataFrame):
    node_ids = sorted(set(df_edges["src"]) | set(df_edges["tgt"]))
    id_map = {pid: i for i, pid in enumerate(node_ids)}

    log.info("Mapping edges to node indices...")
    src_mapped = df_edges["src"].map(id_map)
    tgt_mapped = df_edges["tgt"].map(id_map)

    mask = src_mapped.notna() & tgt_mapped.notna()
    edges = list(zip(src_mapped[mask].astype(int), tgt_mapped[mask].astype(int)))

    has_weights = "weight" in df_edges.columns
    weights = list(df_edges.loc[mask, "weight"].astype(float)) if has_weights else None

    log.info(
        f"Building graph: {len(node_ids):,} nodes, {len(edges):,} edges (weighted={has_weights})"
    )
    G = ig.Graph(n=len(node_ids), edges=edges, directed=False)
    if weights:
        G.es["weight"] = weights
        # Merge parallel edges by summing weights, remove self-loops
        G.simplify(combine_edges={"weight": "sum"})
    else:
        G.simplify()
    log.info(f"After simplify: {G.vcount():,} nodes, {G.ecount():,} edges")
    return G, node_ids


def compute_layout(node_ids: list[int], membership: list[int]) -> dict:
    """Compute 2D layout coordinates using community-based positioning with jitter.

    This is much faster than force-directed layouts for large graphs and still
    shows community structure clearly.
    """
    log.info("Computing community-based layout...")

    # Group nodes by community
    from collections import defaultdict

    comm_nodes = defaultdict(list)
    for i, pid in enumerate(node_ids):
        cid = membership[i]
        comm_nodes[cid].append(pid)

    # Sort communities by size (largest first)
    sorted_comms = sorted(comm_nodes.items(), key=lambda x: -len(x[1]))

    # Arrange communities in a spiral pattern
    node_coords = {}
    n_comms = len(sorted_comms)

    for comm_idx, (cid, pids) in enumerate(sorted_comms):
        # Position community centers using golden angle spiral from center
        angle = comm_idx * 2.399963  # golden angle in radians
        radius = 0.02 * math.sqrt(comm_idx)  # start from center, spiral out
        cx = 0.5 + radius * math.cos(angle)
        cy = 0.5 + radius * math.sin(angle)

        # Place nodes within community with jitter
        n_nodes = len(pids)
        # Jitter radius proportional to sqrt of community size
        jitter_r = min(0.08, 0.015 * math.sqrt(n_nodes))

        for j, pid in enumerate(pids):
            # Distribute points in a disc around center
            r = jitter_r * math.sqrt(random.random())
            theta = random.random() * 2 * math.pi
            x = cx + r * math.cos(theta)
            y = cy + r * math.sin(theta)
            # Clamp to [0, 1]
            node_coords[pid] = {
                "x": max(0, min(1, x)),
                "y": max(0, min(1, y)),
            }

    log.info(f"Layout computed for {len(node_coords):,} nodes in {n_comms} communities")
    return node_coords


def run_leiden(G: ig.Graph, resolution: float) -> list[int]:
    has_weights = "weight" in G.es.attributes()
    log.info(f"Running Leiden (resolution={resolution}, weighted={has_weights})...")
    kwargs: dict = {
        "resolution_parameter": resolution,
        "n_iterations": 10,
        "seed": 42,
    }
    if has_weights:
        kwargs["weights"] = "weight"
    partition = leidenalg.find_partition(
        G,
        leidenalg.CPMVertexPartition,
        **kwargs,
    )
    mem = partition.membership
    sizes = sorted(Counter(mem).values(), reverse=True)
    n_big = sum(1 for s in sizes if s >= 50)
    log.info(f"  {len(set(mem)):,} communities, {n_big} with 50+ members")
    return mem


# Maximum number of communities to keep (rest merged into nearest)
MAX_COMMUNITIES = int(os.environ.get("MAX_COMMUNITIES", "100"))


def merge_small_communities(
    G,
    node_ids: list[int],
    membership: list[int],
    min_size: int = None,
) -> list[int]:
    """
    Merge communities below min_size into their most-connected neighbor.
    Uses actual edge connections rather than layout proximity.
    """
    if min_size is None:
        min_size = MIN_COMMUNITY_SIZE
    log.info(
        f"Merging communities below {min_size} members into most-connected neighbor..."
    )

    new_membership = list(membership)
    iteration = 0
    max_iterations = 100

    while iteration < max_iterations:
        iteration += 1

        # Count community sizes
        comm_sizes = Counter(new_membership)
        small_comms = {cid for cid, size in comm_sizes.items() if size < min_size}

        if not small_comms:
            log.info(f"  No small communities remaining after {iteration} iterations")
            break

        log.info(
            f"  Iteration {iteration}: {len(small_comms):,} communities below threshold"
        )

        # Build node index -> community mapping
        node_to_comm = {idx: cid for idx, cid in enumerate(new_membership)}

        # For each small community, count connections to other communities
        small_comm_connections = defaultdict(lambda: defaultdict(int))

        has_weights = "weight" in G.es.attributes()
        for edge in G.es:
            src_idx, tgt_idx = edge.source, edge.target
            w = edge["weight"] if has_weights else 1.0
            src_comm = node_to_comm[src_idx]
            tgt_comm = node_to_comm[tgt_idx]

            if src_comm == tgt_comm:
                continue

            # Accumulate weighted cross-community connections
            if src_comm in small_comms:
                small_comm_connections[src_comm][tgt_comm] += w
            if tgt_comm in small_comms:
                small_comm_connections[tgt_comm][src_comm] += w

        # Merge each small community into its most-connected neighbor
        merge_map = {}
        for small_cid in small_comms:
            connections = small_comm_connections[small_cid]
            if connections:
                # Find the community with most connections
                best_target = max(connections.keys(), key=lambda c: connections[c])
                merge_map[small_cid] = best_target
            else:
                # No connections - merge into largest community
                largest_cid = comm_sizes.most_common(1)[0][0]
                if largest_cid != small_cid:
                    merge_map[small_cid] = largest_cid

        if not merge_map:
            log.info(f"  No merges possible, stopping")
            break

        # Apply merges
        for idx in range(len(new_membership)):
            if new_membership[idx] in merge_map:
                new_membership[idx] = merge_map[new_membership[idx]]

        log.info(f"  Merged {len(merge_map):,} small communities")

    # Renumber communities to be contiguous (0, 1, 2, ...)
    final_comm_sizes = Counter(new_membership)
    old_ids = [cid for cid, _ in final_comm_sizes.most_common()]
    id_remap = {old_id: new_id for new_id, old_id in enumerate(old_ids)}

    new_membership = [id_remap[cid] for cid in new_membership]

    log.info(
        f"  Final: {len(final_comm_sizes):,} communities (renumbered 0-{len(final_comm_sizes)-1})"
    )

    return new_membership


# ---------------------------------------------------------------------------
# Step 6: Analyze Frontiers journals in the global context
# ---------------------------------------------------------------------------
def analyze_frontiers_in_global_network(
    node_ids: list[int],
    membership: list[int],
    node_lookup: dict,
    frontiers_journal_ids: list[int],
    year_range: tuple,
    comm_labels: dict = None,
    node_coords: dict = None,
) -> dict:
    """
    For each Frontiers journal, analyze:
    - What communities do its papers land in?
    - What is the composition of those communities (Frontiers vs external, by field)?
    - Is the journal "in scope" (clusters with related literature) or drifting?
    """
    log.info("Analyzing Frontiers journals in global network context...")

    yr_lo, yr_hi = int(year_range[0]), int(year_range[1])

    # Build community profiles
    comm_profiles = defaultdict(
        lambda: {
            "total": 0,
            "frontiers": 0,
            "by_journal": Counter(),
            "by_publisher": Counter(),
            "years": Counter(),
        }
    )

    for idx, pid in enumerate(node_ids):
        cid = membership[idx]
        meta = node_lookup.get(pid, {})
        if not meta:
            continue

        comm_profiles[cid]["total"] += 1

        if meta.get("IsFrontiers"):
            comm_profiles[cid]["frontiers"] += 1

        jname = meta.get("JournalName") or "Unknown"
        comm_profiles[cid]["by_journal"][jname] += 1

        pub_id = meta.get("PublisherId")
        if pub_id == FRONTIERS_PUBLISHER_ID:
            comm_profiles[cid]["by_publisher"]["Frontiers"] += 1
        elif pub_id:
            comm_profiles[cid]["by_publisher"]["Other"] += 1
        else:
            comm_profiles[cid]["by_publisher"]["Unknown"] += 1

    # Build journal-level analysis
    frontiers_ids_set = set(frontiers_journal_ids)
    journal_results = []

    # Group Frontiers papers by journal
    journal_papers = defaultdict(list)
    for idx, pid in enumerate(node_ids):
        meta = node_lookup.get(pid, {})
        if not meta:
            continue
        jid = meta.get("JournalId")
        if jid in frontiers_ids_set:
            journal_papers[jid].append((idx, pid, meta))

    for jid in frontiers_journal_ids:
        papers = journal_papers.get(jid, [])
        if not papers:
            continue

        jname = papers[0][2].get("JournalName", "Unknown").replace("Frontiers in ", "")

        # First pass: count papers by community to identify primary clusters
        comm_dist = Counter()
        paper_communities = []  # (idx, pid, meta, cid)

        for idx, pid, meta in papers:
            cid = membership[idx]
            comm_dist[cid] += 1
            paper_communities.append((idx, pid, meta, cid))

        total = len(paper_communities)

        # Identify primary clusters: smallest set of communities containing
        # PRIMARY_CLUSTER_COVERAGE of the journal's papers
        primary_clusters = set()
        cumulative = 0
        coverage_target = total * PRIMARY_CLUSTER_COVERAGE

        for cid, count in comm_dist.most_common():
            primary_clusters.add(cid)
            cumulative += count
            if cumulative >= coverage_target:
                break

        # Second pass: papers outside primary clusters are OOS
        # Also collect scatter plot data
        per_year_total = Counter()
        per_year_oos = Counter()
        oos = 0
        scatter_data = []  # For visualization

        for idx, pid, meta, cid in paper_communities:
            y = int(meta.get("PublishedYear") or 0)
            per_year_total[y] += 1

            is_oos = cid not in primary_clusters
            if is_oos:
                oos += 1
                per_year_oos[y] += 1

            # Collect scatter data if coordinates available
            if node_coords and pid in node_coords:
                coord = node_coords[pid]
                scatter_data.append(
                    {
                        "x": round(coord["x"], 4),
                        "y": round(coord["y"], 4),
                        "c": int(cid),
                        "oos": is_oos,
                        "yr": y,
                        "t": (meta.get("Title") or "")[:60],
                    }
                )

        oos_pct = round(100.0 * oos / total, 2) if total else 0.0

        # How many clusters make up the primary set?
        n_primary = len(primary_clusters)
        primary_coverage_actual = (
            round(100.0 * (total - oos) / total, 1) if total else 0
        )

        # Top communities for this journal (mark which are primary)
        top_comms = []
        for cid, count in comm_dist.most_common(10):
            profile = comm_profiles[cid]
            top_journals = profile["by_journal"].most_common(3)
            frontiers_pct = (
                round(100 * profile["frontiers"] / profile["total"], 1)
                if profile["total"]
                else 0
            )
            label = (comm_labels or {}).get(cid, f"Community {cid}")

            top_comms.append(
                {
                    "comm_id": int(cid),
                    "label": label,
                    "is_primary": cid in primary_clusters,
                    "papers_in_comm": int(count),
                    "share_of_journal": round(100 * count / total, 1) if total else 0,
                    "comm_size": int(profile["total"]),
                    "frontiers_pct_in_comm": frontiers_pct,
                    "top_journals_in_comm": [
                        {
                            "name": j,
                            "count": c,
                            "pct": round(100 * c / profile["total"], 1),
                        }
                        for j, c in top_journals
                    ],
                }
            )

        # Per-year breakdown
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

        journal_results.append(
            {
                "journal_id": int(jid),
                "name": jname,
                "articles": int(total),
                "n_primary_clusters": n_primary,
                "primary_coverage_pct": primary_coverage_actual,
                "out_of_scope": int(oos),
                "out_of_scope_pct": oos_pct,
                "top_communities": top_comms,
                "oos_by_year": oos_by_year,
                "scatter": scatter_data,
            }
        )

    # Community summary (all communities after merge)
    comm_summary = []
    for cid, profile in sorted(comm_profiles.items(), key=lambda x: -x[1]["total"]):
        if profile["total"] < MIN_COMMUNITY_SIZE:
            continue
        top_j = profile["by_journal"].most_common(5)
        label = (comm_labels or {}).get(cid, f"Community {cid}")
        # Add dominant_journal to profile for labelling fallback
        profile["dominant_journal"] = top_j[0][0] if top_j else "Unknown"
        comm_summary.append(
            {
                "id": int(cid),
                "label": label,
                "size": int(profile["total"]),
                "frontiers_count": int(profile["frontiers"]),
                "frontiers_pct": round(
                    100 * profile["frontiers"] / profile["total"], 1
                ),
                "dominant_journal": top_j[0][0] if top_j else "Unknown",
                "dominant_pct": (
                    round(100 * top_j[0][1] / profile["total"], 1) if top_j else 0
                ),
                "top_journals": [
                    {"name": j, "pct": round(100 * c / profile["total"], 1)}
                    for j, c in top_j
                ],
            }
        )

    meta = {
        "network_type": NETWORK_MODE,
        "year_range": [yr_lo, yr_hi],
        "primary_cluster_coverage": PRIMARY_CLUSTER_COVERAGE,
        "primary_cluster_level": JOURNAL_DRIFT_LEVEL,
        "edge_weighting": {
            "enabled": ENABLE_EDGE_WEIGHTS,
            "temporal_decay_tau": TEMPORAL_DECAY_TAU,
            "bc_edges_enabled": ENABLE_BC_EDGES,
            "bc_min_shared_refs": BC_MIN_SHARED_REFS,
            "self_cite_journal_weight": SELF_CITE_JOURNAL_WEIGHT,
        },
        "oos_rule": (
            f"Primary clusters = smallest set of communities containing "
            f"{PRIMARY_CLUSTER_COVERAGE:.0%} of a journal's papers at {JOURNAL_DRIFT_LEVEL} resolution. "
            f"An article is out-of-scope if it falls outside those primary clusters."
        ),
        "oos_per_year_years": list(range(yr_lo, yr_hi + 1)),
    }

    return {
        "meta": meta,
        "journals": sorted(journal_results, key=lambda r: -r["out_of_scope_pct"]),
        "communities": comm_summary,
    }


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    log.info("=" * 60)
    log.info("SCOPE DRIFT — Global Citation Network Analysis")
    log.info(f"  Mode: {NETWORK_MODE.upper()}, Years: {YEAR_RANGE[0]}-{YEAR_RANGE[1]}")
    log.info("=" * 60)

    # Step 1: Get target Frontiers journals
    if JOURNAL_IDS_OVERRIDE:
        # Use specific journal IDs if provided
        journal_ids = [
            int(x.strip()) for x in JOURNAL_IDS_OVERRIDE.split(",") if x.strip()
        ]
        log.info(f"Using {len(journal_ids)} specified journal ID(s): {journal_ids}")
        df_journals = None  # Will fetch names separately if needed
    else:
        # Get top N journals by publication count
        df_journals = get_top_frontiers_journals(TOP_N_JOURNALS)
        journal_ids = df_journals["JournalId"].tolist()

    # Step 2: Get Frontiers publication IDs
    frontiers_pub_ids = get_frontiers_publication_ids(journal_ids)

    # Step 3: Build network based on mode
    if NETWORK_MODE == "global":
        # Global network: ALL publications from ALL publishers in year range
        df_edges, final_nodes, all_journal_ids = get_global_network_edges()
        log.info(f"  Frontiers papers in global network: {len(frontiers_pub_ids & final_nodes):,}")
    elif NETWORK_MODE == "full":
        # Full network: Frontiers + related journals (creates connected network)
        df_edges, final_nodes, all_journal_ids = get_full_network_edges(
            frontiers_pub_ids, journal_ids
        )
    else:
        # Ego network: Frontiers papers + their citations (may have disconnected components)
        df_edges, final_nodes = get_ego_network_edges(frontiers_pub_ids)
        all_journal_ids = set(journal_ids)

    # Step 4: Get node metadata
    df_meta = get_node_metadata(final_nodes, journal_ids)
    node_lookup = df_meta.set_index("PublicationId").to_dict("index")

    # Step 4b: Phase 2 edge weighting
    if ENABLE_EDGE_WEIGHTS:
        log.info("Phase 2 edge weighting enabled...")
        df_edges = apply_edge_weights(df_edges, node_lookup)
        if ENABLE_BC_EDGES:
            df_bc = get_bibliographic_coupling_edges(frontiers_pub_ids, all_journal_ids)
            if len(df_bc) > 0:
                df_edges = merge_edge_lists(df_edges, df_bc)
            del df_bc
    else:
        log.info("Edge weighting disabled — using binary unweighted edges")
        df_edges["weight"] = 1.0

    # Step 5: Build graph and run clustering
    G, node_ids = build_graph(df_edges)
    del df_edges

    clarivate_results = None
    use_clarivate = USE_CLARIVATE_TOPICS  # Local flag (avoids modifying global)

    if use_clarivate:
        # Use Clarivate citation topics directly instead of Leiden
        log.info("=" * 40)
        log.info("Using CLARIVATE citation topics (not Leiden)")
        log.info("=" * 40)

        clarivate_results = assign_papers_to_clarivate_topics(node_ids, node_lookup)

        if clarivate_results:
            memberships = {
                "macro": clarivate_results["macro_membership"],
                "meso": clarivate_results["meso_membership"],
                "micro": clarivate_results["micro_membership"],
            }
            membership = memberships[JOURNAL_DRIFT_LEVEL]

            # Build comm_labels from Clarivate topic names
            if JOURNAL_DRIFT_LEVEL == "macro":
                idx_to_id = clarivate_results["idx_to_macro"]
                names = clarivate_results["macro_names"]
            elif JOURNAL_DRIFT_LEVEL == "meso":
                idx_to_id = clarivate_results["idx_to_meso"]
                names = clarivate_results["meso_names"]
            else:
                idx_to_id = clarivate_results["idx_to_micro"]
                names = clarivate_results["micro_names"]

            comm_labels = {
                idx: names.get(topic_id, f"Topic {topic_id}")
                for idx, topic_id in idx_to_id.items()
            }
        else:
            log.error("Failed to assign Clarivate topics — falling back to Leiden")
            use_clarivate = False

    if not use_clarivate:
        # Run Leiden at all resolutions if MULTI_RESOLUTION, else just the configured level
        if MULTI_RESOLUTION:
            log.info("Running multi-resolution Leiden (macro, meso, micro)...")
            memberships = {}
            for level in ["macro", "meso", "micro"]:
                res = LEIDEN_RESOLUTIONS[level]
                raw_mem = run_leiden(G, res)
                min_sz = MIN_COMMUNITY_SIZES[level]
                memberships[level] = merge_small_communities(
                    G, node_ids, raw_mem, min_size=min_sz
                )
                n_comms = len(set(memberships[level]))
                log.info(f"  {level}: {n_comms} communities after merging")
            # Primary membership for OOS calculation and dashboard uses JOURNAL_DRIFT_LEVEL
            membership = memberships[JOURNAL_DRIFT_LEVEL]
        else:
            resolution = LEIDEN_RESOLUTIONS[JOURNAL_DRIFT_LEVEL]
            membership = run_leiden(G, resolution)
            membership = merge_small_communities(G, node_ids, membership)
            memberships = {JOURNAL_DRIFT_LEVEL: membership}

    del G

    # Step 5c: Compute layout for scatter plots (community-based, fast)
    node_coords = compute_layout(node_ids, membership)

    # Step 6: Build community profiles
    log.info("Building community profiles...")
    comm_profiles = defaultdict(
        lambda: {
            "total": 0,
            "frontiers": 0,
            "by_journal": Counter(),
        }
    )
    for idx, pid in enumerate(node_ids):
        cid = membership[idx]
        meta = node_lookup.get(pid, {})
        if not meta:
            continue
        comm_profiles[cid]["total"] += 1
        if meta.get("IsFrontiers"):
            comm_profiles[cid]["frontiers"] += 1
        jname = meta.get("JournalName") or "Unknown"
        comm_profiles[cid]["by_journal"][jname] += 1

    # Add dominant_journal to each profile for labelling fallback
    for cid, profile in comm_profiles.items():
        top_j = profile["by_journal"].most_common(1)
        profile["dominant_journal"] = top_j[0][0] if top_j else f"Community {cid}"

    # Label communities at each level using corresponding Clarivate level
    # (macro→macro, meso→meso, micro→micro)
    if not use_clarivate or not clarivate_results:
        topics_df = load_clarivate_topics()
        all_comm_labels = {}

        for level in ["macro", "meso", "micro"]:
            if level not in memberships:
                continue

            # Build profiles for this level's membership
            level_profiles = defaultdict(
                lambda: {"total": 0, "frontiers": 0, "by_journal": Counter()}
            )
            for idx, pid in enumerate(node_ids):
                cid = memberships[level][idx]
                meta = node_lookup.get(pid, {})
                if not meta:
                    continue
                level_profiles[cid]["total"] += 1
                if meta.get("IsFrontiers"):
                    level_profiles[cid]["frontiers"] += 1
                jname = meta.get("JournalName") or "Unknown"
                level_profiles[cid]["by_journal"][jname] += 1

            for cid, profile in level_profiles.items():
                top_j = profile["by_journal"].most_common(1)
                profile["dominant_journal"] = (
                    top_j[0][0] if top_j else f"Community {cid}"
                )

            # Label this level's communities with corresponding Clarivate level
            all_comm_labels[level] = label_communities(
                dict(level_profiles),
                node_ids,
                memberships[level],
                node_lookup,
                level=level,
                topics_df=topics_df,
            )
            log.info(f"Labelled {len(all_comm_labels[level])} {level} communities")

        # Use the primary level's labels for the main analysis
        comm_labels = all_comm_labels.get(JOURNAL_DRIFT_LEVEL, {})

    # Step 7: Analyze Frontiers journals
    results = analyze_frontiers_in_global_network(
        node_ids,
        membership,
        node_lookup,
        journal_ids,
        YEAR_RANGE,
        comm_labels,
        node_coords,
    )

    # Store all level labels in results
    if not use_clarivate and "all_comm_labels" in dir():
        results["community_labels_by_level"] = all_comm_labels

    # Add clustering method info and multi-resolution assignments to results
    results["clustering_method"] = "clarivate" if use_clarivate else "leiden"
    results["multi_resolution"] = True
    results["cluster_counts"] = {
        level: len(set(mem)) for level, mem in memberships.items()
    }

    # Add per-node cluster assignments for all levels
    node_clusters = []
    for idx, pid in enumerate(node_ids):
        meta = node_lookup.get(pid, {})
        if meta.get("IsFrontiers"):
            entry = {"pub_id": pid}
            for level in ["macro", "meso", "micro"]:
                if level in memberships:
                    entry[f"{level}_cluster"] = memberships[level][idx]
            # Add Clarivate topic info if available
            if clarivate_results and clarivate_results["paper_topics"][idx]:
                entry["clarivate_topic"] = clarivate_results["paper_topics"][idx]
            node_clusters.append(entry)
    results["frontiers_node_clusters"] = node_clusters
    log.info(
        f"Added multi-resolution clusters for {len(node_clusters):,} Frontiers papers"
    )

    # Add Clarivate topic summary if using that mode
    if use_clarivate and clarivate_results:
        results["clarivate_summary"] = {
            "n_matched": clarivate_results["n_matched"],
            "n_unmatched": clarivate_results["n_unmatched"],
            "match_rate": round(
                100 * clarivate_results["n_matched"] / len(node_ids), 1
            ),
        }

    # Save outputs
    output_path = os.path.join(OUTPUT_DIR, "scope_global_network.json")
    with open(output_path, "w") as f:
        json.dump(results, f, indent=2, default=str)
    log.info(f"Saved results to {output_path}")

    dash_path = os.path.join(OUTPUT_DIR, "scope_global_dashboard.html")
    create_html_output.write_dashboard_html(dash_path, results)
    log.info(f"Dashboard: {dash_path}")

    # Summary
    log.info("\n" + "=" * 60)
    log.info("SUMMARY")
    log.info("=" * 60)
    for j in results["journals"]:
        log.info(
            f"  {j['name']}: {j['out_of_scope_pct']:.1f}% OOS ({j['articles']:,} articles)"
        )

    log.info("\nDone!")


if __name__ == "__main__":
    main()
