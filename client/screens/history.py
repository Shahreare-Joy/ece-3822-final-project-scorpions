from __future__ import annotations

import pygame

from client.components import draw_history_row, draw_panel, draw_text, draw_wrapped
from client.core import Palette

from .base_screen import BaseScreen


class HistoryScreen(BaseScreen):
    def __init__(self, app) -> None:
        super().__init__(app)
        self.scroll_offset = 0
        self.max_scroll = 0
        self.sessions = []

    def enter(self) -> None:
        super().enter()
        self._refresh_cached_sessions()
        self._clamp_scroll()

    def _refresh_cached_sessions(self) -> None:
        sessions = self.app.backend.get_cached_history_sessions(limit=80)
        if sessions is not None:
            self.sessions = sessions
            return
        if self.app.current_player is not None:
            self.app.backend.start_post_login_preload(self.app.current_player)

    def _clamp_scroll(self) -> None:
        row_height = 48
        row_gap = 8
        viewport_height = 434
        content_height = len(self.sessions) * (row_height + row_gap)
        self.max_scroll = max(0, content_height - viewport_height)
        self.scroll_offset = max(0, min(self.scroll_offset, self.max_scroll))

    def _scroll(self, amount: int) -> None:
        old_offset = self.scroll_offset
        self.scroll_offset = max(0, min(self.scroll_offset + amount, self.max_scroll))
        if self.scroll_offset != old_offset:
            self._clamp_scroll()

    def handle_event(self, event: pygame.event.Event) -> None:
        super().handle_event(event)
        if event.type == pygame.MOUSEWHEEL:
            self._scroll(-event.y * 72)
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_DOWN:
                self._scroll(72)
            elif event.key == pygame.K_UP:
                self._scroll(-72)
            elif event.key == pygame.K_PAGEDOWN:
                self._scroll(280)
            elif event.key == pygame.K_PAGEUP:
                self._scroll(-280)

    def draw(self) -> None:
        if not self.sessions:
            self._refresh_cached_sessions()
            self._clamp_scroll()
        self.page_title("Match History", "Recent game sessions with indexed history hooks ready for larger datasets.")
        panel = pygame.Rect(30, 170, 780, 510)
        notes = pygame.Rect(840, 170, 330, 510)
        draw_panel(self.app.screen, panel)
        draw_panel(self.app.screen, notes)
        draw_text(self.app.screen, "Recent Platform Sessions", self.app.fonts.subheading, Palette.TEXT, panel.x + 18, panel.y + 16)
        if self.max_scroll:
            draw_text(self.app.screen, "Mouse wheel / Up / Down scrolls", self.app.fonts.tiny, Palette.MUTED, panel.right - 194, panel.y + 24, max_width=170)
        row_height = 48
        row_gap = 8
        row_top = panel.y + 62
        viewport = pygame.Rect(panel.x + 12, row_top - 4, panel.width - 24, panel.bottom - row_top - 14)
        old_clip = self.app.screen.get_clip()
        self.app.screen.set_clip(viewport)
        if not self.sessions:
            draw_text(self.app.screen, "Loading session history...", self.app.fonts.small, Palette.MUTED, panel.x + 18, row_top + 10)
        # TODO (DONE)(HISTORY): HistoryService now exposes player/game/result/date query helpers.
        for index, session in enumerate(self.sessions):
            game = self.app.backend.get_game(session.game_id)
            player = self.app.backend.get_player(session.username)
            game_name = game.title if game else session.game_id
            player_name = player.display_name if player else session.username
            subtitle = f"{player_name} | {session.duration_minutes} min | {session.played_at}"
            session_value = f"{session.result} {session.score:,} pts"
            y = row_top + index * (row_height + row_gap) - self.scroll_offset
            row = pygame.Rect(panel.x + 16, y, panel.width - 32, row_height)
            if row.bottom < viewport.top or row.top > viewport.bottom:
                continue
            draw_history_row(self.app.screen, row, self.app.fonts, game_name, subtitle, session_value)
        self.app.screen.set_clip(old_clip)
        if self.max_scroll:
            track = pygame.Rect(panel.right - 10, row_top, 6, panel.bottom - row_top - 18)
            pygame.draw.rect(self.app.screen, Palette.PANEL_DARK, track, border_radius=3)
            thumb_h = max(32, int(track.height * track.height / (track.height + self.max_scroll)))
            thumb_y = track.y + int((track.height - thumb_h) * (self.scroll_offset / self.max_scroll))
            pygame.draw.rect(self.app.screen, Palette.ACCENT, pygame.Rect(track.x, thumb_y, track.width, thumb_h), border_radius=3)
        draw_text(self.app.screen, "History Indexes", self.app.fonts.body, Palette.TEXT, notes.x + 18, notes.y + 20)
        note = "Player, game, result, and date-range query paths are available in the history service. Use mouse wheel, arrow keys, or page keys to scroll the session list."
        draw_wrapped(self.app.screen, note, self.app.fonts.small, Palette.MUTED, pygame.Rect(notes.x + 18, notes.y + 58, notes.width - 36, 150), max_lines=6)
