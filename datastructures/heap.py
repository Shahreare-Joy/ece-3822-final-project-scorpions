from __future__ import annotations

"""Custom max-heap / priority queue skeleton.

Use cases:
- top-N leaderboard scores
- popular games by active players
- priority matchmaking queues

Expected complexity:
- push: O(log n)
- pop: O(log n)
- peek: O(1)

TODO(HEAP): Implement with custom array storage, not Python heapq as the final
assignment solution.
"""


class MaxHeap:
    def __init__(self) -> None:
        # TODO: store heap nodes in custom Array/dynamic array.
        raise NotImplementedError("Team must implement custom heap.")

    def push(self, priority: int, value: object) -> None:
        _ = (priority, value)
        raise NotImplementedError

    def pop_max(self) -> object:
        raise NotImplementedError

    def peek_max(self) -> object:
        raise NotImplementedError
