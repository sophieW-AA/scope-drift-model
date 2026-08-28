"""Run the opportunity mapper: P0 → P5.

Reads only from BigQuery and writes only to BigQuery (`opportunity_mapping`).
No local files are read or written at any phase.

Usage (from repo root):

    python -m opportunities.run
    python -m opportunities.run --level meso --drilldown micro
    python -m opportunities.run --journal "Frontiers in Neurorobotics"

The JD market reference table is loaded separately, once:

    python -m opportunities.seed_jd
"""

from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path

# Allow `python opportunities/run.py` from repo root
_ROOT = Path(__file__).resolve().parents[1]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from opportunities import config as C  # noqa: E402
from opportunities.p0_inventory import run_p0  # noqa: E402
from opportunities.p1_home import run_p1  # noqa: E402
from opportunities.p2_volume import run_p2  # noqa: E402
from opportunities.p3_market import run_p3  # noqa: E402
from opportunities.p4_engine import run_p4  # noqa: E402
from opportunities.p5_persist import run_p5  # noqa: E402

log = logging.getLogger("opportunities")


def run(
    run_timestamp: str = C.DEFAULT_RUN,
    phase: str = "all",
    journal: str | None = None,
    level: str | None = None,
    drilldown: str | None = None,
) -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s  %(message)s",
        datefmt="%H:%M:%S",
    )
    level = level or C.COMMUNITY_LEVEL
    drilldown = drilldown or C.DRILLDOWN_LEVEL
    phases = ["p0", "p1", "p2", "p3", "p4", "p5"] if phase == "all" else [phase]
    papers = candidates = home = volume = market = dec = None
    if "p0" in phases:
        log.info(
            "P0 inventory (all Frontiers titles in the run) — %s communities, %s drill-down",
            level,
            drilldown,
        )
        p0 = run_p0(
            run_timestamp, journal=journal, level=level, drilldown=drilldown
        )
        papers, candidates = p0["papers"], p0["candidates"]
    if "p1" in phases:
        log.info("P1 home finder")
        home = run_p1(run_timestamp, papers=papers, candidates=candidates)
    if "p2" in phases:
        log.info("P2 volume")
        volume = run_p2(run_timestamp, papers=papers, candidates=candidates)
    if "p3" in phases:
        log.info("P3 market")
        market = run_p3(run_timestamp, candidates=candidates, home=home)
    if "p4" in phases:
        log.info("P4 decisions")
        dec = run_p4(
            run_timestamp,
            candidates=candidates,
            home=home,
            volume=volume,
            market=market,
        )
        log.info("tree calls:\n%s", dec["call"].value_counts().to_string())
        from opportunities.portfolio import write_portfolio

        launches = write_portfolio(run_timestamp, dec)
        log.info(
            "portfolio: %s already-publish, %s whitespace launches, %s section, %s journal",
            int((launches["presence"] == "already_publish").sum()) if len(launches) and "presence" in launches.columns else 0,
            int((launches["presence"] == "whitespace").sum()) if len(launches) and "presence" in launches.columns else 0,
            int((launches["opportunity_kind"] == "section").sum()) if len(launches) else 0,
            int((launches["opportunity_kind"] == "journal").sum()) if len(launches) else 0,
        )
    if "p5" in phases:
        log.info("P5 persist")
        run_p5(run_timestamp, decisions=dec, papers=papers)
    dest = f"{C.BQ_PROJECT}.{C.BQ_OUT_DATASET}.*_{run_timestamp}"
    log.info("done -> %s", dest)


def main() -> None:
    ap = argparse.ArgumentParser(description="Scope-drift opportunity mapper")
    ap.add_argument("--run", default=C.DEFAULT_RUN, help="Scope-drift run timestamp")
    ap.add_argument(
        "--phase",
        default="all",
        choices=["all", "p0", "p1", "p2", "p3", "p4", "p5"],
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
    args = ap.parse_args()
    run(
        run_timestamp=args.run,
        phase=args.phase,
        journal=args.journal,
        level=args.level,
        drilldown=args.drilldown,
    )


if __name__ == "__main__":
    main()
