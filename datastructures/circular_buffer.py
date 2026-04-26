from __future__ import annotations

"""Circular buffer for chat.

Use cases:
- keep only the most recent N chat messages per session
- prevent unlimited client/server memory growth

Expected complexity:
- append: O(1)
- recent traversal: O(k), where k is number of returned messages

TODO (DONE)(CIRCULAR BUFFER): Implement with fixed-size custom array storage.
"""

from .array import Array


class CircularBuffer:
    def __init__(self, capacity: int = 100) -> None:
        # initialize buffer with fixed capacity and reset pointers
        if capacity <= 0:
            raise ValueError("capacity must be positive")
        self.capacity = capacity

        # allocate underlying array storage
        self._storage = Array(capacity)

        # _start points to oldest element, _count tracks current size
        self._start = 0
        self._count = 0

    def __len__(self) -> int:
        '''return current number of elements in buffer'''
        return self._count

    def append(self, value: object) -> None:
        '''append new value, overwrite oldest if buffer is full'''

        if self._count < self.capacity:
            # buffer not full: insert at end position
            index = (self._start + self._count) % self.capacity
            self._count += 1
        else:
            # buffer full: overwrite oldest and move start forward
            index = self._start
            self._start = (self._start + 1) % self.capacity

        # store value in computed index
        self._storage.set(index, value)

    def recent(self, limit: int | None = None) -> list[object]:
        '''return most recent elements up to limit'''

        if limit is None or limit > self._count:
            # default to all elements if limit is not provided or too large
            limit = self._count

        if limit <= 0:
            # no elements requested
            return []

        # calculate starting offset for recent elements
        start_offset = self._count - limit
        results: list[object] = []

        # iterate from oldest relevant to newest
        for offset in range(start_offset, self._count):
            index = (self._start + offset) % self.capacity
            results.append(self._storage.get(index))

        return results

    def get_recent(self, count: int | None = None) -> list[object]:
        '''alias for recent() for readability in other modules'''
        return self.recent(count)

    def is_full(self) -> bool:
        '''check if buffer has reached capacity'''
        return self._count == self.capacity

    def clear(self) -> None:
        '''reset buffer to empty state'''

        # reinitialize storage to clear all values
        self._storage = Array(self.capacity)

        # reset pointers
        self._start = 0
        self._count = 0