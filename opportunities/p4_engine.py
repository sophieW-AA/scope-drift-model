"""P4 — six-way call, 0–12 score, uniqueness pass."""

from __future__ import annotations

from datetime import datetime, timezone

import pandas as pd

from . import config as C

LAUNCH = C.LAUNCH_CALLS


def _fi_share(mkt) -> float | None:
    share = mkt.get("field1_fi_share")
    if pd.notna(share) if share is not None else False:
        return float(share)
    fi = mkt.get("field1_fi_articles")
    mkt_n = mkt.get("field1_mkt_2025")
    if pd.notna(fi) and pd.notna(mkt_n) and float(mkt_n) > 0:
        return float(fi) / float(mkt_n)
    return None


def classify_presence(cand, home, vol, mkt, call: str) -> tuple[str, str]:
    """already_publish = Frontiers already has this demand; whitespace = thin FI vs market."""
    n3 = int(cand.get("n_3y") or 0)
    inside = bool(cand.get("in_baseline_primary"))
    home_else = bool(home.get("home_elsewhere"))
    section_scale = bool(vol.get("section_scale"))
    journal_scale = bool(vol.get("journal_scale"))
    fi_share = _fi_share(mkt)
    pattern = str(mkt.get("field1_pattern") or "")
    market_gate = bool(mkt.get("market_journal_gate"))
    jd_gap = any(p in pattern for p in C.WHITESPACE_JD_PATTERNS)
    thin_fi = fi_share is not None and fi_share < C.FI_SHARE_WHITESPACE
    existing_sec = (
        bool(home.get("existing_section"))
        and float(home.get("existing_section_jaccard") or 0) >= 0.45
    )

    if call in {"expand_rename", "redirect_crosslist", "gate_intake"}:
        return "already_publish", "Frontiers already publishes this community"
    if inside or home_else or existing_sec or section_scale or journal_scale:
        return "already_publish", "material Frontiers volume or a better home already exists"
    if n3 >= C.PAPER_FLOOR_SECTION:
        return "already_publish", f"{n3} papers in 3y at this title"
    if n3 < C.PAPER_FLOOR_SECTION and (
        thin_fi or (market_gate and fi_share is None)
    ):
        why = []
        if thin_fi:
            why.append(f"FI share {fi_share:.1%} of OpenAlex subfield")
        if jd_gap:
            why.append(pattern.strip() or "JD gap pattern")
        if not why:
            why.append("market gate with little mapped Frontiers volume")
        return "whitespace", "; ".join(why)
    if n3 >= C.MIN_COMMUNITY_PAPERS:
        return "already_publish", "community present in the Frontiers citation network"
    if market_gate and (thin_fi or fi_share is None):
        return "whitespace", "market without much Frontiers volume"
    return "already_publish", "seeded from Frontiers papers"


def _internal_score(cand: pd.Series, vol: pd.Series) -> int:
    pts = 0
    share = float(cand["share_3y"])
    n3 = int(cand["n_3y"])
    jn = int(cand["journal_n_3y"])
    if share >= C.JOURNAL_SHARE or (
        n3 >= C.PAPER_FLOOR_JOURNAL and jn >= C.VERY_LARGE_JOURNAL_3Y
    ):
        pts += 2
    elif share >= C.SECTION_SHARE or (
        n3 >= C.PAPER_FLOOR_SECTION and jn >= C.LARGE_JOURNAL_3Y
    ):
        pts += 1
    cagr = cand.get("share_cagr")
    if pd.notna(cagr) and abs(float(cagr)) >= C.SHARE_CAGR_SHIFT:
        pts += 1
    elif abs(float(cand.get("share_pp_delta") or 0)) >= C.SHARE_PP_SHIFT:
        pts += 1
    if bool(vol.get("persist_ok")):
        pts += 1
    return min(pts, 4)


def _home_score(home: pd.Series) -> int:
    pts = 0
    if not bool(home.get("home_elsewhere")):
        pts += 2
    if not bool(home.get("parent_owns_gated")):
        pts += 1
    if not home.get("gate_string"):
        pts += 1
    return min(pts, 4)


