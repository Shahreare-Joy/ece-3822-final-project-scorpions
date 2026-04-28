"""
graph_complexity.py - Performance benchmarks for Graph

Author: Kevin Le
Date:   4/26/2026
Lab:    Lab 7 - NPC Dialog with Graphs

-------------
Write a benchmarking script that measures the performance of your Graph
implementation. Your script must:

  1. Build graphs of at least three different sizes (e.g. 100, 500, 1000 nodes).
  2. Measure the time for each of these operations at each size:
       - Building the graph (add_node / add_edge)
       - has_node (many random queries)
       - bfs from a starting node
       - dfs from a starting node
       - shortest_path for several random pairs
  3. Print a results table you can paste into analysis_write_up.md.

Optionally, compare against networkx (pip install networkx).

Run with:
    cd code/game/datastructures/complexity
    python graph_complexity.py
"""
import os
import sys
import time

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from datastructures.graph import Graph


def build_graph(size):
    """Create a moderately connected directed graph."""
    graph = Graph(directed=True)
    for node_id in range(size):
        graph.add_node(node_id)
    for node_id in range(size):
        if node_id + 1 < size:
            graph.add_edge(node_id, node_id + 1)
        if node_id + 2 < size:
            graph.add_edge(node_id, node_id + 2)
        if node_id + 5 < size:
            graph.add_edge(node_id, node_id + 5)
    return graph


def time_call(fn, repeats=1):
    """Measure average runtime for a callable."""
    start = time.perf_counter()
    for _ in range(repeats):
        fn()
    end = time.perf_counter()
    return (end - start) / repeats


def benchmark_size(size):
    """Run all benchmarks for one graph size."""
    build_time = time_call(lambda: build_graph(size))
    graph = build_graph(size)

    has_node_time = time_call(lambda: [graph.has_node(i) for i in range(size)], repeats=5)
    bfs_time = time_call(lambda: graph.bfs(0), repeats=5)
    dfs_time = time_call(lambda: graph.dfs(0), repeats=5)
    shortest_time = time_call(
        lambda: [graph.shortest_path(0, target) for target in range(min(size, 20))],
        repeats=5,
    )

    return {
        "size": size,
        "build": build_time,
        "has_node": has_node_time,
        "bfs": bfs_time,
        "dfs": dfs_time,
        "shortest_path": shortest_time,
    }


def main():
    """Print a benchmark table for several graph sizes."""
    sizes = [100, 500, 1000]
    results = [benchmark_size(size) for size in sizes]

    print("Graph Benchmark Results")
    print("=" * 72)
    print(
        f"{'Nodes':>8} {'Build(s)':>12} {'has_node(s)':>14} "
        f"{'BFS(s)':>10} {'DFS(s)':>10} {'Shortest(s)':>12}"
    )
    print("-" * 72)

    for row in results:
        print(
            f"{row['size']:>8} "
            f"{row['build']:>12.6f} "
            f"{row['has_node']:>14.6f} "
            f"{row['bfs']:>10.6f} "
            f"{row['dfs']:>10.6f} "
            f"{row['shortest_path']:>12.6f}"
        )


if __name__ == "__main__":
    main()
