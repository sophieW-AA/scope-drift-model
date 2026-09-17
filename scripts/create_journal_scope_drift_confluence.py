"""Create or update the Journal Scope Drift page under Scope Drift."""

from __future__ import annotations

import json
from pathlib import Path

import requests

ROOT = Path(__file__).resolve().parents[1]
ENV_FILE = Path(r"C:\Users\sophie.wilson\Documents\advanced-analytics-sophie\.env")
BODY_FILE = ROOT / "docs" / "confluence-journal-scope-drift.storage.html"
SPACE_KEY = "DA"
PARENT_ID = "725460028"
TITLE = "Journal Scope Drift"


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
        raise RuntimeError(
            f"Confluence returned HTTP {response.status_code}: {response.text[:1_000]}"
        )
    return response


def main() -> None:
    env = read_env(ENV_FILE)
    base_url = (
        env.get("CONFLUENCE_BASE_URL") or env.get("CONFLUENCE_URL") or ""
    ).rstrip("/")
    token = (
        env.get("CONFLUENCE_PAT_TOKEN") or env.get("CONFLUENCE_PERSONAL_TOKEN") or ""
    )
    if not base_url or not token:
        raise RuntimeError("Confluence URL or personal access token is not configured")

    session = requests.Session()
    session.headers.update(
        {"Authorization": "Bearer " + token, "Accept": "application/json"}
    )
    timeout = (20, 120)

    children = checked(
        session.get(
            f"{base_url}/rest/api/content/{PARENT_ID}/child/page",
            params={"expand": "version", "limit": 200},
            timeout=timeout,
        )
    ).json()
    existing = next(
        (page for page in children.get("results", []) if page["title"] == TITLE),
        None,
    )

    body = BODY_FILE.read_text(encoding="utf-8")
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
            "message": "Journal scope drift method documentation",
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
    print(f"{action} page {page['id']}")
    print(f"{base_url}{page.get('_links', {}).get('webui', '')}")


if __name__ == "__main__":
    main()
