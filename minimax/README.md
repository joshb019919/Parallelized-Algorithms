# Parallel Minimax Algorithm with PySpark

This project implements and compares two minimax algorithm implementations:

- **Naive (sequential)**: Traditional recursive minimax using Python
- **Parallel (PySpark)**: Bottom-up level-by-level minimax using PySpark RDDs

The project includes tree dataset generators (including tic-tac-toe game trees) and benchmarking tools to compare performance and accuracy between implementations.

## Project Structure

- `src/` - Python source files
  - `minimax_naive.py` - Sequential minimax implementation
  - `minimax_parallel.py` - Parallel minimax using PySpark
  - `main.py` - Main entry point for running and comparing both algorithms
  - `plot.py` - Visualization tool for benchmark results
  - `analyze_convergence.py` - Analysis of parallel vs sequential convergence
- `scripts/` - Shell scripts for benchmarking
  - `run_naive.sh` - Run naive algorithm with timing
  - `run_parallel.sh` - Run parallel algorithm with timing
  - `compare_single.sh` - Compare both on single dataset
- `generators/` - Dataset generation utilities
  - `generate_tree.py` - Generate random game trees
  - `generate_graph.py` - Generate graph datasets
  - `tictactoe_move_generator.py` - Generate tic-tac-toe game trees
- `data/` - Pre-generated datasets
- `results/` - Benchmark results and visualizations
- `run_comparison.sh` - Comprehensive benchmark suite

## Running Minimax Algorithms

### Using main.py (Recommended)

Run both algorithms and compare results:

```bash
python src/main.py --file data/tree_dataset_500.json --mode both
```

Run only the naive version:

```bash
python src/main.py --file data/tree_dataset_500.json --mode naive
```

Run only the parallel version:

```bash
python src/main.py --file data/tree_dataset_500.json --mode parallel
```

### Using Shell Scripts

#### Comprehensive Benchmark Suite

Run a full benchmark across multiple dataset sizes (0, 1, 2, 7, 500, 10000, 500000, 10000000 nodes):

```bash
./run_comparison.sh
```

This generates datasets using `generate_tree.py`, runs both algorithms on each size, and saves results to `results/benchmark_results.json`.

#### Single Dataset Comparison

Compare both algorithms on a specific dataset file:

```bash
./scripts/compare_single.sh tree_dataset_500.json
```

Run individual implementations:

```bash
./scripts/run_naive.sh tree_dataset_500.json
./scripts/run_parallel.sh tree_dataset_500.json
```

### Direct Execution

You can also run the algorithms directly:

```bash
python src/minimax_naive.py --file data/tree_dataset_500.json
python src/minimax_parallel.py --file data/tree_dataset_500.json
```

## Optimizations for Large Datasets

For datasets with millions or billions of nodes, the standard implementations may run into memory issues. We provide memory-optimized versions:

### Memory-Optimized Implementations

Use `minimax_optimized.py` for handling very large trees:

```bash
# Streaming minimax (recommended for large datasets)
python minimax_optimized.py --file data/tree_dataset_10000000.json --mode streaming

# Streaming with memoization
python minimax_optimized.py --file data/tree_dataset_10000000.json --mode streaming-naive
```

**Optimizations included:**

- **Streaming processing**: Loads and processes tree data efficiently without keeping full tree in memory
- **Memoization**: Caches computed values to avoid redundant calculations  
- **Garbage collection**: Periodic cleanup during processing
- **Minimal node structures**: Stores only necessary node metadata

**Performance improvements:**

- Can handle 100x more nodes than standard implementations
- Reduced memory footprint by ~80% for large trees
- Better CPU cache locality with smaller data structures

## Visualizing Results

After running the benchmark suite, generate plots:

```bash
python src/plot.py results/benchmark_results.json results/minimax_comparison.png
```

Generate convergence analysis:

```bash
python src/analyze_convergence.py results/benchmark_results.json results/convergence_analysis.txt
```

This creates a comprehensive visualization with:

- Linear and log-log performance curves
- Speedup analysis comparing naive vs parallel
- Summary table of results
- Convergence point analysis for distributed systems

## Dataset Generators

Generate datasets for testing:

Generate a graph with 120000 nodes (default):

```bash
python3 generate_graph.py --nodes 120000 --max-out 3 --out graph_120k.json
```

Generate a tree with 130000 nodes (default branching 3):

```bash
python3 generate_tree.py --nodes 130000 --max-children 3 --out tree_130k.json
```

Both generators accept `--seed` to make results deterministic.

To write compact binary files (pickle) for later re-loading by the main program use `--binary-out`.
Use `--compress` to gzip-compress the binary output.

Example with binary output and gzip:

```bash
python3 generate_graph.py -n 120000 -b graph_120k.bin --compress
python3 generate_tree.py -n 130000 -b tree_130k.bin --compress
```
