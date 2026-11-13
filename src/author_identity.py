"""
author_identity.py
==================
Decide whether AIRAK AuthorIds that share a name are one person or two.

The rules were set on Axel Cleeremans. His 309-paper profile cites three
sole-authored works that AIRAK stored under other AuthorIds, and a 2018
many-author paper under a fifth AuthorId cites that profile and shares
coauthors with it. A second person with the same name would carry a different
ORCID, or a sizeable career with no citations and no coauthors in common.

Usage
-----
    python src/author_identity.py --self-check
    python src/author_identity.py --name "Axel Cleeremans" --timestamp 20261023_114612
    python src/author_identity.py --all --timestamp 20261023_114612

`--timestamp` limits the name search to one person-network run. The paper
counts, citations, and coauthors are then read from the full AIRAK career,
not only the papers that fell inside that network.
"""

from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass

from google.cloud import bigquery

BQ_READ_PROJECT = "ocean-tech-adv-analytics-p-usr"
AIRAK = "ocean-breeze-tier-1.airak"
PERSON_DATASET = "ocean-tech-adv-analytics-c-tfs.raw_citation_network_data_person"

# A record with this many papers or fewer can be an unmerged work of a larger
# profile. Above it, one citation is not enough to merge two careers.
STUB_MAX_PAPERS = 3
# Two long records with no shared papers, citations, or coauthors stay apart.
SUBSTANTIAL_PAPERS = 10
SHARED_COAUTHORS_MIN = 3

ORCID_RE = re.compile(r"\d{4}-\d{4}-\d{4}-\d{3}[\dXx]")


@dataclass(frozen=True)
class AuthorProfile:
    author_id: int
    name: str
    n_papers: int
    year_min: int | None
    year_max: int | None
    orcids: frozenset[str]
    n_coauthors: int


@dataclass(frozen=True)
class PairEvidence:
    shared_papers: int
    cites_a_to_b: int
    cites_b_to_a: int
    shared_coauthors: int


@dataclass(frozen=True)
class Verdict:
    label: str
    strength: str
    reason: str


def _years_overlap(a: AuthorProfile, b: AuthorProfile) -> bool:
    if None in (a.year_min, a.year_max, b.year_min, b.year_max):
        return False
    return a.year_min <= b.year_max and b.year_min <= a.year_max


def decide_pair(a: AuthorProfile, b: AuthorProfile, evidence: PairEvidence) -> Verdict:
    """Classify one pair. `a` and `b` are interchangeable."""
    if a.orcids and b.orcids and a.orcids.isdisjoint(b.orcids):
        return Verdict(
            "different_people",
            "strong",
            "the two records carry different ORCIDs",
        )
    if a.orcids and b.orcids and not a.orcids.isdisjoint(b.orcids):
        return Verdict(
            "same_person",
            "strong",
            "both records carry the same ORCID",
        )
    if evidence.shared_papers:
        return Verdict(
            "same_person",
            "strong",
            f"{evidence.shared_papers} publication(s) list both AuthorIds",
        )

    larger, smaller = (a, b) if a.n_papers >= b.n_papers else (b, a)
    large_cites_small = (
        evidence.cites_a_to_b if larger is a else evidence.cites_b_to_a
    )
    small_cites_large = (
        evidence.cites_b_to_a if larger is a else evidence.cites_a_to_b
    )

    if large_cites_small and smaller.n_papers <= STUB_MAX_PAPERS:
        return Verdict(
            "same_person",
            "strong",
            (
                f"the {larger.n_papers}-paper record cites the "
                f"{smaller.n_papers}-paper record in {large_cites_small} paper(s)"
            ),
        )
    if (
        small_cites_large
        and smaller.n_papers <= STUB_MAX_PAPERS
        and evidence.shared_coauthors >= SHARED_COAUTHORS_MIN
        and _years_overlap(a, b)
    ):
        return Verdict(
            "same_person",
            "medium",
            (
                f"the {smaller.n_papers}-paper record cites the larger one and "
                f"they share {evidence.shared_coauthors} coauthors"
            ),
        )
    if (
        evidence.shared_coauthors >= SHARED_COAUTHORS_MIN
        and _years_overlap(a, b)
        and smaller.n_papers <= STUB_MAX_PAPERS
    ):
        return Verdict(
            "same_person",
            "medium",
            f"they share {evidence.shared_coauthors} coauthors and their years overlap",
        )
    if (
        a.n_papers >= SUBSTANTIAL_PAPERS
        and b.n_papers >= SUBSTANTIAL_PAPERS
        and evidence.shared_papers == 0
        and evidence.shared_coauthors == 0
        and evidence.cites_a_to_b == 0
        and evidence.cites_b_to_a == 0
    ):
        return Verdict(
            "different_people",
            "medium",
            (
                "both records have at least "
                f"{SUBSTANTIAL_PAPERS} papers and share no papers, coauthors, or citations"
            ),
        )
    return Verdict(
        "uncertain",
        "weak",
        "no shared identifier, paper, citation, or coauthor overlap strong enough to decide",
    )


