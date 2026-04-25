"""Search tests.

Unit tests for search helper functions.
Tests cover case-insensitive prefix matching,
empty-query behavior, and no-match cases.
"""

import unittest

from algorithms.search_algorithms import (
    brute_force_prefix,
    make_fallback_index,
    prefix_search,
)


class TestSearch(unittest.TestCase):
    def setUp(self) -> None:
        """Create a small sample dataset used by all search tests."""
        self.players = [
            {"username": "alice"},
            {"username": "ALIEN"},
            {"username": "bob"},
            {"username": "bobby"},
            {"username": "carol"},
        ]
        self.key_func = lambda row: row["username"]

    def test_case_insensitive_player_search(self) -> None:
        """Verify prefix matching ignores case."""
        matches = brute_force_prefix(self.players, "ali", self.key_func)
        self.assertEqual([row["username"] for row in matches], ["alice", "ALIEN"])

    def test_prefix_search_returns_expected_usernames(self) -> None:
        """Verify prefix search returns all matching usernames."""
        index = make_fallback_index(self.players, self.key_func)
        matches = prefix_search(index, "bob", limit=10)
        self.assertEqual([row["username"] for row in matches], ["bob", "bobby"])

    def test_empty_query_returns_all_records(self) -> None:
        """Verify an empty prefix returns every record."""
        matches = brute_force_prefix(self.players, "", self.key_func)
        self.assertEqual(matches, self.players)

    def test_no_match_returns_empty_list(self) -> None:
        """Verify a non-matching prefix returns an empty list."""
        self.assertEqual(brute_force_prefix(self.players, "zzz", self.key_func), [])

    def test_fallback_index_matches_bruteforce_baseline(self) -> None:
        """Verify fallback indexed search matches brute-force results."""
        index = make_fallback_index(self.players, self.key_func)
        brute_force = brute_force_prefix(self.players, "al", self.key_func)
        indexed = prefix_search(index, "al", limit=10)
        self.assertEqual(indexed, brute_force