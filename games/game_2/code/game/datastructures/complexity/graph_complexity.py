"""
graph_complexity.py - Performance benchmarks for Graph

Author: [Your Name]
Date:   [Date]
Lab:    Lab 7 - NPC Dialog with Graphs

TODO (Part 6)
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
