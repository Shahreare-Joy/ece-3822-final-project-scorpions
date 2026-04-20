from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class Genre(str, Enum):
    ACTION = "Action"
    ADVENTURE = "Adventure"
    RACING = "Racing"
    STRATEGY = "Strategy"
    PUZZLE = "Puzzle"
    ARCADE = "Arcade"
    COOP = "Co-op"
    PLATFORMER = "Platformer"


ALL_GENRES = [genre.value for genre in Genre]


@dataclass
class Game:
    game_id: str
    title: str
    genre: str
    description: str
    creator: str
    players_now: int
    total_plays: int
    status: str
    playable: bool
    color: tuple[int, int, int]
    tags: list[str]
    release_year: int
    last_updated: str
    activity_note: str
    team_game: bool = False
    # Placeholder asset paths for future thumbnail/screenshot loading.
    # TODO(ASSETS): Replace color-card rendering with real image loading from
    # client/assets/thumbnails and client/assets/screenshots when art is ready.
    thumbnail_path: str = ""
    screenshot_path: str = ""
