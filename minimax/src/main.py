#!/usr/bin/env python3
"""
Main entry point for running minimax algorithms (naive and parallel).
"""

import argparse
import sys
import os
import subprocess


def main():
    parser = argparse.ArgumentParser(
        description="Run minimax algorithm comparison (naive vs parallel)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --file data/tree_dataset_500.json --mode naive
  %(prog)s --file data/tree_dataset_500.json --mode parallel
  %(prog)s --file data/tree_dataset_500.json --mode both
        """
    )
    
    parser.add_argument(
        "--file",
        required=True,
        help="Path to the tree dataset JSON file"
    )
    
    parser.add_argument(
        "--mode",
        choices=["naive", "parallel", "both"],
        default="both",
        help="Which algorithm to run (default: both)"
    )
    
    args = parser.parse_args()
    
    # Get Python executable from current environment
    python_exe = sys.executable
    
    # Verify file exists
    if not os.path.exists(args.file):
        print(f"Error: File not found: {args.file}", file=sys.stderr)
        sys.exit(1)
    
    if args.mode in ["naive", "both"]:
        print("=" * 60)
        print("  NAIVE (Non-Parallel) Minimax")
        print("=" * 60)
        result = subprocess.run(
            [python_exe, "minimax_naive.py", "--file", args.file],
            cwd=os.path.dirname(os.path.abspath(__file__))
        )
        if result.returncode != 0:
            print(f"\nError: Naive minimax failed with exit code {result.returncode}")
            if args.mode == "naive":
                sys.exit(result.returncode)
        print()
    
    if args.mode in ["parallel", "both"]:
        print("=" * 60)
        print("  PARALLEL (PySpark) Minimax")
        print("=" * 60)
        result = subprocess.run(
            [python_exe, "minimax_parallel.py", "--file", args.file],
            cwd=os.path.dirname(os.path.abspath(__file__))
        )
        if result.returncode != 0:
            print(f"\nError: Parallel minimax failed with exit code {result.returncode}")
            if args.mode == "parallel":
                sys.exit(result.returncode)
        print()
    
    if args.mode == "both":
        print("=" * 60)
        print("  Comparison complete!")
        print("=" * 60)


if __name__ == "__main__":
    main()
