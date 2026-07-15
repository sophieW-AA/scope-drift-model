(function () {
  const M = DATA.meta || {};
  const J = DATA.journals || [];
  const C = DATA.communities || [];

  /* ── Timestamp & scope ── */
  const now = new Date();
  const p = n => String(n).padStart(2,"0");
  document.getElementById("snapStamp").textContent =
    now.getUTCFullYear()+"-"+p(now.getUTCMonth()+1)+"-"+p(now.getUTCDate())
    +" "+p(now.getUTCHours())+":"+p(now.getUTCMinutes())+" UTC";
  document.getElementById("scopeDesc").textContent =
    (M.year_range||[]).join("–")+", "+J.length+" journals, "
    +((M.primary_cluster_coverage||0.8)*100).toFixed(0)+"% primary cluster coverage";

  /* ── Footer ── */
  const totalPapers = J.reduce((s,r)=>s+(r.articles||0),0);
  const totalOOS    = J.reduce((s,r)=>s+(r.out_of_scope||0),0);
  document.getElementById("ftYears").textContent    = (M.year_range||[]).join("–");
  document.getElementById("ftCov").textContent      = ((M.primary_cluster_coverage||0.8)*100).toFixed(0);
  document.getElementById("ftJournals").textContent = J.length;
  document.getElementById("ftPapers").textContent   = totalPapers.toLocaleString();
  document.getElementById("ftComms").textContent    = C.length;
  
  /* ── Source metadata ── */
  const R = DATA.run_metadata || {};
  const ftSource = document.getElementById("ftSource");
  if (ftSource && (R.generated_utc || R.run_timestamp)) {
    const parts = [];
    if (R.generated_utc) parts.push("Generated " + R.generated_utc);
    if (R.bq_source_dataset) parts.push("Source: " + R.bq_source_dataset);
    if (R.network_mode) parts.push("Mode: " + R.network_mode);
    if (R.start_year && R.end_year) parts.push("Years: " + R.start_year + "–" + R.end_year);
    if (R.edge_weighting_enabled && R.temporal_decay_tau) parts.push("τ=" + R.temporal_decay_tau);
    if (R.run_timestamp) parts.push("Run: " + R.run_timestamp);
    ftSource.textContent = parts.join(" · ");
  }

  /* ── KPI strip ── */
  const avgOOS = totalPapers ? (totalOOS/totalPapers*100) : 0;
  const worst  = J.slice().sort((a,b)=>b.out_of_scope_pct-a.out_of_scope_pct)[0];
  [
    { label:"Journals analysed",   value:J.length,                    sub:"Frontiers journals in scope" },
    { label:"Articles",            value:totalPapers.toLocaleString(),sub:(M.year_range||[]).join("–") },
    { label:"Out of scope",        value:totalOOS.toLocaleString(),   sub:avgOOS.toFixed(1)+"% overall" },
    { label:"Communities",         value:C.length,                    sub:"themes in global network" },
    { label:"Highest OOS journal", value:worst?worst.out_of_scope_pct.toFixed(1)+"%":"—", sub:worst?worst.name:"" }
  ].forEach(k=>{
    const el=document.createElement("div");
    el.className="kpi";
    el.innerHTML='<div class="kpi-label">'+k.label+'</div>'
      +'<div class="kpi-value">'+k.value+'</div>'
      +'<div class="kpi-sub">'+k.sub+'</div>';
    document.getElementById("kpiRow").appendChild(el);
  });

  /* ── Tabs ── */
  document.querySelectorAll(".tab-btn").forEach(btn=>{
    btn.addEventListener("click",()=>{
      document.querySelectorAll(".tab-btn").forEach(b=>b.classList.remove("active"));
      document.querySelectorAll(".tab-content").forEach(c=>c.classList.remove("active"));
      btn.classList.add("active");
      document.getElementById("tab-"+btn.dataset.tab).classList.add("active");
      window.dispatchEvent(new Event("resize"));
    });
  });

  /* ── Plotly defaults ── */
  const FONT = { family:'-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,sans-serif', color:"#1a1f36", size:12 };
  const AX   = { gridcolor:"#f0f2f7", linecolor:"#e3e7ee", zerolinecolor:"#e3e7ee",
                  tickfont:{size:11,color:"#5f6b7c"}, titlefont:{size:11,color:"#5f6b7c"} };
  const BASE = { paper_bgcolor:"#ffffff", plot_bgcolor:"#ffffff", font:FONT };
  const CFG  = { responsive:true, displayModeBar:false };
  const ext  = (a,b)=>Object.assign({},a,b);

  /* ── OOS by year ── */
  const years = M.oos_per_year_years||[];
  if (years.length) {
    const PAL=["#2c5fa3","#1f8a4c","#d4a300","#856DF0","#31C7D1","#FF953E","#c93030","#279F94","#b07a00","#6366f1"];
    Plotly.newPlot("barOOSYear", J.map((r,i)=>({
      type:"bar", name:r.name,
      x:years,
      y:years.map(y=>{ const row=(r.oos_by_year||[]).find(o=>o.year===y); return row&&row.articles?row.out_of_scope_pct:null; }),
      marker:{color:PAL[i%PAL.length]},
      hovertemplate:"<b>%{fullData.name}</b><br>Year %{x}<br>OOS: %{y:.1f}%<extra></extra>"
    })), ext(BASE,{
      barmode:"group",
      xaxis:ext(AX,{title:"Year",dtick:1,automargin:true}),
      yaxis:ext(AX,{title:"Out-of-scope %",ticksuffix:"%",range:[0,50],automargin:true}),
      legend:{orientation:"h",y:-0.3,font:{size:11}},
      margin:{l:50,r:20,t:10,b:110}
    }), CFG);
  }

  /* ── Journal table ── */
  const tb1=document.querySelector("#tblJournal tbody");
  J.slice().sort((a,b)=>b.out_of_scope_pct-a.out_of_scope_pct).forEach(r=>{
    const tc=(r.top_communities||[])[0];
    const lbl=tc?((tc.label||("C"+tc.comm_id)).slice(0,50)+(tc.is_primary?" ✓":"")+" ("+tc.share_of_journal+"%)"):("—");
    const cls=r.out_of_scope_pct>=20?"hi":r.out_of_scope_pct<10?"lo":"";
    const tr=document.createElement("tr");
    tr.innerHTML="<td><b>"+r.name+"</b></td>"
      +"<td class='num'>"+r.articles.toLocaleString()+"</td>"
      +"<td class='num'>"+r.n_primary_clusters+" <span style='color:#8893a6'>("+( r.primary_coverage_pct||0).toFixed(0)+"% cov)</span></td>"
      +"<td class='num'>"+r.out_of_scope.toLocaleString()+"</td>"
      +"<td class='num "+cls+"'>"+r.out_of_scope_pct.toFixed(1)+"%</td>"
      +"<td class='muted'>"+lbl+"</td>";
    tb1.appendChild(tr);
  });

  /* ── Community table ── */
  const tb2=document.querySelector("#tblComm tbody");
  C.slice(0,20).forEach(c=>{
    const topJ=(c.top_journals||[]).map(j=>j.name.slice(0,22)+" ("+j.pct+"%)").join(", ");
    const tr=document.createElement("tr");
    tr.innerHTML="<td><b>"+(c.label||("C"+c.id)).slice(0,55)+"</b></td>"
      +"<td class='num'>"+c.size.toLocaleString()+"</td>"
      +"<td class='num'>"+c.frontiers_pct.toFixed(1)+"%</td>"
      +"<td>"+c.dominant_journal.slice(0,35)+" <span class='muted'>("+c.dominant_pct+"%)</span></td>"
      +"<td class='muted'>"+topJ+"</td>";
    tb2.appendChild(tr);
  });

  /* ── Scatter — one bubble per community ── */
  const commLabels={};
  C.forEach(c=>{ commLabels[c.id]=c.label||("Community "+c.id); });

  J.forEach((j,jIdx)=>{
    const scatter=j.scatter||[];
    if (!scatter.length) return;

    const primaryIds=new Set((j.top_communities||[]).filter(c=>c.is_primary).map(c=>c.comm_id));

    // Group articles by community, compute centroid
    const byCom={};
    scatter.forEach(p=>{ (byCom[p.c]=byCom[p.c]||[]).push(p); });

    const inX=[],inY=[],inSz=[],inLbl=[],inN=[];
    const outX=[],outY=[],outSz=[],outLbl=[],outN=[];
    const allN=[];

    Object.keys(byCom).forEach(cid=>{
      const pts=byCom[cid], n=pts.length;
      const cx=pts.reduce((s,p)=>s+p.x,0)/n;
      const cy=pts.reduce((s,p)=>s+p.y,0)/n;
      const lbl=commLabels[cid]||("Community "+cid);
      allN.push(n);
      if (primaryIds.has(parseInt(cid))) {
        inX.push(cx);inY.push(cy);inSz.push(n);inLbl.push(lbl);inN.push(n);
      } else {
        outX.push(cx);outY.push(cy);outSz.push(n);outLbl.push(lbl);outN.push(n);
      }
    });

    const maxN=Math.max(...allN,1);
    const sz=n=>Math.max(20, Math.sqrt(n/maxN)*120);

    const mkT=(x,y,sizes,labels,counts,color,name)=>({
      type:"scatter", mode:"markers", name,
      x,y, text:labels, customdata:counts,
      marker:{
        size:sizes.map(sz), sizemode:"diameter",
        color, opacity:0.55,
        line:{color:"rgba(255,255,255,0.7)",width:1.5}
      },
      hovertemplate:"<b>%{text}</b><br>Articles: %{customdata:,}<br>"+name+"<extra></extra>"
    });

    const traces=[];
    if (inX.length)  traces.push(mkT(inX, inY, inSz, inLbl, inN,  "#1f8a4c","In scope"));
    if (outX.length) traces.push(mkT(outX,outY,outSz,outLbl,outN,"#c93030","Out of scope"));

    const card=document.createElement("div");
    card.className="card";
    card.style.marginBottom="12px";
    card.innerHTML='<h2>'+j.name
      +' <span style="color:#8893a6;font-weight:400;font-size:13px;">— '
      +scatter.length.toLocaleString()+' papers · '
      +j.out_of_scope_pct.toFixed(1)+'% out of scope</span></h2>'
      +'<div id="scatter'+jIdx+'" class="plot scatter"></div>';
    document.getElementById("scatterGrid").appendChild(card);

    Plotly.newPlot("scatter"+jIdx, traces, ext(BASE,{
      font:ext(FONT,{size:11}),
      xaxis:{showgrid:false,zeroline:false,showticklabels:false,showline:false},
      yaxis:{showgrid:false,zeroline:false,showticklabels:false,showline:false},
      legend:{orientation:"h",y:-0.04,font:{size:11}},
      margin:{l:10,r:10,t:10,b:50},
      hovermode:"closest"
    }), CFG);
  });

})();
