---
name: product-prd
description: Create structured Product Requirements Documents for Frontiers Media SA and publish them to Confluence. Use when a PM or engineer says "write a PRD", "document requirements", "plan a feature", or needs to translate a product idea into a specification that engineers can use with GitHub Spec Kit for spec-driven development.
---

# Product Requirements Document (PRD)

Generate a complete PRD in Confluence from a product idea. The PRD bridges PM intent and engineering execution via GitHub Spec Kit.

## Workflow

### Phase 1 — Discovery

Before writing anything, ask the user to fill gaps. Do not assume context.

**Mandatory inputs** (block until answered):

1. **Problem** — Why are we building this now? What pain exists today?
2. **Success metrics** — How do we know it worked? (concrete numbers, not "improve")
3. **Constraints** — Budget, team size, deadline, compliance, tech stack mandates?

**Optional inputs** (ask if not obvious):

- Target users / personas
- Dependencies on other teams or systems
- Relevant JIRA epic or Confluence space
- Existing Spec Kit project or new?

Stop after ≤5 questions. If the user says "just write it," use `[NEEDS CLARIFICATION]` markers and proceed.

### Phase 2 — Draft

Generate the PRD using the schema below. Write in Confluence wiki markup (Atlassian Storage Format) so it can be published directly via the REST API.

### Phase 3 — Publish to Confluence

Use the Confluence REST API to create the page:

```python
import os, requests, json

page_data = {
    "type": "page",
    "title": "<PRD title>",
    "space": {"key": "<space key>"},  # Default: "PM" unless user specifies
    "ancestors": [{"id": "<parent page id>"}],  # Optional
    "body": {
        "storage": {
            "value": "<generated markup>",
            "representation": "storage"
        }
    }
}

resp = requests.post(
    f'{os.environ["CONFLUENCE_URL"]}/rest/api/content',
    json=page_data,
    headers={
        "Authorization": f'Bearer {os.environ["CONFLUENCE_PERSONAL_TOKEN"]}',
        "Content-Type": "application/json"
    },
    verify=False
)
```

After publishing, return the page URL to the user.

### Phase 4 — Review

Present a summary and ask: "Anything to change before I finalize?" Apply feedback, update the Confluence page via PUT.

## PRD Schema

Follow this structure exactly. Every section is mandatory unless marked optional.

### 1. Header

