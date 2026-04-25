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
        # create lookup table for game_id searches
        self._games_by_id = ChainedHashTable()  # TODO (DONE): custom hash table.

        # create genre index for filtering games by category
        self._genre_index = ChainedHashTable()  # TODO (DONE): custom index for genre filtering.

        # create graph for recommendation relationships
        self._recommendation_graph = Graph()  # TODO (DONE): custom graph.

        # load starter games from registry
        self._starter_registry = all_registered_games()
        self.load_games(self._starter_registry)

    def load_games(self, games: list[RegisteredGame]) -> None:
        '''load games into hash indexes and recommendation graph'''

        # keep copy of all games for all_games and fallback browsing
        self._starter_registry = list(games)

        # rebuild game lookup table with enough capacity
        self._games_by_id = ChainedHashTable(max(16, len(games) * 2))

        # rebuild genre index and recommendation graph
        self._genre_index = ChainedHashTable()
        self._recommendation_graph = Graph()

        for game in games:
            # index game by exact game_id
            self._games_by_id.put(game.game_id, game)

            # get existing list for this genre
            existing = self._genre_index.get(game.genre)

            # create new genre list if this is the first game in genre
            if not isinstance(existing, list):
                existing = []
                self._genre_index.put(game.genre, existing)

            # add game to genre list
            existing.append(game)

            # connect genre node to game node in recommendation graph
            self._recommendation_graph.add_edge(f"genre:{game.genre}", f"game:{game.game_id}", 1.0)

    def get_game(self, game_id: str) -> RegisteredGame | None:
        '''return one game by exact game_id'''

        # TODO (DONE)(RESILIENCE): Validate game_id before lookup.

        # reject empty game_id
        if not game_id:
            return None

        # lookup game in custom hash table
        game = self._games_by_id.get(game_id)

        # return only valid RegisteredGame objects
        return game if isinstance(game, RegisteredGame) else None

    def filter_by_genre(self, genre: str) -> list[RegisteredGame]:
        '''return games matching selected genre'''

        # TODO (DONE)(RESILIENCE): Normalize genre and reject unsupported filters in the API layer.

        # return all games if no specific genre is selected
        if not genre or genre == "All":
            return list(self._starter_registry)

        # get games from genre index
        games = self._genre_index.get(genre)

        # return matching games or empty list
        return list(games) if isinstance(games, list) else []

    def popular_games(self, limit: int = 20) -> list[RegisteredGame]:
        '''return popular games limited to requested count'''

        # TODO (DONE)(BENCHMARK): Compare popularity sorting algorithms on large catalogs.

        # keep limit in safe range
        limit = max(1, min(int(limit), 100))

        # sort playable games first as simple popularity placeholder
        return sorted(self._starter_registry, key=lambda game: game.playable, reverse=True)[:limit]

    def all_games(self) -> list[RegisteredGame]:
        '''return all catalog games'''

        # TODO (DONE)(CATALOG): Return dataset/registry-backed catalog rows.

        # return copy so caller does not mutate original registry
        return list(self._starter_registry)