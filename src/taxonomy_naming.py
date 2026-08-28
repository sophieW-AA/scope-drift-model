"""
taxonomy_naming.py
==================
Maps CWTS publication clusters to academic taxonomy using BigQuery taxonomy tables
and GPT-4o for structured judgment.

Pipeline (per level, coarsest first):
1. Cluster index from classification_raw_{timestamp} (counts only)
2. Sample up to 300 papers per cluster in BigQuery (QUALIFY ROW_NUMBER), with pub_year
3. JOIN taxonomy scores to that sample; years read straight off the sample
4. Build community profiles and filter in-scope L2 topics
5. Aggregate L2 → L1 → L1-cluster → L0
6. Build candidate hierarchy per cluster
7. LLM assigns each cluster to core/bleed taxonomy categories (checkpointed per cluster)
8. Upload this level to BigQuery before the next level starts

Usage:
    python taxonomy_naming.py <timestamp>                       # macro, meso, micro
    python taxonomy_naming.py <timestamp> --levels micro        # one level only
    python taxonomy_naming.py <timestamp> --fresh               # ignore checkpoints

    Or import and call (same timestamp as classification_raw_{timestamp}):
        import taxonomy_naming
        taxonomy_naming.main(timestamp)                  # macro, meso, micro
        taxonomy_naming.main(timestamp, levels="micro")  # one level only

    CLI also reads env RUN_TIMESTAMP (same as cwts_export / dashboards) and
    env CLUSTER_LEVELS.

Levels:
    All three run by default, coarsest first, so macro (~26 clusters) and meso
    (~323) are labelled and uploaded before micro (~3k GPT calls) starts.

Resume:
    Each cluster's LLM result is appended to
    cwts_output/llm_checkpoints/llm_{timestamp}_{level}.jsonl, so a dropped run
    picks up where it stopped instead of re-paying for GPT. Use --fresh to ignore.

Output:
    cwts_output/cluster_taxonomy_labels.csv
    cwts_output/{macro|meso|micro}_labels.csv
    cwts_output/cluster_taxonomy_labels_{macro|meso|micro}.csv
    BigQuery ocean-tech-adv-analytics-c-tfs.taxonomy_labelling (3 tables per run):
      labels_dashboard_{timestamp}  — one row per cluster (level in classification_join_column)
      labels_detail_{timestamp}     — core/bleed taxonomy rows per cluster
      sample_pubs_{timestamp}       — sampled papers (publication_id, community_id,
                                      cluster_level, pub_year)
"""

import json
import logging
import os
import time
from datetime import date
from hashlib import sha256
from pathlib import Path
from textwrap import dedent

import pandas as pd
from google.cloud import bigquery
from openai import OpenAI
import pandas_gbq

# Load .env file if present
from dotenv import load_dotenv
load_dotenv()


# ══════════════════════════════════════════════════════════════════════════════
# CONFIGURATION
# ══════════════════════════════════════════════════════════════════════════════
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)-8s %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger(__name__)

# BigQuery projects
PROJECT_BILL = "ocean-tech-adv-analytics-c-esf"
PROJECT_DATA = "ocean-tech-adv-analytics-c-esf"
BQ_SRC_PROJECT = "ocean-tech-adv-analytics-c-tfs"
BQ_SRC_DATASET = "raw_citation_network_data"

# Source tables
TBL_SCORES = f"{PROJECT_DATA}.aa_taxonomy.article_taxonomy_scores_current"
# Publication years now come from pub_metadata_raw via the sample table,
# so AIRAK Publication (~163M rows) is no longer joined.
TBL_L2_CLUS = f"{PROJECT_DATA}.aa_taxonomy.l2_cluster_assignments"
TBL_L1_CLUS = f"{PROJECT_DATA}.aa_taxonomy.l1_cluster_assignments"

# CWTS tables (constructed from timestamp / RUN_TIMESTAMP)
TBL_CLASSIF = None  # Set in main()
TBL_PUB_META = None  # Set in main()
RUN_TIMESTAMP = os.environ.get("RUN_TIMESTAMP", "")

# Taxonomy labels land in a dedicated dataset; cluster_id joins
# classification_raw_{ts}.{macro|meso|micro} from the scope-drift run.
# Per run: labels_dashboard_{ts}, labels_detail_{ts}, sample_pubs_{ts}.
BQ_DEST_PROJECT = "ocean-tech-adv-analytics-c-tfs"
BQ_LABEL_DATASET = "taxonomy_labelling"
BQ_LOCATION = "EU"
pandas_gbq.context.location = BQ_LOCATION


def bq_labels_dashboard(timestamp: str) -> str:
    return f"{BQ_DEST_PROJECT}.{BQ_LABEL_DATASET}.labels_dashboard_{timestamp}"


def bq_labels_detail(timestamp: str) -> str:
    return f"{BQ_DEST_PROJECT}.{BQ_LABEL_DATASET}.labels_detail_{timestamp}"


def bq_sample_pubs(timestamp: str) -> str:
    return f"{BQ_DEST_PROJECT}.{BQ_LABEL_DATASET}.sample_pubs_{timestamp}"

# Cluster levels to label in one run (classification_raw has micro, meso, macro).
# Coarsest first so usable labels land before the expensive levels run.
ALL_CLUSTER_LEVELS = ("macro", "meso", "micro")
# All three by default; narrow with --levels or env CLUSTER_LEVELS when testing.
CLUSTER_LEVELS = ALL_CLUSTER_LEVELS
CLUSTER_LEVEL = "macro"  # current level while a run is in progress

# Sample size per cluster in BigQuery (None = all papers in the cluster)
SAMPLE_SIZE_PER_CLUSTER = 300

# Output
OUTPUT_DIR = Path("cwts_output")
# Per-cluster LLM results, so a dropped run resumes instead of re-paying for GPT
CHECKPOINT_DIR = OUTPUT_DIR / "llm_checkpoints"

# Scope thresholds
SCOPE_ABS_FLOORS = {"micro": 2, "small": 3, "medium": 5, "large": 10, "mega": 15}
SCOPE_PCT_FLOOR = 0.005

# L1 depth thresholds
L1_DEPTH_FULL = 0.35
L1_DEPTH_PARTIAL = 0.10
L1_ARTICLE_SHARE_FLOOR = 0.010

# LLM settings
LLM_MODEL = "gpt-4o"
LLM_TEMP = 0.0
MAX_CORE = 4
MAX_BLEED = 5

RUN_DATE = date.today().isoformat()

# ══════════════════════════════════════════════════════════════════════════════
# GLOBAL STATE (populated by load functions)
# ══════════════════════════════════════════════════════════════════════════════
bq = None
bq_src = None
oai = None

df_l2_map = None
l1_vocab = {}
l1c_members = {}
l1c_meta = {}
l1_to_clusters = {}
l0_members = {}
l0_name_to_taxref = {}
l2c_members = {}
l2c_meta = {}
l2_to_clusters = {}

community_names = {}
community_pubs = {}
profiles = {}
df_scope = None
df_l1_sig = None
df_clusters_agg = None
df_l0_agg = None
briefs = {}


# ══════════════════════════════════════════════════════════════════════════════
# 1. INITIALIZE CLIENTS
# ══════════════════════════════════════════════════════════════════════════════
def init_clients():
    """Initialize BigQuery and OpenAI clients."""
    global bq, bq_src, oai
    log.info("Initializing clients...")
    bq = bigquery.Client(project=PROJECT_BILL, location=BQ_LOCATION)
    bq_src = bigquery.Client(project=BQ_SRC_PROJECT, location=BQ_LOCATION)
    api_key = os.environ.get("OPENAI_API_KEY") or os.environ.get("GPT4_OPENAI_KEY")
    if not api_key:
        raise RuntimeError("Set OPENAI_API_KEY environment variable")
    oai = OpenAI(api_key=api_key)
    log.info("Clients ready. Run date: %s", RUN_DATE)


BQ_QUERY_RETRIES = 6
CLUSTER_LEVEL_COLS = ("micro", "meso", "macro")


