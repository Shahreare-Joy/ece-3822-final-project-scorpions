# Graph Complexity Analysis

**Author:** [Your Name]
**Date:** [Date]
**Lab:** Lab 7 — NPC Dialog with Graphs

---

## 1. Implementation Overview

*Describe your Graph implementation in 2–3 sentences. What does your adjacency list look like in memory? Is it directed or undirected by default?*

---

## 2. Time Complexity Table

| Method            | Your Big-O | Justification (1 sentence each) |
|-------------------|------------|----------------------------------|
| `add_node`        |            |                                  |
| `add_edge`        |            |                                  |
| `remove_node`     |            |                                  |
| `remove_edge`     |            |                                  |
| `has_node`        |            |                                  |
| `has_edge`        |            |                                  |
| `get_neighbors`   |            |                                  |
| `bfs`             |            |                                  |
| `dfs`             |            |                                  |
| `shortest_path`   |            |                                  |

---

## 3. Benchmark Results

*Run `python graph_complexity.py` and paste the output below.*

```
(paste output here)
```

---

## 4. Space Complexity

*How much memory does your graph use?*
*Express as O(V + E), and explain what V and E represent in your implementation.*

---

## 5. Reflection Questions

**Q1.** BFS and DFS both visit every reachable node exactly once.
Why might BFS be preferred for `shortest_path` even though both are O(V + E)?

*Your answer:*

---

**Q2.** Your adjacency list uses O(V + E) space. An adjacency *matrix* uses O(V²).
For the NPC dialog trees in this lab (small, sparse graphs), which representation is
more appropriate? Would your answer change for a 10,000-node social network graph?

*Your answer:*

---

**Q3.** Compare your `bfs` timing to networkx's (if you ran the comparison).
What accounts for the difference? Is networkx faster or slower, and why?

*Your answer:*

---

## 6. Conclusions

*Write 2–3 sentences summarising: (1) how your implementation performed, (2) one thing you would change to make it faster, and (3) how graphs appear in the game (dialog trees, NPC relationships, etc.).*

---

## 7. References

*List any resources you consulted (textbooks, websites, lecture slides). AI tool use must also appear in `ai_conversations.md`.*
