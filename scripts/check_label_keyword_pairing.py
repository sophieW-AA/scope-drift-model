"""Are a cluster's label and its keywords a single unit, or independent fields?

Read-only, runs against the ORIGINAL clusters.html.bak.

Matters because build_cluster_profiles takes both from one lookup:
    label_info = GPT_LABELS_ALL[level][cluster_id]
    label    = label_info["short_label"]
    keywords = label_info["keywords"]

If label is essentially keywords[0], then label+keywords must move together;
relabelling alone would leave the Keywords tab contradicting the new label.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

BAK = Path(
    r"C:\Users\sophie.wilson\Documents\scope_drift_outputs\output\clusters.html.bak"
)


def load(path: Path) -> dict:
    text = path.read_text(encoding="utf8", errors="replace")
    return json.loads(re.search(r"const D\s*=\s*(\{.*?\});\s*\n", text, re.S).group(1))


def norm(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "", str(text or "").lower())


def main() -> None:
    data = load(BAK)
    print(f"source: {BAK}\n")

    for level in ("macro", "meso", "micro"):
        clusters = data.get(level) or []
        exact = near = 0
        no_kw = 0
        for c in clusters:
            kws = c.get("fos") or []
            if not kws:
                no_kw += 1
                continue
            label, first = norm(c.get("label")), norm(kws[0])
            if label == first:
                exact += 1
            elif label and first and (label in first or first in label):
                near += 1
        n = len(clusters)
        print(f"{level.upper():6s} clusters={n}")
        print(f"   label identical to first keyword : {exact}")
        print(f"   label contains/contained by it   : {near}")
        print(f"   label+keywords aligned           : {exact + near}/{n - no_kw}")
        print(f"   no keywords at all               : {no_kw}\n")


if __name__ == "__main__":
    main()
