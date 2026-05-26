"""
Test Edge Weight Configurations
================================
Runs scope drift analysis with 3 different edge weight configurations,
saving results to separate files for comparison.

Configs:
  1. baseline     - No edge weights (binary edges)
  2. decay_only   - Temporal decay + self-cite discounting (no BC)
  3. full_phase2  - Full Phase 2 (decay + self-cite + bibliographic coupling)

Usage:
    python test_edge_weight_configs.py

Outputs:
    output/scope_global_network_baseline.json
    output/scope_global_network_decay_only.json
    output/scope_global_network_full_phase2.json
    output/config_comparison.txt
"""

import os
import json
import logging
from pathlib import Path
from collections import Counter, defaultdict
from copy import deepcopy

# Import functions from the main script
from scope_drift_airak_global_1 import (
    get_top_frontiers_journals,
    get_frontiers_publication_ids,
    get_full_network_edges,
    get_ego_network_edges,
    get_node_metadata,
    apply_edge_weights,
    get_bibliographic_coupling_edges,
    merge_edge_lists,
    build_graph,
    run_leiden,
    merge_small_communities,
    compute_layout,
    label_communities,
    analyze_frontiers_in_global_network,
    write_dashboard_html,
    TOP_N_JOURNALS,
    NETWORK_MODE,
    YEAR_RANGE,
    LEIDEN_RESOLUTIONS,
    MIN_COMMUNITY_SIZES,
    JOURNAL_DRIFT_LEVEL,
    MULTI_RESOLUTION,
    TEMPORAL_DECAY_TAU,
    BC_MIN_SHARED_REFS,
    SELF_CITE_JOURNAL_WEIGHT,
)

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s"
)
log = logging.getLogger(__name__)

OUTPUT_DIR = Path(__file__).resolve().parent / "output"
OUTPUT_DIR.mkdir(exist_ok=True)

# Configuration definitions
CONFIGS = {
    "baseline": {
        "enable_edge_weights": False,
        "enable_bc_edges": False,
        "description": "No edge weights (binary edges)",
    },
    "decay_only": {
        "enable_edge_weights": True,
        "enable_bc_edges": False,
        "description": "Temporal decay + self-cite discounting (no BC)",
    },
    "full_phase2": {
        "enable_edge_weights": True,
        "enable_bc_edges": True,
        "description": "Full Phase 2 (decay + self-cite + BC)",
    },
}


def run_single_config(
    config_name: str,
    config: dict,
    df_edges_original,
    node_lookup: dict,
    frontiers_pub_ids: set,
    all_journal_ids: set,
    journal_ids: list,
) -> dict:
    """Run analysis with a specific edge weight configuration."""
    log.info("=" * 60)
    log.info(f"CONFIG: {config_name} — {config['description']}")
    log.info("=" * 60)
    
    # Start with a fresh copy of edges
    df_edges = df_edges_original.copy()
    
    # Apply edge weighting based on config
    if config["enable_edge_weights"]:
        log.info("Applying temporal decay + self-cite discounting...")
        df_edges = apply_edge_weights(df_edges, node_lookup)
        
        if config["enable_bc_edges"]:
            log.info("Computing bibliographic coupling edges...")
            df_bc = get_bibliographic_coupling_edges(frontiers_pub_ids, all_journal_ids)
            if len(df_bc) > 0:
                df_edges = merge_edge_lists(df_edges, df_bc)
            del df_bc
    else:
        log.info("Using binary unweighted edges")
        df_edges["weight"] = 1.0
    
    # Build graph and run Leiden
    G, node_ids = build_graph(df_edges)
    del df_edges
    
    # Run multi-resolution Leiden
    if MULTI_RESOLUTION:
        log.info("Running multi-resolution Leiden (macro, meso, micro)...")
        memberships = {}
        for level in ["macro", "meso", "micro"]:
            res = LEIDEN_RESOLUTIONS[level]
            raw_mem = run_leiden(G, res)
            min_sz = MIN_COMMUNITY_SIZES[level]
            memberships[level] = merge_small_communities(G, node_ids, raw_mem, min_size=min_sz)
            n_comms = len(set(memberships[level]))
            log.info(f"  {level}: {n_comms} communities after merging")
        membership = memberships[JOURNAL_DRIFT_LEVEL]
    else:
        resolution = LEIDEN_RESOLUTIONS[JOURNAL_DRIFT_LEVEL]
        membership = run_leiden(G, resolution)
        membership = merge_small_communities(G, node_ids, membership)
        memberships = {JOURNAL_DRIFT_LEVEL: membership}
    
    del G
    
    # Compute layout
    node_coords = compute_layout(node_ids, membership)
    
    # Build community profiles
    log.info("Building community profiles...")
    comm_profiles = defaultdict(lambda: {"total": 0, "frontiers": 0, "by_journal": Counter()})
    for idx, pid in enumerate(node_ids):
        cid = membership[idx]
        meta = node_lookup.get(pid, {})
        if not meta:
            continue
        comm_profiles[cid]["total"] += 1
        if meta.get("IsFrontiers"):
            comm_profiles[cid]["frontiers"] += 1
        jname = meta.get("JournalName") or "Unknown"
        comm_profiles[cid]["by_journal"][jname] += 1
    
    for cid, profile in comm_profiles.items():
        top_j = profile["by_journal"].most_common(1)
        profile["dominant_journal"] = top_j[0][0] if top_j else f"Community {cid}"
    
    # Label communities
    comm_labels = label_communities(dict(comm_profiles), node_ids, membership, node_lookup)
    
    # Analyze results
    results = analyze_frontiers_in_global_network(
        node_ids, membership, node_lookup, journal_ids, YEAR_RANGE, comm_labels, node_coords
    )
    
    # Add config metadata
    results["meta"]["config_name"] = config_name
    results["meta"]["edge_weighting"] = {
        "enabled": config["enable_edge_weights"],
        "temporal_decay_tau": TEMPORAL_DECAY_TAU,
        "bc_edges_enabled": config["enable_bc_edges"],
        "bc_min_shared_refs": BC_MIN_SHARED_REFS,
        "self_cite_journal_weight": SELF_CITE_JOURNAL_WEIGHT,
    }
    
    # Add multi-resolution data
    if MULTI_RESOLUTION:
        results["multi_resolution"] = True
        results["cluster_counts"] = {level: len(set(mem)) for level, mem in memberships.items()}
        node_clusters = []
        for idx, pid in enumerate(node_ids):
            meta = node_lookup.get(pid, {})
            if meta.get("IsFrontiers"):
                entry = {"pub_id": int(pid)}
                for level in ["macro", "meso", "micro"]:
                    if level in memberships:
                        entry[f"{level}_cluster"] = int(memberships[level][idx])
                node_clusters.append(entry)
        results["frontiers_node_clusters"] = node_clusters
    
    return results


