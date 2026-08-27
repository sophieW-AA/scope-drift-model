"""
Build Neurorobotics further-work PDF brief.

Reads dashboards in output/, writes:
  further_work/Neurorobotics_Scope_Drift_Brief.pdf

Usage (from repo root):
  python further_work/build_neurorobotics_brief_pdf.py
"""

from __future__ import annotations

import io
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import (
    Image,
    ListFlowable,
    ListItem,
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

HERE = Path(__file__).resolve().parent
REPO = HERE.parent
sys.path.insert(0, str(HERE))

from neuro_analysis import (  # noqa: E402
    JOURNAL,
    PRIMARY_LABELS,
    contested_oos_titles,
    drift_trend,
    get_journal,
    load_dashboards,
    onset_year,
    primary_share_by_year,
    run_meta,
)

OUT_PDF = HERE / "Neurorobotics_Scope_Drift_Brief.pdf"
FIG_DIR = HERE / "figures"

NAVY = colors.HexColor("#0b1f3a")
BLUE = colors.HexColor("#1a4f8c")
MUTED = colors.HexColor("#6b7280")
RULE = colors.HexColor("#d1d5db")
SOFT = colors.HexColor("#f5f7fb")
GREEN = colors.HexColor("#1f8a4c")
RED = colors.HexColor("#c93030")
AMBER = colors.HexColor("#d97706")
BLACK = colors.HexColor("#1a1f36")
WHITE = colors.white


def styles():
    base = getSampleStyleSheet()
    return {
        "cover_title": ParagraphStyle(
            "cover_title", parent=base["Title"], fontSize=22, textColor=NAVY, spaceAfter=8, alignment=TA_CENTER
        ),
        "cover_sub": ParagraphStyle(
            "cover_sub", parent=base["Normal"], fontSize=11, textColor=MUTED, alignment=TA_CENTER, spaceAfter=4
        ),
        "h1": ParagraphStyle("h1", parent=base["Heading1"], fontSize=14, textColor=NAVY, spaceBefore=12, spaceAfter=6),
        "h2": ParagraphStyle("h2", parent=base["Heading2"], fontSize=12, textColor=BLUE, spaceBefore=10, spaceAfter=4),
        "body": ParagraphStyle("body", parent=base["Normal"], fontSize=9.5, textColor=BLACK, leading=13, spaceAfter=6),
        "bullet": ParagraphStyle("bullet", parent=base["Normal"], fontSize=9.5, textColor=BLACK, leading=12),
        "small": ParagraphStyle("small", parent=base["Normal"], fontSize=8, textColor=MUTED, leading=10),
        "kpi": ParagraphStyle("kpi", parent=base["Normal"], fontSize=9, textColor=BLACK, alignment=TA_CENTER),
    }


def footer(canvas, doc):
    canvas.saveState()
    canvas.setStrokeColor(RULE)
    canvas.line(18 * mm, 12 * mm, A4[0] - 18 * mm, 12 * mm)
    canvas.setFont("Helvetica", 7)
    canvas.setFillColor(MUTED)
    canvas.drawString(18 * mm, 7 * mm, "Further work · Neurorobotics scope drift · Confidential")
    canvas.drawRightString(A4[0] - 18 * mm, 7 * mm, f"Page {doc.page}")
    canvas.restoreState()


def fig_jsd(trend: dict, path: Path) -> Path:
    years = trend.get("years") or []
    jsd = trend.get("jsd") or []
    fig, ax = plt.subplots(figsize=(7.2, 3.2), dpi=140)
    ax.plot(years, jsd, marker="o", color="#1a4f8c", linewidth=2)
    ax.axhline(0.20, color="#d97706", linestyle="--", linewidth=1, label="Medium drift (0.20)")
    ax.axhline(0.30, color="#c93030", linestyle="--", linewidth=1, label="High drift (0.30)")
    ax.set_ylabel("JSD vs 2020 baseline")
    ax.set_xlabel("Year")
    ax.set_title("Neurorobotics — composition drift (JSD)")
    ax.legend(fontsize=8, loc="upper left")
    ax.set_ylim(0, max(jsd + [0.4]) * 1.05)
    ax.grid(True, alpha=0.25)
    fig.tight_layout()
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path, bbox_inches="tight")
    plt.close(fig)
    return path


