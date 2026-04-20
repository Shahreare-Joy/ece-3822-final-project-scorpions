from __future__ import annotations


class SortingHooks:
    """Starter placeholder for required sorting algorithm work.

    TODO(SORTING): Implement and benchmark the sorting algorithms required by
    the assignment. Keep UI screens calling services rather than sorting inside
    drawing code.

    Requirement target: at least two sorting algorithms used for real platform
    features such as catalog browsing, leaderboard display, or match history.
    Do the final implementations here, then call them from services.
    """

    def sort_catalog(self, records: list[object], sort_by: str) -> list[object]:
        # TODO(SORTING): Replace this pass-through with algorithm 1 or a
        # dispatcher that calls your team's catalog sorting implementation.
        _ = sort_by
        return records

    def sort_leaderboard(self, records: list[object], sort_by: str) -> list[object]:
        # TODO(SORTING): Implement leaderboard sorting by total score, win rate,
        # or play time. Benchmark against Python/brute-force baseline only for
        # analysis, not as the final assignment shortcut.
        _ = sort_by
        return records

    def sort_match_history(self, records: list[object], sort_by: str) -> list[object]:
        # TODO(SORTING): Implement date/time or score sorting for 100,000+
        # session records. Record timing in placeholders/analysis.py.
        _ = sort_by
        return records
