"""
label_clusters.py
=================
Labels CWTS classification output using OpenAI API.

Data source: BigQuery tables in scope_drift_raw dataset
    - classification_raw_{timestamp}
    - pub_metadata_raw_{timestamp}
    - cit_links_raw_{timestamp}

The int_id column (0..N-1) is used by the CWTS Java tool. The pub_id
column contains the original BigQuery PublicationId, enabling joins with
taxonomy tables (e.g. aa_taxonomy.article_taxonomy_scores_current).

Writes:
    cwts_output/micro_labels.csv
    cwts_output/meso_labels.csv
    cwts_output/macro_labels.csv

Usage:
    export OPENAI_API_KEY=sk-...
    export RUN_TIMESTAMP=20260618_130306
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

LEVELS = ["macro"]
# LEVELS = ["macro"]

# ---------------------------------------------------------------------------
# BigQuery Config
# ---------------------------------------------------------------------------
BQ_PROJECT = "ocean-tech-adv-analytics-c-tfs"
BQ_DATASET = "scope_drift_raw"


def get_table_names(run_timestamp: str) -> dict:
    """Construct BigQuery table names from run timestamp."""
    if not run_timestamp:
        raise ValueError("run_timestamp must be provided")
    return {
        "classification": f"{BQ_PROJECT}.{BQ_DATASET}.classification_raw_{run_timestamp}",
        "pub_metadata": f"{BQ_PROJECT}.{BQ_DATASET}.pub_metadata_raw_{run_timestamp}",
        "cit_links": f"{BQ_PROJECT}.{BQ_DATASET}.cit_links_raw_{run_timestamp}",
    }


# ---------------------------------------------------------------------------
# System prompt 1
# ---------------------------------------------------------------------------
# SYSTEM_PROMPT = """You are a research librarian classifying a cluster of academic papers into a single topic. You will be provided with the titles of a representative sample of papers from a larger cluster of related scientific papers.

# Your task is to identify the topic of the entire cluster based on the titles of the representative papers. Identify the single broad research area that best describes the majority of these papers, not just the most distinctive or novel sub-theme. Some papers in the sample may be off-topic outliers — ignore them.
# Focus only on the papers that clearly belong together.

# Output the following items (in English) that describe the topic of the cluster: 'short label' (at most 3 words and format in Title Case), 'long label' (at most 8 words and format in Title Case), list of 10 'keywords' (ordered by relevance and format in Title Case), 'summary' (few sentences), and 'wikipedia page' (URL).
# Do not start short and long labels with the word "The".

# Respond with ONLY a JSON object with these exact keys:
# {
#   "short_label": "2-3 words, Title Case, no leading 'The'",
#   "long_label": "at most 8 words, Title Case, no leading 'The'",
#   "keywords": ["10", "Keywords", "Ordered", "By", "Relevance", "In", "Title", "Case"],
#   "summary": "This cluster of papers focuses on...",
#   "wikipedia_page": "https://en.wikipedia.org/wiki/...",
#   "coverage_pct": 80
# }

# coverage_pct is your estimate of what percentage of the sample papers fit the chosen label (integer, 0-100).
# Do not include markdown fences or any text outside the JSON
# """

