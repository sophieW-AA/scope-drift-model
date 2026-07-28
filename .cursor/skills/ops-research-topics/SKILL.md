---
name: ops-research-topics
description: >
  Research Topics lifecycle management for Frontiers Media SA. Use when planning, proposing,
  evaluating, tracking, or closing Research Topics. Covers topic ideation, submission yield
  estimation, editor recruitment for topics, performance monitoring, and strategic alignment
  with journal growth goals. Research Topics are themed, collaborative article collections
  organized by leading researchers around emerging areas of research.
---

# Research Topics — Lifecycle Management

## Overview

Research Topics are one of Frontiers' most important products and a major driver of submissions.
This skill manages the full lifecycle: from ideation through performance tracking to closure.

## When to Use

- Planning new Research Topics for a journal
- Estimating expected submission yield for a proposed topic
- Evaluating a Research Topic proposal from an editor
- Tracking active Research Topic performance (submissions, acceptance, citations)
- Deciding when to close a Research Topic
- Analyzing which past RTs drove the most submissions and impact
- Aligning RT strategy with journal growth goals

## Prerequisites

- `core-analytics` — submission data, RT performance history, article metrics
- `core-salesforce` — RT records, editor contacts, campaign data
- `core-frontiers` — understanding of what Research Topics are

## What Are Research Topics?

Research Topics are collaborative article collections where:
- Leading researchers **propose** a theme around an emerging or important area
- They serve as **Topic Editors**, inviting contributors and curating submissions
- Articles can span **multiple journals** (cross-listed sections)
- Completed topics become **ebooks** (free, downloadable collections)
- They drive **targeted submissions** from specific research communities

## Workflow

### 1. Topic Ideation
- Analyze trending subfields using publication growth data
- Identify gaps in the journal's RT coverage
- Cross-reference with competitor special issues
- Propose 3–5 candidate topics with rationale

### 2. Proposal Evaluation
When an editor proposes a RT, assess:
- **Relevance** — Does it align with journal scope and growth priorities?
- **Timeliness** — Is the field growing? Any recent breakthroughs?
- **Editor credibility** — Do the proposed Topic Editors have standing in the field?
- **Yield estimate** — How many submissions can we realistically expect?
- **Overlap** — Does it duplicate an active or recent RT?

### 3. Yield Estimation
Based on historical data, estimate submissions by considering:
- Topic Editors' network size and publication volume
- Field publication rate (from BigQuery / OpenAlex)
- Historical RT yield for similar topics in this journal
- Season (submission patterns vary by quarter)

### 4. Performance Monitoring
Track active RTs on:
- Submissions received vs. target
- Acceptance rate
- Time-to-decision
- Geographic and institutional diversity of contributors
- Comparison to journal's organic submission performance

### 5. Closure Decision
A RT should be closed when:
- Submission deadline has passed and extensions are exhausted
- Yield is well below target with no pipeline
- Topic Editors are unresponsive
- The field has moved on

## Output Format

- RT proposal scorecard (0–100 viability score)
- Yield forecast (optimistic / base / conservative)
- Active RT dashboard (submissions, conversions, timeline)
- RT retrospective report (what worked, what didn't, lessons)
- Strategic RT plan (next quarter's recommended topics)

## Data Sources

| Source | What we get |
|--------|-------------|
| BigQuery | RT submission history, article performance, yield benchmarks |
| Salesforce | RT records, Topic Editor contacts, campaign associations |
| OpenAlex | Field growth trends, potential Topic Editor identification |
