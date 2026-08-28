"""
Scope drift pipeline orchestrator.

Default: Leiden + taxonomy + dashboard + PDF. Pass --timestamp to reuse an
existing BigQuery export (or --export to build a new network first).

Optional: --export (new CWTS network), --gt (GT map). Use --skip-leiden to
reuse an existing classification_raw_{timestamp}.

Examples:
  # Reuse export + classification (skip re-clustering)
  python main.py --timestamp 20260721_122750 --skip-leiden
  python main.py -t 20260721_122750 --skip-leiden --gt

  # New export (Leiden runs by default), then the rest
  python main.py --export --start-year 2025 --end-year 2026 --network-mode ego
  python main.py --export -t 20260828_120000 --start-year 2023 --end-year 2026

  # Re-cluster an existing export, then dashboards
  python main.py -t 20260828_120000
"""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path

REPO = Path(__file__).resolve().parent

DEFAULT_JOURNALS = [
    "Frontiers in Neurorobotics",
    "Frontiers in Earth Science",
    "Frontiers in Surgery",
    "Frontiers in Aging Neuroscience",
    "Frontiers in Environmental Science",
    "Frontiers in Chemistry",
    "Frontiers in Materials",
    "Frontiers in Robotics and AI",
]


def load_dotenv(path: Path) -> None:
    if not path.exists():
        return
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


def run_step(name: str, script: Path, env: dict[str, str], extra_args: list[str] | None = None) -> None:
    if not script.exists():
        raise SystemExit(f"[{name}] missing script: {script}")
    cmd = [sys.executable, str(script), *(extra_args or [])]
    print(f"\n{'=' * 60}")
    print(f"[{name}] {' '.join(cmd)}")
    print(f"{'=' * 60}\n", flush=True)
    result = subprocess.run(cmd, cwd=str(REPO), env=env)
    if result.returncode != 0:
        raise SystemExit(f"[{name}] failed with exit code {result.returncode}")
    print(f"\n[{name}] OK", flush=True)


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description=(
            "Run the scope-drift pipeline. "
            "Leiden runs by default; pass --timestamp to reuse an export, "
            "or --export for a new network. Use --skip-leiden to reuse clusters."
        ),
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    p.add_argument(
        "-t",
        "--timestamp",
        default=os.environ.get("RUN_TIMESTAMP", ""),
        help=(
            "BigQuery / cwts run id to build outputs from. "
            "Required when not using --export (the usual path)."
        ),
    )
    p.add_argument("--cluster-level", default="macro", choices=["micro", "meso", "macro"])
    p.add_argument(
        "--journals",
        default=",".join(DEFAULT_JOURNALS),
        help="Comma-separated journal names for dashboard / PDF steps.",
    )
    p.add_argument("--start-year", default="2023", help="Used with --export.")
    p.add_argument("--end-year", default="2026", help="Used with --export.")
    p.add_argument(
        "--network-mode",
        default="full",
        choices=["ego", "full", "global"],
        help="Used with --export.",
    )

    p.add_argument(
        "--export",
        action="store_true",
        help=(
            "Run cwts_export first (slow). Without this flag, export is skipped "
            "and --timestamp is used as-is."
        ),
    )
    p.add_argument(
        "--gt",
        action="store_true",
        help="Build GT network map after dashboards (needs local truth ODS).",
    )
    p.add_argument(
        "--skip-leiden",
        action="store_true",
        help="Skip clustering; reuse existing classification_raw_{timestamp}.",
    )
    p.add_argument("--skip-taxonomy", action="store_true")
    p.add_argument("--skip-dashboard", action="store_true")
    p.add_argument("--skip-pdf", action="store_true")
    return p.parse_args()


def base_env(args: argparse.Namespace, timestamp: str) -> dict[str, str]:
    env = os.environ.copy()

    # Step scripts log arrows and box characters; without this children inherit
    # the Windows cp1252 default and every such line raises in the log handler.
    env["PYTHONUTF8"] = "1"
    env["PYTHONIOENCODING"] = "utf-8"

    env["RUN_TIMESTAMP"] = timestamp
    env["CLUSTER_LEVEL"] = args.cluster_level
    if args.journals:
        env["JOURNALS"] = args.journals

    # Unified dashboard scope defaults (match run_pipeline.ipynb Step 3)
    env.setdefault("SCOPE_LLM_BORDERLINE_ENABLED", "1")
    env.setdefault("SCOPE_LLM_BORDERLINE_MODEL", "gpt-4o-mini")
    env.setdefault("SCOPE_LLM_BORDERLINE_PROMPT_VERSION", "v2")
    env.setdefault("SCOPE_DISTANCE_ENABLED", "0")
    env.setdefault("SCOPE_HARD_NEGATIVES_ENABLED", "1")
    env.setdefault("SCOPE_PAPER_LLM_ENABLED", "1")
    env.setdefault("SCOPE_PAPER_LLM_MODEL", "gpt-4o-mini")
    env.setdefault("LAYOUT_SEED", "42")
    return env


def main() -> None:
    os.chdir(REPO)
    load_dotenv(REPO / ".env")
    args = parse_args()

    timestamp = (args.timestamp or "").strip()
    if args.export and not timestamp:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    if not timestamp:
        raise SystemExit(
            "Pass --timestamp / -t (or set RUN_TIMESTAMP) to reuse an existing run.\n"
            "Or pass --export to create a new run (optionally with -t)."
        )

    env = base_env(args, timestamp)
    parts = []
    if args.export:
        parts.append("export")
    if not args.skip_leiden:
        parts.append("leiden")
    print(f"Mode:         {' + '.join(parts) + ' + ' if parts else ''}pipeline")
    print(f"RUN_TIMESTAMP={timestamp}")
    print(f"CLUSTER_LEVEL={args.cluster_level}")
    print(f"JOURNALS={env.get('JOURNALS', '')}")

    if args.export:
        export_env = env.copy()
        export_env["START_YEAR"] = args.start_year
        export_env["END_YEAR"] = args.end_year
        export_env["NETWORK_MODE"] = args.network_mode
        export_env["RUN_TIMESTAMP"] = timestamp
        run_step("export", REPO / "src" / "cwts_export.py", export_env)

    if not args.skip_leiden:
        run_step("leiden", REPO / "src" / "subprocess_leiden.py", env)

    if not args.skip_taxonomy:
        run_step(
            "taxonomy",
            REPO / "src" / "taxonomy_naming.py",
            env,
            extra_args=[timestamp],
        )

    if not args.skip_dashboard:
        run_step("dashboard", REPO / "src" / "build_unified_dashboard.py", env)

    if args.gt:
        run_step("gt_map", REPO / "scripts" / "build_gt_network_map.py", env)

    if not args.skip_pdf:
        run_step("pdf", REPO / "src" / "build_scope_drift_report_pdf.py", env)

    out = Path(r"C:\Users\sophie.wilson\Documents\scope_drift_outputs\dashboards")
    print(f"\nPipeline finished for RUN_TIMESTAMP={timestamp}")
    print(f"  Dashboards: {out / 'combined_dashboard.html'}")
    if args.gt:
        print("  GT map:     (see scripts/build_gt_network_map.py OUT_HTML)")
    if not args.skip_pdf:
        print(f"  PDF:        {out / 'Scope_Drift_Report.pdf'}")


if __name__ == "__main__":
    main()
