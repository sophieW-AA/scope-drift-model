"""
cwts_export.py
==============
Standalone script: pull the citation network from BigQuery, apply edge
weights (temporal decay + journal self-citation discount + optional
bibliographic coupling), then write the text files required by the
CWTS publicationclassification Java tool.

Optionally runs the CWTS Java classification and uploads results to BigQuery.

Output files:
    pubs.txt           — <int_pub_id>  <core_pub>
    pub_metadata.txt   — <int_id> <pub_id> <is_frontiers> <journal> <date> <title>
    cit_links.txt      — <int_pub_id1> <int_pub_id2> <weight>
    classification.txt — <int_id> <micro> <meso> <macro>  (if RUN_CLASSIFICATION=true)

Usage
-----
    python cwts_export.py
    OR nohup python cwts_export.py &
    OR nohup python cwts_export.py > nohup_out.log 2>&1 & AND tail -f nohup_out.log


Optional env vars (all have defaults):
    TOP_N_JOURNALS          int   default 5
    JOURNAL_IDS             str   comma-separated IDs, overrides TOP_N_JOURNALS
    START_YEAR              int   default 2021
    END_YEAR                int   default 2025
    NETWORK_MODE            str   "ego" | "full" | "global" (default "global")
    ENABLE_EDGE_WEIGHTS     bool  default true
    TEMPORAL_DECAY_TAU      float default 5.0
    SELF_CITE_JOURNAL_WEIGHT float default 0.5
    ENABLE_BC_EDGES         bool  default true
    BC_MIN_SHARED_REFS      int   default 3
    MAX_EXTERNAL_PAPERS     int   default 50000  (ego mode only)
    OUTPUT_DIR              str   default ./cwts_output

Classification env vars (when RUN_CLASSIFICATION=true):
    RUN_CLASSIFICATION      bool  default true
    CWTS_JAR_PATH           str   default publicationclassification.jar
    JAVA_HEAP_SIZE          str   default 350g
    CWTS_LARGEST_COMPONENT  str   default true
    CWTS_ITERATIONS         str   default 100
    CWTS_MICRO_RES          str   default 4e-4
    CWTS_MICRO_MIN_SIZE     str   default 200
    CWTS_MESO_RES           str   default 1e-6
    CWTS_MESO_MIN_SIZE      str   default 1000
    CWTS_MACRO_RES          str   default 5e-7
    CWTS_MACRO_MIN_SIZE     str   default 50000
"""

import logging
import math
import os
from collections import defaultdict
from pathlib import Path

import numpy as np
import pandas as pd
from google.cloud import bigquery

from datetime import datetime
import pandas_gbq


# ---------------------------------------------------------------------------
# Config — mirrors scope_drift_airak_global.py so results are comparable
# ---------------------------------------------------------------------------
BQ_PROJECT = "ocean-tech-adv-analytics-p-usr"
AIRAK_DATASET = "ocean-breeze-tier-1.airak"
pandas_gbq.context.location = "EU"
FRONTIERS_PUBLISHER_ID = 1563368095744

TOP_N_JOURNALS = int(os.environ.get("TOP_N_JOURNALS", "5"))  # these ones are test journals
# JOURNAL_IDS_OVERRIDE = os.environ.get(
#     "JOURNAL_IDS",
#     "1675037245440,1589137899520,2336462209024,2774548873217,120259084288,764504178688,1005022347264,558345748481",
# ).strip()

# this is every frontiers journal
JOURNAL_IDS_OVERRIDE = os.environ.get(
    "JOURNAL_IDS",
    "8589934592,17179869184,34359738368,42949672960,42949672961,51539607552,68719476736,103079215104,103079215105,120259084288,188978561024,188978561025,223338299392,231928233984,283467841536,300647710720,326417514496,343597383680,352187318272,386547056640,446676598784,446676598785,455266533376,463856467968,481036337152,489626271744,498216206336,532575944704,541165879296,549755813888,549755814587,558345748480,558345748481,601295421440,609885356032,618475290624,618475290625,635655159808,644245094400,695784701952,695784701953,704374636544,704374636545,764504178688,781684047872,781684047873,790273982464,798863917056,807453851648,807453851649,816043786240,824633720832,841813590016,876173328385,901943132724,910533066752,910533066753,936302870528,936302870529,944892805120,953482739712,979252543489,987842478080,987842478081,996432412673,1005022347264,1005022347265,1013612281856,1039382085632,1108101562368,1108101562369,1125281431552,1151051235328,1151051236101,1159641169920,1159641169921,1185410973696,1185410973697,1211180777472,1279900254208,1279900254209,1288490189606,1305670057984,1305670057985,1314259992576,1314259992577,1314259992578,1340029796352,1340029796353,1348619730944,1357209665536,1391569403904,1400159338496,1417339207680,1425929142272,1434519076864,1443109011456,1443109011457,1443109011458,1477468749824,1503238553600,1503238553601,1511828488192,1511828488193,1511828488196,1520418422784,1529008357376,1537598291968,1537598291969,1546188226560,1546188226561,1554778161152,1580547964928,1589137899520,1623497637888,1623497637889,1632087572480,1649267441665,1675037245440,1709396983808,1735166787584,1769526525952,1769526525953,1786706395136,1803886264320,1821066133504,1821066133505,1829656068096,1829656068097,1838246002688,1846835937280,1855425871872,1864015806464,1924145348608,1941325217792,1967095021568,1967095021569,1975684956160,1984274890752,2061584302080,2078764171264,2113123909632,2121713844224,2121713844225,2156073582592,2156073582593,2190433320960,2199023255552,2216203124736,2224793059328,2233382993920,2233382993921,2302102470656,2319282339840,2336462209024,2336462209025,2345052143616,2379411881984,2388001816576,2405181685760,2405181685761,2439541424128,2499670966272,2516850835456,2568390443008,2568390443009,2594160246784,2628519985152,2731599200256,2748779069440,2757369004032,2774548873216,2774548873217,2826088480769,2834678415360,2843268349952,2843268349953,2843268349954,2860448219136,2869038153728,2869038153729,2877628088320,2877628088321,2886218022912,2886218022913,2929167695872,2929167695873,2963527434240,2963527434241,2963527434242,2963527434243,2972117368832,2972117368834,3006477107200,3075196583936,3083786518528,3118146256896,3135326126080,3143916060672,3178275799040,3204045602816,3212635537408,3246995275776,3255585210368,3255585210369,3264175144960,3272765079552,3281355014144,3307124817920,3315714752512,3341484556288,3384434229248,3393024163840,3401614098432,3410204033024",
).strip()



