from __future__ import annotations

import pygame

from client.components import draw_badge, draw_history_row, draw_panel, draw_player_avatar, draw_text, draw_wrapped
from client.core import Palette

from .base_screen import BaseScreen


class ProfileScreen(BaseScreen):
    def enter(self) -> None:
        super().enter()
        self.player_sessions = None
        self.profile_summary = None
        self.chat_preview = None
        self.chat_message_count = 0
        self.chat_session_id = ""
        self._refresh_cached_data()

    def _profile_player(self):
        return self.app.profile_player or self.app.current_player

    def _refresh_cached_data(self) -> None:
        player = self._profile_player()
        if player is None:
            return
        self.profile_summary = self.app.backend.get_cached_profile_summary(player) or self.app.backend.get_profile_summary(player)
        self.player_sessions = self.app.backend.get_cached_player_sessions(player.username, limit=5)
        if self.player_sessions is None:
            self.player_sessions = self.app.backend.get_live_player_sessions(player.username, limit=5)
        self.chat_preview = self.app.backend.get_player_chat_messages(player.username, limit=5)
        self.chat_message_count = self.app.backend.get_player_chat_count(player.username)

    def draw(self) -> None:
        player = self._profile_player()
        if player is None:
            return
        self._refresh_cached_data()
        subtitle = "Your arcade profile, recent sessions, stats, and session chat preview."
        if self.app.profile_player is not None and self.app.profile_player != self.app.current_player:
            subtitle = "Public player profile, recent sessions, stats, and session chat preview."
        self.page_title("Player Profile", subtitle)
        left = pygame.Rect(30, 174, 500, 220)
        right = pygame.Rect(550, 174, 620, 220)
        draw_panel(self.app.screen, left)
        draw_panel(self.app.screen, right)
        avatar_center = (left.x + 70, left.y + 74)
        draw_player_avatar(self.app.screen, avatar_center, 40, player.display_name, player.avatar_id, self.app.fonts.subheading)
        text_x = left.x + 132
        draw_text(self.app.screen, player.display_name, self.app.fonts.heading, Palette.TEXT, text_x, left.y + 30, max_width=left.width - 152)
        draw_text(self.app.screen, f"@{player.username} | {player.country} | Joined {player.joined_year}", self.app.fonts.small, Palette.MUTED, text_x, left.y + 70, max_width=left.width - 152)
        draw_badge(self.app.screen, player.status, pygame.Rect(text_x, left.y + 100, 115, 28), self.app.fonts.small, Palette.SUCCESS if player.status == "Online" else Palette.WARNING)
        draw_wrapped(self.app.screen, player.bio, self.app.fonts.small, Palette.TEXT, pygame.Rect(left.x + 24, left.y + 148, left.width - 48, 58), max_lines=2)
        draw_text(self.app.screen, "Player Stats", self.app.fonts.body, Palette.TEXT, right.x + 18, right.y + 20)
        summary = self.profile_summary or {}
        stats = [
            ("Total Sessions", f"{int(summary.get('total_sessions', summary.get('games_played', player.total_sessions)) or 0):,}"),
            ("Total Score", f"{int(summary.get('total_score', 0) or 0):,}"),
            ("Best Score", f"{int(summary.get('best_score', 0) or 0):,}"),
            ("Average Score", f"{summary.get('average_score', 0)}"),
            ("Total Play Time", f"{int(summary.get('total_play_time', 0) or 0):,} min"),
            ("Messages Sent", f"{int(summary.get('messages_sent', self.chat_message_count) or 0):,}"),
        ]
        for index, (label, value) in enumerate(stats):
            x = right.x + 20 + (index % 3) * 200
            y = right.y + 58 + (index // 3) * 72
            draw_text(self.app.screen, label, self.app.fonts.small, Palette.MUTED, x, y)
            draw_text(self.app.screen, str(value), self.app.fonts.subheading, Palette.TEXT, x, y + 22, max_width=180)
        draw_text(self.app.screen, f"Favorite: {summary.get('favorite_game', 'No games yet')} | {summary.get('favorite_genre', player.favorite_genre)}", self.app.fonts.small, Palette.ACCENT, right.x + 20, right.bottom - 34, max_width=right.width - 40)

        history = pygame.Rect(30, 420, 560, 260)
        chat = pygame.Rect(610, 420, 560, 260)
        draw_panel(self.app.screen, history)
        draw_panel(self.app.screen, chat)
        draw_text(self.app.screen, "Recent Sessions", self.app.fonts.body, Palette.TEXT, history.x + 16, history.y + 14)
        player_sessions = self.player_sessions
        if player_sessions is None:
            draw_text(self.app.screen, "Loading recent sessions...", self.app.fonts.small, Palette.MUTED, history.x + 18, history.y + 56)
            return
        if not player_sessions:
            draw_wrapped(self.app.screen, "No recent sessions yet. Play Fruit Drop Rush to create the first real session.", self.app.fonts.small, Palette.MUTED, pygame.Rect(history.x + 18, history.y + 58, history.width - 36, 80), max_lines=3)
        for index, session in enumerate(player_sessions[:4]):
            game = self.app.backend.get_game(session.game_id)
            row = pygame.Rect(history.x + 14, history.y + 50 + index * 50, history.width - 28, 44)
            game_name = game.title if game else session.game_id
            subtitle = f"{session.result} | {session.duration_minutes} min | {session.played_at}"
            draw_history_row(self.app.screen, row, self.app.fonts, game_name, subtitle, f"Score: {session.score:,}")
        draw_text(self.app.screen, "Recent Chat / Messages", self.app.fonts.body, Palette.TEXT, chat.x + 16, chat.y + 14)
        draw_text(self.app.screen, f"Messages sent: {self.chat_message_count:,}", self.app.fonts.small, Palette.MUTED, chat.right - 160, chat.y + 18, max_width=140)
        if not self.chat_preview:
            draw_text(self.app.screen, "No sent chat messages yet.", self.app.fonts.small, Palette.MUTED, chat.x + 18, chat.y + 86)
            return
        for index, message in enumerate(self.chat_preview[-5:]):
            y = chat.y + 54 + index * 38
            draw_text(self.app.screen, f"{message.timestamp} | {message.session_id}", self.app.fonts.small, Palette.ACCENT, chat.x + 18, y, max_width=210)
            draw_text(self.app.screen, message.text, self.app.fonts.small, Palette.TEXT, chat.x + 236, y, max_width=300)
