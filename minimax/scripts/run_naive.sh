#!/bin/bash
# Run naive (non-parallel) minimax with timing

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

echo "=== NAIVE (Non-Parallel) Minimax ==="
echo "Dataset: $DATASET"
echo ""

# Use time command for accurate timing
/usr/bin/time -f "Wall clock time: %e seconds\nCPU time: %U seconds (user) + %S seconds (system)\nMemory: %M KB" \
    $PYTHON $PROJECT_DIR/src/minimax_naive.py --file "$DATASET"

echo ""