def fig_shares(rows: list[dict], path: Path) -> Path:
    years = [r["year"] for r in rows]
    fig, ax = plt.subplots(figsize=(7.2, 3.4), dpi=140)
    palette = {
        "Computer vision": "#2c5fa3",
        "Therapeutic Movement Sciences": "#1f8a4c",
        "Autonomous Systems and Control": "#856DF0",
        "Neuroscience": "#d4a300",
    }
    for lab, color in palette.items():
        ax.plot(years, [r[lab] for r in rows], marker="o", label=lab, color=color, linewidth=2)
    ax.set_ylabel("Share of journal papers (%)")
    ax.set_xlabel("Year")
    ax.set_title("Primary community mix over time")
    ax.legend(fontsize=7.5, loc="best")
    ax.set_ylim(0, 50)
    ax.grid(True, alpha=0.25)
    fig.tight_layout()
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path, bbox_inches="tight")
    plt.close(fig)
    return path


def kpi_table(s, items: list[tuple[str, str, str]]):
    data = []
    for label, value, sub in items:
        data.append(
            [
                Paragraph(f"<b>{label}</b><br/><font size='14'>{value}</font><br/><font color='#6b7280' size='8'>{sub}</font>", s["kpi"])
            ]
        )
    # 5 KPIs in a row
    row = [c[0] for c in data]
    t = Table([row], colWidths=[34 * mm] * len(row))
    t.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), SOFT),
                ("BOX", (0, 0), (-1, -1), 0.5, RULE),
                ("INNERGRID", (0, 0), (-1, -1), 0.4, RULE),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 6),
                ("RIGHTPADDING", (0, 0), (-1, -1), 6),
                ("TOPPADDING", (0, 0), (-1, -1), 8),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
            ]
        )
    )
    return t


