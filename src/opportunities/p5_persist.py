"""P5 — dated decision log; community matching is journal+community_id within a run,
and paper-Jaccard across runs when a prior pack exists (IDs may change)."""

from __future__ import annotations

import logging
from collections import defaultdict

import pandas as pd

from . import bq as bqmod

log = logging.getLogger("opportunities.p5")


def match_communities(
    current_papers: pd.DataFrame, previous_papers: pd.DataFrame, threshold: float = 0.5
) -> pd.DataFrame:
    """Greedy Jaccard of paper int_id sets (journal, community_id).

    Candidates are bucketed by journal so this does not scan every previous
    community for every current one.
    """
    rows = []
    cur = {
        (j, int(c)): set(g["int_id"].astype(int))
        for (j, c), g in current_papers.groupby(["journal", "community_id"])
    }
    prev_by_journal: dict[str, dict[tuple, set]] = defaultdict(dict)
    for (j, c), g in previous_papers.groupby(["journal", "community_id"]):
        prev_by_journal[j][(j, int(c))] = set(g["int_id"].astype(int))

    used = set()
    for key, ids in cur.items():
        best = None
        best_j = 0.0
        for pkey, pids in prev_by_journal.get(key[0], {}).items():
            if pkey in used:
                continue
            union = ids | pids
            if not union:
                continue
            jac = len(ids & pids) / len(union)
            if jac > best_j:
                best_j = jac
                best = pkey
        if best and best_j >= threshold:
            used.add(best)
            rows.append(
                {
                    "journal": key[0],
                    "community_id": key[1],
                    "matched_community_id": best[1],
                    "paper_jaccard": round(best_j, 3),
                }
            )
        else:
            rows.append(
                {
                    "journal": key[0],
                    "community_id": key[1],
                    "matched_community_id": None,
                    "paper_jaccard": round(best_j, 3),
                }
            )
    return pd.DataFrame(rows)


def _previous_papers(run_timestamp: str) -> pd.DataFrame | None:
    prev = bqmod.previous_run_timestamp(run_timestamp)
    if prev and bqmod.table_exists("papers", prev):
        log.info("P5: comparing against previous run %s", prev)
        return bqmod.read_table("papers", prev)
    log.info("P5: no previous run in BigQuery — skipping community matching")
    return None


def run_p5(
    run_timestamp: str,
    decisions: pd.DataFrame | None = None,
    papers: pd.DataFrame | None = None,
) -> None:
    if decisions is None:
        decisions = bqmod.read_table("decisions", run_timestamp)

    prev_p = _previous_papers(run_timestamp)
    if prev_p is None or prev_p.empty:
        return
    if papers is None:
        papers = bqmod.read_table("papers", run_timestamp)
    matches = match_communities(papers, prev_p)
    bqmod.write_table(matches, "community_matches", run_timestamp)
