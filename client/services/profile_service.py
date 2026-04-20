from __future__ import annotations

from client.models import Player


class ProfileService:
    """Temporary profile lookup service.

    Requirement target: fast profile lookup plus aggregate stats from 100,000+
    sessions, such as games played, win rate, play time, and score history.

    TODO(PROFILE/HASH): Replace mock dict with the team's documented player
    lookup/index. TODO(PROFILE AGGREGATION): Compute derived stats from the
    final history index instead of hardcoding them in Player rows.
    """

    def __init__(self, players: dict[str, Player]) -> None:
        self.players = players

    def get_player(self, username: str) -> Player | None:
        # TODO(HASH TABLE): Replace dict with your documented player lookup structure.
        return self.players.get(username)

    def aggregate_profile_stats(self, username: str) -> dict[str, object]:
        # MOCK AGGREGATION WARNING:
        # These values come from Player mock fields. The final profile should
        # aggregate from indexed session/history records.
        # TODO(PROFILE): Aggregate from final session-history structures:
        # games_played, total_play_time, win_rate, best_score, score_history.
        player = self.get_player(username)
        if player is None:
            return {}
        return {
            "games_played": player.total_sessions,
            "wins": player.total_wins,
            "favorite_genre": player.favorite_genre,
            "source": "temporary Player mock fields",
        }
