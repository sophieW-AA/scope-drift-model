---
name: ops-editorial
description: >
  Day-to-day editorial operations support for Frontiers Media SA. Use when a Journal Manager,
  Peer Review Manager, or editorial team member needs help with editor assignment bottlenecks,
  reviewer load balancing, escalation patterns, desk reject workflows, editorial board performance,
  or any operational editorial question. This is the "how do I handle this situation" skill for
  editorial staff.
---

# Editorial Operations — Daily Support

## Overview

This skill supports the day-to-day work of Frontiers' editorial operations teams: Journal Managers,
Peer Review Managers, and Research Integrity Managers. It covers common workflows, decision patterns,
and operational best practices.

## When to Use

- Diagnosing why manuscripts are stuck in the pipeline
- Balancing reviewer load across the editorial board
- Handling editor assignment bottlenecks
- Managing desk reject decisions and criteria
- Evaluating editorial board member performance
- Escalation workflows (when to involve Chief Editors)
- Onboarding guidance for new Journal/Peer Review Managers

## Prerequisites

- `core-analytics` — editorial pipeline data, turnaround times, reviewer metrics
- `core-salesforce` — editor records, board membership, article status
- `core-frontiers` — editorial roles and peer review model

## Common Workflows

### Editor Assignment Bottleneck
When manuscripts are waiting too long for an Associate Editor:
1. Check AE workload — how many active manuscripts per AE?
2. Identify AEs with capacity (< 3 active manuscripts)
3. Match manuscript scope to AE expertise
4. If no suitable AE available, flag to Specialty Chief Editor
5. Consider inviting external AEs if pattern persists

### Reviewer Sourcing Difficulties
When reviewers are hard to find:
1. Check invite-to-accept ratio for this journal/section
2. Analyze reviewer response times — are invites being ignored or declined?
3. Review decline reasons (if captured)
4. Expand search: check co-author networks of submitted manuscript
5. Consider cross-section reviewers with relevant expertise
6. Flag to AE if > 10 invitations sent without acceptance

### Desk Reject Criteria
Manuscripts should be desk-rejected when:
- Out of scope for the journal/section
- Fails basic quality thresholds (AIRA flags)
- Insufficient novelty or significance
- Ethical concerns identified by Research Integrity team
- Language quality below minimum standard
- Duplicate or concurrent submission detected

### Escalation Patterns

| Situation | Escalate to |
|-----------|-------------|
| AE unresponsive > 7 days | Specialty Chief Editor |
| Reviewer conflict of interest discovered | Research Integrity Manager |
| Author disputes rejection | Specialty Chief Editor → Field Chief Editor |
| Suspected paper mill submission | Research Integrity Manager |
| AE wants to accept but RI flags concerns | Research Integrity Manager has override authority |

### Editorial Board Health
Regular (quarterly) checks:
- AEs with zero assignments in 6 months → re-engage or rotate off
- AEs with consistently slow decisions → coaching conversation
- Sections with < 5 active AEs → recruitment needed
- Geographic/gender balance assessment

## Output Format

- Pipeline status report (manuscripts by stage, age, bottleneck)
- Reviewer availability dashboard
- Editor workload distribution
- Escalation recommendation with context
- Board health scorecard