START_YEAR = int(os.environ.get("START_YEAR", "2023"))
END_YEAR = int(os.environ.get("END_YEAR", "2026"))
RUN_TIMESTAMP = os.environ.get(
    "RUN_TIMESTAMP", datetime.now().strftime("%Y%m%d_%H%M%S")
)
YEAR_RANGE = (START_YEAR, END_YEAR)

NETWORK_MODE = os.environ.get("NETWORK_MODE", "global").strip().lower()
if NETWORK_MODE not in ("ego", "full", "global"):
    print(f"[WARNING] Unknown NETWORK_MODE '{NETWORK_MODE}', defaulting to 'full'")
    NETWORK_MODE = "full"

ENABLE_EDGE_WEIGHTS = os.environ.get("ENABLE_EDGE_WEIGHTS", "true").lower() in (
    "1",
    "true",
    "yes",
)
TEMPORAL_DECAY_TAU = float(os.environ.get("TEMPORAL_DECAY_TAU", "5.0"))
SELF_CITE_JOURNAL_WEIGHT = float(os.environ.get("SELF_CITE_JOURNAL_WEIGHT", "0.5"))
ENABLE_BC_EDGES = os.environ.get("ENABLE_BC_EDGES", "true").lower() in (
    "1",
    "true",
    "yes",
)
BC_MIN_SHARED_REFS = int(os.environ.get("BC_MIN_SHARED_REFS", "3"))
MAX_EXTERNAL_PAPERS = int(os.environ.get("MAX_EXTERNAL_PAPERS", "50000"))

OUTPUT_DIR = Path(os.environ.get("OUTPUT_DIR", "../cwts_output"))

# CWTS Classification (Java step) - set to true to run classification after export
RUN_CLASSIFICATION = os.environ.get("RUN_CLASSIFICATION", "true").lower() in (
    "1",
    "true",
    "yes",
)
CWTS_JAR_PATH = os.environ.get("CWTS_JAR_PATH", "publicationclassification.jar")

# Classification parameters (can be overridden via env vars)
CWTS_PARAMS = {
    "largest_component_only": os.environ.get("CWTS_LARGEST_COMPONENT", "false"),
    "iterations": os.environ.get("CWTS_ITERATIONS", "100"),
    "micro_resolution": os.environ.get("CWTS_MICRO_RES", "5e-3"),
    "micro_min_cluster_size": os.environ.get("CWTS_MICRO_MIN_SIZE", "1000"),
    "meso_resolution": os.environ.get("CWTS_MESO_RES", "5e-5"),
    "meso_min_cluster_size": os.environ.get("CWTS_MESO_MIN_SIZE", "5000"),
    "macro_resolution": os.environ.get("CWTS_MACRO_RES", "1e-5"),
    "macro_min_cluster_size": os.environ.get("CWTS_MACRO_MIN_SIZE", "2000"),
}
# Java heap size - set to empty string "" to disable (e.g. JAVA_HEAP_SIZE="")
JAVA_HEAP_SIZE = os.environ.get("JAVA_HEAP_SIZE", "")

LOG_DIR = Path("../cwts_logs")
LOG_DIR.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(
            LOG_DIR / f"cwts_export{RUN_TIMESTAMP}.log",
            mode="w",
        ),
        logging.StreamHandler(),
    ],
)
log = logging.getLogger(__name__)
log.info("=" * 60)
log.info("Configuration")
log.info("=" * 60)
log.info(f"  BQ_PROJECT              : {BQ_PROJECT}")
log.info(f"  AIRAK_DATASET           : {AIRAK_DATASET}")
log.info(f"  NETWORK_MODE            : {NETWORK_MODE}")
log.info(f"  START_YEAR              : {START_YEAR}")
log.info(f"  END_YEAR                : {END_YEAR}")
log.info(f"  TOP_N_JOURNALS          : {TOP_N_JOURNALS}")
log.info(f"  JOURNAL_IDS_OVERRIDE    : {JOURNAL_IDS_OVERRIDE or '(none)'}")
log.info(f"  ENABLE_EDGE_WEIGHTS     : {ENABLE_EDGE_WEIGHTS}")
log.info(f"  TEMPORAL_DECAY_TAU      : {TEMPORAL_DECAY_TAU}")
log.info(f"  SELF_CITE_JOURNAL_WEIGHT: {SELF_CITE_JOURNAL_WEIGHT}")
log.info(f"  ENABLE_BC_EDGES         : {ENABLE_BC_EDGES}")
log.info(f"  BC_MIN_SHARED_REFS      : {BC_MIN_SHARED_REFS}")
log.info(f"  MAX_EXTERNAL_PAPERS     : {MAX_EXTERNAL_PAPERS}")
log.info(f"  OUTPUT_DIR              : {OUTPUT_DIR}")
log.info(f"  RUN_CLASSIFICATION      : {RUN_CLASSIFICATION}")
if RUN_CLASSIFICATION:
    log.info(f"  CWTS_JAR_PATH           : {CWTS_JAR_PATH}")
    log.info(f"  JAVA_HEAP_SIZE          : {JAVA_HEAP_SIZE}")
