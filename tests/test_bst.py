"""
BST tests.

Unit tests for the BinarySearchTree implementation.
Tests cover insert/search behavior, sorted traversal,
duplicate-key updates, and range queries.
"""

import unittest

from datastructures.bst import BinarySearchTree

class TestBST(unittest.TestCase):
    
    def test_empty_tree_search_returns_none(self) -> None:
        """Verify that searching an empty tree returns None."""
        tree = BinarySearchTree()
        self.assertIsNone(tree.search("missing"))

    def test_insert_and_search(self) -> None:
        """Verify that inserted keys can be searched successfully."""
        tree = BinarySearchTree()
        tree.insert("bob", 20)
        tree.insert("alice", 10)
        tree.insert("carol", 30)

        self.assertEqual(tree.search("alice"), 10)
        self.assertEqual(tree.search("bob"), 20)
        self.assertEqual(tree.search("carol"), 30)

    def test_inorder_returns_sorted_values(self) -> None:
        """Verify that inorder traversal follows sorted key order."""
        tree = BinarySearchTree()
        tree.insert("bob", "B")
        tree.insert("alice", "A")
        tree.insert("carol", "C")

        self.assertEqual(tree.inorder(), ["A", "B", "C"])

    def test_duplicate_key_updates_value(self) -> None:
        """Verify that inserting the same key again updates its value."""
        tree = BinarySearchTree()
        tree.insert("alice", 10)
        tree.insert("alice", 99)

        self.assertEqual(tree.search("alice"), 99)

    def test_range_query_returns_expected_values(self) -> None:
        """Verify that range_query returns values whose keys fall within the bounds."""
        tree = BinarySearchTree()
        tree.insert("alice", "A")
        tree.insert("bob", "B")
        tree.insert("carol", "C")
        tree.insert("dave", "D")
        tree.insert("eve", "E")

        self.assertEqual(tree.range_query("bob", "dave"), ["B", "C", "D"])