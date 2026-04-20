from __future__ import annotations

from pathlib import Path

import pygame

from client.core import Palette
from .text import draw_text


AVATAR_DIR = Path(__file__).resolve().parents[1] / "assets" / "avatars"
AVATAR_COLORS = [
    (69, 154, 225),
    (75, 198, 130),
    (245, 184, 75),
    (210, 86, 98),
    (138, 104, 212),
    (66, 196, 190),
]


def draw_player_avatar(
    surface: pygame.Surface,
    center: tuple[int, int],
    radius: int,
    display_name: str,
    avatar_id: str = "",
    font: pygame.font.Font | None = None,
) -> None:
    """Draw a circular player avatar with image fallback.

    TODO(AVATAR): When the account system exists, let players choose an avatar
    and store the selected avatar_id in the real profile record.
    """
    image = _load_avatar_image(avatar_id, radius * 2)
    if image is not None:
        _draw_circular_image(surface, image, center, radius)
    else:
        color = _placeholder_color(avatar_id or display_name)
        pygame.draw.circle(surface, color, center, radius)
        pygame.draw.circle(surface, Palette.BORDER, center, radius, width=2)
        pygame.draw.circle(surface, tuple(min(255, value + 28) for value in color), center, radius - 7, width=1)
        if font is not None:
            initials = _initials(display_name)
            draw_text(surface, initials, font, Palette.TEXT, center[0], center[1] - 1, center=True, max_width=radius * 2 - 10)


def _load_avatar_image(avatar_id: str, size: int) -> pygame.Surface | None:
    if not avatar_id:
        return None
    for extension in (".png", ".jpg", ".jpeg"):
        path = AVATAR_DIR / f"{avatar_id}{extension}"
        if path.exists():
            try:
                image = pygame.image.load(str(path)).convert_alpha()
            except pygame.error:
                return None
            return pygame.transform.smoothscale(image, (size, size))
    return None


def _draw_circular_image(surface: pygame.Surface, image: pygame.Surface, center: tuple[int, int], radius: int) -> None:
    avatar = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
    mask = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
    pygame.draw.circle(mask, (255, 255, 255, 255), (radius, radius), radius)
    avatar.blit(image, (0, 0))
    avatar.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
    surface.blit(avatar, (center[0] - radius, center[1] - radius))
    pygame.draw.circle(surface, Palette.BORDER, center, radius, width=2)


def _placeholder_color(seed: str) -> tuple[int, int, int]:
    index = sum(ord(char) for char in seed) % len(AVATAR_COLORS)
    return AVATAR_COLORS[index]


def _initials(display_name: str) -> str:
    parts = [part for part in display_name.replace("_", " ").split(" ") if part]
    if not parts:
        return "?"
    if len(parts) == 1:
        return parts[0][:2].upper()
    return (parts[0][0] + parts[-1][0]).upper()
