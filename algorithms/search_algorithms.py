from __future__ import annotations
"""Search algorithm comparison skeleton.
Use this file for brute-force baselines and prefix-search comparisons. The final
optimized structures should live in datastructures/.
"""
import time


# ---------------------------------------------------------------------------
# Public API — matches skeleton signatures exactly
# ---------------------------------------------------------------------------

def brute_force_prefix(records: list[object], prefix: str, key_func) -> list[object]:
    """
    Scan every record and return those whose key starts with `prefix`.

    This is the O(n) baseline used in benchmarks to compare against
    the optimised prefix index (BST / trie) that Mykai implements.

    Args:
        records:  Full list of player or game records.
        prefix:   The search string, e.g. "ali" to match "alice", "alien42".
        key_func: Callable that extracts the searchable string from a record,
                  e.g. lambda p: p["username"]

    Returns:
        All records whose extracted key starts with `prefix`
        (case-insensitive). Original order is preserved.

    Time:  O(n) — every record is visited exactly once.
    Space: O(k) — k is the number of matching records returned.

    Example:
        matches = brute_force_prefix(players, "ali", lambda p: p["username"])
    """
    if not prefix:
        return list(records)

    needle = prefix.lower()
    return [r for r in records if key_func(r).lower().startswith(needle)]


def prefix_search(index: object, prefix: str, limit: int = 10) -> list[object]:
    """
    Query an optimised prefix index (BST or trie) built by Mykai.

    This function is a thin adapter: it calls the index's own lookup
    method and enforces the result limit so callers don't need to know
    the index's internal API.

    Args:
        index:  A prefix-index object that exposes a `.search(prefix)`
                method returning a list of matching records.
                Expected to be a BST or trie from datastructures/.
        prefix: The search string, e.g. "ali".
        limit:  Maximum number of results to return (default 10,
                suitable for autocomplete dropdowns).

    Returns:
        Up to `limit` matching records from the index.

    Time:  Depends on the index structure:
           - Trie:          O(p + k)  where p = len(prefix), k = matches
           - BST (sorted):  O(log n + k)
           Both are faster than the O(n) brute-force baseline for large n.
    Space: O(k)

    NOTE: If Mykai's structure is not yet ready, pass a _FallbackIndex
          built with make_fallback_index() so the rest of the system
          can still run end-to-end.

    TODO(TRIE/BST): Replace _FallbackIndex with the real structure once
                    datastructures/bst.py or a trie is finalised.
    """
    results = index.search(prefix)
    return results[:limit]


# ---------------------------------------------------------------------------
# Fallback index — lets the platform run before Mykai's structure is ready
# ---------------------------------------------------------------------------

class _FallbackIndex:
    """
    A dead-simple brute-force index that satisfies the same .search()
    contract as the real BST/trie.

    Drop this in anywhere prefix_search() is called so the system works
    end-to-end while datastructures/ is still being built.

    Usage:
        idx = make_fallback_index(players, lambda p: p["username"])
        results = prefix_search(idx, "ali", limit=5)
    """

    def __init__(self, records: list[object], key_func) -> None:
        self._records  = records
        self._key_func = key_func

    def search(self, prefix: str) -> list[object]:
        """Return all records whose key starts with prefix (case-insensitive)."""
        return brute_force_prefix(self._records, prefix, self._key_func)


def make_fallback_index(records: list[object], key_func) -> _FallbackIndex:
    """
    Build a fallback brute-force index.

    Swap this out for the real BST/trie once datastructures/ is ready —
    the rest of the code that calls prefix_search() won't need to change.

    Args:
        records:  Full list of records to index.
        key_func: Callable extracting the searchable string from each record.

    Returns:
        A _FallbackIndex that supports .search(prefix).
    """
    return _FallbackIndex(records, key_func)


# ---------------------------------------------------------------------------
# Timing helpers — Kevin can import these directly for benchmarks
# ---------------------------------------------------------------------------

def timed_brute_force(
    records: list[object],
    prefix: str,
    key_func,
) -> tuple[list[object], float]:
    """
    Run brute_force_prefix and return (results, elapsed_seconds).

    Kevin's benchmarks can call this directly without any extra timing code.

    Example:
        results, elapsed = timed_brute_force(players, "ali", lambda p: p["username"])
        print(f"Brute force: {len(results)} matches in {elapsed:.6f}s")
    """
    start   = time.perf_counter()
    results = brute_force_prefix(records, prefix, key_func)
    elapsed = time.perf_counter() - start
    return results, elapsed


