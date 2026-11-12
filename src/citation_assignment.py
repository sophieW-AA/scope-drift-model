"""
Place new Frontiers papers into an existing Leiden run by what they cite.

The communities stay as Leiden left them. A new paper is filed under the
community that holds the most weight among papers it cites, at the finest
level that clears the cutoff. Same-journal citations count at half weight.
Papers with fewer than two in-network citations are left out. Taxonomy
assignment can place those when run with --few-citations. A paper with
enough citations but no clear winning community stays unplaced.

Nothing is written unless --write is passed. --dest copies the run first and
leaves the source tables alone. --in-place edits the source run.

    python src/citation_assignment.py --timestamp 20260827_081311
    python src/citation_assignment.py --timestamp 20260827_081311 --through-year 2026 --dest 20261111_160000 --write
    python src/citation_assignment.py --timestamp 20260827_081311 --in-place --write

The share and margin cutoffs have not been checked against a holdout.
"""

from __future__ import annotations

import argparse
import logging
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd
from google.api_core.exceptions import NotFound
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
BQ_LABEL_DATASET = "taxonomy_labelling"
BQ_LOCATION = "EU"
AIRAK_PUBLICATION = "ocean-breeze-tier-1.airak.Publication"
AIRAK_JOURNAL = "ocean-breeze-tier-1.airak.Journal"
AIRAK_CITATION = "ocean-breeze-tier-1.airak.PublicationCitation"

# Same discount the export uses when it builds the graph.
SELF_CITE_JOURNAL_WEIGHT = 0.5
TEMPORAL_DECAY_TAU = 5.0
# Uncalibrated. A paper needs two cited papers inside the run, the winner
# needs half of that weight, and a 20 point gap over the next community.
MIN_CITATIONS = 2
MIN_SHARE = 0.5
MIN_MARGIN = 0.20

NETWORK_SUFFIXES = (
    "pubs_raw",
    "pub_metadata_raw",
    "cit_links_raw",
    "classification_raw",
    "run_metadata",
)
LABEL_PREFIXES = (
    "cluster_labels",
    "cluster_taxonomy_labels",
    "cluster_l2_topics",
)
LEVELS = ("micro", "meso", "macro")
TS_RE = re.compile(r"^\d{8}_\d{6}$")

LOG_DIR = Path(r"C:\Users\sophie.wilson\Documents\scope_drift_outputs\logs\citation_assignment")
log = logging.getLogger("citation_assignment")


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
        LOG_DIR / f"citation_assignment_{run_timestamp}.log", encoding="utf-8"
    )
    file_handler.setFormatter(fmt)
    root.addHandler(stream_handler)
    root.addHandler(file_handler)


def require_timestamp(timestamp: str, label: str) -> str:
    ts = (timestamp or "").strip()
    if not TS_RE.match(ts):
        raise SystemExit(f"{label} must be YYYYMMDD_HHMMSS. Got {timestamp!r}.")
    return ts


def client() -> bigquery.Client:
    return bigquery.Client(project=BQ_BILL_PROJECT, location=BQ_LOCATION)


def table_id(suffix: str, timestamp: str) -> str:
    return f"{BQ_PROJECT}.{BQ_DATASET}.{suffix}_{timestamp}"


def label_id(prefix: str, level: str, timestamp: str) -> str:
    return f"{BQ_PROJECT}.{BQ_LABEL_DATASET}.{prefix}_{level}_{timestamp}"


def table_exists(bq: bigquery.Client, table: str) -> bool:
    try:
        bq.get_table(table)
    except NotFound:
        return False
    return True


def column_names(bq: bigquery.Client, table: str) -> set[str]:
    return {field.name for field in bq.get_table(table).schema}


def query_df(bq: bigquery.Client, sql: str) -> pd.DataFrame:
    job = bq.query(sql)
    frame = job.result().to_dataframe()
    log.info("  query processed %s bytes", f"{job.total_bytes_processed or 0:,}")
    return frame


def run_script(bq: bigquery.Client, sql: str) -> pd.DataFrame:
    job = bq.query(sql)
    frame = job.result().to_dataframe()
    log.info("  script processed %s bytes", f"{job.total_bytes_processed or 0:,}")
    return frame


