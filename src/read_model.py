"""Publish the scope-drift read model for one run.

The pipeline tables stay in ``raw_citation_network_data``. This script adds
three stable tables in ``leiden_output``. Each row carries ``run_timestamp``.
Publishing a run again deletes only that run's rows in ``leiden_output`` and
appends the new ones.

    papers        one row per paper (classification + metadata + scope)
    communities   one row per community at macro, meso, and micro
    journals      one row per journal the dashboard scored

Usage:
    python src/read_model.py --timestamp 20260721_122750
    python src/read_model.py -t 20260721_122750
"""

from __future__ import annotations

import argparse
import logging
import os
import re
import sys
from pathlib import Path

import pandas as pd
import pandas_gbq
from google.cloud import bigquery
from google.cloud.exceptions import NotFound

try:
    from dotenv import load_dotenv
except ImportError:  # pragma: no cover - dotenv is a project dependency
    load_dotenv = None

REPO = Path(__file__).resolve().parent.parent
if load_dotenv is not None:
    load_dotenv(REPO / ".env", override=True)

BQ_PROJECT = os.environ.get("BQ_PROJECT", "ocean-tech-adv-analytics-c-tfs")
BQ_DATASET = os.environ.get("BQ_DATASET", "raw_citation_network_data")
BQ_LABEL_DATASET = os.environ.get("BQ_LABEL_DATASET", "taxonomy_labelling")
BQ_READ_DATASET = os.environ.get("BQ_READ_DATASET", "leiden_output")
BQ_LOCATION = "EU"
LEVELS = ("macro", "meso", "micro")
TS_RE = re.compile(r"^\d{8}_\d{6}$")

LOG_DIR = Path(r"C:\Users\sophie.wilson\Documents\scope_drift_outputs\logs")
log = logging.getLogger("read_model")

PAPERS_FIELDS = [
    ("run_timestamp", "STRING", "REQUIRED"),
    ("int_id", "INT64", "REQUIRED"),
    ("pub_id", "STRING", "NULLABLE"),
    ("title", "STRING", "NULLABLE"),
    ("journal", "STRING", "NULLABLE"),
    ("is_frontiers", "BOOL", "NULLABLE"),
    ("pub_year", "INT64", "NULLABLE"),
    ("macro_id", "INT64", "NULLABLE"),
    ("meso_id", "INT64", "NULLABLE"),
    ("micro_id", "INT64", "NULLABLE"),
    ("assignment_method", "STRING", "NULLABLE"),
    ("scope", "STRING", "NULLABLE"),
    ("scope_reason", "STRING", "NULLABLE"),
    ("scope_level", "STRING", "NULLABLE"),
]
COMMUNITIES_FIELDS = [
    ("run_timestamp", "STRING", "REQUIRED"),
    ("level", "STRING", "REQUIRED"),
    ("community_id", "INT64", "REQUIRED"),
    ("name", "STRING", "NULLABLE"),
    ("n_papers", "INT64", "NULLABLE"),
    ("n_papers_enriched", "INT64", "NULLABLE"),
    ("parent_name", "STRING", "NULLABLE"),
    ("topics", "STRING", "NULLABLE"),
    ("taxonomy_key", "STRING", "NULLABLE"),
]
JOURNALS_FIELDS = [
    ("run_timestamp", "STRING", "REQUIRED"),
    ("journal", "STRING", "REQUIRED"),
    ("cluster_level", "STRING", "NULLABLE"),
    ("n_articles", "INT64", "NULLABLE"),
    ("n_out_of_scope", "INT64", "NULLABLE"),
    ("out_of_scope_pct", "FLOAT64", "NULLABLE"),
    ("primary_coverage_pct", "FLOAT64", "NULLABLE"),
    ("primary_communities", "STRING", "NULLABLE"),
    ("borderline_communities", "STRING", "NULLABLE"),
    ("oos_by_year", "STRING", "NULLABLE"),
    ("n_borderline_papers", "INT64", "NULLABLE"),
    ("n_hard_negative_papers", "INT64", "NULLABLE"),
    ("n_paper_demoted", "INT64", "NULLABLE"),
]


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
        LOG_DIR / f"read_model_{run_timestamp}.log", encoding="utf-8"
    )
    file_handler.setFormatter(fmt)
    root.addHandler(stream_handler)
    root.addHandler(file_handler)


