"""Scope-drift brief for any journal in the current run.

Usage:
  python src/scope_drift/build_journal_brief_pdf.py --journal "Frontiers in Earth Science"
"""
from __future__ import annotations

import argparse
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.platypus import (
    CondPageBreak,
    ListFlowable,
    ListItem,
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
)

from paths import ensure_code_on_path

ensure_code_on_path()

import build_neurorobotics_brief_pdf as layout  # noqa: E402
from journal_profile import (  # noqa: E402
    contested_oos_titles,
    journal_dir,
    journal_profile,
    journal_short,
    primary_share_by_year,
    rename_candidates,
)
from neuro_analysis import (  # noqa: E402
    JOURNAL as DEFAULT_JOURNAL,
    drift_trend,
    get_journal,
    load_dashboards,
    onset_year,
    run_meta,
)

PALETTE = ["#2c5fa3", "#1f8a4c", "#856DF0", "#d4a300", "#c93030", "#0b1f3a"]

# Renaming is the most disruptive call in the brief, so it has to clear a high bar. A journal
# publishing its own subject in a new area (surgical sports medicine, geomaterials) is not drift
# and does not need a new masthead; only genuinely foreign work that has displaced the core does.
RENAME_MIN_SHARE = 20.0  # gaining community, % of recent output
RENAME_MIN_FOREIGN = 15.0  # % of that work the scope model flags as out of scope
RENAME_MIN_DELTA = 15.0  # pp share shift since the baseline year


def a_or_an(word: str) -> str:
    return "an" if word[:1].lower() in "aeiou" else "a"


def recent_mix(mj: dict, profile: dict, start_year: int) -> dict:
    """Recent-window mix, including how much of the gaining community reads as out of scope."""
    pts = [p for p in (mj.get("scatter") or []) if (p.get("yr") or 0) >= start_year]
    if not pts:
        return {}
    labels = {int(k): v for k, v in (profile.get("primary_labels") or {}).items()}
    gid = profile["gainer"]["id"]
    gp = [p for p in pts if p.get("c") == gid]
    top_id, top_n = Counter(p.get("c") for p in pts).most_common(1)[0]
    return {
        "n": len(pts),
        "gainer_share": round(100 * len(gp) / len(pts), 1),
        "gainer_oos_pct": round(100 * sum(1 for p in gp if p.get("s") == 0) / len(gp), 1) if gp else 0.0,
        "journal_oos_pct": round(100 * sum(1 for p in pts if p.get("s") == 0) / len(pts), 1),
        "core_label": labels.get(top_id) or f"Community {top_id}",
        "core_share": round(100 * top_n / len(pts), 1),
        "gainer_is_core": top_id == gid,
    }


def rename_verdict(profile: dict, mix: dict) -> dict:
    """Rename only on genuine drift: foreign work, at scale, that has displaced the core."""
    g_lab = profile["gainer"]["label"]
    short = profile["short"]
    share = mix.get("gainer_share", 0.0)
    g_oos = mix.get("gainer_oos_pct", 0.0)
    foreign = max(g_oos, mix.get("journal_oos_pct", 0.0))
    delta = abs(float(profile["gainer"].get("delta") or 0))

    if share < RENAME_MIN_SHARE:
        why = (
            f"{g_lab} is only <b>{share}%</b> of recent output. A community that small does not "
            "change what the journal is."
        )
    elif foreign < RENAME_MIN_FOREIGN:
        why = (
            f"{g_lab} is <b>{share}%</b> of recent output, but only <b>{g_oos}%</b> of those papers "
            f"are flagged out of scope. That reads as {short} applied to a new area rather than a "
            "different field, so the current title still describes the work."
        )
    elif not mix.get("gainer_is_core"):
        why = (
            f"{g_lab} has not displaced the core: <b>{mix.get('core_label')}</b> is still "
            f"<b>{mix.get('core_share')}%</b> of recent output against {share}%."
        )
    elif delta < RENAME_MIN_DELTA:
        why = (
            f"The shift toward {g_lab} is <b>{delta:.1f} pp</b> since the baseline year — a "
            "reweighting rather than a change of subject."
        )
    else:
        return {
            "call": "yes",
            "headline": "Yes — the title now names the smaller half.",
            "why": (
                f"{g_lab} is <b>{share}%</b> of recent output and the journal's largest community, "
                f"<b>{foreign}%</b> of recent work is flagged out of scope, and the shift is "
                f"<b>{delta:.1f} pp</b>. That is genuine drift, not {short} applied to a new area."
            ),
            "shortlist": True,
        }
    return {
        "call": "no",
        "headline": "No — restate the scope instead.",
        "why": why,
        "shortlist": False,
    }


