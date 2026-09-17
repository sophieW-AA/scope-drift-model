"""Permute the existing macro label strings so each macro fits its meso children.

Strictly a reordering: the 50 label strings already in clusters.html are dealt
out to different macro ids. No label text is created, edited or reworded, and
nothing else in the payload is touched - parent_macro, size, dominant and every
meso/micro label stay exactly as they are.

Usage:
    python -X utf8 scripts/relabel_macros.py            # dry run
    python -X utf8 scripts/relabel_macros.py --apply    # write
"""

from __future__ import annotations

import json
import re
import shutil
import sys
from collections import Counter
from pathlib import Path

HTML = Path(r"C:\Users\sophie.wilson\Documents\scope_drift_outputs\output\clusters.html")
BACKUP = HTML.with_name("clusters.html.prelabel.bak")
REPORT = Path(__file__).resolve().parents[1] / "logs" / "macro_relabel_report.txt"

# macro id -> the existing label string that should sit on it.
# Every value must already be a macro label in the file, used exactly once.
MAPPING = {
    # --- macros that have meso children: label chosen to fit those children ---
    0: "Oncological Care and Treatment Integration",
    1: "Infectious Disease and Public Health",
    2: "Earth and Planetary Sciences",
    3: "Earth Sciences and Energy Resources",
    4: "Pathogenesis and Resistance",
    5: "Integrative Biological Sciences",
    6: "Organic and Organometallic Chemistry",
    7: "Nutraceuticals and Microbiome Interactions",
    8: "Neuroscience",
    9: "Cardiometabolic Health Sciences",
    10: "Computer vision",
    11: "Public Health and Nutrition Dynamics",
    12: "Intelligent Decision-Making Systems",
    13: "Aging Health and Nutrition Research",
    14: "Transport Geography",
    15: "Oncological Surgical Pathology Research",
    16: "Dentistry",
    19: "Engineering geology",
    20: "Interdisciplinary Language and Health Technology",
    21: "Materials Science",
    22: "Reproductive Health",
    24: "Pediatric Neurological Critical Care",
    25: "Agricultural and Biological Sciences",
    27: "Therapeutic Movement Sciences",
    28: "Digital Innovation in Education",
    29: "Audiology and Hearing",
    34: "Health Education and Knowledge Dissemination",
    36: "Marine Renewable Energy Engineering",
    39: "Maternal and Child Mental Health",
    42: "Acute Care and Emergency Medicine",
    43: "Head and Neck Health Sciences",
    49: "Autonomous Systems and Control Engineering",
    # --- macros with no meso children in this export: keep their own label
    #     where it is still free, otherwise take a leftover (no basis to fit) ---
    18: "Cloud and Security",
    30: "Ophthalmology",
    31: "Quantum mechanics",
    35: "Sexual and Infectious Disease Research",
    40: "Parasitology Studies",
    41: "Astrophysics and Cosmology",
    44: "Differential equations",
    45: "Integrated Telecommunications and Electromagnetics",
    46: "Integrated Optics and Robotics Research",
    17: "Biochemistry, Genetics and Molecular Biology",
    23: "Business, Management and Accounting",
    26: "Electronic and photonic properties",
    32: "Metals and Mechanical Properties",
    33: "Combustion and Thermal Management",
    37: "Sports medicine",
    38: "Surgical Oncology in Hepatic Disease",
    47: "Endocrine-Oncology Surgical Pathology",
    48: "Space physics",
}


