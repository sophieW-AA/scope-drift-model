"""Paper scope dashboard: Frontiers journals and how their topics are changing. Rebuilds network_bubbles_<RUN>.html from BigQuery (EU). Usage: RUN=20260827_081311 OUT=/path/to/output python3 build.py [--refresh]"""
import datetime,os,sys,json,colorsys,pickle,numpy as np,pandas as pd,scipy.sparse as sp,igraph as ig
from pathlib import Path
from google.cloud import bigquery
RUN=os.environ.get("RUN","20260827_081311"); P="ocean-tech-adv-analytics-c-tfs"; BILL="gcp-innovation-hub"
HERE=Path(__file__).resolve().parent; OUT=Path(os.environ.get("OUT",str(HERE/"out"))); OUT.mkdir(parents=True,exist_ok=True); CACHE=OUT/f"cache_{RUN}"; CACHE.mkdir(exist_ok=True)
REFRESH="--refresh" in sys.argv
bq=bigquery.Client(project=BILL)
QLOG=[]
def q(name,sql,cap=20):
    f=CACHE/f"{name}.parquet"
    if f.exists() and not REFRESH: df=pd.read_parquet(f)
    else: df=bq.query(sql,job_config=bigquery.QueryJobConfig(maximum_bytes_billed=cap*10**9)).to_dataframe(); df.to_parquet(f); print("bq",name,len(df),flush=True)
    QLOG.append(dict(name=name,sql=sql,rows=int(len(df)),ran=datetime.datetime.fromtimestamp(f.stat().st_mtime,datetime.timezone.utc).strftime("%Y-%m-%d %H:%M")))
    return df
RAW=f"`{P}.raw_citation_network_data."; OM=f"`{P}.opportunity_mapping."; TL=f"`{P}.taxonomy_labelling."; LO=f"`{P}.leiden_output."
# 1 journal x community counts for the Frontiers papers this run scores (opportunity_mapping.papers)
jc=q("jc",f"select journal,community_id,count(*) n from {OM}papers_{RUN}` group by 1,2")
jcy=q("jcy",f"select journal,community_id,year,count(*) n from {OM}papers_{RUN}` where year is not null group by 1,2,3")
YD={}
for r in jcy.itertuples(): YD.setdefault((r.journal,int(r.community_id)),{})[str(int(r.year))]=int(r.n)
# 2 stored scope calls (only the journals the run scored) -> community level
# stored scope: paper_scope has one stored scope_code per paper; join to the paper's meso community so each bubble takes the stored call
SJ=q("stored_scope_cy",f"select o.journal,o.community_id,o.year,p.scope_code,count(*) n from {OM}papers_{RUN}` o join {RAW}paper_scope_{RUN}` p using(int_id) where o.year is not null and p.cluster_level='macro' group by 1,2,3,4")
SUM=q("s_summary",f"select * from {RAW}journal_summary_{RUN}` where cluster_level='macro'").set_index('journal')
SCM=q("s_comm",f"select journal,community_id,community_label,rank_in_journal,papers_in_journal,share_of_journal_pct,community_role,borderline_verdict,borderline_reason from {RAW}scope_journal_communities_{RUN}` where cluster_level='macro' order by journal,rank_in_journal")
SDY=q("s_drift",f"select journal,pub_year,jsd,new_community_pct,entropy_delta from {RAW}scope_journal_drift_yearly_{RUN}` where cluster_level='macro' order by journal,pub_year")
SEX=q("s_ex",f"select journal,sample_type,sample_rank,title,pub_year,community_label,hard_negative from {RAW}scope_example_papers_{RUN}` where cluster_level='macro' and sample_rank<=5 order by journal,sample_type,sample_rank")
SSC=q("s_sc",f"select community_id,label,keywords,frontiers_size from {RAW}scope_communities_{RUN}` where cluster_level='macro' order by community_id")
SPR=q("s_prof",f"select cluster_id,dominant_journal,dominant_pct,keywords_top from {RAW}scope_cluster_profiles_{RUN}` where cluster_level='macro'")
SHN=q("s_hn",f"select p.journal,p.pub_year,p.community_id,p.hard_negative_pattern pat,p.is_primary_community prim,k.title from {RAW}paper_scope_{RUN}` p left join {OM}papers_{RUN}` k using(int_id) where p.hard_negative and p.cluster_level='macro'")
DRF=q("s_flags",f"select journal,community_id,logical_or(in_baseline_primary) b,logical_or(in_current_primary) c,count(distinct in_baseline_primary) kb,count(distinct in_current_primary) kc from {OM}papers_{RUN}` group by 1,2")
assert (DRF.kb==1).all() and (DRF.kc==1).all()
DRFK={(r.journal,int(r.community_id)):(bool(r.b),bool(r.c)) for r in DRF.itertuples()}
SCFG=q("s_cfg",f"select * from {RAW}scope_run_config_{RUN}` where cluster_level='macro'").iloc[0]
SMC=q("s_mcnt",f"select journal,community_id,pub_year,count(*) n from {RAW}paper_scope_{RUN}` where cluster_level='macro' group by 1,2,3")
def js_(x):
    if x is None or x is pd.NA or (isinstance(x,float) and pd.isna(x)): return None
    try: return json.loads(x)
    except Exception: return None
