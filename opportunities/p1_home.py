"""P1 — topic/title home finder + gated parent-owns (not macro ID force-Redirect)."""

from __future__ import annotations

import logging
import re

import pandas as pd

from . import config as C
from . import text as T

log = logging.getLogger("opportunities.p1")
METHODS_RE = re.compile(C.METHODS_SHARED_RE, re.I)
OFFBRAND_RE = re.compile(C.OFFBRAND_TITLE_RE, re.I)


def is_methods_shared(label: str) -> bool:
    return bool(METHODS_RE.search(label or ""))


def gate_string(journal: str, label: str, methods_shared: bool) -> str:
    if not methods_shared:
        return ""
    bare = re.sub(r"(?i)^frontiers\s+in\s+", "", journal).strip()
    domain = T.journal_domain_tokens(journal)
    if domain:
        bits = ", ".join(sorted(domain)[:6])
        return f"must involve {bare.lower()} substance ({bits}) — not methods-only"
    return f"must involve {bare} as the application domain, not methods-only"


def _profiles(papers: pd.DataFrame) -> dict[tuple[str, int], set[str]]:
    out = {}
    for (journal, cid), g in papers.groupby(["journal", "community_id"]):
        titles = g["title"].fillna("").astype(str).tolist()
        out[(journal, int(cid))] = T.token_profile(titles)
    return out


def _baseline_profile(papers: pd.DataFrame, journal: str, exclude_cid: int | None) -> set[str]:
    sub = papers[
        (papers["journal"] == journal) & (papers["in_baseline_primary"].astype(bool))
    ]
    if exclude_cid is not None:
        sub = sub[sub["community_id"] != exclude_cid]
    return T.token_profile(sub["title"].fillna("").astype(str).tolist())


def build_home(papers: pd.DataFrame, candidates: pd.DataFrame) -> pd.DataFrame:
    journals = sorted(papers["journal"].dropna().unique())
    sample = papers.copy()
    sample["_t"] = sample["title"].fillna("").astype(str)
    # Cap titles per community so 100k+ paper journals stay tractable
    sample = (
        sample.groupby(["journal", "community_id"], group_keys=False)
        .head(250)
    )
    # One pass instead of a boolean mask over the whole frame per candidate
    titles_by_key = {
        (j, int(c)): g["_t"].tolist()
        for (j, c), g in sample.groupby(["journal", "community_id"])
    }
    profiles = {k: T.token_profile(v) for k, v in titles_by_key.items()}

    base = papers[papers["in_baseline_primary"].astype(bool)].copy()
    base["_t"] = base["title"].fillna("").astype(str)
    base = base.groupby("journal", group_keys=False).head(400)
    baseline_prof = {
        j: T.token_profile(g["_t"].tolist())
        for j, g in base.groupby("journal")
    }

    j_n = papers.groupby("journal").size().to_dict()
    jc_n = papers.groupby(["journal", "community_id"]).size().to_dict()
    domain_by_journal = {j: T.journal_domain_tokens(j) for j in journals}

    hit_cache: dict[tuple[str, int], tuple[float, float]] = {}
    rows = []

    for _, cand in candidates.iterrows():
        journal = cand["journal"]
        cid = int(cand["community_id"])
        label = str(cand["community_label"])
        methods = is_methods_shared(label)
        key = (journal, cid)
        if key not in hit_cache:
            titles = titles_by_key.get(key, [])
            domain = domain_by_journal.get(journal) or T.journal_domain_tokens(journal)
            hit_cache[key] = (
                T.domain_hit_rate(titles, domain),
                (
                    sum(bool(OFFBRAND_RE.search(t)) for t in titles) / len(titles)
                    if titles
                    else 0.0
                ),
            )
        hit, offbrand_share = hit_cache[key]

        parent_j = T.jaccard(profiles.get(key, set()), baseline_prof.get(journal, set()))

        homes = []
        for k in journals:
            if k == journal:
                continue
            jac = T.jaccard(profiles.get(key, set()), baseline_prof.get(k, set()))
            kn = j_n.get(k) or 1
            macro_share = (jc_n.get((k, cid)) or 0) / kn
            homes.append((k, jac, macro_share))
        homes.sort(key=lambda x: -x[1])
        best = homes[0] if homes else ("", 0.0, 0.0)

        on_brand = (not methods and bool(cand["in_baseline_primary"])) or (
            methods and hit >= C.DOMAIN_HIT_ON_BRAND
        )
        if offbrand_share >= 0.35:
            on_brand = False

        home_elsewhere = best[1] >= C.TOPIC_JACCARD_HOME
        parent_owns = (not home_elsewhere) and (
            bool(cand["in_baseline_primary"]) or parent_j >= C.PARENT_JACCARD_OWN
        )
        if methods and not on_brand:
            parent_owns = False

        rows.append(
            {
                "journal": journal,
                "community_id": cid,
                "community_label": label,
                "methods_shared": methods,
                "domain_hit_rate": round(hit, 3),
                "offbrand_title_share": round(offbrand_share, 3),
                "parent_jaccard": round(parent_j, 3),
                "on_brand_gated": on_brand,
                "parent_owns_gated": parent_owns,
                "home_elsewhere": home_elsewhere,
                "best_home_journal": best[0],
                "best_home_jaccard": round(float(best[1]), 3),
                "macro_id_share_in_best_home": round(float(best[2]), 3),
                "gate_string": gate_string(journal, label, methods) if methods else "",
                "home_method": "title_token_jaccard",
            }
        )
    return pd.DataFrame(rows)


