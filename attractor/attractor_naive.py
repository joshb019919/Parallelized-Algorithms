#!/usr/bin/env python3
"""
Non-PySpark sequential implementation of the attractor algorithm.

Computes the winning region (attractor) for Player 1 to reach a target set
in a two-player game graph.
"""

import argparse
import json
import sys
import time
from typing import Set, Dict, List


def load_graph(filename: str) -> Dict:
    """Load graph from JSON file."""
    with open(filename, 'r') as f:
        return json.load(f)


def compute_attractor_naive(graph: Dict, target_set: Set[int]):
    """
    Compute attractor using naive sequential algorithm.
    
    Args:
        graph: Graph with nodes containing owner (0 or 1) and edges list
        target_set: Target set W (nodes to reach)
    
    Returns:
        Attractor set A (winning region for Player 1)
    """
    nodes = graph['nodes']
    node_count = graph['node_count']
    
    # Build adjacency structures
    outgoing = {i: set(nodes[i]['edges']) for i in range(node_count)}
    incoming = {i: set() for i in range(node_count)}
    
    for node in nodes:
        node_id = node['id']
        for target in node['edges']:
            incoming[target].add(node_id)
    
    # Algorithm 1: Attractor computation
    A = set(target_set)
    changed = True
    iterations = 0
    
    while changed:
        iterations += 1
        changed = False
        
        # Player 1 positions (owner == 0)
        # If any outgoing edge goes to A, add to A
        for v in range(node_count):
            if v not in A and nodes[v]['owner'] == 0:
                # Check if there exists an edge from v to A
                if any(w in A for w in outgoing[v]):
                    A.add(v)
                    changed = True
        
        # Player 2 positions (owner == 1)
        # Only add if ALL outgoing edges go to A
        for v in range(node_count):
            if v not in A and nodes[v]['owner'] == 1:
                succ_v = outgoing[v]
                if succ_v and all(w in A for w in succ_v):
                    A.add(v)
                    changed = True
    
    return A, iterations


def compute_attractor_worklist(graph: Dict, target_set: Set[int]):
    """
    Compute attractor using worklist algorithm (more efficient).
    
    Instead of iterating all nodes each round, only process nodes that
    might be affected by recent additions.
    """
    nodes = graph['nodes']
    node_count = graph['node_count']
    
    # Build adjacency structures
    outgoing = {i: set(nodes[i]['edges']) for i in range(node_count)}
    incoming = {i: set() for i in range(node_count)}
    
    for node in nodes:
        node_id = node['id']
        for target in node['edges']:
            incoming[target].add(node_id)
    
    # Initialize
    A = set(target_set)
    worklist = list(target_set)
    iterations = 0
    
    # For Player 2 nodes, track how many outgoing edges are NOT in A
    out_degree_not_in_A = {}
    for v in range(node_count):
        out_degree_not_in_A[v] = len(outgoing[v])
    
    # Update for initial target set
    for v in target_set:
        out_degree_not_in_A[v] = 0
    
    while worklist:
        iterations += 1
        v = worklist.pop(0)
        
        # Process predecessors of v
        for pred in incoming[v]:
            if pred in A:
                continue
            
            if nodes[pred]['owner'] == 0:
                # Player 1: any edge to A means we can add
                A.add(pred)
                worklist.append(pred)
            else:
                # Player 2: check if all edges now point to A
                out_degree_not_in_A[pred] -= 1
                if out_degree_not_in_A[pred] == 0 and outgoing[pred]:
                    A.add(pred)
                    worklist.append(pred)
    
    return A, iterations


def main():
    parser = argparse.ArgumentParser(
        description="Compute attractor region in a two-player game graph"
    )
    parser.add_argument(
        "--file",
        required=True,
        help="Path to graph dataset JSON file"
    )
    parser.add_argument(
        "--target-size",
        type=int,
        default=10,
        help="Number of nodes in target set (random selection)"
    )
    parser.add_argument(
        "--algorithm",
        choices=["naive", "worklist"],
        default="worklist",
        help="Algorithm to use (default: worklist)"
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=42,
        help="Random seed for target set selection"
    )
    
    args = parser.parse_args()
    
    # Load graph
    try:
        graph = load_graph(args.file)
    except FileNotFoundError:
        print(f"Error: File not found: {args.file}", file=sys.stderr)
        sys.exit(1)
    except json.JSONDecodeError:
        print(f"Error: Invalid JSON in {args.file}", file=sys.stderr)
        sys.exit(1)
    
    node_count = graph['node_count']
    
    # Create random target set
    import random
    random.seed(args.seed)
    target_size = min(args.target_size, node_count)
    target_set = set(random.sample(range(node_count), target_size))
    
    # Compute attractor
    start_time = time.time()
    
    if args.algorithm == "naive":
        attractor, iterations = compute_attractor_naive(graph, target_set)
    else:
        attractor, iterations = compute_attractor_worklist(graph, target_set)
    
    elapsed = time.time() - start_time
    
    # Output results
    print(f"Graph nodes: {node_count}")
    print(f"Target set size: {len(target_set)}")
    print(f"Attractor size: {len(attractor)}")
    print(f"Algorithm: {args.algorithm}")
    print(f"Iterations/rounds: {iterations}")
    print(f"Time: {elapsed:.6f} seconds")
    print(f"Result: {sorted(list(attractor))[:20]}..." if len(attractor) > 20 else f"Result: {sorted(list(attractor))}")


if __name__ == "__main__":
    main()
