"""Frontiers-independent market universe and hybrid Leiden scope mapping.

AIRAK level-1 fields decide whether a market opportunity exists.  Frontiers
volume is attached only after qualification to choose an action.  Leiden still
defines the scope: world field volume is apportioned across the Leiden
communities that touch that field, using a stable all-years corpus weight.

Fields with no Leiden or Frontiers papers remain in ``world_opportunities`` as
greenfield opportunities; they are never lost merely because the ego network
cannot see them.
"""

from __future__ import annotations

import logging

import pandas as pd

from . import config as C

log = logging.getLogger("opportunities.world_market")


def _world_table() -> str:
    return f"{C.BQ_PROJECT}.{C.BQ_OUT_DATASET}.{C.WORLD_MARKET_TABLE}"


def materialize_world_market(force: bool = False) -> str:
    """Create the reusable AIRAK monthly field market table when stale."""
    from . import bq as bqmod

    cli = bqmod.client()
    fq = _world_table()
    source_version = cli.query(
        f"SELECT MAX(airak_version) v FROM `{C.AIRAK_PUBLICATION}`"
    ).result().to_dataframe().iloc[0]["v"]

    if not force:
        try:
            current = cli.query(
                f"SELECT MAX(source_version) v FROM `{fq}`"
            ).result().to_dataframe().iloc[0]["v"]
            if pd.notna(current) and str(current) == str(source_version):
                log.info("world market is current (%s) ← %s", current, fq)
                return fq
        except Exception:
            pass

    bqmod.ensure_output_dataset()
    sql = f"""
    CREATE OR REPLACE TABLE `{fq}`
    CLUSTER BY field_id, year AS
    WITH l1 AS (
      SELECT FieldOfStudyId AS field_id, DisplayName AS field
      FROM `{C.AIRAK_FIELD_OF_STUDY}`
      WHERE Level = 1
    ),
    pub AS (
      SELECT
        p.PublicationId AS publication_id,
        p.PublishedYear AS year,
        EXTRACT(MONTH FROM p.PublishedDate) AS month,
        j.PublisherId AS publisher_id
      FROM `{C.AIRAK_PUBLICATION}` p
      JOIN `{C.AIRAK_JOURNAL}` j USING (JournalId)
      WHERE p.PublishedYear BETWEEN {C.WORLD_MARKET_YEAR_FROM}
        AND {C.WORLD_MARKET_YEAR_TO}
        AND p.PublishedDate IS NOT NULL
    ),
    primary_field AS (
      SELECT
        pf.PublicationId AS publication_id,
        pf.FieldOfStudyId AS field_id
      FROM `{C.AIRAK_PUBLICATION_FIELD}` pf
      JOIN l1 ON l1.field_id = pf.FieldOfStudyId
      JOIN pub ON pub.publication_id = pf.PublicationId
      QUALIFY ROW_NUMBER() OVER (
        PARTITION BY pf.PublicationId
        ORDER BY pf.Similarity DESC, pf.FieldOfStudyId
      ) = 1
    )
    SELECT
      primary_field.field_id,
      l1.field,
      pub.year,
      pub.month,
      COUNT(*) AS n_world,
      COUNTIF(pub.publisher_id = {C.FRONTIERS_PUBLISHER_ID}) AS n_fi,
      DATE('{source_version}') AS source_version
    FROM pub
    JOIN primary_field USING (publication_id)
    JOIN l1 USING (field_id)
    GROUP BY field_id, field, year, month
    """
    job = cli.query(sql)
    job.result()
    log.info(
        "materialized independent world market (%.1f GB scanned) → %s",
        job.total_bytes_processed / 1e9,
        fq,
    )
    return fq


