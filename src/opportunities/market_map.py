"""Hybrid market map: independent world markets, subdivided by Leiden scope.

AIRAK level-1 fields decide whether opportunity exists. Leiden communities only
subdivide those independently measured markets into useful journal and section
scopes. Frontiers share is applied afterwards and does one job: choose what to
do about the opportunity.

This is deliberately independent of the P0-P5 drift tree, which answers a
different question ("which journals are drifting"). Inputs are
`classification_raw` / `pub_metadata_raw`, plus the taxonomy label and L2 topic
tables for naming.

    python src/opportunities/market_map.py --run 20260827_081311
"""

from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path

import pandas as pd

_SRC = Path(__file__).resolve().parents[1]
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))

from opportunities import config as C  # noqa: E402

log = logging.getLogger("opportunities.market")


def fetch_year_counts(run_timestamp: str, level: str) -> pd.DataFrame:
    """Independent world and Frontiers counts per (community, year, month).

    World counts come from every AIRAK publisher and are apportioned to Leiden
    scopes with stable field-to-community weights. The citation ego network is
    never used as the global denominator.
    """
    from opportunities.world_market import fetch_community_year_counts

    return fetch_community_year_counts(run_timestamp, level)


def resolve_growth_months(df: pd.DataFrame) -> tuple[list[int], int, float]:
    """Every year in the run, plus the month cut-off growth is measured on.

    The run is exported part-way through its newest year, so that year holds a
    fraction of a real year's papers. Dropping it threw away the most
    decision-relevant data. Scaling it up to a full-year equivalent is worse
    than it looks: any scale factor derived from prior-year volume has that
    period's growth baked into it, so the correction quietly drags every
    growth rate toward zero — it moved the corpus from 8%/yr to 3.4%/yr on
    this run purely as an artefact.

    So nothing is scaled and nothing is dropped. Growth is measured on the
    same months in every year — January to `max_month` — which is like-for-like
    by construction and needs no assumption about how the rest of the year
    will land. Volume columns still count every paper in the run.

    Publication dates accrue for weeks after the fact, so the final month or
    two of the newest year are under-reported; trailing months below
    `MARKET_MONTH_REPORTED_RATIO` of the year's peak month are treated as not
    yet in.
    """
    years = sorted(int(y) for y in df["year"].unique())
    newest = years[-1]
    by_month = (
        df[df["year"] == newest].groupby("month")["n_global"].sum().sort_index()
    )
    max_month = 12
    if len(by_month):
        peak = float(by_month.max()) * C.MARKET_MONTH_REPORTED_RATIO
        reported = [int(m) for m, n in by_month.items() if float(n) >= peak]
        max_month = max(reported) if reported else int(by_month.index.max())

    # How much of a normal year those months represent, from the prior years'
    # own seasonality. Reported for transparency; growth does not use it.
    prior = df[df["year"] < newest]
    ytd_share = 1.0
    if len(prior) and max_month < 12:
        prior_full = prior.groupby("year")["n_global"].sum()
        prior_ytd = prior[prior["month"] <= max_month].groupby("year")[
            "n_global"
        ].sum()
        per_year = prior_ytd.reindex(prior_full.index, fill_value=0) / prior_full.clip(
            lower=1
        )
        ytd_share = float(per_year.mean())

    if max_month < 12:
        log.info(
            "%s is reported through month %s (~%.0f%% of a normal year) — growth "
            "compares months 1-%s across every year, volume counts every paper",
            newest,
            max_month,
            ytd_share * 100,
            max_month,
        )
    log.info("years: %s", ", ".join(str(y) for y in years))
    return years, max_month, ytd_share


