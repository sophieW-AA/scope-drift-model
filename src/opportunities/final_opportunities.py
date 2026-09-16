"""Final, auditable journal-opportunity slate.

The candidate universe is the 252 OpenAlex subfields. Market qualification is
computed from all-publisher OpenAlex works and cannot see Frontiers volume.
Leiden is used afterwards to test whether a market has a coherent,
journal-shaped footprint in the citation neighbourhood. Frontiers placement is
then used only to choose the action: greenfield launch, consolidation launch,
grow an existing title, or validate/pass.

This module deliberately does not consume any prior canvas or hand-exported
CSV. It writes a versioned BigQuery result and manifest so the presentation can
always be traced back to source data, thresholds and a scope-drift run.
"""

from __future__ import annotations

import argparse
import json
import logging
import re
from pathlib import Path

import pandas as pd

from . import config as C

log = logging.getLogger("opportunities.final")

OPENALEX_DATASET = "ocean-breeze-tier-3.openalex"
OPENALEX_WORKS = f"{OPENALEX_DATASET}.works"
OPENALEX_SUBFIELDS = f"{OPENALEX_DATASET}.subfields"
FINAL_PREFIX = "final_journal_opportunities"
FINAL_MANIFEST_PREFIX = "final_journal_opportunities_manifest"
MARKET_BASE_YEAR = 2022
MARKET_LATE_YEAR = 2025
MARKET_MIN_ANNUAL = 10_000
MARKET_MIN_CAGR = 0.05
LOW_CONCENTRATION_MAX = 0.25
FINAL_SHORTLIST_SIZE = 20


def _norm(value: object) -> str:
    return re.sub(r"[^a-z0-9]+", " ", str(value or "").lower()).strip()


def _title_tokens(value: object) -> set[str]:
    stop = {
        "and", "of", "the", "in", "for", "frontiers", "science", "sciences",
        "research", "studies", "general",
    }
    return {t for t in _norm(value).split() if len(t) > 3 and t not in stop}


def title_matches_subfield(title: object, subfield: object) -> bool:
    """Conservative title-to-subfield coverage test.

    This is portfolio screening, not market mapping. A title counts as a
    dedicated home only when at least half the meaningful subfield tokens occur
    in its name. Broad adjacent anchors such as "Frontiers in Medicine" do not
    hide Pulmonary and Respiratory Medicine.
    """
    title_set = _title_tokens(title)
    field_set = _title_tokens(subfield)
    if not title_set or not field_set:
        return False
    if len(title_set & field_set) / len(field_set) >= 0.5:
        return True
    ordered = [t for t in _norm(subfield).split() if t in field_set]
    # Compound governed subfields often append adjacent areas after their
    # defining discipline: "Endocrinology, Diabetes and Metabolism" is already
    # covered by Frontiers in Endocrinology. Broad suffixes such as "Medicine"
    # must not make Frontiers in Medicine a dedicated respiratory title.
    generic = {
        "medicine", "health", "science", "sciences", "engineering",
        "management", "systems", "studies",
    }
    first_defining = next((t for t in ordered if t not in generic), "")
    return bool(first_defining and first_defining in title_set)


def find_dedicated_home(row: pd.Series) -> str:
    """Return the first active Frontiers title that explicitly names the market."""
    candidates = [
        str(row.get("anchor_journal") or ""),
        *str(row.get("fi_titles_10plus") or "").split("; "),
        str(row.get("lead_journal") or ""),
    ]
    for title in candidates:
        if title_matches_subfield(title, row["taxonomy_subfield"]):
            return title
    return ""


def governed_score(row: pd.Series) -> int:
    """Recompute the documented 0–12 opportunity evidence score."""
    funding = str(row.get("funding") or "").lower()
    score = 2 if funding == "strong" else 1 if funding == "mid" else 0
    funded_pct = row.get("funded_pct")
    gold_pct = row.get("gold_oa_pct")
    cagr = row.get("cagr")
    market = row.get("mkt_2025")
    top3 = row.get("top3_share")
    fi_articles = row.get("fi_articles_2025")
    anchor = str(row.get("anchor_journal") or "").strip()
    if pd.notna(funded_pct) and float(funded_pct) >= 0.45:
        score += 1
    if pd.notna(gold_pct) and float(gold_pct) >= 0.38:
        score += 1
    if pd.notna(cagr):
        score += 2 if float(cagr) >= 0.10 else 1 if float(cagr) >= 0.05 else 0
    if pd.notna(market):
        score += 2 if float(market) >= 30_000 else 1 if float(market) >= 15_000 else 0
    if (pd.isna(fi_articles) or float(fi_articles) == 0) and not anchor:
        score += 1
    if pd.notna(top3) and float(top3) < LOW_CONCENTRATION_MAX:
        score += 1
    return int(score)