def nn(x):
    if x is None or x is pd.NA: return None
    try:
        if pd.isna(x): return None
    except (TypeError, ValueError): pass
    return x.item() if hasattr(x,'item') else x
# 3 labels
ml=q("meso_lab",f"select cluster_id,short_label from {TL}cluster_labels_meso_{RUN}`").set_index('cluster_id').short_label.to_dict()
Ml=q("macro_lab",f"select cluster_id,short_label from {TL}cluster_labels_macro_{RUN}`").set_index('cluster_id').short_label.to_dict()
# 4 meso->macro, and the all-publisher journal x meso matrix used for similarity
mm=q("meso_macro",f"select meso,macro,count(*) n from {RAW}classification_raw_{RUN}` group by 1,2")
m2m=mm.sort_values('n').drop_duplicates('meso',keep='last').set_index('meso').macro.to_dict()
am=q("allpub_meso",f"select m.journal,m.is_frontiers fr,k.meso,count(*) n from {RAW}pub_metadata_raw_{RUN}` m join {RAW}classification_raw_{RUN}` k using(int_id) where m.journal is not null group by 1,2,3")
jm=q("jmacro",f"select m.journal,k.macro,count(*) n from {RAW}pub_metadata_raw_{RUN}` m join {RAW}classification_raw_{RUN}` k using(int_id) where m.is_frontiers=1 group by 1,2",cap=10)
# 5 community-to-community citation weight (one aggregate in BigQuery, ~5 GB scanned)
ce=q("comm_edges",f"select a.meso m1,b.meso m2,sum(l.weight) w from {RAW}cit_links_raw_{RUN}` l join {RAW}classification_raw_{RUN}` a on a.int_id=l.int_id1 join {RAW}classification_raw_{RUN}` b on b.int_id=l.int_id2 group by 1,2")

