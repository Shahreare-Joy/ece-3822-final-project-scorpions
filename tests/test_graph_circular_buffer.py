"""Graph and circular-buffer tests for chat/recommendation structures."""

import unittest

from datastructures.circular_buffer import CircularBuffer
from datastructures.graph import Graph


class TestGraphAndCircularBuffer(unittest.TestCase):
    def test_circular_buffer_overwrites_oldest(self) -> None:
        buffer = CircularBuffer(capacity=3)
        buffer.append("one")
        buffer.append("two")
        buffer.append("three")
        self.assertTrue(buffer.is_full())
        buffer.append("four")
        self.assertEqual(buffer.get_recent(), ["two", "three", "four"])
        buffer.clear()
        self.assertEqual(buffer.get_recent(), [])

    def test_graph_neighbors_traversal_and_remove_edge(self) -> None:
        graph = Graph()
        graph.add_edge("player", "game-a")
        graph.add_edge("player", "game-b")
        graph.add_edge("game-a", "genre-arcade")
        self.assertEqual([edge.target for edge in graph.neighbors("player")], ["game-a", "game-b"])
        self.assertEqual(graph.bfs("player")[:3], ["player", "game-a", "game-b"])
        self.assertIn("genre-arcade", graph.dfs("player"))
        self.assertTrue(graph.remove_edge("player", "game-b"))
        self.assertFalse(graph.remove_edge("player", "missing"))


if __name__ == "__main__":
    unittest.main()