def grade_for_score(score: int) -> str:
    return "A" if score >= 8 else "B" if score >= 5 else "C"


def route_action(row: pd.Series) -> str:
    """Choose a portfolio action after market qualification is fixed."""
    if not bool(row.get("market_qualified", False)):
        return "pass_market"
    if str(row.get("scope_confidence") or "") == "low":
        return "validate_scope"
    if str(row.get("ownership_status") or "") == "dedicated_home":
        return "grow_existing"
    if float(row.get("n_fi_3y") or 0) < C.WORLD_GREENFIELD_MAX_FI_3Y:
        return "launch_greenfield"
    return "launch_consolidation"


def classify_ownership(row: pd.Series) -> str:
    if bool(row.get("dedicated_home", False)):
        return "dedicated_home"
    lead_share = row.get("lead_share")
    core_share = row.get("run_fi_core_share")
    if (
        pd.notna(lead_share)
        and float(lead_share) >= C.OWNED_MIN_FI_SHARE
        and pd.notna(core_share)
        and float(core_share) >= 0.60
    ):
        return "adjacent_core_owner"
    if pd.notna(lead_share) and float(lead_share) >= C.OWNED_MIN_FI_SHARE:
        return "concentrated_drift"
    return "scattered"


def coverage_status(row: pd.Series) -> str:
    if bool(row.get("dedicated_home", False)):
        return "served"
    ratio = row.get("fi_share_vs_portfolio")
    if pd.isna(ratio) or float(ratio) < C.MARKET_WHITESPACE_RATIO:
        return "whitespace"
    if float(ratio) < C.MARKET_COVERED_RATIO:
        return "under_indexed"
    return "fragmented_existing"


def discover_latest_complete_run() -> str:
    """Latest portfolio-scale run with complete meso and micro taxonomy."""
    from . import bq as bqmod

    taxonomy_tables = [
        t.table_id
        for t in bqmod.client().list_tables(
            f"{C.BQ_PROJECT}.{C.BQ_LABEL_DATASET}"
        )
    ]
    raw_tables = [
        t.table_id
        for t in bqmod.client().list_tables(
            f"{C.BQ_PROJECT}.{C.BQ_DATASET}"
        )
    ]
    raw = {
        re.search(r"classification_raw_(\d{8}_\d{6})$", name).group(1)
        for name in raw_tables
        if re.search(r"classification_raw_(\d{8}_\d{6})$", name)
    }
    metadata = {
        re.search(r"pub_metadata_raw_(\d{8}_\d{6})$", name).group(1)
        for name in raw_tables
        if re.search(r"pub_metadata_raw_(\d{8}_\d{6})$", name)
    }
    scope_flags = {
        re.search(r"paper_scope_(\d{8}_\d{6})$", name).group(1)
        for name in raw_tables
        if re.search(r"paper_scope_(\d{8}_\d{6})$", name)
    }
    meso_labels = {
        re.search(r"cluster_labels_meso_(\d{8}_\d{6})$", name).group(1)
        for name in taxonomy_tables
        if re.search(r"cluster_labels_meso_(\d{8}_\d{6})$", name)
    }
    micro_labels = {
        re.search(r"cluster_labels_micro_(\d{8}_\d{6})$", name).group(1)
        for name in taxonomy_tables
        if re.search(r"cluster_labels_micro_(\d{8}_\d{6})$", name)
    }
    candidates = sorted(
        raw & metadata & scope_flags & meso_labels & micro_labels, reverse=True
    )
    for run in candidates:
        meso = bqmod.client().get_table(
            f"{C.BQ_PROJECT}.{C.BQ_LABEL_DATASET}.cluster_labels_meso_{run}"
        )
        micro = bqmod.client().get_table(
            f"{C.BQ_PROJECT}.{C.BQ_LABEL_DATASET}.cluster_labels_micro_{run}"
        )
        # Exclude journal-specific probes and partially named global runs.
        if meso.num_rows >= 100 and micro.num_rows >= 500:
            return run
    if not candidates:
        raise RuntimeError("no complete classification + metadata + taxonomy run found")
    raise RuntimeError(
        "taxonomy-labelled runs exist, but none is portfolio-scale and complete"
    )