# ---- community layout: Fruchterman-Reingold, edge weight normalised by community size (fixed seed)
ids=sorted(int(i) for i in am.meso.unique()); ix={i:k for k,i in enumerate(ids)}
sz=am.groupby('meso').n.sum()
e=ce[(ce.m1!=ce.m2)].copy(); e['a']=np.minimum(e.m1,e.m2); e['b']=np.maximum(e.m1,e.m2); e=e.groupby(['a','b'],as_index=False).w.sum()
w=(e.w/np.sqrt(e.a.map(sz)*e.b.map(sz))); w=(w/w.max()).tolist()
g=ig.Graph(n=len(ids),edges=[(ix[a],ix[b]) for a,b in zip(e.a,e.b)]); np.random.seed(7)
import random; random.seed(7); ig.set_random_number_generator(random)  # igraph draws from Python's random, not numpy
_seed=np.random.default_rng(7).random((len(ids),2)).tolist()  # fixed start: igraph ignores np.random.seed
L=np.array(g.layout_fruchterman_reingold(weights=w,niter=500,seed=_seed).coords); L=(L-L.min(0))/(L.max(0)-L.min(0))
XY={i:L[ix[i]] for i in ids}
# ---- macro palette and meso shades
PAL=["#003BDE","#279F94","#E8590C","#9C36B5","#C2255C","#5C940D","#1971C2","#F08C00","#0B7285","#862E9C","#2B8A3E","#D6336C","#495057","#E03131","#3B5BDB","#74B816","#7048E8","#099268","#A61E4D"]
macros=sorted({int(m) for m in jm.macro}); RUN_PALETTE={"0": "#003BDE", "3": "#279F94", "5": "#E7323B", "1": "#FF953E", "7": "#856DF0", "4": "#00A0DC", "2": "#287863", "10": "#7D0022", "12": "#822907", "6": "#2D1D7F", "15": "#046379", "14": "#91CF7A", "13": "#001991", "8": "#C45C26", "16": "#5B8DEF", "9": "#1F8A4C", "11": "#8E3A6B", "18": "#3D6B8C", "17": "#545454"}  # design palette copied from the original page; falls back to PAL for unseen macros
mcol={str(m):RUN_PALETTE.get(str(m),PAL[k%len(PAL)]) for k,m in enumerate(macros)}
def shade(base,k,n):
    r,gc,b=[int(base[i:i+2],16)/255 for i in (1,3,5)]; h,l,s=colorsys.rgb_to_hls(r,gc,b)
    h=(h+0.04*((k%7)-3))%1; l=min(.7,max(.35,l+0.03*((k%5)-2))); r,gc,b=colorsys.hls_to_rgb(h,l,s); return "#%02X%02X%02X"%(int(r*255),int(gc*255),int(b*255))
# ---- similarity: cosine of community-share vectors across every publisher
jn,ji=np.unique(am.journal.values,return_inverse=True); mi=np.array([ix[int(m)] for m in am.meso.values])
V=sp.csr_matrix((am.n.values.astype('float32'),(ji,mi)),shape=(len(jn),len(ids))); S=sp.diags(1/np.asarray(V.sum(1)).ravel())@V
NR=(sp.diags(1/np.sqrt(np.asarray(S.multiply(S).sum(1)).ravel()))@S).tocsr(); name2i={n:i for i,n in enumerate(jn)}
# ---- journals
fr=sorted(jc.journal.unique()); jid={n:i for i,n in enumerate(fr)}
CODE={2:'p',1:'b',0:'o'}
def plur(df,keys):  # the stored code that most of the papers carry (ties -> lowest code); 34 of 282,689 papers differ from their community's call
    t=df.groupby(keys+['scope_code'],as_index=False).n.sum().sort_values(['n','scope_code'],ascending=[False,True]).drop_duplicates(keys)
    return {tuple(r[k] if k!='community_id' else int(r[k]) for k in keys):CODE[int(r.scope_code)] for _,r in t.iterrows()}
k_all=plur(SJ,['journal','community_id']); k_y=plur(SJ,['journal','community_id','year'])
SJY=SJ.groupby(['journal','year','scope_code']).n.sum()
def sy_of(jn_):
    out={}
    for y in sorted(SJ.year.unique()):
        a=[int(SJY.get((jn_,y,c),0)) for c in (2,1,0)]
        if sum(a): out[str(int(y))]=dict(a=sum(a),o=a[2],b=a[1])
    return out
