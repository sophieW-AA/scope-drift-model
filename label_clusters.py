"""
label_clusters.py
=================
Labels CWTS classification output using OpenAI API.

Reads:
    cwts_output/classification.txt
    cwts_output/pub_metadata.txt

Writes:
    cwts_output/micro_labels.csv
    cwts_output/meso_labels.csv
    cwts_output/macro_labels.csv

Usage:
    export OPENAI_API_KEY=sk-...
    python label_clusters.py
"""

import json
import os
import time
import urllib.request
from pathlib import Path

import pandas as pd

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------
OPENAI_MODEL = "gpt-4o-mini"  # cheap and good enough; swap to gpt-4o if needed
TOP_N_TITLES = 250  # titles sampled per cluster
RANDOM_SEED = 42
RETRY_ATTEMPTS = 3
RETRY_DELAY = 5  # seconds between retries
OUTPUT_DIR = Path("cwts_output")

# LEVELS = ["micro", "meso", "macro"]
LEVELS = ["macro"]

# ---------------------------------------------------------------------------
# System prompt 1
# ---------------------------------------------------------------------------
SYSTEM_PROMPT = """You are a research librarian classifying a cluster of academic papers into a single topic. You will be provided with the titles of a representative sample of papers from a larger cluster of related scientific papers.

Your task is to identify the topic of the entire cluster based on the titles of the representative papers. Identify the single broad research area that best describes the majority of these papers, not just the most distinctive or novel sub-theme. Some papers in the sample may be off-topic outliers — ignore them.
Focus only on the papers that clearly belong together.

Output the following items (in English) that describe the topic of the cluster: 'short label' (at most 3 words and format in Title Case), 'long label' (at most 8 words and format in Title Case), list of 10 'keywords' (ordered by relevance and format in Title Case), 'summary' (few sentences), and 'wikipedia page' (URL).
Do not start short and long labels with the word "The".

Respond with ONLY a JSON object with these exact keys:
{
  "short_label": "2-3 words, Title Case, no leading 'The'",
  "long_label": "at most 8 words, Title Case, no leading 'The'",
  "keywords": ["10", "Keywords", "Ordered", "By", "Relevance", "In", "Title", "Case"],
  "summary": "This cluster of papers focuses on...",
  "wikipedia_page": "https://en.wikipedia.org/wiki/...",
  "coverage_pct": 80
}

coverage_pct is your estimate of what percentage of the sample papers fit the chosen label (integer, 0-100).
Do not include markdown fences or any text outside the JSON
"""
# ---------------------------------------------------------------------------
# Improved System Prompt (Solves the "Too Narrow" labeling bug) 2
# ---------------------------------------------------------------------------
# SYSTEM_PROMPT = """You are a research librarian classifying a cluster of academic papers.

# Your goal: find the single academic field or discipline that covers the MAJORITY of these papers.

# Rules:
# - Choose the PARENT DISCIPLINE, not the most distinctive sub-topic.
# - If papers span cancer, neurology, immunology and surgery → label it "Medical Sciences", not "Cancer Research".
# - If papers span geopolymers, steel, concrete and composites → label it "Construction & Engineering Materials", not "Geopolymer Concrete".
# - Some papers will be off-topic outliers — ignore them.
# - A good label covers at least 70% of papers.

# Before finalising, check: would a paper about the least distinctive topic in the sample still fit under this label? If not, go one level up. Avoid using a label that has already been assigned to another cluster — be more specific if needed

# Output a JSON object with these exact keys:
# {
#   "short_label": "at most 3 words, Title Case, no leading 'The'",
#   "long_label": "at most 8 words, Title Case, no leading 'The'",
#   "keywords": ["10", "Keywords", "Ordered", "By", "Relevance", "In", "Title", "Case"],
#   "summary": "This cluster of papers focuses on...",
#   "wikipedia_page": "URL"
# }

# # Do not include markdown fences or any explanation outside the JSON."""
# CWTS SYSTEM PROMPT 3
# SYSTEM_PROMPT = """You will be provided with the titles of a representative sample of papers from a larger cluster of related scientific papers.

# Your task is to identify the topic of the entire cluster based on the titles of the representative papers.

# Output the following items (in English) that describe the topic of the cluster: 'short label' (at most 3 words and format in Title Case), 'long label' (at most 8 words and format in Title Case), list of 10 'keywords' (ordered by relevance and format in Title Case), 'summary' (few sentences), and 'wikipedia page' (URL).
# Do not start short and long labels with the word "The".
# Start each summary with "This cluster of papers".
# # Output a JSON object with these exact keys:
# # {
# #   "short_label": "at most 3 words, Title Case, no leading 'The'",
# #   "long_label": "at most 8 words, Title Case, no leading 'The'",
# #   "keywords": ["10", "Keywords", "Ordered", "By", "Relevance", "In", "Title", "Case"],
# #   "summary": "This cluster of papers focuses on...",
# #   "wikipedia_page": "URL"
# # }

