"""
person_network_export.py
=========================
Build an author citation network in BigQuery and upload the Leiden inputs.

Nodes are AIRAK authors (AuthorId), not papers. A paper by author A that cites
a paper by author B creates an author-author edge. The edge weight is the same
temporal decay as cwts_export.py, multiplied by each author's role weight.

First and last authors weigh 1. A sole author weighs 1. Middle authors weigh
0.25. Position comes from PublicationAuthor.AuthorSequenceNumber, with
IsFirstAuthor / IsLastAuthor used when those flags are set.

All writes go to:
    ocean-tech-adv-analytics-c-tfs.raw_citation_network_data_person
and every table name ends in _person_{timestamp}. The paper dataset is not
touched. This script does not run Leiden.

Usage
-----
    python src/person_network_export.py

Optional env vars (same defaults as cwts_export.py):
    NETWORK_MODE            journal_window (default), global, seed, or country
    PERSON_AUTHOR_ROLES     all (default) or first_last
    PERSON_SEED_AUTHOR_IDS  comma-separated AIRAK AuthorIds, required for seed
    PERSON_SEED_COUNTRIES   comma-separated ISO alpha-3 codes, required for country
    PERSON_CITATION_HOPS    citation hops around the starting papers, default 2
    JOURNAL_IDS             comma-separated journal ids, journal_window only
    START_YEAR              default 2023
    END_YEAR                default 2026
    RUN_TIMESTAMP           default now, YYYYMMDD_HHMMSS
    TEMPORAL_DECAY_TAU      default 5.0

journal_window keeps both papers inside JOURNAL_IDS. global keeps every
citation whose citing and cited papers were both published in the year window.
seed starts with the selected authors' papers and keeps an induced citation
network around them. country does the same, starting from papers that list an
organization in PERSON_SEED_COUNTRIES. Each hop adds papers cited by the
current set and papers that cite it. Both papers stay inside the year window,
unless PERSON_SEED_ALL_YEARS is set. That keeps every paper by the seed authors,
then walks the citation hops with no year cutoff.
first_last drops middle authors, so an edge only joins a first or last author
to a first or last author. A sole author counts as both.
"""

from __future__ import annotations

import json
import logging
import os
import re
import sys
from datetime import datetime
from pathlib import Path

from google.cloud import bigquery

BQ_READ_PROJECT = "ocean-tech-adv-analytics-p-usr"
AIRAK_DATASET = "ocean-breeze-tier-1.airak"
BQ_DEST_PROJECT = "ocean-tech-adv-analytics-c-tfs"
BQ_DEST_DATASET = "raw_citation_network_data_person"

FIRST_LAST_WEIGHT = 1.0
MIDDLE_WEIGHT = 0.25
DECAY_FLOOR = 0.01

NETWORK_MODE = (os.environ.get("NETWORK_MODE") or "journal_window").strip().lower()
if NETWORK_MODE not in ("journal_window", "global", "seed", "country"):
    raise SystemExit(
        "Person NETWORK_MODE must be journal_window, global, seed, or country, "
        f"got {NETWORK_MODE!r}. Paper modes ego and full are not person networks."
    )
AUTHOR_ROLES = (os.environ.get("PERSON_AUTHOR_ROLES") or "all").strip().lower()
if AUTHOR_ROLES not in ("all", "first_last"):
    raise SystemExit(
        "PERSON_AUTHOR_ROLES must be all or first_last, "
        f"got {AUTHOR_ROLES!r}"
    )
SEED_AUTHOR_IDS = [
    int(value.strip())
    for value in os.environ.get("PERSON_SEED_AUTHOR_IDS", "").split(",")
    if value.strip()
]
SEED_COUNTRIES = []
for value in os.environ.get("PERSON_SEED_COUNTRIES", "").split(","):
    code = value.strip().upper()
    if not code:
        continue
    if not re.fullmatch(r"[A-Z]{3}", code):
        raise SystemExit(
            "PERSON_SEED_COUNTRIES must be ISO alpha-3 codes such as BEL,USA,ESP,ITA, "
            f"got {value.strip()!r}"
        )
    SEED_COUNTRIES.append(code)
