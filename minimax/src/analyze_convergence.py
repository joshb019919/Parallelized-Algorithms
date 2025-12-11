#!/usr/bin/env python3
"""
Analyze convergence point where parallel minimax becomes faster than sequential,
accounting for Spark overhead and modeling true distributed speedup with N CPUs.
"""

import json
import numpy as np
from scipy.optimize import curve_fit
import sys


def load_results(filename):
    """Load benchmark results."""
    with open(filename, 'r') as f:
        return json.load(f)


def estimate_spark_overhead(results):
    """
    Estimate fixed Spark overhead by analyzing small datasets where
    overhead dominates actual computation.
    """
    # Use smallest datasets to estimate overhead
    small_results = [r for r in results if r['nodes'] <= 500000]
    if not small_results:
        return 7.0  # Default estimate
    
    # Overhead is roughly the difference when naive time is very small
    overheads = [r['parallel_time'] - r['naive_time'] for r in small_results]
    return np.mean(overheads)


def fit_complexity(nodes, times):
    """
    Fit time complexity to T(n) = a*n + b
    Minimax is O(n) for tree traversal.
    """
    def linear(n, a, b):
        return a * n + b
    
    params, _ = curve_fit(linear, nodes, times)
    return params


def predict_distributed_time(nodes, naive_params, spark_overhead, num_cpus):
    """
    Model distributed execution time:
    T_distributed = overhead + (computation / num_cpus) + communication
    
    Where:
    - overhead: Spark initialization, job setup (~3-7 seconds)
    - computation: actual minimax work divided by CPUs
    - communication: data serialization/shuffling (estimated ~5-10% of computation)
    """
    a_naive, b_naive = naive_params
    
    # Naive computation time (no overhead)
    computation_time = a_naive * nodes + b_naive
    
    # Distributed: divide computation by CPUs, add overhead and communication cost
    communication_factor = 1.07  # 7% overhead for data transfer
    distributed_time = spark_overhead + (computation_time / num_cpus) * communication_factor
    
    return distributed_time


def find_convergence_point(naive_params, spark_overhead, num_cpus):
    """
    Find number of nodes where:
    T_naive(n) = T_distributed(n, num_cpus)
    
    Solving: a*n + b = overhead + ((a*n + b) / num_cpus) * 1.07
    """
    a_naive, b_naive = naive_params
    communication_factor = 1.07
    
    # Rearrange: a*n + b = overhead + (a*n*1.07)/num_cpus + (b*1.07)/num_cpus
    # a*n - (a*n*1.07)/num_cpus = overhead + (b*1.07)/num_cpus - b
    # a*n * (1 - 1.07/num_cpus) = overhead + b*(1.07/num_cpus - 1)
    
    left_coef = a_naive * (1 - communication_factor / num_cpus)
    right_const = spark_overhead + b_naive * (communication_factor / num_cpus - 1)
    
    if left_coef <= 0:
        # Parallel never catches up
        return float('inf')
    
    convergence_nodes = right_const / left_coef
    return max(0, convergence_nodes)


