import os, json, math, time
import numpy as np, pandas as pd
from google.cloud import bigquery
os.environ.setdefault("GOOGLE_APPLICATION_CREDENTIALS", "/home/user/.gcp-credentials.json")
c = bigquery.Client(project="gcp-innovation-hub")
P = "ocean-tech-adv-analytics-c-tfs"; D = f"{P}.raw_citation_network_data_person"; R = "20261016_150236"
L = f"`{D}.cit_links_raw_person_{R}`"; C = f"`{D}.classification_raw_person_{R}`"
M = f"`{D}.pub_metadata_raw_person_{R}`"; AP = f"`{D}.author_papers_person_{R}`"
PUB = f"`{P}.airak_v2.Publication`"; JR = f"`{P}.airak_v2.Journal`"
OUT = "/home/user/cn"; os.makedirs(OUT, exist_ok=True)
t0 = time.time(); QLOG = []; GB = [0.0]
def log(m): print(f"[{round(time.time()-t0)}s] {m}", flush=True)
def run(title, feeds, desc, sql, params=None, page=None, record=True):
    j = c.query(sql, job_config=bigquery.QueryJobConfig(maximum_bytes_billed=200 * 10**9, query_parameters=params or []))
    r = j.result(page_size=page)
    gb = (j.total_bytes_billed or 0) / 1e9; GB[0] += gb
    if record: QLOG.append({"title": title, "feeds": feeds, "desc": desc, "sql": sql.strip(), "gb": round(gb, 1)})
    return r
dump = lambda o: json.dumps(o, separators=(",", ":"), ensure_ascii=False)

# 1 community sizes, parents and top journals
meta = {}
for lv in ("macro", "meso", "micro"):
    sql = f"""
WITH cl AS (SELECT int_id, {lv} cid, meso, macro FROM {C}),
pj AS (SELECT ap.int_id, j.DisplayName jn
       FROM {AP} ap JOIN {PUB} p ON p.PublicationId = ap.publication_id
       JOIN {JR} j ON j.JournalId = p.JournalId),
sz AS (SELECT cid, COUNT(*) n,
              APPROX_TOP_COUNT(meso, 1)[OFFSET(0)].value pmeso,
              APPROX_TOP_COUNT(macro, 1)[OFFSET(0)].value pmacro
       FROM cl GROUP BY 1),
jr AS (SELECT cl.cid, APPROX_TOP_COUNT(pj.jn, 3) tj FROM pj JOIN cl USING(int_id) GROUP BY 1)
SELECT sz.cid, sz.n, sz.pmeso, sz.pmacro, jr.tj FROM sz LEFT JOIN jr USING(cid) ORDER BY sz.cid"""
    rows = run("Community sizes, parent groups and top journals", "Every tab: community lists, sizes, top journals",
               "Run 3 times, with the level column set to macro, meso and micro (this is the micro run). The parent meso and macro are each community's most common one. Top journals count author-paper rows.",
               sql, record=(lv == "micro"))
    meta[lv] = [{"id": r["cid"], "n": r["n"], "meso": r["pmeso"], "macro": r["pmacro"], "j": [[t["value"], t["count"]] for t in (r["tj"] or [])]} for r in rows]
    log(f"meta {lv}: {len(meta[lv])}")
meta["total"] = list(run("", "", "", f"SELECT COUNT(*) n FROM {M}", record=False))[0]["n"]

# 2 macro pairs and macro stats
E = run("Citation between macro communities", "Community map (positions and lines), macro overview (internal citation share, most linked macros)",
        "Sums link weight for every ordered pair of macros, including a macro with itself. Python turns this into the size-adjusted strength and the map layout (see Processing steps).",
        f"""
WITH cl AS (SELECT int_id, macro g FROM {C})
SELECT a.g a, b.g b, SUM(l.weight) w, COUNT(*) k
FROM {L} l JOIN cl a ON a.int_id = l.int_id1 JOIN cl b ON b.int_id = l.int_id2
GROUP BY 1, 2""").to_dataframe()
NP = run("Papers per macro community", "Macro overview (papers, papers per author)", "Distinct papers written by each macro's authors.",
         f"SELECT cl.macro m, COUNT(DISTINCT ap.publication_id) np FROM {AP} ap JOIN {C} cl USING(int_id) GROUP BY 1").to_dataframe()
