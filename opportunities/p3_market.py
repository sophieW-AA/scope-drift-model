"""P3 — two-field market overlay from the JD opportunities table in BigQuery."""

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
    label: str, profiles: list[tuple[set[str], dict]], top_n: int = 2
) -> list[dict]:
    if not profiles:
        return []
    lab = T.token_profile([label], k=20)
    scored = []
    for prof, row in profiles:
        jac = T.jaccard(lab, prof)
        if jac <= 0:
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


def build_market(candidates: pd.DataFrame, home: pd.DataFrame, jd: pd.DataFrame) -> pd.DataFrame:
    h = home.set_index(["journal", "community_id"])
    profiles = jd_profiles(jd)
    rows = []
    for _, cand in candidates.iterrows():
        key = (cand["journal"], int(cand["community_id"]))
        matches = match_subfields(str(cand["community_label"]), profiles)
        f1 = matches[0] if matches else {}
        f2 = matches[1] if len(matches) > 1 and matches[1]["jaccard"] >= C.SECOND_FIELD_MIN else {}
        parent_owns = False
        if key in h.index:
            parent_owns = bool(h.loc[key, "parent_owns_gated"])
        mkt = f1.get("mkt_2025")
        cagr = f1.get("cagr")
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
                "field1": f1.get("subfield"),
                "field1_jaccard": f1.get("jaccard"),
                "field1_mkt_2025": mkt,
                "field1_cagr": cagr,
                "field1_funding": f1.get("funding"),
                "field1_tier": f1.get("tier"),
                "field1_pattern": f1.get("pattern"),
                "field1_fi_articles": f1.get("fi_articles"),
                "field1_fi_share": f1.get("fi_share"),
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
    jd = bqmod.fetch_jd_opportunities()
    market = build_market(candidates, home, jd)
    bqmod.write_table(market, "market", run_timestamp)
    return market
