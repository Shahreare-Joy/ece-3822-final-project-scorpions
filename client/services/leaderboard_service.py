"""Client leaderboard service adapter.

TODO(LEADERBOARD): Request top-N, player rank, and score ranges from
platform_server/leaderboard.py.
"""


class ClientLeaderboardService:
    def top_scores(self, game_id: str, limit: int = 10) -> list[object]:
        _ = (game_id, limit)
        return []
