;
const J = DATA.journals;
const MACROS = DATA.macros;
const macroColor = DATA.macroColor;
const shown = {};
MACROS.forEach(m => { shown[m.id] = true; });
let colorMode = "macro";
let query = "";
let selected = null;

const statsEl = document.getElementById("stats");
const detail = document.getElementById("detail");

const YS = j => j.ys, KC = c => c.k, KY = c => c.ks, NO = j => j.nOos, PC = j => j.oosPct;
const RULE_NOTE = () => "scope: stored call from BigQuery";
function nv(j) { return yearIdx > 0 ? j.ys[yearIdx - 1].n : j.n; }
function sizePx(n, maxN) {
  if (n <= 0) return 0;
  return Math.max(9, Math.sqrt(n / Math.max(maxN, 1)) * (selected == null ? 72 : 86));
}

let spot = null;
function matches(j) {
  return true;
  if (!query) return true;
  return j.short.toLowerCase().indexOf(query) >= 0
    || j.name.toLowerCase().indexOf(query) >= 0
    || j.mesoLabel.toLowerCase().indexOf(query) >= 0
    || j.macroLabel.toLowerCase().indexOf(query) >= 0;
}

function frame() {
  const near = new Set();
  if (selected != null) {
    near.add(selected);
    (J[selected].near || []).forEach(item => { if (item.id != null) near.add(item.id); });
  }
  let maxN = 1;
  const visible = [];
  J.forEach(j => {
    if (!shown[j.macro] || nv(j) <= 0) return;
    if (nv(j) > maxN) maxN = nv(j);
    visible.push(nv(j));
  });
  if (yearIdx > 0) maxN = YMAX;
  visible.sort((a, b) => b - a);
  const labelCut = visible[11] || 0;
  const sp = spot != null ? J[spot] : null;
  const R = 0.11;
  const inWin = j => sp && Math.abs(j.y - sp.y) < R && Math.abs(j.x - sp.x) < R;
  const x = [], y = [], sizes = [], colors = [], text = [], opacity = [], line = [], custom = [];
  let shownCount = 0;
  J.forEach(j => {
    const on = !!shown[j.macro] && matches(j) && nv(j) > 0;
    const focus = selected == null ? (sp ? inWin(j) || j.id === spot : true) : near.has(j.id);
    if (on) shownCount += 1;
    x.push(j.y);
    y.push(-j.x);
    sizes.push(on ? sizePx(nv(j), maxN) : 0);
    colors.push(colorMode === "meso" ? j.mesoColor : macroColor[String(j.macro)]);
    const named = on && (sp ? (inWin(j) || j.id === spot) : (nv(j) >= labelCut || near.has(j.id)));
    text.push(named ? j.short : "");
    opacity.push(!on ? 0 : (j.id === spot ? 1 : (focus ? 0.8 : (sp ? 0.18 : 0.1))));
    line.push(j.id === selected || j.id === spot ? 3 : 1);
    custom.push(j.id);
  });
  return {
    shownCount,
    trace: {
      type: "scatter",
      mode: "markers+text",
      x, y, text,
      customdata: custom,
      textposition: "top center",
      textfont: { size: 10, color: "#1a1f36" },
      hovertext: J.map(j => "<b>" + j.short + "</b><br>Main topic: " + j.mesoLabel
        + " (" + j.mesoShare + "% of its papers)<br>Broad field: " + j.macroLabel
        + "<br>" + nv(j).toLocaleString() + " papers" + (yearIdx ? " in " + YEARS[yearIdx - 1] + " · " + (nv(j) ? (100 * YS(j)[yearIdx - 1].o / nv(j)).toFixed(1) : "0.0") + "% outside the core" : (" · " + PC(j) + "% outside the core")) + "<br>Similar journals (estimate): "
        + (j.near || []).slice(0, 3).map(n => n.name).join(", ")),
      hoverinfo: "text",
      marker: {
        size: sizes,
        sizemode: "diameter",
        color: colors,
        opacity,
        line: { color: J.map(j => j.id === spot ? "#1a1f36" : "rgba(255,255,255,0.9)"), width: line }
      }
    }
  };
}

const layout = {
  paper_bgcolor: "#ffffff",
  plot_bgcolor: "#ffffff",
  font: { family: '-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,sans-serif', color: "#1a1f36", size: 11 },
  autosize: true,
  xaxis: { showgrid: false, zeroline: false, showticklabels: false, showline: false },
  yaxis: { showgrid: false, zeroline: false, showticklabels: false, showline: false, scaleanchor: "x", scaleratio: 1 },
  margin: { l: 8, r: 8, t: 8, b: 8 },
  hovermode: "closest",
  showlegend: false
};
const config = { responsive: true, displayModeBar: false };

function applyZoom() {
  if (spot != null) {
    const s = J[spot], R = 0.11;
    layout.xaxis.range = [s.y - R, s.y + R];
    layout.yaxis.range = [-s.x - R, -s.x + R];
    layout.xaxis.autorange = false; layout.yaxis.autorange = false;
  } else {
    delete layout.xaxis.range; delete layout.yaxis.range;
    layout.xaxis.autorange = true; layout.yaxis.autorange = true;
  }
  layout.uirevision = "z" + (spot == null ? "all" : spot);
}
function draw() {
  applyZoom();
  const f = frame();
  Plotly.react("plot", [f.trace], layout, config);
  const mode = colorMode === "meso" ? "meso" : "macro";
  statsEl.textContent = f.shownCount.toLocaleString() + " journals" + (yearIdx ? " with papers in " + YEARS[yearIdx - 1] : "") + " · colour = main broad field · search to find a journal";
}

const COMM = {};
(DATA.comms || []).forEach(c => { COMM[c.id] = c; });
const SCOPE = {
  p: { color: "#0072B2", name: "Core" },
  b: { color: "#56B4E9", name: "Borderline" },
  o: { color: "#D55E00", name: "Outside the core" }
};

