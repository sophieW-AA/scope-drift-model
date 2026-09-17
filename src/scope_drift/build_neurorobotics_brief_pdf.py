"""
Build Neurorobotics further-work PDF brief.

Reads dashboards in scope_drift_outputs/output, writes:
  scope_drift_outputs/further_work/Neurorobotics_Scope_Drift_Brief.pdf

Usage (from repo root):
  python src/scope_drift/build_neurorobotics_brief_pdf.py
"""

from __future__ import annotations

import io
import json
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
from reportlab.pdfbase.pdfmetrics import stringWidth
from reportlab.platypus import (
    CondPageBreak,
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

from paths import WORK_DIR, ensure_code_on_path

ensure_code_on_path()

from neuro_analysis import (  # noqa: E402
    JOURNAL,
    PRIMARY_LABELS,
    contested_oos_titles,
    drift_trend,
    get_journal,
    load_dashboards,
    load_section_rt_summary,
    onset_year,
    primary_share_by_year,
    run_meta,
)

OUT_PDF = WORK_DIR / "Neurorobotics_Scope_Drift_Brief.pdf"
FIG_DIR = WORK_DIR / "figures"

# A4 minus the 16 mm side margins set on the document template. Tables and images
# are sized against this so they line up with the body text.
FRAME_W = 178 * mm

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
        "h1": ParagraphStyle(
            "h1",
            parent=base["Heading1"],
            fontSize=14,
            textColor=NAVY,
            spaceBefore=14,
            spaceAfter=6,
            keepWithNext=1,
        ),
        "h2": ParagraphStyle(
            "h2",
            parent=base["Heading2"],
            fontSize=12,
            textColor=BLUE,
            spaceBefore=11,
            spaceAfter=4,
            keepWithNext=1,
        ),
        "body": ParagraphStyle("body", parent=base["Normal"], fontSize=9.5, textColor=BLACK, leading=13, spaceAfter=6),
        "bullet": ParagraphStyle("bullet", parent=base["Normal"], fontSize=9.5, textColor=BLACK, leading=12),
        "small": ParagraphStyle(
            "small", parent=base["Normal"], fontSize=8, textColor=MUTED, leading=10, spaceBefore=4
        ),
        "kpi": ParagraphStyle("kpi", parent=base["Normal"], fontSize=9, textColor=BLACK, alignment=TA_CENTER),
        "cell": ParagraphStyle("cell", parent=base["Normal"], fontSize=7.5, textColor=BLACK, leading=9.5),
        "cell_c": ParagraphStyle(
            "cell_c", parent=base["Normal"], fontSize=7.5, textColor=BLACK, leading=9.5, alignment=TA_CENTER
        ),
        "cell_head": ParagraphStyle(
            "cell_head",
            parent=base["Normal"],
            fontSize=7.5,
            textColor=WHITE,
            leading=9.5,
            fontName="Helvetica-Bold",
        ),
        "cell_head_c": ParagraphStyle(
            "cell_head_c",
            parent=base["Normal"],
            fontSize=7.5,
            textColor=WHITE,
            leading=9.5,
            fontName="Helvetica-Bold",
            alignment=TA_CENTER,
        ),
    }


def _fitted_head_styles(header, widths, s, floor: float = 5.5):
    """Shrink header text just enough that no column word is split mid-word."""
    size = s["cell_head"].fontSize
    for h, w in zip(header, widths):
        avail = w - 10  # table LEFTPADDING + RIGHTPADDING
        words = str(h).split()
        if not words or avail <= 0:
            continue
        longest = max(stringWidth(word, "Helvetica-Bold", size) for word in words)
        if longest > avail:
            size = max(floor, min(size, size * avail / longest))
    if size >= s["cell_head"].fontSize:
        return s["cell_head"], s["cell_head_c"]
    return (
        ParagraphStyle("cell_head_fit", parent=s["cell_head"], fontSize=size, leading=size + 2),
        ParagraphStyle("cell_head_c_fit", parent=s["cell_head_c"], fontSize=size, leading=size + 2),
    )