def fetch_live_market() -> pd.DataFrame:
    """All 252 OpenAlex subfields with fresh market, funding and FI placement."""
    from . import bq as bqmod

    query = f"""
    WITH eligible_works AS (
      SELECT
        w.id AS work_id,
        w.publication_year AS year,
        w.primary_topic.subfield.id AS subfield_id,
        w.primary_topic.subfield.display_name AS subfield,
        w.primary_topic.field.display_name AS field,
        w.primary_topic.domain.display_name AS domain,
        w.primary_location.source.id AS source_id,
        w.primary_location.source.display_name AS source_name,
        w.primary_location.source.host_organization_name AS host_name,
        w.open_access.oa_status AS oa_status,
        ARRAY_LENGTH(w.funders.list) > 0 AS is_funded,
        ARRAY_LENGTH(w.awards.list) > 0 AS has_award
      FROM `{OPENALEX_WORKS}` w
      WHERE w.publication_year BETWEEN {MARKET_BASE_YEAR} AND {MARKET_LATE_YEAR}
        AND w.type = 'article'
        AND w.primary_location.source.type = 'journal'
        AND (w.language IS NULL OR w.language = 'en')
        AND w.primary_topic.subfield.id IS NOT NULL
    ),
    annual AS (
      SELECT
        subfield_id,
        ANY_VALUE(subfield) AS subfield,
        ANY_VALUE(field) AS field,
        ANY_VALUE(domain) AS domain,
        year,
        COUNT(*) AS n_world,
        COUNTIF(host_name = 'Frontiers Media') AS n_fi,
        COUNTIF(is_funded) AS n_funded,
        COUNTIF(oa_status = 'gold') AS n_gold,
        COUNTIF(has_award) AS n_awarded
      FROM eligible_works
      GROUP BY subfield_id, year
    ),
    source_counts AS (
      SELECT subfield_id, source_id, ANY_VALUE(source_name) AS source_name,
             COUNT(*) AS n
      FROM eligible_works
      WHERE year = {MARKET_LATE_YEAR}
      GROUP BY subfield_id, source_id
    ),
    source_rank AS (
      SELECT *, ROW_NUMBER() OVER (
        PARTITION BY subfield_id ORDER BY n DESC, source_name
      ) AS rn
      FROM source_counts
    ),
    concentration AS (
      SELECT
        subfield_id,
        SUM(IF(rn <= 3, n, 0)) AS top3_n,
        STRING_AGG(
          IF(rn <= 3, CONCAT(source_name, ' (', CAST(n AS STRING), ')'), NULL),
          '; ' ORDER BY rn
        ) AS top_competitors
      FROM source_rank
      GROUP BY subfield_id
    ),
    fi_title_counts AS (
      SELECT subfield_id, source_name AS journal, COUNT(*) AS n
      FROM eligible_works
      WHERE year BETWEEN {MARKET_LATE_YEAR - 2} AND {MARKET_LATE_YEAR}
        AND host_name = 'Frontiers Media'
      GROUP BY subfield_id, journal
    ),
    fi_rank AS (
      SELECT *,
        SAFE_DIVIDE(n, SUM(n) OVER (PARTITION BY subfield_id)) AS lead_share,
        SUM(n) OVER (PARTITION BY subfield_id) AS n_fi_3y,
        COUNTIF(n >= 10) OVER (PARTITION BY subfield_id) AS n_titles_10plus,
        ROW_NUMBER() OVER (
          PARTITION BY subfield_id ORDER BY n DESC, journal
        ) AS rn
      FROM fi_title_counts
    ),
    fi_summary AS (
      SELECT
        subfield_id,
        MAX(IF(rn = 1, journal, NULL)) AS journal,
        MAX(IF(rn = 1, n, NULL)) AS lead_n,
        MAX(IF(rn = 1, lead_share, NULL)) AS lead_share,
        MAX(n_fi_3y) AS n_fi_3y,
        MAX(n_titles_10plus) AS n_titles_10plus,
        STRING_AGG(
          IF(n >= 10, journal, NULL), '; ' ORDER BY n DESC, journal
        ) AS fi_titles_10plus
      FROM fi_rank
      GROUP BY subfield_id
    ),
    rolled AS (
      SELECT
        s.id AS subfield_id,
        s.display_name AS taxonomy_subfield,
        s.field.display_name AS taxonomy_field,
        s.domain.display_name AS taxonomy_domain,
        MAX(IF(a.year = {MARKET_BASE_YEAR}, a.n_world, NULL)) AS n_global_base,
        MAX(IF(a.year = {MARKET_LATE_YEAR}, a.n_world, NULL)) AS mkt_2025,
        MAX(IF(a.year = {MARKET_LATE_YEAR}, a.n_fi, NULL)) AS fi_articles_2025,
        SUM(IF(a.year BETWEEN {MARKET_LATE_YEAR - 2} AND {MARKET_LATE_YEAR}, a.n_fi, 0))
          AS n_fi_3y,
        SAFE_DIVIDE(
          MAX(IF(a.year = {MARKET_LATE_YEAR}, a.n_funded, NULL)),
          MAX(IF(a.year = {MARKET_LATE_YEAR}, a.n_world, NULL))
        ) AS funded_pct,
        SAFE_DIVIDE(
          MAX(IF(a.year = {MARKET_LATE_YEAR}, a.n_gold, NULL)),
          MAX(IF(a.year = {MARKET_LATE_YEAR}, a.n_world, NULL))
        ) AS gold_oa_pct,
        SAFE_DIVIDE(
          MAX(IF(a.year = {MARKET_LATE_YEAR}, a.n_awarded, NULL)),
          MAX(IF(a.year = {MARKET_LATE_YEAR}, a.n_world, NULL))
        ) AS awarded_pct
      FROM `{OPENALEX_SUBFIELDS}` s
      LEFT JOIN annual a ON a.subfield_id = s.id
      GROUP BY subfield_id, taxonomy_subfield, taxonomy_field, taxonomy_domain
    ),
    totals AS (
      SELECT
        SUM(IF(year = {MARKET_LATE_YEAR}, n_world, 0)) AS world_total,
        SUM(IF(year = {MARKET_LATE_YEAR}, n_fi, 0)) AS fi_total
      FROM annual
    )
    SELECT
      r.*,
      SAFE_DIVIDE(c.top3_n, r.mkt_2025) AS top3_share,
      c.top_competitors,
      f.journal AS lead_journal,
      f.lead_n AS lead_n_3y,
      f.lead_share,
      COALESCE(f.n_titles_10plus, 0) AS n_titles_10plus,
      f.fi_titles_10plus,
      SAFE_DIVIDE(r.fi_articles_2025, r.mkt_2025) AS fi_share,
      SAFE_DIVIDE(
        SAFE_DIVIDE(r.fi_articles_2025, r.mkt_2025),
        SAFE_DIVIDE(t.fi_total, t.world_total)
      ) AS fi_share_vs_portfolio,
      SAFE_DIVIDE(t.fi_total, t.world_total) AS fi_portfolio_share
    FROM rolled r
    CROSS JOIN totals t
    LEFT JOIN concentration c USING (subfield_id)
    LEFT JOIN fi_summary f USING (subfield_id)
    """
    out = bqmod.client().query(query).result().to_dataframe()
    years = MARKET_LATE_YEAR - MARKET_BASE_YEAR
    out["cagr"] = (
        out["mkt_2025"] / out["n_global_base"].replace(0, pd.NA)
    ) ** (1 / years) - 1
    out["market_qualified"] = (
        (out["mkt_2025"] >= MARKET_MIN_ANNUAL)
        & (out["cagr"] >= MARKET_MIN_CAGR)
    )
    return out


