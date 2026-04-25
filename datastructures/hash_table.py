from __future__ import annotations

"""Custom chained hash table.

Use cases:
- account username lookup
- player profile lookup
- game_id lookup
- session indexes

Expected average complexity:
- insert: O(1) average, O(n) worst case
- get: O(1) average, O(n) worst case
- delete: O(1) average, O(n) worst case

TODO (DONE)(HASH TABLE): Implement chaining with custom node/array storage. This
uses ``datastructures.array.Array`` for buckets and linked nodes for collision
chains instead of Python dict as the core storage.
"""

from dataclasses import dataclass
from typing import Iterator

from .array import Array


@dataclass
class _HashNode:
    # store key-value pair and pointer to next node in chain
    key: object
    value: object
    next: "_HashNode | None" = None


class ChainedHashTable:
    """readable separate-chaining hash table."""

    def __init__(self, capacity: int = 1024, max_load_factor: float = 0.75) -> None:
        # validate hash table capacity
        if capacity <= 0:
            raise ValueError("capacity must be positive")

        # validate resizing threshold
        if max_load_factor <= 0:
            raise ValueError("max_load_factor must be positive")

        # store capacity and max load factor
        self.capacity = capacity
        self.max_load_factor = max_load_factor

        # TODO (DONE): create bucket array using datastructures/array.py.

        # create bucket array for linked-list chains
        self._buckets = Array(capacity)

        # track number of stored key-value pairs
        self._size = 0

    def __len__(self) -> int:
        '''return number of key-value pairs'''
        return self._size

    def _bucket_index(self, key: object) -> int:
        '''convert key into bucket index'''

        # use Python hash, then fit into bucket range
        return hash(key) % self.capacity

    def put(self, key: object, value: object) -> None:
        '''insert or update key-value pair'''

        # resize if adding this item would exceed load factor
        if (self._size + 1) / self.capacity > self.max_load_factor:
            self._resize(self.capacity * 2)

        # find correct bucket
        index = self._bucket_index(key)
        node = self._buckets.get(index)

        # search chain for existing key
        while node is not None:
            if node.key == key:
                # update value if key already exists
                node.value = value
                return
            node = node.next

        # insert new node at front of chain
        self._buckets.set(index, _HashNode(key, value, self._buckets.get(index)))
        self._size += 1

    def get(self, key: object, default: object | None = None) -> object | None:
        '''return value for key, or default if missing'''

        # start at bucket chain
        node = self._buckets.get(self._bucket_index(key))

        # search linked chain
        while node is not None:
            if node.key == key:
                return node.value
            node = node.next

        return default

    def contains(self, key: object) -> bool:
        '''check whether key exists in table'''

        # use unique sentinel so stored None values still work correctly
        sentinel = object()
        return self.get(key, sentinel) is not sentinel

    def remove(self, key: object) -> bool:
        '''remove key-value pair if it exists'''

        # find bucket for key
        index = self._bucket_index(key)
        node = self._buckets.get(index)
        previous: _HashNode | None = None

        # walk chain until key is found
        while node is not None:
            if node.key == key:
                if previous is None:
                    # removing first node in chain
                    self._buckets.set(index, node.next)
                else:
                    # skip over removed node
                    previous.next = node.next

                self._size -= 1
                return True

            previous = node
            node = node.next

        return False

    def items(self) -> Iterator[tuple[object, object]]:
        '''iterate through all key-value pairs'''

        # scan every bucket
        for bucket_index in range(self.capacity):
            node = self._buckets.get(bucket_index)

            # yield each node in this chain
            while node is not None:
                yield node.key, node.value
                node = node.next

    def values(self) -> Iterator[object]:
        '''iterate through all stored values'''

        # reuse items iterator and return only values
        for _, value in self.items():
            yield value

    def _resize(self, new_capacity: int) -> None:
        '''resize table and rehash all items'''

        # save existing items before replacing buckets
        old_items = list(self.items())

        # create new bucket array
        self.capacity = new_capacity
        self._buckets = Array(new_capacity)
        self._size = 0

        # reinsert old items so bucket indexes are recalculated
        for key, value in old_items:
            self.put(key, value)