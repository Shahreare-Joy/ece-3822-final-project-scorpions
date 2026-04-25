from __future__ import annotations

"""Match history query stress-test.

Goal:
- test session records directly through history indexes
- compare indexed lookup against brute-force scans

TODO (DONE)(TEAM): Implement after platform_server/history.py and indexes are ready.
"""

from dataclasses import asdict, dataclass
from pathlib import Path
import sys
from time import perf_counter

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from platform_server.data_ingest import DataIngestService
from platform_server.history import HistoryService
from benchmarks.plotting_hooks import export_plot_data


@dataclass
class HistoryBenchmarkCase:
    '''Describes one history-query workload.'''

    session_count: int
    query_count: int
    filter_type: str
    structure_name: str


def planned_history_cases() -> list[HistoryBenchmarkCase]:
    '''return planned benchmark cases for history queries'''

    return [
        HistoryBenchmarkCase(2_000, 50, "by_player", "brute_force_scan"),
        HistoryBenchmarkCase(2_000, 50, "by_player", "hash_index"),
        HistoryBenchmarkCase(10_000, 50, "by_game", "hash_index"),
    ]


def run_history_benchmark() -> list[dict[str, object]]:
    '''run benchmark cases and collect timing rows'''
    # TODO (DONE)(BENCHMARK): Time player/game/date/outcome filters over data.

    # load session dataset
    sessions = DataIngestService().load_sessions()

    # store benchmark result rows
    rows: list[dict[str, object]] = []

    # run each planned benchmark case
    for case in planned_history_cases():
        # limit sample size based on benchmark case
        sample = sessions[: min(case.session_count, len(sessions))]

        # choose first available username/game_id as query target
        username = str(sample[0].get("username", "")) if sample else ""
        game_id = str(sample[0].get("game_id", "")) if sample else ""

        if case.structure_name == "brute_force_scan":
            # baseline: scan every row and filter by username
            elapsed = _time_queries(
                lambda: [row for row in sample if row.get("username") == username][:50],
                case.query_count
            )
        else:
            # indexed version: load sessions into HistoryService indexes
            service = HistoryService()
            service.load_sessions(sample)

            if case.filter_type == "by_game":
                # query indexed game history
                elapsed = _time_queries(lambda: service.by_game(game_id, 50), case.query_count)
            else:
                # query indexed player history
                elapsed = _time_queries(lambda: service.by_player(username, 50), case.query_count)

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
    rows = run_history_benchmark()

    # export rows for plotting/reporting
    export_plot_data(rows, "benchmarks/results/history_benchmark.csv")

    # print rows for quick terminal review
    for row in rows:
        print(row)