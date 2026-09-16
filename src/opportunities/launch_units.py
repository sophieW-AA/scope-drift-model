"""Launch units — sizing the thing we would actually launch.

A launch unit is what a journal or a section could be, not the community that
happened to surface it. Getting that unit right is most of the work:

    journal   one meso community, or a bundle of micro communities sharing a
              meso parent, used when the parent is too broad to be one title
    section   one micro community, or a small bundle of them under one parent

That split is not a preference. There are ~406 meso communities against ~220
Frontiers journals, and ~3,031 micro communities against ~1,500 specialty
sections — meso is journal-shaped and micro is section-shaped, and the cluster
names say the same thing ("Haematology" and "Materials Science" at meso;
"Object detection" and "Learning to rank" at micro). Proposing a journal from
one micro community gives you "Frontiers in Image Captioning". The size bands
are calibrated against the addressable market of the journals and sections
Frontiers already runs rather than asserted.

Presence is then read on two axes that used to be collapsed into one:

    ownership   absent / scattered / drift / core — which title, if any, owns
                the community, and whether its papers belong there
    coverage    thin / under-indexed / at-or-above, measured against
                Frontiers' own share of world output

Conflating those is what let communities Frontiers barely touches be reported
as "already publish", and what hid drift inside "covered". Ownership answers
"is this ours"; coverage answers "are we under-weight". A journal can own a
community and still be under-indexed in it, and Frontiers can hold plenty of
papers in a community no title owns.

    python src/opportunities/launch_units.py --run 20260827_081311
"""

from __future__ import annotations

import argparse
import logging
import re
import sys
from pathlib import Path

import pandas as pd

_SRC = Path(__file__).resolve().parents[1]
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))

from opportunities import config as C  # noqa: E402
from opportunities import market_map  # noqa: E402

log = logging.getLogger("opportunities.units")

# Market columns copied straight onto a unit when it is a whole community.
MARKET_CARRY = (
    "n_global_3y",
    "n_global_base_ytd",
    "n_global_late_ytd",
    "n_fi_3y",
    "cagr",
    "excess_cagr",
    "fi_share",
    "fi_share_vs_portfolio",
    "is_large",
    "is_growing",
    "is_opportunity",
    "opportunity_kind",
    "primary_world_field",
    "primary_world_field_share",
    "world_field_mix",
    "world_field_is_opportunity",
    "world_field_action",
    "world_field_n_global_3y",
    "world_field_cagr",
    "name",
    "name_source",
)


# --- inputs -----------------------------------------------------------------


def fetch_hierarchy(
    run_timestamp: str, parent: str | None = None, child: str | None = None
) -> pd.DataFrame:
    """One row per child cluster with the parent it sits inside.

    Leiden emits the levels as columns on the same row, so the nesting is read
    back rather than inferred. `parent_purity` records how cleanly a child sits
    in one parent; anything below 1.0 means the levels were not produced from
    a single hierarchical run and bundling would be crossing boundaries.
    """
    from opportunities import bq as bqmod

    parent = bqmod._assert_level(parent or C.UNIT_JOURNAL_LEVEL)
    child = bqmod._assert_level(child or C.UNIT_SECTION_LEVEL)
    tbl = f"{C.BQ_PROJECT}.{C.BQ_DATASET}.classification_raw_{run_timestamp}"
    q = f"""
    SELECT
      CAST({child} AS INT64) AS child_id,
      CAST({parent} AS INT64) AS parent_id,
      COUNT(*) AS n
    FROM `{tbl}`
    WHERE {child} IS NOT NULL AND {parent} IS NOT NULL
    GROUP BY 1, 2
    """
    df = bqmod.client().query(q).to_dataframe()
    if df.empty:
        raise RuntimeError(f"no {child}/{parent} hierarchy in {tbl}")
    total = df.groupby("child_id")["n"].sum()
    top = (
        df.sort_values(["child_id", "n"], ascending=[True, False])
        .drop_duplicates("child_id")
        .copy()
    )
    top["parent_purity"] = (top["n"] / top["child_id"].map(total)).round(4)
    clean = float((top["parent_purity"] >= 0.999).mean())
    log.info(
        "hierarchy: %s %s children under %s %s parents | %.1f%% sit wholly "
        "inside one parent",
        f"{len(top):,}",
        child,
        f"{top['parent_id'].nunique():,}",
        parent,
        clean * 100,
    )
    if clean < 0.9:
        log.warning(
            "only %.0f%% of %s clusters nest cleanly in a %s parent — bundles "
            "may span unrelated neighbourhoods",
            clean * 100,
            child,
            parent,
        )
    return top[["child_id", "parent_id", "parent_purity"]]


def fetch_frontiers_placement(run_timestamp: str) -> pd.DataFrame:
    """Frontiers papers with the two flags that separate core scope from drift.

    Read from the P0 `papers` table rather than recomputed, because
    `in_baseline_primary` (was this area part of the title's baseline output)
    and `is_oos` (did the scope classifier reject the paper) only exist there.
    Without them, presence can say how much Frontiers publishes in a community
    but not whether it belongs there.
    """
    from opportunities import bq as bqmod

    fq = bqmod.fq_table("papers", run_timestamp)
    q = f"""
    SELECT
      CAST(journal AS STRING) AS journal,
      CAST(community_id AS INT64) AS parent_id,
      CAST(drilldown_id AS INT64) AS child_id,
      CAST(year AS INT64) AS year,
      COALESCE(CAST(in_baseline_primary AS BOOL), FALSE) AS in_baseline_primary,
      COALESCE(CAST(is_oos AS BOOL), FALSE) AS is_oos
    FROM `{fq}`
    WHERE drilldown_id IS NOT NULL AND journal IS NOT NULL
    """
    df = bqmod.client().query(q).to_dataframe()
    if df.empty:
        raise RuntimeError(
            f"{fq} is empty — run `python src/opportunities/run.py --phase p0` first"
        )
    for col in ("parent_id", "child_id", "year"):
        df[col] = df[col].astype(int)
    log.info(
        "placement: %s Frontiers papers | %s journals | %s scored out-of-scope "
        "(%.1f%% — the rest were not covered by the scope classifier)",
        f"{len(df):,}",
        f"{df['journal'].nunique():,}",
        f"{int(df['is_oos'].sum()):,}",
        100.0 * float(df["is_oos"].mean()),
    )
    return df