def load_run_bounds(bq: bigquery.Client, timestamp: str) -> tuple[int, int, str]:
    table = table_id("run_metadata", timestamp)
    if not table_exists(bq, table):
        raise SystemExit(f"Missing {table}")
    frame = query_df(
        bq,
        f"""
        SELECT
          CAST(start_year AS INT64) AS start_year,
          CAST(end_year AS INT64) AS end_year,
          journal_ids
        FROM `{table}`
        LIMIT 1
        """,
    )
    if frame.empty:
        raise SystemExit(f"{table} has no rows")
    row = frame.iloc[0]
    if pd.isna(row["start_year"]) or pd.isna(row["end_year"]):
        raise SystemExit(f"{table} has no start_year or end_year")
    journal_ids = "" if pd.isna(row["journal_ids"]) else str(row["journal_ids"]).strip()
    if not journal_ids:
        raise SystemExit(f"{table} has no journal_ids, so there is no journal set to extend")
    return int(row["start_year"]), int(row["end_year"]), journal_ids


def leiden_predicate(alias: str, *, column_present: bool, backfilled: bool) -> str:
    if backfilled:
        return f"{alias}.assignment_method = 'leiden'"
    if column_present:
        return (
            f"({alias}.assignment_method IS NULL "
            f"OR {alias}.assignment_method = 'leiden')"
        )
    return "TRUE"


def vote_sql(level: str) -> str:
    return f"""
    CREATE TEMP TABLE {level}_vote AS
    WITH summed AS (
      SELECT pub_id, {level} AS cluster_id, SUM(weight) AS weight
      FROM cited_community
      WHERE {level} IS NOT NULL
      GROUP BY pub_id, cluster_id
    ),
    ranked AS (
      SELECT
        pub_id,
        cluster_id,
        weight,
        SUM(weight) OVER (PARTITION BY pub_id) AS total_weight,
        ROW_NUMBER() OVER (
          PARTITION BY pub_id ORDER BY weight DESC, cluster_id
        ) AS rn
      FROM summed
    )
    SELECT
      pub_id,
      MAX(IF(rn = 1, cluster_id, NULL)) AS cluster_id,
      SAFE_DIVIDE(MAX(IF(rn = 1, weight, NULL)), ANY_VALUE(total_weight)) AS share,
      SAFE_DIVIDE(
        MAX(IF(rn = 1, weight, NULL)) - IFNULL(MAX(IF(rn = 2, weight, NULL)), 0),
        ANY_VALUE(total_weight)
      ) AS margin
    FROM ranked
    WHERE rn <= 2
    GROUP BY pub_id;
    """


