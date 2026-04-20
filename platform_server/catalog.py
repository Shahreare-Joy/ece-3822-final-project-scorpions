from __future__ import annotations

"""Game catalog service.

Likely data structures:
- Hash table for exact game_id lookup
- BST/index for title/creator/genre browsing
- Graph for player-game recommendations
- Sorting algorithms for popularity, recency, and play count

TODO(CATALOG): Replace mock catalog scans with indexes built from data/.
"""

from .game_registry import RegisteredGame, all_registered_games, get_registered_game


class CatalogService:
    def __init__(self) -> None:
        self._games_by_id = None  # TODO: custom hash table.
        self._genre_index = None  # TODO: custom index for genre filtering.
        self._recommendation_graph = None  # TODO: custom graph.
        self._starter_registry = all_registered_games()

    def get_game(self, game_id: str) -> RegisteredGame | None:
        # TODO(RESILIENCE): Validate game_id before lookup once this is network-facing.
        # SAFE PLACEHOLDER: uses registry fallback until final catalog index is
        # implemented. Screens/services can call this without crashing.
        return get_registered_game(game_id)

    def filter_by_genre(self, genre: str) -> list[RegisteredGame]:
        # BRUTE-FORCE MOCK WARNING: replace with genre index for large catalogs.
        # TODO(RESILIENCE): Normalize genre and reject unsupported filters in the API layer.
        if genre == "All":
            return list(self._starter_registry)
        return [game for game in self._starter_registry if game.genre == genre]

    def popular_games(self, limit: int = 20) -> list[RegisteredGame]:
        # SAFE PLACEHOLDER: preserves UI behavior. Final version should use
        # catalog popularity fields and sorting/heap-backed ranking.
        # TODO(BENCHMARK): Compare popularity sorting algorithms on large catalogs.
        return self._starter_registry[:limit]

    def all_games(self) -> list[RegisteredGame]:
        # TODO(CATALOG): Replace with final dataset-backed catalog rows.
        return list(self._starter_registry)
