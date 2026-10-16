"""
Assign Frontiers papers that Leiden did not classify.

Leiden stays the citation clustering. This step appends the missing Frontiers
papers to classification_raw_{timestamp} and records who placed each row:

    assignment_method   leiden | taxonomy | unassigned

Profiles are fit on Leiden papers only, using Frontiers taxonomy v6
(CORE_TOPIC, score level 3). A paper is placed at micro, then meso, then
macro, and only as deep as the calibrated similarity and margin allow.

Nothing is written unless --write is passed. main.py only does that when
--taxonomy-enrichment is set.

    python src/taxonomy_assignment.py --timestamp 20260827_081311 --audit
    python src/taxonomy_assignment.py --timestamp 20260827_081311 --calibrate
    python src/taxonomy_assignment.py --timestamp 20260827_081311
    python src/taxonomy_assignment.py --timestamp 20260827_081311 --write
"""

from __future__ import annotations

import argparse
import logging
import os
import re
import sys
from pathlib import Path

import pandas as pd
from google.cloud import bigquery

try:
    from dotenv import load_dotenv
except ImportError:  # pragma: no cover - dotenv is a project dependency
    load_dotenv = None

REPO = Path(__file__).resolve().parent.parent
if load_dotenv is not None:
    load_dotenv(REPO / ".env", override=True)

BQ_BILL_PROJECT = "ocean-tech-adv-analytics-c-esf"
BQ_PROJECT = "ocean-tech-adv-analytics-c-tfs"
BQ_DATASET = "raw_citation_network_data"
BQ_LOCATION = "EU"
AIRAK_PUBLICATION = "ocean-breeze-tier-1.airak.Publication"
AIRAK_JOURNAL = "ocean-breeze-tier-1.airak.Journal"
TAXONOMY_DATASET = "ocean-tech-adv-analytics-c-esf.fw_taxonomy"
# Base table, not the current view. The view hides the publication_id cluster,
# so a join through it scans every score row.
TBL_SCORES = f"{TAXONOMY_DATASET}.article_taxonomy_scores"
SCORE_VERSION = "6"
TBL_TAXONOMY = f"{TAXONOMY_DATASET}.flat_taxonomy"
TOPIC_AXIS = "CORE_TOPIC"
SCORE_LEVEL = 3

# Profiles use a stable sample of Leiden papers. The score table is clustered
# on publication_id, so the sample is what gets joined, not the whole network.
PROFILE_PAPERS = 250
PROFILE_TOPICS = 30
CALIBRATION_PER_MACRO = 25
TS_RE = re.compile(r"^\d{8}_\d{6}$")

# Operating points from the 20260827_081311 holdout (25 low-degree Frontiers
# papers per macro, 475 papers, median degree 1).
# Macro similarity >= 0.15 and margin >= 0.02: 77.8% precision, 27 accepted.
# Meso best precision was 40.4%. Micro best precision was 35.7%.
# Those two levels are closed (threshold above 1) so a paper is never given
# a meso or micro id from taxonomy. Similarity is cosine against the cluster
# profile. Margin is the gap between the best cluster and the next.
THRESHOLDS = {
    "micro": {"min_similarity": 1.1, "min_margin": 1.1},
    "meso": {"min_similarity": 1.1, "min_margin": 1.1},
    "macro": {"min_similarity": 0.15, "min_margin": 0.02},
}
GRID_SIMILARITY = (0.15, 0.20, 0.25, 0.30, 0.40, 0.50)
GRID_MARGIN = (0.02, 0.05, 0.08, 0.12)

LOG_DIR = Path(r"C:\Users\sophie.wilson\Documents\scope_drift_outputs\logs\taxonomy_assignment")
log = logging.getLogger("taxonomy_assignment")

CLASSIFICATION_EXTRA = (
    "assignment_method",
    "assignment_level",
    "assignment_confidence",
    "assignment_margin",
    "exclusion_reason",
    "taxonomy_top_topic",
)


def setup_logging(run_timestamp: str) -> None:
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8", errors="replace")
    root = logging.getLogger()
    root.handlers.clear()
    root.setLevel(logging.INFO)
    fmt = logging.Formatter("%(asctime)s %(levelname)-8s %(message)s", datefmt="%H:%M:%S")
    stream_handler = logging.StreamHandler(sys.stdout)
    stream_handler.setFormatter(fmt)
    file_handler = logging.FileHandler(
        LOG_DIR / f"taxonomy_assignment_{run_timestamp}.log", encoding="utf-8"
    )
    file_handler.setFormatter(fmt)
    root.addHandler(stream_handler)
    root.addHandler(file_handler)


def require_timestamp(timestamp: str) -> str:
    ts = (timestamp or os.environ.get("RUN_TIMESTAMP") or "").strip()
    if not TS_RE.match(ts):
        raise SystemExit(
            "Pass --timestamp as YYYYMMDD_HHMMSS "
            f"(or set RUN_TIMESTAMP). Got {timestamp!r}."
        )
    return ts


def client() -> bigquery.Client:
    return bigquery.Client(project=BQ_BILL_PROJECT, location=BQ_LOCATION)


