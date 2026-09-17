"""Build scope-drift briefs for every test journal in the current run except Neurorobotics.

Usage (from repo root, conda env scope_drift):
  python src/scope_drift/build_all_journal_briefs.py
  python src/scope_drift/build_all_journal_briefs.py --skip-bq   # PDF only, data already on disk
"""
from __future__ import annotations

import argparse
import sys

from paths import ensure_code_on_path

ensure_code_on_path()

from analyze_rts import analyze_journal  # noqa: E402
from build_journal_brief_pdf import build_pdf  # noqa: E402
from journal_profile import journal_dir, list_journal_names  # noqa: E402
from neuro_analysis import JOURNAL as SKIP, load_dashboards  # noqa: E402
from probe_sections_rts import probe_journal  # noqa: E402


def main() -> None:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    parser = argparse.ArgumentParser()
    parser.add_argument("--skip-bq", action="store_true")
    parser.add_argument("--skip-existing", action="store_true")
    parser.add_argument("--journal", default="")
    args = parser.parse_args()

    scope, _, _ = load_dashboards()
    names = list_journal_names(scope)
    if args.journal:
        names = [args.journal]
    else:
        names = [n for n in names if n != SKIP]
    print("Journals:", ", ".join(names))

    written = []
    for name in names:
        outdir = journal_dir(name)
        pdf_path = outdir / f"{outdir.name}_scope_drift_brief.pdf"
        if args.skip_existing and pdf_path.exists():
            print(f"skip existing {pdf_path}")
            written.append(pdf_path)
            continue
        print(f"\n######## {name} -> {outdir}")
        if not args.skip_bq:
            probe_journal(name, outdir)
            analyze_journal(name, outdir)
        path = build_pdf(name, outdir)
        print(f"PDF {path}")
        written.append(path)

    print("\nDone:")
    for p in written:
        print(f"  {p}")


if __name__ == "__main__":
    main()
