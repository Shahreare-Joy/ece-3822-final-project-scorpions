from __future__ import annotations

from dataclasses import dataclass


@dataclass
class FilterState:
    """UI filter state passed into future service/data hook layers."""

    genre: str = "All"
    query: str = ""
    sort_by: str = "popular"


@dataclass
class SearchResult:
    label: str
    detail: str
    score_text: str = ""

