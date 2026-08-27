---
name: jd-indexing
description: >
  Indexing readiness assessment for Frontiers journals targeting Web of Science, Scopus, PubMed, or DOAJ. Use when evaluating whether a journal meets indexing criteria, identifying gaps, or building an action plan to achieve indexation. Covers publication cadence, editorial standards, citation metrics, and compliance requirements.
---

# Journal Indexing — Readiness Assessment

## Overview

This skill evaluates a journal's readiness for indexing by major databases and produces an actionable gap report.

## When to Use

- Preparing a journal for WoS/Scopus/PubMed/DOAJ application
- Assessing which indexing criteria are met vs. missing
- Building a timeline and action plan to achieve indexation
- Tracking progress on indexing milestones

## Prerequisites

- `core-analytics` — publication cadence, citation data, article volumes
- `core-salesforce` — editorial board data, journal metadata
- `core-openalex` — external citation metrics, field benchmarks

## Workflow

1. **Select target index** — WoS, Scopus, PubMed, DOAJ (each has different criteria)
2. **Criteria checklist** — Map the index's requirements to measurable indicators
3. **Data collection** — Pull current journal metrics for each criterion
4. **Gap analysis** — Identify criteria not yet met, with severity rating
5. **Action plan** — For each gap, recommend specific actions, owners, and timelines
6. **Timeline projection** — Estimate earliest realistic application date

## Indexing Criteria (Summary)

| Criterion | WoS | Scopus | PubMed | DOAJ |
|-----------|-----|--------|--------|------|
| Publication history | 2+ years | 2+ years | 1+ year | Any |
| Article volume | 25+/year | Regular | Regular | 5+/year |
| Editorial board | International | International | Expert | Documented |
| Peer review | Documented | Documented | Documented | Documented |
| Citation performance | Field-relevant | CiteScore | N/A | N/A |
| Ethical standards | COPE/ICMJE | COPE | ICMJE | Best practices |
| Open access compliance | N/A | N/A | N/A | Required |

## Output Format

- Readiness scorecard (% criteria met per index)
- Detailed gap report with severity levels
- Action plan with owners and deadlines
- Timeline to application readiness
- Risk factors (what could delay indexation)
