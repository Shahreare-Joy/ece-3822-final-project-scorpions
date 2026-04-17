from __future__ import annotations

from scorpions_arcade.models import Player


class SearchService:
    """Temporary player search service.

    Requirement target: responsive player search/autocomplete for 10,000+
    players. The current implementation scans mock data so the UI can run now.

    TODO(PLAYER SEARCH): Replace scans with a final structure such as:
    - Trie for prefix autocomplete
    - Hash table for exact username lookup
    - BST if ordered/range traversal is part of your design
    TODO(ANALYSIS): Benchmark final search against this brute-force scan.
    """

    def __init__(self, players: dict[str, Player]) -> None:
        self.players = players

    def search_players(self, query: str, limit: int = 8) -> list[Player]:
        # BRUTE-FORCE MOCK WARNING:
        # This loops through every player. It is acceptable for the UI demo, but
        # must be replaced before using 10,000+ player records in the final
        # project.
        # TODO(TRIE/HASH/BST): Replace scan with final search structure.
        query = query.strip().lower()
        if not query:
            return list(self.players.values())[:limit]
        return [player for player in self.players.values() if query in player.username.lower() or query in player.display_name.lower() or query in player.favorite_genre.lower()][:limit]

    def autocomplete_players(self, prefix: str, limit: int = 8) -> list[Player]:
        # BRUTE-FORCE MOCK WARNING:
        # Prefix autocomplete should not scan every player in the final project.
        # TODO(TRIE): Replace this prefix scan with an autocomplete index.
        prefix = prefix.strip().lower()
        if not prefix:
            return []
        return [player for player in self.players.values() if player.username.lower().startswith(prefix) or player.display_name.lower().startswith(prefix)][:limit]
