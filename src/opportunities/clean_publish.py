"""Publish the stakeholder opportunity tables.

Dataset ``opportunity_clean`` holds two stable tables, ``runs`` and
``subfields``. ``run_timestamp`` is the citation-network run, the same id
carried on ``leiden_output``.

Publishing inserts rows for a run that is not already there. It does not
delete, replace, or update existing BigQuery data, including rows already
stored in ``opportunity_clean``.
"""

from __future__ import annotations

import json
import logging
import math
import re
from typing import Any

import pandas as pd
from google.cloud import bigquery
from google.cloud.exceptions import NotFound

from . import config as C

log = logging.getLogger("opportunities.clean")

CLEAN_DATASET = C.BQ_CLEAN_DATASET
RUNS_TABLE = "runs"
SUBFIELDS_TABLE = "subfields"
TS_RE = re.compile(r"^\d{8}_\d{6}$")
BANNED = re.compile(
    r"\b(delete|drop|truncate|update|merge)\b|create\s+or\s+replace",
    re.IGNORECASE,
)

RUNS_FIELDS = [
    ("run_timestamp", "STRING", "REQUIRED"),
    ("openalex_works_modified", "STRING", "NULLABLE"),
    ("openalex_subfields_modified", "STRING", "NULLABLE"),
    ("market_base_year", "INT64", "NULLABLE"),
    ("market_late_year", "INT64", "NULLABLE"),
    ("market_min_annual", "INT64", "NULLABLE"),
    ("market_min_cagr", "FLOAT64", "NULLABLE"),
    ("scope_coverage_target", "FLOAT64", "NULLABLE"),
    ("ownership_threshold", "FLOAT64", "NULLABLE"),
    ("greenfield_max_fi_3y", "INT64", "NULLABLE"),
    ("n_subfields", "INT64", "NULLABLE"),
    ("n_market_qualified", "INT64", "NULLABLE"),
    ("n_launch_candidates", "INT64", "NULLABLE"),
    ("n_shortlisted", "INT64", "NULLABLE"),
    ("action_counts", "STRING", "NULLABLE"),
    ("coverage_counts", "STRING", "NULLABLE"),
    ("notes", "STRING", "NULLABLE"),
]
SUBFIELDS_FIELDS = [
    ("run_timestamp", "STRING", "REQUIRED"),
    ("subfield_id", "STRING", "REQUIRED"),
    ("proposed_journal", "STRING", "NULLABLE"),
    ("subfield", "STRING", "NULLABLE"),
    ("field", "STRING", "NULLABLE"),
    ("domain", "STRING", "NULLABLE"),
    ("grade", "STRING", "NULLABLE"),
    ("score", "INT64", "NULLABLE"),
    ("world_2025", "INT64", "NULLABLE"),
    ("cagr", "FLOAT64", "NULLABLE"),
    ("fi_2025", "INT64", "NULLABLE"),
    ("share_vs_parity", "FLOAT64", "NULLABLE"),
    ("lead_title", "STRING", "NULLABLE"),
    ("ownership", "STRING", "NULLABLE"),
    ("coverage", "STRING", "NULLABLE"),
    ("scope_confidence", "STRING", "NULLABLE"),
    ("scope_names", "STRING", "NULLABLE"),
    ("section_themes", "STRING", "NULLABLE"),
    ("scope_community_ids", "INT64", "REPEATED"),
    ("action", "STRING", "NULLABLE"),
    ("action_reason", "STRING", "NULLABLE"),
    ("warning", "STRING", "NULLABLE"),
    ("shortlist_rank", "INT64", "NULLABLE"),
]


def _client() -> bigquery.Client:
    return bigquery.Client(project=C.BQ_PROJECT, location=C.BQ_LOCATION)


def _fq(table: str) -> str:
    return f"{C.BQ_PROJECT}.{CLEAN_DATASET}.{table}"


def _schema(fields: list[tuple[str, str, str]]) -> list[bigquery.SchemaField]:
    return [bigquery.SchemaField(name, typ, mode=mode) for name, typ, mode in fields]


def _refuse(sql: str) -> None:
    if BANNED.search(sql):
        raise RuntimeError("Refusing a statement that could delete or replace data.")
    writes = re.search(r"\b(insert\s+into|create\s+table)\b", sql, re.IGNORECASE)
    if writes and CLEAN_DATASET not in sql:
        raise RuntimeError("Refusing a write that does not target opportunity_clean.")
    if re.search(
        r"insert\s+into\s+`[^`]*(opportunity_mapping|raw_citation|taxonomy_labelling|leiden_output)\.",
        sql,
        re.IGNORECASE,
    ):
        raise RuntimeError("Refusing a write aimed at an existing dataset.")


