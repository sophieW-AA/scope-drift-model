"""Decide which label level is wrong: the macro labels or the meso labels.

For each macro cluster we pull the real article titles from BigQuery, rank the
distinctive terms with TF-IDF, and print them next to (a) the macro label the
dashboard shows and (b) the labels of the meso clusters sitting under it.

If the terms match the macro label, the macro names are fine and the meso names
are misassigned. If they match the meso labels, the reverse is true.

Read-only: touches BigQuery and clusters.html only for reading.
"""

from __future__ import annotations

import argparse
import json
import math
import re
from collections import Counter, defaultdict
from pathlib import Path

from google.cloud import bigquery

PROJECT = "ocean-tech-adv-analytics-c-tfs"
DATASET = "scope_drift"
HTML = Path(r"C:\Users\sophie.wilson\Documents\scope_drift_outputs\output\clusters.html")
BAK = HTML.with_suffix(".html.bak")

STOP = set(
    """a an the of and or for to in on with by from as at is are was were be been being
    this that these those it its their his her our your using use used based via towards
    toward new novel study studies analysis approach approaches method methods methodology
    results result effect effects role impact impacts review systematic case report
    evidence evaluation assessment investigation research development application
    applications between during under over after before both such into than then there
    which who whom whose what when where why how all any more most other others some
    no not non nor only own same so too very can will just also across among within
    without high low higher lower increased decreased associated association correlation
    comparison compared versus vs among multi single first second third one two three
    potential clinical patients patient human humans mice rat rats cell cells preliminary
    data model models modeling modelling simulation framework system systems analysis
    characterization characterisation performance properties property structure
    structures design optimization optimisation improved enhanced efficient effective
    """.split()
)


def terms(title: str) -> set[str]:
    words = [w for w in re.findall(r"[a-z][a-z0-9\-]{2,}", (title or "").lower()) if w not in STOP]
    out = set(words)
    out.update(f"{a} {b}" for a, b in zip(words, words[1:]))
    return out


def load_dashboard(path: Path) -> dict:
    text = path.read_text(encoding="utf8")
    return json.loads(re.search(r"const D\s*=\s*(\{.*?\});\s*\n", text, re.S).group(1))


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--ts", default="20260721_122750")
    ap.add_argument("--macros", default="", help="comma separated macro ids; default = top 10")
    ap.add_argument("--top", type=int, default=12, help="terms to show per macro")
    args = ap.parse_args()

    src = BAK if BAK.exists() else HTML
    data = load_dashboard(src)
    macro_label = {m["id"]: m.get("label", "?") for m in data["macro"]}
    macro_size = {m["id"]: m.get("size", 0) for m in data["macro"]}
    meso_kids: dict[int, list[tuple[int, int, str]]] = defaultdict(list)
    for m in data["meso"]:
        meso_kids[m.get("parent_macro")].append((m.get("size", 0), m["id"], m.get("label", "?")))

    if args.macros:
        targets = [int(x) for x in args.macros.split(",")]
    else:
        targets = sorted(macro_size, key=lambda i: -macro_size[i])[:10]

    client = bigquery.Client(project=PROJECT, location="EU")
    sql = f"""
    SELECT c.macro AS macro_id, p.title AS title
    FROM `{PROJECT}.{DATASET}.classification_raw_{args.ts}` c
    JOIN `{PROJECT}.{DATASET}.pub_metadata_raw_{args.ts}` p USING (pub_id)
    WHERE c.macro IN UNNEST(@ids) AND p.title IS NOT NULL
    """
    job = client.query(
        sql,
        job_config=bigquery.QueryJobConfig(
            query_parameters=[bigquery.ArrayQueryParameter("ids", "INT64", targets)]
        ),
    )

    docs: dict[int, list[set[str]]] = defaultdict(list)
    for row in job.result():
        docs[int(row.macro_id)].append(terms(row.title))

    # document frequency across the macros we sampled, for TF-IDF weighting
    df = Counter()
    total_docs = 0
    for bag_list in docs.values():
        total_docs += len(bag_list)
        for bag in bag_list:
            df.update(bag)

    lines = [
        f"run: classification_raw_{args.ts}",
        f"structure read from: {src.name}",
        f"macros sampled: {len(docs)}   articles: {total_docs}",
        "",
    ]
    for mid in targets:
        bags = docs.get(mid, [])
        if not bags:
            lines.append(f"MACRO C{mid} {macro_label.get(mid,'?')} - no articles returned\n")
            continue
        tf = Counter()
        for bag in bags:
            tf.update(bag)
        scored = sorted(
            (
                (cnt / len(bags)) * math.log(total_docs / (1 + df[t])),
                t,
            )
            for t, cnt in tf.items()
            if cnt >= max(3, len(bags) * 0.02)
        )
        top = [t for _, t in scored[::-1][: args.top]]

        lines.append(f"MACRO C{mid}  dashboard label: {macro_label.get(mid,'?')}")
        lines.append(f"  articles in run      : {len(bags)}")
        lines.append(f"  actual top terms     : {', '.join(top)}")
        kids = sorted(meso_kids.get(mid, []), reverse=True)
        lines.append(
            "  meso labels under it : "
            + (", ".join(f"{lab} ({sz})" for sz, _, lab in kids) if kids else "none")
        )
        lines.append("")

    out = Path(__file__).resolve().parents[1] / "logs" / "macro_label_fit_audit.txt"
    out.parent.mkdir(exist_ok=True)
    out.write_text("\n".join(lines), encoding="utf8")
    print("\n".join(lines))
    print(f"report -> {out}")


if __name__ == "__main__":
    main()