def group_same_people(
    profiles: list[AuthorProfile],
    pair_verdicts: dict[tuple[int, int], Verdict],
) -> tuple[list[list[int]], list[tuple[int, int]]]:
    """Merge pairs labelled same_person. Return groups and any conflicts.

    A conflict is a different_people pair that the same_person links placed
    in one group.
    """
    parent = {profile.author_id: profile.author_id for profile in profiles}

    def find(author_id: int) -> int:
        while parent[author_id] != author_id:
            parent[author_id] = parent[parent[author_id]]
            author_id = parent[author_id]
        return author_id

    for (left, right), verdict in pair_verdicts.items():
        if verdict.label != "same_person":
            continue
        left_root, right_root = find(left), find(right)
        if left_root != right_root:
            parent[right_root] = left_root

    conflicts = []
    for (left, right), verdict in pair_verdicts.items():
        if verdict.label == "different_people" and find(left) == find(right):
            conflicts.append((left, right))

    groups: dict[int, list[int]] = {}
    for profile in profiles:
        groups.setdefault(find(profile.author_id), []).append(profile.author_id)
    ordered = [sorted(members) for members in groups.values()]
    ordered.sort(key=lambda members: (-len(members), members[0] if members else 0))
    return ordered, conflicts


def _profile(
    author_id: int,
    n_papers: int,
    year_min: int,
    year_max: int,
    orcids: frozenset[str] = frozenset(),
    n_coauthors: int = 0,
    name: str = "Axel Cleeremans",
) -> AuthorProfile:
    return AuthorProfile(author_id, name, n_papers, year_min, year_max, orcids, n_coauthors)


def self_check() -> None:
    """The Cleeremans numbers, plus a conflicting-ORCID pair and a namesake."""
    main = _profile(1, 309, 1989, 2026, frozenset({"0000-0002-9757-5235"}), 400)
    book_1993 = _profile(2, 1, 1993, 1993, n_coauthors=0)
    chapter_1997 = _profile(3, 1, 1997, 1997, n_coauthors=0)
    book_2003 = _profile(4, 1, 2003, 2003, n_coauthors=1)
    paper_2018 = _profile(5, 1, 2018, 2018, n_coauthors=40)
    other = _profile(
        6, 40, 2000, 2020, frozenset({"0000-0001-1111-1111-1111"}), 80, "Alex Example"
    )
    namesake = _profile(7, 1, 2020, 2020, n_coauthors=2, name="Axel Cleeremans")

    cases = [
        (main, book_1993, PairEvidence(0, 9, 0, 0), "same_person"),
        (main, chapter_1997, PairEvidence(0, 9, 0, 0), "same_person"),
        (main, book_2003, PairEvidence(0, 6, 0, 0), "same_person"),
        (main, paper_2018, PairEvidence(0, 0, 1, 6), "same_person"),
        (book_1993, chapter_1997, PairEvidence(0, 0, 0, 0), "uncertain"),
        (main, other, PairEvidence(0, 0, 0, 0), "different_people"),
        (main, namesake, PairEvidence(0, 0, 1, 0), "uncertain"),
    ]
    for left, right, evidence, expected in cases:
        got = decide_pair(left, right, evidence)
        if got.label != expected:
            raise SystemExit(
                f"self-check failed for {left.author_id}/{right.author_id}: "
                f"expected {expected}, got {got.label} ({got.reason})"
            )

    profiles = [main, book_1993, chapter_1997, book_2003, paper_2018]
    verdicts = {}
    for left_i, left in enumerate(profiles):
        for right in profiles[left_i + 1 :]:
            evidence = PairEvidence(0, 0, 0, 0)
            if {left.author_id, right.author_id} == {1, 2}:
                evidence = PairEvidence(0, 9, 0, 0)
            elif {left.author_id, right.author_id} == {1, 3}:
                evidence = PairEvidence(0, 9, 0, 0)
            elif {left.author_id, right.author_id} == {1, 4}:
                evidence = PairEvidence(0, 6, 0, 0)
            elif {left.author_id, right.author_id} == {1, 5}:
                evidence = PairEvidence(0, 0, 1, 6)
            pair = tuple(sorted((left.author_id, right.author_id)))
            verdicts[pair] = decide_pair(left, right, evidence)
    groups, conflicts = group_same_people(profiles, verdicts)
    if conflicts or len(groups) != 1 or set(groups[0]) != {1, 2, 3, 4, 5}:
        raise SystemExit(f"self-check grouping failed: {groups} conflicts={conflicts}")
    print("self-check ok")