def _fetch_jd_reference() -> pd.DataFrame:
    from . import bq as bqmod

    try:
        return bqmod.fetch_jd_opportunities()
    except Exception:
        return pd.DataFrame()


def enrich_governed_reference(market: pd.DataFrame) -> pd.DataFrame:
    """Attach governed funding, anchor and competitor context by taxonomy path."""
    jd = _fetch_jd_reference()
    if jd.empty:
        for col in (
            "funding", "anchor_journal", "competitor_1", "competitor_2",
            "competitor_3", "source_action",
        ):
            market[col] = ""
        return market

    for frame, cols in (
        (market, ("taxonomy_domain", "taxonomy_field", "taxonomy_subfield")),
        (jd, ("domain", "field", "subfield")),
    ):
        frame["_join_key"] = frame[list(cols)].apply(
            lambda r: "|".join(_norm(x) for x in r), axis=1
        )
    keep = [
        "_join_key", "funding", "anchor_journal", "competitor_1",
        "competitor_2", "competitor_3", "source_action", "score",
    ]
    for col in keep:
        if col not in jd:
            jd[col] = ""
    reference = jd[keep].drop_duplicates("_join_key").rename(
        columns={"score": "governed_source_score"}
    )
    out = market.merge(reference, on="_join_key", how="left")
    out = out.drop(columns="_join_key")
    for col in keep[1:-1]:
        out[col] = out[col].fillna("")
    return out


