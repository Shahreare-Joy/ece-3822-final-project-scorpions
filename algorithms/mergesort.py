from __future__ import annotations
"""Merge sort skeleton.
Expected complexity:
- time: O(n log n)
- extra space: O(n)
Use cases:
- catalog sorting
- match history sorting
- leaderboard/report comparisons
"""


def mergesort(records: list[object], key=None, reverse: bool = False) -> list[object]:
    """
    Sort a list of records using merge sort.

    Stability: STABLE — when two records have equal keys, their original
    relative order is preserved. This matters when sorting match history
    by timestamp or leaderboard records with tied scores.

    Args:
        records: List of items to sort. Can be plain values, dicts, or
                 any objects as long as `key` produces comparable values.
        key:     Optional callable that extracts a comparison value from
                 each record, e.g. lambda r: r["score"].
                 If None, records are compared directly.
        reverse: If True, sort in descending order (highest first).

    Returns:
        A new sorted list. The original list is not modified.

    Time:  O(n log n)
    Space: O(n)
    """
    # Base case: a list of 0 or 1 elements is already sorted
    if len(records) <= 1:
        return list(records)

    mid = len(records) // 2
    left  = mergesort(records[:mid],  key=key, reverse=reverse)
    right = mergesort(records[mid:], key=key, reverse=reverse)

    return _merge(left, right, key=key, reverse=reverse)


def _merge(
    left: list[object],
    right: list[object],
    key=None,
    reverse: bool = False,
) -> list[object]:
    """
    Merge two already-sorted sublists into one sorted list.

    Stability is preserved: when both sides share an equal key value,
    the left element is always taken first, keeping original ordering.
    """
    result: list[object] = []
    i = j = 0

    while i < len(left) and j < len(right):
        left_val  = key(left[i])  if key else left[i]
        right_val = key(right[j]) if key else right[j]

        # Take left on equality to preserve stability
        if reverse:
            take_left = left_val >= right_val
        else:
            take_left = left_val <= right_val

        if take_left:
            result.append(left[i]);  i += 1
        else:
            result.append(right[j]); j += 1

    # Append whichever side still has elements
    result.extend(left[i:])
    result.extend(right[j:])
    return result


# ---------------------------------------------------------------------------
# Quick self-test — run with:  python algorithms/mergesort.py
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    # 1 — plain numbers
    nums = [5, 2, 8, 1, 9, 3]
    assert mergesort(nums) == [1, 2, 3, 5, 8, 9]
    assert mergesort(nums, reverse=True) == [9, 8, 5, 3, 2, 1]
    print("PASS  plain numbers")

    # 2 — dicts sorted by key
    players = [
        {"username": "alice", "total_score": 4200},
        {"username": "bob",   "total_score": 8800},
        {"username": "carol", "total_score": 1500},
    ]
    asc  = mergesort(players, key=lambda p: p["total_score"])
    desc = mergesort(players, key=lambda p: p["total_score"], reverse=True)
    assert [p["username"] for p in asc]  == ["carol", "alice", "bob"]
    assert [p["username"] for p in desc] == ["bob",   "alice", "carol"]
    print("PASS  dict sort by score (asc + desc)")

    # 3 — stability: equal keys must preserve original order
    tied = [{"name": "X", "score": 100},
            {"name": "Y", "score": 100},
            {"name": "Z", "score": 100}]
    assert [r["name"] for r in mergesort(tied, key=lambda r: r["score"])] == ["X", "Y", "Z"]
    print("PASS  stability with tied keys")

    # 4 — edge cases
    assert mergesort([]) == []
    assert mergesort([42]) == [42]
    print("PASS  edge cases (empty, single element)")

    # 5 — session history sorted by ISO 8601 timestamp
    sessions = [
        {"session_id": "s3", "started_at": "2024-03-15T10:00:00"},
        {"session_id": "s1", "started_at": "2024-01-01T08:00:00"},
        {"session_id": "s2", "started_at": "2024-02-20T14:30:00"},
    ]
    sorted_s = mergesort(sessions, key=lambda s: s["started_at"])
    assert [s["session_id"] for s in sorted_s] == ["s1", "s2", "s3"]
    print("PASS  session sort by timestamp")

    print("\nAll mergesort tests passed.")