def _is_transient_bq(exc: BaseException) -> bool:
    msg = str(exc).lower()
    return any(
        token in msg
        for token in (
            "ssl",
            "eof",
            "max retries",
            "connection reset",
            "connection aborted",
            "timeout of",
            "temporarily unavailable",
            "503",
            "429",
            "502",
            "reset by peer",
            "broken pipe",
        )
    )


def query_df(sql: str, job_config=None, *, client=None, retries: int = BQ_QUERY_RETRIES) -> pd.DataFrame:
    """Run a query and download results, retrying SSL / connection drops."""
    cli = client or bq
    last = None
    for attempt in range(1, retries + 1):
        try:
            return cli.query(sql, job_config=job_config).to_dataframe()
        except Exception as exc:
            last = exc
            if attempt >= retries or not _is_transient_bq(exc):
                raise
            wait = min(2 ** attempt, 60)
            log.warning(
                "BigQuery query failed (%s); retry %s/%s in %ss",
                type(exc).__name__,
                attempt,
                retries,
                wait,
            )
            time.sleep(wait)
    raise last


def run_sql(sql: str, *, client=None, retries: int = BQ_QUERY_RETRIES):
    """Run a DDL/DML job (no dataframe), retrying SSL / connection drops."""
    cli = client or bq_src
    last = None
    for attempt in range(1, retries + 1):
        try:
            return cli.query(sql).result()
        except Exception as exc:
            last = exc
            if attempt >= retries or not _is_transient_bq(exc):
                raise
            wait = min(2 ** attempt, 60)
            log.warning(
                "BigQuery job failed (%s); retry %s/%s in %ss",
                type(exc).__name__,
                attempt,
                retries,
                wait,
            )
            time.sleep(wait)
    raise last


def _assert_level(level: str) -> str:
    if level not in CLUSTER_LEVEL_COLS:
        raise ValueError(f"level must be one of {CLUSTER_LEVEL_COLS}, got {level!r}")
    return level


def cluster_sample_select_sql(level: str) -> str:
    """Up to SAMPLE_SIZE_PER_CLUSTER papers per cluster, chosen in BigQuery."""
    level = _assert_level(level)
    qualify = ""
    if SAMPLE_SIZE_PER_CLUSTER:
        qualify = f"""
        QUALIFY ROW_NUMBER() OVER (
          PARTITION BY c.{level}
          ORDER BY FARM_FINGERPRINT(CAST(m.pub_id AS STRING))
        ) <= {int(SAMPLE_SIZE_PER_CLUSTER)}
        """
    return f"""
    SELECT
      CAST(m.pub_id AS INT64) AS publication_id,
      CAST(c.{level} AS INT64) AS community_id,
      '{level}' AS cluster_level,
      EXTRACT(YEAR FROM SAFE.PARSE_DATE(
        '%Y-%m-%d', SUBSTR(CAST(m.date AS STRING), 1, 10)
      )) AS pub_year
    FROM `{TBL_CLASSIF}` c
    INNER JOIN `{TBL_PUB_META}` m
      ON c.int_id = m.int_id
    WHERE c.{level} IS NOT NULL
      AND SAFE_CAST(m.pub_id AS INT64) IS NOT NULL
    {qualify}
    """


def bq_table_columns(fq: str, *, client=None) -> set[str] | None:
    """Column names for a table, or None when it does not exist."""
    from google.cloud.exceptions import NotFound

    cli = client or bq_src
    try:
        return {f.name for f in cli.get_table(fq).schema}
    except NotFound:
        return None


def materialize_cluster_sample(
    level: str, timestamp: str, *, replace_table: bool = False
) -> str:
    """Write sampled pubs into sample_pubs_{ts} (all levels share one table).

    Columns: publication_id, community_id, cluster_level, pub_year.
    First level of a run uses CREATE OR REPLACE; later levels DELETE+INSERT that level.
    """
    ensure_label_dataset()
    fq = bq_sample_pubs(timestamp)
    cap = SAMPLE_SIZE_PER_CLUSTER or "all"
    log.info("Sampling up to %s papers per %s cluster in BigQuery → %s", cap, level, fq)
    select_sql = cluster_sample_select_sql(level)
    cols = bq_table_columns(fq)
    # Rebuild when missing, or when an older run left a table without pub_year
    if replace_table or cols is None or "pub_year" not in cols:
        run_sql(f"CREATE OR REPLACE TABLE `{fq}` AS\n{select_sql}", client=bq_src)
    else:
        run_sql(
            f"DELETE FROM `{fq}` WHERE cluster_level = '{level}'",
            client=bq_src,
        )
        run_sql(f"INSERT INTO `{fq}`\n{select_sql}", client=bq_src)
    n = query_df(
        f"SELECT COUNT(*) AS n FROM `{fq}` WHERE cluster_level = '{level}'",
        client=bq_src,
    )
    log.info(
        "%s sample: %s publication rows",
        level,
        f"{int(n['n'].iloc[0]):,}" if len(n) else "0",
    )
    return fq


# ══════════════════════════════════════════════════════════════════════════════
# 2. LOAD CWTS COMMUNITIES
# ══════════════════════════════════════════════════════════════════════════════
def fetch_classification_papers() -> pd.DataFrame:
    """Load classification + metadata once (all three cluster columns)."""
    log.info("Loading CWTS data from BigQuery...")
    df = bq_src.query(f"""
        SELECT
            c.int_id, c.micro, c.meso, c.macro,
            m.pub_id, m.is_frontiers, m.journal, m.date, m.title
        FROM `{TBL_CLASSIF}` c
        JOIN `{TBL_PUB_META}` m ON c.int_id = m.int_id
    """).to_dataframe()
    log.info("Loaded %d papers from BigQuery", len(df))
    return df


def group_communities(df: pd.DataFrame, level: str) -> dict:
    """Cluster ids and full paper counts at this level. Sampling happens in SQL."""
    global community_names, community_pubs, CLUSTER_LEVEL

    CLUSTER_LEVEL = _assert_level(level)
    if level not in df.columns:
        raise ValueError(f"No column {level!r} in classification papers")

    counts = df.dropna(subset=[level]).groupby(level).size()
    community_pubs = {int(k): int(n) for k, n in counts.items()}
    community_ids = sorted(community_pubs)
    community_names = {cid: f"Cluster {cid}" for cid in community_ids}

    log.info("%s communities: %d | publications (full): %s",
             level, len(community_ids), f"{sum(community_pubs.values()):,}")
    return {"community_ids": community_ids}


def load_cluster_index(level: str) -> dict:
    """Cluster ids + full n_papers from classification — does not download papers."""
    global community_names, community_pubs, CLUSTER_LEVEL

    CLUSTER_LEVEL = _assert_level(level)
    df = query_df(
        f"""
        SELECT
          CAST({level} AS INT64) AS community_id,
          COUNT(*) AS n_papers
        FROM `{TBL_CLASSIF}`
        WHERE {level} IS NOT NULL
        GROUP BY 1
        """,
        client=bq_src,
    )
    community_pubs = {
        int(r.community_id): int(r.n_papers) for r in df.itertuples(index=False)
    }
    community_ids = sorted(community_pubs)
    community_names = {cid: f"Cluster {cid}" for cid in community_ids}
    log.info(
        "%s communities: %d | publications (full): %s",
        level,
        len(community_ids),
        f"{sum(community_pubs.values()):,}",
    )
    return {"community_ids": community_ids}


def load_communities() -> dict:
    """Back-compat: cluster index for the current CLUSTER_LEVEL."""
    return load_cluster_index(CLUSTER_LEVEL)


