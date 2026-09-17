"""Per-journal profile for the further-work briefs.

Neurorobotics had a hardcoded gainer (computer vision) and loser (neuroscience).
Every other test journal gets those two poles from its own 2020 → latest share shift.
"""
from __future__ import annotations

import re
from pathlib import Path

from paths import WORK_DIR

STOP = {"frontiers", "in", "and", "the", "of", "for", "a"}

from collections import defaultdict


def primary_share_by_year(maps_journal: dict, labels: dict[int, str]) -> list[dict]:
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
        row = {"year": int(y), "articles": n, "oos_pct": round(100 * oos_n[y] / n, 1)}
        for cid, lab in labels.items():
            row[lab] = round(100 * by[y].get(cid, 0) / n, 1)
        rows.append(row)
    return rows


def contested_oos_titles(maps_journal: dict, keywords: tuple[str, ...], limit: int = 12) -> list[dict]:
    out = []
    keys = tuple(k.lower() for k in keywords if k)
    for p in maps_journal.get("scatter") or []:
        if p.get("s") != 0:
            continue
        title = p.get("t") or ""
        low = title.lower()
        if keys and not any(k in low for k in keys):
            continue
        out.append({"year": p.get("yr"), "community_id": p.get("c"), "title": title})
    out.sort(key=lambda r: (r.get("year") or 0, r.get("community_id") or 0))
    return out[:limit]



def journal_slug(name: str) -> str:
    short = re.sub(r"^Frontiers in\s+", "", name, flags=re.I)
    slug = re.sub(r"[^a-z0-9]+", "_", short.lower()).strip("_")
    return slug or "journal"


def journal_short(name: str) -> str:
    return re.sub(r"^Frontiers in\s+", "", name, flags=re.I)


def journal_dir(name: str) -> Path:
    return WORK_DIR / "journals" / journal_slug(name)


def list_journal_names(scope: dict) -> list[str]:
    return [j.get("name") for j in (scope.get("journals") or []) if j.get("name")]


def _share_map(rows: list[dict]) -> dict[int, dict]:
    out = {}
    for r in rows or []:
        cid = r.get("comm_id")
        if cid is None:
            continue
        out[int(cid)] = {
            "id": int(cid),
            "label": r.get("label") or f"Community {cid}",
            "share": float(r.get("share_of_year") or 0),
            "papers": int(r.get("papers") or 0),
        }
    return out


