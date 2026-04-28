from __future__ import annotations

"""Team game launch registry.

Purpose:
    Keep all game-folder launch metadata in one file so UI screens never
    hardcode paths. Each team game should follow this folder convention:

        games/<folder_name>/code/game/main.py

How teammates add their game:
    1. Paste the full game folder into `games/game_2/`, `games/game_3/`, etc.
    2. Make sure the runnable file is `code/game/main.py`.
    3. By default, the launcher runs `main.py` as a subprocess with the working
       directory set to `games/<folder_name>/code/game/`.
    4. Optional: if a teammate later adds a clean
       `run_game(player_info=None, session_info=None)` adapter, set
       `launch_mode="adapter"` for that game.

TODO(C++ HANDOFF):
    Later, pass real `session_id`, `server_host`, `server_port`, and player
    token values from the C++ multiplayer server into each game.

Project 02 reference:
    The older project passed `--server`, `--port`, and `--serializer` into the
    game client. This registry keeps that pattern, but uses only this class
    project's approved local/tunneled ports.
"""

from dataclasses import dataclass
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
TEAM_GAME_ENTRY = Path("code") / "game" / "main.py"


@dataclass(frozen=True)
class GameLaunchTarget:
    """Launch metadata for one catalog game."""

    game_id: str
    title: str
    creator: str
    folder_name: str
    playable: bool = True
    entry_relative_path: Path = TEAM_GAME_ENTRY
    function_name: str = "run_game"
    # Use subprocess by default because pasted Pygame games often rely on their
    # own working directory, sys.path, pygame lifecycle, and relative assets.
    launch_mode: str = "subprocess"  # "subprocess", "adapter", or "auto"
    script_args: tuple[str, ...] = ("{username}",)
    not_connected_message: str = "This game folder is not connected yet."
    notes: str = ""

    @property
    def folder_path(self) -> Path:
        return PROJECT_ROOT / "games" / self.folder_name

    @property
    def entry_path(self) -> Path:
        return self.folder_path / self.entry_relative_path

    def exists(self) -> bool:
        return self.folder_path.exists()

    def has_entry_file(self) -> bool:
        return self.entry_path.exists()

    def missing_reason(self) -> str:
        if not self.exists():
            return f"Missing folder: games/{self.folder_name}/"
        if not self.has_entry_file():
            return f"Missing entry file: games/{self.folder_name}/{self.entry_relative_path.as_posix()}"
        if not self.playable:
            return self.not_connected_message
        return ""

    def render_script_args(self, player_info: dict[str, object], session_info: dict[str, object]) -> list[str]:
        values = {
            "username": str(player_info.get("username", "guest")),
            "display_name": str(player_info.get("display_name", "Guest")),
            "session_id": str(session_info.get("session_id", "")),
            "server_host": str(session_info.get("server_host", "localhost")),
            "server_port": str(session_info.get("server_port", "50068")),
            "serializer": str(session_info.get("serializer", "text")),
            "game_id": self.game_id,
        }
        return [arg.format(**values) for arg in self.script_args]


# Keep launch wiring here instead of hardcoding it inside UI screen files.
# The visible catalog still uses friendly IDs/titles, but each target maps to a
# standard team folder under top-level `games/`.
GAME_LAUNCH_TARGETS: dict[str, GameLaunchTarget] = {
    "scorpions-arena": GameLaunchTarget(
        game_id="scorpions-arena",
        title="Fruit Drop Rush",
        creator="Shahreare Joy",
        folder_name="game_1",
        script_args=("{username}", "--server", "{server_host}", "--port", "{server_port}", "--serializer", "{serializer}"),
        not_connected_message="Game 1 is not pasted into games/game_1/code/game/main.py yet.",
        notes="Team game 1. Map-based fruit collection game.",
    ),
    "sky-raiders": GameLaunchTarget(
        game_id="sky-raiders",
        title="Escape the City",
        creator="Team Member 2",
        folder_name="game_2",
        script_args=("{username}", "--server", "{server_host}", "--port", "{server_port}", "--serializer", "{serializer}"),
        not_connected_message="Game 2 is not pasted into games/game_2/code/game/main.py yet.",
    ),
    "turbo-sprint": GameLaunchTarget(
        game_id="turbo-sprint",
        title="Forgotten",
        creator="Team Member 3",
        folder_name="game_3",
        script_args=("{username}", "--server", "{server_host}", "--port", "{server_port}", "--serializer", "{serializer}"),
        not_connected_message="Game 3 is not pasted into games/game_3/code/game/main.py yet.",
    ),
    "crystal-run": GameLaunchTarget(
        game_id="crystal-run",
        title="Mystical Bamboo",
        creator="Team Member 4",
        folder_name="game_4",
        not_connected_message="Game 4 is not pasted into games/game_4/code/game/main.py yet.",
    ),
    # TEMP TEST GAME - SAFE TO DELETE LATER:
    # Snake does not follow the uploaded team folder convention because it is
    # just a tiny local test harness.
    "snake-test": GameLaunchTarget(
        game_id="snake-test",
        title="Snake Test Lab",
        creator="Local Test Harness",
        folder_name="game_5",
        entry_relative_path=Path("main.py"),
        launch_mode="adapter",
        script_args=(),
        not_connected_message="Snake Test is temporary and is not connected right now.",
        notes="TEMP TEST GAME - SAFE TO DELETE LATER.",
    ),
}


def get_launch_target(game_id: str) -> GameLaunchTarget | None:
    """Return launch metadata for a catalog game."""

    return GAME_LAUNCH_TARGETS.get(game_id)


def get_team_launch_targets() -> list[GameLaunchTarget]:
    """Return the four team-game folder targets."""

    return [GAME_LAUNCH_TARGETS[key] for key in ("scorpions-arena", "sky-raiders", "turbo-sprint", "crystal-run")]


def discover_team_game_status() -> dict[str, dict[str, object]]:
    """Return folder/entry status for setup screens or debugging.

    TODO(UI): A future Settings screen can call this to show which teammates'
    folders are pasted correctly.
    """

    status: dict[str, dict[str, object]] = {}
    for target in get_team_launch_targets():
        status[target.game_id] = {
            "folder": target.folder_path.as_posix(),
            "entry": target.entry_path.as_posix(),
            "working_directory": target.entry_path.parent.as_posix(),
            "launch_mode": target.launch_mode,
            "folder_exists": target.exists(),
            "entry_exists": target.has_entry_file(),
            "ready": target.exists() and target.has_entry_file() and target.playable,
            "message": target.missing_reason() or "Ready to launch.",
        }
    return status
