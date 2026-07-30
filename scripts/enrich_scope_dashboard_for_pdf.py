"""
Enrich existing scope_dashboard.html with:
  - primary_shift (2020 vs latest year primary clusters)
  - example_papers preferring 2026 titles

Does NOT re-run LLM borderline / layout — reuses in_scope_cluster_ids and
paper_scope_overrides already stored in the dashboard.

Usage:
  set RUN_TIMESTAMP=20260721_122750
  python scripts/enrich_scope_dashboard_for_pdf.py
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

import pandas as pd

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "src"))

import build_unified_dashboard as bud  # noqa: E402

SCOPE_HTML = REPO / "output" / "scope_dashboard.html"
CLUSTER_LEVEL = os.environ.get("CLUSTER_LEVEL", "macro")


def load_scope_html(path: Path) -> tuple[str, dict, int, int]:
    text = path.read_text(encoding="utf-8")
    marker = "const DATA = "
    i = text.find(marker)
    if i < 0:
        raise ValueError(f"No DATA JSON in {path}")
    start = i + len(marker)
    data, end = json.JSONDecoder().raw_decode(text, start)
    return text, data, start, end


def apply_scope_flags(jdf: pd.DataFrame, journal_obj: dict) -> pd.DataFrame:
    """Reconstruct is_oos / is_borderline from stored dashboard scope sets."""
    out = jdf.copy()
    in_scope = {int(c) for c in (journal_obj.get("in_scope_cluster_ids") or [])}
    borderline = {int(c) for c in (journal_obj.get("borderline_cluster_ids") or [])}
    overrides = journal_obj.get("paper_scope_overrides") or {}

    out["is_oos"] = ~out[CLUSTER_LEVEL].astype(int).isin(in_scope)
    out["is_borderline"] = out[CLUSTER_LEVEL].astype(int).isin(borderline)
    out["hard_negative"] = False
    out["paper_demoted"] = False

    for iid_str, entry in overrides.items():
        try:
            iid = int(iid_str)
        except (TypeError, ValueError):
            continue
        mask = out["int_id"] == iid
        if not mask.any():
            continue
        verdict = str((entry or {}).get("verdict") or "").lower()
        source = str((entry or {}).get("source") or "")
        if verdict in {"out_of_scope", "oos"}:
            out.loc[mask, "is_oos"] = True
            out.loc[mask, "is_borderline"] = False
            if source == "hard_negative":
                out.loc[mask, "hard_negative"] = True
            if source == "paper_llm":
                out.loc[mask, "paper_demoted"] = True
    return out


def main() -> None:
    if not os.environ.get("RUN_TIMESTAMP"):
        # Fall back to timestamp stored in the dashboard itself
        pass

    text, data, start, end = load_scope_html(SCOPE_HTML)
    journals = data.get("journals") or []
    if not journals:
        raise SystemExit("No journals in scope dashboard")

    meta_ts = (data.get("run_metadata") or {}).get("run_timestamp")
    if not os.environ.get("RUN_TIMESTAMP") and meta_ts:
        os.environ["RUN_TIMESTAMP"] = str(meta_ts)
        bud.RUN_TIMESTAMP = str(meta_ts)

    journal_names = [j["name"] for j in journals]
    os.environ["JOURNALS"] = ",".join(journal_names)
    bud.JOURNALS = journal_names

    print(f"RUN_TIMESTAMP={bud.RUN_TIMESTAMP}")
    print(f"Journals ({len(journal_names)}): {journal_names}")

    bud.GPT_LABELS = bud.load_gpt_labels_single(CLUSTER_LEVEL)
    bud.GPT_LABELS_ALL = bud.load_gpt_labels_all()

    print("Loading papers from BigQuery…")
    df = bud.load_merged_data()
    print(f"Loaded {len(df):,} papers")

    for j in journals:
        name = j["name"]
        jdf = df[df["journal"] == name].copy()
        if jdf.empty:
            print(f"  skip (no rows): {name}")
            continue
        jdf = apply_scope_flags(jdf, j)
        j["primary_shift"] = bud.compute_primary_shift(jdf, baseline_year=2020)
        j["example_papers"] = bud.sample_example_papers(
            jdf, n_each=20, prefer_year=2026, random_state=42, journal=name
        )
        ps = j["primary_shift"]
        years = {}
        clear_oos = 0
        for e in j["example_papers"]:
            y = e.get("year")
            years[y] = years.get(y, 0) + 1
            if not e.get("is_in_scope") and (
                e.get("hard_negative") or e.get("paper_demoted")
            ):
                clear_oos += 1
        print(
            f"  {name}: changed={ps.get('changed')} "
            f"examples_by_year={dict(sorted((k or 0, v) for k, v in years.items()))} "
            f"clear_oos_examples={clear_oos}"
        )

    new_json = json.dumps(data, separators=(",", ":"))
    new_text = text[:start] + new_json + text[end:]
    SCOPE_HTML.write_text(new_text, encoding="utf-8")
    print(f"Updated {SCOPE_HTML}")

    bud.build_paper_examples_dashboard(journals)
    print(f"Updated {bud.OUTPUT_DIR / 'paper_examples.html'}")


if __name__ == "__main__":
    main()
