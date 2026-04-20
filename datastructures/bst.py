from __future__ import annotations

"""Binary Search Tree skeleton.

Use cases:
- ordered player/game search
- autocomplete or prefix range traversal if keys are strings
- score range queries
- date range queries for match history

Expected complexity:
- balanced tree: O(log n) insert/search
- unbalanced tree: O(n) worst case

TODO(BST): Implement insert, search, range query, and traversal. If the team
needs guaranteed balance, document the chosen balancing strategy.
"""


class BinarySearchTree:
    def __init__(self) -> None:
        self.root = None

    def insert(self, key: object, value: object) -> None:
        _ = (key, value)
        raise NotImplementedError

    def search(self, key: object) -> object | None:
        _ = key
        raise NotImplementedError

    def range_query(self, low: object, high: object) -> list[object]:
        # TODO(BST RANGE): Return values with low <= key <= high.
        _ = (low, high)
        raise NotImplementedError

    def inorder(self) -> list[object]:
        raise NotImplementedError
