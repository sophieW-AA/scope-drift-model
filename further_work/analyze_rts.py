"""
Research Topic deep-dive for Frontiers in Neurorobotics.

Answers:
  1. Which RTs contribute to OOS?
  2. Which RTs contribute to drift (CV takeover / away from 2020 mix)?
  3. RT vs spontaneous submissions — how do they differ?
  4. Should any RTs be added / removed (or closed / gated)?

Usage:
  python further_work/analyze_rts.py
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import pandas as pd
from google.cloud import bigquery

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from neuro_analysis import (  # noqa: E402
    JOURNAL,
    PRIMARY_IDS,
    PRIMARY_LABELS,
    get_journal,
    load_dashboards,
)

RUN = "20260721_122750"
BQ_PROJECT = "ocean-tech-adv-analytics-c-tfs"
TBL_META = f"{BQ_PROJECT}.raw_citation_network_data.pub_metadata_raw_{RUN}"

# Themes that pull Neurorobotics off its neural–robot–rehab core
OFFBRAND_RE = re.compile(
    r"privacy|cyber.?physical|image fusion|traffic|cancer|geolog|thermal|"
    r"organic chem|immunotherap|management science|remote.?sens|"
    r"heterogeneous view perception",
    re.I,
)
# Themes aligned with recommended expand (embodied/vision/rehab/neural–robot)
ONBRAND_RE = re.compile(
    r"neurorobotic|exoskeleton|prosthes|rehabilit|bci|brain.?computer|"
    r"human.?robot|embodied|enactive|motor|neural.?interface|"
    r"humanoid|assistive|neuroergonom|biomimetic|semg|gait",
    re.I,
)
CVISH_RE = re.compile(
    r"vision|visual|image|perception|cnn|deep learning|machine learning|"
    r"neural network|intelligent algorithm",
    re.I,
)


def fetch_joined(client: bigquery.Client, int_ids: list[int]) -> pd.DataFrame:
    ids_sql = ",".join(str(i) for i in int_ids)
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
    linked AS (
      SELECT
        a.article_id,
        a.article_title,
        rt.research_topic_id,
        rt.title AS research_topic_title,
        CAST(COALESCE(rt.create_date, rt.research_topic_create_date) AS STRING) AS rt_create_date,
        CAST(rt.online_date AS STRING) AS rt_online_date,
        CAST(COALESCE(a.first_publish_date, a.stage_date_published) AS STRING) AS article_pub_date,
        LOWER(TRIM(REGEXP_REPLACE(a.article_title, r'\\s+', ' '))) AS title_norm
      FROM `ocean-breeze-tier-1.reporting_data_mart.article` a
      LEFT JOIN `ocean-breeze-tier-1.reporting_data_mart.taxonomy` t
        ON a.taxonomy_id = t.taxonomy_id
      LEFT JOIN `ocean-breeze-tier-1.reporting_data_mart.research_topic` rt
        ON a.article_research_topic_id = rt.research_topic_id
      WHERE a.space_id = 1
        AND a.is_deleted = FALSE
        AND a.is_published = TRUE
        AND LOWER(t.journal) = LOWER(@journal)
    )
    SELECT
      r.int_id,
      r.title,
      r.airak_year,
      l.article_id,
      l.research_topic_id,
      l.research_topic_title,
      l.rt_create_date,
      l.rt_online_date,
      l.article_pub_date
    FROM run r
    LEFT JOIN linked l ON r.title_norm = l.title_norm
    """
    return client.query(
        q,
        job_config=bigquery.QueryJobConfig(
            query_parameters=[bigquery.ScalarQueryParameter("journal", "STRING", JOURNAL)]
        ),
    ).to_dataframe()


def primary_label(cid) -> str:
    if cid is None or (isinstance(cid, float) and pd.isna(cid)):
        return "other"
    cid = int(cid)
    return PRIMARY_LABELS.get(cid, "other")


def mix_shares(sub: pd.DataFrame) -> dict[str, float]:
    if sub.empty:
        return {lab: 0.0 for lab in list(PRIMARY_LABELS.values()) + ["other"]}
    labs = sub["community_label"]
    n = len(labs)
    out = {lab: round(100 * (labs == lab).sum() / n, 1) for lab in PRIMARY_LABELS.values()}
    out["other"] = round(100 * (labs == "other").sum() / n, 1)
    return out


