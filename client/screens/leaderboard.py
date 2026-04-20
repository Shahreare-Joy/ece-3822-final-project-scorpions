from __future__ import annotations

import pygame

from client.components import Button, draw_panel, draw_text, draw_wrapped
from client.core import Palette
from client.models import Game

from .base_screen import BaseScreen


class LeaderboardScreen(BaseScreen):
    def enter(self) -> None:
        super().enter()
        team_games = [game for game in self.app.backend.get_games() if game.team_game]
        for index, game in enumerate(team_games[:4]):
            self.buttons.append(Button((30 + index * 220, 165, 205, 36), game.title, lambda selected=game: self.select_game(selected), self.app.fonts.small, selected=self.app.current_game == game))
        if self.app.current_game is None:
            self.app.current_game = self.app.backend.get_game("scorpions-arena")

    def select_game(self, game: Game) -> None:
        self.app.current_game = game
        self.enter()

    def draw(self) -> None:
        game = self.app.current_game or self.app.backend.get_game("scorpions-arena")
        self.page_title("Leaderboards", "Leaderboard data is mocked. Later, connect ranking to custom sorting, heap, BST, or indexed structures.")
        for button in self.buttons:
            button.draw(self.app.screen)
        panel = pygame.Rect(30, 225, 760, 455)
        detail = pygame.Rect(820, 225, 350, 455)
        draw_panel(self.app.screen, panel)
        draw_panel(self.app.screen, detail)
        draw_text(self.app.screen, f"{game.title if game else 'Game'} Top Scores", self.app.fonts.subheading, Palette.TEXT, panel.x + 18, panel.y + 16)
        if game:
            # TODO(LEADERBOARD): Final ranking/tie-breaking belongs in LeaderboardService.
            for index, entry in enumerate(self.app.backend.get_leaderboard(game.game_id, 10)):
                row = pygame.Rect(panel.x + 16, panel.y + 60 + index * 36, panel.width - 32, 30)
                self.draw_list_row(row, f"#{entry.rank} {entry.display_name}", f"{entry.wins} wins", f"{entry.score:,} pts")
            draw_text(self.app.screen, "Data Structure Hook", self.app.fonts.body, Palette.TEXT, detail.x + 18, detail.y + 18)
            draw_wrapped(self.app.screen, "TODO: replace generated leaderboard rows with ranking logic from your chosen custom data structure and sorting analysis.", self.app.fonts.small, Palette.MUTED, pygame.Rect(detail.x + 18, detail.y + 58, detail.width - 36, 120), max_lines=5)
            draw_text(self.app.screen, "Selected Game", self.app.fonts.body, Palette.TEXT, detail.x + 18, detail.y + 210)
            draw_wrapped(self.app.screen, f"{game.title} | {game.genre} | {game.status}", self.app.fonts.small, Palette.ACCENT, pygame.Rect(detail.x + 18, detail.y + 244, detail.width - 36, 60), max_lines=3)

