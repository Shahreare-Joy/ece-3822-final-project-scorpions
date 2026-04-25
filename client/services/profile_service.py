from __future__ import annotations

from client.models import Player
from datastructures.hash_table import ChainedHashTable


class ProfileService:
    """Profile lookup and aggregate stat service."""

    def __init__(self, players: dict[str, Player]) -> None:
        self.players = players
        self._player_index = ChainedHashTable(max(16, len(players) * 2))
        for player in players.values():
            self._player_index.put(player.username, player)

    def get_player(self, username: str) -> Player | None:
        # TODO (DONE)(HASH TABLE): Replace dict with documented player lookup structure.
        player = self._player_index.get(username)
        return player if isinstance(player, Player) else None

    def aggregate_profile_stats(self, username: str) -> dict[str, object]:
        # TODO (DONE)(PROFILE): Aggregate available profile fields into a stable summary.
        player = self.get_player(username)
        if player is None:
            return {}
        win_rate = 0.0 if player.total_sessions == 0 else round((player.total_wins / player.total_sessions) * 100, 1)
        return {
            "games_played": player.total_sessions,
            "wins": player.total_wins,
            "win_rate": win_rate,
            "favorite_genre": player.favorite_genre,
            "level": player.level,
            "source": "indexed Player profile fields",
        }