def journal_profile(scope_journal: dict) -> dict:
    """Gainer / loser communities plus the primary set used in mix charts."""
    name = scope_journal["name"]
    ps = scope_journal.get("primary_shift") or {}
    baseline = _share_map(ps.get("baseline_top") or [])
    latest = _share_map(ps.get("latest_top") or [])
    ids = set(int(x) for x in (ps.get("baseline_primary_ids") or []))
    ids |= set(int(x) for x in (ps.get("latest_primary_ids") or []))
    for row in scope_journal.get("top_communities") or []:
        if row.get("is_primary") and row.get("comm_id") is not None:
            ids.add(int(row["comm_id"]))

    labels = {}
    for row in scope_journal.get("top_communities") or []:
        cid = row.get("comm_id")
        if cid is None:
            continue
        labels[int(cid)] = row.get("label") or f"Community {cid}"
    for src in (baseline, latest):
        for cid, rec in src.items():
            labels.setdefault(cid, rec["label"])

    deltas = []
    for cid in ids | set(baseline) | set(latest):
        b = baseline.get(cid, {}).get("share", 0.0)
        l = latest.get(cid, {}).get("share", 0.0)
        deltas.append(
            {
                "id": cid,
                "label": labels.get(cid, f"Community {cid}"),
                "baseline_share": round(b, 1),
                "latest_share": round(l, 1),
                "delta": round(l - b, 1),
            }
        )
    deltas.sort(key=lambda r: r["delta"], reverse=True)
    gainer = deltas[0] if deltas else {"id": None, "label": "gaining community", "delta": 0}
    loser_pool = [d for d in deltas if d["id"] != gainer["id"]]
    loser_pool.sort(key=lambda r: r["delta"])
    loser = loser_pool[0] if loser_pool else {"id": None, "label": "core community", "delta": 0}

    # Mix chart: primary communities, largest first, capped so the legend stays readable.
    ranked = []
    for row in scope_journal.get("top_communities") or []:
        if not row.get("is_primary"):
            continue
        ranked.append((int(row["comm_id"]), row.get("label"), float(row.get("share_of_journal") or 0)))
    if not ranked:
        ranked = [(d["id"], d["label"], abs(d["delta"])) for d in deltas]
    ranked.sort(key=lambda t: -t[2])
    chart = ranked[:5]

    # The narrative names the gainer and the loser, so both have to be on the chart
    # even when neither is a top-5 community by share.
    chart_ids = {cid for cid, _, _ in chart}
    poles = [p["id"] for p in (gainer, loser) if p["id"] is not None]
    for pole in (gainer, loser):
        cid = pole["id"]
        if cid is None or cid in chart_ids:
            continue
        entry = next(
            (t for t in ranked if t[0] == cid),
            (cid, pole["label"], pole.get("latest_share", 0.0)),
        )
        chart.append(entry)
        chart_ids.add(cid)
    if len(chart) > 5:
        kept = [t for t in chart if t[0] in poles]
        for t in chart:
            if len(kept) >= 5:
                break
            if t[0] not in poles:
                kept.append(t)
        chart = kept
    chart.sort(key=lambda t: -t[2])

    primary_ids = {cid for cid, _, _ in chart}
    primary_ids.add(gainer["id"])
    primary_ids.add(loser["id"])
    primary_ids.discard(None)
    primary_labels = {cid: labels[cid] for cid in primary_ids if cid in labels}

    return {
        "name": name,
        "slug": journal_slug(name),
        "short": journal_short(name),
        "gainer": gainer,
        "loser": loser,
        "primary_ids": sorted(primary_ids),
        "primary_labels": primary_labels,
        "chart_labels": [lab for _, lab, _ in chart],
        "primary_changed": bool(ps.get("changed")),
        "gained_labels": ps.get("gained_labels") or [],
        "lost_labels": ps.get("lost_labels") or [],
        "keywords": _keywords(name, primary_labels),
    }


def _keywords(name: str, labels: dict) -> tuple[str, ...]:
    tokens = []
    for part in re.split(r"[^A-Za-z]+", journal_short(name).lower()):
        if len(part) >= 4 and part not in STOP:
            tokens.append(part)
    for lab in labels.values():
        for part in re.split(r"[^A-Za-z]+", lab.lower()):
            if len(part) >= 5 and part not in STOP:
                tokens.append(part)
    # Stable unique, keep the first ~12 so contested-OOS sampling stays tight.
    seen = []
    for t in tokens:
        if t not in seen:
            seen.append(t)
    return tuple(seen[:12])


def rename_candidates(profile: dict) -> list[tuple[str, str, str]]:
    """(title, what it signals, watch-out) — fit to mix, not switching cost."""
    short = profile["short"]
    g = profile["gainer"]["label"]
    l = profile["loser"]["label"]
    return [
        (
            f"Frontiers in {short} and {g}",
            f"Keeps the current title and names the gaining community ({g}) beside it.",
            "Longest option; two-field titles can read as a merger rather than a restatement.",
        ),
        (
            f"Frontiers in {g}",
            f"The most literal fit to where share has moved (latest {profile['gainer']['latest_share']}%).",
            f"Drops the {short} identity and the declining {l} core.",
        ),
        (
            f"Frontiers in {l} and {g}",
            f"Names both poles of the shift: {l} (losing share) and {g} (gaining).",
            "Generic pairing; may not match how authors already search for the journal.",
        ),
        (
            f"Frontiers in {short}",
            "Keep the current name and restating scope only.",
            "Leaves the masthead describing the smaller half of recent output if the mix has flipped.",
        ),
    ]
