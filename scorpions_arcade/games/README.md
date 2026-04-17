# Games Folder

Place uploaded team games here, one folder per game.

Recommended shape:

```text
scorpions_arcade/games/
  scorpions_arena/
    __init__.py
    main.py
  snake_test/              # TEMP TEST GAME - SAFE TO DELETE LATER
    __init__.py
    README.md
    main.py
  sky_raiders/
    __init__.py
    main.py
```

Each connected game should expose:

```python
def run_game(player_info=None, session_info=None):
    ...
    return {"ok": True, "message": "Returned to arcade."}
```

Important notes:

- Do not call `sys.exit()` from a child game; return to the arcade instead.
- If a child game uses Pygame, be careful with `pygame.quit()` because it can
  shut down the launcher too. Prefer cleaning up only game-owned state.
- Add the game's module path to
  `scorpions_arcade/services/game_launch_registry.py`.
- Temporary test games should stay isolated the same way. To remove Snake Test,
  delete `scorpions_arcade/games/snake_test/`, remove its registry block, and
  remove its single mock catalog row in `scorpions_arcade/data/mock_games.py`.
- TODO(C++): Use `session_info["session_id"]`, `session_info["server_host"]`,
  and `session_info["server_port"]` after the C++ multiplayer server exists.
