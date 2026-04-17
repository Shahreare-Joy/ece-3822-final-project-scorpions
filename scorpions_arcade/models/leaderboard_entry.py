from __future__ import annotations

from dataclasses import dataclass


@dataclass
class LeaderboardEntry:
    game_id: str
    username: str
    display_name: str
    score: int
    wins: int
    rank: int

