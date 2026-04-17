from __future__ import annotations

from scorpions_arcade.models import LeaderboardEntry, Player


class LeaderboardService:
    """Temporary leaderboard service backed by mock rows.

    Requirement targets:
    - top-N lookup
    - player rank lookup
    - score range queries
    - sorting by score, win rate, and play time

    TODO(HEAP/BST/SORTING): Replace mock scans with final structures. A heap or
    priority queue can support top-N, while a BST/tree-like index can support
    score ranges and rank lookup. Sorting algorithms should live in
    placeholders/sorting_algorithms.py and be benchmarked in analysis.py.
    """

    def __init__(self, entries: list[LeaderboardEntry], players: dict[str, Player]) -> None:
        self.entries = entries
        self.players = players

    def get_leaderboard(self, game_id: str, limit: int = 8) -> list[LeaderboardEntry]:
        # BRUTE-FORCE MOCK WARNING:
        # This filters mock rows directly. Replace with heap/priority queue,
        # tree, or other documented leaderboard structure for scale.
        # TODO(HEAP/BST/SORTING): Replace this with final ranking structures.
        existing = [entry for entry in self.entries if entry.game_id == game_id]
        if existing:
            return existing[:limit]
        generated: list[LeaderboardEntry] = []
        for index, player in enumerate(list(self.players.values())[:limit], start=1):
            generated.append(LeaderboardEntry(game_id, player.username, player.display_name, max(1000, 50000 - index * 3175 - player.level * 42), max(1, player.total_wins // 2), index))
        return generated

    def get_player_rank(self, game_id: str, username: str) -> int | None:
        # BRUTE-FORCE MOCK WARNING:
        # Rank lookup should not require walking a full leaderboard at scale.
        # TODO(BST/RANK INDEX): Replace scan with rank lookup structure.
        for entry in self.get_leaderboard(game_id, limit=len(self.entries) or 100):
            if entry.username == username:
                return entry.rank
        return None

    def get_score_range(self, game_id: str, low_score: int, high_score: int) -> list[LeaderboardEntry]:
        # BRUTE-FORCE MOCK WARNING:
        # Score range queries are a natural place for a BST/tree-like index.
        # TODO(BST RANGE QUERY): Replace scan with score-range traversal.
        entries = [entry for entry in self.entries if entry.game_id == game_id and low_score <= entry.score <= high_score]
        return sorted(entries, key=lambda entry: entry.score, reverse=True)

    def sort_by_metric(self, game_id: str, metric: str, limit: int = 8) -> list[LeaderboardEntry]:
        # TODO(SORTING): Replace with one of the team's required sorting
        # algorithms after implementing placeholders/sorting_algorithms.py.
        entries = [entry for entry in self.entries if entry.game_id == game_id]
        if metric == "wins":
            entries = sorted(entries, key=lambda entry: entry.wins, reverse=True)
        else:
            entries = sorted(entries, key=lambda entry: entry.score, reverse=True)
        return entries[:limit]