def query_df(bq: bigquery.Client, sql: str) -> pd.DataFrame:
    job = bq.query(sql)
    frame = job.result().to_dataframe()
    log.info("  query processed %s bytes", f"{job.total_bytes_processed or 0:,}")
    return frame


def tables(timestamp: str) -> dict[str, str]:
    base = f"{BQ_PROJECT}.{BQ_DATASET}"
    return {
        "classif": f"{base}.classification_raw_{timestamp}",
        "meta": f"{base}.pub_metadata_raw_{timestamp}",
        "pubs": f"{base}.pubs_raw_{timestamp}",
        "links": f"{base}.cit_links_raw_{timestamp}",
        "run": f"{base}.run_metadata_{timestamp}",
    }


def column_names(bq: bigquery.Client, table: str) -> set[str]:
    return {field.name for field in bq.get_table(table).schema}


def leiden_filter(bq: bigquery.Client, table: str, alias: str = "c") -> str:
    """Ignore taxonomy rows when the column already exists. Older runs have no column."""
    if "assignment_method" not in column_names(bq, table):
        return ""
    return (
        f"AND ({alias}.assignment_method IS NULL "
        f"OR {alias}.assignment_method = 'leiden')"
    )


def score_id_type(bq: bigquery.Client) -> str:
    for field in bq.get_table(TBL_SCORES).schema:
        if field.name == "publication_id":
            return field.field_type
    raise SystemExit(f"{TBL_SCORES} has no publication_id column")


def score_on(pub_expr: str, id_type: str) -> str:
    """Join predicate that keeps the clustered publication_id column bare.

    Casting publication_id disables cluster pruning and scans the whole score table.
    """
    if id_type in {"STRING"}:
        return f"t.publication_id = CAST({pub_expr} AS STRING)"
    if id_type in {"INTEGER", "INT64"}:
        return f"t.publication_id = {pub_expr}"
    raise SystemExit(
        f"Unexpected publication_id type {id_type!r}; refusing a join that would full-scan scores."
    )


def frontiers_flag(alias: str = "m") -> str:
    return f"""(
      SAFE_CAST({alias}.is_frontiers AS INT64) = 1
      OR SAFE_CAST({alias}.is_frontiers AS BOOL)
      OR LOWER(CAST({alias}.is_frontiers AS STRING)) IN ('1', 'true')
    )"""


def run_meta_ctes(ts: dict[str, str]) -> str:
    return f"""
    run_meta AS (
      SELECT
        CAST(start_year AS INT64) AS start_year,
        CAST(end_year AS INT64) AS end_year,
        network_mode,
        journal_ids
      FROM `{ts["run"]}`
    ),
    journals AS (
      SELECT DISTINCT CAST(j AS INT64) AS journal_id
      FROM run_meta, UNNEST(JSON_VALUE_ARRAY(journal_ids)) AS j
    ),
    frontier_pubs AS (
      SELECT p.PublicationId AS pub_id
      FROM `{AIRAK_PUBLICATION}` p
      JOIN journals j ON p.JournalId = j.journal_id
      CROSS JOIN run_meta m
      WHERE p.PublishedYear BETWEEN m.start_year AND m.end_year
    )
    """