def assignment_script(
    ts: dict[str, str],
    *,
    through_year: int,
    leiden_on: str,
    write: bool,
    reset: bool,
    source_timestamp: str,
    dest_timestamp: str,
) -> str:
    """Build the BigQuery script. `leiden_on` is a boolean SQL expression."""
    preamble = ""
    insert_sql = ""
    if write:
        reset_sql = ""
        if reset:
            reset_sql = f"""
            CREATE TEMP TABLE old_citation AS
            SELECT CAST(int_id AS INT64) AS int_id
            FROM `{ts["classif"]}`
            WHERE assignment_method = 'citation';

            DELETE FROM `{ts["links"]}`
            WHERE CAST(int_id1 AS INT64) IN (SELECT int_id FROM old_citation)
               OR CAST(int_id2 AS INT64) IN (SELECT int_id FROM old_citation);

            DELETE FROM `{ts["classif"]}`
            WHERE assignment_method = 'citation';

            DELETE FROM `{ts["pubs"]}`
            WHERE CAST(int_id AS INT64) IN (SELECT int_id FROM old_citation);

            DELETE FROM `{ts["meta"]}`
            WHERE CAST(int_id AS INT64) IN (SELECT int_id FROM old_citation);
            """
        generated = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
        timestamp_sql = ""
        if dest_timestamp != source_timestamp:
            timestamp_sql = f"run_timestamp = '{dest_timestamp}',"
        preamble = f"""
        ALTER TABLE `{ts["classif"]}`
          ADD COLUMN IF NOT EXISTS assignment_method STRING,
          ADD COLUMN IF NOT EXISTS assignment_level STRING,
          ADD COLUMN IF NOT EXISTS assignment_confidence FLOAT64,
          ADD COLUMN IF NOT EXISTS assignment_margin FLOAT64,
          ADD COLUMN IF NOT EXISTS exclusion_reason STRING,
          ADD COLUMN IF NOT EXISTS taxonomy_top_topic STRING;

        UPDATE `{ts["classif"]}`
        SET assignment_method = 'leiden'
        WHERE assignment_method IS NULL;

        {reset_sql}
        """
        insert_sql = f"""
        CREATE TEMP TABLE new_rows AS
        SELECT
          (SELECT IFNULL(MAX(CAST(int_id AS INT64)), -1) FROM `{ts["pubs"]}`)
            + ROW_NUMBER() OVER (ORDER BY pub_id) AS int_id,
          pub_id,
          journal,
          date,
          title,
          macro,
          meso,
          micro,
          assignment_level,
          assignment_confidence,
          assignment_margin
        FROM placed;

        INSERT INTO `{ts["pubs"]}` (int_id, core_pub)
        SELECT int_id, 1 FROM new_rows;

        INSERT INTO `{ts["meta"]}` (int_id, pub_id, is_frontiers, journal, date, title)
        SELECT int_id, pub_id, 1, journal, date, title FROM new_rows;

        INSERT INTO `{ts["classif"]}` (
          int_id, macro, meso, micro, assignment_method, assignment_level,
          assignment_confidence, assignment_margin
        )
        SELECT
          int_id, macro, meso, micro, 'citation', assignment_level,
          assignment_confidence, assignment_margin
        FROM new_rows;

        INSERT INTO `{ts["links"]}` (int_id1, int_id2, weight)
        SELECT int_id1, int_id2, SUM(weight) AS weight
        FROM (
          SELECT n.int_id AS int_id1, d.cited_int_id AS int_id2, d.weight
          FROM new_rows n
          JOIN cited_community d ON d.pub_id = n.pub_id
          UNION ALL
          SELECT d.cited_int_id AS int_id1, n.int_id AS int_id2, d.weight
          FROM new_rows n
          JOIN cited_community d ON d.pub_id = n.pub_id
        )
        GROUP BY int_id1, int_id2;

        ALTER TABLE `{ts["run"]}`
          ADD COLUMN IF NOT EXISTS citation_source_run STRING;

        UPDATE `{ts["run"]}`
        SET
          {timestamp_sql}
          end_year = GREATEST(CAST(end_year AS INT64), {through_year}),
          citation_source_run = '{source_timestamp}',
          generated_utc = '{generated}'
        WHERE TRUE;
        """

    return f"""
    {preamble}
    CREATE TEMP TABLE existing AS
    SELECT
      SAFE_CAST(pub_id AS INT64) AS pub_id,
      CAST(int_id AS INT64) AS int_id
    FROM `{ts["meta"]}`
    WHERE SAFE_CAST(pub_id AS INT64) IS NOT NULL;

    CREATE TEMP TABLE candidates AS
    SELECT
      p.PublicationId AS pub_id,
      p.JournalId AS journal_id,
      IFNULL(j.DisplayName, '') AS journal,
      COALESCE(
        CAST(p.PublishedDate AS STRING),
        CAST(p.PublishedYear AS STRING),
        '0000-01-01'
      ) AS date,
      REPLACE(REPLACE(IFNULL(p.Title, ''), '\\t', ' '), '\\n', ' ') AS title
    FROM `{AIRAK_PUBLICATION}` p
    JOIN `{AIRAK_JOURNAL}` j ON p.JournalId = j.JournalId
    JOIN (
      SELECT DISTINCT CAST(journal_raw AS INT64) AS journal_id
      FROM UNNEST(JSON_VALUE_ARRAY({journal_ids_sql(ts["run"])})) AS journal_raw
    ) journals ON p.JournalId = journals.journal_id
    LEFT JOIN existing e ON e.pub_id = p.PublicationId
    WHERE p.PublishedYear BETWEEN {ts["start_year"]} AND {through_year}
      AND e.pub_id IS NULL;

    CREATE TEMP TABLE cited AS
    SELECT DISTINCT
      c.pub_id,
      c.journal_id AS src_journal,
      cited_pub.PublicationId AS cited_pub_id,
      cited_pub.JournalId AS cited_journal,
      cited_pub.PublishedYear AS cited_year,
      ex.int_id AS cited_int_id
    FROM candidates c
    JOIN `{AIRAK_CITATION}` pc ON pc.PublicationId = c.pub_id
    JOIN `{AIRAK_PUBLICATION}` cited_pub
      ON cited_pub.PublicationId = pc.CitedPublicationId
    JOIN existing ex ON ex.pub_id = cited_pub.PublicationId
    WHERE cited_pub.PublicationId != c.pub_id;

    CREATE TEMP TABLE cited_community AS
    SELECT
      d.pub_id,
      d.cited_int_id,
      IF(d.src_journal = d.cited_journal, {SELF_CITE_JOURNAL_WEIGHT}, 1.0)
        * GREATEST(
            EXP(
              -SAFE_DIVIDE(
                CAST({through_year} AS FLOAT64)
                  - CAST(IFNULL(d.cited_year, {through_year}) AS FLOAT64),
                {TEMPORAL_DECAY_TAU}
              )
            ),
            0.01
          ) AS weight,
      CAST(cl.micro AS INT64) AS micro,
      CAST(cl.meso AS INT64) AS meso,
      CAST(cl.macro AS INT64) AS macro
    FROM cited d
    JOIN `{ts["classif"]}` cl ON CAST(cl.int_id AS INT64) = d.cited_int_id
    WHERE {leiden_on.replace("c.", "cl.")};

    CREATE TEMP TABLE paper_support AS
    SELECT pub_id, COUNT(DISTINCT cited_int_id) AS n_citations
    FROM cited_community
    GROUP BY pub_id;

    {vote_sql("micro")}
    {vote_sql("meso")}
    {vote_sql("macro")}

    CREATE TEMP TABLE micro_parent AS
    SELECT
      CAST(c.micro AS INT64) AS micro_id,
      (APPROX_TOP_COUNT(CAST(c.meso AS INT64), 1)[SAFE_OFFSET(0)]).value AS meso_id,
      (APPROX_TOP_COUNT(CAST(c.macro AS INT64), 1)[SAFE_OFFSET(0)]).value AS macro_id
    FROM `{ts["classif"]}` c
    WHERE c.micro IS NOT NULL
      AND {leiden_on}
    GROUP BY micro_id;

    CREATE TEMP TABLE meso_parent AS
    SELECT
      CAST(c.meso AS INT64) AS meso_id,
      (APPROX_TOP_COUNT(CAST(c.macro AS INT64), 1)[SAFE_OFFSET(0)]).value AS macro_id
    FROM `{ts["classif"]}` c
    WHERE c.meso IS NOT NULL
      AND {leiden_on}
    GROUP BY meso_id;

    CREATE TEMP TABLE placed AS
    WITH decided AS (
      SELECT
        c.pub_id,
        c.journal,
        c.date,
        c.title,
        s.n_citations,
        i.cluster_id AS micro_id,
        i.share AS micro_share,
        i.margin AS micro_margin,
        m.cluster_id AS meso_id,
        m.share AS meso_share,
        m.margin AS meso_margin,
        g.cluster_id AS macro_id,
        g.share AS macro_share,
        g.margin AS macro_margin,
        (s.n_citations >= {MIN_CITATIONS} AND i.share >= {MIN_SHARE} AND i.margin >= {MIN_MARGIN}) AS micro_ok,
        (s.n_citations >= {MIN_CITATIONS} AND m.share >= {MIN_SHARE} AND m.margin >= {MIN_MARGIN}) AS meso_ok,
        (s.n_citations >= {MIN_CITATIONS} AND g.share >= {MIN_SHARE} AND g.margin >= {MIN_MARGIN}) AS macro_ok
      FROM candidates c
      JOIN paper_support s ON s.pub_id = c.pub_id
      LEFT JOIN micro_vote i ON i.pub_id = c.pub_id
      LEFT JOIN meso_vote m ON m.pub_id = c.pub_id
      LEFT JOIN macro_vote g ON g.pub_id = c.pub_id
    )
    SELECT
      d.pub_id,
      d.journal,
      d.date,
      d.title,
      CASE
        WHEN d.micro_ok THEN mp.macro_id
        WHEN d.meso_ok THEN sp.macro_id
        ELSE d.macro_id
      END AS macro,
      CASE
        WHEN d.micro_ok THEN mp.meso_id
        WHEN d.meso_ok THEN d.meso_id
        ELSE CAST(NULL AS INT64)
      END AS meso,
      CASE
        WHEN d.micro_ok THEN d.micro_id
        ELSE CAST(NULL AS INT64)
      END AS micro,
      CASE
        WHEN d.micro_ok THEN 'micro'
        WHEN d.meso_ok THEN 'meso'
        ELSE 'macro'
      END AS assignment_level,
      CASE
        WHEN d.micro_ok THEN d.micro_share
        WHEN d.meso_ok THEN d.meso_share
        ELSE d.macro_share
      END AS assignment_confidence,
      CASE
        WHEN d.micro_ok THEN d.micro_margin
        WHEN d.meso_ok THEN d.meso_margin
        ELSE d.macro_margin
      END AS assignment_margin
    FROM decided d
    LEFT JOIN micro_parent mp ON mp.micro_id = d.micro_id
    LEFT JOIN meso_parent sp ON sp.meso_id = d.meso_id
    WHERE d.micro_ok OR d.meso_ok OR d.macro_ok;

    {insert_sql}

    SELECT
      {through_year} AS through_year,
      (SELECT COUNT(*) FROM candidates) AS n_candidates,
      (SELECT COUNT(*) FROM paper_support) AS n_with_citation,
      (
        SELECT COUNT(*)
        FROM candidates c
        LEFT JOIN paper_support s ON s.pub_id = c.pub_id
        WHERE s.pub_id IS NULL
      ) AS n_no_citation,
      (
        SELECT COUNTIF(n_citations < {MIN_CITATIONS}) FROM paper_support
      ) AS n_below_min_citations,
      (
        SELECT COUNT(*)
        FROM paper_support s
        LEFT JOIN placed p ON p.pub_id = s.pub_id
        WHERE s.n_citations >= {MIN_CITATIONS}
          AND p.pub_id IS NULL
      ) AS n_failed_vote,
      (SELECT COUNTIF(assignment_level = 'micro') FROM placed) AS n_placed_micro,
      (SELECT COUNTIF(assignment_level = 'meso') FROM placed) AS n_placed_meso,
      (SELECT COUNTIF(assignment_level = 'macro') FROM placed) AS n_placed_macro,
      (SELECT COUNT(*) FROM placed) AS n_placed,
      (
        SELECT COUNT(*) * 2
        FROM placed p
        JOIN cited_community d ON d.pub_id = p.pub_id
      ) AS n_edges
    ;
    """


