from __future__ import annotations

"""Low-level fixed-capacity array.

TODO (DONE)(ARRAY): Implement fixed-capacity storage without using Python's
built-in list as the core data structure. This implementation uses
``ctypes.py_object`` storage so the higher-level structures have a small,
assignment-friendly building block.
"""

import ctypes


class Array:
    """Tiny bounds-checked array wrapper used by custom structures."""

    def __init__(self, capacity: int) -> None:
        # validate array capacity before allocating storage
        if capacity <= 0:
            raise ValueError("capacity must be positive")

        # store current capacity and logical size
        self.capacity = capacity
        self._size = 0

        # TODO (DONE)(ARRAY): Allocate low-level storage here.

        # allocate fixed-size ctypes storage
        self._storage = (ctypes.py_object * capacity)()

        # initialize all slots to None
        for index in range(capacity):
            self._storage[index] = None

    def __len__(self) -> int:
        '''return logical number of stored items'''
        return self._size

    def _check_bounds(self, index: int) -> None:
        '''raise error if index is outside array capacity'''

        # reject negative indexes and indexes beyond capacity
        if index < 0 or index >= self.capacity:
            raise IndexError(f"array index {index} out of range")

    def get(self, index: int) -> object:
        '''return item at index after bounds check'''
        # TODO (DONE)(ARRAY): Bounds-check and return item.

        # validate index before reading
        self._check_bounds(index)

        # return stored value
        return self._storage[index]

    def set(self, index: int, value: object) -> None:
        '''store item at index after bounds check'''
        # TODO (DONE)(ARRAY): Bounds-check and store item.

        # validate index before writing
        self._check_bounds(index)

        # assign value into low-level storage
        self._storage[index] = value

        # update logical size if setting past current end
        if index >= self._size:
            self._size = index + 1

    def append(self, value: object) -> None:
        """Append a value, growing capacity when needed.

        Complexity: O(1) amortized, O(n) when resizing.
        """

        # grow storage when array is full
        if self._size >= self.capacity:
            self.resize(self.capacity * 2)

        # store value at next available position
        self.set(self._size, value)

    def resize(self, new_capacity: int) -> None:
        """Resize storage while preserving existing values."""

        # new capacity cannot lose existing logical items
        if new_capacity < self._size:
            raise ValueError("new capacity cannot be smaller than current size")

        # allocate new low-level storage
        new_storage = (ctypes.py_object * new_capacity)()

        # initialize all slots to None
        for index in range(new_capacity):
            new_storage[index] = None

        # copy current logical values into new storage
        for index in range(self._size):
            new_storage[index] = self._storage[index]

        # replace old storage with resized storage
        self.capacity = new_capacity
        self._storage = new_storage

    def to_list(self) -> list[object]:
        """Return logical contents for tests/debugging only."""

        # convert only logical portion, not unused capacity
        return [self._storage[index] for index in range(self._size)]