def load_json(path: Path) -> dict:
    if not path.exists():
        raise SystemExit(f"Missing {path}. Run probe_sections_rts.py and analyze_rts.py for this journal.")
    return json.loads(path.read_text(encoding="utf-8"))


def make_footer(short: str):
    def footer(canvas, doc):
        canvas.saveState()
        canvas.setStrokeColor(layout.RULE)
        canvas.line(18 * mm, 12 * mm, A4[0] - 18 * mm, 12 * mm)
        canvas.setFont("Helvetica", 7)
        canvas.setFillColor(layout.MUTED)
        canvas.drawString(18 * mm, 7 * mm, f"Further work · {short} scope drift · Confidential")
        canvas.drawRightString(A4[0] - 18 * mm, 7 * mm, f"Page {doc.page}")
        canvas.restoreState()

    return footer


def fig_jsd(trend: dict, short: str, path: Path) -> Path:
    years = trend.get("years") or []
    jsd = trend.get("jsd") or []
    fig, ax = plt.subplots(figsize=(7.8, 2.6), dpi=140)
    ax.plot(years, jsd, marker="o", color="#1a4f8c", linewidth=2)
    ax.axhline(0.20, color="#d97706", linestyle="--", linewidth=1, label="Medium drift (0.20)")
    ax.axhline(0.30, color="#c93030", linestyle="--", linewidth=1, label="High drift (0.30)")
    ax.set_ylabel("JSD vs 2020 baseline")
    ax.set_xlabel("Year")
    ax.set_title(f"{short} — composition drift (JSD)")
    ax.legend(fontsize=8, loc="upper left")
    ax.set_ylim(0, max((jsd or [0]) + [0.4]) * 1.05)
    ax.grid(True, alpha=0.25)
    fig.tight_layout()
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path, bbox_inches="tight")
    plt.close(fig)
    return path


def fig_shares(rows: list[dict], labels: list[str], path: Path) -> Path:
    years = [r["year"] for r in rows]
    fig, ax = plt.subplots(figsize=(7.8, 2.8), dpi=140)
    for i, lab in enumerate(labels):
        ax.plot(
            years,
            [r.get(lab, 0) for r in rows],
            marker="o",
            label=lab,
            color=PALETTE[i % len(PALETTE)],
            linewidth=2,
        )
    ax.set_ylabel("Share of journal papers (%)")
    ax.set_xlabel("Year")
    ax.set_title("Primary community mix over time")
    ax.legend(fontsize=7, loc="best")
    ax.set_ylim(0, max(55, max((max((r.get(l, 0) for l in labels), default=0) for r in rows), default=0) + 5))
    ax.grid(True, alpha=0.25)
    fig.tight_layout()
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path, bbox_inches="tight")
    plt.close(fig)
    return path


