"""One-off script to emit incites_cwts_leiden_citation_communities.ipynb. Safe to delete after run."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "incites_cwts_leiden_citation_communities.ipynb"


def md(s: str) -> dict:
    return {"cell_type": "markdown", "metadata": {}, "source": s.splitlines(keepends=True)}


def code(s: str) -> dict:
    return {"cell_type": "code", "metadata": {}, "outputs": [], "source": s.splitlines(keepends=True)}


cells = []

cells.append(
    md(
        """# CWTS Leiden citation communities (InCites-style)

**Goal:** Build a **citation network** (documents = nodes, citations = links), export **[CWTS `publicationclassification`](https://github.com/CWTSLeiden/publicationclassification)** inputs, and run **multi-resolution Leiden** for **micro / meso / macro** cluster IDs per document — the same *method family* as **Clarivate InCites Citation Topics** (CWTS + Leiden; see [Clarivate on Citation Topics](https://clarivate.com/blog/introducing-citation-topics/)).

**Not included:** proprietary InCites parameters, Web of Science scale, or ISI topic names. You supply the **edge list**; CWTS supplies the **algorithm**.

**Flow:** `edges` → `pubs.txt` + `cit_links.txt` → Java `PublicationClassificationCreator` → `classification.txt` → DataFrame with publication IDs.
"""
    )
)

cells.append(
    md(
        """## Prerequisites

1. **JDK** on `PATH` or `JAVA_HOME` (use **17–21** to build CWTS with Gradle 8.2.x).
2. Clone [publicationclassification](https://github.com/CWTSLeiden/publicationclassification) and run `gradlew.bat build`.
3. Set **`PUBLICATION_CLASSIFICATION_ROOT`** to the clone path (or edit the config cell).
4. Optional: **`GRADLE_JAVA_HOME`** if the default JDK is too new for Gradle.
5. Large graphs: **`CWTS_JVM_OPTS`** e.g. `-Xmx16g -XX:+ExitOnOutOfMemoryError`.
"""
    )
)

cells.append(
    code(
        r"""# --- Configuration ---
from __future__ import annotations

import os
from pathlib import Path

import pandas as pd

PUBLICATION_CLASSIFICATION_ROOT = Path(
    os.environ.get(
        "PUBLICATION_CLASSIFICATION_ROOT",
        r"C:\Users\sophie.wilson\publicationclassification",
    )
)

NOTEBOOK_DIR = Path.cwd()
WORK_DIR = NOTEBOOK_DIR / "_cwts_incites_style"
WORK_DIR.mkdir(parents=True, exist_ok=True)

PUBS_TSV = WORK_DIR / "pubs.txt"
CITS_TSV = WORK_DIR / "cit_links.txt"
CLASS_OUT = WORK_DIR / "classification.txt"

# True: synthetic multi-clique citation graph (no external data).
# False: load EDGES_CSV with columns citing_id, cited_id [, weight]
USE_SYNTHETIC = True
EDGES_CSV = WORK_DIR / "edges_input.csv"

# If None, every publication that appears in edges is "core" (core_pub=1).
CORE_IDS: set[int] | None = None

print("WORK_DIR:", WORK_DIR.resolve())
print("CWTS clone:", PUBLICATION_CLASSIFICATION_ROOT)
"""
    )
)

cells.append(
    code(
        r"""def build_cwts_pubs_and_cit_links(
    df_edges: pd.DataFrame,
    col_citing: str = "citing_id",
    col_cited: str = "cited_id",
    col_weight: str = "weight",
    core_publication_ids: set[int] | None = None,
) -> tuple[pd.DataFrame, pd.DataFrame, list[int]]:
    # Build pubs_df and bidirectional sorted cit_df for CWTS file format.
    df = df_edges.copy()
    if col_weight not in df.columns:
        df[col_weight] = 1.0

    def norm_pid(x):
        if pd.isna(x):
            return None
        return int(x)

    df["_src"] = df[col_citing].map(norm_pid)
    df["_tgt"] = df[col_cited].map(norm_pid)
    df = df.dropna(subset=["_src", "_tgt"])
    df["_src"] = df["_src"].astype(int)
    df["_tgt"] = df["_tgt"].astype(int)
    df = df[df["_src"] != df["_tgt"]]

    edge_nodes = set(df["_src"]) | set(df["_tgt"])
    core_ids = set(edge_nodes) if core_publication_ids is None else set(core_publication_ids)
    all_ids = sorted(edge_nodes | core_ids)
    pub_map = {pid: i for i, pid in enumerate(all_ids)}

    pubs_df = pd.DataFrame(
        [(pub_map[pid], 1 if pid in core_ids else 0) for pid in all_ids],
        columns=["pub_no", "core_pub"],
    )

    agg = (
        df.groupby(["_src", "_tgt"], as_index=False)[col_weight]
        .sum()
        .rename(columns={"_src": "raw_src", "_tgt": "raw_tgt"})
    )
    agg["pub_no1"] = agg["raw_src"].map(pub_map)
    agg["pub_no2"] = agg["raw_tgt"].map(pub_map)
    agg = agg.dropna(subset=["pub_no1", "pub_no2"])
    agg["pub_no1"] = agg["pub_no1"].astype(int)
    agg["pub_no2"] = agg["pub_no2"].astype(int)
    agg = agg.sort_values(["pub_no1", "pub_no2"])
    wcol = col_weight
    _forward = agg[["pub_no1", "pub_no2", wcol]].copy()
    _reverse = pd.DataFrame(
        {
            "pub_no1": _forward["pub_no2"].values,
            "pub_no2": _forward["pub_no1"].values,
            wcol: _forward[wcol].values,
        }
    )
    _bidir = pd.concat([_forward, _reverse], ignore_index=True)
    cit_df = (
        _bidir.groupby(["pub_no1", "pub_no2"], as_index=False)[wcol]
        .sum()
        .sort_values(["pub_no1", "pub_no2"])
        .rename(columns={wcol: "cit_weight"})
    )
    return pubs_df, cit_df, all_ids
"""
    )
)

cells.append(
    code(
        r"""# --- Build or load edge list ---
if USE_SYNTHETIC:
    # Three dense cliques + weak bridges (similar idea to cwts_synthetic_test)
    edges = []
    w = 1.0
    n_cliques, sz = 3, 8
    for c in range(n_cliques):
        base = c * sz
        nodes = list(range(base, base + sz))
        for i, u in enumerate(nodes):
            for v in nodes[i + 1 :]:
                edges.append((u, v, w))
        if c < n_cliques - 1:
            edges.append((base + sz - 1, base + sz, w))
    # Use synthetic integer "publication IDs" 0..N-1
    df_edges = pd.DataFrame(edges, columns=["citing_id", "cited_id", "weight"])
    print("Synthetic edges:", len(df_edges), "unique nodes:", df_edges[["citing_id", "cited_id"]].stack().nunique())
else:
    df_edges = pd.read_csv(EDGES_CSV)
    for c in ("citing_id", "cited_id"):
        if c not in df_edges.columns:
            raise ValueError(f"{EDGES_CSV} must contain columns citing_id, cited_id")
    print("Loaded", len(df_edges), "rows from", EDGES_CSV)

pubs_df, cit_df, all_ids = build_cwts_pubs_and_cit_links(
    df_edges, core_publication_ids=CORE_IDS
)
pubs_df.to_csv(PUBS_TSV, sep="\t", header=False, index=False)
cit_df.to_csv(CITS_TSV, sep="\t", header=False, index=False)
print("Wrote", PUBS_TSV, "rows", len(pubs_df))
print("Wrote", CITS_TSV, "rows", len(cit_df))
"""
    )
)

cells.append(
    code(
        r"""# --- Run CWTS PublicationClassificationCreator (Leiden, micro/meso/macro) ---
import shlex
import subprocess
import os
import shutil

def _find_cwts_jars(jar_dir: Path) -> list[Path]:
    if not jar_dir.is_dir():
        return []
    jars = []
    for p in jar_dir.glob("*.jar"):
        if p.name.endswith("-sources.jar") or p.name.endswith("-javadoc.jar"):
            continue
        jars.append(p)
    pref = [p for p in jars if p.name.startswith("publicationclassification")]
    return pref or jars


def _java_executable() -> str:
    j = shutil.which("java")
    if j:
        return j
    jh = os.environ.get("JAVA_HOME", "").strip()
    p = Path(jh) / "bin" / "java.exe"
    if p.is_file():
        return str(p)
    raise RuntimeError("Install a JDK and add java to PATH or set JAVA_HOME.")


JAR_DIR = PUBLICATION_CLASSIFICATION_ROOT / "build" / "libs"
GRADLEW = PUBLICATION_CLASSIFICATION_ROOT / "gradlew.bat"
jars = _find_cwts_jars(JAR_DIR)
if not jars and GRADLEW.is_file():
    env = os.environ.copy()
    gjh = os.environ.get("GRADLE_JAVA_HOME", "").strip()
    if gjh:
        env["JAVA_HOME"] = gjh
    r = subprocess.run(
        ["cmd.exe", "/c", "gradlew.bat", "build"],
        cwd=str(PUBLICATION_CLASSIFICATION_ROOT),
        env=env,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    if r.returncode != 0:
        raise RuntimeError("gradlew build failed:\n" + (r.stderr or "")[-4000:])
    jars = _find_cwts_jars(JAR_DIR)
if not jars:
    raise FileNotFoundError(f"No CWTS jar in {JAR_DIR}. Build the clone or set PUBLICATION_CLASSIFICATION_ROOT.")

jar_path = max(jars, key=lambda p: p.stat().st_mtime)

n_nodes = len(all_ids)
# CWTS default-ish params for large graphs; gentler params for small demos
if n_nodes < 5000:
    RES_MICRO, THR_MICRO = "0.02", "3"
    RES_MESO, THR_MESO = "0.01", "3"
    RES_MACRO, THR_MACRO = "0.005", "3"
else:
    RES_MICRO, THR_MICRO = "4e-4", "25"
    RES_MESO, THR_MESO = "2e-4", "250"
    RES_MACRO, THR_MACRO = "7e-5", "1000"

LARGEST_COMPONENT = "true"
N_ITER = "100"
MAIN = "nl.cwts.publicationclassification.run.PublicationClassificationCreator"
JVM_OPTS = shlex.split(os.environ.get("CWTS_JVM_OPTS", "-Xmx8g -XX:+ExitOnOutOfMemoryError"))

cmd = [
    _java_executable(),
    *JVM_OPTS,
    "-cp",
    str(jar_path),
    MAIN,
    str(PUBS_TSV),
    str(CITS_TSV),
    str(CLASS_OUT),
    LARGEST_COMPONENT,
    N_ITER,
    RES_MICRO,
    THR_MICRO,
    RES_MESO,
    THR_MESO,
    RES_MACRO,
    THR_MACRO,
]
print("JAR:", jar_path.name, "| nodes:", n_nodes, "| JVM:", " ".join(JVM_OPTS))
print("Leiden params (micro/meso/macro res, min cluster size):", RES_MICRO, THR_MICRO, RES_MESO, THR_MESO, RES_MACRO, THR_MACRO)

proc = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace")
if proc.returncode != 0:
    raise RuntimeError("CWTS failed:\n" + (proc.stderr or "")[-8000:])
print(proc.stdout[-2000:] if len(proc.stdout) > 2000 else proc.stdout)
print("Wrote", CLASS_OUT)
"""
    )
)

cells.append(
    code(
        r"""# --- Load communities and map pub_no -> your publication_id ---
cls = pd.read_csv(
    CLASS_OUT,
    sep="\t",
    header=None,
    names=["pub_no", "micro_cluster", "meso_cluster", "macro_cluster"],
)
cls["publication_id"] = cls["pub_no"].astype(int).map(lambda i: all_ids[i])
out = cls[["publication_id", "micro_cluster", "meso_cluster", "macro_cluster"]]
display(out.head(12))
for col in ("micro_cluster", "meso_cluster", "macro_cluster"):
    print(col, "nunique:", out[col].nunique())
# Optional: save for Tableau / SQL
# out.to_csv(WORK_DIR / "publication_communities.csv", index=False)
"""
    )
)

cells.append(
    md(
        """## Interpretation

- **Citation network:** Each row in your edge list is a directed citation (citing → cited). CWTS uses a **symmetrized, sorted** edge list internally as required by their `Network(..., sortedEdges=True)` loader.
- **Communities:** `micro_cluster` / `meso_cluster` / `macro_cluster` are **successive Leiden resolutions** with **minimum cluster size** thresholds (CWTS-style), analogous in *role* to fine vs coarse **Citation Topic** levels in InCites — not the same numeric labels as Clarivate.
- **Next steps:** Replace `USE_SYNTHETIC = False` and provide a real `edges_input.csv` from BigQuery or elsewhere; tune `RES_*` and `THR_*` for your graph size (see [CWTS repo](https://github.com/CWTSLeiden/publicationclassification) and small-graph notes under `cwts_synthetic_test/README.md` in this folder).
"""
    )
)

nb = {
    "nbformat": 4,
    "nbformat_minor": 5,
    "metadata": {
        "kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
        "language_info": {"name": "python", "version": "3.10.0"},
    },
    "cells": cells,
}

OUT.write_text(json.dumps(nb, indent=1), encoding="utf-8")
print("Wrote", OUT)
