"""After renaming macros in dashboards/clusters.html, do sibling tabs still show old names?

Read-only. Several old macro labels ("Cardiology", "Botany", "Surgery") are also
meso labels in the same run, and scope_dashboard.html reports at the meso level,
so a raw string hit there is expected and correct. This separates the two cases.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

DASH = Path(r"C:\Users\sophie.wilson\Documents\scope_drift_outputs\dashboards")
OLD_MACRO = [
    "Cardiology", "Botany", "Surgery", "Dentistry", "Audiology",
    "Energy And Materials Chemistry", "Educational Technology And Digital Learning",
    "Computer Vision", "Engineering Geology", "Sports Therapy",
    "Dietetics And Nutrition", "Immunology And Disease", "Electronics And Computing",
]
TABS = ["scope_dashboard.html", "drift_dashboard.html", "network_maps.html", "paper_examples.html"]


def load(path: Path) -> dict:
    text = path.read_text(encoding="utf8", errors="replace")
    for marker in ("const DATA = ", "const D=", "const D = ", "const D={"):
        i = text.find(marker)
        if i >= 0:
            start = i + len(marker) - (1 if marker.endswith("{") else 0)
            return json.JSONDecoder().raw_decode(text, start)[0]
    raise ValueError(f"no payload in {path}")


def main() -> None:
    data = load(DASH / "clusters.html")
    meso_labels = {m["label"] for m in data["meso"]}
    micro_labels = {m["label"] for m in data["micro"]}

    print("old macro label                                also a meso label?")
    print("-" * 70)
    for lab in OLD_MACRO:
        where = []
        if lab in meso_labels:
            where.append("meso")
        if lab in micro_labels:
            where.append("micro")
        print(f"{lab:46s} {', '.join(where) if where else 'NO - macro only'}")

    print("\nraw string hits in sibling tabs:")
    for name in TABS:
        path = DASH / name
        if not path.exists():
            print(f"  {name:26s} MISSING")
            continue
        text = path.read_text(encoding="utf8", errors="replace")
        hits = {lab: text.count(lab) for lab in OLD_MACRO if lab in text}
        macro_only = {
            lab: n for lab, n in hits.items()
            if lab not in meso_labels and lab not in micro_labels
        }
        print(f"\n  {name}")
        print(f"    total old-macro-name hits      : {sum(hits.values())}")
        print(f"    of which MACRO-ONLY (a problem): {sum(macro_only.values())} {macro_only or ''}")
        if hits:
            shared = {lab: n for lab, n in hits.items() if lab not in macro_only}
            print(f"    shared with meso/micro (fine)  : {shared}")


if __name__ == "__main__":
    main()
