---
name: core-sprinklr
description: Sprinklr Paid Advertising reporting for Frontiers Media SA. Use when the user asks about paid media performance, ad spend, campaign results, advertising KPIs, impressions, clicks, CPM, CPC, CTR, engagements, video views, or any Sprinklr Paid Dashboard data. Also use when the user wants to query the Sprinklr Reporting API (PAID engine), compare ad performance across time periods, or break down results by initiative, platform, or date.
---

# Sprinklr Paid Reporting

## Script Architecture

```
scripts/
├── client.py      # Generic Sprinklr reporting client (auth, post, parse, payload builder)
└── paid_ads.py    # Paid Advertising constants + convenience query functions
```

Future modules (social_listening, case_reporting, etc.) import `client` and add their own constants.

## Quick Start

Copy both scripts and import:

```python
import shutil, os
src = "/home/user/skills/core-sprinklr/scripts"
for f in ["client.py", "paid_ads.py"]:
    shutil.copy(f"{src}/{f}", f"/home/user/{f}")

from paid_ads import query_global_summary, query_by_group, query_raw
```

### Global summary

```python
rows = query_global_summary(start_ms=1772492400000, end_ms=1775080799999)
# Returns list with one dict: SPENT, IMPRESSIONS, CPM, CLICKS, CTR, CPC,
# ENGAGEMENTS, ENGAGEMENT_RATE, VIDEO_VIEWS, VIDEO_VIEWS_50
# Each metric also has _CHANGE and _PERCENTAGE_CHANGE variants.
```

### Grouped breakdown

```python
rows = query_by_group(
    start_ms=..., end_ms=...,
    group_bys=[{"heading": "AD_VARIANT_ID", ...}],
    page_size=100,
)
```

### Full control

```python
data = query_raw(start_ms=..., end_ms=..., filters=[...], projections=[...], group_bys=[...])
# Returns raw {"headings": [...], "rows": [[...]]}
```

Pass `include_initiatives=False` to any function to skip the initiative filter.

## What the Scripts Handle

**`client.py`** — generic, reusable across all Sprinklr engines:
- Authentication via `SPRINKLR_ACCESS_TOKEN` and `SPRINKLR_API_KEY` env vars
- Base URL: `https://api3.sprinklr.com/api/v2` (no `/prod5/` segment)
- `build_payload(report, engine, ...)` — assembles any report query
- `post_report(payload)` — executes and returns `data` dict
- `parse_response(data)` — converts `{headings, rows}` to `list[dict]`
- `to_epoch_ms(dt)` — datetime to epoch milliseconds

**`paid_ads.py`** — Frontiers paid advertising specifics:
- Account IDs: LinkedIn `1719371`, Facebook `1719385`
- Campaign filter: `26608_44`
- ~150 paid initiative IDs (current scope)
- 10 standard projections (spend, impressions, CPM, clicks, CTR, CPC, engagements, engagement rate, video views, video views 50%)
- Filter `details` metadata required by Sprinklr
- `query_global_summary()`, `query_by_group()`, `query_raw()`

Inspect script constants directly for exact values. Do not duplicate them in conversation.

## Frontiers-Specific Notes

- All times are **epoch milliseconds**, timezone `Europe/Zurich`. Use `to_epoch_ms(dt)` from `client`.
- Sprinklr auto-calculates the comparison period as the preceding window of equal length.
- The `paidInitiativeId` filter accepts both MongoDB ObjectIds and platform-prefixed IDs (e.g., `LINKEDIN_881500814`, `FACEBOOK_120230504083150697`).
- Use `skipResolve=False` (default) to get human-readable dimension names in grouped results.
- Paginate grouped queries with `page` and `page_size` params; check `hasMore` in raw response.

## Discovering New Dimensions and Metrics

```python
from client import headers
import requests

# Report metadata for the PAID engine
resp = requests.get("https://api3.sprinklr.com/api/v2/reports/reports/PAID", headers=headers())

# List all reporting engines
resp = requests.get("https://api3.sprinklr.com/api/v2/reports/engines", headers=headers())
```

API reference: https://developer.sprinklr.com/api2-0
