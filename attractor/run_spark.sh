#!/bin/bash
# Run spark attractor with timing

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

if [ -z "$1" ]; then
    echo "Usage: $0 <dataset_filename>"
    echo "Example: $0 graph_1000.json"
    exit 1
fi

DATASET="$SCRIPT_DIR/data/$1"
PYTHON="$PROJECT_DIR/.venv/bin/python"

echo "=== SPARK Attractor (Parallel MapReduce) ==="
echo "Dataset: $DATASET"
echo ""

/usr/bin/time -f "Wall clock time: %e seconds\nCPU time: %U seconds (user) + %S seconds (system)\nMemory: %M KB" \
    $PYTHON $SCRIPT_DIR/attractor_spark.py --file "$DATASET" --target-size 10 --algorithm mapreduce 2>&1 | grep -v "WARN\|Using Spark\|WARNING"

echo ""
