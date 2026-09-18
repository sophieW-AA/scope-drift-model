"""Widen the 19 macro labels in the 3 Sep dashboard to fit their meso children.

The 3 Sep run named each macro after its single dominant child, so broad groups
ended up with narrow names - "Cardiology" over 29 biomedical mesos, "Botany"
over 15 environmental ones. This rewrites only ``label`` on the macro array.

Nothing else is touched: every meso and micro label, all keywords, example
papers, journal graphs, years, sizes, dominant journals and all parent links are
snapshotted before and after and the write is refused if any of them differ.

Usage:
    python -X utf8 scripts/widen_macro_labels.py            # dry run
    python -X utf8 scripts/widen_macro_labels.py --apply    # write
"""

from __future__ import annotations

import json
import re
import shutil
import sys
from collections import defaultdict
from pathlib import Path

HTML = Path(r"C:\Users\sophie.wilson\Documents\scope_drift_outputs\dashboards\clusters.html")
BACKUP = HTML.with_name("clusters.html.premacro.bak")
REPORT = Path(__file__).resolve().parents[1] / "logs" / "macro_widen_report.txt"

# macro id -> broader label covering the meso children it actually holds.
# Macros with no meso children keep their existing label (no basis to rename).
RENAMES = {
    0: "Clinical and Biomedical Sciences",          # was Cardiology (29 meso)
    10: "Surgery and Acute Clinical Care",          # was Surgery (11 meso)
    3: "Ecology and Environmental Sciences",        # was Botany (15 meso)
    2: "Chemistry, Materials and Manufacturing",    # was Energy And Materials Chemistry (10)
    1: "Management, Society and Digital Systems",   # was Educational Technology And Digital Learning (8)
    4: "Robotics, Control and Engineering Systems", # was Computer Vision (8 meso)
    6: "Earth and Civil Engineering",               # was Engineering Geology (5 meso)
    15: "Rehabilitation and Sports Therapy",        # was Sports Therapy (3 meso)
    5: "Ageing and Reproductive Health",            # was Dietetics And Nutrition (2 meso)
    12: "Cognition, Hearing and Speech",            # was Audiology (2 meso)
    14: "Dentistry and Oral Surgery",               # was Dentistry (2 meso)
    7: "Public Health and Infectious Disease",      # was Immunology And Disease (2 meso)
    8: "Photonics and Electronic Engineering",      # was Electronics And Computing (1 meso)
}


def load(path: Path) -> tuple[str, re.Match, dict]:
    text = path.read_text(encoding="utf8")
    match = re.search(r"(const D\s*=\s*)(\{.*?\})(;\s*\n)", text, re.S)
    if not match:
        raise SystemExit(f"could not locate the 'const D = {{...}};' payload in {path}")
    return text, match, json.loads(match.group(2))


def main() -> None:
    apply = "--apply" in sys.argv
    text, match, data = load(HTML)

    macros = data["macro"]
    macro_by_id = {m["id"]: m for m in macros}

    unknown = set(RENAMES) - set(macro_by_id)
    if unknown:
        raise SystemExit(f"macro ids not in file: {sorted(unknown)}")

    kids = defaultdict(list)
    for meso in data["meso"]:
        kids[meso.get("parent_macro")].append(meso)

    # renaming a childless macro has no justification
    for mid in RENAMES:
        if not kids.get(mid):
            raise SystemExit(f"refusing: macro C{mid} has no meso children to justify a rename")

    def snapshot() -> dict:
        return {
            "macro_ids": sorted(m["id"] for m in macros),
            "macro_sizes": {m["id"]: m.get("size") for m in macros},
            "macro_fos": {m["id"]: json.dumps(m.get("fos")) for m in macros},
            "macro_examples": {m["id"]: json.dumps(m.get("examples")) for m in macros},
            "macro_journals": {m["id"]: json.dumps(m.get("journals")) for m in macros},
            "macro_dominant": {m["id"]: m.get("dominant") for m in macros},
            "meso": json.dumps(data["meso"], sort_keys=True),
            "micro": json.dumps(data["micro"], sort_keys=True),
        }

    before = snapshot()
    old_label = {m["id"]: m.get("label") for m in macros}

    for mid, new_label in RENAMES.items():
        macro_by_id[mid]["label"] = new_label

    after = snapshot()
    for key in before:
        if before[key] != after[key]:
            raise SystemExit(f"refusing to write: {key} changed")

    # do any macro labels also appear as static text outside the payload?
    outside = text[: match.start()] + text[match.end():]
    static_hits = {lab: outside.count(lab) for lab in old_label.values() if lab and lab in outside}

    renamed = [i for i in RENAMES if RENAMES[i] != old_label[i]]
    lines = [
        f"source : {HTML}",
        f"mode   : {'APPLY' if apply else 'DRY RUN'}",
        "",
        f"macros in file        : {len(macros)}",
        f"macro labels rewritten: {len(renamed)}",
        f"macros left untouched : {len(macros) - len(renamed)}",
        "",
        "unchanged: every meso/micro record, all keywords, example papers,",
        "journal graphs, sizes and all parent links (verified by snapshot).",
        "",
        "=== RENAMED (with the children that justify it) ===",
    ]
    for mid in sorted(RENAMES, key=lambda i: -len(kids.get(i, []))):
        children = sorted(kids.get(mid, []), key=lambda m: -m.get("size", 0))
        lines.append(
            f"\nC{mid:<3} {old_label[mid]}"
            f"\n     -> {RENAMES[mid]}"
            f"\n     ({len(children)} meso, {sum(c.get('size', 0) for c in children):,} articles)"
        )
        for kid in children[:8]:
            lines.append(f"        meso C{kid['id']:<4} {kid.get('size', 0):>6}  {kid.get('label')}")
        if len(children) > 8:
            lines.append(f"        ... and {len(children) - 8} more")

    untouched = [m for m in macros if m["id"] not in RENAMES]
    lines += ["", f"=== LEFT AS-IS ({len(untouched)}) ==="]
    for macro in untouched:
        lines.append(
            f"  C{macro['id']:<3} {macro.get('label')}  ({len(kids.get(macro['id'], []))} meso)"
        )

    lines += ["", "=== MACRO LABELS APPEARING AS STATIC TEXT OUTSIDE const D ==="]
    lines.append(
        "  none - every macro label is rendered from the payload"
        if not static_hits
        else "\n".join(f"  {lab}: {n}x" for lab, n in static_hits.items())
    )

    REPORT.parent.mkdir(exist_ok=True)
    REPORT.write_text("\n".join(lines), encoding="utf8")
    print("\n".join(lines))
    print(f"\nreport -> {REPORT}")

    if apply:
        if not BACKUP.exists():
            shutil.copy2(HTML, BACKUP)
            print(f"backup -> {BACKUP}")
        payload = json.dumps(data, separators=(",", ":"), ensure_ascii=False)
        out = text[: match.start()] + match.group(1) + payload + match.group(3) + text[match.end():]
        HTML.write_text(out, encoding="utf8")
        print(f"applied {len(renamed)} macro renames to {HTML.name}")
    else:
        print("dry run only - nothing written. re-run with --apply")


if __name__ == "__main__":
    main()
