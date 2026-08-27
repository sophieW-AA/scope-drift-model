"""
Re-probe Neurorobotics sections/RTs using the taxonomy join path:

  article → taxonomy (journal, section, type)
  article → research_topic (via article_research_topic_id)

Also joins run scatter papers for OOS vs section/RT.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pandas as pd
from google.cloud import bigquery

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from neuro_analysis import JOURNAL, get_journal, load_dashboards  # noqa: E402

RUN = "20260721_122750"
BQ_PROJECT = "ocean-tech-adv-analytics-c-tfs"
TBL_META = f"{BQ_PROJECT}.raw_citation_network_data.pub_metadata_raw_{RUN}"


def main() -> None:
    client = bigquery.Client(project=BQ_PROJECT, location="EU")

    # 1) Inventory via taxonomy (user-provided pattern)
    inv = client.query(
        """
        SELECT
          t.type AS taxonomy_type,
          t.section,
          t.section_id,
          DATE(t.publish_date) AS section_publish_date,
          DATE(t.journal_launch_date) AS journal_launch_date,
          DATE(t.create_date) AS taxonomy_create_date,
          COUNT(*) AS n_articles
        FROM `ocean-breeze-tier-1.reporting_data_mart.article` a
        LEFT JOIN `ocean-breeze-tier-1.reporting_data_mart.taxonomy` t
          ON a.taxonomy_id = t.taxonomy_id
        WHERE a.space_id = 1
          AND a.is_deleted = FALSE
          AND a.is_published = TRUE
          AND LOWER(t.journal) = LOWER(@journal)
          AND EXTRACT(YEAR FROM COALESCE(a.first_publish_date, a.stage_date_published, a.create_date))
              BETWEEN 2020 AND 2026
        GROUP BY 1, 2, 3, 4, 5, 6
        ORDER BY n_articles DESC
        """,
        job_config=bigquery.QueryJobConfig(
            query_parameters=[bigquery.ScalarQueryParameter("journal", "STRING", JOURNAL)]
        ),
    ).to_dataframe()
    print("=== Taxonomy inventory (Neurorobotics 2020-2026 published) ===")
    print(inv.to_string(index=False))
    print("total articles", int(inv["n_articles"].sum()) if len(inv) else 0)

    # 2) Join run papers → taxonomy + RT via title match to article, then taxonomy path
    _, _, maps = load_dashboards()
    mj = get_journal(maps)
    scatter = mj.get("scatter") or []
    scope_by_id = {int(p["i"]): int(p.get("s", 1)) for p in scatter if p.get("i") is not None}
    ids_sql = ",".join(str(i) for i in scope_by_id)

    q = f"""
    WITH run AS (
      SELECT
        m.int_id,
        m.pub_id,
        m.title,
        EXTRACT(YEAR FROM SAFE.PARSE_DATE('%Y-%m-%d', SUBSTR(CAST(m.date AS STRING), 1, 10))) AS airak_year,
        LOWER(TRIM(REGEXP_REPLACE(m.title, r'\\s+', ' '))) AS title_norm
      FROM `{TBL_META}` m
      WHERE m.int_id IN ({ids_sql})
        AND LOWER(m.journal) = LOWER(@journal)
    ),
    art AS (
      SELECT
        a.article_id,
        COALESCE(a.article_title, a.title) AS article_title,
        a.taxonomy_id,
        a.article_research_topic_id,
        a.research_topic_id,
        DATE(COALESCE(a.first_publish_date, a.stage_date_published)) AS article_pub_date,
        LOWER(TRIM(REGEXP_REPLACE(COALESCE(a.article_title, a.title), r'\\s+', ' '))) AS title_norm
      FROM `ocean-breeze-tier-1.reporting_data_mart.article` a
      WHERE a.space_id = 1
        AND a.is_deleted = FALSE
        AND a.is_published = TRUE
    )
    SELECT
      r.int_id,
      r.pub_id,
      r.title,
      r.airak_year,
      art.article_id,
      t.journal,
      t.section,
      t.section_id,
      t.type AS taxonomy_type,
      DATE(t.publish_date) AS section_publish_date,
      DATE(t.create_date) AS taxonomy_create_date,
      DATE(t.journal_launch_date) AS journal_launch_date,
      COALESCE(rt.research_topic_id, rt2.research_topic_id) AS research_topic_id,
      COALESCE(rt.title, rt2.title) AS research_topic_title,
      DATE(COALESCE(rt.create_date, rt2.create_date)) AS rt_create_date,
      DATE(COALESCE(rt.posted_date, rt2.posted_date)) AS rt_posted_date,
      art.article_pub_date
    FROM run r
    LEFT JOIN art ON r.title_norm = art.title_norm
    LEFT JOIN `ocean-breeze-tier-1.reporting_data_mart.taxonomy` t
      ON art.taxonomy_id = t.taxonomy_id
    LEFT JOIN `ocean-breeze-tier-1.reporting_data_mart.research_topic` rt
      ON art.article_research_topic_id = rt.research_topic_id
    LEFT JOIN `ocean-breeze-tier-1.reporting_data_mart.research_topic` rt2
      ON art.research_topic_id = rt2.research_topic_id
    """
    # Probe article title column name first if needed
    try:
        df = client.query(
            q,
            job_config=bigquery.QueryJobConfig(
                query_parameters=[bigquery.ScalarQueryParameter("journal", "STRING", JOURNAL)]
            ),
        ).to_dataframe()
    except Exception as e:
        print("Query failed, retrying with article_title only:", e)
        q2 = q.replace("COALESCE(a.article_title, a.title)", "a.article_title").replace(
            "COALESCE(rt.posted_date, rt2.posted_date)", "COALESCE(rt.create_date, rt2.create_date)"
        )
        # also fix posted_date if missing
        df = client.query(
            q2,
            job_config=bigquery.QueryJobConfig(
                query_parameters=[bigquery.ScalarQueryParameter("journal", "STRING", JOURNAL)]
            ),
        ).to_dataframe()

    print(f"\nJoin rows before dedupe: {len(df)}")
    df["matched"] = df["article_id"].notna()
    df = df.sort_values(["int_id", "matched"], ascending=[True, False]).drop_duplicates("int_id")
    df["is_oos"] = df["int_id"].map(scope_by_id) == 0
    df["in_rt"] = df["research_topic_id"].notna()
    df["has_section"] = df["section"].notna() & (df["section"].astype(str).str.strip() != "")

    print(f"matched={int(df['matched'].sum())}/{len(df)}")
    print("\n=== taxonomy_type ===")
    print(df["taxonomy_type"].fillna("(none)").value_counts().to_string())
    print("\n=== section ===")
    print(df["section"].fillna("(none)").value_counts().head(20).to_string())
    print("with section:", int(df["has_section"].sum()))

    if df["has_section"].any():
        by_sec = (
            df.groupby(["section", "taxonomy_type", "section_publish_date", "taxonomy_create_date"], dropna=False)
            .agg(n=("int_id", "count"), oos_n=("is_oos", "sum"))
            .reset_index()
        )
        by_sec["oos_pct"] = (100 * by_sec["oos_n"] / by_sec["n"]).round(1)
        by_sec = by_sec.sort_values("n", ascending=False)
        print("\n=== OOS by section ===")
        print(by_sec.to_string(index=False))
        by_sec.to_csv(HERE / "neurorobotics_oos_by_section_taxonomy.csv", index=False)

    print("\n=== RT fill ===")
    print("with RT:", int(df["in_rt"].sum()))
    cmp = df.groupby("in_rt").agg(n=("int_id", "count"), oos_n=("is_oos", "sum"))
    cmp["oos_pct"] = (100 * cmp["oos_n"] / cmp["n"]).round(1)
    print(cmp.to_string())

    out = HERE / "neurorobotics_taxonomy_join.parquet"
    df.to_parquet(out, index=False)
    print(f"\nWrote {out}")

    summary = {
        "join_path": "article.taxonomy_id → taxonomy; article_research_topic_id → research_topic",
        "n_scatter": len(scope_by_id),
        "n_matched": int(df["matched"].sum()),
        "n_with_section": int(df["has_section"].sum()),
        "n_with_rt": int(df["in_rt"].sum()),
        "taxonomy_types": df["taxonomy_type"].fillna("(none)").value_counts().to_dict(),
        "sections": df["section"].fillna("(none)").value_counts().head(20).to_dict(),
        "oos_pct_overall": round(100 * float(df["is_oos"].mean()), 1),
    }
    (HERE / "neurorobotics_taxonomy_summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(json.dumps(summary, indent=2, default=str))


if __name__ == "__main__":
    main()
