from __future__ import annotations

from client.models import Player
from datastructures.bst import BinarySearchTree
from datastructures.hash_table import ChainedHashTable


class SearchService:
    """Indexed player search service.

    TODO (DONE)(PLAYER SEARCH): Replace scans with a custom hash table for exact
    lookup and a BST prefix index for autocomplete/search.
    TODO (DONE)(ANALYSIS): Benchmarks compare this style against brute force.
    """

    def __init__(self, players: dict[str, Player]) -> None:
        self.players = players
        self._username_index = ChainedHashTable(max(16, len(players) * 2))
        self._name_index = BinarySearchTree()
        name_values: dict[str, list[Player]] = {}
        for player in players.values():
            username = player.username.lower()
            display_name = player.display_name.lower()
            self._username_index.put(username, player)
            name_values.setdefault(username, []).append(player)
            name_values.setdefault(display_name, []).append(player)
        self._insert_balanced_name_index(sorted(name_values.items()))

    def _insert_balanced_name_index(self, items: list[tuple[str, list[Player]]]) -> None:
        """Insert sorted search keys in median order to avoid a degenerate BST.

        The generated dataset usernames are naturally sorted
        (`scorpion_00001`, `scorpion_00002`, ...). Inserting them directly into
        an unbalanced BST creates a linked-list-shaped tree and makes first
        search painfully slow. Median-order insertion keeps the scaffold tree
        shallow without implementing AVL/Red-Black rotation logic here.
        """

        stack: list[tuple[int, int]] = [(0, len(items))]
        while stack:
            start, end = stack.pop()
            if start >= end:
                continue
            mid = (start + end) // 2
            key, players = items[mid]
            for player in players:
                self._name_index.insert(key, player)
            stack.append((mid + 1, end))
            stack.append((start, mid))

    def search_players(self, query: str, limit: int = 8) -> list[Player]:
        # TODO (DONE)(TRIE/HASH/BST): Replace scan with final search structure.
        query = query.strip().lower()
        limit = max(1, min(limit, 50))
        if not query:
            return list(self.players.values())[:limit]
        exact = self._username_index.get(query)
        results: list[Player] = [exact] if isinstance(exact, Player) else []
        for player in self._name_index.prefix_query(query, limit * 2):
            if isinstance(player, Player) and player not in results:
                results.append(player)
            if len(results) >= limit:
                break
        if len(results) < limit:
            for player in self.players.values():
                haystack = f"{player.username} {player.display_name}".lower()
                if query in haystack and player not in results:
                    results.append(player)
                if len(results) >= limit:
                    break
        return results

    def autocomplete_players(self, prefix: str, limit: int = 8) -> list[Player]:
        # TODO (DONE)(TRIE): Replace prefix scan with an autocomplete index.
        prefix = prefix.strip().lower()
        if not prefix:
            return []
        return [player for player in self._name_index.prefix_query(prefix, max(1, min(limit, 50))) if isinstance(player, Player)]