def _market_score(mkt: pd.Series) -> int:
    pts = 0
    n = mkt.get("field1_mkt_2025")
    cagr = mkt.get("field1_cagr")
    if pd.notna(n):
        if n >= 30_000:
            pts += 2
        elif n >= 15_000:
            pts += 1
    if pd.notna(cagr):
        if cagr >= 0.10:
            pts += 2
        elif cagr >= 0.05:
            pts += 1
    fund = str(mkt.get("field1_funding") or "")
    if "Strong" in fund:
        pts += 1
    return min(pts, 4)


def decide_row(cand, home, vol, mkt) -> dict:
    quality_fail = float(cand.get("oos_pct") or 0) >= 70 or int(cand.get("n_3y") or 0) < 5
    inside = bool(cand["in_baseline_primary"])
    on_brand = bool(home.get("on_brand_gated"))
    methods = bool(home.get("methods_shared"))
    home_else = bool(home.get("home_elsewhere"))
    parent_owns = bool(home.get("parent_owns_gated"))
    section_scale = bool(vol.get("section_scale"))
    journal_scale = bool(vol.get("journal_scale"))
    persist = bool(vol.get("persist_ok"))
    market_gate = bool(mkt.get("market_journal_gate"))
    blocks_journal = bool(mkt.get("parent_owns_blocks_journal")) or parent_owns
    n_off = int(vol.get("n_offbrand_rts") or 0)
    offbrand_titles = float(home.get("offbrand_title_share") or 0) >= 0.35

    reasons = []
    call = "emerging_watch"

    if quality_fail:
        call = "gate_intake"
        reasons.append("quality: high OOS or too few papers")
    elif inside:
        rising = float(cand.get("share_pp_delta") or 0) > 0 or (
            pd.notna(cand.get("share_cagr")) and float(cand.get("share_cagr")) > 0
        )
        # Large rising mix-shift inside 2020 primary → expand+gate, even if
        # domain-hit is weak (truncated titles; generic+embodied mixed in CV).
        if methods and not on_brand and not (section_scale and rising):
            call = "gate_intake"
            reasons.append("off-brand methods dump inside a broad primary")
        elif on_brand or section_scale or persist:
            call = "expand_rename"
            reasons.append("mix-shift inside 2020 primary")
            if methods and home.get("gate_string"):
                reasons.append("gated section recommended under expand")
            if offbrand_titles:
                reasons.append("also gate off-brand titles inside this community")
        else:
            call = "emerging_watch"
            reasons.append("inside 2020 primary but below brand/scale gates")
    elif home_else:
        call = "redirect_crosslist"
        reasons.append(
            f"topic overlap with {home.get('best_home_journal')} "
            f"(jaccard={home.get('best_home_jaccard')})"
        )
    elif (
        home.get("existing_section")
        and float(home.get("existing_section_jaccard") or 0) >= 0.45
        and str(home.get("existing_section_journal") or "") != str(cand["journal"])
    ):
        call = "redirect_crosslist"
        reasons.append(
            f"specialty section already exists: {home.get('existing_section')} "
            f"({home.get('existing_section_journal')})"
        )
    elif parent_owns and section_scale and persist:
        call = "new_gated_section"
        reasons.append("gated parent-owns + section-scale share")
        if methods and not home.get("gate_string"):
            call = "gate_intake"
            reasons.append("methods-shared but no gate string — tighten not section")
    elif (
        not parent_owns
        and not blocks_journal
        and journal_scale
        and market_gate
        and persist
    ):
        call = "new_journal"
        reasons.append("no topic-level home, journal-scale, market gate")
    else:
        call = "emerging_watch"
        reasons.append("below share/home/market gates")

    if n_off and call in {"expand_rename", "new_gated_section", "emerging_watch"}:
        reasons.append(f"{n_off} off-brand RT(s) to gate/close")

    i = _internal_score(cand, vol)
    h = _home_score(home)
    m = _market_score(mkt)
    presence, presence_reason = classify_presence(cand, home, vol, mkt, call)
    return {
        "call": call,
        "presence": presence,
        "presence_reason": presence_reason,
        "score": i + h + m,
        "score_internal": i,
        "score_home": h,
        "score_market": m,
        "reasons": "; ".join(reasons),
        "gate_string": home.get("gate_string") or "",
        "pending_persist": call in LAUNCH,
    }


