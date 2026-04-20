from __future__ import annotations

"""Leaderboard query stress-test scaffold.

Goal:
- compare heap/BST/range-query leaderboard structures against brute-force sort
- test top-N, player rank, and score range query workloads

Plot idea:
- x-axis = number of scores or query count
- y-axis = response time / memory usage

TODO(TEAM): Implement after datastructures/heap.py and BST/range index exist.
"""

from dataclasses import dataclass, asdict


@dataclass
class LeaderboardBenchmarkCase:
    """Describes one planned leaderboard workload."""

    score_count: int
    query_count: int
    query_type: str
    structure_name: str


def planned_leaderboard_cases() -> list[LeaderboardBenchmarkCase]:
    """Return starter workloads for final benchmark planning."""

    return [
        LeaderboardBenchmarkCase(10_000, 100, "top_n", "brute_force_sort"),
        LeaderboardBenchmarkCase(10_000, 100, "top_n", "future_heap"),
        LeaderboardBenchmarkCase(100_000, 500, "score_range", "future_bst_range_index"),
        LeaderboardBenchmarkCase(100_000, 500, "player_rank", "future_rank_index"),
    ]


def run_leaderboard_benchmark() -> list[dict[str, object]]:
    # TODO(BENCHMARK): Time top-N, rank lookup, and score range queries.
    # Plot x-axis: score_count or query_count.
    # Plot y-axis: average response time and optional memory usage.
    return []


if __name__ == "__main__":
    print("TODO: implement leaderboard benchmark.")
    for case in planned_leaderboard_cases():
        print(asdict(case))
