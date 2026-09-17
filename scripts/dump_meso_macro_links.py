"""Dump the current macro -> meso link structure from a clusters.html dashboard.

Read-only. Writes a plain-text report so the meso/macro labels can be reviewed
without editing the dashboard.
"""

import json
import re
import sys
from pathlib import Path

DEFAULT_HTML = Path(
    r"C:\Users\sophie.wilson\Documents\scope_drift_outputs\output\clusters.html"
)


def load_dashboard(path: Path) -> dict:
    text = path.read_text(encoding="utf8")
    match = re.search(r"const D\s*=\s*(\{.*?\});\s*\n", text, re.S)
    if not match:
        raise SystemExit(f"no 'const D = {{...}};' payload found in {path}")
    return json.loads(match.group(1))


def main() -> None:
    path = Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_HTML
    data = load_dashboard(path)

    macros = {m["id"]: m for m in data["macro"]}
    children: dict[int, list[dict]] = {}
    for meso in data["meso"]:
        children.setdefault(meso.get("parent_macro"), []).append(meso)

    lines = [f"source: {path}", f"macros: {len(macros)}  mesos: {len(data['meso'])}", ""]
    for macro_id in sorted(macros, key=lambda i: -macros[i].get("n_papers", 0)):
        macro = macros[macro_id]
        kids = sorted(children.get(macro_id, []), key=lambda m: -m.get("n_papers", 0))
        lines.append(
            f"MACRO C{macro_id}  {macro.get('label','?')}  "
            f"({macro.get('n_papers',0)} papers, {len(kids)} meso)"
        )
        for kid in kids:
            lines.append(
                f"    meso C{kid['id']:<4} {kid.get('n_papers',0):>6} papers  "
                f"{kid.get('label','?')}"
            )
        lines.append("")

    orphans = [m for m in data["meso"] if m.get("parent_macro") not in macros]
    if orphans:
        lines.append(f"UNPARENTED MESO ({len(orphans)}):")
        for kid in sorted(orphans, key=lambda m: -m.get("n_papers", 0)):
            lines.append(
                f"    meso C{kid['id']:<4} {kid.get('n_papers',0):>6} papers  "
                f"{kid.get('label','?')}  parent={kid.get('parent_macro')}"
            )

    out = Path(__file__).resolve().parents[1] / "logs" / "meso_macro_links_current.txt"
    out.parent.mkdir(exist_ok=True)
    out.write_text("\n".join(lines), encoding="utf8")
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
