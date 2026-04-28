from __future__ import annotations

import pygame

from client.components import GameCard, draw_panel, draw_text, draw_wrapped
from client.core import CONTENT_TOP, PAGE_PAD, Palette

from .base_screen import BaseScreen


class HomeScreen(BaseScreen):
    def enter(self) -> None:
        super().enter()
        # One backend function owns Home shelf labels and row contents so the
        # screen does not switch sources after login, after preload, or after
        # clicking through other screens.
        visible_rows = self.app.backend.get_home_sections(self.app.current_player)
        row_count = max(1, len(visible_rows))
        shelf_top = 206
        shelf_bottom = 744
        if row_count <= 2:
            card_h = 126
        elif row_count == 3:
            card_h = 118
        elif row_count == 4:
            card_h = 112
        elif row_count == 5:
            card_h = 88
        else:
            card_h = 68
        row_gap = int((shelf_bottom - shelf_top - card_h) / max(1, row_count - 1)) if row_count > 1 else 0
        self.row_specs = [(title, games, shelf_top + index * row_gap) for index, (title, games) in enumerate(visible_rows)]
        for _, games, y in self.row_specs:
            for index, game in enumerate(games[:5]):
                self.cards.append(GameCard((30 + index * 230, y, 218, card_h), game, self.app.open_game, self.app.fonts, compact=True))

    def draw(self) -> None:
        player = self.app.current_player
        stats = self.app.backend.get_platform_stats()
        hero = pygame.Rect(PAGE_PAD, CONTENT_TOP, 760, 82)
        draw_panel(self.app.screen, hero)
        draw_text(self.app.screen, f"Welcome back, {player.display_name if player else 'Player'}", self.app.fonts.heading, Palette.TEXT, hero.x + 20, hero.y + 14, max_width=hero.width - 40)
        draw_wrapped(self.app.screen, "A platform-style arcade home with saved sessions, catalog history, and live-feeling activity.", self.app.fonts.small, Palette.MUTED, pygame.Rect(hero.x + 22, hero.y + 48, hero.width - 44, 28), max_lines=1)

        stats_box = pygame.Rect(815, CONTENT_TOP, 355, 82)
        draw_panel(self.app.screen, stats_box)
        draw_text(self.app.screen, "Platform Snapshot", self.app.fonts.body, Palette.TEXT, stats_box.x + 16, stats_box.y + 10)
        draw_text(self.app.screen, f"{stats.players_online:,} online  |  {stats.sessions_today:,} sessions today", self.app.fonts.small, Palette.MUTED, stats_box.x + 16, stats_box.y + 38, max_width=320)
        draw_text(self.app.screen, f"{stats.registered_players:,} players  |  {stats.total_sessions:,} all-time sessions", self.app.fonts.small, Palette.MUTED, stats_box.x + 16, stats_box.y + 58, max_width=320)

        for title, _, y in self.row_specs:
            draw_text(self.app.screen, title, self.app.fonts.body, Palette.TEXT, 30, y - 24)
        for card in self.cards:
            card.draw(self.app.screen)
        self.draw_message()
