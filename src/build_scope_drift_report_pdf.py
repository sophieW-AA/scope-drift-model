"""
Build Journal Scope Drift Report PDF from dashboard HTML outputs.

Reads:
  output/scope_dashboard.html
  output/drift_dashboard.html

Writes:
  output/Scope_Drift_Report.pdf

Layout and wording match the existing Scope_Drift_Report PDF
(Sophie Wilson · Journal Scope Drift Report). Do not redesign.

Usage:
  python scripts/build_scope_drift_report_pdf.py
"""

from __future__ import annotations

import argparse
import io
import json
import os
from datetime import datetime
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import (
    Flowable,
    Image,
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

DASH_DIR = Path(r"C:\Users\sophie.wilson\Documents\scope_drift_outputs\dashboards")
SCOPE_HTML = DASH_DIR / "scope_dashboard.html"
DRIFT_HTML = DASH_DIR / "drift_dashboard.html"
OUT_PDF = DASH_DIR / "Scope_Drift_Report.pdf"

AUTHOR = os.environ.get("REPORT_AUTHOR", "Sophie Wilson")

# Visual tokens matching the reference ReportLab PDF
NAVY = colors.HexColor("#0b1f3a")
BLUE = colors.HexColor("#1a4f8c")
KPI_BLUE = colors.HexColor("#1f4e8c")
MUTED = colors.HexColor("#6b7280")
RULE = colors.HexColor("#d1d5db")
CARD_BG = colors.white
SOFT_BG = colors.HexColor("#f5f7fb")
NOTE_BG = colors.HexColor("#fbf6e9")
NOTE_BORDER = colors.HexColor("#c9a227")
ACCENT_LINE = colors.HexColor("#1f4e8c")
IN_GREEN = colors.HexColor("#1f8a4c")
OUT_RED = colors.HexColor("#c93030")
HIGH = colors.HexColor("#c93030")
MOD = colors.HexColor("#d97706")
LOW = colors.HexColor("#1f8a4c")
WHITE = colors.white
BLACK = colors.HexColor("#1a1f36")
TH_GREY = colors.HexColor("#6b7280")


def load_js_const(
    path: Path,
    markers: tuple[str, ...] = ("const DATA = ", "const D=", "const D = ", "const D={"),
) -> dict:
    text = path.read_text(encoding="utf-8")
    for marker in markers:
        i = text.find(marker)
        if i >= 0:
            # For "const D={" the JSON starts at "{"
            start = i + len(marker)
            if marker.endswith("{"):
                start = i + len(marker) - 1
            data, _ = json.JSONDecoder().raw_decode(text, start)
            return data
    raise ValueError(f"No DATA/D JSON found in {path}")


def short_journal(name: str) -> str:
    return name.replace("Frontiers in ", "Fr. ")


def bare_journal(name: str) -> str:
    return name.replace("Frontiers in ", "")


def drift_band(jsd: float) -> str:
    # Band on 3-dp rounded JSD so 0.280 displays and labels consistently.
    j = round(float(jsd), 3)
    if j >= 0.34:
        return "High"
    if j >= 0.28:
        return "Moderate"
    return "Low"


def fmt_int(n: int) -> str:
    return f"{n:,}"


def fmt_pct(x: float) -> str:
    return f"{x:.1f}%"


def fmt_jsd(x: float) -> str:
    return f"{x:.3f}"


def fmt_entropy(x: float) -> str:
    sign = "+" if x > 0 else ""
    if abs(x) < 0.1:
        return f"{sign}{x:.4g}"
    return f"{sign}{x:.4f}".rstrip("0").rstrip(".")


def oos_trend_phrase(j: dict) -> str:
    series = j.get("oos_by_year") or []
    if len(series) < 2:
        return "stayed similar"
    first = float(series[0].get("out_of_scope_pct") or 0)
    last = float(series[-1].get("out_of_scope_pct") or 0)
    if last > first + 0.5:
        return "risen"
    if last < first - 0.5:
        return "fallen"
    return "stayed similar"


def entropy_phrase(delta: float) -> str:
    if delta <= -0.08:
        return (
            "At the same time, the journal is concentrating more tightly around a smaller "
            "set of themes rather than spreading out."
        )
    if delta >= 0.08:
        return (
            "The journal is also spreading across a wider range of topics rather than "
            "staying tightly focused."
        )
    return "The spread of topics it covers has stayed fairly stable."


def community_in_scope(c: dict) -> bool:
    if c.get("is_in_scope") is not None:
        return bool(c.get("is_in_scope"))
    return bool(c.get("is_primary") or c.get("is_borderline"))


def top_oos_labels(j: dict, n: int = 2) -> str:
    oos = [c for c in (j.get("top_communities") or []) if not community_in_scope(c)]
    oos = sorted(oos, key=lambda c: -int(c.get("papers_in_comm") or 0))
    labels = [c.get("label") or f"Cluster {c.get('comm_id')}" for c in oos[:n]]
    if not labels:
        return "peripheral topics"
    if len(labels) == 1:
        return labels[0]
    return f"{labels[0]}, {labels[1]}"


def _join_labels(labels: list[str], limit: int = 3) -> str:
    labels = [str(x).strip() for x in labels if str(x).strip()][:limit]
    if not labels:
        return "its main topics"
    if len(labels) == 1:
        return labels[0]
    if len(labels) == 2:
        return f"{labels[0]} and {labels[1]}"
    return f"{', '.join(labels[:-1])}, and {labels[-1]}"


def primary_shift_sentence(j: dict, short: str) -> str:
    """One sentence on whether primary clusters changed since ~2020 and where they went."""
    ps = j.get("primary_shift") or {}
    if not ps or ps.get("insufficient_data"):
        return (
            f"There is not enough year-level volume to say cleanly whether "
            f"{short}'s primary clusters have changed since 2020."
        )

    by = int(ps.get("baseline_year") or 2020)
    ly = int(ps.get("latest_year") or 2026)
    base_labels = [r.get("label") for r in (ps.get("baseline_top") or [])]
    late_labels = [r.get("label") for r in (ps.get("latest_top") or [])]
    gained = [x for x in (ps.get("gained_labels") or []) if x]
    lost = [x for x in (ps.get("lost_labels") or []) if x]
    changed = ps.get("changed")

    if changed is False:
        return (
            f"Its primary clusters have not meaningfully changed since {by} — "
            f"still centred on {_join_labels(base_labels or late_labels)}."
        )

    # changed or unknown-but-present
    bits = [f"Its primary clusters have changed since {by}."]
    if lost:
        bits.append(f"Areas that have left the core include {_join_labels(lost, 2)}.")
    if gained:
        bits.append(f"Newer core areas include {_join_labels(gained, 2)}.")
    bits.append(
        f"In {ly} the largest core topics are {_join_labels(late_labels)} "
        f"(versus {_join_labels(base_labels)} in {by})."
    )
    return " ".join(bits)


def commentary(j: dict, jsd: float, entropy_delta: float, band: str) -> list[str]:
    short = bare_journal(j["name"])
    arts = int(j.get("articles") or 0)
    oos = int(j.get("out_of_scope") or 0)
    oos_pct = float(j.get("out_of_scope_pct") or 0)
    trend = oos_trend_phrase(j)
    top_label = (j.get("top_communities") or [{}])[0].get("label") or "its main topic"
    oos_topics = top_oos_labels(j)

    if band == "High":
        p1 = (
            f"{short} shows the clearest signs of scope movement in this review. "
            f"Compared with where the journal stood in 2020, the mix of research it "
            f"publishes has shifted noticeably — a change of this size (JSD {jsd:.2f}) "
            f"means the papers coming in today look meaningfully different from the "
            f"ones that defined the journal a few years ago."
        )
    elif band == "Moderate":
        p1 = (
            f"{short} is showing a moderate amount of movement away from its 2020 "
            f"starting point (JSD {jsd:.2f}). This isn't dramatic, but the journal's "
            f"content mix has evolved enough to be worth keeping an eye on."
        )
    else:
        p1 = (
            f"{short} remains close to its original scope. Its content mix has changed "
            f"only slightly since 2020 (JSD {jsd:.2f}), which suggests the journal is "
            f"publishing consistently within its intended focus."
        )

    if trend == "risen":
        trend_clause = "This out-of-scope share has risen since 2020."
    elif trend == "fallen":
        trend_clause = "This out-of-scope share has fallen since 2020."
    else:
        trend_clause = "This out-of-scope share has stayed similar since 2020."

    p2 = (
        f"Right now, about {round(oos_pct)}% of {short}'s papers ({fmt_int(oos)} out of "
        f"{fmt_int(arts)}) fall outside its core subject clusters — mostly work related to "
        f"{oos_topics}. {trend_clause} {entropy_phrase(entropy_delta)} Its largest single "
        f"topic area today is “{top_label}.” {primary_shift_sentence(j, short)}"
    )
    return [p1, p2]


def example_split(
    j: dict, n: int = 5, prefer_year: int = 2026
) -> tuple[list[str], list[str]]:
    """Prefer prefer_year titles; fill from more recent years, then older.

    Out-of-scope prefers really-OOS examples in prefer_year: clear flags
    (hard_negative / paper_demoted), then titles that do not look on-topic.
    """
    examples = j.get("example_papers") or []

    def _oos_rank(e: dict) -> tuple:
        clear = (
            1
            if (e.get("clear_oos") or e.get("hard_negative") or e.get("paper_demoted"))
            else 0
        )
        # Prefer titles that do NOT still look on-scope for the journal.
        off_topic = 0 if e.get("title_on_scope") else 1
        foreign = 1 if e.get("foreign_community") else 0
        return (
            0 if e.get("year") == prefer_year else 1,
            -clear,
            -off_topic,
            -foreign,
            -(int(e.get("year") or 0)),
        )

    def _pick(in_scope: bool) -> list[str]:
        pool = [e for e in examples if bool(e.get("is_in_scope")) == in_scope]
        if in_scope:
            preferred = [e for e in pool if e.get("year") == prefer_year]
            rest = sorted(
                [e for e in pool if e.get("year") != prefer_year],
                key=lambda e: -(int(e.get("year") or 0)),
            )
            ordered = preferred + rest
        else:
            ordered = sorted(pool, key=_oos_rank)
        titles = [str(e.get("title") or "") for e in ordered]
        return [t for t in titles if t][:n]

    return _pick(True), _pick(False)


def build_rows(scope: dict, drift: dict) -> list[dict]:
    by_name = {j["name"]: j for j in scope.get("journals") or []}
    summary = list(drift.get("summary") or [])
    # Journal detail pages stay ordered by drift (JSD desc).
    summary.sort(key=lambda r: -float(r.get("JSD") or 0))
    rows = []
    for s in summary:
        name = s["Journal"]
        j = by_name.get(name)
        if not j:
            continue
        jsd = float(s.get("JSD") or 0)
        rows.append(
            {
                "journal": j,
                "jsd": jsd,
                "entropy_delta": float(s.get("EntropyDelta") or 0),
                "band": drift_band(jsd),
                "year": int(s.get("Year") or 2026),
                "oos_pct": float(j.get("out_of_scope_pct") or 0),
            }
        )
    return rows


def rows_by_oos(rows: list[dict]) -> list[dict]:
    return sorted(rows, key=lambda r: -float(r.get("oos_pct") or 0))


def kpi_block(scope: dict, rows: list[dict]) -> dict:
    journals = scope.get("journals") or []
    total_papers = sum(int(j.get("articles") or 0) for j in journals)
    total_oos = sum(int(j.get("out_of_scope") or 0) for j in journals)
    oos_pct = (100.0 * total_oos / total_papers) if total_papers else 0.0
    high = sum(1 for r in rows if r["band"] == "High")
    mean_jsd = (sum(r["jsd"] for r in rows) / len(rows)) if rows else 0.0
    return {
        "total_papers": total_papers,
        "oos_pct": oos_pct,
        "high_drift": high,
        "n_journals": len(rows),
        "mean_jsd": mean_jsd,
    }


def join_names(names: list[str]) -> str:
    if not names:
        return "none"
    if len(names) == 1:
        return names[0]
    if len(names) == 2:
        return f"{names[0]} and {names[1]}"
    return ", ".join(names[:-1]) + f" and {names[-1]}"


def executive_summary(kpis: dict, rows: list[dict], start_y: int) -> str:
    high_names = [
        bare_journal(r["journal"]["name"]) for r in rows if r["band"] == "High"
    ]
    if kpis["oos_pct"] > 0:
        one_in = max(2, round(100.0 / kpis["oos_pct"]))
        oos_phrase = f"about 1 in {one_in} papers ({fmt_pct(kpis['oos_pct'])})"
    else:
        oos_phrase = "no papers"
    n_high = len(high_names)
    n_word = {1: "One journal", 2: "Two journals", 3: "Three journals"}.get(
        n_high, f"{n_high} journals"
    )
    high_bit = ""
    if high_names:
        high_bit = (
            f" {n_word} — {join_names(high_names)} — have moved the furthest from their "
            f"original focus."
        )
    return (
        f"This report looks at {kpis['n_journals']} Frontiers journals and asks a simple "
        f"question: is the type of research each one publishes drifting away from where it "
        f"started in {start_y}? Across all of them, {oos_phrase} now falls outside the "
        f"journal's core subject areas.{high_bit} A page of plain-language commentary and "
        f"supporting detail follows for each journal."
    )


def esc(s: str) -> str:
    return str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


class Badge(Flowable):
    def __init__(self, text: str, band: str, height: float = 14):
        super().__init__()
        self.text = text
        self.band = band
        self.height = height
        self.width = 58 if band != "Moderate" else 72

    def wrap(self, availWidth, availHeight):
        return self.width, self.height

    def draw(self):
        fill = {"High": HIGH, "Moderate": MOD, "Low": LOW}.get(self.band, MUTED)
        self.canv.setFillColor(fill)
        self.canv.roundRect(0, 0, self.width, self.height, 7, fill=1, stroke=0)
        self.canv.setFillColor(WHITE if self.band != "Moderate" else BLACK)
        self.canv.setFont("Helvetica-Bold", 8)
        self.canv.drawCentredString(self.width / 2, 3.5, self.text)


def make_styles() -> dict:
    base = getSampleStyleSheet()
    styles = {
        "title": ParagraphStyle(
            "RTitle",
            parent=base["Normal"],
            fontName="Helvetica-Bold",
            fontSize=22,
            leading=26,
            textColor=NAVY,
            spaceAfter=4,
        ),
        "subhead": ParagraphStyle(
            "RSub",
            parent=base["Normal"],
            fontName="Helvetica",
            fontSize=8.5,
            leading=11,
            textColor=MUTED,
            spaceAfter=6,
        ),
        "h2": ParagraphStyle(
            "RH2",
            parent=base["Normal"],
            fontName="Helvetica-Bold",
            fontSize=11,
            leading=14,
            textColor=NAVY,
            spaceBefore=12,
            spaceAfter=6,
        ),
        "body": ParagraphStyle(
            "RBody",
            parent=base["Normal"],
            fontName="Helvetica",
            fontSize=9.5,
            leading=13,
            textColor=BLACK,
            spaceAfter=8,
            alignment=TA_LEFT,
        ),
        "note": ParagraphStyle(
            "RNote",
            parent=base["Normal"],
            fontName="Helvetica",
            fontSize=7.5,
            leading=10,
            textColor=colors.HexColor("#5c5346"),
        ),
        "kpi_v": ParagraphStyle(
            "RKpiV",
            parent=base["Normal"],
            fontName="Helvetica-Bold",
            fontSize=16,
            leading=19,
            textColor=KPI_BLUE,
            alignment=TA_LEFT,
        ),
        "kpi_l": ParagraphStyle(
            "RKpiL",
            parent=base["Normal"],
            fontName="Helvetica",
            fontSize=8,
            leading=10,
            textColor=MUTED,
        ),
        "th": ParagraphStyle(
            "RTh",
            parent=base["Normal"],
            fontName="Helvetica",
            fontSize=8,
            leading=10,
            textColor=TH_GREY,
        ),
        "td": ParagraphStyle(
            "RTd",
            parent=base["Normal"],
            fontName="Helvetica",
            fontSize=8.5,
            leading=11,
            textColor=BLACK,
        ),
        "td_r": ParagraphStyle(
            "RTdR",
            parent=base["Normal"],
            fontName="Helvetica",
            fontSize=8.5,
            leading=11,
            textColor=BLACK,
            alignment=TA_RIGHT,
        ),
        "drift_high": ParagraphStyle(
            "RDriftH",
            parent=base["Normal"],
            fontName="Helvetica-Bold",
            fontSize=8.5,
            leading=11,
            textColor=HIGH,
        ),
        "drift_mod": ParagraphStyle(
            "RDriftM",
            parent=base["Normal"],
            fontName="Helvetica-Bold",
            fontSize=8.5,
            leading=11,
            textColor=MOD,
        ),
        "drift_low": ParagraphStyle(
            "RDriftL",
            parent=base["Normal"],
            fontName="Helvetica-Bold",
            fontSize=8.5,
            leading=11,
            textColor=LOW,
        ),
        "td_in": ParagraphStyle(
            "RTdIn",
            parent=base["Normal"],
            fontName="Helvetica-Bold",
            fontSize=8,
            leading=10,
            textColor=IN_GREEN,
        ),
        "td_out": ParagraphStyle(
            "RTdOut",
            parent=base["Normal"],
            fontName="Helvetica-Bold",
            fontSize=8,
            leading=10,
            textColor=OUT_RED,
        ),
        "journal": ParagraphStyle(
            "RJournal",
            parent=base["Normal"],
            fontName="Helvetica-Bold",
            fontSize=14,
            leading=18,
            textColor=NAVY,
        ),
        "ex_h": ParagraphStyle(
            "RExH",
            parent=base["Normal"],
            fontName="Helvetica-Bold",
            fontSize=9,
            leading=11,
            spaceAfter=4,
        ),
        "ex": ParagraphStyle(
            "REx",
            parent=base["Normal"],
            fontName="Helvetica",
            fontSize=7.5,
            leading=9.5,
            textColor=BLACK,
            leftIndent=8,
            bulletIndent=0,
        ),
        "split_v": ParagraphStyle(
            "RSplitV",
            parent=base["Normal"],
            fontName="Helvetica-Bold",
            fontSize=10,
            leading=12,
            textColor=NAVY,
            alignment=TA_CENTER,
        ),
        "split_l": ParagraphStyle(
            "RSplitL",
            parent=base["Normal"],
            fontName="Helvetica",
            fontSize=6.5,
            leading=8,
            textColor=MUTED,
            alignment=TA_CENTER,
        ),
    }
    return styles


class AccentRule(Flowable):
    """Thick blue rule under the cover title block."""

    def __init__(self, width: float = 168 * mm, height: float = 2.2):
        super().__init__()
        self.width = width
        self.height = height

    def wrap(self, availWidth, availHeight):
        return self.width, self.height + 6

    def draw(self):
        self.canv.setFillColor(ACCENT_LINE)
        self.canv.rect(0, 4, self.width, self.height, fill=1, stroke=0)


def kpi_table(kpis: dict, end_y: int, styles: dict) -> Table:
    cells = [
        [
            [
                Paragraph(fmt_int(kpis["total_papers"]), styles["kpi_v"]),
                Paragraph("Papers analysed", styles["kpi_l"]),
            ],
            [
                Paragraph(fmt_pct(kpis["oos_pct"]), styles["kpi_v"]),
                Paragraph("Overall out-of-scope", styles["kpi_l"]),
            ],
            [
                Paragraph(
                    f"{kpis['high_drift']} / {kpis['n_journals']}", styles["kpi_v"]
                ),
                Paragraph("High-drift journals", styles["kpi_l"]),
            ],
            [
                Paragraph(fmt_jsd(kpis["mean_jsd"]), styles["kpi_v"]),
                Paragraph(f"Mean JSD {end_y}", styles["kpi_l"]),
            ],
        ]
    ]
    t = Table(cells, colWidths=[42 * mm, 42 * mm, 42 * mm, 42 * mm], hAlign="LEFT")
    t.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), WHITE),
                ("BOX", (0, 0), (-1, -1), 0.6, RULE),
                ("INNERGRID", (0, 0), (-1, -1), 0.6, RULE),
                ("LEFTPADDING", (0, 0), (-1, -1), 10),
                ("RIGHTPADDING", (0, 0), (-1, -1), 10),
                ("TOPPADDING", (0, 0), (-1, -1), 10),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ]
        )
    )
    return t


