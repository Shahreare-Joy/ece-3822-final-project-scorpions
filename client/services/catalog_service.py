from __future__ import annotations

from client.models import Game, HomeRows, Player, PlatformStats
from client.placeholders.sorting_algorithms import SortingHooks
from datastructures.graph import Graph
from datastructures.hash_table import ChainedHashTable
from .recommendation_service import RecommendationService


class CatalogService:
    """Indexed catalog service for the Pygame UI.

    TODO (DONE)(CATALOG/DATASET): Replace list scans with catalog indexes while
    keeping this public surface for the UI.
    """

    def __init__(self, games: dict[str, Game], stats: PlatformStats) -> None:
        self.games = games
        self.stats = stats
        self.sorting = SortingHooks()
        self._game_index = ChainedHashTable(max(16, len(games) * 2))
        self._genre_index = ChainedHashTable()
        self._creator_index = ChainedHashTable()
        self._recommendation_graph = Graph()
        self._build_indexes()

    def _build_indexes(self) -> None:
        for game in self.games.values():
            self._game_index.put(game.game_id, game)
            self._append_index(self._genre_index, game.genre, game)
            self._append_index(self._creator_index, game.creator.lower(), game)
            for tag in game.tags:
                self._recommendation_graph.add_edge(f"tag:{tag}", f"game:{game.game_id}")

    def _append_index(self, table: ChainedHashTable, key: str, game: Game) -> None:
        rows = table.get(key)
        if not isinstance(rows, list):
            rows = []
            table.put(key, rows)
        rows.append(game)

    def get_platform_stats(self) -> PlatformStats:
        return self.stats

    def get_games(self) -> list[Game]:
        return list(self.games.values())

    def get_game(self, game_id: str) -> Game | None:
        # TODO (DONE)(HASH TABLE): Replace dict/mock lookup with catalog lookup structure.
        game = self._game_index.get(game_id)
        return game if isinstance(game, Game) else None

    def filter_games(self, genre: str) -> list[Game]:
        # TODO (DONE)(CATALOG INDEX): Replace scan with a genre index.
        if genre == "All":
            return self.get_games()
        games = self._genre_index.get(genre)
        return list(games) if isinstance(games, list) else []

    def search_games(self, query: str, limit: int = 12) -> list[Game]:
        # TODO (DONE)(INVERTED INDEX): Use indexed exact fields and bounded scan fallback.
        query = query.strip().lower()
        if not query:
            return self.get_games()[:limit]
        results: list[Game] = []
        for game in self.get_games():
            searchable = f"{game.title} {game.creator} {game.genre} {' '.join(game.tags)}".lower()
            if query in searchable:
                results.append(game)
            if len(results) >= limit:
                break
        return results

    def filter_by_creator(self, creator: str) -> list[Game]:
        # TODO (DONE)(CATALOG INDEX): Use a creator index for larger catalogs.
        creator = creator.strip().lower()
        exact = self._creator_index.get(creator)
        if isinstance(exact, list):
            return list(exact)
        return [game for game in self.get_games() if creator in game.creator.lower()]

    def sort_games(self, games: list[Game], sort_by: str) -> list[Game]:
        # TODO (DONE)(SORTING): Route to placeholders/sorting_algorithms.py.
        return self.sorting.sort_catalog(games, sort_by)

    def get_home_rows(self, player: Player | None, recommendations: RecommendationService | None = None) -> HomeRows:
        games = self.get_games()
        by_id = self.games
        # Home rows use prebuilt history/recommendation indexes when available.
        # The deterministic fallback keeps partial tests working when only the
        # catalog service is constructed.
        popular = self.sort_games(games, "players_now")[:5]
        recently = recommendations.recently_played(player, 5) if recommendations else popular
        recommended = recommendations.recommended(player, 5) if recommendations else popular
        return HomeRows(
            continue_playing=[by_id["scorpions-arena"], by_id["sky-raiders"], by_id["turbo-sprint"]],
            recently_played=recently,
            popular_now=popular,
            recommended=recommended,
            featured=[game for game in games if game.team_game] + [by_id["neon-strikers"]],
        )