def timed_prefix_search(
    index: object,
    prefix: str,
    limit: int = 10,
) -> tuple[list[object], float]:
    """
    Run prefix_search and return (results, elapsed_seconds).

    Example:
        results, elapsed = timed_prefix_search(idx, "ali", limit=10)
        print(f"Index search: {len(results)} matches in {elapsed:.6f}s")
    """
    start   = time.perf_counter()
    results = prefix_search(index, prefix, limit)
    elapsed = time.perf_counter() - start
    return results, elapsed


# ---------------------------------------------------------------------------
# Quick self-test — run with:  python algorithms/search_algorithms.py
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    # Sample dataset — mimics real player records at small scale
    players = [
        {"username": "alice",    "display_name": "Alice A"},
        {"username": "alien42",  "display_name": "Alien42"},
        {"username": "bob",      "display_name": "Bob B"},
        {"username": "bobby",    "display_name": "Bobby B"},
        {"username": "carol",    "display_name": "Carol C"},
        {"username": "carlos",   "display_name": "Carlos C"},
        {"username": "dan",      "display_name": "Dan D"},
        {"username": "ALICE_X",  "display_name": "Alice X"},   # uppercase — tests case-insensitivity
    ]
    key = lambda p: p["username"]

    # 1 — brute force basic match
    results = brute_force_prefix(players, "ali", key)
    names = [r["username"] for r in results]
    assert "alice"   in names, "alice should match 'ali'"
    assert "alien42" in names, "alien42 should match 'ali'"
    assert "bob"     not in names, "bob should not match 'ali'"
    print("PASS  brute_force_prefix basic match")

    # 2 — case-insensitive match
    results = brute_force_prefix(players, "ALI", key)
    names = [r["username"] for r in results]
    assert "alice"   in names, "alice should match 'ALI' (case-insensitive)"
    assert "ALICE_X" in names, "ALICE_X should match 'ALI'"
    print("PASS  brute_force_prefix case-insensitive")

    # 3 — empty prefix returns everything
    results = brute_force_prefix(players, "", key)
    assert len(results) == len(players), "Empty prefix should return all records"
    print("PASS  brute_force_prefix empty prefix returns all")

    # 4 — no matches
    results = brute_force_prefix(players, "zzz", key)
    assert results == [], "Non-matching prefix should return empty list"
    print("PASS  brute_force_prefix no matches")

    # 5 — fallback index gives same results as brute force
    idx = make_fallback_index(players, key)
    index_results = prefix_search(idx, "car", limit=10)
    brute_results = brute_force_prefix(players, "car", key)
    assert index_results == brute_results, "Fallback index should match brute force"
    print("PASS  fallback index matches brute force")

    # 6 — limit is respected
    idx = make_fallback_index(players, key)
    limited = prefix_search(idx, "a", limit=1)
    assert len(limited) <= 1, "limit=1 should return at most 1 result"
    print("PASS  prefix_search respects limit")

    # 7 — timed helpers return correct types
    results, elapsed = timed_brute_force(players, "bob", key)
    assert isinstance(elapsed, float), "elapsed should be a float"
    assert len(results) == 2, "bob + bobby should match 'bob'"
    print(f"PASS  timed_brute_force ({elapsed:.6f}s for {len(players)} records)")

    idx = make_fallback_index(players, key)
    results, elapsed = timed_prefix_search(idx, "bob", limit=10)
    assert isinstance(elapsed, float)
    print(f"PASS  timed_prefix_search ({elapsed:.6f}s)")

    # 8 — large dataset smoke test (10,000 records — matches assignment scale)
    import random, string
    random.seed(42)
    def rand_name():
        return "".join(random.choices(string.ascii_lowercase, k=random.randint(4, 12)))
    large = [{"username": rand_name()} for _ in range(10_000)]
    large.append({"username": "searchme_001"})
    large.append({"username": "searchme_002"})

    results, elapsed = timed_brute_force(large, "searchme", lambda p: p["username"])
    assert len(results) == 2, f"Expected 2 matches, got {len(results)}"
    print(f"PASS  large dataset brute force (10 000 records, {elapsed:.4f}s)")

    print("\nAll search_algorithms tests passed.")
