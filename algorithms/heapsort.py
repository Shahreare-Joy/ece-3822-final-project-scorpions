from __future__ import annotations

"""Heap sort / heap-based ranking.

Expected complexity:
- heap build: O(n) with bottom-up heapify
- sort/top extraction: O(n log n) for full sort
- top N extraction: O(n + k log n)

Use cases:
- leaderboard ranking
- popular games ranking
"""

from typing import Callable, TypeVar


T = TypeVar("T")


def heapsort(records: list[T], key: Callable[[T], object] | None = None, reverse: bool = False) -> list[T]:
    '''sort records using manual heap sort'''
    # TODO (DONE)(HEAPSORT): Implement heap sort manually, not with Python heapq.

    # choose key function or use the item itself
    key_func = key or (lambda item: item)

    # copy input so original list is not changed
    items = list(records)

    # build heap before extracting items
    _build_heap(items, key_func, reverse)

    # Move the highest-priority item to the end one slot at a time. With a
    # max-heap this produces ascending order; with a min-heap it produces
    # descending order for reverse=True.
    for end in range(len(items) - 1, 0, -1):
        # swap root with last item in active heap
        items[0], items[end] = items[end], items[0]

        # restore heap order after removing root
        _sift_down(items, 0, end, key_func, reverse)

    return items


def top_n(records: list[T], n: int, key: Callable[[T], object] | None = None) -> list[T]:
    """Return the top n records by key without sorting the full result list."""

    # reject invalid limits
    if n <= 0:
        return []

    # choose key function or use the item itself
    key_func = key or (lambda item: item)

    # copy records before heap operations
    items = list(records)

    # build max-heap so largest values come out first
    _build_heap(items, key_func, reverse=False)

    results: list[T] = []
    heap_size = len(items)

    # repeatedly extract highest-priority item until n results are collected
    while heap_size > 0 and len(results) < n:
        results.append(items[0])

        # move last heap item to root and shrink heap
        items[0] = items[heap_size - 1]
        heap_size -= 1

        # restore heap after extraction
        _sift_down(items, 0, heap_size, key_func, reverse=False)

    return results


def heap_sort(records: list[T], key: Callable[[T], object] | None = None, reverse: bool = False) -> list[T]:
    """Alias matching the team task document."""

    # call main heapsort implementation
    return heapsort(records, key=key, reverse=reverse)


def _build_heap(items: list[T], key_func: Callable[[T], object], reverse: bool) -> None:
    '''build heap using bottom-up heapify'''

    # start at last parent node and sift down toward root
    for index in range((len(items) // 2) - 1, -1, -1):
        _sift_down(items, index, len(items), key_func, reverse)


def _sift_down(items: list[T], start: int, heap_size: int, key_func: Callable[[T], object], reverse: bool) -> None:
    '''move one item down until heap property is restored'''

    root = start
    while True:
        # calculate child indexes
        left = 2 * root + 1
        right = left + 1
        selected = root

        # compare left child with current selected node
        if left < heap_size and _has_higher_priority(items[left], items[selected], key_func, reverse):
            selected = left

        # compare right child with current selected node
        if right < heap_size and _has_higher_priority(items[right], items[selected], key_func, reverse):
            selected = right

        # stop when root is already in correct position
        if selected == root:
            return

        # swap root with higher-priority child
        items[root], items[selected] = items[selected], items[root]
        root = selected


def _has_higher_priority(left: T, right: T, key_func: Callable[[T], object], reverse: bool) -> bool:
    '''compare two items based on heap direction'''

    # reverse=True uses min-heap behavior
    if reverse:
        return key_func(left) < key_func(right)

    # default uses max-heap behavior
    return key_func(left) > key_func(right)