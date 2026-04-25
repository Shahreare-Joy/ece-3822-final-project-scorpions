from __future__ import annotations

"""Search algorithm comparisons.

Use this file for brute-force baselines and prefix-search comparisons. The final
optimized structures should live in datastructures/.
"""

from time import perf_counter
from typing import Callable, TypeVar


T = TypeVar("T")


def brute_force_prefix(records: list[T], prefix: str, key_func: Callable[[T], str]) -> list[T]:
    '''run simple prefix search using full list scan'''
    # TODO (DONE)(BASELINE): Implement simple O(n) scan for benchmark comparison only.

    # normalize prefix for case-insensitive comparison
    normalized = prefix.strip().lower()

    # return empty list when search prefix is empty
    if not normalized:
        return []

    # scan every record and keep items that start with prefix
    return [record for record in records if key_func(record).lower().startswith(normalized)]


def case_insensitive_contains(records: list[T], query: str, key_func: Callable[[T], str]) -> list[T]:
    """O(n) case-insensitive contains search for benchmarks."""

    # normalize query for case-insensitive comparison
    normalized = query.strip().lower()

    # return empty list when query is empty
    if not normalized:
        return []

    # scan every record and keep items that contain query
    return [record for record in records if normalized in key_func(record).lower()]


def prefix_search(index: object, prefix: str, limit: int = 10) -> list[object]:
    '''call available prefix-search method from index'''
    # TODO (DONE)(TRIE/BST): Call the final prefix index and record timing.

    # reject invalid limits
    if limit <= 0:
        return []

    # prefer prefix_query if the index supports it
    if hasattr(index, "prefix_query"):
        return list(index.prefix_query(prefix, limit))[:limit]

    # otherwise try search_prefix
    if hasattr(index, "search_prefix"):
        return list(index.search_prefix(prefix, limit))[:limit]

    # otherwise try generic search method
    if hasattr(index, "search"):
        try:
            return list(index.search(prefix, limit))[:limit]
        except TypeError:
            return list(index.search(prefix))[:limit]

    # fail clearly if index has no supported search method
    raise TypeError("index must provide prefix_query, search_prefix, or search")


class FallbackPrefixIndex:
    """Small adapter used when the optimized prefix index is not ready yet.

    This keeps services and benchmarks using the same prefix_search() call while
    still making the O(n) brute-force behavior explicit.
    """

    def __init__(self, records: list[T], key_func: Callable[[T], str]) -> None:
        # store records and key function for brute-force fallback search
        self._records = records
        self._key_func = key_func

    def search_prefix(self, prefix: str, limit: int = 10) -> list[T]:
        '''search prefix using brute-force scan, then apply limit'''

        # use baseline prefix scan and trim to requested result count
        return brute_force_prefix(self._records, prefix, self._key_func)[:limit]


def make_fallback_index(records: list[T], key_func: Callable[[T], str]) -> FallbackPrefixIndex[T]:
    '''create fallback prefix index adapter'''

    # return adapter around records and key function
    return FallbackPrefixIndex(records, key_func)


def timed_brute_force(records: list[T], prefix: str, key_func: Callable[[T], str]) -> tuple[list[T], float]:
    '''measure brute-force prefix search runtime'''

    # start timer before search
    started = perf_counter()

    # run baseline search
    results = brute_force_prefix(records, prefix, key_func)

    # return results and elapsed time
    return results, perf_counter() - started


def timed_prefix_search(index: object, prefix: str, limit: int = 10) -> tuple[list[object], float]:
    '''measure indexed prefix search runtime'''

    # start timer before search
    started = perf_counter()

    # run prefix search through supported index API
    results = prefix_search(index, prefix, limit)

    # return results and elapsed time
    return results, perf_counter() - started