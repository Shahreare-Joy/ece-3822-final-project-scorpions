from __future__ import annotations

from typing import Callable

import pygame

from client.core.theme import Palette
from client.models import Game
from .fonts import FontSet
from .image_assets import load_image
from .panel import draw_badge
from .text import draw_text


class GameCard:
    def __init__(self, rect: tuple[int, int, int, int], game: Game, on_click: Callable[[Game], None], fonts: FontSet, compact: bool = False) -> None:
        
        # store card layout, game data, click action, fonts, and display mode
        self.rect = pygame.Rect(rect)
        self.game = game
        self.on_click = on_click
        self.fonts = fonts
        self.compact = compact
        self.hovered = False

    def handle_event(self, event: pygame.event.Event) -> None:
        '''handle mouse movement and click events for the card'''
        if event.type == pygame.MOUSEMOTION:
            self.hovered = self.rect.collidepoint(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and self.rect.collidepoint(event.pos):
            self.on_click(self.game)

    def draw(self, surface: pygame.Surface) -> None:
        rect = self.rect.move(0, -2 if self.hovered else 0)
        fill = tuple(min(255, value + 18) for value in self.game.color) if self.hovered else self.game.color
        thumbnail = load_image(self.game.thumbnail_path, (rect.width, rect.height))
        if thumbnail is not None:
            surface.blit(thumbnail, rect)
        else:
            pygame.draw.rect(surface, fill, rect, border_radius=8)
        pygame.draw.rect(surface, Palette.BORDER, rect, width=2, border_radius=8)

        plate_h = 52 if self.compact else 70
        plate = pygame.Rect(rect.x, rect.bottom - plate_h, rect.width, plate_h)
        pygame.draw.rect(surface, Palette.PANEL_DARK, plate, border_radius=8)
        pygame.draw.rect(surface, Palette.PANEL_DARK, (plate.x, plate.y, plate.width, 14))

        x = rect.x + 12
        max_w = rect.width - 24
        draw_text(surface, self.game.title, self.fonts.body, Palette.TEXT, x, plate.y + 8, max_width=max_w)
        draw_text(surface, f"{self.game.genre} | {self.game.status}", self.fonts.small, Palette.MUTED, x, plate.y + 31, max_width=max_w)
        if not self.compact:
            draw_text(surface, f"{self.game.players_now:,} playing | {self.game.total_plays:,} plays", self.fonts.tiny, Palette.SOFT, x, plate.y + 52, max_width=max_w)
        elif self.game.playable:
            draw_badge(surface, "PLAYABLE", pygame.Rect(rect.right - 82, rect.y + 8, 70, 22), self.fonts.tiny, Palette.SUCCESS)
