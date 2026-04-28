# Graph Complexity Analysis

**Author:** Kevin Le
**Date:** 2026-04-24
**Lab:** Lab 7 - NPC Dialog with Graphs

---

## 1. Implementation Overview

My graph uses an adjacency-list representation backed by a custom `HashTable`. Each node ID maps to a list of outgoing edges stored as `(neighbor_id, weight, edge_data)` tuples, and node payloads are stored in a second `HashTable`. The graph is undirected by default, but `DialogGraph` creates it in directed mode for NPC dialog trees.

---

## 2. Time Complexity Table

| Method            | Your Big-O | Justification (1 sentence each) |
|-------------------|------------|----------------------------------|
| `add_node`        | O(1) avg   | It inserts or updates entries in two hash tables. |
| `add_edge`        | O(1) avg   | It appends one edge tuple to an adjacency list, plus one reverse append for undirected graphs. |
| `remove_node`     | O(V + E)   | It must scan every node's outgoing edge list to remove references to the deleted node. |
| `remove_edge`     | O(degree)  | It linearly searches the source node's adjacency list to find the matching edge. |
| `has_node`        | O(1) avg   | Membership is a hash-table lookup. |
| `has_edge`        | O(degree)  | It scans the source node's adjacency list until it finds the destination. |
| `get_neighbors`   | O(1)       | It returns a shallow copy of the already-stored adjacency list for that node. |
| `bfs`             | O(V + E)   | Each reachable node is dequeued once and each outgoing edge is inspected once. |
| `dfs`             | O(V + E)   | Each reachable node is popped once and each outgoing edge is inspected once. |
| `shortest_path`   | O(V + E)   | It uses BFS and parent tracking, so the traversal still touches each reachable node and edge at most once. |

---

## 3. Benchmark Results

Run `python graph_complexity.py` and paste the output below.

```
Graph Benchmark Results
========================================================================
   Nodes     Build(s)    has_node(s)     BFS(s)     DFS(s)  Shortest(s)
------------------------------------------------------------------------
     100     0.001791       0.000027   0.000314   0.000333     0.000460
     500     0.004192       0.000230   0.001399   0.001927     0.000473
    1000     0.006426       0.000380   0.002772   0.003672     0.000529
```

---

## 4. Space Complexity

The graph uses **O(V + E)** space, where `V` is the number of nodes and `E` is the number of edges. There is one adjacency-list entry per node plus one stored tuple for each edge, along with a separate hash-table entry for each node's data payload.

---

## 5. Reflection Questions

**Q1.** BFS and DFS both visit every reachable node exactly once.
Why might BFS be preferred for `shortest_path` even though both are O(V + E)?

*Your answer:* BFS explores nodes in layers by edge count, so the first time it reaches the goal it has found the fewest-edge path. DFS can reach the goal through a much longer branch before it ever explores a shorter route.

---

**Q2.** Your adjacency list uses O(V + E) space. An adjacency *matrix* uses O(V^2).
For the NPC dialog trees in this lab (small, sparse graphs), which representation is
more appropriate? Would your answer change for a 10,000-node social network graph?

*Your answer:* An adjacency list is the better choice for these sparse dialog trees because each node only connects to a few choices. I would still prefer an adjacency list for a 10,000-node social network because that graph is also usually sparse compared with a full `V^2` matrix.

---

**Q3.** Compare your `bfs` timing to networkx's (if you ran the comparison).
What accounts for the difference? Is networkx faster or slower, and why?

*Your answer:* I did not run the optional `networkx` comparison. If I did, I would expect `networkx` to be competitive because it is a mature library with optimized internals, while my implementation prioritizes clarity and lab requirements.

---

## 6. Conclusions

The graph performed well for the benchmark sizes in this lab, and the traversal times scaled in a way that matches the expected linear behavior over nodes and edges. One improvement would be replacing some list-based bookkeeping with a purpose-built queue structure to reduce constant factors. In the game, graphs directly model NPC dialog trees by storing dialog states as nodes and player choices as edges.

---

## 7. References

