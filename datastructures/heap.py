from __future__ import annotations
 
"""Custom max-heap / priority queue.
 
Use cases:
- platform_server/leaderboard.py -> top-N scores, win rates, play times
- popular games by active players
- priority matchmaking queues
 
Expected complexity:
- push:     O(log n)
- pop_max:  O(log n)
- peek_max: O(1)
- heapify:  O(n)
- top_n:    O(n + k log n) where k is the number of results requested
 
NOTE: Backed by a custom Array (datastructures/array.py), not Python heapq
or a Python list as the core storage structure.
"""
 
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))
from array import Array
 
 
# ---------------------------------------------------------------------------
# Internal node
# ---------------------------------------------------------------------------
 
class _HeapNode:
    """A single entry in the heap.
 
    Attributes:
        priority: Numeric value used for heap ordering (higher = higher rank).
        value:    Associated payload (player record, game record, etc.).
    """
 
    def __init__(self, priority: int | float, value: object) -> None:
        self.priority: int | float = priority
        self.value: object = value
 
    def __repr__(self) -> str:
        return f"_HeapNode(priority={self.priority}, value={self.value})"
 
 
# ---------------------------------------------------------------------------
# Max-Heap
# ---------------------------------------------------------------------------
 
class MaxHeap:
    """Array-backed max-heap where the highest priority is always at the root.
 
    The heap is stored as a flat Array using standard 0-indexed parent/child
    index arithmetic:
        parent(i)      = (i - 1) // 2
        left_child(i)  = 2 * i + 1
        right_child(i) = 2 * i + 2
 
    Attributes:
        _data (Array): Custom array holding _HeapNode entries.
        _size (int):   Number of elements currently in the heap.
    """
 
    def __init__(self) -> None:
        """Create an empty max-heap.
 
        Time complexity: O(1)
        """
        self._data: Array = Array(16)   # start small, append will grow it
        self._size: int = 0
 
    # ------------------------------------------------------------------
    # Public interface
    # ------------------------------------------------------------------
 
    def push(self, priority: int | float, value: object) -> None:
        """Insert a new entry with *priority* and *value*.
 
        Appends to the end of the array then sifts up to restore heap order.
 
        Args:
            priority: Numeric rank (higher number = higher priority).
            value:    Any Python object to store with this priority.
 
        Time complexity: O(log n)
        """
        node = _HeapNode(priority, value)
        self._data.append(node)
        self._size += 1
        self._sift_up(self._size - 1)
 
    def pop_max(self) -> object:
        """Remove and return the value with the highest priority.
 
        Swaps root with the last element, shrinks the array, then sifts
        the new root down to restore heap order.
 
        Returns:
            Value associated with the highest priority entry.
 
        Raises:
            IndexError: If the heap is empty.
 
        Time complexity: O(log n)
        """
        if self._size == 0:
            raise IndexError("pop from empty heap")
 
        # Swap root (max) with last element
        self._swap(0, self._size - 1)
        max_node = self._data.get(self._size - 1)
        self._size -= 1
        # Overwrite the now-unused last slot with None to free reference
        self._data.set(self._size, None) if self._size < self._data.capacity else None
 
        if self._size > 0:
            self._sift_down(0)
 
        return max_node.value
 
    def peek_max(self) -> object:
        """Return the value with the highest priority without removing it.
 
        Returns:
            Value at the root of the heap.
 
        Raises:
            IndexError: If the heap is empty.
 
        Time complexity: O(1)
        """
        if self._size == 0:
            raise IndexError("peek from empty heap")
        return self._data.get(0).value
 
    def peek_max_priority(self) -> int | float:
        """Return the highest priority score without removing it.
 
        Raises:
            IndexError: If the heap is empty.
 
        Time complexity: O(1)
        """
        if self._size == 0:
            raise IndexError("peek from empty heap")
        return self._data.get(0).priority
 
    def heapify(self, records: list) -> None:
        """Build the heap from a list of (priority, value) tuples.
 
        Uses the classic bottom-up heapify algorithm which is O(n),
        faster than pushing each record individually which would be O(n log n).
 
        Args:
            records: List of (priority, value) tuples.
 
        Time complexity: O(n)
        """
        # Reset
        self._data = Array(max(len(records), 16))
        self._size = 0
        for priority, value in records:
            self._data.append(_HeapNode(priority, value))
            self._size += 1
        # Sift down from last internal node up to root
        start = (self._size - 2) // 2
        for i in range(start, -1, -1):
            self._sift_down(i)
 
    def top_n(self, n: int) -> list:
        """Return the values of the top *n* highest-priority entries.
 
        Makes a temporary copy of the heap so the original is not modified.
        Pops n times from the copy.
 
        Args:
            n: Number of top entries to return.
 
        Returns:
            List of values in descending priority order (highest first).
 
        Time complexity: O(n + k log n) where k = min(n, size)
        """
        if n <= 0:
            return []
        # Build a copy so we don't destroy the live heap
        copy = MaxHeap()
        copy._size = self._size
        copy._data = Array(max(self._data.capacity, 16))
        for i in range(self._size):
            copy._data.append(self._data.get(i))
 
        results = []
        count = min(n, self._size)
        for _ in range(count):
            results.append(copy.pop_max())
        return results
 
    def __len__(self) -> int:
        """Return number of entries in the heap. Time complexity: O(1)."""
        return self._size
 
    def is_empty(self) -> bool:
        """Return True if the heap has no entries. Time complexity: O(1)."""
        return self._size == 0
 
    def __repr__(self) -> str:
        return f"MaxHeap(size={self._size})"
 
    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------
 
    def _sift_up(self, index: int) -> None:
        """Move node at *index* up until heap property is restored.
 
        A node sifts up by swapping with its parent while its priority
        is greater than the parent's priority.
 
        Time complexity: O(log n)
        """
        while index > 0:
            parent = (index - 1) // 2
            if self._data.get(index).priority > self._data.get(parent).priority:
                self._swap(index, parent)
                index = parent
            else:
                break
 
    def _sift_down(self, index: int) -> None:
        """Move node at *index* down until heap property is restored.
 
        A node sifts down by swapping with its largest child while that
        child has a higher priority.
 
        Time complexity: O(log n)
        """
        while True:
            largest = index
            left = 2 * index + 1
            right = 2 * index + 2
 
            if (left < self._size and
                    self._data.get(left).priority > self._data.get(largest).priority):
                largest = left
 
            if (right < self._size and
                    self._data.get(right).priority > self._data.get(largest).priority):
                largest = right
 
            if largest != index:
                self._swap(index, largest)
                index = largest
            else:
                break
 
    def _swap(self, i: int, j: int) -> None:
        """Swap nodes at positions *i* and *j* in the array.
 
        Time complexity: O(1)
        """
        a = self._data.get(i)
        b = self._data.get(j)
        self._data.set(i, b)
        self._data.set(j, a)

 # end of file
