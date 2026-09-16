"""Run the journal-opportunity mapper.

The default command runs the final OpenAlex + Leiden method and writes the
machine result, manifest, readable Excel workbook and run log under
``scope_drift_outputs/opportunities``.

Usage (from repo root):

    python src/opportunities/run.py
    python src/opportunities/run.py --run 20260827_081311
    python src/opportunities/run.py --skip-llm

The older P0-P5 community mapper remains available for diagnostics:

    python src/opportunities/run.py --phase all --run 20260827_081311
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
from datetime import datetime
from pathlib import Path

# Allow `python src/opportunities/run.py` from repo root
_SRC = Path(__file__).resolve().parents[1]
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))

from opportunities import config as C  # noqa: E402
from opportunities.p0_inventory import run_p0  # noqa: E402
from opportunities.p1_home import run_p1  # noqa: E402
from opportunities.p2_volume import run_p2  # noqa: E402
from opportunities.p3_market import run_p3  # noqa: E402
from opportunities.p4_engine import run_p4  # noqa: E402
from opportunities.p5_persist import run_p5  # noqa: E402

log = logging.getLogger("opportunities")


def configure_logging() -> Path:
    """Log to console and the external opportunities log directory."""
    from opportunities.paths import configure_logging as configure

    return configure("opportunities")


def write_final_outputs(
    result,
    manifest: dict,
    *,
    use_llm: bool,
) -> dict[str, Path]:
    """Write JSON, manifest and the readable Excel to the external output dir."""
    from opportunities.export_workbook import export_workbook
    from opportunities.paths import OUTPUT_DIR, ensure_directories

    ensure_directories()
    stamp = datetime.now().strftime("%Y%m%d")
    json_path = OUTPUT_DIR / f"final_journal_opportunities_{stamp}.json"
    manifest_path = OUTPUT_DIR / (
        f"final_journal_opportunities_{stamp}.manifest.json"
    )
    excel_path = OUTPUT_DIR / (
        f"leiden_journal_opportunities_readable_{stamp}.csv.xlsx"
    )
    json_path.write_text(
        result.to_json(orient="records", indent=2), encoding="utf-8"
    )
    manifest_path.write_text(
        json.dumps(manifest, indent=2, default=str), encoding="utf-8"
    )
    saved_excel = export_workbook(result, excel_path, use_llm=use_llm)
    return {
        "json": json_path,
        "manifest": manifest_path,
        "excel": saved_excel,
    }


def run(
    run_timestamp: str | None = None,
    phase: str = "final",
    journal: str | None = None,
    level: str | None = None,
    drilldown: str | None = None,
    *,
    write_excel: bool = True,
    use_llm: bool = True,
    write_bq: bool = True,
) -> dict[str, Path]:
    configure_logging()
    legacy_run = run_timestamp or C.DEFAULT_RUN
    level = level or C.COMMUNITY_LEVEL
    drilldown = drilldown or C.DRILLDOWN_LEVEL
    phases = (
        ["world", "p0", "p1", "p2", "p3", "p4", "p5", "units", "final"]
        if phase == "all"
        else [phase]
    )
    papers = candidates = home = volume = market = dec = None
    if "world" in phases:
        log.info("World market (all AIRAK publishers; Frontiers selects action only)")
        from opportunities.world_market import build_world_opportunities

        world = build_world_opportunities(legacy_run)
        log.info(
            "world opportunities:\n%s",
            world[world["is_opportunity"]]["action"].value_counts().to_string(),
        )
    if "p0" in phases:
        log.info(
            "P0 inventory (all Frontiers titles in the run) — %s communities, %s drill-down",
            level,
            drilldown,
        )
        p0 = run_p0(
            legacy_run, journal=journal, level=level, drilldown=drilldown
        )
        papers, candidates = p0["papers"], p0["candidates"]
    if "p1" in phases:
        log.info("P1 home finder")
        home = run_p1(legacy_run, papers=papers, candidates=candidates)
    if "p2" in phases:
        log.info("P2 volume")
        volume = run_p2(legacy_run, papers=papers, candidates=candidates)
    if "p3" in phases:
        log.info("P3 market")
        market = run_p3(legacy_run, candidates=candidates, home=home)
    if "p4" in phases:
        log.info("P4 decisions")
        dec = run_p4(
            legacy_run,
            candidates=candidates,
            home=home,
            volume=volume,
            market=market,
        )
        log.info("tree calls:\n%s", dec["call"].value_counts().to_string())
        from opportunities.portfolio import write_portfolio

        launches = write_portfolio(legacy_run, dec)
        log.info(
            "portfolio: %s already-publish, %s whitespace launches, %s section, %s journal",
            int((launches["presence"] == "already_publish").sum()) if len(launches) and "presence" in launches.columns else 0,
            int((launches["presence"] == "whitespace").sum()) if len(launches) and "presence" in launches.columns else 0,
            int((launches["opportunity_kind"] == "section").sum()) if len(launches) else 0,
            int((launches["opportunity_kind"] == "journal").sum()) if len(launches) else 0,
        )
    if "p5" in phases:
        log.info("P5 persist")
        run_p5(legacy_run, decisions=dec, papers=papers)
    if "units" in phases:
        # Launch units run after P0 because they read `in_baseline_primary`
        # and `is_oos` back from the papers table.
        log.info("Launch units (journal = meso or micro bundle, section = micro)")
        from opportunities.launch_units import run_launch_units

        units = run_launch_units(legacy_run)
        log.info(
            "units:\n%s",
            units[units["action"].astype(bool)]["action"]
            .value_counts()
            .to_string(),
        )
    if "final" in phases:
        log.info("Final OpenAlex-subfield launch slate with Leiden validation")
        from opportunities.final_opportunities import build_final_opportunities

        final_run = run_timestamp if phase == "final" else legacy_run
        _final, manifest = build_final_opportunities(
            final_run, write=write_bq
        )
        log.info(
            "final slate: %s shortlisted from %s qualified subfields",
            manifest["n_shortlisted"],
            manifest["n_market_qualified"],
        )
        if write_excel:
            outputs = write_final_outputs(
                _final, manifest, use_llm=use_llm
            )
            for kind, path in outputs.items():
                log.info("%s: %s", kind, path)
            return outputs
    dest = f"{C.BQ_PROJECT}.{C.BQ_OUT_DATASET}.*_{legacy_run}"
    log.info("done -> %s", dest)
    return {}


def main() -> None:
    ap = argparse.ArgumentParser(description="Scope-drift opportunity mapper")
    ap.add_argument(
        "--run",
        default=None,
        help=(
            "Scope-drift run timestamp. The final phase discovers the latest "
            "complete run when omitted."
        ),
    )
    ap.add_argument(
        "--phase",
        default="final",
        choices=[
            "all", "world", "p0", "p1", "p2", "p3", "p4", "p5", "units", "final",
        ],
    )
    ap.add_argument(
        "--journal",
        default=None,
        help="Optional: restrict to one journal. Default is all Frontiers titles in the run.",
    )
    ap.add_argument(
        "--level",
        default=C.COMMUNITY_LEVEL,
        choices=list(C.COMMUNITY_LEVELS),
        help=f"Citation-network level used as the community unit (default {C.COMMUNITY_LEVEL})",
    )
    ap.add_argument(
        "--drilldown",
        default=C.DRILLDOWN_LEVEL,
        choices=list(C.COMMUNITY_LEVELS),
        help=f"Finer level kept alongside each community (default {C.DRILLDOWN_LEVEL})",
    )
    ap.add_argument(
        "--skip-excel",
        action="store_true",
        help="Run the final analysis without writing local JSON/Excel outputs",
    )
    ap.add_argument(
        "--skip-llm",
        action="store_true",
        help="Use deterministic scope templates instead of GPT-written blurbs",
    )
    ap.add_argument(
        "--no-write-bq",
        action="store_true",
        help="Do not write the final result or manifest to BigQuery",
    )
    args = ap.parse_args()
    run(
        run_timestamp=args.run,
        phase=args.phase,
        journal=args.journal,
        level=args.level,
        drilldown=args.drilldown,
        write_excel=not args.skip_excel,
        use_llm=not args.skip_llm,
        write_bq=not args.no_write_bq,
    )


if __name__ == "__main__":
    main()
