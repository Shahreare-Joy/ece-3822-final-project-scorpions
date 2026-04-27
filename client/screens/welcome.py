from __future__ import annotations

import pygame

from client.components import Button, draw_panel, draw_text, draw_wrapped
from client.core import WIDTH, Palette, ScreenName

from .base_screen import BaseScreen


class WelcomeScreen(BaseScreen):
    def enter(self) -> None:
        super().enter()
        self.buttons = [
            Button((475, 330, 250, 56), "Log In", lambda: self.app.navigate(ScreenName.LOGIN), self.app.fonts.button, bg=Palette.ACCENT, hover=Palette.ACCENT_HOVER),
            Button((475, 398, 250, 56), "Create Account", lambda: self.app.navigate(ScreenName.CREATE_ACCOUNT), self.app.fonts.button),
            Button((475, 466, 250, 50), "Quit", self.app.quit, self.app.fonts.button, bg=Palette.LOGOUT, hover=Palette.LOGOUT_HOVER),
        ]

    def draw(self) -> None:
        draw_text(self.app.screen, "SCORPIONS ARCADE", self.app.fonts.title, Palette.TEXT, WIDTH // 2, 120, center=True)
        draw_wrapped(self.app.screen, "A multiplayer arcade hub for ECE 3822 Spring 2026.", self.app.fonts.body, Palette.MUTED, pygame.Rect(330, 165, 540, 52), align="center")
        panel = pygame.Rect(360, 250, 480, 320)
        draw_panel(self.app.screen, panel)
        draw_text(self.app.screen, "Enter the arcade", self.app.fonts.heading, Palette.TEXT, panel.centerx, 288, center=True)
        draw_wrapped(self.app.screen, "Sign in with a class account or create your own player profile.", self.app.fonts.small, Palette.MUTED, pygame.Rect(panel.x + 45, 306, panel.width - 90, 48), align="center", max_lines=2)
        for button in self.buttons:
            button.draw(self.app.screen)
        self.draw_message(610)
