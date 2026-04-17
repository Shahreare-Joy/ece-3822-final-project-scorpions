from __future__ import annotations

from dataclasses import dataclass


@dataclass
class GameSession:
    session_id: str
    game_id: str
    username: str
    result: str
    score: int
    duration_minutes: int
    played_at: str
    status: str

