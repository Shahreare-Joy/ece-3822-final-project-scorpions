from __future__ import annotations

"""Leaderboard service.

Likely data structures:
- Custom Heap / PriorityQueue for top-N scores
- BST or ordered score index for score range queries
- Sorting algorithms from algorithms/ for report comparisons

TODO(LEADERBOARD): Implement ranking using datastructures/heap.py and range
queries using datastructures/bst.py or a documented alternative.
"""


class LeaderboardService:
    def __init__(self) -> None:
        self._score_heap = None  # TODO: custom heap per game.
        self._score_tree = None  # TODO: score range structure per game.

    def top_n(self, game_id: str, n: int = 10) -> list[object]:
        # TODO(RESILIENCE): Validate game_id and clamp n to a safe maximum.
        # TODO(HEAP): Return top N scores without sorting the full dataset.
        # WARNING(SCALE): Sorting every score for every request will not scale well.
        _ = (game_id, n)
        raise NotImplementedError("Team must implement heap-based top-N ranking.")

    def player_rank(self, game_id: str, username: str) -> int | None:
        # TODO(RESILIENCE): Return None or structured errors for missing players/games.
        # TODO(RANK INDEX): Implement efficient player rank lookup.
        _ = (game_id, username)
        raise NotImplementedError("Team must implement player rank lookup.")

    def score_range(self, game_id: str, low: int, high: int) -> list[object]:
        # TODO(RESILIENCE): Validate low <= high and numeric bounds.
        # TODO(BST RANGE): Return scores in [low, high].
        # TODO(BENCHMARK): Compare BST range query against brute-force filtering.
        _ = (game_id, low, high)
        raise NotImplementedError("Team must implement score range query.")
