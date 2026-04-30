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
    width: int = 350
    height: int = 154
    margin: int = 14
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
        self.font = pygame.font.Font(None, 17)
        self.small_font = pygame.font.Font(None, 15)
        self.title_font = pygame.font.Font(None, 18)
        self.cursor_ms = 0
        self.cursor_visible = True
        self.scroll_offset = 0
        self._last_message_count = 0
        self.status_text = getattr(self.chat_service, "last_status", "Local session chat ready.")
        if config.storage_dir and not os.path.exists(config.storage_dir):
            os.makedirs(config.storage_dir, exist_ok=True)
        if not self.chat_service.get_recent_messages(config.session_id, 1):
            self.chat_service.add_message(config.session_id, "Arcade Host", "Press Enter to chat. Press T or C to hide/show.")
        self.status_text = getattr(self.chat_service, "last_status", self.status_text)

    def toggle_visible(self) -> None:
        self.visible = not self.visible
        if not self.visible:
            self.input_active = False
            self.chat_service.stop_polling()
        else:
            self.chat_service.resume_polling()
            self.status_text = getattr(self.chat_service, "last_status", self.status_text)

    def close(self) -> None:
        """Stop chat polling when the owning game exits or disposes overlay."""

        self.input_active = False
        self.visible = False
        self.chat_service.stop_polling()

    def dispose(self) -> None:
        self.close()

    def handle_event(self, event: pygame.event.Event) -> bool:
        """Return True when the overlay consumed the event."""

        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_t, pygame.K_c) and (not self.input_active or not self.visible):
                self.toggle_visible()
                return True
            if not self.visible:
                return False
            if event.key in (pygame.K_PAGEUP, pygame.K_PAGEDOWN):
                self._scroll(-3 if event.key == pygame.K_PAGEDOWN else 3)
                return True
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
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if not self.visible:
                return False
            if event.button in (4, 5):
                self._scroll(1 if event.button == 4 else -1)
                return True
            if event.button != 1:
                return False
            input_rect = self._input_rect(pygame.display.get_surface())
            if input_rect and input_rect.collidepoint(event.pos):
                self.input_active = True
                return True
            if self.visible and self._panel_rect(pygame.display.get_surface()).collidepoint(event.pos):
                if self.input_active:
                    self.input_active = False
                return True
            if self.input_active:
                self.input_active = False
                return False
        elif event.type == pygame.MOUSEWHEEL:
            if self.visible:
                self._scroll(1 if event.y > 0 else -1)
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
        self.status_text = getattr(self.chat_service, "last_status", self.status_text)
        self.input_text = ""
        self.scroll_offset = 0

    def recent_messages(self, limit: int = 12) -> list[ChatMessage]:
        messages = self.chat_service.get_recent_messages(self.config.session_id, limit)
        self.status_text = getattr(self.chat_service, "last_status", self.status_text)
        if len(messages) != self._last_message_count:
            if self.scroll_offset == 0:
                self.scroll_offset = 0
            self._last_message_count = len(messages)
        return messages

    def draw(self, surface: pygame.Surface) -> None:
        if not self.visible:
            self._draw_hidden_hint(surface)
            return

        panel = self._panel_rect(surface)
        overlay = pygame.Surface((panel.width, panel.height), pygame.SRCALPHA)
        overlay.fill((8, 12, 20, 206))
        pygame.draw.rect(overlay, (92, 116, 154, 230), overlay.get_rect(), width=2, border_radius=8)
        surface.blit(overlay, panel)

        surface.blit(self.title_font.render(self.config.title, True, (240, 244, 252)), (panel.x + 10, panel.y + 8))
        status = self._trim(self.status_text or "Session chat ready.", 26)
        surface.blit(self.small_font.render(status, True, (188, 199, 220)), (panel.right - 160, panel.y + 10))

        hint = "Wheel to scroll" if self.scroll_offset == 0 else f"Older +{self.scroll_offset}"
        surface.blit(self.small_font.render(hint, True, (142, 154, 180)), (panel.right - 94, panel.y + 25))

        messages = self.recent_messages(12)
        lines = self._wrapped_chat_lines(messages, panel.width - 20)
        visible_count = 5
        max_scroll = max(0, len(lines) - visible_count)
        self.scroll_offset = max(0, min(self.scroll_offset, max_scroll))
        start = max(0, len(lines) - visible_count - self.scroll_offset)
        visible_lines = lines[start:start + visible_count]

        start_y = panel.y + 44
        for index, (sender, text, is_continuation) in enumerate(visible_lines):
            y = start_y + index * 16
            if is_continuation:
                surface.blit(self.small_font.render(text, True, (240, 244, 252)), (panel.x + 78, y))
                continue
            sender_surface = self.small_font.render(f"{sender}:", True, (103, 181, 242))
            surface.blit(sender_surface, (panel.x + 10, y))
            surface.blit(self.small_font.render(text, True, (240, 244, 252)), (panel.x + 78, y))

        input_rect = self._input_rect(surface)
        pygame.draw.rect(surface, (20, 26, 40), input_rect, border_radius=6)
        pygame.draw.rect(surface, (126, 205, 255) if self.input_active else (92, 116, 154), input_rect, width=2, border_radius=6)
        label = self._visible_input_text(input_rect.width - 16) if self.input_text else "Type message..."
        color = (240, 244, 252) if self.input_text else (170, 181, 203)
        surface.blit(self.font.render(label, True, color), (input_rect.x + 8, input_rect.y + 6))
        if self.input_active and self.cursor_visible:
            cursor_x = min(input_rect.x + 8 + self.font.size(label)[0] + 2, input_rect.right - 8)
            pygame.draw.line(surface, (240, 244, 252), (cursor_x, input_rect.y + 5), (cursor_x, input_rect.bottom - 5), 2)

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
        return pygame.Rect(panel.x + 10, panel.bottom - 34, panel.width - 20, 26)

    def _scroll(self, amount: int) -> None:
        self.scroll_offset = max(0, self.scroll_offset + amount)

    def _wrapped_chat_lines(self, messages: list[ChatMessage], max_width: int) -> list[tuple[str, str, bool]]:
        body_width = max(70, max_width - 82)
        lines: list[tuple[str, str, bool]] = []
        for message in messages:
            wrapped = self._wrap_text(message.text, body_width, max_lines=4)
            if not wrapped:
                continue
            for index, line in enumerate(wrapped):
                lines.append((message.sender, line, index > 0))
        return lines

    def _wrap_text(self, text: str, max_width: int, max_lines: int = 3) -> list[str]:
        words = str(text).split()
        if not words:
            return []
        lines: list[str] = []
        current = ""
        for word in words:
            candidate = f"{current} {word}".strip()
            if self.small_font.size(candidate)[0] <= max_width:
                current = candidate
                continue
            if current:
                lines.append(current)
            current = word
            while self.small_font.size(current)[0] > max_width and len(current) > 1:
                split_at = max(1, len(current) - 1)
                while split_at > 1 and self.small_font.size(current[:split_at] + "-")[0] > max_width:
                    split_at -= 1
                lines.append(current[:split_at] + "-")
                current = current[split_at:]
            if len(lines) >= max_lines:
                break
        if current and len(lines) < max_lines:
            lines.append(current)
        if len(lines) > max_lines:
            lines = lines[:max_lines]
        if len(lines) == max_lines and len(" ".join(words)) > len(" ".join(lines)):
            lines[-1] = self._trim_to_width(lines[-1], max_width)
        return lines

    def _trim_to_width(self, text: str, max_width: int) -> str:
        ellipsis = "..."
        trimmed = text
        while trimmed and self.small_font.size(trimmed + ellipsis)[0] > max_width:
            trimmed = trimmed[:-1]
        return (trimmed or text[:1]) + ellipsis

    def _visible_input_text(self, max_width: int) -> str:
        """Show the newest typed characters instead of collapsing to ellipsis."""

        text = self.input_text
        if self.font.size(text)[0] <= max_width:
            return text
        visible = text
        while visible and self.font.size(visible)[0] > max_width:
            visible = visible[1:]
        return visible or text[-1:]

    @staticmethod
    def _trim(text: str, max_chars: int) -> str:
        return text if len(text) <= max_chars else text[: max_chars - 1] + "..."
