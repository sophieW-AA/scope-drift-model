"""Quick script to show Gini coefficients for CWTS clustering."""
import numpy as np
from google.cloud import bigquery

BQ_PROJECT = "ocean-tech-adv-analytics-c-tfs"
TBL_CLASSIF = "ocean-tech-adv-analytics-c-tfs.scope_drift_raw.classification_raw_20260617_120737"
TBL_PUB_META = "ocean-tech-adv-analytics-c-tfs.scope_drift_raw.pub_metadata_raw_20260617_135005"

JOURNALS = [
    "Frontiers in Immunology",
    "Frontiers in Public Health",
    "Frontiers in Medicine",
    "Frontiers in Oncology",
    "Frontiers in Psychology",
]

def calculate_gini(sizes):
    if not sizes or len(sizes) == 0:
        return 1.0
    sizes = sorted(sizes)
    n = len(sizes)
    total = sum(sizes)
    if total == 0:
        return 1.0
    gini = (2 * sum((i + 1) * s for i, s in enumerate(sizes)) - (n + 1) * total) / (n * total)
    return gini

def calculate_balance(sizes):
    if not sizes or len(sizes) == 1:
        return 0.0
    total = sum(sizes)
    probs = [s / total for s in sizes]
    entropy = -sum(p * np.log(p) for p in probs if p > 0)
    max_entropy = np.log(len(sizes))
    return entropy / max_entropy if max_entropy > 0 else 0.0

def main():
    client = bigquery.Client(project=BQ_PROJECT)
    journals_str = ", ".join(f"'{j}'" for j in JOURNALS)

    print("=" * 60)
    print("CWTS CLUSTERING METRICS")
    print("=" * 60)
    
    for level in ["micro", "meso", "macro"]:
        query = f"""
        SELECT c.{level} AS cluster, COUNT(*) AS size
        FROM `{TBL_CLASSIF}` c
        JOIN `{TBL_PUB_META}` m ON c.int_id = m.int_id
        WHERE m.journal IN ({journals_str})
        GROUP BY c.{level}
        ORDER BY size DESC
        """
        df = client.query(query).to_dataframe()
        sizes = df["size"].tolist()
        
        total = sum(sizes)
        gini = calculate_gini(sizes)
        balance = calculate_balance(sizes)
        
        print(f"\n{level.upper()} LEVEL")
        print("-" * 40)
        print(f"  Clusters:          {len(sizes)}")
        print(f"  Total papers:      {total:,}")
        print(f"  Gini coefficient:  {gini:.4f}")
        print(f"  Balance score:     {balance:.4f}")
        print(f"  Largest cluster:   {max(sizes):,} ({100*max(sizes)/total:.1f}%)")
        print(f"  Smallest cluster:  {min(sizes):,} ({100*min(sizes)/total:.2f}%)")
        print(f"\n  Size distribution:")
        for i, row in df.iterrows():
            pct = 100 * row["size"] / total
            bar = "#" * int(pct / 2)
            print(f"    Cluster {int(row['cluster']):>2}: {int(row['size']):>6,} ({pct:>5.1f}%) {bar}")

if __name__ == "__main__":
    main()
