"""
Heap tests.

Unit tests for the MaxHeap implementation.
Tests cover empty-heap behavior, push/pop order,
and peek behavior for leaderboard-style priorities.

"""

import unittest

from datastructures.heap import MaxHeap

class TestHeap(unittest.TestCase):
    def test_empty_heap_pop_raises_error(self) -> None:
        """Verify that popping from an empty heap raises an error."""
        heap = MaxHeap()
        with self.assertRaises(IndexError):
            heap.pop_max()

    def test_empty_heap_peek_raises_error(self) -> None:
        """Verify that peeking into an empty heap raises an error."""
        heap = MaxHeap()
        with self.assertRaises(IndexError):
            heap.peek_max()

    def test_push_one_item_and_peek(self) -> None:
        """Verify that a single pushed item becomes the max item."""
        heap = MaxHeap()
        heap.push(100, "alice")
        self.assertEqual(heap.peek_max(), "alice")

    def test_push_many_and_pop_in_priority_order(self) -> None:
        """Verify that items are popped from highest priority to lowest."""
        heap = MaxHeap()
        heap.push(100, "alice")
        heap.push(300, "carol")
        heap.push(200, "bob")

        self.assertEqual(heap.pop_max(), "carol")
        self.assertEqual(heap.pop_max(), "bob")
        self.assertEqual(heap.pop_max(), "alice")

    def test_peek_does_not_remove_item(self) -> None:
        """Verify that peek_max returns the top item without removing it."""
        heap = MaxHeap()
        heap.push(100, "alice")
        heap.push(300, "carol")

        self.assertEqual(heap.peek_max(), "carol")
        self.assertEqual(heap.pop_max(), "carol")

    def test_push_after_pop_still_maintains_heap_order(self) -> None:
        """Verify heap order remains correct after popping and pushing again."""
        heap = MaxHeap()
        heap.push(100, "alice")
        heap.push(300, "carol")
        self.assertEqual(heap.pop_max(), "carol")

        heap.push(200, "bob")
        self.assertEqual(heap.pop_max(), "bob")
        self.assertEqual(heap.pop_max(), "alice")