def fetch_leiden_overlap(
    run_timestamp: str, subfield_ids: list[str]
) -> pd.DataFrame:
    """Paper-level OpenAlex subfield overlap with Leiden meso/micro communities."""
    from google.cloud import bigquery
    from . import bq as bqmod

    if not subfield_ids:
        return pd.DataFrame()
    tbl_c = f"{C.BQ_PROJECT}.{C.BQ_DATASET}.classification_raw_{run_timestamp}"
    tbl_m = f"{C.BQ_PROJECT}.{C.BQ_DATASET}.pub_metadata_raw_{run_timestamp}"
    tbl_s = f"{C.BQ_PROJECT}.{C.BQ_DATASET}.paper_scope_{run_timestamp}"
    query = f"""
    WITH scope_flags AS (
      SELECT
        int_id,
        journal,
        LOGICAL_OR(is_oos) AS is_oos,
        LOGICAL_OR(is_borderline) AS is_borderline
      FROM `{tbl_s}`
      WHERE cluster_level = 'meso'
      GROUP BY int_id, journal
    ),
    run_pub AS (
      SELECT DISTINCT
        SAFE_CAST(m.pub_id AS INT64) AS publication_id,
        CAST(c.macro AS INT64) AS macro_id,
        CAST(c.meso AS INT64) AS meso_id,
        CAST(c.micro AS INT64) AS micro_id,
        CAST(m.is_frontiers AS STRING) IN ('1', 'true', 'True') AS is_fi,
        m.journal,
        COALESCE(s.is_oos, FALSE) AS is_oos,
        COALESCE(s.is_borderline, FALSE) AS is_borderline
      FROM `{tbl_c}` c
      JOIN `{tbl_m}` m USING (int_id)
      LEFT JOIN scope_flags s
        ON s.int_id = m.int_id AND s.journal = m.journal
      WHERE SAFE_CAST(m.pub_id AS INT64) IS NOT NULL
        AND c.meso IS NOT NULL
        AND c.micro IS NOT NULL
    ),
    airak_doi AS (
      SELECT DISTINCT
        p.PublicationId AS publication_id,
        REGEXP_REPLACE(LOWER(p.Doi), r'^https?://(dx\\.)?doi\\.org/', '') AS doi
      FROM `{C.AIRAK_PUBLICATION}` p
      JOIN (SELECT DISTINCT publication_id FROM run_pub) r
        ON r.publication_id = p.PublicationId
      WHERE p.Doi IS NOT NULL AND TRIM(p.Doi) != ''
    ),
    openalex AS (
      SELECT
        REGEXP_REPLACE(LOWER(w.doi), r'^https?://(dx\\.)?doi\\.org/', '') AS doi,
        ANY_VALUE(w.primary_topic.subfield.id) AS subfield_id
      FROM `{OPENALEX_WORKS}` w
      WHERE w.publication_year BETWEEN 2023 AND {MARKET_LATE_YEAR}
        AND w.primary_topic.subfield.id IN UNNEST(@subfield_ids)
        AND w.doi IS NOT NULL
      GROUP BY doi
    )
    SELECT
      o.subfield_id,
      r.macro_id,
      r.meso_id,
      r.micro_id,
      r.journal,
      r.is_oos,
      r.is_borderline,
      COUNT(*) AS n_papers,
      COUNTIF(r.is_fi) AS n_fi,
      COUNTIF(NOT r.is_fi) AS n_non_fi
    FROM run_pub r
    JOIN airak_doi a USING (publication_id)
    JOIN openalex o USING (doi)
    GROUP BY subfield_id, macro_id, meso_id, micro_id, journal, is_oos, is_borderline
    """
    cfg = bigquery.QueryJobConfig(
        query_parameters=[
            bigquery.ArrayQueryParameter(
                "subfield_ids", "STRING", subfield_ids
            )
        ]
    )
    return (
        bqmod.client().query(query, job_config=cfg).result().to_dataframe()
    )


