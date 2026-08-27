---
name: ops-integrity
description: >
  Research integrity workflows for Frontiers Media SA. Use when investigating potential integrity
  issues — paper mills, image manipulation, citation rings, authorship disputes, plagiarism,
  duplicate submissions, or ethical violations. Covers COPE-aligned investigation procedures,
  pattern detection, retraction/correction workflows, and reporting. High-stakes skill for
  Research Integrity Managers and editorial leadership.
---

# Research Integrity — Investigation & Protection

## Overview

This skill supports Research Integrity Managers in detecting, investigating, and resolving
integrity issues. It follows COPE (Committee on Publication Ethics) guidelines and Frontiers'
three-layered quality approach.

## When to Use

- Investigating suspected paper mill activity
- Analyzing image manipulation flags from AIRA
- Detecting citation manipulation or ring patterns
- Handling plagiarism cases
- Managing authorship disputes
- Processing retraction or correction requests
- Generating investigation reports for COPE compliance
- Identifying patterns across multiple submissions

## Prerequisites

- `core-analytics` — submission history, author patterns, citation data
- `core-salesforce` — article records, author contacts, case tracking
- `core-frontiers` — peer review model and integrity policies

## Frontiers' Three-Layered Quality Approach

1. **In-house expertise** — Research Integrity Managers with scientific backgrounds
2. **Independent editorial boards** — Associate Editors make acceptance decisions
3. **AI (AIRA)** — 40+ automated checks before peer review

Research Integrity Managers can **reject manuscripts at any stage** and **override acceptance decisions**.

## Investigation Workflows

### Paper Mill Detection
Signs to look for:
- Unusual submission patterns (same institution, same timeframe, similar topics)
- Templated manuscript structures with swapped variables
- Authors with no discoverable academic presence
- Suggested reviewers with fake or suspicious profiles
- Manuscripts that don't match the authors' stated expertise

Investigation steps:
1. Flag the cluster of suspicious manuscripts
2. Cross-reference author profiles against institutional databases
3. Check suggested reviewer email domains and publication records
4. Analyze manuscript similarity (structure, references, figures)
5. Contact institutions if warranted
6. Document findings in COPE-compliant investigation report
7. Reject and notify (or escalate to COPE if post-publication)

### Image Manipulation
When AIRA or manual review flags potential image issues:
1. Classify the concern: duplication, splicing, inappropriate adjustment, fabrication
2. Compare flagged images against known databases
3. Contact authors for original raw data/images
4. Assess whether the issue is honest error or intentional manipulation
5. Decision: accept explanation / request correction / reject / retract

### Citation Manipulation
Indicators:
- Excessive self-citation (> 25% of references to own work without justification)
- Citation rings (group of authors systematically citing each other)
- Editor-coerced citations
- Irrelevant citations to boost specific journals

### Retraction / Correction Workflow
Following COPE Retraction Guidelines:
1. Identify the issue and severity
2. Contact authors for response (21-day deadline)
3. Consult with handling editor
4. Decision: correction (erratum/corrigendum) or retraction
5. Draft retraction/correction notice
6. Publish notice linked to original article
7. Notify indexing services (CrossRef, PubMed, etc.)

## Output Format

- Investigation report (COPE-compliant format)
- Pattern analysis dashboard (author clusters, institutional patterns)
- Decision recommendation with evidence summary
- Retraction/correction notice draft
- Risk flag for editorial board awareness

## COPE Resources

- Retraction guidelines: https://publicationethics.org/retraction-guidelines
- Flowcharts: https://publicationethics.org/guidance/Flowcharts
- Case taxonomy: https://publicationethics.org/guidance/Case
