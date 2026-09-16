"""BigQuery input enrichment and mapper output (no local artifact files)."""

from __future__ import annotations

import json
import logging
import re

import pandas as pd

from . import config as C

log = logging.getLogger("opportunities.bq")

_TS_RE = re.compile(r"^\d{8}_\d{6}$")


def client():
    from google.cloud import bigquery

    return bigquery.Client(project=C.BQ_PROJECT, location=C.BQ_LOCATION)


def _assert_level(level: str) -> str:
    if level not in C.COMMUNITY_LEVELS:
        raise ValueError(f"level must be one of {C.COMMUNITY_LEVELS}, got {level!r}")
    return level


def fetch_frontiers_run_papers(
    run_timestamp: str,
    level: str | None = None,
    drilldown: str | None = None,
) -> pd.DataFrame:
    """Every Frontiers paper in the scope-drift run (not a journal subset).

    `community_id` is the chosen level; `drilldown_id` is the finer level kept
    alongside it so a shortlisted community can be opened up without a re-query.
    """
    level = _assert_level(level or C.COMMUNITY_LEVEL)
    drill = _assert_level(drilldown or C.DRILLDOWN_LEVEL)
    tbl_c = f"{C.BQ_PROJECT}.{C.BQ_DATASET}.classification_raw_{run_timestamp}"
    tbl_m = f"{C.BQ_PROJECT}.{C.BQ_DATASET}.pub_metadata_raw_{run_timestamp}"
    q = f"""
    SELECT
      CAST(c.int_id AS INT64) AS int_id,
      CAST(c.{level} AS INT64) AS community_id,
      CAST(c.{drill} AS INT64) AS drilldown_id,
      '{level}' AS community_level,
      '{drill}' AS drilldown_level,
      CAST(m.pub_id AS STRING) AS pub_id,
      CAST(m.journal AS STRING) AS journal,
      CAST(m.title AS STRING) AS title,
      EXTRACT(YEAR FROM SAFE.PARSE_DATE('%Y-%m-%d', SUBSTR(CAST(m.date AS STRING), 1, 10))) AS year
    FROM `{tbl_c}` c
    JOIN `{tbl_m}` m ON c.int_id = m.int_id
    -- is_frontiers only: a `journal LIKE 'frontiers%'` fallback also matches 144
    -- other publishers' titles (IOS Press, IMR Press, Elsevier, BMC), while the
    -- flag correctly keeps partnership titles such as Dystonia that are not
    -- named "Frontiers in ...".
    WHERE CAST(m.is_frontiers AS STRING) IN ('1', 'true', 'True')
      AND m.journal IS NOT NULL
      AND m.journal != ''
    """
    df = client().query(q).to_dataframe()
    df = df.dropna(subset=["journal", "community_id", "year", "int_id"])
    df["year"] = df["year"].astype(int)
    df["community_id"] = df["community_id"].astype(int)
    df["int_id"] = df["int_id"].astype(int)
    log.info(
        "P0 BQ: %s Frontiers papers, %s journals, %s %s communities",
        f"{len(df):,}",
        df["journal"].nunique(),
        df["community_id"].nunique(),
        level,
    )
    return df


