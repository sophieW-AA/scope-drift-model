import os, json, math
import numpy as np, pandas as pd
from google.cloud import bigquery
from sklearn.manifold import MDS
os.environ.setdefault("GOOGLE_APPLICATION_CREDENTIALS", "/home/user/.gcp-credentials.json")
c = bigquery.Client(project="gcp-innovation-hub")
D = "ocean-tech-adv-analytics-c-tfs.raw_citation_network_data_person"; R = "20261016_150236"
B = "/home/user/cn"
small = json.load(open(f"{B}/small.json"))
par = {m["id"]: m["macro"] for m in small["meta"]["meso"]}
SQL = f"""
WITH cl AS (SELECT int_id, meso FROM `{D}.classification_raw_person_{R}`)
SELECT LEAST(a.meso, b.meso) a, GREATEST(a.meso, b.meso) b, SUM(l.weight) w
FROM `{D}.cit_links_raw_person_{R}` l
JOIN cl a ON a.int_id = l.int_id1 JOIN cl b ON b.int_id = l.int_id2
WHERE l.int_id1 < l.int_id2 AND a.meso != b.meso
GROUP BY 1, 2"""
j = c.query(SQL, job_config=bigquery.QueryJobConfig(maximum_bytes_billed=50 * 10**9))
E = j.result().to_dataframe(); gb = round((j.total_bytes_billed or 0) / 1e9, 1)
E["ma"] = E.a.map(par); E["mb"] = E.b.map(par); E = E[E.ma == E.mb]
print("meso pairs inside the same macro:", len(E), "|", gb, "GB")

mesoL, mesoP, rhos = {}, {}, []
for m, g in E.groupby("ma"):
    g = g.copy()
    s = pd.concat([g.groupby("a").w.sum(), g.groupby("b").w.sum()]).groupby(level=0).sum()
    g["s"] = g.w / (s.reindex(g.a).values * s.reindex(g.b).values) * 2 * g.w.sum()
    ids = sorted(k for k, v in par.items() if v == m); ix = {k: i for i, k in enumerate(ids)}; n = len(ids)
    if n <= 2:
        P = np.array([[0.0, 0.0], [1.0, 0.0]])[:n]
    else:
        far = 1 / math.sqrt(max(g.s.min(), 1e-3) / 2)
        Dm = np.full((n, n), far); np.fill_diagonal(Dm, 0)
        for a, b, v in zip(g.a, g.b, g.s): Dm[ix[a], ix[b]] = Dm[ix[b], ix[a]] = 1 / math.sqrt(v)
        best = None
        for seed in range(6):
            mm = MDS(n_components=2, dissimilarity="precomputed", random_state=seed, n_init=1, max_iter=2000, normalized_stress="auto")
            Pm = mm.fit_transform(Dm)
            if best is None or mm.stress_ < best[1]: best = (Pm, mm.stress_)
        P = best[0]
        if len(g) >= 10:
            d = np.array([math.dist(P[ix[a]], P[ix[b]]) for a, b in zip(g.a, g.b)])
            rhos.append(pd.Series(d).corr(g.s.reset_index(drop=True), method="spearman"))
    mesoP[int(m)] = {int(k): [round(float(P[ix[k], 0]), 4), round(float(P[ix[k], 1]), 4)] for k in ids}
    mesoL[int(m)] = [[int(a), int(b), round(float(v), 3)] for a, b, v in zip(g.a, g.b, g.s)]
allS = pd.Series([x[2] for v in mesoL.values() for x in v])
print("strength quantiles:", allS.quantile([.1, .5, .9, .99]).round(2).to_dict(), "| share > 1.8x:", round((allS > 1.8).mean(), 2))
print("median layout fit (rank corr):", round(float(np.median(rhos)), 2))
small["mesoL"] = mesoL; small["mesoP"] = mesoP; small["mesoRho"] = round(float(np.median(rhos)), 2)
json.dump(small, open(f"{B}/small.json", "w"), separators=(",", ":"), ensure_ascii=False)
Q = json.load(open(f"{B}/queries.json"))
Q = [q for q in Q if q["title"] != "Citation between meso communities"]
Q.insert(3, {"title": "Citation between meso communities", "feeds": "Community map, sub-group layer (positions and lines)",
             "desc": "Python keeps pairs inside the same macro, computes size-adjusted strength within each macro, and lays each macro's sub-groups out with MDS (see Processing steps).",
             "sql": SQL.strip(), "gb": gb})
json.dump(Q, open(f"{B}/queries.json", "w"), ensure_ascii=False, indent=0)