def _query(bq: bigquery.Client, sql: str, params: list | None = None) -> None:
    _refuse(sql)
    job_config = bigquery.QueryJobConfig(query_parameters=params or [])
    bq.query(sql, job_config=job_config).result()


def ensure_tables(bq: bigquery.Client | None = None) -> None:
    """Create the dataset and tables when they are absent. Never replace them."""
    bq = bq or _client()
    dataset_id = f"{C.BQ_PROJECT}.{CLEAN_DATASET}"
    try:
        bq.get_dataset(dataset_id)
    except NotFound:
        dataset = bigquery.Dataset(dataset_id)
        dataset.location = C.BQ_LOCATION
        bq.create_dataset(dataset, exists_ok=True)
        log.info("Created dataset %s", dataset_id)
    for name, fields in (
        (RUNS_TABLE, RUNS_FIELDS),
        (SUBFIELDS_TABLE, SUBFIELDS_FIELDS),
    ):
        table = bigquery.Table(_fq(name), schema=_schema(fields))
        table.clustering_fields = ["run_timestamp"]
        bq.create_table(table, exists_ok=True)


def run_present(bq: bigquery.Client, table: str, run_timestamp: str) -> int:
    sql = f"SELECT COUNT(*) AS n FROM `{_fq(table)}` WHERE run_timestamp = @ts"
    _refuse(sql)
    job = bq.query(
        sql,
        job_config=bigquery.QueryJobConfig(
            query_parameters=[
                bigquery.ScalarQueryParameter("ts", "STRING", run_timestamp)
            ]
        ),
    )
    return int(next(job.result()).n)


def _missing(value: Any) -> bool:
    if value is None:
        return True
    if isinstance(value, str):
        return False
    if isinstance(value, (list, tuple, dict)):
        return False
    try:
        return bool(pd.isna(value))
    except (TypeError, ValueError):
        return False


def _text(value: Any) -> str | None:
    if _missing(value):
        return None
    return str(value)


def _int(value: Any) -> int | None:
    if _missing(value):
        return None
    return int(value)


def _float(value: Any) -> float | None:
    if _missing(value):
        return None
    number = float(value)
    if math.isnan(number) or math.isinf(number):
        return None
    return number


def _community_ids(value: Any) -> list[int]:
    if _missing(value):
        return []
    if isinstance(value, str):
        text = value.strip()
        if not text:
            return []
        value = json.loads(text)
    if not isinstance(value, (list, tuple)):
        return []
    ids: list[int] = []
    for item in value:
        if _missing(item):
            continue
        ids.append(int(item))
    return ids


def _json_text(value: Any) -> str | None:
    if _missing(value):
        return None
    if isinstance(value, str):
        return value
    return json.dumps(value, default=str)


def subfield_record(row: pd.Series, run_timestamp: str) -> dict[str, Any]:
    """One stakeholder subfield row, keyed by the citation run."""
    return {
        "run_timestamp": run_timestamp,
        "subfield_id": str(row["subfield_id"]),
        "proposed_journal": _text(row.get("proposed_journal")),
        "subfield": _text(row.get("taxonomy_subfield")),
        "field": _text(row.get("taxonomy_field")),
        "domain": _text(row.get("taxonomy_domain")),
        "grade": _text(row.get("grade")),
        "score": _int(row.get("score")),
        "world_2025": _int(row.get("mkt_2025")),
        "cagr": _float(row.get("cagr")),
        "fi_2025": _int(row.get("fi_articles_2025")),
        "share_vs_parity": _float(row.get("fi_share_vs_portfolio")),
        "lead_title": _text(row.get("lead_journal")),
        "ownership": _text(row.get("ownership_status")),
        "coverage": _text(row.get("coverage_status")),
        "scope_confidence": _text(row.get("scope_confidence")),
        "scope_names": _text(row.get("scope_names")),
        "section_themes": _text(row.get("section_themes")),
        "scope_community_ids": _community_ids(row.get("scope_community_ids")),
        "action": _text(row.get("action")),
        "action_reason": _text(row.get("action_reason")),
        "warning": _text(row.get("evidence_warnings")),
        "shortlist_rank": _int(row.get("shortlist_rank")),
    }


