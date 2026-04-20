# Game Launching Scaffold

## Flow

```text
main.py
  -> Scorpions Arcade UI
  -> Game Details Play / Launch button
  -> MockArcadeBackend.launch_game(...)
  -> GameLaunchService.launch(...)
  -> game launch registry
  -> games/<game_folder>/code/game/main.py
  -> game returns or writes optional result payload
  -> SessionResultService.handle_launch_result(...)
  -> platform_server/session_results.py
  -> future leaderboard/history/profile/persistence updates
  -> return control to arcade
```

## Required Team Folder Convention

Each teammate should paste their game into one of these folders:

```text
games/
  game_1/
    code/
      game/
        main.py
    graphics/
  game_2/
    code/
      game/
        main.py
  game_3/
    code/
      game/
        main.py
  game_4/
    code/
      game/
        main.py
```

The launcher automatically builds the path:

```text
games/<folder_name>/code/game/main.py
```

The registry lives in:

```text
client/services/game_launch_registry.py
```

## Launch Approach

The launcher uses subprocess launching by default for pasted team games.

Why:

- It preserves the game's own working directory.
- It keeps relative asset paths such as `../../graphics` working.
- It isolates copied Pygame event loops from the arcade.
- It avoids problems if a teammate's game calls `pygame.quit()` or `sys.exit()`.

Optional clean adapter:

```python
def run_game(player_info=None, session_info=None):
    ...
```

If a game adds this adapter later, set `launch_mode="adapter"` for that game in
`client/services/game_launch_registry.py`.

The subprocess starts with its working directory set to `code/game/`, which
matches the current team-folder convention.

## Placeholder Game Behavior

If a teammate has not pasted their folder yet, pressing Play shows a clear
message such as:

```text
Missing entry file: games/game_2/code/game/main.py
```

The launcher should not crash when a game is missing.

## Completed Session Result Flow

The result pipeline is scaffolded now so the team does not need to redesign the
launcher later.

Future adapter-style games can return a dictionary:

```python
def run_game(player_info=None, session_info=None):
    # game loop here
    return {
        "message": "Game finished.",
        "session_result": {
            "player_id": player_info["username"],
            "game_id": session_info["game_id"],
            "session_id": session_info["session_id"],
            "score": 18420,
            "outcome": "Win",
            "duration_seconds": 315,
            "metadata": {"level": 4, "coins": 88}
        }
    }
```

Subprocess-style games can write JSON to the file path provided by the launcher:

```python
import json
import os

result_path = os.environ.get("SCORPIONS_RESULT_PATH")
if result_path:
    with open(result_path, "w", encoding="utf-8") as file:
        json.dump({
            "score": 18420,
            "outcome": "Win",
            "duration_seconds": 315,
            "metadata": {"level": 4}
        }, file)
```

Files involved:

- `client/services/game_launch_service.py` captures adapter returns or
  subprocess result JSON.
- `client/services/session_result_service.py` bridges the UI launcher
  to the platform result processor.
- `platform_server/session_results.py` is the central future backend processor.
- `client/models/session_result.py` and `client/services/session_result_service.py`
  document the top-level client API shape for the final structure.

TODO(RESULTS): The final backend must validate results server-side, reject
duplicate submissions, update leaderboards/history/profile stats, and persist
accepted results.

## Temporary Test Game

`snake-test` is a TEMP TEST GAME and SAFE TO DELETE LATER. It exists only to
verify that the arcade Play button can hand off to a game folder and then return
control to the launcher.

To remove it later:

1. Delete `games/game_5/`.
2. Remove the `snake-test` block in `client/services/game_launch_registry.py`.
3. Remove the `snake-test` row in `client/data/mock_games.py`.

If the folder is deleted before the registry/catalog cleanup happens, the
launcher service should still fail safely with a missing entry-point message.

## Future C++ Handoff

The launch service currently builds a local demo `session_info` dictionary. Your
team should later replace those values with server-owned values:

- `session_id`
- `server_host`
- `server_port`
- player token
- match/lobby settings

TODO(C++): request these values from the C++ multiplayer server before calling
the game entry point.
