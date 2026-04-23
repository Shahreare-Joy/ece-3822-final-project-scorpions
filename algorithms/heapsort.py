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


# ---------------------------------------------------------------------------
# Internal heap helpers (manual implementation — no heapq used)
# NOTE: This is a MAX-heap by default. heapsort() flips comparisons as needed
# to produce ascending or descending output.
# ---------------------------------------------------------------------------

def _get_val(record: object, key) -> object:
    """Extract comparison value from a record."""
    return key(record) if key else record


def _sift_down(
    arr: list[object],
    root: int,
    end: int,
    key=None,
    reverse: bool = False,
) -> None:
    """
    Sift the element at `root` down to restore heap property
    over the subarray arr[0:end].

    For ascending sort  (reverse=False) we build a MAX-heap:
        parent >= children  →  largest ends up at root each time.
    For descending sort (reverse=True)  we build a MIN-heap:
        parent <= children  →  smallest ends up at root each time.

    Time: O(log n) per call.
    """
    while True:
        largest = root          # index of the dominant element so far
        left    = 2 * root + 1
        right   = 2 * root + 2

        if left < end:
            lv = _get_val(arr[left],    key)
            rv = _get_val(arr[largest], key)
            # For MAX-heap: promote left if left > current largest
            # For MIN-heap: promote left if left < current largest
            if (not reverse and lv > rv) or (reverse and lv < rv):
                largest = left

        if right < end:
            lv = _get_val(arr[right],   key)
            rv = _get_val(arr[largest], key)
            if (not reverse and lv > rv) or (reverse and lv < rv):
                largest = right

        if largest == root:
            break   # heap property satisfied

        arr[root], arr[largest] = arr[largest], arr[root]
        root = largest


def _build_heap(arr: list[object], key=None, reverse: bool = False) -> None:
    """
    Convert arr into a heap in-place using Floyd's algorithm.
    Time: O(n)  —  better than inserting one-by-one which is O(n log n).
    """
    n = len(arr)
    # Start from the last non-leaf node and sift each one down
    for i in range(n // 2 - 1, -1, -1):
        _sift_down(arr, i, n, key=key, reverse=reverse)


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def heapsort(records: list[object], key=None, reverse: bool = False) -> list[object]:
    """
    Sort a list of records using an in-place heap sort.

    NOTE: Uses the team's own heap logic (_build_heap / _sift_down).
          Python's heapq is NOT used anywhere in this file.

    Args:
        records: List of items to sort. Can be plain values, dicts, or
                 any objects as long as `key` produces comparable values.
        key:     Optional callable that extracts a comparison value,
                 e.g. lambda r: r["total_score"].
                 If None, records are compared directly.
        reverse: If True, sort descending (highest score first).

    Returns:
        A new sorted list. The original list is not modified.

    Time:  O(n log n)  — O(n) build + O(n log n) extraction
    Space: O(n)        — copy is made so original is preserved
    """
    # Work on a copy so we never mutate the caller's list
    arr = list(records)
    n   = len(arr)

    if n <= 1:
        return arr

    # Phase 1 — Build heap: O(n)
    # reverse=False → MAX-heap (ascending output after extraction)
    # reverse=True  → MIN-heap (descending output after extraction)
    _build_heap(arr, key=key, reverse=reverse)

    # Phase 2 — Extract: O(n log n)
    # Repeatedly swap root (max/min) to the end of the unsorted region,
    # then restore heap property over the shrinking prefix.
    for end in range(n - 1, 0, -1):
        arr[0], arr[end] = arr[end], arr[0]
        _sift_down(arr, 0, end, key=key, reverse=reverse)

    return arr


def top_n(records: list[object], n: int, key=None) -> list[object]:
    """
    Return the top-N records by key, highest first.

    More efficient than a full sort when n << len(records):
    build once O(n_records), extract n times O(n log n_records).

    Args:
        records: Full list of records (e.g. all players).
        n:       How many top records to return.
        key:     Callable to extract the ranking value.

    Returns:
        List of up to n records, sorted highest-first.

    Time:  O(n_records + n log n_records)
    Space: O(n_records)  — working copy

    Use case:
        top_players = top_n(all_players, 10, key=lambda p: p["total_score"])
    """
    if n <= 0:
        return []

    # Build a MAX-heap (reverse=False) then extract n times
    arr = list(records)
    _build_heap(arr, key=key, reverse=False)

    result = []
    end = len(arr)
    for _ in range(min(n, end)):
        # Root is always the current maximum
        result.append(arr[0])
        end -= 1
        arr[0], arr[end] = arr[end], arr[0]
        _sift_down(arr, 0, end, key=key, reverse=False)

    return result


# ---------------------------------------------------------------------------
# Quick self-test — run with:  python algorithms/heapsort.py
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    # 1 — plain numbers ascending
    nums = [5, 2, 8, 1, 9, 3]
    assert heapsort(nums) == [1, 2, 3, 5, 8, 9], "Ascending failed"
    assert heapsort(nums, reverse=True) == [9, 8, 5, 3, 2, 1], "Descending failed"
    print("PASS  plain numbers (asc + desc)")

    # 2 — leaderboard-style dicts sorted by score
    players = [
        {"username": "alice", "total_score": 4200},
        {"username": "bob",   "total_score": 8800},
        {"username": "carol", "total_score": 1500},
        {"username": "dan",   "total_score": 6100},
    ]
    asc  = heapsort(players, key=lambda p: p["total_score"])
    desc = heapsort(players, key=lambda p: p["total_score"], reverse=True)
    assert [p["username"] for p in asc]  == ["carol", "alice", "dan", "bob"]
    assert [p["username"] for p in desc] == ["bob", "dan", "alice", "carol"]
    print("PASS  leaderboard dict sort (asc + desc)")

    # 3 — highest-score-first (most common leaderboard use-case)
    leaderboard = heapsort(players, key=lambda p: p["total_score"], reverse=True)
    assert leaderboard[0]["username"] == "bob", "Top player should be bob"
    print("PASS  highest-score-first ordering")

    # 4 — top_n extraction
    top3 = top_n(players, 3, key=lambda p: p["total_score"])
    assert len(top3) == 3
    assert top3[0]["username"] == "bob",   "top_n[0] should be bob"
    assert top3[1]["username"] == "dan",   "top_n[1] should be dan"
    assert top3[2]["username"] == "alice", "top_n[2] should be alice"
    print("PASS  top_n(3) extracts correct top players")

    # 5 — original list is not mutated
    original = [3, 1, 4, 1, 5]
    _ = heapsort(original)
    assert original == [3, 1, 4, 1, 5], "Original list was mutated"
    print("PASS  original list not mutated")

    # 6 — edge cases
    assert heapsort([]) == []
    assert heapsort([42]) == [42]
    assert top_n([], 5, key=lambda x: x) == []
    print("PASS  edge cases (empty, single, top_n on empty)")

    # 7 — implementation check: heapq must not be imported
    import ast, pathlib
    src = pathlib.Path(__file__).read_text()
    tree = ast.parse(src)
    imports = [
        node.names[0].name
        for node in ast.walk(tree)
        if isinstance(node, ast.Import)
    ]
    assert "heapq" not in imports, "heapq must not be used — implement manually"
    print("PASS  heapq not imported (custom heap confirmed)")

    print("\nAll heapsort tests passed.")