def require_timestamp(timestamp: str) -> str:
    ts = (timestamp or "").strip()
    if not TS_RE.match(ts):
        raise SystemExit(
            "Pass --timestamp / -t as YYYYMMDD_HHMMSS "
            f"(or set RUN_TIMESTAMP). Got {timestamp!r}."
        )
    return ts


def client() -> bigquery.Client:
    return bigquery.Client(project=BQ_PROJECT, location=BQ_LOCATION)


def ensure_dataset(bq: bigquery.Client) -> None:
    dataset_id = f"{BQ_PROJECT}.{BQ_READ_DATASET}"
    dataset = bigquery.Dataset(dataset_id)
    dataset.location = BQ_LOCATION
    bq.create_dataset(dataset, exists_ok=True)
    log.info("BigQuery dataset %s (%s)", dataset_id, BQ_LOCATION)


def table_exists(bq: bigquery.Client, fq_table: str) -> bool:
    try:
        bq.get_table(fq_table)
    except NotFound:
        return False
    return True


def ensure_table(bq: bigquery.Client, table: str, fields: list[tuple[str, str, str]]) -> str:
    fq = f"{BQ_PROJECT}.{BQ_READ_DATASET}.{table}"
    schema = [bigquery.SchemaField(name, typ, mode=mode) for name, typ, mode in fields]
    try:
        existing = bq.get_table(fq)
    except NotFound:
        bq.create_table(bigquery.Table(fq, schema=schema))
        return fq
    have = {field.name for field in existing.schema}
    extra = [field for field in schema if field.name not in have]
    if extra:
        existing.schema = list(existing.schema) + extra
        bq.update_table(existing, ["schema"])
    return fq


def delete_run(bq: bigquery.Client, fq_table: str, run_timestamp: str) -> None:
    job_config = bigquery.QueryJobConfig(
        query_parameters=[
            bigquery.ScalarQueryParameter("ts", "STRING", run_timestamp)
        ]
    )
    bq.query(
        f"DELETE FROM `{fq_table}` WHERE run_timestamp = @ts",
        job_config=job_config,
    ).result()


def write_frame(
    bq: bigquery.Client,
    df: pd.DataFrame,
    table: str,
    fields: list[tuple[str, str, str]],
    run_timestamp: str,
) -> None:
    fq = ensure_table(bq, table, fields)
    delete_run(bq, fq, run_timestamp)
    columns = [name for name, _, _ in fields]
    if df is None or df.empty:
        log.info("  %s: removed rows for %s; nothing new to append", table, run_timestamp)
        return
    out = df.loc[:, columns].copy()
    pandas_gbq.to_gbq(
        out,
        f"{BQ_READ_DATASET}.{table}",
        project_id=BQ_PROJECT,
        if_exists="append",
        location=BQ_LOCATION,
    )
    log.info("  → %s.%s (%s rows for %s)", BQ_PROJECT, fq, f"{len(out):,}", run_timestamp)


def _flag(alias: str, column: str) -> str:
    """True when a BigQuery column is a BOOL or a 1/true string."""
    return (
        f"COALESCE(SAFE_CAST({alias}.{column} AS BOOL), "
        f"LOWER(CAST({alias}.{column} AS STRING)) IN ('1', 'true'), FALSE)"
    )


