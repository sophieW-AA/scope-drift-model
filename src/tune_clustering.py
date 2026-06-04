"""
Clustering Parameter Tuning Script
===================================
Tests different combinations of edge weight parameters to find optimal clustering.

Evaluates:
- Number of communities
- Size distribution (std dev, max size %)
- Balance score (how evenly sized communities are)

Usage:
    python src/tune_clustering.py
"""

import os
import sys
import json
import itertools
from pathlib import Path
from collections import Counter
import numpy as np

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent))

# Base configuration (modify these as needed)
BASE_CONFIG = {
    "START_YEAR": "2025",
    "END_YEAR": "2025",
    "NETWORK_MODE": "ego",
    "TOP_N_JOURNALS": "5",
    "JOURNAL_DRIFT_LEVEL": "meso",
    "MIN_COMMUNITY_SIZE": "200",
    "TEMPORAL_DECAY_TAU": "2.0",
    "SELF_CITE_JOURNAL_WEIGHT": "0.2",
    "BC_MIN_SHARED_REFS": "5",
}

# Parameter grid to search
PARAM_GRID = {
    "WEIGHT_TRANSFORM": ["none", "log", "sqrt"],
    "EDGE_WEIGHT_THRESHOLD": ["0.0", "0.05", "0.1", "0.15"],
    "WEIGHT_CONTRAST": ["1.0", "1.5", "2.0", "3.0"],
    "LEIDEN_RESOLUTION_MESO": ["0.00003", "0.00005", "0.0001"],
}

# Quick test mode - fewer combinations
QUICK_GRID = {
    "WEIGHT_TRANSFORM": ["none", "log"],
    "EDGE_WEIGHT_THRESHOLD": ["0.0", "0.1"],
    "WEIGHT_CONTRAST": ["1.0", "2.0"],
    "LEIDEN_RESOLUTION_MESO": ["0.00005"],
}


def calculate_balance_score(sizes: list) -> float:
    """
    Calculate how balanced the community sizes are.
    Returns 0-1 where 1 = perfectly balanced, 0 = one giant cluster.
    Uses normalized entropy.
    """
    if not sizes or len(sizes) == 1:
        return 0.0
    
    total = sum(sizes)
    probs = [s / total for s in sizes]
    
    # Entropy
    entropy = -sum(p * np.log(p) for p in probs if p > 0)
    
    # Max entropy (uniform distribution)
    max_entropy = np.log(len(sizes))
    
    return entropy / max_entropy if max_entropy > 0 else 0.0


def calculate_gini(sizes: list) -> float:
    """
    Calculate Gini coefficient for community sizes.
    0 = perfect equality, 1 = perfect inequality
    """
    if not sizes:
        return 1.0
    
    sizes = sorted(sizes)
    n = len(sizes)
    total = sum(sizes)
    
    if total == 0:
        return 1.0
    
    cumsum = np.cumsum(sizes)
    gini = (2 * sum((i + 1) * s for i, s in enumerate(sizes)) - (n + 1) * total) / (n * total)
    
    return gini


def evaluate_clustering(results: dict) -> dict:
    """Extract clustering metrics from results."""
    communities = results.get("communities", [])
    
    if not communities:
        return {"error": "No communities found"}
    
    sizes = [c["size"] for c in communities]
    total_nodes = sum(sizes)
    
    metrics = {
        "n_communities": len(communities),
        "total_nodes": total_nodes,
        "largest_size": max(sizes),
        "largest_pct": round(100 * max(sizes) / total_nodes, 1) if total_nodes else 0,
        "smallest_size": min(sizes),
        "mean_size": round(np.mean(sizes), 1),
        "std_size": round(np.std(sizes), 1),
        "balance_score": round(calculate_balance_score(sizes), 3),
        "gini": round(calculate_gini(sizes), 3),
    }
    
    # Size distribution buckets
    size_buckets = {"<100": 0, "100-500": 0, "500-1000": 0, "1000-5000": 0, ">5000": 0}
    for s in sizes:
        if s < 100:
            size_buckets["<100"] += 1
        elif s < 500:
            size_buckets["100-500"] += 1
        elif s < 1000:
            size_buckets["500-1000"] += 1
        elif s < 5000:
            size_buckets["1000-5000"] += 1
        else:
            size_buckets[">5000"] += 1
    
    metrics["size_distribution"] = size_buckets
    
    return metrics


