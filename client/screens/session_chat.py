from __future__ import annotations

import pygame

from client.components import Button, InputBox, draw_badge, draw_panel, draw_text, draw_wrapped
from client.core import Palette, ScreenName

from .base_screen import BaseScreen


class SessionChatScreen(BaseScreen):
    """Session lobby with chat plus a safe launch button.

    Existing teammate games run as external processes so their graphics/assets
    keep working. Because that means the arcade cannot draw over the game window
    yet, this screen gives players a visible chat space immediately before and
    after launching the selected game.
    """

    def enter(self) -> None:
        super().enter()
        game = self.app.current_game
        self.session_id = self.app.backend.session_id_for_game(game)
        self.message_box = InputBox((602, 626, 390, 44), "Type a session message", self.app.fonts.body, max_length=120)
        self.inputs = [self.message_box]
        self.buttons = [
            Button((30, 626, 210, 44), "Launch Game", self.launch_game, self.app.fonts.button, bg=Palette.ACCENT, hover=Palette.ACCENT_HOVER),
            Button((258, 626, 190, 44), "Back to Details", lambda: self.app.navigate(ScreenName.GAME_DETAILS), self.app.fonts.button),
            Button((1012, 626, 158, 44), "Send", self.send_message, self.app.fonts.button, bg=Palette.ACCENT, hover=Palette.ACCENT_HOVER),
        ]
        if not self.app.backend.get_chat_preview(self.session_id, 1):
            self.app.backend.add_chat_message(self.session_id, "Arcade Host", "Session chat is open. Players can coordinate before launching.")

    def launch_game(self) -> None:
        game = self.app.current_game
        if game is None:
            self.app.show_message("Choose a game before launching.", Palette.WARNING)
            return
        message = self.app.backend.launch_game(self.app.current_player, game)
        self.app.show_message(message, Palette.SUCCESS if game.playable else Palette.WARNING)

    def send_message(self) -> None:
        text = self.message_box.text.strip()
        if not text:
            self.app.show_message("Type a message before sending.", Palette.WARNING)
            return
        sender = self.app.current_player.display_name if self.app.current_player else "Guest"
        self.app.backend.add_chat_message(self.session_id, sender, text)
        self.message_box.text = ""
        self.app.show_message("Message sent to session chat.", Palette.SUCCESS)

    def handle_event(self, event: pygame.event.Event) -> None:
        super().handle_event(event)
        result = self.message_box.handle_event(event)
        if result == "enter":
            self.send_message()

    def draw(self) -> None:
        game = self.app.current_game
        if game is None:
            self.page_title("Session Lobby", "Choose a game from Browse to open its session lobby.")
            self.draw_message(710)
            return

        self.page_title("Session Lobby", "Chat with players in this game session, then launch when everyone is ready.")
        left = pygame.Rect(30, 154, 520, 438)
        right = pygame.Rect(580, 154, 590, 438)
        draw_panel(self.app.screen, left)
        draw_panel(self.app.screen, right)

        art = pygame.Rect(left.x + 18, left.y + 18, left.width - 36, 132)
        pygame.draw.rect(self.app.screen, game.color, art, border_radius=8)
        pygame.draw.rect(self.app.screen, Palette.BORDER, art, width=2, border_radius=8)
        draw_text(self.app.screen, game.title, self.app.fonts.subheading, Palette.TEXT, left.x + 20, left.y + 170, max_width=left.width - 40)
        draw_text(self.app.screen, f"{game.genre} | {game.creator}", self.app.fonts.small, Palette.ACCENT, left.x + 20, left.y + 204, max_width=left.width - 40)
        draw_wrapped(self.app.screen, game.description, self.app.fonts.small, Palette.MUTED, pygame.Rect(left.x + 20, left.y + 236, left.width - 40, 92), max_lines=4)
        draw_badge(self.app.screen, "Ready to launch" if game.playable else "Not connected yet", pygame.Rect(left.x + 20, left.y + 346, 170, 30), self.app.fonts.small, Palette.SUCCESS if game.playable else Palette.WARNING)
        draw_text(self.app.screen, f"Session: {self.session_id}", self.app.fonts.small, Palette.MUTED, left.x + 20, left.y + 392, max_width=left.width - 40)

        draw_text(self.app.screen, "Game Session Chat", self.app.fonts.subheading, Palette.TEXT, right.x + 18, right.y + 18)
        draw_wrapped(self.app.screen, "Messages stay local for this demo and keep only the most recent entries for this session.", self.app.fonts.small, Palette.MUTED, pygame.Rect(right.x + 18, right.y + 55, right.width - 36, 48), max_lines=2)
        messages = self.app.backend.get_chat_preview(self.session_id, 8)
        if not messages:
            draw_text(self.app.screen, "No messages yet.", self.app.fonts.small, Palette.MUTED, right.x + 18, right.y + 120)
        for index, message in enumerate(messages[-8:]):
            row_y = right.y + 112 + index * 38
            row = pygame.Rect(right.x + 16, row_y, right.width - 32, 32)
            pygame.draw.rect(self.app.screen, Palette.PANEL_ALT, row, border_radius=8)
            draw_text(self.app.screen, f"[{message.timestamp}] {message.sender}", self.app.fonts.tiny, Palette.ACCENT, row.x + 10, row.y + 5, max_width=180)
            draw_text(self.app.screen, message.text, self.app.fonts.small, Palette.TEXT, row.x + 200, row.y + 6, max_width=row.width - 210)

        self.message_box.draw(self.app.screen)
        for button in self.buttons:
            button.draw(self.app.screen)
        self.draw_message(710)