def assemble_scope(
    rows: pd.DataFrame, coverage_target: float = C.PRIMARY_COVERAGE
) -> dict:
    """Smallest sibling meso set covering the target share of non-FI papers."""
    if rows.empty or int(rows["n_non_fi"].sum()) == 0:
        return {
            "mapped_non_fi_papers": 0,
            "scope_community_ids": [],
            "scope_community_count": 0,
            "scope_coverage": 0.0,
            "top_community_share": 0.0,
            "dominant_macro_share": 0.0,
            "scope_confidence": "low",
        }
    total = int(rows["n_non_fi"].sum())
    macro = (
        rows.groupby("macro_id", as_index=False)["n_non_fi"].sum()
        .sort_values("n_non_fi", ascending=False)
        .reset_index(drop=True)
    )
    dominant_macro_share = float(macro.iloc[0]["n_non_fi"] / total)
    meso = (
        rows.groupby("meso_id", as_index=False)["n_non_fi"].sum()
        .sort_values("n_non_fi", ascending=False)
        .reset_index(drop=True)
    )
    meso["cum_share"] = meso["n_non_fi"].cumsum() / total
    crossing = int((meso["cum_share"] < coverage_target).sum())
    selected = meso.iloc[: min(crossing + 1, len(meso))]
    count = len(selected)
    mapped = total
    coverage = float(selected["n_non_fi"].sum() / total)
    top_share = float(meso.iloc[0]["n_non_fi"] / total)
    if mapped >= 300 and coverage >= coverage_target and count <= 30:
        confidence = "high"
    elif mapped >= 100 and coverage >= 0.70 and count <= 45:
        confidence = "medium"
    else:
        confidence = "low"
    return {
        "mapped_non_fi_papers": mapped,
        "scope_community_ids": selected["meso_id"].astype(int).tolist(),
        "scope_community_count": count,
        "scope_coverage": coverage,
        "top_community_share": top_share,
        "dominant_macro_share": dominant_macro_share,
        "scope_confidence": confidence,
    }


def build_scope_evidence(
    run_timestamp: str, market: pd.DataFrame
) -> pd.DataFrame:
    """Leiden names and section themes for every market-qualified subfield."""
    from . import bq as bqmod

    qualified = market[market["market_qualified"]].copy()
    overlap = fetch_leiden_overlap(
        run_timestamp, qualified["subfield_id"].astype(str).tolist()
    )
    meso_labels = bqmod.fetch_cluster_labels(run_timestamp, "meso")
    micro_labels = bqmod.fetch_cluster_labels(run_timestamp, "micro")
    meso_name = dict(
        zip(
            meso_labels["community_id"].astype(int),
            meso_labels["community_label"].fillna("").astype(str),
        )
    )
    micro_name = dict(
        zip(
            micro_labels["community_id"].astype(int),
            micro_labels["community_label"].fillna("").astype(str),
        )
    )
    evidence = []
    for sid in qualified["subfield_id"].astype(str):
        rows = overlap[overlap["subfield_id"].astype(str) == sid].copy()
        scope = assemble_scope(rows)
        selected = set(scope["scope_community_ids"])
        scope["subfield_id"] = sid
        fi_rows = rows[rows["n_fi"] > 0] if not rows.empty else rows
        scope["run_fi_papers"] = int(fi_rows["n_fi"].sum()) if not fi_rows.empty else 0
        scope["run_fi_core_share"] = (
            float(fi_rows.loc[~fi_rows["is_oos"], "n_fi"].sum())
            / scope["run_fi_papers"]
            if scope["run_fi_papers"]
            else pd.NA
        )
        if not fi_rows.empty:
            journal_counts = (
                fi_rows.groupby("journal", dropna=True)["n_fi"].sum()
                .sort_values(ascending=False)
            )
            scope["run_lead_journal"] = (
                str(journal_counts.index[0]) if len(journal_counts) else ""
            )
            scope["run_lead_share"] = (
                float(journal_counts.iloc[0] / journal_counts.sum())
                if len(journal_counts)
                else pd.NA
            )
        else:
            scope["run_lead_journal"] = ""
            scope["run_lead_share"] = pd.NA
        named = [
            meso_name.get(i, "").strip() for i in scope["scope_community_ids"]
        ]
        scope["label_strength"] = (
            sum(bool(name) for name in named) / len(named) if named else 0.0
        )
        scope["scope_names"] = "; ".join(
            meso_name.get(i, f"meso:{i}") for i in scope["scope_community_ids"]
        )
        if selected and not rows.empty:
            micro = (
                rows[rows["meso_id"].astype(int).isin(selected)]
                .groupby("micro_id", as_index=False)["n_non_fi"].sum()
                .sort_values("n_non_fi", ascending=False)
                .head(8)
            )
            scope["section_themes"] = "; ".join(
                micro_name.get(int(i), f"micro:{int(i)}")
                for i in micro["micro_id"]
            )
        else:
            scope["section_themes"] = ""
        if scope["label_strength"] < 0.8:
            scope["scope_confidence"] = "low"
        evidence.append(scope)
    return pd.DataFrame(evidence)


def _scope_confidence_points(value: object) -> int:
    return {"high": 2, "medium": 1}.get(str(value), 0)