def publish_papers(bq: bigquery.Client, run_timestamp: str) -> None:
    classification = f"{BQ_PROJECT}.{BQ_DATASET}.classification_raw_{run_timestamp}"
    metadata = f"{BQ_PROJECT}.{BQ_DATASET}.pub_metadata_raw_{run_timestamp}"
    if not table_exists(bq, classification) or not table_exists(bq, metadata):
        raise SystemExit(
            "papers need "
            f"classification_raw_{run_timestamp} and pub_metadata_raw_{run_timestamp} "
            f"in {BQ_DATASET}."
        )

    class_fields = {field.name for field in bq.get_table(classification).schema}
    if "assignment_method" in class_fields:
        assignment_sql = (
            "COALESCE(NULLIF(CAST(c.assignment_method AS STRING), ''), 'leiden')"
        )
    else:
        assignment_sql = "'leiden'"

    scope = f"{BQ_PROJECT}.{BQ_DATASET}.paper_scope_{run_timestamp}"
    has_scope = table_exists(bq, scope)
    if has_scope:
        scope_join = f"LEFT JOIN `{scope}` s ON CAST(c.int_id AS INT64) = CAST(s.int_id AS INT64)"
        oos = _flag("s", "is_oos")
        borderline = _flag("s", "is_borderline")
        demoted = _flag("s", "paper_demoted")
        hard_negative = _flag("s", "hard_negative")
        scope_sql = f"""
          CASE
            WHEN s.int_id IS NULL THEN NULL
            WHEN {oos} THEN 'out_of_scope'
            WHEN {borderline} THEN 'borderline'
            ELSE 'in_scope'
          END AS scope,
          CASE
            WHEN s.int_id IS NULL THEN NULL
            WHEN {demoted} THEN 'paper_llm'
            WHEN {hard_negative} THEN 'hard_negative'
            WHEN {borderline} THEN 'borderline_community'
            WHEN NOT {oos} THEN 'primary'
            ELSE 'outside_primary'
          END AS scope_reason,
          IF(s.int_id IS NULL, NULL, CAST(s.cluster_level AS STRING)) AS scope_level
        """
        log.info("  paper scope: %s", scope)
    else:
        scope_join = ""
        scope_sql = """
          CAST(NULL AS STRING) AS scope,
          CAST(NULL AS STRING) AS scope_reason,
          CAST(NULL AS STRING) AS scope_level
        """
        log.info(
            "  paper_scope_%s not found; scope columns will be null",
            run_timestamp,
        )

    fq = ensure_table(bq, "papers", PAPERS_FIELDS)
    delete_run(bq, fq, run_timestamp)
    job_config = bigquery.QueryJobConfig(
        query_parameters=[
            bigquery.ScalarQueryParameter("ts", "STRING", run_timestamp)
        ]
    )
    insert_sql = f"""
    INSERT INTO `{fq}` (
      run_timestamp, int_id, pub_id, title, journal, is_frontiers, pub_year,
      macro_id, meso_id, micro_id, assignment_method, scope, scope_reason, scope_level
    )
    SELECT
      @ts AS run_timestamp,
      CAST(c.int_id AS INT64) AS int_id,
      CAST(m.pub_id AS STRING) AS pub_id,
      CAST(m.title AS STRING) AS title,
      NULLIF(CAST(m.journal AS STRING), '') AS journal,
      COALESCE(
        SAFE_CAST(m.is_frontiers AS BOOL),
        LOWER(CAST(m.is_frontiers AS STRING)) IN ('1', 'true'),
        FALSE
      ) AS is_frontiers,
      COALESCE(
        EXTRACT(YEAR FROM SAFE.PARSE_DATE(
          '%Y-%m-%d', SUBSTR(CAST(m.date AS STRING), 1, 10)
        )),
        SAFE_CAST(SUBSTR(CAST(m.date AS STRING), 1, 4) AS INT64)
      ) AS pub_year,
      CAST(c.macro AS INT64) AS macro_id,
      CAST(c.meso AS INT64) AS meso_id,
      CAST(c.micro AS INT64) AS micro_id,
      {assignment_sql} AS assignment_method,
      {scope_sql}
    FROM `{classification}` c
    JOIN `{metadata}` m
      ON CAST(c.int_id AS INT64) = CAST(m.int_id AS INT64)
    {scope_join}
    """
    bq.query(insert_sql, job_config=job_config).result()
    count = list(
        bq.query(
            f"SELECT COUNT(*) AS n FROM `{fq}` WHERE run_timestamp = @ts",
            job_config=job_config,
        ).result()
    )[0]["n"]
    log.info("  → %s (%s papers)", fq, f"{int(count):,}")