def _orcid(value: str | None) -> str | None:
    if not value:
        return None
    match = ORCID_RE.search(value)
    return match.group(0).upper() if match else None


def _metadata_table(timestamp: str) -> str:
    if not re.fullmatch(r"\d{8}_\d{6}", timestamp):
        raise SystemExit(f"timestamp must look like YYYYMMDD_HHMMSS, got {timestamp!r}")
    return f"`{PERSON_DATASET}.pub_metadata_raw_person_{timestamp}`"


def _fetch(name: str, timestamp: str) -> tuple[list[AuthorProfile], dict[tuple[int, int], PairEvidence]]:
    metadata = _metadata_table(timestamp)
    sql = f"""
    CREATE TEMP TABLE axels AS
    SELECT author_id, ANY_VALUE(name) AS name
    FROM {metadata}
    WHERE LOWER(name) = LOWER(@name)
    GROUP BY author_id;

    CREATE TEMP TABLE papers AS
    SELECT DISTINCT
      pa.AuthorId AS author_id,
      pa.PublicationId AS publication_id,
      p.PublishedYear AS year
    FROM `{AIRAK}.PublicationAuthor` pa
    JOIN axels a ON a.author_id = pa.AuthorId
    JOIN `{AIRAK}.Publication` p ON p.PublicationId = pa.PublicationId
    WHERE pa.AuthorId IS NOT NULL;

    CREATE TEMP TABLE coauthors AS
    SELECT DISTINCT focus.author_id AS axel_id, pa.AuthorId AS coauthor_id
    FROM papers focus
    JOIN `{AIRAK}.PublicationAuthor` pa
      ON pa.PublicationId = focus.publication_id
    WHERE pa.AuthorId IS NOT NULL
      AND pa.AuthorId != focus.author_id
      AND pa.AuthorId NOT IN (SELECT author_id FROM axels);

    SELECT kind, a, b, c, d FROM (
      SELECT
        'author' AS kind,
        CAST(axels.author_id AS STRING) AS a,
        axels.name AS b,
        CAST(COUNT(DISTINCT papers.publication_id) AS STRING) AS c,
        CONCAT(
          IFNULL(CAST(MIN(papers.year) AS STRING), ''), '|',
          IFNULL(CAST(MAX(papers.year) AS STRING), ''), '|',
          IFNULL((
            SELECT STRING_AGG(DISTINCT s.SourceValue, ',')
            FROM `{AIRAK}.AuthorSource` s
            WHERE s.AuthorId = axels.author_id AND s.SourceId = 10
          ), ''),
          '|',
          CAST((
            SELECT COUNT(DISTINCT coauthor_id) FROM coauthors
            WHERE axel_id = axels.author_id
          ) AS STRING)
        ) AS d
      FROM axels
      LEFT JOIN papers ON papers.author_id = axels.author_id
      GROUP BY axels.author_id, axels.name
      UNION ALL
      SELECT
        'pair',
        CAST(lo.author_id AS STRING),
        CAST(hi.author_id AS STRING),
        CONCAT(
          CAST(COUNT(DISTINCT IF(p1.publication_id = p2.publication_id, p1.publication_id, NULL)) AS STRING),
          '|',
          CAST((
            SELECT COUNT(DISTINCT co1.coauthor_id)
            FROM coauthors co1
            JOIN coauthors co2
              ON co2.coauthor_id = co1.coauthor_id
             AND co2.axel_id = hi.author_id
            WHERE co1.axel_id = lo.author_id
          ) AS STRING)
        ),
        CONCAT(
          CAST((
            SELECT COUNT(DISTINCT pc.PublicationId)
            FROM `{AIRAK}.PublicationCitation` pc
            JOIN papers citing ON citing.publication_id = pc.PublicationId AND citing.author_id = lo.author_id
            JOIN papers cited ON cited.publication_id = pc.CitedPublicationId AND cited.author_id = hi.author_id
            WHERE pc.PublicationId != pc.CitedPublicationId
          ) AS STRING),
          '|',
          CAST((
            SELECT COUNT(DISTINCT pc.PublicationId)
            FROM `{AIRAK}.PublicationCitation` pc
            JOIN papers citing ON citing.publication_id = pc.PublicationId AND citing.author_id = hi.author_id
            JOIN papers cited ON cited.publication_id = pc.CitedPublicationId AND cited.author_id = lo.author_id
            WHERE pc.PublicationId != pc.CitedPublicationId
          ) AS STRING)
        )
      FROM axels lo
      JOIN axels hi ON lo.author_id < hi.author_id
      LEFT JOIN papers p1 ON p1.author_id = lo.author_id
      LEFT JOIN papers p2 ON p2.author_id = hi.author_id AND p2.publication_id = p1.publication_id
      GROUP BY lo.author_id, hi.author_id
    )
    ORDER BY kind, a
    """
    client = bigquery.Client(project=BQ_READ_PROJECT, location="EU")
    job_config = bigquery.QueryJobConfig(
        query_parameters=[bigquery.ScalarQueryParameter("name", "STRING", name)]
    )
    job = client.query(sql, job_config=job_config)
    rows = list(job.result())
    print(f"Query scanned {job.total_bytes_processed or 0:,} bytes", flush=True)

    profiles: list[AuthorProfile] = []
    evidence: dict[tuple[int, int], PairEvidence] = {}
    for row in rows:
        if row.kind == "author":
            year_min_s, year_max_s, orcid_raw, n_coauthors_s = (row.d or "|||").split("|")
            orcids = frozenset(
                code for code in (_orcid(part) for part in orcid_raw.split(",")) if code
            )
            profiles.append(
                AuthorProfile(
                    author_id=int(row.a),
                    name=row.b,
                    n_papers=int(row.c or 0),
                    year_min=int(year_min_s) if year_min_s not in ("", "None") else None,
                    year_max=int(year_max_s) if year_max_s not in ("", "None") else None,
                    orcids=orcids,
                    n_coauthors=int(n_coauthors_s or 0),
                )
            )
        elif row.kind == "pair":
            shared_s, coauthor_s = row.c.split("|")
            cites_lo_s, cites_hi_s = row.d.split("|")
            evidence[(int(row.a), int(row.b))] = PairEvidence(
                shared_papers=int(shared_s),
                cites_a_to_b=int(cites_lo_s),
                cites_b_to_a=int(cites_hi_s),
                shared_coauthors=int(coauthor_s),
            )
    if not profiles:
        raise SystemExit(f"No author named {name!r} in run {timestamp}")
    return profiles, evidence


