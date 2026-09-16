"""Build the readable journal-opportunities Excel from a final-run table.

This is the single export for the presentation workbook:

    python src/opportunities/export_workbook.py \\
        --json C:\\path\\to\\final_journal_opportunities_YYYYMMDD.json

It reads the machine table from `final_opportunities.py` (JSON or a DataFrame)
and writes one branded `.xlsx` with human column names, Leiden community-market
text, and concise journal-scope blurbs.

Flow:
    1. Load the 252-row result
    2. Map actions/coverage into readable labels
    3. Write Community market (Leiden) from meso/micro names (no LLM)
    4. Write Journal scope (GPT-4o; template fallback if --skip-llm)
    5. Save the workbook

The analytics themselves are not recomputed here.
"""

from __future__ import annotations

import argparse
import json
import logging
import time
from datetime import date
from pathlib import Path

import pandas as pd
from dotenv import load_dotenv
from openpyxl import Workbook
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter

from .paths import (
    OUTPUT_DIR,
    REPO,
    configure_logging,
    ensure_directories,
    resolve_under,
)

log = logging.getLogger("opportunities.export_workbook")

ACTION_LABEL = {
    "pass_market": "No launch - failed market gate",
    "grow_existing": "Expand existing journal",
    "validate_scope": "Validate scope - do not launch yet",
    "launch_consolidation": "Launch new journal (consolidation)",
    "launch_greenfield": "Launch new journal (greenfield)",
}

COLUMNS = [
    ("Proposed journal", 42),
    ("Subfield", 36),
    ("Domain", 18),
    ("Grade", 10),
    ("Score", 10),
    ("World 2025", 14),
    ("CAGR", 10),
    ("FI 2025", 12),
    ("Share vs parity", 16),
    ("Lead title", 36),
    ("Ownership", 18),
    ("Coverage", 20),
    ("Scope confidence", 16),
    ("Community market (Leiden)", 72),
    ("Journal scope", 78),
    ("Action", 36),
    ("Warning", 48),
]

RESPIRATORY_SCOPE = (
    "Frontiers in Pulmonary and Respiratory Medicine would cover "
    "lung disease, airway critical care, and the diagnostics and "
    "pharmacology used to treat them. In the citation map that core "
    "sits inside a wider clinical-biomedical neighbourhood. Papers "
    "that co-cite with respiratory work also come from oncology, "
    "pathology, cardiology, biomaterials, and clinical pharmacology. "
    "Those belong in the market, not at the fringe. Smaller neighbours "
    "— radiology, anaesthetics, occupational and air-quality health, "
    "microbiome, public health, and some veterinary respiratory work "
    "— are plausible sections, not the centre of the title. This is "
    "not a lungs-only island: oncology is as large a neighbour as "
    "respiratory medicine. A launch needs editorial walls so it does "
    "not become a second Frontiers in Oncology or a generic clinical journal."
)

SCOPE_EXAMPLE = RESPIRATORY_SCOPE


def split_names(val: object, n: int | None = None) -> list[str]:
    if val is None or (isinstance(val, float) and pd.isna(val)):
        return []
    parts = [p.strip() for p in str(val).split(";") if p.strip()]
    parts = [p for p in parts if not p.lower().startswith("micro:")]
    return parts[:n] if n else parts


def oxford(items: list[str]) -> str:
    items = [i for i in items if i]
    if not items:
        return ""
    if len(items) == 1:
        return items[0]
    if len(items) == 2:
        return f"{items[0]} and {items[1]}"
    return ", ".join(items[:-1]) + ", and " + items[-1]


def _readable(value: object) -> str:
    return str(value or "").replace("_", " ").strip()


