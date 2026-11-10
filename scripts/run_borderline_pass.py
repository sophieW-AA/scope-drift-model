"""Borderline scope pass for every Frontiers journal in a citation run.

Uses the same prompt, model and cache file as the scope dashboard
(scope_llm_borderline_{run}_meso.json). Communities outside the 80% core
are sent in small batches so the reply is not cut off. A community with
fewer than 3 papers and under 0.3% of the journal is left out of scope
without a call, matching the dashboard.

    python scripts/run_borderline_pass.py
    python scripts/run_borderline_pass.py --run 20260827_081311
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

import pandas as pd

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "src"))

RUN = "20260827_081311"
os.environ["RUN_TIMESTAMP"] = os.environ.get("RUN_TIMESTAMP", RUN)
os.environ["CLUSTER_LEVEL"] = "meso"

from build_unified_dashboard import (  # noqa: E402
    BORDERLINE_PROMPT_VERSION,
    PRIMARY_COVERAGE,
    SCOPE_LLM_BORDERLINE_MODEL,
    _borderline_cache_path,
    _call_openai_borderline,
    _load_dotenv_openai,
    _parse_borderline_json,
)

CACHE_DIR = Path.home() / "Documents" / "scope_drift_outputs" / "cache"
BATCH = 12
MIN_PAPERS = 3
MIN_SHARE = 0.3
WORKERS = 3
LOCK = threading.Lock()


def primary_ids(counts: pd.Series) -> list[int]:
    total = int(counts.sum()) or 1
    chosen = []
    covered = 0
    for comm, count in counts.sort_values(ascending=False).items():
        chosen.append(int(comm))
        covered += int(count)
        if covered >= total * PRIMARY_COVERAGE:
            break
    return chosen


def load_inputs(run: str) -> tuple[pd.DataFrame, dict[int, str], dict[int, str]]:
    folder = CACHE_DIR / f"network_bubbles_{run}"
    journals = pd.read_parquet(folder / "journals_all.parquet")
    journals["meso"] = journals["meso"].astype(int)
    journals["n"] = journals["n"].astype(int)
    journals["is_fi"] = journals["is_fi"].fillna(0).astype(int) == 1
    journals = journals[journals["is_fi"]].copy()

    from google.cloud import bigquery

    client = bigquery.Client(project="ocean-tech-adv-analytics-c-tfs", location="EU")
    labels = client.query(
        f"""
        SELECT cluster_id, short_label, long_label
        FROM `ocean-tech-adv-analytics-c-tfs.taxonomy_labelling.cluster_labels_meso_{run}`
        """
    ).to_dataframe()
    short, long = {}, {}
    for row in labels.itertuples(index=False):
        cid = int(row.cluster_id)
        name = str(row.short_label) if pd.notna(row.short_label) else f"Community {cid}"
        short[cid] = name
        long[cid] = str(row.long_label) if pd.notna(row.long_label) else name
    return journals, short, long


def candidates_for(counts: pd.Series, core: set[int], total: int) -> list[dict]:
    rows = []
    for comm, count in counts.items():
        cid = int(comm)
        if cid in core:
            continue
        share = round(100.0 * int(count) / total, 2) if total else 0.0
        if int(count) < MIN_PAPERS and share < MIN_SHARE:
            continue
        rows.append(
            {
                "comm_id": cid,
                "papers_in_journal": int(count),
                "share_of_journal_pct": share,
            }
        )
    rows.sort(key=lambda item: -item["papers_in_journal"])
    return rows


def classify_batch(journal: str, primary_payload: list[dict], batch: list[dict]) -> list[dict]:
    prompt = (
        f"Journal: {journal}\n\n"
        f"Primary (in-scope) communities for this journal "
        f"(~{PRIMARY_COVERAGE * 100:.0f}% coverage core):\n"
        f"{json.dumps(primary_payload, indent=2)}\n\n"
        f"Candidate non-primary communities to classify "
        f"(borderline vs out_of_scope):\n"
        f"{json.dumps(batch, indent=2)}\n"
    )
    raw = _call_openai_borderline(prompt)
    return _parse_borderline_json(raw)


def one_journal(
    journal: str,
    counts: pd.Series,
    short: dict[int, str],
    long: dict[int, str],
    cache: dict,
) -> str:
    total = int(counts.sum()) or 1
    core = primary_ids(counts)
    core_set = set(core)
    pending = candidates_for(counts, core_set, total)
    primary_sig = sorted(core)
    cand_sig = sorted(item["comm_id"] for item in pending)
    cached = cache.get(journal)
    if (
        isinstance(cached, dict)
        and cached.get("candidate_ids") == cand_sig
        and cached.get("primary_ids") == primary_sig
        and cached.get("model") == SCOPE_LLM_BORDERLINE_MODEL
        and cached.get("prompt_version") == BORDERLINE_PROMPT_VERSION
        and cached.get("decisions")
    ):
        return f"cached {journal} ({len(cached.get('borderline_ids') or [])} borderline)"

    primary_payload = [
        {
            "comm_id": cid,
            "label": short.get(cid, f"Community {cid}"),
            "long_label": long.get(cid, short.get(cid, f"Community {cid}")),
            "papers_in_journal": int(counts.get(cid, 0)),
            "share_of_journal_pct": round(100.0 * int(counts.get(cid, 0)) / total, 2),
        }
        for cid in core
    ]
    described = []
    for item in pending:
        cid = item["comm_id"]
        described.append(
            {
                **item,
                "label": short.get(cid, f"Community {cid}"),
                "long_label": long.get(cid, short.get(cid, f"Community {cid}")),
            }
        )

    borderline: set[int] = set()
    cleaned = []
    valid = {item["comm_id"] for item in described}
    for start in range(0, len(described), BATCH):
        batch = described[start : start + BATCH]
        decisions = classify_batch(journal, primary_payload, batch)
        for decision in decisions:
            try:
                cid = int(decision.get("comm_id"))
            except (TypeError, ValueError):
                continue
            if cid not in valid:
                continue
            verdict = str(decision.get("verdict", "")).strip().lower().replace(" ", "_")
            if verdict in {"borderline", "border_line", "border-line"}:
                borderline.add(cid)
                verdict = "borderline"
            else:
                verdict = "out_of_scope"
            cleaned.append(
                {
                    "comm_id": cid,
                    "label": short.get(cid, f"Community {cid}"),
                    "verdict": verdict,
                    "reason": str(decision.get("reason") or "")[:240],
                }
            )

    entry = {
        "model": SCOPE_LLM_BORDERLINE_MODEL,
        "prompt_version": BORDERLINE_PROMPT_VERSION,
        "primary_ids": primary_sig,
        "candidate_ids": cand_sig,
        "borderline_ids": sorted(borderline),
        "decisions": cleaned,
    }
    path = _borderline_cache_path()
    with LOCK:
        cache[journal] = entry
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(cache, indent=2), encoding="utf-8")
    return (
        f"{journal}: {len(borderline)} borderline / {len(described)} candidates"
    )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run", default=RUN)
    args = parser.parse_args()
    os.environ["RUN_TIMESTAMP"] = args.run
    _load_dotenv_openai()
    if not os.environ.get("OPENAI_API_KEY"):
        raise SystemExit("OPENAI_API_KEY is not set")

    journals, short, long = load_inputs(args.run)
    grouped = {
        name: group.groupby("meso")["n"].sum()
        for name, group in journals.groupby("journal")
    }
    path = _borderline_cache_path()
    cache: dict = {}
    if path.exists():
        try:
            cache = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            cache = {}
    todo = []
    calls = 0
    for name, counts in sorted(grouped.items()):
        total = int(counts.sum()) or 1
        core = set(primary_ids(counts))
        n_cand = len(candidates_for(counts, core, total))
        calls += (n_cand + BATCH - 1) // BATCH if n_cand else 0
        todo.append(name)
    print(
        f"{len(todo)} journals, about {calls} model calls, cache {path}",
        flush=True,
    )

    done = 0
    failed = []
    with ThreadPoolExecutor(max_workers=WORKERS) as pool:
        futures = {
            pool.submit(one_journal, name, grouped[name], short, long, cache): name
            for name in todo
        }
        for future in as_completed(futures):
            name = futures[future]
            done += 1
            try:
                print(f"[{done}/{len(todo)}] {future.result()}", flush=True)
            except Exception as exc:
                failed.append(name)
                print(f"[{done}/{len(todo)}] FAILED {name}: {exc}", flush=True)
                time.sleep(2)
    print(f"finished, {len(failed)} failed", flush=True)
    if failed:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