def report(profiles: list[AuthorProfile], evidence: dict[tuple[int, int], PairEvidence]) -> None:
    by_id = {profile.author_id: profile for profile in profiles}
    verdicts: dict[tuple[int, int], Verdict] = {}
    for pair, pair_evidence in evidence.items():
        verdicts[pair] = decide_pair(by_id[pair[0]], by_id[pair[1]], pair_evidence)
    groups, conflicts = group_same_people(profiles, verdicts)

    print(f"\n{profiles[0].name}: {len(profiles)} AuthorIds, {len(groups)} person group(s)")
    for index, members in enumerate(groups, start=1):
        print(f"\nGroup {index}")
        for author_id in members:
            profile = by_id[author_id]
            orcid = ", ".join(sorted(profile.orcids)) or "none"
            years = (
                f"{profile.year_min}–{profile.year_max}"
                if profile.year_min is not None
                else "no years"
            )
            print(
                f"  {author_id}  {profile.n_papers} papers  {years}  "
                f"coauthors {profile.n_coauthors}  ORCID {orcid}"
            )
    print("\nPair decisions")
    for pair in sorted(verdicts):
        verdict = verdicts[pair]
        pair_evidence = evidence[pair]
        print(
            f"  {pair[0]} / {pair[1]}: {verdict.label} ({verdict.strength}) — {verdict.reason}"
            f"  [shared papers {pair_evidence.shared_papers},"
            f" citations {pair_evidence.cites_a_to_b}+{pair_evidence.cites_b_to_a},"
            f" shared coauthors {pair_evidence.shared_coauthors}]"
        )
    if conflicts:
        print("\nConflicts: a same-person chain also contains a different-people pair")
        for left, right in conflicts:
            print(f"  {left} / {right}")
    elif len(groups) == 1:
        print("\nOne person. Every same-person link leads back to a single group.")
    else:
        print(f"\n{len(groups)} people. Records in different groups were not linked.")


