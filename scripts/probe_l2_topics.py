"""Probe the retained L2 layer for one level without running the LLM.

`export_l2_topics` depends only on the BigQuery taxonomy join, so the L2
granularity can be checked before spending LLM calls on every cluster.

Pass `--upload` to also write `cluster_l2_topics_{level}_{ts}`, which is how
the L2 layer gets published for a level the LLM naming step has not been run
for. The table is identical to the one `upload_labels_to_bigquery` writes.

Usage: python scripts/probe_l2_topics.py <timestamp> [level] [regex] [--upload]
"""

from __future__ import annotations

import os
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))
sys.path.insert(0, str(REPO / "src"))

import taxonomy_naming as tn  # noqa: E402


def main(argv: list[str]) -> int:
    upload = "--upload" in argv
    args = [a for a in argv if a != "--upload"]
    ts = args[1] if len(args) > 1 else os.environ.get("RUN_TIMESTAMP", "")
    level = args[2] if len(args) > 2 else "micro"
    pattern = args[3] if len(args) > 3 else r"embol|thromb|coagul"
    if not ts:
        print(
            "Usage: python scripts/probe_l2_topics.py <timestamp> [level] "
            "[regex] [--upload]"
        )
        return 1

    tn.RUN_TIMESTAMP = ts
    os.environ["RUN_TIMESTAMP"] = ts
    tn.CLUSTER_LEVEL = level
    tn.TBL_CLASSIF = f"{tn.BQ_SRC_PROJECT}.{tn.BQ_SRC_DATASET}.classification_raw_{ts}"
    tn.TBL_PUB_META = f"{tn.BQ_SRC_PROJECT}.{tn.BQ_SRC_DATASET}.pub_metadata_raw_{ts}"

    tn.init_clients()
    tn.load_taxonomy()

    comm = tn.load_level_communities(level)
    ids, totals = comm["community_ids"], comm["totals"]
    print(f"{level}: {len(ids)} communities")

    df_l2 = tn.pull_taxonomy_scores(level)
    tn.build_profiles(ids, tn.fetch_pub_year_counts(level), totals)
    tn.aggregate_to_higher_levels(df_l2)

    topics = tn.export_l2_topics(level)
    if topics.empty:
        print("no L2 topics produced")
        return 1

    out_dir = REPO / "logs"
    out_dir.mkdir(exist_ok=True)
    out = out_dir / f"l2_topics_{level}_{ts}.csv"
    topics.to_csv(out, index=False)
    print(f"\nwrote {out} ({len(topics)} rows)")

    print(f"\ndistinct L2 names: {topics.l2_name.nunique()} "
          f"vs distinct L1 names: {topics.l1_name.nunique()}")

    rank1 = topics[topics.l2_rank == 1]
    print(f"distinct rank-1 L2 names: {rank1.l2_name.nunique()} of {len(rank1)} communities")

    if "unit_name" in topics.columns:
        top3 = topics[topics.l2_rank <= 3].groupby("community_id").l2_share.sum()
        print(
            f"distinct unit names: {rank1.unit_name.nunique()} of {len(rank1)}; "
            f"rollup covers a median {rank1.l1_roll_share.median():.1%} of a "
            f"cluster vs {top3.median():.1%} for the top three L2 terms"
        )
        big = rank1.nlargest(10, "n_articles")[
            ["community_id", "unit_name", "l1_roll_share", "l2_name", "l2_share"]
        ]
        print("\n=== largest clusters, new name vs leading L2 term ===")
        print(big.to_string(index=False))

    if upload:
        empty = tn.pd.DataFrame()
        tn.upload_labels_to_bigquery(empty, empty, ts, topics)

    hits = topics[topics.l2_name.str.contains(pattern, case=False, regex=True, na=False)]
    print(f"\n=== L2 topics matching /{pattern}/ : {len(hits)} rows ===")
    if len(hits):
        cols = ["community_id", "l2_rank", "l2_name", "l2_share", "n_articles", "l1_name"]
        print(hits.sort_values(["l2_share"], ascending=False)[cols].to_string(index=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
