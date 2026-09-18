"""Is each meso group correctly filed, judged by its papers rather than its labels?

Read-only, against the ORIGINAL 28 Aug export.

parent_macro is not guesswork - build_cluster_profiles sets it from real data:
    macro_counts = cdf["macro"].value_counts()
    profile["parent_macro"] = int(macro_counts.index[0])
So the grouping reflects genuine citation structure. This prints, per macro, the
macro's own label and keywords next to the example papers of its meso children,
so we can see whether the papers agree with the macro even when the meso label
text does not.
"""

from __future__ import annotations

import json
import re
from collections import defaultdict
from pathlib import Path

HTML = Path(r"C:\Users\sophie.wilson\Documents\scope_drift_outputs\output\clusters.html")


def load(path: Path) -> dict:
    text = path.read_text(encoding="utf8", errors="replace")
    return json.loads(re.search(r"const D\s*=\s*(\{.*?\});\s*\n", text, re.S).group(1))


def clean(text: str) -> str:
    return re.sub(r"&[a-z]+;|&#\d+;", " ", str(text or ""))


def main() -> None:
    data = load(HTML)
    macro_by_id = {m["id"]: m for m in data["macro"]}

    groups = defaultdict(list)
    for meso in data["meso"]:
        groups[meso.get("parent_macro")].append(meso)

    ranked = sorted(
        groups.items(),
        key=lambda kv: -sum(m.get("size", 0) for m in kv[1]),
    )

    for mid, children in ranked[:8]:
        macro = macro_by_id.get(mid)
        if not macro:
            continue
        children = sorted(children, key=lambda m: -m.get("size", 0))
        print("=" * 78)
        print(f"MACRO C{mid}  {macro.get('label')}")
        print(f"  macro keywords : {', '.join((macro.get('fos') or [])[:4])}")
        print("  macro's own example papers:")
        for ex in (macro.get("examples") or [])[:2]:
            print(f"      {clean(ex.get('title'))[:84]}")
        print(f"  {len(children)} meso children - their labels vs their papers:")
        for kid in children[:5]:
            print(f"\n    meso C{kid['id']}  {kid.get('size', 0)} papers  label={kid.get('label')!r}")
            for ex in (kid.get("examples") or [])[:2]:
                print(f"        paper: {clean(ex.get('title'))[:80]}")
        print()


if __name__ == "__main__":
    main()
