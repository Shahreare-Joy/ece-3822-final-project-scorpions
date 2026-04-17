"""Client search service adapter.

TODO(SEARCH): Forward player/game search queries to platform_server/search.py.
The client should not implement Trie/BST/hash table logic.
"""


class ClientSearchService:
    def search_players(self, query: str) -> list[object]:
        _ = query
        return []