# ══════════════════════════════════════════════════════════════════════════════
# 3. LOAD TAXONOMY REFERENCE DATA
# ══════════════════════════════════════════════════════════════════════════════
def load_taxonomy():
    """Load L0/L1/L2 taxonomy hierarchy from BigQuery."""
    global df_l2_map, l1_vocab, l1c_members, l1c_meta, l1_to_clusters
    global l0_members, l0_name_to_taxref, l2c_members, l2c_meta, l2_to_clusters
    
    log.info("Loading taxonomy reference data...")
    
    # L2 → L1 → L0 mapping
    _df_l2_raw = bq.query(f"""
        SELECT DISTINCT l2_taxref AS l2_key, l2_name, l1_taxref, l1_name
        FROM `{TBL_L2_CLUS}`
    """).to_dataframe()
    
    _df_l1_l0 = bq.query(f"""
        SELECT DISTINCT l1_taxref, l1_name, l0_taxref, l0_name
        FROM `{TBL_L1_CLUS}`
    """).to_dataframe()
    
    df_l2_map = _df_l2_raw.merge(
        _df_l1_l0[["l1_taxref", "l0_taxref", "l0_name"]].drop_duplicates("l1_taxref"),
        on="l1_taxref", how="left"
    )
    log.info("L2 map: %d rows", len(df_l2_map))
    
    # L1 vocabulary size
    l1_vocab = df_l2_map.groupby("l1_taxref")["l2_key"].count().astype(int).to_dict()
    
    # L1 cluster membership
    df_l1c_raw = bq.query(f"""
        SELECT l0_taxref, l0_name, l1_taxref, l1_name, cluster_id, cluster_name, level_index
        FROM `{TBL_L1_CLUS}`
        ORDER BY level_index
    """).to_dataframe()
    
    seen_fs = set()
    _canon = (df_l1c_raw.sort_values("level_index")
              .drop_duplicates(["l0_taxref", "cluster_id"])
              .set_index(["l0_taxref", "cluster_id"])["cluster_name"])
    
    for (l0_txr, cid), grp in df_l1c_raw.groupby(["l0_taxref", "cluster_id"]):
        members = frozenset(grp["l1_taxref"].tolist())
        if len(members) < 2 or members in seen_fs:
            continue
        seen_fs.add(members)
        key = f"l1c_{sha256(','.join(sorted(str(x) for x in members)).encode()).hexdigest()[:8]}"
        name = _canon.get((l0_txr, cid), f"cluster_{cid}")
        l1c_members[key] = members
        l1c_meta[key] = {"key": key, "name": name, "l0_taxref": int(l0_txr), "l0_name": grp["l0_name"].iloc[0]}
    
    # L1 to clusters mapping
    for ck, mems in l1c_members.items():
        for t in mems:
            l1_to_clusters.setdefault(int(t), []).append(ck)
    
    # L0 membership
    for _, r in df_l1c_raw.dropna(subset=["l0_taxref", "l1_taxref"]).iterrows():
        txr = int(r["l0_taxref"])
        if txr not in l0_members:
            l0_members[txr] = {"name": r["l0_name"], "l1s": set()}
        l0_members[txr]["l1s"].add(int(r["l1_taxref"]))
    
    l0_name_to_taxref = {v["name"]: k for k, v in l0_members.items()}
    
    # L2 cluster membership
    df_l2c_raw = bq.query(f"""
        SELECT l1_taxref, l1_name, l2_taxref AS l2_key, l2_name, cluster_id, cluster_name
        FROM `{TBL_L2_CLUS}`
        ORDER BY cluster_id
    """).to_dataframe()
    
    seen_l2fs = set()
    _l2c_canon = df_l2c_raw.drop_duplicates(["l1_taxref", "cluster_id"]).set_index(["l1_taxref", "cluster_id"])["cluster_name"]
    
    for (l1_txr, cid), grp in df_l2c_raw.groupby(["l1_taxref", "cluster_id"]):
        members = frozenset(grp["l2_name"].tolist())
        if len(members) < 2 or members in seen_l2fs:
            continue
        seen_l2fs.add(members)
        key = f"l2c_{sha256(','.join(sorted(members)).encode()).hexdigest()[:8]}"
        name = _l2c_canon.get((l1_txr, cid), f"cluster_{cid}")
        l2c_members[key] = members
        l2c_meta[key] = {"key": key, "name": name, "l1_taxref": int(l1_txr), "l1_name": grp["l1_name"].iloc[0]}
    
    for ck, mems in l2c_members.items():
        for l2 in mems:
            l2_to_clusters.setdefault(l2, []).append(ck)
    
    log.info("L1 clusters: %d unique | L0 domains: %d | L2 clusters: %d", 
             len(l1c_members), len(l0_members), len(l2c_members))


# ══════════════════════════════════════════════════════════════════════════════
# 4. PULL TAXONOMY SCORES
# ══════════════════════════════════════════════════════════════════════════════
def pull_taxonomy_scores(id_table: str, level: str | None = None) -> pd.DataFrame:
    """L2 taxonomy scores for the SQL-sampled papers (community_id already on the sample)."""
    level = level or CLUSTER_LEVEL
    log.info("Pulling taxonomy scores from sample %s (level=%s)", id_table, level)
    df_scores_raw = query_df(
        f"""
        SELECT
            CAST(t.publication_id AS INT64) AS publication_id,
            t.taxref AS l2_key,
            l2.l2_name,
            ids.community_id
        FROM `{id_table}` ids
        INNER JOIN `{TBL_SCORES}` t
          ON CAST(t.publication_id AS INT64) = ids.publication_id
        INNER JOIN `{TBL_L2_CLUS}` l2
          ON t.taxref = l2.l2_taxref
        WHERE t.level = 2
          AND t.in_top_k = TRUE
          AND t.is_weak_match = FALSE
          AND ids.cluster_level = '{level}'
        """,
        client=bq_src,
    )

    if df_scores_raw is None or df_scores_raw.empty:
        log.warning("No taxonomy score rows for this sample")
        return pd.DataFrame(
            columns=[
                "community_id",
                "l2_key",
                "n_articles",
                "l2_name",
                "l1_taxref",
                "l1_name",
                "l0_taxref",
                "l0_name",
            ]
        )

    log.info(
        "Score rows: %d | Unique pubs matched: %d",
        len(df_scores_raw),
        int(df_scores_raw["publication_id"].nunique()),
    )

    df_scores_raw = df_scores_raw.dropna(subset=["community_id"])
    df_scores_raw["community_id"] = df_scores_raw["community_id"].astype(int)
    
    # Aggregate to (community, L2)
    df_l2_counts = (df_scores_raw.groupby(["community_id", "l2_key"])["publication_id"]
                    .nunique().reset_index().rename(columns={"publication_id": "n_articles"}))
    
    # Merge taxonomy hierarchy
    df_l2_counts = df_l2_counts.merge(
        df_l2_map[["l2_key", "l2_name", "l1_taxref", "l1_name", "l0_taxref", "l0_name"]],
        on="l2_key", how="left"
    )
    df_l2_counts = df_l2_counts.dropna(subset=["l1_taxref"]).copy()
    df_l2_counts["l1_taxref"] = df_l2_counts["l1_taxref"].astype(int)
    df_l2_counts["l0_taxref"] = df_l2_counts["l0_taxref"].astype(int)
    
    log.info("(community, L2) pairs after taxonomy join: %d", len(df_l2_counts))
    return df_l2_counts


