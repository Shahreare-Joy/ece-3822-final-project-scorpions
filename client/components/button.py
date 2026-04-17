from __future__ import annotations

from collections.abc import Callable

import pygame


class UIButton:
    """Minimal reusable Pygame button scaffold.

    TODO(UI): Expand styling only here so screens do not duplicate button
    drawing logic.
    """

    def __init__(self, rect: pygame.Rect, label: str, on_click: Callable[[], None]) -> None:
        self.rect = rect
        self.label = label
        self.on_click = on_click

    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and self.rect.collidepoint(event.pos):
            self.on_click()

    def draw(self, surface: pygame.Surface, font: pygame.font.Font) -> None:
        pygame.draw.rect(surface, (45, 56, 78), self.rect, border_radius=8)
        text = font.render(self.label, True, (240, 244, 252))
        surface.blit(text, text.get_rect(center=self.rect.center))
