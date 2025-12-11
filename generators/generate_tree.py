#!/usr/bin/env python3
"""Generate a rooted tree dataset for testing minimax algorithms.

Output format (JSON):
{
  "node_count": n,
  "root": 0,
  "nodes": [
    {"id": 0, "owner": 0, "value": null, "children": [1,2]},
    {"id": 1, "owner": 1, "value": 5, "children": []},
    ...
  ]
}

The generator builds the tree breadth-first until the requested node count is reached.
"""
import argparse
import json
import random
import sys
import os
from collections import deque
from typing import Any, Deque, List


def generate_tree(n: int, max_children: int, leaf_value_range: tuple, seed: int = 0):
    if seed is not None:
        random.seed(seed)

    if n <= 0:
        return {"node_count": 0, "root": None, "nodes": []}

    nodes: list[dict[str, Any]] = []
    type = "max"

    # Create root
    root: dict[str, Any] = {"id": 0, "type": type, "children": [], "value": None}
    nodes.append(root)
    next_id = 1
    q: Deque[dict[str, Any]] = deque()
    q.append(root)

    while next_id < n and q:
        parent = q.popleft()
        parent_type = parent["type"]
        child_type = "min" if parent_type == "max" else "max"

        # Remaining nodes available for children
        remaining = n - next_id

        # Propose up to max_children, but not more than remaining
        max_c = min(max_children, remaining)
        if max_c <= 0:
            continue

        # Give parent at least 1 child when possible
        num_children = random.randint(1, max_c)
        children = []
        for _ in range(num_children):
            owner = random.randint(0, 1)

            # Initially add internal node; value assigned when leaf
            child = {"id": next_id, "type": child_type, "children": [], "value": None}
            nodes.append(child)
            children.append(next_id)
            q.append(child)
            next_id += 1

            if next_id >= n:
                break

        nodes[parent["id"]]["children"] = children

    # Any nodes without children are leaves: assign value
    for node in nodes:
        if not node["children"]:
            node["value"] = random.randint(leaf_value_range[0], leaf_value_range[1])
            node["type"] = "leaf"

    return {"node_count": len(nodes), "root": 0, "nodes": nodes}


def main(argv: List[str]):
    p = argparse.ArgumentParser(description="Generate a rooted tree dataset for minimax tests")
    p.add_argument("--nodes", "-n", type=int, default=120000,
                   help="Number of nodes to generate (recommended 100000-150000)")
    p.add_argument("--max-children", type=int, default=3,
                   help="Maximum number of children per internal node")
    p.add_argument("--seed", type=int, default=None, help="Random seed")
    p.add_argument("--leaf-min", type=int, default=-100, help="Min leaf value")
    p.add_argument("--leaf-max", type=int, default=100, help="Max leaf value")
    p.add_argument("--out", "-o", type=str, default="tree_dataset.json",
                   help="Output JSON file path")
    args = p.parse_args(argv)

    if args.nodes < 1:
        print("--nodes must be >=1", file=sys.stderr)
        sys.exit(2)

    # Add tree size to file names
    args.out = args.out.split(".")
    args.out = ".".join(["data/" + args.out[0] + f"_{args.nodes}", args.out[1]])

    # Check if output file already exists
    if os.path.exists(args.out):
        print(f"File already exists: {args.out}")
        print(f"Skipping generation. Remove the file if you want to regenerate.")
        sys.exit(0)

    data = generate_tree(args.nodes, args.max_children, (args.leaf_min, args.leaf_max), args.seed)
    with open(args.out, "w") as fh:
        json.dump(data, fh, separators=(',', ':'), ensure_ascii=False)

    print(f"Wrote tree with {data['node_count']} nodes to {args.out}")
if __name__ == "__main__":
    main(None)
