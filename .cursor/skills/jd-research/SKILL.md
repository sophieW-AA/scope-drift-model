---
name: jd-research
description: >
  Landscape analysis for new journal opportunities at Frontiers Media SA. Use when a Journal Development Manager, strategist, or editor asks about whitespace in a research field, competitor journals, potential editors, estimated submission pools, or whether a new journal idea has merit. This skill identifies gaps in the publishing landscape and sizes the opportunity before a formal business case.
---

# Journal Research — Landscape Analysis

## Overview

This skill performs systematic landscape analysis to evaluate new journal opportunities. It answers: *Is there a gap in the market, and is it big enough to fill?*

## When to Use

- User asks about whitespace or gaps in a research field
- Someone proposes a new journal and wants initial research
- Need to identify competitor journals in a specific domain
- Need to estimate the potential author/submission pool
- Evaluating whether a field is growing or declining

## Prerequisites

- `core-analytics` — for internal Frontiers data (existing journals, submission history)
- `core-openalex` — for external bibliometric data (publications, authors, trends)
- `core-salesforce` — for existing journal pipeline and contacts

## Workflow

1. **Define the field** — Clarify the research domain, keywords, and scope
2. **Map competitors** — Identify journals in the same or adjacent space (publisher, IF, APC, volume)
3. **Size the market** — Count publications/year in the field, growth rate, geographic distribution
4. **Identify key authors** — Top-publishing and top-cited researchers who could serve as editors or authors
5. **Assess Frontiers position** — Check if Frontiers already covers adjacent areas, look for overlap and cannibalization risk
6. **Synthesize** — Produce a one-page landscape brief with go/explore/pass recommendation

## Data Sources

| Source | What we get |
|--------|-------------|
| OpenAlex | Publication volumes, citation trends, top authors, institutional affiliations |
| BigQuery | Frontiers submission history by field, author overlap, journal performance |
| Scopus/WoS (manual) | Impact factors, journal rankings |
| Salesforce | Existing pipeline, contact relationships |

## Output Format

A structured landscape brief containing:
- Field definition and scope
- Market size (publications/year, growth %)
- Competitor matrix (top 5–10 journals with key metrics)
- Author pool heatmap (geography, institution)
- Frontiers overlap/cannibalization analysis
- Recommendation: **Go** / **Explore further** / **Pass**

## Examples

> "Is there room for a Frontiers journal in computational social science?"
> "What does the landscape look like for sustainable packaging research?"
> "Who are the top researchers in quantum machine learning?"
