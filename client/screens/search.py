from __future__ import annotations

import pygame

from client.components import Button, InputBox, draw_panel, draw_text, draw_wrapped
from client.core import Palette

from .base_screen import BaseScreen


class SearchPlayersScreen(BaseScreen):
    RESULT_LIMIT = 25
    VISIBLE_ROWS = 12

    def enter(self) -> None:
        super().enter()
        old_text = getattr(self, "query_box", None).text if hasattr(self, "query_box") else ""
        self.query_box = InputBox((30, 165, 360, 44), "Search username, display name, or genre", self.app.fonts.body)
        self.query_box.text = old_text
        self.query_box.active = True
        self.inputs = [self.query_box]
        self.buttons = [Button((410, 165, 110, 44), "Search", self.run_search, self.app.fonts.button, bg=Palette.ACCENT, hover=Palette.ACCENT_HOVER)]
        self.results = self.app.backend.search_players(self.query_box.text, self.RESULT_LIMIT)
        self.result_rows: list[tuple[pygame.Rect, object]] = []

    def run_search(self) -> None:
        # TODO (DONE)(SEARCH): SearchService uses indexed username/autocomplete lookup.
        self.results = self.app.backend.search_players(self.query_box.text, self.RESULT_LIMIT)
        self.app.show_message(f"Showing top {len(self.results)} player result(s) from the loaded dataset.", Palette.MUTED)

    def handle_event(self, event: pygame.event.Event) -> None:
        super().handle_event(event)
        result = self.query_box.handle_event(event)
        if result == "enter":
            self.run_search()
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            for row, player in getattr(self, "result_rows", []):
                if row.collidepoint(event.pos):
                    self.app.open_player_profile(player)
                    return

    def draw(self) -> None:
        self.page_title("Search Players", "Search the loaded player dataset by username or display name.")
        self.query_box.draw(self.app.screen)
        for button in self.buttons:
            button.draw(self.app.screen)
        panel = pygame.Rect(30, 240, 780, 440)
        notes = pygame.Rect(840, 240, 330, 440)
        draw_panel(self.app.screen, panel)
        draw_panel(self.app.screen, notes)
        draw_text(self.app.screen, "Player Results", self.app.fonts.subheading, Palette.TEXT, panel.x + 18, panel.y + 16)
        visible = self.results[: self.VISIBLE_ROWS]
        self.result_rows = []
        draw_text(self.app.screen, f"Showing {len(visible)} visible of top {len(self.results)} matches. Refine search for narrower results.", self.app.fonts.tiny, Palette.MUTED, panel.x + 260, panel.y + 24, max_width=480)
        for index, player in enumerate(visible):
            row = pygame.Rect(panel.x + 16, panel.y + 60 + index * 31, panel.width - 32, 28)
            self.result_rows.append((row, player))
            self.draw_list_row(row, player.display_name, f"@{player.username} | {player.favorite_genre} | {player.status}", f"Lv {player.level}", Palette.SUCCESS if player.status == "Online" else Palette.ACCENT)
        draw_text(self.app.screen, "Search Coverage", self.app.fonts.body, Palette.TEXT, notes.x + 18, notes.y + 20)
        draw_wrapped(self.app.screen, "Search includes class accounts, saved local accounts, and generated platform player records. Click a player row to open that profile.", self.app.fonts.small, Palette.MUTED, pygame.Rect(notes.x + 18, notes.y + 58, notes.width - 36, 170), max_lines=7)