def data_table(
    header: list[str],
    rows: list[list],
    widths: list[float],
    s: dict,
    align_from: int = 1,
    last_row_bold: bool = False,
) -> Table:
    """Full-width table that repeats its header when it splits across pages."""
    head_l, head_c = _fitted_head_styles(header, widths, s)
    head = [
        Paragraph(str(h), head_l if i < align_from else head_c)
        for i, h in enumerate(header)
    ]
    body = [
        [
            c if hasattr(c, "wrap") else Paragraph(str(c), s["cell"] if i < align_from else s["cell_c"])
            for i, c in enumerate(row)
        ]
        for row in rows
    ]
    style = [
        ("BACKGROUND", (0, 0), (-1, 0), NAVY),
        ("GRID", (0, 0), (-1, -1), 0.3, RULE),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [WHITE, SOFT]),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("ALIGN", (align_from, 0), (-1, -1), "CENTER"),
        ("LEFTPADDING", (0, 0), (-1, -1), 5),
        ("RIGHTPADDING", (0, 0), (-1, -1), 5),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]
    if last_row_bold:
        style.append(("BACKGROUND", (0, -1), (-1, -1), SOFT))
        style.append(("LINEABOVE", (0, -1), (-1, -1), 0.8, NAVY))
    t = Table([head] + body, colWidths=widths, repeatRows=1, hAlign="LEFT")
    t.setStyle(TableStyle(style))
    return t


def cover_rule() -> Table:
    """Short centred divider between the cover title block and the run details."""
    t = Table([[""]], colWidths=[60 * mm], rowHeights=[0.1])
    t.setStyle(TableStyle([("LINEBELOW", (0, 0), (-1, -1), 1, BLUE)]))
    t.hAlign = "CENTER"
    return t


def scaled(path: Path, width: float = FRAME_W) -> Image:
    """Image scaled to the text column, preserving the figure's aspect ratio."""
    img = Image(str(path))
    ratio = img.imageHeight / float(img.imageWidth)
    img.drawWidth = width
    img.drawHeight = width * ratio
    img.hAlign = "LEFT"
    return img


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
    fig, ax = plt.subplots(figsize=(7.8, 2.6), dpi=140)
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
    fig, ax = plt.subplots(figsize=(7.8, 2.8), dpi=140)
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
    # 5 KPIs in a row, spanning the full text column
    row = [c[0] for c in data]
    t = Table([row], colWidths=[FRAME_W / len(row)] * len(row), hAlign="LEFT")
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


def rename_options_block(rt_sum: dict, recent_period: str, recent_n: int, s: dict) -> list:
    """Section 6.2 — the rename call and a shortlist of candidate titles.

    The shortlist is judged on fit to the published mix, not on switching cost: a
    title has to name the vision and control majority, keep the neural–motor angle
    that differentiates the journal, and still read as a scope rather than a field.
    """
    cv = rt_sum.get("recent_cv_pct", 0)
    auto = rt_sum.get("recent_auto_pct", 0)
    tms = rt_sum.get("recent_tms_pct", 0)
    neuro = rt_sum.get("recent_neuro_pct", 0)

    out = [Paragraph("6.2 Rename?", s["h2"])]
    out.append(
        Paragraph(
            f"<b>Yes.</b> Across {recent_n} papers in {recent_period} the machine side of the journal "
            f"— computer vision {cv}% plus autonomous systems and control {auto}% — is "
            f"{round(cv + auto, 1)}% of output, against {tms}% therapeutic movement and {neuro}% "
            "neuroscience. The current title promises the smaller half. If the stated scope is "
            "widened to cover embodied and robot vision (§6.1), leaving the name unchanged puts the "
            "mismatch in the most visible place the journal has.",
            s["body"],
        )
    )
    out.append(
        data_table(
            ["Candidate", "What it signals", "Watch-out"],
            [
                [
                    "<b>Frontiers in Neurorobotics and Embodied AI</b> <i>(recommended)</i>",
                    "Keeps the established term and adds the vision-and-learning majority beside it. "
                    "Covers all four communities without disowning the existing readership.",
                    "Longest of the options, and <i>embodied AI</i> is a term still in motion.",
                ],
                [
                    "<b>Frontiers in Embodied Intelligence</b>",
                    "One clean idea spanning perception, learning and control — the strongest forward "
                    "signal, and the best fit to where submissions are actually heading.",
                    "Drops both <i>neuro</i> and <i>robot</i>; weakest continuity with the current title.",
                ],
                [
                    "<b>Frontiers in Neural and Robotic Systems</b>",
                    "Neural interfaces plus robotics and control. Reads as a natural widening rather "
                    "than a change of direction.",
                    "Generic — does not signal the vision majority that drove the shift.",
                ],
                [
                    "<b>Frontiers in Robot Learning and Perception</b>",
                    f"The most literal fit to the published mix ({round(cv + auto, 1)}% vision plus "
                    "control).",
                    "Abandons the neural–motor identity that differentiates the journal from "
                    "mainstream robotics and ML venues.",
                ],
                [
                    "<b>Frontiers in Robotics, Perception and Neural Control</b>",
                    "Descriptive across all four communities; leaves least room for misreading the scope.",
                    "Three-noun titles scan poorly and abbreviate badly.",
                ],
            ],
            [52 * mm, 76 * mm, 50 * mm],
            s,
            align_from=3,
        )
    )
    out.append(Spacer(1, 3 * mm))
    out.append(
        Paragraph(
            "Whichever title is chosen, pair it with the embodiment gate from §6.1. A broader name "
            "without that gate reads as an invitation to the generic vision work that produced the "
            f"{rt_sum.get('recent_oos_pct', 0)}% out-of-scope rate in this window.",
            s["body"],
        )
    )
    return out


