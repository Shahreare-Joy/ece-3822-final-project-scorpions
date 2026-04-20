from __future__ import annotations

from dataclasses import dataclass

import pygame


@dataclass
class FontSet:
    """Font bundle used by the UI components and screens."""

    title: pygame.font.Font
    heading: pygame.font.Font
    subheading: pygame.font.Font
    body: pygame.font.Font
    small: pygame.font.Font
    tiny: pygame.font.Font
    button: pygame.font.Font


def make_fonts() -> FontSet:
    """Create all fonts in one place so visual style stays consistent."""
    return FontSet(
        title=pygame.font.SysFont("arial", 40, bold=True),
        heading=pygame.font.SysFont("arial", 28, bold=True),
        subheading=pygame.font.SysFont("arial", 22, bold=True),
        body=pygame.font.SysFont("arial", 18),
        small=pygame.font.SysFont("arial", 15),
        tiny=pygame.font.SysFont("arial", 13),
        button=pygame.font.SysFont("arial", 17, bold=True),
    )