def build_market_map(
    df_years: pd.DataFrame,
    labels: pd.DataFrame | None = None,
    topics: pd.DataFrame | None = None,
    launchable_band: tuple[float, float] | None = None,
    min_3y: float | None = None,
) -> tuple[pd.DataFrame, dict]:
    """Size, growth and Frontiers share per community, then classify.

    `min_3y` overrides the small-community floor. Bundling needs the unfiltered
    frame, since children below the floor still contribute volume to a bundle.
    """
    years, max_month, ytd_share = resolve_growth_months(df_years)
    if len(years) < 2:
        raise RuntimeError(f"need at least 2 years to measure growth, got {years}")
    base_year, late_year = years[0], years[-1]
    window = years[-3:] if len(years) >= 3 else years
    k = late_year - base_year

    d = df_years[df_years["year"].isin(years)]
    win = d[d["year"].isin(window)]
    # Like-for-like slice: the same calendar months in every year.
    ytd = d[d["month"] <= max_month]

    agg = win.groupby("community_id").agg(
        n_global_3y=("n_global", "sum"), n_fi_3y=("n_fi", "sum")
    )
    full = d.groupby(["community_id", "year"])[["n_global", "n_fi"]].sum()
    slice_ = ytd.groupby(["community_id", "year"])["n_global"].sum()

    def _at(frame, year, col=None):
        sub = frame.xs(year, level="year")
        sub = sub[col] if col else sub
        return sub.reindex(agg.index).fillna(0)

    agg["n_global_base"] = _at(full, base_year, "n_global")
    agg["n_global_late"] = _at(full, late_year, "n_global")
    agg["n_fi_base"] = _at(full, base_year, "n_fi").astype(int)
    agg["n_fi_late"] = _at(full, late_year, "n_fi").astype(int)
    # Growth endpoints. Same months at both ends, so no scaling is applied and
    # the part-year newest endpoint is not a collapse. Volume columns above
    # still hold every paper in the run.
    agg["n_global_base_ytd"] = _at(slice_.to_frame("n_global"), base_year, "n_global")
    agg["n_global_late_ytd"] = _at(slice_.to_frame("n_global"), late_year, "n_global")

    corpus_base = int(d.loc[d["year"] == base_year, "n_global"].sum())
    corpus_late = int(d.loc[d["year"] == late_year, "n_global"].sum())
    corpus_base_ytd = int(ytd.loc[ytd["year"] == base_year, "n_global"].sum())
    corpus_late_ytd = int(ytd.loc[ytd["year"] == late_year, "n_global"].sum())
    corpus_cagr = (corpus_late_ytd / max(corpus_base_ytd, 1)) ** (1 / k) - 1
    fi_baseline_share = float(
        win["n_fi"].sum() / max(win["n_global"].sum(), 1)
    )
    log.info(
        "corpus: %s papers in %s-%s | growth %s -> %s over months 1-%s "
        "(%.1f%%/yr) | Frontiers share of corpus %.3f%%",
        f"{int(win['n_global'].sum()):,}",
        window[0],
        window[-1],
        f"{corpus_base_ytd:,}",
        f"{corpus_late_ytd:,}",
        max_month,
        corpus_cagr * 100,
        fi_baseline_share * 100,
    )

    floor = C.MARKET_MIN_3Y if min_3y is None else float(min_3y)
    m = agg[agg["n_global_3y"] >= floor].copy()
    log.info(
        "%s of %s communities clear the %s-paper floor",
        f"{len(m):,}",
        f"{len(agg):,}",
        f"{int(floor):,}",
    )

    # Growth. Absolute CAGR is reported but the gate is excess over the corpus,
    # so a community growing slower than world output is not called "growing".
    grow_ok = m["n_global_base_ytd"] > 0
    m["cagr"] = pd.NA
    m.loc[grow_ok, "cagr"] = (
        m.loc[grow_ok, "n_global_late_ytd"] / m.loc[grow_ok, "n_global_base_ytd"]
    ) ** (1 / k) - 1
    m["cagr"] = pd.to_numeric(m["cagr"], errors="coerce")
    m["excess_cagr"] = m["cagr"] - corpus_cagr
    # Shares are ratios within a year, so they need no annualisation.
    m["share_of_world_base"] = m["n_global_base"] / max(corpus_base, 1)
    m["share_of_world_late"] = m["n_global_late"] / max(corpus_late, 1)
    m["share_of_world_delta"] = (
        m["share_of_world_late"] - m["share_of_world_base"]
    )

    # Frontiers presence is attached after the market test. It chooses the
    # action and never contributes to `is_large`, `is_growing`, or the score.
    m["fi_share"] = m["n_fi_3y"] / m["n_global_3y"].where(m["n_global_3y"] > 0, 1)
    m["fi_share_vs_portfolio"] = m["fi_share"] / max(fi_baseline_share, 1e-12)

    band = launchable_band or (C.MARKET_LAUNCHABLE_MIN_3Y, C.MARKET_LAUNCHABLE_MAX_3Y)
    m["is_large"] = m["n_global_3y"] >= C.MARKET_LARGE_3Y
    m["is_launchable_size"] = m["n_global_3y"].between(band[0], band[1])
    # Gate on the endpoint that actually forms the ratio, not the full base year.
    m["growth_reliable"] = m["n_global_base_ytd"] >= C.MARKET_GROWTH_MIN_BASE
    m["is_growing"] = m["growth_reliable"] & (
        m["excess_cagr"].fillna(-1) >= C.MARKET_EXCESS_CAGR
    )
    m["is_opportunity"] = m["is_large"] | m["is_growing"]
    log.info(
        "growth gate: %s of %s communities have a base year of %s+ papers",
        f"{int(m['growth_reliable'].sum()):,}",
        f"{len(m):,}",
        C.MARKET_GROWTH_MIN_BASE,
    )

    m["presence"] = "partial"
    m.loc[
        m["fi_share_vs_portfolio"] < C.MARKET_WHITESPACE_RATIO, "presence"
    ] = "whitespace"
    m.loc[
        m["fi_share_vs_portfolio"] >= C.MARKET_COVERED_RATIO, "presence"
    ] = "covered"

    def _kind(r) -> str:
        if r["is_large"] and r["is_growing"]:
            return "large_and_growing"
        if r["is_large"]:
            return "large"
        if r["is_growing"]:
            return "growing"
        return ""

    m["opportunity_kind"] = m.apply(_kind, axis=1)

    out = m.reset_index()
    out = _attach_names(out, labels, topics)

    # Rank on market facts only. Frontiers thinness used to multiply the score,
    # which made our current publishing footprint determine opportunity.
    size_f = (out["n_global_3y"] / C.MARKET_SIZE_SCORE_REF).clip(upper=10.0)
    grow_f = 1.0 + out["excess_cagr"].fillna(0.0).clip(lower=0.0) * 5.0
    out["opportunity_score"] = (size_f * grow_f).round(3)

    out["base_year"] = base_year
    out["late_year"] = late_year
    out["window_years"] = ",".join(str(y) for y in window)
    out["corpus_cagr"] = round(float(corpus_cagr), 4)
    out["fi_portfolio_share"] = round(fi_baseline_share, 5)
    out["growth_max_month"] = max_month
    out["growth_ytd_share"] = round(float(ytd_share), 4)
    for col in (
        "cagr",
        "excess_cagr",
        "fi_share",
        "fi_share_vs_portfolio",
        "share_of_world_base",
        "share_of_world_late",
        "share_of_world_delta",
    ):
        out[col] = pd.to_numeric(out[col], errors="coerce").round(6)

    out = out.sort_values(
        ["is_opportunity", "opportunity_score"], ascending=[False, False]
    ).reset_index(drop=True)

    meta = {
        "base_year": base_year,
        "late_year": late_year,
        "years": ",".join(str(y) for y in years),
        "window_years": ",".join(str(y) for y in window),
        "growth_max_month": max_month,
        "growth_ytd_share": round(float(ytd_share), 4),
        "launchable_band": f"{int(band[0]):,}-{int(band[1]):,}",
        "corpus_base": corpus_base,
        "corpus_late": corpus_late,
        "corpus_base_ytd": corpus_base_ytd,
        "corpus_late_ytd": corpus_late_ytd,
        "corpus_cagr": round(float(corpus_cagr), 4),
        "fi_portfolio_share": round(fi_baseline_share, 5),
        "n_communities": int(len(out)),
        "n_opportunities": int(out["is_opportunity"].sum()),
        "n_large": int(out["is_large"].sum()),
        "n_growing": int(out["is_growing"].sum()),
        "n_whitespace": int((out["presence"] == "whitespace").sum()),
        "n_whitespace_opportunities": int(
            (out["is_opportunity"] & (out["presence"] == "whitespace")).sum()
        ),
    }
    log.info(
        "opportunities: %s of %s communities (%s large, %s growing) | "
        "%s are whitespace",
        f"{meta['n_opportunities']:,}",
        f"{meta['n_communities']:,}",
        f"{meta['n_large']:,}",
        f"{meta['n_growing']:,}",
        f"{meta['n_whitespace_opportunities']:,}",
    )
    return out, meta


