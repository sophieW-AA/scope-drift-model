"""Check a Confluence storage-format body parses as well-formed XML."""

import re
import sys
from pathlib import Path
from xml.etree import ElementTree

NS = (
    'xmlns:ac="http://atlassian.com/content" '
    'xmlns:ri="http://atlassian.com/resource/identifier"'
)
# Confluence resolves the HTML named entities; ElementTree only knows the XML five.
XML_ENTITIES = {"amp", "lt", "gt", "quot", "apos"}

path = Path(sys.argv[1])
body = path.read_text(encoding="utf-8")
probe = re.sub(
    r"&([a-zA-Z][a-zA-Z0-9]*);",
    lambda m: m.group(0) if m.group(1) in XML_ENTITIES else "@",
    body,
)
try:
    ElementTree.fromstring(f"<root {NS}>{probe}</root>")
except ElementTree.ParseError as exc:
    line, col = exc.position
    lines = body.splitlines()
    print(f"PARSE ERROR {exc}")
    for i in range(max(0, line - 4), min(len(lines), line + 2)):
        print(f"{i + 1:5d}| {lines[i]}")
    raise SystemExit(1)
print(f"OK: {path.name} is well-formed ({len(body.splitlines())} lines)")