# --- size bands -------------------------------------------------------------


def _norm_journal(s: str) -> str:
    return re.sub(r"[^a-z0-9]+", " ", str(s or "").lower()).strip()


def _pct_summary(s: pd.Series) -> str:
    q = s.quantile([0.1, 0.25, 0.5, 0.75, 0.9])
    return " | ".join(
        f"p{int(p * 100)} {int(v):,}" for p, v in zip(q.index, q.to_numpy())
    )


def calibrate_bands(
    placement: pd.DataFrame,
    sections: pd.DataFrame | None,
    window_years: list[int],
    portfolio_share: float,
) -> dict:
    """Plausible community size for a journal and for a section.

    The **floor** of each band is a global publication rate: how much
    literature has to exist per year, published anywhere by anyone, before a
    community can carry a title. It is the same pair of numbers the market map
    gates on (`C.MARKET_LARGE_3Y`, `C.MARKET_MIN_3Y`), so the size a launch
    needs and the size that counts as an opportunity cannot drift apart, and it
    deliberately says nothing about Frontiers. Deriving it from Frontiers' own
    viability floors instead — the smallest live title, divided by Frontiers'
    share of world output — conflated "this field is big enough to publish in"
    with "Frontiers already publishes here", which is the coverage axis and is
    scored separately.

    The **ceiling** does measure against the live portfolio, because it answers
    a different question: how broad a community has one title ever actually
    covered? A journal publishing N papers per 3 years at Frontiers' ~1.6%
    share of world output is evidence that a community of N / 1.6% can be
    served by one title, so the top of the band is a high percentile of that
    addressable market. It exists to stop a 300,000-paper cluster being
    proposed as a single journal, not to score anything.

    The two bands meet at the journal floor, so on size alone a section is
    what clears the section floor but cannot stand as its own journal. Most
    section candidates no longer come from here at all — see
    `promote_relative_sections`.
    """
    share = float(portfolio_share) or 0.0158
    journal_floor = float(C.MARKET_LARGE_3Y)
    section_floor = float(C.MARKET_MIN_3Y)
    win = placement[placement["year"].isin(window_years)]
    journal_3y = win.groupby("journal").size()

    band = {
        "journal": (journal_floor, float(C.MARKET_LAUNCHABLE_MAX_3Y)),
        "section": (section_floor, journal_floor),
        "source": "global floors, config ceiling",
        "n_journals_calibrated": 0,
        "n_sections_calibrated": 0,
        "journal_median": journal_floor,
        "section_median": section_floor,
    }
    if len(journal_3y) < 20:
        log.warning(
            "only %s journals in the run — keeping the configured fallback ceiling",
            len(journal_3y),
        )
        return band

    hi_q = C.BAND_HIGH_PCT / 100.0
    log.info("journal output per 3y: %s papers", _pct_summary(journal_3y))
    # Ceiling only. Half the titles in the run publish under ~120 papers per 3
    # years — new launches, partnerships and titles winding down — so the
    # percentile is taken over the titles that clear `PAPER_FLOOR_JOURNAL`
    # rather than the raw distribution.
    established = journal_3y[journal_3y >= C.PAPER_FLOOR_JOURNAL]
    band["journal"] = (
        journal_floor,
        float(established.quantile(hi_q) / share)
        if len(established) >= 10
        else float(journal_3y.max() / share),
    )
    band["journal_median"] = float(
        (established.median() if len(established) else journal_3y.median()) / share
    )
    band["n_journals_calibrated"] = int(len(established))
    band["source"] = "global floors, ceiling calibrated against live titles"

    # Sections: split each journal's 3y output by the share each of its
    # specialty sections holds of its published articles. Journal naming
    # differs between the citation run and the taxonomy tables, so the join is
    # on a normalised title.
    if sections is not None and not sections.empty:
        sec = sections.copy()
        sec["_j"] = sec["journal"].map(_norm_journal)
        j_key = pd.Series(
            {j: _norm_journal(j) for j in journal_3y.index}, name="_j"
        )
        out_by_key = journal_3y.groupby(j_key).sum()
        sec = sec[sec["_j"].isin(out_by_key.index)].copy()
        if len(sec) >= 50:
            tot = sec.groupby("_j")["n_articles"].transform("sum")
            sec["section_3y"] = (
                sec["n_articles"] / tot.where(tot > 0, 1)
            ) * sec["_j"].map(out_by_key)
            log.info(
                "section output per 3y: %s papers",
                _pct_summary(sec["section_3y"]),
            )
            live = sec.loc[
                sec["section_3y"] >= C.PAPER_FLOOR_SECTION, "section_3y"
            ]
            if len(live) >= 10:
                # The section band itself is the global floor up to the journal
                # floor; this is kept as an observation of how big the
                # communities behind live sections actually are, so a floor
                # wildly out of step with the portfolio is visible in the log.
                band["section_median"] = float(live.median() / share)
                band["n_sections_calibrated"] = int(len(live))

    log.info(
        "size bands (%s): journal %s-%s global papers per 3y = %s/yr published "
        "anywhere | section %s-%s = %s/yr | for reference, the communities "
        "behind live titles run to a median of %s papers per 3y (%s titles) and "
        "live sections to %s (%s sections) at Frontiers' %.2f%% share",
        band["source"],
        f"{int(band['journal'][0]):,}",
        f"{int(band['journal'][1]):,}",
        f"{C.UNIT_JOURNAL_MIN_GLOBAL_PER_YEAR:,}",
        f"{int(band['section'][0]):,}",
        f"{int(band['section'][1]):,}",
        f"{C.UNIT_SECTION_MIN_GLOBAL_PER_YEAR:,}",
        f"{int(band['journal_median']):,}",
        band["n_journals_calibrated"],
        f"{int(band['section_median']):,}",
        band["n_sections_calibrated"],
        share * 100,
    )
    return band


