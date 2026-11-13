"""Build the stakeholder views in clean_views.

Every view starts with run_type ('paper' or 'person') and run_id (the run
timestamp), so one filter works everywhere:

    SELECT * FROM `ocean-tech-adv-analytics-c-tfs.clean_views.members`
    WHERE run_type = 'person'

Views are read-only queries over the run tables; nothing they read is changed.

    runs            one row per run
    members         one row per clustered paper or author
    communities     one row per community, level and run
    paper_details   paper-only attributes, joined on member_key
    author_details  author-only attributes, joined on member_key
    paper_scope     scope verdict per paper and journal (paper runs)
    author_papers   which papers link each author into the network (person runs)

Usage:
    python scripts/build_clean_views.py
"""

from __future__ import annotations

from google.api_core.exceptions import NotFound
from google.cloud import bigquery

BILL_PROJECT = "ocean-tech-adv-analytics-p-usr"
PROJECT = "ocean-tech-adv-analytics-c-tfs"
DEST = f"{PROJECT}.clean_views"
LABELS = f"{PROJECT}.taxonomy_labelling"
LEVELS = ("macro", "meso", "micro")
PARENT = {"micro": "meso", "meso": "macro"}

RUNS = [
    {
        "run_type": "paper",
        "run_id": "20260827_081311",
        "member_type": "paper",
        "description": "Citation network of papers, global mode, 2023-2026. Members are papers.",
        "dataset": f"{PROJECT}.raw_citation_network_data",
        "suffix": "_20260827_081311",
    },
    {
        "run_type": "person",
        "run_id": "20261023_114612",
        "member_type": "author",
        "description": (
            "Author citation network around 4 seed authors, 1 citation hop, "
            "every year of their papers. Members are authors."
        ),
        "dataset": f"{PROJECT}.raw_citation_network_data_person",
        "suffix": "_person_20261023_114612",
    },
]

# Labels store keywords as a Python list literal; this turns them into "a; b; c".
KEYWORDS_SQL = (
    "ARRAY_TO_STRING(ARRAY(SELECT TRIM(k, \"'\\\"\") FROM UNNEST("
    "REGEXP_EXTRACT_ALL({col}, r\"('[^']*'|\\\"[^\\\"]*\\\")\")) AS k), '; ')"
)

client = bigquery.Client(project=BILL_PROJECT, location="EU")


def exists(table: str) -> bool:
    try:
        client.get_table(table)
        return True
    except NotFound:
        return False


def src(run: dict, name: str) -> str:
    return f"`{run['dataset']}.{name}{run['suffix']}`"


def label_table(run: dict, level: str) -> str:
    return f"`{LABELS}.cluster_labels_{level}_{run['run_id']}`"


def name_sql(alias: str, level: str, id_expr: str) -> str:
    return (
        f"COALESCE(NULLIF(TRIM({alias}.short_label), ''), "
        f"CONCAT('Unlabelled {level} community ', CAST({id_expr} AS STRING)))"
    )


def run_keys(run: dict) -> str:
    return f"'{run['run_type']}' AS run_type, '{run['run_id']}' AS run_id"


def runs_sql() -> str:
    parts = []
    for run in RUNS:
        parts.append(
            f"""
SELECT
  {run_keys(run)},
  '{run['member_type']}' AS member_type,
  '{run['description']}' AS description,
  md.network_mode,
  md.start_year,
  md.end_year,
  md.generated_utc AS built_utc,
  md.total_edges AS n_links,
  cnt.n_members,
  cnt.n_macro_communities,
  cnt.n_meso_communities,
  cnt.n_micro_communities
FROM (SELECT * FROM {src(run, 'run_metadata')} LIMIT 1) AS md
CROSS JOIN (
  SELECT
    COUNT(*) AS n_members,
    COUNT(DISTINCT macro) AS n_macro_communities,
    COUNT(DISTINCT meso) AS n_meso_communities,
    COUNT(DISTINCT micro) AS n_micro_communities
  FROM {src(run, 'classification_raw')}
) AS cnt"""
        )
    return "\nUNION ALL\n".join(parts)


