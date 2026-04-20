from __future__ import annotations

import pygame

from client.core.theme import Palette
from .fonts import FontSet
from .text import draw_text, trim_text


def draw_list_row(
    surface: pygame.Surface,
    rect: pygame.Rect,
    fonts: FontSet,
    left: str,
    right: str,
    subtitle: str = "",
    right_color: tuple[int, int, int] = Palette.ACCENT,
    hover: bool = True,
) -> None:
    """Draw a compact row for leaderboards, search, and short history lists."""
    is_hovered = hover and rect.collidepoint(pygame.mouse.get_pos())
    bg = Palette.PANEL_ALT if is_hovered else Palette.PANEL_DARK
    pygame.draw.rect(surface, bg, rect, border_radius=7)
    pygame.draw.rect(surface, Palette.BORDER, rect, width=1, border_radius=7)

    pad_x = 12
    right_pad = 14
    right_text = trim_text(right, fonts.small, rect.width // 2)
    right_surface = fonts.small.render(right_text, True, right_color)
    right_rect = right_surface.get_rect()
    right_rect.midright = (rect.right - right_pad, rect.centery)
    surface.blit(right_surface, right_rect)

    left_width = max(40, right_rect.x - rect.x - pad_x * 2)
    if subtitle and rect.height >= 34:
        draw_text(surface, left, fonts.small, Palette.TEXT, rect.x + pad_x, rect.y + 5, max_width=left_width)
        draw_text(surface, subtitle, fonts.tiny, Palette.MUTED, rect.x + pad_x, rect.y + 22, max_width=left_width)
    else:
        if subtitle:
            left = f"{left} | {subtitle}"
        left_surface = fonts.small.render(trim_text(left, fonts.small, left_width), True, Palette.TEXT)
        left_rect = left_surface.get_rect()
        left_rect.midleft = (rect.x + pad_x, rect.centery)
        surface.blit(left_surface, left_rect)


def draw_history_row(
    surface: pygame.Surface,
    rect: pygame.Rect,
    fonts: FontSet,
    title: str,
    subtitle: str,
    value: str,
    value_color: tuple[int, int, int] = Palette.ACCENT,
    hover: bool = True,
) -> None:
    """Draw a roomy two-line session/history row with a right-aligned value."""
    is_hovered = hover and rect.collidepoint(pygame.mouse.get_pos())
    bg = Palette.PANEL_ALT if is_hovered else Palette.PANEL_DARK
    pygame.draw.rect(surface, bg, rect, border_radius=8)
    pygame.draw.rect(surface, Palette.BORDER, rect, width=1, border_radius=8)

    pad_x = 16
    value_surface = fonts.small.render(trim_text(value, fonts.small, max(100, rect.width // 3)), True, value_color)
    value_rect = value_surface.get_rect()
    value_rect.midright = (rect.right - pad_x, rect.centery)
    surface.blit(value_surface, value_rect)

    left_width = max(80, value_rect.x - rect.x - pad_x * 2)
    draw_text(surface, title, fonts.small, Palette.TEXT, rect.x + pad_x, rect.y + 8, max_width=left_width)
    draw_text(surface, subtitle, fonts.tiny, Palette.MUTED, rect.x + pad_x, rect.y + 30, max_width=left_width)
