from __future__ import annotations

"""Match history query stress-test scaffold.

Goal:
- test 100,000+ session records directly through history indexes
- compare indexed lookup against brute-force scans
- test player, game, date range, and outcome filters

Plot idea:
- x-axis = number of sessions
- y-axis = response time / memory usage

TODO(TEAM): Implement after platform_server/history.py and indexes are ready.
"""

from dataclasses import dataclass, asdict


@dataclass
class HistoryBenchmarkCase:
    """Describes one planned history-query workload."""

    session_count: int
    query_count: int
    filter_type: str
    structure_name: str


def planned_history_cases() -> list[HistoryBenchmarkCase]:
    """Return starter workloads for the final history benchmark."""

    return [
        HistoryBenchmarkCase(100_000, 100, "by_player", "brute_force_scan"),
        HistoryBenchmarkCase(100_000, 100, "by_player", "future_player_hash_index"),
        HistoryBenchmarkCase(100_000, 100, "date_range", "future_bst_time_index"),
        HistoryBenchmarkCase(100_000, 100, "by_game", "future_game_hash_index"),
    ]


def run_history_benchmark() -> list[dict[str, object]]:
    # TODO(BENCHMARK): Time player/game/date/outcome filters over large data.
    # Output row idea:
    # {"session_count": 100000, "filter_type": "date_range",
    #  "structure": "BST time index", "avg_ms": 0.0}
    return []


if __name__ == "__main__":
    print("TODO: implement history benchmark.")
    for case in planned_history_cases():
        print(asdict(case))