DYG={j:g for j,g in SDY.groupby('journal')}; EXG={j:g for j,g in SEX.groupby('journal')}; HNG={j:g for j,g in SHN.groupby('journal')}
MCY={}
for r in SMC.itertuples(): MCY.setdefault((r.journal,int(r.community_id)),{})[str(int(r.pub_year))]=int(r.n)
SCG={j:g for j,g in SCM.groupby('journal')}
def extras(jn_,N):
    r=SUM.loc[jn_]; assert int(r.n_articles)==N,(jn_,r.n_articles,N)
    sy=sy_of(jn_)
    for o in (js_(r.oos_by_year) or []):
        y=str(o['year']); assert sy[y]['a']==o['articles'] and sy[y]['o']==o['out_of_scope'],(jn_,y,sy[y],o); sy[y]['p']=o['out_of_scope_pct']
    for d in DYG.get(jn_,pd.DataFrame()).itertuples(): sy.setdefault(str(int(d.pub_year)),{}).update(jsd=nn(d.jsd),newc=nn(d.new_community_pct),ed=nn(d.entropy_delta))
    ex={'in_scope':[],'out_of_scope':[]}
    if jn_ in EXG:
        for x in EXG[jn_].itertuples(): ex[x.sample_type].append(dict(t=x.title,y=nn(x.pub_year),c=nn(x.community_label),hn=bool(x.hard_negative)))
    mc=[dict(id=int(c.community_id),rank=int(c.rank_in_journal),n=int(c.papers_in_journal),share=nn(c.share_of_journal_pct),role=c.community_role,verdict=nn(c.borderline_verdict),reason=nn(c.borderline_reason),y=MCY.get((jn_,int(c.community_id)),{})) for c in SCG[jn_].itertuples()]
    hn=[dict(t=nn(h.title),y=nn(h.pub_year),c=int(h.community_id),pat=h.pat,prim=bool(h.prim)) for h in HNG[jn_].itertuples()] if jn_ in HNG else []
    return dict(oosPct=nn(r.out_of_scope_pct),nOos=int(r.n_out_of_scope),nBord=int(r.n_borderline_papers),nHard=int(r.n_hard_negative_papers),nPrim=int(r.n_primary_clusters),cov=nn(r.primary_coverage_pct),
      sd=dict(jsd=nn(r.drift_jsd),newc=nn(r.drift_new_community_frac),top5=nn(r.drift_top5_jaccard),ent=nn(r.drift_entropy),ed=nn(r.drift_entropy_delta),rank=nn(r.drift_rank),latest=nn(r.drift_latest_year),base=nn(r.drift_baseline_years)),
      ss=dict(by=nn(r.primary_shift_baseline_year),ly=nn(r.primary_shift_latest_year),changed=nn(r.primary_shift_changed),insuff=nn(r.primary_shift_insufficient_data),gained=js_(r.primary_shift_gained_labels) or [],lost=js_(r.primary_shift_lost_labels) or [],baseTop=js_(r.primary_shift_baseline_top) or [],latTop=js_(r.primary_shift_latest_top) or []),
      sy=sy,mc=mc,ex=ex,hn=hn)
J=[]
for jn_ in fr:
    gj=jc[jc.journal==jn_].sort_values(['n','community_id'],ascending=[False,True]); N=int(gj.n.sum())
    comms=[]
    for r in gj.itertuples():
        c_=int(r.community_id)
        fb,fc=DRFK[(jn_,c_)]
        comms.append(dict(id=c_,n=int(r.n),k=k_all[(jn_,c_)],db=fb,dc=fc,y=YD.get((jn_,c_),{})))
    YRS=sorted(int(y) for y in jcy.year.unique())
    for y in YRS:
        for c in comms: c['ks']=c.get('ks','')+k_y.get((jn_,c['id'],y),'-')
    main=comms[0]['id']; mac=int(jm[jm.journal==jn_].sort_values(['n','macro'],ascending=[False,True]).macro.iloc[0]); wsum=gj.n.values/N
    x=float(sum(wsum*np.array([XY[int(c)][0] for c in gj.community_id]))); y=float(sum(wsum*np.array([XY[int(c)][1] for c in gj.community_id])))
    s=np.asarray((NR@NR[name2i[jn_]].T).todense()).ravel(); s[name2i[jn_]]=-1; nb=np.argsort(-s)[:6]
    near=[dict(id=jid.get(jn[a]),name=jn[a],sim=round(100*float(s[a]),1)) for a in nb]
    # DERIVED (not stored): core per year = fewest communities holding 80% (scope_run_config.primary_coverage) of that year's papers
    for c in comms: c['cy']=''
    for yy in YRS:
        ys_=str(yy); tot_=sum(c['y'].get(ys_,0) for c in comms); coreY=set(); acc=0
        for c in sorted([c for c in comms if c['y'].get(ys_,0)>0],key=lambda c:(-c['y'][ys_],-c['n'],c['id'])):
            if tot_ and acc/tot_>=float(SCFG.primary_coverage): break
            coreY.add(c['id']); acc+=c['y'][ys_]
        for c in comms: c['cy']+='-' if not c['y'].get(ys_,0) else ('1' if c['id'] in coreY else '0')
    ST=extras(jn_,N)
    J.append(dict(id=jid[jn_],name=jn_,short=jn_,n=N,macro=mac,meso=main,macroLabel=Ml.get(mac,str(mac)),mesoLabel=ml.get(main,f"Community {main}"),mesoShare=round(100*comms[0]['n']/N,1),
      mesoColor=shade(mcol[str(mac)],main,0),x=x,y=y,top=[dict(label=ml.get(c["id"],f"Community {c['id']}"),n=c['n'],share=round(100*c['n']/N,1)) for c in comms[:3]],near=near,comms=comms,nBorder=ST['nBord'],**ST))
