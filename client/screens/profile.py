from __future__ import annotations

import pygame

from client.components import draw_badge, draw_panel, draw_player_avatar, draw_text, draw_wrapped
from client.core import Palette

from .base_screen import BaseScreen


class ProfileScreen(BaseScreen):
    def enter(self) -> None:
        super().enter()
        self.player_sessions = None
        self.profile_summary = None
        self.chat_preview = None
        self.chat_session_id = ""
        self._refresh_cached_data()

    def _profile_player(self):
        return self.app.profile_player or self.app.current_player

    def _refresh_cached_data(self) -> None:
        player = self._profile_player()
        if player is None:
            return
        self.profile_summary = self.app.backend.get_cached_profile_summary(player)
        self.player_sessions = self.app.backend.get_cached_player_sessions(player.username, limit=5)
        if self.player_sessions is None and not self.app.backend.is_preload_loading(player):
            self.app.backend.start_post_login_preload(player)

    def draw(self) -> None:
        player = self._profile_player()
        if player is None:
            return
        self._refresh_cached_data()
        subtitle = "Your arcade profile, recent sessions, stats, and session chat preview."
        if self.app.profile_player is not None and self.app.profile_player != self.app.current_player:
            subtitle = "Public player profile, recent sessions, stats, and session chat preview."
        self.page_title("Player Profile", subtitle)
        left = pygame.Rect(30, 178, 480, 230)
        right = pygame.Rect(540, 178, 630, 230)
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
            ("Level", summary.get("level", player.level)),
            ("Favorite Genre", summary.get("favorite_genre", player.favorite_genre)),
            ("Total Sessions", f"{int(summary.get('games_played', player.total_sessions) or 0):,}"),
            ("Total Wins", f"{int(summary.get('wins', player.total_wins) or 0):,}"),
        ]
        for index, (label, value) in enumerate(stats):
            x = right.x + 20 + (index % 2) * 300
            y = right.y + 62 + (index // 2) * 72
            draw_text(self.app.screen, label, self.app.fonts.small, Palette.MUTED, x, y)
            draw_text(self.app.screen, str(value), self.app.fonts.subheading, Palette.TEXT, x, y + 22, max_width=260)

        history = pygame.Rect(30, 435, 560, 245)
        chat = pygame.Rect(610, 435, 560, 245)
        draw_panel(self.app.screen, history)
        draw_panel(self.app.screen, chat)
        draw_text(self.app.screen, "Recent Sessions", self.app.fonts.body, Palette.TEXT, history.x + 16, history.y + 14)
        player_sessions = self.player_sessions
        if player_sessions is None:
            draw_text(self.app.screen, "Loading recent sessions...", self.app.fonts.small, Palette.MUTED, history.x + 18, history.y + 56)
            draw_text(self.app.screen, "Loading chat preview...", self.app.fonts.small, Palette.MUTED, chat.x + 18, chat.y + 100)
            return
        for index, session in enumerate(player_sessions):
            game = self.app.backend.get_game(session.game_id)
            row = pygame.Rect(history.x + 14, history.y + 50 + index * 34, history.width - 28, 28)
            game_name = game.title if game else session.game_id
            self.draw_list_row(row, game_name, "", f"{session.result} {session.score:,} pts")
        draw_text(self.app.screen, "Session Chat Preview", self.app.fonts.body, Palette.TEXT, chat.x + 16, chat.y + 14)
        if not player_sessions:
            draw_text(self.app.screen, "No recent session chat to preview.", self.app.fonts.small, Palette.MUTED, chat.x + 18, chat.y + 100)
            return
        chat_session_id = player_sessions[0].session_id
        if self.chat_preview is None or self.chat_session_id != chat_session_id:
            self.chat_session_id = chat_session_id
            self.chat_preview = self.app.backend.get_chat_preview(chat_session_id)
        draw_wrapped(self.app.screen, f"Recent messages for session {chat_session_id}. Open a game from Browse to use the full session chat.", self.app.fonts.small, Palette.MUTED, pygame.Rect(chat.x + 16, chat.y + 45, chat.width - 32, 44), max_lines=2)
        for index, message in enumerate(self.chat_preview):
            draw_text(self.app.screen, f"[{message.timestamp}] {message.sender}", self.app.fonts.small, Palette.ACCENT, chat.x + 18, chat.y + 100 + index * 42, max_width=220)
            draw_text(self.app.screen, message.text, self.app.fonts.small, Palette.TEXT, chat.x + 250, chat.y + 100 + index * 42, max_width=290)