def _string_expr(columns: set[str], column: str) -> str:
    if column in columns:
        return f"CAST({column} AS STRING)"
    return "''"


def fetch_label_rows(bq: bigquery.Client, run_timestamp: str, level: str) -> pd.DataFrame | None:
    """One community per row for a level, or None when that level was not labelled."""
    labels = f"{BQ_PROJECT}.{BQ_LABEL_DATASET}.cluster_labels_{level}_{run_timestamp}"
    try:
        label_table = bq.get_table(labels)
    except NotFound:
        log.info("  skip %s: %s not found", level, labels)
        return None

    label_cols = {field.name for field in label_table.schema}
    if "cluster_id" not in label_cols:
        log.warning("  skip %s: %s has no cluster_id", level, labels)
        return None

    query = f"""
    SELECT
      CAST(cluster_id AS INT64) AS community_id,
      {_string_expr(label_cols, "short_label")} AS short_label,
      {("CAST(n_papers AS INT64)" if "n_papers" in label_cols else "0")} AS n_papers,
      {_string_expr(label_cols, "taxonomy_key")} AS taxonomy_key,
      {_string_expr(label_cols, "l2_topics")} AS topics
    FROM `{labels}`
    """
    frame = bq.query(query).to_dataframe()
    frame = frame.dropna(subset=["community_id"]).drop_duplicates("community_id")
    if frame.empty:
        log.info("  %s labels table is empty", level)
        return frame
    frame["community_id"] = frame["community_id"].astype("int64")

    rollup = fetch_topic_rollup(bq, run_timestamp, level)
    if rollup.empty:
        frame["unit_name"] = ""
        frame["parent_name"] = ""
        frame["topics_fallback"] = ""
    else:
        frame = frame.merge(rollup, on="community_id", how="left")

    unit = frame["unit_name"].fillna("").astype(str).str.strip()
    short = frame["short_label"].fillna("").astype(str).str.strip()
    frame["name"] = unit.where(unit != "", short)
    unnamed = frame["name"].str.strip() == ""
    frame.loc[unnamed, "name"] = "Cluster " + frame.loc[unnamed, "community_id"].astype(int).astype(str)

    topics = frame["topics"].fillna("").astype(str).str.strip()
    fallback = frame["topics_fallback"].fillna("").astype(str).str.strip()
    frame["topics"] = topics.where(topics != "", fallback)
    frame["parent_name"] = frame["parent_name"].fillna("").astype(str).str.strip()
    frame["taxonomy_key"] = frame["taxonomy_key"].fillna("").astype(str)
    frame["n_papers"] = pd.to_numeric(frame["n_papers"], errors="coerce").fillna(0).astype("int64")
    # Leiden count until publish_communities replaces it with leiden + taxonomy.
    frame["n_papers_enriched"] = frame["n_papers"]
    frame["community_id"] = frame["community_id"].astype("int64")
    frame["run_timestamp"] = run_timestamp
    frame["level"] = level
    log.info("  %s: %s communities", level, f"{len(frame):,}")
    return frame.loc[:, [name for name, _, _ in COMMUNITIES_FIELDS]]


