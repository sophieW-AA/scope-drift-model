"""
Research Topic deep-dive for one Frontiers journal in the current run.

Usage:
  python src/scope_drift/analyze_rts.py
  python src/scope_drift/analyze_rts.py --journal "Frontiers in Earth Science"
"""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import pandas as pd
from google.cloud import bigquery

from paths import WORK_DIR, ensure_code_on_path

ensure_code_on_path()

from journal_profile import journal_dir, journal_profile  # noqa: E402
from neuro_analysis import (  # noqa: E402
    JOURNAL as DEFAULT_JOURNAL,
    drift_trend,
    get_journal,
    load_dashboards,
    onset_year,
)

RUN = "20260721_122750"
BQ_PROJECT = "ocean-tech-adv-analytics-c-tfs"
TBL_META = f"{BQ_PROJECT}.raw_citation_network_data.pub_metadata_raw_{RUN}"
CURRENT_YEAR = 2026
RECENT_START_YEAR = 2024

OFFBRAND_RE = re.compile(
    r"privacy|cyber.?physical|image fusion|traffic|cancer|geolog|thermal|"
    r"organic chem|immunotherap|management science|remote.?sens|"
    r"heterogeneous view perception",
    re.I,
)
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
SERIES_VOLUME_RE = re.compile(r"[\s,\-–:]+Volume\s+[IVXLC0-9]+\s*$", re.I)

# Bound per journal in analyze_journal().
JOURNAL = DEFAULT_JOURNAL
PRIMARY_IDS: set[int] = set()
PRIMARY_LABELS: dict[int, str] = {}
GAINER_ID = None
LOSER_ID = None
GAINER_LABEL = "gaining community"
LOSER_LABEL = "core community"
USE_NEURO_HEURISTICS = False


def bind_profile(profile: dict) -> None:
    global JOURNAL, PRIMARY_IDS, PRIMARY_LABELS, GAINER_ID, LOSER_ID, GAINER_LABEL, LOSER_LABEL
    global USE_NEURO_HEURISTICS
    JOURNAL = profile["name"]
    PRIMARY_IDS = set(profile["primary_ids"])
    PRIMARY_LABELS = dict(profile["primary_labels"])
    GAINER_ID = profile["gainer"]["id"]
    LOSER_ID = profile["loser"]["id"]
    GAINER_LABEL = profile["gainer"]["label"]
    LOSER_LABEL = profile["loser"]["label"]
    USE_NEURO_HEURISTICS = JOURNAL == DEFAULT_JOURNAL


def out_file(outdir: Path, stem: str) -> Path:
    if outdir.resolve() == WORK_DIR.resolve():
        return outdir / f"neurorobotics_{stem}"
    return outdir / stem