def _cannibalisation_risk(row: pd.Series) -> str:
    if bool(row.get("dedicated_home", False)):
        return "duplicate"
    lead_share = row.get("lead_share")
    if pd.notna(lead_share) and float(lead_share) >= C.OWNED_MIN_FI_SHARE:
        return "high"
    ratio = row.get("fi_share_vs_portfolio")
    if pd.notna(ratio) and float(ratio) >= C.MARKET_COVERED_RATIO:
        return "medium"
    return "low"


def _evidence_warnings(row: pd.Series) -> str:
    warnings: list[str] = []
    if not str(row.get("funding") or ""):
        warnings.append("funding evidence not present in governed reference")
    if str(row.get("scope_confidence") or "") == "medium":
        warnings.append("Leiden scope requires editorial validation")
    if str(row.get("cannibalisation_risk") or "") in {"high", "duplicate"}:
        warnings.append("high overlap with one operating Frontiers title")
    top3 = row.get("top3_share")
    if pd.notna(top3) and float(top3) >= LOW_CONCENTRATION_MAX:
        warnings.append("competitor market is relatively concentrated")
    return "; ".join(warnings)


def _action_reason(row: pd.Series) -> str:
    action = row["action"]
    if action == "launch_greenfield":
        return (
            f"Market qualifies independently; only {int(row['n_fi_3y'])} "
            "Frontiers papers in three years and no dedicated title."
        )
    if action == "launch_consolidation":
        lead = str(row.get("lead_journal") or "the leading title")
        share = float(row.get("lead_share") or 0)
        return (
            f"Frontiers already publishes here, but {lead} holds only "
            f"{share:.0%}; a dedicated title would consolidate scattered volume."
        )
    if action == "grow_existing":
        home = (
            row.get("dedicated_home_title")
            or row.get("anchor_journal")
            or row.get("lead_journal")
        )
        return (
            f"{home} "
            "already names the market; invest in that title rather than duplicate it."
        )
    if action == "validate_scope":
        return "The market passes, but Leiden does not provide a coherent enough journal scope."
    return "The subfield does not pass the market size and growth gate."


def build_final_opportunities(
    run_timestamp: str | None = None, write: bool = True
) -> tuple[pd.DataFrame, dict]:
    """Execute the clean hybrid run and return results plus manifest."""
    from . import bq as bqmod

    run_timestamp = run_timestamp or discover_latest_complete_run()
    market = enrich_governed_reference(fetch_live_market())
    scope = build_scope_evidence(run_timestamp, market)
    out = market.merge(scope, on="subfield_id", how="left")
    for col, default in (
        ("scope_confidence", "low"),
        ("scope_names", ""),
        ("section_themes", ""),
        ("mapped_non_fi_papers", 0),
        ("scope_community_count", 0),
        ("scope_coverage", 0.0),
        ("top_community_share", 0.0),
        ("dominant_macro_share", 0.0),
        ("label_strength", 0.0),
        ("run_fi_papers", 0),
        ("run_fi_core_share", pd.NA),
        ("run_lead_journal", ""),
        ("run_lead_share", pd.NA),
    ):
        out[col] = out[col].fillna(default)

    out["dedicated_home_title"] = out.apply(
        find_dedicated_home,
        axis=1,
    )
    out["dedicated_home"] = out["dedicated_home_title"].astype(str).str.strip().ne("")
    out["ownership_status"] = out.apply(classify_ownership, axis=1)
    recomputed_score = out.apply(governed_score, axis=1)
    out["score"] = out.get(
        "governed_source_score", pd.Series(pd.NA, index=out.index)
    ).fillna(recomputed_score).astype(int)
    out["grade"] = out["score"].map(grade_for_score)
    out["coverage_status"] = out.apply(coverage_status, axis=1)
    out["action"] = out.apply(route_action, axis=1)
    out["expected_fi_at_parity"] = out["mkt_2025"] * out["fi_portfolio_share"]
    out["cannibalisation_risk"] = out.apply(_cannibalisation_risk, axis=1)
    cannibal_penalty = out["cannibalisation_risk"].map(
        {"duplicate": 3, "high": 2, "medium": 1, "low": 0}
    )
    out["launch_confidence"] = (
        out["score"]
        + out["scope_confidence"].map(_scope_confidence_points)
        + (out["coverage_status"] == "whitespace").astype(int)
        - cannibal_penalty
    )
    out["proposed_journal"] = "Frontiers in " + out["taxonomy_subfield"].str.replace(
        r"\s*\[.*?\]\s*", "", regex=True
    )
    out["action_reason"] = out.apply(_action_reason, axis=1)
    out["evidence_warnings"] = out.apply(_evidence_warnings, axis=1)
    out["is_launch_candidate"] = out["action"].isin(
        ["launch_greenfield", "launch_consolidation"]
    )
    out["shortlist_rank"] = pd.NA
    shortlist_index = (
        out[out["is_launch_candidate"] & out["scope_confidence"].isin(["high", "medium"])]
        .sort_values(
            ["grade", "launch_confidence", "mkt_2025", "cagr"],
            ascending=[True, False, False, False],
        )
        .head(FINAL_SHORTLIST_SIZE)
        .index
    )
    out.loc[shortlist_index, "shortlist_rank"] = range(1, len(shortlist_index) + 1)
    out = out.sort_values(
        ["shortlist_rank", "market_qualified", "score", "mkt_2025"],
        ascending=[True, False, False, False],
        na_position="last",
    ).reset_index(drop=True)

    client = bqmod.client()
    openalex_works_meta = client.get_table(OPENALEX_WORKS)
    openalex_subfields_meta = client.get_table(OPENALEX_SUBFIELDS)
    manifest = {
        "source_scope_run": run_timestamp,
        "openalex_works_modified": str(openalex_works_meta.modified),
        "openalex_subfields_modified": str(openalex_subfields_meta.modified),
        "market_base_year": MARKET_BASE_YEAR,
        "market_late_year": MARKET_LATE_YEAR,
        "market_min_annual": MARKET_MIN_ANNUAL,
        "market_min_cagr": MARKET_MIN_CAGR,
        "scope_coverage_target": C.PRIMARY_COVERAGE,
        "ownership_threshold": C.OWNED_MIN_FI_SHARE,
        "greenfield_max_fi_3y": C.WORLD_GREENFIELD_MAX_FI_3Y,
        "n_subfields": int(len(out)),
        "n_market_qualified": int(out["market_qualified"].sum()),
        "n_launch_candidates": int(out["is_launch_candidate"].sum()),
        "n_shortlisted": int(out["shortlist_rank"].notna().sum()),
        "action_counts": out["action"].value_counts().to_dict(),
        "coverage_counts": out["coverage_status"].value_counts().to_dict(),
        "notes": (
            "Market qualification uses all-publisher OpenAlex only. "
            "Frontiers placement selects the action after qualification. "
            "Leiden validates scope by DOI-linked paper overlap and never sizes the market."
        ),
    }
    if write:
        bqmod.write_table(out, FINAL_PREFIX, run_timestamp)
        bqmod.write_json_row(manifest, FINAL_MANIFEST_PREFIX, run_timestamp)
    return out, manifest


