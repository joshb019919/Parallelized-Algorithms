# Parallelized Algorithms: Minimax & Attractor

This project implements and benchmarks two graph algorithms using both sequential and PySpark parallel approaches:

1. **Minimax Algorithm**: Minimax game tree evaluation
   - Naive (sequential): Traditional recursive minimax in Python
   - Parallel (PySpark): Bottom-up level-by-level evaluation using PySpark RDDs

2. **Attractor Algorithm**: Two-player game graph attractor computation
   - Naive (sequential): Iterative worklist algorithm in Python
   - Parallel (PySpark): Worklist-based computation in PySpark context

Both algorithms include comprehensive benchmarking tools comparing performance and accuracy across implementations, with automatic dataset generation and visualization.

## Project Structure

```
.
├── README.md                    # This file
├── generators/                  # Dataset generation utilities
│   ├── generate_tree.py        # Generate random game trees
│   ├── generate_graph.py       # Generate random game graphs
│   └── tictactoe_move_generator.py  # Generate tic-tac-toe game trees
├── minimax/                     # Minimax algorithm implementations
│   ├── README.md               # Minimax-specific documentation
│   ├── minimax_naive.py        # Sequential minimax
│   ├── minimax_spark.py        # PySpark minimax
│   ├── main.py                 # Entry point
│   ├── plot.py                 # Visualization
│   ├── run_comparison.sh       # Comprehensive benchmark suite
│   ├── run_naive.sh            # Individual naive benchmark
│   ├── run_spark.sh            # Individual PySpark benchmark
│   ├── data/                   # Pre-generated datasets
│   └── results/                # Benchmark outputs
└── attractor/                   # Attractor algorithm implementations
    ├── README.md               # Attractor-specific documentation
    ├── attractor_naive.py      # Sequential attractor
    ├── attractor_spark.py      # PySpark attractor
    ├── main.py                 # Entry point
    ├── plot.py                 # Visualization
    ├── ALGORITHM.md            # Algorithm specification
    ├── PERFORMANCE_ANALYSIS.md # Detailed crossover analysis
    ├── CROSSOVER_SUMMARY.txt   # Quick reference summary
    ├── run_comparison.sh       # Comprehensive benchmark suite
    ├── run_naive.sh            # Individual naive benchmark
    ├── run_spark.sh            # Individual PySpark benchmark
    ├── data/                   # Pre-generated datasets
    └── results/                # Benchmark outputs
```

## Running Algorithms

### Quick Start: Full Benchmark Suite

The easiest way to run comprehensive benchmarks for either algorithm is to use the `run_comparison.sh` scripts.

#### Minimax Benchmarking

```bash
cd minimax/
./run_comparison.sh
```

This will:
1. Create a Python virtual environment (if needed)
2. Install dependencies (numpy, matplotlib, pyspark, etc.)
3. Generate tree datasets at multiple scales (0 to 10M nodes)
4. Run both naive and PySpark implementations on each dataset
5. Save results to `results/benchmark_results.json`
6. Generate a 4-panel visualization: `results/minimax_comparison.png`
  - Panel 1: Linear-scale timing comparison
  - Panel 2: Log-log scale timing
  - Panel 3: Speedup analysis (naive / spark)
  - Panel 4: Performance summary table

#### Attractor Benchmarking

```bash
cd attractor/
./run_comparison.sh
```

Same process as minimax, with results saved to:
- `results/benchmark_results.json`
- `results/attractor_comparison.png`

Additionally, the attractor project includes performance analysis:
- `ALGORITHM.md` - Formal algorithm specification
- `PERFORMANCE_ANALYSIS.md` - Detailed crossover analysis with math
- `CROSSOVER_SUMMARY.txt` - Quick reference summary

### Individual Algorithm Execution

#### Minimax

Run both algorithms and compare:

```bash
cd minimax/
python main.py --file data/tree_dataset_1000.json --mode both
```

Run only naive:

```bash
python main.py --file data/tree_dataset_1000.json --mode naive
```

Run only PySpark:

```bash
python main.py --file data/tree_dataset_1000.json --mode parallel
```

#### Attractor

Run both algorithms and compare:

```bash
cd attractor/
python main.py --file data/graph_1000.json --target-size 10 --mode both
```

Run only naive:

```bash
python main.py --file data/graph_1000.json --target-size 10 --algorithm naive
```

Run only PySpark (mapreduce variant):

```bash
python main.py --file data/graph_1000.json --target-size 10 --algorithm mapreduce
```

Run PySpark mapreduce-key variant:

```bash
python main.py --file data/graph_1000.json --target-size 10 --algorithm mapreduce-key
```

### Individual Shell Scripts

#### Minimax Scripts

```bash
cd minimax/
./scripts/run_naive.sh tree_dataset_500.json
./scripts/run_parallel.sh tree_dataset_500.json
./scripts/compare_single.sh tree_dataset_500.json
```

#### Attractor Scripts

```bash
cd attractor/
./run_naive.sh graph_1000.json
./run_spark.sh graph_1000.json
```

## Optimizations for Large Datasets

Both algorithms are optimized to handle large datasets efficiently:

### Minimax Optimizations

