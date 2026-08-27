---
name: jd-validation
description: >
  Business case validation for new journal proposals at Frontiers Media SA. Use when someone needs a financial projection, break-even analysis, revenue estimate, cost model, or go/no-go recommendation for a proposed journal. This skill builds a 3-year P&L forecast using historical Frontiers data and market assumptions.
---

# Journal Validation — Business Case

## Overview

This skill builds a data-driven business case for a proposed journal. It answers: *Will this journal reach profitability, and when?*

## When to Use

- Building a financial case for a new journal
- Estimating 3-year revenue, costs, and break-even
- Comparing a proposal against benchmarks of similar Frontiers journals
- Producing a go/no-go recommendation with financial backing

## Prerequisites

- `core-analytics` — historical journal economics, ramp-up curves
- `core-salesforce` — APC pricing, discount patterns, waiver rates
- `jd-research` — landscape brief as input (optional but recommended)

## Workflow

1. **Gather assumptions** — Target APC, estimated submissions/year (Y1–Y3), acceptance rate, waiver %
2. **Model revenue** — Articles published × net APC (after waivers/discounts)
3. **Model costs** — Editorial operations, marketing, technology, per-article processing
4. **Project P&L** — Year 1 through Year 3, monthly granularity in Y1
5. **Benchmark** — Compare projections to actual performance of analogous Frontiers journals at same maturity
6. **Score and recommend** — Financial viability score (0–100), break-even quarter, risk flags

## Data Sources

| Source | What we get |
|--------|-------------|
| BigQuery | Historical ramp-up curves, cost benchmarks, acceptance rates by field |
| Salesforce | APC pricing tiers, discount code usage, waiver approval rates |
| Landscape brief | Market size, competitor pricing, author pool |

## Output Format

A business case document containing:
- Executive summary with recommendation
- 3-year P&L projection (revenue, costs, net)
- Break-even analysis (quarter and scenario: optimistic / base / pessimistic)
- Benchmark comparison vs. analogous journals
- Risk register (top 5 risks with mitigations)
- Financial viability score: **Strong** (70+) / **Conditional** (40–69) / **Weak** (<40)
