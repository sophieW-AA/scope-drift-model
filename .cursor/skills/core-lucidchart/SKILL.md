---
name: core-lucidchart
description: Native, fully-editable Lucidchart documents (flowcharts and diagrams) the user can open in Lucid and keep in their account. Use when they want chart output in Lucid, an editable Lucid-native document, or a flowchart/diagram meant to live in Lucid rather than as a static export.
---

# Create Lucidchart documents directly via API

## Mechanism

Build a Lucid **Standard Import** `document.json`, zip it as a `.lucid` archive, and `POST` to `https://api.lucid.co/documents` as multipart (`file`, `title`, `product=lucidchart`) with bearer `LUCIDCHART_ACCESS_TOKEN` and header `Lucid-Api-Version: 1`. The response includes an `editUrl` for the user. Prefer this path over Mermaid-then-import when they want Lucid-native output unless they ask otherwise (**What NOT to do**).

## Capabilities and limits

**Can do (via `POST /documents`):**
- Create a new Lucidchart document with native shapes and connectors
- Use native shapes from the **Flowchart**, **Standard**, **Container**, **BPMN 2.0**, and **Lucidspark** Standard Import libraries; concrete `type` strings and required fields are in `references/shape-types.md`, with official docs linked there for full schemas
- Set labels on shapes and connector lines
- Multi-page documents

**Cannot do via REST:**
- Edit shapes/text/lines inside an existing document (no shape-level PATCH endpoint)
- The Update Document endpoint only changes title, parent folder, and sharing
- For content changes: regenerate as a new doc, or tell the user to edit in the Lucid UI

**Auth:** `LUCIDCHART_ACCESS_TOKEN` env var. Always send header `Lucid-Api-Version: 1`.

## Workflow

1. Pick `type` values and required properties from `references/shape-types.md`. For generic flowcharts, prefer the **Flowchart** library (`terminator`, `process`, `decision`, `database`, `data`, `document`, `delay`, `manualInput`, `predefinedProcess`, `note`, …). Use **BPMN** / **Lucidspark** / **Standard** / **Container** entries in that file when the diagram calls for them.
2. Lay out shapes on a coordinate grid (x, y, w, h in points). Treat the first page as roughly **1100×850 points** (US Letter landscape); content beyond that still imports but may sit off-canvas—tighten layout, shrink shapes, or add another page for large flows. Typical sizes: decisions 180×90, processes and terminators 140×60. The reference script also defines defaults for `data`, `database`, and `document` (see `DEFAULTS` in `scripts/create_flowchart.py`). Vertical spacing 100–140 between rows.
3. Build connectors with `endpoint1` (source) and `endpoint2` (target, with `style: "arrow"`). Optional `text` array for labels (e.g., Yes/No on decisions).
4. Zip, upload, and return `editUrl` per **Mechanism** (in-memory `BytesIO` for the zip is fine).

## Reference script

`scripts/create_flowchart.py` — minimal builder from node/edge lists. Every connector uses bottom-center → top-center endpoints; branching from a decision’s sides needs custom `position` values or hand-built JSON. Use it as a starting point and adjust shapes and coordinates.

## Document format essentials

```json
{
  "version": 1,
  "pages": [{
    "id": "p1",
    "title": "My Flow",
    "shapes": [
      {"id": "s1", "type": "terminator", "boundingBox": {"x":400,"y":50,"w":140,"h":60}, "text": "Start"},
      {"id": "s2", "type": "process", "boundingBox": {"x":400,"y":200,"w":140,"h":60}, "text": "Next"}
    ],
    "lines": [
      {"id": "l1", "lineType": "elbow",
       "endpoint1": {"type":"shapeEndpoint","style":"none","shapeId":"s1","position":{"x":0.5,"y":1}},
       "endpoint2": {"type":"shapeEndpoint","style":"arrow","shapeId":"s2","position":{"x":0.5,"y":0}},
       "text": [{"text":"Yes","position":0.5,"side":"middle"}]
      }
    ]
  }]
}
```

`position` on endpoints is fractional within the shape: `(0.5, 0)` = top-center, `(0.5, 1)` = bottom-center, `(0, 0.5)` = left-middle, `(1, 0.5)` = right-middle.

## Title gotcha

Document titles are safest as **ASCII only** (letters, digits, spaces, and ASCII punctuation such as `-`, `|`, `_`). Lucid replaces many non-ASCII characters—including em-dash (`—`), en-dash, curly quotes, and accented letters—with `?`. If you need Unicode in the diagram body, keep the upload `title` ASCII and rename in the Lucid UI if needed.

## After creation

- The returned `editUrl` opens the doc in Lucid; user can drag, restyle, double-click to rename — all native edits.
- If the user asks to modify the diagram afterward: rebuild as a new document and return a fresh URL. Be upfront that the old doc is not edited in place.
- For title-only changes on an existing doc: `PUT https://api.lucid.co/documents/{id}` with `{"title": "..."}`.

## What NOT to do

- Don't fall back to Mermaid + manual import unless the user explicitly wants that flow.
- Don't claim Lucid is "read-only" for agents — uploading new documents via the API is supported.
- Don't try to PATCH shapes inside an existing doc; the endpoint doesn't exist.
