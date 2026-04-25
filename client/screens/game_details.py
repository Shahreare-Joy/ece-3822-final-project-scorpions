from __future__ import annotations

import pygame

from client.components import Button, draw_badge, draw_list_row, draw_panel, draw_text, draw_wrapped, load_image
from client.core import Palette, ScreenName

from .base_screen import BaseScreen


class GameDetailsScreen(BaseScreen):
    def enter(self) -> None:
        super().enter()
        if self.app.current_game is None:
            self.app.current_game = self.app.backend.get_game("scorpions-arena")
        self.buttons = [
            Button((728, 414, 198, 38), "Play / Launch", self.play_game, self.app.fonts.button, bg=Palette.ACCENT, hover=Palette.ACCENT_HOVER),
            Button((946, 414, 176, 38), "Back to Browse", lambda: self.app.navigate(ScreenName.BROWSE), self.app.fonts.button),
            Button((728, 462, 394, 34), "Open Full Leaderboard", lambda: self.app.navigate(ScreenName.LEADERBOARD), self.app.fonts.button),
        ]

    def play_game(self) -> None:
        game = self.app.current_game
        if game:
            self.app.navigate(ScreenName.SESSION_CHAT, "Session lobby opened. Chat is available before and after launch.", Palette.SUCCESS)

    def draw(self) -> None:
        game = self.app.current_game or self.app.backend.get_game("scorpions-arena")
        if game is None:
            return
        self.page_title("Game Details", "Every game has a full catalog page with status, activity, leaderboard preview, and launch options.")
        art = pygame.Rect(30, 154, 640, 246)
        art_image = load_image(game.thumbnail_path, (art.width, art.height))
        if art_image is not None:
            self.app.screen.blit(art_image, art)
        else:
            pygame.draw.rect(self.app.screen, game.color, art, border_radius=8)
        pygame.draw.rect(self.app.screen, Palette.BORDER, art, width=2, border_radius=8)
        if art_image is None:
            preview = pygame.Rect(art.x + 18, art.y + 18, art.width - 36, 118)
            pygame.draw.rect(self.app.screen, tuple(max(0, value - 24) for value in game.color), preview, border_radius=8)
            pygame.draw.rect(self.app.screen, Palette.BORDER, preview, width=1, border_radius=8)
            draw_text(self.app.screen, "THUMBNAIL / GAME ART", self.app.fonts.tiny, Palette.TEXT, preview.x + 16, preview.y + 12)
            draw_wrapped(self.app.screen, "Season preview art and screenshot area for the selected arcade game.", self.app.fonts.small, Palette.TEXT, pygame.Rect(preview.x + 16, preview.y + 42, preview.width - 32, 54), max_lines=2)
        overlay = pygame.Surface((art.width, 92), pygame.SRCALPHA)
        overlay.fill((12, 16, 24, 185))
        self.app.screen.blit(overlay, (art.x, art.bottom - 92))
        draw_text(self.app.screen, game.title, self.app.fonts.heading, Palette.TEXT, art.x + 22, 300, max_width=art.width - 44)
        draw_text(self.app.screen, f"Last updated: {game.last_updated}", self.app.fonts.small, Palette.TEXT, art.x + 24, art.bottom - 62, max_width=art.width - 220)
        draw_text(self.app.screen, game.activity_note, self.app.fonts.small, Palette.TEXT, art.x + 24, art.bottom - 38, max_width=art.width - 220)
        draw_badge(self.app.screen, "PLAYABLE NOW" if game.playable else "NOT CONNECTED", pygame.Rect(art.right - 166, art.bottom - 44, 140, 28), self.app.fonts.small, Palette.SUCCESS if game.playable else Palette.WARNING)

        panel = pygame.Rect(700, 154, 470, 216)
        draw_panel(self.app.screen, panel)
        draw_text(self.app.screen, game.title, self.app.fonts.subheading, Palette.TEXT, panel.x + 22, panel.y + 18, max_width=panel.width - 44)
        draw_text(self.app.screen, f"Creator: {game.creator}", self.app.fonts.small, Palette.ACCENT, panel.x + 22, panel.y + 50, max_width=panel.width - 44)
        draw_text(self.app.screen, f"Genre: {game.genre} | Released: {game.release_year}", self.app.fonts.small, Palette.MUTED, panel.x + 22, panel.y + 74, max_width=panel.width - 44)
        draw_wrapped(self.app.screen, game.description, self.app.fonts.small, Palette.MUTED, pygame.Rect(panel.x + 22, panel.y + 105, panel.width - 44, 62), max_lines=3)
        stat_y = panel.y + 172
        draw_text(self.app.screen, f"{game.players_now:,}", self.app.fonts.body, Palette.TEXT, panel.x + 22, stat_y)
        draw_text(self.app.screen, "playing", self.app.fonts.tiny, Palette.MUTED, panel.x + 22, stat_y + 24)
        draw_text(self.app.screen, f"{game.total_plays:,}", self.app.fonts.body, Palette.TEXT, panel.x + 172, stat_y, max_width=130)
        draw_text(self.app.screen, "total plays", self.app.fonts.tiny, Palette.MUTED, panel.x + 172, stat_y + 24)
        draw_text(self.app.screen, game.status, self.app.fonts.body, Palette.WARNING if not game.playable else Palette.SUCCESS, panel.x + 330, stat_y, max_width=118)
        draw_text(self.app.screen, "status", self.app.fonts.tiny, Palette.MUTED, panel.x + 330, stat_y + 24)

        action_panel = pygame.Rect(700, 382, 470, 124)
        draw_panel(self.app.screen, action_panel, Palette.PANEL_DARK, Palette.BORDER, radius=8, width=1)
        draw_text(self.app.screen, "Actions", self.app.fonts.small, Palette.MUTED, action_panel.x + 22, action_panel.y + 14)
        for button in self.buttons:
            button.draw(self.app.screen)

        board = pygame.Rect(30, 526, 555, 170)
        activity = pygame.Rect(615, 526, 555, 170)
        draw_panel(self.app.screen, board)
        draw_panel(self.app.screen, activity)
        draw_text(self.app.screen, "Leaderboard Preview", self.app.fonts.body, Palette.TEXT, board.x + 16, board.y + 14)
        for index, entry in enumerate(self.app.backend.get_leaderboard(game.game_id, 5)):
            row = pygame.Rect(board.x + 14, board.y + 48 + index * 24, board.width - 28, 22)
            draw_list_row(self.app.screen, row, self.app.fonts, f"#{entry.rank} {entry.display_name}", f"{entry.score:,} pts", right_color=Palette.ACCENT)
        draw_text(self.app.screen, "Recent Activity / Sessions", self.app.fonts.body, Palette.TEXT, activity.x + 16, activity.y + 14)
        sessions = self.app.backend.get_sessions(game_id=game.game_id, limit=5)
        if not sessions:
            draw_wrapped(self.app.screen, "No recent public sessions yet. Check back after this game receives live match activity.", self.app.fonts.small, Palette.MUTED, pygame.Rect(activity.x + 18, activity.y + 54, activity.width - 36, 80))
        for index, session in enumerate(sessions):
            player = self.app.backend.get_player(session.username)
            name = player.display_name if player else session.username
            row = pygame.Rect(activity.x + 14, activity.y + 46 + index * 24, activity.width - 28, 24)
            draw_list_row(self.app.screen, row, self.app.fonts, name, f"{session.result} {session.score:,} pts", right_color=Palette.ACCENT)
        self.draw_message(724)