tot = E.groupby("a").w.sum(); intra = E[E.a == E.b].set_index("a").w; kk = E.groupby("a").k.sum()
npm = NP.set_index("m").np
mstats = {int(m): {"np": int(npm.get(m, 0)), "intra": round(100 * float(intra.get(m, 0)) / float(tot[m]), 1), "links": int(kk[m])} for m in tot.index}
X = E[E.a != E.b].copy(); X["p"] = X[["a", "b"]].min(1); X["q"] = X[["a", "b"]].max(1)
U = X.groupby(["p", "q"]).w.sum().reset_index()
s = pd.concat([U.groupby("p").w.sum(), U.groupby("q").w.sum()]).groupby(level=0).sum()
U["s"] = U.w / (s.reindex(U.p).values * s.reindex(U.q).values) * 2 * U.w.sum()
mall = [[int(p), int(q), round(float(v), 3), round(float(w), 1)] for p, q, v, w in zip(U.p, U.q, U.s, U.w)]
from sklearn.manifold import MDS
ids = sorted(set(U.p) | set(U.q)); ix = {k: i for i, k in enumerate(ids)}; n = len(ids)
Dm = np.zeros((n, n))
for p, q, v in zip(U.p, U.q, U.s): Dm[ix[p], ix[q]] = Dm[ix[q], ix[p]] = 1 / math.sqrt(v)
best = None
for seed in range(8):
    mm = MDS(n_components=2, dissimilarity="precomputed", random_state=seed, n_init=1, max_iter=3000, normalized_stress="auto")
    Pm = mm.fit_transform(Dm)
    if best is None or mm.stress_ < best[1]: best = (Pm, mm.stress_)
Pm = best[0]
dd = np.array([math.dist(Pm[ix[p]], Pm[ix[q]]) for p, q in zip(U.p, U.q)])
rho = pd.Series(dd).corr(U.s.reset_index(drop=True), method="spearman")
mpos = {int(k): [round(float(Pm[ix[k], 0]), 4), round(float(Pm[ix[k], 1]), 4)] for k in ids}
top18 = U.sort_values("s", ascending=False).head(1)
log(f"macro pairs {len(mall)}, rank corr {rho:.2f}, strongest {top18.p.iloc[0]}-{top18.q.iloc[0]} {top18.s.iloc[0]:.2f}x")

# 4 top-100 authors for each meso and micro
with open(f"{OUT}/comm2.part", "w", encoding="utf-8") as f:
    first = True
    for lv in ("meso",):
        order = "(rs <= 2) DESC, s DESC" if lv == "meso" else "s DESC"
        sql = f"""
WITH cl AS (SELECT int_id, {lv} cid, micro FROM {C}),
coauth AS (SELECT DISTINCT a.int_id i1, b.int_id i2
           FROM {AP} a JOIN {AP} b USING(publication_id) WHERE a.int_id < b.int_id),
st AS (SELECT a.int_id, a.cid, ANY_VALUE(a.micro) sub, SUM(l.weight) s, COUNT(*) k
       FROM {L} l JOIN cl a ON a.int_id = l.int_id1
       JOIN cl b ON b.int_id = l.int_id2 AND b.cid = a.cid
       GROUP BY 1, 2),
rk AS (SELECT *, ROW_NUMBER() OVER(PARTITION BY cid, sub ORDER BY s DESC) rs FROM st),
sel AS (SELECT * FROM rk QUALIFY ROW_NUMBER() OVER(PARTITION BY cid ORDER BY {order}) <= 100),
dir AS (SELECT s1.cid, l.int_id1 i1, l.int_id2 i2, l.weight w
        FROM {L} l
        JOIN sel s1 ON s1.int_id = l.int_id1
        JOIN sel s2 ON s2.int_id = l.int_id2 AND s2.cid = s1.cid
        QUALIFY ROW_NUMBER() OVER(PARTITION BY s1.cid, l.int_id1 ORDER BY l.weight DESC) <= 6),
ed AS (SELECT cid, LEAST(i1, i2) a, GREATEST(i1, i2) b, MAX(w) w FROM dir GROUP BY 1, 2, 3),
edc AS (SELECT ed.cid, STRING_AGG(FORMAT('[%d,%d,%.3g,%d]', ed.a, ed.b, ed.w, IF(co.i1 IS NULL, 0, 1)), ',') e
        FROM ed LEFT JOIN coauth co ON co.i1 = ed.a AND co.i2 = ed.b GROUP BY 1),
nd AS (SELECT s.cid, STRING_AGG(FORMAT('[%d,%s,%.4g,%d,%d]', s.int_id, TO_JSON_STRING(IFNULL(m.name, '')), s.s, s.k, s.sub), ',' ORDER BY s.s DESC) n
       FROM sel s JOIN {M} m USING(int_id) GROUP BY 1)
SELECT nd.cid, nd.n, IFNULL(edc.e, '') e FROM nd LEFT JOIN edc USING(cid)"""
        rows = run("Top 100 authors in each meso community", "Network tab (people in a sub-group, author table)",
                   "The top 2 authors of each micro come first, then the strongest overall, up to 100. Each author keeps their 6 strongest links to the others selected; coauthor pairs are flagged.",
                   sql, page=100, record=True)
        cnt = 0
        for r in rows:
            f.write(("" if first else ",") + f'"{lv}_{r["cid"]}":{{"n":[{r["n"]}],"e":[{r["e"]}]}}'); first = False; cnt += 1
        log(f"comm2 {lv}: {cnt}")