def run_record(manifest: dict, run_timestamp: str) -> dict[str, Any]:
    """One run row. The citation run id is the only timestamp stored."""
    return {
        "run_timestamp": run_timestamp,
        "openalex_works_modified": _text(manifest.get("openalex_works_modified")),
        "openalex_subfields_modified": _text(manifest.get("openalex_subfields_modified")),
        "market_base_year": _int(manifest.get("market_base_year")),
        "market_late_year": _int(manifest.get("market_late_year")),
        "market_min_annual": _int(manifest.get("market_min_annual")),
        "market_min_cagr": _float(manifest.get("market_min_cagr")),
        "scope_coverage_target": _float(manifest.get("scope_coverage_target")),
        "ownership_threshold": _float(manifest.get("ownership_threshold")),
        "greenfield_max_fi_3y": _int(manifest.get("greenfield_max_fi_3y")),
        "n_subfields": _int(manifest.get("n_subfields")),
        "n_market_qualified": _int(manifest.get("n_market_qualified")),
        "n_launch_candidates": _int(manifest.get("n_launch_candidates")),
        "n_shortlisted": _int(manifest.get("n_shortlisted")),
        "action_counts": _json_text(manifest.get("action_counts")),
        "coverage_counts": _json_text(manifest.get("coverage_counts")),
        "notes": _text(manifest.get("notes")),
    }


def _append(bq: bigquery.Client, table: str, rows: list[dict[str, Any]], fields) -> None:
    if not rows:
        raise RuntimeError(f"Refusing to append zero rows to {table}.")
    destination = _fq(table)
    if CLEAN_DATASET not in destination:
        raise RuntimeError("Refusing a write that does not target opportunity_clean.")
    job_config = bigquery.LoadJobConfig(
        schema=_schema(fields),
        write_disposition=bigquery.WriteDisposition.WRITE_APPEND,
        source_format=bigquery.SourceFormat.NEWLINE_DELIMITED_JSON,
    )
    job = bq.load_table_from_json(rows, destination, job_config=job_config)
    job.result()
    log.info("Appended %s rows to %s", f"{len(rows):,}", destination)


def publish_clean(
    frame: pd.DataFrame,
    manifest: dict,
    run_timestamp: str,
) -> dict[str, int]:
    """Append one citation run to opportunity_clean. Skip a run already stored."""
    if not TS_RE.match(run_timestamp or ""):
        raise ValueError(f"run_timestamp must be YYYYMMDD_HHMMSS, got {run_timestamp!r}")
    bq = _client()
    ensure_tables(bq)
    runs_n = run_present(bq, RUNS_TABLE, run_timestamp)
    subfields_n = run_present(bq, SUBFIELDS_TABLE, run_timestamp)
    if runs_n and subfields_n:
        log.info(
            "opportunity_clean already has %s (%s runs, %s subfields); leaving it unchanged",
            run_timestamp,
            runs_n,
            subfields_n,
        )
        return {"runs": runs_n, "subfields": subfields_n}
    if runs_n or subfields_n:
        raise RuntimeError(
            f"opportunity_clean has a partial copy of {run_timestamp} "
            f"(runs={runs_n}, subfields={subfields_n}). Nothing was deleted."
        )
    subfields = [subfield_record(row, run_timestamp) for _, row in frame.iterrows()]
    _append(bq, SUBFIELDS_TABLE, subfields, SUBFIELDS_FIELDS)
    _append(bq, RUNS_TABLE, [run_record(manifest, run_timestamp)], RUNS_FIELDS)
    written = {
        "runs": run_present(bq, RUNS_TABLE, run_timestamp),
        "subfields": run_present(bq, SUBFIELDS_TABLE, run_timestamp),
    }
    log.info(
        "opportunity_clean.%s %s runs, %s subfields",
        run_timestamp,
        written["runs"],
        written["subfields"],
    )
    return written


