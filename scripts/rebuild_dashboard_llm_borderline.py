"""Rebuild unified dashboard with LLM borderline (loads .env locally)."""
from __future__ import annotations

import os
import runpy
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
os.chdir(REPO)

env_path = REPO / ".env"
if env_path.exists():
    for line in env_path.read_text(encoding="utf-8").splitlines():
        if "=" in line and not line.strip().startswith("#"):
            k, v = line.split("=", 1)
            os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))

os.environ.setdefault("RUN_TIMESTAMP", "20260721_122750")
os.environ.setdefault("CLUSTER_LEVEL", "macro")
os.environ.setdefault("SCOPE_LLM_BORDERLINE_ENABLED", "1")
os.environ.setdefault("SCOPE_LLM_BORDERLINE_MODEL", "gpt-4o-mini")
os.environ.setdefault("SCOPE_DISTANCE_ENABLED", "0")
os.environ.setdefault("LAYOUT_SEED", "42")
os.environ.setdefault(
    "JOURNALS",
    ",".join(
        [
            "Frontiers in Neurorobotics",
            "Frontiers in Earth Science",
            "Frontiers in Surgery",
            "Frontiers in Aging Neuroscience",
            "Frontiers in Environmental Science",
            "Frontiers in Chemistry",
            "Frontiers in Materials",
            "Frontiers in Robotics and AI",
        ]
    ),
)

print("openai_set", bool(os.environ.get("OPENAI_API_KEY")))
print("RUN_TIMESTAMP", os.environ["RUN_TIMESTAMP"])
runpy.run_path(str(REPO / "src" / "build_unified_dashboard.py"), run_name="__main__")