# ---- overview layout (calculated, not stored): t-SNE on each journal's topic mix, then push overlapping bubbles apart
from sklearn.manifold import TSNE
_ids=sorted({int(c) for c in jc.community_id}); _ix={c:k for k,c in enumerate(_ids)}
_M=np.zeros((len(J),len(_ids)))
_row={jj['name']:k for k,jj in enumerate(J)}
for r_ in jc.itertuples():
    if r_.journal in _row: _M[_row[r_.journal],_ix[int(r_.community_id)]]+=r_.n
_M=np.sqrt(_M/_M.sum(1,keepdims=True))
_E=TSNE(n_components=2,perplexity=15,metric="euclidean",init="pca",random_state=42,max_iter=2000).fit_transform(_M)
# rotate so the widest spread runs left to right, then stretch to a wide panel (about 2.1 : 1)
_E=_E-_E.mean(0); _u,_s,_vt=np.linalg.svd(_E,full_matrices=False); _E=_E@_vt.T
ASP=2.1; _E[:,0]=_E[:,0]/np.ptp(_E[:,0]); _E[:,1]=_E[:,1]/np.ptp(_E[:,1])/ASP
_n=np.array([jj['n'] for jj in J],float); _r=0.5*np.maximum(9,np.sqrt(_n/_n.max())*72)/1150.0
_P=_E.copy()
for _it in range(1500):
    _d=_P[:,None,:]-_P[None,:,:]; _dist=np.sqrt((_d**2).sum(-1))+1e-9; _need=(_r[:,None]+_r[None,:])*1.06
    _ov=np.clip(_need-_dist,0,None); np.fill_diagonal(_ov,0)
    if _ov.max()<1e-4: break
    _P+=0.5*((_d/_dist[...,None])*_ov[...,None]).sum(1)/np.maximum(1,(_ov>0).sum(1))[:,None]
    _P+=0.003*(_E-_P)
# screen x is the journal's "y" and screen y is minus its "x" (see frame() in the page)
for k,jj in enumerate(J): jj['y'],jj['x']=float(_P[k,0]),float(_P[k,1])
_w=max(jj['y'] for jj in J)-min(jj['y'] for jj in J); _h=max(jj['x'] for jj in J)-min(jj['x'] for jj in J)
print("overview layout: t-SNE, rotated wide, aspect",round(_w/_h,2),"| overlap removal",_it,"iterations, max overlap",round(float(_ov.max()),4))
print("overview layout: t-SNE + overlap removal,",_it,"iterations, max overlap",round(float(_ov.max()),4))
_lo={ax:min(jj[ax] for jj in J) for ax in 'xy'}; _sp=max(max(jj[ax] for jj in J)-_lo[ax] for ax in 'xy')
for jj in J:
    for ax in 'xy': jj[ax]=float(0.1+0.8*(jj[ax]-_lo[ax])/_sp)
assert all(0.1-1e-9<=jj['y']<=0.9+1e-9 for jj in J)
mac_n=jm.groupby('macro').n.sum()
SPD={int(r.cluster_id):dict(dom=nn(r.dominant_journal),domPct=nn(r.dominant_pct),kw=js_(r.keywords_top) or []) for r in SPR.itertuples()}
DATA=dict(run=RUN,macros=[dict(id=int(m),label=Ml.get(m,str(m)),n=int(mac_n.get(m,0)),color=mcol[str(m)]) for m in sorted(macros,key=lambda m:-mac_n.get(m,0)) if mac_n.get(m,0)>0],macroColor=mcol,journals=J,papers=int(jc.n.sum()),years=sorted(int(y) for y in jcy.year.unique()),
  comms=[dict(id=i,label=ml.get(i,f"Community {i}"),x=float(XY[i][0]),y=float(XY[i][1]),macro=int(m2m.get(i,-1))) for i in ids])
