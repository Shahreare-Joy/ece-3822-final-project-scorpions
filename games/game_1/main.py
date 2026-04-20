from __future__ import annotations

"""Game 1 placeholder.

This folder is reserved for one of the four final team games.

TODO(GAME 1): Replace this placeholder with the real team game. Keep the public
entry point as run_game(player=None, session_info=None) so the arcade launcher
can call it through client/services/game_launch_service.py.
"""


def run_game(player: object = None, session_info: object = None) -> dict[str, object]:
    _ = (player, session_info)
    return {"ok": False, "message": "Game 1 is reserved for a team game and is not connected yet."}
