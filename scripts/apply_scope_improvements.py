"""
Apply scope-check improvements to an existing scope_dashboard.html.

Layers (no full citation-layout rebuild):
  1) Community LLM borderline (prompt v2)
  2) Journal title hard-negatives
  3) Paper-level LLM demotion inside risky primary communities

Loads journal titles + cluster IDs from BigQuery for the current RUN_TIMESTAMP.

Usage:
  python scripts/apply_scope_improvements.py
  python scripts/apply_scope_improvements.py --journal "Frontiers in Neurorobotics"
  python scripts/apply_scope_improvements.py --finalize   # maps only
  python scripts/apply_scope_improvements.py --skip-finalize
"""

from __future__ import annotations

import argparse
import json
import os
import sys
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
os.environ.setdefault("SCOPE_LLM_BORDERLINE_PROMPT_VERSION", "v2")
os.environ.setdefault("SCOPE_DISTANCE_ENABLED", "0")
os.environ.setdefault("SCOPE_HARD_NEGATIVES_ENABLED", "1")
os.environ.setdefault("SCOPE_PAPER_LLM_ENABLED", "1")
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
    path.write_text(new_text, encoding="utf-8")


def primary_from_journal(j: dict) -> set[int]:
    primary = {
        int(c["comm_id"])
        for c in (j.get("top_communities") or [])
        if c.get("is_primary")
    }
    if primary:
        return primary
    return set(j.get("in_scope_cluster_ids") or []) - set(
        j.get("borderline_cluster_ids")
        or j.get("distance_rescued_cluster_ids")
        or []
    )


