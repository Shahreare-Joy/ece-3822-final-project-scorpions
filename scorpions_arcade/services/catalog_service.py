from __future__ import annotations

from scorpions_arcade.models import Game, HomeRows, Player, PlatformStats


class CatalogService:
    """Temporary mock catalog service.

    TODO(CATALOG/DATASET): Replace list scans with cleaned dataset records and
    custom catalog indexes while keeping this public surface for the UI.

    Requirement targets:
    - game search and filtering by genre, creator, tags, popularity, recency
    - catalog sorting by popularity, recent activity, title, play count
    - scalable browsing when the catalog grows beyond the visible mock rows
    """

    def __init__(self, games: dict[str, Game], stats: PlatformStats) -> None:
        self.games = games
        self.stats = stats

    def get_platform_stats(self) -> PlatformStats:
        return self.stats

    def get_games(self) -> list[Game]:
        # MOCK DATA WARNING:
        # Returning the full catalog is fine for the small template. For a larger
        # dataset, expose paged/filter-ready results from a catalog index.
        return list(self.games.values())

    def get_game(self, game_id: str) -> Game | None:
        # TODO(HASH TABLE): Replace dict/mock lookup with the final catalog
        # lookup structure after dataset ingestion.
        return self.games.get(game_id)

    def filter_games(self, genre: str) -> list[Game]:
        # BRUTE-FORCE MOCK WARNING:
        # This scans every game. Replace it with a genre index before using a
        # large catalog.
        # TODO(CATALOG INDEX): Replace scan with a genre index or tree traversal.
        if genre == "All":
            return self.get_games()
        return [game for game in self.get_games() if game.genre == genre]

    def search_games(self, query: str, limit: int = 12) -> list[Game]:
        # BRUTE-FORCE MOCK WARNING:
        # Title/tag/creator search should use an index for the final platform.
        # TODO(INVERTED INDEX): Replace mock scan with title/tag/creator index.
        query = query.strip().lower()
        if not query:
            return self.get_games()[:limit]
        matches = [
            game
            for game in self.get_games()
            if query in game.title.lower()
            or query in game.creator.lower()
            or query in game.genre.lower()
            or any(query in tag.lower() for tag in game.tags)
        ]
        return matches[:limit]

    def filter_by_creator(self, creator: str) -> list[Game]:
        # TODO(CATALOG INDEX): Use a creator index for larger catalogs.
        creator = creator.strip().lower()
        return [game for game in self.get_games() if creator in game.creator.lower()]

    def sort_games(self, games: list[Game], sort_by: str) -> list[Game]:
        # MOCK SORT WARNING:
        # Python's built-in sorted keeps the UI useful for now. The final
        # assignment sorting algorithms should be called from here after your
        # team implements and benchmarks them.
        # TODO(SORTING): Route to placeholders/sorting_algorithms.py after the
        # team implements the required sorting algorithms.
        if sort_by == "players_now":
            return sorted(games, key=lambda game: game.players_now, reverse=True)
        if sort_by == "total_plays":
            return sorted(games, key=lambda game: game.total_plays, reverse=True)
        if sort_by == "release_year":
            return sorted(games, key=lambda game: game.release_year, reverse=True)
        return sorted(games, key=lambda game: game.title)

    def get_home_rows(self, player: Player | None) -> HomeRows:
        _ = player
        games = self.get_games()
        by_id = self.games
        # TODO(GRAPH): Replace recommended row with a graph-based recommender.
        # TODO(SCALE): Do not compute all home rows by sorting/scanning the full
        # final dataset on every frame. Build cached service results or indexes.
        return HomeRows(
            continue_playing=[by_id["scorpions-arena"], by_id["crystal-run"], by_id["block-arena"]],
            recently_played=[by_id["sky-raiders"], by_id["turbo-sprint"], by_id["logic-lab"], by_id["castle-quest"]],
            popular_now=sorted(games, key=lambda game: game.players_now, reverse=True)[:5],
            recommended=[by_id["circuit-chef"], by_id["astro-miners"], by_id["tiny-tactics"], by_id["buddy-bots"]],
            featured=[game for game in games if game.team_game] + [by_id["neon-strikers"]],
        )