def decisions_section(rt_sum: dict, recent_period: str, recent_n: int, s: dict) -> list:
    """Section 7 — a straight answer on each of the four editorial decisions.

    Sections 5 and 6 weigh the evidence; this section makes the call, because
    "choose strategy A or B" leaves the reader with the decision they came here for.
    """
    sa = rt_sum.get("series_attribution") or {}
    top_series = (sa.get("top_series") or [{}])[0]
    oos_pct = rt_sum.get("recent_oos_pct", 0)
    cv_pct = rt_sum.get("recent_cv_pct", 0)
    neuro_pct = rt_sum.get("recent_neuro_pct", 0)
    machine_pct = round(cv_pct + rt_sum.get("recent_auto_pct", 0), 1)

    out = [Paragraph("7. The four decisions", s["h1"])]
    out.append(
        Paragraph(
            f"Each call below rests on the {recent_period} window ({recent_n} papers), not on the "
            f"{rt_sum.get('open_rt_n_papers', 0)}-paper open-RT sample. Sections 5 and 6 hold the "
            "evidence; this section is the recommendation.",
            s["body"],
        )
    )
    out.append(
        data_table(
            ["Decision", "Call", "Basis"],
            [
                [
                    "Remove or close Research Topics?",
                    "<b>No</b> — block renewals instead",
                    f"None of the {rt_sum.get('n_rts')} Online RTs meets a close or gate threshold: "
                    f"{rt_sum.get('open_rt_oos_n', 0)} of their {rt_sum.get('open_rt_n_papers', 0)} "
                    "papers is out of scope. Every large drift contributor is already closed, so the "
                    "only live lever is refusing the next volume of vision-heavy series.",
                ],
                [
                    "Tighten enforcement?",
                    "<b>Yes</b>",
                    f"{oos_pct}% of {recent_period} papers are out of scope. The hard cases — thermal, "
                    "geology, immunotherapy, urban mobility, pure remote sensing and medical imaging — "
                    "have no robot and no neural–motor loop. Desk-reject them.",
                ],
                [
                    "Expand the stated scope?",
                    "<b>Yes</b>, selectively",
                    f"Computer vision is {cv_pct}% of recent output against {neuro_pct}% neuroscience. "
                    "Much of it is embodied and robot vision that the current scope statement never "
                    "names, and some measured OOS is that work being mis-assigned rather than "
                    "genuinely off-topic. Name it; do not open the door to materials, IoT security "
                    "or generic NLP.",
                ],
                [
                    "Rename the journal?",
                    "<b>Yes</b> — alongside the scope restatement",
                    f"Vision and control together are {machine_pct}% of {recent_period} output "
                    f"against {neuro_pct}% neuroscience, so the title promises the smaller half. "
                    "Renaming and restating scope are the same decision: doing one without the "
                    "other leaves the mismatch on the masthead. Shortlist in §6.2.",
                ],
            ],
            [46 * mm, 34 * mm, 98 * mm],
            s,
            align_from=3,
        )
    )
    out.append(Spacer(1, 2 * mm))
    out.append(
        Paragraph(
            "<b>Tightening and expanding are not opposites here.</b> Both are the same test: work is "
            "in scope if it involves a robot, an embodied agent or a neural–motor loop. Expanding the "
            "stated scope names what already passes that test — robot vision, embodied AI, neural "
            "interfaces, assistive and therapeutic robotics. Tightening enforcement rejects what fails "
            "it, including vision work with no embodiment.",
            s["body"],
        )
    )
    if top_series:
        out.append(
            Paragraph(
                f"<b>The one concrete removal action.</b> Do not commission a further volume of "
                f"<i>{top_series.get('series') or ''}</i> without the embodiment gate — "
                f"{top_series.get('volumes')} volumes, {top_series.get('n')} papers, "
                f"{top_series.get('cv_n')} computer vision against {top_series.get('neuro_n')} "
                f"neuroscience, <b>{top_series.get('pull_share')}%</b> of all drift pull. The "
                f"{sa.get('n_multi_volume', 0)} recurring series together carry "
                f"<b>{sa.get('multi_volume_pull_share', 0)}%</b> of the pull.",
                s["body"],
            )
        )
    out.append(Paragraph("7.1 Supporting actions", s["h2"]))
    out.append(
        ListFlowable(
            [
                ListItem(Paragraph(x, s["bullet"]))
                for x in [
                    f"Audit the {rt_sum.get('open_rt_oos_n', 0)} out-of-scope "
                    f"{'paper' if rt_sum.get('open_rt_oos_n', 0) == 1 else 'papers'} in Online RTs "
                    "before changing any of those topics' scope.",
                    f"Monitor the {rt_sum.get('n_watch')} Online RTs with fewer than three papers; "
                    "too early to judge.",
                    "Use completed RTs only to explain historic drift; attach no action to them, and "
                    + launch_next_step(rt_sum).replace("Do not blame", "do not blame"),
                    "Pick a title from the §6.2 shortlist, announce it with the restated scope, and "
                    "re-measure in 12 months to confirm the mix stays inside the embodiment gate.",
                ]
            ],
            bulletType="bullet",
            leftIndent=12,
        )
    )
    return out


