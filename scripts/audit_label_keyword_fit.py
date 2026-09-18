"""Do each cluster's label and keywords describe its own example papers?

Read-only. In build_unified_dashboard.build_cluster_profiles, size / dominant /
journals / years / examples / parent_macro / parent_meso are all derived from the
actual papers in the cluster, while label and keywords come from a single
GPT_LABELS_ALL[level][cluster_id] lookup. So label+keywords are the only movable
pair; examples are real cluster members.

This script scores, per cluster, how well its own label+keywords match its own
example titles, and finds which other cluster's label+keywords would fit better.

Usage:
    python -X utf8 scripts/audit_label_keyword_fit.py [path-to-clusters.html]
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

DEFAULT_HTML = Path(
    r"C:\Users\sophie.wilson\Documents\scope_drift_outputs\output\clusters.html"
)
REPORT = Path(__file__).resolve().parents[1] / "logs" / "label_keyword_fit.txt"

STOP = {
    "a", "an", "and", "the", "of", "for", "in", "on", "to", "with", "by", "from",
    "at", "as", "is", "are", "be", "using", "based", "via", "study", "studies",
    "analysis", "research", "review", "effect", "effects", "case", "new", "novel",
    "its", "their", "this", "that", "into", "under", "over", "between", "during",
    "after", "before", "not", "can", "may", "how", "what", "we", "our",
}


def load(path: Path) -> dict:
    text = path.read_text(encoding="utf8", errors="replace")
    match = re.search(r"const D\s*=\s*(\{.*?\});\s*\n", text, re.S)
    if not match:
        raise SystemExit(f"no 'const D = {{...}};' payload in {path}")
    return json.loads(match.group(1))


def words(text: str) -> set[str]:
    text = re.sub(r"&[a-z]+;|&#\d+;", " ", str(text or "").lower())
    return {w for w in re.findall(r"[a-z]{4,}", text) if w not in STOP}


def label_terms(cluster: dict) -> set[str]:
    """Vocabulary of the movable pair: label text + keywords."""
    parts = [cluster.get("label") or ""]
    parts += list(cluster.get("fos") or [])
    parts += list(cluster.get("fos_specific") or [])
    return words(" ".join(parts))


def content_terms(cluster: dict) -> set[str]:
    """Vocabulary of the immovable data: the cluster's own example titles."""
    return words(" ".join(str(p.get("title") or "") for p in cluster.get("examples") or []))


def score(terms: set[str], content: set[str]) -> int:
    return len(terms & content)


def main() -> None:
    path = Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_HTML
    data = load(path)

    lines = [f"source: {path}", ""]

    for level in ("macro", "meso"):
        clusters = [c for c in data.get(level) or [] if c.get("examples")]
        if not clusters:
            continue

        terms = {c["id"]: label_terms(c) for c in clusters}
        content = {c["id"]: content_terms(c) for c in clusters}

        self_fit = {c["id"]: score(terms[c["id"]], content[c["id"]]) for c in clusters}
        best = {}
        for c in clusters:
            cid = c["id"]
            ranked = sorted(
                ((score(terms[o], content[cid]), o) for o in terms),
                key=lambda t: -t[0],
            )
            best[cid] = ranked[0]

        zero = [cid for cid, s in self_fit.items() if s == 0]
        better = [cid for cid in self_fit if best[cid][0] > self_fit[cid] and best[cid][1] != cid]

        lines += [
            "=" * 78,
            f"{level.upper()}  clusters with examples: {len(clusters)}",
            f"  own label+keywords share NO word with own examples : {len(zero)}",
            f"  some other cluster's label+keywords fit better     : {len(better)}",
            "",
        ]
        by_size = sorted(clusters, key=lambda c: -c.get("size", 0))
        for c in by_size[:15]:
            cid = c["id"]
            bs, bid = best[cid]
            lines.append(
                f"  C{cid:<4} size={c.get('size', 0):>6}  self-fit={self_fit[cid]}  "
                f"best-fit=C{bid} ({bs})"
            )
            lines.append(f"        label now : {c.get('label')}")
            lines.append(f"        keywords  : {', '.join((c.get('fos') or [])[:5])}")
            for ex in (c.get("examples") or [])[:2]:
                lines.append(f"        paper     : {str(ex.get('title'))[:78]}")
            if bid != cid:
                other = next(x for x in clusters if x["id"] == bid)
                lines.append(f"        would fit : {other.get('label')}")
            lines.append("")
        lines.append("")

    REPORT.parent.mkdir(exist_ok=True)
    REPORT.write_text("\n".join(lines), encoding="utf8")
    print("\n".join(lines))
    print(f"report -> {REPORT}")


if __name__ == "__main__":
    main()