def community_market(row: pd.Series) -> str:
    """Deterministic Leiden-neighbourhood paragraph."""
    names = split_names(row.get("scope_names"))
    themes = split_names(row.get("section_themes"), 6)
    n = int(row.get("scope_community_count") or 0)
    mapped = int(row.get("mapped_non_fi_papers") or 0)
    cov = row.get("scope_coverage")
    conf = str(row.get("scope_confidence") or "")
    top_share = row.get("top_community_share")
    macro_share = row.get("dominant_macro_share")

    if not bool(row.get("market_qualified")):
        return (
            "Not assembled. The OpenAlex subfield did not pass the world "
            "size/growth gate, so Leiden communities were not used to define "
            "a journal market."
        )
    if mapped < 100 or n == 0 or not names:
        return (
            "No journal-shaped citation market. Too few non-Frontiers papers "
            "in the Leiden network mapped to this subfield to define a "
            "coherent community set."
        )

    lead = names[:5]
    rest = max(0, n - len(lead))
    lead_txt = oxford(lead)
    if rest:
        lead_txt = f"{lead_txt}, plus {rest} smaller neighbouring communities"

    cov_pct = f"{float(cov):.0%}" if pd.notna(cov) else "—"
    top_pct = f"{float(top_share):.0%}" if pd.notna(top_share) else "—"
    macro_pct = f"{float(macro_share):.0%}" if pd.notna(macro_share) else "—"

    if float(top_share or 0) >= 0.35:
        shape = (
            f"The market is concentrated: {names[0]} alone holds {top_pct} "
            "of the non-Frontiers papers."
        )
    elif float(macro_share or 0) >= 0.70:
        shape = (
            f"No single community dominates (largest {top_pct}), but "
            f"{macro_pct} of the papers sit in one broad research "
            "neighbourhood, so the set is still journal-shaped."
        )
    else:
        shape = (
            f"The market is mixed: the largest community is only {top_pct} "
            "and papers spread across more than one broad neighbourhood."
        )

    theme_txt = ""
    if themes:
        theme_txt = " Candidate sections from the micro map: " + oxford(themes) + "."

    conf_txt = {
        "high": "Scope confidence is high.",
        "medium": "Scope confidence is medium and needs editorial reading.",
        "low": (
            "Scope confidence is low: treat this as a topic cluster, "
            "not a launch-ready journal."
        ),
    }.get(conf, "")

    return (
        f"Citation-community market of {mapped:,} non-Frontiers papers. "
        f"{n} meso communities cover {cov_pct} of that volume. "
        f"Led by {lead_txt}. {shape}{theme_txt} {conf_txt}"
    ).strip()


def pass_market_scope(row: pd.Series) -> str:
    return (
        f"{row['proposed_journal']} has no launch-ready scope. "
        "The OpenAlex subfield did not pass the world size and growth gate, "
        "so Leiden communities were not used to define a journal."
    )


def weak_scope(row: pd.Series) -> str:
    return (
        f"{row['proposed_journal']} does not yet have a coherent citation market. "
        "Too few non-Frontiers papers in the Leiden network map to this field "
        "to define a journal-shaped neighbourhood."
    )


def template_scope(row: pd.Series) -> str:
    names = split_names(row.get("scope_names"), 6)
    themes = split_names(row.get("section_themes"), 5)
    core = oxford(names[:3]) if names else str(row.get("taxonomy_subfield") or "this field")
    neighbours = oxford(names[3:6]) if len(names) > 3 else ""
    sections = oxford(themes) if themes else "the leading micro themes"
    extra = ""
    if neighbours:
        extra = f" Neighbouring communities in the market include {neighbours}."
    return (
        f"{row['proposed_journal']} would cover the citation communities led by "
        f"{core}.{extra} Plausible sections include {sections}. "
        "Editorial walls are needed if those neighbours are as large as the core."
    )


def _brief(row: pd.Series) -> dict:
    return {
        "proposed_journal": row["proposed_journal"],
        "subfield": row["taxonomy_subfield"],
        "domain": row["taxonomy_domain"],
        "action": row["action"],
        "ownership": row.get("ownership_status"),
        "coverage": row.get("coverage_status"),
        "scope_confidence": row.get("scope_confidence"),
        "meso_count": int(row.get("scope_community_count") or 0),
        "coverage_share": (
            None if pd.isna(row.get("scope_coverage")) else round(float(row["scope_coverage"]), 3)
        ),
        "largest_community_share": (
            None
            if pd.isna(row.get("top_community_share"))
            else round(float(row["top_community_share"]), 3)
        ),
        "dominant_macro_share": (
            None
            if pd.isna(row.get("dominant_macro_share"))
            else round(float(row["dominant_macro_share"]), 3)
        ),
        "lead_communities": split_names(row.get("scope_names"), 12),
        "section_themes": split_names(row.get("section_themes"), 8),
        "lead_frontiers_title": row.get("lead_journal") or "",
    }


