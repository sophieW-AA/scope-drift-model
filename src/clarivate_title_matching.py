"""
Clarivate Citation Topic Assignment via Title Matching
=======================================================
Assigns papers to Clarivate's pre-built citation topic hierarchy (10 macro,
326 meso, 2478 micro topics) using TF-IDF similarity on paper titles.

This bypasses Leiden clustering entirely and directly maps papers to the
Clarivate taxonomy, enabling comparison with Clarivate's own topic assignments.

Usage:
    from clarivate_title_matching import ClarivateTopicMatcher
    
    matcher = ClarivateTopicMatcher()
    result = matcher.assign_paper("Phytochemicals targeting autophagy in cancer")
    # Returns: {
    #     "macro": {"id": 1, "topic": "Clinical & Life Sciences", "score": 0.45},
    #     "meso": {"id": 25, "topic": "Molecular & Cell Biology...", "score": 0.38},
    #     "micro": {"id": 797, "topic": "Autophagy", "score": 0.52},
    # }
"""

import logging
from pathlib import Path
from collections import Counter, defaultdict

import pandas as pd
import numpy as np

log = logging.getLogger(__name__)


class ClarivateTopicMatcher:
    """
    Assigns papers to Clarivate citation topics via TF-IDF title matching.
    Supports macro (10), meso (326), and micro (2478) level assignments.
    """
    
    def __init__(self, csv_path: str = None):
        """
        Initialize the matcher by loading Clarivate topics and building TF-IDF models.
        
        Args:
            csv_path: Path to clarivate_citation_topics_2025.csv
                      Defaults to data/clarivate_citation_topics_2025.csv
        """
        if csv_path is None:
            csv_path = Path(__file__).resolve().parent.parent / "data" / "clarivate_citation_topics_2025.csv"
        else:
            csv_path = Path(csv_path)
        
        if not csv_path.exists():
            raise FileNotFoundError(f"Clarivate topics file not found: {csv_path}")
        
        self.topics_df = pd.read_csv(csv_path)
        log.info(f"Loaded {len(self.topics_df)} Clarivate citation topics")
        
        # Build matchers for each level
        self._build_matchers()
    
    def _build_matchers(self):
        """Build TF-IDF vectorizers and topic vectors for each level."""
        try:
            from sklearn.feature_extraction.text import TfidfVectorizer
            from sklearn.metrics.pairwise import cosine_similarity
        except ImportError:
            raise ImportError("scikit-learn is required: pip install scikit-learn")
        
        self.cosine_similarity = cosine_similarity
        self.matchers = {}
        
        # Build macro matcher (10 topics)
        self.matchers["macro"] = self._build_level_matcher("macro")
        
        # Build meso matcher (326 topics)
        self.matchers["meso"] = self._build_level_matcher("meso")
        
        # Build micro matcher (2478 topics)
        self.matchers["micro"] = self._build_level_matcher("micro")
        
        log.info(f"Built matchers: {len(self.matchers['macro']['ids'])} macro, "
                 f"{len(self.matchers['meso']['ids'])} meso, "
                 f"{len(self.matchers['micro']['ids'])} micro topics")
    
    def _build_level_matcher(self, level: str) -> dict:
        """Build TF-IDF matcher for a specific level."""
        from sklearn.feature_extraction.text import TfidfVectorizer
        
        df = self.topics_df
        
        if level == "macro":
            unique = df.drop_duplicates(subset=["Macro ID"])
            texts = []
            ids = []
            names = []
            
            for _, row in unique.iterrows():
                macro_id = row["Macro ID"]
                # Aggregate descriptions from all micro topics under this macro
                macro_rows = df[df["Macro ID"] == macro_id]
                descriptions = " ".join(
                    macro_rows["Micro Description"].dropna().astype(str).tolist()[:30]
                )
                texts.append(f"{row['Macro Topic']} {descriptions}")
                ids.append(macro_id)
                names.append(row["Macro Topic"])
                
        elif level == "meso":
            unique = df.drop_duplicates(subset=["Meso ID"])
            texts = []
            ids = []
            names = []
            
            for _, row in unique.iterrows():
                meso_id = row["Meso ID"]
                # Aggregate descriptions from all micro topics under this meso
                meso_rows = df[df["Meso ID"] == meso_id]
                descriptions = " ".join(
                    meso_rows["Micro Description"].dropna().astype(str).tolist()[:20]
                )
                texts.append(f"{row['Meso Topic']} {row['Macro Topic']} {descriptions}")
                ids.append(meso_id)
                names.append(row["Meso Topic"])
                
        else:  # micro
            texts = []
            ids = []
            names = []
            
            for _, row in df.iterrows():
                text_parts = [
                    str(row.get("Micro Topic", "")),
                    str(row.get("Micro Longer Label", "")),
                    str(row.get("Micro Description", "")),
                ]
                texts.append(" ".join(text_parts))
                ids.append(row["Micro ID"])
                names.append(row["Micro Topic"])
        
        vectorizer = TfidfVectorizer(
            stop_words="english",
            ngram_range=(1, 2),
            max_features=15000,
            min_df=1,
        )
        vectors = vectorizer.fit_transform(texts)
        
        # Build ID to info lookup
        id_to_info = {}
        for i, (topic_id, name) in enumerate(zip(ids, names)):
            row = df[df[f"{level.capitalize()} ID"] == topic_id].iloc[0] if level != "micro" else df[df["Micro ID"] == topic_id].iloc[0]
            id_to_info[topic_id] = {
                "id": topic_id,
                "name": name,
                "macro_id": row.get("Macro ID"),
                "macro_topic": row.get("Macro Topic"),
                "meso_id": row.get("Meso ID") if level in ["meso", "micro"] else None,
                "meso_topic": row.get("Meso Topic") if level in ["meso", "micro"] else None,
            }
        
        return {
            "vectorizer": vectorizer,
            "vectors": vectors,
            "ids": ids,
            "names": names,
            "id_to_info": id_to_info,
        }
    
    def assign_paper(self, title: str, threshold: float = 0.01) -> dict:
        """
        Assign a single paper to Clarivate topics at all levels.
        
        Args:
            title: Paper title
            threshold: Minimum similarity score to accept (default 0.01)
        
        Returns:
            Dict with macro, meso, micro assignments, each containing:
            - id: Clarivate topic ID
            - topic: Topic name
            - score: Similarity score
            - full_info: Complete topic hierarchy info
        """
        if not title or not title.strip():
            return {"macro": None, "meso": None, "micro": None}
        
        result = {}
        
        for level in ["macro", "meso", "micro"]:
            matcher = self.matchers[level]
            
            # Transform title to TF-IDF vector
            query_vec = matcher["vectorizer"].transform([title])
            
            # Compute similarities
            sims = self.cosine_similarity(query_vec, matcher["vectors"])[0]
            
            # Get best match
            best_idx = sims.argmax()
            best_score = float(sims[best_idx])
            
            if best_score >= threshold:
                topic_id = matcher["ids"][best_idx]
                result[level] = {
                    "id": topic_id,
                    "topic": matcher["names"][best_idx],
                    "score": round(best_score, 4),
                    "full_info": matcher["id_to_info"].get(topic_id),
                }
            else:
                result[level] = None
        
        return result
    
    def assign_papers_batch(
        self,
        papers: list[dict],
        title_field: str = "Title",
        id_field: str = "PublicationId",
        threshold: float = 0.01,
    ) -> pd.DataFrame:
        """
        Assign multiple papers to Clarivate topics.
        
        Args:
            papers: List of paper dicts with title and ID fields
            title_field: Key for paper title in dict
            id_field: Key for paper ID in dict
            threshold: Minimum similarity score
        
        Returns:
            DataFrame with columns: paper_id, title, macro_id, macro_topic, macro_score,
            meso_id, meso_topic, meso_score, micro_id, micro_topic, micro_score
        """
        results = []
        
        for i, paper in enumerate(papers):
            paper_id = paper.get(id_field)
            title = str(paper.get(title_field, "")).strip()
            
            assignment = self.assign_paper(title, threshold)
            
            row = {
                "paper_id": paper_id,
                "title": title[:100],
            }
            
            for level in ["macro", "meso", "micro"]:
                if assignment[level]:
                    row[f"{level}_id"] = assignment[level]["id"]
                    row[f"{level}_topic"] = assignment[level]["topic"]
                    row[f"{level}_score"] = assignment[level]["score"]
                else:
                    row[f"{level}_id"] = None
                    row[f"{level}_topic"] = None
                    row[f"{level}_score"] = None
            
            results.append(row)
            
            if (i + 1) % 1000 == 0:
                log.info(f"Assigned {i + 1}/{len(papers)} papers")
        
        return pd.DataFrame(results)
    
    def get_topic_distribution(
        self,
        papers: list[dict],
        level: str = "meso",
        title_field: str = "Title",
        top_n: int = 20,
    ) -> pd.DataFrame:
        """
        Get topic distribution for a set of papers.
        
        Args:
            papers: List of paper dicts
            level: "macro", "meso", or "micro"
            title_field: Key for paper title
            top_n: Number of top topics to return
        
        Returns:
            DataFrame with topic distribution (topic, count, percentage)
        """
        assignments = self.assign_papers_batch(papers, title_field=title_field)
        
        topic_col = f"{level}_topic"
        counts = assignments[topic_col].value_counts()
        
        total = len(papers)
        result = pd.DataFrame({
            "topic": counts.index,
            "count": counts.values,
            "percentage": (counts.values / total * 100).round(2),
        })
        
        return result.head(top_n)
    
    def compare_with_clarivate(
        self,
        papers: list[dict],
        clarivate_ground_truth: dict,
        level: str = "meso",
        title_field: str = "Title",
    ) -> dict:
        """
        Compare our assignments with Clarivate's ground truth.
        
        Args:
            papers: List of paper dicts
            clarivate_ground_truth: Dict of {topic_name: paper_count} from Clarivate
            level: Comparison level
            title_field: Key for paper title
        
        Returns:
            Comparison metrics and distributions
        """
        our_dist = self.get_topic_distribution(papers, level=level, title_field=title_field, top_n=50)
        
        # Normalize Clarivate ground truth
        clarivate_total = sum(clarivate_ground_truth.values())
        clarivate_dist = {
            topic: {
                "count": count,
                "percentage": round(count / clarivate_total * 100, 2)
            }
            for topic, count in clarivate_ground_truth.items()
        }
        
        return {
            "our_distribution": our_dist.to_dict("records"),
            "clarivate_distribution": clarivate_dist,
            "our_total": len(papers),
            "clarivate_total": clarivate_total,
        }


