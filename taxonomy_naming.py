"""CLI entry: implementation lives in src/taxonomy_naming.py."""

from pathlib import Path
import runpy
import sys

if __name__ == "__main__":
    target = Path(__file__).resolve().parent / "src" / "taxonomy_naming.py"
    sys.argv[0] = str(target)
    runpy.run_path(str(target), run_name="__main__")