# ══════════════════════════════════════════════════════════════════════════════
# 5. BUILD PROFILES AND SCOPE FILTER
# ══════════════════════════════════════════════════════════════════════════════
def build_profiles(community_ids: list, id_table: str, level: str | None = None):
    """Build community profiles and compute in-scope L2 filter."""
    global profiles
    level = level or CLUSTER_LEVEL

    log.info("Building community profiles...")
    current_year = date.today().year

    # Years come from the sample table (pub_metadata date), aggregated in BigQuery.
    df_pub_years = query_df(
        f"""
        SELECT
          community_id,
          pub_year,
          COUNT(*) AS n_articles
        FROM `{id_table}`
        WHERE cluster_level = '{level}'
          AND pub_year IS NOT NULL
        GROUP BY 1, 2
        """,
        client=bq_src,
    )

    if df_pub_years is None or df_pub_years.empty:
        years_by_cid: dict[int, pd.DataFrame] = {}
    else:
        df_pub_years = df_pub_years.dropna(subset=["community_id"])
        df_pub_years["community_id"] = df_pub_years["community_id"].astype(int)
        years_by_cid = {
            int(cid): grp.sort_values("pub_year")
            for cid, grp in df_pub_years.groupby("community_id")
        }

    for cid in community_ids:
        total = int(community_pubs[cid])
        
        # Size class
        if total < 50: size_class = "micro"
        elif total < 300: size_class = "small"
        elif total < 2000: size_class = "medium"
        elif total < 10000: size_class = "large"
        else: size_class = "mega"
        
        # Age and growth
        yr_grp = years_by_cid.get(cid, pd.DataFrame(columns=["pub_year", "n_articles"])).copy()

        if not yr_grp.empty:
            yr_grp["cumpct"] = yr_grp["n_articles"].cumsum() / yr_grp["n_articles"].sum()
            start_row = yr_grp[yr_grp["cumpct"] >= 0.10].iloc[0]
            effective_start = int(start_row["pub_year"])
            age = max(1, current_year - effective_start)
            recent = int(yr_grp[yr_grp["pub_year"] >= current_year - 2]["n_articles"].sum())
            early = int(yr_grp[yr_grp["pub_year"] <= effective_start + 2]["n_articles"].sum())
            growth_ratio = recent / max(early, 1)
            
            age_class = "new" if age < 3 else "growing" if age < 7 else "established" if age < 15 else "mature"
            growth_class = ("accelerating" if growth_ratio > 3.0 else "growing" if growth_ratio > 1.2 
                           else "stable" if growth_ratio > 0.8 else "declining")
        else:
            effective_start, age, growth_ratio = current_year, 1, 1
            age_class = growth_class = "unknown"
        
        profiles[cid] = {
            "community_id": cid, "n_articles": total, "effective_start": effective_start,
            "age_years": age, "growth_ratio": round(growth_ratio, 2),
            "size_class": size_class, "age_class": age_class, "growth_class": growth_class,
        }
    
    log.info("Profiles built for %d communities", len(profiles))


def mark_in_scope(df: pd.DataFrame) -> pd.DataFrame:
    """Apply adaptive in-scope filter."""
    df = df.copy()
    abs_floors = df["community_id"].map(
        lambda cid: SCOPE_ABS_FLOORS.get(profiles.get(cid, {}).get("size_class", "medium"), 5))
    total_arts = df["community_id"].map(lambda cid: profiles.get(cid, {}).get("n_articles", 1))
    df["pct"] = df["n_articles"] / total_arts
    df["in_scope"] = (df["n_articles"] >= abs_floors) | (df["pct"] >= SCOPE_PCT_FLOOR)
    return df[df["in_scope"]].drop(columns=["pct", "in_scope"])


# ══════════════════════════════════════════════════════════════════════════════
# 6. AGGREGATE L2 → L1 → L1-CLUSTER → L0
# ══════════════════════════════════════════════════════════════════════════════
def aggregate_to_higher_levels(df_l2_counts: pd.DataFrame):
    """Aggregate L2 counts to L1, L1-cluster, and L0 levels."""
    global df_scope, df_l1_sig, df_clusters_agg, df_l0_agg
    
    log.info("Aggregating to higher levels...")
    
    # Apply in-scope filter
    df_scope = mark_in_scope(df_l2_counts)
    df_scope = df_scope.rename(columns={"community_id": "journal_id"})
    log.info("In-scope (community, L2) pairs: %d", len(df_scope))
    
    # L1 aggregation
    df_l1_agg = (df_scope.groupby(["journal_id", "l1_taxref", "l1_name", "l0_taxref", "l0_name"])
                 .agg(n_scope_l2=("l2_key", "count"), n_articles_in_l1=("n_articles", "sum"))
                 .reset_index())
    df_l1_agg["l1_vocab_size"] = df_l1_agg["l1_taxref"].map(l1_vocab).fillna(1).astype(int)
    df_l1_agg["depth"] = df_l1_agg["n_scope_l2"] / df_l1_agg["l1_vocab_size"]
    df_l1_agg["depth_class"] = pd.cut(df_l1_agg["depth"], 
                                       bins=[-1, L1_DEPTH_PARTIAL, L1_DEPTH_FULL, 2.0],
                                       labels=["noise", "partial", "full"])
    df_l1_sig = df_l1_agg[df_l1_agg["depth_class"] != "noise"].copy()
    log.info("Significant (journal, L1) pairs: %d", len(df_l1_sig))
    
    # L1-cluster aggregation
    cluster_rows = []
    for jid, jgrp in df_l1_sig.groupby("journal_id"):
        sig_l1s = set(jgrp["l1_taxref"].astype(int))
        full_l1s = set(jgrp[jgrp["depth_class"] == "full"]["l1_taxref"].astype(int))
        for ck, mems in l1c_members.items():
            active = mems & sig_l1s
            full = mems & full_l1s
            if not active or len(active) / len(mems) < 0.5:
                continue
            art_in_cluster = int(jgrp[jgrp["l1_taxref"].isin(active)]["n_articles_in_l1"].sum())
            cluster_rows.append({
                "journal_id": int(jid), "cluster_key": ck, "cluster_name": l1c_meta[ck]["name"],
                "l0_taxref": l1c_meta[ck]["l0_taxref"], "l0_name": l1c_meta[ck]["l0_name"],
                "n_l1s": len(mems), "n_active_l1s": len(active), "n_full_l1s": len(full),
                "frac_active": round(len(active) / len(mems), 3),
                "frac_full": round(len(full) / len(mems), 3),
                "n_articles": art_in_cluster,
            })
    df_clusters_agg = pd.DataFrame(cluster_rows)
    log.info("(journal, L1-cluster) pairs: %d", len(df_clusters_agg))
    
    # L0 aggregation
    l0_rows = []
    for jid, jgrp in df_l1_sig.groupby("journal_id"):
        sig_l1s = set(jgrp["l1_taxref"].astype(int))
        full_l1s = set(jgrp[jgrp["depth_class"] == "full"]["l1_taxref"].astype(int))
        j_total_arts = jgrp["n_articles_in_l1"].sum()
        concentrated_l1s = set(jgrp[jgrp["n_articles_in_l1"] / j_total_arts >= L1_ARTICLE_SHARE_FLOOR]["l1_taxref"].astype(int))
        
        for l0_txr, l0 in l0_members.items():
            active = l0["l1s"] & concentrated_l1s
            active_any = l0["l1s"] & sig_l1s
            full = l0["l1s"] & full_l1s
            if not active:
                continue
            frac_active = len(active) / len(l0["l1s"])
            art_in_l0 = int(jgrp[jgrp["l1_taxref"].isin(active_any)]["n_articles_in_l1"].sum())
            l0_rows.append({
                "journal_id": int(jid), "l0_taxref": l0_txr, "l0_name": l0["name"],
                "n_l1s": len(l0["l1s"]), "n_active_l1s": len(active_any), "n_full_l1s": len(full),
                "frac_active": round(frac_active, 3), "n_articles": art_in_l0,
            })
    df_l0_agg = pd.DataFrame(l0_rows)
    log.info("(journal, L0) pairs: %d", len(df_l0_agg))


