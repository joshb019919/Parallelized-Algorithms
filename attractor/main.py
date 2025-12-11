#!/usr/bin/env python3
"""
Main entry point for attractor algorithm comparison.
"""

import argparse
import sys
import os
import subprocess


def main():
    parser = argparse.ArgumentParser(
        description="Run attractor algorithm (naive vs PySpark)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --file data/graph_1000.json --mode naive
  %(prog)s --file data/graph_1000.json --mode spark
  %(prog)s --file data/graph_1000.json --mode both
        """
    )
    
    parser.add_argument(
        "--file",
        required=True,
        help="Path to graph dataset JSON file"
    )
    
    parser.add_argument(
        "--mode",
        choices=["naive", "spark", "both"],
        default="both",
        help="Which implementation to run (default: both)"
    )
    
    parser.add_argument(
        "--target-size",
        type=int,
        default=10,
        help="Target set size (default: 10)"
    )
    
    parser.add_argument(
        "--algorithm",
        choices=["naive", "worklist"],
        default="worklist",
        help="Algorithm for naive version (default: worklist)"
    )
    
    args = parser.parse_args()
    
    # Get Python executable from current environment
    python_exe = sys.executable
    
    # Verify file exists
    if not os.path.exists(args.file):
        print(f"Error: File not found: {args.file}", file=sys.stderr)
        sys.exit(1)
    
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    if args.mode in ["naive", "both"]:
        print("=" * 60)
        print("  NAIVE (Sequential) Attractor")
        print("=" * 60)
        result = subprocess.run(
            [python_exe, os.path.join(script_dir, "attractor_naive.py"),
             "--file", args.file,
             "--target-size", str(args.target_size),
             "--algorithm", args.algorithm]
        )
        if result.returncode != 0:
            print(f"\nError: Naive attractor failed with exit code {result.returncode}")
            if args.mode == "naive":
                sys.exit(result.returncode)
        print()
    
    if args.mode in ["spark", "both"]:
        print("=" * 60)
        print("  SPARK (Parallel) Attractor")
        print("=" * 60)
        result = subprocess.run(
            [python_exe, os.path.join(script_dir, "attractor_spark.py"),
             "--file", args.file,
             "--target-size", str(args.target_size)]
        )
        if result.returncode != 0:
            print(f"\nError: Spark attractor failed with exit code {result.returncode}")
            if args.mode == "spark":
                sys.exit(result.returncode)
        print()
    
    if args.mode == "both":
        print("=" * 60)
        print("  Comparison complete!")
        print("=" * 60)


if __name__ == "__main__":
    main()