| Field | Value |
|---|---|
| Title | PRD: [Feature Name] |
| Author | [User's name] |
| Status | Draft |
| Date | [Today] |
| JIRA Epic | [Link or TBD] |
| Spec Kit Branch | [###-feature-name or TBD] |

### 2. Executive Summary

- **Problem Statement**: 1–2 sentences on the pain point. Be specific about who feels it and how often.
- **Proposed Solution**: 1–2 sentences on the fix. No implementation details.
- **Success Criteria**: 3–5 measurable KPIs with target numbers.

### 3. User Scenarios & Stories

Adopt the Spec Kit format — prioritized, independently testable user stories.

For each story:

```
### User Story [N] — [Title] (Priority: P[N])

[Plain language description]

**Why this priority**: [Value justification]

**Independent Test**: [How to verify this works on its own]

**Acceptance Scenarios**:
1. **Given** [state], **When** [action], **Then** [outcome]
2. **Given** [state], **When** [action], **Then** [outcome]
```

Rules:
- P1 = MVP. If you build only P1, the product still delivers value.
- Each story must be independently deployable and testable.
- Use concrete language. Replace "fast" with "< 200ms p95." Replace "easy" with a specific interaction count.

**Non-Goals**: List what this PRD explicitly does NOT cover. Protect the timeline.

**Edge Cases**: Enumerate boundary conditions and error scenarios.

### 4. Requirements

**Functional Requirements** — Use IDs (FR-001, FR-002…):

- System MUST [capability]
- Mark unknowns: `[NEEDS CLARIFICATION: specific question]`

**Key Entities** (if the feature involves data):

- Entity name, attributes, relationships — no implementation details yet.

**Non-Functional Requirements**:

- Performance targets (latency, throughput)
- Security & compliance (GDPR, data residency)
- Availability / SLAs
- Accessibility standards

### 5. Frontiers Context

This section anchors the PRD in the Frontiers business domain.

- **Affected systems**: Which Frontiers platform areas does this touch? (e.g., Editorial, Billing, AIRA, Loop, Author Portal)
- **Data domains**: Reference relevant BigQuery datasets/tables from the Frontiers data lakehouse if applicable.
- **Journal / author impact**: How does this affect the research community? Quantify where possible (journals, articles, authors affected).
- **Compliance**: Any Open Access, GDPR, or publishing ethics considerations.

### 6. Technical Orientation

Provide enough context for engineers to initialize a Spec Kit project. Do NOT design the solution — that's the engineer's job via `/speckit.plan`.

- **Suggested tech stack**: Language, framework, database preferences (or "team's choice").
- **Integration points**: APIs, services, databases this feature must connect to.
- **Known constraints**: Auth method, infra requirements, deployment targets.
- **Spec Kit readiness**: Can this go straight to `/speckit.specify`, or does it need a research spike first?

### 7. Risks & Phased Rollout

**Phased Rollout**:

| Phase | Scope | Stories | Target |
|---|---|---|---|
| MVP | [Minimal viable scope] | P1 | [Date or sprint] |
| v1.1 | [Extended scope] | P1 + P2 | [Date or sprint] |
| v2.0 | [Full vision] | All | [Date or sprint] |

**Risks**:

| Risk | Impact | Likelihood | Mitigation |
|---|---|---|---|
| [Technical risk] | High/Med/Low | High/Med/Low | [Action] |
| [Dependency risk] | High/Med/Low | High/Med/Low | [Action] |

### 8. Open Questions

Consolidate all `[NEEDS CLARIFICATION]` markers here as a checklist:

- [ ] [Question 1]
- [ ] [Question 2]

This section must be empty (all resolved) before the PRD moves from Draft to Ready.

## Spec Kit Bridge

The PRD is the input artifact for Spec Kit. When an engineer picks up the PRD:

1. Run `/speckit.specify` using Section 3 (User Scenarios) as the feature description.
2. Run `/speckit.plan` using Section 6 (Technical Orientation) for tech stack input.
3. Run `/speckit.tasks` to generate the implementation task list.
4. Run `/speckit.implement` to execute.

Structure the PRD so that Section 3 can be copy-pasted as the `/speckit.specify` prompt with zero editing.

## Quality Rules

### DO

- Use concrete, measurable criteria. "Search returns results in < 200ms for 10K records."
- Mark every ambiguity with `[NEEDS CLARIFICATION: ...]`.
- Include Non-Goals to prevent scope creep.
- Write user stories that are independently testable and deployable.
- Reference Frontiers systems, data, and business context.

### DON'T

- Skip Discovery. Always ask ≥2 clarifying questions before drafting.
- Invent constraints the user didn't mention — mark as TBD.
- Include implementation details (architecture, code, class diagrams) — that's Spec Kit's job.
- Use vague language: "intuitive", "fast", "modern", "seamless", "easy to use."

## Confluence Formatting

Generate pages using Atlassian Storage Format (XHTML). Key patterns:

- Headings: `<h2>`, `<h3>`
- Tables: `<table><tr><th>` / `<td>`
- Status macro: `<ac:structured-macro ac:name="status"><ac:parameter ac:name="colour">Blue</ac:parameter><ac:parameter ac:name="title">Draft</ac:parameter></ac:structured-macro>`
- Info panel: `<ac:structured-macro ac:name="info"><ac:rich-text-body><p>text</p></ac:rich-text-body></ac:structured-macro>`
- Warning panel: `<ac:structured-macro ac:name="warning">` for `[NEEDS CLARIFICATION]` items
- Checklist: `<ac:task-list>` / `<ac:task>` for open questions
- JIRA link: `<ac:structured-macro ac:name="jira"><ac:parameter ac:name="key">PROJ-123</ac:parameter></ac:structured-macro>`

Wrap the full body in a single string for the API call. Escape special characters in user-provided text.
