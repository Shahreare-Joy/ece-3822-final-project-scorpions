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
        self.chat_scroll_offset = 0
        self.chat_max_scroll = 0
        self.sessions = []
        self.chat_messages = []
        self.message_count = 0

    def enter(self) -> None:
        super().enter()
        self._refresh_cached_sessions()
        self._clamp_scroll()

    def _refresh_cached_sessions(self) -> None:
        player = self.app.current_player
        if player is None:
            self.sessions = []
            self.chat_messages = []
            self.message_count = 0
            return
        sessions = self.app.backend.get_cached_player_sessions(player.username, limit=80)
        if sessions is None:
            sessions = self.app.backend.get_live_player_sessions(player.username, limit=80)
        self.sessions = sessions
        self.chat_messages = self.app.backend.get_player_chat_messages(player.username, limit=80)
        self.message_count = self.app.backend.get_player_chat_count(player.username)

    def _clamp_scroll(self) -> None:
        row_height = 48
        row_gap = 8
        viewport_height = 434
        content_height = len(self.sessions) * (row_height + row_gap)
        self.max_scroll = max(0, content_height - viewport_height)
        self.scroll_offset = max(0, min(self.scroll_offset, self.max_scroll))
        chat_row_height = 50
        chat_viewport_height = 382
        chat_content_height = len(self.chat_messages) * chat_row_height
        self.chat_max_scroll = max(0, chat_content_height - chat_viewport_height)
        self.chat_scroll_offset = max(0, min(self.chat_scroll_offset, self.chat_max_scroll))

    def _scroll(self, amount: int) -> None:
        old_offset = self.scroll_offset
        self.scroll_offset = max(0, min(self.scroll_offset + amount, self.max_scroll))
        if self.scroll_offset != old_offset:
            self._clamp_scroll()

    def _scroll_chat(self, amount: int) -> None:
        old_offset = self.chat_scroll_offset
        self.chat_scroll_offset = max(0, min(self.chat_scroll_offset + amount, self.chat_max_scroll))
        if self.chat_scroll_offset != old_offset:
            self._clamp_scroll()

    def handle_event(self, event: pygame.event.Event) -> None:
        super().handle_event(event)
        if event.type == pygame.MOUSEWHEEL:
            if pygame.mouse.get_pos()[0] >= 820:
                self._scroll_chat(-event.y * 72)
            else:
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
        self._refresh_cached_sessions()
        self._clamp_scroll()
        player_name = self.app.current_player.display_name if self.app.current_player else "Player"
        self.page_title("Match History", f"{player_name}'s real session history and sent chat messages.")
        panel = pygame.Rect(30, 170, 780, 510)
        notes = pygame.Rect(840, 170, 330, 510)
        draw_panel(self.app.screen, panel)
        draw_panel(self.app.screen, notes)
        draw_text(self.app.screen, "Your Recent Sessions", self.app.fonts.subheading, Palette.TEXT, panel.x + 18, panel.y + 16)
        if self.max_scroll:
            draw_text(self.app.screen, "Mouse wheel / Up / Down scrolls", self.app.fonts.tiny, Palette.MUTED, panel.right - 194, panel.y + 24, max_width=170)
        row_height = 48
        row_gap = 8
        row_top = panel.y + 62
        viewport = pygame.Rect(panel.x + 12, row_top - 4, panel.width - 24, panel.bottom - row_top - 14)
        old_clip = self.app.screen.get_clip()
        self.app.screen.set_clip(viewport)
        if not self.sessions:
            draw_text(self.app.screen, "No sessions yet. Play a game to create your first history row.", self.app.fonts.small, Palette.MUTED, panel.x + 18, row_top + 10)
        # TODO (DONE)(HISTORY): HistoryService now exposes player/game/result/date query helpers.
        for index, session in enumerate(self.sessions):
            game = self.app.backend.get_game(session.game_id)
            player = self.app.backend.get_player(session.username)
            game_name = game.title if game else session.game_id
            player_name = player.display_name if player else session.username
            subtitle = f"{player_name} | {session.duration_minutes} min | {session.played_at}"
            session_value = f"Score: {session.score:,} | {session.result}"
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
        draw_text(self.app.screen, "Chat Message History", self.app.fonts.body, Palette.TEXT, notes.x + 18, notes.y + 20)
        draw_text(self.app.screen, f"Messages sent: {self.message_count:,}", self.app.fonts.small, Palette.MUTED, notes.x + 18, notes.y + 52)
        if self.chat_max_scroll:
            draw_text(self.app.screen, "Mouse wheel scrolls", self.app.fonts.tiny, Palette.MUTED, notes.right - 142, notes.y + 54, max_width=120)
        chat_top = notes.y + 86
        chat_viewport = pygame.Rect(notes.x + 14, chat_top, notes.width - 28, notes.bottom - chat_top - 16)
        old_clip = self.app.screen.get_clip()
        self.app.screen.set_clip(chat_viewport)
        if not self.chat_messages:
            draw_wrapped(self.app.screen, "No sent chat messages yet. Messages you send during game sessions will appear here.", self.app.fonts.small, Palette.MUTED, pygame.Rect(chat_viewport.x + 4, chat_viewport.y + 6, chat_viewport.width - 8, 90), max_lines=4)
        for index, message in enumerate(self.chat_messages):
            y = chat_top + index * 50 - self.chat_scroll_offset
            row = pygame.Rect(notes.x + 14, y, notes.width - 28, 42)
            if row.bottom < chat_viewport.top or row.top > chat_viewport.bottom:
                continue
            pygame.draw.rect(self.app.screen, Palette.PANEL_DARK, row, border_radius=6)
            pygame.draw.rect(self.app.screen, Palette.BORDER, row, width=1, border_radius=6)
            draw_text(self.app.screen, f"{message.timestamp} | {message.session_id}", self.app.fonts.tiny, Palette.ACCENT, row.x + 10, row.y + 6, max_width=row.width - 20)
            draw_text(self.app.screen, message.text, self.app.fonts.small, Palette.TEXT, row.x + 10, row.y + 22, max_width=row.width - 20)
        self.app.screen.set_clip(old_clip)
