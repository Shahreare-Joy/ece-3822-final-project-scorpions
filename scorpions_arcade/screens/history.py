from __future__ import annotations

import pygame

from scorpions_arcade.components import draw_history_row, draw_panel, draw_text, draw_wrapped
from scorpions_arcade.core import Palette

from .base_screen import BaseScreen


class HistoryScreen(BaseScreen):
    def draw(self) -> None:
        self.page_title("Match History", "A history screen for recent game sessions. Filtering and analysis hooks are intentionally marked for later work.")
        panel = pygame.Rect(30, 170, 780, 510)
        notes = pygame.Rect(840, 170, 330, 510)
        draw_panel(self.app.screen, panel)
        draw_panel(self.app.screen, notes)
        draw_text(self.app.screen, "Recent Platform Sessions", self.app.fonts.subheading, Palette.TEXT, panel.x + 18, panel.y + 16)
        row_height = 48
        row_gap = 8
        row_top = panel.y + 62
        # TODO(HISTORY): Add player/date/game/result filters after the history index is implemented.
        for index, session in enumerate(self.app.backend.get_sessions(limit=8)):
            game = self.app.backend.get_game(session.game_id)
            player = self.app.backend.get_player(session.username)
            game_name = game.title if game else session.game_id
            player_name = player.display_name if player else session.username
            subtitle = f"{player_name} | {session.duration_minutes} min | {session.played_at}"
            session_value = f"{session.result} {session.score:,} pts"
            row = pygame.Rect(panel.x + 16, row_top + index * (row_height + row_gap), panel.width - 32, row_height)
            draw_history_row(self.app.screen, row, self.app.fonts, game_name, subtitle, session_value)
        draw_text(self.app.screen, "TODO Hooks", self.app.fonts.body, Palette.TEXT, notes.x + 18, notes.y + 20)
        todo = "Add player/date/game filters, connect this to a custom session list or indexed history structure, then use it for performance analysis."
        draw_wrapped(self.app.screen, todo, self.app.fonts.small, Palette.MUTED, pygame.Rect(notes.x + 18, notes.y + 58, notes.width - 36, 150), max_lines=6)

