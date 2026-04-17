# Team Games

Each team member's game should live in its own folder:

```text
games/
  game_1/
  game_2/
  game_3/
  game_4/
```

Every connected game should expose:

```python
def run_game(player):
    ...
```

TODO(GAME INTEGRATION): The Python client should launch games through
`client/services/game_launch_service.py`, and the future C++ server should pass
session information for multiplayer gameplay.