def launch_next_step(rt_sum: dict) -> str:
    """One next-step line matching whatever the launch attribution concluded."""
    la = rt_sum.get("launch_attribution") or {}
    verdict = la.get("verdict")
    onset = la.get("onset_year")
    if verdict == "launches followed the drift":
        return (
            f"Do not blame a launch for the {onset} onset — the vision-heavy cohorts start "
            f"{la.get('first_cv_heavy_cohort')}; police new RT proposals instead of re-litigating old ones."
        )
    if verdict in ("one launch dominates", "a small group of launches"):
        return (
            f"Treat the {la.get('n_to_half', 0)} topics carrying half the CV pull as the drift "
            "source and apply the scope gate to their successor volumes."
        )
    return (
        f"Attribute drift to commissioning volume, not one launch — it takes "
        f"{la.get('n_to_half', 0)} topics to reach half the CV pull."
    )


def launch_attribution_section(rt_sum: dict, s: dict) -> list:
    """Section 5.4 — which structural launch, if any, caused the drift.

    A Frontiers Specialty Journal has no Specialty Sections, so there is no section
    launch to test and the Research Topic is the only launch unit available. Field
    journals do have sections, so the section question stays in the brief for them.
    """
    sec, has_sections = section_state()
    if has_sections:
        return section_launch_block(sec, s)
    return rt_launch_block(rt_sum, sec, s)


def section_state() -> tuple[dict, bool]:
    """Section probe output, and whether the journal actually has Specialty Sections."""
    try:
        sec = load_section_rt_summary()
    except FileNotFoundError:
        sec = {}
    return sec, int(sec.get("n_with_section") or 0) > 0


def section_launch_block(sec: dict, s: dict) -> list:
    """Journals that do have Specialty Sections keep the section-launch question."""
    sections = sec.get("sections") or {}
    named = [k for k in sections if k and k != "(none)"]
    out = [Paragraph("5.4 Did a section launch cause the drift?", s["h2"])]
    out.append(
        Paragraph(
            f"This journal has <b>{len(named)}</b> Specialty Sections covering "
            f"{sec.get('n_with_section', 0)} of {sec.get('n_scatter', 0)} papers. Read "
            "per-section OOS from <i>neurorobotics_oos_by_section_taxonomy.csv</i> and compare "
            "each section's launch date against the drift onset before attributing the shift.",
            s["body"],
        )
    )
    return out


