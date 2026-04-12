"""
main.py — ECE 3822 Arcade Pygame Client
========================================
Run with:  python main.py

Connects to:
  • Python Platform Server  localhost:5000  (profiles, leaderboards, chat)
  • C++ Game Server         localhost:9000  (live gameplay via game subprocesses)

Runs in OFFLINE DEMO MODE automatically if the platform server is unreachable.

File layout:
  main.py           ← this file
  screens.py        ← all UI screens
  widgets.py        ← Button, InputBox, ScrollPanel, etc.
  api_client.py     ← HTTP calls to platform server
  constants.py      ← colors, layout, screen IDs
  game_launcher.py  ← discovers + launches games from games/ folder

  games/
    dungeon_crawler/
      main.py       ← your real game goes here
      config.json   ← optional metadata
    space_shooter/
      main.py
      config.json
    ...
"""

import sys
import subprocess
import pygame

import api_client as api
from constants import *
from widgets import toast, scanline_overlay
from screens import (
    AppState,
    draw_top_bar, draw_sidebar, sidebar_click,
    LoginScreen, LobbyScreen, GameSelectScreen, LeaderboardScreen,
    ProfileScreen, SearchScreen, ChatScreen, LaunchingScreen,
)
from game_launcher import discover_games, launch_game, is_running, stop_game, create_stub_games


class App:
    """
    Top-level application controller.

    Screen transitions happen via string IDs returned from each screen's
    handle_event(). The currently running game subprocess is tracked so
    the arcade can detect when the player quits and return them to the lobby.
    """

    def __init__(self):
        pygame.init()
        pygame.display.set_caption(TITLE)
        self.screen = pygame.display.set_mode((WINDOW_W, WINDOW_H))
        self.clock  = pygame.time.Clock()
        self.state  = AppState()

        # Check server connectivity once on startup
        self.state.online = api.ping()
        if not self.state.online:
            print("[arcade] Platform server unreachable — running in offline demo mode")

        # Discover games folder; create stubs if empty
        games = discover_games()
        if not games:
            print("[arcade] No games found — creating stub placeholders in games/")
            create_stub_games()
            games = discover_games()

        # Merge discovered local games into the catalog so the UI shows them
        self.state.local_games = games
        print(f"[arcade] Found {len(games)} local game(s): {list(games.keys())}")

        # Build all screens (share AppState)
        self.scenes: dict = {
            SCREEN_LOGIN:        LoginScreen(self.state),
            SCREEN_LOBBY:        LobbyScreen(self.state),
            SCREEN_GAME_SELECT:  GameSelectScreen(self.state),
            SCREEN_LEADERBOARD:  LeaderboardScreen(self.state),
            SCREEN_PROFILE:      ProfileScreen(self.state),
            SCREEN_SEARCH:       SearchScreen(self.state),
            SCREEN_CHAT:         ChatScreen(self.state),
            SCREEN_LAUNCHING:    LaunchingScreen(self.state),
        }

        self.current       = SCREEN_LOGIN
        self._show_nav     = False
        self._game_proc: subprocess.Popen | None = None  # running game subprocess

    # ── Screen transition ─────────────────────────────────────────────────────

    def _transition(self, target: str):
        if not target or target == self.current:
            return
        # Kill any running game if going back to a menu screen
        if target != SCREEN_LAUNCHING and self._game_proc:
            stop_game(self._game_proc)
            self._game_proc = None

        self.current   = target
        self._show_nav = target != SCREEN_LOGIN

        # Mark data stale so screens re-fetch
        scene = self.scenes.get(target)
        if hasattr(scene, "_loaded"):
            scene._loaded = False

    # ── Launch a game subprocess ──────────────────────────────────────────────

    def _do_launch(self):
        """Called when LaunchingScreen becomes active."""
        gid = self.state.current_game
        try:
            self._game_proc = launch_game(
                gid,
                username=self.state.username,
                server_host=api.GAME_SERVER_HOST,
                server_port=api.GAME_SERVER_PORT,
            )
            toast.show(f"Game started!", GREEN)
        except FileNotFoundError as e:
            toast.show(str(e)[:60], RED)
            self._transition(SCREEN_GAME_SELECT)
        except Exception as e:
            toast.show(f"Launch error: {e}"[:60], RED)
            self._transition(SCREEN_GAME_SELECT)

    # ── Main loop ─────────────────────────────────────────────────────────────

    def run(self):
        running      = True
        prev_screen  = None

        while running:
            self.clock.tick(FPS)

            # Detect when we first enter LAUNCHING screen → spawn subprocess
            if self.current == SCREEN_LAUNCHING and prev_screen != SCREEN_LAUNCHING:
                self._do_launch()
            prev_screen = self.current

            # If a game was running and has now exited → return to lobby
            if self.current == SCREEN_LAUNCHING and self._game_proc:
                if not is_running(self._game_proc):
                    self._game_proc = None
                    toast.show("Game ended — back to arcade", CYAN)
                    self._transition(SCREEN_LOBBY)

            # ── Events ────────────────────────────────────────────────────────
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    break

                # Global hotkeys (F1-F6)
                if event.type == pygame.KEYDOWN:
                    hotkeys = {
                        pygame.K_F1: SCREEN_LOBBY,
                        pygame.K_F2: SCREEN_GAME_SELECT,
                        pygame.K_F3: SCREEN_LEADERBOARD,
                        pygame.K_F4: SCREEN_PROFILE,
                        pygame.K_F5: SCREEN_SEARCH,
                        pygame.K_F6: SCREEN_CHAT,
                    }
                    if event.key in hotkeys:
                        self._transition(hotkeys[event.key])
                        continue

                # Sidebar nav click
                if self._show_nav and event.type == pygame.MOUSEBUTTONDOWN:
                    dest = sidebar_click(event.pos, self.current)
                    if dest:
                        self._transition(dest)
                        continue

                # Delegate to active screen
                result = self.scenes[self.current].handle_event(event)
                if result:
                    self._transition(result)

            # ── Update ────────────────────────────────────────────────────────
            self.scenes[self.current].update()

            # ── Draw ──────────────────────────────────────────────────────────
            self.screen.fill(BG)

            if self._show_nav:
                draw_sidebar(self.screen, self.current)

            self.scenes[self.current].draw(self.screen)

            if self._show_nav:
                draw_top_bar(self.screen, self.state)

            toast.draw(self.screen)
            scanline_overlay(self.screen, alpha=12)
            pygame.display.flip()

        # Cleanup
        stop_game(self._game_proc)
        pygame.quit()
        sys.exit(0)


def main():
    App().run()


if __name__ == "__main__":
    main()