def summary_table(rows: list[dict], end_y: int, styles: dict) -> Table:
    header = [
        Paragraph("Journal", styles["th"]),
        Paragraph("Papers", styles["th"]),
        Paragraph("OOS", styles["th"]),
        Paragraph("OOS %", styles["th"]),
        Paragraph(f"JSD {end_y}", styles["th"]),
        Paragraph("Drift", styles["th"]),
    ]
    data = [header]
    band_style = {
        "High": styles["drift_high"],
        "Moderate": styles["drift_mod"],
        "Low": styles["drift_low"],
    }
    for r in rows_by_oos(rows):
        j = r["journal"]
        data.append(
            [
                Paragraph(esc(short_journal(j["name"])), styles["td"]),
                Paragraph(fmt_int(int(j.get("articles") or 0)), styles["td_r"]),
                Paragraph(fmt_int(int(j.get("out_of_scope") or 0)), styles["td_r"]),
                Paragraph(
                    fmt_pct(float(j.get("out_of_scope_pct") or 0)), styles["td_r"]
                ),
                Paragraph(fmt_jsd(r["jsd"]), styles["td_r"]),
                Paragraph(esc(r["band"]), band_style.get(r["band"], styles["td"])),
            ]
        )
    t = Table(data, colWidths=[55 * mm, 22 * mm, 22 * mm, 22 * mm, 24 * mm, 23 * mm])
    style_cmds = [
        ("LINEBELOW", (0, 0), (-1, 0), 0.8, RULE),
        ("LINEBELOW", (0, 1), (-1, -2), 0.4, RULE),
        ("LINEBELOW", (0, -1), (-1, -1), 0.8, RULE),
        ("LEFTPADDING", (0, 0), (-1, -1), 4),
        ("RIGHTPADDING", (0, 0), (-1, -1), 4),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("ALIGN", (1, 0), (4, -1), "RIGHT"),
    ]
    t.setStyle(TableStyle(style_cmds))
    return t


