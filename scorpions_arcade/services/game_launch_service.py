from __future__ import annotations

from dataclasses import dataclass
from importlib import import_module
from typing import Any, Callable

from scorpions_arcade.integrations import ServerConnectionInfo, ServerSessionRequest
from scorpions_arcade.models import Game, Player
from .game_launch_registry import GAME_LAUNCH_TARGETS, GameLaunchTarget


@dataclass
class LaunchRequest:
    game_id: str
    username: str
    requested_mode: str = "matchmaking"
    session_id: str = "local-demo-session"


@dataclass
class LaunchResult:
    ok: bool
    message: str
    session_id: str = ""
    server_host: str = ""
    server_port: int = 0


class GameLaunchService:
    """Starter launch/handoff layer for playable games.

    This service owns game importing and execution so UI screens never hardcode
    folders or module names. A connected game should expose:

        run_game(player_info=None, session_info=None)

    TODO(C++ LAUNCH): Replace the local demo session values with session_id,
    server_host, server_port, and player token from the multiplayer server.
    """

    def __init__(self, connection: ServerConnectionInfo | None = None) -> None:
        self.connection = connection or ServerConnectionInfo()

    def launch(self, player: Player | None, game: Game) -> LaunchResult:
        username = player.username if player else "guest"
        request = LaunchRequest(game.game_id, username)
        # TODO(C++ LAUNCH): Replace the local LaunchRequest path with a call to
        # CppServerClient.create_or_join_session(ServerSessionRequest(...)).
        # Keep the response mapped into session_info so each game receives the
        # same clean run_game(player_info, session_info) contract.
        _future_server_request = ServerSessionRequest(username=username, game_id=game.game_id, requested_mode=request.requested_mode)
        _ = _future_server_request
        target = GAME_LAUNCH_TARGETS.get(game.game_id)
        if target is None:
            return LaunchResult(False, f"{game.title} is not connected to a game folder yet.")
        if not game.playable or not target.connected:
            return LaunchResult(False, target.not_connected_message)

        run_game = self._load_run_game(target)
        if run_game is None:
            return LaunchResult(False, f"{game.title} is missing a valid {target.function_name}(...) entry point.")

        player_info = self._build_player_info(player)
        session_info = self._build_session_info(request)
        try:
            result = run_game(player_info=player_info, session_info=session_info)
        except Exception as exc:
            return LaunchResult(False, f"{game.title} crashed during launch: {exc}")

        message = self._result_message(game, result)
        return LaunchResult(True, message, session_id=request.session_id, server_host=self.connection.host, server_port=self.connection.port)

    def _load_run_game(self, target: GameLaunchTarget) -> Callable[..., Any] | None:
        try:
            module = import_module(target.module_path)
        except Exception:
            return None
        run_game = getattr(module, target.function_name, None)
        return run_game if callable(run_game) else None

    def _build_player_info(self, player: Player | None) -> dict[str, object]:
        if player is None:
            return {"username": "guest", "display_name": "Guest"}
        return {
            "username": player.username,
            "display_name": player.display_name,
            "level": player.level,
            "favorite_genre": player.favorite_genre,
        }

    def _build_session_info(self, request: LaunchRequest) -> dict[str, object]:
        return {
            "game_id": request.game_id,
            "session_id": request.session_id,
            "server_host": self.connection.host,
            "server_port": self.connection.port,
            "requested_mode": request.requested_mode,
            # TODO(C++): Add player_token and authoritative session settings
            # after the C++ server creates/joins a real multiplayer session.
        }

    def _result_message(self, game: Game, result: object) -> str:
        if isinstance(result, dict):
            message = result.get("message")
            if isinstance(message, str) and message:
                return message
        return f"{game.title} returned control to Scorpions Arcade."