const YEARS = DATA.years || [];
J.forEach(j => {
  j.ys = YEARS.map(y => { const s = (j.sy || {})[String(y)] || { a: 0, o: 0, b: 0 }; return { n: s.a, o: s.o, b: s.b }; });
});
function smallY(j, y) { const s = (j.sy || {})[String(y)]; if (!s || !s.a) return false; const mx = Math.max.apply(null, YEARS.map(v => ((j.sy || {})[String(v)] || {}).a || 0)); return s.a < 0.5 * mx; }
function smallNote(j) { const sm = YEARS.filter(y => smallY(j, y)); return sm.length ? "&#9888; " + (sm.length > 1 ? sm.slice(0, -1).join(", ") + " and " + sm[sm.length - 1] + " have" : sm[0] + " has") + " far fewer papers than the busiest year, so changes in " + (sm.length > 1 ? "those years" : "that year") + " look bigger than they are." : ""; }
function headline(j) {
  const ys = YEARS.filter(y => ((j.sy || {})[String(y)] || {}).p != null), f = (j.sy || {})[String(ys[0])], l = (j.sy || {})[String(ys[ys.length - 1])];
  let s = "<b>" + Number(j.oosPct).toFixed(1) + "% of its papers sit outside the journal's core</b>";
  if (ys.length > 1) { const d = l.p - f.p; s += Math.abs(d) < 0.5 ? ", about the same as in " + ys[0] + " (" + f.p.toFixed(1) + "% then, " + l.p.toFixed(1) + "% in " + ys[ys.length - 1] + ")." : ", " + (d < 0 ? "down" : "up") + " from " + f.p.toFixed(1) + "% in " + ys[0] + " to " + l.p.toFixed(1) + "% in " + ys[ys.length - 1] + "."; }
  else s += ".";
  if (ys.length > 1 && smallY(j, ys[ys.length - 1])) s += " <span class='warn'>&#9888; " + ys[ys.length - 1] + " has far fewer papers, so treat the latest figure with care.</span>";
  return s;
}
(function () { const fd = d => { const p = String(d || "").split("-"); return p.length === 3 ? Number(p[2]) + " " + ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"][Number(p[1]) - 1] + " " + p[0] : String(d || "n/a"); };
  const rd = String(DATA.cfg.runDate || ""); const el = document.getElementById("srcline");
  if (el) el.textContent = "Data: citation run " + DATA.run + " (dated " + fd(rd.slice(0, 4) + "-" + rd.slice(4, 6) + "-" + rd.slice(6, 8)) + "), BigQuery. Core results generated " + fd(DATA.cfg.generated) + ". Page built " + fd(DATA.cfg.built) + ". Topic layout and similar journals are estimates made for this page. See Data & queries for every query used."; })();
let YMAX = 1; J.forEach(j => j.ys.forEach(s => { if (s.n > YMAX) YMAX = s.n; }));
let commColor = "scope", yearIdx = 0, playTimer = null;
const MACRO_NAME = {}; MACROS.forEach(m => { MACRO_NAME[m.id] = m.label; });
function curYear() { return yearIdx > 0 ? YEARS[yearIdx - 1] : null; }

function drawCommunities(j) {
  const yr = curYear();
  const all = (j.comms || []).filter(c => COMM[c.id]);
  const kAt = c => yr == null ? KC(c) : ({ p: 'p', o: 'o', b: 'b' }[(KY(c) || '')[yearIdx - 1]] || KC(c));
  const rows = all.map(c => Object.assign({}, c, { m: yr == null ? c.n : ((c.y || {})[yr] || 0), k: kAt(c) })).filter(c => c.m > 0);
  let peak = 1;
  all.forEach(c => { if (yr == null) peak = Math.max(peak, c.n); else Object.keys(c.y || {}).forEach(k => { peak = Math.max(peak, c.y[k]); }); });
  const total = rows.reduce((s, c) => s + c.m, 0);
  const mk = (name, color, subset, lines) => ({
    type: "scatter", mode: "markers+text", name: name,
    x: subset.map(c => COMM[c.id].y), y: subset.map(c => -COMM[c.id].x),
    text: subset.map(c => c.m >= peak * 0.14 ? COMM[c.id].label : ""),
    textposition: "top center", textfont: { size: 11, color: "#1a1f36" },
    hovertext: subset.map(c => "<b>" + COMM[c.id].label + "</b><br>" + c.m.toLocaleString() + " papers" + (yr == null ? "" : " in " + yr)
      + "<br>Broad field: " + (MACRO_NAME[COMM[c.id].macro] || "n/a") + "<br>" + SCOPE[c.k].name),
    hoverinfo: "text",
    marker: { size: subset.map(c => Math.max(10, Math.sqrt(c.m / peak) * 120)), sizemode: "diameter", color: color,
      opacity: 0.62,
      line: { color: lines ? subset.map(c => c.k === "p" ? "rgba(255,255,255,0.85)" : SCOPE[c.k].color) : "rgba(255,255,255,0.85)",
              width: lines ? subset.map(c => c.k === "p" ? 1.2 : 3.5) : 1.4 }
    }
  });
  const DR = yr == null ? { stay: { n: "In the core before and now", c: "#1f8a4c" }, joined: { n: "Joined the core", c: "#0b6bcb" }, left: { n: "Left the core", c: "#e8590c" }, never: { n: "Never in the core", c: "#9aa3b2" } }
    : { stay: { n: "In the core in " + yr, c: "#1f8a4c" }, joined: { n: "Joined the core in " + yr, c: "#0b6bcb" }, left: { n: "Left the core in " + yr, c: "#e8590c" }, never: { n: "Not in the core in " + yr, c: "#9aa3b2" } };
  const dk = yr == null ? (c => c.db && c.dc ? "stay" : (!c.db && c.dc ? "joined" : (c.db && !c.dc ? "left" : "never")))
    : (c => { const i = yearIdx - 1, now = (c.cy || "")[i] === "1", prev = i > 0 ? (c.cy || "")[i - 1] === "1" : now; return now ? (prev ? "stay" : "joined") : (prev ? "left" : "never"); });
  const totM = rows.reduce((s, c) => s + c.m, 0) || 1, tot0 = (j.comms || []).reduce((s, c) => s + ((c.y || {})[YEARS[0]] || 0), 0) || 1;
  let traces;
  if (commColor === "drift") {
    traces = ["stay", "joined", "left", "never"].map(k => { const sub = rows.filter(c => dk(c) === k), t = mk(DR[k].n + " (" + sub.length + ")", DR[k].c, sub, false);
      t.hovertext = sub.map(c => "<b>" + COMM[c.id].label + "</b><br>" + c.m.toLocaleString() + " papers" + (yr == null ? "" : " in " + yr) + " · " + (100 * c.m / totM).toFixed(1) + "% of the journal's papers" + (yr == null ? "" : " (" + YEARS[0] + ": " + (100 * (((c.y || {})[YEARS[0]]) || 0) / tot0).toFixed(1) + "%)") + "<br>" + DR[k].n + (yr == null ? " (stored baseline vs latest core)" : " (derived 80% core, compared with " + (yearIdx > 1 ? YEARS[yearIdx - 2] : "itself") + ")")); return t; });
  } else if (commColor === "scope") {
    traces = ["p", "b", "o"].map(k => mk(SCOPE[k].name, SCOPE[k].color, rows.filter(c => c.k === k), false));
  } else {
    const ids = Array.from(new Set(rows.map(c => COMM[c.id].macro)));
    ids.sort((a, b) => rows.filter(c => COMM[c.id].macro === b).reduce((s, c) => s + c.m, 0) - rows.filter(c => COMM[c.id].macro === a).reduce((s, c) => s + c.m, 0));
    traces = ids.map(id => mk(MACRO_NAME[id] || "Field " + id, macroColor[String(id)] || "#888", rows.filter(c => COMM[c.id].macro === id), false));
  }
  // invisible anchor so the axes do not jump between years
  traces.push({ type: "scatter", mode: "markers", x: all.map(c => COMM[c.id].y), y: all.map(c => -COMM[c.id].x), hoverinfo: "none", showlegend: false, marker: { size: 1, opacity: 0 } });
  const sT = yr == null ? { n: j.n, o: NO(j) } : YS(j)[yearIdx - 1];
  const note = (yr == null ? "All years" : String(yr)) + " · " + sT.n.toLocaleString() + " papers · " + (sT.n ? (100 * sT.o / sT.n).toFixed(1) : "0.0") + "% outside the core"
    + (yr != null && smallY(j, yr) ? " · \u26A0 far fewer papers than the busiest year, so changes look bigger" : "");
  Plotly.react("plot", traces, {
    paper_bgcolor: "#ffffff", plot_bgcolor: "#ffffff", font: layout.font, autosize: true, showlegend: true,
    legend: { orientation: "h", y: -0.06, font: { size: 12 } },
    margin: { l: 16, r: 16, t: 28, b: 48 }, hovermode: "closest",
    annotations: [{ text: note, xref: "paper", yref: "paper", x: 0, y: 1.02, xanchor: "left", yanchor: "bottom", showarrow: false, font: { size: 12, color: "#5f6b7c" } }],
    xaxis: { showgrid: false, zeroline: false, showticklabels: false, showline: false },
    yaxis: { showgrid: false, zeroline: false, showticklabels: false, showline: false, scaleanchor: "x", scaleratio: 1 },
    uirevision: "c" + j.id
  }, config);
}

function yearStats(j) {
  return YEARS.map((y, i) => ({ y: y, n: YS(j)[i].n, o: YS(j)[i].o, b: YS(j)[i].b }));
}
function renderYears(j) {
  let box = document.getElementById("yt");
  if (!box) { box = document.createElement("div"); box.id = "yt"; detail.appendChild(box); }
  const st = yearStats(j), cur = curYear(), maxN = Math.max.apply(null, st.map(s => s.n).concat([1]));
  box.innerHTML = "<h3>Share outside the core, by year</h3><div class='yt'>" + st.filter(s => s.n > 0).map(s => {
    const p = 100 * s.o / s.n, w = 100 * s.n / maxN;
    return "<div class='yr" + (s.y === cur ? " on" : "") + "' data-y='" + s.y + "'><span>" + s.y + (smallY(j, s.y) ? " &#9888;" : "") + "</span>"
      + "<span class='bar' title='" + s.n + " papers'><i style='width:" + (w * (1 - s.o / s.n)).toFixed(1) + "%;background:#0072B2'></i><i style='width:" + (w * s.o / s.n).toFixed(1) + "%;background:#D55E00'></i></span>"
      + "<span class='v'>" + p.toFixed(0) + "% · " + s.n + "</span></div>";
  }).join("") + "</div><p class='meta' style='margin-top:6px'>Bar length is papers that year. Orange is the share outside the core. &#9888; = far fewer papers than the busiest year, so the figure moves more easily.</p>";
  box.querySelectorAll(".yr").forEach(el => el.addEventListener("click", () => setYear(YEARS.indexOf(Number(el.dataset.y)) + 1)));
}
function setYear(i) {
  yearIdx = i;
  const s = document.getElementById("yearSlider"); s.value = i;
  document.getElementById("yearLab").textContent = i ? String(YEARS[i - 1]) : "All years";
  if (selected != null) { renderDetail(selected); drawCommunities(J[selected]); renderYears(J[selected]); }
  else { draw(); if (view === "market") renderMarket(); else if (spot != null) showSpot(spot); }
}
function setCommColor(m) {
  commColor = m;
  document.getElementById("cScope").classList.toggle("active", m === "scope");
  document.getElementById("cMacro").classList.toggle("active", m === "macro"); document.getElementById("cDrift").classList.toggle("active", m === "drift");
  if (selected != null) drawCommunities(J[selected]);
}
function stopPlay() { if (playTimer) { clearInterval(playTimer); playTimer = null; document.getElementById("yearPlay").innerHTML = "&#9654;"; } }
(function initCtl() {
  const s = document.getElementById("yearSlider"); s.max = YEARS.length;
  s.addEventListener("input", () => { stopPlay(); setYear(Number(s.value)); });
  document.getElementById("cScope").addEventListener("click", () => setCommColor("scope"));
  document.getElementById("cMacro").addEventListener("click", () => setCommColor("macro"));
  document.getElementById("yearPlay").addEventListener("click", () => {
    if (playTimer) { stopPlay(); return; }
    document.getElementById("yearPlay").innerHTML = "&#10074;&#10074;";
    if (yearIdx >= YEARS.length) setYear(0);
    playTimer = setInterval(() => { if (yearIdx >= YEARS.length) { stopPlay(); return; } setYear(yearIdx + 1); }, 900);
  });
})();

function setPanel(open) {
  detail.classList.toggle("collapsed", !open);
  document.getElementById("panelTab").hidden = open || (selected == null && spot == null);
  setTimeout(() => Plotly.Plots.resize("plot"), 280);
}
document.getElementById("panelTab").addEventListener("click", () => setPanel(true));
detail.addEventListener("transitionend", ev => { if (ev.propertyName === "width") Plotly.Plots.resize("plot"); });
function renderDetail(id) {
  setPanel(true);
  const j = J[id], yi = yearIdx, yr = curYear();
  const st = yi ? YS(j)[yi - 1] : { n: j.n, o: NO(j), b: j.nBord };
  const pct = st.n ? (100 * st.o / st.n).toFixed(1) : "0.0";
  const rows = (j.comms || []).map(c => ({ id: c.id, m: yi ? ((c.y || {})[yr] || 0) : c.n })).filter(c => c.m > 0).sort((a, b) => b.m - a.m);
  const tot = rows.reduce((s, c) => s + c.m, 0);
  const lab = id2 => (COMM[id2] ? COMM[id2].label : "Topic " + id2);
  const communities = rows.slice(0, yi ? 5 : 3).map(c =>
    "<li><span>" + lab(c.id) + "</span> <span class='share'>" + (100 * c.m / tot).toFixed(1) + "%</span></li>").join("");
  const near = (j.near || []).map(n => {
    const other = n.id == null;
    const tag = other ? " <span class='tag'>other publisher</span>" : "";
    return "<button type='button' class='near-btn' data-id='" + (other ? "" : n.id) + "'"
      + (other ? " disabled" : "") + "><span>" + n.name + tag + "</span><span class='share'>" + n.sim + "</span></button>";
  }).join("");
  const main = rows[0];
  detail.innerHTML =
    "<h2>" + j.short + (yr ? " <span class='share'>· " + yr + "</span>" : "") + "</h2>"
    + (st.n ? "<p class='meta'>" + st.n.toLocaleString() + " papers" + (yr ? " in " + yr : "") + " · "
      + pct + "% outside the core · " + st.b.toLocaleString() + " borderline papers" + (yi && smallY(j, yr) ? " · <span class='warn'>&#9888; fewer papers this year</span>" : "") + "</p>"
      : "<p class='meta'>No papers in " + yr + ".</p>")
    + "<p class='headline'>" + headline(j) + "</p>"
    + "<p style='margin:10px 0 4px'><button type='button' class='filter-btn active' id='moreBtn'>Scope details &#8250;</button></p>"
    + (main ? "<h3>Main topic</h3><p>" + lab(main.id) + " <span class='share'>(" + (100 * main.m / tot).toFixed(1) + "%)</span></p>" : "")
    + "<p class='meta'>Broad field: " + j.macroLabel + "</p>"
    + (main ? "<h3>Its biggest topics</h3><ul>" + communities + "</ul>" : "")
    + "<h3>Similar journals <span class='share'>(estimate)</span></h3>" + near
    + "<p class='meta' style='margin-top:10px'>Colours and percentages are the stored results from BigQuery. Similar-journal scores are an estimate made for this page: 100 means an identical topic mix, across every publisher.</p>";
  detail.querySelectorAll(".near-btn").forEach(btn => {
    btn.addEventListener("click", () => goJournal(Number(btn.dataset.id)));
  });
  const mb = document.getElementById("moreBtn"); if (mb) mb.addEventListener("click", () => goView("scope"));
}

function openDetails(id) {
  const j = J[id], ov = document.getElementById("ov");
  const lab = cid => (COMM[cid] ? COMM[cid].label : "Topic " + cid);
  const rows = (j.comms || []).filter(c => COMM[c.id]);
  const ks = (c, i) => (c.ks || "")[i] || "-";
  const st = YEARS.map((y, i) => { const s = j.ys[i]; return { y: y, p: s.n - s.o - s.b, b: s.b, o: s.o, n: s.n }; });
  const pct = s => s.n ? 100 * s.o / s.n : 0;
  const nCore = YEARS.map((y, i) => rows.filter(c => ks(c, i) === "p").length);
  const nAct = YEARS.map((y, i) => rows.filter(c => ((c.y || {})[y] || 0) > 0).length);
  const first = st.findIndex(s => s.n > 0), last = st.length - 1 - st.slice().reverse().findIndex(s => s.n > 0);
  const delta = pct(st[last]) - pct(st[first]);
  const trans = [];
  for (let i = 1; i < YEARS.length; i++) {
    const ent = rows.filter(c => ks(c, i) === "p" && ks(c, i - 1) !== "p").map(c => ({ l: lab(c.id), v: (c.y || {})[YEARS[i]] || 0, from: ks(c, i - 1) === "o" ? "was outside the core" : ks(c, i - 1) === "-" ? "new" : "was borderline" })).sort((a, b) => b.v - a.v);
    const lft = rows.filter(c => ks(c, i - 1) === "p" && ks(c, i) !== "p").map(c => ({ l: lab(c.id), v: (c.y || {})[YEARS[i]] || 0, to: ks(c, i) === "-" ? "no papers" : ks(c, i) === "o" ? "now outside the core" : "now borderline" })).sort((a, b) => b.v - a.v);
    trans.push({ from: YEARS[i - 1], to: YEARS[i], ent: ent, lft: lft });
  }
  const li = (x, w) => "<li><span>" + x.l + "</span><span class='share'>" + x.v + " papers · " + (x.from || x.to) + "</span></li>";
  const kp = (b, s) => "<div class='kpi'><b>" + b + "</b><span>" + s + "</span></div>";
  document.getElementById("ovTitle").textContent = j.name + " · how its topics changed, " + YEARS[0] + "–" + YEARS[YEARS.length - 1];
  setJournalTabs(true);
  document.getElementById("ovBody").innerHTML = "<div id='ovRep'></div><div id='ovTime'></div><div id='ovCore'></div><div id='ovData'></div><div id='ovMeso'>" +
    "<div class='kpis'>"
    + kp(j.n.toLocaleString(), "papers in the run")
    + kp(pct(st[first]).toFixed(1) + "% → " + pct(st[last]).toFixed(1) + "%", "outside the core, " + YEARS[first] + " to " + YEARS[last] + " (<span class='" + (delta > 0 ? "dn" : "up") + "'>" + (delta > 0 ? "+" : "") + delta.toFixed(1) + " pts</span>)")
    + kp(nCore[first] + " → " + nCore[last], "core topics with papers")
    + kp(nAct[first] + " → " + nAct[last], "topics with papers")
    + "</div>"
    + "<div class='sec'><h3>Papers each year: core, borderline and outside the core</h3><p class='note'>The line is the share outside the core. " + smallNote(j) + "</p><div id='dtA' style='height:340px'></div></div>"
    + "<div class='sec'><h3>Topic mix by year</h3><p class='note'>Each line is one topic's share of that year's papers, so the lines show the mix shifting. Dot colour is the topic's core status: dark blue core, light blue borderline, orange outside the core. A gap means no papers that year.</p><p style='margin:0 0 6px'><span class='label'>Show:</span> <select id='dtSel' class='filter-btn'><option value='size10'>Top 10 by size</option><option value='size20'>Top 20 by size</option><option value='move10'>10 biggest movers</option><option value='move20'>20 biggest movers</option></select></p><div id='dtB' style='height:460px'></div></div>"
    + "<div class='sec'><h3>Which broad fields the papers outside the core come from</h3><p class='note'>Papers outside the core each year, split by broad field.</p><div id='dtC' style='height:340px'></div></div></div>";
  ov.hidden = false; document.body.style.overflow = "hidden";
  srRender(j);
  const fnt = layout.font, ax = { showgrid: false, zeroline: false };
  Plotly.react("dtA", [
    { type: "bar", name: "Core", x: YEARS.map(String), y: st.map(s => s.p), marker: { color: SCOPE.p.color } },
    { type: "bar", name: "Borderline", x: YEARS.map(String), y: st.map(s => s.b), marker: { color: SCOPE.b.color } },
    { type: "bar", name: "Outside the core", x: YEARS.map(String), y: st.map(s => s.o), marker: { color: SCOPE.o.color } },
    { type: "scatter", mode: "lines+markers+text", name: "% outside the core", x: YEARS.map(String), y: st.map(s => +pct(s).toFixed(1)), yaxis: "y2", line: { color: "#1a1f36", width: 2 }, text: st.map(s => pct(s).toFixed(1) + "%"), textposition: "top center", hoverinfo: "text" }
  ], { barmode: "stack", paper_bgcolor: "#fff", plot_bgcolor: "#fff", font: fnt, margin: { l: 50, r: 50, t: 10, b: 40 }, legend: { orientation: "h", y: -0.18 },
       xaxis: { type: "category" }, yaxis: { title: "Papers", gridcolor: "#eef0f4" }, yaxis2: { overlaying: "y", side: "right", range: [0, Math.max(40, Math.ceil(Math.max.apply(null, st.map(pct)) + 10))], ticksuffix: "%", showgrid: false } }, config);
  const PALX = ["#003BDE","#E8590C","#279F94","#9C36B5","#C2255C","#5C940D","#F08C00","#0B7285","#862E9C","#2B8A3E","#D6336C","#495057","#E03131","#3B5BDB","#74B816","#7048E8","#099268","#A61E4D","#1971C2","#B08968"];
  const share = (c, i) => st[i].n ? 100 * (((c.y || {})[YEARS[i]]) || 0) / st[i].n : null;
  const nmK = { p: "Core", b: "Borderline", o: "Outside the core", "-": "No papers" };
  const drawMix = () => {
    const mode = document.getElementById("dtSel").value;
    const act = rows.filter(c => YEARS.some(y => ((c.y || {})[y] || 0) > 0));
    const span = c => { const v = YEARS.map((y, i) => share(c, i) || 0); return Math.max.apply(null, v) - Math.min.apply(null, v); };
    const moved = c => YEARS.some((y, i) => i && (ks(c, i) === "p") !== (ks(c, i - 1) === "p") && (ks(c, i) !== "-" && ks(c, i - 1) !== "-"));
    let pick;
    if (mode === "core") pick = act.filter(moved).sort((a, b) => span(b) - span(a));
    else if (mode.indexOf("move") === 0) pick = act.slice().sort((a, b) => span(b) - span(a)).slice(0, Number(mode.slice(4)));
    else pick = act.slice().sort((a, b) => b.n - a.n).slice(0, Number(mode.slice(4)));
    const traces = pick.map((c, k) => {
      const xs = [], ys = [], cols = [], tips = [];
      YEARS.forEach((y, i) => { const v = ((c.y || {})[y]) || 0; if (!v) return; xs.push(String(y)); ys.push(+share(c, i).toFixed(2)); const kk = ks(c, i); cols.push(kk === "o" ? SCOPE.o.color : kk === "b" ? SCOPE.b.color : SCOPE.p.color); tips.push("<b>" + lab(c.id) + "</b><br>" + y + ": " + share(c, i).toFixed(1) + "% of papers (" + v + ")<br>" + nmK[kk] + "<br>Broad field: " + (MACRO_NAME[COMM[c.id].macro] || "n/a")); });
      const col = PALX[k % PALX.length];
      return { type: "scatter", mode: "lines+markers", name: lab(c.id), x: xs, y: ys, line: { color: col, width: 2 }, connectgaps: false,
        marker: { size: 11, color: cols, line: { color: col, width: 2 } }, text: tips, hoverinfo: "text" };
    });
    if (!traces.length) { document.getElementById("dtB").innerHTML = "<p class='meta'>No topics to show for this journal.</p>"; return; }
    Plotly.react("dtB", traces, { paper_bgcolor: "#fff", plot_bgcolor: "#fff", font: fnt, margin: { l: 55, r: 10, t: 10, b: 40 }, hovermode: "closest",
      legend: { font: { size: 11 } }, xaxis: { type: "category" }, yaxis: { title: "% of that year's papers", ticksuffix: "%", gridcolor: "#eef0f4", rangemode: "tozero" } }, config);
  };
  document.getElementById("dtSel").addEventListener("change", drawMix); drawMix();
  const mt = {}; rows.forEach(c => { const m = COMM[c.id].macro; YEARS.forEach((y, i) => { if (ks(c, i) === "o") { mt[m] = mt[m] || YEARS.map(() => 0); mt[m][i] += (c.y || {})[y] || 0; } }); });
  const ml = Object.keys(mt).sort((a, b) => mt[b].reduce((s, v) => s + v, 0) - mt[a].reduce((s, v) => s + v, 0));
  Plotly.react("dtC", ml.slice(0, 10).map(m => ({ type: "bar", name: MACRO_NAME[m] || "Field " + m, x: YEARS.map(String), y: mt[m], marker: { color: macroColor[m] || "#888" } })),
    { barmode: "stack", paper_bgcolor: "#fff", plot_bgcolor: "#fff", font: fnt, margin: { l: 50, r: 10, t: 10, b: 40 }, legend: { font: { size: 11 } }, xaxis: { type: "category" }, yaxis: { title: "Papers outside the core", gridcolor: "#eef0f4" } }, config);
  showTab("rep");
  document.getElementById("ovBody").scrollTop = 0;
  document.body.style.overflow = "";
}
function setJournalTabs(on) { ["tabRep", "tabTime", "tabCore", "tabMeso"].forEach(i => { document.getElementById(i).hidden = !on; }); }
function dataHtml() {
  const e = s => String(s == null ? "" : s).replace(/[&<>]/g, c => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;" }[c]));
  const qs = DATA.queries || [], bq = DATA.bq || {};
  const cards = qs.map((x, i) => "<div class='qcard'><button type='button' class='filter-btn qcopy' data-q='" + i + "'>Copy SQL</button><h4>" + (i + 1) + ". " + e(x.title) + "</h4>"
    + "<p class='qmeta'><b>Used for:</b> " + e(x.use) + "<br><b>Tables:</b> " + x.tables.map(e).join(", ") + " · <b>Rows returned:</b> " + x.rows.toLocaleString() + " · <b>Run:</b> " + e(x.ran) + " UTC · <b>Saved as:</b> " + e(x.name) + "</p>"
    + "<pre>" + e(x.sql) + "</pre></div>").join("");
  return "<div class='rpt'><div class='sec'><h3>Where this page's data comes from</h3>"
    + "<p>Every figure on this page comes from the " + qs.length + " BigQuery queries below, run against project <code>" + e(bq.project) + "</code> (" + e(bq.region) + " region), billed to <code>" + e(bq.billing) + "</code>. Each query ran once; the page was then built from the saved results.</p>"
    + "<div class='qnote'><b>Since 12 Nov 2026 the run " + e(DATA.run) + " scope tables hold two levels</b> (broad field and topic). The queries below filter to <code>cluster_level = 'macro'</code>, so they reproduce the broad-field figures on this page.</div>"
    + "<h3>Worked out on this page, not stored</h3><ul>"
    + "<li><b>Percentages</b>: stored counts divided by stored totals.</li>"
    + "<li><b>Bubble colour in Core status view</b>: the status most of a topic's papers carry (query 3).</li>"
    + "<li><b>Topic positions</b>: laid out from the citation links between topics (last query).</li>"
    + "<li><b>Journal positions in Frontiers view</b>: journals with a similar mix of topics are placed near each other (a t-SNE layout of each journal's topic shares, fixed seed), then turned so the widest spread runs left to right, stretched to fit a wide screen, and nudged apart so bubbles do not overlap. Distance is a rough guide only, and up/down versus left/right has no meaning.</li>"
    + "<li><b>Similar journals</b>: how alike two journals' topic mixes are, across all publishers (an estimate).</li>"
    + "<li><b>Main topics by year</b>: the fewest topics holding " + Math.round(100 * DATA.cfg.coverage) + "% of each year's papers, using the stored threshold. An estimate, not a stored result.</li>"
    + "<li><b>Small-year warnings</b>: a year with less than half the papers of the journal's busiest year.</li>"
    + "<li><b>Broad-field colours</b>: copied from the original network-maps page.</li></ul></div>"
    + "<div class='sec'><h3>The queries</h3>" + cards + "</div></div>";
}
function wireCopy(root) { root.querySelectorAll(".qcopy").forEach(btn => btn.addEventListener("click", () => { const s = DATA.queries[Number(btn.dataset.q)].sql; (navigator.clipboard ? navigator.clipboard.writeText(s) : Promise.reject()).then(() => { btn.textContent = "Copied"; setTimeout(() => btn.textContent = "Copy SQL", 1500); }).catch(() => { btn.textContent = "Select the text to copy"; }); })); }
function renderData() { const b = document.getElementById("ovData"); if (b && !b.dataset.done) { b.innerHTML = dataHtml(); b.dataset.done = "1"; wireCopy(b); } }
function openData() {
  setJournalTabs(false);
  document.getElementById("ovTitle").textContent = "Data & queries";
  document.getElementById("ovBody").innerHTML = "<div id='ovRep'></div><div id='ovTime'></div><div id='ovCore'></div><div id='ovMeso'></div><div id='ovData'></div>";
  document.getElementById("ov").hidden = false;
  showTab("data");
}
function showTab(t) {
  const m = { rep: "ovRep", time: "ovTime", core: "ovCore", meso: "ovMeso", data: "ovData" };
  if (t === "data") renderData();
  document.getElementById("tabData").classList.toggle("active", t === "data");
  Object.keys(m).forEach(k => { document.getElementById(m[k]).hidden = k !== t; });
  document.getElementById("tabRep").classList.toggle("active", t === "rep"); document.getElementById("tabTime").classList.toggle("active", t === "time"); document.getElementById("tabCore").classList.toggle("active", t === "core"); document.getElementById("tabMeso").classList.toggle("active", t === "meso");
  document.getElementById("ovBody").scrollTop = 0;
  setTimeout(() => ["rpTrend", "rpTop", "tmA", "tmB", "tmC", "tmD", "dtA", "dtB", "dtC"].forEach(d => { const el = document.getElementById(d); if (el && el.offsetParent) Plotly.Plots.resize(d); }), 50);
}
document.getElementById("tabRep").addEventListener("click", () => showTab("rep"));
document.getElementById("tabTime").addEventListener("click", () => showTab("time"));
document.getElementById("tabMeso").addEventListener("click", () => showTab("meso"));
document.getElementById("tabCore").addEventListener("click", () => showTab("core"));
document.getElementById("tabData").addEventListener("click", () => showTab("data"));
document.getElementById("dataBtn").addEventListener("click", openData);
function closeDetails() { goView("journal"); }
document.getElementById("ovBack").addEventListener("click", closeDetails);

function select(id) {
  selected = id; spot = null; curJ = id;
  document.getElementById("commCtl").hidden = false;
  document.getElementById("backBtn").hidden = false;
  renderDetail(id);
  drawCommunities(J[id]);
  renderYears(J[id]);
  statsEl.textContent = J[id].name;
}

function clearSelection() { goView("market"); }
function resetMarket() {
  selected = null; spot = null;
  document.getElementById("commCtl").hidden = true;
  document.getElementById("backBtn").hidden = true;
  detail.innerHTML = "<p class='empty'>Search for a journal, or click one, to see its topics.</p>";
  document.getElementById("search").value = ""; query = "";
  draw();
  renderMarket();
}

document.getElementById("backBtn").addEventListener("click", () => clearSelection());
const slider = document.getElementById("viewSlider");
function setView(v) {
  colorMode = v ? "meso" : "macro";
  slider.value = v;
  document.getElementById("vMacro").classList.toggle("on", !v);
  document.getElementById("vComm").classList.toggle("on", !!v);
  if (selected == null) draw();
}
slider.addEventListener("input", () => setView(Number(slider.value)));
document.getElementById("vMacro").addEventListener("click", () => setView(0));
document.getElementById("vComm").addEventListener("click", () => setView(1));

let view = "market";
let curJ = (J.find(j => j.name === "Frontiers in Energy Research") || J.slice().sort((a, b) => b.n - a.n)[0]).id;
const INTRO = {
  market: "Each bubble is one Frontiers journal, sized by its papers and coloured by its main broad field. Journals with similar topics sit close together. Click a journal, or use Find, to open it.",
  journal: "Each bubble is a topic this journal publishes in, sized by its papers. Colour shows whether the topic is inside the journal's core. Use Find to switch journal.",
  scope: "The full report for this journal: headline figures, how its topic mix changed, and example papers.",
  data: "Every BigQuery query behind this page, and what the page works out itself."
};
function popGroup() { const g = document.getElementById("navGroup"); g.classList.remove("pop"); void g.offsetWidth; g.classList.add("pop"); }
function goJournal(id) { curJ = id; goView("journal"); popGroup(); }
function goView(v) {
  view = v;
  ["Market", "Journal", "Scope", "Data"].forEach(k => document.getElementById("nav" + k).classList.toggle("active", "nav" + k === "nav" + v.charAt(0).toUpperCase() + v.slice(1)));
  document.getElementById("navJName").textContent = ": " + J[curJ].name.replace(/^Frontiers in /, "");
  document.getElementById("navGroup").classList.toggle("on", v === "journal" || v === "scope");
  document.getElementById("viewIntro").textContent = INTRO[v];
  const map = v === "market" || v === "journal";
  document.getElementById("mainView").hidden = !map;
  document.getElementById("ov").hidden = map;
  document.getElementById("yearCtl").hidden = !map;
  document.getElementById("toolbar").hidden = v === "data";
  document.getElementById("howto").hidden = !map;
  results.hidden = true;
  if (v === "market") { resetMarket(); }
  else if (v === "journal") { select(curJ); }
  else if (v === "scope") {
    selected = curJ; openDetails(curJ);
    const t = document.getElementById("ovTitle"), nm = J[curJ].name.replace(/^Frontiers in /, "");
    t.innerHTML = "<button type='button' class='crumb' id='crumbJ' title='Back to this journal's map'>Journal: " + nm.replace(/[&<>]/g, "") + "</button><span class='crumbsep'>&#8250;</span>Scope details<span class='crumbsub'>how its topics changed, " + YEARS[0] + "&ndash;" + YEARS[YEARS.length - 1] + "</span>";
    document.getElementById("crumbJ").addEventListener("click", () => goView("journal"));
  }
  else if (v === "data") { selected = null; openData(); }
  if (map) { setPanel(true); setTimeout(() => Plotly.Plots.resize("plot"), 60); }
  window.scrollTo(0, 0);
}
function renderMarket() {
  const yi = yearIdx, yr = curYear();
  const st = j => yi ? j.ys[yi - 1] : { n: j.n, o: j.nOos };
  const act = J.filter(j => st(j).n > 0);
  const N = act.reduce((s, j) => s + st(j).n, 0), O = act.reduce((s, j) => s + st(j).o, 0);
  const mode = (document.getElementById("mkSort") || {}).value || "pct";
  const pc = j => st(j).n ? 100 * st(j).o / st(j).n : 0;
  const lst = act.filter(j => mode !== "pct" || st(j).n >= 50).sort(mode === "size" ? (a, b) => st(b).n - st(a).n : (a, b) => pc(b) - pc(a)).slice(0, 12);
  const fields = DATA.macros.map(m => "<span><i class='swatch' style='background:" + macroColor[String(m.id)] + "'></i>" + m.label + "</span>").join("");
  detail.innerHTML = "<h2>All Frontiers journals" + (yr ? " <span class='share'>· " + yr + "</span>" : "") + "</h2>"
    + "<div class='mk-kpis'><div><b>" + act.length + "</b><span>journals" + (yr ? " with papers in " + yr : "") + "</span></div><div><b>" + N.toLocaleString() + "</b><span>papers</span></div>"
    + "<div><b>" + (N ? (100 * O / N).toFixed(1) : "0.0") + "%</b><span>of papers outside their journal's core</span></div><div><b>" + O.toLocaleString() + "</b><span>papers outside the core</span></div></div>"
    + "<h3>Journals</h3><select id='mkSort' class='filter-btn mk-sel'><option value='pct'" + (mode === "pct" ? " selected" : "") + ">Highest share outside the core</option><option value='size'" + (mode === "size" ? " selected" : "") + ">Largest by papers</option></select>"
    + "<div class='mk-list'>" + lst.map(j => "<button type='button' data-id='" + j.id + "'><span>" + j.name.replace(/^Frontiers in /, "") + "</span><span class='share'>" + (mode === "size" ? st(j).n.toLocaleString() : pc(j).toFixed(1) + "%") + "</span></button>").join("") + "</div>"
    + (mode === "pct" ? "<p class='meta' style='margin-top:6px'>Journals with at least 50 papers" + (yr ? " in " + yr : "") + ". Click one to open it.</p>" : "<p class='meta' style='margin-top:6px'>Click one to open it.</p>")
    + "<h3>Broad fields (bubble colour)</h3><div class='legend-f'>" + fields + "</div>";
  detail.querySelectorAll(".mk-list button").forEach(b => b.addEventListener("click", () => goJournal(Number(b.dataset.id))));
  document.getElementById("mkSort").addEventListener("change", renderMarket);
}
["Market", "Journal", "Scope", "Data"].forEach(k => document.getElementById("nav" + k).addEventListener("click", () => goView(k.toLowerCase())));
const search = document.getElementById("search"), results = document.getElementById("results");
let hits = [], act = 0;
const esc = s => s.replace(/[&<>]/g, c => ({"&":"&amp;","<":"&lt;",">":"&gt;"}[c]));
function rank(q) {
  const out = [];
  J.forEach(j => {
    const nm = j.name.toLowerCase().replace(/^frontiers in /, "");
    const full = j.name.toLowerCase();
    let s = -1;
    if (full === q || nm === q) s = 0;
    else if (nm.startsWith(q) || full.startsWith(q)) s = 1;
    else if (nm.split(/[^a-z0-9]+/).some(w => w.startsWith(q))) s = 2;
    else if (full.indexOf(q) >= 0) s = 3;
    else if (q.split(/\s+/).every(w => full.indexOf(w) >= 0)) s = 4;
    else if (j.mesoLabel.toLowerCase().indexOf(q) >= 0) s = 5;
    else if (j.macroLabel.toLowerCase().indexOf(q) >= 0) s = 6;
    if (s >= 0) out.push([s, -j.n, j]);
  });
  out.sort((a, b) => a[0] - b[0] || a[1] - b[1]);
  return out.slice(0, 10).map(o => o[2]);
}
function hl(name, q) {
  const i = name.toLowerCase().indexOf(q);
  return i < 0 ? esc(name) : esc(name.slice(0, i)) + "<mark>" + esc(name.slice(i, i + q.length)) + "</mark>" + esc(name.slice(i + q.length));
}
function renderResults(q) {
  if (!q) { results.hidden = true; return; }
  hits = rank(q); act = 0;
  results.innerHTML = hits.length ? hits.map((j, i) =>
    "<div class='res" + (i === 0 ? " act" : "") + "' data-id='" + j.id + "'><span>" + hl(j.name, q) + "</span><small>" + esc(j.mesoLabel) + " · " + j.n.toLocaleString() + "</small></div>").join("")
    : "<div class='nores'>No journal matches</div>";
  results.hidden = false;
  results.querySelectorAll(".res").forEach(el => el.addEventListener("mousedown", ev => { ev.preventDefault(); pick(Number(el.dataset.id)); }));
}
function showSpot(id) {
  renderDetail(id);
  const d = document.createElement("p");
  d.style.marginTop = "12px";
  d.innerHTML = "<button type='button' class='filter-btn active' id='openComms'>Open its topics</button>";
  detail.appendChild(d);
  document.getElementById("openComms").addEventListener("click", () => { spot = null; select(id); });
  detail.querySelectorAll(".near-btn").forEach(btn => { btn.cloneNode; btn.replaceWith(btn.cloneNode(true)); });
  detail.querySelectorAll(".near-btn").forEach(btn => btn.addEventListener("click", () => pick(Number(btn.dataset.id))));
}
function pick(id) {
  results.hidden = true;
  search.value = ""; query = "";
  search.blur();
  curJ = id;
  goView(view === "scope" ? "scope" : "journal"); popGroup();
}
search.addEventListener("input", ev => renderResults(ev.target.value.trim().toLowerCase()));
search.addEventListener("focus", () => { if (search.value.trim() && spot == null) renderResults(search.value.trim().toLowerCase()); });
search.addEventListener("blur", () => { results.hidden = true; });
search.addEventListener("keydown", ev => {
  const els = results.querySelectorAll(".res");
  if (ev.key === "ArrowDown" || ev.key === "ArrowUp") {
    if (!els.length) return; ev.preventDefault();
    act = (act + (ev.key === "ArrowDown" ? 1 : -1) + els.length) % els.length;
    els.forEach((e, i) => e.classList.toggle("act", i === act)); els[act].scrollIntoView({ block: "nearest" });
  } else if (ev.key === "Enter") { if (hits[act]) { ev.preventDefault(); pick(hits[act].id); } }
  else if (ev.key === "Escape") { search.value = ""; results.hidden = true; if (spot != null) clearSelection(); }
});
search.addEventListener("search", () => { if (!search.value && (spot != null)) clearSelection(); });
window.addEventListener("resize", () => Plotly.Plots.resize("plot"));

Plotly.newPlot("plot", [frame().trace], layout, config).then(gd => {
  gd.on("plotly_click", ev => {
    if (selected != null) return;
    if (!ev.points || !ev.points.length || ev.points[0].customdata == null) return;
    goJournal(ev.points[0].customdata);
  });
  goView("market");
});
;(function () {
  const MC = {}; DATA.mcomms.forEach(c => { MC[c.id] = c; });
  const ROLE = { primary: { c: "#0072B2", n: "Core", pill: "in", t: "Core" }, borderline: { c: "#56B4E9", n: "Borderline", pill: "bd", t: "Borderline" }, out_of_scope: { c: "#D55E00", n: "Outside the core", pill: "out", t: "Outside the core" } };
  const lab = id => (MC[id] ? MC[id].label : "Topic " + id);
  const esc = s => String(s == null ? "" : s).replace(/[&<>]/g, c => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;" }[c]));
  const P1 = x => (x == null ? "n/a" : Number(x).toFixed(1)), nf = x => (x == null ? "n/a" : Number(x).toLocaleString());
  const layoutOv = { font: { family: '-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,sans-serif', color: "#1a1f36", size: 11 } };
  const config = { responsive: true, displayModeBar: false };
  const yd = (j, y) => j.sy[String(y)];
  const yrsOf = j => YEARS.filter(y => yd(j, y) && yd(j, y).a != null);
  const kp = (b, s) => "<div class='kpi'><b>" + b + "</b><span>" + s + "</span></div>";
  const lst = a => a.length <= 1 ? (a[0] || "") : a.slice(0, -1).join(", ") + " and " + a[a.length - 1];
function renderReport(j) {
  const box = document.getElementById("ovRep"), dr = j.sd, sh = j.ss, ys = yrsOf(j), fy = ys[0], ly = ys[ys.length - 1];
  const hasDrift = dr.jsd != null, outs = j.mc.filter(c => c.role === "out_of_scope").slice(0, 2).map(c => lab(c.id));
  const tr = ys.length > 1 ? (yd(j, ly).p < yd(j, fy).p ? "fallen" : yd(j, ly).p > yd(j, fy).p ? "risen" : "stayed the same") : null;
  const baseL = sh.baseTop.map(t => t.label), latL = sh.latTop.map(t => t.label);
  const p1 = "About " + P1(j.oosPct) + "% of " + esc(j.name) + "'s papers (" + nf(j.nOos) + " of " + nf(j.n) + ") sit outside its core broad fields" + (outs.length ? " &mdash; mostly work related to " + esc(lst(outs)) : "") + "."
    + (tr ? " This share has " + tr + " (" + P1(yd(j, fy).p) + "% in " + fy + ", " + P1(yd(j, ly).p) + "% in " + ly + ")." : "")
    + " Its largest broad field is &ldquo;" + esc(lab(j.mc[0].id)) + ".&rdquo;";
  const p2 = sh.insuff ? "There are not enough papers in every year to compare its core broad fields over time."
    : (sh.changed ? "Its core broad fields changed between " + sh.by + " and " + sh.ly + "." + (sh.lost.length ? " Areas that have left the core include " + esc(lst(sh.lost)) + "." : "") + (sh.gained.length ? " Areas that joined the core include " + esc(lst(sh.gained)) + "." : "")
      + (latL.length ? " In " + sh.ly + " the largest core fields are " + esc(lst(latL)) + " (versus " + esc(lst(baseL)) + " in " + sh.by + ")." : "")
      : "Its core broad fields did not change between " + sh.by + " and " + sh.ly + ".");
  const p3 = hasDrift ? "How much its topic mix changed: comparing " + dr.latest + " with " + esc(String(dr.base).replace(/,/g, ", ")) + ", the score is " + dr.jsd + " on a scale from 0 (same mix) to 1 (completely different)" + (dr.rank != null ? ". That ranks it " + dr.rank + " of " + DATA.nRanked + " journals with enough data (1 = most change)" : "") + "."
    : "How much its topic mix changed is not reported for this journal: it does not have enough papers per year.";
  const rows = j.mc.filter(c => c.rank <= 15).map(c => "<tr><td>" + esc(lab(c.id)) + (c.reason ? "<span class='why'>Reviewer note: " + esc(c.reason) + "</span>" : "") + "</td><td><span class='pill " + ROLE[c.role].pill + "'>" + ROLE[c.role].t + "</span>" + (c.verdict ? "<span class='why'>review verdict: " + esc(c.verdict) + "</span>" : "") + "</td><td class='r'>" + nf(c.n) + "</td><td class='r'>" + P1(c.share) + "%</td></tr>").join("");
  const exL = (arr) => arr.length ? arr.map(e => "<li>" + esc(e.t) + (e.hn ? " <span class='pill out'>title rule</span>" : "") + "<span class='why'>" + esc(e.c || "") + (e.y ? " · " + e.y : "") + "</span></li>").join("") : "<li>none stored</li>";
  const profRows = j.mc.slice(0, 8).map(c => { const p = DATA.prof[c.id] || {}, sh = Object.entries(p.shares || {}).slice(0, 3).map(e => esc(e[0]) + " " + e[1] + "%").join(", ");
    return "<tr><td>" + esc(lab(c.id)) + "</td><td>" + esc((p.kwTop || []).join(", ") || "none stored") + "</td><td>" + (p.dom ? esc(p.dom) + " (" + p.domPct + "%)" : "n/a") + "</td><td class='r'>" + (MC[c.id] ? nf(MC[c.id].size) : "n/a") + "</td></tr>"; }).join("");
  const hnHtml = j.hn.length ? "<div class='sec'><h3>Papers moved outside the core by a title rule (" + j.hn.length + ")</h3><p class='note'>These papers' titles match a rule that marks them as outside the core (for example &ldquo;fintech&rdquo;). They count towards the share outside the core, even though " + j.hn.filter(h => h.prim).length + " of them sit in a core broad field, which is still shown as core.</p><table class='rt'><tr><th>Title</th><th>Broad field</th><th>Rule</th></tr>" + j.hn.map(h => "<tr><td>" + esc(h.t || "(title not available)") + (h.y ? " <span class='why'>" + h.y + "</span>" : "") + "</td><td>" + esc(lab(h.c)) + (h.prim ? " <span class='pill in'>core</span>" : "") + "</td><td><code>" + esc(h.pat) + "</code></td></tr>").join("") + "</table></div>" : "";
  box.innerHTML = "<div class='rpt'>"
    + "<div class='sec'><h3>Summary · " + (fy || "") + " &rarr; " + (ly || "") + "</h3><p class='headline'>" + headline(j) + "</p>"
    + "<div class='rpbar2'><div style='width:" + j.oosPct + "%'>" + P1(j.oosPct) + "% outside the core</div></div>"
    + "<div class='kpis'>" + kp(nf(j.n), "papers analysed") + kp(nf(j.nOos) + " (" + P1(j.oosPct) + "%)", "papers outside the core") + kp(nf(j.nBord), "borderline papers") + kp(nf(j.nHard), "moved out by a title rule")
    + kp(hasDrift ? dr.jsd : "n/a", hasDrift ? "topic mix change, " + dr.latest + " vs " + YEARS[0] + "&ndash;" + YEARS[2] + " (0 = same, 1 = all different)" : "topic mix change (not enough data)") + kp(dr.ed != null ? dr.ed : "n/a", "change in focus (below 0 = more focused)") + kp(dr.rank != null ? dr.rank + " / " + DATA.nRanked : "n/a", "rank for topic change (1 = most change)") + kp(j.nPrim, "core broad fields (holding " + P1(j.cov) + "% of papers)") + "</div>"
    + "<p>" + p1 + "</p><p>" + p2 + "</p><p>" + p3 + "</p></div>"
    + "<div class='rpgrid'><div class='sec'><h3>Topic mix change and share outside the core</h3><div id='rpTrend' style='height:300px'></div></div><div class='sec'><h3>Biggest broad fields</h3><div id='rpTop' style='height:300px'></div></div></div>"
    + "<div class='sec'><h3>Broad fields in this journal</h3><table class='rt'><tr><th>Broad field</th><th>Status</th><th class='r'>Papers</th><th class='r'>Share of journal</th></tr>" + rows + "</table><p class='src'>Top 15 by size.</p></div>"
    + "<div class='sec'><h3>Broad-field profiles</h3><table class='rt'><tr><th>Broad field</th><th>Keywords</th><th>Biggest Frontiers journal in it</th><th class='r'>Frontiers papers in it</th></tr>" + profRows + "</table><p class='src'>Top 8 broad fields for this journal.</p></div>"
    + hnHtml
    + "<div class='sec ex'><h3>Example papers</h3><div class='rpgrid'><div><h4 class='tin'>Core</h4><ul>" + exL(j.ex.in_scope) + "</ul></div><div><h4 class='tout'>Outside the core</h4><ul>" + exL(j.ex.out_of_scope) + "</ul></div></div></div>"
    + "<div class='rnote'><b>How to read this.</b> These figures come from citation patterns, not from reading the papers. Methods papers and reviews cite widely, so they can look outside the core when they are not. A journal's core broad fields are the fewest that together hold " + Math.round(DATA.cfg.coverage * 100) + "% of its papers, the same threshold for every journal. Treat the figures as a prompt to look closer, not a final verdict. No paper-by-paper AI review is available for this run. " + smallNote(j) + "</div></div>";
  const X = ys.map(String);
  Plotly.react("rpTrend", [
    { type: "scatter", mode: "lines+markers", name: "Topic mix change", x: ys.filter(y => yd(j, y).jsd != null).map(String), y: ys.filter(y => yd(j, y).jsd != null).map(y => yd(j, y).jsd), line: { color: "#1f4fbf", width: 2 } },
    { type: "scatter", mode: "lines+markers", name: "% outside the core", x: X, y: ys.map(y => yd(j, y).p), yaxis: "y2", line: { color: "#e8590c", width: 2 } }],
    { paper_bgcolor: "#fff", plot_bgcolor: "#fff", font: layoutOv.font, margin: { l: 50, r: 50, t: 8, b: 40 }, legend: { orientation: "h", y: -0.2 }, xaxis: { type: "category" }, yaxis: { title: "Change score (0–1)", rangemode: "tozero", gridcolor: "#eef0f4" }, yaxis2: { title: "% outside the core", overlaying: "y", side: "right", rangemode: "tozero", showgrid: false } }, config);
  const tp = j.mc.slice(0, 8).slice().reverse();
  Plotly.react("rpTop", [{ type: "bar", orientation: "h", y: tp.map(c => lab(c.id)), x: tp.map(c => c.share), marker: { color: tp.map(c => ROLE[c.role].c) }, hoverinfo: "x+y" }],
    { paper_bgcolor: "#fff", plot_bgcolor: "#fff", font: layoutOv.font, margin: { l: 210, r: 10, t: 8, b: 40 }, xaxis: { title: "% of journal papers", gridcolor: "#eef0f4" }, yaxis: { automargin: true } }, config);
}
function renderTime(j) {
  const box = document.getElementById("ovTime"), ys = yrsOf(j), dr = j.sd, sh = j.ss, X = ys.map(String);
  const dyr = ys.filter(y => yd(j, y).jsd != null);
  const shRow = (t) => "<tr><td>" + esc(t.label) + "</td><td class='r'>" + nf(t.papers) + "</td><td class='r'>" + P1(t.share_of_year) + "%</td></tr>";
  box.innerHTML = "<div class='rpt'>"
    + "<div class='sec'><h3>Papers and papers outside the core, by year</h3><p class='note'>Years with fewer than 20 papers are not reported. Each broad field keeps the same core status in every year. " + smallNote(j) + "</p><div id='tmA' style='height:320px'></div></div>"
    + "<div class='sec'><h3>How much the topic mix changed, by year</h3><p class='note'>" + (dyr.length ? "Each year's mix of broad fields compared with " + esc(String(dr.base || "the first years").replace(/,/g, ", ")) + ": a score from 0 (same mix) to 1 (completely different), the share of papers in fields new since then, and the change in focus (below 0 = more focused). Years with too few papers are left out." : "Not reported for this journal: it does not have enough papers per year.") + "</p><div class='rpgrid'><div id='tmB' style='height:300px'></div><div id='tmC' style='height:300px'></div></div></div>"
    + "<div class='sec'><h3>Broad-field mix by year</h3><p class='note'>Each line is one broad field's share of that year's papers. Dot colour is its core status.</p><p style='margin:0 0 6px'><span class='label'>Show:</span> <select id='tmSel' class='filter-btn'><option value='10'>Top 10 by size</option><option value='19'>All broad fields</option></select></p><div id='tmD' style='height:440px'></div></div>"
    + "<div class='sec'><h3>Core broad fields, " + (sh.by || "") + " vs " + (sh.ly || "") + "</h3>" + (sh.insuff ? "<p class='note'>Not enough papers per year to compare.</p>" : "<p class='note'>" + (sh.changed ? "The core changed." : "The core did not change.") + (sh.lost.length ? " Left: " + esc(lst(sh.lost)) + "." : "") + (sh.gained.length ? " Joined: " + esc(lst(sh.gained)) + "." : "") + "</p><div class='rpgrid'><div><h4>" + sh.by + "</h4><table class='rt'><tr><th>Broad field</th><th class='r'>Papers</th><th class='r'>Share of year</th></tr>" + (sh.baseTop.map(shRow).join("") || "") + "</table></div><div><h4>" + sh.ly + "</h4><table class='rt'><tr><th>Broad field</th><th class='r'>Papers</th><th class='r'>Share of year</th></tr>" + (sh.latTop.map(shRow).join("") || "") + "</table></div></div>") + "</div></div>";
  Plotly.react("tmA", [
    { type: "bar", name: "All papers", x: X, y: ys.map(y => yd(j, y).a), marker: { color: "#b8c4dc" } },
    { type: "bar", name: "Outside the core", x: X, y: ys.map(y => yd(j, y).o), marker: { color: ROLE.out_of_scope.c } },
    { type: "scatter", mode: "lines+markers+text", name: "% outside the core", x: X, y: ys.map(y => yd(j, y).p), yaxis: "y2", line: { color: "#1a1f36", width: 2 }, text: ys.map(y => (yd(j, y).p == null ? "" : yd(j, y).p + "%")), textposition: "top center", hoverinfo: "text" }],
    { barmode: "group", paper_bgcolor: "#fff", plot_bgcolor: "#fff", font: layoutOv.font, margin: { l: 50, r: 50, t: 10, b: 40 }, legend: { orientation: "h", y: -0.18 }, xaxis: { type: "category" }, yaxis: { title: "Papers", gridcolor: "#eef0f4" }, yaxis2: { overlaying: "y", side: "right", rangemode: "tozero", ticksuffix: "%", showgrid: false } }, config);
  if (dyr.length) {
    Plotly.react("tmB", [{ type: "scatter", mode: "lines+markers", name: "Topic mix change", x: dyr.map(String), y: dyr.map(y => yd(j, y).jsd), line: { color: "#1f4fbf", width: 2 } },
      { type: "scatter", mode: "lines+markers", name: "% in new fields", x: dyr.map(String), y: dyr.map(y => yd(j, y).newc), yaxis: "y2", line: { color: "#9c36b5", width: 2 } }],
      { paper_bgcolor: "#fff", plot_bgcolor: "#fff", font: layoutOv.font, margin: { l: 50, r: 50, t: 8, b: 40 }, legend: { orientation: "h", y: -0.2 }, xaxis: { type: "category" }, yaxis: { title: "Change score (0–1)", rangemode: "tozero", gridcolor: "#eef0f4" }, yaxis2: { title: "% in new fields", overlaying: "y", side: "right", rangemode: "tozero", showgrid: false } }, config);
    Plotly.react("tmC", [{ type: "bar", name: "Change in focus", x: dyr.map(String), y: dyr.map(y => yd(j, y).ed), marker: { color: dyr.map(y => yd(j, y).ed < 0 ? "#1f4fbf" : "#e8590c") } }],
      { paper_bgcolor: "#fff", plot_bgcolor: "#fff", font: layoutOv.font, margin: { l: 50, r: 10, t: 8, b: 40 }, xaxis: { type: "category" }, yaxis: { title: "Change in focus (below 0 = more focused)", gridcolor: "#eef0f4" } }, config);
  } else { document.getElementById("tmB").innerHTML = ""; document.getElementById("tmC").innerHTML = ""; }
  const drawMix = () => {
    const n = Number(document.getElementById("tmSel").value), pick = j.mc.slice(0, n), PALX = ["#003BDE", "#E8590C", "#279F94", "#9C36B5", "#C2255C", "#5C940D", "#F08C00", "#0B7285", "#862E9C", "#2B8A3E", "#D6336C", "#495057", "#E03131", "#3B5BDB", "#74B816", "#7048E8", "#099268", "#A61E4D", "#1971C2"];
    const tr = pick.map((c, k) => { const xs = [], vs = [], cols = [], tips = [];
      ys.forEach(y => { const v = (c.y || {})[String(y)] || 0, a = yd(j, y).a; if (!v || !a) return; const s = +(100 * v / a).toFixed(2); xs.push(String(y)); vs.push(s); cols.push(ROLE[c.role].c); tips.push("<b>" + esc(lab(c.id)) + "</b><br>" + y + ": " + s + "% of papers (" + v + ")<br>" + ROLE[c.role].n); });
      return { type: "scatter", mode: "lines+markers", name: lab(c.id), x: xs, y: vs, line: { color: PALX[k % PALX.length], width: 2 }, marker: { size: 11, color: cols, line: { color: PALX[k % PALX.length], width: 2 } }, text: tips, hoverinfo: "text", connectgaps: false }; });
    Plotly.react("tmD", tr, { paper_bgcolor: "#fff", plot_bgcolor: "#fff", font: layoutOv.font, margin: { l: 55, r: 10, t: 10, b: 40 }, hovermode: "closest", legend: { font: { size: 11 } }, xaxis: { type: "category" }, yaxis: { title: "% of that year's papers", ticksuffix: "%", gridcolor: "#eef0f4", rangemode: "tozero" } }, config);
  };
  document.getElementById("tmSel").addEventListener("change", drawMix); drawMix();
}


  function renderCore(j) {
  const box = document.getElementById("ovCore"), cl = id => (COMM[id] ? COMM[id].label : "Topic " + id);
  const tot = YEARS.map((y, i) => j.comms.reduce((s, c) => s + (((c.y || {})[y]) || 0), 0));
  const sh = (c, i) => tot[i] ? 100 * (((c.y || {})[YEARS[i]]) || 0) / tot[i] : 0;
  const inC = (c, i) => (c.cy || "")[i] === "1";
  const rows = j.comms.filter(c => (c.cy || "").indexOf("1") >= 0 || /1/.test(c.cy || "")).slice();
  const ever = new Set(rows.map(c => c.id));
  j.comms.forEach(c => { if (!ever.has(c.id) && inC(c, 0)) { rows.push(c); } });
  rows.sort((a, b) => (b.cy.split("1").length - a.cy.split("1").length) || b.n - a.n);
  const head = "<tr><th>Topic</th>" + YEARS.map(y => "<th class='r'>" + y + "</th>").join("") + "</tr>";
  const cell = (c, i) => { const v = ((c.y || {})[YEARS[i]]) || 0; if (!v) return "<td class='cell cnone'>&ndash;</td>"; const now = inC(c, i), prev = i > 0 ? inC(c, i - 1) : now;
    const cls = now ? (prev ? "cin" : "cjoin") : (prev ? "cleft" : "cnone"); const tag = now ? (prev ? "" : " new") : (prev ? " dropped" : ""); return "<td class='cell " + cls + "'>" + sh(c, i).toFixed(1) + "%" + tag + "</td>"; };
  const body = rows.map(c => "<tr><td>" + esc(cl(c.id)) + "</td>" + YEARS.map((y, i) => cell(c, i)).join("") + "</tr>").join("");
  const summ = YEARS.map((y, i) => {
    if (!tot[i]) return "";
    const now = j.comms.filter(c => inC(c, i)), cover = now.reduce((s, c) => s + sh(c, i), 0);
    const ent = i > 0 ? j.comms.filter(c => inC(c, i) && (c.cy || "")[i - 1] !== "1") : [];
    const lft = i > 0 ? j.comms.filter(c => !inC(c, i) && (c.cy || "")[i - 1] === "1") : [];
    const chip = (arr, cls, verb) => arr.map(c => "<span class='" + cls + "'>" + verb + " " + esc(cl(c.id)) + " (" + sh(c, i).toFixed(1) + "%" + (((c.y || {})[y]) ? "" : ", no papers") + ")</span>").join("");
    return "<tr><td><b>" + y + "</b></td><td class='r'>" + now.length + "</td><td class='r'>" + cover.toFixed(1) + "%</td><td><div class='chg'>" + (i === 0 ? "<span class='cnone'>first year</span>" : (chip(lft, "cleft", "Dropped out:") + chip(ent, "cjoin", "New:") || "<span class='cnone'>no change</span>")) + "</div></td></tr>";
  }).join("");
  box.innerHTML = "<div class='rpt'><div class='sec'><h3>Main topics, year by year</h3>"
    + "<p>For each year, the main topics are the fewest topics that together hold " + Math.round(100 * DATA.cfg.coverage) + "% of that year's papers. A topic <b>dropped out</b> when it was a main topic the year before and is not now, and is <b>new</b> when the reverse is true. " + smallNote(j) + "</p>"
    + "<table class='rt'><tr><th>Year</th><th class='r'>Main topics</th><th class='r'>Share of papers they hold</th><th>What changed from the year before</th></tr>" + summ + "</table></div>"
    + "<div class='sec'><h3>Each topic's share of the journal's papers, by year</h3><table class='rt cmx'>" + head + body + "</table>"
    + "<p class='src'>Dark blue = a main topic that year, light blue = new that year, orange = dropped out that year, grey = not a main topic. Shown: topics that were a main topic in at least one year.</p></div>"
    + "<div class='rnote'><b>An estimate.</b> This view is worked out on this page from each year's paper counts. It is not a stored result, and it can differ from the core broad fields shown in the other tabs, which are the official figures. Use it to see the shape of the change.</div></div>";
}
window.srRender = function (j) { renderReport(j); renderTime(j); renderCore(j); };
})();
</script>
</body>
</html>

