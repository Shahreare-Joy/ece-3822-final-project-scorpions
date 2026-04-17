from __future__ import annotations

import pygame


class ListRowView:
    """Reusable list row scaffold for history, search, and leaderboards."""

    def __init__(self, rect: pygame.Rect, left: str, right: str = "") -> None:
        self.rect = rect
        self.left = left
        self.right = right

    def draw(self, surface: pygame.Surface, font: pygame.font.Font) -> None:
        pygame.draw.rect(surface, (29, 35, 48), self.rect, border_radius=8)
        surface.blit(font.render(self.left, True, (240, 244, 252)), (self.rect.x + 12, self.rect.y + 8))
        if self.right:
            right_text = font.render(self.right, True, (105, 180, 240))
            surface.blit(right_text, (self.rect.right - right_text.get_width() - 12, self.rect.y + 8))
