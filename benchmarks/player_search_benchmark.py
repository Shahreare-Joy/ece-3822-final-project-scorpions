from __future__ import annotations

"""Player search stress-test.

Goal:
- test player records directly through search structures
- compare optimized structure vs brute-force prefix search

Plot idea:
- x-axis = number of players
- y-axis = average response time / memory usage

TODO (DONE)(TEAM): Implement after datastructures/search indexes are complete.
"""

from dataclasses import asdict, dataclass
from pathlib import Path
import sys
from time import perf_counter

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from algorithms.search_algorithms import brute_force_prefix
from benchmarks.plotting_hooks import export_plot_data
from platform_server.data_ingest import DataIngestService
from platform_server.search import SearchService


@dataclass
class PlayerSearchBenchmarkCase:
    """Describes one benchmark workload."""

    dataset_size: int
    query_count: int
    query_type: str
    structure_name: str


def planned_player_search_cases() -> list[PlayerSearchBenchmarkCase]:
    """Return benchmark workloads.

    TODO (DONE)(BENCHMARK): Add 10,000 and larger player datasets. This script
    uses the committed dataset and safely caps at available records.
    """

    return [
        PlayerSearchBenchmarkCase(1_000, 50, "prefix", "brute_force_baseline"),
        PlayerSearchBenchmarkCase(1_000, 50, "prefix", "bst_prefix_index"),
        PlayerSearchBenchmarkCase(10_000, 100, "prefix", "brute_force_baseline"),
        PlayerSearchBenchmarkCase(10_000, 100, "prefix", "bst_prefix_index"),
    ]


def run_player_search_benchmark() -> list[dict[str, object]]:
    '''run player search benchmark cases and collect timing rows'''
    # TODO (DONE)(BENCHMARK): Load player records, time brute force vs BST search,
    # then return rows for plotting.

    # load player dataset
    players = DataIngestService().load_players()

    # store benchmark result rows
    rows: list[dict[str, object]] = []

    # run each planned player-search benchmark case
    for case in planned_player_search_cases():
        # limit sample size based on benchmark case
        sample = players[: min(case.dataset_size, len(players))]

        # build search prefixes from the first records in the sample
        queries = [str(row.get("username", ""))[:3] for row in sample[: case.query_count]]

        if case.structure_name == "bst_prefix_index":
            # indexed version: build player search index first
            service = SearchService()
            service.index_players(sample)

            # time autocomplete lookups through optimized search service
            elapsed = _time_queries(
                lambda query: service.autocomplete_players(query, 10),
                queries
            )
        else:
            # baseline version: scan every player and return matching prefixes
            elapsed = _time_queries(
                lambda query: brute_force_prefix(
                    sample,
                    query,
                    lambda row: str(row.get("username", ""))
                )[:10],
                queries
            )

        # save timing result for this case
        rows.append({**asdict(case), "actual_size": len(sample), "avg_ms": elapsed})

    return rows


def _time_queries(function, queries: list[str]) -> float:
    '''time repeated search queries and return average milliseconds'''

    # start timer before search loop
    start = perf_counter()

    # run each query once
    for query in queries:
        function(query)

    # compute elapsed runtime
    elapsed = perf_counter() - start

    # return average runtime per query in milliseconds
    return (elapsed / max(1, len(queries))) * 1000


if __name__ == "__main__":
    # run benchmark script directly
    rows = run_player_search_benchmark()

    # export rows for plotting/reporting
    export_plot_data(rows, "benchmarks/results/player_search_benchmark.csv")

    # print rows for quick terminal review
    for row in rows:
        print(row)