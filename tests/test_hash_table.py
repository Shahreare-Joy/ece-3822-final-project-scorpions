"""
Hash table tests.

Unit tests for the ChainedHashTable implementation.
Tests cover basic CRUD operations (Create, Read, Update, Delete) 
and edge cases like missing keys.
"""
import unittest

from datastructures.hash_table import ChainedHashTable

class TestHashTable(unittest.TestCase):

    def test_empty_table_returns_none_for_missing_key(self) -> None:
        """Verify that searching for a key that doesn't exist returns None."""
        table = ChainedHashTable()
        self.assertIsNone(table.get("missing"))

    def test_insert_and_lookup(self) -> None: 
        """Verify that a value can be successfully stored and retrieved."""
        table = ChainedHashTable()
        table.put("alice", 100)
        self.assertEqual(table.get("alice"), 100)

    def test_update_existing_key(self) -> None:
        """Verify that putting a new value for an existing key overwrites the old value."""
        table = ChainedHashTable()
        table.put("alice", 100)
        table.put("alice", 200)
        self.assertEqual(table.get("alice"), 200)

    def test_remove_existing_key(self) -> None:
        """Verify that removing a key works and returns True, and the key is gone."""
        table = ChainedHashTable()
        table.put("alice", 100)
        self.assertTrue(table.remove("alice"))
        self.assertIsNone(table.get("alice"))

    def test_remove_missing_key_returns_false(self) -> None:
        """Verify that attempting to remove a non-existent key returns False."""
        table = ChainedHashTable()
        # Correctly asserts that deletion fails gracefully for missing keys
        self.assertFalse(table.remove("missing"))