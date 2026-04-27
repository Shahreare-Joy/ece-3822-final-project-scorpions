from __future__ import annotations

import pygame

from client.components import draw_panel, draw_section_header, draw_wrapped
from client.core import Palette

from .base_screen import BaseScreen


class SettingsScreen(BaseScreen):
    def draw(self) -> None:
        self.page_title("Arcade Settings", "Quick reference for arcade status, data sources, and server settings.")
        left = pygame.Rect(30, 170, 545, 510)
        right = pygame.Rect(605, 170, 565, 510)
        draw_panel(self.app.screen, left)
        draw_panel(self.app.screen, right)

        draw_section_header(self.app.screen, "Arcade Status", "Local services are active and ready for class play.", self.app.fonts, pygame.Rect(left.x + 18, left.y + 18, left.width - 36, 50))
        status_rows = [
            ("Entry point", "main.py"),
            ("Class accounts", "saved local account storage"),
            ("Playable games", "Fruit Collection, Escape the City, Forgotten"),
            ("Server ports", "50068, 50069, 50075, 50082"),
            ("Data source", "class accounts + generated dataset"),
        ]
        for index, (label, value) in enumerate(status_rows):
            row = pygame.Rect(left.x + 18, left.y + 88 + index * 48, left.width - 36, 36)
            self.draw_list_row(row, label, "", value)

        draw_section_header(self.app.screen, "System Paths", "Core files used by the arcade client and server.", self.app.fonts, pygame.Rect(right.x + 18, right.y + 18, right.width - 36, 50))
        hooks = [
            ("datastructures/", "hash table, BST, heap, graph, history index"),
            ("integrations/cpp_server.py", "allowed port configuration and server handoff"),
            ("services/game_launch_service.py", "game folder launch and session handoff"),
            ("data/synthetic_dataset/", "generated platform records"),
            ("docs/project_notes.md", "branch plan and professor checklist"),
        ]
        for index, (label, value) in enumerate(hooks):
            row = pygame.Rect(right.x + 18, right.y + 88 + index * 56, right.width - 36, 44)
            self.draw_list_row(row, label, value, "Hook", Palette.WARNING)

        reminder = "Game folders launch with their own working directory so uploaded assets keep working."
        draw_wrapped(self.app.screen, reminder, self.app.fonts.small, Palette.MUTED, pygame.Rect(right.x + 18, right.bottom - 95, right.width - 36, 70), max_lines=3)