def copy_mapped_run(run_timestamp: str) -> dict[str, int]:
    """Insert an existing final slate into opportunity_clean. Source tables are read only."""
    if not TS_RE.match(run_timestamp or ""):
        raise ValueError(f"run_timestamp must be YYYYMMDD_HHMMSS, got {run_timestamp!r}")
    bq = _client()
    source_slate = (
        f"{C.BQ_PROJECT}.{C.BQ_OUT_DATASET}.final_journal_opportunities_{run_timestamp}"
    )
    source_manifest = (
        f"{C.BQ_PROJECT}.{C.BQ_OUT_DATASET}."
        f"final_journal_opportunities_manifest_{run_timestamp}"
    )
    before = {
        source_slate: int(bq.get_table(source_slate).num_rows or 0),
        source_manifest: int(bq.get_table(source_manifest).num_rows or 0),
    }
    ensure_tables(bq)
    runs_n = run_present(bq, RUNS_TABLE, run_timestamp)
    subfields_n = run_present(bq, SUBFIELDS_TABLE, run_timestamp)
    if runs_n and subfields_n:
        _assert_sources_unchanged(bq, before)
        log.info("opportunity_clean already has %s; source tables left unchanged", run_timestamp)
        return {"runs": runs_n, "subfields": subfields_n}
    if runs_n or subfields_n:
        raise RuntimeError(
            f"Partial copy of {run_timestamp} in opportunity_clean "
            f"(runs={runs_n}, subfields={subfields_n}). Nothing was deleted."
        )
    params = [bigquery.ScalarQueryParameter("ts", "STRING", run_timestamp)]
    _query(
        bq,
        f"""
        INSERT INTO `{_fq(SUBFIELDS_TABLE)}` (
          run_timestamp, subfield_id, proposed_journal, subfield, field, domain,
          grade, score, world_2025, cagr, fi_2025, share_vs_parity, lead_title,
          ownership, coverage, scope_confidence, scope_names, section_themes,
          scope_community_ids, action, action_reason, warning, shortlist_rank
        )
        SELECT
          @ts AS run_timestamp,
          CAST(subfield_id AS STRING) AS subfield_id,
          proposed_journal,
          taxonomy_subfield AS subfield,
          taxonomy_field AS field,
          taxonomy_domain AS domain,
          grade,
          CAST(score AS INT64) AS score,
          CAST(mkt_2025 AS INT64) AS world_2025,
          cagr,
          CAST(fi_articles_2025 AS INT64) AS fi_2025,
          fi_share_vs_portfolio AS share_vs_parity,
          lead_journal AS lead_title,
          ownership_status AS ownership,
          coverage_status AS coverage,
          scope_confidence,
          scope_names,
          section_themes,
          ARRAY(
            SELECT SAFE_CAST(community_id AS INT64)
            FROM UNNEST(
              IFNULL(JSON_VALUE_ARRAY(scope_community_ids), ARRAY<STRING>[])
            ) AS community_id
            WHERE SAFE_CAST(community_id AS INT64) IS NOT NULL
          ) AS scope_community_ids,
          action,
          action_reason,
          evidence_warnings AS warning,
          CAST(shortlist_rank AS INT64) AS shortlist_rank
        FROM `{source_slate}`
        """,
        params,
    )
    _query(
        bq,
        f"""
        INSERT INTO `{_fq(RUNS_TABLE)}` (
          run_timestamp, openalex_works_modified, openalex_subfields_modified,
          market_base_year, market_late_year, market_min_annual, market_min_cagr,
          scope_coverage_target, ownership_threshold, greenfield_max_fi_3y,
          n_subfields, n_market_qualified, n_launch_candidates, n_shortlisted,
          action_counts, coverage_counts, notes
        )
        SELECT
          @ts AS run_timestamp,
          openalex_works_modified,
          openalex_subfields_modified,
          market_base_year,
          market_late_year,
          market_min_annual,
          market_min_cagr,
          scope_coverage_target,
          ownership_threshold,
          greenfield_max_fi_3y,
          n_subfields,
          n_market_qualified,
          n_launch_candidates,
          n_shortlisted,
          action_counts,
          coverage_counts,
          notes
        FROM `{source_manifest}`
        """,
        params,
    )
    _assert_sources_unchanged(bq, before)
    written = {
        "runs": run_present(bq, RUNS_TABLE, run_timestamp),
        "subfields": run_present(bq, SUBFIELDS_TABLE, run_timestamp),
    }
    log.info(
        "Copied %s into opportunity_clean: %s runs, %s subfields. Sources unchanged: %s",
        run_timestamp,
        written["runs"],
        written["subfields"],
        before,
    )
    return written


def _assert_sources_unchanged(bq: bigquery.Client, before: dict[str, int]) -> None:
    after = {name: int(bq.get_table(name).num_rows or 0) for name in before}
    if after != before:
        raise RuntimeError(
            f"Source row counts changed. Before {before}. After {after}."
        )
