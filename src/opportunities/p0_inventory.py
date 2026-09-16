"""P0 — freeze papers and candidate communities (mix-shift + non-primary).

Inputs are BigQuery only: classification_raw / pub_metadata_raw for papers,
taxonomy_labelling for community labels, and an optional paper_scope table for
scope flags.
"""

from __future__ import annotations

import logging

import pandas as pd

from . import config as C

log = logging.getLogger("opportunities.p0")


def resolve_years(papers: pd.DataFrame, baseline_year: int) -> tuple[int, int, list[int]]:
    """Baseline year, late year and the 3y window, derived from the data.

    The configured baseline is used only when the run actually covers it. The
    newest year is dropped when it looks incomplete, so share and CAGR
    endpoints are not measured against a part-year.
    """
    years = sorted(int(y) for y in papers["year"].dropna().unique())
    if not years:
        return baseline_year, baseline_year, []

    late_year = years[-1]
    if C.DROP_PARTIAL_LATE_YEAR and len(years) >= 2:
        by_year = papers["year"].value_counts()
        n_late = int(by_year.get(late_year, 0))
        prior = [int(by_year.get(y, 0)) for y in years[:-1]]
        typical = sorted(prior)[len(prior) // 2] if prior else 0
        if typical and n_late < typical * C.PARTIAL_YEAR_RATIO:
            log.info(
                "dropping %s as a partial year (%s papers vs typical %s)",
                late_year,
                f"{n_late:,}",
                f"{typical:,}",
            )
            years = years[:-1]
            late_year = years[-1]

    used_baseline = baseline_year if baseline_year in years else years[0]
    if used_baseline != baseline_year:
        log.info(
            "baseline %s absent from this run (%s-%s); using %s",
            baseline_year,
            years[0],
            years[-1],
            used_baseline,
        )
    window = [y for y in years if y >= late_year - 2]
    return used_baseline, late_year, window


def coverage_primary(sub: pd.DataFrame, coverage: float = C.PRIMARY_COVERAGE) -> set[int]:
    if sub.empty:
        return set()
    counts = sub["community_id"].value_counts()
    primary: set[int] = set()
    cum = 0
    total = int(counts.sum()) or 1
    for cid, n in counts.items():
        primary.add(int(cid))
        cum += int(n)
        if cum >= total * coverage:
            break
    return primary


def _share_cagr(share_base: float, share_late: float, k: int) -> float | None:
    if k <= 0 or share_base is None or share_late is None:
        return None
    if share_base <= 0:
        return None
    return float((share_late / share_base) ** (1 / k) - 1)


def build_inventory(
    papers: pd.DataFrame,
    baseline_year: int = C.BASELINE_YEAR,
) -> tuple[pd.DataFrame, pd.DataFrame, dict]:
    papers = papers.dropna(subset=["journal", "community_id", "year"]).copy()
    papers["year"] = papers["year"].astype(int)
    papers["community_id"] = papers["community_id"].astype(int)
    papers["in_baseline_primary"] = False
    papers["in_current_primary"] = False

    run_baseline, late_year, window_years = resolve_years(papers, baseline_year)
    if window_years:
        # Never score against years excluded as partial
        papers = papers[papers["year"] <= late_year].copy()

    meta_rows = []
    cand_rows = []

    for journal, jdf in papers.groupby("journal"):
        base = jdf[jdf["year"] == run_baseline]
        if len(base) < C.MIN_PAPERS_YEAR:
            first = sorted(jdf["year"].unique())[0]
            base = jdf[jdf["year"] == first]
            used_baseline = int(first)
        else:
            used_baseline = run_baseline

        baseline_primary = coverage_primary(base)
        current_primary = coverage_primary(jdf)
        n_3y = jdf[jdf["year"].isin(window_years)]
        journal_n_3y = len(n_3y)
        journal_n_base = len(base)

        meta_rows.append(
            {
                "journal": journal,
                "baseline_year": used_baseline,
                "late_year": late_year,
                "n_papers": len(jdf),
                "n_3y": journal_n_3y,
                "baseline_primary": ",".join(str(i) for i in sorted(baseline_primary)),
                "current_primary": ",".join(str(i) for i in sorted(current_primary)),
            }
        )

        for cid, cdf in jdf.groupby("community_id"):
            cid = int(cid)
            label = str(cdf["community_label"].iloc[0])
            c3 = cdf[cdf["year"].isin(window_years)]
            n3 = len(c3)
            if n3 < C.MIN_COMMUNITY_PAPERS and cid not in baseline_primary:
                continue

            n_base = int((cdf["year"] == used_baseline).sum())
            n_late = int((cdf["year"] == late_year).sum())
            n_journal_late = int((jdf["year"] == late_year).sum()) or 1
            share_base = (n_base / journal_n_base * 100) if journal_n_base else 0.0
            share_late = n_late / n_journal_late * 100
            share_3y = (n3 / journal_n_3y) if journal_n_3y else 0.0
            k = max(late_year - used_baseline, 1)
            cagr = _share_cagr(
                share_base / 100.0 if share_base else 0.0,
                share_late / 100.0,
                k,
            )
            years_present = sorted(int(y) for y in cdf["year"].dropna().unique())
            in_base = cid in baseline_primary
            in_cur = cid in current_primary
            oos_pct = float(c3["is_oos"].mean() * 100) if n3 else 0.0
            pp_delta = share_late - share_base
            mix = in_base and (
                abs(pp_delta) >= C.SHARE_PP_SHIFT
                or (cagr is not None and abs(cagr) >= C.SHARE_CAGR_SHIFT)
            )
            if in_base:
                ctype = "mix_shift" if mix else "stable_core"
            else:
                ctype = "non_primary"

            if ctype == "stable_core" and n3 < C.MIN_COMMUNITY_PAPERS:
                continue
            if ctype == "non_primary" and n3 < C.MIN_COMMUNITY_PAPERS:
                continue

            cand_rows.append(
                {
                    "journal": journal,
                    "community_id": cid,
                    "community_label": label,
                    "candidate_type": ctype,
                    "in_baseline_primary": in_base,
                    "in_current_primary": in_cur,
                    "n_3y": n3,
                    "n_baseline": n_base,
                    "n_late": n_late,
                    "journal_n_3y": journal_n_3y,
                    "share_3y": round(share_3y, 4),
                    "share_baseline_pct": round(share_base, 2),
                    "share_late_pct": round(share_late, 2),
                    "share_pp_delta": round(pp_delta, 2),
                    "share_cagr": None if cagr is None else round(float(cagr), 4),
                    "n_years": len(years_present),
                    "years_present": ",".join(str(y) for y in years_present),
                    "oos_pct": round(oos_pct, 1),
                    "baseline_year": used_baseline,
                    "late_year": late_year,
                }
            )

        papers.loc[jdf.index, "in_baseline_primary"] = papers.loc[
            jdf.index, "community_id"
        ].isin(baseline_primary)
        papers.loc[jdf.index, "in_current_primary"] = papers.loc[
            jdf.index, "community_id"
        ].isin(current_primary)

    candidates = pd.DataFrame(cand_rows)
    journal_meta = pd.DataFrame(meta_rows)
    return papers, candidates, {
        "baseline_year": run_baseline,
        "baseline_year_configured": baseline_year,
        "late_year": late_year,
        "window_years": ",".join(str(y) for y in window_years),
        "n_journals": int(papers["journal"].nunique()),
        "n_papers": int(len(papers)),
        "n_candidates": int(len(candidates)),
        "journals": journal_meta.to_dict(orient="records"),
    }


def attach_labels(papers: pd.DataFrame, labels: pd.DataFrame) -> pd.DataFrame:
    """Vectorised label join; unlabelled communities keep a `Cluster N` placeholder."""
    out = papers.copy()
    if labels is None or labels.empty:
        out["community_label"] = "Cluster " + out["community_id"].astype(str)
        out["labelled"] = False
        return out
    lookup = labels.set_index("community_id")["community_label"]
    mapped = out["community_id"].map(lookup)
    out["labelled"] = mapped.notna()
    out["community_label"] = mapped.fillna(
        "Cluster " + out["community_id"].astype(str)
    )
    return out


def attach_l2_topics(papers: pd.DataFrame, topics: pd.DataFrame) -> pd.DataFrame:
    """Join the drilldown cluster's leading L2 topic onto each paper.

    The community label is an L1 term shared by many clusters, so the topic is
    taken from the finer `drilldown_id`. Papers in a drilldown cluster with no
    dominant topic keep an empty topic and fall back to the community label.
    """
    out = papers.copy()
    for col, default in (("l2_key", ""), ("l2_name", ""), ("l2_share", 0.0)):
        out[col] = default
    if topics is None or topics.empty or "drilldown_id" not in out.columns:
        if topics is None or topics.empty:
            log.warning("no gated L2 topics — candidates keep their L1 labels")
        return out

    lookup = topics.drop_duplicates("cluster_id").set_index("cluster_id")
    drill = pd.to_numeric(out["drilldown_id"], errors="coerce")
    out["l2_key"] = drill.map(lookup["l2_key"]).fillna("")
    out["l2_name"] = drill.map(lookup["l2_name"]).fillna("")
    out["l2_share"] = drill.map(lookup["l2_share"]).fillna(0.0)
    n_topic = int((out["l2_name"].astype(str).str.strip() != "").sum())
    log.info(
        "L2 topics attached to %s / %s papers (%.1f%%), %s distinct topics",
        f"{n_topic:,}",
        f"{len(out):,}",
        100.0 * n_topic / max(len(out), 1),
        out.loc[out["l2_name"] != "", "l2_name"].nunique(),
    )
    return out


def build_topic_inventory(
    papers: pd.DataFrame, window_years: list[int]
) -> pd.DataFrame:
    """One row per (journal, community, L2 topic) with its 3y Frontiers volume.

    This is the launch unit: a community answers "which section", a topic
    answers "which journal".
    """
    if "l2_name" not in papers.columns:
        return pd.DataFrame()
    win = papers[
        papers["year"].isin(window_years) & (papers["l2_name"].astype(str) != "")
    ]
    if win.empty:
        log.warning("no in-window papers carry an L2 topic")
        return pd.DataFrame()

    journal_n_3y = win.groupby("journal")["int_id"].count()
    comm_n_3y = win.groupby(["journal", "community_id"])["int_id"].count()

    rows = (
        win.groupby(["journal", "community_id", "l2_key", "l2_name"])
        .agg(
            n_3y=("int_id", "count"),
            l2_share=("l2_share", "max"),
            oos_pct=("is_oos", "mean"),
            n_late=("year", lambda s: int((s == max(window_years)).sum())),
        )
        .reset_index()
    )
    rows = rows[rows["n_3y"] >= C.TOPIC_MIN_PAPERS].copy()
    if rows.empty:
        log.warning("no (journal, community, topic) row clears %s papers", C.TOPIC_MIN_PAPERS)
        return rows

    keys = list(zip(rows["journal"], rows["community_id"]))
    rows["community_n_3y"] = [int(comm_n_3y.get(k, 0)) for k in keys]
    rows["journal_n_3y"] = rows["journal"].map(journal_n_3y).fillna(0).astype(int)
    rows["share_of_community"] = (
        rows["n_3y"] / rows["community_n_3y"].where(rows["community_n_3y"] > 0, 1)
    ).round(4)
    rows["share_of_journal"] = (
        rows["n_3y"] / rows["journal_n_3y"].where(rows["journal_n_3y"] > 0, 1)
    ).round(4)
    rows["oos_pct"] = (rows["oos_pct"] * 100).round(1)
    rows = rows.sort_values(
        ["journal", "community_id", "n_3y", "l2_key"],
        ascending=[True, True, False, True],
    )
    log.info(
        "topic inventory: %s (journal, community, topic) rows | %s journals | "
        "%s distinct topics",
        f"{len(rows):,}",
        rows["journal"].nunique(),
        rows["l2_name"].nunique(),
    )
    return rows


MARKET_COLS = (
    "n_global_3y",
    "n_global_late",
    "n_fi_3y",
    "fi_share",
    "fi_share_vs_portfolio",
    "cagr",
    "excess_cagr",
    "is_large",
    "is_growing",
    "is_opportunity",
    "is_launchable_size",
    "opportunity_kind",
    "presence",
    "primary_world_field",
    "primary_world_field_share",
    "world_field_mix",
    "world_field_is_opportunity",
    "world_field_action",
    "world_field_n_global_3y",
    "world_field_cagr",
)


def attach_market(candidates: pd.DataFrame, market: pd.DataFrame) -> pd.DataFrame:
    """Join each candidate's community to its global market position.

    Frontiers paper counts cannot answer whether we already publish something:
    200 papers in a 50,000-paper field is thin and 30 in a 400-paper field is
    not. These columns carry the global denominator so P4 can stop inferring
    presence from Frontiers volume alone.
    """
    out = candidates.copy()
    for col in MARKET_COLS:
        out[f"mkt_{col}"] = pd.NA
    if out.empty or market is None or market.empty:
        log.warning("no market frame — P4 will fall back to Frontiers-only presence")
        return out

    src = market.drop_duplicates("community_id").set_index("community_id")
    cid = out["community_id"]
    for col in MARKET_COLS:
        if col in src.columns:
            out[f"mkt_{col}"] = cid.map(src[col]).to_numpy()
    for col in (
        "is_large",
        "is_growing",
        "is_opportunity",
        "is_launchable_size",
        "world_field_is_opportunity",
    ):
        out[f"mkt_{col}"] = (
            out[f"mkt_{col}"].astype(object).where(out[f"mkt_{col}"].notna(), False)
        ).astype(bool)
    for col in (
        "presence",
        "opportunity_kind",
        "primary_world_field",
        "world_field_mix",
        "world_field_action",
    ):
        out[f"mkt_{col}"] = out[f"mkt_{col}"].astype(object).fillna("")
    matched = int(out["mkt_n_global_3y"].notna().sum())
    log.info(
        "market position joined to %s / %s candidates (%s in a large or "
        "growing community)",
        f"{matched:,}",
        f"{len(out):,}",
        int(out["mkt_is_opportunity"].sum()),
    )
    return out


def attach_topic_label(
    candidates: pd.DataFrame,
    topic_rows: pd.DataFrame,
    community_topics: pd.DataFrame | None = None,
) -> pd.DataFrame:
    """Name each candidate as specifically as the evidence allows.

    Preference order: the largest gated L2 topic the journal actually publishes
    in this community — journal-specific and backed by that journal's own papers
    — then the community's L1 rollup, then its compound L2 label for runs
    exported before the rollup existed, then the L1 community label.

    The rollup outranks the compound because the compound names a median tenth
    of a cluster and its ordering turns on a few articles, so it reads far more
    precisely than the counts behind it justify.
    """
    out = candidates.copy()
    out["l2_key"] = ""
    out["l2_topic"] = ""
    out["l2_topic_n_3y"] = 0
    out["l2_topic_share"] = 0.0
    out["topic_compound"] = ""
    out["unit_name"] = ""
    out["topic_label"] = out.get("community_label", "")
    out["topic_label_source"] = "l1"
    if out.empty:
        return out

    if topic_rows is not None and not topic_rows.empty:
        lead = (
            topic_rows.sort_values(["n_3y", "l2_key"], ascending=[False, True])
            .drop_duplicates(["journal", "community_id"])
            .set_index(["journal", "community_id"])
        )
        idx = pd.MultiIndex.from_arrays([out["journal"], out["community_id"]])
        for col, src, default in (
            ("l2_key", "l2_key", ""),
            ("l2_topic", "l2_name", ""),
            ("l2_topic_n_3y", "n_3y", 0),
            ("l2_topic_share", "share_of_community", 0.0),
        ):
            out[col] = pd.Series(idx.map(lead[src]).to_numpy(), index=out.index).fillna(
                default
            )

    if community_topics is not None and not community_topics.empty:
        ct = community_topics.drop_duplicates("cluster_id").set_index("cluster_id")
        for col in ("topic_compound", "unit_name"):
            if col in ct.columns:
                out[col] = out["community_id"].map(ct[col]).fillna("")

    compound = out["topic_compound"].astype(str).str.strip()
    rollup = out["unit_name"].astype(str).str.strip()
    named = out["l2_topic"].astype(str).str.strip() != ""
    out.loc[compound != "", "topic_label"] = compound[compound != ""]
    out.loc[compound != "", "topic_label_source"] = "l2_compound"
    out.loc[rollup != "", "topic_label"] = rollup[rollup != ""]
    out.loc[rollup != "", "topic_label_source"] = "l1_rollup"
    out.loc[named, "topic_label"] = out.loc[named, "l2_topic"]
    out.loc[named, "topic_label_source"] = "l2_topic"
    log.info(
        "topic label: %s from a gated L2 topic, %s L1 rollup, %s compound, "
        "%s L1 fallback",
        int(named.sum()),
        int((~named & (rollup != "")).sum()),
        int((~named & (rollup == "") & (compound != "")).sum()),
        int((~named & (rollup == "") & (compound == "")).sum()),
    )
    return out


def attach_scope(papers: pd.DataFrame, scope: pd.DataFrame) -> pd.DataFrame:
    """Merge per-paper scope flags; anything not covered is treated as in-scope."""
    out = papers
    if scope is not None and not scope.empty:
        keys = ["int_id", "journal"]
        extra = scope[keys + ["scope_code", "is_oos", "is_borderline"]].drop_duplicates(keys)
        out = out.merge(extra, on=keys, how="left")
    for col, default in (("is_oos", False), ("is_borderline", False), ("scope_code", 2)):
        if col not in out.columns:
            out[col] = default
        else:
            out[col] = out[col].fillna(default)
    out["is_oos"] = out["is_oos"].astype(bool)
    out["is_borderline"] = out["is_borderline"].astype(bool)
    out["scope_code"] = out["scope_code"].astype(int)
    return out


def run_p0(
    run_timestamp: str,
    journal: str | None = None,
    level: str | None = None,
    drilldown: str | None = None,
) -> dict:
    from . import bq as bqmod

    level = level or C.COMMUNITY_LEVEL
    drilldown = drilldown or C.DRILLDOWN_LEVEL

    papers = bqmod.fetch_frontiers_run_papers(run_timestamp, level, drilldown)
    if papers.empty:
        raise RuntimeError(
            f"No Frontiers papers found for run {run_timestamp} — check that "
            f"classification_raw_{run_timestamp} and pub_metadata_raw_{run_timestamp} exist."
        )

    labels = bqmod.fetch_cluster_labels(run_timestamp, level)
    papers = attach_labels(papers, labels)
    papers = attach_scope(papers, bqmod.fetch_paper_scope(run_timestamp))
    papers = attach_l2_topics(
        papers, bqmod.fetch_l2_topics(run_timestamp, drilldown)
    )

    n_labelled = int(papers["labelled"].sum())
    log.info(
        "labels cover %s / %s papers (%.1f%%) and %s / %s communities",
        f"{n_labelled:,}",
        f"{len(papers):,}",
        100.0 * n_labelled / max(len(papers), 1),
        papers.loc[papers["labelled"], "community_id"].nunique(),
        papers["community_id"].nunique(),
    )

    papers, candidates, meta = build_inventory(papers)
    window_years = [int(y) for y in str(meta.get("window_years") or "").split(",") if y]
    topic_rows = build_topic_inventory(papers, window_years)
    candidates = attach_topic_label(
        candidates, topic_rows, bqmod.fetch_l2_topics(run_timestamp, level)
    )

    from . import market_map

    try:
        market, market_meta = market_map.compute_market(run_timestamp, level)
        candidates = attach_market(candidates, market)
        meta["fi_portfolio_share"] = market_meta.get("fi_portfolio_share")
        meta["corpus_cagr"] = market_meta.get("corpus_cagr")
    except Exception as exc:
        log.warning("market position unavailable (%s)", exc)
        candidates = attach_market(candidates, pd.DataFrame())
    if journal:
        papers = papers[papers["journal"] == journal].copy()
        if len(candidates):
            candidates = candidates[candidates["journal"] == journal].copy()
        if len(topic_rows):
            topic_rows = topic_rows[topic_rows["journal"] == journal].copy()
        meta["journal_filter"] = journal
        meta["n_papers"] = int(len(papers))
        meta["n_candidates"] = int(len(candidates))
        meta["n_journals"] = int(papers["journal"].nunique()) if len(papers) else 0
    meta["community_level"] = level
    meta["drilldown_level"] = drilldown
    meta["n_labelled_papers"] = n_labelled
    meta["paper_source"] = "bigquery"
    meta["n_topic_rows"] = int(len(topic_rows))
    meta["n_distinct_topics"] = (
        int(topic_rows["l2_name"].nunique()) if len(topic_rows) else 0
    )

    bqmod.write_table(papers, "papers", run_timestamp)
    bqmod.write_table(candidates, "candidates", run_timestamp)
    bqmod.write_table(topic_rows, "topics", run_timestamp)
    journals = pd.DataFrame(meta.get("journals") or [])
    bqmod.write_table(journals, "journal_meta", run_timestamp)
    summary = {k: v for k, v in meta.items() if k != "journals"}
    bqmod.write_json_row(summary, "p0_meta", run_timestamp)
    return {
        "papers": papers,
        "candidates": candidates,
        "topics": topic_rows,
        "meta": meta,
    }
