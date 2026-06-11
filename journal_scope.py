"""
journal_scope.py
================
Analyses the research scope of specific Frontiers journals using CWTS cluster
assignments, and computes Out-of-Scope (OOS) rates at each classification level.

A paper is classified as Out-of-Scope when it falls outside the journal's
"core cluster set" — the minimum set of clusters (ranked by paper count) that
together account for at least SCOPE_THRESHOLD of the journal's total papers.

Reads:
    cwts_output/classification.txt   (int_id TAB micro TAB meso TAB macro)
    cwts_output/pub_titles.txt       (int_id TAB title)
    cwts_output/journal_papers.txt   (int_id TAB journal)   ← join key

int_id is the CWTS sequential ID. To get airak PublicationId for taxonomy
joins, use pub_metadata.txt which contains both int_id and pub_id.

Writes:
    cwts_output/journal_scope.csv    journal-level summary + OOS rates
    cwts_output/paper_oos_flags.csv  paper-level OOS flags + cluster IDs
    cwts_output/scope_descriptions.csv  GPT-generated scope statements (optional)

Usage:
    export OPENAI_API_KEY=sk-...
    python journal_scope.py [--no-gpt]
"""

import json
import os
import sys
import time
import urllib.request
from pathlib import Path
from collections import defaultdict

import pandas as pd

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------
OUTPUT_DIR = Path("cwts_output")
OPENAI_MODEL = "gpt-4o-mini"

TARGET_JOURNALS = []  # empty = all journals

# Which cluster level to use for scope calculation
# "meso" gives better granularity than "macro"; "micro" is often too fine
SCOPE_LEVEL = "meso"

# Cumulative paper share that defines the "core" clusters for a journal.
# E.g. 0.80 → the top clusters that together hold 80% of the journal's papers
# are "in-scope"; everything else is OOS.
SCOPE_THRESHOLD = 0.80

# Journals with fewer papers than this are excluded (too noisy)
MIN_PAPERS = 50

# How many titles to sample per journal when generating GPT scope descriptions
GPT_SAMPLE_N = 100
RANDOM_SEED = 42

RETRY_ATTEMPTS = 3
RETRY_DELAY = 5


