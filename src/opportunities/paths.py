"""Local artifact paths for the opportunity mapper.

Generated files live outside the repository by default:

    ~/Documents/scope_drift_outputs/opportunities/
        output/   JSON, manifests and Excel workbooks
        logs/     run logs

Set ``OPPORTUNITIES_OUTPUT_ROOT`` to override the opportunities directory.
"""

from __future__ import annotations

import os
import logging
import sys
from datetime import datetime
from pathlib import Path


def find_repo_root() -> Path:
    """Repo root (contains main.py and src/), independent of package depth."""
    start = Path(__file__).resolve()
    for parent in start.parents:
        if (parent / "main.py").is_file() and (parent / "src").is_dir():
            return parent
    raise RuntimeError(f"Could not find repo root from {start}")


def ensure_src_on_path() -> Path:
    """Make `import opportunities` work when scripts live under src/."""
    src = find_repo_root() / "src"
    if str(src) not in sys.path:
        sys.path.insert(0, str(src))
    return src


def resolve_under(base: Path, raw: str | Path) -> Path:
    """Keep absolute paths; join relative paths onto ``base``."""
    path = Path(raw)
    if path.is_absolute():
        return path
    return (base / path).resolve()


REPO = find_repo_root()
SRC = REPO / "src"

DEFAULT_ROOT = (
    Path.home() / "Documents" / "scope_drift_outputs" / "opportunities"
)
ROOT = Path(
    os.environ.get("OPPORTUNITIES_OUTPUT_ROOT", str(DEFAULT_ROOT))
).expanduser()
OUTPUT_DIR = ROOT / "output"
LOG_DIR = ROOT / "logs"


def ensure_directories() -> tuple[Path, Path]:
    """Create and return the local output and log directories."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    return OUTPUT_DIR, LOG_DIR


def configure_logging(prefix: str = "opportunities") -> Path:
    """Configure console + UTF-8 file logging and return the log path."""
    ensure_directories()
    log_path = LOG_DIR / (
        f"{prefix}_" + datetime.now().strftime("%Y%m%d_%H%M%S") + ".log"
    )
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s  %(message)s",
        datefmt="%H:%M:%S",
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler(log_path, encoding="utf-8"),
        ],
        force=True,
    )
    logging.getLogger("opportunities").info("run log: %s", log_path)
    return log_path
