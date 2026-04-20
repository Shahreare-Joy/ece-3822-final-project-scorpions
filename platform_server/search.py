from __future__ import annotations

"""Player and game search service.

Likely data structures:
- BST for ordered search/range traversal
- Trie for prefix autocomplete if the team chooses it
- Hash table for exact username/game_id lookup

TODO(SEARCH): Replace brute-force comparisons with custom search structures and
benchmark against brute force in tests/test_search.py.
"""


class SearchService:
    def __init__(self) -> None:
        self._player_tree = None  # TODO: custom BST or Trie.
        self._game_tree = None  # TODO: custom BST or indexed catalog.

    def search_players(self, query: str, limit: int = 10) -> list[object]:
        # TODO(RESILIENCE): Clamp limit and reject empty/oversized search strings.
        # TODO(BST/TRIE): Implement scalable player search for 10,000+ records.
        # WARNING(SCALE): A brute-force scan is acceptable only as a baseline benchmark.
        _ = (query, limit)
        raise NotImplementedError("Team must implement player search.")

    def autocomplete_players(self, prefix: str, limit: int = 10) -> list[object]:
        # TODO(RESILIENCE): Normalize prefix safely before lookup.
        # TODO(TRIE): Implement prefix autocomplete and compare to brute force.
        _ = (prefix, limit)
        raise NotImplementedError("Team must implement player autocomplete.")

    def search_games(self, query: str, limit: int = 10) -> list[object]:
        # TODO(RESILIENCE): Handle missing query and invalid limits.
        # TODO(BST/INDEX): Implement game search by title, genre, creator, tags.
        # WARNING(SCALE): Do not leave final catalog search as repeated full scans.
        _ = (query, limit)
        raise NotImplementedError("Team must implement game search.")
