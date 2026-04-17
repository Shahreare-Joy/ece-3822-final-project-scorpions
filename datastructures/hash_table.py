from __future__ import annotations

"""Custom chained hash table skeleton.

Use cases:
- account username lookup
- player profile lookup
- game_id lookup
- session indexes

Expected average complexity:
- insert: O(1) average, O(n) worst case
- get: O(1) average, O(n) worst case
- delete: O(1) average, O(n) worst case

TODO(HASH TABLE): Implement chaining with custom node/array storage. Do not use
Python dict as the final assignment solution.
"""


class ChainedHashTable:
    def __init__(self, capacity: int = 1024) -> None:
        self.capacity = capacity
        # TODO: create bucket array using datastructures/array.py.
        raise NotImplementedError("Team must implement chained hash table.")

    def put(self, key: str, value: object) -> None:
        _ = (key, value)
        raise NotImplementedError

    def get(self, key: str) -> object | None:
        _ = key
        raise NotImplementedError

    def remove(self, key: str) -> bool:
        _ = key
        raise NotImplementedError