def rt_launch_block(rt_sum: dict, sec: dict, s: dict) -> list:
    """Attribute drift to Research Topic launches, the only launch unit that exists here."""
    la = rt_sum.get("launch_attribution") or {}
    out = [Paragraph("5.4 Did a Research Topic launch cause the drift?", s["h2"])]
    if not la:
        out.append(
            Paragraph(
                "Launch attribution not available — re-run <i>python src/scope_drift/analyze_rts.py</i>.",
                s["body"],
            )
        )
        return out

    verdict = la.get("verdict")
    onset = la.get("onset_year")
    window = la.get("onset_window") or []
    net = la.get("onset_net_pull", 0)
    first_cv = la.get("first_cv_heavy_cohort")
    lead = {
        "one launch dominates": "<b>Yes — a single launch accounts for most of the pull.</b>",
        "a small group of launches": "<b>Partly — a handful of launches accounts for half the pull.</b>",
        "launches followed the drift": "<b>No — the vision-heavy launches came after the drift, not before it.</b>",
        "no single launch": "<b>No single launch explains it.</b>",
    }.get(verdict, "<b>No measurable Research Topic pull toward computer vision.</b>")

    out.append(
        Paragraph(
            f"{lead} There are no Specialty Sections to test — all "
            f"{sec.get('n_scatter', 0):,} papers sit directly under the Specialty Journal with a null "
            "section — so the Research Topic is the only structural launch unit available.",
            s["body"],
        )
    )
    out.append(
        Paragraph(
            f"<b>The pull is spread thin.</b> Of the topics that pull toward computer vision "
            f"({la.get('n_rts_with_pull', 0)} of them, {la.get('total_pull', 0)} net CV papers between "
            f"them), the largest single topic accounts for <b>{la.get('top1_share', 0)}%</b> and the "
            f"top three for <b>{la.get('top3_share', 0)}%</b>. It takes "
            f"<b>{la.get('n_to_half', 0)}</b> separate topics to reach half the total. No one "
            "commissioning decision is large enough to have moved the journal on its own.",
            s["body"],
        )
    )
    if onset and first_cv:
        out.append(
            Paragraph(
                f"<b>The timing rules out causation.</b> Drift starts in <b>{onset}</b>, but the "
                f"{la.get('n_rts_launched_at_onset', 0)} topics launched in "
                f"{window[0] if window else onset}–{onset} are net <b>{net:+d}</b> papers — they lean "
                f"toward neuroscience, not away from it. The first launch cohort with a clear vision "
                f"tilt is <b>{first_cv}</b>, a year later. Research Topics amplified and entrenched a "
                "shift that was already under way rather than starting it.",
                s["body"],
            )
        )

    cohorts = [c for c in (la.get("cohorts") or []) if (c.get("papers") or 0) >= 10]
    if cohorts:
        out.append(
            data_table(
                ["Launch year", "RTs", "Papers", "CV%", "Neuro%", "Net CV pull"],
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
                [34 * mm, 22 * mm, 28 * mm, 30 * mm, 30 * mm, 34 * mm],
                s,
            )
        )
        out.append(Spacer(1, 3 * mm))

    top = la.get("top_launches") or []
    if top:
        out.append(
            Paragraph(
                "<b>Largest individual contributors</b> (net CV papers, share of total pull):",
                s["body"],
            )
        )
        out.append(
            ListFlowable(
                [
                    ListItem(
                        Paragraph(
                            f"<b>{r.get('research_topic_title') or ''}</b> — launched "
                            f"{int(float(r['rt_launch_year']))}, n={int(r['n'])}, "
                            f"net {int(r['drift_pull']):+d} ({r.get('pull_share', 0)}% of pull) · "
                            f"{r.get('rt_stage') or 'Unknown'}",
                            s["bullet"],
                        )
                    )
                    for r in top[:5]
                ],
                bulletType="bullet",
                leftIndent=12,
                bulletFontSize=8,
            )
        )
        if all(not r.get("rt_is_open") for r in top[:5]):
            out.append(Spacer(1, 2 * mm))
            out.append(
                Paragraph(
                    "Every one of these is already closed or completed, so none of them is an "
                    "action on its own. The lever is the commissioning standard applied to new "
                    "topics (§5.3) and to the renewal of recurring series.",
                    s["body"],
                )
            )
    sa = rt_sum.get("series_attribution") or {}
    if sa.get("n_multi_volume"):
        out.append(
            Paragraph(
                f"<b>Series concentrate what single topics do not.</b> Rolling recurring volumes up "
                f"into their series, the largest one accounts for <b>{sa.get('top_series_share', 0)}%</b> "
                f"of the pull — nearly double the biggest individual topic — and the "
                f"{sa.get('n_multi_volume')} multi-volume series together carry "
                f"<b>{sa.get('multi_volume_pull_share', 0)}%</b>. Drift is a commissioning pattern that "
                "repeats, which is what makes it addressable (§7).",
                s["body"],
            )
        )
    return out


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
    story.append(Spacer(1, 80 * mm))
    story.append(Paragraph("Frontiers in Neurorobotics", s["cover_title"]))
    story.append(Paragraph("Scope drift deep-dive & editorial options", s["cover_sub"]))
    story.append(Spacer(1, 5 * mm))
    story.append(cover_rule())
    story.append(Spacer(1, 5 * mm))
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
            "This brief separates <b>historic attribution (2020–2025)</b> from the "
            "<b>current actionable position</b>. Historic RTs explain how the journal drifted; they "
            "do not generate actions once they are closed or completed. Recommendations cover only "
            "RTs currently marked <b>Online</b> in RDM, scored on every paper they have published.",
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

    story.append(Paragraph("2. Historic narrative (2020–2025)", s["h1"]))
    story.append(Paragraph("2.1 When did drift start?", s["h2"]))
    story.append(
        Paragraph(
            f"JSD jumps in <b>{onset or 2021}</b> (0 → ~0.23), then climbs through 2023–2025 to "
            f"<b>{latest_jsd:.2f}</b> in 2026. The historic attribution window is 2020–2025; "
            "2026 is shown as current YTD context and is not folded into the retrospective.",
            s["body"],
        )
    )
    story.append(scaled(jsd_path))
    story.append(Spacer(1, 2 * mm))

    story.append(Paragraph("2.2 How did the journal drift?", s["h2"]))
    story.append(
        Paragraph(
            "Primary community <b>IDs are unchanged</b> (Computer vision, Therapeutic Movement Sciences, "
            "Autonomous Systems &amp; Control, Neuroscience), but <b>shares flipped</b>: vision rose from "
            "~16% (2020) to ~40%+ (2025–26); neuroscience fell from ~21% to ~6–7%.",
            s["body"],
        )
    )
    story.append(scaled(share_path))
    story.append(Spacer(1, 3 * mm))

    story.append(
        data_table(
            ["Year", "n", "OOS%", "CV%", "TMS%", "Auto%", "Neuro%"],
            [
                [
                    str(r["year"]),
                    str(r["articles"]),
                    f"{r['oos_pct']:.1f}",
                    f"{r['Computer vision']:.1f}",
                    f"{r['Therapeutic Movement Sciences']:.1f}",
                    f"{r['Autonomous Systems and Control']:.1f}",
                    f"{r['Neuroscience']:.1f}",
                ]
                for r in shares
            ],
            [28 * mm, 22 * mm, 24 * mm, 24 * mm, 26 * mm, 26 * mm, 28 * mm],
            s,
        )
    )
    story.append(Spacer(1, 3 * mm))
    story.append(
        Paragraph(
            f"Primary shift flag (2020→{ps.get('latest_year', 2026)}): "
            f"<b>{'changed' if ps.get('changed') else 'unchanged set'}</b>. "
            "Gain/loss labels: none — drift is reweighting, not replacement of the core set.",
            s["body"],
        )
    )

    story.append(CondPageBreak(60 * mm))
    story.append(Paragraph("3. Is the out-of-scope signal genuine?", s["h1"]))
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
    story.append(Paragraph("3.1 Contested OOS examples (keyword overlap)", s["h2"]))
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
    rt_summary_path = WORK_DIR / "neurorobotics_rt_analysis_summary.json"
    rt_deep_path = WORK_DIR / "neurorobotics_rt_deep_dive.csv"
    if not rt_summary_path.exists():
        raise SystemExit("Missing RT analysis. Run: python src/scope_drift/analyze_rts.py")
    rt_sum = json.loads(rt_summary_path.read_text(encoding="utf-8"))

    story.append(Paragraph("4. Historic RT contribution to drift (pre-2026)", s["h1"]))
    story.append(
        Paragraph(
            "Historic RTs are included here to explain the accumulated change in journal composition. "
            "Drift pull is the number of papers in the Computer Vision community minus Neuroscience "
            "for each RT. A positive value indicates a pull toward the observed CV-heavy mix. "
            "<b>Lifecycle status does not affect attribution, but no recommendation is attached to "
            "a historic RT that is no longer open.</b>",
            s["body"],
        )
    )
    drift_fig = FIG_DIR / "rt_drift_pull.png"
    if drift_fig.exists():
        story.append(scaled(drift_fig, 165 * mm))
        story.append(Spacer(1, 3 * mm))
    historic_drift = rt_sum.get("historic_top_drift_rts") or []
    if historic_drift:
        story.append(
            data_table(
                ["Historic Research Topic", "n", "CV−Neuro", "Current status"],
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

    story.append(CondPageBreak(70 * mm))
    story.append(Paragraph("5. Current RT position and actions", s["h1"]))
    story.append(
        Paragraph(
            rt_sum.get("verdict") or "See src/scope_drift/analyze_rts.py outputs.",
            s["body"],
        )
    )
    story.append(Paragraph("5.1 Online RTs vs spontaneous papers", s["h2"]))
    oos_n = rt_sum.get("open_rt_oos_n", 0)
    cv_n = rt_sum.get("open_rt_cv_n", 0)
    story.append(
        Paragraph(
            f"The {rt_sum.get('n_rts')} currently Online RTs account for "
            f"<b>{rt_sum.get('open_rt_n_papers', 0)}</b> papers in the run, published "
            f"{rt_sum.get('open_rt_first_year', '—')}–{rt_sum.get('open_rt_last_year', '—')}. "
            f"That is the full actionable pool, and it is the same {rt_sum.get('open_rt_n_papers', 0)} "
            "papers broken out topic by topic in the table below. Of them, "
            f"<b>{oos_n}</b> {'is' if oos_n == 1 else 'are'} out of scope and "
            f"<b>{cv_n}</b> {'sits' if cv_n == 1 else 'sit'} in the Computer vision community.",
            s["body"],
        )
    )
    story.append(
        Paragraph(
            f"The rest of the journal is not actionable through RT management: "
            f"<b>{rt_sum.get('closed_rt_n_papers', 0)}</b> papers sit in RTs that are closed, "
            f"completed or deleted, and <b>{rt_sum.get('spontaneous_n_papers', 0)}</b> arrived as "
            "spontaneous submissions. As a benchmark only — the group sizes are very different — "
            f"the open RTs run at {rt_sum.get('open_rt_oos_pct', 0)}% OOS and "
            f"{rt_sum.get('open_rt_cv_pct', 0)}% computer vision, against "
            f"{rt_sum.get('spontaneous_oos_pct', 0)}% and {rt_sum.get('spontaneous_cv_pct', 0)}% "
            f"across all {rt_sum.get('spontaneous_n_papers', 0)} spontaneous papers.",
            s["body"],
        )
    )
    mix_fig = FIG_DIR / "rt_vs_spontaneous_mix.png"
    if mix_fig.exists():
        story.append(scaled(mix_fig, 168 * mm))
        story.append(Spacer(1, 2 * mm))

    story.append(Paragraph("5.2 Currently Online RTs by OOS since launch", s["h2"]))
    intro_52 = (
        "Counts cover every paper each topic has published inside the run window, so an RT that "
        "has been open for several years is judged on its whole output rather than one year."
    )
    oos_fig = FIG_DIR / "rt_top_oos.png"
    n_with_oos = sum(1 for r in (rt_sum.get("current_top_oos_rts") or []) if (r.get("oos_pct") or 0) > 0)
    if not oos_fig.exists():
        intro_52 += (
            f" Out-of-scope work is concentrated in <b>{n_with_oos}</b> of the "
            f"{rt_sum.get('n_rts')} Online topics, so the detail sits in the table rather than a chart."
        )
    story.append(Paragraph(intro_52, s["body"]))
    if oos_fig.exists():
        story.append(scaled(oos_fig, 165 * mm))
        story.append(Spacer(1, 3 * mm))
    top_oos = rt_sum.get("current_top_oos_rts") or []
    if top_oos:
        rows = []
        for r in top_oos[:10]:
            first = r.get("first_year")
            last = r.get("last_year")
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
            data_table(
                ["Research Topic", "Years", "n", "OOS%", "Action"],
                rows,
                [84 * mm, 20 * mm, 12 * mm, 18 * mm, 44 * mm],
                s,
            )
        )

    story.append(Paragraph("5.3 Actions for current Online RTs only", s["h2"]))
    story.append(
        Paragraph(
            f"Heuristic on {rt_sum.get('n_rts')} currently Online RTs with papers in the run: "
            f"<b>{rt_sum.get('n_remove')}</b> remove/do-not-renew or tight-gate; "
            f"<b>{rt_sum.get('n_gate')}</b> gate with robot/embodied requirement; "
            f"<b>{rt_sum.get('n_keep_grow')}</b> keep/audit and "
            f"<b>{rt_sum.get('n_watch')}</b> watch because n&lt;3. Closed, completed and deleted RTs are "
            "excluded even when they contributed strongly to historic drift.",
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
                        f"<b>{r.get('research_topic_title') or ''}</b> — "
                        f"n={r.get('n')}, OOS {r.get('oos_pct')}% · {r.get('recommendation')}",
                        s["bullet"],
                    )
                )
            )
        story.append(Paragraph("<b>Close / gate current Online RTs (priority):</b>", s["body"]))
        story.append(ListFlowable(bullets, bulletType="bullet", leftIndent=12, bulletFontSize=8))
    watch_list = rt_sum.get("watch_list") or []
    if watch_list:
        story.append(Paragraph("<b>Watch — too few papers so far to act on:</b>", s["body"]))
        story.append(
            ListFlowable(
                [
                    ListItem(
                        Paragraph(
                            f"<b>{r.get('research_topic_title') or ''}</b> — "
                            f"n={r.get('n')}, OOS {r.get('oos_pct')}%",
                            s["bullet"],
                        )
                    )
                    for r in watch_list
                ],
                bulletType="bullet",
                leftIndent=12,
                bulletFontSize=8,
            )
        )
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
            "Historic table: <i>neurorobotics_rt_historic_drift.csv</i>. "
            "Current action table: <i>neurorobotics_current_open_rt.csv</i>. "
            "(re-run <i>python src/scope_drift/analyze_rts.py</i>).",
            s["small"],
        )
    )

    story.append(CondPageBreak(70 * mm))
    story.extend(launch_attribution_section(rt_sum, s))

    recent_period = rt_sum.get("recent_period", "2024-2026").replace("-", "–")
    recent_n = rt_sum.get("recent_n_papers", 0)
    story.append(CondPageBreak(80 * mm))
    story.append(Paragraph("6. Current editorial options", s["h1"]))
    story.append(
        Paragraph(
            f"These options are judged on the <b>{recent_period}</b> window — "
            f"<b>{recent_n}</b> papers, the journal's recent output regardless of whether the "
            "publishing RT is still open. That is a wider base than the RT actions in §5, which stay "
            "restricted to topics you can still act on. The three questions below are the journal-level "
            "calls — expand, rename, add sections. Launch-vs-drift attribution sits in §5.4.",
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
                f"{r.get('cv_pct')}%",
                f"{r.get('neuro_pct')}%",
            ]
            for r in recent_rows
        ]
        rows.append(
            [
                f"<b>{recent_period}</b>",
                f"<b>{recent_n}</b>",
                f"<b>{rt_sum.get('recent_oos_pct', 0)}%</b>",
                f"<b>{rt_sum.get('recent_cv_pct', 0)}%</b>",
                f"<b>{rt_sum.get('recent_neuro_pct', 0)}%</b>",
            ]
        )
        story.append(
            data_table(
                ["Year", "n", "OOS%", "CV%", "Neuro%"],
                rows,
                [38 * mm, 30 * mm, 36 * mm, 36 * mm, 38 * mm],
                s,
                last_row_bold=True,
            )
        )
        story.append(Spacer(1, 3 * mm))

    story.append(Paragraph("6.1 Expand scope?", s["h2"]))
    story.append(
        Paragraph(
            f"<b>Yes, selectively.</b> Across {recent_period}, computer vision is "
            f"<b>{rt_sum.get('recent_cv_pct', 0)}%</b> of output against "
            f"<b>{rt_sum.get('recent_neuro_pct', 0)}%</b> for neuroscience, with "
            f"{rt_sum.get('recent_tms_pct', 0)}% therapeutic movement and "
            f"{rt_sum.get('recent_auto_pct', 0)}% autonomous systems. Formalise what the journal "
            "already publishes — embodied / robot vision and learning, therapeutic and assistive "
            "robotics, neural interfaces to robot control — and gate it on a robot, embodied agent "
            "or neural–motor loop. <b>Do not</b> expand into materials, IoT cybersecurity, traffic "
            "forecasting or generic NLP, which make up much of the "
            f"{rt_sum.get('recent_oos_pct', 0)}% out-of-scope rate in this window.",
            s["body"],
        )
    )
    story.extend(rename_options_block(rt_sum, recent_period, recent_n, s))
    story.append(Paragraph("6.3 New sections?", s["h2"]))
    story.append(
        Paragraph(
            f"{'Sections already exist' if section_state()[1] else 'There are no existing Specialty Sections'}. "
            f"On the {recent_period} mix, a workable "
            "forward architecture is: 1) neural interfaces and motor neuroscience · 2) therapeutic "
            "and assistive robotics · 3) embodied vision and multimodal perception · 4) learning and "
            "control for physical agents. Gate 3 and 4 on a robot, embodied agent or neural–motor "
            "loop. These are <b>proposed future sections</b>, not an explanation of past drift "
            "(see §5.4).",
            s["body"],
        )
    )

    story.append(CondPageBreak(60 * mm))
    story.extend(decisions_section(rt_sum, recent_period, recent_n, s))
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