# ══════════════════════════════════════════════════════════════════════════════
# 7. BUILD CANDIDATE HIERARCHY
# ══════════════════════════════════════════════════════════════════════════════
def build_candidates(journal_id: int) -> dict:
    """Build non-overlapping candidate hierarchy for one community."""
    profile = profiles.get(journal_id, {})
    l1_rows = df_l1_sig[df_l1_sig["journal_id"] == journal_id]
    clus_rows = df_clusters_agg[df_clusters_agg["journal_id"] == journal_id]
    l0_rows_j = df_l0_agg[df_l0_agg["journal_id"] == journal_id]
    
    sig_l1_set = set(l1_rows["l1_taxref"].astype(int))
    full_l1_set = set(l1_rows[l1_rows["depth_class"] == "full"]["l1_taxref"].astype(int))
    covered_by_cluster = set()
    
    # Step A: L1 clusters
    surfaced_clusters = []
    for _, cr in clus_rows[clus_rows["n_full_l1s"] >= 2].iterrows():
        mems = l1c_members[cr["cluster_key"]]
        full_in_cluster = mems & full_l1_set
        surfaced_clusters.append({
            "level": "l1_cluster", "key": cr["cluster_key"], "name": cr["cluster_name"],
            "l0_name": cr["l0_name"], "n_l1s": cr["n_l1s"], "n_full_l1s": cr["n_full_l1s"],
            "frac_full": cr["frac_full"], "n_articles": cr["n_articles"],
            "member_l1s": [l1_rows[l1_rows["l1_taxref"] == t]["l1_name"].iloc[0]
                          for t in full_in_cluster if len(l1_rows[l1_rows["l1_taxref"] == t]) > 0],
        })
        covered_by_cluster |= mems
    
    # Step B: L1 singles
    surfaced_l1s = []
    for _, lr in l1_rows[~l1_rows["l1_taxref"].isin(covered_by_cluster)].iterrows():
        l2s_for_l1 = (df_scope[(df_scope["journal_id"] == journal_id) & (df_scope["l1_taxref"] == lr["l1_taxref"])]
                      .sort_values("n_articles", ascending=False).head(5)[["l2_key", "l2_name", "n_articles"]].to_dict("records"))
        surfaced_l1s.append({
            "level": "l1_single", "key": f"l1_{int(lr['l1_taxref'])}", "name": lr["l1_name"],
            "l0_name": lr["l0_name"], "depth": round(float(lr["depth"]), 3),
            "depth_class": str(lr["depth_class"]), "n_scope_l2": int(lr["n_scope_l2"]),
            "l1_vocab_size": int(lr["l1_vocab_size"]), "n_articles": int(lr["n_articles_in_l1"]),
            "top_l2s": l2s_for_l1,
        })
    
    # Step C: L0 domains
    surfaced_l0s = []
    for _, lr in l0_rows_j[l0_rows_j["frac_active"] >= 0.5].iterrows():
        clusters_in_l0 = [c for c in surfaced_clusters if c["l0_name"] == lr["l0_name"]]
        if len(clusters_in_l0) < 2:
            continue
        surfaced_l0s.append({
            "level": "l0_domain", "key": f"l0_{int(lr['l0_taxref'])}", "name": lr["l0_name"],
            "n_l1s_total": lr["n_l1s"], "n_active_l1s": lr["n_active_l1s"],
            "n_full_l1s": lr["n_full_l1s"], "frac_active": lr["frac_active"],
            "n_articles": lr["n_articles"], "clusters": [c["name"] for c in clusters_in_l0],
        })
    
    # Step D: L2 cluster fallback for niche communities
    is_niche = (not surfaced_l0s and not surfaced_clusters and 
                (not surfaced_l1s or (profile.get("size_class") in ("micro", "small") 
                 and all(s["depth_class"] == "partial" for s in surfaced_l1s))))
    
    l2_clusters_out = []
    l2_fallback = False
    if is_niche:
        l2_rows = df_scope[df_scope["journal_id"] == journal_id]
        if not l2_rows.empty:
            l2_fallback = True
            surfaced_l1s = []
            jl2_keys = set(l2_rows["l2_key"].tolist())
            for ck, members in l2c_members.items():
                overlap = members & jl2_keys
                if not overlap:
                    continue
                art_count = int(l2_rows[l2_rows["l2_key"].isin(overlap)]["n_articles"].sum())
                meta = l2c_meta[ck]
                l2_clusters_out.append({
                    "level": "l2_cluster", "key": ck, "name": meta["name"],
                    "l1_name": meta["l1_name"], "n_l2s_total": len(members),
                    "n_l2s_covered": len(overlap), "frac_covered": round(len(overlap) / len(members), 3),
                    "n_articles": art_count, "member_l2s": sorted(overlap)[:6],
                })
            l2_clusters_out.sort(key=lambda x: -x["n_articles"])
    
    return {
        "journal_id": journal_id, "journal_name": community_names.get(journal_id, str(journal_id)),
        "profile": profile, "l0_domains": surfaced_l0s, "l1_clusters": surfaced_clusters,
        "l1_singles": surfaced_l1s, "l2_clusters": l2_clusters_out,
        "n_scope_l2_total": int(df_scope[df_scope["journal_id"] == journal_id].shape[0]),
        "_l2_fallback": l2_fallback,
    }


def build_all_briefs(community_ids: list):
    """Build candidate briefs for all communities."""
    global briefs
    log.info("Building candidate briefs...")
    briefs = {cid: build_candidates(cid) for cid in community_ids}
    log.info("Candidate briefs built for %d communities", len(briefs))


# ══════════════════════════════════════════════════════════════════════════════
# 8. LLM JUDGMENT
# ══════════════════════════════════════════════════════════════════════════════
SYSTEM_PROMPT = dedent("""
    You are an expert in academic publishing and research taxonomy.
    Your task: determine the **academic topic position** of a publication community.
    
    You will receive a structured brief with candidate taxonomy clusters.
    Select 1-{max_core} **core** clusters (primary focus) and optionally 1-{max_bleed} **bleed** clusters (secondary).
    
    Keys must be copied exactly from the brief. Return JSON:
    ```json
    {{
      "core": [{{"key": "...", "name": "...", "level": "...", "rationale": "..."}}],
      "bleed": [...],
      "match_mode": "primary | combination",
      "confidence": "high | medium | low",
      "overall_reasoning": "..."
    }}
    ```
""").strip()


def format_brief(brief: dict, journal_name: str, used_labels: set = None) -> str:
    """Convert candidate brief to LLM prompt text.
    
    Args:
        brief: Candidate hierarchy for this community
        journal_name: Name of the community/cluster
        used_labels: Set of (key, name) tuples already assigned to other communities
    """
    p = brief["profile"]
    lines = [
        f"## Publication community: {journal_name}",
        f"Profile: {p.get('size_class','?')} ({p.get('n_articles','?')} papers), "
        f"{p.get('age_class','?')} ({p.get('age_years','?')} yrs), growth: {p.get('growth_class','?')}",
        f"Total in-scope L2 topics: {brief['n_scope_l2_total']}", ""
    ]
    
    # Option 1: Add warning about already-used labels
    if used_labels:
        used_names = sorted(set(name for _, name in used_labels))
        if used_names:
            lines.append("### ⚠️ Labels already assigned to other communities (avoid if possible):")
            for name in used_names[:15]:  # Show up to 15
                lines.append(f"  - {name}")
            if len(used_names) > 15:
                lines.append(f"  ... and {len(used_names) - 15} more")
            lines.append("")
    
    if brief["l0_domains"]:
        lines.append("### L0 Domain candidates")
        for d in sorted(brief["l0_domains"], key=lambda x: -x["n_articles"]):
            lines.append(f"  key={d['key']}  name='{d['name']}'  articles={d['n_articles']:,}")
        lines.append("")
    
    if brief["l1_clusters"]:
        lines.append("### L1 Cluster candidates")
        for c in sorted(brief["l1_clusters"], key=lambda x: -x["n_articles"]):
            lines.append(f"  key={c['key']}  name='{c['name']}'  articles={c['n_articles']:,}")
        lines.append("")
    
    if brief["l1_singles"]:
        lines.append("### L1 Single-discipline candidates")
        for s in sorted(brief["l1_singles"], key=lambda x: -x["n_articles"]):
            top = ", ".join(t["l2_name"].split(" - ", 1)[-1] for t in s.get("top_l2s", [])[:3])
            lines.append(f"  key={s['key']}  name='{s['name']}'  articles={s['n_articles']:,}  top: {top}")
        lines.append("")
    
    if brief.get("l2_clusters"):
        lines.append("### L2 Cluster candidates (niche)")
        for c in brief["l2_clusters"][:10]:
            lines.append(f"  key={c['key']}  name='{c['name']}'  articles={c['n_articles']:,}")
        lines.append("")
    
    return "\n".join(lines)


def parse_llm_response(text: str) -> dict:
    """Extract JSON from LLM response."""
    import re
    match = re.search(r"```json\s*([\s\S]+?)\s*```", text)
    if match:
        return json.loads(match.group(1))
    match = re.search(r"(\{[\s\S]+\})", text)
    if match:
        return json.loads(match.group(1))
    raise ValueError("No JSON found")