def run_single_config(config: dict, run_id: int) -> dict:
    """Run scope_drift with a specific configuration."""
    print(f"\n{'='*60}")
    print(f"Run {run_id}: Testing configuration...")
    for k, v in config.items():
        if k not in BASE_CONFIG or BASE_CONFIG.get(k) != v:
            print(f"  {k} = {v}")
    print("="*60)
    
    # Set environment variables
    for key, value in config.items():
        os.environ[key] = value
    
    # Import and run (reload to pick up new env vars)
    import importlib
    import scope_drift
    importlib.reload(scope_drift)
    
    try:
        # Run the analysis
        results = scope_drift.main()
        
        # Load saved results (main() saves to file)
        output_path = Path(__file__).parent.parent / "output" / "scope_global_network.json"
        with open(output_path) as f:
            results = json.load(f)
        
        metrics = evaluate_clustering(results)
        metrics["config"] = {k: v for k, v in config.items() if k not in BASE_CONFIG or BASE_CONFIG.get(k) != v}
        metrics["status"] = "success"
        
        return metrics
        
    except Exception as e:
        print(f"  ERROR: {e}")
        return {
            "config": config,
            "status": "error",
            "error": str(e)
        }


def run_grid_search(quick: bool = True):
    """Run parameter grid search."""
    grid = QUICK_GRID if quick else PARAM_GRID
    
    # Generate all combinations
    keys = list(grid.keys())
    values = list(grid.values())
    combinations = list(itertools.product(*values))
    
    print(f"\nParameter Grid Search")
    print(f"=====================")
    print(f"Testing {len(combinations)} configurations")
    print(f"Parameters: {keys}")
    
    results = []
    
    for i, combo in enumerate(combinations):
        config = BASE_CONFIG.copy()
        for key, value in zip(keys, combo):
            config[key] = value
        
        metrics = run_single_config(config, i + 1)
        results.append(metrics)
        
        # Print summary
        if metrics.get("status") == "success":
            print(f"\n  Results: {metrics['n_communities']} communities, "
                  f"largest={metrics['largest_pct']}%, "
                  f"balance={metrics['balance_score']}, "
                  f"gini={metrics['gini']}")
    
    return results


def print_summary(results: list):
    """Print comparison summary."""
    print("\n" + "="*80)
    print("TUNING RESULTS SUMMARY")
    print("="*80)
    
    # Filter successful runs
    successful = [r for r in results if r.get("status") == "success"]
    
    if not successful:
        print("No successful runs!")
        return
    
    # Sort by balance score (higher is better)
    by_balance = sorted(successful, key=lambda x: x.get("balance_score", 0), reverse=True)
    
    # Sort by largest cluster % (lower is better)
    by_largest = sorted(successful, key=lambda x: x.get("largest_pct", 100))
    
    print("\n--- Top 5 by Balance Score (higher = more even) ---")
    print(f"{'Rank':<5} {'Balance':<10} {'Gini':<10} {'N Comms':<10} {'Largest%':<10} {'Config'}")
    print("-" * 80)
    for i, r in enumerate(by_balance[:5]):
        config_str = ", ".join(f"{k}={v}" for k, v in r.get("config", {}).items())
        print(f"{i+1:<5} {r['balance_score']:<10} {r['gini']:<10} {r['n_communities']:<10} {r['largest_pct']:<10} {config_str[:40]}")
    
    print("\n--- Top 5 by Smallest Largest Cluster (lower = better) ---")
    print(f"{'Rank':<5} {'Largest%':<10} {'Balance':<10} {'N Comms':<10} {'Config'}")
    print("-" * 80)
    for i, r in enumerate(by_largest[:5]):
        config_str = ", ".join(f"{k}={v}" for k, v in r.get("config", {}).items())
        print(f"{i+1:<5} {r['largest_pct']:<10} {r['balance_score']:<10} {r['n_communities']:<10} {config_str[:40]}")
    
    # Save full results
    output_path = Path(__file__).parent.parent / "output" / "tuning_results.json"
    with open(output_path, "w") as f:
        json.dump(results, f, indent=2)
    print(f"\nFull results saved to: {output_path}")


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Tune clustering parameters")
    parser.add_argument("--full", action="store_true", help="Run full grid (slower)")
    parser.add_argument("--quick", action="store_true", help="Run quick grid (default)")
    args = parser.parse_args()
    
    quick = not args.full
    
    print("\n" + "="*60)
    print("CLUSTERING PARAMETER TUNING")
    print("="*60)
    print(f"Mode: {'QUICK' if quick else 'FULL'} grid search")
    
    results = run_grid_search(quick=quick)
    print_summary(results)


if __name__ == "__main__":
    main()
