from __future__ import annotations

"""Plotting hooks for benchmark results.

This file intentionally avoids requiring matplotlib right now so the scaffold
runs without extra dependencies.

TODO(PLOTTING):
- optionally install matplotlib later
- plot x-axis as dataset size or query volume
- plot y-axis as response time or memory usage
- export figures for the final report
"""


def export_plot_data(rows: list[dict[str, object]], output_path: str) -> None:
    """Placeholder for writing benchmark rows to CSV/JSON before plotting."""
    # TODO(PLOTTING): Write rows to disk for reproducible graph generation.
    # Recommended columns:
    # feature, dataset_size, query_count, structure_name, avg_ms, memory_mb
    _ = (rows, output_path)


def plot_response_times(rows: list[dict[str, object]], output_path: str) -> None:
    """Placeholder plotting API.

    Keep this function as the single plotting entry point so benchmark scripts
    do not each invent their own graphing style.
    """
    # TODO(PLOTTING): Create line/bar chart after plotting dependency is chosen.
    # Required final graphs:
    # - player search: dataset size vs avg response time
    # - leaderboard: score count/query type vs avg response time
    # - history: session count/filter type vs avg response time
    _ = (rows, output_path)


def summarize_rows(rows: list[dict[str, object]]) -> dict[str, object]:
    """Starter summary hook for benchmark reports.

    TODO(ANALYSIS): Compute averages, fastest structure, slowest baseline, and
    speedup ratios after benchmark rows are real.
    """

    return {"row_count": len(rows), "status": "summary scaffold only"}