def main():
    """Test the matcher with sample titles."""
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
    
    matcher = ClarivateTopicMatcher()
    
    # Test with sample pharmacology titles
    test_titles = [
        "Phytochemicals targeting autophagy in cancer cells",
        "Network pharmacology analysis of traditional Chinese medicine",
        "PI3K/AKT/mTOR pathway inhibitors in breast cancer treatment",
        "Gut microbiota modulation by polyphenols",
        "Drug-drug interactions in elderly patients with diabetes",
        "Curcumin nanoparticles for enhanced bioavailability",
        "Immune checkpoint inhibitors in melanoma",
        "Pharmacovigilance of COVID-19 vaccines",
    ]
    
    print("\n" + "=" * 70)
    print("Clarivate Topic Assignment Test")
    print("=" * 70)
    
    for title in test_titles:
        result = matcher.assign_paper(title)
        print(f"\nTitle: {title[:60]}...")
        print(f"  Macro: {result['macro']['topic'] if result['macro'] else 'None'} "
              f"(score: {result['macro']['score'] if result['macro'] else 'N/A'})")
        print(f"  Meso:  {result['meso']['topic'] if result['meso'] else 'None'} "
              f"(score: {result['meso']['score'] if result['meso'] else 'N/A'})")
        print(f"  Micro: {result['micro']['topic'] if result['micro'] else 'None'} "
              f"(score: {result['micro']['score'] if result['micro'] else 'N/A'})")


if __name__ == "__main__":
    main()