- **Level-by-level evaluation**: PySpark processes game tree levels in parallel
- **Bottom-up computation**: Only computes values once, no redundant traversals
- **Memory efficiency**: Processes and discards completed levels
- **RDD caching**: Intermediate results cached for efficient reuse

### Attractor Optimizations

- **Worklist algorithm**: Avoids redundant node processing
- **Predecessor tracking**: Efficiently identifies nodes that can join the attractor
- **Out-degree counting** (for Player 2): Optimizes edge satisfaction checks
- **Broadcast variables**: Efficiently shares graph data across Spark workers

## Performance Analysis

### When to Use Each Implementation

#### Minimax

| Metric | Naive | Spark |
|--------|-------|-------|
| **Best for** | Trees < 500k nodes | Trees > 500k nodes |
| **Startup cost** | ~10ms | ~3 seconds |
| **Per-node efficiency** | ~5 µs | ~3 µs |
| **Crossover point** | ~500k nodes | ~500k nodes |

#### Attractor

| Metric | Naive | Spark |
|--------|-------|-------|
| **Best for** | Graphs < 1.25M nodes | Graphs > 1.25M nodes |
| **Startup cost** | ~10ms | ~3 seconds |
| **Per-node efficiency** | ~5.8 µs | ~3.4 µs |
| **Crossover point** | ~1.25M nodes | ~1.25M nodes |

**Key Finding**: PySpark has better per-node efficiency but higher startup overhead. Sequential algorithms dominate for practical sizes but PySpark wins for extremely large instances.

For detailed analysis with mathematical derivations, see:
- `minimax/README.md` - Minimax-specific details
- `attractor/PERFORMANCE_ANALYSIS.md` - Detailed crossover math
- `attractor/CROSSOVER_SUMMARY.txt` - Quick reference

## Dataset Generators

Both algorithms include utilities to generate test datasets:

### Generating Tree Datasets (for Minimax)

Generate a tree with 130,000 nodes (default branching 3):

```bash
cd generators/
python generate_tree.py --nodes 130000 --max-children 3 --out tree_130k.json
```

Generate tic-tac-toe game tree:

```bash
python tictactoe_move_generator.py
```

### Generating Graph Datasets (for Attractor)

Generate a graph with 120,000 nodes (default max out-degree 3):

```bash
cd generators/
python generate_graph.py --nodes 120000 --max-out 3 --out graph_120k.json
```

### Generator Options

Both generators accept:
- `--seed N` - Make results deterministic
- `--binary-out` or `-b` - Output as compact pickle binary
- `--compress` - Gzip-compress binary output

Example with binary output and gzip:

```bash
python generate_graph.py -n 120000 -b graph_120k.bin --compress
python generate_tree.py -n 130000 -b tree_130k.bin --compress
```

## Benchmark Results & Visualization

After running `./run_comparison.sh` in either directory, results are saved to:

**Minimax**:
- `minimax/results/benchmark_results.json` - Raw benchmark data
- `minimax/results/minimax_comparison.png` - 4-panel visualization

**Attractor**:
- `attractor/results/benchmark_results.json` - Raw benchmark data
- `attractor/results/attractor_comparison.png` - 4-panel visualization

Each visualization includes:
- **Linear-scale timing comparison**: Shows raw execution times
- **Log-log scale**: Reveals algorithmic complexity
- **Speedup analysis**: PySpark speedup over naive
- **Summary table**: Results with correctness verification (✓/✗)

## Algorithm Documentation

### Minimax Algorithm

The minimax algorithm computes optimal game values for game trees using a recursive approach (naive) or PySpark-based level-by-level evaluation (parallel).

See `minimax/README.md` for:
- Detailed algorithm explanation
- Usage examples
- Performance characteristics
- Algorithm complexity analysis

### Attractor Algorithm

The attractor algorithm computes the set of nodes in a two-player game graph that can attract play to a target set, using either iterative worklist (naive) or PySpark context (parallel).

See `attractor/README.md` for:
- Formal algorithm specification in `ALGORITHM.md`
- Detailed performance analysis in `PERFORMANCE_ANALYSIS.md`
- Quick reference in `CROSSOVER_SUMMARY.txt`

## Requirements

- Python 3.8+
- PySpark 4.0+
- NumPy
- Matplotlib
- Java runtime (for PySpark)

## Installation

### Using the Virtual Environment (Recommended)

Each algorithm's `run_comparison.sh` script automatically creates and configures a virtual environment with all dependencies:

```bash
cd minimax/
./run_comparison.sh  # Automatically sets up environment
```

### Manual Installation

```bash
python -m venv venv
source venv/bin/activate
pip install pyspark numpy matplotlib
```

## Project Status

**✅ Completed**:
- Minimax sequential and PySpark implementations
- Attractor sequential and PySpark implementations
- Comprehensive benchmarking for both algorithms
- Automatic visualization generation
- Performance analysis and crossover point identification
- All correctness tests passing

**Current Findings**:
- Sequential implementations dominate for practical sizes
- PySpark becomes advantageous at 500k nodes (minimax) and 1.25M nodes (attractor)
- ~3-second JVM startup overhead is the main limiting factor
- Per-node efficiency favors PySpark (~3-3.4 µs vs 5-5.8 µs for naive)
