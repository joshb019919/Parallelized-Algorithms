import json
import sys
import time


class NaiveMinimax:
    def __init__(self):
        pass

    def minimax(self, tree):
        """
        Non-parallel (naive) minimax using simple recursion.
        Assumes tree nodes have: id, type ('max'/'min'/'leaf'), children[], value
        """
        if tree["node_count"] == 0:
            return None
        
        nodes_dict = {node["id"]: node for node in tree["nodes"]}
        
        def compute_value(node_id):
            node = nodes_dict[node_id]
            
            # Base case: leaf node
            if node["type"] == "leaf" or not node["children"]:
                return node["value"]
            
            # Recursive case: compute children values
            child_values = [compute_value(child_id) for child_id in node["children"]]
            
            # Apply min or max based on node type
            if node["type"] == "max":
                return max(child_values)
            else:  # "min"
                return min(child_values)
        
        return compute_value(tree["root"])


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Run naive (non-parallel) minimax algorithm")
    parser.add_argument("--file", required=True, help="Path to the tree dataset JSON file")
    args = parser.parse_args()
    
    nm = NaiveMinimax()

    with open(args.file, "r") as f:
        tree = json.load(f)
    
    print(f"Computing minimax for {tree['node_count']}-node tree...")
    start = time.time()
    result = nm.minimax(tree)
    elapsed = time.time() - start
    
    print(f"Result: {result}")
    print(f"Time: {elapsed:.4f} seconds")