def build_pdf(out_pdf: Path = OUT_PDF) -> Path:
    scope, drift, maps = load_dashboards()
    j = get_journal(scope)
    mj = get_journal(maps)
    trend = drift_trend(drift)
    shares = primary_share_by_year(mj)
    contested = contested_oos_titles(mj, limit=25)
    meta = run_meta(scope)
    onset = onset_year(trend)
    s = styles()

    jsd_path = fig_jsd(trend, FIG_DIR / "neuro_jsd.png")
    share_path = fig_shares(shares, FIG_DIR / "neuro_shares.png")

    latest_jsd = (trend.get("jsd") or [None])[-1]
    oos2026 = next((r for r in (j.get("oos_by_year") or []) if r.get("year") == 2026), None)
    ps = j.get("primary_shift") or {}

    story = []
    story.append(Spacer(1, 28 * mm))
    story.append(Paragraph("Frontiers in Neurorobotics", s["cover_title"]))
    story.append(Paragraph("Scope drift deep-dive & editorial options", s["cover_sub"]))
    story.append(Spacer(1, 6 * mm))
    story.append(
        Paragraph(
            f"Run {meta.get('run_timestamp', '20260721_122750')} · Generated {meta.get('generated_utc', '')}<br/>"
            f"Source: {meta.get('bq_source_dataset', 'ocean-breeze-tier-1.airak')} · "
            f"Years {meta.get('start_year', 2020)}–{meta.get('end_year', 2026)} · τ={meta.get('temporal_decay_tau', 5)}",
            s["cover_sub"],
        )
    )
    story.append(Paragraph("Sophie Wilson · Advanced Analytics · Further work", s["cover_sub"]))
    story.append(Paragraph(f"PDF built {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}", s["cover_sub"]))
    story.append(PageBreak())

    # Executive summary
    story.append(Paragraph("1. Executive summary", s["h1"]))
    story.append(
        Paragraph(
            "Against a <b>2020 baseline</b>, Neurorobotics shows clear composition drift from 2021, "
            "driven mainly by a shift toward <b>computer vision</b> and away from <b>neuroscience</b>, "
            "not by a collapse of the primary community set. Out-of-scope rate stays roughly flat "
            "(~16–25%). A meaningful minority of “OOS” papers look like <b>false OOS</b> "
            "(neurorobotics titles parked in far-field Leiden clusters).",
            s["body"],
        )
    )
    story.append(
        kpi_table(
            s,
            [
                ("Onset", str(onset or "—"), "JSD ≥ 0.20"),
                ("JSD 2026", f"{latest_jsd:.2f}" if latest_jsd is not None else "—", "vs 2020"),
                ("OOS 2026", f"{oos2026['out_of_scope_pct']:.1f}%" if oos2026 else "—", f"{oos2026['articles'] if oos2026 else '—'} papers"),
                ("Primary set", "Unchanged", "same 4 clusters"),
                ("All-years OOS", f"{j['out_of_scope_pct']:.1f}%", f"{j['articles']:,} papers"),
            ],
        )
    )
    story.append(Spacer(1, 4 * mm))

    story.append(Paragraph("2. When did drift start?", s["h1"]))
    story.append(
        Paragraph(
            f"JSD jumps in <b>{onset or 2021}</b> (0 → ~0.23), then climbs through 2023–2025 to "
            f"<b>{latest_jsd:.2f}</b> in 2026. Treat 2021 as onset; weight 2023–25 more than early 2026 "
            "(small n).",
            s["body"],
        )
    )
    story.append(Image(str(jsd_path), width=170 * mm, height=75 * mm))

    story.append(Paragraph("3. How is the journal drifting?", s["h1"]))
    story.append(
        Paragraph(
            "Primary community <b>IDs are unchanged</b> (Computer vision, Therapeutic Movement Sciences, "
            "Autonomous Systems &amp; Control, Neuroscience), but <b>shares flipped</b>: vision rose from "
            "~16% (2020) to ~40%+ (2025–26); neuroscience fell from ~21% to ~6–7%.",
            s["body"],
        )
    )
    story.append(Image(str(share_path), width=170 * mm, height=78 * mm))

    # Share table
    hdr = ["Year", "n", "OOS%", "CV%", "TMS%", "Auto%", "Neuro%"]
    tbl = [hdr]
    for r in shares:
        tbl.append(
            [
                str(r["year"]),
                str(r["articles"]),
                f"{r['oos_pct']:.1f}",
                f"{r['Computer vision']:.1f}",
                f"{r['Therapeutic Movement Sciences']:.1f}",
                f"{r['Autonomous Systems and Control']:.1f}",
                f"{r['Neuroscience']:.1f}",
            ]
        )
    t = Table(tbl, colWidths=[18 * mm, 16 * mm, 18 * mm, 18 * mm, 20 * mm, 20 * mm, 20 * mm])
    t.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), NAVY),
                ("TEXTCOLOR", (0, 0), (-1, 0), WHITE),
                ("FONTSIZE", (0, 0), (-1, -1), 8),
                ("GRID", (0, 0), (-1, -1), 0.4, RULE),
                ("ALIGN", (1, 0), (-1, -1), "CENTER"),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [WHITE, SOFT]),
            ]
        )
    )
    story.append(t)
    story.append(Spacer(1, 3 * mm))
    story.append(
        Paragraph(
            f"Primary shift flag (2020→{ps.get('latest_year', 2026)}): "
            f"<b>{'changed' if ps.get('changed') else 'unchanged set'}</b>. "
            "Gain/loss labels: none — drift is reweighting, not replacement of the core set.",
            s["body"],
        )
    )

    story.append(PageBreak())
    story.append(Paragraph("4. Is OOS genuine?", s["h1"]))
    story.append(
        Paragraph(
            "<b>Mostly yes for far-field clusters; partly no for misplaced neurorobotics.</b> "
            "LLM borderline labelled all non-primary candidates as hard OOS (materials, IoT security, "
            "geology, thermal, etc.). That is appropriate for true far-field work. However, titles in "
            "Materials / Business / Language–Health clusters often still read as robot–neural–rehab — "
            "these are <b>false or soft OOS</b> from Leiden macro assignment.",
            s["body"],
        )
    )
    story.append(Paragraph("4.1 Contested OOS examples (keyword overlap)", s["h2"]))
    story.append(
        Paragraph(
            "Sample of community-OOS titles that mention robot / neural / prosthetic / embodied terms "
            "(truncated). These are candidates for expand/keep, not automatic reject:",
            s["body"],
        )
    )
    bullets = []
    for c in contested[:12]:
        bullets.append(
            ListItem(
                Paragraph(
                    f"{c.get('year')} · C{c.get('community_id')} — {c.get('title')}",
                    s["bullet"],
                )
            )
        )
    story.append(ListFlowable(bullets, bulletType="bullet", leftIndent=12, bulletFontSize=8))
    story.append(Spacer(1, 3 * mm))
    story.append(
        Paragraph(
            "<b>Genuine OOS to keep rejecting:</b> thermal energy, geology, cancer immunotherapy, "
            "organic chemistry, urban mobility, generic management without robots, pure remote-sensing / "
            "medical X-ray CV without embodiment.",
            s["body"],
        )
    )

    # --- Research Topics ---
    rt_summary_path = HERE / "neurorobotics_rt_analysis_summary.json"
    rt_deep_path = HERE / "neurorobotics_rt_deep_dive.csv"
    if not rt_summary_path.exists():
        raise SystemExit("Missing RT analysis. Run: python further_work/analyze_rts.py")
    rt_sum = json.loads(rt_summary_path.read_text(encoding="utf-8"))

    story.append(Paragraph("5. Research Topics — OOS, drift, keep/cut", s["h1"]))
    story.append(
        Paragraph(
            rt_sum.get("verdict")
            or "See further_work/analyze_rts.py outputs.",
            s["body"],
        )
    )
    story.append(Paragraph("5.1 RT vs spontaneous submissions", s["h2"]))
    story.append(
        Paragraph(
            f"Of {rt_sum['n_papers']} run papers, <b>{rt_sum['n_rt']}</b> are in a Research Topic "
            f"and <b>{rt_sum['n_spontaneous']}</b> are spontaneous. "
            f"OOS: RT <b>{rt_sum['oos_pct_rt']}%</b> vs spontaneous <b>{rt_sum['oos_pct_spontaneous']}%</b>. "
            f"Computer vision share: RT <b>{rt_sum['cv_pct_rt']}%</b> vs spontaneous <b>{rt_sum['cv_pct_spontaneous']}%</b>. "
            f"Neuroscience share: RT <b>{rt_sum['neuro_pct_rt']}%</b> vs spontaneous <b>{rt_sum['neuro_pct_spontaneous']}%</b>. "
            "Spontaneous is the stronger CV-mix driver; RTs carry more OOS risk.",
            s["body"],
        )
    )
    mix_fig = FIG_DIR / "rt_vs_spontaneous_mix.png"
    if mix_fig.exists():
        story.append(Image(str(mix_fig), width=160 * mm, height=65 * mm))
        story.append(Spacer(1, 2 * mm))

    story.append(Paragraph("5.2 Which RTs contribute to OOS?", s["h2"]))
    oos_fig = FIG_DIR / "rt_top_oos.png"
    if oos_fig.exists():
        story.append(Image(str(oos_fig), width=155 * mm, height=85 * mm))
    top_oos = rt_sum.get("top_oos_rts") or []
    if top_oos:
        rows = [["RT (short)", "n", "OOS%", "Action"]]
        for r in top_oos[:8]:
            title = str(r.get("research_topic_title") or "")[:48]
            rows.append(
                [
                    title,
                    str(r.get("n")),
                    f"{r.get('oos_pct')}%",
                    str(r.get("recommendation") or "")[:28],
                ]
            )
        t = Table(rows, colWidths=[85 * mm, 12 * mm, 16 * mm, 45 * mm])
        t.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), NAVY),
                    ("TEXTCOLOR", (0, 0), (-1, 0), WHITE),
                    ("FONTSIZE", (0, 0), (-1, -1), 7.5),
                    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                    ("GRID", (0, 0), (-1, -1), 0.3, RULE),
                    ("ROWBACKGROUNDS", (0, 1), (-1, -1), [WHITE, SOFT]),
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ]
            )
        )
        story.append(Spacer(1, 2 * mm))
        story.append(t)

    story.append(Paragraph("5.3 Which RTs contribute to drift?", s["h2"]))
    story.append(
        Paragraph(
            "Drift pull ≈ papers in the Computer Vision community minus Neuroscience for each RT. "
            "Image-fusion / ANN–embedded-systems series are pure CV volume with little neural–robot content — "
            "they move the mix even when OOS% is moderate.",
            s["body"],
        )
    )
    drift_fig = FIG_DIR / "rt_drift_pull.png"
    if drift_fig.exists():
        story.append(Image(str(drift_fig), width=155 * mm, height=85 * mm))

    story.append(Paragraph("5.4 Remove / gate / add", s["h2"]))
    story.append(
        Paragraph(
            f"Heuristic on {rt_sum.get('n_rts')} RTs with papers in the run: "
            f"<b>{rt_sum.get('n_remove')}</b> remove/do-not-renew or tight-gate; "
            f"<b>{rt_sum.get('n_gate')}</b> gate with robot/embodied requirement; "
            f"<b>{rt_sum.get('n_keep_grow')}</b> keep/grow. Brand series (Women/Horizons/Insights) kept for audit, not auto-cut.",
            s["body"],
        )
    )
    remove_list = rt_sum.get("remove_list") or []
    if remove_list:
        bullets = []
        for r in remove_list[:10]:
            bullets.append(
                ListItem(
                    Paragraph(
                        f"<b>{str(r.get('research_topic_title') or '')[:70]}</b> — "
                        f"n={r.get('n')}, OOS {r.get('oos_pct')}% · {r.get('recommendation')}",
                        s["bullet"],
                    )
                )
            )
        story.append(Paragraph("<b>Remove / do not renew (priority):</b>", s["body"]))
        story.append(ListFlowable(bullets, bulletType="bullet", leftIndent=12, bulletFontSize=8))
    adds = rt_sum.get("add_proposals") or []
    if adds:
        story.append(Paragraph("<b>Add (proposed new RTs):</b>", s["body"]))
        story.append(
            ListFlowable(
                [
                    ListItem(
                        Paragraph(
                            f"<b>{a['proposed_rt']}</b> — {a['rationale']}",
                            s["bullet"],
                        )
                    )
                    for a in adds
                ],
                bulletType="bullet",
                leftIndent=12,
                bulletFontSize=8,
            )
        )
    story.append(
        Paragraph(
            "Full table: <i>further_work/neurorobotics_rt_deep_dive.csv</i> "
            "(re-run <i>python further_work/analyze_rts.py</i>).",
            s["small"],
        )
    )

    story.append(Paragraph("6. Editorial options", s["h1"]))
    story.append(Paragraph("6.1 Expand scope?", s["h2"]))
    story.append(
        Paragraph(
            "<b>Yes, selectively.</b> Formalise what you already publish: embodied / robot vision &amp; "
            "learning; therapeutic &amp; assistive robotics; neural interfaces ↔ robot control. "
            "<b>Do not</b> expand into materials, IoT cybersecurity, traffic forecasting, or generic NLP.",
            s["body"],
        )
    )
    story.append(Paragraph("6.2 Rename?", s["h2"]))
    story.append(
        Paragraph(
            "<b>Strong case.</b> “Neurorobotics” undersells vision/control dominance and over-promises "
            "neuroscience (~6–7% recently). Options: <i>Neurorobotics and Embodied AI</i>; "
            "<i>Neural and Robotic Systems</i>; or keep the name with an explicit scope line covering "
            "neural interfaces, embodied intelligence, and robot-assisted motor systems.",
            s["body"],
        )
    )
    story.append(Paragraph("6.3 Did a section launch cause the drift?", s["h2"]))
    story.append(
        Paragraph(
            "<b>No.</b> Taxonomy join shows all papers as <b>Specialty Journal</b> with null section — "
            "no Specialty Section rows. Use Research Topics (§5) for launch-vs-drift attribution instead.",
            s["body"],
        )
    )
    story.append(Paragraph("6.4 New sections — where (forward architecture)?", s["h2"]))
    story.append(
        Paragraph(
            "1) Neural interfaces &amp; motor neuroscience · "
            "2) Therapeutic &amp; assistive robotics · "
            "3) Embodied vision &amp; multimodal perception (robot-centric gate) · "
            "4) Learning &amp; control for physical agents · "
            "5) Optional social/assistive HRI only if you choose to expand. "
            "Gate sections 3–4 with “must involve a robot / embodied agent / neural–motor loop”. "
            "These are <b>recommended future sections</b>, not an explanation of past drift.",
            s["body"],
        )
    )

    story.append(Paragraph("7. Recommended next steps", s["h1"]))
    next_steps = [
        "Treat 2021 as onset; use 2023–25 as the CV-takeover window in JD narratives.",
        "Act on RT list: close off-brand / high-OOS topics; gate ML–vision RTs with robot/embodied requirement.",
        "Do not attribute drift to section launches — none exist.",
        "Manually audit false OOS in clusters 0 / 3 / 20 (Materials, Business, Lang–Health).",
        "Choose strategy A (broaden + rename toward embodied AI) or B (tighten to neural–robot + rehab and desk-reject pure CV).",
        "Stand up sections / on-brand RTs under the chosen strategy; do not add materials/IoT topics.",
        "Re-check mid/late 2026 volume before locking 2026-only conclusions.",
    ]
    story.append(
        ListFlowable(
            [ListItem(Paragraph(x, s["bullet"])) for x in next_steps],
            bulletType="bullet",
            leftIndent=12,
        )
    )
    story.append(Spacer(1, 6 * mm))
    story.append(
        Paragraph(
            "Disclaimer: This brief was created with AI assistance from dashboard outputs of the "
            "scope-drift pipeline. Community labels are model-generated; contested OOS needs editorial review.",
            s["small"],
        )
    )

    out_pdf.parent.mkdir(parents=True, exist_ok=True)
    doc = SimpleDocTemplate(
        str(out_pdf),
        pagesize=A4,
        leftMargin=16 * mm,
        rightMargin=16 * mm,
        topMargin=14 * mm,
        bottomMargin=16 * mm,
        title="Neurorobotics Scope Drift Brief",
        author="Sophie Wilson",
    )
    doc.build(story, onFirstPage=footer, onLaterPages=footer)
    return out_pdf


if __name__ == "__main__":
    path = build_pdf()
    print(f"Wrote {path} ({path.stat().st_size / 1024:.1f} KB)")
