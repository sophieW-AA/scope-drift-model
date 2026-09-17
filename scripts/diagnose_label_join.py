"""Check whether cluster_labels_{level}_{ts} actually describes classification_raw_{ts}.

The dashboard joins labels to clusters on cluster_id alone, with no check that the
label row came from the same clustering. This compares each label table's stored
n_papers against real cluster sizes in every classification run, so a label table
built against a different run shows up as a size mismatch.
"""

from __future__ import annotations

import argparse
import sys

from google.cloud import bigquery

PROJECT = "ocean-tech-adv-analytics-c-tfs"
LABEL_DATASET = "taxonomy_labelling"
LEVELS = ("micro", "meso", "macro")


def list_tables(client: bigquery.Client) -> list[tuple[str, str, str, int]]:
    sql = f"""
    SELECT table_schema, table_name,
           FORMAT_TIMESTAMP('%Y-%m-%d %H:%M', creation_time) AS created,
           total_rows
    FROM `{PROJECT}.region-eu.INFORMATION_SCHEMA.TABLE_STORAGE`
    WHERE table_name LIKE 'cluster_labels%'
       OR table_name LIKE 'classification_raw%'
    ORDER BY table_name
    """
    return [
        (r.table_schema, r.table_name, r.created, r.total_rows)
        for r in client.query(sql).result()
    ]


def cluster_sizes(client: bigquery.Client, dataset: str, ts: str, level: str) -> dict:
    sql = f"""
    SELECT {level} AS cluster_id, COUNT(*) AS n
    FROM `{PROJECT}.{dataset}.classification_raw_{ts}`
    GROUP BY cluster_id
    """
    return {int(r.cluster_id): int(r.n) for r in client.query(sql).result()}


def label_rows(client: bigquery.Client, ts: str, level: str) -> dict:
    sql = f"""
    SELECT cluster_id, short_label, n_papers
    FROM `{PROJECT}.{LABEL_DATASET}.cluster_labels_{level}_{ts}`
    """
    return {
        int(r.cluster_id): (r.short_label, int(r.n_papers or 0))
        for r in client.query(sql).result()
    }


def compare(labels: dict, sizes: dict) -> tuple[int, int, int]:
    """Return (exact n_papers matches, ids present in both, total label rows)."""
    shared = [cid for cid in labels if cid in sizes]
    exact = sum(1 for cid in shared if labels[cid][1] == sizes[cid])
    return exact, len(shared), len(labels)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--ts", required=True, help="run timestamp of the dashboard")
    ap.add_argument(
        "--class-dataset",
        default="scope_drift",
        help="dataset holding classification_raw_{ts}",
    )
    args = ap.parse_args()

    client = bigquery.Client(project=PROJECT, location="EU")

    print("=" * 78)
    print("TABLES")
    print("=" * 78)
    class_runs = []
    label_runs = set()
    for schema, name, created, rows in list_tables(client):
        print(f"{created}  {schema:20s} {name:46s} rows={rows}")
        if name.startswith("classification_raw_"):
            class_runs.append((schema, name.replace("classification_raw_", "")))
        for lvl in LEVELS:
            if name.startswith(f"cluster_labels_{lvl}_"):
                label_runs.add(name.replace(f"cluster_labels_{lvl}_", ""))

    print()
    print("=" * 78)
    print(f"DOES cluster_labels_*_{args.ts} DESCRIBE classification_raw_{args.ts}?")
    print("=" * 78)

    for level in LEVELS:
        try:
            labels = label_rows(client, args.ts, level)
        except Exception as e:
            print(f"{level:6s} no label table for {args.ts}: {str(e)[:90]}")
            continue

        print(f"\n--- {level} ({len(labels)} label rows) ---")
        best = []
        for schema, ts in class_runs:
            try:
                sizes = cluster_sizes(client, schema, ts, level)
            except Exception:
                continue
            exact, shared, total = compare(labels, sizes)
            pct = 100 * exact / max(total, 1)
            best.append((pct, exact, shared, total, ts, schema))
        best.sort(reverse=True)
        for pct, exact, shared, total, ts, schema in best[:6]:
            flag = "  <-- dashboard run" if ts == args.ts else ""
            print(
                f"  vs classification_raw_{ts} ({schema}): "
                f"n_papers exact {exact}/{total} ({pct:.0f}%), ids overlapping {shared}{flag}"
            )

        # Show a few concrete rows against the dashboard's own run
        try:
            sizes = cluster_sizes(client, args.class_dataset, args.ts, level)
        except Exception:
            continue
        print(f"  sample (label n_papers vs real size in {args.ts}):")
        for cid in sorted(labels)[:6]:
            lab, n = labels[cid]
            real = sizes.get(cid, "absent")
            mark = "ok" if real == n else "MISMATCH"
            print(f"    id={cid:<5} {lab[:34]:34s} label={n:<8} real={real:<8} {mark}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
