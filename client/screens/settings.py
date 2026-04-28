from __future__ import annotations

import pygame

from client.components import draw_panel, draw_section_header, draw_wrapped
from client.core import Palette

from .base_screen import BaseScreen


class SettingsScreen(BaseScreen):
    def enter(self) -> None:
        super().enter()
        self.platform_status = self.app.backend.get_platform_availability()
        self.gameplay_status = self.app.backend.get_gameplay_availability(refresh=True)

    def draw(self) -> None:
        self.page_title("Arcade Settings", "Quick reference for arcade status, data sources, and server settings.")
        left = pygame.Rect(30, 170, 545, 510)
        right = pygame.Rect(605, 170, 565, 510)
        draw_panel(self.app.screen, left)
        draw_panel(self.app.screen, right)

        platform_status = getattr(self, "platform_status", self.app.backend.get_platform_availability())
        gameplay_status = getattr(self, "gameplay_status", self.app.backend.get_gameplay_availability(refresh=False))

        draw_section_header(self.app.screen, "Arcade Status", "Platform features stay available even if the gameplay relay is offline.", self.app.fonts, pygame.Rect(left.x + 18, left.y + 18, left.width - 36, 50))
        status_rows = [
            ("Run mode", self.app.backend.run_mode_label),
            ("Entry point", "main.py"),
            ("Platform server", platform_status.message),
            ("Gameplay server", gameplay_status.message),
            ("Playable games", "Fruit Drop Rush, Escape the City, Forgotten"),
            ("Allowed ports", "50068, 50069, 50075, 50082"),
            ("Serializer", f"{self.app.backend.game_launch_service.connection.serializer} game messages"),
        ]
        for index, (label, value) in enumerate(status_rows):
            row = pygame.Rect(left.x + 18, left.y + 88 + index * 48, left.width - 36, 36)
            if label == "Platform server":
                status_label = "Online" if platform_status.reachable else "Offline"
                accent = Palette.SUCCESS if platform_status.reachable else Palette.ERROR
                self.draw_list_row(row, label, value, status_label, accent)
            elif label == "Gameplay server":
                status_label = "Online" if gameplay_status.reachable else "Offline"
                accent = Palette.SUCCESS if gameplay_status.reachable else Palette.WARNING
                self.draw_list_row(row, label, value, status_label, accent)
            else:
                self.draw_list_row(row, label, "", value)

        draw_section_header(self.app.screen, "Connection Layers", "The arcade separates account/data features from live gameplay sockets.", self.app.fonts, pygame.Rect(right.x + 18, right.y + 18, right.width - 36, 50))
        hooks = [
            ("Python Platform", "login, accounts, search, profiles, catalog, leaderboard, history"),
            ("Platform endpoint", platform_status.endpoint),
            ("C++ Gameplay", "live game session socket, join/leave, state updates"),
            ("Gameplay endpoint", gameplay_status.endpoint),
            ("Launch args", "--server, --port, --serializer"),
            ("SSH tunnel model", "Local Client -> SSH Tunnel -> ECE Platform/Game Servers"),
        ]
        for index, (label, value) in enumerate(hooks):
            row = pygame.Rect(right.x + 18, right.y + 88 + index * 56, right.width - 36, 44)
            self.draw_list_row(row, label, value, "Hook", Palette.WARNING)

        reminder = "If the gameplay server is offline, the arcade warns cleanly and still lets the class log in, browse, search, and run local game fallbacks."
        draw_wrapped(self.app.screen, reminder, self.app.fonts.small, Palette.MUTED, pygame.Rect(right.x + 18, right.bottom - 95, right.width - 36, 70), max_lines=3)