# 5 which authors get a details page
rows = run("Authors with a details page", "Details tab (who can be opened), macro overview (most connected authors)",
           "Everyone in the top 40 of their micro, meso or macro community by link strength inside that community.",
           f"""
WITH cl AS (SELECT int_id, micro, meso, macro FROM {C}),
st AS (SELECT l.int_id1 i, a.micro, a.meso, a.macro,
              SUM(IF(b.micro = a.micro, l.weight, 0)) smi,
              SUM(IF(b.meso = a.meso, l.weight, 0)) sme,
              SUM(IF(b.macro = a.macro, l.weight, 0)) sma
       FROM {L} l JOIN cl a ON a.int_id = l.int_id1 JOIN cl b ON b.int_id = l.int_id2
       GROUP BY 1, 2, 3, 4),
rk AS (SELECT i, macro,
              ROW_NUMBER() OVER(PARTITION BY micro ORDER BY smi DESC) r1,
              ROW_NUMBER() OVER(PARTITION BY meso ORDER BY sme DESC) r2,
              ROW_NUMBER() OVER(PARTITION BY macro ORDER BY sma DESC) r3
       FROM st)
SELECT i, macro, r3 FROM rk WHERE r1 <= 40 OR r2 <= 40 OR r3 <= 40""", page=50000)
emb = {65198}; mtop = {}
for r in rows:
    emb.add(r["i"])
    if r["r3"] <= 5: mtop.setdefault(r["macro"], []).append((r["r3"], r["i"]))
mtop = {int(k): [i for _, i in sorted(v)] for k, v in mtop.items()}
emb = sorted(emb); log(f"embedded authors {len(emb)}")
PRM = [bigquery.ArrayQueryParameter("ids", "INT64", emb)]

