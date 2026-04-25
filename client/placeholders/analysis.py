from __future__ import annotations

from time import perf_counter
from typing import Callable

from .data_structures import QueryMetrics


class AnalysisHooks:
    """Starter helper for performance and complexity analysis."""

    def __init__(self) -> None:
        # store benchmark/timing metrics
        self._metrics: list[QueryMetrics] = []

    def record_metric(self, metric: QueryMetrics) -> None:
        '''store one metric row'''

        # TODO (DONE)(ANALYSIS): Store metrics for final tables/graphs/report text.
        self._metrics.append(metric)

    def time_operation(self, operation_name: str, input_size: int, structure_name: str, function: Callable[[], object]) -> QueryMetrics:
        '''time one operation and record its metric'''

        # start timer before operation
        start = perf_counter()

        # run operation being measured
        function()

        # calculate elapsed time in milliseconds
        elapsed_ms = (perf_counter() - start) * 1000

        # create metric row
        metric = QueryMetrics(
            operation_name=operation_name,
            input_size=input_size,
            structure_name=structure_name,
            elapsed_ms=elapsed_ms,
            notes="measured"
        )

        # store metric
        self.record_metric(metric)

        return metric

    def compare_to_bruteforce(self, operation_name: str, input_size: int) -> QueryMetrics:
        '''create placeholder comparison metric'''

        # TODO (DONE)(ANALYSIS): Return a structured placeholder row for report comparison.

        # create comparison row
        metric = QueryMetrics(
            operation_name=operation_name,
            structure_name="final-vs-bruteforce",
            input_size=input_size,
            notes="comparison hook ready"
        )

        # store metric
        self.record_metric(metric)

        return metric

    def export_summary_rows(self) -> list[dict[str, object]]:
        '''export stored metrics as report-ready rows'''

        # TODO (DONE)(ANALYSIS): Return rows for the final report/demo table.

        # convert metric objects into dictionaries
        return [metric.__dict__.copy() for metric in self._metrics]