def main() -> None:
    _, _, maps = load_dashboards()
    mj = get_journal(maps)
    scatter = mj.get("scatter") or []
    sc = pd.DataFrame(scatter)
    sc["int_id"] = sc["i"].astype(int)
    sc["is_oos"] = sc["s"] == 0
    sc["community_id"] = sc["c"]
    sc["community_label"] = sc["community_id"].map(primary_label)
    sc["year"] = sc["yr"]

    client = bigquery.Client(project=BQ_PROJECT, location="EU")
    linked = fetch_joined(client, sc["int_id"].tolist())
    linked = linked.sort_values(["int_id", "article_id"]).drop_duplicates("int_id")

    df = sc.merge(linked, on="int_id", how="left")
    df["in_rt"] = df["research_topic_id"].notna()
    df["channel"] = df["in_rt"].map({True: "Research Topic", False: "Spontaneous"})
    df["rt_launch_year"] = pd.to_datetime(df["rt_create_date"], errors="coerce").dt.year
    df["is_cv"] = df["community_id"] == 8
    df["is_neuro"] = df["community_id"] == 4
    df["is_primary"] = df["community_id"].isin(PRIMARY_IDS)

    # Persist paper-level CSV (no parquet date issues)
    paper_cols = [
        "int_id",
        "year",
        "title",
        "is_oos",
        "community_id",
        "community_label",
        "channel",
        "research_topic_id",
        "research_topic_title",
        "rt_launch_year",
    ]
    df[paper_cols].to_csv(HERE / "neurorobotics_papers_rt_scope.csv", index=False)

    # --- 1) Channel comparison: RT vs spontaneous ---
    channel = (
        df.groupby("channel")
        .agg(
            n=("int_id", "count"),
            oos_n=("is_oos", "sum"),
            cv_n=("is_cv", "sum"),
            neuro_n=("is_neuro", "sum"),
            primary_n=("is_primary", "sum"),
        )
        .reset_index()
    )
    channel["oos_pct"] = (100 * channel["oos_n"] / channel["n"]).round(1)
    channel["cv_pct"] = (100 * channel["cv_n"] / channel["n"]).round(1)
    channel["neuro_pct"] = (100 * channel["neuro_n"] / channel["n"]).round(1)
    channel["primary_pct"] = (100 * channel["primary_n"] / channel["n"]).round(1)
    for ch in channel["channel"]:
        shares = mix_shares(df[df["channel"] == ch])
        for k, v in shares.items():
            channel.loc[channel["channel"] == ch, f"share_{k}"] = v
    channel.to_csv(HERE / "neurorobotics_rt_vs_spontaneous.csv", index=False)
    print("=== RT vs spontaneous ===")
    print(channel.to_string(index=False))

    ch_year = (
        df.groupby(["year", "channel"])
        .agg(n=("int_id", "count"), oos_n=("is_oos", "sum"), cv_n=("is_cv", "sum"))
        .reset_index()
    )
    ch_year["oos_pct"] = (100 * ch_year["oos_n"] / ch_year["n"]).round(1)
    ch_year["cv_pct"] = (100 * ch_year["cv_n"] / ch_year["n"]).round(1)
    ch_year.to_csv(HERE / "neurorobotics_channel_by_year.csv", index=False)

    # --- 2) Per-RT OOS + drift contribution ---
    rt = df[df["in_rt"]].copy()
    by_rt = (
        rt.groupby(["research_topic_id", "research_topic_title", "rt_launch_year"], dropna=False)
        .agg(
            n=("int_id", "count"),
            oos_n=("is_oos", "sum"),
            cv_n=("is_cv", "sum"),
            neuro_n=("is_neuro", "sum"),
            primary_n=("is_primary", "sum"),
            first_year=("year", "min"),
            last_year=("year", "max"),
        )
        .reset_index()
    )
    by_rt["oos_pct"] = (100 * by_rt["oos_n"] / by_rt["n"]).round(1)
    by_rt["cv_pct"] = (100 * by_rt["cv_n"] / by_rt["n"]).round(1)
    by_rt["neuro_pct"] = (100 * by_rt["neuro_n"] / by_rt["n"]).round(1)
    by_rt["primary_pct"] = (100 * by_rt["primary_n"] / by_rt["n"]).round(1)
    # Share of all OOS / all CV papers attributable to this RT
    total_oos = int(df["is_oos"].sum())
    total_cv = int(df["is_cv"].sum())
    by_rt["oos_share_of_journal"] = (100 * by_rt["oos_n"] / max(total_oos, 1)).round(1)
    by_rt["cv_share_of_journal"] = (100 * by_rt["cv_n"] / max(total_cv, 1)).round(1)
    # Drift score: volume-weighted pull toward CV and away from neuroscience
    # (positive = contributes to observed mix shift)
    by_rt["drift_pull"] = (
        by_rt["cv_n"] - by_rt["neuro_n"]
    ).astype(float)  # net papers pushing CV vs neuro
    title = by_rt["research_topic_title"].fillna("")
    by_rt["flag_offbrand"] = title.map(lambda t: bool(OFFBRAND_RE.search(str(t))))
    by_rt["flag_onbrand"] = title.map(lambda t: bool(ONBRAND_RE.search(str(t))))
    by_rt["flag_cvish"] = title.map(lambda t: bool(CVISH_RE.search(str(t))))

    def recommend(row) -> str:
        title = str(row.get("research_topic_title") or "")
        if re.search(r"(?i)^(women in|horizons in|insights in)\b", title):
            return "keep (brand series) / audit OOS"
        if row["n"] < 3:
            return "watch (small n)"
        if row["flag_offbrand"]:
            if row["oos_pct"] >= 30 or row["cv_pct"] >= 50:
                return "remove / do not renew"
            return "gate / do not renew series"
        if row["oos_pct"] >= 45 and row["primary_pct"] < 50:
            return "remove / tight gate"
        if row["oos_pct"] >= 35 and row["cv_pct"] >= 50 and not row["flag_onbrand"]:
            return "gate (robot/embodied required)"
        if row["flag_onbrand"] and row["oos_pct"] <= 25 and row["primary_pct"] >= 60:
            return "keep / grow"
        if row["flag_cvish"] and (row["oos_pct"] >= 30 or row["cv_pct"] >= 50):
            return "gate (robot/embodied required)"
        if row["oos_pct"] >= 30:
            return "review / tighten scope"
        return "keep"

    by_rt["recommendation"] = by_rt.apply(recommend, axis=1)
    by_rt = by_rt.sort_values(["oos_n", "cv_n", "n"], ascending=False)
    by_rt.to_csv(HERE / "neurorobotics_rt_deep_dive.csv", index=False)

    print("\n=== Top OOS contributors (by oos_n) ===")
    cols = [
        "rt_launch_year",
        "n",
        "oos_n",
        "oos_pct",
        "oos_share_of_journal",
        "cv_pct",
        "recommendation",
        "research_topic_title",
    ]
    print(by_rt[cols].head(20).to_string(index=False))

    print("\n=== Top drift contributors (net CV - neuro papers) ===")
    drift_top = by_rt.sort_values("drift_pull", ascending=False)
    print(
        drift_top[
            ["rt_launch_year", "n", "cv_n", "neuro_n", "drift_pull", "cv_pct", "recommendation", "research_topic_title"]
        ]
        .head(15)
        .to_string(index=False)
    )

    print("\n=== Recommendation counts ===")
    print(by_rt["recommendation"].value_counts().to_string())

    remove = by_rt[by_rt["recommendation"].str.startswith("remove")]
    gate = by_rt[by_rt["recommendation"].str.startswith("gate")]
    keep = by_rt[by_rt["recommendation"].isin(["keep", "keep / grow"])]

    # Suggested NEW RTs from strategy gaps (not in data — editorial proposals)
    add_proposals = [
        {
            "proposed_rt": "Embodied robot vision & multimodal perception",
            "rationale": "CV already dominates volume; formalise robot-gated vision so spontaneous/CV RTs don't stretch OOS.",
        },
        {
            "proposed_rt": "Therapeutic & assistive robotics (exoskeletons, prostheses, rehab)",
            "rationale": "Therapeutic Movement share fell; dedicated RT can rebuild neural–rehab identity.",
        },
        {
            "proposed_rt": "Neural interfaces ↔ robot control (BCI, motor decoding, neurorobotic loops)",
            "rationale": "Neuroscience share collapsed to ~6–7%; RT can re-anchor the journal name.",
        },
        {
            "proposed_rt": "Learning & control for physical agents (embodied RL, adaptive control)",
            "rationale": "Aligns with Autonomous Systems primary; keeps ML on-robot rather than generic ML.",
        },
    ]
    pd.DataFrame(add_proposals).to_csv(HERE / "neurorobotics_rt_add_proposals.csv", index=False)

    # Figures
    FIG = HERE / "figures"
    FIG.mkdir(exist_ok=True)

    # Channel mix bars
    fig, axes = plt.subplots(1, 2, figsize=(9, 3.6), dpi=140)
    for ax, ch in zip(axes, ["Research Topic", "Spontaneous"]):
        sub = df[df["channel"] == ch]
        shares = mix_shares(sub)
        labs = list(PRIMARY_LABELS.values()) + ["other"]
        vals = [shares[l] for l in labs]
        ax.barh(labs[::-1], vals[::-1], color="#1a4f8c")
        ax.set_xlim(0, max(vals + [40]) * 1.15)
        oos = 100 * sub["is_oos"].mean() if len(sub) else 0
        ax.set_title(f"{ch}\nn={len(sub)} · OOS {oos:.1f}%")
        ax.set_xlabel("% of papers")
    fig.suptitle("Community mix: Research Topic vs spontaneous", fontsize=11, y=1.02)
    fig.tight_layout()
    fig.savefig(FIG / "rt_vs_spontaneous_mix.png", bbox_inches="tight")
    plt.close(fig)

    # Top OOS RTs
    top = by_rt.head(12).copy()
    top["short"] = top["research_topic_title"].astype(str).str.slice(0, 42)
    fig, ax = plt.subplots(figsize=(8, 4.5), dpi=140)
    ax.barh(top["short"][::-1], top["oos_n"][::-1], color="#c93030", alpha=0.85)
    ax.set_xlabel("OOS papers in run")
    ax.set_title("Top Research Topics by OOS paper count")
    fig.tight_layout()
    fig.savefig(FIG / "rt_top_oos.png", bbox_inches="tight")
    plt.close(fig)

    # Drift pull
    top_d = drift_top.head(12).copy()
    top_d["short"] = top_d["research_topic_title"].astype(str).str.slice(0, 42)
    fig, ax = plt.subplots(figsize=(8, 4.5), dpi=140)
    colors = ["#1a4f8c" if v >= 0 else "#6b7280" for v in top_d["drift_pull"][::-1]]
    ax.barh(top_d["short"][::-1], top_d["drift_pull"][::-1], color=colors)
    ax.axvline(0, color="#999", lw=0.8)
    ax.set_xlabel("Net papers (CV − Neuroscience communities)")
    ax.set_title("RT drift pull toward computer vision")
    fig.tight_layout()
    fig.savefig(FIG / "rt_drift_pull.png", bbox_inches="tight")
    plt.close(fig)

    summary = {
        "n_papers": int(len(df)),
        "n_rt": int(df["in_rt"].sum()),
        "n_spontaneous": int((~df["in_rt"]).sum()),
        "oos_pct_rt": round(100 * float(df.loc[df["in_rt"], "is_oos"].mean()), 1),
        "oos_pct_spontaneous": round(100 * float(df.loc[~df["in_rt"], "is_oos"].mean()), 1),
        "cv_pct_rt": round(100 * float(df.loc[df["in_rt"], "is_cv"].mean()), 1),
        "cv_pct_spontaneous": round(100 * float(df.loc[~df["in_rt"], "is_cv"].mean()), 1),
        "neuro_pct_rt": round(100 * float(df.loc[df["in_rt"], "is_neuro"].mean()), 1),
        "neuro_pct_spontaneous": round(100 * float(df.loc[~df["in_rt"], "is_neuro"].mean()), 1),
        "n_rts": int(by_rt["research_topic_id"].nunique()),
        "n_remove": int(len(remove)),
        "n_gate": int(len(gate)),
        "n_keep_grow": int(len(keep)),
        "top_oos_rts": by_rt.head(8)[
            ["research_topic_title", "n", "oos_n", "oos_pct", "recommendation"]
        ].to_dict(orient="records"),
        "top_drift_rts": drift_top.head(8)[
            ["research_topic_title", "n", "cv_n", "neuro_n", "drift_pull", "recommendation"]
        ].to_dict(orient="records"),
        "remove_list": remove[
            ["research_topic_title", "n", "oos_pct", "cv_pct", "recommendation"]
        ].to_dict(orient="records"),
        "gate_list": gate[
            ["research_topic_title", "n", "oos_pct", "cv_pct", "recommendation"]
        ].head(15).to_dict(orient="records"),
        "add_proposals": add_proposals,
        "verdict": (
            "Spontaneous submissions are more CV-heavy than RTs (~40% vs ~23% CV) and slightly "
            "less OOS (~16% vs ~22%). So the CV takeover is not 'RTs alone' — open submissions "
            "drive mix shift; RTs add OOS risk and volume, especially ML/vision/cyber-physical "
            "topics (2020-22 launch wave). Close/gate off-brand high-OOS RTs; add rehab / "
            "neural-interface / embodied-vision RTs to rebalance identity."
        ),
    }
    (HERE / "neurorobotics_rt_analysis_summary.json").write_text(
        json.dumps(summary, indent=2, default=str), encoding="utf-8"
    )
    print("\nVERDICT:", summary["verdict"])
    print(f"\nRemove/do-not-renew ({len(remove)}):")
    if len(remove):
        print(remove[["n", "oos_pct", "research_topic_title"]].to_string(index=False))
    print(f"\nGate ({len(gate)}):")
    if len(gate):
        print(gate[["n", "oos_pct", "cv_pct", "research_topic_title"]].head(12).to_string(index=False))
    print("\nWrote CSVs + figures under further_work/")


if __name__ == "__main__":
    main()
