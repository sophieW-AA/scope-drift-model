"""Local paths for journal scope-drift further-work scripts.

Code lives in ``src/scope_drift``. Generated CSVs, JSON and PDFs stay under
``scope_drift_outputs/further_work``. Dashboard HTML is read from
``scope_drift_outputs/output``.

Override the outputs root with ``SCOPE_DRIFT_OUTPUT_ROOT``.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path


def find_repo_root() -> Path:
    start = Path(__file__).resolve()
    for parent in start.parents:
        if (parent / "main.py").is_file() and (parent / "src").is_dir():
            return parent
    raise RuntimeError(f"Could not find repo root from {start}")


REPO = find_repo_root()
SRC = REPO / "src"
CODE_DIR = Path(__file__).resolve().parent

DEFAULT_OUTPUTS = Path.home() / "Documents" / "scope_drift_outputs"
OUTPUTS = Path(os.environ.get("SCOPE_DRIFT_OUTPUT_ROOT", str(DEFAULT_OUTPUTS))).expanduser()
WORK_DIR = OUTPUTS / "further_work"
DASHBOARDS = OUTPUTS / "output"


def ensure_code_on_path() -> Path:
    """Allow sibling imports when running ``python src/scope_drift/<script>.py``."""
    if str(CODE_DIR) not in sys.path:
        sys.path.insert(0, str(CODE_DIR))
    return CODE_DIR
