from __future__ import annotations

import pygame

from client.components import draw_badge, draw_panel, draw_player_avatar, draw_text, draw_wrapped
from client.core import Palette

from .base_screen import BaseScreen


class ProfileScreen(BaseScreen):
    def draw(self) -> None:
        player = self.app.profile_player or self.app.current_player
        if player is None:
            return
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
        stats = [("Level", player.level), ("Favorite Genre", player.favorite_genre), ("Total Sessions", f"{player.total_sessions:,}"), ("Total Wins", f"{player.total_wins:,}")]
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
        # TODO(HISTORY): Replace this mock lookup with an indexed player-session query.
        player_sessions = self.app.backend.get_sessions(username=player.username, limit=5)
        for index, session in enumerate(player_sessions):
            game = self.app.backend.get_game(session.game_id)
            row = pygame.Rect(history.x + 14, history.y + 50 + index * 34, history.width - 28, 28)
            game_name = game.title if game else session.game_id
            self.draw_list_row(row, game_name, "", f"{session.result} {session.score:,} pts")
        chat_session_id = player_sessions[0].session_id if player_sessions else "global"
        draw_text(self.app.screen, "Session Chat Preview", self.app.fonts.body, Palette.TEXT, chat.x + 16, chat.y + 14)
        draw_wrapped(self.app.screen, f"Recent messages for session {chat_session_id}. Open a game from Browse to use the full session chat.", self.app.fonts.small, Palette.MUTED, pygame.Rect(chat.x + 16, chat.y + 45, chat.width - 32, 44), max_lines=2)
        for index, message in enumerate(self.app.backend.get_chat_preview(chat_session_id)):
            draw_text(self.app.screen, f"[{message.timestamp}] {message.sender}", self.app.fonts.small, Palette.ACCENT, chat.x + 18, chat.y + 100 + index * 42, max_width=220)
            draw_text(self.app.screen, message.text, self.app.fonts.small, Palette.TEXT, chat.x + 250, chat.y + 100 + index * 42, max_width=290)