# # Do not include markdown fences or any explanation outside the JSON."""


# ---------------------------------------------------------------------------
# OpenAI call (no external packages)
# ---------------------------------------------------------------------------
def call_openai(user_prompt: str) -> str:
    key = os.environ.get("OPENAI_API_KEY")
    # key = "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"
    if not key:
        raise RuntimeError("OPENAI_API_KEY environment variable is not set")

    body = json.dumps(
        {
            "model": OPENAI_MODEL,
            "max_tokens": 600,
            "temperature": 0.1,
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt},
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
            print(f"    [attempt {attempt}/{RETRY_ATTEMPTS}] Error: {e}")
            if attempt < RETRY_ATTEMPTS:
                time.sleep(RETRY_DELAY)

    raise RuntimeError(f"OpenAI call failed after {RETRY_ATTEMPTS} attempts")


# ---------------------------------------------------------------------------
# Label one level
# ---------------------------------------------------------------------------
def label_level(merged: pd.DataFrame, level: str) -> pd.DataFrame:
    groups = merged.groupby(level)
    total = len(groups)
    results = []

    print(f"\n--- Labelling {level} ({total} clusters) ---")

    for i, (cluster_id, group) in enumerate(groups, 1):
        titles = group["title"].dropna().tolist()
        sample = (
            group["title"]
            .dropna()
            .sample(min(TOP_N_TITLES, len(titles)), random_state=RANDOM_SEED)
            .tolist()
        )
        titles_str = "\n".join(f"- {t}" for t in sample)

        user_prompt = (
            f"This cluster contains {len(titles):,} academic papers. "
            f"Here is a sample of their titles:\n\n{titles_str}"
        )

        try:
            raw = call_openai(user_prompt)
            out = json.loads(raw)
        except json.JSONDecodeError:
            print(f"  [{i}/{total}] cluster {cluster_id} — bad JSON, storing raw")
            out = {"short_label": raw, "long_label": "", "keywords": []}
        except Exception as e:
            print(f"  [{i}/{total}] cluster {cluster_id} — failed: {e}")
            out = {"short_label": "ERROR", "long_label": str(e), "keywords": []}

        out["level"] = level
        out["cluster_id"] = cluster_id
        out["n_papers"] = len(titles)
        results.append(out)

        print(
            f"  [{i}/{total}] cluster {cluster_id} ({len(titles):,} papers) → {out.get('short_label')}"
        )

    return pd.DataFrame(results)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    # Load files
    classif_path = OUTPUT_DIR / "classification.txt"
    titles_path = OUTPUT_DIR / "pub_metadata.txt"
    cit_links_path = OUTPUT_DIR / "cit_links.txt"

    if not classif_path.exists():
        raise FileNotFoundError(f"Not found: {classif_path}")
    if not titles_path.exists():
        raise FileNotFoundError(f"Not found: {titles_path}")
    if not cit_links_path.exists():
        raise FileNotFoundError(f"Not found: {cit_links_path}")

    print("Loading classification...")
    classif = pd.read_csv(
        classif_path,
        sep="\t",
        header=None,
        names=["pub_no", "micro", "meso", "macro"],
    )

    print("Loading titles...")
    titles = pd.read_csv(
        titles_path,
        sep="\t",
        header=None,
        names=["pub_no", "title"],
    )

    print("Loading citation links...")
    cit_links = pd.read_csv(
        cit_links_path,
        sep="\t",
        header=None,
        names=["pub_no1", "pub_no2", "weight"],
    )

    print("Calculating citation counts...")
    # Group by pub_no1 and sum the weights to get the total citation/link strength for each paper.
    # Since the CWTS network is symmetricized, the degree (sum of weights) of pub_no1 is
    # a perfect proxy for overall citation impact inside the network.
    cit_counts = (
        cit_links.groupby("pub_no1")["weight"]
        .sum()
        .reset_index()
        .rename(columns={"pub_no1": "pub_no", "weight": "citation_count"})
    )

    # Merge classification, titles, and citation counts
    merged = classif.merge(titles, on="pub_no")
    merged = merged.merge(cit_counts, on="pub_no", how="left")
    merged["citation_count"] = merged["citation_count"].fillna(0)

    print(f"Merged: {len(merged):,} publications")
    # Label each level
    for level in LEVELS:
        df_labels = label_level(merged, level)
        out_path = OUTPUT_DIR / f"{level}_labels.csv"
        df_labels.to_csv(out_path, index=False)
        print(f"\nSaved → {out_path}")

    print("\nDone.")


if __name__ == "__main__":
    main()