log.info("=" * 60)


# ---------------------------------------------------------------------------
# BigQuery helpers
# ---------------------------------------------------------------------------
def bq_client() -> bigquery.Client:
    return bigquery.Client(project=BQ_PROJECT)


def query_df(sql: str) -> pd.DataFrame:
    return bq_client().query(sql).to_dataframe()


# ---------------------------------------------------------------------------
# Step 1: Identify target Frontiers journals
# ---------------------------------------------------------------------------
def get_top_frontiers_journals(n: int) -> list[int]:
    log.info(f"Fetching top {n} Frontiers journals by publication count...")
    q = f"""
    SELECT j.JournalId
    FROM `{AIRAK_DATASET}.Publication` p
    JOIN `{AIRAK_DATASET}.Journal` j ON p.JournalId = j.JournalId
    WHERE j.PublisherId = {FRONTIERS_PUBLISHER_ID}
      AND p.PublishedYear BETWEEN {YEAR_RANGE[0]} AND {YEAR_RANGE[1]}
    GROUP BY j.JournalId, j.DisplayName
    ORDER BY COUNT(*) DESC
    LIMIT {n}
    """
    df = query_df(q)
    ids = df["JournalId"].tolist()
    log.info(f"  Journal IDs: {ids}")
    return ids


# ---------------------------------------------------------------------------
# Step 2: Frontiers publication IDs
# ---------------------------------------------------------------------------
def get_frontiers_pub_ids(journal_ids: list[int]) -> set[int]:
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
    log.info(f"  {len(pub_ids):,} Frontiers publications")
    return pub_ids


# ---------------------------------------------------------------------------
# Step 3a: Ego network edges (Frontiers papers + direct citations)
# ---------------------------------------------------------------------------
def get_ego_network_edges(frontiers_pub_ids: set[int]) -> tuple[pd.DataFrame, set[int]]:
    log.info(f"Building ego network (top {MAX_EXTERNAL_PAPERS:,} external papers)...")
    ids_list = list(frontiers_pub_ids)
    batch_size = 50_000
    all_edges = []

    for i in range(0, len(ids_list), batch_size):
        batch = ids_list[i : i + batch_size]
        ids_str = ",".join(str(x) for x in batch)
        batch_no = i // batch_size + 1
        n_batches = math.ceil(len(ids_list) / batch_size)
        log.info(f"  Ego batch {batch_no}/{n_batches}...")

        for direction, col_a, col_b in [
            ("outgoing", "PublicationId", "CitedPublicationId"),
            ("incoming", "CitedPublicationId", "PublicationId"),
        ]:
            q = f"""
            SELECT PublicationId AS src, CitedPublicationId AS tgt
            FROM `{AIRAK_DATASET}.PublicationCitation`
            WHERE {col_a} IN ({ids_str})
            """
            all_edges.append(query_df(q))

    df_edges = pd.concat(all_edges, ignore_index=True).drop_duplicates()
    log.info(f"  Raw edges: {len(df_edges):,}")

    # Keep only top MAX_EXTERNAL_PAPERS most-connected external nodes
    all_nodes = set(df_edges["src"]) | set(df_edges["tgt"])
    external_nodes = all_nodes - frontiers_pub_ids

    src_counts = df_edges["src"].value_counts()
    tgt_counts = df_edges["tgt"].value_counts()
    ext_src = src_counts[src_counts.index.isin(external_nodes)]
    ext_tgt = tgt_counts[tgt_counts.index.isin(external_nodes)]
    ext_counts = ext_src.add(ext_tgt, fill_value=0)

    top_external = set(ext_counts.nlargest(MAX_EXTERNAL_PAPERS).index)
    keep_nodes = frontiers_pub_ids | top_external
    df_filtered = df_edges[
        df_edges["src"].isin(keep_nodes) & df_edges["tgt"].isin(keep_nodes)
    ].copy()
    final_nodes = set(df_filtered["src"]) | set(df_filtered["tgt"])

    log.info(f"  Filtered: {len(df_filtered):,} edges, {len(final_nodes):,} nodes")
    return df_filtered, final_nodes


# ---------------------------------------------------------------------------
# Step 3a-bis: Global network edges (every paper published in the year range)
# ---------------------------------------------------------------------------
def get_global_network_edges(
    frontiers_pub_ids: set[int],
) -> tuple[pd.DataFrame, set[int]]:
    """All citation edges where both endpoints were published in YEAR_RANGE.

    No journal filter — this is the full publication graph for the window.
    Warning: can be very large; pair with a narrow year range (e.g. 2025-2025).
    """
    log.info(
        f"Building GLOBAL network for {YEAR_RANGE[0]}-{YEAR_RANGE[1]} "
        f"(every publication, no journal filter)..."
    )
    q = f"""
    SELECT pc.PublicationId AS src, pc.CitedPublicationId AS tgt
    FROM `{AIRAK_DATASET}.PublicationCitation` pc
    JOIN `{AIRAK_DATASET}.Publication` p1 ON pc.PublicationId      = p1.PublicationId
    JOIN `{AIRAK_DATASET}.Publication` p2 ON pc.CitedPublicationId = p2.PublicationId
    WHERE p1.PublishedYear BETWEEN {YEAR_RANGE[0]} AND {YEAR_RANGE[1]}
      AND p2.PublishedYear BETWEEN {YEAR_RANGE[0]} AND {YEAR_RANGE[1]}
    """
    df_edges = query_df(q).drop_duplicates()
    final_nodes = set(df_edges["src"]) | set(df_edges["tgt"])
    n_core = len(frontiers_pub_ids & final_nodes)
    log.info(
        f"  {len(df_edges):,} edges, {len(final_nodes):,} nodes "
        f"({n_core:,} Frontiers core)"
    )
    return df_edges, final_nodes