# ---------------------------------------------------------------------------
# System prompt 2
# ---------------------------------------------------------------------------
SYSTEM_PROMPT = """You are a senior bibliometrician and research librarian classifying a cluster of academic papers. You will be provided with a list of titles from a representative sample of papers.

Your task is to identify the single, cohesive core topic that unites the majority of these papers. 

To ensure accuracy, follow these analytical steps before deciding on your labels:
1. Scan all titles and identify the "lowest common denominator" — the fundamental scientific domain or methodology shared by most papers, even if some use novel or interdisciplinary terms.
2. Guard against "Novelty Bias": Do not let highly specific, trendy, or catchy sub-themes (e.g., a few papers mentioning "Machine Learning" or "Agriculture" in a power engineering cluster) override the broader, dominant theme of the collection.
3. Identify outlier papers that do not fit the main theme. 

Constraints:
- 'short_label': At most 3 words, Title Case. Do not start with "The".
- 'long_label': At most 8 words, Title Case. Do not start with "The".
- 'keywords': 10 distinct, relevant keywords in Title Case, ordered from most central to least.
- 'summary': 2-3 sentences explaining the core focus of the cluster and its main applications.
- 'wikipedia_page': A real, highly relevant Wikipedia URL. If no exact match exists, use the closest broad field (e.g., https://en.wikipedia.org/wiki/Control_engineering instead of a specific algorithm).
- 'coverage_pct': An integer (0-100) representing your estimate of the percentage of papers that fit your labels. 

Respond with ONLY a JSON object with these exact keys. You must include a "reasoning_steps" key at the top of the JSON to do your thinking before outputting the final labels:

{
  "reasoning_steps": "Briefly list: 1. The dominant 2-3 methods/themes seen across the list. 2. Any noisy outliers. 3. Why your chosen label is the most accurate broad umbrella.",
  "short_label": "Title Case Label",
  "long_label": "Title Case Broad Label Description",
  "keywords": ["Keyword1", "Keyword2", "Keyword3", "Keyword4", "Keyword5", "Keyword6", "Keyword7", "Keyword8", "Keyword9", "Keyword10"],
  "summary": "This cluster of papers focuses on...",
  "wikipedia_page": "https://en.wikipedia.org/wiki/...",
  "coverage_pct": 80
}

Do not include markdown fences, preambles, or any text outside the JSON block."""


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
# Main
# ---------------------------------------------------------------------------
def main(run_timestamp: str):
    """
    Label CWTS clusters using GPT.

    Args:
        run_timestamp: The timestamp suffix for BigQuery tables (e.g., "20260618_130306")
    """
    import pandas_gbq

    tables = get_table_names(run_timestamp)
    print(f"Loading from BigQuery (run_timestamp={run_timestamp})...")
    print(f"  Classification: {tables['classification']}")
    print(f"  Pub metadata:   {tables['pub_metadata']}")
    print(f"  Cit links:      {tables['cit_links']}")

    # Optional: Load citation links if needed for weighted sampling or other purposes
    # Uncomment below to load cit_links and compute citation counts per paper
    # -------------------------------------------------------------------------
    # print("Loading citation links...")
    # cit_links = pandas_gbq.read_gbq(
    #     f"SELECT int_id1, int_id2, weight FROM `{tables['cit_links']}`",
    #     project_id=BQ_PROJECT,
    # )
    # print(f"  Loaded {len(cit_links):,} rows")
    # cit_counts = (
    #     cit_links.groupby("int_id1")["weight"]
    #     .sum()
    #     .reset_index()
    #     .rename(columns={"int_id1": "int_id", "weight": "citation_count"})
    # )
    # -------------------------------------------------------------------------

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    for level in LEVELS:
        print(f"\n{'='*60}")
        print(f"Processing {level} level...")
        print(f"{'='*60}")
        
        # Efficient query: only fetch sampled titles per cluster
        # Uses window function to randomly sample TOP_N_TITLES per cluster
        query = f"""
        WITH ranked AS (
            SELECT 
                c.{level} as cluster_id,
                m.title,
                ROW_NUMBER() OVER (
                    PARTITION BY c.{level} 
                    ORDER BY FARM_FINGERPRINT(CONCAT(CAST(c.int_id AS STRING), '{RANDOM_SEED}'))
                ) as rn
            FROM `{tables['classification']}` c
            JOIN `{tables['pub_metadata']}` m ON c.int_id = m.int_id
            WHERE m.title IS NOT NULL
        ),
        cluster_counts AS (
            SELECT {level} as cluster_id, COUNT(*) as n_papers
            FROM `{tables['classification']}`
            GROUP BY {level}
        )
        SELECT 
            r.cluster_id,
            r.title,
            cc.n_papers
        FROM ranked r
        JOIN cluster_counts cc ON r.cluster_id = cc.cluster_id
        WHERE r.rn <= {TOP_N_TITLES}
        ORDER BY r.cluster_id, r.rn
        """
        
        print(f"  Fetching up to {TOP_N_TITLES} titles per cluster...")
        df = pandas_gbq.read_gbq(query, project_id=BQ_PROJECT)
        
        n_clusters = df['cluster_id'].nunique()
        print(f"  Loaded {len(df):,} titles across {n_clusters} clusters")
        
        # Label this level
        df_labels = label_level_efficient(df, level)
        out_path = OUTPUT_DIR / f"{level}_labels.csv"
        df_labels.to_csv(out_path, index=False)
        print(f"\nSaved → {out_path}")

    print("\nDone.")


