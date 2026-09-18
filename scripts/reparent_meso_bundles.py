"""Re-file each meso cluster under the macro that best represents it.

Every meso record moves as one intact bundle - label, keywords (fos /
fos_specific), example papers, journal graph, years, size and dominant journal
are all left exactly as they are. The only field written on a meso is
``parent_macro``. Macro labels are never touched.

Macro ``size`` is the one exception: the sunburst uses ``branchvalues:'total'``,
so a parent must cover the sum of its children or Plotly drops the branch. Where
re-filing pushes a macro's children past its own count, the macro size is raised
to that sum.

Matching uses IDF-weighted cosine over each cluster's own text, with the
displayed identity (label + keywords) weighted above the sampled paper titles.

Usage:
    python -X utf8 scripts/reparent_meso_bundles.py            # dry run
    python -X utf8 scripts/reparent_meso_bundles.py --apply    # write
"""

from __future__ import annotations

import json
import math
import re
import shutil
import sys
from collections import Counter, defaultdict
from pathlib import Path

HTML = Path(r"C:\Users\sophie.wilson\Documents\scope_drift_outputs\output\clusters.html")
BACKUP = HTML.with_name("clusters.html.prereparent.bak")
REPORT = Path(__file__).resolve().parents[1] / "logs" / "meso_reparent_report.txt"

LABEL_WEIGHT = 3  # label + keywords: what the sunburst actually shows
TITLE_WEIGHT = 1  # sampled example titles

STOP = {
    "a", "an", "and", "the", "of", "for", "in", "on", "to", "with", "by", "from",
    "at", "as", "is", "are", "be", "been", "using", "used", "based", "via",
    "study", "studies", "analysis", "analyses", "research", "review", "effect",
    "effects", "case", "new", "novel", "its", "their", "this", "that", "these",
    "those", "into", "under", "over", "between", "during", "after", "before",
    "not", "can", "may", "how", "what", "we", "our", "editorial", "approach",
    "approaches", "method", "methods", "results", "role", "impact", "impacts",
    "toward", "towards", "high", "low", "more", "than", "also", "among",
    "cluster", "sciences", "science", "general", "comprehensive", "integrated",
    "integrative", "interdisciplinary",
}


def load(path: Path) -> tuple[str, re.Match, dict]:
    text = path.read_text(encoding="utf8")
    match = re.search(r"(const D\s*=\s*)(\{.*?\})(;\s*\n)", text, re.S)
    if not match:
        raise SystemExit(f"could not locate the 'const D = {{...}};' payload in {path}")
    return text, match, json.loads(match.group(2))


def words(text: str) -> list[str]:
    text = re.sub(r"&[a-z]+;|&#\d+;", " ", str(text or "").lower())
    return [w for w in re.findall(r"[a-z]{4,}", text) if w not in STOP]


def cluster_doc(cluster: dict) -> Counter:
    """Weighted bag of words for one cluster: identity text plus its titles."""
    bag: Counter = Counter()
    identity = " ".join(
        [cluster.get("label") or ""]
        + list(cluster.get("fos") or [])
        + list(cluster.get("fos_specific") or [])
    )
    for w in words(identity):
        bag[w] += LABEL_WEIGHT
    titles = " ".join(str(p.get("title") or "") for p in cluster.get("examples") or [])
    for w in words(titles):
        bag[w] += TITLE_WEIGHT
    return bag


def idf_weights(docs: list[Counter]) -> dict[str, float]:
    n = len(docs)
    seen: Counter = Counter()
    for d in docs:
        seen.update(set(d))
    return {w: math.log((n + 1) / (c + 1)) + 1.0 for w, c in seen.items()}


def cosine(a: Counter, b: Counter, idf: dict[str, float]) -> float:
    shared = set(a) & set(b)
    if not shared:
        return 0.0
    dot = sum(a[w] * b[w] * idf.get(w, 1.0) ** 2 for w in shared)
    na = math.sqrt(sum((v * idf.get(w, 1.0)) ** 2 for w, v in a.items()))
    nb = math.sqrt(sum((v * idf.get(w, 1.0)) ** 2 for w, v in b.items()))
    return dot / (na * nb) if na and nb else 0.0


