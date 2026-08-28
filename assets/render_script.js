(function () {
  const M = DATA.meta || {};
  const J = DATA.journals || [];
  const C = DATA.communities || [];

  /* ── Latest year (headline OOS / article figures) ── */
  const yearList = (M.oos_per_year_years || []).map(Number).filter(Boolean).sort((a,b)=>a-b);
  const latestYear = yearList.length
    ? yearList[yearList.length - 1]
    : ((M.year_range || [])[1] || null);

  function oosRowForYear(journal, year) {
    return (journal.oos_by_year || []).find(o => Number(o.year) === Number(year)) || null;
  }

  let latestArticles = 0;
  let latestOOS = 0;
  J.forEach(j => {
    const row = latestYear != null ? oosRowForYear(j, latestYear) : null;
    if (!row) return;
    latestArticles += row.articles || 0;
    latestOOS += row.out_of_scope || 0;
  });
  const latestOOSPct = latestArticles ? (latestOOS / latestArticles * 100) : 0;
  const worstLatest = J.slice()
    .map(j => {
      const row = latestYear != null ? oosRowForYear(j, latestYear) : null;
      return {
        name: j.name,
        pct: row && row.articles ? row.out_of_scope_pct : null,
        articles: row ? row.articles : 0,
      };
    })
    .filter(r => r.pct != null)
    .sort((a,b)=>b.pct - a.pct)[0];

  /* ── Timestamp & scope ── */
  const now = new Date();
  const p = n => String(n).padStart(2,"0");
  document.getElementById("snapStamp").textContent =
    now.getUTCFullYear()+"-"+p(now.getUTCMonth()+1)+"-"+p(now.getUTCDate())
    +" "+p(now.getUTCHours())+":"+p(now.getUTCMinutes())+" UTC";
  const period = (M.year_range||[]).join("–");
  document.getElementById("scopeDesc").textContent =
    period+", "+J.length+" journals, "
    +((M.primary_cluster_coverage||0.8)*100).toFixed(0)+"% primary cluster coverage"
    + (latestYear != null ? " · headline OOS figures for "+latestYear : "");

  /* ── Footer ── */
  const totalPapers = J.reduce((s,r)=>s+(r.articles||0),0);
  document.getElementById("ftYears").textContent    = period;
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

  /* ── KPI strip (OOS / articles = most recent year) ── */
  const yearLabel = latestYear != null ? String(latestYear) : "latest year";
  [
    { label:"Journals analysed",   value:J.length,                         sub:"Frontiers journals in scope" },
    { label:"Articles ("+yearLabel+")", value:latestArticles.toLocaleString(), sub:"of "+totalPapers.toLocaleString()+" in "+(period||"all years") },
    { label:"Out of scope ("+yearLabel+")", value:latestOOS.toLocaleString(), sub:latestOOSPct.toFixed(1)+"% in "+yearLabel },
    { label:"Communities",         value:C.length,                         sub:"themes in global network" },
    { label:"Highest OOS ("+yearLabel+")", value:worstLatest?worstLatest.pct.toFixed(1)+"%":"—", sub:worstLatest?worstLatest.name:"" }
  ].forEach(k=>{
    const el=document.createElement("div");
    el.className="kpi";
    el.innerHTML='<div class="kpi-label">'+k.label+'</div>'
      +'<div class="kpi-value">'+k.value+'</div>'
      +'<div class="kpi-sub">'+k.sub+'</div>';
    document.getElementById("kpiRow").appendChild(el);
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

  /* ── Journal table (OOS columns = most recent year; all-years in muted note) ── */
  const tb1=document.querySelector("#tblJournal tbody");
  if (tb1) {
    const ranked = J.slice().map(r => {
      const row = latestYear != null ? oosRowForYear(r, latestYear) : null;
      return {
        r,
        latestPct: row && row.articles ? row.out_of_scope_pct : null,
        latestOOS: row ? row.out_of_scope : 0,
        latestN: row ? row.articles : 0,
      };
    }).sort((a,b)=>(b.latestPct||0)-(a.latestPct||0));

    ranked.forEach(({r, latestPct, latestOOS, latestN}) => {
      const tc=(r.top_communities||[])[0];
      const lbl=tc?((tc.label||("C"+tc.comm_id)).slice(0,50)+(tc.is_primary?" ✓":"")+" ("+tc.share_of_journal+"%)"):("—");
      const pct = latestPct != null ? latestPct : r.out_of_scope_pct;
      const cls=pct>=20?"hi":pct<10?"lo":"";
      const tr=document.createElement("tr");
      tr.innerHTML="<td><b>"+r.name+"</b></td>"
        +"<td class='num'>"+latestN.toLocaleString()
        +"<div class='muted' style='font-size:0.75em'>"+r.articles.toLocaleString()+" all years</div></td>"
        +"<td class='num'>"+r.n_primary_clusters+" <span style='color:#8893a6'>("+( r.primary_coverage_pct||0).toFixed(0)+"% cov)</span></td>"
        +"<td class='num'>"+latestOOS.toLocaleString()
        +"<div class='muted' style='font-size:0.75em'>"+r.out_of_scope.toLocaleString()+" all years</div></td>"
        +"<td class='num "+cls+"'>"+(latestPct!=null?latestPct.toFixed(1):r.out_of_scope_pct.toFixed(1))+"%"
        +"<div class='muted' style='font-size:0.75em'>"+r.out_of_scope_pct.toFixed(1)+"% all years</div></td>"
        +"<td class='muted'>"+lbl+"</td>";
      tb1.appendChild(tr);
    });

    // Clarify table headers for latest-year figures
    const ths = document.querySelectorAll("#tblJournal thead th");
    if (ths.length >= 5 && latestYear != null) {
      ths[1].textContent = "Articles ("+latestYear+")";
      ths[3].textContent = "Out of Scope ("+latestYear+")";
      ths[4].textContent = "OOS % ("+latestYear+")";
    }
  }

  /* ── Community table ── */
  const tb2=document.querySelector("#tblComm tbody");
  if (tb2) {
    const esc=(s)=>String(s||"")
      .replace(/&/g,"&amp;").replace(/</g,"&lt;").replace(/>/g,"&gt;")
      .replace(/"/g,"&quot;");
    C.slice(0,20).forEach(c=>{
      const theme=esc((c.label||("C"+c.id)).slice(0,55));
      const longLab=esc(c.long_label||"");
      const desc=esc(c.description||c.summary||c.long_label||"");
      const kws=(c.keywords||[]).map(k=>esc(k)).filter(Boolean);
      const kwHtml=kws.length
        ? "<div class='muted' style='margin-top:4px;font-size:0.85em'><b>Keywords:</b> "+kws.join("; ")+"</div>"
        : "";
      const longHtml=(longLab && longLab!==theme)
        ? "<div class='muted' style='font-size:0.85em;margin-top:2px'>"+longLab+"</div>"
        : "";
      const tr=document.createElement("tr");
      tr.innerHTML="<td><b>"+theme+"</b>"+longHtml+"</td>"
        +"<td class='num'>"+c.size.toLocaleString()+"</td>"
        +"<td style='max-width:520px;white-space:normal;line-height:1.35'>"+desc+kwHtml+"</td>";
      tb2.appendChild(tr);
    });
  }

})();