def fetch_community_year_counts(run_timestamp: str, level: str) -> pd.DataFrame:
    """Allocate world field markets to Leiden scopes without using FI demand.

    The annual allocation weight is the share of *non-Frontiers* neighbourhood
    papers in a world field that fall in each Leiden community. It lets a scope
    such as Respiratory Medicine grow differently from its broad Internal
    medicine parent without letting Frontiers demand influence opportunity.
    """
    from . import bq as bqmod

    level = bqmod._assert_level(level)
    materialize_world_market()
    tbl_c = f"{C.BQ_PROJECT}.{C.BQ_DATASET}.classification_raw_{run_timestamp}"
    tbl_m = f"{C.BQ_PROJECT}.{C.BQ_DATASET}.pub_metadata_raw_{run_timestamp}"
    q = f"""
    WITH l1 AS (
      SELECT FieldOfStudyId AS field_id, DisplayName AS field
      FROM `{C.AIRAK_FIELD_OF_STUDY}`
      WHERE Level = 1
    ),
    run_pub AS (
      SELECT
        CAST(c.{level} AS INT64) AS community_id,
        SAFE_CAST(m.pub_id AS INT64) AS publication_id,
        EXTRACT(YEAR FROM SAFE_CAST(m.date AS DATE)) AS year,
        EXTRACT(MONTH FROM SAFE_CAST(m.date AS DATE)) AS month,
        CAST(m.is_frontiers AS STRING) IN ('1', 'true', 'True') AS is_fi
      FROM `{tbl_c}` c
      JOIN `{tbl_m}` m ON c.int_id = m.int_id
      WHERE c.{level} IS NOT NULL
        AND SAFE_CAST(m.pub_id AS INT64) IS NOT NULL
        AND SAFE_CAST(m.date AS DATE) IS NOT NULL
    ),
    primary_field AS (
      SELECT pf.PublicationId AS publication_id, pf.FieldOfStudyId AS field_id
      FROM `{C.AIRAK_PUBLICATION_FIELD}` pf
      JOIN l1 ON l1.field_id = pf.FieldOfStudyId
      JOIN (SELECT DISTINCT publication_id FROM run_pub) rp
        ON rp.publication_id = pf.PublicationId
      QUALIFY ROW_NUMBER() OVER (
        PARTITION BY pf.PublicationId
        ORDER BY pf.Similarity DESC, pf.FieldOfStudyId
      ) = 1
    ),
    community_field AS (
      SELECT r.community_id, p.field_id, r.year, COUNT(*) AS n
      FROM run_pub r
      JOIN primary_field p USING (publication_id)
      WHERE NOT r.is_fi
      GROUP BY community_id, field_id, year
    ),
    weights AS (
      SELECT
        community_id,
        field_id,
        year,
        SAFE_DIVIDE(n, SUM(n) OVER (PARTITION BY field_id, year)) AS allocation_weight
      FROM community_field
    ),
    allocated AS (
      SELECT
        w.community_id,
        wm.year,
        wm.month,
        SUM(wm.n_world * w.allocation_weight) AS n_global
      FROM weights w
      JOIN `{_world_table()}` wm USING (field_id, year)
      GROUP BY community_id, year, month
    ),
    fi AS (
      SELECT community_id, year, month, COUNTIF(is_fi) AS n_fi
      FROM run_pub
      GROUP BY community_id, year, month
    )
    SELECT
      a.community_id,
      a.year,
      a.month,
      a.n_global,
      COALESCE(fi.n_fi, 0) AS n_fi
    FROM allocated a
    LEFT JOIN fi USING (community_id, year, month)
    """
    df = bqmod.client().query(q).result().to_dataframe()
    if df.empty:
        raise RuntimeError(f"no AIRAK world markets could be mapped to {level} communities")
    for col in ("community_id", "year", "month", "n_fi"):
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0).astype(int)
    df["n_global"] = pd.to_numeric(df["n_global"], errors="coerce").fillna(0.0)
    log.info(
        "%s: allocated independent world markets to %s communities",
        level,
        f"{df['community_id'].nunique():,}",
    )
    return df