def apply_journal(j: dict, jdf: pd.DataFrame) -> None:
    name = j["name"]
    print(f"=== {name} ===", flush=True)
    if jdf.empty:
        print("  no BQ rows — skip", flush=True)
        return

    primary = primary_from_journal(j)
    if not primary:
        print("  no primary — skip", flush=True)
        return

    borderline, border_meta = bud.compute_llm_borderline_clusters(name, jdf, primary)
    print(
        f"  primary={sorted(primary)} borderline={sorted(borderline)} "
        f"cached={border_meta.get('cached')} prompt={border_meta.get('prompt_version')}",
        flush=True,
    )
    for d in border_meta.get("decisions") or []:
        if d.get("verdict") == "borderline":
            print(
                f"    BORDERLINE C{d['comm_id']} {d.get('label')}: {d.get('reason')}",
                flush=True,
            )

    soft = set(primary) | set(borderline)
    work = jdf.copy()
    work["is_oos"] = ~work[bud.CLUSTER_LEVEL].isin(soft)
    work["is_borderline"] = work[bud.CLUSTER_LEVEL].isin(borderline)
    work["hard_negative"] = False
    work["paper_demoted"] = False

    hn_mask, hn_meta = bud.apply_hard_negatives(name, work)
    if hn_mask.any():
        work.loc[hn_mask, "is_oos"] = True
        work.loc[hn_mask, "is_borderline"] = False
        work.loc[hn_mask, "hard_negative"] = True

    demotions, paper_meta = bud.compute_paper_scope_overrides(
        name, work, primary, already_oos_mask=work["is_oos"]
    )
    if demotions:
        demote_mask = work["int_id"].isin(set(demotions.keys()))
        work.loc[demote_mask, "is_oos"] = True
        work.loc[demote_mask, "is_borderline"] = False
        work.loc[demote_mask, "paper_demoted"] = True

    paper_overrides: dict[str, dict] = {}
    for idx in work.index[work["hard_negative"]]:
        iid = int(work.at[idx, "int_id"])
        paper_overrides[str(iid)] = {
            "verdict": "out_of_scope",
            "reason": "hard_negative title rule",
            "source": "hard_negative",
            "community_id": int(work.at[idx, bud.CLUSTER_LEVEL]),
        }
    for iid, entry in demotions.items():
        paper_overrides[str(iid)] = {
            "verdict": "out_of_scope",
            "reason": entry.get("reason") or "",
            "source": "paper_llm",
            "community_id": entry.get("community_id"),
        }

    n_articles = len(work)
    n_oos = int(work["is_oos"].sum())
    n_border = int(work["is_borderline"].sum())
    n_hard = int(work["hard_negative"].sum())
    n_demoted = int(work["paper_demoted"].sum())

    print(
        f"  oos={n_oos}/{n_articles} ({100.0 * n_oos / n_articles:.1f}%) "
        f"hard_neg={n_hard} paper_demoted={n_demoted}",
        flush=True,
    )

    # Refresh scatter flags when possible (match community + truncated title)
    by_key: dict[tuple[int, str], list[dict]] = {}
    for _, row in work.iterrows():
        title = str(row.get("title") or "")
        key = (int(row[bud.CLUSTER_LEVEL]), title[:50])
        if row["is_oos"]:
            s = 0
        elif row["is_borderline"]:
            s = 1
        else:
            s = 2
        by_key.setdefault(key, []).append({"i": int(row["int_id"]), "s": s})

    new_scatter = []
    for p in j.get("scatter") or []:
        key = (int(p["c"]), str(p.get("t") or ""))
        bucket = by_key.get(key) or []
        q = dict(p)
        if bucket:
            hit = bucket.pop(0)
            q["i"] = hit["i"]
            q["s"] = hit["s"]
        new_scatter.append(q)

    borderline_ids = [int(c) for c in sorted(borderline)]
    j["borderline_cluster_ids"] = borderline_ids
    j["distance_rescued_cluster_ids"] = borderline_ids
    j["n_borderline_clusters"] = len(borderline_ids)
    j["n_borderline_papers"] = n_border
    j["n_hard_negative_papers"] = n_hard
    j["n_paper_demoted"] = n_demoted
    j["n_distance_rescued_clusters"] = len(borderline_ids)
    j["n_distance_rescued_papers"] = n_border
    j["in_scope_cluster_ids"] = [int(c) for c in sorted(soft)]
    j["articles"] = n_articles
    j["out_of_scope"] = n_oos
    j["out_of_scope_pct"] = round(100.0 * n_oos / n_articles, 1) if n_articles else 0.0
    j["scope_borderline"] = border_meta
    j["scope_distance"] = {"enabled": False, "replaced_by": "llm_borderline"}
    j["scope_hard_negatives"] = hn_meta
    j["scope_paper_llm"] = paper_meta
    j["paper_scope_overrides"] = paper_overrides
    j["scatter"] = new_scatter

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
    ap.add_argument("--journal", action="append", default=None)
    ap.add_argument("--finalize", action="store_true")
    ap.add_argument("--skip-finalize", action="store_true")
    args = ap.parse_args()

    if not SCOPE_HTML.exists():
        raise SystemExit(f"Missing {SCOPE_HTML}")

    print(f"openai_set={bool(os.environ.get('OPENAI_API_KEY'))}", flush=True)
    data, text, start, end = load_scope(SCOPE_HTML)

    wanted = args.journal or []
    env_journals = os.environ.get("APPLY_JOURNALS", "").strip()
    if not wanted and env_journals:
        wanted = [j.strip() for j in env_journals.split("|") if j.strip()]
    if args.finalize and not wanted:
        finalize(data)
        return

    all_journals = data.get("journals") or []
    names = [j["name"] for j in all_journals]
    if wanted:
        missing = [n for n in wanted if n not in set(names)]
        if missing:
            raise SystemExit(f"Journal not found: {missing}")
        selected = set(wanted)
        load_names = list(wanted)
    else:
        selected = None
        load_names = names

    os.environ["JOURNALS"] = ",".join(load_names)
    bud.JOURNALS = load_names
    bud._HARD_NEG_CONFIG_CACHE = None  # reload config

    bud.GPT_LABELS = {
        int(c["id"]): c.get("label") or f"Cluster {c['id']}"
        for c in data.get("communities", [])
    }
    bud.GPT_LABELS.update(bud.load_gpt_labels_single(bud.CLUSTER_LEVEL))
    bud.GPT_LABELS_ALL = bud.load_gpt_labels_all()

    print(f"Loading BQ papers for {len(load_names)} journal(s)…", flush=True)
    df = bud.load_merged_data()
    print(f"  loaded {len(df):,} rows", flush=True)

    for j in all_journals:
        if selected is not None and j["name"] not in selected:
            continue
        jdf = df[df["journal"] == j["name"]].copy()
        apply_journal(j, jdf)
        save_scope(SCOPE_HTML, text, start, end, data)
        data, text, start, end = load_scope(SCOPE_HTML)

    print(f"Updated {SCOPE_HTML}", flush=True)
    if not args.skip_finalize:
        finalize(data)


if __name__ == "__main__":
    main()
