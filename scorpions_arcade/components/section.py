from __future__ import annotations

import pygame

from scorpions_arcade.core.theme import Palette
from .fonts import FontSet
from .text import draw_text


def draw_section_header(surface: pygame.Surface, title: str, subtitle: str, fonts: FontSet, area: pygame.Rect) -> None:
    """Draw a reusable section title with optional helper text."""
    draw_text(surface, title, fonts.body, Palette.TEXT, area.x, area.y, max_width=area.width)
    if subtitle:
        draw_text(surface, subtitle, fonts.tiny, Palette.MUTED, area.x, area.y + 24, max_width=area.width)
