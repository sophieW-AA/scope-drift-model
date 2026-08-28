"""One-off loader: JD-strategy opportunities markdown → BigQuery reference table.

The mapper itself never reads local files. This admin script is the only place
that touches the repo markdown, and you re-run it when the JD table changes:

    python -m opportunities.seed_jd
    python -m opportunities.seed_jd --path .\\some\\other\\opportunities.md
    python -m opportunities.seed_jd --dry-run

It writes `ocean-tech-adv-analytics-c-tfs.opportunity_mapping.jd_opportunities`,
which is un-versioned and shared by every run.
"""

from __future__ import annotations

import argparse
import logging
import re
import sys
from pathlib import Path

import pandas as pd

_ROOT = Path(__file__).resolve().parents[1]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from opportunities import config as C  # noqa: E402

log = logging.getLogger("opportunities.seed_jd")

DEFAULT_PATH = (
    C.REPO / ".cursor" / "skills" / "jd-strategy" / "references" / "opportunities.md"
)


def _num(s: str) -> float | None:
    s = str(s).replace(",", "").replace("%", "").strip()
    try:
        return float(s)
    except ValueError:
        return None


def _clean(s: str) -> str:
    """Drop the decorative emoji the JD table uses as tier/pattern markers."""
    txt = re.sub(r"[^\x00-\x7F]+", " ", str(s or ""))
    return re.sub(r"\s+", " ", txt).strip()


def parse_markdown(path: Path) -> pd.DataFrame:
    """Parse the JD opportunities pipe table into rows."""
    if not path.exists():
        raise FileNotFoundError(f"JD opportunities markdown not found: {path}")
    rows = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.startswith("|"):
            continue
        parts = [c.strip() for c in line.strip("|").split("|")]
        if len(parts) < 8:
            continue
        if parts[0] in {"Tier", "---"} or parts[0].startswith("---") or "---" in parts[1]:
            continue
        if not re.search(r"Priority|Potential|Radar", parts[0]):
            continue

        fi_articles = _num(parts[7])
        mkt_2025 = _num(parts[5])
        fi_share_raw = _num(parts[8]) if len(parts) > 8 else None
        if fi_share_raw is not None and str(parts[8]).endswith("%"):
            fi_share = fi_share_raw / 100.0
        elif fi_articles is not None and mkt_2025:
            fi_share = fi_articles / mkt_2025
        else:
            fi_share = fi_share_raw

        cagr = _num(parts[6])
        if cagr is not None and parts[6].endswith("%"):
            cagr = cagr / 100.0

        rows.append(
            {
                "tier": _clean(parts[0]),
                "score": _num(parts[1]),
                "domain": _clean(parts[2]),
                "field": _clean(parts[3]),
                "subfield": _clean(parts[4]),
                "mkt_2025": mkt_2025,
                "cagr": cagr,
                "fi_articles": fi_articles,
                "fi_share": fi_share,
                "pattern": _clean(parts[9]) if len(parts) > 9 else "",
                "funding": _clean(parts[10]) if len(parts) > 10 else "",
                "anchor_journal": _clean(parts[12]) if len(parts) > 12 else "",
            }
        )
    df = pd.DataFrame(rows)
    if df.empty:
        raise ValueError(f"No JD opportunity rows parsed from {path}")
    return df


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s  %(message)s", datefmt="%H:%M:%S")
    ap = argparse.ArgumentParser(description="Load JD opportunities into BigQuery")
    ap.add_argument("--path", default=str(DEFAULT_PATH), help="Source markdown file")
    ap.add_argument("--dry-run", action="store_true", help="Parse and report, do not write")
    args = ap.parse_args()

    df = parse_markdown(Path(args.path))
    log.info("parsed %s JD subfields from %s", len(df), args.path)
    log.info("tiers: %s", df["tier"].value_counts().to_dict())
    if args.dry_run:
        log.info("dry run — nothing written")
        print(df.head(10).to_string())
        return

    from opportunities import bq as bqmod

    fq = bqmod.write_reference_table(df, C.JD_TABLE)
    log.info("done -> %s", fq)


if __name__ == "__main__":
    main()
