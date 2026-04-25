from __future__ import annotations

"""Small image-loading helpers for game thumbnails and screenshots."""

from pathlib import Path

import pygame


PROJECT_ROOT = Path(__file__).resolve().parents[2]
_IMAGE_CACHE: dict[tuple[str, int, int], pygame.Surface] = {}


def resolve_asset_path(path_text: str) -> Path:
    path = Path(path_text)
    if path.is_absolute():
        return path
    return PROJECT_ROOT / path


def load_image(path_text: str, size: tuple[int, int]) -> pygame.Surface | None:
    """Load and scale an image, returning None when the asset is unavailable."""

    if not path_text:
        return None
    key = (path_text, size[0], size[1])
    if key in _IMAGE_CACHE:
        return _IMAGE_CACHE[key]
    path = resolve_asset_path(path_text)
    if not path.exists():
        return None
    try:
        image = pygame.image.load(str(path)).convert_alpha()
    except pygame.error:
        return None
    scaled = pygame.transform.smoothscale(image, size)
    _IMAGE_CACHE[key] = scaled
    return scaled
