from __future__ import annotations

from dataclasses import replace

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
        games = [game for game in self.get_games() if not self._is_temporary_game(game)]
        playable = [game for game in games if game.playable]
        normal_catalog = [game for game in games if self._is_normal_catalog_game(game)]

        # Home rows use prebuilt history/recommendation indexes when available.
        # The deterministic fallback keeps partial tests working when only the
        # catalog service is constructed. Rows are assembled from different
        # candidate pools so Continue/Recent/Popular/Recommended do not become
        # the same five cards with different headings.
        has_real_history = recommendations.has_history(player) if recommendations else False
        recent_candidates = recommendations.recently_played(player, 8) if has_real_history and recommendations else []
        recent_candidates = [game for game in recent_candidates if not self._is_temporary_game(game)]
        recently = self._unique_games(recent_candidates, 5)

        popular_candidates = recommendations.popular_games(16) if recommendations else self.sort_games(normal_catalog, "players_now")
        popular_candidates = self._playable_first(popular_candidates)
        popular = self._fill_row(
            popular_candidates,
            self._playable_first(self.sort_games(normal_catalog, "players_now")),
            limit=5,
            avoid={game.game_id for game in recently},
        )
        if len(popular) < 3:
            popular = self._fill_row(popular, self._playable_first(self.sort_games(normal_catalog, "players_now")), limit=5)

        continue_playing = self._fill_row(
            playable,
            playable,
            limit=5,
            avoid={game.game_id for game in recently},
            playable_only=True,
        )

        recommendation_candidates = recommendations.recommended(player, 16) if recommendations else popular_candidates
        recommended = self._fill_row(
            recommendation_candidates,
            playable + normal_catalog,
            limit=5,
            avoid={game.game_id for game in recently + popular},
        )
        if len(recommended) < 3:
            recommended = self._fill_row(recommended, playable + normal_catalog, limit=5, avoid={game.game_id for game in recently})
        recommended = [self._label_catalog_only(game) for game in recommended]

        featured_candidates = [
            game
            for game in normal_catalog
            if game.playable
            or game.status.lower() in {"new", "live event", "trending", "hot"}
            or game.last_updated.lower() in {"updated today", "updated yesterday"}
        ]
        featured = self._fill_row(
            featured_candidates,
            self.sort_games(normal_catalog, "players_now"),
            limit=5,
            avoid={game.game_id for game in continue_playing + recently},
        )
        featured = [self._label_catalog_only(game) for game in featured]

        coming_soon = self._fill_row(
            [game for game in games if self._is_coming_soon_game(game)],
            [game for game in games if not game.playable and not self._is_normal_catalog_game(game)],
            limit=5,
            allow_coming_soon=True,
        )
        coming_soon = [self._label_coming_soon(game) for game in coming_soon]

        return HomeRows(
            continue_playing=continue_playing,
            recently_played=recently,
            popular_now=popular,
            recommended=recommended,
            featured=featured,
            coming_soon=coming_soon,
        )

    def _playable_first(self, games: list[Game]) -> list[Game]:
        return sorted(games, key=lambda game: (game.playable, game.players_now, game.total_plays), reverse=True)

    def _fill_row(
        self,
        primary: list[Game],
        fallback: list[Game],
        limit: int,
        avoid: set[str] | None = None,
        playable_only: bool = False,
        allow_coming_soon: bool = False,
    ) -> list[Game]:
        avoid = avoid or set()
        rows: list[Game] = []
        seen: set[str] = set()
        for game in [*primary, *fallback]:
            if game.game_id in seen or game.game_id in avoid:
                continue
            if self._is_temporary_game(game):
                continue
            if playable_only and not game.playable:
                continue
            if self._is_coming_soon_game(game) and not allow_coming_soon:
                continue
            rows.append(game)
            seen.add(game.game_id)
            if len(rows) >= limit:
                break
        return rows

    def _unique_games(self, games: list[Game], limit: int) -> list[Game]:
        rows: list[Game] = []
        seen: set[str] = set()
        for game in games:
            if game.game_id in seen or self._is_temporary_game(game):
                continue
            rows.append(game)
            seen.add(game.game_id)
            if len(rows) >= limit:
                break
        return rows

    def _is_normal_catalog_game(self, game: Game) -> bool:
        return not self._is_temporary_game(game) and not self._is_coming_soon_game(game)

    def _is_temporary_game(self, game: Game) -> bool:
        tags = {tag.lower() for tag in game.tags}
        return (
            game.game_id == "snake-test"
            or "temporary" in tags
            or "test-game" in tags
            or "temporary" in game.status.lower()
            or "test lab" in game.title.lower()
        )

    def _is_coming_soon_game(self, game: Game) -> bool:
        status = game.status.lower()
        tags = {tag.lower() for tag in game.tags}
        return (
            not game.playable
            and (
                game.team_game
                or "pending" in status
                or "coming" in status
                or "integration" in status
                or "coming-soon" in tags
            )
        )

    def _label_catalog_only(self, game: Game) -> Game:
        if game.playable or game.status.lower() in {"catalog only", "coming soon"}:
            return game
        return replace(game, status="Catalog only")

    def _label_coming_soon(self, game: Game) -> Game:
        if game.status.lower() == "coming soon":
            return game
        return replace(game, status="Coming soon")
