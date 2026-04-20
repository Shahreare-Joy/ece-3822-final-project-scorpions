from __future__ import annotations

"""Heap sort / heap-based ranking skeleton.

Expected complexity:
- heap build: O(n)
- sort/top extraction: O(n log n) for full sort
- top-N with heap: often O(n log k) depending on design

Use cases:
- leaderboard ranking
- popular games ranking
"""


def heapsort(records: list[object], key=None, reverse: bool = False) -> list[object]:
    # TODO(HEAPSORT): Use the team's custom heap, not Python heapq.
    _ = (records, key, reverse)
    raise NotImplementedError("Team must implement heapsort.")
