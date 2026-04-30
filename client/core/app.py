from __future__ import annotations

import argparse
import sys

import pygame

from client.components import Button, build_nav_buttons, draw_nav_bar, make_fonts
from client.core import AppState, FPS, HEIGHT, TITLE, WIDTH, Palette, ScreenName, draw_background_grid
from client.core.screen_registry import create_screens
from client.models import Game, Player
from client.runtime_config import RuntimeConfig
from client.services import MockArcadeBackend


class ArcadeApp:
    """Main Pygame application shell and router.

    This file owns startup, navigation, and the event loop. It should not grow
    backend/data-structure logic. UI-facing behavior belongs under
    client/services, while final backend/data-structure work belongs under the
    top-level platform_server/, datastructures/, and algorithms/ folders.
    """

    def __init__(self, config: RuntimeConfig | None = None) -> None:
        pygame.init()
        pygame.font.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption(TITLE)
        self.clock = pygame.time.Clock()
        self.fonts = make_fonts()
        self.config = config or RuntimeConfig.local()
        self.backend = MockArcadeBackend(self.config)
        self.state = AppState()

        self.screens = create_screens(self)
        self.nav_buttons: list[Button] = []
        self.navigate(ScreenName.WELCOME)
        if self.config.is_server_mode:
            if self.backend.local_fallback_active:
                self.show_message("Server Mode requested, but remote platform is unavailable. Using Local Mode fallback.", Palette.WARNING)
            else:
                self.show_message(f"Server Mode configured for {self.config.server_host}:{self.config.platform_port}.", Palette.SUCCESS)

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

    @property
    def profile_player(self) -> Player | None:
        return self.state.profile_player

    @profile_player.setter
    def profile_player(self, value: Player | None) -> None:
        self.state.profile_player = value

    def navigate(self, screen_name: ScreenName, message: str = "", color: tuple[int, int, int] = Palette.MUTED, preserve_profile: bool = False) -> None:
        if screen_name == ScreenName.PROFILE and not preserve_profile:
            self.profile_player = None
        self.current_screen = screen_name
        self.message = message
        self.message_color = color
        self.build_nav()
        self.screens[self.current_screen].enter()

    def open_game(self, game: Game) -> None:
        self.current_game = game
        self.navigate(ScreenName.GAME_DETAILS)

    def open_player_profile(self, player: Player) -> None:
        self.profile_player = player
        self.navigate(ScreenName.PROFILE, f"Viewing {player.display_name}'s profile.", Palette.MUTED, preserve_profile=True)

    def show_message(self, message: str, color: tuple[int, int, int] = Palette.MUTED) -> None:
        self.message = message
        self.message_color = color

    def logout(self) -> None:
        self.current_player = None
        self.profile_player = None
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
        try:
            while self.running:
                dt = self.clock.tick(FPS)
                for event in pygame.event.get():
                    self.handle_event(event)
                self.screens[self.current_screen].update(dt)
                self.draw_background()
                self.draw_nav()
                self.screens[self.current_screen].draw()
                pygame.display.flip()
        finally:
            self.backend.close()
            pygame.quit()
        sys.exit()


def parse_runtime_config(argv: list[str] | None = None) -> RuntimeConfig:
    parser = argparse.ArgumentParser(description="Run Scorpions Arcade in local or server mode.")
    parser.add_argument("--server", help="Server hostname or IP for ECE/server mode.")
    parser.add_argument("--port", type=int, default=50068, help="Python platform server port.")
    parser.add_argument("--game-port", type=int, help="Optional C++ gameplay server port. Defaults to --port.")
    parser.add_argument("--serializer", choices=("text", "json"), default="json", help="Network message format for server mode.")
    args = parser.parse_args(argv)
    if not args.server:
        return RuntimeConfig.local()
    return RuntimeConfig.server(args.server, args.port, args.serializer, gameplay_port=args.game_port)


def main(argv: list[str] | None = None) -> None:
    ArcadeApp(parse_runtime_config(argv)).run()