def main() -> None:
    from .paths import configure_logging

    configure_logging("opportunities_final")
    ap = argparse.ArgumentParser(description="Final hybrid journal-opportunity run")
    ap.add_argument("--run", default=None, help="Scope-drift run; default latest complete")
    ap.add_argument("--no-write", action="store_true")
    ap.add_argument("--json", default=None, help="Optional local JSON export")
    ap.add_argument(
        "--excel",
        nargs="?",
        const="AUTO",
        default=None,
        help=(
            "Write the readable presentation workbook. Pass a path, or omit "
            "the path to use scope_drift_outputs/opportunities/output/"
        ),
    )
    ap.add_argument(
        "--skip-llm",
        action="store_true",
        help="With --excel, skip GPT journal-scope blurbs",
    )
    args = ap.parse_args()
    out, manifest = build_final_opportunities(args.run, write=not args.no_write)
    shortlist = out[out["shortlist_rank"].notna()]
    log.info("manifest: %s", json.dumps(manifest, default=str))
    print(
        shortlist[
            [
                "shortlist_rank", "grade", "proposed_journal", "mkt_2025",
                "cagr", "coverage_status", "action", "scope_confidence",
                "lead_journal", "lead_share",
            ]
        ].to_string(index=False)
    )
    if args.json:
        from .paths import OUTPUT_DIR, ensure_directories, resolve_under

        ensure_directories()
        json_path = resolve_under(OUTPUT_DIR, args.json)
        json_path.parent.mkdir(parents=True, exist_ok=True)
        json_path.write_text(
            out.to_json(orient="records", indent=2), encoding="utf-8"
        )
        json_path.with_suffix(".manifest.json").write_text(
            json.dumps(manifest, indent=2, default=str), encoding="utf-8"
        )
    if args.excel:
        from .export_workbook import default_out_path, export_workbook
        from .paths import OUTPUT_DIR, resolve_under

        excel_path = (
            default_out_path()
            if args.excel == "AUTO"
            else resolve_under(OUTPUT_DIR, args.excel)
        )
        export_workbook(out, excel_path, use_llm=not args.skip_llm)


if __name__ == "__main__":
    main()
