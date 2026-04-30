# Team Games

Each team member's game should live in its own folder:

```text
games/
  game_1/
  game_2/
  game_3/
  game_4/
  game_5/   # TEMP Snake test game, safe to delete later
```

For the four team games, use this exact runnable-file convention:

```text
games/<game_id>/code/game/main.py
```

Examples:

```text
games/game_1/code/game/main.py
games/game_2/code/game/main.py
games/game_3/code/game/main.py
games/game_4/code/game/main.py
```

Default launch behavior:

- The arcade runs `code/game/main.py` as a subprocess.
- The subprocess working directory is `code/game/`.
- Relative paths like `../../graphics` should continue to work.

Optional clean adapter inside `main.py`:

```python
def run_game(player_info=None, session_info=None):
    ...
```

If you add this adapter, update only `client/services/game_launch_registry.py`
to set `launch_mode="adapter"` for your game.

Important teammate checklist:

1. Paste your full folder into `games/game_2/`, `games/game_3/`, or `games/game_4/`.
2. Keep the runnable file at `code/game/main.py`.
3. Keep supporting folders such as `graphics/` inside the game folder.
4. Do not edit UI screen files to launch your game.
5. If your game needs special command-line args, update only
   `client/services/game_launch_registry.py`.

`game_5` currently contains the temporary Snake game used to test launcher
handoff. It is not intended to be the final project game unless the team chooses
to keep it.

TODO(GAME INTEGRATION): The Python client should launch games through
`client/services/game_launch_service.py`, and the future C++ server should pass
session information for multiplayer gameplay.