def uniqueness_pass(decisions: pd.DataFrame) -> pd.DataFrame:
    """One expand/section per community_id; better parent keeps it."""
    out = decisions.copy()
    out["uniqueness_note"] = ""
    launch_like = out["call"].isin(["expand_rename", "new_gated_section"])
    for cid, g in out[launch_like].groupby("community_id"):
        if len(g) < 2:
            continue
        ranked = g.sort_values(
            ["in_baseline_primary", "parent_jaccard", "score"],
            ascending=[False, False, False],
        )
        winner = ranked.index[0]
        for idx in ranked.index[1:]:
            out.at[idx, "call"] = "redirect_crosslist"
            out.at[idx, "pending_persist"] = False
            out.at[idx, "presence"] = "already_publish"
            out.at[idx, "presence_reason"] = (
                f"already published; uniqueness winner={out.at[winner, 'journal']}"
            )
            out.at[idx, "uniqueness_note"] = (
                f"duplicate of community {cid}; winner={out.at[winner, 'journal']}"
            )
            out.at[idx, "reasons"] = (
                str(out.at[idx, "reasons"]) + "; uniqueness: redirected to better parent"
            )
    return out


def apply_portfolio_presence(decisions: pd.DataFrame) -> pd.DataFrame:
    """If any title already publishes the community or matched subfield at scale, it is not whitespace."""
    out = decisions.copy()
    if "presence" not in out.columns or out.empty:
        return out
    scaled = out["n_3y"].fillna(0) >= C.PAPER_FLOOR_SECTION
    if "section_scale" in out.columns:
        scaled = scaled | out["section_scale"].fillna(False).astype(bool)
    if "journal_scale" in out.columns:
        scaled = scaled | out["journal_scale"].fillna(False).astype(bool)
    owned = out["presence"].eq("already_publish") & scaled
    covered_fields = set(out.loc[owned, "field1"].dropna().astype(str))
    covered_cids = set(
        pd.to_numeric(out.loc[owned, "community_id"], errors="coerce").dropna().astype(int)
    )
    cid = pd.to_numeric(out["community_id"], errors="coerce")
    flip = out["presence"].eq("whitespace") & (
        cid.isin(covered_cids) | out["field1"].fillna("").astype(str).isin(covered_fields)
    )
    out.loc[flip, "presence"] = "already_publish"
    out.loc[flip, "presence_reason"] = "already published elsewhere in the portfolio"
    return out


def apply_two_quarter(decisions: pd.DataFrame, previous: pd.DataFrame | None) -> pd.DataFrame:
    out = decisions.copy()
    out["prior_call"] = ""
    out["persist_ok"] = False
    if previous is None or previous.empty:
        for idx, row in out.iterrows():
            if row["call"] in LAUNCH:
                out.at[idx, "pending_persist"] = True
                out.at[idx, "call_effective"] = "emerging_watch"
                out.at[idx, "reasons"] = (
                    str(row["reasons"]) + "; first quarter — watch until persist"
                )
            else:
                out.at[idx, "call_effective"] = row["call"]
        return out

    prev = previous.set_index(["journal", "community_id"])
    for idx, row in out.iterrows():
        key = (row["journal"], int(row["community_id"]))
        prior = ""
        if key in prev.index:
            prior = str(prev.loc[key, "call_effective"] if "call_effective" in prev.columns else prev.loc[key, "call"])
            if hasattr(prior, "iloc"):
                prior = str(prior.iloc[0])
        out.at[idx, "prior_call"] = prior
        if row["call"] in LAUNCH:
            if prior == row["call"]:
                out.at[idx, "persist_ok"] = True
                out.at[idx, "pending_persist"] = False
                out.at[idx, "call_effective"] = row["call"]
            else:
                out.at[idx, "pending_persist"] = True
                out.at[idx, "call_effective"] = "emerging_watch"
                out.at[idx, "reasons"] = (
                    str(row["reasons"]) + "; first quarter — watch until persist"
                )
        else:
            out.at[idx, "call_effective"] = row["call"]
    return out