def label_level_efficient(df: pd.DataFrame, level: str) -> pd.DataFrame:
    """Label clusters from pre-sampled data with two-pass duplicate handling."""
    groups = df.groupby('cluster_id')
    total = len(groups)
    results = []
    
    # Store group data for potential retry
    group_data = {cluster_id: group for cluster_id, group in groups}

    print(f"\n--- Pass 1: Labelling {level} ({total} clusters) ---")

    for i, (cluster_id, group) in enumerate(group_data.items(), 1):
        titles = group["title"].tolist()
        n_papers = group["n_papers"].iloc[0]
        
        titles_str = "\n".join(f"- {t}" for t in titles)

        user_prompt = (
            f"This cluster contains {n_papers:,} academic papers. "
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
        out["n_papers"] = n_papers
        results.append(out)

        print(
            f"  [{i}/{total}] cluster {cluster_id} ({n_papers:,} papers) → {out.get('short_label')}"
        )

    # Pass 2: Resolve duplicates
    results = resolve_duplicate_labels(results, group_data, level)
    
    return pd.DataFrame(results)


def resolve_duplicate_labels(results: list, group_data: dict, level: str) -> list:
    """
    Detect duplicate short_labels and retry conflicting clusters.
    Keeps the cluster with the most papers for each duplicate label.
    """
    from collections import defaultdict
    
    # Group results by short_label
    label_to_clusters = defaultdict(list)
    for r in results:
        label = r.get("short_label", "").strip().lower()
        if label and label != "error":
            label_to_clusters[label].append(r)
    
    # Find duplicates
    duplicates = {label: clusters for label, clusters in label_to_clusters.items() 
                  if len(clusters) > 1}
    
    if not duplicates:
        print("\n  No duplicate labels found.")
        return results
    
    print(f"\n--- Pass 2: Resolving {len(duplicates)} duplicate labels ---")
    
    # For each duplicate, keep the one with most papers, retry the rest
    retry_cluster_ids = set()
    taken_labels = set()
    
    for label, clusters in duplicates.items():
        # Sort by n_papers descending, keep the largest
        clusters_sorted = sorted(clusters, key=lambda x: x.get("n_papers", 0), reverse=True)
        keeper = clusters_sorted[0]
        taken_labels.add(keeper.get("short_label", "").strip())
        
        print(f"  Duplicate '{label}': keeping Cluster {keeper['cluster_id']} ({keeper['n_papers']:,} papers), will retry {len(clusters_sorted)-1} others")
        
        for c in clusters_sorted[1:]:
            retry_cluster_ids.add(c["cluster_id"])
    
    # Also add all non-duplicate labels to taken_labels
    for r in results:
        if r["cluster_id"] not in retry_cluster_ids:
            label = r.get("short_label", "").strip()
            if label:
                taken_labels.add(label)
    
    if not retry_cluster_ids:
        return results
    
    # Retry clusters with taken_labels context
    print(f"\n  Retrying {len(retry_cluster_ids)} clusters with {len(taken_labels)} labels already taken...")
    
    results_map = {r["cluster_id"]: r for r in results}
    
    for i, cluster_id in enumerate(sorted(retry_cluster_ids), 1):
        group = group_data[cluster_id]
        titles = group["title"].tolist()
        n_papers = group["n_papers"].iloc[0]
        
        titles_str = "\n".join(f"- {t}" for t in titles)
        
        # Add warning about taken labels
        taken_str = ", ".join(sorted(taken_labels))
        user_prompt = (
            f"This cluster contains {n_papers:,} academic papers. "
            f"Here is a sample of their titles:\n\n{titles_str}\n\n"
            f"IMPORTANT: The following labels are already assigned to other clusters and MUST NOT be used: {taken_str}\n"
            f"You must choose a DIFFERENT, more specific label for this cluster."
        )

        try:
            raw = call_openai(user_prompt)
            out = json.loads(raw)
        except json.JSONDecodeError:
            print(f"  [retry {i}/{len(retry_cluster_ids)}] cluster {cluster_id} — bad JSON")
            out = {"short_label": f"Cluster {cluster_id}", "long_label": "", "keywords": []}
        except Exception as e:
            print(f"  [retry {i}/{len(retry_cluster_ids)}] cluster {cluster_id} — failed: {e}")
            out = {"short_label": f"Cluster {cluster_id}", "long_label": str(e), "keywords": []}

        out["level"] = level
        out["cluster_id"] = cluster_id
        out["n_papers"] = n_papers
        
        old_label = results_map[cluster_id].get("short_label", "")
        new_label = out.get("short_label", "")
        
        # Update taken_labels with new label
        taken_labels.add(new_label.strip())
        
        results_map[cluster_id] = out
        print(f"  [retry {i}/{len(retry_cluster_ids)}] cluster {cluster_id}: '{old_label}' → '{new_label}'")
    
    return list(results_map.values())


if __name__ == "__main__":
    import sys

    # Accept timestamp from command line or environment variable
    if len(sys.argv) > 1:
        ts = sys.argv[1]
    else:
        ts = os.environ.get("RUN_TIMESTAMP", "")
    if not ts:
        print("Usage: python label_clusters.py <run_timestamp>")
        print("   or: RUN_TIMESTAMP=... python label_clusters.py")
        sys.exit(1)
    main(ts)
