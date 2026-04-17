from __future__ import annotations

import sys

import pygame

from scorpions_arcade.components import Button, build_nav_buttons, draw_nav_bar, make_fonts
from scorpions_arcade.core import AppState, FPS, HEIGHT, TITLE, WIDTH, Palette, ScreenName, draw_background_grid
from scorpions_arcade.core.screen_registry import create_screens
from scorpions_arcade.models import Game, Player
from scorpions_arcade.services import MockArcadeBackend


class ArcadeApp:
    """Main Pygame application shell and router.

    This file owns startup, navigation, and the event loop. It should not grow
    backend/data-structure logic; add that work under services/placeholders.
    """

    def __init__(self) -> None:
        pygame.init()
        pygame.font.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption(TITLE)
        self.clock = pygame.time.Clock()
        self.fonts = make_fonts()
        self.backend = MockArcadeBackend()
        self.state = AppState()

        self.screens = create_screens(self)
        self.nav_buttons: list[Button] = []
        self.navigate(ScreenName.WELCOME)

    @property
    def running(self) -> bool:
        return self.state.running

    @running.setter
    def running(self, value: bool) -> None:
        self.state.running = value

    @property
    def current_player(self) -> Player | None:
        return self.state.current_player

    @current_player.setter
    def current_player(self, value: Player | None) -> None:
        self.state.current_player = value

    @property
    def current_game(self) -> Game | None:
        return self.state.current_game

    @current_game.setter
    def current_game(self, value: Game | None) -> None:
        self.state.current_game = value

    @property
    def current_screen(self) -> ScreenName:
        return self.state.current_screen

    @current_screen.setter
    def current_screen(self, value: ScreenName) -> None:
        self.state.current_screen = value

    @property
    def message(self) -> str:
        return self.state.message

    @message.setter
    def message(self, value: str) -> None:
        self.state.message = value

    @property
    def message_color(self) -> tuple[int, int, int]:
        return self.state.message_color

    @message_color.setter
    def message_color(self, value: tuple[int, int, int]) -> None:
        self.state.message_color = value

    def navigate(self, screen_name: ScreenName, message: str = "", color: tuple[int, int, int] = Palette.MUTED) -> None:
        self.current_screen = screen_name
        self.message = message
        self.message_color = color
        self.build_nav()
        self.screens[self.current_screen].enter()

    def open_game(self, game: Game) -> None:
        self.current_game = game
        self.navigate(ScreenName.GAME_DETAILS)

    def show_message(self, message: str, color: tuple[int, int, int] = Palette.MUTED) -> None:
        self.message = message
        self.message_color = color

    def logout(self) -> None:
        self.current_player = None
        self.current_game = None
        self.navigate(ScreenName.WELCOME, "You have been logged out.", Palette.MUTED)

    def quit(self) -> None:
        self.running = False

    def build_nav(self) -> None:
        self.nav_buttons = []
        if self.current_player is None or self.current_screen in {ScreenName.WELCOME, ScreenName.LOGIN, ScreenName.CREATE_ACCOUNT}:
            return

        self.nav_buttons = build_nav_buttons(self.current_screen, self.navigate, self.logout, self.fonts)

    def draw_background(self) -> None:
        draw_background_grid(self.screen)

    def draw_nav(self) -> None:
        draw_nav_bar(self.screen, self.nav_buttons, self.fonts, self.backend.connected)

    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame.QUIT:
            self.quit()
            return
        for button in self.nav_buttons:
            button.handle_event(event)
        self.screens[self.current_screen].handle_event(event)

    def run(self) -> None:
        while self.running:
            dt = self.clock.tick(FPS)
            for event in pygame.event.get():
                self.handle_event(event)
            self.screens[self.current_screen].update(dt)
            self.draw_background()
            self.draw_nav()
            self.screens[self.current_screen].draw()
            pygame.display.flip()

        pygame.quit()
        sys.exit()


def main() -> None:
    ArcadeApp().run()