def audit(bq: bigquery.Client, timestamp: str) -> pd.DataFrame:
    """Read-only counts for Frontiers papers this run never classified."""
    ts = tables(timestamp)
    id_type = score_id_type(bq)
    log.info("Taxonomy publication_id type: %s", id_type)
    counts = query_df(
        bq,
        f"""
        WITH {run_meta_ctes(ts)},
        meta_ids AS (
          SELECT int_id, SAFE_CAST(pub_id AS INT64) AS pub_id
          FROM `{ts["meta"]}`
        ),
        classified AS (
          SELECT m.pub_id
          FROM `{ts["classif"]}` c
          JOIN meta_ids m ON c.int_id = m.int_id
        ),
        edged AS (
          SELECT DISTINCT int_id1 AS int_id
          FROM `{ts["links"]}`
        ),
        gaps AS (
          SELECT
            f.pub_id,
            m.int_id,
            m.pub_id IS NOT NULL AS in_metadata,
            c.pub_id IS NOT NULL AS in_classification,
            e.int_id IS NOT NULL AS has_edge
          FROM frontier_pubs f
          LEFT JOIN meta_ids m ON f.pub_id = m.pub_id
          LEFT JOIN classified c ON f.pub_id = c.pub_id
          LEFT JOIN edged e ON m.int_id = e.int_id
        )
        SELECT
          (SELECT start_year FROM run_meta) AS start_year,
          (SELECT end_year FROM run_meta) AS end_year,
          (SELECT network_mode FROM run_meta) AS network_mode,
          (SELECT COUNT(*) FROM journals) AS n_journals,
          (SELECT COUNT(*) FROM `{ts["pubs"]}`) AS pubs_raw,
          (SELECT COUNT(*) FROM `{ts["classif"]}`) AS classified_rows,
          (SELECT COUNT(DISTINCT macro) FROM `{ts["classif"]}`) AS n_macro,
          (SELECT COUNT(DISTINCT meso) FROM `{ts["classif"]}`) AS n_meso,
          (SELECT COUNT(DISTINCT micro) FROM `{ts["classif"]}`) AS n_micro,
          COUNT(*) AS frontiers_pubs,
          COUNTIF(in_metadata) AS frontiers_in_metadata,
          COUNTIF(NOT in_metadata) AS frontiers_missing_metadata,
          COUNTIF(in_metadata AND NOT in_classification) AS frontiers_unclassified,
          COUNTIF(in_metadata AND NOT in_classification AND NOT has_edge) AS zero_degree,
          COUNTIF(in_metadata AND NOT in_classification AND has_edge) AS network_unclassified,
          COUNTIF(in_classification) AS frontiers_classified
        FROM gaps
        """,
    )
    row = counts.iloc[0]
    for key, value in row.items():
        log.info("  %-32s %s", key, value)

    on_missing = score_on("g.pub_id", id_type)
    on_sample = score_on("s.pub_id", id_type)
    coverage = query_df(
        bq,
        f"""
        WITH {run_meta_ctes(ts)},
        meta_ids AS (
          SELECT int_id, SAFE_CAST(pub_id AS INT64) AS pub_id
          FROM `{ts["meta"]}`
        ),
        classified AS (
          SELECT m.pub_id
          FROM `{ts["classif"]}` c
          JOIN meta_ids m ON c.int_id = m.int_id
        ),
        gaps AS (
          SELECT f.pub_id, 'missing_metadata' AS gap_group
          FROM frontier_pubs f
          LEFT JOIN meta_ids m ON f.pub_id = m.pub_id
          WHERE m.pub_id IS NULL
          UNION ALL
          SELECT f.pub_id, 'unclassified' AS gap_group
          FROM frontier_pubs f
          JOIN meta_ids m ON f.pub_id = m.pub_id
          LEFT JOIN classified c ON f.pub_id = c.pub_id
          WHERE c.pub_id IS NULL
        ),
        scored AS (
          SELECT DISTINCT g.pub_id, g.gap_group
          FROM gaps g
          JOIN `{TBL_SCORES}` t ON {on_missing}
          JOIN `{TBL_TAXONOMY}` tax
            ON tax.taxref = t.taxref
           AND tax.level = 'level_2'
           AND tax.axis = '{TOPIC_AXIS}'
          WHERE t.level = {SCORE_LEVEL}
            AND t.axis = '{TOPIC_AXIS}'
            AND t.scorer_version = '{SCORE_VERSION}'
            AND t.in_top_k = TRUE
            AND t.is_weak_match = FALSE
        ),
        classified_sample AS (
          SELECT pub_id
          FROM classified
          WHERE MOD(ABS(FARM_FINGERPRINT(CAST(pub_id AS STRING))), 200) = 0
        ),
        sample_scored AS (
          SELECT DISTINCT s.pub_id
          FROM classified_sample s
          JOIN `{TBL_SCORES}` t ON {on_sample}
          JOIN `{TBL_TAXONOMY}` tax
            ON tax.taxref = t.taxref
           AND tax.level = 'level_2'
           AND tax.axis = '{TOPIC_AXIS}'
          WHERE t.level = {SCORE_LEVEL}
            AND t.axis = '{TOPIC_AXIS}'
            AND t.scorer_version = '{SCORE_VERSION}'
            AND t.in_top_k = TRUE
            AND t.is_weak_match = FALSE
        )
        SELECT
          g.gap_group,
          COUNT(*) AS n_papers,
          COUNTIF(s.pub_id IS NOT NULL) AS n_with_v6_score
        FROM gaps g
        LEFT JOIN scored s
          ON g.pub_id = s.pub_id AND g.gap_group = s.gap_group
        GROUP BY g.gap_group
        UNION ALL
        SELECT
          'classified_sample_1_in_200' AS gap_group,
          (SELECT COUNT(*) FROM classified_sample) AS n_papers,
          (SELECT COUNT(*) FROM sample_scored) AS n_with_v6_score
        """,
    )
    for item in coverage.itertuples(index=False):
        share = (item.n_with_v6_score / item.n_papers) if item.n_papers else 0
        log.info(
            "  v6 coverage %-28s %s / %s (%.1f%%)",
            item.gap_group,
            f"{int(item.n_with_v6_score):,}",
            f"{int(item.n_papers):,}",
            share * 100,
        )
    return counts


def _level_ok(level: str) -> str:
    if level not in THRESHOLDS:
        raise ValueError(f"Unknown level {level!r}")
    return level


