---
name: jd-board
description: >
  Editorial board assembly and management for Frontiers journals. Use when a journal needs to recruit editors, build or expand its editorial board, generate invitation emails, assess board diversity and coverage, or identify potential conflicts of interest. Works for both new journal launches and existing journal board refreshes.
---

# Editorial Board Assembly

## Overview

This skill helps build, expand, and optimize editorial boards. It sources candidates, generates personalized invitations, and monitors board health metrics.

## When to Use

- Launching a new journal and need to assemble an editorial board
- An existing journal needs to fill gaps (geography, subfield, seniority)
- Need to generate invitation emails for editor candidates
- Need to assess board diversity metrics
- Checking for conflicts of interest among board candidates

## Prerequisites

- `core-analytics` — author/reviewer publication history, editorial experience
- `core-openalex` — external profiles, h-index, institutional affiliations
- `core-salesforce` — contact records, past board invitations, response history
- `core-email` — generate and send invitation drafts

## Workflow

1. **Define needs** — Journal scope, target board size, subfield coverage gaps, diversity goals
2. **Source candidates** — Query top authors/reviewers in the field from BigQuery + OpenAlex
3. **Score and rank** — Publication volume, citation impact, editorial experience, geographic diversity
4. **Conflict check** — Flag candidates with competing journal roles, institutional conflicts
5. **Generate invitations** — Personalized emails referencing the candidate's work
6. **Track responses** — Monitor acceptance/decline rates, follow-up reminders
7. **Board health report** — Coverage map, diversity metrics, gaps remaining

## Data Sources

| Source | What we get |
|--------|-------------|
| BigQuery | Frontiers author/reviewer history, past editorial roles |
| OpenAlex | Publications, citations, h-index, co-author networks |
| Salesforce | Contact info, invitation history, board membership records |

## Output Format

- Candidate shortlist (ranked, with key metrics)
- Personalized invitation emails (ready to send)
- Board composition dashboard (geography, gender, seniority, subfield)
- Conflict of interest report
- Gap analysis (what's still missing)