def note_box(styles: dict) -> Table:
    text = (
        "<b>A note on how to read this report:</b> This analysis is based purely on "
        "citation patterns (which papers cite which), not on reading the papers "
        "themselves. Citation-based methods like this can misclassify certain paper "
        "types — methods papers and meta-analyses in particular tend to cite (and be "
        "cited by) a much wider range of fields than their own subject matter would "
        "suggest, so they can appear more “out-of-scope” than they really are. Scope "
        "itself is also defined statistically here: a journal's “primary” clusters are "
        "simply whichever citation communities together account for 80% of its papers. "
        "This threshold is applied uniformly across all journals and hasn't been tuned "
        "per journal, so some journals may need a different cutoff to reflect their "
        "actual editorial scope. Treat the figures below as a useful signal for further "
        "investigation, not a definitive scope audit."
    )
    inner = Table([[Paragraph(text, styles["note"])]], colWidths=[168 * mm])
    inner.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), NOTE_BG),
                ("BOX", (0, 0), (-1, -1), 0.8, NOTE_BORDER),
                ("LEFTPADDING", (0, 0), (-1, -1), 10),
                ("RIGHTPADDING", (0, 0), (-1, -1), 10),
                ("TOPPADDING", (0, 0), (-1, -1), 8),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
            ]
        )
    )
    return inner


