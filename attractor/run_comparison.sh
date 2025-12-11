#!/bin/bash
# Run comprehensive benchmark comparing naive and spark attractor across multiple graph sizes
# Generates graphs, runs experiments, and saves results

# Get project root directory
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
VENV_DIR="$PROJECT_DIR/.venv"
PYTHON_EXEC="$VENV_DIR/bin/python"

echo "========================================"
echo "  Attractor Benchmark Suite"
echo "========================================"
echo ""

# Check and create virtual environment if needed
echo "Checking Python environment..."
if [ ! -d "$VENV_DIR" ]; then
    echo "Virtual environment not found. Creating at: $VENV_DIR"
    python3 -m venv "$VENV_DIR"
    if [ $? -ne 0 ]; then
        echo "ERROR: Failed to create virtual environment"
        exit 1
    fi
    echo "✓ Virtual environment created"
else
    echo "✓ Virtual environment already exists"
fi

# Activate virtual environment
source "$VENV_DIR/bin/activate"

# Install/upgrade dependencies
echo ""
echo "Checking dependencies..."
DEPS_INSTALLED=false

# Check if required packages are installed
$PYTHON_EXEC -c "import pyspark; import matplotlib" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "Installing dependencies (pyspark, matplotlib)..."
    $PYTHON_EXEC -m pip install -q pyspark matplotlib
    if [ $? -ne 0 ]; then
        echo "ERROR: Failed to install dependencies"
        exit 1
    fi
    echo "✓ Dependencies installed"
    DEPS_INSTALLED=true
else
    echo "✓ Dependencies already present"
fi

echo ""
echo "Environment ready. Generating graphs and running experiments..."
echo ""

PYTHON="$PYTHON_EXEC"
RESULTS_FILE="results/benchmark_results.json"
SEED=42

# Graph sizes to benchmark
SIZES=(1000 5000 10000 50000 100000 500000 1000000)

echo "Results will be saved to: $RESULTS_FILE"
echo ""

# Create results directory if needed
mkdir -p results

# Initialize results JSON
echo "[" > "$RESULTS_FILE"

FIRST=true

for SIZE in "${SIZES[@]}"; do
    DATASET_FILE="graph_${SIZE}.json"
    DATASET_PATH="data/$DATASET_FILE"
    
    echo "=== Testing with $SIZE nodes ==="
    
    # Generate graph
    echo "  Step 1: Generating graph..."
    if ! $PYTHON ../generators/generate_graph.py --nodes "$SIZE" --max-out 3 --seed "$SEED" --out "$DATASET_PATH" 2>&1 | grep -q "Wrote graph"; then
        echo "  ERROR: Failed to generate graph"
        continue
    fi
    echo "  ✓ Graph created"
    
    # Run naive algorithm
    echo "  Step 2: Running naive attractor..."
    NAIVE_START=$(date +%s%N)
    NAIVE_OUTPUT=$($PYTHON attractor_naive.py --file "$DATASET_PATH" --target-size 10 --algorithm worklist 2>&1)
    NAIVE_RESULT=$?
    NAIVE_END=$(date +%s%N)
    
    if [ $NAIVE_RESULT -ne 0 ]; then
        echo "  ERROR: Naive attractor failed"
        echo "$NAIVE_OUTPUT"
        continue
    fi
    
    NAIVE_TIME=$(echo "scale=6; ($NAIVE_END - $NAIVE_START) / 1000000000" | bc)
    NAIVE_SIZE=$(echo "$NAIVE_OUTPUT" | grep "Attractor size:" | awk '{print $3}')
    NAIVE_ITERS=$(echo "$NAIVE_OUTPUT" | grep "Iterations" | awk '{print $2}')
    echo "  ✓ Naive: ${NAIVE_TIME}s, Size: $NAIVE_SIZE, Iterations: $NAIVE_ITERS"
    
    # Run spark algorithm
    echo "  Step 3: Running spark attractor..."
    SPARK_START=$(date +%s%N)
    SPARK_OUTPUT=$($PYTHON attractor_spark.py --file "$DATASET_PATH" --target-size 10 --algorithm mapreduce 2>&1)
    SPARK_RESULT=$?
    SPARK_END=$(date +%s%N)
    
    if [ $SPARK_RESULT -ne 0 ]; then
        echo "  ERROR: Spark attractor failed"
        echo "$SPARK_OUTPUT"
        continue
    fi
    
    SPARK_TIME=$(echo "scale=6; ($SPARK_END - $SPARK_START) / 1000000000" | bc)
    SPARK_SIZE=$(echo "$SPARK_OUTPUT" | grep "Attractor size:" | awk '{print $3}')
    SPARK_ITERS=$(echo "$SPARK_OUTPUT" | grep "Iterations:" | awk '{print $2}')
    echo "  ✓ Spark: ${SPARK_TIME}s, Size: $SPARK_SIZE, Iterations: $SPARK_ITERS"
    
    # Append to results JSON
    if [ "$FIRST" = false ]; then
        echo "," >> "$RESULTS_FILE"
    fi
    FIRST=false
    
    # Ensure times have leading 0 if they start with decimal point
    NAIVE_TIME_JSON=$(echo "$NAIVE_TIME" | sed 's/^\./0./')
    SPARK_TIME_JSON=$(echo "$SPARK_TIME" | sed 's/^\./0./')
    
    cat >> "$RESULTS_FILE" << EOF
  {
    "nodes": $SIZE,
    "naive_time": $NAIVE_TIME_JSON,
    "spark_time": $SPARK_TIME_JSON,
    "naive_attractor_size": ${NAIVE_SIZE:-0},
    "spark_attractor_size": ${SPARK_SIZE:-0},
    "naive_iterations": ${NAIVE_ITERS:-0},
    "spark_iterations": ${SPARK_ITERS:-0},
    "match": $([ "$NAIVE_SIZE" = "$SPARK_SIZE" ] && echo "true" || echo "false")
  }
EOF
    
    echo ""
done

# Close JSON array
echo "" >> "$RESULTS_FILE"
echo "]" >> "$RESULTS_FILE"

echo ""
echo "========================================"
echo "  Benchmark Complete"
echo "========================================"
echo "Results saved to: $RESULTS_FILE"
echo ""
echo "Generating visualizations..."
$PYTHON plot.py "$RESULTS_FILE" "results/attractor_comparison.png"
if [ $? -eq 0 ]; then
    echo ""
    echo "Plot saved to: results/attractor_comparison.png"
else
    echo "WARNING: Could not generate plot (matplotlib may not be installed)"
fi
echo ""
