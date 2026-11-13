import json, gzip, re
B="/home/user/cn"; s=json.load(open(f"{B}/small.json"))
keep_mac={0,2}; mic=[m for m in s["meta"]["micro"] if m["macro"] in keep_mac]; mes=[m for m in s["meta"]["meso"] if m["macro"] in keep_mac]
want={f"meso_{m['id']}" for m in mes}|{f"micro_{m['id']}" for m in mic}
comm2=json.loads("{"+open(f"{B}/comm2.part",encoding="utf-8").read()+"}"); comm2={k:v for k,v in comm2.items() if k in want}
ego=json.loads("{"+open(f"{B}/ego.part",encoding="utf-8").read()+"}")
ids={str(n[0]) for v in comm2.values() for n in v["n"]}|{k for k,v in ego.items() if v[0] in ("Ludmila Müller","Ruth Lanius")}
ids&=set(ego); ego={k:ego[k] for k in ids}
e50=json.loads("{"+open(f"{B}/e50.part",encoding="utf-8").read()+"}"); e50={k:e50[k] for k in ids if k in e50}
nbi={str(j) for v in e50.values() for j in v[0]}
nb=json.loads("{"+open(f"{B}/nb.part",encoding="utf-8").read()+"}"); nb={k:nb[k] for k in nbi if k in nb}
out={k:s[k] for k in ("meta","mall","mpos","mstats","mnet","mtop")}; out.update(comm2=comm2,ego=ego,e50=e50,nb=nb)
with gzip.open("/home/user/sample.gz","wt",encoding="utf-8") as f: json.dump(out,f,separators=(",",":"),ensure_ascii=False)
print("sample: comm2",len(comm2),"ego",len(ego),"nb",len(nb))