def call_llm(journal_id: int, journal_name: str, brief: dict, used_labels: set = None, force_unique: bool = False) -> dict:
    """Call LLM for one community.
    
    Args:
        journal_id: Community ID
        journal_name: Community name
        brief: Candidate hierarchy
        used_labels: Set of (key, name) tuples already assigned
        force_unique: If True, add stronger instruction to avoid duplicates (for retry pass)
    """
    user_text = format_brief(brief, journal_name, used_labels)
    system = SYSTEM_PROMPT.format(max_core=MAX_CORE, max_bleed=MAX_BLEED)
    
    # Option 4: Stronger uniqueness instruction for retry pass
    if force_unique and used_labels:
        used_names = [name for _, name in used_labels]
        system += f"\n\nIMPORTANT: The following labels are ALREADY ASSIGNED to other communities and must NOT be used: {', '.join(used_names[:20])}. Choose more specific alternatives."
    
    try:
        resp = oai.chat.completions.create(
            model=LLM_MODEL, temperature=LLM_TEMP,
            messages=[{"role": "system", "content": system}, {"role": "user", "content": user_text}]
        )
        data = parse_llm_response(resp.choices[0].message.content)
    except Exception as e:
        log.error("LLM error for %s: %s", journal_name, e)
        data = {"core": [], "bleed": [], "match_mode": "error", "confidence": "low", "overall_reasoning": str(e)}
    
    data["_journal_id"] = journal_id
    data["_journal_name"] = journal_name
    return data


# ══════════════════════════════════════════════════════════════════════════════
# 9. RUN LLM AND POST-PROCESS
# ══════════════════════════════════════════════════════════════════════════════
def extract_labels_from_result(result: dict) -> set:
    """Extract (key, name) tuples from an LLM result."""
    labels = set()
    for tier in ["core", "bleed"]:
        for sel in result.get(tier, []):
            key = sel.get("key", "")
            name = sel.get("name", "")
            if key and name:
                labels.add((key, name))
    return labels


def checkpoint_path(timestamp: str, level: str) -> Path:
    return CHECKPOINT_DIR / f"llm_{timestamp}_{level}.jsonl"


def load_checkpoint(timestamp: str, level: str) -> dict:
    """Per-cluster LLM results already paid for in an earlier attempt."""
    path = checkpoint_path(timestamp, level)
    if not path.exists():
        return {}
    done = {}
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                rec = json.loads(line)
            except json.JSONDecodeError:
                continue  # truncated final write from a killed run
            jid = rec.get("_journal_id")
            if jid is None:
                continue
            done[int(jid)] = rec
    if done:
        log.info("Checkpoint: %d %s clusters already labelled (%s)", len(done), level, path)
    return done


def append_checkpoint(timestamp: str, level: str, result: dict) -> None:
    CHECKPOINT_DIR.mkdir(parents=True, exist_ok=True)
    with checkpoint_path(timestamp, level).open("a", encoding="utf-8") as f:
        f.write(json.dumps(result, default=str) + "\n")
        f.flush()


def rewrite_checkpoint(timestamp: str, level: str, llm_results: dict) -> None:
    """Persist final results (after duplicate resolution) so a resume is consistent."""
    CHECKPOINT_DIR.mkdir(parents=True, exist_ok=True)
    tmp = checkpoint_path(timestamp, level).with_suffix(".jsonl.tmp")
    with tmp.open("w", encoding="utf-8") as f:
        for jid, res in llm_results.items():
            rec = {**res, "_journal_id": int(jid)}
            f.write(json.dumps(rec, default=str) + "\n")
    tmp.replace(checkpoint_path(timestamp, level))


def run_llm_for_all(
    community_ids: list,
    timestamp: str,
    level: str,
    *,
    resume: bool = True,
) -> dict:
    """Run LLM per community, checkpointing each result so a crash can resume."""
    done = load_checkpoint(timestamp, level) if resume else {}
    todo = [jid for jid in community_ids if jid not in done]
    log.info(
        "Running LLM for %d %s communities (%d from checkpoint, %d to call)...",
        len(community_ids),
        level,
        len(done),
        len(todo),
    )

    llm_results = {jid: done[jid] for jid in community_ids if jid in done}
    used_labels = set()
    for res in llm_results.values():
        used_labels.update(extract_labels_from_result(res))

    for i, jid in enumerate(todo):
        jname = community_names.get(jid, str(jid))
        brief = briefs[jid]

        if not (brief["l0_domains"] or brief["l1_clusters"] or brief["l1_singles"] or brief.get("l2_clusters")):
            log.warning("[%d/%d] %s — no candidates, skipping", i + 1, len(todo), jname)
            result = {"core": [], "bleed": [], "match_mode": "none",
                      "confidence": "low", "overall_reasoning": "no candidates",
                      "_journal_id": jid, "_journal_name": jname}
        else:
            log.info("[%d/%d] %s...", i + 1, len(todo), jname)
            # Option 1: Pass used_labels to help LLM avoid duplicates
            result = call_llm(jid, jname, brief, used_labels=used_labels)

        llm_results[jid] = result
        append_checkpoint(timestamp, level, result)
        used_labels.update(extract_labels_from_result(result))

    log.info("Pass 1 complete for %d communities", len(llm_results))
    
    # Option 4: Detect duplicates and retry
    llm_results = resolve_duplicates(llm_results, community_ids)
    rewrite_checkpoint(timestamp, level, llm_results)

    return llm_results


def filter_brief_candidates(brief: dict, taken_labels: set) -> dict:
    """Create a copy of brief with taken labels removed from candidates."""
    import copy
    filtered = copy.deepcopy(brief)
    
    taken_keys = {key for key, name in taken_labels}
    taken_names = {name for key, name in taken_labels}
    
    # Filter L0 domains
    if filtered.get("l0_domains"):
        filtered["l0_domains"] = [
            d for d in filtered["l0_domains"]
            if d.get("key") not in taken_keys and d.get("name") not in taken_names
        ]
    
    # Filter L1 clusters
    if filtered.get("l1_clusters"):
        filtered["l1_clusters"] = [
            c for c in filtered["l1_clusters"]
            if c.get("key") not in taken_keys and c.get("name") not in taken_names
        ]
    
    # Filter L1 singles
    if filtered.get("l1_singles"):
        filtered["l1_singles"] = [
            s for s in filtered["l1_singles"]
            if s.get("key") not in taken_keys and s.get("name") not in taken_names
        ]
    
    # Filter L2 clusters
    if filtered.get("l2_clusters"):
        filtered["l2_clusters"] = [
            c for c in filtered["l2_clusters"]
            if c.get("key") not in taken_keys and c.get("name") not in taken_names
        ]
    
    return filtered