def members_sql() -> str:
    parts = []
    for run in RUNS:
        display = "m.title" if run["run_type"] == "paper" else "m.name"
        level_cols = []
        joins = []
        for level in ("micro", "meso", "macro"):
            level_cols.append(
                f"  c.{level} AS {level}_id,\n"
                f"  {name_sql(level, level, f'c.{level}')} AS {level}_name"
            )
            joins.append(
                f"LEFT JOIN {label_table(run, level)} AS {level}\n"
                f"  ON {level}.cluster_id = c.{level}"
            )
        level_sql = ",\n".join(level_cols)
        join_sql = "\n".join(joins)
        parts.append(
            f"""
SELECT
  {run_keys(run)},
  '{run['member_type']}' AS member_type,
  CONCAT('{run['run_type']}:', CAST(m.int_id AS STRING)) AS member_key,
  m.int_id AS member_id,
  {display} AS display_name,
{level_sql}
FROM {src(run, 'pub_metadata_raw')} AS m
JOIN {src(run, 'classification_raw')} AS c
  ON c.int_id = m.int_id
{join_sql}"""
        )
    return "\nUNION ALL\n".join(parts)


def communities_sql() -> str:
    parts = []
    for run in RUNS:
        rt = run["run_type"]
        classif = src(run, "classification_raw")
        for level in LEVELS:
            if rt == "person":
                papers_cte = f"""
  SELECT c.{level} AS community_id, COUNT(DISTINCT ap.publication_id) AS n_papers
  FROM {classif} AS c
  JOIN {src(run, 'author_papers')} AS ap ON ap.int_id = c.int_id
  GROUP BY 1"""
            else:
                papers_cte = f"""
  SELECT {level} AS community_id, COUNT(*) AS n_papers
  FROM {classif}
  GROUP BY 1"""

            topics_table = f"{LABELS}.cluster_l2_topics_{level}_{run['run_id']}"
            if exists(topics_table):
                topics_join = f"""
LEFT JOIN (
  SELECT cluster_id, STRING_AGG(l2_name, '; ' ORDER BY l2_rank) AS top_topics
  FROM `{topics_table}`
  GROUP BY cluster_id
) AS t ON t.cluster_id = n.community_id"""
                topics_col = "t.top_topics"
            else:
                topics_join = ""
                topics_col = "CAST(NULL AS STRING)"

            parent = PARENT.get(level)
            if parent:
                parent_join = f"""
LEFT JOIN (
  SELECT
    {level} AS community_id,
    {parent} AS parent_id,
    COUNT(*) / SUM(COUNT(*)) OVER (PARTITION BY {level}) AS parent_share
  FROM {classif}
  GROUP BY 1, 2
  QUALIFY ROW_NUMBER() OVER (PARTITION BY {level} ORDER BY COUNT(*) DESC, {parent}) = 1
) AS p ON p.community_id = n.community_id
LEFT JOIN {label_table(run, parent)} AS pl ON pl.cluster_id = p.parent_id"""
                parent_cols = f"""
  '{parent}' AS parent_level,
  CONCAT('{rt}:{parent}:', CAST(p.parent_id AS STRING)) AS parent_key,
  p.parent_id,
  {name_sql('pl', parent, 'p.parent_id')} AS parent_name,
  ROUND(p.parent_share, 3) AS parent_share"""
            else:
                parent_join = ""
                parent_cols = """
  CAST(NULL AS STRING) AS parent_level,
  CAST(NULL AS STRING) AS parent_key,
  CAST(NULL AS INT64) AS parent_id,
  CAST(NULL AS STRING) AS parent_name,
  CAST(NULL AS FLOAT64) AS parent_share"""

            parts.append(
                f"""
SELECT
  {run_keys(run)},
  '{run['member_type']}' AS member_type,
  CONCAT('{rt}:{level}:', CAST(n.community_id AS STRING)) AS community_key,
  '{level}' AS level,
  n.community_id,
  {name_sql('l', level, 'n.community_id')} AS name,
  NULLIF(TRIM(l.short_label), '') IS NOT NULL AS is_labelled,
  n.n_members,
  pc.n_papers,
  {KEYWORDS_SQL.format(col='l.keywords')} AS keywords,
  l.summary,
  {topics_col} AS top_topics,{parent_cols}
FROM (
  SELECT {level} AS community_id, COUNT(*) AS n_members
  FROM {classif}
  WHERE {level} IS NOT NULL
  GROUP BY 1
) AS n
LEFT JOIN ({papers_cte}
) AS pc ON pc.community_id = n.community_id
LEFT JOIN {label_table(run, level)} AS l ON l.cluster_id = n.community_id{topics_join}{parent_join}"""
            )
    return "\nUNION ALL\n".join(parts)


