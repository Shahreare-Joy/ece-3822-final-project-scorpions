from __future__ import annotations

"""Reusable Pygame chat overlay for games launched from the arcade.

How other games reuse it:
    1. Make sure the launcher can import the project root. GameLaunchService
       already sets PYTHONPATH for subprocess games.
    2. In the game's main loop, create ChatOverlay(...).
    3. Pass each pygame event to overlay.handle_event(event).
    4. Call overlay.update(dt) and overlay.draw(screen) once per frame.

The overlay uses the existing ChatService/SessionChat circular-buffer path for
local demo messages. Later, ChatService can broadcast through the real server
without changing the overlay's game-facing API.
"""

from dataclasses import dataclass
import os

import pygame

from client.models import ChatMessage
from client.services.chat_service import ChatService


@dataclass
class ChatOverlayConfig:
    session_id: str
    sender_name: str
    title: str = "Session Chat"
    width: int = 390
    height: int = 178
    margin: int = 16
    capacity: int = 50
    storage_dir: str = ""


class ChatOverlay:
    """Lower-left in-game chat panel with bounded recent messages."""

    def __init__(self, config: ChatOverlayConfig, chat_service: ChatService | None = None) -> None:
        self.config = config
        self.chat_service = chat_service or ChatService([], capacity=config.capacity, storage_dir=config.storage_dir or None)
        self.visible = True
        self.input_active = False
        self.input_text = ""
        self.max_chars = 120
        self.font = pygame.font.Font(None, 18)
        self.small_font = pygame.font.Font(None, 16)
        self.title_font = pygame.font.Font(None, 20)
        self.cursor_ms = 0
        self.cursor_visible = True
        if config.storage_dir and not os.path.exists(config.storage_dir):
            os.makedirs(config.storage_dir, exist_ok=True)
        if not self.chat_service.get_recent_messages(config.session_id, 1):
            self.chat_service.add_message(config.session_id, "Arcade Host", "Press Enter to chat. Press T or C to hide/show.")

    def toggle_visible(self) -> None:
        self.visible = not self.visible
        if not self.visible:
            self.input_active = False

    def handle_event(self, event: pygame.event.Event) -> bool:
        """Return True when the overlay consumed the event."""

        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_t, pygame.K_c) and (not self.input_active or not self.visible):
                self.toggle_visible()
                return True
            if not self.visible:
                return False
            if event.key == pygame.K_RETURN:
                if self.input_active and self.input_text.strip():
                    self.send_message()
                self.input_active = True
                return True
            if event.key == pygame.K_ESCAPE and self.input_active:
                self.input_active = False
                return True
            if self.input_active:
                if event.key == pygame.K_BACKSPACE:
                    self.input_text = self.input_text[:-1]
                    return True
                if len(self.input_text) < self.max_chars and event.unicode.isprintable():
                    self.input_text += event.unicode
                    return True
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            input_rect = self._input_rect(pygame.display.get_surface())
            if input_rect and input_rect.collidepoint(event.pos):
                self.input_active = True
                return True
            if self.visible and self._panel_rect(pygame.display.get_surface()).collidepoint(event.pos):
                return True
        return False

    def update(self, dt: int) -> None:
        self.cursor_ms += dt
        if self.cursor_ms >= 500:
            self.cursor_ms = 0
            self.cursor_visible = not self.cursor_visible

    def send_message(self) -> None:
        text = self.input_text.strip()
        if not text:
            return
        self.chat_service.add_message(self.config.session_id, self.config.sender_name, text)
        self.input_text = ""

    def recent_messages(self, limit: int = 4) -> list[ChatMessage]:
        return self.chat_service.get_recent_messages(self.config.session_id, limit)

    def draw(self, surface: pygame.Surface) -> None:
        if not self.visible:
            self._draw_hidden_hint(surface)
            return

        panel = self._panel_rect(surface)
        overlay = pygame.Surface((panel.width, panel.height), pygame.SRCALPHA)
        overlay.fill((10, 14, 22, 188))
        pygame.draw.rect(overlay, (74, 92, 124, 215), overlay.get_rect(), width=2, border_radius=8)
        surface.blit(overlay, panel)

        surface.blit(self.title_font.render(self.config.title, True, (240, 244, 252)), (panel.x + 12, panel.y + 10))
        surface.blit(self.small_font.render("Enter sends | T/C hides", True, (170, 181, 203)), (panel.right - 138, panel.y + 12))

        messages = self.recent_messages(4)
        start_y = panel.y + 38
        for index, message in enumerate(messages[-4:]):
            y = start_y + index * 23
            sender = self.small_font.render(f"{message.sender}:", True, (103, 181, 242))
            surface.blit(sender, (panel.x + 12, y))
            body = self.small_font.render(self._trim(message.text, 38), True, (240, 244, 252))
            surface.blit(body, (panel.x + 92, y))

        input_rect = self._input_rect(surface)
        pygame.draw.rect(surface, (18, 22, 32), input_rect, border_radius=6)
        pygame.draw.rect(surface, (103, 181, 242) if self.input_active else (74, 92, 124), input_rect, width=2, border_radius=6)
        label = self.input_text if self.input_text else "Type message..."
        color = (240, 244, 252) if self.input_text else (170, 181, 203)
        surface.blit(self.font.render(self._trim(label, 42), True, color), (input_rect.x + 10, input_rect.y + 7))
        if self.input_active and self.cursor_visible:
            cursor_x = min(input_rect.x + 10 + self.font.size(self.input_text)[0] + 2, input_rect.right - 10)
            pygame.draw.line(surface, (240, 244, 252), (cursor_x, input_rect.y + 6), (cursor_x, input_rect.bottom - 6), 2)

    def _draw_hidden_hint(self, surface: pygame.Surface) -> None:
        hint = pygame.Surface((180, 28), pygame.SRCALPHA)
        hint.fill((10, 14, 22, 165))
        pygame.draw.rect(hint, (74, 92, 124, 200), hint.get_rect(), width=1, border_radius=6)
        hint.blit(self.small_font.render("Chat hidden - press T", True, (240, 244, 252)), (10, 7))
        surface.blit(hint, (self.config.margin, surface.get_height() - self.config.margin - 28))

    def _panel_rect(self, surface: pygame.Surface | None) -> pygame.Rect:
        if surface is None:
            return pygame.Rect(self.config.margin, self.config.margin, self.config.width, self.config.height)
        return pygame.Rect(
            self.config.margin,
            surface.get_height() - self.config.margin - self.config.height,
            self.config.width,
            self.config.height,
        )

    def _input_rect(self, surface: pygame.Surface | None) -> pygame.Rect:
        panel = self._panel_rect(surface)
        return pygame.Rect(panel.x + 12, panel.bottom - 42, panel.width - 24, 30)

    @staticmethod
    def _trim(text: str, max_chars: int) -> str:
        return text if len(text) <= max_chars else text[: max_chars - 1] + "..."
