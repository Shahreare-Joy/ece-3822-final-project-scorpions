# Snake Test

TEMP TEST GAME - SAFE TO DELETE LATER.

This folder is only here to test the Scorpions Arcade launch flow:

1. Player clicks Play in the arcade UI.
2. `GameLaunchService` imports `scorpions_arcade.games.snake_test.main`.
3. The service calls `run_game(player_info=None, session_info=None)`.
4. Snake runs locally and returns control to the arcade when the player exits.

To remove this test game later:

1. Delete `scorpions_arcade/games/snake_test/`.
2. Remove the `snake-test` block from `scorpions_arcade/services/game_launch_registry.py`.
3. Remove the `snake-test` row from `scorpions_arcade/data/mock_games.py`.

The arcade will still run if this folder is deleted before the registry row is
removed; the launcher service will show a safe missing-entry-point message
instead of crashing.
