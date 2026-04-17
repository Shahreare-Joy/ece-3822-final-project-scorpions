from __future__ import annotations

from collections.abc import Callable

import pygame

from scorpions_arcade.core import WIDTH, Palette, ScreenName
from .button import Button
from .fonts import FontSet


HEADER_HEIGHT = 66
NAV_BUTTON_Y = 15
NAV_BUTTON_HEIGHT = 34
NAV_GAP = 5
RIGHT_ACTION_GAP = 8
RIGHT_PAD = 28


def nav_items() -> list[tuple[str, ScreenName, int]]:
    """Primary center navigation labels. App owns callbacks so routing stays central."""
    return [
        ("Home", ScreenName.HOME, 64),
        ("Browse", ScreenName.BROWSE, 76),
        ("Profile", ScreenName.PROFILE, 76),
        ("Boards", ScreenName.LEADERBOARD, 76),
        ("Search", ScreenName.SEARCH, 74),
        ("History", ScreenName.HISTORY, 76),
    ]


def build_nav_buttons(current_screen: ScreenName, navigate: Callable[[ScreenName], None], logout: Callable[[], None], fonts: FontSet) -> list[Button]:
    """Create grouped top navigation buttons; app passes callbacks, navbar owns layout."""
    buttons: list[Button] = []

    primary_items = nav_items()
    primary_width = sum(width for _, _, width in primary_items) + NAV_GAP * (len(primary_items) - 1)
    x = (WIDTH - primary_width) // 2
    for label, target, width in primary_items:
        buttons.append(
            Button(
                (x, NAV_BUTTON_Y, width, NAV_BUTTON_HEIGHT),
                label,
                lambda destination=target: navigate(destination),
                fonts.button,
                bg=Palette.PANEL_ALT,
                hover=Palette.BUTTON_HOVER,
                selected=current_screen == target,
            )
        )
        x += width + NAV_GAP

    logout_width = 82
    settings_width = 88
    logout_x = WIDTH - RIGHT_PAD - logout_width
    settings_x = logout_x - RIGHT_ACTION_GAP - settings_width
    buttons.append(
        Button(
            (settings_x, NAV_BUTTON_Y, settings_width, NAV_BUTTON_HEIGHT),
            "Settings",
            lambda: navigate(ScreenName.SETTINGS),
            fonts.button,
            bg=Palette.PANEL_DARK,
            hover=Palette.BUTTON_HOVER,
            selected=current_screen == ScreenName.SETTINGS,
            selected_bg=Palette.PANEL_ALT,
            border_color=Palette.BORDER,
        )
    )
    buttons.append(
        Button(
            (logout_x, NAV_BUTTON_Y, logout_width, NAV_BUTTON_HEIGHT),
            "Logout",
            logout,
            fonts.button,
            bg=Palette.PANEL_DARK,
            hover=Palette.LOGOUT,
            text_color=Palette.WARNING,
            border_color=Palette.LOGOUT,
        )
    )
    return buttons


def draw_nav_bar(surface: pygame.Surface, buttons: list[Button], fonts: FontSet, connected: bool) -> None:
    """Draw the shared top navigation bar."""
    if not buttons:
        return
    pygame.draw.rect(surface, Palette.PANEL_DARK, (0, 0, WIDTH, HEADER_HEIGHT))
    pygame.draw.line(surface, Palette.BORDER, (0, HEADER_HEIGHT), (WIDTH, HEADER_HEIGHT), 2)
    surface.blit(fonts.subheading.render("SCORPIONS ARCADE", True, Palette.TEXT), (28, 13))
    status = "Connected" if connected else "Disconnected"
    status_color = Palette.SUCCESS if connected else Palette.ERROR
    surface.blit(fonts.tiny.render(f"Mock backend: {status}", True, status_color), (30, 42))
    pygame.draw.line(surface, Palette.BORDER, (970, 15), (970, 49), 1)
    for button in buttons:
        button.draw(surface)