def fetch_community_fields(run_timestamp: str, level: str) -> pd.DataFrame:
    """Return each Leiden community's dominant AIRAK field and field mixture."""
    from . import bq as bqmod

    level = bqmod._assert_level(level)
    tbl_c = f"{C.BQ_PROJECT}.{C.BQ_DATASET}.classification_raw_{run_timestamp}"
    tbl_m = f"{C.BQ_PROJECT}.{C.BQ_DATASET}.pub_metadata_raw_{run_timestamp}"
    q = f"""
    WITH l1 AS (
      SELECT FieldOfStudyId AS field_id, DisplayName AS field
      FROM `{C.AIRAK_FIELD_OF_STUDY}`
      WHERE Level = 1
    ),
    run_pub AS (
      SELECT CAST(c.{level} AS INT64) community_id,
             SAFE_CAST(m.pub_id AS INT64) publication_id,
             CAST(m.is_frontiers AS STRING) IN ('1', 'true', 'True') AS is_fi
      FROM `{tbl_c}` c JOIN `{tbl_m}` m ON c.int_id = m.int_id
      WHERE c.{level} IS NOT NULL AND SAFE_CAST(m.pub_id AS INT64) IS NOT NULL
    ),
    primary_field AS (
      SELECT pf.PublicationId publication_id, pf.FieldOfStudyId field_id
      FROM `{C.AIRAK_PUBLICATION_FIELD}` pf
      JOIN l1 ON l1.field_id = pf.FieldOfStudyId
      JOIN (SELECT DISTINCT publication_id FROM run_pub) r
        ON r.publication_id = pf.PublicationId
      QUALIFY ROW_NUMBER() OVER (
        PARTITION BY pf.PublicationId
        ORDER BY pf.Similarity DESC, pf.FieldOfStudyId
      ) = 1
    ),
    counted AS (
      SELECT r.community_id, l1.field, COUNT(*) n
      FROM run_pub r JOIN primary_field p USING (publication_id)
      JOIN l1 USING (field_id)
      WHERE NOT r.is_fi
      GROUP BY community_id, field
    ),
    ranked AS (
      SELECT *,
        SAFE_DIVIDE(n, SUM(n) OVER (PARTITION BY community_id)) field_share,
        ROW_NUMBER() OVER (PARTITION BY community_id ORDER BY n DESC, field) rn
      FROM counted
    )
    SELECT
      community_id,
      MAX(IF(rn=1, field, NULL)) AS primary_world_field,
      MAX(IF(rn=1, field_share, NULL)) AS primary_world_field_share,
      STRING_AGG(
        IF(rn <= 5, CONCAT(field, ' (', CAST(ROUND(100*field_share) AS STRING), '%)'), NULL),
        '; ' ORDER BY rn
      ) AS world_field_mix
    FROM ranked
    GROUP BY community_id
    """
    return bqmod.client().query(q).result().to_dataframe()


def qualify_and_route(
    out: pd.DataFrame,
    *,
    min_annual: int,
    large_annual: int,
    size_score_ref: int,
    corpus_cagr: float,
    portfolio_share: float,
) -> pd.DataFrame:
    """Decide opportunity on market facts, then let Frontiers pick the action.

    Qualification reads `n_global_base`, `n_global_late` and the growth they
    imply, and nothing else. No Frontiers column takes part, so a scope can
    qualify with zero Frontiers output. `n_fi_3y` and `lead_share` are consulted
    only after `is_opportunity` is fixed, and can only choose between the three
    actions — never withdraw the opportunity.

    Kept as one auditable rule so market qualification and portfolio routing
    cannot accidentally become entangled again.
    """
    k = C.WORLD_MARKET_LAST_FULL_YEAR - C.WORLD_MARKET_BASE_YEAR
    out = out.copy()
    out["cagr"] = (
        out["n_global_late"] / out["n_global_base"].replace(0, pd.NA)
    ) ** (1 / k) - 1
    out["excess_cagr"] = out["cagr"] - corpus_cagr
    out["is_large"] = out["n_global_late"] >= large_annual
    out["growth_reliable"] = out["n_global_base"] >= C.MARKET_GROWTH_MIN_BASE
    out["is_growing"] = (
        (out["n_global_late"] >= min_annual)
        & out["growth_reliable"]
        & (out["excess_cagr"] >= C.MARKET_EXCESS_CAGR)
    )
    # Size and growth are independent opportunity signals. A large declining
    # market stays visible so the action layer can mark it hold/validate.
    out["is_opportunity"] = out["is_large"] | out["is_growing"]

    # Ranking is deliberately market-only.
    size = (out["n_global_3y"] / size_score_ref).clip(upper=10)
    growth = 1 + out["excess_cagr"].fillna(0).clip(lower=0) * 5
    out["opportunity_score"] = (size * growth).round(3)

    out["fi_share"] = out["n_fi_late"] / out["n_global_late"].replace(0, pd.NA)
    out["fi_share_vs_portfolio"] = out["fi_share"] / portfolio_share
    out["lead_share"] = out.get("lead_share", pd.Series(0.0, index=out.index)).fillna(0.0)

    opportunity = out["is_opportunity"]
    thin = out["n_fi_3y"] < C.WORLD_GREENFIELD_MAX_FI_3Y
    owned = out["lead_share"] >= C.OWNED_MIN_FI_SHARE
    out["action"] = "watch"
    out.loc[opportunity & thin, "action"] = "launch_greenfield"
    out.loc[opportunity & ~thin & ~owned, "action"] = "launch_consolidate"
    out.loc[opportunity & ~thin & owned, "action"] = "grow_existing"

    out["corpus_cagr"] = corpus_cagr
    out["fi_portfolio_share"] = portfolio_share
    return out


