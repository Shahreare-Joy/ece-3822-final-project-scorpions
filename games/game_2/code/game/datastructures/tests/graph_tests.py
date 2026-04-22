"""
graph_tests.py - Unit tests for Graph

Author: [Your Name]
Date:   [Date]
Lab:    Lab 7 - NPC Dialog with Graphs

TODO (Part 5)
-------------
Write at least ten tests. Your tests must cover all of these:
  - add_node, add_edge, has_node, has_edge
  - get_neighbors, get_node_data
  - remove_node, remove_edge
  - bfs  (check discovery order and reachability)
  - dfs  (check discovery order and reachability)
  - shortest_path (path exists, no path exists, self-path)
  - directed vs. undirected edge semantics
  - edge cases: disconnected graph, isolated node, self-loop

Run with:
    cd code/game/datastructures/tests
    python graph_tests.py
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from datastructures.graph import Graph


# ---------------------------------------------------------------------------
# TODO: Write at least 10 tests below.
# Each function must start with 'test_', use assert, and print "PASS <name>".
# Below are some examples you could implement.
# ---------------------------------------------------------------------------



# ---------------------------------------------------------------------------
# Do not modify
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    tests = [
        (name, fn)
        for name, fn in sorted(globals().items())
        if name.startswith("test_") and callable(fn)
    ]

    passed = failed = 0
    for name, fn in tests:
        try:
            fn()
            passed += 1
        except Exception as exc:
            print(f"FAIL {name}: {exc}")
            failed += 1

    print(f"\n{'=' * 50}")
    print(f"Results: {passed} passed, {failed} failed / {passed + failed} total")
    if failed:
        sys.exit(1)
    else:
        print("All tests passed!")