def profile_sql(level: str, ts: dict[str, str], id_type: str, leiden_sql: str) -> str:
    """Temp tables `{level}_profile` and `{level}_parent` for one Leiden level."""
    level = _level_ok(level)
    on_pub = score_on("s.pub_id", id_type)
    if level == "meso":
        parent_select = "cluster_id AS meso_id, macro_id"
    elif level == "micro":
        parent_select = "cluster_id AS micro_id, meso_id, macro_id"
    else:
        parent_select = "cluster_id AS macro_id"
    return f"""
    CREATE TEMP TABLE {level}_sample AS
    SELECT cluster_id, meso_id, macro_id, pub_id
    FROM (
      SELECT
        CAST(c.{level} AS INT64) AS cluster_id,
        CAST(c.meso AS INT64) AS meso_id,
        CAST(c.macro AS INT64) AS macro_id,
        SAFE_CAST(m.pub_id AS INT64) AS pub_id,
        ROW_NUMBER() OVER (
          PARTITION BY c.{level}
          ORDER BY FARM_FINGERPRINT(CAST(m.pub_id AS STRING))
        ) AS rn
      FROM `{ts["classif"]}` c
      JOIN `{ts["meta"]}` m ON c.int_id = m.int_id
      LEFT JOIN hidden h ON SAFE_CAST(m.pub_id AS INT64) = h.pub_id
      WHERE c.{level} IS NOT NULL
        AND h.pub_id IS NULL
        {leiden_sql}
    )
    WHERE rn <= {PROFILE_PAPERS};

    CREATE TEMP TABLE {level}_profile AS
    WITH counted AS (
      SELECT s.cluster_id, t.taxref, COUNT(*) AS n_papers
      FROM {level}_sample s
      JOIN `{TBL_SCORES}` t ON {on_pub}
      JOIN `{TBL_TAXONOMY}` tax
        ON tax.taxref = t.taxref
       AND tax.level = 'level_2'
       AND tax.axis = '{TOPIC_AXIS}'
      WHERE t.level = {SCORE_LEVEL}
        AND t.axis = '{TOPIC_AXIS}'
        AND t.scorer_version = '{SCORE_VERSION}'
        AND t.in_top_k = TRUE
        AND t.is_weak_match = FALSE
      GROUP BY s.cluster_id, t.taxref
    ),
    cluster_n AS (
      SELECT cluster_id, COUNT(*) AS n_papers FROM {level}_sample GROUP BY cluster_id
    ),
    topic_df AS (
      SELECT taxref, COUNT(*) AS n_clusters FROM counted GROUP BY taxref
    ),
    n_clusters AS (
      SELECT COUNT(*) AS n FROM cluster_n
    ),
    weighted AS (
      SELECT
        c.cluster_id,
        c.taxref,
        (c.n_papers / n.n_papers) * LOG((k.n + 1) / (d.n_clusters + 1)) AS weight
      FROM counted c
      JOIN cluster_n n USING (cluster_id)
      JOIN topic_df d USING (taxref)
      CROSS JOIN n_clusters k
      WHERE n.n_papers > 0
    ),
    ranked AS (
      SELECT
        cluster_id,
        taxref,
        weight,
        ROW_NUMBER() OVER (PARTITION BY cluster_id ORDER BY weight DESC, taxref) AS rn
      FROM weighted
      WHERE weight > 0
    )
    SELECT
      r.cluster_id,
      r.taxref,
      r.weight,
      SQRT(SUM(r.weight * r.weight) OVER (PARTITION BY r.cluster_id)) AS profile_norm
    FROM ranked r
    WHERE r.rn <= {PROFILE_TOPICS};

    CREATE TEMP TABLE {level}_parent AS
    SELECT {parent_select}
    FROM (
      SELECT
        cluster_id,
        (APPROX_TOP_COUNT(meso_id, 1)[SAFE_OFFSET(0)]).value AS meso_id,
        (APPROX_TOP_COUNT(macro_id, 1)[SAFE_OFFSET(0)]).value AS macro_id
      FROM {level}_sample
      GROUP BY cluster_id
    );
    """


def match_sql(level: str, paper_topics: str) -> str:
    """Best and second-best cluster for each paper in `paper_topics`."""
    level = _level_ok(level)
    return f"""
    {level}_scored AS (
      SELECT
        p.pub_id,
        pr.cluster_id,
        SAFE_DIVIDE(
          SUM(p.weight * pr.weight),
          pn.paper_norm * pr.profile_norm
        ) AS sim
      FROM {paper_topics} p
      JOIN {level}_profile pr ON pr.taxref = p.taxref
      JOIN paper_norm pn ON pn.pub_id = p.pub_id
      GROUP BY p.pub_id, pr.cluster_id, pn.paper_norm, pr.profile_norm
    ),
    {level}_ranked AS (
      SELECT
        pub_id,
        cluster_id,
        sim,
        ROW_NUMBER() OVER (
          PARTITION BY pub_id ORDER BY sim DESC, cluster_id
        ) AS rn
      FROM {level}_scored
      WHERE sim IS NOT NULL
    ),
    {level}_best AS (
      SELECT
        pub_id,
        MAX(IF(rn = 1, cluster_id, NULL)) AS cluster_id,
        MAX(IF(rn = 1, sim, NULL)) AS sim,
        MAX(IF(rn = 1, sim, NULL)) - IFNULL(MAX(IF(rn = 2, sim, NULL)), 0) AS margin
      FROM {level}_ranked
      WHERE rn <= 2
      GROUP BY pub_id
    )
    """


