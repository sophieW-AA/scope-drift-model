"""Move each intact group of meso children to the macro title that best fits it.

Works on the ORIGINAL 28 Aug export (output/clusters.html), the data that has
"Materials Science" as a macro and the oncology/cancer mesos. Nothing from the
3 Sep run is used.

What a "group" is: the set of meso clusters that currently share a parent_macro.
Those sets are never split, merged or reordered internally - the whole group is
re-filed together under a different macro id. The partition of meso ids into
groups is asserted identical before and after.

Why move groups rather than rename macros: each macro id already carries a
coherent label + keywords + example papers (verified - e.g. C0 "Materials
Science" with electrochemistry keywords over carbon-fibre papers). Keeping the
label with its own keywords and papers, and moving the meso group to it,
preserves that coherence. Renaming the macro would break it.

Assignment is bijective - one group per macro id - so no group is ever dropped
and two groups can never collide on the same title.

Usage:
    python -X utf8 scripts/reassign_meso_groups.py            # dry run
    python -X utf8 scripts/reassign_meso_groups.py --apply    # write
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
BACKUP = HTML.with_name("clusters.html.pregroup.bak")
REPORT = Path(__file__).resolve().parents[1] / "logs" / "meso_group_reassign_report.txt"

LABEL_WEIGHT = 3
TITLE_WEIGHT = 1

STOP = {
    "a", "an", "and", "the", "of", "for", "in", "on", "to", "with", "by", "from",
    "at", "as", "is", "are", "be", "been", "using", "used", "based", "via",
    "study", "studies", "analysis", "analyses", "research", "review", "effect",
    "effects", "case", "new", "novel", "its", "their", "this", "that", "these",
    "those", "into", "under", "over", "between", "during", "after", "before",
    "not", "can", "may", "how", "what", "we", "our", "editorial", "approach",
    "approaches", "method", "methods", "results", "role", "impact", "impacts",
    "toward", "towards", "high", "low", "more", "than", "also", "among",
    "cluster", "general", "comprehensive", "integrated", "integrative",
    "interdisciplinary", "system", "systems", "advanced",
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


def add_cluster(bag: Counter, cluster: dict) -> None:
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


def assign(score: dict, group_keys: list, macro_ids: list) -> dict:
    """Bijective group -> macro id, maximising total similarity."""
    try:
        from scipy.optimize import linear_sum_assignment

        cost = [[-score[g][m] for m in macro_ids] for g in group_keys]
        rows, cols = linear_sum_assignment(cost)
        return {group_keys[r]: macro_ids[c] for r, c in zip(rows, cols)}
    except ImportError:
        pass

    # greedy seed, then pairwise swaps until stable
    pairs = sorted(
        ((score[g][m], g, m) for g in group_keys for m in macro_ids),
        key=lambda t: (-t[0], str(t[1]), t[2]),
    )
    chosen: dict = {}
    taken = set()
    for _, g, m in pairs:
        if g not in chosen and m not in taken:
            chosen[g] = m
            taken.add(m)
    free = [m for m in macro_ids if m not in taken]
    for g in group_keys:
        if g not in chosen:
            chosen[g] = free.pop()

    improved = True
    while improved:
        improved = False
        for i, g1 in enumerate(group_keys):
            for g2 in group_keys[i + 1 :]:
                m1, m2 = chosen[g1], chosen[g2]
                now = score[g1][m1] + score[g2][m2]
                swap = score[g1][m2] + score[g2][m1]
                if swap > now + 1e-12:
                    chosen[g1], chosen[g2] = m2, m1
                    improved = True
    return chosen


def main() -> None:
    apply = "--apply" in sys.argv
    text, match, data = load(HTML)

    macros = data["macro"]
    mesos = data["meso"]
    macro_by_id = {m["id"]: m for m in macros}
    meso_by_id = {m["id"]: m for m in mesos}

    groups: dict[int, list[dict]] = defaultdict(list)
    for meso in mesos:
        groups[meso.get("parent_macro")].append(meso)
    group_keys = sorted(groups)

    if len(group_keys) > len(macros):
        raise SystemExit(f"{len(group_keys)} groups but only {len(macros)} macro ids")

    macro_docs = {}
    for macro in macros:
        bag: Counter = Counter()
        add_cluster(bag, macro)
        macro_docs[macro["id"]] = bag

    group_docs = {}
    for key in group_keys:
        bag = Counter()
        for meso in groups[key]:
            add_cluster(bag, meso)
        group_docs[key] = bag

    idf = idf_weights(list(macro_docs.values()) + list(group_docs.values()))
    score = {
        g: {m: cosine(group_docs[g], macro_docs[m], idf) for m in macro_by_id}
        for g in group_keys
    }

    macro_ids = sorted(macro_by_id)
    placement = assign(score, group_keys, macro_ids)

    # --- snapshots: groups and every record must be untouched apart from links
    partition_before = {frozenset(m["id"] for m in groups[k]) for k in group_keys}
    meso_before = {
        m["id"]: json.dumps({k: v for k, v in m.items() if k != "parent_macro"}, sort_keys=True)
        for m in mesos
    }
    macro_before = {
        m["id"]: json.dumps({k: v for k, v in m.items() if k != "size"}, sort_keys=True)
        for m in macros
    }
    micro_before = json.dumps(data["micro"], sort_keys=True)
    old_parent = {m["id"]: m.get("parent_macro") for m in mesos}

    for key in group_keys:
        for meso in groups[key]:
            meso["parent_macro"] = placement[key]

    groups_after: dict[int, list[dict]] = defaultdict(list)
    for meso in mesos:
        groups_after[meso["parent_macro"]].append(meso)
    partition_after = {frozenset(m["id"] for m in v) for v in groups_after.values()}

    if partition_before != partition_after:
        raise SystemExit("refusing to write: the grouping of meso children changed")

    # branchvalues:'total' - a parent must cover its children
    raised = []
    for mid, children in groups_after.items():
        macro = macro_by_id.get(mid)
        if macro is None:
            continue
        total = sum(c.get("size", 0) for c in children)
        if total > macro.get("size", 0):
            raised.append((mid, macro["size"], total))
            macro["size"] = total

    meso_after = {
        m["id"]: json.dumps({k: v for k, v in m.items() if k != "parent_macro"}, sort_keys=True)
        for m in mesos
    }
    macro_after = {
        m["id"]: json.dumps({k: v for k, v in m.items() if k != "size"}, sort_keys=True)
        for m in macros
    }
    if meso_before != meso_after:
        raise SystemExit("refusing to write: a meso record changed beyond parent_macro")
    if macro_before != macro_after:
        raise SystemExit("refusing to write: a macro record changed beyond size")
    if micro_before != json.dumps(data["micro"], sort_keys=True):
        raise SystemExit("refusing to write: micro records changed")

    moved = [k for k in group_keys if placement[k] != k]
    lines = [
        f"source : {HTML}",
        f"mode   : {'APPLY' if apply else 'DRY RUN'}",
        "",
        f"meso groups            : {len(group_keys)} (covering {len(mesos)} meso clusters)",
        f"groups re-filed        : {len(moved)}",
        f"groups left in place   : {len(group_keys) - len(moved)}",
        f"macro sizes raised     : {len(raised)} (branchvalues:'total')",
        "",
        "groups kept intact - the partition of meso ids is byte-identical.",
        "macro labels, keywords and example papers untouched.",
        "meso records untouched apart from parent_macro.",
        "",
        "=== EACH MACRO TITLE AND THE GROUP IT NOW HOLDS ===",
    ]
    for key in sorted(group_keys, key=lambda k: -sum(m.get("size", 0) for m in groups[k])):
        dst = placement[key]
        macro = macro_by_id[dst]
        src = macro_by_id.get(key)
        children = sorted(groups[key], key=lambda m: -m.get("size", 0))
        lines.append(
            f"\nMACRO C{dst}  {macro.get('label')}"
            f"\n    keywords : {', '.join((macro.get('fos') or [])[:4])}"
            f"\n    group of {len(children)} meso, {sum(c.get('size', 0) for c in children):,} articles"
            f"  (was under C{key} {src.get('label') if src else '?'})"
        )
        for kid in children[:8]:
            lines.append(f"        meso C{kid['id']:<4} {kid.get('size', 0):>6}  {kid.get('label')}")
        if len(children) > 8:
            lines.append(f"        ... and {len(children) - 8} more")

    empty = [m for m in macros if not groups_after.get(m["id"])]
    lines += ["", f"=== MACRO TITLES WITH NO GROUP ({len(empty)}) ==="]
    for macro in empty:
        lines.append(f"  C{macro['id']:<4} {macro.get('label')}")

    if raised:
        lines += ["", "=== MACRO SIZES RAISED TO COVER THEIR GROUP ==="]
        for mid, old, new in sorted(raised, key=lambda t: -(t[2] - t[1])):
            lines.append(f"  C{mid:<4} {old:>6} -> {new:>6}  {macro_by_id[mid].get('label')}")

    REPORT.parent.mkdir(exist_ok=True)
    REPORT.write_text("\n".join(lines), encoding="utf8")
    print("\n".join(lines[:12]))
    print(f"report -> {REPORT}")

    if apply:
        if not BACKUP.exists():
            shutil.copy2(HTML, BACKUP)
            print(f"backup -> {BACKUP}")
        payload = json.dumps(data, separators=(",", ":"), ensure_ascii=False)
        out = text[: match.start()] + match.group(1) + payload + match.group(3) + text[match.end():]
        HTML.write_text(out, encoding="utf8")
        print(f"applied: {len(moved)} meso groups re-filed in {HTML.name}")
    else:
        print("dry run only - nothing written. re-run with --apply")


if __name__ == "__main__":
    main()
