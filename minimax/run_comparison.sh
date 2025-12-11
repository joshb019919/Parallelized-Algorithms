#!/bin/bash
# Run comprehensive benchmark comparing naive and parallel minimax across multiple dataset sizes
# Generates datasets, runs experiments, and saves results

PYTHON="/home/josh-borthick/Documents/msu/csc735/project/.venv/bin/python"
RESULTS_FILE="results/benchmark_results.json"
SEED=42

# Dataset sizes to benchmark
SIZES=(100000 200000 300000 400000 500000 1000000 10000000 20000000)

echo "========================================"
echo "  Minimax Benchmark Suite"
echo "========================================"
echo ""
echo "Generating datasets and running experiments..."
echo "Results will be saved to: $RESULTS_FILE"
echo ""

# Initialize results JSON
echo "[" > "$RESULTS_FILE"

FIRST=true

for SIZE in "${SIZES[@]}"; do
    DATASET_FILE="tree_dataset_${SIZE}.json"
    DATASET_PATH="data/$DATASET_FILE"
    
    echo "=== Testing with $SIZE nodes ==="
    
    # Generate dataset
    echo "  Step 1: Generating dataset..."
    if [ "$SIZE" -eq 0 ]; then
        # Create empty tree manually
        echo '{"node_count": 0, "root": null, "nodes": []}' > "$DATASET_PATH"
        if [ $? -ne 0 ]; then
            echo "  ERROR: Failed to create empty tree"
            continue
        fi
    elif [ "$SIZE" -eq 1 ]; then
        # Create single node manually
        echo '{"node_count": 1, "root": 0, "nodes": [{"id": 0, "type": "leaf", "children": [], "value": 42}]}' > "$DATASET_PATH"
        if [ $? -ne 0 ]; then
            echo "  ERROR: Failed to create single-node tree"
            continue
        fi
    elif [ "$SIZE" -eq 2 ]; then
        # Create 2-node tree manually
        echo '{"node_count": 2, "root": 0, "nodes": [{"id": 0, "type": "max", "children": [1], "value": null}, {"id": 1, "type": "leaf", "children": [], "value": 10}]}' > "$DATASET_PATH"
        if [ $? -ne 0 ]; then
            echo "  ERROR: Failed to create 2-node tree"
            continue
        fi
    elif [ "$SIZE" -eq 7 ]; then
        # Create 7-node tree manually (balanced binary tree)
        echo '{"node_count": 7, "root": 0, "nodes": [{"id": 0, "type": "max", "children": [1, 2], "value": null}, {"id": 1, "type": "min", "children": [3, 4], "value": null}, {"id": 2, "type": "min", "children": [5, 6], "value": null}, {"id": 3, "type": "leaf", "children": [], "value": 5}, {"id": 4, "type": "leaf", "children": [], "value": 4}, {"id": 5, "type": "leaf", "children": [], "value": 7}, {"id": 6, "type": "leaf", "children": [], "value": -2}]}' > "$DATASET_PATH"
        if [ $? -ne 0 ]; then
            echo "  ERROR: Failed to create 7-node tree"
            continue
        fi
    else
        # Generate using generate_tree.py
        # Note: generator adds data/ prefix and _SIZE suffix automatically
        # So we pass just the base filename: tree_dataset.json
        if [ ! -f "$DATASET_PATH" ] || [ ! -s "$DATASET_PATH" ]; then
            echo "  Attempting to generate with generate_tree.py..."
            $PYTHON generators/generate_tree.py --nodes "$SIZE" --max-children 3 --out "tree_dataset.json" --seed "$SEED" > /dev/null 2>&1
            if [ ! -f "$DATASET_PATH" ] || [ ! -s "$DATASET_PATH" ]; then
                echo "  WARNING: Could not generate dataset for $SIZE nodes, skipping..."
                continue
            fi
        fi
    fi
    echo "  ✓ Dataset created"
    
    # Run naive algorithm
    echo "  Step 2: Running naive minimax..."
    NAIVE_START=$(date +%s%N)
    NAIVE_OUTPUT=$($PYTHON src/minimax_naive.py --file "$DATASET_PATH" 2>&1)
    NAIVE_RESULT=$?
    NAIVE_END=$(date +%s%N)
    
    if [ $NAIVE_RESULT -ne 0 ]; then
        echo "  ERROR: Naive minimax failed"
        echo "$NAIVE_OUTPUT"
        continue
    fi
    
    NAIVE_TIME=$(echo "scale=6; ($NAIVE_END - $NAIVE_START) / 1000000000" | bc)
    NAIVE_VALUE=$(echo "$NAIVE_OUTPUT" | grep "Result:" | awk '{print $2}')
    echo "  ✓ Naive: ${NAIVE_TIME}s, Result: $NAIVE_VALUE"
    
    # Run parallel algorithm
    echo "  Step 3: Running parallel minimax..."
    PARALLEL_START=$(date +%s%N)
    PARALLEL_OUTPUT=$($PYTHON src/minimax_parallel.py --file "$DATASET_PATH" 2>&1 | grep -v "WARN\|Using Spark\|WARNING\|Stage \|25/")
    PARALLEL_RESULT=$?
    PARALLEL_END=$(date +%s%N)
    
    if [ $PARALLEL_RESULT -ne 0 ]; then
        echo "  ERROR: Parallel minimax failed"
        echo "$PARALLEL_OUTPUT"
        continue
    fi
    
    PARALLEL_TIME=$(echo "scale=6; ($PARALLEL_END - $PARALLEL_START) / 1000000000" | bc)
    PARALLEL_VALUE=$(echo "$PARALLEL_OUTPUT" | grep "Result:" | awk '{print $2}')
    echo "  ✓ Parallel: ${PARALLEL_TIME}s, Result: $PARALLEL_VALUE"
    
    # Append to results JSON
    if [ "$FIRST" = false ]; then
        echo "," >> "$RESULTS_FILE"
    fi
    FIRST=false
    
    # Convert None to null and ensure proper JSON number format
    NAIVE_JSON_VALUE=$([ "$NAIVE_VALUE" = "None" ] && echo "null" || echo "$NAIVE_VALUE")
    PARALLEL_JSON_VALUE=$([ "$PARALLEL_VALUE" = "None" ] && echo "null" || echo "$PARALLEL_VALUE")
    
    # Ensure times have leading 0 if they start with decimal point
    NAIVE_TIME_JSON=$(echo "$NAIVE_TIME" | sed 's/^\./0./')
    PARALLEL_TIME_JSON=$(echo "$PARALLEL_TIME" | sed 's/^\./0./')
    
    cat >> "$RESULTS_FILE" << EOF
  {
    "nodes": $SIZE,
    "naive_time": $NAIVE_TIME_JSON,
    "parallel_time": $PARALLEL_TIME_JSON,
    "naive_result": $NAIVE_JSON_VALUE,
    "parallel_result": $PARALLEL_JSON_VALUE,
    "match": $([ "$NAIVE_VALUE" = "$PARALLEL_VALUE" ] && echo "true" || echo "false")
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
echo "To generate plots, run:"
echo "  python src/plot.py $RESULTS_FILE results/minimax_comparison.png"
echo "To generate convergence analysis, run:"
echo "  python src/analyze_convergence.py $RESULTS_FILE results/convergence_analysis.txt"
echo ""
