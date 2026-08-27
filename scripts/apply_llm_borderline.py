"""
Apply LLM borderline judgments to an existing scope_dashboard.html
(without reloading the full citation network from BigQuery).

Usage:
  python scripts/apply_llm_borderline.py              # all journals + finalize maps
  python scripts/apply_llm_borderline.py --journal "Frontiers in Surgery"
  python scripts/apply_llm_borderline.py --finalize   # rebuild network + GT maps only
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from collections import defaultdict
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "src"))

env_path = REPO / ".env"
if env_path.exists():
    for line in env_path.read_text(encoding="utf-8").splitlines():
        if "=" in line and not line.strip().startswith("#"):
            k, v = line.split("=", 1)
            os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))

os.environ.setdefault("SCOPE_LLM_BORDERLINE_ENABLED", "1")
os.environ.setdefault("SCOPE_DISTANCE_ENABLED", "0")
os.environ.setdefault("RUN_TIMESTAMP", "20260721_122750")
os.environ.setdefault("CLUSTER_LEVEL", "macro")

import build_unified_dashboard as bud  # noqa: E402
import pandas as pd  # noqa: E402

SCOPE_HTML = REPO / "output" / "scope_dashboard.html"
NETWORK_HTML = REPO / "output" / "network_maps.html"


def load_scope(path: Path):
    text = path.read_text(encoding="utf-8")
    start = text.find("const DATA = ")
    if start < 0:
        raise ValueError(f"No DATA in {path}")
    start += len("const DATA = ")
    data, end = json.JSONDecoder().raw_decode(text, start)
    return data, text, start, end


def save_scope(path: Path, text: str, start: int, end: int, data: dict) -> None:
    new_json = json.dumps(data, separators=(",", ":"))
    new_text = text[:start] + new_json + text[end:]
    new_text = new_text.replace(
        "Amber = borderline (distance-rescued)",
        "Amber = borderline (LLM scope judgment)",
    )
    new_text = new_text.replace(
        "Amber = distance-rescued in-scope",
        "Amber = borderline (LLM scope judgment)",
    )
    path.write_text(new_text, encoding="utf-8")


def apply_journal(j: dict) -> None:
    name = j["name"]
    print(f"=== {name} ===", flush=True)
    rows = []
    for c in j.get("top_communities") or []:
        cid = int(c["comm_id"])
        n = int(c.get("papers_in_comm") or 0)
        rows.extend([{bud.CLUSTER_LEVEL: cid}] * n)
    if not rows:
        print("  no communities — skip", flush=True)
        return

    jdf = pd.DataFrame(rows)
    primary = {
        int(c["comm_id"])
        for c in (j.get("top_communities") or [])
        if c.get("is_primary")
    }
    if not primary:
        primary = set(j.get("in_scope_cluster_ids") or []) - set(
            j.get("distance_rescued_cluster_ids")
            or j.get("borderline_cluster_ids")
            or []
        )
    if not primary:
        print("  no primary — skip", flush=True)
        return

    borderline, meta = bud.compute_llm_borderline_clusters(name, jdf, primary)
    print(
        f"  primary={sorted(primary)} borderline={sorted(borderline)} "
        f"cached={meta.get('cached')}",
        flush=True,
    )
    for d in meta.get("decisions") or []:
        if d.get("verdict") == "borderline":
            print(
                f"    BORDERLINE C{d['comm_id']} {d.get('label')}: {d.get('reason')}",
                flush=True,
            )
    if meta.get("error"):
        print(f"  ERROR: {meta['error']}", flush=True)

    soft = set(primary) | set(borderline)
    scatter = j.get("scatter") or []
    if scatter:
        by_c = defaultdict(int)
        for p in scatter:
            by_c[int(p["c"])] += 1
        n_articles = len(scatter)
        n_oos = sum(n for cid, n in by_c.items() if cid not in soft)
        n_border_papers = sum(n for cid, n in by_c.items() if cid in borderline)
    else:
        n_articles = int(j.get("articles") or 0)
        n_border_papers = sum(
            int(c.get("papers_in_comm") or 0)
            for c in (j.get("top_communities") or [])
            if int(c["comm_id"]) in borderline
        )
        n_oos = max(
            0,
            n_articles
            - sum(
                int(c.get("papers_in_comm") or 0)
                for c in (j.get("top_communities") or [])
                if int(c["comm_id"]) in soft
            ),
        )

    borderline_ids = [int(c) for c in sorted(borderline)]
    j["borderline_cluster_ids"] = borderline_ids
    j["distance_rescued_cluster_ids"] = borderline_ids
    j["n_borderline_clusters"] = len(borderline_ids)
    j["n_borderline_papers"] = int(n_border_papers)
    j["n_distance_rescued_clusters"] = len(borderline_ids)
    j["n_distance_rescued_papers"] = int(n_border_papers)
    j["in_scope_cluster_ids"] = [int(c) for c in sorted(soft)]
    j["out_of_scope"] = int(n_oos)
    j["out_of_scope_pct"] = (
        round(100.0 * n_oos / n_articles, 1) if n_articles else 0.0
    )
    j["scope_borderline"] = meta
    j["scope_distance"] = {"enabled": False, "replaced_by": "llm_borderline"}

    for c in j.get("top_communities") or []:
        cid = int(c["comm_id"])
        c["is_primary"] = cid in primary
        c["is_borderline"] = cid in borderline
        c["is_distance_rescued"] = cid in borderline
        c["is_in_scope"] = cid in soft


def finalize(data: dict) -> None:
    bud.build_network_maps_dashboard(data)
    print(f"Updated {NETWORK_HTML}", flush=True)
    sys.path.insert(0, str(REPO / "scripts"))
    import build_gt_network_map as gtmap

    gtmap.DEFAULT_SCOPE_HTML = SCOPE_HTML
    gtmap.RUN_TIMESTAMP = os.environ["RUN_TIMESTAMP"]
    out = gtmap.build()
    print(f"Updated {out}", flush=True)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "--journal",
        action="append",
        default=None,
        help="Process one journal (repeatable). Default: all journals in the dashboard.",
    )
    ap.add_argument(
        "--finalize",
        action="store_true",
        help="Rebuild network + GT maps (and skip LLM if used alone)",
    )
    ap.add_argument(
        "--skip-finalize",
        action="store_true",
        help="Do not rebuild network/GT maps after LLM pass",
    )
    args = ap.parse_args()

    if not SCOPE_HTML.exists():
        raise SystemExit(f"Missing {SCOPE_HTML}")

    print(f"openai_set={bool(os.environ.get('OPENAI_API_KEY'))}", flush=True)
    data, text, start, end = load_scope(SCOPE_HTML)

    wanted = args.journal or []
    # --finalize alone = rebuild maps only (LLM already applied).
    # Default / --journal = apply LLM; finalize unless --skip-finalize.
    finalize_only = bool(args.finalize and not wanted)
    if finalize_only:
        finalize(data)
        return

    bud.GPT_LABELS = {
        int(c["id"]): c.get("label") or f"Cluster {c['id']}"
        for c in data.get("communities", [])
    }
    bud.GPT_LABELS.update(bud.load_gpt_labels_single(bud.CLUSTER_LEVEL))
    bud.GPT_LABELS_ALL = bud.load_gpt_labels_all()

    all_journals = data.get("journals") or []
    if wanted:
        names = {j["name"] for j in all_journals}
        missing = [n for n in wanted if n not in names]
        if missing:
            raise SystemExit(f"Journal not found: {missing}")
        selected = set(wanted)
    else:
        selected = None

    for j in all_journals:
        if selected is not None and j["name"] not in selected:
            continue
        apply_journal(j)
        save_scope(SCOPE_HTML, text, start, end, data)
        data, text, start, end = load_scope(SCOPE_HTML)

    print(f"Updated {SCOPE_HTML}", flush=True)

    if not args.skip_finalize:
        finalize(data)


if __name__ == "__main__":
    main()