def paper_details_sql() -> str:
    parts = []
    for run in RUNS:
        if run["run_type"] != "paper":
            continue
        parts.append(
            f"""
SELECT
  {run_keys(run)},
  CONCAT('paper:', CAST(m.int_id AS STRING)) AS member_key,
  m.pub_id,
  m.title,
  m.journal,
  CAST(m.is_frontiers AS INT64) = 1 AS is_frontiers,
  SAFE.PARSE_DATE('%Y-%m-%d', m.date) AS publication_date,
  EXTRACT(YEAR FROM SAFE.PARSE_DATE('%Y-%m-%d', m.date)) AS publication_year
FROM {src(run, 'pub_metadata_raw')} AS m
JOIN {src(run, 'classification_raw')} AS c
  ON c.int_id = m.int_id"""
        )
    return "\nUNION ALL\n".join(parts)


def author_details_sql() -> str:
    parts = []
    for run in RUNS:
        if run["run_type"] != "person":
            continue
        parts.append(
            f"""
SELECT
  {run_keys(run)},
  CONCAT('person:', CAST(m.int_id AS STRING)) AS member_key,
  m.author_id,
  m.name,
  COUNT(DISTINCT ap.publication_id) AS n_papers,
  COUNT(DISTINCT IF(ap.role_weight = 1, ap.publication_id, NULL)) AS n_first_last_or_sole_papers,
  COUNT(DISTINCT IF(ap.role_weight < 1, ap.publication_id, NULL)) AS n_middle_author_papers
FROM {src(run, 'pub_metadata_raw')} AS m
JOIN {src(run, 'classification_raw')} AS c
  ON c.int_id = m.int_id
LEFT JOIN {src(run, 'author_papers')} AS ap
  ON ap.int_id = m.int_id
GROUP BY run_type, run_id, member_key, m.author_id, m.name"""
        )
    return "\nUNION ALL\n".join(parts)


def paper_scope_sql() -> str:
    parts = []
    for run in RUNS:
        if run["run_type"] != "paper":
            continue
        parts.append(
            f"""
SELECT
  {run_keys(run)},
  CONCAT('paper:', CAST(s.int_id AS STRING)) AS member_key,
  s.journal,
  s.pub_year AS publication_year,
  s.cluster_level AS scope_level,
  CONCAT('paper:', s.cluster_level, ':', CAST(s.community_id AS STRING)) AS community_key,
  s.community_id,
  s.is_primary_community,
  CASE s.scope_code
    WHEN 2 THEN 'in_scope'
    WHEN 1 THEN 'borderline'
    WHEN 0 THEN 'out_of_scope'
  END AS scope,
  s.hard_negative,
  s.hard_negative_pattern,
  s.paper_demoted,
  s.override_source,
  s.override_reason,
  s.paper_llm_verdict,
  s.paper_llm_reason
FROM {src(run, 'paper_scope')} AS s"""
        )
    return "\nUNION ALL\n".join(parts)


def author_papers_sql() -> str:
    parts = []
    for run in RUNS:
        if run["run_type"] != "person":
            continue
        parts.append(
            f"""
SELECT
  {run_keys(run)},
  CONCAT('person:', CAST(ap.int_id AS STRING)) AS member_key,
  ap.author_id,
  ap.publication_id,
  ap.role_weight,
  IF(ap.role_weight = 1, 'first_last_or_sole', 'middle') AS author_role
FROM {src(run, 'author_papers')} AS ap"""
        )
    return "\nUNION ALL\n".join(parts)


KEYS = {
    "run_type": "Type of run: 'paper' (papers are the members) or 'person' (authors are the members). Filter on this.",
    "run_id": "Run timestamp the rows come from.",
    "member_type": "What a member is in this run: 'paper' or 'author'.",
    "member_key": "Unique member id across runs, '<run_type>:<member_id>'. Join key between member views.",
}