# --- units ------------------------------------------------------------------


def _greedy_bundles(
    kids: list[tuple[int, float]], target_min: float, target_max: float
) -> list[list[int]]:
    """Group one parent's children into units reaching `target_min`.

    Largest child first, so a bundle reaches journal size in as few members as
    possible and stays describable. A child that would push the bundle past the
    top of the band is not absorbed.
    """
    bundles: list[list[int]] = []
    current: list[int] = []
    total = 0.0
    for cid, n in kids:
        if n > target_max:
            continue
        if current and total + n > target_max:
            current, total = [], 0.0
        current.append(cid)
        total += n
        if total >= target_min or len(current) >= C.BUNDLE_MAX_MEMBERS:
            if total >= target_min:
                bundles.append(list(current))
            current, total = [], 0.0
    if current and total >= target_min:
        bundles.append(list(current))
    return bundles


def _unit_role(kind: str, n: float, jb: tuple, sb: tuple) -> str:
    """Which launch a unit of this size and kind could support."""
    if kind == "meso":
        if jb[0] <= n <= jb[1]:
            return "journal"
        return "too_broad" if n > jb[1] else "too_small"
    if kind == "micro_bundle":
        if jb[0] <= n <= jb[1]:
            return "journal"
        if sb[0] <= n <= sb[1]:
            return "section"
        return "too_broad" if n > jb[1] else "too_small"
    # A micro community is section-shaped as a rule, but a handful are whole
    # fields Leiden kept in one cluster — retrieval-augmented generation is
    # 101,000 papers. Size decides, since that is what the band is for; the
    # guard against "Frontiers in Image Captioning" is the journal floor, not
    # the level the cluster came from. The bands are contiguous, so journal is
    # tested first and a community sitting exactly on the floor reads as one.
    if jb[0] <= n <= jb[1]:
        return "journal"
    if sb[0] <= n <= sb[1]:
        return "section"
    return "too_broad" if n > max(sb[1], jb[1]) else "too_small"


