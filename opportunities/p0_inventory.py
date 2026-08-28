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
    if journal:
        papers = papers[papers["journal"] == journal].copy()
        if len(candidates):
            candidates = candidates[candidates["journal"] == journal].copy()
        meta["journal_filter"] = journal
        meta["n_papers"] = int(len(papers))
        meta["n_candidates"] = int(len(candidates))
        meta["n_journals"] = int(papers["journal"].nunique()) if len(papers) else 0
    meta["community_level"] = level
    meta["drilldown_level"] = drilldown
    meta["n_labelled_papers"] = n_labelled
    meta["paper_source"] = "bigquery"

    bqmod.write_table(papers, "papers", run_timestamp)
    bqmod.write_table(candidates, "candidates", run_timestamp)
    journals = pd.DataFrame(meta.get("journals") or [])
    bqmod.write_table(journals, "journal_meta", run_timestamp)
    summary = {k: v for k, v in meta.items() if k != "journals"}
    bqmod.write_json_row(summary, "p0_meta", run_timestamp)
    return {"papers": papers, "candidates": candidates, "meta": meta}
