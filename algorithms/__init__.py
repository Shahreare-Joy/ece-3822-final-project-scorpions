"""Sorting and search algorithms for the final platform.

Implemented modules
-------------------
mergesort.py
    Stable O(n log n) sort using recursive divide-and-conquer.
    Used for: match history by timestamp, catalog sorting, leaderboard snapshots.
    Key function: mergesort(records, key=None, reverse=False)

heapsort.py
    In-place O(n log n) sort using a custom max/min heap (no heapq).
    Used for: leaderboard ranking, popular games ranking, top-N extraction.
    Key functions: heapsort(records, key=None, reverse=False)
                   top_n(records, n, key=None)

search_algorithms.py
    Brute-force O(n) prefix search baseline and optimised index adapter.
    Used for: player autocomplete, game title search, benchmark comparisons.
    Key functions: brute_force_prefix(records, prefix, key_func)
       prefix_search(index, prefix, limit=10)timed_brute_force(...)  / timed_prefix_search(...)
"""