def build_decisions(
    candidates: pd.DataFrame,
    home: pd.DataFrame,
    volume: pd.DataFrame,
    market: pd.DataFrame,
    previous: pd.DataFrame | None = None,
) -> pd.DataFrame:
    h = home.set_index(["journal", "community_id"])
    v = volume.set_index(["journal", "community_id"])
    m = market.set_index(["journal", "community_id"])
    rows = []
    for _, cand in candidates.iterrows():
        key = (cand["journal"], int(cand["community_id"]))
        home_s = h.loc[key] if key in h.index else pd.Series(dtype=object)
        vol_s = v.loc[key] if key in v.index else pd.Series(dtype=object)
        mkt_s = m.loc[key] if key in m.index else pd.Series(dtype=object)
        if isinstance(home_s, pd.DataFrame):
            home_s = home_s.iloc[0]
        if isinstance(vol_s, pd.DataFrame):
            vol_s = vol_s.iloc[0]
        if isinstance(mkt_s, pd.DataFrame):
            mkt_s = mkt_s.iloc[0]
        d = decide_row(cand, home_s, vol_s, mkt_s)
        rows.append(
            {
                **cand.to_dict(),
                "parent_jaccard": home_s.get("parent_jaccard"),
                "on_brand_gated": home_s.get("on_brand_gated"),
                "home_elsewhere": home_s.get("home_elsewhere"),
                "best_home_journal": home_s.get("best_home_journal"),
                "best_home_jaccard": home_s.get("best_home_jaccard"),
                "section_scale": vol_s.get("section_scale"),
                "journal_scale": vol_s.get("journal_scale"),
                "n_offbrand_rts": vol_s.get("n_offbrand_rts"),
                "offbrand_rts": vol_s.get("offbrand_rts"),
                "existing_section": home_s.get("existing_section"),
                "existing_section_journal": home_s.get("existing_section_journal"),
                "field1": mkt_s.get("field1"),
                "field1_mkt_2025": mkt_s.get("field1_mkt_2025"),
                "field1_cagr": mkt_s.get("field1_cagr"),
                "field1_fi_articles": mkt_s.get("field1_fi_articles"),
                "field1_fi_share": mkt_s.get("field1_fi_share"),
                "field1_pattern": mkt_s.get("field1_pattern"),
                **d,
            }
        )
    dec = pd.DataFrame(rows)
    dec = uniqueness_pass(dec)
    dec = apply_portfolio_presence(dec)
    dec = apply_two_quarter(dec, previous)
    return dec


def run_p4(
    run_timestamp: str,
    candidates: pd.DataFrame | None = None,
    home: pd.DataFrame | None = None,
    volume: pd.DataFrame | None = None,
    market: pd.DataFrame | None = None,
) -> pd.DataFrame:
    from . import bq as bqmod

    if candidates is None:
        candidates = bqmod.read_table("candidates", run_timestamp)
    if home is None:
        home = bqmod.read_table("home", run_timestamp)
    if volume is None:
        volume = bqmod.read_table("volume", run_timestamp)
    if market is None:
        market = bqmod.read_table("market", run_timestamp)
    previous = bqmod.previous_decisions(run_timestamp)
    dec = build_decisions(candidates, home, volume, market, previous)
    # Stamped here rather than duplicated into a separate decision_log table
    dec["logged_utc"] = datetime.now(timezone.utc).isoformat()
    bqmod.write_table(dec, "decisions", run_timestamp)
    pack = {
        "run": run_timestamp,
        "n_rows": int(len(dec)),
        "calls": dec["call_effective"].value_counts().to_dict()
        if "call_effective" in dec.columns
        else dec["call"].value_counts().to_dict(),
        "presence": dec["presence"].value_counts().to_dict()
        if "presence" in dec.columns
        else {},
        "pending_launch": int(dec["pending_persist"].sum())
        if "pending_persist" in dec.columns
        else 0,
    }
    bqmod.write_json_row(pack, "pack", run_timestamp)
    return dec