class ScopeSplitBar(Flowable):
    """Stacked in-scope / OOS bar matching the reference PDF."""

    def __init__(self, oos_pct: float, width: float = 168 * mm, height: float = 14):
        super().__init__()
        self.oos_pct = max(0.0, min(100.0, float(oos_pct)))
        self.width = width
        self.height = height

    def wrap(self, availWidth, availHeight):
        return self.width, self.height

    def draw(self):
        in_pct = 100.0 - self.oos_pct
        in_w = self.width * in_pct / 100.0
        oos_w = self.width - in_w
        # Full grey base with rounded corners, then blue in-scope overlay
        self.canv.setFillColor(colors.HexColor("#c5cddb"))
        self.canv.roundRect(0, 0, self.width, self.height, 3, fill=1, stroke=0)
        if in_w > 0.5:
            self.canv.setFillColor(colors.HexColor("#2f6fed"))
            self.canv.roundRect(0, 0, in_w, self.height, 3, fill=1, stroke=0)
            if oos_w > 1:
                # square off the right edge of the blue segment
                self.canv.rect(
                    max(in_w - 3, 0), 0, min(3, in_w), self.height, fill=1, stroke=0
                )
        self.canv.setFillColor(WHITE)
        self.canv.setFont("Helvetica-Bold", 8)
        if in_w > 36:
            self.canv.drawString(6, 3.5, f"{in_pct:.0f}% in-scope")
        if oos_w > 28:
            self.canv.setFillColor(NAVY)
            self.canv.drawRightString(self.width - 6, 3.5, f"{self.oos_pct:.0f}% OOS")