def main() -> None:
    apply = "--apply" in sys.argv
    text = HTML.read_text(encoding="utf8")
    match = re.search(r"(const D\s*=\s*)(\{.*?\})(;\s*\n)", text, re.S)
    if not match:
        raise SystemExit("could not locate the 'const D = {...};' payload")
    data = json.loads(match.group(2))

    old_label = {m["id"]: m.get("label") for m in data["macro"]}

    # --- guardrails: this must be a strict permutation of what is already there
    if set(MAPPING) != set(old_label):
        raise SystemExit(
            f"macro id mismatch: mapping has {len(MAPPING)}, file has {len(old_label)}"
        )
    if Counter(MAPPING.values()) != Counter(old_label.values()):
        extra = Counter(MAPPING.values()) - Counter(old_label.values())
        missing = Counter(old_label.values()) - Counter(MAPPING.values())
        raise SystemExit(
            f"not a permutation.\n  invented/duplicated: {dict(extra)}\n  dropped: {dict(missing)}"
        )

    # --- snapshot everything that must not move
    before = {
        "meso_parents": {m["id"]: m.get("parent_macro") for m in data["meso"]},
        "macro_sizes": {m["id"]: m.get("size") for m in data["macro"]},
        "meso_sizes": {m["id"]: m.get("size") for m in data["meso"]},
        "meso_labels": {m["id"]: m.get("label") for m in data["meso"]},
        "micro_labels": {m["id"]: m.get("label") for m in data["micro"]},
        "micro_parents": {m["id"]: m.get("parent_meso") for m in data["micro"]},
    }

    for macro in data["macro"]:
        macro["label"] = MAPPING[macro["id"]]

    after = {
        "meso_parents": {m["id"]: m.get("parent_macro") for m in data["meso"]},
        "macro_sizes": {m["id"]: m.get("size") for m in data["macro"]},
        "meso_sizes": {m["id"]: m.get("size") for m in data["meso"]},
        "meso_labels": {m["id"]: m.get("label") for m in data["meso"]},
        "micro_labels": {m["id"]: m.get("label") for m in data["micro"]},
        "micro_parents": {m["id"]: m.get("parent_meso") for m in data["micro"]},
    }
    for key in before:
        if before[key] != after[key]:
            raise SystemExit(f"refusing to write: {key} changed")

    # --- do any macro labels also appear as static text outside the payload?
    outside = text[: match.start()] + text[match.end():]
    static_hits = {lab: outside.count(lab) for lab in old_label.values() if lab in outside}

    kids = Counter(m.get("parent_macro") for m in data["meso"])
    moved = [i for i in sorted(MAPPING) if MAPPING[i] != old_label[i]]
    stayed = [i for i in sorted(MAPPING) if MAPPING[i] == old_label[i]]

    lines = [
        f"source : {HTML}",
        f"mode   : {'APPLY' if apply else 'DRY RUN'}",
        f"macro labels moved : {len(moved)} of {len(MAPPING)}",
        f"macro labels kept  : {len(stayed)}",
        "",
        "permutation verified: same 50 label strings, each used exactly once",
        "unchanged: all meso/micro labels, all parent links, all sizes",
        "",
        "=== MACROS WITH MESO CHILDREN ===",
    ]
    for i in sorted(MAPPING, key=lambda x: (-kids.get(x, 0), x)):
        if not kids.get(i):
            continue
        flag = "" if MAPPING[i] != old_label[i] else "   (unchanged)"
        lines.append(f"C{i:<3} ({kids[i]} meso)  {old_label[i]}")
        lines.append(f"       -> {MAPPING[i]}{flag}")
    lines += ["", "=== MACROS WITH NO MESO CHILDREN IN THIS EXPORT ==="]
    for i in sorted(MAPPING):
        if kids.get(i):
            continue
        flag = "" if MAPPING[i] != old_label[i] else "   (unchanged)"
        lines.append(f"C{i:<3} (0 meso)  {old_label[i]}")
        lines.append(f"       -> {MAPPING[i]}{flag}")
    lines += ["", "=== MACRO LABELS APPEARING AS STATIC TEXT OUTSIDE const D ==="]
    lines.append(
        "  none - every macro label is rendered from the payload"
        if not static_hits
        else "\n".join(f"  {lab}: {n}x" for lab, n in static_hits.items())
    )

    REPORT.parent.mkdir(exist_ok=True)
    REPORT.write_text("\n".join(lines), encoding="utf8")
    print("\n".join(lines[:8]))
    print(f"static-text hits outside payload: {len(static_hits)}")
    print(f"report -> {REPORT}")

    if apply:
        if not BACKUP.exists():
            shutil.copy2(HTML, BACKUP)
            print(f"backup -> {BACKUP}")
        new_json = json.dumps(data, separators=(",", ":"), ensure_ascii=False)
        out = text[: match.start()] + match.group(1) + new_json + match.group(3) + text[match.end():]
        HTML.write_text(out, encoding="utf8")
        print(f"applied {len(moved)} macro label moves to {HTML.name}")
    else:
        print("dry run only - nothing written. re-run with --apply")


if __name__ == "__main__":
    main()
