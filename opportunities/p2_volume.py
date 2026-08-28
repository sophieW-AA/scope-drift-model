"""P2 — share of title, RT vs spontaneous channels, off-brand RT flags."""

from __future__ import annotations

import logging
import re

import pandas as pd

from . import config as C

log = logging.getLogger("opportunities.p2")
OFFBRAND_RE = re.compile(C.OFFBRAND_TITLE_RE, re.I)


def _norm_title(s: str) -> str:
    return re.sub(r"\s+", " ", str(s or "").strip().lower())


def attach_rt(papers: pd.DataFrame, rt: pd.DataFrame) -> pd.DataFrame:
    p = papers.copy()
    p["title_norm"] = p["title"].map(_norm_title)
    r = rt.copy()
    if "title_norm" not in r.columns:
        r["title_norm"] = r.get("article_title", pd.Series(dtype=str)).map(_norm_title)
    keep = [
        c
        for c in [
            "title_norm",
            "journal",
            "section",
            "section_id",
            "taxonomy_type",
            "research_topic_id",
            "research_topic_title",
        ]
        if c in r.columns
    ]
    r = r[keep].drop_duplicates(["journal", "title_norm"])
    merged = p.merge(r, on=["journal", "title_norm"], how="left")
    merged["in_rt"] = merged["research_topic_id"].notna()
    return merged


def build_volume(papers: pd.DataFrame, candidates: pd.DataFrame) -> pd.DataFrame:
    has_rt = "in_rt" in papers.columns
    papers = papers.copy()
    if has_rt:
        papers["in_rt"] = papers["in_rt"].fillna(False).astype(bool)
    else:
        papers["in_rt"] = False

    # Precompute every group once, instead of rescanning `papers` per candidate.
    journal_year = papers.groupby(["journal", "year"]).size()
    cjy = papers.groupby(["journal", "community_id", "year", "in_rt"]).size()
    cand_groups = {
        (j, int(c)): g
        for (j, c), g in papers.groupby(["journal", "community_id"])
    }

    def _share_cagr(journal: str, cid: int, rt_flag: bool, window: set[int]) -> float | None:
        try:
            by = cjy.loc[(journal, cid)]
        except KeyError:
            return None
        by = by[by.index.get_level_values("in_rt") == rt_flag]
        by = by.groupby(level="year").sum()
        by = by[by.index.isin(window)]
        if by.empty:
            return None
        try:
            jby = journal_year.loc[journal]
        except KeyError:
            return None
        years = sorted(set(by.index) & set(jby.index))
        if len(years) < 2:
            return None
        y0, y1 = years[0], years[-1]
        if jby[y0] == 0 or jby[y1] == 0:
            return None
        s0 = by[y0] / jby[y0]
        s1 = by[y1] / jby[y1]
        if s0 <= 0:
            return None
        k = max(y1 - y0, 1)
        return float((s1 / s0) ** (1 / k) - 1)

    rows = []
    for _, cand in candidates.iterrows():
        journal = cand["journal"]
        cid = int(cand["community_id"])
        late = int(cand["late_year"])
        window = {late, late - 1, late - 2}
        group = cand_groups.get((journal, cid))
        cdf = (
            group[group["year"].isin(window)]
            if group is not None
            else papers.iloc[0:0]
        )
        n = len(cdf)
        n_rt = int(cdf["in_rt"].sum()) if has_rt and n else None
        n_sp = (n - n_rt) if n_rt is not None else None

        cagr_sp = None
        cagr_rt = None
        if has_rt:
            cagr_sp = _share_cagr(journal, cid, False, window)
            cagr_rt = _share_cagr(journal, cid, True, window)

        offbrand = []
        if has_rt and n and "research_topic_title" in cdf.columns:
            sub = cdf[cdf["in_rt"]].copy()
            sub["_rt"] = sub["research_topic_title"].fillna("(untitled)")
            for title, g in sub.groupby("_rt"):
                oos = float(g["is_oos"].mean()) if "is_oos" in g else 0.0
                off_t = float(g["title"].fillna("").astype(str).map(lambda t: bool(OFFBRAND_RE.search(t))).mean())
                if len(g) >= 5 and (oos >= 0.45 or off_t >= 0.4):
                    offbrand.append(
                        {
                            "research_topic_title": str(title)[:180],
                            "n": int(len(g)),
                            "oos_pct": round(oos * 100, 1),
                        }
                    )

        journal_n_3y = int(cand["journal_n_3y"])
        share_3y = float(cand["share_3y"])
        section_scale = share_3y >= C.SECTION_SHARE
        if journal_n_3y >= C.LARGE_JOURNAL_3Y:
            section_scale = section_scale and (int(cand["n_3y"]) >= C.PAPER_FLOOR_SECTION)
        journal_scale = share_3y >= C.JOURNAL_SHARE
        if journal_n_3y >= C.VERY_LARGE_JOURNAL_3Y:
            journal_scale = journal_scale or int(cand["n_3y"]) >= C.PAPER_FLOOR_JOURNAL

        spont_rising = bool(cagr_sp is not None and cagr_sp >= C.SHARE_CAGR_SHIFT)
        persist_ok = int(cand["n_years"]) >= 3 or (int(cand["n_years"]) >= 2 and spont_rising)

        rows.append(
            {
                "journal": journal,
                "community_id": cid,
                "n_3y": int(cand["n_3y"]),
                "share_3y": share_3y,
                "n_rt": n_rt,
                "n_spontaneous": n_sp,
                "rt_share": None if n_rt is None or n == 0 else round(n_rt / n, 3),
                "share_cagr_spontaneous": None if cagr_sp is None else round(cagr_sp, 4),
                "share_cagr_rt": None if cagr_rt is None else round(cagr_rt, 4),
                "spontaneous_rising": spont_rising,
                "section_scale": section_scale,
                "journal_scale": journal_scale,
                "persist_ok": persist_ok,
                "n_offbrand_rts": len(offbrand),
                "offbrand_rts": "; ".join(
                    f"{x['research_topic_title']} (n={x['n']}, oos={x['oos_pct']}%)"
                    for x in offbrand[:8]
                ),
                "rt_join": has_rt,
            }
        )
    return pd.DataFrame(rows)


def run_p2(
    run_timestamp: str,
    papers: pd.DataFrame | None = None,
    candidates: pd.DataFrame | None = None,
) -> pd.DataFrame:
    from . import bq as bqmod

    if papers is None:
        papers = bqmod.read_table("papers", run_timestamp)
    if candidates is None:
        candidates = bqmod.read_table("candidates", run_timestamp)
    keys = candidates[["journal", "community_id"]].drop_duplicates()
    papers = papers.merge(keys, on=["journal", "community_id"])
    try:
        journals = sorted(papers["journal"].dropna().unique())
        years = papers["year"].dropna().astype(int)
        rt = bqmod.fetch_rt_section(journals, int(years.min()), int(years.max()))
        papers = attach_rt(papers, rt)
        log.info("P2: RT join on candidate papers (%s)", f"{len(papers):,}")
    except Exception as exc:
        log.warning("P2: RT join skipped (%s)", exc)
    volume = build_volume(papers, candidates)
    bqmod.write_table(volume, "volume", run_timestamp)
    return volume