def fetch_cluster_labels(run_timestamp: str, level: str | None = None) -> pd.DataFrame:
    """Taxonomy labels for one cluster level from `taxonomy_labelling`.

    Handles both table layouts: the consolidated `labels_dashboard_{ts}` written
    by the current taxonomy_naming, and the older per-level
    `cluster_labels_{level}_{ts}`.
    """
    level = _assert_level(level or C.COMMUNITY_LEVEL)
    ds = f"{C.BQ_PROJECT}.{C.BQ_LABEL_DATASET}"
    consolidated = f"{ds}.labels_dashboard_{run_timestamp}"
    per_level = f"{ds}.cluster_labels_{level}_{run_timestamp}"
    cli = client()
    for fq, needs_filter in ((consolidated, True), (per_level, False)):
        where = (
            f"WHERE classification_join_column = '{level}'" if needs_filter else ""
        )
        q = f"""
        SELECT
          CAST(cluster_id AS INT64) AS community_id,
          CAST(short_label AS STRING) AS community_label,
          CAST(summary AS STRING) AS community_summary
        FROM `{fq}`
        {where}
        """
        try:
            df = cli.query(q).to_dataframe()
        except Exception as exc:
            log.debug("labels not in %s (%s)", fq, str(exc)[:120])
            continue
        df = df.dropna(subset=["community_id"])
        if df.empty:
            continue
        df["community_id"] = df["community_id"].astype(int)
        df = df.drop_duplicates("community_id")
        log.info("labels: %s %s labels from %s", len(df), level, fq)
        return df
    log.warning(
        "No %s labels found in %s for run %s — communities will be unlabelled, "
        "which disables the market match. Run taxonomy_naming for this timestamp.",
        level,
        ds,
        run_timestamp,
    )
    return pd.DataFrame(columns=["community_id", "community_label", "community_summary"])


def fetch_l2_topics(
    run_timestamp: str,
    level: str | None = None,
    share_floor: float | None = None,
) -> pd.DataFrame:
    """Per-cluster naming evidence: the L1 rollup, plus the L2 detail under it.

    `unit_name` is what a unit should be called. It comes from the cluster's
    leading L1 parent aggregated over every L2 row, so it is backed by the whole
    cluster rather than by the handful of leaf terms that topped a sample. The
    L2 fields stay as supporting detail — they say what sits inside the unit,
    not what the unit is.

    Returns one row per cluster with:

      `unit_name`             L1 rollup, qualified by the leading L2 term where
                              the L1 name repeats across clusters
      `l1_roll_share`         share of the cluster the rollup accounts for
      `l2_name` / `l2_share`  top topic, only when it clears the share floor
      `topic_list`            gated topics in rank order
      `topic_compound`        leading terms regardless of share

    Older tables predate the rollup; those clusters fall back to the compound
    label and `l1_roll_share` stays at zero.
    """
    level = _assert_level(level or C.DRILLDOWN_LEVEL)
    floor = C.L2_SHARE_FLOOR if share_floor is None else float(share_floor)
    fq = (
        f"{C.BQ_PROJECT}.{C.BQ_LABEL_DATASET}."
        f"{C.L2_TOPICS_PREFIX}_{level}_{run_timestamp}"
    )
    cols = [
        "cluster_id",
        "unit_name",
        "l1_roll_name",
        "l1_roll_share",
        "l2_key",
        "l2_name",
        "l2_share",
        "l1_name",
        "topic_list",
        "topic_compound",
    ]
    q = f"SELECT * FROM `{fq}`"
    try:
        df = client().query(q).to_dataframe()
    except Exception as exc:
        log.warning(
            "No L2 topics table %s (%s) — rows will fall back to the L1 "
            "community label. Run taxonomy_naming for this timestamp.",
            fq,
            str(exc)[:120],
        )
        return pd.DataFrame(columns=cols)
    if df.empty:
        log.warning("L2 topics table %s is empty", fq)
        return pd.DataFrame(columns=cols)

    df["cluster_id"] = df["cluster_id"].astype("int64")
    df["l2_rank"] = df["l2_rank"].astype("int64")
    df = df.sort_values(["cluster_id", "l2_rank", "l2_key"])
    compound = df[df["l2_rank"] <= C.L2_COMPOUND_TERMS].groupby("cluster_id")[
        "l2_name"
    ].apply(lambda s: " / ".join(str(x) for x in s if str(x).strip()))

    gated = df[df["l2_share"] >= floor]
    topic_list = gated.groupby("cluster_id")["l2_name"].apply(
        lambda s: "; ".join(str(x) for x in s)
    )
    gated_top = gated.groupby("cluster_id", as_index=False).first()

    first = df.groupby("cluster_id", as_index=False).first()
    out = first[["cluster_id", "l1_name"]].copy()
    for col, default in (
        ("unit_name", ""),
        ("l1_roll_name", ""),
        ("l1_roll_share", 0.0),
    ):
        out[col] = (
            first[col].fillna(default) if col in first.columns else default
        )
    lookup = gated_top.set_index("cluster_id")
    out["l2_key"] = (
        out["cluster_id"].map(lookup["l2_key"]).astype("string").fillna("")
    )
    out["l2_name"] = out["cluster_id"].map(lookup["l2_name"]).fillna("")
    out["l2_share"] = out["cluster_id"].map(lookup["l2_share"]).fillna(0.0)
    out["topic_list"] = out["cluster_id"].map(topic_list).fillna("")
    out["topic_compound"] = out["cluster_id"].map(compound).fillna("")
    out = out[cols]
    n_roll = int((out["unit_name"].astype(str).str.strip() != "").sum())
    log.info(
        "naming %s clusters: %s named from the L1 rollup (median %.0f%% of the "
        "cluster), %s fall back to a compound of leading L2 terms ← %s",
        f"{len(out):,}",
        f"{n_roll:,}",
        out.loc[out["l1_roll_share"] > 0, "l1_roll_share"].median() * 100
        if n_roll
        else 0.0,
        f"{len(out) - n_roll:,}",
        fq,
    )
    return out


