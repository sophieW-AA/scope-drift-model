"""Verify the meso->macro relink changed only parent_macro (and macro sizes).

Compares clusters.html against clusters.html.bak and asserts that every label
string at every level is byte-identical.
"""

import json
import re
from collections import Counter
from pathlib import Path

HTML = Path(r"C:\Users\sophie.wilson\Documents\scope_drift_outputs\output\clusters.html")
BAK = Path(r"C:\Users\sophie.wilson\Documents\scope_drift_outputs\output\clusters.html.bak")


def load(path: Path) -> dict:
    text = path.read_text(encoding="utf8")
    return json.loads(re.search(r"const D\s*=\s*(\{.*?\});\s*\n", text, re.S).group(1))


def main() -> None:
    new, old = load(HTML), load(BAK)
    problems = []

    for level in ("macro", "meso", "micro"):
        o = {c["id"]: c for c in old[level]}
        n = {c["id"]: c for c in new[level]}
        if set(o) != set(n):
            problems.append(f"{level}: cluster id set changed")
        # label text must be identical per id, and as a whole multiset
        for cid in sorted(set(o) & set(n)):
            if o[cid].get("label") != n[cid].get("label"):
                problems.append(
                    f"{level} C{cid}: LABEL CHANGED "
                    f"{o[cid].get('label')!r} -> {n[cid].get('label')!r}"
                )
        if Counter(c.get("label") for c in old[level]) != Counter(
            c.get("label") for c in new[level]
        ):
            problems.append(f"{level}: label multiset changed")
        print(f"{level:6s} clusters={len(n):4d}  labels identical="
              f"{all(o[c].get('label') == n[c].get('label') for c in set(o) & set(n))}")

    moved = [
        (c["id"], c.get("label"), o_parent, c.get("parent_macro"))
        for c in new["meso"]
        for o_parent in [next(x.get("parent_macro") for x in old["meso"] if x["id"] == c["id"])]
        if o_parent != c.get("parent_macro")
    ]
    print(f"\nmeso parent_macro changed: {len(moved)}")

    # sizes
    size_changed = [
        (c["id"], c.get("label"), next(x["size"] for x in old["macro"] if x["id"] == c["id"]), c["size"])
        for c in new["macro"]
        if c.get("size") != next(x.get("size") for x in old["macro"] if x["id"] == c["id"])
    ]
    print(f"macro size changed:        {len(size_changed)}")
    meso_size_changed = sum(
        1
        for c in new["meso"]
        if c.get("size") != next(x.get("size") for x in old["meso"] if x["id"] == c["id"])
    )
    print(f"meso size changed:         {meso_size_changed}")

    # branchvalues:'total' validity at both levels
    macro_size = {c["id"]: c.get("size", 0) for c in new["macro"]}
    meso_size = {c["id"]: c.get("size", 0) for c in new["meso"]}
    macro_children, meso_children = Counter(), Counter()
    for c in new["meso"]:
        if c.get("parent_macro") in macro_size:
            macro_children[c["parent_macro"]] += c.get("size", 0)
    for c in new["micro"]:
        if c.get("parent_meso") in meso_size:
            meso_children[c["parent_meso"]] += c.get("size", 0)
    bad = [f"macro C{p}: {macro_size[p]} < {t}" for p, t in macro_children.items() if t > macro_size[p]]
    bad += [f"meso C{p}: {meso_size[p]} < {t}" for p, t in meso_children.items() if t > meso_size[p]]
    print(f"\nbranchvalues:'total' violations: {len(bad)}")
    for b in bad[:20]:
        print("  " + b)

    # every meso must point at a macro that exists, else it is dropped from the chart
    orphan = [c["id"] for c in new["meso"] if c.get("parent_macro") not in macro_size]
    print(f"meso pointing at a missing macro (would vanish): {len(orphan)} {orphan[:20]}")

    print("\n" + ("PROBLEMS:" if problems else "PASS - no label text was altered"))
    for p in problems:
        print("  " + p)


if __name__ == "__main__":
    main()
