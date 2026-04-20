from __future__ import annotations

from .data_structures import QueryMetrics


class AnalysisHooks:
    """Starter placeholder for performance and complexity analysis.

    TODO(ANALYSIS): Use this module for timing experiments, complexity tables,
    and brute-force comparisons. Do not run benchmarks from Pygame draw methods.
    """

    def record_metric(self, metric: QueryMetrics) -> None:
        # TODO(ANALYSIS): Store metrics for final tables/graphs/report text.
        _ = metric

    def compare_to_bruteforce(self, operation_name: str, input_size: int) -> QueryMetrics:
        # TODO(ANALYSIS): Time the final structure and a brute-force baseline,
        # then return real elapsed_ms/comparisons for the report.
        return QueryMetrics(operation_name=operation_name, structure_name="future-vs-bruteforce", input_size=input_size)

    def export_summary_rows(self) -> list[dict[str, object]]:
        # TODO(ANALYSIS): Return rows for the final report/demo table.
        return []
