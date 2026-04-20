from __future__ import annotations

"""Search algorithm comparison skeleton.

Use this file for brute-force baselines and prefix-search comparisons. The final
optimized structures should live in datastructures/.
"""


def brute_force_prefix(records: list[object], prefix: str, key_func) -> list[object]:
    # TODO(BASELINE): Implement simple O(n) scan for benchmark comparison only.
    _ = (records, prefix, key_func)
    raise NotImplementedError("Team must implement brute-force baseline.")


def prefix_search(index: object, prefix: str, limit: int = 10) -> list[object]:
    # TODO(TRIE/BST): Call the final prefix index and record timing.
    _ = (index, prefix, limit)
    raise NotImplementedError("Team must implement optimized prefix search.")