# 6 author records
rows = run("Author records", "Details tab (name, AIRAK ID, community chips, link and paper counts, papers)",
           "@ids is the list from the previous query. Keeps each author's top 3 papers, by role weight then year.",
           f"""
WITH e AS (SELECT id FROM UNNEST(@ids) id),
deg AS (SELECT l.int_id1 i, COUNT(*) d FROM {L} l JOIN e ON e.id = l.int_id1 GROUP BY 1),
pp AS (SELECT ap.int_id, COUNT(*) OVER(PARTITION BY ap.int_id) np,
              SUBSTR(IFNULL(p.Title, ''), 1, 130) t, IFNULL(p.PublishedYear, 0) y,
              IFNULL(j.DisplayName, '') jn, IFNULL(p.Doi, '') d, ap.role_weight rw
       FROM {AP} ap JOIN e ON e.id = ap.int_id
       LEFT JOIN {PUB} p ON p.PublicationId = ap.publication_id
       LEFT JOIN {JR} j ON j.JournalId = p.JournalId
       QUALIFY ROW_NUMBER() OVER(PARTITION BY ap.int_id ORDER BY ap.role_weight DESC, p.PublishedYear DESC) <= 3),
ppx AS (SELECT int_id, ANY_VALUE(np) np,
               STRING_AGG(FORMAT('[%s,%d,%s,%s,%g]', TO_JSON_STRING(t), y, TO_JSON_STRING(jn), TO_JSON_STRING(d), rw), ',' ORDER BY rw DESC, y DESC) p
        FROM pp GROUP BY 1)
SELECT FORMAT('"%d":[%s,%d,%d,%d,%d,%d,%d,[%s]]', m.int_id, TO_JSON_STRING(IFNULL(m.name, '')), m.author_id,
              IFNULL(cl.macro, -1), IFNULL(cl.meso, -1), IFNULL(cl.micro, -1), IFNULL(deg.d, 0), IFNULL(ppx.np, 0), IFNULL(ppx.p, '')) s
FROM e JOIN {M} m ON m.int_id = e.id
LEFT JOIN {C} cl ON cl.int_id = e.id
LEFT JOIN deg ON deg.i = e.id
LEFT JOIN ppx ON ppx.int_id = e.id""", params=PRM, page=5000)
with open(f"{OUT}/ego.part", "w", encoding="utf-8") as f:
    k = 0
    for r in rows: f.write(("," if k else "") + r["s"]); k += 1
log(f"author records {k}")

# 7 top 50 links + names of linked people
base = f"""
WITH e AS (SELECT id FROM UNNEST(@ids) id),
nb AS (SELECT l.int_id1 i, l.int_id2 j, l.weight w
       FROM {L} l JOIN e ON e.id = l.int_id1
       QUALIFY ROW_NUMBER() OVER(PARTITION BY l.int_id1 ORDER BY l.weight DESC) <= 50)"""
rows = run("Each author's top 50 links", "Details tab (people around the author, grey cross-links, link table)",
           "@ids as above. One compact JSON fragment per author: linked int_ids, weights, and a coauthor flag for each.",
           base + f""",
co AS (SELECT DISTINCT a.int_id i, b.int_id j
       FROM {AP} a JOIN e ON e.id = a.int_id
       JOIN {AP} b USING(publication_id)
       WHERE a.int_id != b.int_id)
SELECT FORMAT('"%d":[[%s],[%s],"%s"]', nb.i,
  STRING_AGG(CAST(nb.j AS STRING), ',' ORDER BY nb.w DESC),
  STRING_AGG(FORMAT('%.3g', nb.w), ',' ORDER BY nb.w DESC),
  STRING_AGG(IF(co.j IS NULL, '0', '1'), '' ORDER BY nb.w DESC)) s
FROM nb LEFT JOIN co ON co.i = nb.i AND co.j = nb.j
GROUP BY nb.i""", params=PRM, page=5000)
with open(f"{OUT}/e50.part", "w", encoding="utf-8") as f:
    k = 0
    for r in rows: f.write(("," if k else "") + r["s"]); k += 1
log(f"link lists {k}")
rows = run("Names and micro community of linked people", "Details tab (labels and groups for the people around each author)",
           "Uses the same e and nb steps as the previous query.",
           base + f"""
SELECT FORMAT('"%d":[%s,%d]', m.int_id, TO_JSON_STRING(IFNULL(m.name, '')), IFNULL(cl.micro, -1)) s
FROM (SELECT DISTINCT j FROM nb) x
JOIN {M} m ON m.int_id = x.j
LEFT JOIN {C} cl ON cl.int_id = x.j""", params=PRM, page=20000)
with open(f"{OUT}/nb.part", "w", encoding="utf-8") as f:
    k = 0
    for r in rows: f.write(("," if k else "") + r["s"]); k += 1
log(f"linked people {k}")

json.dump({"meta": meta, "mall": mall, "mpos": mpos, "mstats": mstats, "mtop": mtop, "doubled": True, "nemb": len(emb), "rho": round(float(rho), 2)},
          open(f"{OUT}/small.json", "w"), separators=(",", ":"), ensure_ascii=False)
json.dump(QLOG, open(f"{OUT}/queries.json", "w"), ensure_ascii=False, indent=0)
log(f"done, {GB[0]:.1f} GB billed")