def _rows_to_people(
    rows: list,
) -> dict[str, tuple[list[AuthorProfile], dict[tuple[int, int], PairEvidence]]]:
    """Group query rows by exact lower-cased name."""
    profiles: dict[str, list[AuthorProfile]] = {}
    evidence: dict[str, dict[tuple[int, int], PairEvidence]] = {}
    for row in rows:
        key = row.name_key
        if row.kind == "author":
            year_min_s, year_max_s, orcid_raw, n_coauthors_s = (row.d or "|||").split("|")
            orcids = frozenset(
                code for code in (_orcid(part) for part in orcid_raw.split(",")) if code
            )
            profiles.setdefault(key, []).append(
                AuthorProfile(
                    author_id=int(row.a),
                    name=row.b,
                    n_papers=int(row.c or 0),
                    year_min=int(year_min_s) if year_min_s not in ("", "None") else None,
                    year_max=int(year_max_s) if year_max_s not in ("", "None") else None,
                    orcids=orcids,
                    n_coauthors=int(n_coauthors_s or 0),
                )
            )
        elif row.kind == "pair":
            shared_s, coauthor_s = row.c.split("|")
            cites_lo_s, cites_hi_s = row.d.split("|")
            evidence.setdefault(key, {})[(int(row.a), int(row.b))] = PairEvidence(
                shared_papers=int(shared_s),
                cites_a_to_b=int(cites_lo_s),
                cites_b_to_a=int(cites_hi_s),
                shared_coauthors=int(coauthor_s),
            )
    return {key: (profiles[key], evidence.get(key, {})) for key in profiles}