# ---------------------------------------------------------------------------
# Step 3b: Full network edges (Frontiers + related journals)
# ---------------------------------------------------------------------------
def get_full_network_edges(
    frontiers_pub_ids: set[int],
    journal_ids: list[int],
) -> tuple[pd.DataFrame, set[int], set[int]]:
    log.info("Building full network (Frontiers + related journals)...")
    ids_str = ",".join(str(x) for x in journal_ids)

    def find_related(direction_sql: str, label: str) -> pd.DataFrame:
        log.info(f"  Finding journals {label} Frontiers...")
        return query_df(direction_sql)

    q_citing = f"""
    SELECT j.JournalId
    FROM `{AIRAK_DATASET}.PublicationCitation` pc
    JOIN `{AIRAK_DATASET}.Publication` p1 ON pc.PublicationId      = p1.PublicationId
    JOIN `{AIRAK_DATASET}.Publication` p2 ON pc.CitedPublicationId = p2.PublicationId
    JOIN `{AIRAK_DATASET}.Journal`     j  ON p1.JournalId          = j.JournalId
    WHERE p2.JournalId IN ({ids_str})
      AND p1.PublishedYear BETWEEN {YEAR_RANGE[0]} AND {YEAR_RANGE[1]}
      AND p2.PublishedYear BETWEEN {YEAR_RANGE[0]} AND {YEAR_RANGE[1]}
      AND p1.JournalId NOT IN ({ids_str})
    GROUP BY j.JournalId
    HAVING COUNT(*) >= 50
    """

    q_cited = f"""
    SELECT j.JournalId
    FROM `{AIRAK_DATASET}.PublicationCitation` pc
    JOIN `{AIRAK_DATASET}.Publication` p1 ON pc.PublicationId      = p1.PublicationId
    JOIN `{AIRAK_DATASET}.Publication` p2 ON pc.CitedPublicationId = p2.PublicationId
    JOIN `{AIRAK_DATASET}.Journal`     j  ON p2.JournalId          = j.JournalId
    WHERE p1.JournalId IN ({ids_str})
      AND p1.PublishedYear BETWEEN {YEAR_RANGE[0]} AND {YEAR_RANGE[1]}
      AND p2.PublishedYear BETWEEN {YEAR_RANGE[0]} AND {YEAR_RANGE[1]}
      AND p2.JournalId NOT IN ({ids_str})
    GROUP BY j.JournalId
    HAVING COUNT(*) >= 50
    """

    df_citing = find_related(q_citing, "citing")
    df_cited_by = find_related(q_cited, "cited by")
    related_ids = set(df_citing["JournalId"].tolist()) | set(
        df_cited_by["JournalId"].tolist()
    )
    all_j_ids = related_ids | set(journal_ids)
    all_j_str = ",".join(str(x) for x in all_j_ids)
    log.info(
        f"  {len(all_j_ids)} journals in network ({len(related_ids)} related + {len(journal_ids)} Frontiers)"
    )

    # All publications from those journals
    q_pubs = f"""
    SELECT PublicationId
    FROM `{AIRAK_DATASET}.Publication`
    WHERE JournalId IN ({all_j_str})
      AND PublishedYear BETWEEN {YEAR_RANGE[0]} AND {YEAR_RANGE[1]}
    """
    all_pub_ids = set(query_df(q_pubs)["PublicationId"].tolist())
    log.info(f"  {len(all_pub_ids):,} publications")

    # Citation edges between those publications (batched)
    pub_list = list(all_pub_ids)
    batch_sz = 50_000
    all_edges = []
    n_batches = math.ceil(len(pub_list) / batch_sz)

    for i in range(0, len(pub_list), batch_sz):
        batch = pub_list[i : i + batch_sz]
        batch_str = ",".join(str(x) for x in batch)
        log.info(f"  Citation batch {i // batch_sz + 1}/{n_batches}...")
        q = f"""
        SELECT pc.PublicationId AS src, pc.CitedPublicationId AS tgt
        FROM `{AIRAK_DATASET}.PublicationCitation` pc
        JOIN `{AIRAK_DATASET}.Publication` p ON pc.CitedPublicationId = p.PublicationId
        WHERE pc.PublicationId IN ({batch_str})
          AND p.JournalId IN ({all_j_str})
          AND p.PublishedYear BETWEEN {YEAR_RANGE[0]} AND {YEAR_RANGE[1]}
        """
        all_edges.append(query_df(q))

    df_edges = pd.concat(all_edges, ignore_index=True).drop_duplicates()
    final_nodes = set(df_edges["src"]) | set(df_edges["tgt"])
    log.info(f"  {len(df_edges):,} edges, {len(final_nodes):,} nodes")
    return df_edges, final_nodes, all_j_ids