def hidden_sql(ts: dict[str, str], leiden_sql: str) -> str:
    return f"""
    CREATE TEMP TABLE hidden AS
    SELECT pub_id, macro_id, meso_id, micro_id, degree
    FROM (
      SELECT
        SAFE_CAST(m.pub_id AS INT64) AS pub_id,
        CAST(c.macro AS INT64) AS macro_id,
        CAST(c.meso AS INT64) AS meso_id,
        CAST(c.micro AS INT64) AS micro_id,
        IFNULL(d.degree, 0) AS degree,
        ROW_NUMBER() OVER (
          PARTITION BY c.macro
          ORDER BY IFNULL(d.degree, 0), FARM_FINGERPRINT(CAST(m.pub_id AS STRING))
        ) AS rn
      FROM `{ts["classif"]}` c
      JOIN `{ts["meta"]}` m ON c.int_id = m.int_id
      LEFT JOIN (
        SELECT int_id1 AS int_id, COUNT(*) AS degree
        FROM `{ts["links"]}`
        GROUP BY int_id1
      ) d ON d.int_id = c.int_id
      WHERE c.macro IS NOT NULL
        AND {frontiers_flag("m")}
        {leiden_sql}
    )
    WHERE rn <= {CALIBRATION_PER_MACRO};
    """


def paper_topic_sql(id_type: str, source: str, dest: str) -> str:
    on_pub = score_on("s.pub_id", id_type)
    return f"""
    CREATE TEMP TABLE {dest} AS
    SELECT s.pub_id, t.taxref, tax.name AS topic_name, GREATEST(t.cosine, 0) AS weight
    FROM {source} s
    JOIN `{TBL_SCORES}` t ON {on_pub}
    JOIN `{TBL_TAXONOMY}` tax
      ON tax.taxref = t.taxref
     AND tax.level = 'level_2'
     AND tax.axis = '{TOPIC_AXIS}'
    WHERE t.level = {SCORE_LEVEL}
      AND t.axis = '{TOPIC_AXIS}'
      AND t.scorer_version = '{SCORE_VERSION}'
      AND t.in_top_k = TRUE
      AND t.is_weak_match = FALSE
      AND t.cosine IS NOT NULL;

    CREATE TEMP TABLE paper_norm AS
    SELECT pub_id, SQRT(SUM(weight * weight)) AS paper_norm
    FROM {dest}
    GROUP BY pub_id
    HAVING paper_norm > 0;
    """


def calibrate(bq: bigquery.Client, timestamp: str) -> dict[str, dict[str, float]]:
    """Hide low-degree Leiden papers and see whether taxonomy recovers them."""
    ts = tables(timestamp)
    id_type = score_id_type(bq)
    leiden_sql = leiden_filter(bq, ts["classif"])
    sql = f"""
    {hidden_sql(ts, leiden_sql)}
    {paper_topic_sql(id_type, "hidden", "hidden_topics")}
    {profile_sql("macro", ts, id_type, leiden_sql)}
    {profile_sql("meso", ts, id_type, leiden_sql)}
    {profile_sql("micro", ts, id_type, leiden_sql)}
    WITH
    {match_sql("macro", "hidden_topics")},
    {match_sql("meso", "hidden_topics")},
    {match_sql("micro", "hidden_topics")}
    SELECT
      h.pub_id,
      h.degree,
      h.macro_id AS true_macro,
      h.meso_id AS true_meso,
      h.micro_id AS true_micro,
      macro_best.cluster_id AS pred_macro,
      macro_best.sim AS macro_sim,
      macro_best.margin AS macro_margin,
      meso_best.cluster_id AS pred_meso,
      meso_best.sim AS meso_sim,
      meso_best.margin AS meso_margin,
      micro_best.cluster_id AS pred_micro,
      micro_best.sim AS micro_sim,
      micro_best.margin AS micro_margin
    FROM hidden h
    LEFT JOIN macro_best ON macro_best.pub_id = h.pub_id
    LEFT JOIN meso_best ON meso_best.pub_id = h.pub_id
    LEFT JOIN micro_best ON micro_best.pub_id = h.pub_id
    """
    log.info(
        "Calibrating on up to %d low-degree Frontiers papers per macro",
        CALIBRATION_PER_MACRO,
    )
    frame = query_df(bq, sql)
    log.info("  hidden papers: %d", len(frame))
    if frame.empty:
        raise SystemExit("Calibration sample was empty.")
    log.info("  median degree: %s", f"{frame['degree'].median():.0f}")
    chosen: dict[str, dict[str, float]] = {}
    for level in ("macro", "meso", "micro"):
        point, grid = pick_operating_point(
            frame,
            level=level,
            sim_col=f"{level}_sim",
            margin_col=f"{level}_margin",
            pred_col=f"pred_{level}",
            true_col=f"true_{level}",
        )
        chosen[level] = point
        if point.get("closed"):
            log.info(
                "  %s closed: best grid precision %.1f%% on %d labelled papers",
                level,
                point["precision"] * 100,
                point["n_labelled"],
            )
        else:
            log.info(
                "  %s threshold similarity >= %.2f, margin >= %.2f "
                "(precision %.1f%%, accepted %d / %d)",
                level,
                point["min_similarity"],
                point["min_margin"],
                point["precision"] * 100,
                point["n_accepted"],
                point["n_labelled"],
            )
        for item in grid:
            log.info(
                "    grid sim %.2f margin %.2f  precision %.1f%%  accepted %d",
                item["min_similarity"],
                item["min_margin"],
                item["precision"] * 100,
                item["n_accepted"],
            )
    return chosen


