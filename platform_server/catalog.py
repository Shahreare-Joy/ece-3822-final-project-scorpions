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
        # TODO(SORT): Once dataset-backed, sort results by total_plays or last_updated
        #             using mergesort from algorithms/mergesort.py:
        #             from algorithms.mergesort import mergesort
        #             results = mergesort(results, key=lambda g: g.total_plays, reverse=True)
        if genre == "All":
            return list(self._starter_registry)
        return [game for game in self._starter_registry if game.genre == genre]
    def popular_games(self, limit: int = 20) -> list[RegisteredGame]:
        # SAFE PLACEHOLDER: preserves UI behavior. Final version should use
        # catalog popularity fields and sorting/heap-backed ranking.
        # TODO(BENCHMARK): Compare popularity sorting algorithms on large catalogs.
        # TODO(SORT): Replace with heap-based top-N once dataset catalog is loaded:
        #             from algorithms.heapsort import top_n
        #             return top_n(all_catalog_rows, limit, key=lambda g: g.total_plays)
        # TODO(SORT ALT): Or use mergesort for a stable full sort then slice:
        #             from algorithms.mergesort import mergesort
        #             sorted_games = mergesort(all_catalog_rows, key=lambda g: g.total_plays, reverse=True)
        #             return sorted_games[:limit]
        return self._starter_registry[:limit]
    def all_games(self) -> list[RegisteredGame]:
        # TODO(CATALOG): Replace with final dataset-backed catalog rows.
        # TODO(SORT): Once dataset rows are loaded, return mergesort by title or recency:
        #             from algorithms.mergesort import mergesort
        #             return mergesort(dataset_rows, key=lambda g: g["title"])
        return list(self._starter_registry)
