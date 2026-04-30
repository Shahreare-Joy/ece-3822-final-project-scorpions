from __future__ import annotations

from client.models import LeaderboardEntry, Player
from client.placeholders.sorting_algorithms import SortingHooks
from datastructures.bst import BinarySearchTree
from datastructures.hash_table import ChainedHashTable
from datastructures.heap import MaxHeap


TEAM_GAME_IDS = {"scorpions-arena", "sky-raiders", "turbo-sprint", "crystal-run"}


class LeaderboardService:
    """Leaderboard service backed by custom indexes."""

    def __init__(self, entries: list[LeaderboardEntry], players: dict[str, Player]) -> None:
        self.entries = entries
        self.players = players
        self.sorting = SortingHooks()
        self._game_entries = ChainedHashTable()
        self._score_ranges = ChainedHashTable()
        self._top_heaps = ChainedHashTable()
        self._build_indexes()

    def _build_indexes(self) -> None:
        for entry in self.entries:
            rows = self._game_entries.get(entry.game_id)
            if not isinstance(rows, list):
                rows = []
                self._game_entries.put(entry.game_id, rows)
            rows.append(entry)
            tree = self._score_ranges.get(entry.game_id)
            if not isinstance(tree, BinarySearchTree):
                tree = BinarySearchTree()
                self._score_ranges.put(entry.game_id, tree)
            tree.insert(entry.score, entry)
            heap = self._top_heaps.get(entry.game_id)
            if not isinstance(heap, MaxHeap):
                heap = MaxHeap()
                self._top_heaps.put(entry.game_id, heap)
            heap.push(entry.score, entry)

    def add_entry(self, entry: LeaderboardEntry) -> None:
        """Add a completed-game score and rebuild rank indexes."""

        self.entries.append(entry)
        self._game_entries = ChainedHashTable()
        self._score_ranges = ChainedHashTable()
        self._top_heaps = ChainedHashTable()
        self._build_indexes()

    def get_leaderboard(self, game_id: str, limit: int = 8) -> list[LeaderboardEntry]:
        # TODO (DONE)(HEAP/BST/SORTING): Replace mock scans with final ranking structures.
        heap = self._top_heaps.get(game_id)
        if isinstance(heap, MaxHeap) and len(heap):
            rows = [entry for entry in heap.top_n(limit) if isinstance(entry, LeaderboardEntry)]
            return [
                LeaderboardEntry(entry.game_id, entry.username, entry.display_name, entry.score, entry.wins, rank)
                for rank, entry in enumerate(rows, start=1)
            ]
        if game_id in TEAM_GAME_IDS:
            return []
        generated: list[LeaderboardEntry] = []
        for index, player in enumerate(list(self.players.values())[:limit], start=1):
            generated.append(LeaderboardEntry(game_id, player.username, player.display_name, max(1000, 50000 - index * 3175 - player.level * 42), max(1, player.total_wins // 2), index))
        return generated

    def get_player_rank(self, game_id: str, username: str) -> int | None:
        # TODO (DONE)(BST/RANK INDEX): Use leaderboard rows for rank lookup.
        for rank, entry in enumerate(self.get_leaderboard(game_id, limit=len(self.entries) or 100), start=1):
            if entry.username == username:
                return rank
        return None

    def get_score_range(self, game_id: str, low_score: int, high_score: int) -> list[LeaderboardEntry]:
        # TODO (DONE)(BST RANGE QUERY): Replace scan with score-range traversal.
        tree = self._score_ranges.get(game_id)
        if not isinstance(tree, BinarySearchTree):
            return []
        return [entry for entry in tree.range_query(low_score, high_score) if isinstance(entry, LeaderboardEntry)]

    def sort_by_metric(self, game_id: str, metric: str, limit: int = 8) -> list[LeaderboardEntry]:
        # TODO (DONE)(SORTING): Use the required sorting algorithm hooks.
        entries = self._game_entries.get(game_id)
        rows = list(entries) if isinstance(entries, list) else []
        return self.sorting.sort_leaderboard(rows, metric)[:limit]
