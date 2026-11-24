// Smoke test for the built page: node test_dashboard.js out/network_bubbles_<RUN>.html   (needs: npm install jsdom)
const { JSDOM } = require("jsdom"); const fs = require("fs");
const file = process.argv[2]; if (!file) { console.error("usage: node test_dashboard.js <built page>"); process.exit(2); }
const html = fs.readFileSync(file, "utf8").replace(/<script src="[^"]*plotly[^"]*"><\/script>/, "");
const calls = {}, errs = []; let click = null;
const dom = new JSDOM(html, { runScripts: "dangerously", beforeParse(w) {
  w.Plotly = { react: (id, t, l) => { calls[id] = { t, l }; }, newPlot: (id, t, l) => { calls[id] = { t, l }; return Promise.resolve({ on(ev, cb) { if (ev === "plotly_click") click = cb; } }); }, Plots: { resize() {} } };
  w.addEventListener("error", e => errs.push(e.message)); } });
const w = dom.window, d = w.document, fails = [];
const ok = (cond, msg) => { if (!cond) fails.push(msg); };
setTimeout(() => {
  const J = w.eval("J"), Y = w.eval("YEARS");
  ok(!errs.length, "page errors: " + errs.join("; "));
  ok(d.querySelector(".navtab.active").id === "navMarket", "opens on Frontiers view");
  ok(calls.plot.t[0].x.length === J.length, "overview draws every journal");
  click({ points: [{ customdata: J[0].id }] });
  ok(d.getElementById("navJournal").classList.contains("active"), "map click opens Journal tab");
  for (const j of J) {
    try {
      w.goJournal(j.id);
      const hdr = calls.plot.l.annotations[0].text, pc = (100 * j.nOos / j.n).toFixed(1);
      ok(hdr.includes(pc + "% outside the core"), j.name + ": header % = stored out-of-scope / papers");
      const n = j.ys.reduce((s, x) => s + x.n, 0), o = j.ys.reduce((s, x) => s + x.o, 0), b = j.ys.reduce((s, x) => s + x.b, 0);
      ok(n === j.n && o === j.nOos && b === j.nBord, j.name + ": per-year counts add up to stored totals");
      ok(w.headline(j).includes(Number(j.oosPct).toFixed(1) + "%"), j.name + ": headline uses stored %");
      w.goView("scope"); ["tabTime", "tabCore", "tabMeso", "tabRep"].forEach(t => d.getElementById(t).click());
    } catch (e) { fails.push(j.name + ": " + e.message); }
  }
  w.goView("data"); ok(d.querySelectorAll("#ovData .qcard").length === (w.eval("DATA").queries || []).length, "Data tab lists every query");
  console.log(fails.length ? "FAIL\n" + fails.slice(0, 20).join("\n") : "PASS: " + J.length + " journals, " + Y.length + " years, all tabs");
  process.exit(fails.length ? 1 : 0);
}, 900);
