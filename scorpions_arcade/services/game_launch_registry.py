from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class GameLaunchTarget:
    """Launch metadata for one catalog game.

    module_path should point to a Python module with a run_game function.
    connected=False keeps placeholder games visible in the arcade without
    crashing when a player presses Play.
    """

    game_id: str
    module_path: str
    function_name: str = "run_game"
    connected: bool = True
    not_connected_message: str = "This game is not connected to the launcher yet."


# Keep launch wiring here instead of hardcoding it inside UI screen files.
# TODO(TEAM): Add your uploaded games here after each game folder exposes
# run_game(player_info=None, session_info=None).
GAME_LAUNCH_TARGETS: dict[str, GameLaunchTarget] = {
    "scorpions-arena": GameLaunchTarget(
        game_id="scorpions-arena",
        module_path="scorpions_arcade.games.scorpions_arena.main",
        connected=True,
    ),
    # TEMP TEST GAME - SAFE TO DELETE LATER:
    # Remove this "snake-test" block and the mock catalog row in
    # scorpions_arcade/data/mock_games.py when Snake is no longer needed.
    "snake-test": GameLaunchTarget(
        game_id="snake-test",
        module_path="scorpions_arcade.games.snake_test.main",
        connected=True,
        not_connected_message="Snake Test is temporary and is not connected right now.",
    ),
    "sky-raiders": GameLaunchTarget(
        game_id="sky-raiders",
        module_path="scorpions_arcade.games.sky_raiders_placeholder.main",
        connected=False,
        not_connected_message="Sky Raiders has a folder stub, but its real run_game entry point is not connected yet.",
    ),
}