SCOPE_PROMPT = """You are a research librarian. Based on the sample titles below from a single academic journal, write a concise scope statement (2-4 sentences) that describes what topics this journal covers.

Then list the 5-10 most representative research topics as keywords.

Respond ONLY with a JSON object:
{
  "scope_statement": "This journal publishes research on ...",
  "core_topics": ["Topic 1", "Topic 2", ...]
}"""

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def call_openai(system: str, user: str) -> str:
    key = os.environ.get("OPENAI_API_KEY")
    if not key:
        raise RuntimeError("OPENAI_API_KEY is not set")

    body = json.dumps(
        {
            "model": OPENAI_MODEL,
            "max_tokens": 500,
            "temperature": 0.1,
            "response_format": {"type": "json_object"},
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
        }
    ).encode("utf-8")

    req = urllib.request.Request(
        "https://api.openai.com/v1/chat/completions",
        data=body,
        headers={
            "Authorization": f"Bearer {key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )

    for attempt in range(1, RETRY_ATTEMPTS + 1):
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                data = json.loads(resp.read().decode("utf-8"))
            return data["choices"][0]["message"]["content"].strip()
        except Exception as e:
            print(f"    [attempt {attempt}/{RETRY_ATTEMPTS}] OpenAI error: {e}")
            if attempt < RETRY_ATTEMPTS:
                time.sleep(RETRY_DELAY)

    raise RuntimeError(f"OpenAI call failed after {RETRY_ATTEMPTS} attempts")


def compute_core_clusters(paper_counts: dict, threshold: float) -> set:
    """
    Return the minimum set of cluster IDs (ranked by descending paper count)
    whose combined papers >= threshold * total_papers.
    """
    total = sum(paper_counts.values())
    ranked = sorted(paper_counts.items(), key=lambda x: x[1], reverse=True)
    core, cumulative = set(), 0
    for cluster_id, count in ranked:
        core.add(cluster_id)
        cumulative += count
        if cumulative / total >= threshold:
            break
    return core


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main():
    use_gpt = "--no-gpt" not in sys.argv

    # ── Load data ────────────────────────────────────────────────────────────
    classif_path = OUTPUT_DIR / "classification.txt"
    titles_path = OUTPUT_DIR / "pub_titles.txt"
    core_path = OUTPUT_DIR / "frontiers_core.txt"

    for p in [classif_path, titles_path, core_path]:
        if not p.exists():
            raise FileNotFoundError(f"Required file not found: {p}")

    print("Loading classification...")
    classif = pd.read_csv(
        classif_path,
        sep="\t",
        header=None,
        names=["int_id", "micro", "meso", "macro"],
    )

    print("Loading titles...")
    titles = pd.read_csv(
        titles_path,
        sep="\t",
        header=None,
        names=["int_id", "title"],
    )

    print("Loading journal assignments...")
    core = pd.read_csv(
        core_path,
        sep="\t",
        header=None,
        names=["int_id", "is_frontiers", "journal"],
    )

    if TARGET_JOURNALS:
        core = core[core["journal"].isin(TARGET_JOURNALS)]

    # ── Merge ────────────────────────────────────────────────────────────────
    df = classif.merge(titles, on="int_id", how="inner").merge(
        core[["int_id", "journal"]], on="int_id", how="inner"
    )
    print(
        f"Merged: {len(df):,} publications across {df['journal'].nunique():,} journals"
    )

    # ── Filter by minimum paper count ────────────────────────────────────────
    counts = df["journal"].value_counts()
    included = counts[counts >= MIN_PAPERS].index
    df = df[df["journal"].isin(included)].copy()
    print(
        f"After MIN_PAPERS={MIN_PAPERS} filter: {df['journal'].nunique():,} journals, {len(df):,} papers"
    )

    # ── Compute scope + OOS per journal ──────────────────────────────────────
    print(
        f"\nComputing scope at '{SCOPE_LEVEL}' level (threshold={SCOPE_THRESHOLD:.0%})..."
    )

    journal_rows = []
    paper_flags = []

    for journal, group in df.groupby("journal"):
        # Count papers per cluster at the chosen level
        cluster_counts = group[SCOPE_LEVEL].value_counts().to_dict()
        core_clusters = compute_core_clusters(cluster_counts, SCOPE_THRESHOLD)

        n_total = len(group)
        n_core = group[SCOPE_LEVEL].isin(core_clusters).sum()
        n_oos = n_total - n_core
        oos_rate = n_oos / n_total

        # Distribution string for inspection
        top5 = sorted(cluster_counts.items(), key=lambda x: x[1], reverse=True)[:5]
        top5_str = ", ".join(f"{cid}({cnt})" for cid, cnt in top5)

        journal_rows.append(
            {
                "journal": journal,
                "n_papers": n_total,
                "n_core_clusters": len(core_clusters),
                "core_clusters": sorted(core_clusters),
                "n_in_scope": int(n_core),
                "n_oos": int(n_oos),
                "oos_rate": round(oos_rate, 4),
                "top5_clusters": top5_str,
                "scope_level": SCOPE_LEVEL,
                "scope_threshold": SCOPE_THRESHOLD,
            }
        )

        # Paper-level flags
        for _, row in group.iterrows():
            paper_flags.append(
                {
                    "int_id": row["int_id"],
                    "journal": journal,
                    "micro": row["micro"],
                    "meso": row["meso"],
                    "macro": row["macro"],
                    "title": row["title"],
                    "is_oos": int(row[SCOPE_LEVEL] not in core_clusters),
                }
            )

        print(
            f"  {journal:<40s} n={n_total:>6,}  "
            f"core_clusters={len(core_clusters):>3}  OOS={oos_rate:.1%}"
        )

    scope_df = pd.DataFrame(journal_rows).sort_values("oos_rate", ascending=False)
    flags_df = pd.DataFrame(paper_flags)

    # ── GPT scope descriptions ────────────────────────────────────────────────
    if use_gpt:
        print("\nGenerating GPT scope descriptions...")
        gpt_rows = []
        for journal, group in df.groupby("journal"):
            sample = (
                group["title"]
                .dropna()
                .sample(min(GPT_SAMPLE_N, len(group)), random_state=RANDOM_SEED)
                .tolist()
            )
            user_prompt = f"Journal: {journal}\n\n" "Sample titles:\n" + "\n".join(
                f"- {t}" for t in sample
            )
            try:
                raw = call_openai(SCOPE_PROMPT, user_prompt)
                parsed = json.loads(raw)
                gpt_rows.append(
                    {
                        "journal": journal,
                        "scope_statement": parsed.get("scope_statement", ""),
                        "core_topics": ", ".join(parsed.get("core_topics", [])),
                    }
                )
                print(f"  {journal}: {parsed.get('scope_statement','')[:80]}...")
            except Exception as e:
                print(f"  {journal}: GPT failed — {e}")
                gpt_rows.append(
                    {"journal": journal, "scope_statement": "ERROR", "core_topics": ""}
                )

        gpt_df = pd.DataFrame(gpt_rows)
        scope_df = scope_df.merge(gpt_df, on="journal", how="left")

    # ── Save outputs ──────────────────────────────────────────────────────────
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    scope_path = OUTPUT_DIR / "journal_scope.csv"
    flags_path = OUTPUT_DIR / "paper_oos_flags.csv"

    scope_df.to_csv(scope_path, index=False)
    flags_df.to_csv(flags_path, index=False)

    print(f"\nSaved journal scope → {scope_path}  ({len(scope_df):,} journals)")
    print(f"Saved paper flags   → {flags_path}  ({len(flags_df):,} papers)")

    # ── Summary stats ─────────────────────────────────────────────────────────
    print("\n── Summary ──────────────────────────────────────────────────────")
    print(f"Journals analysed:        {len(scope_df):,}")
    print(f"Mean OOS rate:            {scope_df['oos_rate'].mean():.1%}")
    print(f"Median OOS rate:          {scope_df['oos_rate'].median():.1%}")
    print(f"Journals with OOS > 20%:  {(scope_df['oos_rate'] > 0.20).sum():,}")
    print(f"Journals with OOS > 40%:  {(scope_df['oos_rate'] > 0.40).sum():,}")

    print("\nTop 10 highest OOS journals:")
    print(
        scope_df[["journal", "n_papers", "n_core_clusters", "oos_rate"]]
        .head(10)
        .to_string(index=False)
    )

    print("\nTop 10 lowest OOS journals (tightest scope):")
    print(
        scope_df[["journal", "n_papers", "n_core_clusters", "oos_rate"]]
        .tail(10)
        .to_string(index=False)
    )

    print("\nDone.")


if __name__ == "__main__":
    main()
