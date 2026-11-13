import json, gzip, glob, base64, html, os
B = "/home/user/cn"; e = html.escape
small = json.load(open(f"{B}/small.json"))
Q = json.load(open(f"{B}/queries.json"))
P = "ocean-tech-adv-analytics-c-tfs"; D = f"{P}.raw_citation_network_data_person"; R = "20261016_150236"
TABLES = [
    (f"{D}.cit_links_raw_person_{R}", "18,378,288 rows (each link stored in both directions, 9.2M pairs)", "Author-to-author citation links with weight"),
    (f"{D}.classification_raw_person_{R}", "793,546 rows", "Leiden community of each author: micro, meso, macro"),
    (f"{D}.pub_metadata_raw_person_{R}", "817,257 rows", "Author int_id, AIRAK author_id and name"),
    (f"{D}.author_papers_person_{R}", "1,138,792 rows", "Which author wrote which paper, with role weight"),
    (f"{P}.airak_v2.Publication", "", "Paper titles, years, DOIs and journal IDs"),
    (f"{P}.airak_v2.Journal", "", "Journal names"),
]
STEPS = [
    ("Size-adjusted link strength (Python)", "Community map lines, Network macro view lines",
     "For each pair of communities a and b: strength = w(a,b) / (s(a) × s(b)) × W, where w is the summed link weight between them, s is each community's total weight to other communities, and W is the total across all pairs. 3× means their authors cite each other three times as much as their sizes predict. Links inside a community are left out."),
    ("Community map layout (Python)", "Community map positions",
     f"The map shows the 27 macro communities. Bubbles are placed by metric MDS (scikit-learn, best of 8 seeds) on all 351 macro pairs, with distance = 1/sqrt(strength), so strongly linked macros sit closer. On a flat page this fits only roughly: distance and strength have a rank correlation of {small['rho']}. Solid lines are links above 0.9×; dotted lines are each macro's 3 strongest links when below 0.9×. Line thickness = 2.2 px per 1× of strength."),
    ("Micro-view groups (browser)", "Network tab, small-group (micro) view",
     "The 100 authors shown are grouped in the browser with a Louvain-style modularity method on the links among them, so the groups are numbered and not stored in BigQuery. With more than 14 groups, single-author groups merge into \"Other\"."),
    ("Details-view groups (browser)", "Details tab",
     "The people around an author are grouped by their micro community. With more than 16 groups, single-person groups merge into \"Other micros\"."),
]
o = ['''<div class="view" id="data">
  <div class="crumbs">Data sources and queries · everything on this dashboard was exported once from BigQuery (EU) and embedded in the page</div>
  <div style="padding:14px 18px;max-width:1200px">
    <p>The dashboard is a snapshot of person-network run <code>20261016_150236</code>. It does not query BigQuery live, so a newer run means rebuilding the page. Queries ran from billing project <code>gcp-innovation-hub</code>; <code>@ids</code> is a query parameter holding the authors with a details page. These are the exact queries used for the current build.</p>
    <h3 class="dh">Source tables</h3>
    <table><tr><th>Table</th><th>Size</th><th>Used for</th></tr>''']
for t, s, u in TABLES: o.append(f"<tr><td><code>{e(t)}</code></td><td>{e(s)}</td><td>{e(u)}</td></tr>")
o.append('</table><h3 class="dh">Queries</h3>')
for k, q in enumerate(Q):
    o.append(f'''<div class="qcard"><div class="qh"><b>{k+1}. {e(q["title"])}</b><button class="qcopy" data-q="q{k}">Copy SQL</button></div>
<div class="qm"><b>Feeds:</b> {e(q["feeds"])} · <b>Scanned:</b> {q["gb"]} GB</div><div class="qm">{e(q["desc"])}</div><pre id="q{k}">{e(q["sql"])}</pre></div>''')
o.append('<h3 class="dh">Processing steps outside SQL</h3>')
for t, f, d in STEPS: o.append(f'<div class="qcard"><div class="qh"><b>{e(t)}</b></div><div class="qm"><b>Feeds:</b> {e(f)}</div><div class="qm">{e(d)}</div></div>')
o.append("</div></div>")

GZ = "/home/user/blob.gz"
with gzip.open(GZ, "wt", compresslevel=9, encoding="utf-8") as z:
    z.write(json.dumps({k: small[k] for k in ("meta", "mall", "mpos", "mstats", "mnet", "mtop")}, separators=(",", ":"), ensure_ascii=False)[:-1])
    for key, fn in (("comm2", "comm2"), ("ego", "ego"), ("e50", "e50"), ("nb", "nb")):
        z.write(f',"{key}":{{')
        with open(f"{B}/{fn}.part", encoding="utf-8") as src:
            while True:
                ch = src.read(1 << 20)
                if not ch: break
                z.write(ch)
        z.write("}")
    z.write("}")
h = open("/home/user/template.html", encoding="utf-8").read()
h = h.replace("__DATATAB__", "\n".join(o)).replace("__NEMB__", f"{small['nemb']:,}")
i = h.index("__BLOB__")
os.makedirs("/home/user/artifacts/citation-network", exist_ok=True)
with open("/home/user/artifacts/citation-network/index.html", "w", encoding="utf-8") as f, open(GZ, "rb") as src:
    f.write(h[:i])
    while True:
        ch = src.read(3 * (1 << 20))
        if not ch: break
        f.write(base64.b64encode(ch).decode())
    f.write(h[i + 8:])
with open("/home/user/page_nodata.html", "w", encoding="utf-8") as f: f.write(h)
print("gz", round(os.path.getsize(GZ) / 1e6, 1), "MB · page", round(os.path.getsize("/home/user/artifacts/citation-network/index.html") / 1e6, 1), "MB")
