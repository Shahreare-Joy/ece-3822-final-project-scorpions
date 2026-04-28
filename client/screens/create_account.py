from __future__ import annotations

import pygame

from client.components import Button, InputBox, draw_panel, draw_text, draw_wrapped
from client.components.auth_background import draw_auth_background
from client.core import Palette, ScreenName

from .base_screen import BaseScreen


class CreateAccountScreen(BaseScreen):
    def enter(self) -> None:
        super().enter()
        self.username = InputBox((435, 240, 330, 46), "Username", self.app.fonts.body)
        self.display_name = InputBox((435, 296, 330, 46), "Display name", self.app.fonts.body)
        self.password = InputBox((435, 352, 330, 46), "Password", self.app.fonts.body, password=True)
        self.confirm = InputBox((435, 408, 330, 46), "Confirm password", self.app.fonts.body, password=True)
        self.country = InputBox((435, 464, 330, 46), "Country", self.app.fonts.body)
        self.username.active = True
        self.inputs = [self.username, self.display_name, self.password, self.confirm, self.country]
        self.buttons = [
            Button((435, 530, 330, 50), "Create Account", self.try_create, self.app.fonts.button, bg=Palette.ACCENT, hover=Palette.ACCENT_HOVER),
            Button((435, 594, 155, 42), "Back", lambda: self.app.navigate(ScreenName.WELCOME), self.app.fonts.button),
            Button((610, 594, 155, 42), "Clear", self.clear, self.app.fonts.button),
        ]

    def try_create(self) -> None:
        # Account creation persists through the auth/account service so players
        # can close and reopen the arcade without losing the new login.
        result = self.app.backend.create_account(self.username.text, self.display_name.text, self.password.text, self.confirm.text, self.country.text)
        if not result.success:
            self.app.show_message(result.message, Palette.ERROR)
            return
        self.app.navigate(ScreenName.LOGIN, result.message, Palette.SUCCESS)

    def clear(self) -> None:
        for box in self.inputs:
            box.text = ""
            box.active = False
        self.username.active = True

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
                self.try_create()
                break

    def draw(self) -> None:
        draw_auth_background(self.app.screen)
        panel = pygame.Rect(360, 160, 480, 515)
        draw_panel(self.app.screen, panel)
        draw_text(self.app.screen, "Create Account", self.app.fonts.heading, Palette.TEXT, panel.centerx, 190, center=True)
        draw_wrapped(self.app.screen, "Create a local Scorpions Arcade account for this machine.", self.app.fonts.small, Palette.MUTED, pygame.Rect(panel.x + 50, 213, panel.width - 100, 42), align="center")
        for box in self.inputs:
            box.draw(self.app.screen)
        for button in self.buttons:
            button.draw(self.app.screen)
        self.draw_message(710)
