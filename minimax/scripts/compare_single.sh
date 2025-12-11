#!/bin/bash
# Run comparison on a single dataset file

if [ -z "$1" ]; then
    echo "Usage: $0 <dataset_filename>"
    echo "Example: $0 tree_dataset_500.json"
    exit 1
fi

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

DATASET="$PROJECT_DIR/data/$1"
PYTHON="$PROJECT_DIR/.venv/bin/python"

echo "========================================"
echo "  Minimax Algorithm Comparison"
echo "  Dataset: $DATASET"
echo "========================================"
echo ""

# Run naive version
echo "--- NAIVE (Non-Parallel) Version ---"
NAIVE_START=$(date +%s.%N)
NAIVE_RESULT=$($PYTHON $PROJECT_DIR/src/minimax_naive.py --file "$DATASET" 2>&1)
NAIVE_END=$(date +%s.%N)
NAIVE_TIME=$(echo "$NAIVE_END - $NAIVE_START" | bc)
echo "$NAIVE_RESULT"
echo ""

# Run parallel version
echo "--- PARALLEL (PySpark) Version ---"
PARALLEL_START=$(date +%s.%N)
PARALLEL_RESULT=$($PYTHON $PROJECT_DIR/src/minimax_parallel.py --file "$DATASET" 2>&1 | grep -v "WARN\|Using Spark\|WARNING\|Stage \|25/")
PARALLEL_END=$(date +%s.%N)
PARALLEL_TIME=$(echo "$PARALLEL_END - $PARALLEL_START" | bc)
echo "$PARALLEL_RESULT"
echo ""

# Extract results for comparison
NAIVE_VALUE=$(echo "$NAIVE_RESULT" | grep "Result:" | awk '{print $2}')
PARALLEL_VALUE=$(echo "$PARALLEL_RESULT" | grep "Result:" | awk '{print $2}')

# Summary
echo "========================================"
echo "  SUMMARY"
echo "========================================"
echo "Naive result:    $NAIVE_VALUE"
echo "Parallel result: $PARALLEL_VALUE"
echo ""
echo "Naive time:      ${NAIVE_TIME}s"
echo "Parallel time:   ${PARALLEL_TIME}s"
echo ""

if [ "$NAIVE_VALUE" = "$PARALLEL_VALUE" ]; then
    echo "✓ Results match!"
else
    echo "✗ Results differ!"
fi

if (( $(echo "$NAIVE_TIME < $PARALLEL_TIME" | bc -l) )); then
    SPEEDUP=$(echo "scale=2; $PARALLEL_TIME / $NAIVE_TIME" | bc)
    echo "Naive is ${SPEEDUP}x faster"
else
    SPEEDUP=$(echo "scale=2; $NAIVE_TIME / $PARALLEL_TIME" | bc)
    echo "Parallel is ${SPEEDUP}x faster"
fi
echo ""
