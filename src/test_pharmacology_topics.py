"""
Test Clarivate topic matching on all 5 Frontiers test journals.
Compares our title+abstract-based assignment with Clarivate's ground truth.
"""

import os
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from google.cloud import bigquery
import pandas as pd
from clarivate_title_matching import ClarivateTopicMatcher

# Config
BQ_PROJECT = "ocean-breeze-tier-1"
AIRAK_DATASET = "ocean-breeze-tier-1.airak"
YEAR_RANGE = (2020, 2025)  # Last 5 years

# All 5 Frontiers test journals
TEST_JOURNALS = {
    "Pharmacology": 910533066753,
    "Oncology": 2972117368834,
    "Public Health": 2379411881984,
    "Immunology": 3315714752512,
    "Psychology": 2405181685761,
}


def get_journal_papers(journal_id: int, journal_name: str) -> pd.DataFrame:
    """Fetch papers with titles and abstracts for a specific journal."""
    print(f"\nQuerying Frontiers in {journal_name} papers ({YEAR_RANGE[0]}-{YEAR_RANGE[1]})...")
    
    client = bigquery.Client(project=BQ_PROJECT)
    
    query = f"""
    SELECT 
        p.PublicationId,
        p.Title,
        pa.Abstract,
        p.PublishedYear
    FROM `{AIRAK_DATASET}.Publication` p
    LEFT JOIN `{AIRAK_DATASET}.PublicationAbstract` pa ON p.PublicationId = pa.PublicationId
    WHERE p.JournalId = {journal_id}
      AND p.PublishedYear BETWEEN {YEAR_RANGE[0]} AND {YEAR_RANGE[1]}
      AND p.Title IS NOT NULL
      AND LENGTH(p.Title) > 10
    """
    
    df = client.query(query).to_dataframe()
    
    # Combine title and abstract for matching
    df["TextForMatching"] = df.apply(
        lambda row: f"{row['Title']} {row['Abstract'] or ''}"[:2000],  # Limit length
        axis=1
    )
    
    n_with_abstract = df["Abstract"].notna().sum()
    print(f"Found {len(df):,} papers ({n_with_abstract:,} with abstracts)")
    return df


def process_journal(journal_name: str, journal_id: int, matcher: ClarivateTopicMatcher) -> pd.DataFrame:
    """Process a single journal and return topic distribution."""
    # Get papers
    df_papers = get_journal_papers(journal_id, journal_name)
    papers = df_papers.to_dict("records")
    
    # Get topic distribution
    print(f"Assigning {len(papers):,} papers to Clarivate topics...")
    dist = matcher.get_topic_distribution(papers, level="meso", title_field="TextForMatching", top_n=30)
    
    # Add journal info
    dist["journal"] = journal_name
    dist["total_papers"] = len(papers)
    
    return dist


def main():
    # Initialize matcher (once for all journals)
    print("Initializing Clarivate topic matcher...")
    matcher = ClarivateTopicMatcher()
    
    all_results = []
    
    # Process each journal
    for journal_name, journal_id in TEST_JOURNALS.items():
        print("\n" + "=" * 70)
        print(f"Processing: Frontiers in {journal_name}")
        print("=" * 70)
        
        dist = process_journal(journal_name, journal_id, matcher)
        all_results.append(dist)
        
        # Print top 10 for this journal
        print(f"\nTop 10 Meso Topics for Frontiers in {journal_name}:")
        print(f"{'Rank':<5} {'Topic':<50} {'Count':<8} {'%':<6}")
        print("-" * 70)
        
        for i, row in dist.head(10).iterrows():
            print(f"{i+1:<5} {row['topic'][:50]:<50} {row['count']:<8} {row['percentage']:<6.2f}")
    
    # Combine all results
    combined = pd.concat(all_results, ignore_index=True)
    
    # Save combined results
    output_path = Path(__file__).parent.parent / "output" / "all_journals_topic_distribution.csv"
    combined.to_csv(output_path, index=False)
    print(f"\n\nCombined results saved to: {output_path}")
    
    # Save individual journal CSVs
    for journal_name in TEST_JOURNALS.keys():
        journal_dist = combined[combined["journal"] == journal_name]
        journal_path = Path(__file__).parent.parent / "output" / f"{journal_name.lower()}_topic_distribution.csv"
        journal_dist.to_csv(journal_path, index=False)
        print(f"Saved: {journal_path}")
    
    # Print summary
    print("\n" + "=" * 70)
    print("SUMMARY - Top Meso Topic per Journal")
    print("=" * 70)
    print(f"{'Journal':<20} {'Top Topic':<45} {'%':<6}")
    print("-" * 70)
    
    for journal_name in TEST_JOURNALS.keys():
        journal_dist = combined[combined["journal"] == journal_name]
        if len(journal_dist) > 0:
            top = journal_dist.iloc[0]
            print(f"{journal_name:<20} {top['topic'][:45]:<45} {top['percentage']:<6.2f}")


if __name__ == "__main__":
    main()