def _attach_names(
    out: pd.DataFrame, labels: pd.DataFrame | None, topics: pd.DataFrame | None
) -> pd.DataFrame:
    """Name each community, with the L2 detail kept alongside as supporting text."""
    out = out.copy()
    out["community_label"] = ""
    out["unit_name"] = ""
    out["l1_roll_share"] = 0.0
    out["l2_topic"] = ""
    out["l2_topic_share"] = 0.0
    out["topic_list"] = ""
    out["topic_compound"] = ""
    if labels is not None and not labels.empty:
        lab = labels.drop_duplicates("community_id").set_index("community_id")
        out["community_label"] = (
            out["community_id"].map(lab["community_label"]).fillna("")
        )
    if topics is not None and not topics.empty:
        tp = topics.drop_duplicates("cluster_id").set_index("cluster_id")
        out["l2_topic"] = out["community_id"].map(tp["l2_name"]).fillna("")
        out["l2_topic_share"] = (
            out["community_id"].map(tp["l2_share"]).fillna(0.0)
        )
        for col in ("topic_list", "topic_compound", "unit_name"):
            if col in tp.columns:
                out[col] = out["community_id"].map(tp[col]).fillna("")
        if "l1_roll_share" in tp.columns:
            out["l1_roll_share"] = (
                out["community_id"].map(tp["l1_roll_share"]).fillna(0.0)
            )

    # The L1 rollup first: it is aggregated over the whole cluster, so it says
    # what the unit is. The compound of leading L2 terms only names a tenth of a
    # typical cluster, so it is a fallback for runs exported before the rollup
    # existed. Only unlabelled clusters end up as "Cluster N".
    name = out["unit_name"].astype(str).str.strip()
    name = name.where(name != "", out["topic_compound"].astype(str).str.strip())
    name = name.where(name != "", out["community_label"].astype(str).str.strip())
    out["name"] = name.where(
        name != "", "Cluster " + out["community_id"].astype(str)
    )
    out["name_source"] = "cluster_id"
    out.loc[out["community_label"].astype(str).str.strip() != "", "name_source"] = "l1"
    out.loc[out["topic_compound"].astype(str).str.strip() != "", "name_source"] = "l2_compound"
    out.loc[out["unit_name"].astype(str).str.strip() != "", "name_source"] = "l1_rollup"
    return out


