---
name: jd-monitoring
description: >
  Operational health monitoring for Frontiers journals. Use when checking a journal's editorial performance — turnaround times, reviewer availability, acceptance/rejection trends, bottlenecks, or anomalies. Provides a real-time health dashboard for Journal Development Managers and editorial leadership.
---

# Journal Monitoring — Operational Health

## Overview

This skill provides an operational health dashboard for any Frontiers journal, highlighting bottlenecks, trends, and anomalies that need attention.

## When to Use

- Routine journal health check (monthly/quarterly)
- Investigating slow turnaround times
- Checking reviewer availability and load
- Spotting trends in rejection/acceptance rates
- Identifying editorial bottlenecks
- Comparing a journal's KPIs to portfolio benchmarks

## Prerequisites

- `core-analytics` — editorial pipeline metrics, turnaround times, reviewer data
- `core-salesforce` — editor workload, article status tracking

## Workflow

1. **Select journal** — Identify journal and time period
2. **Pull KPIs** — Submission volume, desk reject %, time-to-first-decision, time-to-publication, reviewer invite-to-accept ratio
3. **Benchmark** — Compare to portfolio median and same-journal historical trend
4. **Detect anomalies** — Flag metrics >1.5σ from historical mean
5. **Bottleneck analysis** — Identify where articles are stuck (editor assignment, reviewer search, revision cycles)
6. **Generate report** — Health scorecard with traffic-light indicators

## Output Format

- Health scorecard (green/yellow/red per metric)
- Trend charts (6-month rolling)
- Anomaly alerts with context
- Bottleneck diagnosis
- Recommended actions (prioritized)

## Key Metrics

| Metric | Green | Yellow | Red |
|--------|-------|--------|-----|
| Time to first decision | < 30 days | 30–60 days | > 60 days |
| Reviewer accept rate | > 50% | 30–50% | < 30% |
| Desk reject rate | 10–30% | 30–50% | > 50% |
| Revision turnaround | < 14 days | 14–30 days | > 30 days |
