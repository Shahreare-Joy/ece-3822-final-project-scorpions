from __future__ import annotations

"""Merge sort.

Expected complexity:
- time: O(n log n)
- extra space: O(n)

Use cases:
- catalog sorting
- match history sorting
- leaderboard/report comparisons
"""

from typing import Callable, TypeVar


T = TypeVar("T")


def mergesort(records: list[T], key: Callable[[T], object] | None = None, reverse: bool = False) -> list[T]:
    '''sort records using merge sort'''
    # TODO (DONE)(MERGESORT): Implement recursively or iteratively and benchmark.

    # choose key function or use the item itself
    key_func = key or (lambda item: item)

    # base case: already sorted if list has 0 or 1 item
    if len(records) <= 1:
        return list(records)

    # split list into left and right halves
    middle = len(records) // 2
    left = mergesort(records[:middle], key=key_func, reverse=reverse)
    right = mergesort(records[middle:], key=key_func, reverse=reverse)

    # merge sorted halves back together
    return _merge(left, right, key_func, reverse)


def _merge(left: list[T], right: list[T], key_func: Callable[[T], object], reverse: bool) -> list[T]:
    """Merge two already-sorted halves.

    The comparison handles reverse order directly instead of sorting ascending
    and reversing at the end. That keeps equal-key records stable in both
    directions, which is useful for leaderboards and match-history views.
    """

    # store merged sorted result
    result: list[T] = []
    left_index = 0
    right_index = 0

    # compare both halves until one side runs out
    while left_index < len(left) and right_index < len(right):
        left_value = key_func(left[left_index])
        right_value = key_func(right[right_index])

        # choose from left side first when equal to keep sort stable
        should_take_left = left_value >= right_value if reverse else left_value <= right_value

        if should_take_left:
            result.append(left[left_index])
            left_index += 1
        else:
            result.append(right[right_index])
            right_index += 1

    # add any remaining items from either half
    result.extend(left[left_index:])
    result.extend(right[right_index:])

    return result


def merge_sort(records: list[T], key: Callable[[T], object] | None = None, reverse: bool = False) -> list[T]:
    """Alias matching the team task document."""

    # call main mergesort implementation
    return mergesort(records, key=key, reverse=reverse)