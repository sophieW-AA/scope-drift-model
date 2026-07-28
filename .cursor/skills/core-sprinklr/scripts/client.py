"""
Sprinklr Reporting API — generic client.

Handles authentication, request execution, and response parsing.
Import this from domain-specific modules (paid_ads, social_listening, etc.).
"""

import os
import requests
from datetime import datetime

SPRINKLR_BASE = "https://api3.sprinklr.com/api/v2"
REPORTS_URL = f"{SPRINKLR_BASE}/reports/query"


def headers():
    """Standard Sprinklr headers (Authorization + Key + Content-Type)."""
    return {
        "Authorization": f'Bearer {os.environ["SPRINKLR_ACCESS_TOKEN"]}',
        "Key": os.environ["SPRINKLR_API_KEY"],
        "Content-Type": "application/json",
    }


def to_epoch_ms(dt: datetime) -> int:
    """Convert a datetime to epoch milliseconds."""
    return int(dt.timestamp() * 1000)


def post_report(payload: dict) -> dict:
    """POST to the reports/query endpoint. Returns the `data` dict."""
    resp = requests.post(REPORTS_URL, headers=headers(), json=payload)
    resp.raise_for_status()
    body = resp.json()
    if body.get("errors"):
        raise RuntimeError(f"Sprinklr API errors: {body['errors']}")
    return body["data"]


def parse_response(data: dict) -> list[dict]:
    """Convert {headings, rows} into a list of dicts (one per row)."""
    hdgs = data["headings"]
    return [dict(zip(hdgs, row)) for row in data["rows"]]


def build_payload(
    report: str,
    engine: str,
    start_ms: int,
    end_ms: int,
    filters: list[dict],
    projections: list[dict],
    group_bys=None,
    page: int = 0,
    page_size: int = 10,
    timezone: str = "Europe/Zurich",
    currency: str = "USD",
    decorations: list[str] | None = None,
) -> dict:
    """Build a generic Sprinklr report payload."""
    return {
        "report": report,
        "reportingEngine": engine,
        "timeField": None,
        "startTime": start_ms,
        "endTime": end_ms,
        "timeZone": timezone,
        "page": page,
        "pageSize": page_size,
        "filters": filters,
        "groupBys": group_bys,
        "projections": projections,
        "projectionDecorations": decorations or ["CHANGE", "PERCENTAGE_CHANGE"],
        "projectionFilters": None,
        "sorts": None,
        "streamRequestInfo": None,
        "additional": {
            "Timezone": timezone,
            "translateResponse": "false",
            "fetchUnhealthyAccounts": "false",
            "appendClientAccessibleFilters": "true",
            "exportInfo": "false",
            "MARGIN": "false",
            "engine": engine,
            "Currency": currency,
            "chartType": "COUNTER",
        },
        "skipResolve": False,
        "jsonResponse": False,
    }
