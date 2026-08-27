"""
Shared helpers for Frontiers in Neurorobotics further-work analysis.

Reads dashboard HTML from output/ (run 20260721_122750).
"""

from __future__ import annotations

import json
import re
from collections import defaultdict
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
OUTPUT = REPO / "output"
JOURNAL = "Frontiers in Neurorobotics"
PRIMARY_IDS = {4, 8, 15, 27}
PRIMARY_LABELS = {
    8: "Computer vision",
    27: "Therapeutic Movement Sciences",
    15: "Autonomous Systems and Control",
    4: "Neuroscience",
}
NEURO_KEYWORDS = (
    "robot",
    "exoskeleton",
    "prosthetic",
    "neural",
    "motor",
    "bci",
    "embodied",
    "semg",
    "kinematic",
    "dexterous",
    "humanoid",
    "neurorobotic",
    "rehabilitation",
)


def load_js_const(path: Path, markers: tuple[str, ...] = ("const DATA = ", "const D=", "const D = ")) -> dict:
    text = path.read_text(encoding="utf-8")
    for marker in markers:
        i = text.find(marker)
        if i < 0:
            continue
        start = i + len(marker)
        if marker.endswith("{"):
            start = i + len(marker) - 1
        data, _ = json.JSONDecoder().raw_decode(text, start)
        return data
    raise ValueError(f"No DATA/D JSON found in {path}")


def load_dashboards() -> tuple[dict, dict, dict]:
    scope = load_js_const(OUTPUT / "scope_dashboard.html")
    drift = load_js_const(OUTPUT / "drift_dashboard.html", ("const D=", "const D = ", "const DATA = "))
    maps = load_js_const(OUTPUT / "network_maps.html")
    return scope, drift, maps


def get_journal(scope_or_maps: dict, name: str = JOURNAL) -> dict:
    for j in scope_or_maps.get("journals") or []:
        if j.get("name") == name:
            return j
    raise KeyError(name)


def drift_trend(drift: dict, name: str = JOURNAL) -> dict:
    return (drift.get("jsd_trends") or {}).get(name) or {}


def primary_share_by_year(maps_journal: dict) -> list[dict]:
    by = defaultdict(lambda: defaultdict(int))
    tot = defaultdict(int)
    oos_n = defaultdict(int)
    for p in maps_journal.get("scatter") or []:
        y = p.get("yr")
        if y is None:
            continue
        by[y][p["c"]] += 1
        tot[y] += 1
        if p.get("s") == 0:
            oos_n[y] += 1

    rows = []
    for y in sorted(tot):
        n = tot[y]
        row = {
            "year": int(y),
            "articles": n,
            "oos_pct": round(100 * oos_n[y] / n, 1),
        }
        for cid, lab in PRIMARY_LABELS.items():
            row[lab] = round(100 * by[y].get(cid, 0) / n, 1)
        rows.append(row)
    return rows


def contested_oos_titles(maps_journal: dict, limit: int = 40) -> list[dict]:
    out = []
    for p in maps_journal.get("scatter") or []:
        if p.get("s") != 0:
            continue
        title = p.get("t") or ""
        low = title.lower()
        if not any(k in low for k in NEURO_KEYWORDS):
            continue
        out.append(
            {
                "year": p.get("yr"),
                "community_id": p.get("c"),
                "title": title,
            }
        )
    out.sort(key=lambda r: (r.get("year") or 0, r.get("community_id") or 0))
    return out[:limit]


def onset_year(trend: dict, threshold: float = 0.20) -> int | None:
    years = trend.get("years") or []
    jsds = trend.get("jsd") or []
    for y, jsd in zip(years, jsds):
        if y == years[0]:
            continue
        if jsd >= threshold:
            return int(y)
    return None


def run_meta(scope: dict) -> dict:
    return scope.get("run_metadata") or {}


def load_section_rt_summary() -> dict:
    """Load JSON from probe_sections_rts.py (run that script first if missing)."""
    path = REPO / "further_work" / "neurorobotics_section_rt_summary.json"
    if not path.exists():
        raise FileNotFoundError(
            f"Missing {path.name}. Run: python further_work/probe_sections_rts.py"
        )
    return json.loads(path.read_text(encoding="utf-8"))


def load_rt_tables() -> tuple["pd.DataFrame", "pd.DataFrame", "pd.DataFrame"]:
    """Return (launch_cohorts, oos_by_topic, oos_by_year_rt) CSVs from the probe."""
    import pandas as pd

    fw = REPO / "further_work"
    launch = pd.read_csv(fw / "neurorobotics_rt_launch_cohorts.csv")
    by_topic = pd.read_csv(fw / "neurorobotics_rt_oos_by_topic.csv")
    by_year = pd.read_csv(fw / "neurorobotics_oos_by_year_rt.csv")
    return launch, by_topic, by_year
