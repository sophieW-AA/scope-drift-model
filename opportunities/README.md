# Opportunity mapper

Demand-first shortlist on top of a scope-drift run. Turns citation communities into a **six-way call**: expand/rename, gated section, new journal, redirect/cross-list, gate intake, or emerging watch.

Not a trained model. Rule tree on the current Leiden partition. **All mapper output is BigQuery only** — nothing is written under `opportunities/output/`.

## What happens

1. **P0 inventory** — papers from `output/network_maps.html`. 2020 **baseline primary** (80% coverage). Two row types: **mix-shift** (share moving inside that 2020 core) and **non-primary**.
2. **P1 home** — title-token Jaccard vs each journal’s 2020 core (full titles from BigQuery when available). Macro cluster ID is logged, never a forced redirect. Methods-shared communities (CV, DL, control) get a **gate string**.
3. **P2 volume** — share of *that* title, split **Research Topic vs spontaneous**. Off-brand RTs flagged per topic. No RT-share penalty. Relative gates (~8% section, ~12% journal).
4. **P3 market** — two-field match to JD-strategy OpenAlex subfields. Journal path blocked if the parent can own a gated slice.
5. **P4 engine** — score 0–12, then the tree. Uniqueness so two journals do not both launch the same community. Launch calls need **two consecutive quarters** (first time → watch).
6. **P5 persist** — `decision_log_{run}` plus paper-Jaccard community matches across runs (Leiden IDs are not stable).

## Run

From the repo root (conda env `scope_drift`). **Default is the full Frontiers set in the current scope-drift run**, not one journal.

```powershell
python -m opportunities.run
python -m opportunities.run --skip-bq
python -m opportunities.run --journal "Frontiers in Neurorobotics"
```

`--skip-bq` uses dashboard journals only for **input** (whatever was in `output/network_maps.html`). Mapper tables still go to BigQuery. Without that flag, P0 loads every Frontiers paper in `classification_raw_<run>` / `pub_metadata_raw_<run>`. That is still “journals in this citation-network run,” not a guarantee of all ~222 active titles.

Each row is tagged **`already_publish`** (Frontiers already has volume — expand, gate, redirect, or leakage) or **`whitespace`** (OpenAlex market with FI share under 1%, **no Frontiers journal** as the JD anchor, and no section-scale community in this run). The demand-first mapper mostly surfaces already-publish; unmatched JD subfields fill the whitespace gaps.

## Outputs

Dataset: `ocean-tech-adv-analytics-c-tfs.opportunity_mapping` (EU). Tables are replaced per run:

| Table | Phase |
|---|---|
| `papers_{run}` | P0 |
| `candidates_{run}` | P0 |
| `journal_meta_{run}` | P0 |
| `p0_meta_{run}` | P0 |
| `home_{run}` | P1 |
| `volume_{run}` | P2 |
| `jd_opportunities_lookup_{run}` | P3 |
| `market_{run}` | P3 |
| `decisions_{run}` | P4 |
| `pack_{run}` | P4 summary counts |
| `launches_{run}` | Portfolio shortlist (presence + kind) |
| `whitespace_jd_{run}` | JD subfields with thin FI share and no matching community |
| `portfolio_{run}` | One-row pack + `portfolio_markdown` |
| `decision_log_{run}` | P5 |
| `community_matches_{run}` | P5 (if a prior run exists) |

`call` is the tree result; `call_effective` is after the two-quarter rule.

Read the shortlist:

```sql
SELECT *
FROM `ocean-tech-adv-analytics-c-tfs.opportunity_mapping.launches_20260818_090851`
ORDER BY score DESC
```

The write-up that used to be `PORTFOLIO.md` is `portfolio_{run}.portfolio_markdown`.

## v2 rules this encodes

- Mix-shift inside the **2020** primary is first-class (not OOS-only).
- No RT ≥50% penalty.
- Home = title/topic overlap, not macro ID membership.
- Expand vs tighten is a real call.
- Share-of-title gates, not flat 80/200 papers.
- Two-quarter persist + uniqueness pass.
- **Already publish vs whitespace** — mix-shift/expand/redirect is existing demand; JD subfields with FI share <1% and no section-scale community are gaps.
