from __future__ import annotations

from typing import Callable

import pygame

from client.core.theme import Palette
from .text import draw_text


class Button:
    def __init__(
        self,
        rect: tuple[int, int, int, int],
        text: str,
        on_click: Callable[[], None],
        font: pygame.font.Font,
        bg: tuple[int, int, int] = Palette.BUTTON,
        hover: tuple[int, int, int] = Palette.BUTTON_HOVER,
        selected: bool = False,
        text_color: tuple[int, int, int] = Palette.TEXT,
        selected_bg: tuple[int, int, int] = Palette.ACCENT,
        border_color: tuple[int, int, int] = Palette.BORDER,
    ) -> None:
        self.rect = pygame.Rect(rect)
        self.text = text
        self.on_click = on_click
        self.font = font
        self.bg = bg
        self.hover = hover
        self.selected = selected
        self.text_color = text_color
        self.selected_bg = selected_bg
        self.border_color = border_color
        self.hovered = False

    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame.MOUSEMOTION:
            self.hovered = self.rect.collidepoint(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and self.rect.collidepoint(event.pos):
            self.on_click()

    def draw(self, surface: pygame.Surface) -> None:
        color = self.selected_bg if self.selected else (self.hover if self.hovered else self.bg)
        pygame.draw.rect(surface, color, self.rect, border_radius=8)
        outline = Palette.ACCENT_HOVER if self.selected else self.border_color
        pygame.draw.rect(surface, outline, self.rect, width=2 if self.selected else 1, border_radius=8)
        if self.selected:
            underline = pygame.Rect(self.rect.x + 10, self.rect.bottom - 4, self.rect.width - 20, 2)
            pygame.draw.rect(surface, Palette.TEXT, underline, border_radius=2)
        draw_text(surface, self.text, self.font, self.text_color, self.rect.centerx, self.rect.centery, center=True, max_width=self.rect.width - 12)