SEED_ALL_YEARS = (os.environ.get("PERSON_SEED_ALL_YEARS") or "").strip().lower() in (
    "1",
    "true",
    "yes",
)
CITATION_HOPS = int(os.environ.get("PERSON_CITATION_HOPS", "2"))
if NETWORK_MODE == "seed" and not SEED_AUTHOR_IDS:
    raise SystemExit("PERSON_SEED_AUTHOR_IDS is required when NETWORK_MODE=seed")
if NETWORK_MODE == "country" and not SEED_COUNTRIES:
    raise SystemExit("PERSON_SEED_COUNTRIES is required when NETWORK_MODE=country")
if SEED_ALL_YEARS and NETWORK_MODE != "seed":
    raise SystemExit("PERSON_SEED_ALL_YEARS is only valid for a seeded person network")
if CITATION_HOPS not in (1, 2, 3):
    raise SystemExit("PERSON_CITATION_HOPS must be 1, 2, or 3")

START_YEAR = int(os.environ.get("START_YEAR", "2023"))
END_YEAR = int(os.environ.get("END_YEAR", "2026"))
TEMPORAL_DECAY_TAU = float(os.environ.get("TEMPORAL_DECAY_TAU", "5.0"))
RUN_TIMESTAMP = os.environ.get(
    "RUN_TIMESTAMP", datetime.now().strftime("%Y%m%d_%H%M%S")
)

LOG_DIR = Path(r"C:\Users\sophie.wilson\Documents\scope_drift_outputs\logs\cwts_output")
LOG_DIR.mkdir(parents=True, exist_ok=True)

for _stream in (sys.stdout, sys.stderr):
    if hasattr(_stream, "reconfigure"):
        _stream.reconfigure(encoding="utf-8", errors="replace")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(
            LOG_DIR / f"person_network_export_{RUN_TIMESTAMP}.log",
            mode="w",
            encoding="utf-8",
        ),
        logging.StreamHandler(),
    ],
)
log = logging.getLogger(__name__)


def journal_ids() -> list[int]:
    """Same journal list as the paper export, without importing that script.

    Importing cwts_export.py would configure its own logging first and swallow
    this script's log file. Read JOURNAL_IDS from the environment, and otherwise
    reuse the default string literal in cwts_export.py.
    """
    raw = os.environ.get("JOURNAL_IDS", "").strip()
    if not raw:
        source = Path(__file__).with_name("cwts_export.py").read_text(encoding="utf-8")
        match = re.search(
            r'JOURNAL_IDS_OVERRIDE = os\.environ\.get\(\s*"JOURNAL_IDS",\s*"([^"]+)"',
            source,
        )
        if not match:
            raise SystemExit("Could not read the default JOURNAL_IDS from cwts_export.py")
        raw = match.group(1).strip()
    ids = [int(part.strip()) for part in raw.split(",") if part.strip()]
    if not ids:
        raise SystemExit("JOURNAL_IDS is empty")
    return ids


def table(name: str) -> str:
    if not re.fullmatch(r"\d{8}_\d{6}", RUN_TIMESTAMP):
        raise SystemExit(f"RUN_TIMESTAMP must look like YYYYMMDD_HHMMSS, got {RUN_TIMESTAMP!r}")
    return f"`{BQ_DEST_PROJECT}.{BQ_DEST_DATASET}.{name}_person_{RUN_TIMESTAMP}`"


def ensure_dataset(client: bigquery.Client) -> None:
    dataset_id = f"{BQ_DEST_PROJECT}.{BQ_DEST_DATASET}"
    dataset = bigquery.Dataset(dataset_id)
    dataset.location = "EU"
    client.create_dataset(dataset, exists_ok=True)
    log.info("Dataset ready: %s", dataset_id)


