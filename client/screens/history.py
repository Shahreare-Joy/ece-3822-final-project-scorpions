from __future__ import annotations

import pygame

from client.components import draw_history_row, draw_panel, draw_text, draw_wrapped
from client.core import Palette

from .base_screen import BaseScreen


class HistoryScreen(BaseScreen):
    def draw(self) -> None:
        self.page_title("Match History", "Recent game sessions with indexed history hooks ready for larger datasets.")
        panel = pygame.Rect(30, 170, 780, 510)
        notes = pygame.Rect(840, 170, 330, 510)
        draw_panel(self.app.screen, panel)
        draw_panel(self.app.screen, notes)
        draw_text(self.app.screen, "Recent Platform Sessions", self.app.fonts.subheading, Palette.TEXT, panel.x + 18, panel.y + 16)
        row_height = 48
        row_gap = 8
        row_top = panel.y + 62
        # TODO (DONE)(HISTORY): HistoryService now exposes player/game/result/date query helpers.
        for index, session in enumerate(self.app.backend.get_sessions(limit=8)):
            game = self.app.backend.get_game(session.game_id)
            player = self.app.backend.get_player(session.username)
            game_name = game.title if game else session.game_id
            player_name = player.display_name if player else session.username
            subtitle = f"{player_name} | {session.duration_minutes} min | {session.played_at}"
            session_value = f"{session.result} {session.score:,} pts"
            row = pygame.Rect(panel.x + 16, row_top + index * (row_height + row_gap), panel.width - 32, row_height)
            draw_history_row(self.app.screen, row, self.app.fonts, game_name, subtitle, session_value)
        draw_text(self.app.screen, "History Indexes", self.app.fonts.body, Palette.TEXT, notes.x + 18, notes.y + 20)
        note = "Player, game, result, and date-range query paths are available in the history service. Benchmark scripts compare indexed lookups against brute force."
        draw_wrapped(self.app.screen, note, self.app.fonts.small, Palette.MUTED, pygame.Rect(notes.x + 18, notes.y + 58, notes.width - 36, 150), max_lines=6)