def compute_market(
    run_timestamp: str,
    level: str | None = None,
    launchable_band: tuple[float, float] | None = None,
    min_3y: float | None = None,
) -> tuple[pd.DataFrame, dict]:
    """Market frame for one level, without writing. Shared with P0 and units."""
    from opportunities import bq as bqmod

    level = level or C.MARKET_LEVEL
    df_years = fetch_year_counts(run_timestamp, level)
    labels = bqmod.fetch_cluster_labels(run_timestamp, level)
    topics = bqmod.fetch_l2_topics(run_timestamp, level)
    out, meta = build_market_map(df_years, labels, topics, launchable_band, min_3y)
    from opportunities.world_market import fetch_community_fields

    fields = fetch_community_fields(run_timestamp, level)
    out = out.merge(fields, on="community_id", how="left")
    out["primary_world_field"] = out["primary_world_field"].fillna("")
    out["world_field_mix"] = out["world_field_mix"].fillna("")
    # A Leiden scope cannot manufacture an opportunity merely because its
    # allocated slice is large. Its independently measured parent world field
    # must first clear the market-only sieve.
    try:
        world = bqmod.read_table(C.WORLD_OPPORTUNITIES_PREFIX, run_timestamp)
    except Exception:
        from opportunities.world_market import build_world_opportunities

        world = build_world_opportunities(run_timestamp, write=True)
    qualify = world.drop_duplicates("field").set_index("field")
    out["world_field_is_opportunity"] = (
        out["primary_world_field"].map(qualify["is_opportunity"]).fillna(False).astype(bool)
    )
    out["world_field_action"] = (
        out["primary_world_field"].map(qualify["action"]).fillna("")
    )
    out["world_field_n_global_3y"] = (
        out["primary_world_field"].map(qualify["n_global_3y"])
    )
    out["world_field_cagr"] = out["primary_world_field"].map(qualify["cagr"])
    out["is_opportunity"] = (
        out["is_opportunity"].astype(bool) & out["world_field_is_opportunity"]
    )
    out.loc[~out["is_opportunity"], "opportunity_kind"] = ""
    meta["level"] = level
    meta["market_source"] = "AIRAK all-publisher level-1 fields"
    meta["n_field_qualified_communities"] = int(out["is_opportunity"].sum())
    meta["n_opportunities"] = int(out["is_opportunity"].sum())
    meta["n_whitespace_opportunities"] = int(
        (out["is_opportunity"] & out["presence"].eq("whitespace")).sum()
    )
    log.info(
        "field-qualified scopes: %s of %s (%s whitespace)",
        f"{meta['n_opportunities']:,}",
        f"{len(out):,}",
        f"{meta['n_whitespace_opportunities']:,}",
    )
    return out, meta


