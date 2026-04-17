from __future__ import annotations

import pygame

from scorpions_arcade.components import Button, GameCard, draw_panel, draw_text
from scorpions_arcade.core import Palette
from scorpions_arcade.models import ALL_GENRES

from .base_screen import BaseScreen


class BrowseScreen(BaseScreen):
    def __init__(self, app) -> None:
        super().__init__(app)
        self.selected_genre = "All"

    def enter(self) -> None:
        super().enter()
        # TODO(CATALOG INDEX): Later, read counts from a genre index instead of scanning.
        genres = ["All"] + ALL_GENRES
        all_games = self.app.backend.get_games()
        self.genre_counts = {"All": len(all_games)}
        for genre in ALL_GENRES:
            self.genre_counts[genre] = len([game for game in all_games if game.genre == genre])
        for index, genre in enumerate(genres):
            row = index // 6
            col = index % 6
            label = f"{genre} ({self.genre_counts[genre]})"
            self.buttons.append(Button((34 + col * 128, 182 + row * 42, 118, 34), label, lambda value=genre: self.set_genre(value), self.app.fonts.small, selected=self.selected_genre == genre))
        games = self.app.backend.filter_games(self.selected_genre)
        for index, game in enumerate(games[:15]):
            row = index // 5
            col = index % 5
            self.cards.append(GameCard((30 + col * 230, 312 + row * 126, 218, 112), game, self.app.open_game, self.app.fonts))

    def set_genre(self, genre: str) -> None:
        self.selected_genre = genre
        self.enter()
        self.app.show_message(f"Showing {genre} games." if genre != "All" else "Showing the full arcade catalog.", Palette.MUTED)

    def draw(self) -> None:
        self.page_title("Browse Games", "Filter by genre and open a detail page. The catalog is mock data, but the UI flow is final-project ready.")
        filter_panel = pygame.Rect(30, 152, 792, 116)
        draw_panel(self.app.screen, filter_panel, Palette.PANEL_DARK, Palette.BORDER, radius=8, width=1)
        draw_text(self.app.screen, "Genre Filters", self.app.fonts.body, Palette.TEXT, filter_panel.x + 14, filter_panel.y + 12)
        draw_text(self.app.screen, f"Selected: {self.selected_genre}", self.app.fonts.small, Palette.ACCENT, filter_panel.x + 170, filter_panel.y + 16)
        count = len(self.app.backend.filter_games(self.selected_genre))
        summary = pygame.Rect(850, 152, 320, 116)
        draw_panel(self.app.screen, summary, Palette.PANEL_DARK, Palette.BORDER, radius=8, width=1)
        draw_text(self.app.screen, "Catalog Snapshot", self.app.fonts.body, Palette.TEXT, summary.x + 16, summary.y + 12)
        draw_text(self.app.screen, f"{count} matching games", self.app.fonts.small, Palette.ACCENT, summary.x + 16, summary.y + 44)
        draw_text(self.app.screen, f"{len(self.app.backend.get_games())} total mock catalog entries", self.app.fonts.small, Palette.MUTED, summary.x + 16, summary.y + 68)
        draw_text(self.app.screen, "15 shown per page prototype", self.app.fonts.small, Palette.MUTED, summary.x + 16, summary.y + 90)
        for button in self.buttons:
            button.draw(self.app.screen)
        draw_text(self.app.screen, "Games", self.app.fonts.body, Palette.TEXT, 30, 282)
        for card in self.cards:
            card.draw(self.app.screen)
        self.draw_message()

