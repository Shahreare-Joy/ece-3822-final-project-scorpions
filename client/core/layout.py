from __future__ import annotations

import pygame

from .config import WIDTH, HEIGHT
from .theme import Palette


def draw_background_grid(surface: pygame.Surface) -> None:
    """Draw the shared dark arcade background grid."""
    surface.fill(Palette.BG)
    for x in range(0, WIDTH, 40):
        pygame.draw.line(surface, Palette.GRID, (x, 0), (x, HEIGHT))
    for y in range(0, HEIGHT, 40):
        pygame.draw.line(surface, Palette.GRID, (0, y), (WIDTH, y))


def content_rect(y: int, height: int, margin: int = 30) -> pygame.Rect:
    """Small helper for screens that need a full-width content band."""
    return pygame.Rect(margin, y, WIDTH - margin * 2, height)