def save_results(results: dict, config_name: str):
    """Save results to config-specific files."""
    # Convert numpy types to native Python for JSON serialization
    def convert_numpy(obj):
        import numpy as np
        if isinstance(obj, (np.integer, np.int64, np.int32)):
            return int(obj)
        if isinstance(obj, (np.floating, np.float64, np.float32)):
            return float(obj)
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        return obj
    
    json_path = OUTPUT_DIR / f"scope_global_network_{config_name}.json"
    with open(json_path, "w") as f:
        json.dump(results, f, indent=2, default=convert_numpy)
    log.info(f"Saved: {json_path}")
    
    # Skip HTML dashboard to avoid the int64 serialization issue
    # html_path = OUTPUT_DIR / f"scope_global_dashboard_{config_name}.html"
    # write_dashboard_html(str(html_path), results)


def print_comparison(all_results: dict):
    """Print a comparison table of OOS ratings across configs."""
    log.info("\n" + "=" * 80)
    log.info("COMPARISON: OOS % by Journal and Config")
    log.info("=" * 80)
    
    # Get journal names from first config
    first_config = list(all_results.keys())[0]
    journals = [j["name"] for j in all_results[first_config]["journals"]]
    
    # Header
    header = f"{'Journal':<20}"
    for config_name in all_results.keys():
        header += f" | {config_name:<15}"
    log.info(header)
    log.info("-" * len(header))
    
    # Data rows
    for jname in journals:
        row = f"{jname:<20}"
        for config_name, results in all_results.items():
            j_data = next((j for j in results["journals"] if j["name"] == jname), None)
            if j_data:
                row += f" | {j_data['out_of_scope_pct']:>13.2f}%"
            else:
                row += f" | {'N/A':>14}"
        log.info(row)
    
    # Save comparison to file
    comparison_path = OUTPUT_DIR / "config_comparison.txt"
    with open(comparison_path, "w") as f:
        f.write("OOS % Comparison by Config\n")
        f.write("=" * 80 + "\n\n")
        f.write(f"{'Journal':<20}")
        for config_name in all_results.keys():
            f.write(f" | {config_name:<15}")
        f.write("\n" + "-" * 80 + "\n")
        for jname in journals:
            f.write(f"{jname:<20}")
            for config_name, results in all_results.items():
                j_data = next((j for j in results["journals"] if j["name"] == jname), None)
                if j_data:
                    f.write(f" | {j_data['out_of_scope_pct']:>13.2f}%")
                else:
                    f.write(f" | {'N/A':>14}")
            f.write("\n")
    log.info(f"\nComparison saved to: {comparison_path}")


def main():
    log.info("=" * 80)
    log.info("SCOPE DRIFT — Multi-Config Test Runner")
    log.info(f"  Mode: {NETWORK_MODE.upper()}, Years: {YEAR_RANGE[0]}-{YEAR_RANGE[1]}")
    log.info(f"  Configs: {', '.join(CONFIGS.keys())}")
    log.info("=" * 80)
    
    # Step 1: Fetch data ONCE (this is the expensive part)
    log.info("\n[STEP 1] Fetching network data (shared across all configs)...")
    
    df_journals = get_top_frontiers_journals(TOP_N_JOURNALS)
    journal_ids = df_journals["JournalId"].tolist()
    
    frontiers_pub_ids = get_frontiers_publication_ids(journal_ids)
    
    if NETWORK_MODE == "full":
        df_edges, final_nodes, all_journal_ids = get_full_network_edges(frontiers_pub_ids, journal_ids)
    else:
        df_edges, final_nodes = get_ego_network_edges(frontiers_pub_ids)
        all_journal_ids = set(journal_ids)
    
    df_meta = get_node_metadata(final_nodes, journal_ids)
    node_lookup = df_meta.set_index("PublicationId").to_dict("index")
    
    log.info(f"Network ready: {len(final_nodes):,} nodes, {len(df_edges):,} edges")
    
    # Step 2: Run each config
    all_results = {}
    for config_name, config in CONFIGS.items():
        results = run_single_config(
            config_name=config_name,
            config=config,
            df_edges_original=df_edges,
            node_lookup=node_lookup,
            frontiers_pub_ids=frontiers_pub_ids,
            all_journal_ids=all_journal_ids,
            journal_ids=journal_ids,
        )
        save_results(results, config_name)
        all_results[config_name] = results
    
    # Step 3: Print comparison
    print_comparison(all_results)
    
    log.info("\nAll configs complete!")


if __name__ == "__main__":
    main()
