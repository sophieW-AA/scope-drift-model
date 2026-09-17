"""Which dashboard files contain macro/meso cluster label text?

Read-only. Answers whether updating clusters.html alone is enough to refresh the
combined dashboard, or whether sibling tab files repeat the same labels.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

OUT = Path(r"C:\Users\sophie.wilson\Documents\scope_drift_outputs\output")
TABS = [
    "combined_dashboard.html",
    "scope_dashboard.html",
    "drift_dashboard.html",
    "clusters.html",
    "network_maps.html",
    "paper_examples.html",
]

orig = (OUT / "clusters.html.bak").read_text(encoding="utf8")
data = json.loads(re.search(r"const D\s*=\s*(\{.*?\});\s*\n", orig, re.S).group(1))
macro_labels = [m["label"] for m in data["macro"]]
meso_labels = [m["label"] for m in data["meso"] if not re.fullmatch(r"Cluster \d+", m["label"])]

print(f"{len(macro_labels)} macro labels, {len(meso_labels)} named meso labels\n")
print(f"{'file':28s} {'size':>10} {'macro hits':>11} {'meso hits':>10}  {'has const D':>11}")
print("-" * 76)

for name in TABS:
    path = OUT / name
    if not path.exists():
        print(f"{name:28s} {'MISSING':>10}")
        continue
    text = path.read_text(encoding="utf8", errors="replace")
    macro_hits = sum(text.count(lab) for lab in macro_labels)
    meso_hits = sum(text.count(lab) for lab in meso_labels)
    has_d = "yes" if "const D" in text else "no"
    print(f"{name:28s} {len(text):>10,} {macro_hits:>11} {meso_hits:>10}  {has_d:>11}")

print("\nper-label detail for files with any macro hits:")
for name in TABS:
    path = OUT / name
    if not path.exists():
        continue
    text = path.read_text(encoding="utf8", errors="replace")
    hits = {lab: text.count(lab) for lab in macro_labels if lab in text}
    if hits and name != "clusters.html":
        print(f"\n  {name}:")
        for lab, n in sorted(hits.items(), key=lambda kv: -kv[1]):
            print(f"    {n:>5}x  {lab}")
