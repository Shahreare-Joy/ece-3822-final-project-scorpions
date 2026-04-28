from __future__ import annotations

import pygame

from client.components.image_assets import load_image_cover
from client.core import HEIGHT, WIDTH


AUTH_BACKGROUND_PATH = "client/assets/login/scorpions_arcade_hallway.png"


def draw_auth_background(surface: pygame.Surface) -> None:
    """Draw the shared Welcome/Login/Create Account background."""

    background = load_image_cover(AUTH_BACKGROUND_PATH, (WIDTH, HEIGHT))
    if background is not None:
        surface.blit(background, (0, 0))
