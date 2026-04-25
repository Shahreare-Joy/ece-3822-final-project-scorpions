"""Sorting and search algorithms for the final platform.

TODO (DONE)(ALGORITHMS): Implement and benchmark at least two sorting algorithms
and search comparisons required by the project.
"""

from .heapsort import heap_sort, heapsort, top_n
from .mergesort import merge_sort, mergesort
from .search_algorithms import (
    FallbackPrefixIndex,
    brute_force_prefix,
    case_insensitive_contains,
    make_fallback_index,
    prefix_search,
    timed_brute_force,
    timed_prefix_search,
)

__all__ = [
    "FallbackPrefixIndex",
    "brute_force_prefix",
    "case_insensitive_contains",
    "heap_sort",
    "heapsort",
    "make_fallback_index",
    "merge_sort",
    "mergesort",
    "prefix_search",
    "timed_brute_force",
    "timed_prefix_search",
    "top_n",
]