def export_sql() -> str:
    """One script so PublicationAuthor and PublicationCitation are scanned once."""
    author_papers = table("author_papers")
    pubs = table("pubs_raw")
    metadata = table("pub_metadata_raw")
    links = table("cit_links_raw")
    run_meta = table("run_metadata")
    if NETWORK_MODE in ("global", "seed", "country"):
        window_where = "WHERE PublishedYear BETWEEN @start_year AND @end_year"
    else:
        window_where = (
            "WHERE JournalId IN UNNEST(@journal_ids)\n"
            "      AND PublishedYear BETWEEN @start_year AND @end_year"
        )
    if NETWORK_MODE in ("seed", "country"):
        if NETWORK_MODE == "seed" and SEED_ALL_YEARS:
            hop0 = """
    CREATE TEMP TABLE seed_hop_0 AS
    SELECT DISTINCT pa.PublicationId
    FROM `{airak}.PublicationAuthor` pa
    WHERE pa.AuthorId IN UNNEST(@seed_author_ids);
            """.format(airak=AIRAK_DATASET)
            citation_table = f"`{AIRAK_DATASET}.PublicationCitation`"
            cited_year = f"""
    JOIN `{AIRAK_DATASET}.Publication` cited
      ON cited.PublicationId = pc.CitedPublicationId
            """
        elif NETWORK_MODE == "seed":
            hop0 = """
    CREATE TEMP TABLE seed_hop_0 AS
    SELECT DISTINCT pa.PublicationId
    FROM `{airak}.PublicationAuthor` pa
    JOIN person_window p USING (PublicationId)
    WHERE pa.AuthorId IN UNNEST(@seed_author_ids);
            """.format(airak=AIRAK_DATASET)
            citation_table = "all_window_citations"
            cited_year = """
    JOIN person_window cited ON cited.PublicationId = pc.CitedPublicationId
            """
        else:
            hop0 = """
    CREATE TEMP TABLE seed_hop_0 AS
    SELECT DISTINCT pa.PublicationId
    FROM `{airak}.PublicationAuthor` pa
    JOIN person_window p USING (PublicationId)
    JOIN `{airak}.Organization` o ON o.OrganizationId = pa.OrganizationId
    WHERE pa.AuthorId IS NOT NULL
      AND o.CountryIsoCode3 IN UNNEST(@seed_country_codes);
            """.format(airak=AIRAK_DATASET)
            citation_table = "all_window_citations"
            cited_year = """
    JOIN person_window cited ON cited.PublicationId = pc.CitedPublicationId
            """
        hop_statements = [hop0]
        for hop in range(1, CITATION_HOPS + 1):
            prior = hop - 1
            hop_statements.append(
                f"""
    CREATE TEMP TABLE seed_hop_{hop} AS
    SELECT PublicationId FROM seed_hop_{prior}
    UNION DISTINCT
    SELECT c.CitedPublicationId
    FROM {citation_table} c
    JOIN seed_hop_{prior} h ON h.PublicationId = c.PublicationId
    WHERE c.PublicationId != c.CitedPublicationId
    UNION DISTINCT
    SELECT c.PublicationId
    FROM {citation_table} c
    JOIN seed_hop_{prior} h ON h.PublicationId = c.CitedPublicationId
    WHERE c.PublicationId != c.CitedPublicationId;
                """
            )
        if NETWORK_MODE == "seed" and SEED_ALL_YEARS:
            citations_setup = ""
        else:
            citations_setup = f"""
    CREATE TEMP TABLE all_window_citations AS
    SELECT pc.PublicationId, pc.CitedPublicationId
    FROM `{AIRAK_DATASET}.PublicationCitation` pc
    JOIN person_window citing ON citing.PublicationId = pc.PublicationId
    JOIN person_window cited ON cited.PublicationId = pc.CitedPublicationId
    WHERE pc.PublicationId != pc.CitedPublicationId;
            """
        seed_setup = f"""
    {citations_setup}

    {"".join(hop_statements)}

    CREATE TEMP TABLE selected_papers AS
    SELECT PublicationId FROM seed_hop_{CITATION_HOPS};
        """
        citation_source = f"""
    FROM {citation_table} pc
    JOIN selected_papers citing_selected
      ON citing_selected.PublicationId = pc.PublicationId
    JOIN selected_papers cited_selected
      ON cited_selected.PublicationId = pc.CitedPublicationId
    {cited_year}
        """
    else:
        seed_setup = ""
        citation_source = f"""
    FROM `{AIRAK_DATASET}.PublicationCitation` pc
    JOIN person_window citing ON pc.PublicationId = citing.PublicationId
    JOIN person_window cited ON pc.CitedPublicationId = cited.PublicationId
        """
    if AUTHOR_ROLES == "first_last" and NETWORK_MODE == "seed":
        role_filter = (
            f"WHERE role_weight = {FIRST_LAST_WEIGHT} "
            "OR author_id IN UNNEST(@seed_author_ids)"
        )
    elif AUTHOR_ROLES == "first_last":
        role_filter = f"WHERE role_weight = {FIRST_LAST_WEIGHT}"
    else:
        role_filter = ""
    if NETWORK_MODE == "seed" and SEED_ALL_YEARS:
        window_sql = ""
    else:
        window_sql = f"""
    CREATE TEMP TABLE person_window AS
    SELECT PublicationId, PublishedYear
    FROM `{AIRAK_DATASET}.Publication`
    {window_where};
        """
    return f"""
    {window_sql}

    {seed_setup}

    CREATE TEMP TABLE person_citations AS
    SELECT
      pc.PublicationId AS citing_id,
      pc.CitedPublicationId AS cited_id,
      GREATEST(
        {DECAY_FLOOR},
        EXP(
          -SAFE_DIVIDE(
            CAST(@end_year - IFNULL(cited.PublishedYear, @end_year) AS FLOAT64),
            @tau
          )
        )
      ) AS decay
    {citation_source}
    WHERE pc.PublicationId != pc.CitedPublicationId;

    CREATE TEMP TABLE person_roles AS
    WITH endpoints AS (
      SELECT citing_id AS publication_id FROM person_citations
      UNION DISTINCT
      SELECT cited_id FROM person_citations
    ),
    authors AS (
      SELECT
        pa.PublicationId AS publication_id,
        pa.AuthorId AS author_id,
        MIN(pa.AuthorSequenceNumber) AS seq,
        LOGICAL_OR(pa.IsFirstAuthor) AS is_first,
        LOGICAL_OR(pa.IsLastAuthor) AS is_last
      FROM `{AIRAK_DATASET}.PublicationAuthor` pa
      JOIN endpoints e ON pa.PublicationId = e.publication_id
      WHERE pa.AuthorId IS NOT NULL
      GROUP BY pa.PublicationId, pa.AuthorId
    ),
    sized AS (
      SELECT
        publication_id,
        author_id,
        seq,
        is_first,
        is_last,
        COUNT(*) OVER (PARTITION BY publication_id) AS n_authors,
        MAX(seq) OVER (PARTITION BY publication_id) AS max_seq
      FROM authors
    )
    SELECT publication_id, author_id, role_weight
    FROM (
      SELECT
        publication_id,
        author_id,
        CASE
          WHEN n_authors = 1 THEN {FIRST_LAST_WEIGHT}
          WHEN is_first OR is_last THEN {FIRST_LAST_WEIGHT}
          WHEN seq = 1 OR seq = max_seq THEN {FIRST_LAST_WEIGHT}
          ELSE {MIDDLE_WEIGHT}
        END AS role_weight
      FROM sized
    )
    {role_filter};

    CREATE TEMP TABLE person_ids AS
    SELECT
      author_id,
      ROW_NUMBER() OVER (ORDER BY author_id) - 1 AS int_id
    FROM (SELECT DISTINCT author_id FROM person_roles);

    CREATE OR REPLACE TABLE {author_papers} AS
    SELECT
      r.publication_id,
      r.author_id,
      i.int_id,
      r.role_weight
    FROM person_roles r
    JOIN person_ids i USING (author_id);

    CREATE OR REPLACE TABLE {pubs} AS
    SELECT int_id, 1 AS core_pub
    FROM person_ids;

    CREATE OR REPLACE TABLE {metadata} AS
    SELECT
      i.int_id,
      i.author_id,
      TRIM(
        REPLACE(
          REPLACE(IFNULL(a.FullName, ''), CHR(9), ' '),
          CHR(10),
          ' '
        )
      ) AS name
    FROM person_ids i
    LEFT JOIN `{AIRAK_DATASET}.Author` a ON i.author_id = a.AuthorId;

    CREATE OR REPLACE TABLE {links} AS
    WITH directed AS (
      SELECT
        src.int_id AS int_id1,
        tgt.int_id AS int_id2,
        SUM(c.decay * src.role_weight * tgt.role_weight) AS weight
      FROM person_citations c
      JOIN {author_papers} src ON src.publication_id = c.citing_id
      JOIN {author_papers} tgt ON tgt.publication_id = c.cited_id
      WHERE src.author_id != tgt.author_id
      GROUP BY int_id1, int_id2
    ),
    undirected AS (
      SELECT
        IF(int_id1 < int_id2, int_id1, int_id2) AS lo,
        IF(int_id1 < int_id2, int_id2, int_id1) AS hi,
        SUM(weight) AS weight
      FROM directed
      WHERE int_id1 != int_id2
      GROUP BY lo, hi
    )
    SELECT lo AS int_id1, hi AS int_id2, weight FROM undirected
    UNION ALL
    SELECT hi AS int_id1, lo AS int_id2, weight FROM undirected;

    CREATE OR REPLACE TABLE {run_meta} AS
    SELECT
      @run_timestamp AS run_timestamp,
      FORMAT_TIMESTAMP('%Y-%m-%d %H:%M UTC', CURRENT_TIMESTAMP()) AS generated_utc,
      '{BQ_READ_PROJECT}' AS bq_source_project,
      '{AIRAK_DATASET}' AS bq_source_dataset,
      'person' AS network_entity,
      '{NETWORK_MODE}' AS network_mode,
      @seed_author_ids_json AS seed_author_ids,
      @seed_countries_json AS seed_countries,
      {str(SEED_ALL_YEARS).lower()} AS seed_all_years,
      {CITATION_HOPS if NETWORK_MODE in ("seed", "country") else 0} AS citation_hops,
      @start_year AS start_year,
      @end_year AS end_year,
      @journal_ids_json AS journal_ids,
      @tau AS temporal_decay_tau,
      '{AUTHOR_ROLES}' AS author_roles,
      {FIRST_LAST_WEIGHT} AS role_first_last_weight,
      {MIDDLE_WEIGHT} AS role_middle_weight,
      'AuthorSequenceNumber, IsFirstAuthor, IsLastAuthor' AS position_columns,
      (SELECT COUNT(*) FROM {pubs}) AS total_nodes,
      (SELECT COUNT(*) FROM {links}) AS total_edges,
      (SELECT COUNT(*) FROM {author_papers}) AS author_paper_rows;
    """