def build_world_opportunities(run_timestamp: str, write: bool = True) -> pd.DataFrame:
    """Rank all world fields on market facts, then select the portfolio action."""
    from . import bq as bqmod

    materialize_world_market()
    fq = _world_table()
    q = f"""
    WITH annual AS (
      SELECT field_id, field, year, SUM(n_world) n_world, SUM(n_fi) n_fi
      FROM `{fq}`
      GROUP BY field_id, field, year
    ),
    market AS (
      SELECT
        field_id,
        field,
        SUM(IF(year BETWEEN {C.WORLD_MARKET_LAST_FULL_YEAR - 2}
          AND {C.WORLD_MARKET_LAST_FULL_YEAR}, n_world, 0)) AS n_global_3y,
        SUM(IF(year BETWEEN {C.WORLD_MARKET_LAST_FULL_YEAR - 2}
          AND {C.WORLD_MARKET_LAST_FULL_YEAR}, n_fi, 0)) AS n_fi_3y,
        MAX(IF(year={C.WORLD_MARKET_BASE_YEAR}, n_world, NULL)) AS n_global_base,
        MAX(IF(year={C.WORLD_MARKET_LAST_FULL_YEAR}, n_world, NULL)) AS n_global_late,
        MAX(IF(year={C.WORLD_MARKET_LAST_FULL_YEAR}, n_fi, NULL)) AS n_fi_late
      FROM annual
      GROUP BY field_id, field
    ),
    corpus AS (
      SELECT
        SUM(IF(year={C.WORLD_MARKET_BASE_YEAR}, n_world, 0)) corpus_base,
        SUM(IF(year={C.WORLD_MARKET_LAST_FULL_YEAR}, n_world, 0)) corpus_late,
        SUM(IF(year={C.WORLD_MARKET_LAST_FULL_YEAR}, n_fi, 0)) fi_late
      FROM annual
    )
    SELECT market.*, corpus.*
    FROM market CROSS JOIN corpus
    """
    out = bqmod.client().query(q).result().to_dataframe()
    k = C.WORLD_MARKET_LAST_FULL_YEAR - C.WORLD_MARKET_BASE_YEAR
    corpus_cagr = float(
        (out["corpus_late"].iloc[0] / out["corpus_base"].iloc[0]) ** (1 / k) - 1
    )
    portfolio_share = float(out["fi_late"].iloc[0] / out["corpus_late"].iloc[0])

    ownership = _fetch_field_ownership()
    out = out.merge(ownership, on=["field_id", "field"], how="left")
    out["n_titles_10plus"] = out["n_titles_10plus"].fillna(0).astype(int)
    out = qualify_and_route(
        out,
        min_annual=C.WORLD_FIELD_MIN_ANNUAL,
        large_annual=C.WORLD_FIELD_LARGE_ANNUAL,
        size_score_ref=C.WORLD_MARKET_SIZE_SCORE_REF,
        corpus_cagr=corpus_cagr,
        portfolio_share=portfolio_share,
    )

    scopes = build_world_field_scopes(run_timestamp)
    scope_rollup = scopes.groupby("field").agg(
        leiden_scope_count=("community_id", "nunique"),
        leiden_scopes=("scope_name", lambda s: "; ".join(s.head(12))),
    )
    out = out.merge(scope_rollup, left_on="field", right_index=True, how="left")
    out["leiden_scope_count"] = out["leiden_scope_count"].fillna(0).astype(int)
    out["leiden_scopes"] = out["leiden_scopes"].fillna("")

    keep = [
        "field_id", "field", "n_global_3y", "n_global_base", "n_global_late",
        "cagr", "excess_cagr", "is_large", "is_growing", "is_opportunity",
        "opportunity_score", "n_fi_3y", "n_fi_late", "fi_share",
        "fi_share_vs_portfolio", "lead_journal", "lead_n_3y", "lead_share",
        "n_titles_10plus", "leiden_scope_count", "leiden_scopes", "action",
        "corpus_cagr", "fi_portfolio_share",
    ]
    out = out[keep].sort_values(
        ["is_opportunity", "opportunity_score"], ascending=[False, False]
    ).reset_index(drop=True)
    if write:
        bqmod.write_table(out, C.WORLD_OPPORTUNITIES_PREFIX, run_timestamp)
        bqmod.write_table(scopes, "world_field_scopes", run_timestamp)
    return out