def run_p1(
    run_timestamp: str,
    papers: pd.DataFrame | None = None,
    candidates: pd.DataFrame | None = None,
) -> pd.DataFrame:
    from . import bq as bqmod

    if papers is None:
        papers = bqmod.read_table("papers", run_timestamp)
    if candidates is None:
        candidates = bqmod.read_table("candidates", run_timestamp)
    home = build_home(papers, candidates)
    try:
        sections = bqmod.fetch_existing_sections()
        home = _attach_existing_sections(home, sections)
        log.info("P1: matched existing specialty sections")
    except Exception as exc:
        log.warning("P1: section inventory skipped (%s)", exc)
        home["existing_section"] = ""
        home["existing_section_journal"] = ""
        home["existing_section_jaccard"] = 0.0
    bqmod.write_table(home, "home", run_timestamp)
    return home


def _attach_existing_sections(home: pd.DataFrame, sections: pd.DataFrame) -> pd.DataFrame:
    out = home.copy()
    out["existing_section"] = ""
    out["existing_section_journal"] = ""
    out["existing_section_jaccard"] = 0.0
    if sections is None or sections.empty:
        return out
    sec_profiles = [
        (str(j), str(s), T.token_profile([str(s)], k=20))
        for j, s in zip(sections["journal"], sections["section"])
    ]
    label_best: dict[str, tuple[float, str, str]] = {}
    for lab in out["community_label"].dropna().unique():
        prof = T.token_profile([str(lab)], k=20)
        best, best_j, best_s = 0.0, "", ""
        for jn, sec, sprof in sec_profiles:
            jac = T.jaccard(prof, sprof)
            if jac > best:
                best, best_j, best_s = jac, jn, sec
        label_best[str(lab)] = (best, best_j, best_s)

    matched = out["community_label"].astype(str).map(label_best)
    out["existing_section_jaccard"] = [
        round(m[0], 3) if m and m[0] >= 0.45 else 0.0 for m in matched
    ]
    out["existing_section"] = [m[2] if m and m[0] >= 0.45 else "" for m in matched]
    out["existing_section_journal"] = [
        m[1] if m and m[0] >= 0.45 else "" for m in matched
    ]
    return out