def main() -> None:
    if END_YEAR < START_YEAR:
        raise SystemExit(f"END_YEAR {END_YEAR} is before START_YEAR {START_YEAR}")
    if TEMPORAL_DECAY_TAU <= 0:
        raise SystemExit("TEMPORAL_DECAY_TAU must be positive")

    ids = [] if NETWORK_MODE in ("global", "seed", "country") else journal_ids()
    log.info("Person citation network")
    log.info("  mode               : %s", NETWORK_MODE)
    log.info("  years              : %s-%s", START_YEAR, END_YEAR)
    if NETWORK_MODE in ("global", "seed", "country"):
        log.info("  journals           : no journal filter")
    else:
        log.info("  journals           : %s", f"{len(ids):,}")
    log.info("  temporal decay tau : %s", TEMPORAL_DECAY_TAU)
    log.info("  author roles       : %s", AUTHOR_ROLES)
    if NETWORK_MODE == "seed":
        log.info("  seed authors       : %s", ",".join(map(str, SEED_AUTHOR_IDS)))
        log.info("  citation hops      : %s", CITATION_HOPS)
        log.info("  seed all years     : %s", SEED_ALL_YEARS)
    if NETWORK_MODE == "country":
        log.info("  seed countries     : %s", ",".join(SEED_COUNTRIES))
        log.info("  citation hops      : %s", CITATION_HOPS)
    log.info("  role weights       : first/last %s, middle %s", FIRST_LAST_WEIGHT, MIDDLE_WEIGHT)
    log.info("  destination        : %s.%s", BQ_DEST_PROJECT, BQ_DEST_DATASET)
    log.info("  timestamp          : %s", RUN_TIMESTAMP)

    read_client = bigquery.Client(project=BQ_READ_PROJECT, location="EU")
    dest_client = bigquery.Client(project=BQ_DEST_PROJECT, location="EU")
    ensure_dataset(dest_client)

    parameters = [
        bigquery.ScalarQueryParameter("start_year", "INT64", START_YEAR),
        bigquery.ScalarQueryParameter("end_year", "INT64", END_YEAR),
        bigquery.ScalarQueryParameter("tau", "FLOAT64", TEMPORAL_DECAY_TAU),
        bigquery.ScalarQueryParameter("run_timestamp", "STRING", RUN_TIMESTAMP),
        bigquery.ScalarQueryParameter("journal_ids_json", "STRING", json.dumps(ids)),
        bigquery.ScalarQueryParameter(
            "seed_author_ids_json", "STRING", json.dumps(SEED_AUTHOR_IDS)
        ),
        bigquery.ScalarQueryParameter(
            "seed_countries_json", "STRING", json.dumps(SEED_COUNTRIES)
        ),
    ]
    if NETWORK_MODE == "journal_window":
        parameters.insert(
            0, bigquery.ArrayQueryParameter("journal_ids", "INT64", ids)
        )
    elif NETWORK_MODE == "seed":
        parameters.insert(
            0,
            bigquery.ArrayQueryParameter(
                "seed_author_ids", "INT64", SEED_AUTHOR_IDS
            ),
        )
    elif NETWORK_MODE == "country":
        parameters.insert(
            0,
            bigquery.ArrayQueryParameter(
                "seed_country_codes", "STRING", SEED_COUNTRIES
            ),
        )
    job_config = bigquery.QueryJobConfig(query_parameters=parameters)
    log.info("Building author nodes and citation edges in BigQuery")
    job = read_client.query(export_sql(), job_config=job_config)
    job.result()
    counts = list(
        read_client.query(
            f"""
            SELECT
              (SELECT COUNT(*) FROM {table("pubs_raw")}) AS n_authors,
              (SELECT COUNT(*) FROM {table("cit_links_raw")}) AS n_edges,
              (SELECT COUNT(DISTINCT publication_id) FROM {table("author_papers")}) AS n_papers,
              (SELECT COUNT(*) FROM {table("author_papers")}) AS n_author_papers
            """
        ).result()
    )[0]
    log.info("  authors            : %s", f"{counts.n_authors:,}")
    log.info("  papers in edges    : %s", f"{counts.n_papers:,}")
    log.info("  author-paper rows  : %s", f"{counts.n_author_papers:,}")
    log.info("  directed edges     : %s", f"{counts.n_edges:,}")
    log.info("  pubs               : %s", table("pubs_raw"))
    log.info("  pub_metadata       : %s", table("pub_metadata_raw"))
    log.info("  cit_links          : %s", table("cit_links_raw"))
    log.info("  author_papers      : %s", table("author_papers"))
    log.info("  run_metadata       : %s", table("run_metadata"))
    if counts.n_authors == 0 or counts.n_edges == 0:
        raise SystemExit("Person export wrote no authors or no edges")


if __name__ == "__main__":
    try:
        main()
    except Exception:
        log.exception("Person network export failed")
        raise