def journal_ids_sql(run_table: str) -> str:
    return f"(SELECT journal_ids FROM `{run_table}` LIMIT 1)"


def clone_table(bq: bigquery.Client, source: str, dest: str) -> bool:
    if not table_exists(bq, source):
        log.info("  skip missing %s", source)
        return False
    if table_exists(bq, dest):
        raise SystemExit(f"{dest} already exists. Pick another --dest, or delete it first.")
    log.info("  clone %s", dest)
    job = bq.query(f"CREATE TABLE `{dest}` CLONE `{source}`")
    job.result()
    return True


def copy_run(bq: bigquery.Client, source: str, dest: str) -> None:
    """Copy the network tables, then any label tables that exist."""
    missing = [
        table_id(suffix, source)
        for suffix in NETWORK_SUFFIXES
        if not table_exists(bq, table_id(suffix, source))
    ]
    if missing:
        raise SystemExit("Source run is incomplete:\n  " + "\n  ".join(missing))
    occupied = [
        table_id(suffix, dest)
        for suffix in NETWORK_SUFFIXES
        if table_exists(bq, table_id(suffix, dest))
    ]
    if occupied:
        raise SystemExit(
            "Destination already has tables. Pick another --dest.\n  "
            + "\n  ".join(occupied)
        )
    log.info("Copying %s to %s", source, dest)
    for suffix in NETWORK_SUFFIXES:
        clone_table(bq, table_id(suffix, source), table_id(suffix, dest))
    for prefix in LABEL_PREFIXES:
        for level in LEVELS:
            src = label_id(prefix, level, source)
            dst = label_id(prefix, level, dest)
            if not clone_table(bq, src, dst):
                continue
            if "run_timestamp" not in column_names(bq, dst):
                continue
            bq.query(
                f"UPDATE `{dst}` SET run_timestamp = '{dest}' WHERE TRUE"
            ).result()


