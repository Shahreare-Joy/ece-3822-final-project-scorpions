from __future__ import annotations

from dataclasses import dataclass


@dataclass
class Player:
    username: str
    display_name: str
    password: str
    country: str
    joined_year: int
    level: int
    favorite_genre: str
    total_sessions: int
    total_wins: int
    status: str
    bio: str
    avatar_id: str = ""
