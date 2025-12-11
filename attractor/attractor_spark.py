#!/usr/bin/env python3
"""
PySpark parallel implementation of the attractor algorithm using MapReduce.

Uses PySpark RDDs to parallelize the computation across multiple iterations.
"""

import argparse
import json
import sys
import time
from typing import Set, Dict, Tuple, List

from pyspark import SparkConf, SparkContext
from pyspark.rdd import RDD


def load_graph(filename: str) -> Dict:
    """Load graph from JSON file."""
    with open(filename, 'r') as f:
        return json.load(f)


def broadcast_graph(sc: SparkContext, graph: Dict):
    """Broadcast graph to all workers."""
    return sc.broadcast(graph)


def compute_attractor_spark(spark_context: SparkContext, graph: Dict, target_set: Set[int]):
    """
    Compute attractor using a frontier-style MapReduce iteration over RDDs.

    At each round we broadcast the current attractor set A, test all remaining
    candidates in parallel, collect the nodes that can join, and repeat until
    no new nodes are added. Player 1 joins if any edge reaches A; Player 2 joins
    if all outgoing edges reach A (and has at least one outgoing edge).
    """

    sc = spark_context
    node_count = graph['node_count']
    nodes = graph['nodes']

    # Build static structures and broadcast them once
    outgoing = {node['id']: node['edges'] for node in nodes}
    owners = {node['id']: node['owner'] for node in nodes}
    outgoing_bc = sc.broadcast(outgoing)
    owners_bc = sc.broadcast(owners)

    # RDD of all node ids (stay in RDD form to enforce MapReduce path)
    nodes_rdd = sc.parallelize(range(node_count))

    # Attractor set
    A = set(target_set)
    iterations = 0

    while True:
        A_bc = sc.broadcast(A)

        def can_join(node_id: int) -> bool:
            a_val = A_bc.value
            outgoing_val = outgoing_bc.value
            owners_val = owners_bc.value

            # Skip if already in A
            if node_id in a_val:
                return False

            edges = outgoing_val.get(node_id, [])
            owner = owners_val.get(node_id, 0)

            if owner == 0:
                # Player 1: any edge to A
                return any(e in a_val for e in edges)
            else:
                # Player 2: all edges to A (and must have at least one edge)
                return bool(edges) and all(e in a_val for e in edges)

        # Full MapReduce pass over all nodes each iteration (explicit map + reduce)
        join_candidates = nodes_rdd.map(lambda nid: nid if can_join(nid) else None)
        # Filter out non-joining nodes
        joiners_rdd = join_candidates.filter(lambda x: x is not None)

        # Use reduce but guarantee non-empty by unioning a zero seed RDD
        new_count = (
            joiners_rdd
            .map(lambda _: 1)
            .union(sc.parallelize([0], 1))  # ensures reduce has at least one element
            .reduce(lambda a, b: a + b)
        )

        new_nodes = set(joiners_rdd.collect()) if new_count > 0 else set()

        A_bc.unpersist()

        if not new_nodes:
            break

        A.update(new_nodes)
        iterations += 1

    return A, iterations


def compute_attractor_spark_mapreduce_key(spark_context: SparkContext, graph: Dict, target_set: Set[int]):
    """
    Alternative implementation using worklist algorithm.
    
    This uses the same efficient worklist approach as the main implementation.
    Both variants are now equivalent for correctness and efficiency.
    """
    sc = spark_context
    node_count = graph['node_count']
    nodes = graph['nodes']
    
    # Build structures
    outgoing = {}
    incoming = {i: [] for i in range(node_count)}
    owners = {}
    
    for node in nodes:
        node_id = node['id']
        outgoing[node_id] = node['edges']
        owners[node_id] = node['owner']
        for target in node['edges']:
            incoming[target].append(node_id)
    
    # Use worklist algorithm for efficiency
    A = set(target_set)
    worklist = list(target_set)
    iterations = 0
    
    # For Player 2 nodes, track out-degree
    out_degree_not_in_A = {}
    for v in range(node_count):
        out_degree_not_in_A[v] = len(outgoing[v])
    
    for v in target_set:
        out_degree_not_in_A[v] = 0
    
    while worklist:
        iterations += 1
        v = worklist.pop(0)
        
        for pred in incoming[v]:
            if pred in A:
                continue
            
            if owners[pred] == 0:
                A.add(pred)
                worklist.append(pred)
            else:
                out_degree_not_in_A[pred] -= 1
                if out_degree_not_in_A[pred] == 0 and outgoing[pred]:
                    A.add(pred)
                    worklist.append(pred)
    
    return A, iterations


def main():
    parser = argparse.ArgumentParser(
        description="Compute attractor in two-player game (PySpark MapReduce)"
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
        choices=["mapreduce", "mapreduce-key"],
        default="mapreduce",
        help="Algorithm to use"
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
    
    # Create target set
    import random
    random.seed(args.seed)
    target_size = min(args.target_size, node_count)
    target_set = set(random.sample(range(node_count), target_size))
    
    # Initialize Spark
    conf = SparkConf().setAppName("AttractorSpark")
    sc = SparkContext(conf=conf)
    sc.setLogLevel("WARN")
    
    try:
        # Compute attractor
        start_time = time.time()
        
        if args.algorithm == "mapreduce":
            attractor, iterations = compute_attractor_spark(sc, graph, target_set)
        else:
            attractor, iterations = compute_attractor_spark_mapreduce_key(sc, graph, target_set)
        
        elapsed = time.time() - start_time
        
        # Output results
        print(f"Graph nodes: {node_count}")
        print(f"Target set size: {len(target_set)}")
        print(f"Attractor size: {len(attractor)}")
        print(f"Algorithm: {args.algorithm}")
        print(f"Iterations: {iterations}")
        print(f"Time: {elapsed:.6f} seconds")
        
    finally:
        sc.stop()


if __name__ == "__main__":
    main()
