<<<<<<< Updated upstream
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
=======
from __future__ import annotations
 
"""Circular buffer for per-session chat history.
 
Use cases:
- platform_server/chat.py -> keep only the most recent N messages per session
- prevents unlimited memory growth no matter how long a session runs
 
Expected complexity:
- append:      O(1)
- get_recent:  O(k) where k is number of messages returned
- clear:       O(1)
- Memory:      O(capacity) -- fixed, never grows
 
NOTE: Backed by a custom Array (datastructures/array.py), not a Python list.
When the buffer is full the oldest message is overwritten automatically by
advancing the head pointer -- no shifting of elements needed.
"""
 
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))
from array import Array
 
 
class CircularBuffer:
    """Fixed-capacity circular buffer that overwrites oldest data when full.
 
    Internally uses a flat Array of *capacity* slots with three integer
    counters to track position:
        _head  -- index of the oldest message (next to be overwritten)
        _tail  -- index where the next message will be written
        _count -- number of messages currently stored
 
    Attributes:
        capacity (int):  Maximum number of messages stored at once.
        _data (Array):   Fixed-size custom array holding message objects.
        _head (int):     Index of the oldest entry.
        _tail (int):     Index where next write goes.
        _count (int):    Number of entries currently in the buffer.
    """
 
    def __init__(self, capacity: int = 100) -> None:
        """Create an empty circular buffer with fixed *capacity*.
 
        Args:
            capacity: Maximum number of messages to keep. Must be positive.
 
        Raises:
            ValueError: If capacity is not positive.
 
        Time complexity: O(n) to initialise the Array slots.
        """
        if capacity <= 0:
            raise ValueError("capacity must be positive")
        self.capacity: int = capacity
        self._data: Array = Array(capacity)
        # Pre-fill so every slot is addressable via get/set
        for _ in range(capacity):
            self._data.append(None)
        self._head: int = 0   # oldest message slot
        self._tail: int = 0   # next write slot
        self._count: int = 0  # messages currently stored
 
    # ------------------------------------------------------------------
    # Public interface
    # ------------------------------------------------------------------
 
    def append(self, value: object) -> None:
        """Add *value* to the buffer, overwriting the oldest entry if full.
 
        Args:
            value: Any Python object (chat message string, dict, etc.).
 
        Time complexity: O(1)
        """
        self._data.set(self._tail, value)
        self._tail = (self._tail + 1) % self.capacity
 
        if self._count < self.capacity:
            self._count += 1
        else:
            # Buffer was full: head advances to keep up with tail
            self._head = (self._head + 1) % self.capacity
 
    def get_recent(self, limit: int | None = None) -> list:
        """Return recent messages in display order (oldest first).
 
        Args:
            limit: Maximum number of messages to return. If None or larger
                   than the current count, all stored messages are returned.
 
        Returns:
            List of message values, oldest to newest.
 
        Time complexity: O(k) where k is the number of messages returned.
        """
        if self._count == 0:
            return []
 
        k = self._count if limit is None else min(limit, self._count)
 
        # Start from the oldest message that fits in the window
        start_offset = self._count - k
        results = []
        for i in range(k):
            index = (self._head + start_offset + i) % self.capacity
            results.append(self._data.get(index))
        return results
 
    # Alias to match skeleton name
    def recent(self, limit: int | None = None) -> list:
        """Alias for get_recent -- matches skeleton interface."""
        return self.get_recent(limit)
 
    def is_full(self) -> bool:
        """Return True if the buffer is at capacity.
 
        Time complexity: O(1)
        """
        return self._count == self.capacity
 
    def clear(self) -> None:
        """Reset the buffer to empty without reallocating storage.
 
        Time complexity: O(1)
        """
        self._head = 0
        self._tail = 0
        self._count = 0
 
    def __len__(self) -> int:
        """Return number of messages currently stored. Time complexity: O(1)."""
        return self._count
 
    def __repr__(self) -> str:
        return (
            f"CircularBuffer(count={self._count}, capacity={self.capacity}, "
            f"full={self.is_full()})"
        )
 # end of file 
>>>>>>> Stashed changes
