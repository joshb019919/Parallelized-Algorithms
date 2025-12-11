import sys
import os
from typing import Any

# Set string hash determinism to fix [PYTHON_HASH_SEED_NOT_SET] error
os.environ["PYTHONHASHSEED"] = "0"


class ParallelMinimax:
    def __init__(self):
        self.sc = self.create_spark()

        # Quick options for testing
        self.simple_tree = {"node_count": 7, "root": 0, "nodes": [
            # id,  type,  children,  value
            {"id": 0, "type": "max", "children": [1, 2], "value": None},  # Root
            {"id": 1, "type": "min", "children": [3, 4], "value": None},
            {"id": 2, "type": "min", "children": [5, 6], "value": None},
            {"id": 3, "type": "leaf", "children": [], "value": 5},
            {"id": 4, "type": "leaf", "children": [], "value": 4},
            {"id": 5, "type": "leaf", "children": [], "value": 7},
            {"id": 6, "type": "leaf", "children": [], "value": -2}
        ]}

        self.two_nodes = {"node_count": 2, "root": 0, "nodes": 
                         [{"id": 0, "type": "max", "children": [1], "value": None},
                          {"id": 1, "type": "leaf", "children": [], "value": 1}]}
        self.one_node = {"node_count": 1, "root": 0, "nodes": 
                         [{"id": 0, "type": "leaf", "children": [], "value": 1}]}
        self.empty_tree = {"node_count": 0, "root": None, "nodes": []}

    def create_spark(self):
        from pyspark import SparkConf, SparkContext
        conf = SparkConf().setMaster("local[*]").setAppName("Spark Lab")
        return SparkContext(conf = conf)

    def minimax(self, tree):
        """Parallel minimax using PySpark RDDs.

        Assumes tree nodes have: id, type ('max'/'min'/'leaf'), children[], value.
        """

        if tree["node_count"] == 0:
            return None
        elif tree["node_count"] == 1:
            return tree["nodes"][0]["value"]
        elif tree["node_count"] == 2:
            return tree["nodes"][1]["value"]

        nodes_dict = {node["id"]: node for node in tree["nodes"]}
        
        # Start with all leaf values (either marked as "leaf" type or have no children)
        values_dict = {
            node["id"]: node["value"] 
            for node in tree["nodes"] 
            if node["type"] == "leaf" or (not node["children"] and node["value"] is not None)
        }
        
        # Iteratively compute parent values until root is done
        while tree["root"] not in values_dict:
            # Find parents whose ALL children have values
            ready_parents = []
            for node in tree["nodes"]:
                if node["type"] != "leaf" and node["id"] not in values_dict:
                    if all(child_id in values_dict for child_id in node["children"]):
                        ready_parents.append(node)
            
            if not ready_parents:
                break  # No more progress possible
            
            # Compute values for ready parents in parallel
            parent_data = [(node["id"], node["type"], 
                           [values_dict[child_id] for child_id in node["children"]]) 
                          for node in ready_parents]
            
            parent_rdd = self.sc.parallelize(parent_data)
            
            # Apply min or max based on node type
            results = parent_rdd.map(lambda x: (
                x[0],  # parent_id
                max(x[2]) if x[1] == "max" else min(x[2])  # max for "max" nodes, min for "min" nodes
            )).collect()
            
            # Update values dictionary
            for parent_id, value in results:
                values_dict[parent_id] = value
    
        return values_dict.get(tree["root"])


if __name__ == "__main__":
    import json
    import argparse
    import time

    parser = argparse.ArgumentParser(description="Run parallel minimax algorithm with PySpark")
    parser.add_argument("--file", required=True, help="Path to the tree dataset JSON file")
    args = parser.parse_args()
    
    pm = ParallelMinimax()

    with open(args.file, "r") as f:
        tree = json.load(f)
    
    print(f"Computing minimax for {tree['node_count']}-node tree...")
    start = time.time()
    result = pm.minimax(tree)
    elapsed = time.time() - start
    
    print(f"Result: {result}")
    print(f"Time: {elapsed:.4f} seconds")
