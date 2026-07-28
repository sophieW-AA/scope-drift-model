# Lucid Standard Import — common shape types

Official library pages (schemas and edge cases): [Flowchart](https://developer.lucid.co/v1.0/docs/flowchart-library-si), [Standard](https://developer.lucid.co/v1.0/docs/standard-library-si), [Container](https://developer.lucid.co/v1.0/docs/container-library-si), [BPMN 2.0](https://developer.lucid.co/docs/bpmn-20-library-si), [Lucidspark](https://developer.lucid.co/v1.0/docs/lucidspark-library-si). This file summarizes `type` values agents use most often; use the links for complete property lists.

## Flowchart Library (most useful for diagrams)

| `type` value | Visual | Typical use |
|---|---|---|
| `terminator` | Stadium / pill | Start, End |
| `process` | Rectangle | Action / step |
| `decision` | Diamond | Yes/No branch |
| `data` | Parallelogram | Input / output |
| `document` | Rectangle with wavy bottom | Document |
| `database` | Cylinder | Data store |
| `delay` | Half-stadium | Wait / pause |
| `manualInput` | Slanted-top rectangle | Manual entry |
| `manualOperation` | Inverted trapezoid | Manual step |
| `predefinedProcess` | Rectangle with side bars | Subroutine (requires `sideWidth`: 0–0.33) |
| `preparation` | Hexagon | Setup step |
| `merge` | Inverted triangle | Merge paths |
| `or` | Circle with `+` | Or junction (no `text`) |
| `summingJunction` | Circle with `×` | Sum (no `text`) |
| `note` | Folded-corner rectangle | Annotation |
| `connector` | Small circle | Off-page connector |
| `offPageLink` | Pentagon | Off-page link |
| `storedData` | Curved-side rectangle | Stored data |
| `directAccessStorage` | Cylinder (horizontal) | Hard disk |
| `internalStorage` | Rectangle with cross | Internal storage |
| `paperTape` | Wavy top and bottom | Paper tape |
| `display` | Rounded-right rectangle | Display |
| `multipleDocuments` | Stacked documents | Multiple docs |
| `braceNote` | `{` brace | Brace note (requires `rightFacing`, `braceWidth`) |

## Standard Library (basic shapes)

| `type` value | Visual | Typical use |
|---|---|---|
| `rectangle`, `roundedRectangle` | Rectangle / rounded | Boxes, steps |
| `ellipse`, `circle` | Ellipse / circle | States, nodes |
| `triangle`, `diamond`, `hexagon`, `octagon` | Polygon variants | Decision / generic |
| `cloud`, `star` | Cloud / star | Highlights, ratings |
| `arrowRight`, `arrowLeft`, `arrowUp`, `arrowDown` | Directional arrows | Callouts, flow hints |

Full property list: https://developer.lucid.co/v1.0/docs/standard-library-si

## Container Library

| `type` value | Visual | Typical use |
|---|---|---|
| `swimLanes` | Horizontal lanes with vertical dividers | Cross-role or cross-phase flows (pool/lane layout) |

Schema and extra properties: https://developer.lucid.co/v1.0/docs/container-library-si

## BPMN 2.0 Library

All `type` values use the `bpmn…` prefix. Shapes below usually need more than `boundingBox` + `text`; see [BPMN 2.0 library](https://developer.lucid.co/docs/bpmn-20-library-si) for enums and nested objects (e.g. pool `lanes`).

| `type` value | Visual / role | Typical use |
|---|---|---|
| `bpmnActivity` | Task / subprocess / call block (varies) | Work; set `activityType` (`task`, `transaction`, `eventSubProcess`, `callActivity`), optional `taskType`, `activityMarker1`, `activityMarker2` |
| `bpmnEvent` | Circle with BPMN icon | Start / intermediate / end; **required** `eventGroup` (`start`, `intermediate`, `end`); optional `eventType`, `nonInterrupting`, `throwing` |
| `bpmnGateway` | Diamond (variant by type) | Branching; optional `gatewayType` (`exclusive`, `parallel`, `inclusive`, `complex`, …) |
| `bpmnDataObject` | Folded document | Data artifact; optional `dataType` (`none`, `collection`, `input`, `output`) |
| `bpmnDataStore` | Open-topped cylinder | Persistent store |
| `bpmnPool` | Pool with lanes | Participant lanes; **required** `title`, `lanes` array; optional `vertical`, `verticalLaneText`, `magnetize` |
| `bpmnBlackBoxPool` | Collapsed pool | External / opaque participant |
| `bpmnGroup` | Dashed area | Annotation group; optional `magnetize` |
| `bpmnTextAnnotation` | Text + association | Side notes |
| `bpmnConversation` | Conversation node | Collaboration; optional `isCall`, `isSubConversation` |
| `bpmnChoreography` | Choreography task | Message choreography; **required** `choreographyType`, `participants` |

Illustrated variants (which icon shows for which `eventType` / gateway, etc.): https://developer.lucid.co/docs/bpmn-shapes-reference-si

## Lucidspark Library

Lucidchart Standard Import can embed Lucidspark-style shapes (e.g. for workshop-style canvases). Most need library-specific fields beyond a simple flowchart shape.

| `type` value | Visual | Typical use |
|---|---|---|
| `freehandDrawing` | Ink stroke | Sketches; **required** `style` (width, color), `points` array, optional `offset` |
| `sparkCalloutSquare` | Square callout | Sticky-style note |
| `sparkContainer` | Grouping container | Cluster content; optional `magnetize` |
| `sparkFrame` | Titled frame | Section boundary; uses `title`; optional `magnetize` |

## Line types

`lineType` values: `elbow` (right-angle, default for flowcharts), `straight`, `curved`.

`endpoint.style` values: `none`, `arrow`, `hollowArrow`, `triangle`, `hollowTriangle`, `diamond`, `hollowDiamond`, `circle`, `hollowCircle`.

## Style block (optional, for colors)

```json
"style": {
  "fill": {"type": "color", "color": "#ffcc00"},
  "stroke": {"color": "#333333", "width": 2, "style": "solid"}
}
```

## Coordinates

- All coordinates and sizes in points (1pt ≈ 1.33px).
- Origin (0,0) is top-left of the page.
- Standard page is roughly 1100×850 points (US Letter landscape).
- Endpoint `position` is fractional inside the shape: `(0,0)` top-left corner, `(1,1)` bottom-right corner.
