---
name: core-confluence
description: >
  Read, create, and update Confluence pages in the Frontiers Media SA instance. Use when the user needs to publish documentation, retrieve meeting notes, update journal profiles, create decision logs, or interact with any content stored in Confluence. Covers the Confluence REST API, page creation with storage format, space navigation, and content search.
---

# Confluence Integration

## Overview

This skill provides read/write access to the Frontiers Confluence instance for documentation, knowledge management, and content publishing.

## When to Use

- Publishing a document to Confluence (PRD, journal profile, meeting notes)
- Searching for existing Confluence content
- Updating an existing page
- Creating structured pages from templates
- Retrieving content for analysis or summarization

## Configuration

This skill requires the user's Confluence credentials to be available as environment variables:
- `CONFLUENCE_URL` — Base URL of the Confluence instance
- `CONFLUENCE_PERSONAL_TOKEN` — Personal Access Token for authentication

**You must always use these provided credentials.** Do not ask the user for credentials or attempt to authenticate in any other way.

Before making any Confluence API call, check that the credentials are present:

```python
import os
if not os.environ.get("CONFLUENCE_PERSONAL_TOKEN"):
    # Credentials are not configured — tell the user:
    # "Confluence is not connected yet. To set it up, open FrontonGPT → click your
    #  avatar (bottom-left) → Credentials → add a Confluence Personal Access Token.
    #  You can generate a token in Confluence → Profile → Personal Access Tokens."
```

If credentials are missing, do **not** proceed. Instead, instruct the user to configure them in FrontonGPT by going to **FrontonGPT → avatar (bottom-left) → Credentials** and adding a **Confluence Personal Access Token**.

## Key Operations

### Search for pages
```python
GET {CONFLUENCE_URL}/rest/api/content?cql=type=page AND text~"search term"
```

### Get page content
```python
GET {CONFLUENCE_URL}/rest/api/content/{pageId}?expand=body.storage
```

### Create a page
```python
POST {CONFLUENCE_URL}/rest/api/content
{
  "type": "page",
  "title": "Page Title",
  "space": {"key": "SPACE"},
  "body": {"storage": {"value": "<p>HTML content</p>", "representation": "storage"}}
}
```

### Update a page
```python
PUT {CONFLUENCE_URL}/rest/api/content/{pageId}
```

## Guidelines

- Always check if a page already exists before creating a duplicate
- Use storage format (XHTML) for page bodies
- Set meaningful page titles with consistent naming conventions
- Add labels to pages for discoverability
- When publishing, confirm the target space and parent page with the user