def fetch_topic_rollup(bq: bigquery.Client, run_timestamp: str, level: str) -> pd.DataFrame:
    """unit_name, L0 parent, and an L2-topic string for each community."""
    empty = pd.DataFrame(columns=["community_id", "unit_name", "parent_name", "topics_fallback"])
    topics_table = f"{BQ_PROJECT}.{BQ_LABEL_DATASET}.cluster_l2_topics_{level}_{run_timestamp}"
    try:
        table = bq.get_table(topics_table)
    except NotFound:
        log.info("  %s: no cluster_l2_topics table; names fall back to short_label", level)
        return empty

    columns = {field.name for field in table.schema}
    id_col = "community_id" if "community_id" in columns else "cluster_id"
    if id_col not in columns:
        log.warning("  %s: %s has no community id", level, topics_table)
        return empty

    unit_expr = _string_expr(columns, "unit_name")
    parent_expr = _string_expr(columns, "l0_roll_name")
    if "l2_name" in columns:
        order = " ORDER BY l2_rank" if "l2_rank" in columns else ""
        topics_expr = f"STRING_AGG(CAST(l2_name AS STRING), '; '{order})"
    else:
        topics_expr = "''"
    query = f"""
    SELECT
      CAST({id_col} AS INT64) AS community_id,
      ANY_VALUE(NULLIF(TRIM({unit_expr}), '')) AS unit_name,
      ANY_VALUE(NULLIF(TRIM({parent_expr}), '')) AS parent_name,
      {topics_expr} AS topics_fallback
    FROM `{topics_table}`
    GROUP BY 1
    """
    frame = bq.query(query).to_dataframe()
    if frame.empty:
        return empty
    frame = frame.dropna(subset=["community_id"])
    frame["community_id"] = frame["community_id"].astype("int64")
    return frame


def _attach_enriched_counts(
    bq: bigquery.Client, communities: pd.DataFrame, run_timestamp: str
) -> pd.DataFrame:
    """n_papers stays the Leiden count. n_papers_enriched adds taxonomy rows."""
    if communities.empty:
        return communities
    classification = f"{BQ_PROJECT}.{BQ_DATASET}.classification_raw_{run_timestamp}"
    if not table_exists(bq, classification):
        return communities
    fields = {field.name for field in bq.get_table(classification).schema}
    if "assignment_method" not in fields:
        return communities
    parts = []
    for level in LEVELS:
        parts.append(
            f"""
            SELECT
              '{level}' AS level,
              CAST({level} AS INT64) AS community_id,
              COUNTIF(
                assignment_method IS NULL
                OR assignment_method IN ('leiden', 'taxonomy')
              ) AS n_papers_enriched
            FROM `{classification}`
            WHERE {level} IS NOT NULL
            GROUP BY 2
            """
        )
    counts = bq.query(" UNION ALL ".join(parts)).to_dataframe()
    if counts.empty:
        return communities
    counts["community_id"] = counts["community_id"].astype("int64")
    out = communities.drop(columns=["n_papers_enriched"], errors="ignore")
    out["community_id"] = out["community_id"].astype("int64")
    out = out.merge(counts, on=["level", "community_id"], how="left")
    out["n_papers_enriched"] = (
        pd.to_numeric(out["n_papers_enriched"], errors="coerce")
        .fillna(out["n_papers"])
        .astype("int64")
    )
    return out


def publish_communities(bq: bigquery.Client, run_timestamp: str) -> pd.DataFrame | None:
    """Write communities. None means no label tables existed, so existing rows stay."""
    frames: list[pd.DataFrame] = []
    found_any = False
    for level in LEVELS:
        frame = fetch_label_rows(bq, run_timestamp, level)
        if frame is None:
            continue
        found_any = True
        if not frame.empty:
            frames.append(frame)
    if not found_any:
        log.warning(
            "No cluster_labels tables for %s; communities left unchanged",
            run_timestamp,
        )
        return None
    combined = (
        pd.concat(frames, ignore_index=True)
        if frames
        else pd.DataFrame(columns=[name for name, _, _ in COMMUNITIES_FIELDS])
    )
    combined = _attach_enriched_counts(bq, combined, run_timestamp)
    write_frame(bq, combined, "communities", COMMUNITIES_FIELDS, run_timestamp)
    return combined


def load_published_communities(bq: bigquery.Client, run_timestamp: str) -> pd.DataFrame:
    fq = f"{BQ_PROJECT}.{BQ_READ_DATASET}.communities"
    empty = pd.DataFrame(columns=["level", "community_id", "name"])
    if not table_exists(bq, fq):
        return empty
    job_config = bigquery.QueryJobConfig(
        query_parameters=[
            bigquery.ScalarQueryParameter("ts", "STRING", run_timestamp)
        ]
    )
    return bq.query(
        f"""
        SELECT level, community_id, name
        FROM `{fq}`
        WHERE run_timestamp = @ts
        """,
        job_config=job_config,
    ).to_dataframe()