def pick_operating_point(
    frame: pd.DataFrame,
    level: str,
    sim_col: str,
    margin_col: str,
    pred_col: str,
    true_col: str,
) -> tuple[dict[str, float], list[dict[str, float]]]:
    """Pick the loosest grid point that still holds precision at or above 75%.

    A level that cannot reach that precision is closed: similarity and margin
    are set above 1 so taxonomy assignment never uses it. Precision is judged
    only on accepted papers.
    """
    labelled = frame[frame[true_col].notna()].copy()
    n_labelled = int(len(labelled))
    grid: list[dict[str, float]] = []
    for similarity in GRID_SIMILARITY:
        for margin in GRID_MARGIN:
            sims = pd.to_numeric(labelled[sim_col], errors="coerce").fillna(-1)
            margins = pd.to_numeric(labelled[margin_col], errors="coerce").fillna(-1)
            accepted = labelled[(sims >= similarity) & (margins >= margin)]
            n_accepted = int(len(accepted))
            n_correct = int((accepted[pred_col] == accepted[true_col]).sum()) if n_accepted else 0
            grid.append(
                {
                    "level": level,
                    "min_similarity": float(similarity),
                    "min_margin": float(margin),
                    "n_labelled": n_labelled,
                    "n_accepted": n_accepted,
                    "n_correct": n_correct,
                    "precision": (n_correct / n_accepted) if n_accepted else 0.0,
                    "acceptance": (n_accepted / n_labelled) if n_labelled else 0.0,
                }
            )
    precise = [
        item
        for item in grid
        if item["precision"] >= 0.75 and item["n_accepted"] >= max(10, int(0.05 * n_labelled))
    ]
    if precise:
        # Loosest useful point: highest acceptance, then lower similarity.
        chosen = max(precise, key=lambda item: (item["acceptance"], -item["min_similarity"]))
    else:
        best = max(grid, key=lambda item: (item["precision"], item["acceptance"]))
        chosen = {
            "level": level,
            "min_similarity": 1.1,
            "min_margin": 1.1,
            "n_labelled": n_labelled,
            "n_accepted": 0,
            "n_correct": 0,
            "precision": float(best["precision"]),
            "acceptance": 0.0,
            "closed": True,
        }
        return chosen, grid
    chosen = dict(chosen)
    chosen["closed"] = False
    return chosen, grid


def candidate_sql(ts: dict[str, str], leiden_sql: str) -> str:
    return f"""
    CREATE TEMP TABLE candidates AS
    SELECT int_id, pub_id, exclusion_reason
    FROM (
      SELECT
        m.int_id,
        SAFE_CAST(m.pub_id AS INT64) AS pub_id,
        IF(e.int_id IS NULL, 'zero_degree', 'network_unclassified') AS exclusion_reason
      FROM `{ts["meta"]}` m
      LEFT JOIN `{ts["classif"]}` c ON m.int_id = c.int_id
      LEFT JOIN (
        SELECT DISTINCT int_id1 AS int_id FROM `{ts["links"]}`
      ) e ON m.int_id = e.int_id
      WHERE c.int_id IS NULL
        AND {frontiers_flag("m")}
      UNION ALL
      SELECT
        CAST(NULL AS INT64) AS int_id,
        f.pub_id,
        'zero_degree' AS exclusion_reason
      FROM frontiers f
      LEFT JOIN `{ts["meta"]}` m ON SAFE_CAST(m.pub_id AS INT64) = f.pub_id
      WHERE m.pub_id IS NULL
    )
    WHERE pub_id IS NOT NULL;
    """


def assign(bq: bigquery.Client, timestamp: str, write: bool) -> pd.DataFrame:
    """Score excluded Frontiers papers. Write only when `write` is true."""
    ts = tables(timestamp)
    id_type = score_id_type(bq)
    leiden_sql = leiden_filter(bq, ts["classif"], alias="c")
    # Profiles for a real assignment must include every Leiden paper, so the
    # calibration holdout table is absent. An empty hidden table keeps the
    # same SQL and excludes nobody.
    script = _assignment_script(ts, id_type, leiden_sql, write)
    log.info("%s assignment for %s", "Writing" if write else "Dry run", timestamp)
    for level, rule in THRESHOLDS.items():
        log.info(
            "  %s similarity >= %.2f, margin >= %.2f",
            level,
            rule["min_similarity"],
            rule["min_margin"],
        )
    summary = query_df(bq, script)
    if summary.empty:
        log.info("  no excluded Frontiers papers")
    for item in summary.itertuples(index=False):
        log.info(
            "  %-12s %-8s %-22s %s",
            item.assignment_method,
            item.assignment_level if pd.notna(item.assignment_level) else "-",
            item.exclusion_reason,
            f"{int(item.n_papers):,}",
        )
    return summary


