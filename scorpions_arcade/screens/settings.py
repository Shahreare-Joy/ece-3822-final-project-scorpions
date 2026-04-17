from __future__ import annotations

import pygame

from scorpions_arcade.components import draw_panel, draw_section_header, draw_wrapped
from scorpions_arcade.core import Palette

from .base_screen import BaseScreen


class SettingsScreen(BaseScreen):
    def draw(self) -> None:
        self.page_title("Project Settings", "A lightweight project notes screen. It keeps implementation boundaries visible for the team while the prototype is running.")
        left = pygame.Rect(30, 170, 545, 510)
        right = pygame.Rect(605, 170, 565, 510)
        draw_panel(self.app.screen, left)
        draw_panel(self.app.screen, right)

        draw_section_header(self.app.screen, "Prototype Status", "UI scaffold complete; real backend/data-structure work still belongs to the team.", self.app.fonts, pygame.Rect(left.x + 18, left.y + 18, left.width - 36, 50))
        status_rows = [
            ("Entry point", "main.py"),
            ("Mock account", "joy / 123456"),
            ("Playable template", "Scorpions Arena"),
            ("C++ server", "placeholder hook only"),
            ("Data source", "temporary UI mock data"),
        ]
        for index, (label, value) in enumerate(status_rows):
            row = pygame.Rect(left.x + 18, left.y + 88 + index * 48, left.width - 36, 36)
            self.draw_list_row(row, label, "", value)

        draw_section_header(self.app.screen, "Future Integration Hooks", "Starter files are intentionally thin so you can implement final logic yourself.", self.app.fonts, pygame.Rect(right.x + 18, right.y + 18, right.width - 36, 50))
        hooks = [
            ("placeholders/data_structures.py", "hash table, BST, heap, graph, history index"),
            ("integrations/cpp_server.py", "future C++ login/chat/scoreboard calls"),
            ("services/game_launch_service.py", "future session id and server handoff"),
            ("data/mock_games.py", "replace with cleaned dataset feed"),
            ("docs/project_notes.md", "branch plan and professor checklist"),
        ]
        for index, (label, value) in enumerate(hooks):
            row = pygame.Rect(right.x + 18, right.y + 88 + index * 56, right.width - 36, 44)
            self.draw_list_row(row, label, value, "TODO", Palette.WARNING)

        reminder = "Keep the UI separated from final data logic. Screens should ask the backend layer for results; the backend layer can later call your custom structures and C++ service."
        draw_wrapped(self.app.screen, reminder, self.app.fonts.small, Palette.MUTED, pygame.Rect(right.x + 18, right.bottom - 95, right.width - 36, 70), max_lines=3)
