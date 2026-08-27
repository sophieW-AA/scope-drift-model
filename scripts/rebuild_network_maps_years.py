"""
Rebuild network_maps.html with year slider support from an existing scope_dashboard.html.

Enriches scatter points with pub year from BigQuery (int_id -> year), then writes
output/network_maps.html using the current NETWORK_MAPS_TEMPLATE.

Usage (from repo root):
    set RUN_TIMESTAMP=20260721_122750
    python scripts/rebuild_network_maps_years.py
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

from build_unified_dashboard import (  # noqa: E402
    BQ_DATASET,
    BQ_PROJECT,
    OUTPUT_DIR,
    RUN_TIMESTAMP,
    build_network_maps_dashboard,
    combine_dashboards,
)


def _load_scope_data(path: Path) -> dict:
    text = path.read_text(encoding="utf-8")
    for line in text.splitlines():
        if line.startswith("const DATA = "):
            raw = line[len("const DATA = ") :]
            if raw.endswith(";"):
                raw = raw[:-1]
            return json.loads(raw)
    raise RuntimeError(f"No DATA block found in {path}")


def _fetch_years(int_ids: list[int]) -> dict[int, int]:
    from google.cloud import bigquery

    if not RUN_TIMESTAMP:
        raise RuntimeError("RUN_TIMESTAMP env var is required")

    client = bigquery.Client(project=BQ_PROJECT, location="EU")
    tbl = f"{BQ_PROJECT}.{BQ_DATASET}.pub_metadata_raw_{RUN_TIMESTAMP}"
    # Chunk to keep query size reasonable
    years: dict[int, int] = {}
    chunk = 5000
    for i in range(0, len(int_ids), chunk):
        batch = int_ids[i : i + chunk]
        ids_sql = ", ".join(str(x) for x in batch)
        q = f"""
        SELECT int_id, EXTRACT(YEAR FROM SAFE.PARSE_TIMESTAMP('%Y-%m-%d', SUBSTR(CAST(date AS STRING), 1, 10))) AS pub_year
        FROM `{tbl}`
        WHERE int_id IN ({ids_sql})
          AND date IS NOT NULL
        """
        df = client.query(q).to_dataframe()
        for _, row in df.iterrows():
            if row["pub_year"] is None:
                continue
            years[int(row["int_id"])] = int(row["pub_year"])
    return years


def main() -> None:
    scope_path = OUTPUT_DIR / "scope_dashboard.html"
    if not scope_path.exists():
        raise SystemExit(f"Missing {scope_path}")

    print(f"Loading {scope_path} …")
    data = _load_scope_data(scope_path)
    journals = data.get("journals") or []
    ids = sorted({int(p["i"]) for j in journals for p in (j.get("scatter") or [])})
    print(f"  {len(journals)} journals, {len(ids):,} scatter papers")

    print(f"Fetching years from BigQuery (run {RUN_TIMESTAMP}) …")
    year_map = _fetch_years(ids)
    print(f"  resolved {len(year_map):,} / {len(ids):,} years")

    missing = 0
    for j in journals:
        for p in j.get("scatter") or []:
            yr = year_map.get(int(p["i"]))
            if yr is None:
                missing += 1
                p["yr"] = None
            else:
                p["yr"] = yr
    if missing:
        print(f"  warning: {missing} papers without year")

    # Ensure meta years list for the slider
    meta = data.setdefault("meta", {})
    years = meta.get("oos_per_year_years") or []
    if not years:
        found = sorted({p["yr"] for j in journals for p in (j.get("scatter") or []) if p.get("yr")})
        meta["oos_per_year_years"] = found
        if found:
            meta["year_range"] = [found[0], found[-1]]

    print("Writing network_maps.html …")
    build_network_maps_dashboard(data)
    print("Refreshing combined_dashboard.html …")
    combine_dashboards()
    print("Done.")


if __name__ == "__main__":
    main()
