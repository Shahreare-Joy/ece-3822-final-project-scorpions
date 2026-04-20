from __future__ import annotations

from dataclasses import dataclass

from .game import Game
from .player import Player


@dataclass
class PlatformStats:
    players_online: int
    games_active: int
    sessions_today: int
    total_sessions: int
    registered_players: int


@dataclass
class HomeRows:
    continue_playing: list[Game]
    recently_played: list[Game]
    popular_now: list[Game]
    recommended: list[Game]
    featured: list[Game]


@dataclass
class AuthResult:
    success: bool
    message: str
    player: Player | None = None

