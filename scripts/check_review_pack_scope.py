"""
Check review-pack / Tableau articles against scope-drift primary clusters.

Uses local cwts_output if present, else BigQuery classification/pub_metadata.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

import pandas as pd

REPO = Path(__file__).resolve().parents[1]
CWTS_DIR = REPO / "cwts_output"
OUT_PATH = Path(r"C:\Users\sophie.wilson\Downloads\review_packs_scope_checked.xlsx")
RUN_TIMESTAMP = "20260721_122750"  # notebook latest test journals run
PRIMARY_COVERAGE = 0.8
CLUSTER_LEVEL = "macro"

BQ_PROJECT = "ocean-tech-adv-analytics-c-tfs"
BQ_DATASET = "raw_citation_network_data"

REVIEW_FILES = [
    (
        "fnbot",
        r"c:\Users\sophie.wilson\Downloads\fnbot_review_pack-MScheck03312026.xlsx",
        "shortlist",
    ),
    (
        "fenvs",
        r"c:\Users\sophie.wilson\Downloads\fenvs_review_pack-MScheck03312026.xlsx",
        "shortlist",
    ),
    (
        "feart",
        r"c:\Users\sophie.wilson\Downloads\feart_review_pack_OP31032026.xlsx",
        "shortlist",
    ),
    (
        "tableau",
        r"c:\Users\sophie.wilson\Downloads\From Tableau report scope_drift_oos_articles_20260319 1.xlsx",
        0,
    ),
    (
        "surgery",
        r"c:\Users\sophie.wilson\Downloads\Surgery_scope check_RS31032026.xlsx",
        0,
    ),
    (
        "aging_neuro",
        r"c:\Users\sophie.wilson\Downloads\Aging Neuro_scope check_RS31032026.xlsx",
        0,
    ),
]


def norm_title(s: object) -> str:
    if pd.isna(s):
        return ""
    t = str(s).lower()
    t = re.sub(r"[^a-z0-9\s]", " ", t)
    t = re.sub(r"\s+", " ", t).strip()
    return t


def load_inputs() -> pd.DataFrame:
    rows = []
    for source, path, sheet in REVIEW_FILES:
        df = pd.read_excel(path, sheet_name=sheet)
        if "Code" in df.columns:
            for _, r in df.iterrows():
                rows.append(
                    {
                        "source_file": source,
                        "article_code": r.get("Code"),
                        "article_id_original": pd.NA,
                        "journal": str(r.get("Field", "")).strip(),
                        "title": r.get("Title"),
                        "manual_scope_class": r.get("Scope class"),
                        "manual_scope_score": r.get("Scope score (1/10)"),
                        "section": r.get("Section"),
                    }
                )
        elif "article_id_original" in df.columns:
            for _, r in df.iterrows():
                rows.append(
                    {
                        "source_file": source,
                        "article_code": pd.NA,
                        "article_id_original": r.get("article_id_original"),
                        "journal": str(r.get("journal_name", "")).strip(),
                        "title": r.get("title"),
                        "manual_scope_class": r.get("scope_check"),
                        "manual_scope_score": r.get("Scope Score"),
                        "section": pd.NA,
                    }
                )
        else:
            raise ValueError(f"Unrecognized columns in {path}: {list(df.columns)}")
    out = pd.DataFrame(rows)
    out["title_norm"] = out["title"].map(norm_title)
    out["journal_norm"] = out["journal"].str.lower().str.strip()
    return out


def get_primary_clusters(df: pd.DataFrame, journal: str, coverage: float = 0.8) -> set:
    jdf = df[df["journal"].str.lower() == journal.lower()]
    if jdf.empty:
        return set()
    cluster_counts = jdf[CLUSTER_LEVEL].value_counts()
    total = cluster_counts.sum()
    cumsum = 0
    primary = set()
    for cluster, count in cluster_counts.items():
        primary.add(int(cluster))
        cumsum += count
        if cumsum / total >= coverage:
            break
    return primary


def load_from_local() -> tuple[pd.DataFrame, pd.DataFrame] | None:
    class_path = CWTS_DIR / "classification.txt"
    meta_path = CWTS_DIR / "pub_metadata.txt"
    if not class_path.exists() or not meta_path.exists():
        return None
    print(f"Loading local CWTS data from {CWTS_DIR}")
    # classification: int_id micro meso macro (space-separated typical CWTS)
    class_df = pd.read_csv(class_path, sep=r"\s+", header=None, engine="python")
    if class_df.shape[1] >= 4:
        class_df = class_df.iloc[:, :4]
        class_df.columns = ["int_id", "micro", "meso", "macro"]
    else:
        raise ValueError(f"Unexpected classification columns: {class_df.shape}")

    # pub_metadata written by cwts_export as CSV
    try:
        meta_df = pd.read_csv(meta_path)
    except Exception:
        meta_df = pd.read_csv(meta_path, sep=r"\s+", header=None, engine="python")
        # fallback guess
        meta_df.columns = [
            "int_id",
            "pub_id",
            "is_frontiers",
            "journal",
            "date",
            "title",
        ][: meta_df.shape[1]]

    print(f"  classification rows: {len(class_df):,}")
    print(f"  pub_metadata rows: {len(meta_df):,}")
    print(f"  pub_metadata cols: {list(meta_df.columns)}")
    return class_df, meta_df


def load_frontiers_from_bq() -> pd.DataFrame:
    """Load Frontiers papers with cluster assignment (same join as the notebook)."""
    from google.cloud import bigquery

    client = bigquery.Client(project=BQ_PROJECT, location="EU")
    tbl_classif = f"{BQ_PROJECT}.{BQ_DATASET}.classification_raw_{RUN_TIMESTAMP}"
    tbl_pub_meta = f"{BQ_PROJECT}.{BQ_DATASET}.pub_metadata_raw_{RUN_TIMESTAMP}"
    print(f"Loading Frontiers papers from BigQuery run {RUN_TIMESTAMP}")
    query = f"""
    SELECT
      c.int_id,
      c.macro,
      m.journal,
      m.title,
      m.pub_id
    FROM `{tbl_classif}` c
    JOIN `{tbl_pub_meta}` m ON c.int_id = m.int_id
    WHERE m.is_frontiers = 1
    """
    df = client.query(query).to_dataframe()
    print(f"  Loaded {len(df):,} Frontiers papers")
    return df


def match_articles(papers: pd.DataFrame, frontiers: pd.DataFrame) -> pd.DataFrame:
    frontiers = frontiers.copy()
    frontiers["title_norm"] = frontiers["title"].map(norm_title)
    frontiers["journal_norm"] = frontiers["journal"].astype(str).str.lower().str.strip()

    journals = sorted(papers["journal_norm"].dropna().unique())
    primary: dict[str, set] = {}
    for j in journals:
        full_names = frontiers.loc[frontiers["journal_norm"] == j, "journal"].unique()
        if len(full_names) == 0:
            needle = j.replace("frontiers in ", "")
            hits = frontiers[
                frontiers["journal_norm"].str.contains(needle, na=False, regex=False)
            ]
            full_names = hits["journal"].unique() if not hits.empty else []
        if len(full_names) == 0:
            print(f"WARNING: no Frontiers papers for journal '{j}'")
            primary[j] = set()
            continue
        full_name = str(full_names[0])
        primary[j] = get_primary_clusters(frontiers, full_name, PRIMARY_COVERAGE)
        print(f"{full_name}: {len(primary[j])} primary clusters: {sorted(primary[j])}")

    title_map = (
        frontiers.groupby("title_norm")
        .agg(
            int_id=("int_id", "first"),
            macro=("macro", "first"),
            matched_journal=("journal", "first"),
            matched_title=("title", "first"),
            n_matches=("int_id", "count"),
        )
        .reset_index()
    )

    out = papers.merge(title_map, on="title_norm", how="left")

    def scope_status(row):
        if pd.isna(row.get("macro")):
            return "Not in network"
        j = row["journal_norm"]
        p = primary.get(j, set())
        if not p:
            return "Unknown journal"
        return "In Scope" if int(row["macro"]) in p else "Out of Scope"

    out["model_scope_status"] = out.apply(scope_status, axis=1)
    out["primary_clusters"] = out["journal_norm"].map(
        lambda j: ",".join(str(x) for x in sorted(primary.get(j, [])))
    )
    return out


def main() -> int:
    papers = load_inputs()
    print(f"Loaded {len(papers)} article rows from review packs")
    print(papers["source_file"].value_counts().to_string())

    try:
        frontiers = load_frontiers_from_bq()
    except Exception as e:
        raise SystemExit(
            f"BigQuery load failed: {e}\n"
            "Need ADC / GOOGLE_APPLICATION_CREDENTIALS for the 20260721_122750 run "
            "(local cwts_output is a different journal set)."
        ) from e

    result = match_articles(papers, frontiers)

    matched = result["model_scope_status"].ne("Not in network").sum()
    print(f"\nMatched to network: {matched}/{len(result)}")
    print("\nBy source + model status:")
    print(
        result.groupby(["source_file", "model_scope_status"])
        .size()
        .unstack(fill_value=0)
        .to_string()
    )

    # Deduped unique articles (prefer article_id then title)
    dedupe_key = result["article_id_original"].astype(str)
    missing = dedupe_key.isin(["<NA>", "nan", "None", ""])
    dedupe_key = dedupe_key.where(~missing, result["title_norm"])
    unique = result.copy()
    unique["_k"] = dedupe_key
    unique = unique.drop_duplicates("_k").drop(columns=["_k"])

    print(f"\nUnique articles: {len(unique)}")
    print(unique["model_scope_status"].value_counts().to_string())

    cols = [
        "source_file",
        "article_code",
        "article_id_original",
        "journal",
        "title",
        "section",
        "manual_scope_class",
        "manual_scope_score",
        "int_id",
        "macro",
        "matched_journal",
        "model_scope_status",
        "primary_clusters",
        "n_matches",
    ]
    cols = [c for c in cols if c in result.columns]

    with pd.ExcelWriter(OUT_PATH, engine="openpyxl") as writer:
        result[cols].to_excel(writer, sheet_name="all_rows", index=False)
        unique[cols].to_excel(writer, sheet_name="unique_articles", index=False)
        summary = (
            unique.groupby(["journal", "model_scope_status"])
            .size()
            .unstack(fill_value=0)
            .reset_index()
        )
        summary.to_excel(writer, sheet_name="summary", index=False)

        oos = unique[unique["model_scope_status"] == "Out of Scope"][cols]
        oos.to_excel(writer, sheet_name="model_oos", index=False)

    print(f"\nSaved: {OUT_PATH}")

    # Print a compact human summary
    print("\n" + "=" * 80)
    print("SCOPE CHECK RESULTS (unique articles)")
    print("=" * 80)
    for j, jdf in unique.groupby("journal", sort=True):
        in_s = (jdf["model_scope_status"] == "In Scope").sum()
        out_s = (jdf["model_scope_status"] == "Out of Scope").sum()
        miss = (jdf["model_scope_status"] == "Not in network").sum()
        print(f"\n{str(j).upper()}")
        print(f"  In scope: {in_s}, Out of scope: {out_s}, Not in network: {miss}")
        show = jdf.sort_values(["model_scope_status", "title"])
        for _, row in show.iterrows():
            marker = {
                "In Scope": "[OK]",
                "Out of Scope": "[OOS]",
                "Not in network": "[?]",
            }.get(row["model_scope_status"], "[?]")
            macro = row["macro"] if pd.notna(row.get("macro")) else "-"
            title = str(row["title"])[:70]
            line = f"  {marker} [{row['model_scope_status']:14}] C{macro:>3} | {title}"
            try:
                print(line)
            except UnicodeEncodeError:
                print(line.encode("ascii", "replace").decode("ascii"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
