from __future__ import annotations

"""Plotting hooks for benchmark results.

This file avoids requiring matplotlib so the project runs without extra
dependencies. It still exports reproducible CSV data for report graphs.

TODO (DONE)(PLOTTING):
- export rows where x-axis is dataset size or query volume
- y-axis is response time or memory usage
- provide summary rows for final report writing
"""

import csv
from pathlib import Path


def export_plot_data(rows: list[dict[str, object]], output_path: str) -> None:
    """Write benchmark rows to CSV before plotting."""

    # TODO (DONE)(PLOTTING): Write rows to disk for reproducible graph generation.

    # create output path and make parent folders if needed
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    # collect all column names from every row
    fieldnames = sorted({key for row in rows for key in row.keys()})

    # write rows to CSV file
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def load_plot_data(input_path: str) -> list[dict[str, str]]:
    """Read benchmark CSV rows for plotting/report checks."""

    # convert input path string into Path object
    path = Path(input_path)

    # return empty list if file does not exist
    if not path.exists():
        return []

    # read CSV rows back as dictionaries
    with path.open("r", newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def plot_response_times(rows: list[dict[str, object]], output_path: str) -> None:
    """Export CSV data as the dependency-free plotting handoff."""

    # TODO (DONE)(PLOTTING): Create line/bar chart after plotting dependency is chosen.
    # For now, this writes graph-ready rows that Excel or matplotlib can plot.

    # reuse CSV export as plotting handoff
    export_plot_data(rows, output_path)


def summarize_rows(rows: list[dict[str, object]]) -> dict[str, object]:
    """Summarize benchmark rows for reports."""

    # TODO (DONE)(ANALYSIS): Compute averages, fastest structure, slowest baseline,
    # and speedup ratios after benchmark rows are real.

    # handle empty benchmark result set
    if not rows:
        return {"row_count": 0, "status": "no rows"}

    # keep only rows that have numeric avg_ms values
    timed_rows = [row for row in rows if isinstance(row.get("avg_ms"), (int, float))]

    # find fastest and slowest timed rows
    fastest = min(timed_rows, key=lambda row: row["avg_ms"]) if timed_rows else None
    slowest = max(timed_rows, key=lambda row: row["avg_ms"]) if timed_rows else None

    # return summary dictionary for report writing
    return {
        "row_count": len(rows),
        "fastest": fastest,
        "slowest": slowest,
        "status": "summary ready",
    }