def build_units(
    market_parent: pd.DataFrame,
    market_child: pd.DataFrame,
    hierarchy: pd.DataFrame,
    bands: dict,
    meta: dict,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Every candidate launch unit, plus the child communities each contains."""
    jb, sb = bands["journal"], bands["section"]
    kids = market_child.merge(
        hierarchy, left_on="community_id", right_on="child_id", how="inner"
    )
    parent_size = market_parent.set_index("community_id")["n_global_3y"]
    parent_name = market_parent.set_index("community_id")["name"]

    rows: list[dict] = []
    members: list[pd.DataFrame] = []

    # 1. Whole meso communities — the default journal unit.
    child_of = hierarchy.groupby("parent_id")["child_id"].apply(list)
    for _, r in market_parent.iterrows():
        cid = int(r["community_id"])
        uid = f"meso:{cid}"
        rows.append(
            {
                "unit_id": uid,
                "unit_kind": "meso",
                "parent_id": cid,
                "n_members": len(child_of.get(cid, [])),
                "member_ids": ",".join(str(c) for c in sorted(child_of.get(cid, []))),
                "role": _unit_role("meso", float(r["n_global_3y"]), jb, sb),
                **{c: r.get(c) for c in MARKET_CARRY},
            }
        )
        mine = child_of.get(cid, [])
        if mine:
            members.append(pd.DataFrame({"unit_id": uid, "child_id": mine}))

    # 2. Single micro communities — the default section unit.
    for _, r in kids.iterrows():
        cid = int(r["community_id"])
        if float(r["n_global_3y"]) < C.MARKET_MIN_3Y:
            continue
        uid = f"micro:{cid}"
        rows.append(
            {
                "unit_id": uid,
                "unit_kind": "micro",
                "parent_id": int(r["parent_id"]),
                "n_members": 1,
                "member_ids": str(cid),
                "role": _unit_role("micro", float(r["n_global_3y"]), jb, sb),
                **{c: r.get(c) for c in MARKET_CARRY},
            }
        )
        members.append(pd.DataFrame({"unit_id": [uid], "child_id": [cid]}))

    # 3. Bundles of micro children — the "cluster of micro" journal. Two cases
    #    need it: a meso parent too broad to be one title, and a parent we
    #    already cover where a group of its children is nonetheless growing and
    #    under-served. Only children that are an opportunity *and* below
    #    portfolio share are eligible, since the bundle exists to describe a
    #    gap. Bundles inside a parent that is itself proposed as a journal are
    #    folded back into it later by `dedupe_contained_units`.
    eligible = kids[
        kids["is_opportunity"].astype(bool)
        & (kids["fi_share_vs_portfolio"] < C.MARKET_COVERED_RATIO)
    ]
    n_bundles = 0
    n_broad = int(sum(1 for n in parent_size if float(n) > jb[1]))
    for pid, sub in eligible.groupby("parent_id"):
        if len(sub) < 2:
            continue
        ordered = [
            (int(c), float(n))
            for c, n in sub.sort_values("n_global_3y", ascending=False)[
                ["community_id", "n_global_3y"]
            ].itertuples(index=False)
        ]
        for i, group in enumerate(_greedy_bundles(ordered, jb[0], jb[1])):
            if len(group) < 2:
                # A single journal-sized child is already covered as a micro
                # unit and as part of its parent; wrapping it in a bundle would
                # just be the same proposal a third time.
                continue
            uid = f"bundle:{pid}:{i}"
            g = market_child[market_child["community_id"].isin(group)]
            row = _aggregate_bundle(g, meta)
            row["name"] = _bundle_name(g, parent_name.get(pid, ""))
            rows.append(
                {
                    "unit_id": uid,
                    "unit_kind": "micro_bundle",
                    "parent_id": pid,
                    "n_members": len(group),
                    "member_ids": ",".join(str(c) for c in sorted(group)),
                    "role": _unit_role(
                        "micro_bundle", float(row["n_global_3y"]), jb, sb
                    ),
                    "name_source": "bundle",
                    **row,
                }
            )
            members.append(pd.DataFrame({"unit_id": uid, "child_id": group}))
            n_bundles += 1

    units = pd.DataFrame(rows)
    member_df = (
        pd.concat(members, ignore_index=True)
        if members
        else pd.DataFrame(columns=["unit_id", "child_id"])
    )
    log.info(
        "units: %s meso, %s micro, %s micro bundles | %s meso parents are past "
        "the top of the journal band on their own",
        f"{int((units['unit_kind'] == 'meso').sum()):,}",
        f"{int((units['unit_kind'] == 'micro').sum()):,}",
        f"{n_bundles:,}",
        f"{n_broad:,}",
    )
    log.info(
        "roles: %s",
        ", ".join(
            f"{k} {v:,}" for k, v in units["role"].value_counts().items()
        ),
    )
    return units, member_df


def _aggregate_bundle(g: pd.DataFrame, meta: dict) -> dict:
    """Market position of a bundle, recomputed from its members.

    Growth cannot be averaged across members — it has to be recomputed from
    the summed like-for-like endpoints, or a bundle of one fast-growing and one
    shrinking topic reads as fast-growing.
    """
    base = float(g["n_global_base_ytd"].sum())
    late = float(g["n_global_late_ytd"].sum())
    n3 = float(g["n_global_3y"].sum())
    fi = float(g["n_fi_3y"].sum())
    k = max(int(meta["late_year"]) - int(meta["base_year"]), 1)
    corpus_cagr = float(meta["corpus_cagr"])
    portfolio = float(meta["fi_portfolio_share"]) or 1e-12

    cagr = (late / base) ** (1 / k) - 1 if base > 0 else float("nan")
    excess = cagr - corpus_cagr
    is_large = n3 >= C.MARKET_LARGE_3Y
    is_growing = bool(
        base >= C.MARKET_GROWTH_MIN_BASE
        and pd.notna(cagr)
        and excess >= C.MARKET_EXCESS_CAGR
    )
    fi_share = fi / n3 if n3 else 0.0
    kind = (
        "large_and_growing"
        if is_large and is_growing
        else "large"
        if is_large
        else "growing"
        if is_growing
        else ""
    )
    return {
        "n_global_3y": int(n3),
        "n_global_base_ytd": int(base),
        "n_global_late_ytd": int(late),
        "n_fi_3y": int(fi),
        "cagr": round(cagr, 6) if pd.notna(cagr) else None,
        "excess_cagr": round(excess, 6) if pd.notna(excess) else None,
        "fi_share": round(fi_share, 6),
        "fi_share_vs_portfolio": round(fi_share / portfolio, 6),
        "is_large": bool(is_large),
        "is_growing": is_growing,
        "is_opportunity": bool(is_large or is_growing),
        "opportunity_kind": kind,
    }


def _bundle_name(g: pd.DataFrame, parent_label: str) -> str:
    """Name a bundle from its largest members, with the parent as context."""
    names = (
        g.sort_values("n_global_3y", ascending=False)["name"]
        .astype(str)
        .str.split(" / ")
        .str[0]
        .tolist()
    )
    seen: list[str] = []
    for n in names:
        n = n.strip()
        if n and n not in seen:
            seen.append(n)
    head = " + ".join(seen[:3])
    parent = str(parent_label or "").split(" / ")[0].strip()
    if parent and parent.lower() not in head.lower():
        return f"{head} (within {parent})"
    return head


# --- ownership vs coverage --------------------------------------------------


def build_ownership(
    members: pd.DataFrame, placement: pd.DataFrame, window_years: list[int]
) -> pd.DataFrame:
    """Per (unit, journal): how much, whether it is core scope, how off-scope."""
    win = placement[placement["year"].isin(window_years)]
    j_tot = win.groupby("journal").size()
    pairs = members.merge(win, on="child_id", how="inner")
    if pairs.empty:
        log.warning("no Frontiers papers landed in any unit")
        return pd.DataFrame(
            columns=[
                "unit_id",
                "journal",
                "n_fi_3y",
                "baseline_share",
                "oos_pct",
                "share_of_journal",
                "share_of_unit_fi",
                "is_drift",
            ]
        )
    by = (
        pairs.groupby(["unit_id", "journal"])
        .agg(
            n_fi_3y=("year", "size"),
            n_baseline=("in_baseline_primary", "sum"),
            n_oos=("is_oos", "sum"),
        )
        .reset_index()
    )
    by["baseline_share"] = (by["n_baseline"] / by["n_fi_3y"]).round(4)
    by["oos_pct"] = (by["n_oos"] / by["n_fi_3y"] * 100).round(1)
    by["share_of_journal"] = (
        by["n_fi_3y"] / by["journal"].map(j_tot).replace(0, pd.NA)
    ).round(4)
    tot = by.groupby("unit_id")["n_fi_3y"].sum()
    by["share_of_unit_fi"] = (by["n_fi_3y"] / by["unit_id"].map(tot)).round(4)
    # Volume in an area that was not part of the title's baseline output
    # arrived by drift; a high out-of-scope rate says the same about work the
    # title does treat as its own. Either way it is not settled core scope.
    by["is_drift"] = (by["n_fi_3y"] >= C.UNIT_MIN_FI_PAPERS) & (
        (by["baseline_share"] < 0.5) | (by["oos_pct"] >= C.DRIFT_OOS_PCT)
    )
    log.info(
        "ownership: %s (unit, journal) pairs | %s carry drift volume",
        f"{len(by):,}",
        f"{int(by['is_drift'].sum()):,}",
    )
    return by


def _ownership_class(
    n_fi: float, top_share: float, top_drift: bool, drift_share: float
) -> str:
    """Who owns the unit, and whether the papers here belong to them.

    The `drift_share` test is what stops drift hiding behind `scattered`: in a
    large community no single title reaches the 40% ownership bar, so a title
    quietly printing off-baseline work there would otherwise be reported as
    "nobody owns this" and read as whitespace. It is a share rather than a
    presence test because in a 290,000-paper community *some* title always has
    a section's worth of off-baseline papers, and calling every such community
    drift buried the launch candidates instead.
    """
    if pd.isna(n_fi) or n_fi < C.UNIT_MIN_FI_PAPERS:
        return "absent"
    if pd.notna(top_share) and top_share >= C.OWNED_MIN_FI_SHARE:
        return "drift" if top_drift else "core"
    return "drift" if float(drift_share or 0) >= C.DRIFT_UNIT_SHARE else "scattered"


def _coverage_class(ratio) -> str:
    if pd.isna(ratio):
        return ""
    r = float(ratio)
    if r < C.MARKET_WHITESPACE_RATIO:
        return "thin"
    if r < C.MARKET_COVERED_RATIO:
        return "under_indexed"
    return "at_or_above"


def classify_units(units: pd.DataFrame, own: pd.DataFrame) -> pd.DataFrame:
    """Attach the owning title, the ownership class and the coverage class."""
    out = units.copy()
    cols = {
        "owner_journal": "",
        "owner_n_3y": 0,
        "owner_share_of_unit": 0.0,
        "owner_share_of_journal": 0.0,
        "owner_baseline_share": 0.0,
        "owner_oos_pct": 0.0,
        "n_journals_present": 0,
        "unit_n_fi_3y": 0,
        "drift_journals": "",
        "drift_share_of_unit": 0.0,
        "drift_lead_journal": "",
        "drift_lead_n_3y": 0,
        "drift_lead_share_of_journal": 0.0,
        "drift_lead_baseline_share": 0.0,
        "ownership": "absent",
    }
    for c, d in cols.items():
        out[c] = d
    if own.empty:
        out["coverage"] = out["fi_share_vs_portfolio"].map(_coverage_class)
        return out

    ranked = own.sort_values(["unit_id", "n_fi_3y"], ascending=[True, False])
    top = ranked.drop_duplicates("unit_id").set_index("unit_id")
    unit_fi = own.groupby("unit_id")["n_fi_3y"].sum()
    present = own[own["n_fi_3y"] >= C.UNIT_MIN_FI_PAPERS]
    n_present = present.groupby("unit_id")["journal"].nunique()
    drifting = present[present["is_drift"]].sort_values("n_fi_3y", ascending=False)
    # Drift that is material to the title doing it, by the same devotion gates
    # the drift tree uses for a section.
    material = drifting[
        (drifting["n_fi_3y"] >= C.PAPER_FLOOR_SECTION)
        | (drifting["share_of_journal"].fillna(0) >= C.SECTION_SHARE)
    ]
    drift = (
        drifting.groupby("unit_id").apply(
            lambda g: "; ".join(
                f"{r.journal} ({int(r.n_fi_3y)})" for r in g.itertuples()
            )
        )
        if len(drifting)
        else pd.Series(dtype=str)
    )

    uid = out["unit_id"]
    out["owner_journal"] = uid.map(top["journal"]).fillna("")
    out["owner_n_3y"] = uid.map(top["n_fi_3y"]).fillna(0).astype(int)
    out["owner_share_of_unit"] = uid.map(top["share_of_unit_fi"]).fillna(0.0)
    out["owner_share_of_journal"] = uid.map(top["share_of_journal"]).fillna(0.0)
    out["owner_baseline_share"] = uid.map(top["baseline_share"]).fillna(0.0)
    out["owner_oos_pct"] = uid.map(top["oos_pct"]).fillna(0.0)
    out["unit_n_fi_3y"] = uid.map(unit_fi).fillna(0).astype(int)
    out["n_journals_present"] = uid.map(n_present).fillna(0).astype(int)
    out["drift_journals"] = uid.map(drift).fillna("")
    owner_drift = uid.map(top["is_drift"]).fillna(False).astype(bool)
    material_units = set(material["unit_id"])
    drift_vol = drifting.groupby("unit_id")["n_fi_3y"].sum()
    drift_share = (uid.map(drift_vol) / uid.map(unit_fi)).fillna(0.0)
    drift_share = drift_share.where(uid.isin(material_units), 0.0)
    out["drift_share_of_unit"] = drift_share.round(4)
    # The title doing the drifting is not always the one holding the most
    # papers here, so the reroute case names the drifter explicitly.
    lead = drifting.drop_duplicates("unit_id").set_index("unit_id")
    out["drift_lead_journal"] = uid.map(lead["journal"]).fillna("")
    out["drift_lead_n_3y"] = uid.map(lead["n_fi_3y"]).fillna(0).astype(int)
    out["drift_lead_share_of_journal"] = (
        uid.map(lead["share_of_journal"]).fillna(0.0)
    )
    out["drift_lead_baseline_share"] = (
        uid.map(lead["baseline_share"]).fillna(0.0)
    )

    out["ownership"] = [
        _ownership_class(n, s, d, m)
        for n, s, d, m in zip(
            out["unit_n_fi_3y"],
            out["owner_share_of_unit"],
            owner_drift,
            out["drift_share_of_unit"],
        )
    ]
    out["coverage"] = out["fi_share_vs_portfolio"].map(_coverage_class)
    log.info(
        "ownership classes: %s",
        ", ".join(f"{k} {v:,}" for k, v in out["ownership"].value_counts().items()),
    )
    log.info(
        "coverage classes: %s",
        ", ".join(
            f"{k or 'unknown'} {v:,}" for k, v in out["coverage"].value_counts().items()
        ),
    )
    return out


# --- routing ----------------------------------------------------------------


def route_units(units: pd.DataFrame) -> pd.DataFrame:
    """One action per unit, from ownership, coverage, size role and growth.

    Ownership decides the family of action and coverage decides whether it is
    worth doing. A community nobody owns is a launch; one a title owns is an
    expand; one a title drifted into is a reroute or an intake gate, which is
    the case the old single presence axis could not express at all.
    """
    out = units.copy()
    actions: list[str] = []
    whys: list[str] = []

    for r in out.itertuples():
        own = r.ownership
        role = r.role
        opp = bool(r.is_opportunity)
        growing = bool(r.is_growing)
        thin = r.coverage in {"thin", "under_indexed"}
        size = f"{int(r.n_global_3y):,} global papers"
        grow = (
            f"{float(r.excess_cagr):+.1%}/yr vs corpus"
            if pd.notna(r.excess_cagr)
            else "growth not measurable"
        )
        # A large community that is emptying out is not somewhere to launch,
        # however big it still is today.
        declining = (
            pd.notna(r.excess_cagr)
            and float(r.excess_cagr) <= C.MARKET_DECLINE_EXCESS_CAGR
        )
        # Devotion gates, reused from the drift tree: is this material to the
        # title doing it, or a handful of stray papers?
        drifter = r.drift_lead_journal or r.owner_journal
        drift_n = int(r.drift_lead_n_3y or r.owner_n_3y or 0)
        material = (
            float(r.drift_lead_share_of_journal or 0) >= C.SECTION_SHARE
            or drift_n >= C.PAPER_FLOOR_SECTION
        )

        if own == "drift":
            if opp and role == "section" and material:
                actions.append("formalise_section")
                whys.append(
                    f"{drifter} already prints {drift_n:,} papers here outside "
                    f"its baseline scope, in a {size} community — name and gate "
                    f"it as a section rather than let it accrete"
                )
            elif opp:
                actions.append("reroute")
                whys.append(
                    f"drift into {drifter} ({drift_n:,} papers, "
                    f"{float(r.drift_lead_baseline_share):.0%} of it inside "
                    f"baseline scope) in a {size} community — needs a home, "
                    f"not a host"
                )
            else:
                actions.append("gate_intake")
                whys.append(
                    f"drift into {drifter} ({drift_n:,} papers) and the community "
                    f"is neither large nor growing — tighten intake"
                )
        elif own == "core":
            if growing and thin:
                actions.append("expand")
                whys.append(
                    f"{r.owner_journal} owns this ({float(r.owner_share_of_unit):.0%} "
                    f"of Frontiers output here) and it is growing {grow} while we "
                    f"stay under-indexed — expand"
                )
            elif growing:
                actions.append("expand")
                whys.append(
                    f"{r.owner_journal} owns this and it is growing {grow} — expand"
                )
            else:
                actions.append("continue")
                whys.append(f"{r.owner_journal} owns this and it is not growing")
        elif not opp:
            actions.append("")
            whys.append("neither large nor growing")
        elif declining:
            actions.append("")
            whys.append(
                f"{size} but losing share of world output at {grow} — large "
                f"today, not a place to launch"
            )
        elif role == "journal":
            actions.append("launch_journal")
            if own == "scattered" and not thin:
                whys.append(
                    f"consolidation launch: {int(r.n_journals_present)} titles print "
                    f"{int(r.unit_n_fi_3y):,} papers here and none holds "
                    f"{C.OWNED_MIN_FI_SHARE:.0%}; high Frontiers share proves demand "
                    f"but does not provide a home"
                )
            else:
                whys.append(
                    f"{'nobody owns' if own == 'scattered' else 'no Frontiers presence in'} "
                    f"a journal-sized community of {size}, {grow}, Frontiers at "
                    f"{float(r.fi_share_vs_portfolio):.2f}x portfolio share"
                )
        elif role == "section":
            actions.append("launch_section")
            whys.append(
                f"{'nobody owns' if own == 'scattered' else 'no Frontiers presence in'} "
                f"a section-sized community of {size}, {grow}, Frontiers at "
                f"{float(r.fi_share_vs_portfolio):.2f}x portfolio share"
            )
        elif not thin and own == "scattered":
            actions.append("consolidate")
            whys.append(
                f"{int(r.n_journals_present)} titles print "
                f"{int(r.unit_n_fi_3y):,} papers here but the scope is too broad "
                "for one journal — consolidate through multiple homes"
            )
        elif role == "too_broad":
            actions.append("")
            whys.append(
                f"{size} is past what one title serves — see the bundles inside it"
            )
        else:
            actions.append("")
            whys.append(f"{size} is below section scale")

    out["action"] = actions
    out["action_reason"] = whys
    log.info(
        "actions: %s",
        ", ".join(
            f"{k or 'none'} {v:,}" for k, v in out["action"].value_counts().items()
        ),
    )
    return out


def dedupe_contained_units(units: pd.DataFrame) -> pd.DataFrame:
    """One journal proposal per patch of the citation graph.

    The same space is offered at three grains — the whole meso community, a
    bundle of its children, and individual children — so without this the same
    launch is counted up to three times. The coarsest proposal wins, because a
    journal built from the broader community subsumes the narrower ones, and
    anything overlapping it is demoted to a view of that journal's topics.
    Section proposals are untouched: a section inside a proposed journal is a
    section *of* it, which `link_sections_to_journals` records.
    """
    out = units.copy()
    out["superseded_by"] = ""
    launching = out[out["action"] == "launch_journal"].copy()
    if launching.empty:
        return out

    launching["_n"] = launching["member_ids"].map(
        lambda s: len({x for x in str(s).split(",") if x})
    )
    kept: list[tuple[str, set[int]]] = []
    demoted: list[tuple[int, str]] = []
    for r in launching.sort_values(
        ["_n", "n_global_3y"], ascending=[False, False]
    ).itertuples():
        mine = {int(x) for x in str(r.member_ids).split(",") if x}
        winner = next((uid for uid, held in kept if held & mine), "")
        if winner:
            demoted.append((r.Index, winner))
        else:
            kept.append((r.unit_id, mine))

    for idx, winner in demoted:
        out.at[idx, "superseded_by"] = winner
        out.at[idx, "action"] = ""
        out.at[idx, "action_reason"] = (
            f"inside {winner}, which is proposed as the journal — kept as a "
            "view of that journal's topics"
        )
    log.info(
        "deduped %s journal proposals that sat inside a broader one",
        f"{len(demoted):,}",
    )
    return out


def resolve_relative_sections(units: pd.DataFrame, bands: dict) -> pd.DataFrame:
    """A section is where a community sits, not how big it is.

    Once the journal floor became a global publication rate, nearly every micro
    community cleared it and the absolute section band caught almost nothing —
    section launches collapsed to two, while a hundred-odd micro communities
    were demoted to "inside a broader journal proposal" with nothing else said
    about them. But a section was never really a size. It is a micro community
    that belongs *under* something, so candidacy is decided by whether its meso
    parent has a home, whatever the community's own size:

    - parent proposed as a journal in this run: a founding section of it, even
      if the child would clear the journal floor by itself.
    - parent already owned by a live title: a section of that title. This
      *demotes* proposals that would otherwise read as new journals —
      "Adaptive and robust control" is 51,765 papers, but it sits inside a
      community Frontiers in Robotics and AI owns, and the answer there is a
      section, not a competing title.

    Only `core` parents demote. A parent characterised by drift has no
    legitimate claim on its children, and formalising a section under it would
    entrench the drift; those stay journal proposals or `formalise_section`.
    Parents nobody owns leave the child as a journal proposal, since there is
    no existing home to put it in.
    """
    out = units.copy()
    sb = bands["section"]
    meso = out[out["unit_kind"] == "meso"]
    parent_action = meso.set_index("parent_id")["action"].to_dict()
    parent_own = meso.set_index("parent_id")["ownership"].to_dict()
    parent_owner = meso.set_index("parent_id")["owner_journal"].to_dict()
    parent_name = meso.set_index("parent_id")["name"].to_dict()

    def _owner(pid: int) -> str:
        v = parent_owner.get(pid)
        return "" if v is None or pd.isna(v) else str(v)

    n_proposed, n_existing, n_demoted = 0, 0, 0
    for r in out.itertuples():
        if r.unit_kind == "meso":
            continue
        act = "" if pd.isna(r.action) else str(r.action)
        if act and act != "launch_journal":
            continue
        pid = int(r.parent_id)
        owned = parent_own.get(pid) == "core" and bool(_owner(pid))
        if act == "launch_journal" and not owned:
            continue
        if not bool(r.is_opportunity) or r.coverage not in {"thin", "under_indexed"}:
            continue
        # The section floor still applies: below it there is not enough
        # literature in the world to fill a section, whoever would host it.
        if float(r.n_global_3y) < sb[0]:
            continue
        if (
            pd.notna(r.excess_cagr)
            and float(r.excess_cagr) <= C.MARKET_DECLINE_EXCESS_CAGR
        ):
            continue
        size = f"{int(r.n_global_3y):,} global papers"
        if owned:
            why = (
                f"{size} inside a community {_owner(pid)} owns — a section of "
                f"that title rather than a title of its own"
            )
            n_existing += 1
            if act == "launch_journal":
                n_demoted += 1
        elif parent_action.get(pid) == "launch_journal":
            why = (
                f"{size} inside {parent_name.get(pid) or 'the parent community'}, "
                f"which this run proposes as a journal — a founding section of it"
            )
            n_proposed += 1
        else:
            continue
        out.at[r.Index, "action"] = "launch_section"
        out.at[r.Index, "action_reason"] = why

    log.info(
        "relative sections: %s section candidates decided on where they sit "
        "rather than their size — %s under a journal proposed in this run, %s "
        "under a title Frontiers already owns (%s of those were journal "
        "proposals until now)",
        f"{n_proposed + n_existing:,}",
        f"{n_proposed:,}",
        f"{n_existing:,}",
        f"{n_demoted:,}",
    )
    return out


def link_sections_to_journals(units: pd.DataFrame) -> pd.DataFrame:
    """Point each section unit at the journal it would sit under.

    A section proposed inside a community we are also proposing as a journal
    belongs to that new title, not to an existing one. Otherwise the home is
    the title with the most Frontiers output in the parent community, which is
    a citation-graph answer rather than a title-token guess.
    """
    out = units.copy()
    out["home_unit_id"] = ""
    out["suggested_home"] = ""

    launching = out[out["action"] == "launch_journal"]
    journal_by_parent = {}
    for r in launching.itertuples():
        # A whole-meso proposal covers every child; a bundle covers its members.
        journal_by_parent.setdefault(int(r.parent_id), []).append(
            (r.unit_id, set(int(x) for x in str(r.member_ids).split(",") if x))
        )

    owner_by_parent = (
        out[out["unit_kind"] == "meso"]
        .set_index("parent_id")["owner_journal"]
        .to_dict()
    )
    name_by_unit = dict(zip(out["unit_id"], out["name"]))

    homes, home_units, kinds = [], [], []
    for r in out.itertuples():
        if r.action not in {"launch_section", "formalise_section"}:
            homes.append("")
            home_units.append("")
            kinds.append("")
            continue
        mine = {int(x) for x in str(r.member_ids).split(",") if x}
        hit = ""
        for uid, cover in journal_by_parent.get(int(r.parent_id), []):
            if mine & cover:
                hit = uid
                break
        if hit:
            home_units.append(hit)
            homes.append(str(name_by_unit.get(hit, "")))
            kinds.append("proposed_journal")
        elif r.action == "formalise_section":
            home_units.append("")
            homes.append(str(r.drift_lead_journal or r.owner_journal or ""))
            kinds.append("existing_journal")
        else:
            home_units.append("")
            homes.append(str(owner_by_parent.get(int(r.parent_id), "") or ""))
            kinds.append("existing_journal")
    out["home_unit_id"] = home_units
    out["suggested_home"] = homes
    # Without this the column mixes a proposed journal's community name with a
    # live Frontiers title and the two read identically.
    out["home_kind"] = kinds
    return out


# --- orchestration ----------------------------------------------------------

SHORTLIST_ACTIONS = (
    "launch_journal",
    "launch_section",
    "formalise_section",
    "reroute",
    "expand",
    "consolidate",
)


def build_launch_units(run_timestamp: str) -> tuple[pd.DataFrame, dict]:
    from opportunities import bq as bqmod

    parent_level = C.UNIT_JOURNAL_LEVEL
    child_level = C.UNIT_SECTION_LEVEL

    log.info("market at %s (journal level)", parent_level)
    market_parent, meta_parent = market_map.compute_market(run_timestamp, parent_level)
    log.info("market at %s (section level, unfiltered for bundling)", child_level)
    market_child, meta_child = market_map.compute_market(
        run_timestamp, child_level, min_3y=0
    )
    hierarchy = fetch_hierarchy(run_timestamp, parent_level, child_level)
    placement = fetch_frontiers_placement(run_timestamp)
    window_years = [
        int(y) for y in str(meta_child.get("window_years") or "").split(",") if y
    ]

    bands = calibrate_bands(
        placement,
        bqmod.fetch_existing_sections(),
        window_years,
        float(meta_child.get("fi_portfolio_share") or 0.0),
    )
    units, members = build_units(
        market_parent, market_child, hierarchy, bands, meta_child
    )
    own = build_ownership(members, placement, window_years)
    units = classify_units(units, own)
    units = route_units(units)
    units = dedupe_contained_units(units)
    units = resolve_relative_sections(units, bands)
    units = link_sections_to_journals(units)

    units = units.sort_values(
        ["action", "n_global_3y"], ascending=[True, False]
    ).reset_index(drop=True)

    meta = {
        "run": run_timestamp,
        "journal_level": parent_level,
        "section_level": child_level,
        "window_years": meta_child.get("window_years"),
        "growth_max_month": meta_child.get("growth_max_month"),
        "growth_ytd_share": meta_child.get("growth_ytd_share"),
        "corpus_cagr": meta_child.get("corpus_cagr"),
        "fi_portfolio_share": meta_child.get("fi_portfolio_share"),
        "band_source": bands["source"],
        "journal_band": f"{int(bands['journal'][0]):,}-{int(bands['journal'][1]):,}",
        "section_band": f"{int(bands['section'][0]):,}-{int(bands['section'][1]):,}",
        "n_journals_calibrated": bands["n_journals_calibrated"],
        "n_sections_calibrated": bands["n_sections_calibrated"],
        "n_units": int(len(units)),
        "n_ownership_pairs": int(len(own)),
    }
    for kind, n in units["unit_kind"].value_counts().items():
        meta[f"n_{kind}"] = int(n)
    for act, n in units["action"].value_counts().items():
        meta[f"n_action_{act or 'none'}"] = int(n)
    for cls, n in units["ownership"].value_counts().items():
        meta[f"n_ownership_{cls}"] = int(n)
    return units, meta


def run_launch_units(run_timestamp: str, write: bool = True) -> pd.DataFrame:
    from opportunities import bq as bqmod

    units, meta = build_launch_units(run_timestamp)
    if write:
        bqmod.write_table(units, "launch_units", run_timestamp)
        bqmod.write_json_row(meta, "launch_units_meta", run_timestamp)
        shortlist = units[units["action"].isin(SHORTLIST_ACTIONS)]
        bqmod.write_table(shortlist, "launch_shortlist", run_timestamp)
    return units


def main() -> None:
    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s  %(message)s", datefmt="%H:%M:%S"
    )
    ap = argparse.ArgumentParser(description="Journal and section launch units")
    ap.add_argument("--run", default=C.DEFAULT_RUN)
    ap.add_argument("--no-write", action="store_true")
    args = ap.parse_args()
    units = run_launch_units(args.run, write=not args.no_write)

    cols = [
        "unit_kind",
        "name",
        "n_global_3y",
        "excess_cagr",
        "fi_share_vs_portfolio",
        "ownership",
        "coverage",
        "unit_n_fi_3y",
        "home_kind",
        "suggested_home",
    ]
    for action in ("launch_journal", "launch_section", "reroute"):
        sub = units[units["action"] == action]
        print(f"\n=== {action} ({len(sub):,}) ===")
        if sub.empty:
            print("none at current gates")
            continue
        print(
            sub.sort_values("n_global_3y", ascending=False)
            .head(15)[cols]
            .to_string(index=False)
        )


if __name__ == "__main__":
    main()
