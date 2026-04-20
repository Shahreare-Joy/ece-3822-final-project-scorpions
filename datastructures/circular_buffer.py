from __future__ import annotations

"""Circular buffer skeleton for chat.

Use cases:
- keep only the most recent N chat messages per session
- prevent unlimited client/server memory growth

Expected complexity:
- append: O(1)
- recent traversal: O(k), where k is number of returned messages

TODO(CIRCULAR BUFFER): Implement with fixed-size custom array storage.
"""


class CircularBuffer:
    def __init__(self, capacity: int = 100) -> None:
        if capacity <= 0:
            raise ValueError("capacity must be positive")
        self.capacity = capacity
        # TODO: allocate fixed storage and track start/count.
        raise NotImplementedError("Team must implement circular buffer.")

    def append(self, value: object) -> None:
        _ = value
        raise NotImplementedError

    def recent(self, limit: int | None = None) -> list[object]:
        _ = limit
        raise NotImplementedError
