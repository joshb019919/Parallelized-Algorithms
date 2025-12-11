# Attractor Algorithm: Sequential vs PySpark

This project implements and compares two implementations of the attractor algorithm for computing winning regions in two-player game graphs:

- **Naive (sequential)**: Traditional iterative algorithm using Python
- **PySpark (parallel)**: Distributed implementation using PySpark MapReduce operations

## Algorithm Overview

The attractor algorithm computes the set of nodes from which Player 1 can force a win by reaching a target set `W` in a directed game graph. The graph has nodes partitioned into two player sets (Player 1: owner=0, Player 2: owner=1).

**Algorithm logic:**
- Player 1 nodes join the attractor if they have any edge pointing to the current attractor
- Player 2 nodes join the attractor only if ALL their outgoing edges point to the current attractor
- The process repeats until convergence (no more nodes are added)

See `ALGORITHM.md` for formal algorithm specification.

## Project Structure

```
attractor/
├── ALGORITHM.md                 # Algorithm specification
├── README.md                    # This file
├── main.py                      # Main entry point for both implementations
├── attractor_naive.py           # Sequential implementation
├── attractor_spark.py           # PySpark MapReduce implementation
├── plot.py                      # Visualization tool
├── run_comparison.sh            # Comprehensive benchmark suite
├── run_naive.sh                 # Individual naive benchmark
├── run_spark.sh                 # Individual spark benchmark
├── data/                        # Generated graph datasets
└── results/                     # Benchmark results and plots
```

## Implementations

### attractor_naive.py

Sequential Python implementation with two algorithm variants:

1. **Naive Algorithm** (`--algorithm naive`)
   - Simple approach: iterate through all nodes each round
   - Time complexity: O(iterations × nodes × avg_degree)

2. **Worklist Algorithm** (`--algorithm worklist`) - **Recommended**
   - Optimized approach: only process affected nodes
   - Uses worklist of recently-added nodes
   - Tracks out-degree for Player 2 nodes
   - Much faster in practice

### attractor_spark.py

PySpark parallel implementation with two MapReduce variants:

1. **MapReduce** (`--algorithm mapreduce`)
   - Creates RDD of candidate nodes each iteration
   - Filters by player ownership
   - Parallel evaluation of join conditions

2. **MapReduceByKey** (`--algorithm mapreduce-key`)
   - Groups nodes by player ownership
   - Uses `map()` and `reduceByKey()` operations
   - Better data locality for grouped computations

Both variants converge to the same result.

## Installation

Ensure you have the required dependencies:

```bash
# Install matplotlib for visualization
pip install matplotlib

# PySpark should already be installed from minimax project
# If not: pip install pyspark
```

## Running the Algorithms

### Using main.py (Recommended)

Run both implementations:

```bash
python main.py --file data/graph_1000.json --mode both
```

Run only naive:

```bash
python main.py --file data/graph_1000.json --mode naive
```

Run only PySpark:

```bash
python main.py --file data/graph_1000.json --mode spark
```

### Direct Execution

Naive algorithm:

```bash
python attractor_naive.py --file data/graph_1000.json --algorithm worklist
```

PySpark algorithm:

```bash
python attractor_spark.py --file data/graph_1000.json --algorithm mapreduce
```

### Shell Scripts

Individual benchmarks with timing:

```bash
./run_naive.sh graph_1000.json
./run_spark.sh graph_1000.json
```

## Generating Test Graphs

Generate graphs for testing (stored in `data/` directory):

```bash
# Generate 1000-node graph
python ../generators/generate_graph.py --nodes 1000 --max-out 3 --seed 42 --out data/graph_1000.json

# Generate 100,000-node graph
python ../generators/generate_graph.py --nodes 100000 --max-out 3 --seed 42 --out data/graph_100000.json
```

Graph format:
- Each node has an owner (0 or 1 for Player 1/2)
- Priority value (0-15, for other algorithms)
- List of outgoing edges (targets)

## Running Benchmarks

### Comprehensive Benchmark Suite

Run full benchmark across multiple graph sizes:

```bash
./run_comparison.sh
```

This will:
- Generate graphs of sizes: 1000, 5000, 10000, 50000, 100000, 500000
- Run both implementations on each
- Compare results for correctness
- Save timing results to `results/benchmark_results.json`

### Generating Plots

After running benchmarks:

```bash
python plot.py results/benchmark_results.json results/attractor_comparison.png
```

Creates a 4-panel visualization showing:
- Linear-scale execution time comparison
- Log-log scale execution time
- Speedup analysis
- Performance summary table

## Performance Characteristics

### Naive Algorithm
- **Pros**: Simple, predictable, good for small graphs
- **Cons**: O(iterations × nodes) each round
- **Best for**: Graphs < 10,000 nodes

### Worklist Algorithm
- **Pros**: Only processes affected nodes, 5-10x faster
- **Cons**: More complex implementation
- **Best for**: All sizes, recommended algorithm

### PySpark Implementations
- **Pros**: Parallelizes computation, scales to large graphs
- **Cons**: Spark overhead (~3-5 seconds minimum), network overhead
- **Best for**: Very large graphs (> 100,000 nodes) with multiple machines
- **Overhead**: Currently slower on single machine due to initialization cost

## Algorithm Parameters

Both implementations accept:

- `--file`: Path to graph JSON file (required)
- `--target-size`: Number of nodes in target set (default: 10)
- `--seed`: Random seed for target set selection (default: 42)
- `--algorithm`: For naive: `naive` or `worklist`; For spark: `mapreduce` or `mapreduce-key`

## Output

Each implementation prints:
- Graph node count
- Target set size
- Computed attractor size
- Number of iterations/rounds
- Execution time

Example:
```
Graph nodes: 1000
Target set size: 10
Attractor size: 247
Algorithm: worklist
Iterations/rounds: 15
Time: 0.002345 seconds
```

## Troubleshooting

**"File not found"**: Ensure graph has been generated to `data/` directory

**"No such file or directory (script)"**: When running from different directory, use absolute paths:
```bash
/path/to/attractor/run_naive.sh graph_1000.json
```

**PySpark takes too long**: 
- Spark has ~3-5 second startup overhead
- For small graphs (< 50K nodes), naive algorithm is faster
- PySpark advantage appears with very large graphs and multiple machines

**Matplotlib import error**: Install with `pip install matplotlib`

## Convergence Analysis

The number of iterations depends on:
1. Graph structure (how "winning" nodes chain)
2. Target set size
3. Graph size (roughly logarithmic)

Typical iteration counts:
- Small targets (10 nodes): 10-20 iterations
- Medium targets (100 nodes): 20-40 iterations
- Large targets (1000 nodes): 40-80 iterations

## References

See `ALGORITHM.md` for formal algorithm specification and theoretical background.