def build_world_field_scopes(run_timestamp: str) -> pd.DataFrame:
    """Name the Leiden journal-shaped scopes nested in each world field."""
    from . import bq as bqmod

    level = C.UNIT_JOURNAL_LEVEL
    fields = fetch_community_fields(run_timestamp, level)
    labels = bqmod.fetch_cluster_labels(run_timestamp, level)
    topics = bqmod.fetch_l2_topics(run_timestamp, level)
    out = fields.merge(labels, on="community_id", how="left")
    if not topics.empty:
        topic_cols = [
            c for c in ("cluster_id", "unit_name", "topic_compound")
            if c in topics.columns
        ]
        out = out.merge(
            topics[topic_cols].rename(columns={"cluster_id": "community_id"}),
            on="community_id",
            how="left",
        )
    for col in ("unit_name", "topic_compound", "community_label"):
        if col not in out:
            out[col] = ""
        out[col] = out[col].fillna("").astype(str)
    out["scope_name"] = out["unit_name"].where(
        out["unit_name"].str.strip() != "", out["topic_compound"]
    )
    out["scope_name"] = out["scope_name"].where(
        out["scope_name"].str.strip() != "", out["community_label"]
    )
    out["scope_name"] = out["scope_name"].where(
        out["scope_name"].str.strip() != "",
        "Cluster " + out["community_id"].astype(str),
    )
    out = out.rename(columns={"primary_world_field": "field"})
    return out[
        [
            "field", "community_id", "scope_name",
            "primary_world_field_share", "world_field_mix",
        ]
    ].sort_values(["field", "primary_world_field_share"], ascending=[True, False])


def _fetch_field_ownership() -> pd.DataFrame:
    """Observed Frontiers journal distribution per independent world field."""
    from . import bq as bqmod

    q = f"""
    WITH l1 AS (
      SELECT FieldOfStudyId field_id, DisplayName field
      FROM `{C.AIRAK_FIELD_OF_STUDY}` WHERE Level=1
    ),
    pub AS (
      SELECT p.PublicationId publication_id, j.DisplayName journal
      FROM `{C.AIRAK_PUBLICATION}` p JOIN `{C.AIRAK_JOURNAL}` j USING (JournalId)
      WHERE p.PublishedYear BETWEEN {C.WORLD_MARKET_LAST_FULL_YEAR - 2}
        AND {C.WORLD_MARKET_LAST_FULL_YEAR}
        AND j.PublisherId = {C.FRONTIERS_PUBLISHER_ID}
    ),
    primary_field AS (
      SELECT pf.PublicationId publication_id, pf.FieldOfStudyId field_id
      FROM `{C.AIRAK_PUBLICATION_FIELD}` pf
      JOIN l1 ON l1.field_id=pf.FieldOfStudyId
      JOIN pub ON pub.publication_id=pf.PublicationId
      QUALIFY ROW_NUMBER() OVER (
        PARTITION BY pf.PublicationId
        ORDER BY pf.Similarity DESC, pf.FieldOfStudyId
      )=1
    ),
    counts AS (
      SELECT l1.field_id, l1.field, pub.journal, COUNT(*) n
      FROM pub JOIN primary_field USING (publication_id) JOIN l1 USING (field_id)
      GROUP BY field_id, field, journal
    ),
    ranked AS (
      SELECT *,
        SAFE_DIVIDE(n, SUM(n) OVER (PARTITION BY field_id)) lead_share,
        ROW_NUMBER() OVER (PARTITION BY field_id ORDER BY n DESC, journal) rn,
        COUNTIF(n >= 10) OVER (PARTITION BY field_id) n_titles_10plus
      FROM counts
    )
    SELECT field_id, field, journal lead_journal, n lead_n_3y,
           lead_share, n_titles_10plus
    FROM ranked WHERE rn=1
    """
    return bqmod.client().query(q).result().to_dataframe()
