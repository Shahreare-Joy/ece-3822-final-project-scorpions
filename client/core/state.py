from __future__ import annotations

from dataclasses import dataclass

from client.models import Game, Player

from .router import ScreenName
from .theme import Palette


@dataclass
class AppState:
    """Mutable UI state shared by screens.

    Keep only lightweight client state here. Backend data, mock records, and
    future custom data structures belong in services/data/placeholders.
    """

    running: bool = True
    current_player: Player | None = None
    profile_player: Player | None = None
    current_game: Game | None = None
    current_screen: ScreenName = ScreenName.WELCOME
    message: str = ""
    message_color: tuple[int, int, int] = Palette.MUTED
