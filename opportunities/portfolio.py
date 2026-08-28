"""Portfolio shortlist: already-publish vs whitespace, section vs journal."""

from __future__ import annotations

import pandas as pd

from . import config as C

SECTION_CALLS = frozenset({"expand_rename", "new_gated_section"})
JOURNAL_CALLS = frozenset({"new_journal"})

LAUNCH_KEEP = [
    "presence",
    "presence_reason",
    "opportunity_kind",
    "call",
    "journal",
    "community_label",
    "community_id",
    "candidate_type",
    "score",
    "share_3y",
    "share_late_pct",
    "share_pp_delta",
    "n_3y",
    "gate_string",
    "reasons",
    "field1",
    "field1_mkt_2025",
    "field1_fi_articles",
    "field1_fi_share",
    "field1_pattern",
    "best_home_journal",
    "existing_section",
    "existing_section_journal",
    "pending_persist",
]


def _kind(call: str) -> str:
    if call in SECTION_CALLS:
        return "section"
    if call in JOURNAL_CALLS:
        return "journal"
    return ""


def _pct(v, digits: int = 1) -> str:
    if v is None or (isinstance(v, float) and pd.isna(v)):
        return "—"
    try:
        return f"{float(v):.{digits}%}"
    except (TypeError, ValueError):
        return "—"


def build_launches(decisions: pd.DataFrame) -> pd.DataFrame:
    """Current-moment launches use tree `call`, not two-quarter `call_effective`."""
    d = decisions.copy()
    d["opportunity_kind"] = d["call"].map(_kind)
    if "presence" not in d.columns:
        d["presence"] = "already_publish"
        d["presence_reason"] = ""
    launches = d[d["opportunity_kind"].isin(["section", "journal"])].copy()
    if launches.empty:
        return launches
    launches = launches.sort_values(
        ["presence", "opportunity_kind", "score", "share_3y"],
        ascending=[True, True, False, False],
    )
    keep = [c for c in LAUNCH_KEEP if c in launches.columns]
    return launches[keep]


def _has_frontiers_anchor(anchor) -> bool:
    a = str(anchor or "").strip()
    if a in {"", "—", "-", "nan", "None"}:
        return False
    return "frontiers" in a.lower()


def unmatched_jd_whitespace(decisions: pd.DataFrame, jd: pd.DataFrame) -> pd.DataFrame:
    """JD subfields with thin FI share, no Frontiers journal, and no section-scale community."""
    if jd is None or jd.empty:
        return pd.DataFrame()
    covered = set()
    if len(decisions) and "field1" in decisions.columns:
        vol = decisions.copy()
        already = vol["presence"].eq("already_publish") if "presence" in vol.columns else True
        scaled = vol.get("section_scale", False)
        if not isinstance(scaled, pd.Series):
            scaled = pd.Series(False, index=vol.index)
        n3 = vol["n_3y"] if "n_3y" in vol.columns else 0
        keep = already | scaled.astype(bool) | (n3 >= C.PAPER_FLOOR_SECTION)
        covered = {str(x) for x in vol.loc[keep, "field1"].dropna().unique()}
        if "field2" in vol.columns:
            covered |= {str(x) for x in vol.loc[keep, "field2"].dropna().unique()}

    rows = jd.copy()
    if "fi_share" not in rows.columns:
        rows["fi_share"] = rows["fi_articles"] / rows["mkt_2025"].replace(0, pd.NA)
    rows = rows[
        (rows["mkt_2025"].fillna(0) >= C.MARKET_MIN_ARTICLES)
        & (rows["cagr"].fillna(0) >= C.MARKET_MIN_CAGR)
        & (rows["fi_share"].fillna(1) < C.FI_SHARE_WHITESPACE)
        & (~rows["subfield"].astype(str).isin(covered))
        & (~rows["anchor_journal"].map(_has_frontiers_anchor))
    ]
    if rows.empty:
        return rows
    return rows.sort_values(["score", "mkt_2025"], ascending=[False, False])


def write_portfolio(
    run_timestamp: str, decisions: pd.DataFrame, jd: pd.DataFrame | None = None
) -> pd.DataFrame:
    from . import bq as bqmod

    launches = build_launches(decisions)
    already = launches[launches["presence"] == "already_publish"] if len(launches) else launches
    white = launches[launches["presence"] == "whitespace"] if len(launches) else launches
    mapper_white = (
        decisions[decisions["presence"] == "whitespace"].copy()
        if "presence" in decisions.columns and len(decisions)
        else pd.DataFrame()
    )
    if len(mapper_white):
        mapper_white = mapper_white.sort_values(["score", "n_3y"], ascending=[False, False])
        if "field1_mkt_2025" in mapper_white.columns:
            mapper_white = mapper_white[mapper_white["field1_mkt_2025"].notna()]
        mapper_white = mapper_white.head(80)
    if jd is None:
        jd = bqmod.fetch_jd_opportunities()
    jd_white = unmatched_jd_whitespace(decisions, jd)

    section = launches[launches["opportunity_kind"] == "section"] if len(launches) else launches
    journal = launches[launches["opportunity_kind"] == "journal"] if len(launches) else launches
    pack = {
        "run": run_timestamp,
        "n_decisions": int(len(decisions)),
        "n_journals_scored": int(decisions["journal"].nunique()) if len(decisions) else 0,
        "n_already_publish_launches": int(len(already)),
        "n_whitespace_launches": int(len(white)),
        "n_whitespace_mapper_rows": int(len(mapper_white)),
        "n_whitespace_jd_gaps": int(len(jd_white)),
        "n_section_opportunities": int(len(section)),
        "n_journal_opportunities": int(len(journal)),
        "section_by_journal": section["journal"].value_counts().head(20).to_dict()
        if len(section)
        else {},
        "top_already_publish": already.head(25).to_dict(orient="records") if len(already) else [],
        "top_whitespace_launches": white.head(25).to_dict(orient="records") if len(white) else [],
        "top_whitespace_jd": jd_white.head(25).to_dict(orient="records") if len(jd_white) else [],
        "note": (
            "Already publish = Frontiers already has volume in that community "
            "(expand, gated section, redirect, or leakage). Whitespace = OpenAlex "
            "market with FI share <1%, no Frontiers journal as the JD anchor, and no "
            "section-scale community in this run. `call` is the current-moment "
            "recommendation; pending_persist means it has not fired two quarters yet. "
            "Coverage is titles in this scope-drift run, not necessarily all ~222 active journals."
        ),
    }
    markdown = build_markdown(pack, already, white, mapper_white, jd_white)
    pack_row = {**pack, "portfolio_markdown": markdown}
    bqmod.write_table(launches, "launches", run_timestamp)
    bqmod.write_table(jd_white, "whitespace_jd", run_timestamp)
    bqmod.write_json_row(pack_row, "portfolio", run_timestamp)
    return launches