# ---------------------------------------------------------------------------
# Step 4: Node metadata
# ---------------------------------------------------------------------------
def get_node_metadata(
    node_ids: set[int], frontiers_journal_ids: list[int]
) -> pd.DataFrame:
    log.info(f"Fetching metadata for {len(node_ids):,} nodes...")
    ids_list = list(node_ids)
    batch_sz = 20_000
    n_batches = math.ceil(len(ids_list) / batch_sz)
    j_ids_str = ",".join(str(x) for x in frontiers_journal_ids)
    all_meta = []

    for i in range(0, len(ids_list), batch_sz):
        batch = ids_list[i : i + batch_sz]
        ids_str = ",".join(str(x) for x in batch)
        log.info(f"  Metadata batch {i // batch_sz + 1}/{n_batches}...")
        q = f"""
        SELECT
          p.PublicationId,
          p.Title,
          p.PublishedYear,
          p.PublishedDate,
          j.JournalId,
          j.DisplayName as JournalName,
          CASE WHEN j.JournalId IN ({j_ids_str}) THEN TRUE ELSE FALSE END AS IsFrontiers
        FROM `{AIRAK_DATASET}.Publication` p
        LEFT JOIN `{AIRAK_DATASET}.Journal` j ON p.JournalId = j.JournalId
        WHERE p.PublicationId IN ({ids_str})
        """
        all_meta.append(query_df(q))

    df_meta = pd.concat(all_meta, ignore_index=True)
    n_core = int(df_meta["IsFrontiers"].sum())
    log.info(f"  {len(df_meta):,} nodes ({n_core:,} Frontiers core)")
    return df_meta.set_index("PublicationId")


# ---------------------------------------------------------------------------
# Step 5a: Temporal decay + self-citation discount
# ---------------------------------------------------------------------------
def apply_edge_weights(
    df_edges: pd.DataFrame, node_lookup: pd.DataFrame
) -> pd.DataFrame:
    log.info("Applying edge weights (temporal decay + self-citation discount)...")
    end_year = YEAR_RANGE[1]

    pub_years = node_lookup["PublishedYear"].fillna(end_year).to_dict()
    pub_journals = node_lookup["JournalId"].to_dict()

    df = df_edges.copy()
    df["tgt_year"] = df["tgt"].map(pub_years).fillna(end_year)
    df["src_journal"] = df["src"].map(pub_journals)
    df["tgt_journal"] = df["tgt"].map(pub_journals)

    # Temporal decay on cited paper age
    df["decay"] = np.exp(-(end_year - df["tgt_year"]) / TEMPORAL_DECAY_TAU).clip(
        lower=0.01
    )

    # Journal self-citation discount
    same_journal = (
        df["src_journal"].notna()
        & df["tgt_journal"].notna()
        & (df["src_journal"] == df["tgt_journal"])
    )
    df["self_factor"] = np.where(same_journal, SELF_CITE_JOURNAL_WEIGHT, 1.0)
    df["weight"] = (df["decay"] * df["self_factor"]).clip(lower=0.01)

    log.info(
        f"  Decay mean={df['decay'].mean():.3f}  |  Self-citations: {same_journal.sum():,}"
    )
    log.info(f"  Combined weight mean={df['weight'].mean():.3f}")
    return df[["src", "tgt", "weight"]]


# ---------------------------------------------------------------------------
# Step 5b: Bibliographic coupling edges
# ---------------------------------------------------------------------------
def get_bc_edges(
    frontiers_pub_ids: set[int], all_journal_ids: set[int]
) -> pd.DataFrame:
    if not ENABLE_BC_EDGES:
        log.info("BC edges disabled (ENABLE_BC_EDGES=false)")
        return pd.DataFrame(columns=["src", "tgt", "weight"])

    log.info(
        f"Computing bibliographic coupling (min shared refs={BC_MIN_SHARED_REFS})..."
    )
    j_ids_str = ",".join(str(x) for x in all_journal_ids)
    fr_list = list(frontiers_pub_ids)
    batch_sz = 20_000
    n_batches = math.ceil(len(fr_list) / batch_sz)
    all_bc = []

    for i in range(0, len(fr_list), batch_sz):
        batch = fr_list[i : i + batch_sz]
        fr_str = ",".join(str(x) for x in batch)
        log.info(f"  BC batch {i // batch_sz + 1}/{n_batches}...")
        q = f"""
        WITH frontiers_refs AS (
          SELECT PublicationId, CitedPublicationId
          FROM `{AIRAK_DATASET}.PublicationCitation`
          WHERE PublicationId IN ({fr_str})
        ),
        network_refs AS (
          SELECT pc.PublicationId, pc.CitedPublicationId
          FROM `{AIRAK_DATASET}.PublicationCitation` pc
          JOIN `{AIRAK_DATASET}.Publication` p ON pc.PublicationId = p.PublicationId
          WHERE p.JournalId IN ({j_ids_str})
            AND p.PublishedYear BETWEEN {YEAR_RANGE[0]} AND {YEAR_RANGE[1]}
        ),
        ref_counts_fr AS (
          SELECT PublicationId, COUNT(*) AS ref_count
          FROM `{AIRAK_DATASET}.PublicationCitation`
          WHERE PublicationId IN ({fr_str})
          GROUP BY PublicationId
        ),
        ref_counts_net AS (
          SELECT pc.PublicationId, COUNT(*) AS ref_count
          FROM `{AIRAK_DATASET}.PublicationCitation` pc
          JOIN `{AIRAK_DATASET}.Publication` p ON pc.PublicationId = p.PublicationId
          WHERE p.JournalId IN ({j_ids_str})
            AND p.PublishedYear BETWEEN {YEAR_RANGE[0]} AND {YEAR_RANGE[1]}
          GROUP BY pc.PublicationId
        )
        SELECT
          fr.PublicationId AS src,
          nr.PublicationId AS tgt,
          SAFE_DIVIDE(
            CAST(COUNT(*) AS FLOAT64),
            SQRT(CAST(rc_src.ref_count AS FLOAT64) * CAST(rc_tgt.ref_count AS FLOAT64))
          ) AS weight
        FROM frontiers_refs fr
        JOIN network_refs   nr  ON fr.CitedPublicationId = nr.CitedPublicationId
                                AND fr.PublicationId    != nr.PublicationId
        JOIN ref_counts_fr  rc_src ON rc_src.PublicationId = fr.PublicationId
        JOIN ref_counts_net rc_tgt ON rc_tgt.PublicationId = nr.PublicationId
        GROUP BY fr.PublicationId, nr.PublicationId, rc_src.ref_count, rc_tgt.ref_count
        HAVING COUNT(*) >= {BC_MIN_SHARED_REFS}
        """
        df_bc = query_df(q)
        if len(df_bc):
            all_bc.append(df_bc)
        log.info(f"    {len(df_bc):,} BC edges")

    if not all_bc:
        return pd.DataFrame(columns=["src", "tgt", "weight"])

    result = pd.concat(all_bc, ignore_index=True).drop_duplicates(subset=["src", "tgt"])
    result["weight"] = result["weight"].fillna(0).clip(upper=1.0)
    log.info(f"  Total BC edges: {len(result):,}")
    return result[["src", "tgt", "weight"]]