def build_pdf(journal: str, outdir: Path | None = None) -> Path:
    outdir = Path(outdir) if outdir else journal_dir(journal)
    scope, drift, maps = load_dashboards()
    sj = get_journal(scope, journal)
    mj = get_journal(maps, journal)
    profile = journal_profile(sj)
    short = profile["short"]
    g_lab = profile["gainer"]["label"]
    l_lab = profile["loser"]["label"]
    labels = profile["primary_labels"]
    chart_labs = profile["chart_labels"] or list(labels.values())[:5]
    trend = drift_trend(drift, journal)
    shares = primary_share_by_year(mj, labels)
    contested = contested_oos_titles(mj, profile["keywords"], limit=12)
    meta = run_meta(scope)
    onset = onset_year(trend)
    s = layout.styles()
    fig_dir = outdir / "figures"
    jsd_path = fig_jsd(trend, short, fig_dir / "jsd.png")
    share_path = fig_shares(shares, chart_labs, fig_dir / "shares.png")

    rt_sum = load_json(outdir / "rt_analysis_summary.json")
    try:
        sec = load_json(outdir / "section_rt_summary.json")
    except SystemExit:
        sec = {}

    latest_jsd = (trend.get("jsd") or [None])[-1]
    oos2026 = next((r for r in (sj.get("oos_by_year") or []) if r.get("year") == 2026), None)
    ps = sj.get("primary_shift") or {}
    recent_period = rt_sum.get("recent_period", "2024-2026").replace("-", "–")
    recent_n = rt_sum.get("recent_n_papers", 0)
    g_pct = rt_sum.get("recent_gainer_pct", rt_sum.get("recent_cv_pct", 0))
    l_pct = rt_sum.get("recent_loser_pct", rt_sum.get("recent_neuro_pct", 0))
    recent_start = int(str(rt_sum.get("recent_period", "2024-2026")).split("-")[0])
    mix = recent_mix(mj, profile, recent_start)
    rn = rename_verdict(profile, mix)

    story = []
    story.append(Spacer(1, 80 * mm))
    story.append(Paragraph(journal, s["cover_title"]))
    story.append(Paragraph("Scope drift deep-dive & editorial options", s["cover_sub"]))
    story.append(Spacer(1, 5 * mm))
    story.append(layout.cover_rule())
    story.append(Spacer(1, 5 * mm))
    story.append(
        Paragraph(
            f"Run {meta.get('run_timestamp', '20260721_122750')} · Generated {meta.get('generated_utc', '')}<br/>"
            f"Source: {meta.get('bq_source_dataset', 'ocean-breeze-tier-1.airak')} · "
            f"Years {meta.get('start_year', 2020)}–{meta.get('end_year', 2026)}",
            s["cover_sub"],
        )
    )
    story.append(Paragraph("Sophie Wilson · Advanced Analytics · Further work", s["cover_sub"]))
    story.append(Paragraph(f"PDF built {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}", s["cover_sub"]))
    story.append(PageBreak())

    story.append(Paragraph("1. Executive summary", s["h1"]))
    story.append(
        Paragraph(
            "This brief separates <b>historic attribution (2020–2025)</b> from the "
            "<b>current actionable position</b>. Historic RTs explain how the journal drifted; they "
            "do not generate actions once they are closed or completed. Recommendations cover only "
            "RTs currently marked <b>Online</b> in RDM, scored on every paper they have published.",
            s["body"],
        )
    )
    story.append(
        layout.kpi_table(
            s,
            [
                ("Onset", str(onset or "—"), "JSD ≥ 0.20"),
                ("JSD 2026", f"{latest_jsd:.2f}" if latest_jsd is not None else "—", "vs 2020"),
                (
                    "OOS 2026",
                    f"{oos2026['out_of_scope_pct']:.1f}%" if oos2026 else "—",
                    f"{oos2026['articles'] if oos2026 else '—'} papers",
                ),
                ("Gaining", g_lab, f"{profile['gainer']['delta']:+.1f} pp vs 2020"),
                ("All-years OOS", f"{sj['out_of_scope_pct']:.1f}%", f"{sj['articles']:,} papers"),
            ],
        )
    )
    story.append(Spacer(1, 4 * mm))
    story.append(Paragraph("2. Historic narrative (2020–2025)", s["h1"]))
    story.append(Paragraph("2.1 When did drift start?", s["h2"]))
    story.append(
        Paragraph(
            f"JSD first crosses 0.20 in <b>{onset or '—'}</b> and sits at "
            f"<b>{latest_jsd:.2f}</b> in 2026. The historic window is 2020–2025; 2026 is current YTD.",
            s["body"],
        )
    )
    story.append(layout.scaled(jsd_path))
    story.append(Paragraph("2.2 How did the journal drift?", s["h2"]))
    gained = ", ".join(profile.get("gained_labels") or []) or "none"
    lost = ", ".join(profile.get("lost_labels") or []) or "none"
    story.append(
        Paragraph(
            f"The gaining community is <b>{g_lab}</b> "
            f"({profile['gainer']['baseline_share']}% → {profile['gainer']['latest_share']}%). "
            f"The declining core community is <b>{l_lab}</b> "
            f"({profile['loser']['baseline_share']}% → {profile['loser']['latest_share']}%). "
            f"Primary-set flag: <b>{'changed' if ps.get('changed') else 'unchanged set'}</b> "
            f"(gained: {gained}; lost: {lost}).",
            s["body"],
        )
    )
    story.append(layout.scaled(share_path))
    story.append(Spacer(1, 3 * mm))
    hdr = ["Year", "n", "OOS%"] + [f"{lab} %" for lab in chart_labs]
    rows = []
    for r in shares:
        rows.append(
            [str(r["year"]), str(r["articles"]), f"{r['oos_pct']:.1f}"]
            + [f"{r.get(lab, 0):.1f}" for lab in chart_labs]
        )
    nlab = max(len(chart_labs), 1)
    rest = (layout.FRAME_W - 62 * mm) / nlab
    widths = [22 * mm, 18 * mm, 22 * mm] + [rest] * nlab
    story.append(layout.data_table(hdr, rows, widths, s))

    story.append(CondPageBreak(50 * mm))
    story.append(Paragraph("3. Is the out-of-scope signal genuine?", s["h1"]))
    story.append(
        Paragraph(
            "Community assignment is a Leiden label, not an editorial verdict. Titles below mention "
            f"terms from the journal name or its primary communities and are still flagged OOS — "
            "candidates to keep or to write into an expanded scope, not automatic rejects.",
            s["body"],
        )
    )
    if contested:
        story.append(
            ListFlowable(
                [
                    ListItem(Paragraph(f"{c.get('year')} · C{c.get('community_id')} — {c.get('title')}", s["bullet"]))
                    for c in contested
                ],
                bulletType="bullet",
                leftIndent=12,
                bulletFontSize=8,
            )
        )
    else:
        story.append(Paragraph("No contested OOS titles matched the journal keyword list.", s["body"]))

    story.append(Paragraph("4. Historic RT contribution to drift (pre-2026)", s["h1"]))
    story.append(
        Paragraph(
            f"Drift pull is papers in <b>{g_lab}</b> minus papers in <b>{l_lab}</b>. "
            "Positive values pull toward the observed shift. No recommendation is attached to a "
            "historic RT that is no longer open.",
            s["body"],
        )
    )
    drift_fig = fig_dir / "rt_drift_pull.png"
    if drift_fig.exists():
        story.append(layout.scaled(drift_fig, 165 * mm))
        story.append(Spacer(1, 3 * mm))
    historic_drift = rt_sum.get("historic_top_drift_rts") or []
    if historic_drift:
        story.append(
            layout.data_table(
                ["Historic Research Topic", "n", "Net pull", "Status"],
                [
                    [
                        str(r.get("research_topic_title") or ""),
                        str(r.get("n")),
                        str(int(r.get("drift_pull") or 0)),
                        str(r.get("rt_stage") or "Unknown"),
                    ]
                    for r in historic_drift[:8]
                ],
                [106 * mm, 14 * mm, 22 * mm, 36 * mm],
                s,
            )
        )

    story.append(CondPageBreak(60 * mm))
    story.append(Paragraph("5. Current RT position and actions", s["h1"]))
    story.append(Paragraph(rt_sum.get("verdict") or "", s["body"]))
    story.append(Paragraph("5.1 Online RTs vs spontaneous papers", s["h2"]))
    oos_n = rt_sum.get("open_rt_oos_n", 0)
    g_n = rt_sum.get("open_rt_cv_n", 0)
    story.append(
        Paragraph(
            f"The {rt_sum.get('n_rts')} currently Online RTs account for "
            f"<b>{rt_sum.get('open_rt_n_papers', 0)}</b> papers in the run "
            f"({rt_sum.get('open_rt_first_year', '—')}–{rt_sum.get('open_rt_last_year', '—')}). "
            f"Of them, <b>{oos_n}</b> {'is' if oos_n == 1 else 'are'} out of scope and "
            f"<b>{g_n}</b> sit in {g_lab}. "
            f"<b>{rt_sum.get('closed_rt_n_papers', 0)}</b> papers sit in closed/completed RTs and "
            f"<b>{rt_sum.get('spontaneous_n_papers', 0)}</b> arrived spontaneously.",
            s["body"],
        )
    )
    mix_fig = fig_dir / "rt_vs_spontaneous_mix.png"
    if mix_fig.exists():
        story.append(layout.scaled(mix_fig, 168 * mm))

    story.append(Paragraph("5.2 Currently Online RTs by OOS since launch", s["h2"]))
    story.append(
        Paragraph(
            "Counts cover every paper each topic has published inside the run window.",
            s["body"],
        )
    )
    top_oos = rt_sum.get("current_top_oos_rts") or []
    if top_oos:
        rows = []
        for r in top_oos[:10]:
            first, last = r.get("first_year"), r.get("last_year")
            span = f"{first}–{last}" if first and last and first != last else str(first or "—")
            rows.append(
                [
                    str(r.get("research_topic_title") or ""),
                    span,
                    str(r.get("n")),
                    f"{r.get('oos_pct')}%",
                    str(r.get("recommendation") or ""),
                ]
            )
        story.append(
            layout.data_table(
                ["Research Topic", "Years", "n", "OOS%", "Action"],
                rows,
                [84 * mm, 20 * mm, 12 * mm, 18 * mm, 44 * mm],
                s,
            )
        )

    story.append(Paragraph("5.3 Actions for current Online RTs only", s["h2"]))
    story.append(
        Paragraph(
            f"Heuristic on {rt_sum.get('n_rts')} Online RTs: "
            f"<b>{rt_sum.get('n_remove')}</b> remove/do-not-renew; "
            f"<b>{rt_sum.get('n_gate')}</b> gate; "
            f"<b>{rt_sum.get('n_keep_grow')}</b> keep/audit; "
            f"<b>{rt_sum.get('n_watch')}</b> watch (n&lt;3).",
            s["body"],
        )
    )
    watch_list = rt_sum.get("watch_list") or []
    if watch_list:
        story.append(
            ListFlowable(
                [
                    ListItem(
                        Paragraph(
                            f"<b>{r.get('research_topic_title') or ''}</b> — n={r.get('n')}, OOS {r.get('oos_pct')}%",
                            s["bullet"],
                        )
                    )
                    for r in watch_list[:8]
                ],
                bulletType="bullet",
                leftIndent=12,
                bulletFontSize=8,
            )
        )

    story.append(CondPageBreak(70 * mm))
    story.append(Paragraph("5.4 Did a Research Topic launch cause the drift?", s["h2"]))
    la = rt_sum.get("launch_attribution") or {}
    has_sections = int(sec.get("n_with_section") or 0) > 0
    if has_sections:
        story.append(
            Paragraph(
                f"This journal has Specialty Sections covering {sec.get('n_with_section')} of "
                f"{sec.get('n_scatter', 0)} run papers. Read per-section OOS in the journal folder "
                "and compare each section's launch date against the drift onset.",
                s["body"],
            )
        )
    if la:
        verdict = (la.get("verdict") or "").strip()
        verdict = verdict[:1].upper() + verdict[1:]
        story.append(
            Paragraph(
                f"<b>{verdict}.</b> "
                f"Of topics pulling toward {g_lab} ({la.get('n_rts_with_pull', 0)} of them, "
                f"{la.get('total_pull', 0)} net papers), the largest is "
                f"<b>{la.get('top1_share', 0)}%</b> of pull and the top three "
                f"<b>{la.get('top3_share', 0)}%</b>. It takes <b>{la.get('n_to_half', 0)}</b> "
                "topics to reach half.",
                s["body"],
            )
        )
        if la.get("onset_year") and la.get("first_cv_heavy_cohort"):
            story.append(
                Paragraph(
                    f"Drift onset is <b>{la.get('onset_year')}</b>. The first clearly "
                    f"{g_lab}-heavy launch cohort is <b>{la.get('first_cv_heavy_cohort')}</b> "
                    f"(onset-window net pull {la.get('onset_net_pull', 0):+d}).",
                    s["body"],
                )
            )
        cohorts = [c for c in (la.get("cohorts") or []) if (c.get("papers") or 0) >= 10]
        if cohorts:
            story.append(
                layout.data_table(
                    ["Launch year", "RTs", "Papers", f"{g_lab} %", f"{l_lab} %", "Net pull"],
                    [
                        [
                            str(int(float(c["rt_launch_year"]))),
                            str(int(c["n_rts"])),
                            str(int(c["papers"])),
                            f"{c['cv_pct']}%",
                            f"{c['neuro_pct']}%",
                            f"{int(c['drift_pull']):+d}",
                        ]
                        for c in cohorts
                    ],
                    [30 * mm, 20 * mm, 26 * mm, 34 * mm, 34 * mm, 34 * mm],
                    s,
                )
            )

    story.append(CondPageBreak(70 * mm))
    story.append(Paragraph("6. Current editorial options", s["h1"]))
    story.append(
        Paragraph(
            f"Judged on the <b>{recent_period}</b> window — <b>{recent_n}</b> papers. "
            "The three questions are expand, rename, add sections.",
            s["body"],
        )
    )
    recent_rows = rt_sum.get("recent_by_year") or []
    if recent_rows:
        rows = [
            [
                str(r.get("year")),
                str(r.get("n")),
                f"{r.get('oos_pct')}%",
                f"{r.get('gainer_pct', r.get('cv_pct'))}%",
                f"{r.get('loser_pct', r.get('neuro_pct'))}%",
            ]
            for r in recent_rows
        ]
        rows.append(
            [
                f"<b>{recent_period}</b>",
                f"<b>{recent_n}</b>",
                f"<b>{rt_sum.get('recent_oos_pct', 0)}%</b>",
                f"<b>{g_pct}%</b>",
                f"<b>{l_pct}%</b>",
            ]
        )
        story.append(
            layout.data_table(
                ["Year", "n", "OOS%", f"{g_lab} %", f"{l_lab} %"],
                rows,
                [34 * mm, 28 * mm, 28 * mm, 44 * mm, 44 * mm],
                s,
                last_row_bold=True,
            )
        )
        story.append(Spacer(1, 3 * mm))

    name_has_gainer = g_lab.lower().split()[0] in journal.lower()
    if mix.get("gainer_is_core"):
        standing = (
            f"{g_lab} is now the journal's largest community at <b>{g_pct}%</b> of "
            f"{recent_period} output"
        )
    else:
        standing = (
            f"{g_lab} is <b>{g_pct}%</b> of {recent_period} output, against <b>{mix.get('core_share')}%</b> "
            f"for the largest community, {mix.get('core_label')}"
        )
    story.append(Paragraph("6.1 Expand scope?", s["h2"]))
    story.append(
        Paragraph(
            f"<b>{'Selectively' if not name_has_gainer else 'Tighten around the stated field'}.</b> "
            f"{standing}. Formalise work that still belongs in {short}, and gate it on a genuine "
            f"link to the journal's core. Do not expand into the far-field clusters driving the "
            f"{rt_sum.get('recent_oos_pct', 0)}% out-of-scope rate.",
            s["body"],
        )
    )
    story.append(Paragraph("6.2 Rename?", s["h2"]))
    story.append(Paragraph(f"<b>{rn['headline']}</b> {rn['why']}", s["body"]))
    if rn["shortlist"]:
        cands = rename_candidates(profile)
        story.append(
            layout.data_table(
                ["Candidate", "What it signals", "Watch-out"],
                [[f"<b>{a}</b>", b, c] for a, b, c in cands],
                [52 * mm, 76 * mm, 50 * mm],
                s,
                align_from=3,
            )
        )
    else:
        story.append(
            Paragraph(
                f"Restate the scope so it names the {g_lab} work explicitly (§6.1) and gate it on "
                f"{a_or_an(short)} {short} core-scope test. Revisit the title only if that work keeps growing "
                "<i>and</i> starts failing the scope test.",
                s["body"],
            )
        )
    story.append(Paragraph("6.3 New sections?", s["h2"]))
    if has_sections:
        story.append(
            Paragraph(
                "Sections already exist. Use them as the unit for future commissioning standards; "
                "do not invent a parallel architecture until the live sections are gated.",
                s["body"],
            )
        )
    else:
        story.append(
            Paragraph(
                f"There are no Specialty Sections. A workable split on the {recent_period} mix is "
                f"one section for the {l_lab} core and one for {g_lab}, each gated on a genuine "
                f"{short} link. These are proposed future sections, not an explanation of past drift "
                "(see §5.4).",
                s["body"],
            )
        )

    sa = rt_sum.get("series_attribution") or {}
    top_series = (sa.get("top_series") or [{}])[0]
    story.append(CondPageBreak(55 * mm))
    story.append(Paragraph("7. The four decisions", s["h1"]))
    story.append(
        layout.data_table(
            ["Decision", "Call", "Basis"],
            [
                [
                    "Remove or close Research Topics?",
                    "<b>No</b> — block renewals instead"
                    if rt_sum.get("n_remove", 0) == 0
                    else "<b>Yes</b> — see §5.3",
                    f"{rt_sum.get('n_rts')} Online RTs; {rt_sum.get('open_rt_oos_n', 0)} of "
                    f"{rt_sum.get('open_rt_n_papers', 0)} papers OOS. Large historic contributors "
                    "are typically already closed.",
                ],
                [
                    "Tighten enforcement?",
                    "<b>Yes</b>",
                    f"{rt_sum.get('recent_oos_pct', 0)}% of {recent_period} papers are out of scope. "
                    "Desk-reject work with no link to the journal's core.",
                ],
                [
                    "Expand the stated scope?",
                    "<b>Yes</b>, selectively" if not name_has_gainer else "<b>No</b> — already named",
                    f"{g_lab} is {g_pct}% of recent output. Name the in-family work; do not baptise "
                    "far-field OOS.",
                ],
                [
                    "Rename the journal?",
                    "<b>Yes</b> — alongside the scope restatement"
                    if rn["call"] == "yes"
                    else "<b>No</b> — restate scope instead",
                    rn["why"]
                    + (" Shortlist in §6.2." if rn["shortlist"] else ""),
                ],
            ],
            [46 * mm, 40 * mm, 92 * mm],
            s,
            align_from=3,
        )
    )
    if top_series and top_series.get("series"):
        story.append(
            Paragraph(
                f"<b>Concrete renewal block:</b> <i>{top_series.get('series')}</i> — "
                f"{top_series.get('volumes')} volumes, {top_series.get('n')} papers, "
                f"<b>{top_series.get('pull_share')}%</b> of drift pull. Do not commission a further "
                "volume without a core-scope gate.",
                s["body"],
            )
        )
    story.append(Paragraph("7.1 Supporting actions", s["h2"]))
    story.append(
        ListFlowable(
            [
                ListItem(Paragraph(x, s["bullet"]))
                for x in [
                    f"Audit OOS papers in Online RTs ({rt_sum.get('open_rt_oos_n', 0)}) before changing topic scope.",
                    f"Monitor {rt_sum.get('n_watch')} Online RTs with n&lt;3.",
                    "Use completed RTs only to explain historic drift.",
                    f"Police new RT proposals against {a_or_an(short)} {short} core-scope test.",
                    "Pick a title from §6.2 and announce it with the scope restatement."
                    if rn["shortlist"]
                    else f"Re-measure in 12 months; revisit the title only if {g_lab} keeps growing "
                    "and starts failing the scope test.",
                ]
            ],
            bulletType="bullet",
            leftIndent=12,
        )
    )
    story.append(
        Paragraph(
            "Disclaimer: This brief was created with AI assistance from dashboard outputs of the "
            "scope-drift pipeline. Community labels are model-generated; contested OOS needs editorial review.",
            s["small"],
        )
    )

    out_pdf = outdir / f"{profile['slug']}_scope_drift_brief.pdf"
    doc = SimpleDocTemplate(
        str(out_pdf),
        pagesize=A4,
        leftMargin=16 * mm,
        rightMargin=16 * mm,
        topMargin=14 * mm,
        bottomMargin=16 * mm,
        title=f"{short} Scope Drift Brief",
        author="Sophie Wilson",
    )
    doc.build(story, onFirstPage=make_footer(short), onLaterPages=make_footer(short))
    return out_pdf


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--journal", required=True)
    parser.add_argument("--outdir", default="")
    args = parser.parse_args()
    outdir = Path(args.outdir) if args.outdir else journal_dir(args.journal)
    path = build_pdf(args.journal, outdir)
    print(f"Wrote {path} ({path.stat().st_size / 1024:.1f} KB)")


if __name__ == "__main__":
    main()
