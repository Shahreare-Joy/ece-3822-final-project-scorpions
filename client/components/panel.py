from __future__ import annotations

import pygame

from client.core.theme import Palette
from .text import draw_text


def draw_panel(surface: pygame.Surface, rect: pygame.Rect, color: tuple[int, int, int] = Palette.PANEL, border: tuple[int, int, int] = Palette.BORDER, radius: int = 8, width: int = 2) -> None:
    pygame.draw.rect(surface, color, rect, border_radius=radius)
    pygame.draw.rect(surface, border, rect, width=width, border_radius=radius)


def draw_badge(surface: pygame.Surface, text: str, rect: pygame.Rect, font: pygame.font.Font, color: tuple[int, int, int], text_color: tuple[int, int, int] = Palette.TEXT) -> None:
    pygame.draw.rect(surface, color, rect, border_radius=8)
    draw_text(surface, text, font, text_color, rect.centerx, rect.centery, center=True, max_width=rect.width - 12)

