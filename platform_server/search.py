from __future__ import annotations

"""Player and game search service.

Likely data structures:
- BST for ordered search/range traversal
- Trie for prefix autocomplete if the team chooses it
- Hash table for exact username/game_id lookup

TODO (DONE)(SEARCH): Replace brute-force comparisons with custom search
structures and keep brute-force only as a benchmark baseline.
"""

from datastructures.bst import BinarySearchTree
from datastructures.hash_table import ChainedHashTable


class SearchService:
    def __init__(self) -> None:
        # create player search tree for prefix lookup
        self._player_tree = BinarySearchTree()  # TODO (DONE): custom BST or Trie.

        # create game search tree for title lookup
        self._game_tree = BinarySearchTree()  # TODO (DONE): custom BST or indexed catalog.

        # hash table for exact username lookup
        self._players_by_username = ChainedHashTable()

        # hash table for exact game_id lookup
        self._games_by_id = ChainedHashTable()

        # keep original rows for fallback searching
        self._player_rows: list[object] = []
        self._game_rows: list[object] = []

    def index_players(self, players: list[object]) -> None:
        '''index player records for search'''

        # save original player rows
        self._player_rows = list(players)

        # reset player indexes
        self._player_tree = BinarySearchTree()
        self._players_by_username = ChainedHashTable(max(16, len(players) * 2))

        for player in players:
            # normalize username for search
            username = self._field(player, "username").lower()

            if username:
                # insert into prefix-search tree
                self._player_tree.insert(username, player)

                # insert into exact username hash table
                self._players_by_username.put(username, player)

    def index_games(self, games: list[object]) -> None:
        '''index game records for search'''

        # save original game rows
        self._game_rows = list(games)

        # reset game indexes
        self._game_tree = BinarySearchTree()
        self._games_by_id = ChainedHashTable(max(16, len(games) * 2))

        for game in games:
            # get title and game id fields
            title = self._field(game, "title").lower()
            game_id = self._field(game, "game_id")

            if title:
                # insert game by title for prefix search
                self._game_tree.insert(title, game)

            if game_id:
                # insert game by id for exact lookup
                self._games_by_id.put(game_id, game)

    def search_players(self, query: str, limit: int = 10) -> list[object]:
        '''search players by exact username or prefix'''

        # TODO (DONE)(RESILIENCE): Clamp limit and reject empty/oversized search strings.
        # TODO (DONE)(BST/TRIE): Implement scalable player search for 10,000+ records.

        # normalize query and clamp limit
        query = self._normalize_query(query)
        limit = self._clamp_limit(limit)

        if not query:
            return []

        # check exact username match first
        exact = self._players_by_username.get(query)
        results: list[object] = [exact] if exact is not None else []

        # add prefix matches from tree
        for player in self._player_tree.prefix_query(query, limit):
            if player not in results:
                results.append(player)

            if len(results) >= limit:
                return results[:limit]

        return results[:limit]

    def autocomplete_players(self, prefix: str, limit: int = 10) -> list[object]:
        '''return player autocomplete results by prefix'''

        # TODO (DONE)(RESILIENCE): Normalize prefix safely before lookup.
        # TODO (DONE)(TRIE): Implement prefix autocomplete and compare to brute force.

        # normalize prefix
        prefix = self._normalize_query(prefix)

        # return prefix results if prefix exists
        return self._player_tree.prefix_query(prefix, self._clamp_limit(limit)) if prefix else []

    def search_games(self, query: str, limit: int = 10) -> list[object]:
        '''search games by title or fallback metadata scan'''

        # TODO (DONE)(RESILIENCE): Handle missing query and invalid limits.
        # TODO (DONE)(BST/INDEX): Implement game search by title, genre, creator, tags.

        # normalize query and clamp limit
        query = self._normalize_query(query)
        limit = self._clamp_limit(limit)

        if not query:
            return []

        # first try prefix search by title
        results = self._game_tree.prefix_query(query, limit)

        # fallback scan title/creator/genre/tags if not enough results
        if len(results) < limit:
            for game in self._game_rows:
                searchable = " ".join([
                    self._field(game, "title"),
                    self._field(game, "creator"),
                    self._field(game, "genre"),
                    " ".join(self._field(game, "tags", default=[])),
                ]).lower()

                if query in searchable and game not in results:
                    results.append(game)

                if len(results) >= limit:
                    break

        return results[:limit]

    def _normalize_query(self, query: str) -> str:
        '''normalize search query'''

        # lowercase, trim, collapse spaces, and limit length
        return " ".join(str(query).strip().lower().split())[:64]

    def _clamp_limit(self, limit: int) -> int:
        '''clamp search limit into safe range'''

        # keep limit between 1 and 100
        return max(1, min(int(limit), 100))

    def _field(self, row: object, name: str, default: object = "") -> str:
        '''read field from dict or object'''

        # support dictionary rows and dataclass/object rows
        if isinstance(row, dict):
            value = row.get(name, default)
        else:
            value = getattr(row, name, default)

        # convert list fields into list of strings
        if isinstance(value, list):
            return [str(item) for item in value]  # type: ignore[return-value]

        # return field as string
        return str(value)