def _fig_to_image(fig, width_mm: float, height_mm: float) -> Image:
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=160, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    buf.seek(0)
    img = Image(buf, width=width_mm * mm, height=height_mm * mm)
    return img


def drift_oos_trend_chart(j: dict, jsd_trend: dict | None) -> Image | None:
    """Dual-axis line chart: JSD vs 2020 (left) and OOS % (right)."""
    oos_series = j.get("oos_by_year") or []
    if not oos_series and not jsd_trend:
        return None

    years_oos = [int(p["year"]) for p in oos_series]
    oos_vals = [float(p.get("out_of_scope_pct") or 0) for p in oos_series]

    years_jsd = list((jsd_trend or {}).get("years") or [])
    jsd_vals = list((jsd_trend or {}).get("jsd") or [])

    fig, ax1 = plt.subplots(figsize=(4.2, 2.35))
    ax1.set_title(
        "Drift & OOS trend",
        fontsize=10,
        fontweight="bold",
        color="#0b1f3a",
        loc="left",
        pad=8,
    )
    ax1.set_xlabel("Year", fontsize=8, color="#5a6478")
    ax1.set_ylabel("JSD vs 2020", fontsize=8, color="#1f4e8c")
    ax1.tick_params(axis="both", labelsize=7, colors="#5a6478")
    ax1.spines["top"].set_visible(False)
    ax1.grid(True, axis="y", color="#e2e6ef", linewidth=0.6)

    if years_jsd and jsd_vals:
        ax1.plot(
            years_jsd,
            jsd_vals,
            color="#1f4e8c",
            linewidth=2.0,
            marker="o",
            markersize=3.5,
            label="JSD",
        )
        ax1.set_ylim(0, max(0.4, max(jsd_vals) * 1.15))

    ax2 = ax1.twinx()
    ax2.set_ylabel("OOS %", fontsize=8, color="#d97706")
    ax2.tick_params(axis="y", labelsize=7, colors="#d97706")
    ax2.spines["top"].set_visible(False)
    if years_oos and oos_vals:
        ax2.plot(
            years_oos,
            oos_vals,
            color="#d97706",
            linewidth=2.0,
            marker="o",
            markersize=3.5,
            label="OOS %",
        )
        ax2.set_ylim(0, max(20, max(oos_vals) * 1.25))

    all_years = sorted(set(years_jsd) | set(years_oos))
    if all_years:
        ax1.set_xticks(all_years)
        ax1.set_xlim(all_years[0] - 0.2, all_years[-1] + 0.2)

    fig.tight_layout(pad=0.4)
    return _fig_to_image(fig, 82, 48)


