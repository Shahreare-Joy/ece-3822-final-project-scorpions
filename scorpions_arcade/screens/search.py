from __future__ import annotations

import pygame

from scorpions_arcade.components import Button, InputBox, draw_panel, draw_text, draw_wrapped
from scorpions_arcade.core import Palette

from .base_screen import BaseScreen


class SearchPlayersScreen(BaseScreen):
    def enter(self) -> None:
        super().enter()
        old_text = getattr(self, "query_box", None).text if hasattr(self, "query_box") else ""
        self.query_box = InputBox((30, 165, 360, 44), "Search username, display name, or genre", self.app.fonts.body)
        self.query_box.text = old_text
        self.query_box.active = True
        self.inputs = [self.query_box]
        self.buttons = [Button((410, 165, 110, 44), "Search", self.run_search, self.app.fonts.button, bg=Palette.ACCENT, hover=Palette.ACCENT_HOVER)]
        self.results = self.app.backend.search_players(self.query_box.text)

    def run_search(self) -> None:
        # TODO(SEARCH): Replace temporary scan with trie/hash/BST search.
        self.results = self.app.backend.search_players(self.query_box.text)
        self.app.show_message(f"{len(self.results)} player result(s).", Palette.MUTED)

    def handle_event(self, event: pygame.event.Event) -> None:
        super().handle_event(event)
        result = self.query_box.handle_event(event)
        if result == "enter":
            self.run_search()

    def draw(self) -> None:
        self.page_title("Search Players", "Temporary search scans mock players. Later, connect this screen to a trie, hash table, or BST.")
        self.query_box.draw(self.app.screen)
        for button in self.buttons:
            button.draw(self.app.screen)
        panel = pygame.Rect(30, 240, 780, 440)
        notes = pygame.Rect(840, 240, 330, 440)
        draw_panel(self.app.screen, panel)
        draw_panel(self.app.screen, notes)
        draw_text(self.app.screen, "Player Results", self.app.fonts.subheading, Palette.TEXT, panel.x + 18, panel.y + 16)
        for index, player in enumerate(self.results[:8]):
            row = pygame.Rect(panel.x + 16, panel.y + 60 + index * 44, panel.width - 32, 36)
            self.draw_list_row(row, player.display_name, f"@{player.username} | {player.favorite_genre} | {player.status}", f"Lv {player.level}", Palette.SUCCESS if player.status == "Online" else Palette.ACCENT)
        draw_text(self.app.screen, "Search Data Structure", self.app.fonts.body, Palette.TEXT, notes.x + 18, notes.y + 20)
        draw_wrapped(self.app.screen, "TODO: use this screen to demonstrate search performance. Good candidates: trie for player names, hash table for username lookup, BST for sorted profile records.", self.app.fonts.small, Palette.MUTED, pygame.Rect(notes.x + 18, notes.y + 58, notes.width - 36, 170), max_lines=7)