def main():
    if len(sys.argv) < 2:
        print("Usage: python analyze_convergence.py <benchmark_results.json> [output_file.txt]")
        sys.exit(1)
    
    results = load_results(sys.argv[1])
    
    # Determine output file
    output_file = sys.argv[2] if len(sys.argv) > 2 else "convergence_analysis.txt"
    
    # Open file for writing
    outf = open(output_file, 'w')
    
    # Extract data
    nodes = np.array([r['nodes'] for r in results])
    naive_times = np.array([r['naive_time'] for r in results])
    parallel_times = np.array([r['parallel_time'] for r in results])
    
    def output(msg=""):
        """Write to both stdout and file."""
        print(msg)
        outf.write(msg + "\n")
    
    output("=" * 70)
    output("  CONVERGENCE ANALYSIS: When Does Parallel Beat Sequential?")
    output("=" * 70)
    output()
    
    # Estimate Spark overhead
    overhead = estimate_spark_overhead(results)
    output(f"Estimated Spark Overhead: {overhead:.2f} seconds")
    output()
    
    # Fit naive algorithm complexity
    naive_params = fit_complexity(nodes, naive_times)
    a_naive, b_naive = naive_params
    output(f"Naive Time Model: T(n) = {a_naive:.2e}*n + {b_naive:.4f}")
    output(f"  → For 1M nodes: {a_naive * 1e6 + b_naive:.2f}s (actual: {naive_times[nodes == 1000000][0]:.2f}s)")
    output(f"  → For 10M nodes: {a_naive * 1e7 + b_naive:.2f}s (actual: {naive_times[nodes == 10000000][0]:.2f}s)")
    output()
    
    # Current PySpark performance (single machine)
    current_speedup = np.mean(naive_times / parallel_times)
    output(f"Current PySpark Speedup: {current_speedup:.3f}x (SLOWER due to overhead)")
    output()
    
    output("-" * 70)
    output("  HYPOTHETICAL: True Distributed System with N CPUs")
    output("-" * 70)
    output()
    
    # Analyze different CPU counts
    cpu_counts = [2, 4, 8, 16, 32, 64, 128]
    
    output(f"{'CPUs':<6} {'Convergence Point':<20} {'Time at Convergence':<25} {'Speedup':<10}")
    output(f"{'':6} {'(nodes)':<20} {'(Naive / Parallel)':<25} {'@10M nodes':<10}")
    output("-" * 70)
    
    results_table = []
    
    for num_cpus in cpu_counts:
        conv_nodes = find_convergence_point(naive_params, overhead, num_cpus)
        
        if conv_nodes == float('inf'):
            output(f"{num_cpus:<6} {'Never converges':<20} {'N/A':<25} {'N/A':<10}")
            continue
        
        # Calculate times at convergence
        conv_naive_time = a_naive * conv_nodes + b_naive
        conv_parallel_time = predict_distributed_time(conv_nodes, naive_params, overhead, num_cpus)
        
        # Calculate speedup at 10M nodes
        nodes_10m = 10_000_000
        time_10m_naive = a_naive * nodes_10m + b_naive
        time_10m_parallel = predict_distributed_time(nodes_10m, naive_params, overhead, num_cpus)
        speedup_10m = time_10m_naive / time_10m_parallel
        
        results_table.append({
            'cpus': num_cpus,
            'convergence': conv_nodes,
            'speedup_10m': speedup_10m
        })
        
        output(f"{num_cpus:<6} {conv_nodes:>12,.0f} nodes    {conv_naive_time:>6.2f}s / {conv_parallel_time:>6.2f}s    {speedup_10m:>6.2f}x")
    
    output()
    output("-" * 70)
    output("  KEY INSIGHTS")
    output("-" * 70)
    output()
    
    # Find where we get 2x, 5x, 10x speedup at 10M nodes
    if results_table:
        for target_speedup in [2.0, 5.0, 10.0]:
            for r in results_table:
                if r['speedup_10m'] >= target_speedup:
                    output(f"• {target_speedup:.0f}x speedup at 10M nodes: {r['cpus']} CPUs")
                    output(f"  Convergence at {r['convergence']:,.0f} nodes")
                    break
            else:
                output(f"• {target_speedup:.0f}x speedup at 10M nodes: Requires >{cpu_counts[-1]} CPUs")
        
        output()
        output(f"• Current overhead ({overhead:.1f}s) dominates performance below ~{results_table[0]['convergence']:,.0f} nodes")
        output(f"• With sufficient CPUs, parallel becomes worthwhile for trees >500K-1M nodes")
        output(f"• Communication overhead (~7%) limits maximum speedup to ~{0.93 * cpu_counts[-1]:.1f}x with {cpu_counts[-1]} CPUs")
    
    output()
    output("=" * 70)
    output()
    
    # Show realistic scenarios
    output("REALISTIC SCENARIOS:")
    output()
    output("1. Small Cluster (4 CPUs):")
    conv_4 = find_convergence_point(naive_params, overhead, 4)
    output(f"   - Parallel becomes faster at {conv_4:,.0f} nodes")
    output(f"   - Best for trees with 5M+ nodes")
    output()
    
    output("2. Medium Cluster (16 CPUs):")
    conv_16 = find_convergence_point(naive_params, overhead, 16)
    time_100m_naive = a_naive * 100_000_000 + b_naive
    time_100m_parallel = predict_distributed_time(100_000_000, naive_params, overhead, 16)
    output(f"   - Parallel becomes faster at {conv_16:,.0f} nodes")
    output(f"   - For 100M nodes: {time_100m_naive:.1f}s → {time_100m_parallel:.1f}s ({time_100m_naive/time_100m_parallel:.1f}x speedup)")
    output()
    
    output("3. Large Cluster (64 CPUs):")
    conv_64 = find_convergence_point(naive_params, overhead, 64)
    time_1b_naive = a_naive * 1_000_000_000 + b_naive
    time_1b_parallel = predict_distributed_time(1_000_000_000, naive_params, overhead, 64)
    output(f"   - Parallel becomes faster at {conv_64:,.0f} nodes")
    output(f"   - For 1B nodes: {time_1b_naive:.1f}s → {time_1b_parallel:.1f}s ({time_1b_naive/time_1b_parallel:.1f}x speedup)")
    output()
    
    # Close output file
    outf.close()
    print(f"\nAnalysis saved to: {output_file}")


if __name__ == "__main__":
    main()