def main() -> None:
    apply = "--apply" in sys.argv
    text, match, data = load(HTML)

    macros = data["macro"]
    mesos = data["meso"]
    macro_by_id = {m["id"]: m for m in macros}

    macro_docs = {m["id"]: cluster_doc(m) for m in macros}
    meso_docs = {m["id"]: cluster_doc(m) for m in mesos}
    idf = idf_weights(list(macro_docs.values()) + list(meso_docs.values()))

    # --- snapshot everything that must survive untouched
    def snapshot() -> dict:
        return {
            "macro_labels": {m["id"]: m.get("label") for m in macros},
            "macro_fos": {m["id"]: json.dumps(m.get("fos")) for m in macros},
            "meso_labels": {m["id"]: m.get("label") for m in mesos},
            "meso_fos": {m["id"]: json.dumps(m.get("fos")) for m in mesos},
            "meso_fos_spec": {m["id"]: json.dumps(m.get("fos_specific")) for m in mesos},
            "meso_examples": {m["id"]: json.dumps(m.get("examples")) for m in mesos},
            "meso_journals": {m["id"]: json.dumps(m.get("journals")) for m in mesos},
            "meso_years": {m["id"]: json.dumps(m.get("years")) for m in mesos},
            "meso_sizes": {m["id"]: m.get("size") for m in mesos},
            "meso_dominant": {m["id"]: m.get("dominant") for m in mesos},
            "micro_labels": {m["id"]: m.get("label") for m in data["micro"]},
            "micro_parents": {m["id"]: m.get("parent_meso") for m in data["micro"]},
        }

    before = snapshot()
    old_parent = {m["id"]: m.get("parent_macro") for m in mesos}

    # --- choose the best-fitting macro for each meso bundle
    scored = {}
    for meso in mesos:
        ranked = sorted(
            ((cosine(meso_docs[meso["id"]], macro_docs[mid], idf), mid) for mid in macro_docs),
            key=lambda t: (-t[0], t[1]),
        )
        scored[meso["id"]] = ranked

    new_parent = {}
    for meso in mesos:
        best_score, best_id = scored[meso["id"]][0]
        # No lexical signal at all: leave the bundle where it is.
        new_parent[meso["id"]] = best_id if best_score > 0 else old_parent[meso["id"]]

    for meso in mesos:
        meso["parent_macro"] = new_parent[meso["id"]]

    # --- branchvalues:'total' needs every parent to cover its children
    child_total: Counter = Counter()
    for meso in mesos:
        if meso["parent_macro"] in macro_by_id:
            child_total[meso["parent_macro"]] += meso.get("size", 0)

    raised = []
    for mid, total in child_total.items():
        macro = macro_by_id[mid]
        if total > macro.get("size", 0):
            raised.append((mid, macro["size"], total))
            macro["size"] = total

    after = snapshot()
    for key in before:
        if before[key] != after[key]:
            raise SystemExit(f"refusing to write: {key} changed")

    # --- report
    moved = [i for i in sorted(old_parent) if new_parent[i] != old_parent[i]]
    stayed = [i for i in sorted(old_parent) if new_parent[i] == old_parent[i]]
    meso_by_id = {m["id"]: m for m in mesos}
    kids = defaultdict(list)
    for meso in mesos:
        kids[meso["parent_macro"]].append(meso)

    lines = [
        f"source : {HTML}",
        f"mode   : {'APPLY' if apply else 'DRY RUN'}",
        "",
        f"meso bundles re-filed : {len(moved)} of {len(mesos)}",
        f"meso bundles unchanged: {len(stayed)}",
        f"macro sizes raised    : {len(raised)} (branchvalues:'total')",
        "",
        "each meso keeps its own label, keywords, example papers, journal graph,",
        "years, size and dominant journal - only parent_macro was written.",
        "macro labels are untouched.",
        "",
        "=== MACROS AND THEIR MESO CHILDREN (after) ===",
    ]
    for macro in sorted(macros, key=lambda m: -len(kids.get(m["id"], []))):
        children = sorted(kids.get(macro["id"], []), key=lambda m: -m.get("size", 0))
        if not children:
            continue
        lines.append(f"\nMACRO C{macro['id']}  {macro.get('label')}  ({len(children)} meso)")
        for kid in children:
            flag = "  <- moved" if new_parent[kid["id"]] != old_parent[kid["id"]] else ""
            lines.append(f"    meso C{kid['id']:<4} {kid.get('size', 0):>6}  {kid.get('label')}{flag}")

    empty = [m for m in macros if not kids.get(m["id"])]
    lines += ["", f"=== MACROS WITH NO MESO CHILDREN ({len(empty)}) ==="]
    for macro in empty:
        lines.append(f"  C{macro['id']:<4} {macro.get('label')}")

    if raised:
        lines += ["", "=== MACRO SIZES RAISED TO COVER CHILDREN ==="]
        for mid, old, new in sorted(raised, key=lambda t: -(t[2] - t[1])):
            lines.append(f"  C{mid:<4} {old:>6} -> {new:>6}  {macro_by_id[mid].get('label')}")

    lines += ["", "=== WHERE EACH MOVED BUNDLE CAME FROM ==="]
    for i in moved:
        src = macro_by_id.get(old_parent[i])
        dst = macro_by_id.get(new_parent[i])
        lines.append(
            f"  meso C{i:<4} {meso_by_id[i].get('label')}\n"
            f"        {src.get('label') if src else old_parent[i]}"
            f"  ->  {dst.get('label') if dst else new_parent[i]}"
        )

    REPORT.parent.mkdir(exist_ok=True)
    REPORT.write_text("\n".join(lines), encoding="utf8")
    print("\n".join(lines[:9]))
    print(f"report -> {REPORT}")

    if apply:
        if not BACKUP.exists():
            shutil.copy2(HTML, BACKUP)
            print(f"backup -> {BACKUP}")
        payload = json.dumps(data, separators=(",", ":"), ensure_ascii=False)
        out = text[: match.start()] + match.group(1) + payload + match.group(3) + text[match.end():]
        HTML.write_text(out, encoding="utf8")
        print(f"applied: {len(moved)} meso bundles re-filed in {HTML.name}")
    else:
        print("dry run only - nothing written. re-run with --apply")


if __name__ == "__main__":
    main()
