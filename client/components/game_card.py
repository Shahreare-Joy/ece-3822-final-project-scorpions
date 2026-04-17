from __future__ import annotations

import pygame

from client.models import ClientGame


class GameCardView:
    """Reusable game-card scaffold.

    TODO(CATALOG UI): Keep this generic. Do not hardcode a specific game here;
    pass ClientGame objects from services/catalog/search.
    """

    def __init__(self, rect: pygame.Rect, game: ClientGame) -> None:
        self.rect = rect
        self.game = game

    def draw(self, surface: pygame.Surface, font: pygame.font.Font) -> None:
        pygame.draw.rect(surface, (32, 40, 56), self.rect, border_radius=8)
        surface.blit(font.render(self.game.title, True, (240, 244, 252)), (self.rect.x + 12, self.rect.y + 12))
