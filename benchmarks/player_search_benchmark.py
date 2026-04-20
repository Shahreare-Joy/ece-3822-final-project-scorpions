from __future__ import annotations

"""Player search stress-test scaffold.

Goal:
- test 10,000+ and 100,000+ player records directly through search structures
- compare optimized structure vs brute-force prefix search

Plot idea:
- x-axis = number of players
- y-axis = average response time / memory usage

TODO(TEAM): Implement after datastructures/search indexes are complete.
"""

from dataclasses import dataclass, asdict


@dataclass
class PlayerSearchBenchmarkCase:
    """Describes one planned benchmark workload."""

    dataset_size: int
    query_count: int
    query_type: str
    structure_name: str


def planned_player_search_cases() -> list[PlayerSearchBenchmarkCase]:
    """Return starter workloads without running final logic.

    TODO(BENCHMARK): Add 10,000, 50,000, and 100,000+ player datasets. Run
    brute force and the final structure with the same queries.
    """

    return [
        PlayerSearchBenchmarkCase(10_000, 100, "prefix", "brute_force_baseline"),
        PlayerSearchBenchmarkCase(10_000, 100, "prefix", "future_trie_or_bst"),
        PlayerSearchBenchmarkCase(100_000, 1_000, "exact", "future_hash_table"),
    ]


def run_player_search_benchmark() -> list[dict[str, object]]:
    # TODO(BENCHMARK): Generate/load player records, time brute force vs final
    # Trie/BST/Hash Table search, then return rows for plotting.
    # Output row idea:
    # {"dataset_size": 100000, "query_count": 1000, "structure": "Trie",
    #  "avg_ms": 0.0, "memory_mb": 0.0}
    return []


if __name__ == "__main__":
    print("TODO: implement player search benchmark.")
    for case in planned_player_search_cases():
        print(asdict(case))
