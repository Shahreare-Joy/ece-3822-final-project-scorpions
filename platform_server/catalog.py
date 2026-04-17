from __future__ import annotations

"""Game catalog service.

Likely data structures:
- Hash table for exact game_id lookup
- BST/index for title/creator/genre browsing
- Graph for player-game recommendations
- Sorting algorithms for popularity, recency, and play count

TODO(CATALOG): Replace mock catalog scans with indexes built from data/.
"""


class CatalogService:
    def __init__(self) -> None:
        self._games_by_id = None  # TODO: custom hash table.
        self._genre_index = None  # TODO: custom index for genre filtering.
        self._recommendation_graph = None  # TODO: custom graph.

    def get_game(self, game_id: str) -> object | None:
        _ = game_id
        raise NotImplementedError("Team must implement game lookup.")

    def filter_by_genre(self, genre: str) -> list[object]:
        _ = genre
        raise NotImplementedError("Team must implement genre filtering.")

    def popular_games(self, limit: int = 20) -> list[object]:
        _ = limit
        raise NotImplementedError("Team must implement popularity sorting/indexing.")