def resolve_duplicates(llm_results: dict, community_ids: list) -> dict:
    """Option 4: Detect duplicate labels and re-run LLM for conflicts."""
    log.info("Checking for duplicate labels...")
    
    # Build label -> communities mapping (only for PRIMARY core label, rank 1)
    label_to_communities = {}
    for jid, res in llm_results.items():
        core_labels = res.get("core", [])
        if core_labels:
            # Only consider the FIRST (primary) core label
            sel = core_labels[0]
            key = sel.get("key", "")
            name = sel.get("name", "")
            if key and name:
                label_key = (key, name)
                if label_key not in label_to_communities:
                    label_to_communities[label_key] = []
                label_to_communities[label_key].append({
                    "jid": jid,
                    "jname": res.get("_journal_name", str(jid)),
                    "confidence": res.get("confidence", "low"),
                    "n_articles": profiles.get(jid, {}).get("n_articles", 0),
                })
    
    # Find duplicates
    duplicates = {k: v for k, v in label_to_communities.items() if len(v) > 1}
    
    if not duplicates:
        log.info("No duplicate labels found.")
        return llm_results
    
    log.info("Found %d duplicate labels, starting Pass 2 (retry with filtered candidates)...", len(duplicates))
    
    # For each duplicate, keep the best match (most articles) and retry the others
    retry_jids = set()
    for label, communities in duplicates.items():
        # Sort by article count descending - keep the largest
        communities.sort(key=lambda x: -x["n_articles"])
        keeper = communities[0]
        log.info("  Label '%s': keeping %s (%d articles), will retry %d others",
                 label[1], keeper["jname"], keeper["n_articles"], len(communities) - 1)
        for c in communities[1:]:
            retry_jids.add(c["jid"])
    
    if not retry_jids:
        return llm_results
    
    # Collect PRIMARY labels that are "taken" (not from retry candidates)
    taken_labels = set()
    for jid, res in llm_results.items():
        if jid not in retry_jids:
            core_labels = res.get("core", [])
            if core_labels:
                sel = core_labels[0]  # Only primary label
                key = sel.get("key", "")
                name = sel.get("name", "")
                if key and name:
                    taken_labels.add((key, name))
    
    # Retry with filtered candidates (taken labels physically removed)
    for i, jid in enumerate(sorted(retry_jids)):
        jname = community_names.get(jid, str(jid))
        original_brief = briefs[jid]
        
        # Filter out taken labels from candidates
        filtered_brief = filter_brief_candidates(original_brief, taken_labels)
        
        # Check if any candidates remain
        has_candidates = (
            filtered_brief.get("l0_domains") or 
            filtered_brief.get("l1_clusters") or 
            filtered_brief.get("l1_singles") or 
            filtered_brief.get("l2_clusters")
        )
        
        if not has_candidates:
            log.warning("  [Retry %d/%d] %s — no candidates left after filtering, keeping original", 
                       i + 1, len(retry_jids), jname)
            continue
        
        log.info("  [Retry %d/%d] %s (filtered: removed %d taken labels)...", 
                 i + 1, len(retry_jids), jname, len(taken_labels))
        llm_results[jid] = call_llm(jid, jname, filtered_brief, used_labels=taken_labels, force_unique=True)
        
        # Add new PRIMARY label to taken set for subsequent retries
        new_core = llm_results[jid].get("core", [])
        if new_core:
            sel = new_core[0]
            key = sel.get("key", "")
            name = sel.get("name", "")
            if key and name:
                taken_labels.add((key, name))
    
    log.info("Pass 2 complete. Retried %d communities.", len(retry_jids))
    return llm_results


def flatten_results(llm_results: dict, community_ids: list) -> pd.DataFrame:
    """Flatten LLM results to output DataFrame."""
    log.info("Flattening results...")
    output_rows = []
    
    for jid, res in llm_results.items():
        jname = community_names.get(jid, str(jid))
        total_arts = profiles.get(jid, {}).get("n_articles", 0)
        
        for tier in ["core", "bleed"]:
            for rank, sel in enumerate(res.get(tier, []), start=1):
                output_rows.append({
                    "cluster_id": int(jid),
                    "community_id": jid,
                    "community_name": jname,
                    "cluster_level": CLUSTER_LEVEL,
                    "n_community_papers": total_arts,
                    "tier": tier,
                    "cluster_rank": rank,
                    "cluster_key": sel.get("key", ""),
                    "cluster_name": sel.get("name", ""),
                    "taxonomy_level": sel.get("level", ""),
                    "match_mode": res.get("match_mode", ""),
                    "llm_confidence": res.get("confidence", ""),
                    "llm_rationale": sel.get("rationale", ""),
                    "llm_reasoning": res.get("overall_reasoning", ""),
                    "run_date": RUN_DATE,
                })
    
    df_out = pd.DataFrame(output_rows)
    log.info("Output: %d rows (%d communities)", len(df_out), df_out["community_id"].nunique())
    return df_out


def export_dashboard_labels(df_out: pd.DataFrame, cluster_level: str) -> tuple[Path, pd.DataFrame]:
    """Write {level}_labels.csv so build_unified_dashboard can load taxonomy names.

    Uses the top-ranked core taxonomy name per community as short_label.
    """
    if df_out.empty:
        raise ValueError("No taxonomy label rows to export")

    core = df_out[df_out["tier"] == "core"].copy()
    if core.empty:
        core = df_out.copy()
    core = core.sort_values(["community_id", "cluster_rank"])
    top = core.groupby("community_id", as_index=False).first()

    rows = []
    for _, r in top.iterrows():
        name = str(r.get("cluster_name") or "").strip()
        if not name:
            name = f"Cluster {int(r['community_id'])}"
        # Title Case for dashboard consistency with former GPT labels
        short = " ".join(
            w if w.isupper() else w.capitalize()
            for w in name.replace("_", " ").split()
        )
        bleed = df_out[
            (df_out["community_id"] == r["community_id"]) & (df_out["tier"] == "bleed")
        ].sort_values("cluster_rank")
        keywords = [str(x) for x in bleed["cluster_name"].dropna().tolist()[:10]]
        rows.append(
            {
                "short_label": short,
                "long_label": short,
                "keywords": repr(keywords),
                "summary": str(r.get("llm_reasoning") or ""),
                "wikipedia_page": "",
                "coverage_pct": "",
                "level": cluster_level,
                "cluster_id": int(r["community_id"]),
                "n_papers": int(r.get("n_community_papers") or 0),
                "taxonomy_key": str(r.get("cluster_key") or ""),
                "taxonomy_level": str(r.get("taxonomy_level") or ""),
                "match_mode": str(r.get("match_mode") or ""),
                "source": "taxonomy",
            }
        )

    out = pd.DataFrame(rows).sort_values("cluster_id")
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    path = OUTPUT_DIR / f"{cluster_level}_labels.csv"
    out.to_csv(path, index=False)
    log.info("Dashboard labels saved to %s (%d clusters)", path, len(out))
    return path, out


def ensure_label_dataset() -> None:
    """Create taxonomy_labelling in EU if it does not exist."""
    from google.cloud.exceptions import NotFound

    client = bigquery.Client(project=BQ_DEST_PROJECT, location=BQ_LOCATION)
    ds_id = f"{BQ_DEST_PROJECT}.{BQ_LABEL_DATASET}"
    try:
        client.get_dataset(ds_id)
        log.info("BigQuery dataset exists: %s", ds_id)
    except NotFound:
        ds = bigquery.Dataset(ds_id)
        ds.location = BQ_LOCATION
        client.create_dataset(ds, exists_ok=True)
        log.info("Created BigQuery dataset %s (%s)", ds_id, BQ_LOCATION)


def _upload_one_table(
    df: pd.DataFrame, fq: str, rel: str, level: str, replace_table: bool
) -> None:
    """Replace the rows for this level only, so earlier levels survive."""
    cols = bq_table_columns(fq, client=bq_src)
    if replace_table or cols is None or "classification_join_column" not in cols:
        mode = "replace"
    else:
        run_sql(
            f"DELETE FROM `{fq}` WHERE classification_join_column = '{level}'",
            client=bq_src,
        )
        mode = "append"
    pandas_gbq.to_gbq(
        df,
        rel,
        project_id=BQ_DEST_PROJECT,
        if_exists=mode,
        location=BQ_LOCATION,
    )
    log.info("  → BigQuery (%s, %s): %s", level, mode, fq)


def upload_labels_to_bigquery(
    df_out: pd.DataFrame,
    dashboard: pd.DataFrame,
    run_timestamp: str,
    level: str | None = None,
    *,
    replace_tables: bool = False,
) -> None:
    """Write one level into labels_dashboard_{ts} and labels_detail_{ts}."""
    pandas_gbq.context.location = BQ_LOCATION
    ensure_label_dataset()
    level = level or CLUSTER_LEVEL

    if df_out.empty or dashboard.empty:
        log.warning("Skipping BigQuery upload for %s — empty label frames", level)
        return

    dash = dashboard.copy()
    dash["cluster_id"] = dash["cluster_id"].astype("int64")
    dash["run_timestamp"] = run_timestamp
    dash["classification_join_column"] = dash["level"] if "level" in dash.columns else level
    front = ["cluster_id", "run_timestamp", "classification_join_column"]
    dash = dash[front + [c for c in dash.columns if c not in front]]

    long = df_out.copy()
    if "cluster_id" not in long.columns:
        long["cluster_id"] = long["community_id"]
    long["cluster_id"] = long["cluster_id"].astype("int64")
    long["run_timestamp"] = run_timestamp
    long["classification_join_column"] = (
        long["cluster_level"] if "cluster_level" in long.columns else level
    )
    long_front = ["cluster_id", "run_timestamp", "classification_join_column"]
    long = long[long_front + [c for c in long.columns if c not in long_front]]

    _upload_one_table(
        dash,
        bq_labels_dashboard(run_timestamp),
        f"{BQ_LABEL_DATASET}.labels_dashboard_{run_timestamp}",
        level,
        replace_tables,
    )
    _upload_one_table(
        long,
        bq_labels_detail(run_timestamp),
        f"{BQ_LABEL_DATASET}.labels_detail_{run_timestamp}",
        level,
        replace_tables,
    )
    log.info(
        "Join: classification_raw_%s.{level} = labels_dashboard_%s.cluster_id "
        "(filter classification_join_column / level)",
        run_timestamp,
        run_timestamp,
    )


