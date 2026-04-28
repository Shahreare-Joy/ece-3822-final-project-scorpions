from __future__ import annotations

"""One-command project verification for Scorpions Arcade.

Purpose:
    Give the team a safe pre-merge/pre-submission check that verifies the
    current scaffold still imports, the UI can render in headless mode, the
    synthetic dataset is present, and the team-game launcher registry is sane.

Important:
    This is not a replacement for Kevin's final tests/benchmarks. It is a
    lightweight integration smoke test. It checks that the project is wired
    together, the large dataset is present, and the connected game entries are
    launch-ready.

Run from the project root:
    python tools/verify_project.py
"""

import ast
import importlib
import json
import os
import sys
from pathlib import Path
from typing import Iterable


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

PYTHON_SCAN_ROOTS = [
    "client",
    "platform_server",
    "datastructures",
    "algorithms",
    "benchmarks",
    "tests",
    "games",
]

EXPECTED_DATASET_COUNTS = {
    "players.json": 10_000,
    "sessions.json": 100_000,
    "chat_messages.json": 50_000,
    "game_catalog.json": 100,
}


def heading(title: str) -> None:
    print(f"\n== {title} ==")


def iter_python_files() -> Iterable[Path]:
    yield PROJECT_ROOT / "main.py"
    for root_name in PYTHON_SCAN_ROOTS:
        root = PROJECT_ROOT / root_name
        if not root.exists():
            continue
        for path in root.rglob("*.py"):
            if "__pycache__" not in path.parts:
                yield path


def check_syntax() -> None:
    heading("Syntax")
    count = 0
    for path in sorted(iter_python_files()):
        ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        count += 1
    print(f"OK parsed {count} Python files")


def check_imports() -> None:
    heading("Imports")
    modules = [
        "main",
        "client.main",
        "client.core.app",
        "client.core.screen_registry",
        "client.services.arcade_backend",
        "client.services.game_launch_service",
        "client.services.session_result_service",
        "client.data.mock_games",
        "platform_server.server",
        "platform_server.data_ingest",
        "platform_server.session_results",
        "platform_server.session_manager",
    ]
    for module_name in modules:
        importlib.import_module(module_name)
        print(f"OK import {module_name}")


def check_dataset() -> None:
    heading("Synthetic Dataset")
    dataset_root = PROJECT_ROOT / "data" / "synthetic_dataset"
    if not dataset_root.exists():
        raise AssertionError("Missing data/synthetic_dataset. Run data/generate_dataset.py.")

    for file_name, minimum in EXPECTED_DATASET_COUNTS.items():
        path = dataset_root / file_name
        if not path.exists():
            raise AssertionError(f"Missing dataset file: {path}")
        data = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(data, list):
            raise AssertionError(f"{file_name} must be a JSON list")
        if len(data) < minimum:
            raise AssertionError(f"{file_name} has {len(data)} records; expected at least {minimum}")
        print(f"OK {file_name}: {len(data):,} records")


def check_catalog_and_launcher() -> None:
    heading("Catalog And Game Launcher")
    from client.data.mock_games import MOCK_GAMES
    from client.services.game_launch_registry import discover_team_game_status

    if len(MOCK_GAMES) < 100:
        raise AssertionError(f"Mock catalog only has {len(MOCK_GAMES)} games; expected 100+")
    print(f"OK mock catalog: {len(MOCK_GAMES)} games")

    status = discover_team_game_status()
    for game_id, info in status.items():
        ready = "ready" if info["ready"] else "not ready yet"
        print(f"{game_id}: {ready} - {info['message']}")

    required_ready = ("scorpions-arena", "sky-raiders", "turbo-sprint")
    missing = [game_id for game_id in required_ready if not status[game_id]["ready"]]
    if missing:
        raise AssertionError(f"Expected at least the first three team games to be ready; missing: {missing}")


def check_thumbnail_assets() -> None:
    heading("Thumbnail Assets")
    thumbnail = PROJECT_ROOT / "client" / "assets" / "thumbnails" / "fruit_drop_rush.png"
    if not thumbnail.exists():
        raise AssertionError("Missing Fruit Drop Rush thumbnail asset.")
    import pygame

    image = pygame.image.load(str(thumbnail))
    if image.get_width() <= 0 or image.get_height() <= 0:
        raise AssertionError("Fruit Drop Rush thumbnail did not load correctly.")
    print(f"OK fruit_drop_rush.png: {image.get_width()}x{image.get_height()}")


def check_demo_accounts_search_and_chat() -> None:
    heading("Demo Accounts, Full Search, And Chat")
    from client.services import MockArcadeBackend

    backend = MockArcadeBackend()
    login = backend.authenticate("shahreare", "has068")
    if not login.success:
        raise AssertionError("Demo login shahreare / has068 should work.")
    duplicate = backend.create_account("shahreare", "Shahreare Again", "has068", "has068", "USA")
    if duplicate.success:
        raise AssertionError("Duplicate username should be rejected.")
    results = backend.search_players("scorpion", 25)
    if len(results) < 25:
        raise AssertionError(f"Full dataset search returned {len(results)} results; expected 25.")
    game = backend.get_game("scorpions-arena")
    session_id = backend.session_id_for_game(game)
    backend.add_chat_message(session_id, "Verifier", "Session chat smoke test.")
    if not backend.get_chat_preview(session_id, 1):
        raise AssertionError("Session chat should return the message that was just added.")
    print(f"OK demo login, duplicate rejection, {len(results)} search results, and session chat")


def check_pygame_ui() -> None:
    heading("Pygame UI Smoke Test")
    os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
    os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

    import pygame

    from client.core import ScreenName
    from client.core.app import ArcadeApp

    pygame.init()
    try:
        app = ArcadeApp()
        app.current_player = app.backend.get_player("shahreare")
        for screen_name in [
            ScreenName.WELCOME,
            ScreenName.LOGIN,
            ScreenName.CREATE_ACCOUNT,
            ScreenName.HOME,
            ScreenName.BROWSE,
            ScreenName.SESSION_CHAT,
            ScreenName.PROFILE,
            ScreenName.LEADERBOARD,
            ScreenName.SEARCH,
            ScreenName.HISTORY,
            ScreenName.SETTINGS,
        ]:
            app.navigate(screen_name)
            app.screens[app.current_screen].update(0.016)
            app.draw_background()
            app.draw_nav()
            app.screens[app.current_screen].draw()
            print(f"OK rendered {screen_name.value}")

        first_game = app.backend.get_games()[0]
        app.open_game(first_game)
        app.screens[app.current_screen].draw()
        print(f"OK rendered game_details for {first_game.game_id}")
    finally:
        pygame.quit()


def main() -> None:
    check_syntax()
    check_imports()
    check_dataset()
    check_catalog_and_launcher()
    check_thumbnail_assets()
    check_demo_accounts_search_and_chat()
    check_pygame_ui()
    print("\nAll project verification checks passed.")


if __name__ == "__main__":
    main()
