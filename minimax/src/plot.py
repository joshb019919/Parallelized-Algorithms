#!/usr/bin/env python3
"""
Plot minimax algorithm performance comparison across different dataset sizes.
"""

import json
import sys
import os
import matplotlib.pyplot as plt
import numpy as np


def load_results(results_file):
    """Load benchmark results from JSON file."""
    if not os.path.exists(results_file):
        print(f"Error: Results file not found: {results_file}", file=sys.stderr)
        return None
    
    with open(results_file, 'r') as f:
        return json.load(f)


def plot_comparison(results, output_file="minimax_comparison.png"):
    """
    Plot naive vs parallel minimax performance.
    
    Results should be a list of dicts with keys:
    - nodes: number of nodes in tree
    - naive_time: time for naive algorithm (seconds)
    - parallel_time: time for parallel algorithm (seconds)
    - result: minimax value
    """
    
    if not results or len(results) == 0:
        print("No results to plot", file=sys.stderr)
        return
    
    # Sort by node count
    results = sorted(results, key=lambda x: x['nodes'])
    
    nodes = [r['nodes'] for r in results]
    naive_times = [r['naive_time'] for r in results]
    parallel_times = [r['parallel_time'] for r in results]
    
    # Create figure with multiple subplots
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    fig.suptitle('Minimax Algorithm Performance Comparison', fontsize=16, fontweight='bold')
    
    # Plot 1: Linear scale
    ax = axes[0, 0]
    ax.plot(nodes, naive_times, 'o-', label='Naive (Sequential)', linewidth=2, markersize=8)
    ax.plot(nodes, parallel_times, 's-', label='Parallel (PySpark)', linewidth=2, markersize=8)
    ax.set_xlabel('Number of Nodes')
    ax.set_ylabel('Time (seconds)')
    ax.set_title('Execution Time (Linear Scale)')
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    # Plot 2: Log scale
    ax = axes[0, 1]
    ax.loglog(nodes, naive_times, 'o-', label='Naive (Sequential)', linewidth=2, markersize=8)
    ax.loglog(nodes, parallel_times, 's-', label='Parallel (PySpark)', linewidth=2, markersize=8)
    ax.set_xlabel('Number of Nodes (log scale)')
    ax.set_ylabel('Time (seconds, log scale)')
    ax.set_title('Execution Time (Log-Log Scale)')
    ax.legend()
    ax.grid(True, alpha=0.3, which='both')
    
    # Plot 3: Speedup
    ax = axes[1, 0]
    speedup = [n / p if p > 0 else 0 for n, p in zip(naive_times, parallel_times)]
    ax.plot(nodes, speedup, 'D-', color='green', linewidth=2, markersize=8)
    ax.axhline(y=1, color='red', linestyle='--', label='Parity (speedup = 1)')
    ax.set_xlabel('Number of Nodes')
    ax.set_ylabel('Speedup (Naive Time / Parallel Time)')
    ax.set_title('Naive Speedup over Parallel')
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    # Plot 4: Time ratio table
    ax = axes[1, 1]
    ax.axis('tight')
    ax.axis('off')
    
    table_data = []
    table_data.append(['Nodes', 'Naive (s)', 'Parallel (s)', 'Speedup'])
    for r in results:
        speedup = r['naive_time'] / r['parallel_time'] if r['parallel_time'] > 0 else 0
        table_data.append([
            f"{r['nodes']:,}",
            f"{r['naive_time']:.6f}",
            f"{r['parallel_time']:.6f}",
            f"{speedup:.2f}x"
        ])
    
    table = ax.table(cellText=table_data, cellLoc='center', loc='center',
                     colWidths=[0.25, 0.25, 0.25, 0.25])
    table.auto_set_font_size(False)
    table.set_fontsize(9)
    table.scale(1, 2)
    
    # Style header row
    for i in range(4):
        table[(0, i)].set_facecolor('#40466e')
        table[(0, i)].set_text_props(weight='bold', color='white')
    
    ax.set_title('Performance Summary')
    
    plt.tight_layout()
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"Plot saved to: {output_file}")
    plt.close(fig)  # Close the figure to release file handle and ensure file is written


def main():
    if len(sys.argv) < 2:
        print("Usage: python plot.py <results_json_file>")
        print("Example: python plot.py benchmark_results.json")
        sys.exit(1)
    
    results_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else "minimax_comparison.png"
    
    results = load_results(results_file)
    if results:
        plot_comparison(results, output_file)


if __name__ == "__main__":
    main()
