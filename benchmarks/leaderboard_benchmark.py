from __future__ import annotations

"""Leaderboard query stress-test.

Goal:
- compare heap/BST/range-query leaderboard structures against brute-force sort
- test top-N and score range query workloads

TODO (DONE)(TEAM): Implement after datastructures/heap.py and BST/range index exist.
"""

from dataclasses import asdict, dataclass
from pathlib import Path
import sys
from time import perf_counter

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from platform_server.data_ingest import DataIngestService
from platform_server.leaderboard import LeaderboardService
from benchmarks.plotting_hooks import export_plot_data


@dataclass
class LeaderboardBenchmarkCase:
    """Describes one leaderboard workload."""

    score_count: int
    query_count: int
    query_type: str
    structure_name: str


def planned_leaderboard_cases() -> list[LeaderboardBenchmarkCase]:
    '''return planned benchmark cases for leaderboard queries'''

    return [
        LeaderboardBenchmarkCase(2_000, 50, "top_n", "brute_force_sort"),
        LeaderboardBenchmarkCase(2_000, 50, "top_n", "heap_top_n"),
        LeaderboardBenchmarkCase(10_000, 50, "score_range", "bst_range_index"),
    ]


def run_leaderboard_benchmark() -> list[dict[str, object]]:
    '''run leaderboard benchmark cases and collect timing rows'''
    # TODO (DONE)(BENCHMARK): Time top-N and score range queries.

    # load session dataset
    sessions = DataIngestService().load_sessions()

    # store benchmark result rows
    rows: list[dict[str, object]] = []

    # run each planned leaderboard benchmark case
    for case in planned_leaderboard_cases():
        # limit sample size based on benchmark case
        sample = sessions[: min(case.score_count, len(sessions))]

        # load sample into leaderboard service indexes
        service = LeaderboardService()
        service.load_from_sessions(sample)

        # choose first available game_id as query target
        game_id = str(sample[0].get("game_id", "")) if sample else ""

        if case.structure_name == "brute_force_sort":
            # baseline: filter rows by game_id, sort by score, and take top 10
            elapsed = _time_queries(
                lambda: sorted(
                    [row for row in sample if row.get("game_id") == game_id],
                    key=lambda row: int(row.get("score", 0)),
                    reverse=True
                )[:10],
                case.query_count
            )
        elif case.query_type == "score_range":
            # indexed range query using leaderboard service
            elapsed = _time_queries(
                lambda: service.score_range(game_id, 1_000, 20_000),
                case.query_count
            )
        else:
            # indexed top-n query using leaderboard service
            elapsed = _time_queries(
                lambda: service.top_n(game_id, 10),
                case.query_count
            )

        # save timing result for this case
        rows.append({**asdict(case), "actual_size": len(sample), "avg_ms": elapsed})

    return rows


def _time_queries(function, query_count: int) -> float:
    '''time repeated calls and return average milliseconds'''

    # start timer before repeated queries
    start = perf_counter()

    # run function multiple times
    for _ in range(query_count):
        function()

    # compute average runtime in milliseconds
    return ((perf_counter() - start) / max(1, query_count)) * 1000


if __name__ == "__main__":
    # run benchmark script directly
    rows = run_leaderboard_benchmark()

    # export rows for plotting/reporting
    export_plot_data(rows, "benchmarks/results/leaderboard_benchmark.csv")

    # print rows for quick terminal review
    for row in rows:
        print(row)