def fetch_paper_scope(run_timestamp: str) -> pd.DataFrame:
    """Per-paper scope flags from BigQuery, if build_unified_dashboard wrote them.

    Optional: the dashboard only covers its configured journal list, so this is
    usually a subset. Missing papers are treated as in-scope by the caller.
    """
    fq = f"{C.BQ_PROJECT}.{C.BQ_DATASET}.{C.PAPER_SCOPE_PREFIX}_{run_timestamp}"
    q = f"""
    SELECT
      CAST(int_id AS INT64) AS int_id,
      CAST(journal AS STRING) AS journal,
      CAST(scope_code AS INT64) AS scope_code,
      CAST(is_oos AS BOOL) AS is_oos,
      CAST(is_borderline AS BOOL) AS is_borderline
    FROM `{fq}`
    """
    try:
        df = client().query(q).to_dataframe()
    except Exception as exc:
        log.info(
            "No paper scope table for run %s (%s) — all papers treated as in-scope",
            run_timestamp,
            str(exc)[:100],
        )
        return pd.DataFrame(
            columns=["int_id", "journal", "scope_code", "is_oos", "is_borderline"]
        )
    log.info(
        "paper scope: %s rows, %s journals ← %s",
        f"{len(df):,}",
        df["journal"].nunique() if len(df) else 0,
        fq,
    )
    return df


def fetch_jd_opportunities() -> pd.DataFrame:
    """JD-strategy market reference table (not per-run).

    Loaded once by `python src/opportunities/seed_jd.py`. Read-only here.
    """
    fq = f"{C.BQ_PROJECT}.{C.BQ_OUT_DATASET}.{C.JD_TABLE}"
    try:
        df = client().query(f"SELECT * FROM `{fq}`").to_dataframe()
    except Exception as exc:
        log.warning(
            "JD market table %s unavailable (%s) — market overlay will be empty. "
            "Load it with: python src/opportunities/seed_jd.py",
            fq,
            str(exc)[:120],
        )
        return pd.DataFrame()
    log.info("JD market: %s subfields ← %s", len(df), fq)
    return df


def fetch_existing_sections() -> pd.DataFrame:
    q = f"""
    SELECT
      t.journal,
      t.section,
      t.section_id,
      COUNT(*) AS n_articles
    FROM `{C.RDM_ARTICLE}` a
    JOIN `{C.RDM_TAXONOMY}` t
      ON a.taxonomy_id = t.taxonomy_id
    WHERE a.space_id = 1
      AND a.is_deleted = FALSE
      AND a.is_published = TRUE
      AND t.type = 'Specialty Section'
      AND t.section IS NOT NULL
    GROUP BY 1, 2, 3
    HAVING COUNT(*) >= 5
    """
    try:
        return client().query(q).to_dataframe()
    except Exception as exc:
        log.warning("existing sections skipped: %s", exc)
        return pd.DataFrame(columns=["journal", "section", "section_id", "n_articles"])