def top_communities_chart(j: dict) -> Image | None:
    """Horizontal bar chart of top communities (green in-scope / red OOS)."""
    comms = (j.get("top_communities") or [])[:6]
    if not comms:
        return None

    labels = []
    shares = []
    bar_colors = []
    for c in reversed(comms):  # top at top of chart
        label = str(c.get("label") or "")
        if len(label) > 22:
            label = label[:21] + "…"
        labels.append(label)
        shares.append(float(c.get("share_of_journal") or 0))
        bar_colors.append("#1f8a4c" if community_in_scope(c) else "#c93030")

    fig, ax = plt.subplots(figsize=(4.2, 2.35))
    ax.set_title(
        "Top communities",
        fontsize=10,
        fontweight="bold",
        color="#0b1f3a",
        loc="left",
        pad=8,
    )
    ax.barh(labels, shares, color=bar_colors, height=0.62)
    ax.set_xlabel("% of journal papers", fontsize=8, color="#5a6478")
    ax.tick_params(axis="both", labelsize=7, colors="#5a6478")
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.grid(True, axis="x", color="#e2e6ef", linewidth=0.6)
    xmax = max(shares) if shares else 10
    ax.set_xlim(0, xmax * 1.15)
    fig.tight_layout(pad=0.4)
    return _fig_to_image(fig, 82, 48)