def fetch_joined(client: bigquery.Client, int_ids: list[int], journal: str) -> pd.DataFrame:
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
        rt.stage AS rt_stage,
        rt.is_active AS rt_is_active,
        rt.is_online AS rt_is_online,
        rt.is_closed AS rt_is_closed,
        rt.is_completed AS rt_is_completed,
        rt.is_deleted AS rt_is_deleted,
        CAST(rt.submission_deadline AS STRING) AS rt_submission_deadline,
        CAST(rt.extended_submission_deadline AS STRING) AS rt_extended_submission_deadline,
        CAST(rt.public_extended_deadline AS STRING) AS rt_public_extended_deadline,
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
      l.rt_stage,
      l.rt_is_active,
      l.rt_is_online,
      l.rt_is_closed,
      l.rt_is_completed,
      l.rt_is_deleted,
      l.rt_submission_deadline,
      l.rt_extended_submission_deadline,
      l.rt_public_extended_deadline,
      l.article_pub_date
    FROM run r
    LEFT JOIN linked l ON r.title_norm = l.title_norm
    """
    return client.query(
        q,
        job_config=bigquery.QueryJobConfig(
            query_parameters=[bigquery.ScalarQueryParameter("journal", "STRING", journal)]
        ),
    ).to_dataframe()


def primary_label(cid) -> str:
    if cid is None or (isinstance(cid, float) and pd.isna(cid)):
        return "other"
    cid = int(cid)
    return PRIMARY_LABELS.get(cid, "other")


def mix_shares(sub: pd.DataFrame) -> dict[str, float]:
    labs = list(dict.fromkeys(PRIMARY_LABELS.values()))
    if sub.empty:
        return {lab: 0.0 for lab in labs + ["other"]}
    names = sub["community_label"]
    n = len(names)
    out = {lab: round(100 * (names == lab).sum() / n, 1) for lab in labs}
    out["other"] = round(100 * (names == "other").sum() / n, 1)
    return out


def summarise_rts(sub: pd.DataFrame, journal_oos: int, journal_cv: int) -> pd.DataFrame:
    """Aggregate RT metrics for one narrative period."""
    columns = [
        "research_topic_id",
        "research_topic_title",
        "rt_launch_year",
        "rt_stage",
        "rt_is_open",
    ]
    if sub.empty:
        return pd.DataFrame(
            columns=columns
            + [
                "n",
                "oos_n",
                "cv_n",
                "neuro_n",
                "primary_n",
                "first_year",
                "last_year",
                "oos_pct",
                "cv_pct",
                "neuro_pct",
                "primary_pct",
                "oos_share_of_journal",
                "cv_share_of_journal",
                "drift_pull",
                "flag_offbrand",
                "flag_onbrand",
                "flag_cvish",
            ]
        )

    out = (
        sub.groupby(columns, dropna=False)
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
    out["oos_pct"] = (100 * out["oos_n"] / out["n"]).round(1)
    out["cv_pct"] = (100 * out["cv_n"] / out["n"]).round(1)
    out["neuro_pct"] = (100 * out["neuro_n"] / out["n"]).round(1)
    out["primary_pct"] = (100 * out["primary_n"] / out["n"]).round(1)
    out["oos_share_of_journal"] = (100 * out["oos_n"] / max(journal_oos, 1)).round(1)
    out["cv_share_of_journal"] = (100 * out["cv_n"] / max(journal_cv, 1)).round(1)
    out["drift_pull"] = (out["cv_n"] - out["neuro_n"]).astype(float)
    title = out["research_topic_title"].fillna("")
    if USE_NEURO_HEURISTICS:
        out["flag_offbrand"] = title.map(lambda value: bool(OFFBRAND_RE.search(str(value))))
        out["flag_onbrand"] = title.map(lambda value: bool(ONBRAND_RE.search(str(value))))
        out["flag_cvish"] = title.map(lambda value: bool(CVISH_RE.search(str(value))))
    else:
        out["flag_offbrand"] = False
        out["flag_onbrand"] = False
        out["flag_cvish"] = False
    return out


def rt_launch_attribution(
    all_by_rt: pd.DataFrame,
    onset: int | None,
) -> tuple[pd.DataFrame, dict]:
    """Test whether drift traces back to specific Research Topic launches.

    A Frontiers specialty journal has no Specialty Sections, so the Research Topic
    is the only structural launch unit available. Two things decide whether a launch
    "caused" the drift: how concentrated the gainer-community pull is in a few topics, and whether
    those topics launched around the drift onset year rather than after it.
    """
    cohorts = (
        all_by_rt.groupby("rt_launch_year", dropna=False)
        .agg(
            n_rts=("research_topic_id", "nunique"),
            papers=("n", "sum"),
            cv_n=("cv_n", "sum"),
            neuro_n=("neuro_n", "sum"),
            oos_n=("oos_n", "sum"),
        )
        .reset_index()
        .sort_values("rt_launch_year")
    )
    cohorts["drift_pull"] = (cohorts["cv_n"] - cohorts["neuro_n"]).astype(int)
    cohorts["cv_pct"] = (100 * cohorts["cv_n"] / cohorts["papers"]).round(1)
    cohorts["neuro_pct"] = (100 * cohorts["neuro_n"] / cohorts["papers"]).round(1)
    cohorts["oos_pct"] = (100 * cohorts["oos_n"] / cohorts["papers"]).round(1)

    pos = all_by_rt[all_by_rt["drift_pull"] > 0].sort_values(
        ["drift_pull", "n"], ascending=False
    )
    total_pull = float(pos["drift_pull"].sum())

    def pull_share(value: float) -> float:
        return round(100 * float(value) / total_pull, 1) if total_pull else 0.0

    # How many topics it takes to account for half of all positive CV pull. A small
    # number means a few launches drove the shift; a large one means it is cumulative.
    running, n_to_half = 0.0, 0
    for value in pos["drift_pull"]:
        running += float(value)
        n_to_half += 1
        if total_pull and running >= total_pull / 2:
            break

    top1_share = pull_share(pos.iloc[0]["drift_pull"]) if len(pos) else 0.0
    top3_share = pull_share(pos.head(3)["drift_pull"].sum()) if len(pos) else 0.0

    # Launches dated to the drift onset window (onset year and the year before it),
    # which is when a causal launch would have had to appear. The net figure counts
    # every topic in those cohorts, not just the ones pulling toward vision.
    onset_window = [onset - 1, onset] if onset else []
    onset_cohorts = cohorts[cohorts["rt_launch_year"].isin(onset_window)]
    onset_net_pull = int(onset_cohorts["drift_pull"].sum()) if len(onset_cohorts) else 0
    n_rts_at_onset = int(onset_cohorts["n_rts"].sum()) if len(onset_cohorts) else 0

    # First cohort with a clear gainer tilt: at least twice the loser share,
    # on enough papers to read.
    cv_heavy = cohorts[
        (cohorts["papers"] >= 20) & (cohorts["cv_pct"] >= 2 * cohorts["neuro_pct"])
    ]
    first_cv_heavy = int(cv_heavy["rt_launch_year"].min()) if len(cv_heavy) else None

    if total_pull == 0:
        verdict = f"no measurable pull toward {GAINER_LABEL} from any Research Topic"
    elif top1_share >= 25:
        verdict = "one launch dominates"
    elif n_to_half <= 3:
        verdict = "a small group of launches"
    elif onset_net_pull <= 0 and first_cv_heavy and onset and first_cv_heavy > onset:
        verdict = "launches followed the drift"
    else:
        verdict = "no single launch"

    top_launches = pos.head(6)[
        [
            "research_topic_title",
            "rt_launch_year",
            "first_year",
            "last_year",
            "n",
            "cv_n",
            "neuro_n",
            "drift_pull",
            "rt_stage",
            "rt_is_open",
        ]
    ].copy()
    top_launches["pull_share"] = top_launches["drift_pull"].map(pull_share)

    stats = {
        "n_rts_with_pull": int(len(pos)),
        "total_pull": int(total_pull),
        "top1_share": top1_share,
        "top3_share": top3_share,
        "n_to_half": int(n_to_half),
        "onset_year": int(onset) if onset else None,
        "onset_window": [int(y) for y in onset_window],
        "onset_net_pull": onset_net_pull,
        "n_rts_launched_at_onset": n_rts_at_onset,
        "first_cv_heavy_cohort": first_cv_heavy,
        "verdict": verdict,
        "cohorts": cohorts.to_dict(orient="records"),
        "top_launches": top_launches.to_dict(orient="records"),
    }
    return cohorts, stats


def series_attribution(all_by_rt: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    """Roll recurring Research Topic volumes up into their series.

    Individual topics look small because a successful theme is split across
    "Volume II", "Volume III" and so on. Renewal is decided per series, and that
    decision stays live even when every existing volume is closed, so series pull
    is the actionable unit for a keep/renew call.
    """
    out = all_by_rt.copy()
    out["series"] = (
        out["research_topic_title"]
        .astype(str)
        .str.replace(SERIES_VOLUME_RE, "", regex=True)
        .str.strip()
    )
    grouped = (
        out.groupby("series")
        .agg(
            volumes=("research_topic_id", "nunique"),
            n=("n", "sum"),
            cv_n=("cv_n", "sum"),
            neuro_n=("neuro_n", "sum"),
            oos_n=("oos_n", "sum"),
            last_year=("last_year", "max"),
            any_open=("rt_is_open", "any"),
        )
        .reset_index()
    )
    grouped["drift_pull"] = (grouped["cv_n"] - grouped["neuro_n"]).astype(int)
    grouped["oos_pct"] = (100 * grouped["oos_n"] / grouped["n"]).round(1)
    grouped = grouped.sort_values(["drift_pull", "n"], ascending=False)

    total_pull = float(grouped.loc[grouped["drift_pull"] > 0, "drift_pull"].sum())
    grouped["pull_share"] = (
        (100 * grouped["drift_pull"] / total_pull).round(1) if total_pull else 0.0
    )

    multi = grouped[grouped["volumes"] > 1]
    multi_pull = float(multi.loc[multi["drift_pull"] > 0, "drift_pull"].sum())
    top = grouped.head(5)
    stats = {
        "n_series": int(len(grouped)),
        "n_multi_volume": int(len(multi)),
        "multi_volume_pull_share": round(100 * multi_pull / total_pull, 1) if total_pull else 0.0,
        "top_series_share": float(top.iloc[0]["pull_share"]) if len(top) else 0.0,
        "top_series": top[
            [
                "series",
                "volumes",
                "n",
                "cv_n",
                "neuro_n",
                "oos_pct",
                "drift_pull",
                "pull_share",
                "last_year",
                "any_open",
            ]
        ].to_dict(orient="records"),
    }
    return grouped, stats


def fig_rt_top_oos(current_by_rt: pd.DataFrame, path: Path) -> bool:
    """Bar chart of OOS papers per Online RT.

    Skipped when fewer than three topics carry any OOS: a chart of empty bars
    takes a third of a page and says less than the table beside it.
    """
    top = current_by_rt.head(10).copy()
    if int((top["oos_n"] > 0).sum()) < 3:
        path.unlink(missing_ok=True)
        return False
    top["short"] = top["research_topic_title"].astype(str).str.slice(0, 42)
    fig, ax = plt.subplots(figsize=(9.2, 3.2), dpi=140)
    ax.barh(top["short"][::-1], top["oos_n"][::-1], color="#c93030", alpha=0.85)
    ax.set_xlabel("OOS papers since RT launch")
    ax.set_title("Currently Online RTs by OOS paper count")
    fig.tight_layout()
    fig.savefig(path, bbox_inches="tight")
    plt.close(fig)
    return True


def fig_rt_drift_pull(drift_top: pd.DataFrame, path: Path) -> bool:
    top_d = drift_top.head(10).copy()
    top_d["short"] = top_d["research_topic_title"].astype(str).str.slice(0, 42)
    fig, ax = plt.subplots(figsize=(9.2, 3.2), dpi=140)
    bar_colors = ["#1a4f8c" if v >= 0 else "#6b7280" for v in top_d["drift_pull"][::-1]]
    ax.barh(top_d["short"][::-1], top_d["drift_pull"][::-1], color=bar_colors)
    ax.axvline(0, color="#999", lw=0.8)
    ax.set_xlabel(f"Net papers ({GAINER_LABEL} − {LOSER_LABEL})")
    ax.set_title(f"Historic RT drift pull toward {GAINER_LABEL} (pre-2026)")
    fig.tight_layout()
    fig.savefig(path, bbox_inches="tight")
    plt.close(fig)
    return True


def analyze_journal(journal: str, outdir: Path) -> Path:
    scope, drift, maps = load_dashboards()
    sj = get_journal(scope, journal)
    mj = get_journal(maps, journal)
    profile = journal_profile(sj)
    bind_profile(profile)
    outdir.mkdir(parents=True, exist_ok=True)
    print(f"\n=== {JOURNAL} ===")
    print(f"Gainer: {GAINER_LABEL} (id={GAINER_ID}, delta {profile['gainer']['delta']} pp)")
    print(f"Loser:  {LOSER_LABEL} (id={LOSER_ID}, delta {profile['loser']['delta']} pp)")

    scatter = mj.get("scatter") or []
    sc = pd.DataFrame(scatter)
    sc["int_id"] = sc["i"].astype(int)
    sc["is_oos"] = sc["s"] == 0
    sc["community_id"] = sc["c"]
    sc["community_label"] = sc["community_id"].map(primary_label)
    sc["year"] = sc["yr"]

    client = bigquery.Client(project=BQ_PROJECT, location="EU")
    linked = fetch_joined(client, sc["int_id"].tolist(), JOURNAL)
    linked = linked.sort_values(["int_id", "article_id"]).drop_duplicates("int_id")

    df = sc.merge(linked, on="int_id", how="left")
    df["in_rt"] = df["research_topic_id"].notna()
    df["channel"] = df["in_rt"].map({True: "Research Topic", False: "Spontaneous"})
    df["rt_launch_year"] = pd.to_datetime(df["rt_create_date"], errors="coerce").dt.year
    df["community_id"] = pd.to_numeric(df["community_id"], errors="coerce")
    df["is_cv"] = df["community_id"] == GAINER_ID
    df["is_neuro"] = df["community_id"] == LOSER_ID
    df["is_primary"] = df["community_id"].isin(PRIMARY_IDS)
    df["rt_is_open"] = (
        df["rt_is_active"].fillna(False)
        & df["rt_is_online"].fillna(False)
        & ~df["rt_is_closed"].fillna(False)
        & ~df["rt_is_completed"].fillna(False)
        & ~df["rt_is_deleted"].fillna(False)
    )

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
        "rt_stage",
        "rt_is_open",
        "rt_submission_deadline",
        "rt_extended_submission_deadline",
        "rt_public_extended_deadline",
    ]
    df[paper_cols].to_csv(out_file(outdir, "papers_rt_scope.csv"), index=False)

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
    channel.to_csv(out_file(outdir, "rt_vs_spontaneous.csv"), index=False)
    print("=== RT vs spontaneous ===")
    print(channel.to_string(index=False))

    ch_year = (
        df.groupby(["year", "channel"])
        .agg(n=("int_id", "count"), oos_n=("is_oos", "sum"), cv_n=("is_cv", "sum"))
        .reset_index()
    )
    ch_year["oos_pct"] = (100 * ch_year["oos_n"] / ch_year["n"]).round(1)
    ch_year["cv_pct"] = (100 * ch_year["cv_n"] / ch_year["n"]).round(1)
    ch_year.to_csv(out_file(outdir, "channel_by_year.csv"), index=False)

    # --- 2) Split attribution from action ---
    # Historic (<2026): explain which RTs contributed to the accumulated drift.
    # Current: recommend action only for RTs that RDM confirms are Online. These
    # are scored on their whole publication history in the run, not a single year,
    # so a topic that has been open for several years is judged on all its papers.
    rt = df[df["in_rt"]].copy()
    historic = df[df["year"] < CURRENT_YEAR].copy()
    historic_rt = rt[rt["year"] < CURRENT_YEAR].copy()
    open_rt_papers = rt[rt["rt_is_open"]].copy()
    closed_rt_papers = rt[~rt["rt_is_open"]].copy()
    spontaneous_papers = df[~df["in_rt"]].copy()

    historic_by_rt = summarise_rts(
        historic_rt,
        int(historic["is_oos"].sum()),
        int(historic["is_cv"].sum()),
    )
    historic_by_rt["recommendation"] = "historic attribution only"
    historic_by_rt = historic_by_rt.sort_values(["drift_pull", "n"], ascending=False)
    historic_by_rt.to_csv(out_file(outdir, "rt_historic_drift.csv"), index=False)

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
            return "gate (core-scope required)"
        if row["flag_onbrand"] and row["oos_pct"] <= 25 and row["primary_pct"] >= 60:
            return "keep / grow"
        if row["flag_cvish"] and (row["oos_pct"] >= 30 or row["cv_pct"] >= 50):
            return "gate (core-scope required)"
        if row["oos_pct"] >= 30:
            return "review / tighten scope"
        if row["oos_n"] > 0:
            return "keep / audit current OOS"
        return "keep"

    current_by_rt = summarise_rts(
        open_rt_papers,
        int(df["is_oos"].sum()),
        int(df["is_cv"].sum()),
    )
    current_by_rt["recommendation"] = current_by_rt.apply(recommend, axis=1)
    current_by_rt = current_by_rt.sort_values(["oos_n", "cv_n", "n"], ascending=False)
    current_by_rt.to_csv(out_file(outdir, "current_open_rt.csv"), index=False)

    # --- 2b) Launch attribution: this journal has no Specialty Sections, so the
    # Research Topic is the only structural launch unit that could explain drift.
    all_by_rt = summarise_rts(rt, int(df["is_oos"].sum()), int(df["is_cv"].sum()))
    onset = onset_year(drift_trend(drift, JOURNAL))
    launch_cohorts, launch_stats = rt_launch_attribution(all_by_rt, onset)
    launch_cohorts.to_csv(out_file(outdir, "rt_launch_attribution.csv"), index=False)
    series_table, series_stats = series_attribution(all_by_rt)
    series_table.to_csv(out_file(outdir, "rt_series_attribution.csv"), index=False)
    print("\n=== RT series (recurring volumes rolled up) ===")
    print(series_table.head(8).to_string(index=False, max_colwidth=48))
    print("\n=== RT launch cohorts (drift onset %s) ===" % onset)
    print(launch_cohorts.to_string(index=False))
    print(
        f"Pull concentration: top RT {launch_stats['top1_share']}%, top 3 "
        f"{launch_stats['top3_share']}%, {launch_stats['n_to_half']} RTs to reach half "
        f"of {launch_stats['total_pull']} net {GAINER_LABEL} papers -> {launch_stats['verdict']}"
    )

    # Compatibility output: clearly separates non-actionable history from current action rows.
    historic_export = historic_by_rt.copy()
    historic_export["period"] = "Historic (pre-2026)"
    current_export = current_by_rt.copy()
    current_export["period"] = "Current (RT Online, all years)"
    deep_path = (
        WORK_DIR / "neurorobotics_rt_deep_dive.csv" if outdir.resolve() == WORK_DIR.resolve()
        else outdir / "rt_deep_dive.csv"
    )
    pd.concat([historic_export, current_export], ignore_index=True).to_csv(
        deep_path, index=False
    )

    print("\n=== Currently Online RTs, all papers since launch ===")
    cols = [
        "rt_stage",
        "rt_launch_year",
        "first_year",
        "last_year",
        "n",
        "oos_n",
        "oos_pct",
        "oos_share_of_journal",
        "cv_pct",
        "recommendation",
        "research_topic_title",
    ]
    print(current_by_rt[cols].head(20).to_string(index=False))

    print("\n=== Historic drift contributors, pre-2026 (net CV - neuro papers) ===")
    drift_top = historic_by_rt.sort_values("drift_pull", ascending=False)
    print(
        drift_top[
            ["rt_launch_year", "n", "cv_n", "neuro_n", "drift_pull", "cv_pct", "rt_stage", "research_topic_title"]
        ]
        .head(15)
        .to_string(index=False)
    )

    print("\n=== Current recommendation counts ===")
    print(current_by_rt["recommendation"].value_counts().to_string())

    remove = current_by_rt[current_by_rt["recommendation"].str.startswith("remove")]
    gate = current_by_rt[current_by_rt["recommendation"].str.startswith("gate")]
    keep = current_by_rt[current_by_rt["recommendation"].str.startswith("keep")]
    watch = current_by_rt[current_by_rt["recommendation"].str.startswith("watch")]

    # Do not propose new RTs from historic drift; the brief's recommendations stay
    # limited to topics that are currently open and therefore actionable.
    add_proposals: list[dict] = []
    pd.DataFrame(columns=["proposed_rt", "rationale"]).to_csv(
        out_file(outdir, "rt_add_proposals.csv"), index=False
    )

    FIG = outdir / "figures"
    FIG.mkdir(exist_ok=True)

    # Mix bars: currently Online RTs (all their papers) vs spontaneous submissions.
    fig, axes = plt.subplots(1, 2, figsize=(9.6, 2.8), dpi=140)
    for ax, ch in zip(axes, ["Currently Online RTs", "Spontaneous"]):
        if ch == "Currently Online RTs":
            sub = open_rt_papers
        else:
            sub = spontaneous_papers
        shares = mix_shares(sub)
        labs = list(PRIMARY_LABELS.values()) + ["other"]
        vals = [shares[l] for l in labs]
        ax.barh(labs[::-1], vals[::-1], color="#1a4f8c")
        ax.set_xlim(0, max(vals + [40]) * 1.15)
        oos = 100 * sub["is_oos"].mean() if len(sub) else 0
        ax.set_title(f"{ch}\nn={len(sub)} · OOS {oos:.1f}%")
        ax.set_xlabel("% of papers")
    fig.suptitle("Community mix: currently Online RTs vs spontaneous", fontsize=11, y=1.02)
    fig.tight_layout()
    fig.savefig(FIG / "rt_vs_spontaneous_mix.png", bbox_inches="tight")
    plt.close(fig)

    # Current OOS: RTs currently marked Online, counting all papers since launch.
    fig_rt_top_oos(current_by_rt, FIG / "rt_top_oos.png")

    # Historic drift attribution: closed/completed RTs remain evidence, not actions.
    fig_rt_drift_pull(drift_top, FIG / "rt_drift_pull.png")

    def pct(sub: pd.DataFrame, column: str) -> float:
        return round(100 * float(sub[column].mean()), 1) if len(sub) else 0.0

    recent = df[df["year"] >= RECENT_START_YEAR].copy()
    recent_shares = mix_shares(recent)
    gainer_share = recent_shares.get(GAINER_LABEL, 0.0)
    loser_share = recent_shares.get(LOSER_LABEL, 0.0)
    summary = {
        "journal": JOURNAL,
        "gainer": profile["gainer"],
        "loser": profile["loser"],
        "primary_labels": {str(k): v for k, v in PRIMARY_LABELS.items()},
        "historic_period": "2020-2025",
        "current_period": "RTs currently Online (all papers since launch)",
        "recent_period": f"{RECENT_START_YEAR}-{CURRENT_YEAR}",
        "recent_n_papers": int(len(recent)),
        "recent_n_rt": int(recent["in_rt"].sum()),
        "recent_n_spontaneous": int((~recent["in_rt"]).sum()),
        "recent_n_open_rt": int(recent["rt_is_open"].sum()),
        "recent_oos_n": int(recent["is_oos"].sum()),
        "recent_oos_pct": pct(recent, "is_oos"),
        "recent_gainer_pct": gainer_share,
        "recent_loser_pct": loser_share,
        "recent_cv_pct": gainer_share,
        "recent_neuro_pct": loser_share,
        "recent_primary_shares": {k: v for k, v in recent_shares.items() if k != "other"},
        "recent_other_pct": recent_shares.get("other", 0.0),
        "recent_by_year": [
            {
                "year": int(y),
                "n": int(len(sub)),
                "oos_pct": pct(sub, "is_oos"),
                "cv_pct": mix_shares(sub).get(GAINER_LABEL, 0.0),
                "neuro_pct": mix_shares(sub).get(LOSER_LABEL, 0.0),
                "gainer_pct": mix_shares(sub).get(GAINER_LABEL, 0.0),
                "loser_pct": mix_shares(sub).get(LOSER_LABEL, 0.0),
            }
            for y, sub in recent.groupby("year")
        ],
        "n_papers": int(len(df)),
        "n_rt": int(df["in_rt"].sum()),
        "n_spontaneous": int((~df["in_rt"]).sum()),
        "oos_pct_rt": round(100 * float(df.loc[df["in_rt"], "is_oos"].mean()), 1),
        "oos_pct_spontaneous": round(100 * float(df.loc[~df["in_rt"], "is_oos"].mean()), 1),
        "cv_pct_rt": round(100 * float(df.loc[df["in_rt"], "is_cv"].mean()), 1),
        "cv_pct_spontaneous": round(100 * float(df.loc[~df["in_rt"], "is_cv"].mean()), 1),
        "neuro_pct_rt": round(100 * float(df.loc[df["in_rt"], "is_neuro"].mean()), 1),
        "neuro_pct_spontaneous": round(100 * float(df.loc[~df["in_rt"], "is_neuro"].mean()), 1),
        "historic_n_papers": int(len(historic)),
        "historic_n_rts": int(historic_by_rt["research_topic_id"].nunique()),
        "open_rt_n_papers": int(len(open_rt_papers)),
        "closed_rt_n_papers": int(len(closed_rt_papers)),
        "spontaneous_n_papers": int(len(spontaneous_papers)),
        "open_rt_first_year": int(open_rt_papers["year"].min()) if len(open_rt_papers) else None,
        "open_rt_last_year": int(open_rt_papers["year"].max()) if len(open_rt_papers) else None,
        "open_rt_oos_n": int(open_rt_papers["is_oos"].sum()),
        "open_rt_cv_n": int(open_rt_papers["is_cv"].sum()),
        "open_rt_neuro_n": int(open_rt_papers["is_neuro"].sum()),
        "open_rt_oos_pct": pct(open_rt_papers, "is_oos"),
        "open_rt_cv_pct": pct(open_rt_papers, "is_cv"),
        "open_rt_neuro_pct": pct(open_rt_papers, "is_neuro"),
        "spontaneous_oos_n": int(spontaneous_papers["is_oos"].sum()),
        "spontaneous_cv_n": int(spontaneous_papers["is_cv"].sum()),
        "spontaneous_oos_pct": pct(spontaneous_papers, "is_oos"),
        "spontaneous_cv_pct": pct(spontaneous_papers, "is_cv"),
        "spontaneous_neuro_pct": pct(spontaneous_papers, "is_neuro"),
        "n_rts": int(current_by_rt["research_topic_id"].nunique()),
        "n_remove": int(len(remove)),
        "n_gate": int(len(gate)),
        "n_keep_grow": int(len(keep)),
        "n_watch": int(len(watch)),
        "current_top_oos_rts": current_by_rt.head(10)[
            [
                "research_topic_title",
                "rt_stage",
                "first_year",
                "last_year",
                "n",
                "oos_n",
                "oos_pct",
                "recommendation",
            ]
        ].to_dict(orient="records"),
        "historic_top_drift_rts": drift_top.head(8)[
            ["research_topic_title", "rt_stage", "n", "cv_n", "neuro_n", "drift_pull"]
        ].to_dict(orient="records"),
        "remove_list": remove[
            ["research_topic_title", "n", "oos_pct", "cv_pct", "recommendation"]
        ].to_dict(orient="records"),
        "gate_list": gate[
            ["research_topic_title", "n", "oos_pct", "cv_pct", "recommendation"]
        ].head(15).to_dict(orient="records"),
        "watch_list": watch[
            ["research_topic_title", "n", "oos_pct", "cv_pct", "recommendation"]
        ].to_dict(orient="records"),
        "add_proposals": add_proposals,
        "launch_attribution": launch_stats,
        "series_attribution": series_stats,
        "verdict": (
            "Historic RTs are retained only to explain pre-2026 drift. Editorial actions cover only "
            "RTs currently marked Online in RDM, scored on every paper they have published in the "
            "run window rather than a single year. Closed, completed and deleted RTs never appear in "
            "the recommendation lists, however strongly they contributed to past drift."
        ),
    }
    summary_path = out_file(outdir, "rt_analysis_summary.json")
    summary_path.write_text(json.dumps(summary, indent=2, default=str), encoding="utf-8")
    print("\nVERDICT:", summary["verdict"])
    print(f"\nRemove/do-not-renew ({len(remove)}):")
    if len(remove):
        print(remove[["n", "oos_pct", "research_topic_title"]].to_string(index=False))
    print(f"\nGate ({len(gate)}):")
    if len(gate):
        print(gate[["n", "oos_pct", "cv_pct", "research_topic_title"]].head(12).to_string(index=False))
    print(f"Wrote {summary_path}")
    return summary_path


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--journal", default=DEFAULT_JOURNAL)
    parser.add_argument("--outdir", default="")
    args = parser.parse_args()
    outdir = Path(args.outdir) if args.outdir else (
        WORK_DIR if args.journal == DEFAULT_JOURNAL else journal_dir(args.journal)
    )
    analyze_journal(args.journal, outdir)


if __name__ == "__main__":
    main()