def parse_ids(value: object) -> list[int]:
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return []
    text = str(value).strip()
    if not text or text.lower() == "nan":
        return []
    ids: list[int] = []
    for part in text.split(","):
        part = part.strip()
        if not part:
            continue
        ids.append(int(float(part)))
    return ids


def join_names(value: object, lookup: dict[int, str]) -> str:
    return "; ".join(lookup.get(community_id, str(community_id)) for community_id in parse_ids(value))


def publish_journals(
    bq: bigquery.Client,
    run_timestamp: str,
    communities: pd.DataFrame,
) -> None:
    summary_table = f"{BQ_PROJECT}.{BQ_DATASET}.journal_summary_{run_timestamp}"
    if not table_exists(bq, summary_table):
        log.info(
            "journal_summary_%s not found; journals left unchanged. "
            "Re-run the dashboard to write it.",
            run_timestamp,
        )
        return

    summary = bq.query(f"SELECT * FROM `{summary_table}`").to_dataframe()
    if summary.empty:
        write_frame(
            bq,
            pd.DataFrame(columns=[name for name, _, _ in JOURNALS_FIELDS]),
            "journals",
            JOURNALS_FIELDS,
            run_timestamp,
        )
        return

    lookups: dict[str, dict[int, str]] = {}
    if not communities.empty:
        for level, group in communities.groupby("level"):
            lookups[str(level)] = {
                int(row.community_id): str(row.name)
                for row in group.itertuples(index=False)
                if str(getattr(row, "name", "")).strip()
            }

    rows = []
    for row in summary.itertuples(index=False):
        level = str(getattr(row, "cluster_level", "") or "")
        lookup = lookups.get(level, {})
        oos_by_year = getattr(row, "oos_by_year", "[]")
        if oos_by_year is None or (isinstance(oos_by_year, float) and pd.isna(oos_by_year)):
            oos_by_year = "[]"
        rows.append(
            {
                "run_timestamp": run_timestamp,
                "journal": str(row.journal),
                "cluster_level": level,
                "n_articles": int(row.n_articles),
                "n_out_of_scope": int(row.n_out_of_scope),
                "out_of_scope_pct": float(row.out_of_scope_pct),
                "primary_coverage_pct": float(row.primary_coverage_pct),
                "primary_communities": join_names(row.primary_community_ids, lookup),
                "borderline_communities": join_names(row.borderline_community_ids, lookup),
                "oos_by_year": str(oos_by_year),
                "n_borderline_papers": int(row.n_borderline_papers),
                "n_hard_negative_papers": int(row.n_hard_negative_papers),
                "n_paper_demoted": int(row.n_paper_demoted),
            }
        )
    write_frame(bq, pd.DataFrame(rows), "journals", JOURNALS_FIELDS, run_timestamp)


def publish(run_timestamp: str) -> None:
    pandas_gbq.context.project = BQ_PROJECT
    pandas_gbq.context.location = BQ_LOCATION
    bq = client()
    ensure_dataset(bq)
    log.info("Publishing read model for %s", run_timestamp)
    publish_papers(bq, run_timestamp)
    communities = publish_communities(bq, run_timestamp)
    if communities is None:
        communities = load_published_communities(bq, run_timestamp)
    publish_journals(bq, run_timestamp, communities)
    log.info("Read model ready in %s.%s", BQ_PROJECT, BQ_READ_DATASET)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Publish the scope-drift read model for one run.")
    parser.add_argument(
        "-t",
        "--timestamp",
        default=os.environ.get("RUN_TIMESTAMP", ""),
        help="Scope-drift run id (YYYYMMDD_HHMMSS). Defaults to RUN_TIMESTAMP.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    run_timestamp = require_timestamp(args.timestamp)
    setup_logging(run_timestamp)
    publish(run_timestamp)


if __name__ == "__main__":
    main()
