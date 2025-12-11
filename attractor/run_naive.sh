#!/bin/bash
# Run naive attractor with timing

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

if [ -z "$1" ]; then
    echo "Usage: $0 <dataset_filename>"
    echo "Example: $0 graph_1000.json"
    exit 1
fi

DATASET="$SCRIPT_DIR/data/$1"
PYTHON="$PROJECT_DIR/.venv/bin/python"

echo "=== NAIVE Attractor (Sequential) ==="
echo "Dataset: $DATASET"
echo ""

/usr/bin/time -f "Wall clock time: %e seconds\nCPU time: %U seconds (user) + %S seconds (system)\nMemory: %M KB" \
    $PYTHON $SCRIPT_DIR/attractor_naive.py --file "$DATASET" --target-size 10 --algorithm worklist

echo ""