def fetch_rt_section(journals: list[str], year_from: int, year_to: int) -> pd.DataFrame:
    """One row per (journal, normalised title) with its Research Topic, if any.

    Filtered to the journals actually in the run and deduplicated in SQL — the
    unfiltered version of this query returns ~584k rows for every run.
    """
    from google.cloud import bigquery

    q = f"""
    WITH src AS (
      SELECT
        CAST(t.journal AS STRING) AS journal,
        LOWER(TRIM(REGEXP_REPLACE(a.article_title, r'\\s+', ' '))) AS title_norm,
        t.section,
        t.section_id,
        t.type AS taxonomy_type,
        rt.research_topic_id,
        rt.title AS research_topic_title
      FROM `{C.RDM_ARTICLE}` a
      JOIN `{C.RDM_TAXONOMY}` t
        ON a.taxonomy_id = t.taxonomy_id
      LEFT JOIN `{C.RDM_RT}` rt
        ON a.article_research_topic_id = rt.research_topic_id
      WHERE a.space_id = 1
        AND a.is_deleted = FALSE
        AND a.is_published = TRUE
        AND CAST(t.journal AS STRING) IN UNNEST(@journals)
        AND a.article_title IS NOT NULL
        AND EXTRACT(YEAR FROM COALESCE(a.first_publish_date, a.stage_date_published, a.create_date))
            BETWEEN @year_from AND @year_to
    )
    SELECT * FROM src
    QUALIFY ROW_NUMBER() OVER (
      PARTITION BY journal, title_norm
      -- prefer a row that actually carries a Research Topic
      ORDER BY CASE WHEN research_topic_id IS NULL THEN 1 ELSE 0 END
    ) = 1
    """
    cfg = bigquery.QueryJobConfig(
        query_parameters=[
            bigquery.ArrayQueryParameter("journals", "STRING", list(journals)),
            bigquery.ScalarQueryParameter("year_from", "INT64", int(year_from)),
            bigquery.ScalarQueryParameter("year_to", "INT64", int(year_to)),
        ]
    )
    df = client().query(q, job_config=cfg).to_dataframe()
    log.info("RT lookup: %s unique (journal, title) rows", f"{len(df):,}")
    return df


# --- mapper output (opportunity_mapping) ------------------------------------


def table_id(name: str, run_timestamp: str) -> str:
    return f"{C.BQ_OUT_DATASET}.{name}_{run_timestamp}"


def fq_table(name: str, run_timestamp: str) -> str:
    return f"{C.BQ_PROJECT}.{table_id(name, run_timestamp)}"


def ensure_output_dataset() -> None:
    from google.cloud.exceptions import NotFound

    bq = client()
    ds_id = f"{C.BQ_PROJECT}.{C.BQ_OUT_DATASET}"
    try:
        bq.get_dataset(ds_id)
    except NotFound:
        from google.cloud import bigquery

        ds = bigquery.Dataset(ds_id)
        ds.location = C.BQ_LOCATION
        bq.create_dataset(ds, exists_ok=True)
        log.info("Created BigQuery dataset %s (%s)", ds_id, C.BQ_LOCATION)


def _prepare_df(df: pd.DataFrame, run_timestamp: str) -> pd.DataFrame:
    out = df.copy()
    if "run_timestamp" not in out.columns:
        out.insert(0, "run_timestamp", run_timestamp)
    else:
        out["run_timestamp"] = run_timestamp

    def _cell(x):
        if x is None:
            return None
        if isinstance(x, (dict, list, tuple)):
            return json.dumps(x, default=str)
        try:
            if pd.isna(x):
                return None
        except (TypeError, ValueError):
            pass
        return x

    for col in out.columns:
        s = out[col]
        if str(s.dtype) == "boolean":
            out[col] = s.astype(object).where(s.notna(), None)
        elif s.dtype == object:
            # Only pay for the per-cell pass when the column can actually hold
            # containers or NaN; papers/title columns are plain strings.
            head = s.head(1000)
            if head.map(lambda x: isinstance(x, (dict, list, tuple))).any() or s.isna().any():
                out[col] = s.map(_cell)
    return out


