from __future__ import annotations

from client.models import Game


def make_game(
    game_id: str,
    title: str,
    genre: str,
    description: str,
    creator: str,
    players_now: int,
    total_plays: int,
    status: str,
    playable: bool,
    color: tuple[int, int, int],
    tags: list[str],
    release_year: int,
    last_updated: str,
    activity_note: str,
    team_game: bool = False,
    thumbnail_path: str = "",
    screenshot_path: str = "",
) -> Game:
    """Create a mock Game row; keeps mock_games.py focused on catalog records."""
    if not thumbnail_path:
        thumbnail_path = f"client/assets/thumbnails/{game_id}.png"
    if not screenshot_path:
        screenshot_path = f"client/assets/screenshots/{game_id}.png"
    return Game(
        game_id,
        title,
        genre,
        description,
        creator,
        players_now,
        total_plays,
        status,
        playable,
        color,
        tags,
        release_year,
        last_updated,
        activity_note,
        team_game,
        thumbnail_path,
        screenshot_path,
    )
