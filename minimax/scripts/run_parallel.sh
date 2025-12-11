#!/bin/bash
# Run parallel minimax with timing

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

echo "=== PARALLEL Minimax (PySpark) ==="
echo "Dataset: $DATASET"
echo ""

# Use time command for accurate timing, suppress Spark warnings
/usr/bin/time -f "Wall clock time: %e seconds\nCPU time: %U seconds (user) + %S seconds (system)\nMemory: %M KB" \
    $PYTHON $PROJECT_DIR/src/minimax_parallel.py --file "$DATASET" 2>&1 | grep -v "WARN\|Using Spark\|WARNING"

echo ""