def resolve_timestamp(timestamp: str | None = None) -> str:
    """Same id as classification_raw_{timestamp}: arg, then module, then env."""
    ts = (timestamp or RUN_TIMESTAMP or os.environ.get("RUN_TIMESTAMP") or "").strip()
    if not ts:
        raise ValueError(
            "Set timestamp: taxonomy_naming.main(timestamp), "
            "taxonomy_naming.RUN_TIMESTAMP = timestamp, "
            "or env RUN_TIMESTAMP (same value as the scope-drift run)."
        )
    return ts


def run_one_level(
    level: str,
    timestamp: str,
    *,
    replace_sample: bool = False,
    first_level: bool = False,
    resume: bool = True,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Label all clusters at one CWTS level (macro / meso / micro).

    Uploads this level to BigQuery before returning, so a failure in a later
    level cannot discard it.
    """
    global CLUSTER_LEVEL, profiles, briefs, df_scope, df_l1_sig, df_clusters_agg, df_l0_agg

    CLUSTER_LEVEL = _assert_level(level)
    profiles = {}
    briefs = {}
    df_scope = None
    df_l1_sig = None
    df_clusters_agg = None
    df_l0_agg = None

    log.info("=" * 60)
    log.info("Level: %s", level)
    log.info("=" * 60)

    comm_data = load_cluster_index(level)
    community_ids = comm_data["community_ids"]
    if not community_ids:
        log.warning("No %s clusters — skipping", level)
        return pd.DataFrame(), pd.DataFrame()

    id_table = materialize_cluster_sample(
        level, timestamp, replace_table=replace_sample
    )
    df_l2_counts = pull_taxonomy_scores(id_table, level)
    build_profiles(community_ids, id_table, level)
    aggregate_to_higher_levels(df_l2_counts)
    build_all_briefs(community_ids)
    llm_results = run_llm_for_all(community_ids, timestamp, level, resume=resume)
    df_out = flatten_results(llm_results, community_ids)

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    level_path = OUTPUT_DIR / f"cluster_taxonomy_labels_{level}.csv"
    df_out.to_csv(level_path, index=False)
    log.info("Saved to %s", level_path)
    _, dashboard = export_dashboard_labels(df_out, level)

    try:
        upload_labels_to_bigquery(
            df_out, dashboard, timestamp, level, replace_tables=first_level
        )
    except Exception:
        log.exception(
            "BigQuery upload for %s failed; CSV outputs were still written", level
        )
    return df_out, dashboard


def resolve_levels(levels=None) -> tuple[str, ...]:
    """Levels to label: arg, then env CLUSTER_LEVELS, then module default.

    Always ordered coarsest first (macro → meso → micro).
    """
    if isinstance(levels, str):
        levels = [levels]
    if not levels:
        env = os.environ.get("CLUSTER_LEVELS", "").strip()
        levels = [env] if env else None
    if not levels:
        levels = list(CLUSTER_LEVELS)
    # Accept "macro,meso", "macro meso", ("macro", "meso") and "all"
    parts = [
        p.strip().lower()
        for lv in levels
        for p in str(lv).replace(",", " ").split()
        if p.strip()
    ]
    if "all" in parts:
        parts = list(ALL_CLUSTER_LEVELS)
    chosen = {_assert_level(p) for p in parts}
    if not chosen:
        raise ValueError("No cluster levels selected")
    return tuple(lv for lv in ALL_CLUSTER_LEVELS if lv in chosen)


def main(timestamp: str | None = None, levels=None, *, resume: bool = True):
    """Run taxonomy naming for the selected cluster levels on one timestamp.

    Args:
        timestamp: Scope-drift run id (e.g. "20260818_090851"). Reads
            classification_raw_{timestamp} and writes labels_dashboard_{timestamp},
            labels_detail_{timestamp}, sample_pubs_{timestamp}. If omitted, uses
            taxonomy_naming.RUN_TIMESTAMP or env RUN_TIMESTAMP.
        levels: Cluster levels to label, e.g. ("macro", "meso"), "micro", or
            "all". Defaults to CLUSTER_LEVELS / env CLUSTER_LEVELS. Always run
            coarsest first, and each level is uploaded before the next starts.
        resume: Reuse per-cluster LLM checkpoints from an earlier attempt.
    """
    global TBL_CLASSIF, TBL_PUB_META, RUN_TIMESTAMP

    timestamp = resolve_timestamp(timestamp)
    run_levels = resolve_levels(levels)
    RUN_TIMESTAMP = timestamp
    os.environ["RUN_TIMESTAMP"] = timestamp

    TBL_CLASSIF = f"{BQ_SRC_PROJECT}.{BQ_SRC_DATASET}.classification_raw_{timestamp}"
    TBL_PUB_META = f"{BQ_SRC_PROJECT}.{BQ_SRC_DATASET}.pub_metadata_raw_{timestamp}"

    log.info("=" * 60)
    log.info("Taxonomy Naming Pipeline")
    log.info("Run timestamp: %s", timestamp)
    log.info("Cluster levels: %s", ", ".join(run_levels))
    log.info("Resume from checkpoints: %s", resume)
    log.info("=" * 60)

    init_clients()
    load_taxonomy()

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    detail_parts = []
    for i, level in enumerate(run_levels):
        # Only wipe shared tables on an explicit fresh run; otherwise each level
        # replaces just its own rows so separate invocations do not clobber.
        rebuild = (not resume) and i == 0
        df_level, _dashboard = run_one_level(
            level,
            timestamp,
            replace_sample=rebuild,
            first_level=rebuild,
            resume=resume,
        )
        if df_level is not None and not df_level.empty:
            detail_parts.append(df_level)
            core = df_level[df_level["tier"] == "core"]
            log.info(
                "%s: %d clusters labelled",
                level,
                core["community_id"].nunique() if len(core) else 0,
            )

    df_out = pd.concat(detail_parts, ignore_index=True) if detail_parts else pd.DataFrame()
    combined = OUTPUT_DIR / "cluster_taxonomy_labels.csv"
    df_out.to_csv(combined, index=False)
    log.info("Combined labels saved to %s", combined)

    log.info("=" * 60)
    log.info("Summary")
    log.info("=" * 60)
    if not df_out.empty and "tier" in df_out.columns:
        print(
            df_out[df_out["tier"] == "core"]
            .groupby(["cluster_level", "community_name"])["cluster_name"]
            .first()
            .to_string()
        )
    return df_out


if __name__ == "__main__":
    import argparse

    ap = argparse.ArgumentParser(description="CWTS cluster taxonomy naming")
    ap.add_argument(
        "timestamp",
        nargs="?",
        default=os.environ.get("RUN_TIMESTAMP", ""),
        help="Scope-drift run id, e.g. 20260818_090851",
    )
    ap.add_argument(
        "--levels",
        default=None,
        help=(
            "Comma-separated cluster levels, or 'all'. "
            f"Default: {','.join(CLUSTER_LEVELS)} (always coarsest first)"
        ),
    )
    ap.add_argument(
        "--fresh",
        action="store_true",
        help="Ignore LLM checkpoints and rebuild the shared BigQuery tables",
    )
    args = ap.parse_args()
    if not args.timestamp:
        ap.error(
            "Missing timestamp. Example: python taxonomy_naming.py 20260818_090851 "
            "--levels macro,meso"
        )
    main(args.timestamp, levels=args.levels, resume=not args.fresh)