def _fetch_network(
    timestamp: str,
) -> dict[str, tuple[list[AuthorProfile], dict[tuple[int, int], PairEvidence]]]:
    """Every repeated exact name in one person-network run."""
    metadata = _metadata_table(timestamp)
    sql = f"""
    CREATE TEMP TABLE axels AS
    WITH base AS (
      SELECT author_id, ANY_VALUE(name) AS name
      FROM {metadata}
      WHERE TRIM(IFNULL(name, '')) != ''
      GROUP BY author_id
    )
    SELECT author_id, name, LOWER(TRIM(name)) AS name_key
    FROM base
    QUALIFY COUNT(*) OVER (PARTITION BY LOWER(TRIM(name))) >= 2;

    CREATE TEMP TABLE papers AS
    SELECT DISTINCT
      pa.AuthorId AS author_id,
      pa.PublicationId AS publication_id,
      p.PublishedYear AS year
    FROM `{AIRAK}.PublicationAuthor` pa
    JOIN axels a ON a.author_id = pa.AuthorId
    JOIN `{AIRAK}.Publication` p ON p.PublicationId = pa.PublicationId
    WHERE pa.AuthorId IS NOT NULL;

    CREATE TEMP TABLE coauthors AS
    SELECT DISTINCT focus.author_id AS axel_id, pa.AuthorId AS coauthor_id
    FROM papers focus
    JOIN axels focus_name ON focus_name.author_id = focus.author_id
    JOIN `{AIRAK}.PublicationAuthor` pa
      ON pa.PublicationId = focus.publication_id
    LEFT JOIN axels same_name
      ON same_name.author_id = pa.AuthorId
     AND same_name.name_key = focus_name.name_key
    WHERE pa.AuthorId IS NOT NULL
      AND pa.AuthorId != focus.author_id
      AND same_name.author_id IS NULL;

    CREATE TEMP TABLE orcids AS
    SELECT s.AuthorId AS author_id, STRING_AGG(DISTINCT s.SourceValue, ',') AS orcid
    FROM `{AIRAK}.AuthorSource` s
    JOIN axels a ON a.author_id = s.AuthorId
    WHERE s.SourceId = 10
    GROUP BY s.AuthorId;

    CREATE TEMP TABLE coauthor_counts AS
    SELECT axel_id AS author_id, COUNT(DISTINCT coauthor_id) AS n_coauthors
    FROM coauthors
    GROUP BY axel_id;

    CREATE TEMP TABLE shared_papers AS
    SELECT p1.author_id AS lo, p2.author_id AS hi, COUNT(DISTINCT p1.publication_id) AS n
    FROM papers p1
    JOIN papers p2
      ON p2.publication_id = p1.publication_id
     AND p1.author_id < p2.author_id
    JOIN axels a1 ON a1.author_id = p1.author_id
    JOIN axels a2 ON a2.author_id = p2.author_id AND a2.name_key = a1.name_key
    GROUP BY lo, hi;

    CREATE TEMP TABLE shared_coauthors AS
    SELECT c1.axel_id AS lo, c2.axel_id AS hi, COUNT(DISTINCT c1.coauthor_id) AS n
    FROM coauthors c1
    JOIN axels a1 ON a1.author_id = c1.axel_id
    JOIN coauthors c2
      ON c2.coauthor_id = c1.coauthor_id
     AND c2.axel_id > c1.axel_id
    JOIN axels a2 ON a2.author_id = c2.axel_id AND a2.name_key = a1.name_key
    GROUP BY lo, hi;

    CREATE TEMP TABLE citations AS
    SELECT
      citing.author_id AS citing_author,
      cited.author_id AS cited_author,
      COUNT(DISTINCT pc.PublicationId) AS n
    FROM `{AIRAK}.PublicationCitation` pc
    JOIN papers citing ON citing.publication_id = pc.PublicationId
    JOIN papers cited ON cited.publication_id = pc.CitedPublicationId
    JOIN axels a1 ON a1.author_id = citing.author_id
    JOIN axels a2
      ON a2.author_id = cited.author_id
     AND a2.name_key = a1.name_key
    WHERE pc.PublicationId != pc.CitedPublicationId
      AND citing.author_id != cited.author_id
    GROUP BY citing_author, cited_author;

    SELECT kind, a, b, c, d, name_key FROM (
      SELECT
        'author' AS kind,
        CAST(axels.author_id AS STRING) AS a,
        axels.name AS b,
        CAST(COUNT(DISTINCT papers.publication_id) AS STRING) AS c,
        CONCAT(
          IFNULL(CAST(MIN(papers.year) AS STRING), ''), '|',
          IFNULL(CAST(MAX(papers.year) AS STRING), ''), '|',
          IFNULL(orcids.orcid, ''), '|',
          CAST(IFNULL(coauthor_counts.n_coauthors, 0) AS STRING)
        ) AS d,
        axels.name_key
      FROM axels
      LEFT JOIN papers ON papers.author_id = axels.author_id
      LEFT JOIN orcids ON orcids.author_id = axels.author_id
      LEFT JOIN coauthor_counts ON coauthor_counts.author_id = axels.author_id
      GROUP BY axels.author_id, axels.name, axels.name_key, orcids.orcid, coauthor_counts.n_coauthors
      UNION ALL
      SELECT
        'pair',
        CAST(lo.author_id AS STRING),
        CAST(hi.author_id AS STRING),
        CONCAT(
          CAST(IFNULL(shared_papers.n, 0) AS STRING), '|',
          CAST(IFNULL(shared_coauthors.n, 0) AS STRING)
        ),
        CONCAT(
          CAST(IFNULL(lo_to_hi.n, 0) AS STRING), '|',
          CAST(IFNULL(hi_to_lo.n, 0) AS STRING)
        ),
        lo.name_key
      FROM axels lo
      JOIN axels hi
        ON hi.name_key = lo.name_key
       AND lo.author_id < hi.author_id
      LEFT JOIN shared_papers
        ON shared_papers.lo = lo.author_id AND shared_papers.hi = hi.author_id
      LEFT JOIN shared_coauthors
        ON shared_coauthors.lo = lo.author_id AND shared_coauthors.hi = hi.author_id
      LEFT JOIN citations lo_to_hi
        ON lo_to_hi.citing_author = lo.author_id
       AND lo_to_hi.cited_author = hi.author_id
      LEFT JOIN citations hi_to_lo
        ON hi_to_lo.citing_author = hi.author_id
       AND hi_to_lo.cited_author = lo.author_id
    )
    ORDER BY name_key, kind, a
    """
    client = bigquery.Client(project=BQ_READ_PROJECT, location="EU")
    job = client.query(sql)
    rows = list(job.result())
    print(f"Query scanned {job.total_bytes_processed or 0:,} bytes", flush=True)
    print(f"Rows returned {len(rows):,}", flush=True)
    return _rows_to_people(rows)


