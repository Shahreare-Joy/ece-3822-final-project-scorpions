from __future__ import annotations

"""Small image-loading helpers for game thumbnails and screenshots."""

from pathlib import Path

import pygame


PROJECT_ROOT = Path(__file__).resolve().parents[2]
_IMAGE_CACHE: dict[tuple[str, int, int, str], pygame.Surface] = {}


def resolve_asset_path(path_text: str) -> Path:
    path = Path(path_text)
    if path.is_absolute():
        return path
    return PROJECT_ROOT / path


def load_image(path_text: str, size: tuple[int, int]) -> pygame.Surface | None:
    """Load and scale an image, returning None when the asset is unavailable."""

    if not path_text:
        return None
    key = (path_text, size[0], size[1], "fit")
    if key in _IMAGE_CACHE:
        return _IMAGE_CACHE[key]
    path = resolve_asset_path(path_text)
    if not path.exists():
        return None
    try:
        image = pygame.image.load(str(path))
        try:
            image = image.convert_alpha()
        except pygame.error:
            image = image.copy()
    except pygame.error:
        return None
    scaled = pygame.transform.smoothscale(image, size)
    _IMAGE_CACHE[key] = scaled
    return scaled


def load_image_cover(path_text: str, size: tuple[int, int]) -> pygame.Surface | None:
    """Load an image using cover scaling, similar to CSS object-fit: cover."""

    if not path_text:
        return None
    key = (path_text, size[0], size[1], "cover")
    if key in _IMAGE_CACHE:
        return _IMAGE_CACHE[key]
    path = resolve_asset_path(path_text)
    if not path.exists():
        return None
    try:
        image = pygame.image.load(str(path))
        try:
            image = image.convert_alpha()
        except pygame.error:
            image = image.copy()
    except pygame.error:
        return None

    source_w, source_h = image.get_size()
    target_w, target_h = size
    if source_w <= 0 or source_h <= 0 or target_w <= 0 or target_h <= 0:
        return None
    scale = max(target_w / source_w, target_h / source_h)
    scaled_size = (max(1, int(source_w * scale)), max(1, int(source_h * scale)))
    scaled = pygame.transform.smoothscale(image, scaled_size)
    crop = pygame.Rect(
        max(0, (scaled_size[0] - target_w) // 2),
        max(0, (scaled_size[1] - target_h) // 2),
        target_w,
        target_h,
    )
    covered = pygame.Surface(size, pygame.SRCALPHA)
    covered.blit(scaled, (0, 0), crop)
    _IMAGE_CACHE[key] = covered
    return covered
