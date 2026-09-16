"""P3 — independent AIRAK market overlay for Leiden candidate scopes.

The complete world market attached in P0 is authoritative for size, growth and
qualification. The curated JD table remains optional context (funding/tier);
its 98 rows cannot define the opportunity universe.
"""

from __future__ import annotations

import logging

import pandas as pd

from . import config as C
from . import text as T

log = logging.getLogger("opportunities.p3")


def jd_profiles(jd: pd.DataFrame) -> list[tuple[set[str], dict]]:
    """Token profile per JD subfield, computed once for the whole run."""
    if jd is None or jd.empty:
        return []
    out = []
    for row in jd.to_dict(orient="records"):
        prof = T.token_profile(
            [str(row.get("subfield") or ""), str(row.get("field") or "")], k=20
        )
        out.append((prof, row))
    return out


def match_subfields(
    label: str,
    profiles: list[tuple[set[str], dict]],
    top_n: int = 2,
    min_jaccard: float | None = None,
) -> list[dict]:
    if not profiles:
        return []
    floor = C.FIELD_MATCH_MIN_JACCARD if min_jaccard is None else float(min_jaccard)
    lab = T.token_profile([label], k=20)
    scored = []
    for prof, row in profiles:
        jac = T.jaccard(lab, prof)
        if jac < floor:
            continue
        scored.append((jac, row))
    scored.sort(key=lambda x: -x[0])
    out = []
    for jac, row in scored[:top_n]:
        out.append(
            {
                "subfield": row["subfield"],
                "jaccard": round(float(jac), 3),
                "mkt_2025": row["mkt_2025"],
                "cagr": row["cagr"],
                "funding": row["funding"],
                "tier": row["tier"],
                "pattern": row["pattern"],
                "anchor_journal": row["anchor_journal"],
                "fi_articles": row.get("fi_articles"),
                "fi_share": row.get("fi_share"),
            }
        )
    return out


def build_market(
    candidates: pd.DataFrame,
    home: pd.DataFrame,
    jd: pd.DataFrame | None = None,
) -> pd.DataFrame:
    h = home.set_index(["journal", "community_id"])
    profiles = jd_profiles(jd) if jd is not None else []
    rows = []
    for _, cand in candidates.iterrows():
        key = (cand["journal"], int(cand["community_id"]))
        # Match on the L2 topic when one was resolved: the L1 community label is
        # reused across many clusters, so it matches whichever subfield happens
        # to share a token with it.
        match_on = str(
            cand.get("mkt_primary_world_field")
            or cand.get("topic_label")
            or cand["community_label"]
        )
        matches = match_subfields(match_on, profiles)
        f1 = matches[0] if matches else {}
        f2 = matches[1] if len(matches) > 1 and matches[1]["jaccard"] >= C.SECOND_FIELD_MIN else {}
        parent_owns = False
        if key in h.index:
            parent_owns = bool(h.loc[key, "parent_owns_gated"])
        # World figures come from all AIRAK publishers. They were allocated to
        # this Leiden scope in P0 without any Frontiers term in the opportunity
        # test. JD is enrichment only.
        mkt = cand.get("mkt_n_global_late")
        if pd.isna(mkt):
            mkt = (
                float(cand.get("mkt_n_global_3y") or 0) / C.WINDOW_YEARS
                if pd.notna(cand.get("mkt_n_global_3y"))
                else None
            )
        cagr = cand.get("mkt_cagr")
        market_gate = (
            mkt is not None
            and cagr is not None
            and mkt >= C.MARKET_MIN_ARTICLES
            and cagr >= C.MARKET_MIN_CAGR
        )
        rows.append(
            {
                "journal": cand["journal"],
                "community_id": int(cand["community_id"]),
                "matched_on": match_on,
                "market_source": "AIRAK all-publisher level-1 fields",
                "field1": cand.get("mkt_primary_world_field") or None,
                "field1_jaccard": None,
                "field1_mkt_2025": mkt,
                "field1_cagr": cagr,
                "field1_funding": f1.get("funding"),
                "field1_tier": f1.get("tier"),
                "field1_pattern": f1.get("pattern"),
                "field1_fi_articles": (
                    float(cand.get("mkt_n_fi_3y") or 0) / C.WINDOW_YEARS
                ),
                "field1_fi_share": cand.get("mkt_fi_share"),
                "field1_anchor": f1.get("anchor_journal"),
                "field2": f2.get("subfield"),
                "field2_jaccard": f2.get("jaccard"),
                "market_journal_gate": market_gate,
                "parent_owns_blocks_journal": parent_owns,
            }
        )
    return pd.DataFrame(rows)


def run_p3(
    run_timestamp: str,
    candidates: pd.DataFrame | None = None,
    home: pd.DataFrame | None = None,
) -> pd.DataFrame:
    from . import bq as bqmod

    if candidates is None:
        candidates = bqmod.read_table("candidates", run_timestamp)
    if home is None:
        home = bqmod.read_table("home", run_timestamp)
    # Optional contextual enrichment only. The run remains complete when a
    # field has no row in the curated JD table.
    jd = bqmod.fetch_jd_opportunities()
    market = build_market(candidates, home, jd)
    bqmod.write_table(market, "market", run_timestamp)
    return market