def report_merges(
    people: dict[str, tuple[list[AuthorProfile], dict[tuple[int, int], PairEvidence]]],
) -> None:
    """Print only the groups the rules collapse into one person."""
    merged_rows = []
    conflict_rows = []
    names_with_a_merge = 0
    for _key, (profiles, evidence) in people.items():
        by_id = {profile.author_id: profile for profile in profiles}
        verdicts = {
            pair: decide_pair(by_id[pair[0]], by_id[pair[1]], pair_evidence)
            for pair, pair_evidence in evidence.items()
        }
        groups, conflicts = group_same_people(profiles, verdicts)
        kept = [members for members in groups if len(members) > 1]
        if not kept:
            continue
        names_with_a_merge += 1
        display = max(profiles, key=lambda profile: profile.n_papers).name
        for members in kept:
            reasons = []
            for left_i, left in enumerate(members):
                for right in members[left_i + 1 :]:
                    pair = tuple(sorted((left, right)))
                    verdict = verdicts.get(pair)
                    if verdict is None or verdict.label != "same_person":
                        continue
                    reasons.append(
                        f"{left} / {right}: {verdict.strength} — {verdict.reason}"
                    )
            merged_rows.append((display, members, by_id, reasons))
        for left, right in conflicts:
            conflict_rows.append((display, left, right))

    merged_rows.sort(key=lambda item: (item[0].lower(), -len(item[1]), item[1][0]))
    author_ids = {author_id for _name, members, _by_id, _reasons in merged_rows for author_id in members}
    print(
        f"\n{len(people):,} repeated names, {names_with_a_merge:,} contain a merge, "
        f"{len(merged_rows):,} merged groups, {len(author_ids):,} AuthorIds"
    )
    for display, members, by_id, reasons in merged_rows:
        print(f"\n{display}")
        for author_id in members:
            profile = by_id[author_id]
            orcid = ", ".join(sorted(profile.orcids)) or "none"
            years = (
                f"{profile.year_min}–{profile.year_max}"
                if profile.year_min is not None
                else "no years"
            )
            print(
                f"  {author_id}  {profile.n_papers} papers  {years}  ORCID {orcid}"
            )
        for reason in reasons:
            print(f"  {reason}")
    if conflict_rows:
        print(f"\nConflicts: {len(conflict_rows)}")
        for display, left, right in conflict_rows:
            print(f"  {display}: {left} / {right}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Group same-name AIRAK authors into people.")
    parser.add_argument("--name", default="", help="Exact author name, case insensitive.")
    parser.add_argument("--timestamp", default="", help="Person-network run YYYYMMDD_HHMMSS.")
    parser.add_argument("--self-check", action="store_true", help="Run the Cleeremans fixtures only.")
    parser.add_argument(
        "--all",
        action="store_true",
        help="Score every repeated name in the person-network run.",
    )
    args = parser.parse_args()
    self_check()
    if args.self_check and not args.name and not args.all:
        return
    if args.all:
        if not args.timestamp:
            raise SystemExit("Pass --timestamp with --all.")
        report_merges(_fetch_network(args.timestamp))
        return
    if not args.name or not args.timestamp:
        raise SystemExit("Pass --name and --timestamp, --all and --timestamp, or --self-check.")
    profiles, evidence = _fetch(args.name, args.timestamp)
    report(profiles, evidence)


if __name__ == "__main__":
    try:
        main()
    except Exception:
        sys.stderr.write("Author identity check failed\n")
        raise