def tables_for(timestamp: str, start_year: int) -> dict[str, str]:
    return {
        "classif": table_id("classification_raw", timestamp),
        "meta": table_id("pub_metadata_raw", timestamp),
        "pubs": table_id("pubs_raw", timestamp),
        "links": table_id("cit_links_raw", timestamp),
        "run": table_id("run_metadata", timestamp),
        "start_year": str(int(start_year)),
    }


def log_summary(frame: pd.DataFrame, *, wrote: bool) -> None:
    if frame.empty:
        log.info("No summary row returned")
        return
    row = frame.iloc[0]
    for key, value in row.items():
        shown = f"{int(value):,}" if pd.notna(value) and key != "through_year" else value
        log.info("  %-24s %s", key, shown)
    log.info("Wrote rows" if wrote else "Dry run: no tables were changed")


def assign(
    bq: bigquery.Client,
    source_timestamp: str,
    target_timestamp: str,
    through_year: int,
    *,
    write: bool,
    reset: bool,
) -> pd.DataFrame:
    start_year, end_year, _journal_ids = load_run_bounds(bq, target_timestamp)
    if through_year < start_year:
        raise SystemExit(
            f"--through-year {through_year} is before the run start year {start_year}"
        )
    log.info(
        "Run years %s-%s, adding Frontiers papers through %s",
        start_year,
        end_year,
        through_year,
    )
    log.info(
        "Vote: at least %s in-network citations, share >= %.2f, margin >= %.2f, same-journal weight %.2f",
        MIN_CITATIONS,
        MIN_SHARE,
        MIN_MARGIN,
        SELF_CITE_JOURNAL_WEIGHT,
    )
    classif = table_id("classification_raw", target_timestamp)
    present = table_exists(bq, classif) and "assignment_method" in column_names(bq, classif)
    # A write backfills assignment_method before the vote, so the predicate can
    # require 'leiden' even when the column was missing at the start.
    predicate = leiden_predicate("c", column_present=present, backfilled=write)
    sql = assignment_script(
        tables_for(target_timestamp, start_year),
        through_year=through_year,
        leiden_on=predicate,
        write=write,
        reset=reset,
        source_timestamp=source_timestamp,
        dest_timestamp=target_timestamp,
    )
    log.info("%s citation assignment on %s", "Writing" if write else "Scoring", target_timestamp)
    return run_script(bq, sql)


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Place new Frontiers papers into an existing Leiden run by citation."
    )
    parser.add_argument("-t", "--timestamp", default=os.environ.get("RUN_TIMESTAMP", ""))
    parser.add_argument(
        "--dest",
        default="",
        help="Copy the run to this id and write there. The source run is not modified.",
    )
    parser.add_argument(
        "--through-year",
        type=int,
        default=0,
        help="Last publication year to add. Default: the run's end_year.",
    )
    parser.add_argument(
        "--write",
        action="store_true",
        help="Write the placed papers. Without this flag the command only reports counts.",
    )
    parser.add_argument(
        "--in-place",
        action="store_true",
        help="Write into --timestamp. Replaces any earlier citation rows in that run.",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> None:
    args = parse_args(argv)
    source = require_timestamp(args.timestamp or os.environ.get("RUN_TIMESTAMP", ""), "--timestamp")
    dest = (args.dest or "").strip()
    if dest:
        dest = require_timestamp(dest, "--dest")
    if args.write and not dest and not args.in_place:
        raise SystemExit(
            "Pass --dest YYYYMMDD_HHMMSS to copy the run, or --in-place to edit it. "
            "A dry run needs neither."
        )
    if dest and args.in_place:
        raise SystemExit("Pass only one of --dest and --in-place.")
    if dest and dest == source:
        raise SystemExit("--dest must be a different run id from --timestamp.")
    if args.in_place and not args.write:
        raise SystemExit("--in-place only applies with --write.")

    setup_logging(dest or source)
    log.info("Source run %s", source)
    bq = client()
    _start, end_year, _journals = load_run_bounds(bq, source)
    through_year = args.through_year or end_year
    if through_year < 1900 or through_year > 2100:
        raise SystemExit(f"--through-year {through_year} is not a publication year")

    target = source
    reset = False
    if args.write and dest:
        copy_run(bq, source, dest)
        target = dest
        log.info("Source %s was not modified", source)
    elif args.write and args.in_place:
        reset = True
        log.info("In-place write on %s. Earlier citation rows in this run will be replaced.", source)

    try:
        summary = assign(
            bq,
            source,
            target,
            through_year,
            write=args.write,
            reset=reset,
        )
    except Exception:
        if dest and args.write:
            log.exception(
                "Assignment failed. %s may be an unfinished copy of %s.",
                dest,
                source,
            )
        raise
    log_summary(summary, wrote=args.write)


if __name__ == "__main__":
    main()