def run_market_map(
    run_timestamp: str, level: str | None = None, write: bool = True
) -> pd.DataFrame:
    from opportunities import bq as bqmod

    level = level or C.MARKET_LEVEL
    out, meta = compute_market(run_timestamp, level)
    if write:
        # Level in the table name so micro and meso runs can coexist.
        bqmod.write_table(out, f"market_opportunities_{level}", run_timestamp)
        bqmod.write_json_row(
            meta, f"market_opportunities_{level}_meta", run_timestamp
        )
    return out


def main() -> None:
    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s  %(message)s", datefmt="%H:%M:%S"
    )
    ap = argparse.ArgumentParser(
        description="Large-or-growing market opportunity map"
    )
    ap.add_argument("--run", default=C.DEFAULT_RUN)
    ap.add_argument(
        "--level", default=C.MARKET_LEVEL, choices=list(C.COMMUNITY_LEVELS)
    )
    ap.add_argument("--no-write", action="store_true")
    args = ap.parse_args()
    out = run_market_map(args.run, args.level, write=not args.no_write)
    top = out[out["is_opportunity"] & (out["presence"] == "whitespace")].head(25)
    cols = [
        "name",
        "n_global_3y",
        "cagr",
        "excess_cagr",
        "fi_share",
        "fi_share_vs_portfolio",
        "opportunity_kind",
        "opportunity_score",
    ]
    print("\n=== top whitespace opportunities ===")
    print(top[cols].to_string(index=False))


if __name__ == "__main__":
    main()