def build_markdown(
    pack: dict,
    already: pd.DataFrame,
    white_launches: pd.DataFrame,
    mapper_white: pd.DataFrame,
    jd_white: pd.DataFrame,
) -> str:
    lines = [
        "# Frontiers launch opportunities",
        "",
        f"Run `{pack['run']}` · {pack['n_journals_scored']} journals scored · "
        f"{pack['n_already_publish_launches']} already-publish launches · "
        f"{pack['n_whitespace_launches']} whitespace launches · "
        f"{pack['n_whitespace_jd_gaps']} JD market gaps.",
        "",
        pack["note"],
        "",
        "## Already publish",
        "",
        "Frontiers already prints this work. The question is expand, gate, redirect, "
        "or stop treating leakage as a new journal.",
        "",
    ]
    already_j = already[already["opportunity_kind"] == "journal"] if len(already) else already
    already_s = already[already["opportunity_kind"] == "section"] if len(already) else already
    lines += ["### Journal-path (usually leakage, not a gap)", ""]
    if already_j is None or already_j.empty:
        lines.append("None at current gates.")
    else:
        lines += [
            "| Score | Journal | Community | Share 3y | FI share | Why |",
            "| ---: | --- | --- | ---: | ---: | --- |",
        ]
        for _, r in already_j.head(40).iterrows():
            lines.append(
                f"| {int(r['score'])} | {r['journal']} | {r['community_label']} | "
                f"{float(r['share_3y']):.1%} | {_pct(r.get('field1_fi_share'))} | "
                f"{str(r.get('reasons') or '')[:140]} |"
            )
    lines += ["", "### Section / expand", ""]
    if already_s is None or already_s.empty:
        lines.append("None at current gates.")
    else:
        lines += [
            "| Score | Kind | Journal | Community | Share 3y | Gate |",
            "| ---: | --- | --- | --- | ---: | --- |",
        ]
        for _, r in already_s.head(60).iterrows():
            gate = str(r.get("gate_string") or "—")[:80]
            if gate in {"nan", "None"}:
                gate = "—"
            lines.append(
                f"| {int(r['score'])} | {r['call']} | {r['journal']} | "
                f"{r['community_label']} | {float(r['share_3y']):.1%} | {gate} |"
            )

    lines += [
        "",
        "## Whitespace",
        "",
        "Market is large/growing, Frontiers share of that OpenAlex subfield is "
        f"under {C.FI_SHARE_WHITESPACE:.0%}, and there is no Frontiers journal "
        "listed as the JD anchor. These are gaps, not mix-shifts of existing output.",
        "",
        "### Mapper rows (thin internal volume)",
        "",
    ]
    show_white = white_launches if white_launches is not None and len(white_launches) else mapper_white
    if show_white is None or show_white.empty:
        lines.append("No mapper rows classified as whitespace at current gates.")
    else:
        lines += [
            "| Score | Call | Journal | Community | n 3y | FI share | Why |",
            "| ---: | --- | --- | --- | ---: | ---: | --- |",
        ]
        for _, r in show_white.head(40).iterrows():
            why = str(r.get("presence_reason") or r.get("reasons") or "")[:120]
            lines.append(
                f"| {int(r.get('score') or 0)} | {r.get('call')} | {r.get('journal')} | "
                f"{r.get('community_label')} | {int(r.get('n_3y') or 0)} | "
                f"{_pct(r.get('field1_fi_share'))} | {why} |"
            )

    lines += ["", "### Market gaps (no Frontiers journal, no section-scale community)", ""]
    if jd_white is None or jd_white.empty:
        lines.append("None — every thin-FI JD subfield already has a Frontiers home or a matching community in this run.")
    else:
        lines += [
            "| Score | Subfield | Mkt 2025 | CAGR | FI articles | FI share | Pattern | Anchor |",
            "| ---: | --- | ---: | ---: | ---: | ---: | --- | --- |",
        ]
        for _, r in jd_white.head(40).iterrows():
            anchor = str(r.get("anchor_journal") or "—")
            if anchor in {"nan", "None", "—"}:
                anchor = "—"
            pat = str(r.get("pattern") or "—").replace("🔀 ", "").replace("📊 ", "").replace("🏔️ ", "").replace("📈 ", "")
            lines.append(
                f"| {int(r.get('score') or 0)} | {r['subfield']} | "
                f"{int(r['mkt_2025']):,} | {_pct(r.get('cagr'))} | "
                f"{int(r.get('fi_articles') or 0):,} | {_pct(r.get('fi_share'))} | "
                f"{pat} | {anchor} |"
            )
    return "\n".join(lines)
