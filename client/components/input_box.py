from __future__ import annotations

import pygame


class TextInputBox:
    """Simple input box scaffold.

    TODO(AUTH/UI): Reuse this for login/signup, then pass values to
    client/services/auth_service.py instead of validating inside screens.
    """

    def __init__(self, rect: pygame.Rect, placeholder: str = "") -> None:
        self.rect = rect
        self.placeholder = placeholder
        self.text = ""
        self.active = False

    def handle_event(self, event: pygame.event.Event) -> None:
        # TODO(UI): Add text editing behavior when migrating screens into client/.
        _ = event

    def draw(self, surface: pygame.Surface, font: pygame.font.Font) -> None:
        pygame.draw.rect(surface, (18, 22, 32), self.rect, border_radius=8)
        value = self.text or self.placeholder
        color = (240, 244, 252) if self.text else (150, 160, 180)
        surface.blit(font.render(value, True, color), (self.rect.x + 12, self.rect.y + 9))
