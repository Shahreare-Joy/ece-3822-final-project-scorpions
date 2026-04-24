from __future__ import annotations

"""Game catalog service.

Likely data structures:
- Hash table for exact game_id lookup
- Hash table index for genre browsing
- Graph for player-game recommendations
- Sorting algorithms for popularity, recency, and play count

TODO (DONE)(CATALOG): Replace mock catalog scans with indexes built from data/.
"""

from datastructures.graph import Graph
from datastructures.hash_table import ChainedHashTable

from .game_registry import RegisteredGame, all_registered_games


class CatalogService:
    def __init__(self) -> None:
        # Main lookup tables and graph initialized here
        self._games_by_id = ChainedHashTable()  # Fast O(1) average lookup by game_id
        self._genre_index = ChainedHashTable()  # Maps genre -> list of games
        self._recommendation_graph = Graph()  # Graph connects genres to games
        self._starter_registry = all_registered_games()
        self.load_games(self._starter_registry)

    def load_games(self, games: list[RegisteredGame]) -> None:
        # Rebuild all internal structures when loading a new dataset
        self._starter_registry = list(games)
        self._games_by_id = ChainedHashTable(max(16, len(games) * 2))  # Resize based on dataset size
        self._genre_index = ChainedHashTable()
        self._recommendation_graph = Graph()

        for game in games:
            # Insert into ID lookup table
            self._games_by_id.put(game.game_id, game)

            # Build genre index (group games by genre)
            existing = self._genre_index.get(game.genre)
            if not isinstance(existing, list):
                existing = []
                self._genre_index.put(game.genre, existing)
            existing.append(game)

            # Add edge in recommendation graph (genre -> game)
            self._recommendation_graph.add_edge(
                f"genre:{game.genre}", f"game:{game.game_id}", 1.0
            )

    def get_game(self, game_id: str) -> RegisteredGame | None:
        # TODO (DONE)(RESILIENCE): Validate game_id before lookup.
        if not game_id:
            return None

        # Retrieve from hash table and type-check
        game = self._games_by_id.get(game_id)
        return game if isinstance(game, RegisteredGame) else None

    def filter_by_genre(self, genre: str) -> list[RegisteredGame]:
        # TODO (DONE)(RESILIENCE): Normalize genre and reject unsupported filters in the API layer.
        if not genre or genre == "All":
            return list(self._starter_registry)  # Return all if no filter

        # Lookup pre-built genre index
        games = self._genre_index.get(genre)
        return list(games) if isinstance(games, list) else []

    def popular_games(self, limit: int = 20) -> list[RegisteredGame]:
        # TODO (DONE)(BENCHMARK): Compare popularity sorting algorithms on large catalogs.
        limit = max(1, min(int(limit), 100))  # Clamp limit between 1 and 100

        # Sort by "playable" flag (placeholder for popularity metric)
        return sorted(
            self._starter_registry,
            key=lambda game: game.playable,
            reverse=True
        )[:limit]

    def all_games(self) -> list[RegisteredGame]:
        # TODO (DONE)(CATALOG): Return dataset/registry-backed catalog rows.
        return list(self._starter_registry)  # Return a copy to avoid external mutation