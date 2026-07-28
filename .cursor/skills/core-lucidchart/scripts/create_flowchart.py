"""Create a Lucidchart flowchart from a list of nodes and edges.

This file is skills/core-lucidchart/scripts/create_flowchart.py under the skill. The
import below works when that scripts directory is on sys.path (e.g. insert its absolute
path first) or when Python's working directory is scripts. Otherwise use
importlib.util.spec_from_file_location with the path to this file.

Usage:
    from create_flowchart import create_flowchart
    nodes = [
        ("start",  "terminator", "Start",       400,  50),
        ("step1",  "process",    "Do thing",    400, 150),
        ("check",  "decision",   "OK?",         400, 260),
        ("end",    "terminator", "End",         400, 400),
    ]
    edges = [
        ("start", "step1"),
        ("step1", "check"),
        ("check", "end", "Yes"),
    ]
    url = create_flowchart("My Title", nodes, edges)
    print(url)
"""
import os, io, json, zipfile, requests

HTTP_TIMEOUT = 60

DEFAULTS = {"process": (140, 60), "decision": (180, 90), "terminator": (140, 60),
            "data": (160, 60), "database": (140, 90), "document": (160, 80)}

def create_flowchart(title, nodes, edges, page_title="Page 1"):
    """nodes: list of (id, type, text, x, y) or (id, type, text, x, y, w, h)
       edges: list of (src_id, dst_id) or (src_id, dst_id, label)"""
    shapes = []
    for n in nodes:
        nid, ntype, text, x, y = n[:5]
        w, h = (n[5], n[6]) if len(n) >= 7 else DEFAULTS.get(ntype, (140, 60))
        shape = {"id": nid, "type": ntype, "boundingBox": {"x": x, "y": y, "w": w, "h": h}}
        if ntype not in ("or", "summingJunction"):
            shape["text"] = text
        shapes.append(shape)

    lines = []
    for i, e in enumerate(edges):
        src, dst = e[0], e[1]
        label = e[2] if len(e) > 2 else None
        line = {
            "id": f"l{i}",
            "lineType": "elbow",
            "endpoint1": {"type":"shapeEndpoint","style":"none","shapeId":src,"position":{"x":0.5,"y":1}},
            "endpoint2": {"type":"shapeEndpoint","style":"arrow","shapeId":dst,"position":{"x":0.5,"y":0}},
        }
        if label:
            line["text"] = [{"text": label, "position": 0.5, "side": "middle"}]
        lines.append(line)

    doc = {"version": 1, "pages": [{"id":"p1","title":page_title,"shapes":shapes,"lines":lines}]}

    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("document.json", json.dumps(doc))
    buf.seek(0)

    headers = {"Authorization": f'Bearer {os.environ["LUCIDCHART_ACCESS_TOKEN"]}',
               "Lucid-Api-Version": "1"}
    files = {
        "file": ("diagram.lucid", buf.getvalue(), "x-application/vnd.lucid.standardImport"),
        "title": (None, title),
        "product": (None, "lucidchart"),
    }
    r = requests.post("https://api.lucid.co/documents", headers=headers, files=files,
                      timeout=HTTP_TIMEOUT)
    r.raise_for_status()
    return r.json()["editUrl"]


def update_title(document_id, new_title):
    """Rename an existing Lucidchart document. Prefer ASCII-only titles (see SKILL Title gotcha)."""
    headers = {"Authorization": f'Bearer {os.environ["LUCIDCHART_ACCESS_TOKEN"]}',
               "Lucid-Api-Version": "1", "Content-Type": "application/json"}
    r = requests.put(f"https://api.lucid.co/documents/{document_id}",
                     headers=headers, json={"title": new_title}, timeout=HTTP_TIMEOUT)
    r.raise_for_status()
    return r.json()
