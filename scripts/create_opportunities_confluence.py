"""Create or update the Opportunities page and attach its Excel output."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import requests

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT / "src") not in sys.path:
    sys.path.insert(0, str(ROOT / "src"))
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from opportunities.paths import OUTPUT_DIR  # noqa: E402

ENV_FILE = Path(r"C:\Users\sophie.wilson\Documents\advanced-analytics-sophie\.env")
BODY_FILE = ROOT / "docs" / "confluence-opportunities.storage.html"
SPACE_KEY = "DA"
PARENT_ID = "725460028"
TITLE = "Opportunities"


def read_env(path: Path) -> dict[str, str]:
    values: dict[str, str] = {}
    for raw in path.read_text(encoding="utf-8-sig").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        values[key.strip()] = value.strip().strip("\"'")
    return values


def checked(response: requests.Response) -> requests.Response:
    if not response.ok:
        detail = response.text[:1_000]
        raise RuntimeError(
            f"Confluence returned HTTP {response.status_code}: {detail}"
        )
    return response


def latest_workbook() -> Path:
    matches = sorted(
        OUTPUT_DIR.glob("leiden_journal_opportunities_readable_*.xlsx"),
        key=lambda path: path.stat().st_mtime,
        reverse=True,
    )
    if not matches:
        raise FileNotFoundError(
            f"No opportunity workbook found in {OUTPUT_DIR}; "
            "run `python src/opportunities/run.py` first"
        )
    return matches[0]


def main() -> None:
    attachment = latest_workbook()
    env = read_env(ENV_FILE)
    base_url = (
        env.get("CONFLUENCE_BASE_URL")
        or env.get("CONFLUENCE_URL")
        or ""
    ).rstrip("/")
    token = (
        env.get("CONFLUENCE_PAT_TOKEN")
        or env.get("CONFLUENCE_PERSONAL_TOKEN")
        or ""
    )
    if not base_url or not token:
        raise RuntimeError("Confluence URL or personal access token is not configured")

    session = requests.Session()
    session.headers.update(
        {"Authorization": f"Bearer {token}", "Accept": "application/json"}
    )
    timeout = (20, 120)

    children_url = f"{base_url}/rest/api/content/{PARENT_ID}/child/page"
    children = checked(
        session.get(
            children_url,
            params={"expand": "version", "limit": 200},
            timeout=timeout,
        )
    ).json()
    existing = next(
        (page for page in children.get("results", []) if page["title"] == TITLE),
        None,
    )

    body = BODY_FILE.read_text(encoding="utf-8").replace(
        "leiden_journal_opportunities_readable_20260909.csv.xlsx",
        attachment.name,
    )
    payload: dict[str, object] = {
        "type": "page",
        "title": TITLE,
        "space": {"key": SPACE_KEY},
        "ancestors": [{"id": PARENT_ID}],
        "body": {"storage": {"value": body, "representation": "storage"}},
    }
    if existing:
        page_id = existing["id"]
        payload["id"] = page_id
        payload["version"] = {
            "number": int(existing["version"]["number"]) + 1,
            "message": "Opportunity mapper walkthrough",
        }
        response = session.put(
            f"{base_url}/rest/api/content/{page_id}",
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json; charset=utf-8"},
            timeout=timeout,
        )
        action = "Updated"
    else:
        response = session.post(
            f"{base_url}/rest/api/content",
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json; charset=utf-8"},
            timeout=timeout,
        )
        action = "Created"

    page = checked(response).json()
    page_id = page["id"]

    attachment_url = f"{base_url}/rest/api/content/{page_id}/child/attachment"
    attachment_results = checked(
        session.get(
            attachment_url,
            params={"filename": attachment.name},
            timeout=timeout,
        )
    ).json().get("results", [])
    if attachment_results:
        upload_url = (
            f"{attachment_url}/{attachment_results[0]['id']}/data"
        )
    else:
        upload_url = attachment_url

    with attachment.open("rb") as source:
        upload = session.post(
            upload_url,
            headers={"X-Atlassian-Token": "no-check"},
            files={
                "file": (
                    attachment.name,
                    source,
                    "application/vnd.openxmlformats-officedocument."
                    "spreadsheetml.sheet",
                )
            },
            data={"comment": "Latest readable opportunity-mapper output"},
            timeout=(20, 180),
        )
    checked(upload)

    web_ui = page.get("_links", {}).get("webui", "")
    print(f"{action} page {page_id}")
    print(f"Attached {attachment.name}")
    print(f"{base_url}{web_ui}")


if __name__ == "__main__":
    main()