def charts_row(j: dict, jsd_trend: dict | None) -> Table | None:
    left = drift_oos_trend_chart(j, jsd_trend)
    right = top_communities_chart(j)
    if left is None and right is None:
        return None
    cells = [[left or "", right or ""]]
    t = Table(cells, colWidths=[84 * mm, 84 * mm])
    t.setStyle(
        TableStyle(
            [
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 0),
                ("RIGHTPADDING", (0, 0), (-1, -1), 2),
                ("TOPPADDING", (0, 0), (-1, -1), 2),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
            ]
        )
    )
    return t


def scope_split_table(j: dict, r: dict, end_y: int, styles: dict) -> Table:
    arts = int(j.get("articles") or 0)
    oos = int(j.get("out_of_scope") or 0)
    oos_pct = float(j.get("out_of_scope_pct") or 0)
    n_primary = int(j.get("n_primary_clusters") or 0)
    cov = float(j.get("primary_coverage_pct") or 80.0)
    items = [
        (fmt_int(arts), "Papers"),
        (f"{fmt_int(oos)} ({fmt_pct(oos_pct)})", "Out-of-scope"),
        (fmt_jsd(r["jsd"]), f"JSD {end_y}"),
        (fmt_entropy(r["entropy_delta"]), "Entropy Δ"),
        (str(n_primary), "Primary clusters"),
        (fmt_pct(cov), "Primary coverage"),
    ]
    cells = [
        [
            [Paragraph(v, styles["split_v"]), Paragraph(l, styles["split_l"])]
            for v, l in items
        ]
    ]
    t = Table(cells, colWidths=[28 * mm] * 6)
    t.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), SOFT_BG),
                ("BOX", (0, 0), (-1, -1), 0.4, RULE),
                ("INNERGRID", (0, 0), (-1, -1), 0.4, RULE),
                ("TOPPADDING", (0, 0), (-1, -1), 6),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
                ("LEFTPADDING", (0, 0), (-1, -1), 3),
                ("RIGHTPADDING", (0, 0), (-1, -1), 3),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ]
        )
    )
    return t


def community_table(j: dict, styles: dict) -> Table:
    header = [
        Paragraph("Community", styles["th"]),
        Paragraph("Status", styles["th"]),
        Paragraph("Papers", styles["th"]),
        Paragraph("Share of journal", styles["th"]),
    ]
    data = [header]
    for c in (j.get("top_communities") or [])[:6]:
        in_scope = community_in_scope(c)
        status_style = styles["td_in"] if in_scope else styles["td_out"]
        data.append(
            [
                Paragraph(esc(c.get("label") or ""), styles["td"]),
                Paragraph("In-scope" if in_scope else "Out-of-scope", status_style),
                Paragraph(fmt_int(int(c.get("papers_in_comm") or 0)), styles["td_r"]),
                Paragraph(
                    f"{float(c.get('share_of_journal') or 0):.1f}%", styles["td_r"]
                ),
            ]
        )
    t = Table(data, colWidths=[78 * mm, 30 * mm, 25 * mm, 35 * mm])
    t.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), SOFT_BG),
                ("LINEBELOW", (0, 0), (-1, -1), 0.4, RULE),
                ("LEFTPADDING", (0, 0), (-1, -1), 4),
                ("RIGHTPADDING", (0, 0), (-1, -1), 4),
                ("TOPPADDING", (0, 0), (-1, -1), 3),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ]
        )
    )
    return t


def examples_table(ins: list[str], outs: list[str], styles: dict) -> Table:
    in_paras = [
        Paragraph('<font color="#1f8a4c"><b>In-scope</b></font>', styles["ex_h"])
    ]
    out_paras = [
        Paragraph('<font color="#c93030"><b>Out-of-scope</b></font>', styles["ex_h"])
    ]
    for t in ins:
        in_paras.append(Paragraph(f"• {esc(t)}", styles["ex"]))
    for t in outs:
        out_paras.append(Paragraph(f"• {esc(t)}", styles["ex"]))
    if not ins:
        in_paras.append(Paragraph("• —", styles["ex"]))
    if not outs:
        out_paras.append(Paragraph("• —", styles["ex"]))
    tbl = Table([[in_paras, out_paras]], colWidths=[84 * mm, 84 * mm])
    tbl.setStyle(
        TableStyle(
            [
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 0),
                ("RIGHTPADDING", (0, 0), (-1, -1), 6),
            ]
        )
    )
    return tbl


def journal_title_row(name: str, band: str, styles: dict) -> Table:
    title = Paragraph(esc(name), styles["journal"])
    badge = Badge(band, band)
    t = Table([[title, badge]], colWidths=[140 * mm, 28 * mm])
    t.setStyle(
        TableStyle(
            [
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("ALIGN", (1, 0), (1, 0), "RIGHT"),
                ("LEFTPADDING", (0, 0), (-1, -1), 0),
                ("RIGHTPADDING", (0, 0), (-1, -1), 0),
            ]
        )
    )
    return t


