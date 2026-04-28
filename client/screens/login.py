from __future__ import annotations

import pygame

from client.components import Button, InputBox, draw_panel, draw_text, draw_wrapped
from client.core import WIDTH, Palette, ScreenName

from .base_screen import BaseScreen


class LoginScreen(BaseScreen):
    def enter(self) -> None:
        super().enter()
        self.username = InputBox((450, 295, 300, 50), "Username", self.app.fonts.body)
        self.password = InputBox((450, 358, 300, 50), "Password", self.app.fonts.body, password=True)
        self.username.active = True
        self.inputs = [self.username, self.password]
        self.buttons = [
            Button((450, 430, 300, 52), "Log In", self.try_login, self.app.fonts.button, bg=Palette.ACCENT, hover=Palette.ACCENT_HOVER),
            Button((450, 496, 140, 44), "Back", lambda: self.app.navigate(ScreenName.WELCOME), self.app.fonts.button),
            Button((610, 496, 140, 44), "Clear", self.clear, self.app.fonts.button),
        ]

    def try_login(self) -> None:
        # Local classroom accounts are backed by data/demo_accounts.json.
        # The server auth layer can replace this service later without changing
        # the screen behavior.
        result = self.app.backend.authenticate(self.username.text, self.password.text)
        if not result.success:
            self.app.show_message(result.message, Palette.ERROR)
            return
        self.app.current_player = result.player
        self.app.navigate(ScreenName.HOME, result.message, Palette.SUCCESS)
        self.app.backend.start_post_login_preload(result.player)

    def clear(self) -> None:
        self.username.text = ""
        self.password.text = ""
        self.username.active = True
        self.password.active = False
        self.app.show_message("Login form cleared.", Palette.MUTED)

    def handle_event(self, event: pygame.event.Event) -> None:
        super().handle_event(event)
        for index, box in enumerate(self.inputs):
            result = box.handle_event(event)
            if result == "focus":
                for other in self.inputs:
                    other.active = False
                box.active = True
            elif result == "tab":
                box.active = False
                self.inputs[(index + 1) % len(self.inputs)].active = True
                break
            elif result == "enter":
                self.try_login()
                break

    def draw(self) -> None:
        draw_text(self.app.screen, "SCORPIONS ARCADE", self.app.fonts.title, Palette.TEXT, WIDTH // 2, 118, center=True)
        panel = pygame.Rect(380, 215, 440, 380)
        draw_panel(self.app.screen, panel)
        draw_text(self.app.screen, "Log In", self.app.fonts.heading, Palette.TEXT, panel.centerx, 252, center=True)
        draw_wrapped(self.app.screen, "Use your class account, or create a new local arcade account.", self.app.fonts.small, Palette.MUTED, pygame.Rect(panel.x + 54, 275, panel.width - 108, 40), align="center")
        for box in self.inputs:
            box.draw(self.app.screen)
        for button in self.buttons:
            button.draw(self.app.screen)
        self.draw_message(632)