def _assignment_script(ts: dict[str, str], id_type: str, leiden_sql: str, write: bool) -> str:
    write_sql = ""
    if write:
        write_sql = f"""
        CREATE TEMP TABLE new_meta AS
        SELECT
          (SELECT IFNULL(MAX(int_id), -1) FROM `{ts["pubs"]}`)
            + ROW_NUMBER() OVER (ORDER BY p.PublicationId) AS int_id,
          p.PublicationId AS pub_id,
          1 AS is_frontiers,
          IFNULL(j.DisplayName, '') AS journal,
          COALESCE(CAST(p.PublishedDate AS STRING), CAST(p.PublishedYear AS STRING), '0000-01-01') AS date,
          REPLACE(REPLACE(IFNULL(p.Title, ''), '\\t', ' '), '\\n', ' ') AS title
        FROM `{AIRAK_PUBLICATION}` p
        LEFT JOIN `{AIRAK_JOURNAL}` j ON p.JournalId = j.JournalId
        JOIN frontiers f ON f.pub_id = p.PublicationId
        LEFT JOIN `{ts["meta"]}` m ON SAFE_CAST(m.pub_id AS INT64) = p.PublicationId
        WHERE m.pub_id IS NULL;

        INSERT INTO `{ts["pubs"]}` (int_id, core_pub)
        SELECT int_id, 1 FROM new_meta;

        INSERT INTO `{ts["meta"]}` (int_id, pub_id, is_frontiers, journal, date, title)
        SELECT int_id, pub_id, is_frontiers, journal, date, title FROM new_meta;

        ALTER TABLE `{ts["classif"]}`
          ADD COLUMN IF NOT EXISTS assignment_method STRING,
          ADD COLUMN IF NOT EXISTS assignment_level STRING,
          ADD COLUMN IF NOT EXISTS assignment_confidence FLOAT64,
          ADD COLUMN IF NOT EXISTS assignment_margin FLOAT64,
          ADD COLUMN IF NOT EXISTS exclusion_reason STRING,
          ADD COLUMN IF NOT EXISTS taxonomy_top_topic STRING;

        UPDATE `{ts["classif"]}`
        SET assignment_method = 'leiden'
        WHERE assignment_method IS NULL OR assignment_method = 'leiden';

        DELETE FROM `{ts["classif"]}`
        WHERE assignment_method IN ('taxonomy', 'unassigned');

        INSERT INTO `{ts["classif"]}` (
          int_id, macro, meso, micro, assignment_method, assignment_level,
          assignment_confidence, assignment_margin, exclusion_reason, taxonomy_top_topic
        )
        SELECT
          COALESCE(a.int_id, n.int_id) AS int_id,
          a.macro, a.meso, a.micro, a.assignment_method, a.assignment_level,
          a.assignment_confidence, a.assignment_margin, a.exclusion_reason,
          a.taxonomy_top_topic
        FROM assigned a
        LEFT JOIN new_meta n ON n.pub_id = a.pub_id
        WHERE COALESCE(a.int_id, n.int_id) IS NOT NULL;
        """
    return f"""
    CREATE TEMP TABLE frontiers AS
    WITH {run_meta_ctes(ts)}
    SELECT pub_id FROM frontier_pubs;

    CREATE TEMP TABLE hidden AS
    SELECT CAST(NULL AS INT64) AS pub_id FROM (SELECT 1) WHERE FALSE;

    {candidate_sql(ts, leiden_sql)}
    {paper_topic_sql(id_type, "candidates", "paper_topics")}
    {profile_sql("macro", ts, id_type, leiden_sql)}
    {profile_sql("meso", ts, id_type, leiden_sql)}
    {profile_sql("micro", ts, id_type, leiden_sql)}

    CREATE TEMP TABLE assigned AS
    WITH
    {match_sql("macro", "paper_topics")},
    {match_sql("meso", "paper_topics")},
    {match_sql("micro", "paper_topics")},
    top_topic AS (
      SELECT pub_id, topic_name
      FROM paper_topics
      QUALIFY ROW_NUMBER() OVER (PARTITION BY pub_id ORDER BY weight DESC, taxref) = 1
    ),
    placed AS (
      SELECT
        c.int_id,
        c.pub_id,
        c.exclusion_reason,
        micro_best.sim AS micro_sim,
        micro_best.margin AS micro_margin,
        micro_best.cluster_id AS micro_match,
        meso_best.sim AS meso_sim,
        meso_best.margin AS meso_margin,
        meso_best.cluster_id AS meso_match,
        macro_best.sim AS macro_sim,
        macro_best.margin AS macro_margin,
        macro_best.cluster_id AS macro_match,
        top_topic.topic_name
      FROM candidates c
      LEFT JOIN micro_best ON micro_best.pub_id = c.pub_id
      LEFT JOIN meso_best ON meso_best.pub_id = c.pub_id
      LEFT JOIN macro_best ON macro_best.pub_id = c.pub_id
      LEFT JOIN top_topic ON top_topic.pub_id = c.pub_id
    )
    SELECT
      p.int_id,
      p.pub_id,
      CASE
        WHEN p.micro_sim >= {THRESHOLDS["micro"]["min_similarity"]}
         AND p.micro_margin >= {THRESHOLDS["micro"]["min_margin"]}
          THEN mp.macro_id
        WHEN p.meso_sim >= {THRESHOLDS["meso"]["min_similarity"]}
         AND p.meso_margin >= {THRESHOLDS["meso"]["min_margin"]}
          THEN sp.macro_id
        WHEN p.macro_sim >= {THRESHOLDS["macro"]["min_similarity"]}
         AND p.macro_margin >= {THRESHOLDS["macro"]["min_margin"]}
          THEN p.macro_match
        ELSE CAST(NULL AS INT64)
      END AS macro,
      CASE
        WHEN p.micro_sim >= {THRESHOLDS["micro"]["min_similarity"]}
         AND p.micro_margin >= {THRESHOLDS["micro"]["min_margin"]}
          THEN mp.meso_id
        WHEN p.meso_sim >= {THRESHOLDS["meso"]["min_similarity"]}
         AND p.meso_margin >= {THRESHOLDS["meso"]["min_margin"]}
          THEN p.meso_match
        ELSE CAST(NULL AS INT64)
      END AS meso,
      CASE
        WHEN p.micro_sim >= {THRESHOLDS["micro"]["min_similarity"]}
         AND p.micro_margin >= {THRESHOLDS["micro"]["min_margin"]}
          THEN p.micro_match
        ELSE CAST(NULL AS INT64)
      END AS micro,
      CASE
        WHEN p.micro_sim >= {THRESHOLDS["micro"]["min_similarity"]}
         AND p.micro_margin >= {THRESHOLDS["micro"]["min_margin"]}
          THEN 'taxonomy'
        WHEN p.meso_sim >= {THRESHOLDS["meso"]["min_similarity"]}
         AND p.meso_margin >= {THRESHOLDS["meso"]["min_margin"]}
          THEN 'taxonomy'
        WHEN p.macro_sim >= {THRESHOLDS["macro"]["min_similarity"]}
         AND p.macro_margin >= {THRESHOLDS["macro"]["min_margin"]}
          THEN 'taxonomy'
        ELSE 'unassigned'
      END AS assignment_method,
      CASE
        WHEN p.micro_sim >= {THRESHOLDS["micro"]["min_similarity"]}
         AND p.micro_margin >= {THRESHOLDS["micro"]["min_margin"]}
          THEN 'micro'
        WHEN p.meso_sim >= {THRESHOLDS["meso"]["min_similarity"]}
         AND p.meso_margin >= {THRESHOLDS["meso"]["min_margin"]}
          THEN 'meso'
        WHEN p.macro_sim >= {THRESHOLDS["macro"]["min_similarity"]}
         AND p.macro_margin >= {THRESHOLDS["macro"]["min_margin"]}
          THEN 'macro'
        ELSE CAST(NULL AS STRING)
      END AS assignment_level,
      CASE
        WHEN p.micro_sim >= {THRESHOLDS["micro"]["min_similarity"]}
         AND p.micro_margin >= {THRESHOLDS["micro"]["min_margin"]}
          THEN p.micro_sim
        WHEN p.meso_sim >= {THRESHOLDS["meso"]["min_similarity"]}
         AND p.meso_margin >= {THRESHOLDS["meso"]["min_margin"]}
          THEN p.meso_sim
        WHEN p.macro_sim >= {THRESHOLDS["macro"]["min_similarity"]}
         AND p.macro_margin >= {THRESHOLDS["macro"]["min_margin"]}
          THEN p.macro_sim
        ELSE CAST(NULL AS FLOAT64)
      END AS assignment_confidence,
      CASE
        WHEN p.micro_sim >= {THRESHOLDS["micro"]["min_similarity"]}
         AND p.micro_margin >= {THRESHOLDS["micro"]["min_margin"]}
          THEN p.micro_margin
        WHEN p.meso_sim >= {THRESHOLDS["meso"]["min_similarity"]}
         AND p.meso_margin >= {THRESHOLDS["meso"]["min_margin"]}
          THEN p.meso_margin
        WHEN p.macro_sim >= {THRESHOLDS["macro"]["min_similarity"]}
         AND p.macro_margin >= {THRESHOLDS["macro"]["min_margin"]}
          THEN p.macro_margin
        ELSE CAST(NULL AS FLOAT64)
      END AS assignment_margin,
      p.exclusion_reason,
      p.topic_name AS taxonomy_top_topic
    FROM placed p
    LEFT JOIN micro_parent mp ON mp.micro_id = p.micro_match
    LEFT JOIN meso_parent sp ON sp.meso_id = p.meso_match;

    {write_sql}

    SELECT
      assignment_method,
      assignment_level,
      exclusion_reason,
      COUNT(*) AS n_papers
    FROM assigned
    GROUP BY assignment_method, assignment_level, exclusion_reason
    ORDER BY assignment_method, assignment_level, exclusion_reason
    """


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Assign uncited Frontiers papers with taxonomy v6.")
    parser.add_argument("-t", "--timestamp", default=os.environ.get("RUN_TIMESTAMP", ""))
    parser.add_argument("--audit", action="store_true", help="Print coverage counts only.")
    parser.add_argument(
        "--calibrate",
        action="store_true",
        help="Measure recovery of held-out Leiden papers. Does not write.",
    )
    parser.add_argument(
        "--write",
        action="store_true",
        help="Append taxonomy and unassigned rows to classification_raw_{timestamp}.",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> None:
    args = parse_args(argv)
    timestamp = require_timestamp(args.timestamp)
    setup_logging(timestamp)
    bq = client()
    if args.audit:
        audit(bq, timestamp)
        return
    if args.calibrate:
        calibrate(bq, timestamp)
        return
    if args.write:
        log.info("Write is on: classification_raw_%s will gain taxonomy rows", timestamp)
    else:
        log.info("Dry run: no BigQuery tables will be changed")
    assign(bq, timestamp, write=args.write)


if __name__ == "__main__":
    main()