def write_reference_table(df: pd.DataFrame, name: str) -> str:
    """Replace an un-versioned reference table (no run_timestamp column)."""
    import pandas_gbq

    pandas_gbq.context.location = C.BQ_LOCATION
    ensure_output_dataset()
    dest = f"{C.BQ_OUT_DATASET}.{name}"
    fq = f"{C.BQ_PROJECT}.{dest}"
    if df is None or df.empty:
        raise ValueError(f"refusing to write empty reference table {fq}")
    pandas_gbq.to_gbq(
        df,
        dest,
        project_id=C.BQ_PROJECT,
        if_exists="replace",
        location=C.BQ_LOCATION,
    )
    log.info("BQ wrote %s reference rows → %s", f"{len(df):,}", fq)
    return fq


def write_table(df: pd.DataFrame | None, name: str, run_timestamp: str) -> str:
    """Replace `opportunity_mapping.{name}_{timestamp}`. Empty frame deletes the table."""
    import pandas_gbq

    pandas_gbq.context.location = C.BQ_LOCATION
    ensure_output_dataset()
    dest = table_id(name, run_timestamp)
    fq = fq_table(name, run_timestamp)
    if df is None or df.empty:
        _delete_table(name, run_timestamp)
        log.info("BQ skip (empty): %s", fq)
        return fq
    prepared = _prepare_df(df, run_timestamp)
    kwargs = {}
    if len(prepared) > 50_000:
        kwargs["chunksize"] = 50_000
    pandas_gbq.to_gbq(
        prepared,
        dest,
        project_id=C.BQ_PROJECT,
        if_exists="replace",
        location=C.BQ_LOCATION,
        **kwargs,
    )
    log.info("BQ wrote %s rows → %s", f"{len(prepared):,}", fq)
    return fq


def write_json_row(obj: dict, name: str, run_timestamp: str) -> str:
    row = {k: (json.dumps(v, default=str) if isinstance(v, (dict, list)) else v) for k, v in obj.items()}
    return write_table(pd.DataFrame([row]), name, run_timestamp)


def read_table(name: str, run_timestamp: str) -> pd.DataFrame:
    import pandas_gbq

    pandas_gbq.context.location = C.BQ_LOCATION
    fq = fq_table(name, run_timestamp)
    sql = f"SELECT * FROM `{fq}`"
    df = pandas_gbq.read_gbq(
        sql,
        project_id=C.BQ_PROJECT,
        location=C.BQ_LOCATION,
        progress_bar_type=None,
    )
    log.info("BQ read %s rows ← %s", f"{len(df):,}", fq)
    return df


def table_exists(name: str, run_timestamp: str) -> bool:
    from google.cloud.exceptions import NotFound

    try:
        client().get_table(fq_table(name, run_timestamp))
        return True
    except NotFound:
        return False


def _delete_table(name: str, run_timestamp: str) -> None:
    client().delete_table(fq_table(name, run_timestamp), not_found_ok=True)


def list_run_timestamps() -> list[str]:
    ds_id = f"{C.BQ_PROJECT}.{C.BQ_OUT_DATASET}"
    try:
        tables = client().list_tables(ds_id)
    except Exception as exc:
        log.warning("list opportunity_mapping tables: %s", exc)
        return []
    stamps = set()
    for t in tables:
        tid = t.table_id
        if not tid.startswith("decisions_"):
            continue
        ts = tid[len("decisions_") :]
        if _TS_RE.match(ts):
            stamps.add(ts)
    return sorted(stamps)


def previous_run_timestamp(current_run: str) -> str | None:
    stamps = [s for s in list_run_timestamps() if s != current_run]
    return stamps[-1] if stamps else None


def previous_decisions(current_run: str) -> pd.DataFrame | None:
    prev = previous_run_timestamp(current_run)
    if not prev:
        return None
    try:
        return read_table("decisions", prev)
    except Exception as exc:
        log.warning("previous decisions %s: %s", prev, exc)
        return None