def generate_llm_scopes(rows: list[pd.Series]) -> dict[str, str]:
    from openai import OpenAI

    client = OpenAI()
    out: dict[str, str] = {}
    batch_size = 8
    system = (
        "You write concise journal-scope blurbs for Frontiers Media launch analysis. "
        "Use only the Leiden community names provided. Do not invent topics. "
        "Match this tone and length:\n\n"
        + SCOPE_EXAMPLE
        + "\n\nWrite 4-6 short sentences. Name the core, the citation neighbours "
        "that belong in the market, plausible sections, and one editorial bound "
        "if the neighbourhood is mixed. Return JSON: "
        '{"scopes": [{"proposed_journal": "...", "scope": "..."}]}'
    )
    for i in range(0, len(rows), batch_size):
        payload = [_brief(r) for r in rows[i : i + batch_size]]
        for attempt in range(4):
            try:
                resp = client.chat.completions.create(
                    model="gpt-4o",
                    temperature=0.2,
                    response_format={"type": "json_object"},
                    messages=[
                        {"role": "system", "content": system},
                        {
                            "role": "user",
                            "content": json.dumps({"journals": payload}, ensure_ascii=False),
                        },
                    ],
                )
                data = json.loads(resp.choices[0].message.content)
                items = data.get("scopes") or data.get("journals") or []
                for item in items:
                    title = str(item.get("proposed_journal") or "").strip()
                    text = str(item.get("scope") or item.get("journal_scope") or "").strip()
                    if title and text:
                        out[title] = text
                break
            except Exception as exc:
                log.warning("scope batch %s attempt %s failed: %s", i // batch_size + 1, attempt + 1, exc)
                time.sleep(2 ** attempt)
        log.info("journal scopes %s/%s", min(i + batch_size, len(rows)), len(rows))
        time.sleep(0.4)
    return out


def add_narrative_columns(src: pd.DataFrame, use_llm: bool) -> pd.DataFrame:
    out = src.copy()
    out["community_market"] = out.apply(community_market, axis=1)
    out["journal_scope"] = ""
    need: list[pd.Series] = []
    for idx, row in out.iterrows():
        if not bool(row.get("market_qualified")):
            out.at[idx, "journal_scope"] = pass_market_scope(row)
        elif int(row.get("mapped_non_fi_papers") or 0) < 100 or int(
            row.get("scope_community_count") or 0
        ) == 0:
            out.at[idx, "journal_scope"] = weak_scope(row)
        elif str(row.get("taxonomy_subfield")) == "Pulmonary and Respiratory Medicine":
            out.at[idx, "journal_scope"] = RESPIRATORY_SCOPE
        else:
            need.append(row)

    generated: dict[str, str] = {}
    if use_llm and need:
        log.info("Generating %s journal-scope blurbs with GPT-4o", len(need))
        generated = generate_llm_scopes(need)

    missing = 0
    for row in need:
        text = generated.get(str(row["proposed_journal"]), "")
        if not text:
            missing += 1
            text = template_scope(row)
        out.at[row.name, "journal_scope"] = text
    if missing:
        log.warning("Template fallback used for %s titles", missing)
    return out


def readable_frame(src: pd.DataFrame) -> pd.DataFrame:
    def share_txt(val: object) -> str:
        if val is None or (isinstance(val, float) and pd.isna(val)):
            return ""
        return f"{float(val):.2f}x"

    rows = []
    for _, r in src.iterrows():
        rows.append(
            {
                "Proposed journal": r.get("proposed_journal") or "",
                "Subfield": r.get("taxonomy_subfield") or "",
                "Domain": r.get("taxonomy_domain") or "",
                "Grade": r.get("grade") or "",
                "Score": int(r["score"]) if pd.notna(r.get("score")) else "",
                "World 2025": int(r["mkt_2025"]) if pd.notna(r.get("mkt_2025")) else "",
                "CAGR": round(float(r["cagr"]), 3) if pd.notna(r.get("cagr")) else "",
                "FI 2025": int(r["fi_articles_2025"]) if pd.notna(r.get("fi_articles_2025")) else "",
                "Share vs parity": share_txt(r.get("fi_share_vs_portfolio")),
                "Lead title": r.get("lead_journal") or "",
                "Ownership": _readable(r.get("ownership_status")),
                "Coverage": _readable(r.get("coverage_status")),
                "Scope confidence": r.get("scope_confidence") or "",
                "Community market (Leiden)": r.get("community_market") or "",
                "Journal scope": r.get("journal_scope") or "",
                "Action": ACTION_LABEL.get(str(r.get("action") or ""), str(r.get("action") or "")),
                "Warning": r.get("evidence_warnings") or "",
            }
        )
    return pd.DataFrame(rows, columns=[c for c, _ in COLUMNS])


def write_xlsx(table: pd.DataFrame, path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    wb = Workbook()
    ws = wb.active
    ws.title = "leiden_journal_opportunities_re"

    header_fill = PatternFill("solid", fgColor="003BDE")
    header_font = Font(name="Calibri", bold=True, color="FFFFFF", size=11)
    body_font = Font(name="Calibri", size=10, color="282828")
    wrap = Alignment(wrap_text=True, vertical="top")
    center = Alignment(wrap_text=True, vertical="center", horizontal="center")
    thin = Border(
        left=Side(style="thin", color="D0D0D0"),
        right=Side(style="thin", color="D0D0D0"),
        top=Side(style="thin", color="D0D0D0"),
        bottom=Side(style="thin", color="D0D0D0"),
    )

    names = [c for c, _ in COLUMNS]
    for col, (name, width) in enumerate(COLUMNS, 1):
        cell = ws.cell(1, col, name)
        cell.fill = header_fill
        cell.font = header_font
        cell.alignment = center
        cell.border = thin
        ws.column_dimensions[get_column_letter(col)].width = width
    ws.row_dimensions[1].height = 32
    ws.freeze_panes = "A2"

    wrap_cols = {
        "Community market (Leiden)",
        "Journal scope",
        "Warning",
        "Proposed journal",
        "Lead title",
    }
    for ridx, row in enumerate(table.itertuples(index=False), 2):
        values = list(row)
        for cidx, value in enumerate(values, 1):
            cell = ws.cell(ridx, cidx, value)
            cell.font = body_font
            cell.border = thin
            header = names[cidx - 1]
            cell.alignment = wrap if header in wrap_cols else Alignment(vertical="top")
        ws.row_dimensions[ridx].height = 90

    last = get_column_letter(len(names))
    ws.auto_filter.ref = f"A1:{last}{ws.max_row}"

    try:
        wb.save(path)
        saved = path
    except PermissionError:
        saved = path.with_name(path.stem + "_new.xlsx")
        wb.save(saved)
        log.warning("Original file locked; wrote %s", saved)
    return saved


def export_workbook(
    src: pd.DataFrame,
    out_path: Path,
    use_llm: bool = True,
) -> Path:
    framed = add_narrative_columns(src, use_llm=use_llm)
    table = readable_frame(framed)
    saved = write_xlsx(table, out_path)
    log.info("Wrote %s (%s rows)", saved, len(table))
    return saved


def default_out_path() -> Path:
    ensure_directories()
    stamp = date.today().strftime("%Y%m%d")
    return OUTPUT_DIR / f"leiden_journal_opportunities_readable_{stamp}.csv.xlsx"


def main(argv: list[str] | None = None) -> Path:
    configure_logging("opportunities_export")
    load_dotenv(REPO / ".env", override=True)

    ap = argparse.ArgumentParser(
        description="Write the readable journal-opportunities Excel from a final JSON run"
    )
    ap.add_argument(
        "--json",
        required=True,
        help="Path to final_journal_opportunities JSON",
    )
    ap.add_argument(
        "--out",
        default=None,
        help=(
            "Output .xlsx path (default "
            "scope_drift_outputs/opportunities/output/"
            "leiden_journal_opportunities_readable_YYYYMMDD.csv.xlsx)"
        ),
    )
    ap.add_argument(
        "--skip-llm",
        action="store_true",
        help="Skip GPT scope blurbs and use the template text instead",
    )
    args = ap.parse_args(argv)

    json_path = resolve_under(REPO, args.json)
    src = pd.read_json(json_path)
    out_path = (
        default_out_path()
        if args.out is None
        else resolve_under(OUTPUT_DIR, args.out)
    )
    return export_workbook(src, out_path, use_llm=not args.skip_llm)


if __name__ == "__main__":
    main()