VIEWS = {
    "runs": (
        runs_sql,
        "One row per run. Start here to see which runs are in this dataset.",
        {
            "description": "What the run is.",
            "network_mode": "How the network was built.",
            "start_year": "First publication year in the network.",
            "end_year": "Last publication year in the network.",
            "built_utc": "When the network was exported.",
            "n_links": "Citation links in the network, from the run metadata.",
            "n_members": "Members placed in communities.",
            "n_macro_communities": "Number of macro communities.",
            "n_meso_communities": "Number of meso communities.",
            "n_micro_communities": "Number of micro communities.",
        },
    ),
    "members": (
        members_sql,
        "One row per paper or author placed in a community. Each member sits in one micro, one meso and one macro community.",
        {
            "member_id": "Member id inside its run. Only unique together with run_type.",
            "display_name": "Paper title, or author name.",
            "micro_id": "Micro community id. Finest level.",
            "micro_name": "Micro community name.",
            "meso_id": "Meso community id. Middle level.",
            "meso_name": "Meso community name.",
            "macro_id": "Macro community id. Broadest level.",
            "macro_name": "Macro community name.",
        },
    ),
    "communities": (
        communities_sql,
        "One row per community, level and run. community_key matches the level id columns on members.",
        {
            "community_key": "Unique community id across runs, '<run_type>:<level>:<community_id>'.",
            "level": "Community level: micro, meso or macro.",
            "community_id": "Community id inside its run and level.",
            "name": "Community name from taxonomy labelling, or 'Unlabelled ...' when no label was found.",
            "is_labelled": "True when the name came from taxonomy labelling.",
            "n_members": "Members in the community.",
            "n_papers": "Papers behind the community. Same as n_members for paper runs; distinct papers by the authors for person runs.",
            "keywords": "Secondary taxonomy topics, '; '-separated.",
            "summary": "Why the community was given its name.",
            "top_topics": "Leading detailed topics, largest first, '; '-separated.",
            "parent_level": "Level of the parent community.",
            "parent_key": "community_key of the parent community.",
            "parent_id": "Parent community id: the one most members sit in.",
            "parent_name": "Parent community name.",
            "parent_share": "Share of members that sit in the parent community.",
        },
    ),
    "paper_details": (
        paper_details_sql,
        "Paper-only attributes for paper runs. Join to members on member_key.",
        {
            "pub_id": "AIRAK PublicationId.",
            "title": "Paper title.",
            "journal": "Journal name.",
            "is_frontiers": "True when the journal is a Frontiers journal.",
            "publication_date": "Publication date.",
            "publication_year": "Publication year.",
        },
    ),
    "author_details": (
        author_details_sql,
        "Author-only attributes for person runs. Join to members on member_key.",
        {
            "author_id": "AIRAK AuthorId.",
            "name": "Author name.",
            "n_papers": "Papers that link the author into the network.",
            "n_first_last_or_sole_papers": "Of those, papers where the author is first, last or sole author.",
            "n_middle_author_papers": "Of those, papers where the author is a middle author.",
        },
    ),
    "paper_scope": (
        paper_scope_sql,
        "Scope verdict per paper and journal, for paper runs. A paper can have more than one row.",
        {
            "journal": "Journal the paper is judged against.",
            "publication_year": "Publication year.",
            "scope_level": "Community level used for the verdict.",
            "community_key": "community_key of the community the verdict used.",
            "community_id": "Community id the verdict used.",
            "is_primary_community": "True when the community is one of the journal's core communities.",
            "scope": "in_scope, borderline or out_of_scope.",
            "hard_negative": "A journal title rule forced the paper out of scope.",
            "hard_negative_pattern": "The title rule that matched.",
            "paper_demoted": "The paper-level check moved it out of scope.",
            "override_source": "What overrode the community verdict, if anything.",
            "override_reason": "Why it was overridden.",
            "paper_llm_verdict": "Verdict from the paper-level check.",
            "paper_llm_reason": "Reason from the paper-level check.",
        },
    ),
    "author_papers": (
        author_papers_sql,
        "Which papers link each author into the network, for person runs.",
        {
            "author_id": "AIRAK AuthorId.",
            "publication_id": "AIRAK PublicationId of the paper.",
            "role_weight": "Weight of the author's role on the paper: 1 first, last or sole; 0.25 middle.",
            "author_role": "first_last_or_sole or middle.",
        },
    ),
}

OLD_VIEWS = ("papers", "authors", "journal_scope", "person_communities")


def describe(name: str, description: str, columns: dict) -> None:
    table = client.get_table(f"{DEST}.{name}")
    table.description = description
    docs = {**KEYS, **columns}
    table.schema = [
        bigquery.SchemaField(
            f.name, f.field_type, mode=f.mode, description=docs.get(f.name, f.description)
        )
        for f in table.schema
    ]
    client.update_table(table, ["description", "schema"])


def main() -> None:
    for name, (build, description, columns) in VIEWS.items():
        client.query(
            f"CREATE OR REPLACE VIEW `{DEST}.{name}` AS\n{build()}", location="EU"
        ).result()
        describe(name, description, columns)
        print("built", name)

    for name in OLD_VIEWS:
        client.delete_table(f"{DEST}.{name}", not_found_ok=True)
        print("dropped", name)


if __name__ == "__main__":
    main()
