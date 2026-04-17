from __future__ import annotations

from scorpions_arcade.models import Game


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
) -> Game:
    """Create a mock Game row; keeps mock_games.py focused on catalog records."""
    return Game(game_id, title, genre, description, creator, players_now, total_plays, status, playable, color, tags, release_year, last_updated, activity_note, team_game)