def build_pdf(
    scope: dict,
    drift: dict,
    out_pdf: Path,
    author: str,
    report_date: str,
) -> None:
    rows = build_rows(scope, drift)
    kpis = kpi_block(scope, rows)
    styles = make_styles()
    meta = scope.get("run_metadata") or {}
    run_ts = meta.get("run_timestamp") or os.environ.get("RUN_TIMESTAMP") or ""
    start_y = (
        meta.get("start_year") or (scope.get("meta") or {}).get("year_range", [2020])[0]
    )
    end_y = (
        meta.get("end_year") or (scope.get("meta") or {}).get("year_range", [2026])[-1]
    )
    level = (scope.get("meta") or {}).get("primary_cluster_level") or "macro"
    footer_left = f"{author}  ·  {report_date}"

    page_state = {"n": 0}

    def on_page(canvas, doc):
        page_state["n"] += 1
        canvas.saveState()
        canvas.setFont("Helvetica", 8)
        canvas.setFillColor(MUTED)
        canvas.drawString(18 * mm, A4[1] - 12 * mm, footer_left)
        canvas.drawRightString(
            A4[0] - 18 * mm, A4[1] - 12 * mm, f"Page {page_state['n']}"
        )
        canvas.setStrokeColor(RULE)
        canvas.setLineWidth(0.5)
        canvas.line(18 * mm, A4[1] - 14 * mm, A4[0] - 18 * mm, A4[1] - 14 * mm)
        canvas.restoreState()

    doc = SimpleDocTemplate(
        str(out_pdf),
        pagesize=A4,
        leftMargin=18 * mm,
        rightMargin=18 * mm,
        topMargin=20 * mm,
        bottomMargin=16 * mm,
        title="Journal Scope Drift Report",
        author=author,
    )

    story: list = []
    story.append(Paragraph("Journal Scope Drift Report", styles["title"]))
    story.append(
        Paragraph(
            f"CWTS Leiden citation clustering · {esc(str(level))} level · "
            f"baseline {esc(str(start_y))} → {esc(str(end_y))} · run {esc(str(run_ts))}",
            styles["subhead"],
        )
    )
    story.append(AccentRule())
    story.append(Spacer(1, 8))
    story.append(kpi_table(kpis, int(end_y), styles))
    story.append(Paragraph("Summary", styles["h2"]))
    story.append(
        Paragraph(esc(executive_summary(kpis, rows, int(start_y))), styles["body"])
    )
    story.append(Paragraph("Scope Drift &amp; OOS Summary by Journal", styles["h2"]))
    story.append(summary_table(rows, int(end_y), styles))
    story.append(Spacer(1, 10))
    story.append(note_box(styles))

    for r in rows:
        j = r["journal"]
        paras = commentary(j, r["jsd"], r["entropy_delta"], r["band"])
        # Long titles on these journals overflow; fewer examples keep each to one sheet.
        name = j.get("name") or ""
        n_examples = 3 if ("Environmental Science" in name or "Surgery" in name) else 5
        ins, outs = example_split(j, n=n_examples)
        story.append(PageBreak())
        story.append(journal_title_row(j["name"], r["band"], styles))
        story.append(Spacer(1, 6))
        for p in paras:
            story.append(Paragraph(esc(p), styles["body"]))
        story.append(Paragraph("Scope split", styles["h2"]))
        story.append(ScopeSplitBar(float(j.get("out_of_scope_pct") or 0)))
        story.append(Spacer(1, 4))
        story.append(scope_split_table(j, r, int(end_y), styles))
        jsd_trend = (drift.get("jsd_trends") or {}).get(j["name"])
        charts = charts_row(j, jsd_trend)
        if charts is not None:
            story.append(Spacer(1, 6))
            story.append(charts)
        story.append(Paragraph("Community composition", styles["h2"]))
        story.append(community_table(j, styles))
        story.append(Paragraph("Example papers", styles["h2"]))
        story.append(examples_table(ins, outs, styles))

    out_pdf.parent.mkdir(parents=True, exist_ok=True)
    doc.build(story, onFirstPage=on_page, onLaterPages=on_page)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--scope-html", type=Path, default=SCOPE_HTML)
    ap.add_argument("--drift-html", type=Path, default=DRIFT_HTML)
    ap.add_argument("--out-pdf", type=Path, default=OUT_PDF)
    ap.add_argument("--author", default=AUTHOR)
    ap.add_argument(
        "--date",
        default=datetime.now().strftime("%m/%d"),
        help="Footer date like 07/26",
    )
    args = ap.parse_args()

    if not args.scope_html.exists():
        raise SystemExit(f"Missing {args.scope_html}")
    if not args.drift_html.exists():
        raise SystemExit(f"Missing {args.drift_html}")

    scope = load_js_const(args.scope_html)
    drift = load_js_const(args.drift_html)
    build_pdf(scope, drift, args.out_pdf, args.author, args.date)
    print(
        f"Wrote {args.out_pdf} ({args.out_pdf.stat().st_size / 1024:.1f} KB)",
        flush=True,
    )


if __name__ == "__main__":
    main()