# ---------------------------------------------------------------------------
# Step 5c: Merge direct + BC edge lists
# ---------------------------------------------------------------------------
def merge_edges(df_direct: pd.DataFrame, df_bc: pd.DataFrame) -> pd.DataFrame:
    log.info("Merging direct citation and BC edges...")

    def normalise(df: pd.DataFrame) -> pd.DataFrame:
        mask = df["src"] > df["tgt"]
        out = df.copy()
        out.loc[mask, ["src", "tgt"]] = out.loc[mask, ["tgt", "src"]].values
        return out

    merged = (
        pd.concat([normalise(df_direct), normalise(df_bc)], ignore_index=True)
        .groupby(["src", "tgt"], as_index=False)["weight"]
        .sum()
    )
    merged["weight"] = merged["weight"].clip(upper=2.0)
    log.info(
        f"  Merged: {len(merged):,} edges (mean weight={merged['weight'].mean():.3f})"
    )
    return merged


# Step 6: Upload CWTS tables to BigQuery
# ---------------------------------------------------------------------------
BQ_DEST_PROJECT = "ocean-tech-adv-analytics-c-tfs"
BQ_DEST_DATASET = "raw_citation_network_data"


# ---------------------------------------------------------------------------
# Step 6: Write CWTS input files (text files + BigQuery upload)
# ---------------------------------------------------------------------------
def write_cwts_files(
    df_edges: pd.DataFrame,
    final_nodes: set[int],
    node_lookup: pd.DataFrame,
    upload_to_bq: bool = True,
) -> None:
    """
    Write CWTS output files and optionally upload to BigQuery.

    Outputs:
      1. pubs.txt - int_id, core_pub (always 1)
      2. pub_metadata.txt - int_id, pub_id, is_frontiers, journal, date, title
      3. cit_links.txt - int_id1, int_id2, weight (edges in both directions)
    """
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    sorted_pids = sorted(final_nodes)
    pid_to_int = {pid: i for i, pid in enumerate(sorted_pids)}
    timestamp = RUN_TIMESTAMP

    log.info(f"Writing CWTS files to {OUTPUT_DIR}/  ({len(sorted_pids):,} nodes)...")

    # Convert DataFrame to dictionary for O(1) row access in loop
    node_dict = node_lookup.to_dict("index")

    # ═══════════════════════════════════════════════════════════════════════
    # 1. pubs.txt
    # ═══════════════════════════════════════════════════════════════════════
    pubs_df = pd.DataFrame(
        {"int_id": [pid_to_int[pid] for pid in sorted_pids], "core_pub": 1}
    )

    # Write text file
    pubs_path = OUTPUT_DIR / "pubs.txt"
    pubs_df.to_csv(pubs_path, sep="\t", index=False, header=False)
    n_core = sum(1 for pid in sorted_pids if node_dict.get(pid, {}).get("IsFrontiers"))
    log.info(f"  pubs.txt        : {len(pubs_df):,} rows  ({n_core:,} Frontiers)")

    # Upload to BigQuery
    if upload_to_bq:
        pandas_gbq.to_gbq(
            pubs_df,
            f"{BQ_DEST_DATASET}.pubs_raw_{timestamp}",
            project_id=BQ_DEST_PROJECT,
            if_exists="replace",
        )
        log.info(f"  → BigQuery: {BQ_DEST_DATASET}.pubs_raw_{timestamp}")

    # ═══════════════════════════════════════════════════════════════════════
    # 2. pub_metadata.txt
    # ═══════════════════════════════════════════════════════════════════════
    meta_rows = []
    for pid in sorted_pids:
        m = node_dict.get(pid, {})
        meta_rows.append(
            {
                "int_id": pid_to_int[pid],
                "pub_id": pid,
                "is_frontiers": 1 if m.get("IsFrontiers") else 0,
                "journal": (
                    str(m.get("JournalName") or m.get("JournalId") or "")
                    .replace("\t", " ")
                    .strip()
                ),
                "date": str(
                    m.get("PublishedDate") or m.get("PublishedYear") or ""
                ).strip()
                or "0000-01-01",
                "title": str(m.get("Title") or "")
                .replace("\t", " ")
                .replace("\n", " ")
                .strip(),
            }
        )
    pub_metadata_df = pd.DataFrame(meta_rows)

    # Write text file
    meta_path = OUTPUT_DIR / "pub_metadata.txt"
    pub_metadata_df.to_csv(
        meta_path, sep="\t", index=False, header=False, encoding="utf-8"
    )
    log.info(f"  pub_metadata.txt: {len(pub_metadata_df):,} rows")

    # Upload to BigQuery
    if upload_to_bq:
        pandas_gbq.to_gbq(
            pub_metadata_df,
            f"{BQ_DEST_DATASET}.pub_metadata_raw_{timestamp}",
            project_id=BQ_DEST_PROJECT,
            if_exists="replace",
        )

        log.info(f"  → BigQuery: {BQ_DEST_DATASET}.pub_metadata_raw_{timestamp}")

    # ═══════════════════════════════════════════════════════════════════════
    # 3. cit_links.txt
    # ═══════════════════════════════════════════════════════════════════════
    df = df_edges.copy()
    df["src_int"] = df["src"].map(pid_to_int)
    df["tgt_int"] = df["tgt"].map(pid_to_int)
    df = df.dropna(subset=["src_int", "tgt_int"])
    df[["src_int", "tgt_int"]] = df[["src_int", "tgt_int"]].astype(int)

    # Dedupe undirected pairs (src < tgt), sum weights
    swap = df["src_int"] > df["tgt_int"]
    df.loc[swap, ["src_int", "tgt_int"]] = df.loc[swap, ["tgt_int", "src_int"]].values
    df = df[df["src_int"] != df["tgt_int"]]
    df = df.groupby(["src_int", "tgt_int"], as_index=False)["weight"].sum()

    # Both directions (A→B and B→A)
    df_rev = df.rename(columns={"src_int": "tgt_int", "tgt_int": "src_int"})
    cit_links_df = (
        pd.concat([df, df_rev[["src_int", "tgt_int", "weight"]]], ignore_index=True)
        .sort_values(["src_int", "tgt_int"])
        .reset_index(drop=True)
    )

    # Write text file
    links_path = OUTPUT_DIR / "cit_links.txt"
    cit_links_df.to_csv(
        links_path, sep="\t", index=False, header=False, float_format="%.6f"
    )
    log.info(
        f"  cit_links.txt   : {len(cit_links_df):,} rows  ({len(df):,} unique × 2 directions)"
    )

    # Upload to BigQuery
    if upload_to_bq:
        cit_links_bq = cit_links_df.rename(
            columns={"src_int": "int_id1", "tgt_int": "int_id2"}
        )
        pandas_gbq.to_gbq(
            cit_links_bq,
            f"{BQ_DEST_DATASET}.cit_links_raw_{timestamp}",
            project_id=BQ_DEST_PROJECT,
            if_exists="replace",
        )
        log.info(f"  → BigQuery: {BQ_DEST_DATASET}.cit_links_raw_{timestamp}")


