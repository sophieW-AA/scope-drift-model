"""
HTML Dashboard Generation for Scope Drift Analysis
===================================================
Generates an interactive Plotly-based HTML dashboard for visualizing
scope drift results from the global citation network analysis.
"""

import json


def write_dashboard_html(path: str, payload: dict) -> None:
    """
    Write an interactive HTML dashboard with scope drift analysis results.
    
    Args:
        path: Output file path for the HTML dashboard
        payload: Dictionary containing analysis results with keys:
            - meta: Analysis metadata (network_type, year_range, etc.)
            - journals: List of journal-level results
            - communities: List of community summaries
    """
    import numpy as np
    
    def _json_default(obj):
        """Handle numpy types for JSON serialization."""
        if isinstance(obj, (np.integer, np.int64, np.int32)):
            return int(obj)
        if isinstance(obj, (np.floating, np.float64, np.float32)):
            return float(obj)
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        raise TypeError(f"Object of type {type(obj).__name__} is not JSON serializable")
    
    blob = json.dumps(payload, indent=2, ensure_ascii=True, default=_json_default).replace("</", "<\\/")
    
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8" />
<meta name="viewport" content="width=device-width, initial-scale=1" />
<title>Scope Drift — Global Network Analysis</title>
<script src="https://cdn.plot.ly/plotly-2.35.2.min.js"></script>
<style>
  body {{ font-family: system-ui, sans-serif; margin: 0; background: #0f172a; color: #e2e8f0; }}
  header {{ padding: 20px 24px; border-bottom: 1px solid #334155; }}
  h1 {{ font-size: 1.35rem; margin: 0 0 6px; }}
  .sub {{ color: #94a3b8; font-size: 0.85rem; max-width: 1000px; line-height: 1.45; }}
  
  /* Tab navigation */
  .tab-nav {{ display: flex; gap: 4px; padding: 16px 24px 0; background: #0f172a; }}
  .tab-btn {{ padding: 10px 20px; border: none; background: #1e293b; color: #94a3b8; cursor: pointer; border-radius: 8px 8px 0 0; font-size: 0.9rem; transition: all 0.2s; }}
  .tab-btn:hover {{ background: #334155; color: #e2e8f0; }}
  .tab-btn.active {{ background: #334155; color: #f8fafc; font-weight: 600; }}
  .tab-content {{ display: none; }}
  .tab-content.active {{ display: block; }}
  
  main {{ padding: 16px 24px 40px; }}
  .grid {{ display: grid; gap: 18px; grid-template-columns: 1fr 1fr; max-width: 1400px; }}
  @media (max-width: 1000px) {{ .grid {{ grid-template-columns: 1fr; }} }}
  .card {{ background: #1e293b; border-radius: 10px; padding: 14px 16px; border: 1px solid #334155; }}
  .card h2 {{ font-size: 0.95rem; margin: 0 0 10px; color: #f8fafc; }}
  .plot {{ height: 420px; }}
  .plot.tall {{ height: 480px; }}
  .plot.scatter {{ height: 550px; }}
  table {{ width: 100%; border-collapse: collapse; font-size: 0.8rem; margin-top: 10px; }}
  th, td {{ text-align: left; padding: 6px 8px; border-bottom: 1px solid #334155; }}
  th {{ color: #94a3b8; font-weight: 600; }}
  .small {{ font-size: 0.75rem; color: #94a3b8; }}
  
  /* Scatter page layout */
  .scatter-grid {{ display: grid; gap: 18px; grid-template-columns: repeat(auto-fit, minmax(600px, 1fr)); max-width: 1800px; }}
  .legend-note {{ font-size: 0.8rem; color: #94a3b8; margin-bottom: 16px; padding: 10px 14px; background: #1e293b; border-radius: 8px; border-left: 3px solid #f97316; max-width: 1000px; }}
  .legend-note strong {{ color: #f8fafc; }}
</style>
</head>
<body>
<header>
  <h1>Scope Drift — Global Citation Network</h1>
  <p class="sub" id="metaLine"></p>
  <p class="sub" id="ruleLine"></p>
</header>

<nav class="tab-nav">
  <button class="tab-btn active" data-tab="overview">Overview</button>
  <button class="tab-btn" data-tab="scatter">Network Maps</button>
</nav>

<div id="tab-overview" class="tab-content active">
<main>
  <div class="grid">
    <div class="card" style="grid-column: 1 / -1;">
      <h2>Out-of-scope % by journal (global network)</h2>
      <div id="barOOS" class="plot"></div>
    </div>
    <div class="card" style="grid-column: 1 / -1;">
      <h2>Out-of-scope % by publication year</h2>
      <div id="barOOSYear" class="plot tall"></div>
    </div>
    <div class="card" style="grid-column: 1 / -1;">
      <h2>Top communities (by size)</h2>
      <div id="barComm" class="plot tall"></div>
    </div>
  </div>
  <div class="card" style="max-width:1400px;margin-top:18px;">
    <h2>Journal summary</h2>
    <table id="tblJournal"><thead><tr>
      <th>Journal</th><th>Articles</th><th>Primary clusters</th><th>Out-of-scope</th><th>OOS %</th><th>Top community</th>
    </tr></thead><tbody></tbody></table>
  </div>
  <div class="card" style="max-width:1400px;margin-top:18px;">
    <h2>Community composition</h2>
    <table id="tblComm"><thead><tr>
      <th>Theme</th><th>Size</th><th>Frontiers %</th><th>Dominant journal</th><th>Top journals</th>
    </tr></thead><tbody></tbody></table>
  </div>
</main>
</div>

<div id="tab-scatter" class="tab-content">
<main>
  <div class="legend-note">
    <strong>Reading these plots:</strong> Each dot is a publication. 
    <strong style="color:#22c55e;">Green rings = primary clusters</strong> (in-scope), 
    <strong style="color:#ef4444;">Red rings = non-primary clusters</strong> (out-of-scope). 
    Papers are positioned by their citation relationships — nearby papers cite similar literature.
    Hover for paper titles and community labels.
  </div>
  <div class="scatter-grid" id="scatterGrid"></div>
</main>
</div>

<script>
const DATA = {blob};
(function () {{
  const M = DATA.meta || {{}};
  document.getElementById("metaLine").textContent =
    "Network type: " + (M.network_type || "unknown") +
    " · Years " + (M.year_range || []).join("–") +
    " · Primary cluster coverage: " + ((M.primary_cluster_coverage || 0.8) * 100).toFixed(0) + "%";
  document.getElementById("ruleLine").textContent = M.oos_rule || "";

  const J = DATA.journals || [];
  const C = DATA.communities || [];
  
  // Build community label lookup
  const commLabels = {{}};
  C.forEach(c => {{ commLabels[c.id] = c.label || ("Community " + c.id); }});

  // Tab switching
  document.querySelectorAll(".tab-btn").forEach(btn => {{
    btn.addEventListener("click", () => {{
      document.querySelectorAll(".tab-btn").forEach(b => b.classList.remove("active"));
      document.querySelectorAll(".tab-content").forEach(c => c.classList.remove("active"));
      btn.classList.add("active");
      document.getElementById("tab-" + btn.dataset.tab).classList.add("active");
      
      // Trigger Plotly resize when switching tabs
      window.dispatchEvent(new Event("resize"));
    }});
  }});

  // OOS bar chart
  Plotly.newPlot("barOOS", [{{
    type: "bar",
    x: J.map(r => r.name),
    y: J.map(r => r.out_of_scope_pct),
    text: J.map(r => r.articles + " articles"),
    marker: {{ color: "#f97316" }},
    hovertemplate: "%{{x}}<br>OOS %: %{{y:.1f}}<br>%{{text}}<extra></extra>"
  }}], {{
    paper_bgcolor: "#1e293b", plot_bgcolor: "#0f172a",
    font: {{ color: "#e2e8f0" }},
    xaxis: {{ tickangle: -25 }},
    yaxis: {{ title: "Out-of-scope %", gridcolor: "#334155", range: [0, 100] }},
    margin: {{ t: 20, l: 48, r: 16, b: 100 }}
  }}, {{ responsive: true }});

  // OOS by year
  const years = M.oos_per_year_years || [];
  if (years.length) {{
    const traces = J.map(r => ({{
      type: "bar",
      name: r.name,
      x: years,
      y: years.map(y => {{
        const row = (r.oos_by_year || []).find(o => o.year === y);
        return row && row.articles ? row.out_of_scope_pct : null;
      }}),
      hovertemplate: "<b>%{{fullData.name}}</b><br>Year %{{x}}<br>OOS %: %{{y:.1f}}<extra></extra>"
    }}));
    Plotly.newPlot("barOOSYear", traces, {{
      paper_bgcolor: "#1e293b", plot_bgcolor: "#0f172a",
      font: {{ color: "#e2e8f0" }},
      barmode: "group",
      xaxis: {{ title: "Publication year", gridcolor: "#334155", dtick: 1 }},
      yaxis: {{ title: "Out-of-scope %", gridcolor: "#334155", range: [0, 100] }},
      legend: {{ orientation: "h", y: -0.25 }},
      margin: {{ t: 20, l: 48, r: 16, b: 120 }}
    }}, {{ responsive: true }});
  }}

  // Community bar chart
  Plotly.newPlot("barComm", [{{
    type: "bar",
    x: C.map(c => (c.label || "C" + c.id).slice(0, 35)),
    y: C.map(c => c.size),
    text: C.map(c => c.dominant_journal.slice(0, 30)),
    marker: {{ color: C.map(c => c.frontiers_pct), colorscale: "Viridis", showscale: true, colorbar: {{ title: "Frontiers %" }} }},
    hovertemplate: "<b>%{{x}}</b><br>Size: %{{y}}<br>Dominant journal: %{{text}}<extra></extra>"
  }}], {{
    paper_bgcolor: "#1e293b", plot_bgcolor: "#0f172a",
    font: {{ color: "#e2e8f0" }},
    xaxis: {{ tickangle: -45 }},
    yaxis: {{ title: "Community size", gridcolor: "#334155", type: "log" }},
    margin: {{ t: 20, l: 56, r: 16, b: 100 }}
  }}, {{ responsive: true }});

  // Journal table
  const tb1 = document.querySelector("#tblJournal tbody");
  J.forEach(r => {{
    const topC = (r.top_communities || [])[0];
    const topLabel = topC ? ((topC.label || "C" + topC.comm_id).slice(0, 40) + (topC.is_primary ? " ✓" : "") + " (" + topC.share_of_journal + "%)") : "—";
    const primStr = r.n_primary_clusters + " (" + (r.primary_coverage_pct || 0).toFixed(0) + "% coverage)";
    const tr = document.createElement("tr");
    tr.innerHTML = "<td>" + r.name + "</td><td>" + r.articles + "</td><td>" + primStr +
      "</td><td>" + r.out_of_scope + "</td><td>" + r.out_of_scope_pct.toFixed(1) + "</td><td>" + topLabel + "</td>";
    tb1.appendChild(tr);
  }});

  // Community table
  const tb2 = document.querySelector("#tblComm tbody");
  C.slice(0, 20).forEach(c => {{
    const topJ = (c.top_journals || []).map(j => j.name.slice(0, 25) + " (" + j.pct + "%)").join(", ");
    const tr = document.createElement("tr");
    tr.innerHTML = "<td>" + (c.label || "C" + c.id).slice(0, 45) + "</td><td>" + c.size + "</td><td>" + c.frontiers_pct.toFixed(1) +
      "</td><td>" + c.dominant_journal.slice(0, 35) + " (" + c.dominant_pct + "%)</td><td class='small'>" + topJ + "</td>";
    tb2.appendChild(tr);
  }});
  
  // Scatter plots for each journal
  const scatterGrid = document.getElementById("scatterGrid");
  const colors = ["#06b6d4", "#8b5cf6", "#f59e0b", "#ec4899", "#10b981", "#6366f1", "#f97316", "#14b8a6", "#a855f7", "#eab308"];
  
  J.forEach((j, jIdx) => {{
    const scatter = j.scatter || [];
    if (!scatter.length) return;
    
    // Get primary cluster IDs for this journal
    const primaryIds = new Set((j.top_communities || []).filter(c => c.is_primary).map(c => c.comm_id));
    
    // Group by community (now only 100 communities after merging)
    const byCommunity = {{}};
    scatter.forEach(p => {{
      if (!byCommunity[p.c]) byCommunity[p.c] = [];
      byCommunity[p.c].push(p);
    }});
    
    // Sort communities by size
    const sortedComms = Object.keys(byCommunity)
      .sort((a, b) => byCommunity[b].length - byCommunity[a].length);
    
    // Create traces for each community
    const traces = [];
    sortedComms.forEach((cid, idx) => {{
      const papers = byCommunity[cid];
      const isPrimary = primaryIds.has(parseInt(cid));
      const label = commLabels[cid] || ("Community " + cid);
      const ringColor = isPrimary ? "#22c55e" : "#ef4444";
      const fillColor = colors[idx % colors.length];
      
      traces.push({{
        type: "scatter",
        mode: "markers",
        name: label.slice(0, 25) + (isPrimary ? " ✓" : " ⚠"),
        x: papers.map(p => p.x),
        y: papers.map(p => p.y),
        text: papers.map(p => p.t || "Untitled"),
        customdata: papers.map(p => [label, p.yr, isPrimary ? "In scope" : "Out of scope"]),
        marker: {{
          size: 8,
          color: fillColor,
          opacity: 0.7,
          line: {{ color: ringColor, width: 2 }}
        }},
        hovertemplate: "<b>%{{text}}</b><br>Community: %{{customdata[0]}}<br>Year: %{{customdata[1]}}<br>%{{customdata[2]}}<extra></extra>"
      }});
    }});
    
    // Create card for this journal
    const card = document.createElement("div");
    card.className = "card";
    card.innerHTML = '<h2>' + j.name + ' — ' + scatter.length + ' papers (' + j.out_of_scope_pct.toFixed(1) + '% OOS)</h2><div id="scatter' + jIdx + '" class="plot scatter"></div>';
    scatterGrid.appendChild(card);
    
    Plotly.newPlot("scatter" + jIdx, traces, {{
      paper_bgcolor: "#1e293b",
      plot_bgcolor: "#0f172a",
      font: {{ color: "#e2e8f0", size: 10 }},
      xaxis: {{ showgrid: false, zeroline: false, showticklabels: false }},
      yaxis: {{ showgrid: false, zeroline: false, showticklabels: false }},
      legend: {{ orientation: "h", y: -0.08, font: {{ size: 9 }}, itemwidth: 30 }},
      margin: {{ t: 10, l: 10, r: 10, b: 80 }},
      hovermode: "closest"
    }}, {{ responsive: true }});
  }});
}})();
</script>
</body>
</html>"""
    
    with open(path, "w", encoding="utf-8") as f:
        f.write(html)
