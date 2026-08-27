---
name: finance-apc
description: >
  APC (Article Processing Charge) pricing strategy and analysis for Frontiers Media SA. Use when
  modeling pricing changes, analyzing waiver and discount impact, benchmarking APCs against
  competitors, forecasting revenue under different pricing scenarios, evaluating fee policy
  compliance, or supporting pricing decisions for new or existing journals. Complements
  jd-sustainability with a specific focus on the pricing lever.
---

# APC Pricing — Strategy & Analysis

## Overview

This skill focuses on APC pricing as a strategic lever for revenue optimization, competitiveness,
and author accessibility. It supports pricing decisions for both new and existing journals.

## When to Use

- Setting APC pricing for a new journal
- Evaluating a price increase or decrease for an existing journal
- Analyzing the impact of waivers and discounts on net revenue
- Benchmarking Frontiers APCs against competitor journals
- Modeling revenue under different pricing scenarios
- Evaluating flat-fee vs. per-article pricing for institutional deals
- Assessing fee policy compliance and waiver utilization

## Prerequisites

- `core-salesforce` — APC pricing tiers, discount codes, waiver records, invoicing
- `core-analytics` — publication volumes, revenue data, author demographics
- `core-frontiers` — fee policy and gold OA model

## Frontiers Fee Policy Context

Frontiers operates a **gold open access** model:
- Authors (or their institutions/funders) pay an APC upon acceptance
- All articles are immediately free to read under CC-BY 4.0
- APCs vary by journal, reflecting editorial costs and field norms
- Waivers and discounts are available (institutional agreements, low-income countries, etc.)
- Fee policy: https://www.frontiersin.org/about/fee-policy

## Key Analyses

### Pricing Benchmarking
For a given journal or field:
1. Identify 5–10 comparable journals (same field, similar IF/CiteScore)
2. Collect their APCs (from publisher websites)
3. Normalize by quality signal (APC per IF point, APC per CiteScore)
4. Position Frontiers journal on the price-quality map
5. Identify if priced above, below, or at market

### Revenue Waterfall
Decompose gross-to-net revenue:
```
Gross APC revenue (list price × articles)
  − Institutional discounts
  − Promotional discounts
  − Fee waivers (low-income, editorial, etc.)
  = Net APC revenue
```

### Price Change Modeling
For a proposed price change:
1. **Elasticity estimate** — How will submission volume respond? (use historical data from past changes)
2. **Revenue projection** — Net revenue under new price × projected volume
3. **Competitive impact** — Does the new price change our positioning?
4. **Author impact** — Which author segments are most price-sensitive?
5. **Scenario table** — Best case / base case / worst case

### Waiver Analysis
- Waiver utilization rate by journal
- Waiver cost (foregone revenue)
- Waiver by category (institutional, country-based, editorial, hardship)
- Trend over time — is waiver usage growing?
- Comparison to budget/policy limits

### New Journal Pricing
Setting the right APC for a new journal:
1. Benchmark against field competitors
2. Consider launch discount strategy (reduced APC for first 1–2 years)
3. Model break-even under different price points
4. Factor in institutional agreement coverage
5. Align with Frontiers pricing tiers

## Output Format

- APC benchmarking matrix (Frontiers vs. competitors)
- Revenue waterfall chart
- Price change scenario analysis (table + visualization)
- Waiver utilization report
- Pricing recommendation memo (with rationale)

## Data Sources

| Source | What we get |
|--------|-------------|
| Salesforce | APC list prices, discount codes, waiver records, invoiced amounts |
| BigQuery | Publication volumes, author country, institutional affiliation |
| Competitor websites | Published APC schedules |
| DOAJ | APC data for OA journals (bulk data available) |