# ---------------------------------------------------------------------------
# Step 7: Run CWTS Java Classification
# ---------------------------------------------------------------------------
def run_cwts_classification() -> bool:
    """
    Run the CWTS Java classification tool to generate micro/meso/macro clusters.

    Returns True if classification succeeded, False otherwise.
    """
    import subprocess

    pubs_path = OUTPUT_DIR / "pubs.txt"
    cit_links_path = OUTPUT_DIR / "cit_links.txt"
    classification_path = OUTPUT_DIR / "classification.txt"

    if not Path(CWTS_JAR_PATH).exists():
        log.error(f"CWTS JAR not found at: {CWTS_JAR_PATH}")
        return False

    log.info("=" * 60)
    log.info("Running CWTS Classification")
    log.info("=" * 60)
    log.info(f"  JAR: {CWTS_JAR_PATH}")
    if JAVA_HEAP_SIZE:
        log.info(f"  Java heap: -Xmx{JAVA_HEAP_SIZE}")
    log.info(f"  Parameters:")
    for k, v in CWTS_PARAMS.items():
        log.info(f"    {k}: {v}")

    # Build command - only add heap flag if specified
    cmd = ["java"]
    if JAVA_HEAP_SIZE:
        cmd.append(f"-Xmx{JAVA_HEAP_SIZE}")
    cmd.extend(
        [
            "-cp",
            CWTS_JAR_PATH,
            "nl.cwts.publicationclassification.run.PublicationClassificationCreator",
            str(pubs_path),
            str(cit_links_path),
            str(classification_path),
            CWTS_PARAMS["largest_component_only"],
            CWTS_PARAMS["iterations"],
            CWTS_PARAMS["micro_resolution"],
            CWTS_PARAMS["micro_min_cluster_size"],
            CWTS_PARAMS["meso_resolution"],
            CWTS_PARAMS["meso_min_cluster_size"],
            CWTS_PARAMS["macro_resolution"],
            CWTS_PARAMS["macro_min_cluster_size"],
        ]
    )

    log.info(f"  Running command...")
    result = subprocess.run(cmd, capture_output=True, text=True)

    # Log output
    log_path = LOG_DIR / f"cwts_classification_{RUN_TIMESTAMP}.log"
    with open(log_path, "w") as f:
        f.write(f"CWTS Publication Classification\n")
        f.write(f"{'='*50}\n")
        f.write(f"Timestamp: {RUN_TIMESTAMP}\n\n")
        f.write(f"Parameters\n{'-'*30}\n")
        for k, v in CWTS_PARAMS.items():
            f.write(f"  {k:<26}: {v}\n")
        f.write(f"\nReturn Code: {result.returncode}\n")
        f.write(f"\nSTDOUT\n{'-'*30}\n")
        f.write(result.stdout or "(empty)\n")
        f.write(f"\nSTDERR\n{'-'*30}\n")
        f.write(result.stderr or "(empty)\n")

    log.info(f"  Log written to: {log_path}")

    if result.returncode != 0:
        log.error(f"  Classification failed with return code {result.returncode}")
        if result.stderr:
            log.error(f"  STDERR: {result.stderr[:500]}")
        return False

    if result.stdout:
        log.info(f"  STDOUT: {result.stdout[:200]}...")

    log.info(f"  Classification complete: {classification_path}")
    return True


