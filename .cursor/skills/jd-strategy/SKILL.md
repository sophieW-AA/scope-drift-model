---
name: jd-strategy
description: >-
  Frontiers journal portfolio strategy and analysis. Use when asked about Frontiers journals,
  the Frontiers portfolio, market positioning, journal segments, journal indexing,
  Impact Factors, CiteScores, market share, output volumes,
  portfolio health categories, opportunity scoring, citation impact, funding signals,
  competitor mapping, gap analysis, expansion opportunities,
  sunset candidates, or any strategic portfolio question. Covers all 220 active Frontiers
  journals including 19 partner journals.
metadata:
  author: davor.vidic@frontiersin.org
  version: '3.0'
  data_date: '2026-04-29'
  evolved_from: jd-strategy v2.0
---

# Journal Strategy — Portfolio Advisor v3.0

Comprehensive reference and strategic analysis tool for the Frontiers open-access journal portfolio. Uses the OpenAlex taxonomy as the primary market structure (replacing the JCR-derived sub-domain framework from v2.0).

**Data vintage:** 2025 output (OpenAlex/Dimensions), JIF JCR 2024, CiteScore Scopus 2024, April 2026 snapshot.

## Taxonomy

OpenAlex four-level hierarchy — this replaces the old 10-domain / 54-sub-domain JCR structure:

```
Entire Market (5.05M articles, 2025)
  └── Domain (4)           — Physical Sciences, Health Sciences, Social Sciences, Life Sciences
      └── Field (26)       — e.g. Medicine, Chemistry, Computer Science
          └── Subfield (252) — core market-sizing unit; e.g. Organic Chemistry, Epidemiology
              └── Topic (~4,500) — granular research clusters (not used for portfolio sizing)
```

**Key concept shift from v2.0:** The market-sizing unit is now the **OpenAlex Subfield** (not the JCR sub-domain). Market sizes and CAGR are OpenAlex-derived. WoS category counts differ significantly — see `references/market-taxonomy.md` for why a given field may look smaller than expected (chemistry-related content is spread across Materials Chemistry, Environmental Chemistry, Biochemistry etc., not just the "Chemistry" Field).

## Reference Files — Load as Needed

|| File | Use when … |
||---|---|
|| `references/portfolio-journals.md` | Asking about a specific journal: Domain/Field/Subfield, IF, CS, Segment, indexing, or anchor competitors |
|| `references/market-taxonomy.md` | Asking about market sizes, CAGR, Frontiers share, or the full Domain → Field → Subfield hierarchy |
|| `references/portfolio-review.md` | Asking about portfolio health: flags, categories (Decom Review → On Track), reasons |
|| `references/opportunities.md` | Asking about new journal opportunities, gap analysis, subfields to expand into |

## Portfolio Snapshot

- **220 active journals** (open for submissions), incl. 19 partner journals (marked †)
- **4 Domains | 26 Fields | 252 Subfields**
- **84,459 total Frontiers articles** indexed in OpenAlex (2025)
- **1.67% overall market share**
- **Frontiers 3yr CAGR: −12.5%** vs market CAGR +7.3% — portfolio-wide decline vs growing market

### Segment Distribution (2026 classification)

|| Segment | Count | Description |
||---|---|---|
|| Leader | 9 | Flagship journals |
|| FAAS | 1 | High-priority strategic |
|| Established | 17 | Proven track record |
|| Emerging | 98 | Growing, building share |
|| Incubator | 79 | Early-stage / recently launched |
|| Other | 3 | Uncategorised / partner |

**Note:** Partner journals (19) and some new titles may not have segment data — shown as `—`.

### Indexing

WoS and Scopus flags are sourced from the reporting_data_mart / historical portfolio data. Unindexed journals are primarily Incubator-segment. Partner journals carry their own indexing status.

## Portfolio Health Categories

Defined in `references/portfolio-review.md`. Five flags per journal:

|| Flag | Definition |
||---|---|
|| Declining | YoY article count < 0 |
|| Below Mkt Growth | Growing but slower than field 3yr CAGR |
|| Cite Gap | Avg citations at 24m < 2.0 |
|| Low Presence | Journal holds < 1% of Frontiers output in its primary subfield |
|| Dominated | Top 3 journals hold > 25% of the field |

Categories (severity descending):
1. 🚪 **Decom Review** — severe decline + cite gap + (low presence or dominated)
2. 🔄 **Rescope** — declining + low presence in a growing field (wrong market)
3. 📋 **Quality** — declining + cite gap
4. ⏸️ **Maintenance** — cite gap only, not declining
5. 👁️ **Watch** — any single other flag
6. ✅ **On Track** — no flags

Current breakdown: On Track 73 | Watch 62 | Maintenance 34 | Quality 30 | Rescope 15 | Decom Review 6.

## Opportunity Scoring

Gate-passing subfields (≥10,000 articles AND CAGR ≥5%) are scored 0–12 in `references/opportunities.md`:

|| Tier | Score | Action |
||---|---|---|
|| 🟢 Priority | ≥8 | Recommended for immediate action |
|| 🟡 Potential Launch | 5–7 | Good signal, investigate further |
|| 🔵 On Radar | <5 | Monitor |

Currently: 7 Priority | 57 Potential Launch | 34 On Radar | 154 fail gates.

Patterns used:
- 🔀 **Scope Leakage** — FI articles present via wrong/adjacent journal
- 📊 **Standard Opportunity** — no mapped FJ, low FI presence
- 📈 **Grow Existing** — FJ exists but growing below market rate
- 🏔️ **Massive Market** — very large subfield with minimal Frontiers presence

## Instructions

1. **Journal-specific questions** → load `portfolio-journals.md`. Search by name. Return Domain, Field, Subfield, articles, IF, CS, Segment, WoS, Scopus, 3 competitors.
2. **Market sizing** → load `market-taxonomy.md`. Use Subfield as the primary sizing unit. If a user quotes a WoS market figure, note that OpenAlex figures will differ (see taxonomy note above).
3. **Portfolio health** → load `portfolio-review.md`. Filter by Category or flag. Report reason text verbatim.
4. **Gap analysis / new journal opportunities** → load `opportunities.md`. Filter by Tier. Highlight Pattern and Funding signal.
5. **Domain or Field summaries** → load `market-taxonomy.md` and `portfolio-journals.md`. Aggregate constituent journals; compute total Frontiers output and share for the entity.
6. **Competitor context** → use Competitor 1/2/3 columns in `portfolio-journals.md` (anchor competitor set from market_intelligence basket). For broader competitive analysis, pair with core-analytics or biz-competitive-intel skill.
7. **Data vintage** — Always cite: *2025 output (OpenAlex/Dimensions), JIF JCR 2024, CiteScore Scopus 2024, April 2026 snapshot.* OpenAlex market sizes are English-language journal articles only; WoS figures will be larger.
8. **When presenting data** — use tables for multi-journal comparisons. Spell out category emoji labels in full on first use.