DATA.update(mcomms=[dict(id=int(c.community_id),label=c.label,kw=nn(c.keywords),size=int(c.frontiers_size)) for c in SSC.itertuples()],prof=SPD,nRanked=int(SUM.drift_rank.notna().sum()),
  llm=dict(enabled=nn(SCFG.paper_llm_enabled),model=nn(SCFG.paper_llm_model),scored=int(SUM.paper_llm_n_scored.fillna(0).sum())),cfg=dict(generated=str(SCFG.generated_at)[:10],built=datetime.date.today().isoformat(),runDate=RUN[:8],coverage=nn(SCFG.primary_coverage),level=SCFG.cluster_level,baseline=nn(SCFG.baseline_years)))
head=open(HERE/"page_head.html",encoding="utf-8").read().replace("20260827_081311",RUN); rest=open(HERE/"page_script.js",encoding="utf-8").read()
import re as _re
QDESC={
 "jc":("Papers per journal and topic, all years","Bubble size for each topic, the journal's paper total, main topic and biggest topics"),
 "jcy":("Papers per journal, topic and year","Bubble size when the year slider is on, and the per-year shares in the topic-mix charts"),
 "stored_scope_cy":("Stored core status per paper, grouped by journal, topic and year","Bubble colour in Core status view: each topic takes the status most of its papers carry"),
 "s_summary":("Stored journal summary","Headline %, share outside the core by year, borderline and title-rule counts, topic mix change, change in focus, rank, core broad fields, fields gained and lost"),
 "s_comm":("Stored broad fields per journal","Broad fields table in the Summary report, with status and review verdicts"),
 "s_drift":("Stored topic mix change by year","Charts in the Over time tab"),
 "s_ex":("Stored example papers","Example papers in the Summary report"),
 "s_sc":("Stored broad-field list","Broad-field names, keywords and Frontiers paper counts"),
 "s_prof":("Stored broad-field profiles","Broad-field profiles table (keywords, biggest Frontiers journal)"),
 "s_hn":("Papers moved out by a title rule","The title-rule table in the Summary report"),
 "s_flags":("Stored baseline vs latest core flags","Loaded but not shown: the Drift view was removed because these flags disagree with the stored fields gained and lost"),
 "s_cfg":("Stored run settings","The 80% core threshold, the generated date in the source line, and the paper-level AI review status"),
 "s_mcnt":("Stored papers per journal, broad field and year","Year-by-year counts behind the broad-field mix charts"),
 "meso_lab":("Topic names","Topic labels on bubbles, hovers and tables"),
 "macro_lab":("Broad-field names","Broad-field labels and the colour legend"),
 "meso_macro":("Which broad field each topic belongs to","Colour by Broad field, and the broad field shown in hovers"),
 "allpub_meso":("Papers per journal and topic for every publisher","Similar journals (estimate) and journal positions on the overview"),
 "jmacro":("Frontiers papers per journal and broad field","Each journal's main broad field, which sets its colour on the overview"),
 "comm_edges":("Citation links between topics","Topic positions on the map (the page lays them out from these links)"),
}
def fmt(s):
    s=" ".join(s.split())
    for k in [" left join "," join "," where "," group by "," order by "," from "," having "]:
        s=s.replace(k,"\n"+k.strip()+" ")
    return s.replace("\nleft \njoin","\nleft join")
def tabs(s): return sorted(set(m.split(".")[-1] for m in _re.findall(r"`([^`]+)`",s)))
DATA["queries"]=[dict(name=x["name"],title=QDESC.get(x["name"],(x["name"],""))[0],use=QDESC.get(x["name"],("",""))[1],tables=tabs(x["sql"]),rows=x["rows"],ran=x["ran"],sql=fmt(x["sql"])) for x in QLOG]
DATA["bq"]=dict(project=P,billing=BILL,region="EU")
html=head+" "+json.dumps(DATA,separators=(",",":"))+rest
dst=OUT/f"network_bubbles_{RUN}.html"; dst.write_text(html,encoding="utf-8"); print("wrote",dst,round(len(html)/1e3),"KB",len(J),"journals",DATA['papers'],"papers")
pickle.dump(DATA,open(OUT/f"data_{RUN}.pkl","wb"))