def upload_classification_to_bigquery() -> None:
    """Upload classification.txt to BigQuery."""
    classification_path = OUTPUT_DIR / "classification.txt"

    if not classification_path.exists():
        log.error(f"Classification file not found: {classification_path}")
        return

    log.info("Uploading classification to BigQuery...")

    classification_df = pd.read_csv(
        classification_path,
        sep="\t",
        header=None,
        names=["int_id", "micro", "meso", "macro"],
    )

    log.info(f"  Loaded {len(classification_df):,} rows")
    log.info(f"  Micro clusters: {classification_df['micro'].nunique():,}")
    log.info(f"  Meso clusters:  {classification_df['meso'].nunique():,}")
    log.info(f"  Macro clusters: {classification_df['macro'].nunique():,}")

    pandas_gbq.to_gbq(
        classification_df,
        f"{BQ_DEST_DATASET}.classification_raw_{RUN_TIMESTAMP}",
        project_id=BQ_DEST_PROJECT,
        if_exists="replace",
    )
    log.info(f"  → BigQuery: {BQ_DEST_DATASET}.classification_raw_{RUN_TIMESTAMP}")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    try:
        log.info("=" * 60)
        log.info("CWTS Export — Edge Weight Builder")
        log.info(
            f"  Mode: {NETWORK_MODE.upper()}  |  Years: {YEAR_RANGE[0]}-{YEAR_RANGE[1]}"
        )
        log.info(f"  Edge weights: {'ON' if ENABLE_EDGE_WEIGHTS else 'OFF'}")
        log.info("=" * 60)

        # Step 1: journals
        if JOURNAL_IDS_OVERRIDE:
            journal_ids = [
                int(x.strip()) for x in JOURNAL_IDS_OVERRIDE.split(",") if x.strip()
            ]
            log.info(f"Using specified journal IDs: {journal_ids}")
        else:
            journal_ids = get_top_frontiers_journals(TOP_N_JOURNALS)

        # Step 2: Frontiers pub IDs
        frontiers_pub_ids = get_frontiers_pub_ids(journal_ids)

        # Step 3: Citation network
        all_journal_ids = set(journal_ids)
        if NETWORK_MODE == "full":
            df_edges, final_nodes, all_journal_ids = get_full_network_edges(
                frontiers_pub_ids, journal_ids
            )
        elif NETWORK_MODE == "global":
            df_edges, final_nodes = get_global_network_edges(frontiers_pub_ids)
            # No bounded journal set in global mode — BC's `JournalId IN (...)`
            # filter would be meaningless and the cross-join would explode.
            if ENABLE_BC_EDGES:
                log.warning(
                    "Global mode: disabling bibliographic-coupling edges "
                    "(no journal scope; query would be unbounded)."
                )
                globals()["ENABLE_BC_EDGES"] = False
        else:
            df_edges, final_nodes = get_ego_network_edges(frontiers_pub_ids)

        # Step 4: Node metadata (year + journal — needed for weights)
        node_lookup = get_node_metadata(final_nodes, journal_ids)

        # Step 5: Edge weights
        if ENABLE_EDGE_WEIGHTS:
            df_edges = apply_edge_weights(df_edges, node_lookup)
            df_bc = get_bc_edges(frontiers_pub_ids, all_journal_ids)
            if len(df_bc):
                df_edges = merge_edges(df_edges, df_bc)
        else:
            log.info("Edge weighting disabled — using weight=1.0")
            df_edges["weight"] = 1.0

        # Step 6: Write files
        write_cwts_files(df_edges, final_nodes, node_lookup)

        # Step 7: Run CWTS classification (if enabled)
        if RUN_CLASSIFICATION:
            classification_success = run_cwts_classification()
            if classification_success:
                upload_classification_to_bigquery()
        else:
            log.info("Classification step skipped (RUN_CLASSIFICATION=false)")

        # Step 8: Save run metadata to BigQuery for dashboards
        import json

        metadata_row = {
            "run_timestamp": RUN_TIMESTAMP,
            "generated_utc": datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC"),
            "bq_source_project": BQ_PROJECT,
            "bq_source_dataset": AIRAK_DATASET,
            "network_mode": NETWORK_MODE,
            "start_year": START_YEAR,
            "end_year": END_YEAR,
            "top_n_journals": TOP_N_JOURNALS,
            "journal_ids": json.dumps(journal_ids),
            "edge_weighting_enabled": ENABLE_EDGE_WEIGHTS,
            "temporal_decay_tau": TEMPORAL_DECAY_TAU,
            "self_cite_journal_weight": SELF_CITE_JOURNAL_WEIGHT,
            "bc_edges_enabled": ENABLE_BC_EDGES,
            "bc_min_shared_refs": BC_MIN_SHARED_REFS,
            "total_nodes": len(final_nodes),
            "total_edges": len(df_edges),
        }
        metadata_df = pd.DataFrame([metadata_row])
        pandas_gbq.to_gbq(
            metadata_df,
            f"{BQ_DEST_DATASET}.run_metadata_{RUN_TIMESTAMP}",
            project_id=BQ_DEST_PROJECT,
            if_exists="replace",
        )
        log.info(f"  → BigQuery: {BQ_DEST_DATASET}.run_metadata_{RUN_TIMESTAMP}")

    except Exception as e:
        log.exception("An error occurred during execution of the CWTS export:")
        raise e
    log.info("Done!!!!")


if __name__ == "__main__":
    main()
