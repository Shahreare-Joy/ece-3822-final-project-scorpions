from __future__ import annotations

import pygame

from client.core.theme import Palette
from .text import draw_text


class InputBox:
    def __init__(self, rect: tuple[int, int, int, int], placeholder: str, font: pygame.font.Font, password: bool = False, max_length: int = 32) -> None:
        self.rect = pygame.Rect(rect)
        self.placeholder = placeholder
        self.font = font
        self.password = password
        self.max_length = max_length
        self.text = ""
        self.active = False
        self.cursor_ms = 0
        self.cursor_visible = True

    def handle_event(self, event: pygame.event.Event) -> str | None:
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            self.active = self.rect.collidepoint(event.pos)
            return "focus" if self.active else None
        if event.type == pygame.KEYDOWN and self.active:
            if event.key == pygame.K_BACKSPACE:
                self.text = self.text[:-1]
            elif event.key == pygame.K_TAB:
                return "tab"
            elif event.key == pygame.K_RETURN:
                return "enter"
            elif len(self.text) < self.max_length and event.unicode.isprintable():
                self.text += event.unicode
        return None

    def update(self, dt: int) -> None:
        self.cursor_ms += dt
        if self.cursor_ms >= 500:
            self.cursor_ms = 0
            self.cursor_visible = not self.cursor_visible

    def draw(self, surface: pygame.Surface) -> None:
        bg = Palette.INPUT_ACTIVE if self.active else Palette.INPUT
        pygame.draw.rect(surface, bg, self.rect, border_radius=8)
        pygame.draw.rect(surface, Palette.ACCENT if self.active else Palette.BORDER, self.rect, width=2, border_radius=8)
        shown = "*" * len(self.text) if self.password and self.text else self.text
        label = shown if shown else self.placeholder
        color = Palette.TEXT if shown else Palette.MUTED
        text_y = self.rect.y + max(4, (self.rect.height - self.font.get_height()) // 2)
        draw_text(surface, label, self.font, color, self.rect.x + 14, text_y, max_width=self.rect.width - 28)
        if self.active and self.cursor_visible:
            cursor_x = min(self.rect.x + 14 + self.font.size(shown)[0] + 2, self.rect.right - 12)
            cursor_pad = max(6, (self.rect.height - self.font.get_height()) // 2)
            pygame.draw.line(surface, Palette.TEXT, (cursor_x, self.rect.y + cursor_pad), (cursor_x, self.rect.bottom - cursor_pad), 2)
