from __future__ import annotations

from typing import TYPE_CHECKING

import pygame

from scorpions_arcade.components import Button, GameCard, InputBox, draw_list_row, draw_text, draw_wrapped
from scorpions_arcade.core import CONTENT_TOP, HEIGHT, PAGE_PAD, WIDTH, Palette

if TYPE_CHECKING:
    from scorpions_arcade.core.app import ArcadeApp


class BaseScreen:
    """Base class for UI-only screens.

    Screens should draw and handle input. Real project logic belongs in services,
    integrations, or placeholders so teammates can work independently.
    """

    def __init__(self, app: ArcadeApp) -> None:
        self.app = app
        self.buttons: list[Button] = []
        self.cards: list[GameCard] = []
        self.inputs: list[InputBox] = []

    def enter(self) -> None:
        self.buttons = []
        self.cards = []
        self.inputs = []

    def handle_event(self, event: pygame.event.Event) -> None:
        for button in self.buttons:
            button.handle_event(event)
        for card in self.cards:
            card.handle_event(event)

    def update(self, dt: int) -> None:
        for box in self.inputs:
            box.update(dt)

    def draw(self) -> None:
        raise NotImplementedError

    def draw_message(self, y: int = HEIGHT - 34) -> None:
        if self.app.message:
            draw_wrapped(self.app.screen, self.app.message, self.app.fonts.small, self.app.message_color, pygame.Rect(100, y - 16, WIDTH - 200, 34), align="center", max_lines=2)

    def page_title(self, title: str, subtitle: str) -> None:
        draw_text(self.app.screen, title, self.app.fonts.heading, Palette.TEXT, PAGE_PAD, CONTENT_TOP)
        draw_wrapped(self.app.screen, subtitle, self.app.fonts.small, Palette.MUTED, pygame.Rect(PAGE_PAD, CONTENT_TOP + 35, 820, 40), max_lines=2)

    def draw_list_row(self, rect: pygame.Rect, left: str, middle: str, right: str, accent: tuple[int, int, int] = Palette.ACCENT) -> None:
        draw_list_row(self.app.screen, rect, self.app.fonts, left, right, subtitle=middle, right_color=accent)

