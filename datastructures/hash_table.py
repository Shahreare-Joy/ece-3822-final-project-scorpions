from __future__ import annotations

"""Custom chained hash table.
 
Use cases:
- account username lookup
- platform_server/accounts.py  -> username -> player/account record
- platform_server/catalog.py   -> game_id  -> game record
- platform_server/history.py   -> player_id -> session list pointer
 
Expected average complexity:
- put:    O(1) average, O(n) worst case (all keys collide)
- get:    O(1) average, O(n) worst case
- remove: O(1) average, O(n) worst case
- resize: O(n)  -- rebuilds every bucket
"""
 
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))
from array import Array
 
 
# ---------------------------------------------------------------------------
# Node used for separate chaining inside each bucket
# ---------------------------------------------------------------------------
 
class _HashNode:
    """A single key-value pair in a chain.
 
    Attributes:
        key:   The lookup key (string).
        value: The associated value (any Python object).
        next:  Pointer to the next node in the same bucket chain, or None.
    """
 
    def __init__(self, key: str, value: object) -> None:
        self.key: str = key
        self.value: object = value
        self.next: _HashNode | None = None
 
 
# ---------------------------------------------------------------------------
# Chained hash table
# ---------------------------------------------------------------------------
 
class ChainedHashTable:
    """Hash table that resolves collisions with separate chaining.
 
    Buckets are stored in a custom Array (not a Python list).
    Each bucket slot holds the head _HashNode of a linked chain,
    or None if the bucket is empty.
 
    Attributes:
        capacity (int): Number of buckets currently allocated.
        _size    (int): Number of key-value pairs stored.
        _buckets (Array): Custom array holding the chain heads.
        _load_factor_limit (float): Resize threshold (default 0.75).
    """
 
    _LOAD_FACTOR_LIMIT: float = 0.75
 
    def __init__(self, capacity: int = 16) -> None:
        """Create an empty hash table with *capacity* buckets.
 
        Args:
            capacity: Initial bucket count. Must be positive.
 
        Time complexity: O(n) to initialise the bucket Array.
        """
        if capacity <= 0:
            raise ValueError("capacity must be positive")
        self.capacity: int = capacity
        self._size: int = 0
        self._buckets: Array = self._make_buckets(capacity)
 
    # ------------------------------------------------------------------
    # Public interface
    # ------------------------------------------------------------------
 
    def put(self, key: str, value: object) -> None:
        """Insert or update *key* with *value*.
 
        If the key already exists its value is overwritten.
        Resizes the table when the load factor exceeds the limit.
 
        Args:
            key:   String lookup key.
            value: Any Python object.
 
        Time complexity: O(1) average, O(n) worst case (full collision chain).
        """
        # Resize before inserting if load factor is too high
        if self._size / self.capacity >= self._LOAD_FACTOR_LIMIT:
            self._resize(self.capacity * 2)
 
        index = self._hash(key)
        node = self._buckets.get(index)
 
        # Walk the chain -- update if key already exists
        current = node
        while current is not None:
            if current.key == key:
                current.value = value
                return
            current = current.next
 
        # Key not found -- prepend new node to the chain (O(1))
        new_node = _HashNode(key, value)
        new_node.next = node          # old head becomes second node
        self._buckets.set(index, new_node)
        self._size += 1
 
    def get(self, key: str) -> object | None:
        """Return the value associated with *key*, or None if not found.
 
        Args:
            key: String lookup key.
 
        Returns:
            Stored value, or None.
 
        Time complexity: O(1) average, O(n) worst case.
        """
        index = self._hash(key)
        current = self._buckets.get(index)
        while current is not None:
            if current.key == key:
                return current.value
            current = current.next
        return None
 
    def remove(self, key: str) -> bool:
        """Remove the entry for *key*.
 
        Handles removal from the beginning, middle, or end of a chain.
 
        Args:
            key: String lookup key.
 
        Returns:
            True if the key was found and removed, False otherwise.
 
        Time complexity: O(1) average, O(n) worst case.
        """
        index = self._hash(key)
        current = self._buckets.get(index)
        prev = None
 
        while current is not None:
            if current.key == key:
                if prev is None:
                    # Removing the head of the chain
                    self._buckets.set(index, current.next)
                else:
                    # Bypass the current node
                    prev.next = current.next
                self._size -= 1
                return True
            prev = current
            current = current.next
 
        return False   # key not found
 
    def contains(self, key: str) -> bool:
        """Return True if *key* exists in the table.
 
        Time complexity: O(1) average, O(n) worst case.
        """
        return self.get(key) is not None
 
    def keys(self) -> list:
        """Return a list of all keys in the table.
 
        Time complexity: O(n) -- must visit every bucket and every chain node.
        """
        result = []
        for i in range(self.capacity):
            current = self._buckets.get(i)
            while current is not None:
                result.append(current.key)
                current = current.next
        return result
 
    def values(self) -> list:
        """Return a list of all values in the table.
 
        Time complexity: O(n).
        """
        result = []
        for i in range(self.capacity):
            current = self._buckets.get(i)
            while current is not None:
                result.append(current.value)
                current = current.next
        return result
 
    def __len__(self) -> int:
        """Return number of key-value pairs stored.
 
        Time complexity: O(1).
        """
        return self._size
 
    def __repr__(self) -> str:
        return f"ChainedHashTable(size={self._size}, capacity={self.capacity})"
 
    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------
 
    def _hash(self, key: str) -> int:
        """Map *key* to a bucket index using Python's built-in hash function.
 
        We use Python's hash() only as a numeric primitive (like calling
        a CPU multiply instruction) -- the table logic itself is custom.
 
        Time complexity: O(k) where k is the length of the key string.
        """
        return hash(key) % self.capacity
 
    def _make_buckets(self, capacity: int) -> Array:
        """Allocate a fresh Array of *capacity* slots, all set to None.
 
        Time complexity: O(n).
        """
        buckets = Array(capacity)
        for _ in range(capacity):
            buckets.append(None)
        return buckets
 
    def _resize(self, new_capacity: int) -> None:
        """Rehash all entries into a new bucket array of *new_capacity*.
 
        Called automatically when load factor exceeds the limit.
        All existing keys are reinserted because their bucket index
        depends on the capacity and must be recalculated.
 
        Time complexity: O(n) -- every entry is rehashed once.
        """
        old_buckets = self._buckets
        old_capacity = self.capacity
 
        self.capacity = new_capacity
        self._buckets = self._make_buckets(new_capacity)
        self._size = 0   # put() will recount
 
        for i in range(old_capacity):
            current = old_buckets.get(i)
            while current is not None:
                self.put(current.key, current.value)
                current = current.next

  # end of file
