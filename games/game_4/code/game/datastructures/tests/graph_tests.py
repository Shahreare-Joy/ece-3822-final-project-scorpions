"""
graph_tests.py - Unit tests for Graph

Author: Kevin Le
Date:   4/26/2026
Lab:    Lab 7 - NPC Dialog with Graphs

Run with:
    cd code/game/datastructures/tests
    python graph_tests.py
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from datastructures.graph import Graph


def _sample_graph(directed=True):
    graph = Graph(directed=directed)
    graph.add_edge("A", "B")
    graph.add_edge("A", "C")
    graph.add_edge("B", "D")
    graph.add_edge("C", "E")
    return graph


def test_add_node_and_get_node_data():
    graph = Graph()
    graph.add_node("elder", {"text": "Hello"})
    assert graph.has_node("elder")
    assert graph.get_node_data("elder") == {"text": "Hello"}
    print("PASS test_add_node_and_get_node_data")


def test_add_edge_creates_missing_nodes():
    graph = Graph(directed=True)
    graph.add_edge("start", "end", weight=3, edge_data="Continue")
    assert graph.has_node("start")
    assert graph.has_node("end")
    assert graph.has_edge("start", "end")
    assert graph.get_neighbors("start") == [("end", 3, "Continue")]
    print("PASS test_add_edge_creates_missing_nodes")


def test_undirected_edge_semantics():
    graph = Graph(directed=False)
    graph.add_edge("x", "y")
    assert graph.has_edge("x", "y")
    assert graph.has_edge("y", "x")
    print("PASS test_undirected_edge_semantics")


def test_directed_edge_semantics():
    graph = Graph(directed=True)
    graph.add_edge("x", "y")
    assert graph.has_edge("x", "y")
    assert not graph.has_edge("y", "x")
    print("PASS test_directed_edge_semantics")


def test_remove_edge():
    graph = Graph(directed=True)
    graph.add_edge("a", "b")
    graph.remove_edge("a", "b")
    assert not graph.has_edge("a", "b")
    print("PASS test_remove_edge")


def test_remove_node_removes_touching_edges():
    graph = _sample_graph(directed=True)
    graph.remove_node("B")
    assert not graph.has_node("B")
    assert not graph.has_edge("A", "B")
    print("PASS test_remove_node_removes_touching_edges")


def test_nodes_and_len():
    graph = Graph()
    graph.add_node("one")
    graph.add_node("two")
    assert len(graph) == 2
    assert set(graph.nodes()) == {"one", "two"}
    print("PASS test_nodes_and_len")


def test_bfs_discovery_order():
    graph = _sample_graph(directed=True)
    order = graph.bfs("A")
    assert order[0] == "A"
    assert order == ["A", "B", "C", "D", "E"]
    print("PASS test_bfs_discovery_order")


def test_dfs_reachability_and_start():
    graph = _sample_graph(directed=True)
    order = graph.dfs("A")
    assert order[0] == "A"
    assert set(order) == {"A", "B", "C", "D", "E"}
    print("PASS test_dfs_reachability_and_start")


def test_shortest_path_found():
    graph = _sample_graph(directed=True)
    graph.add_edge("B", "E")
    assert graph.shortest_path("A", "E") == ["A", "B", "E"]
    print("PASS test_shortest_path_found")


def test_shortest_path_no_path():
    graph = Graph(directed=True)
    graph.add_edge("A", "B")
    graph.add_node("C")
    assert graph.shortest_path("A", "C") == []
    print("PASS test_shortest_path_no_path")


def test_shortest_path_self():
    graph = Graph(directed=True)
    graph.add_node("solo")
    assert graph.shortest_path("solo", "solo") == ["solo"]
    print("PASS test_shortest_path_self")


def test_isolated_node_neighbors():
    graph = Graph()
    graph.add_node("alone")
    assert graph.get_neighbors("alone") == []
    assert graph.bfs("alone") == ["alone"]
    print("PASS test_isolated_node_neighbors")


def test_self_loop():
    graph = Graph(directed=True)
    graph.add_edge("loop", "loop")
    assert graph.has_edge("loop", "loop")
    assert graph.bfs("loop") == ["loop"]
    print("PASS test_self_loop")


def test_get_node_data_missing_raises():
    graph = Graph()
    try:
        graph.get_node_data("missing")
        raise AssertionError("Expected KeyError")
    except KeyError:
        pass
    print("PASS test_get_node_data_missing_raises")


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