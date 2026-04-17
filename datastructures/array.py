from __future__ import annotations

"""Low-level array skeleton.

TODO(ARRAY): Implement fixed-capacity storage without using Python's built-in
list as the core data structure. One option is ctypes.py_object arrays. Keep
this small and well-tested because other custom structures may depend on it.
"""


class Array:
    def __init__(self, capacity: int) -> None:
        if capacity <= 0:
            raise ValueError("capacity must be positive")
        self.capacity = capacity
        # TODO(ARRAY): Allocate low-level storage here.
        raise NotImplementedError("Team must implement low-level Array storage.")

    def get(self, index: int) -> object:
        # TODO(ARRAY): Bounds-check and return item.
        _ = index
        raise NotImplementedError

    def set(self, index: int, value: object) -> None:
        # TODO(ARRAY): Bounds-check and store item.
        _ = (index, value)
        raise NotImplementedError
