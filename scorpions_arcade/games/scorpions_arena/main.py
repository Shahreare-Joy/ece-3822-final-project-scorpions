from __future__ import annotations


def run_game(player_info: dict[str, object] | None = None, session_info: dict[str, object] | None = None) -> dict[str, object]:
    """Starter entry point for the connected playable team game.

    TODO(GAME): Replace this demo function with the real playable game loop.
    TODO(C++): Use session_info for session_id, server_host, and server_port
    after the multiplayer server exists.

    Important: return control to the arcade when the game exits. Avoid calling
    sys.exit() from a child game; return a result dictionary instead.
    """

    player_info = player_info or {}
    session_info = session_info or {}
    player_name = player_info.get("display_name", "Guest")
    session_id = session_info.get("session_id", "local-demo-session")
    print(f"[Scorpions Arena] Demo launch for {player_name} in {session_id}.")
    return {"ok": True, "message": f"Scorpions Arena demo returned control for {player_name}."}

