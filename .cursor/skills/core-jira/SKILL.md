---
name: core-jira
description: >
  Create, query, and manage Jira issues in the Frontiers Media SA instance. Use when the user needs to create tickets, track project progress, build task breakdowns, query issue status, or interact with any Jira project. Covers the Jira REST API, JQL queries, issue creation, transitions, and project navigation.
---

# Jira Integration

## Overview

This skill provides access to the Frontiers Jira instance for project management, task tracking, and workflow automation.

## When to Use

- Creating Jira tickets (tasks, stories, epics)
- Querying issue status or project progress
- Building task breakdowns for a project (e.g., journal launch checklist)
- Transitioning issues through workflows
- Generating progress reports from Jira data

## Configuration

This skill requires the user's Jira credentials to be available as environment variables:
- `JIRA_URL` — Base URL of the Jira instance
- `JIRA_PERSONAL_TOKEN` — Personal Access Token for authentication

**You must always use these provided credentials.** Do not ask the user for credentials or attempt to authenticate in any other way.

Before making any Jira API call, check that the credentials are present:

```python
import os
if not os.environ.get("JIRA_PERSONAL_TOKEN"):
    # Credentials are not configured — tell the user:
    # "Jira is not connected yet. To set it up, open FrontonGPT → click your
    #  avatar (bottom-left) → Credentials → add a Jira Personal Access Token.
    #  You can generate a token in Jira → Profile → Personal Access Tokens."
```

If credentials are missing, do **not** proceed. Instead, instruct the user to configure them in FrontonGPT by going to **FrontonGPT → avatar (bottom-left) → Credentials** and adding a **Jira Personal Access Token**.

## Key Operations

### Search issues (JQL)
```python
GET {JIRA_URL}/rest/api/2/search?jql=project=PROJ AND status="Open"
```

### Create an issue
```python
POST {JIRA_URL}/rest/api/2/issue
{
  "fields": {
    "project": {"key": "PROJ"},
    "summary": "Issue title",
    "issuetype": {"name": "Task"},
    "description": "Details here"
  }
}
```

### Transition an issue
```python
POST {JIRA_URL}/rest/api/2/issue/{issueKey}/transitions
```

## Guidelines

- Always verify the project key and issue types before creating tickets
- Use JQL for complex queries
- When creating task breakdowns, use sub-tasks under an epic or story
- Include acceptance criteria in ticket descriptions
