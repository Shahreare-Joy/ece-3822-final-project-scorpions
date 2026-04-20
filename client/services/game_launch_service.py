from __future__ import annotations

"""Game launch service for external team folders.

Chosen approach:
    The launcher runs pasted team games as subprocesses by default.

Why subprocess-first:
    Copied Pygame projects often call `pygame.quit()`, `sys.exit()`, read assets
    using relative paths, or use their own event loops. A subprocess isolates
    those side effects so the arcade launcher can safely regain control after
    the game exits. The subprocess working directory is the selected game's
    `code/game/` folder, preserving relative paths like `../../graphics`.
"""

from contextlib import contextmanager
from dataclasses import dataclass
from importlib import util
from pathlib import Path
from typing import Any, Callable, Iterator
import inspect
import json
import os
import subprocess
import sys
import tempfile

from client.integrations import ServerConnectionInfo, ServerSessionRequest
from client.models import Game, Player
from .game_launch_registry import GameLaunchTarget, get_launch_target


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
    # Future completed-session payload returned by run_game(...) or written by
    # a subprocess game to SCORPIONS_RESULT_PATH. None means the game does not
    # report score/outcome yet, which is safe during scaffold development.
    session_result_payload: dict[str, Any] | None = None


class GameLaunchService:
    """Starter launch/handoff layer for playable team games."""

    def __init__(self, connection: ServerConnectionInfo | None = None) -> None:
        self.connection = connection or ServerConnectionInfo()

    def launch(self, player: Player | None, game: Game) -> LaunchResult:
        username = player.username if player else "guest"
        request = LaunchRequest(game.game_id, username)
        # TODO(C++ LAUNCH): Replace the local LaunchRequest path with a call to
        # CppServerClient.create_or_join_session(ServerSessionRequest(...)).
        _future_server_request = ServerSessionRequest(username=username, game_id=game.game_id, requested_mode=request.requested_mode)
        _ = _future_server_request

        target = get_launch_target(game.game_id)
        if target is None:
            return LaunchResult(False, f"{game.title} is not registered in the game launch registry yet.")

        missing_reason = target.missing_reason()
        if missing_reason:
            return LaunchResult(False, missing_reason)

        player_info = self._build_player_info(player)
        result_path = self._prepare_result_path()
        session_info = self._build_session_info(request, result_path)

        if target.launch_mode in ("adapter", "auto"):
            run_game = self._load_run_game(target)
            if run_game is not None:
                return self._launch_adapter(target, run_game, player_info, session_info, request, game, result_path)
            if target.launch_mode == "adapter":
                return LaunchResult(False, f"{game.title} does not expose {target.function_name}(...).")

        return self._launch_subprocess(target, player_info, session_info, request, game, result_path)

    def _launch_adapter(
        self,
        target: GameLaunchTarget,
        run_game: Callable[..., Any],
        player_info: dict[str, object],
        session_info: dict[str, object],
        request: LaunchRequest,
        game: Game,
        result_path: Path,
    ) -> LaunchResult:
        try:
            with self._game_import_context(target.entry_path.parent):
                result = self._call_run_game(run_game, player_info, session_info)
        except SystemExit as exc:
            code = exc.code if isinstance(exc.code, int) else 0
            if code == 0:
                payload = self._read_result_payload(result_path)
                return LaunchResult(True, f"{game.title} exited and returned to Scorpions Arcade.", request.session_id, self.connection.host, self.connection.port, payload)
            self._cleanup_result_path(result_path)
            return LaunchResult(False, f"{game.title} exited with code {code}.")
        except Exception as exc:
            self._cleanup_result_path(result_path)
            return LaunchResult(False, f"{game.title} crashed during launch: {exc}")

        payload = self._extract_result_payload(result, request, game) or self._read_result_payload(result_path)
        return LaunchResult(True, self._result_message(game, result), request.session_id, self.connection.host, self.connection.port, payload)

    def _launch_subprocess(
        self,
        target: GameLaunchTarget,
        player_info: dict[str, object],
        session_info: dict[str, object],
        request: LaunchRequest,
        game: Game,
        result_path: Path,
    ) -> LaunchResult:
        args = target.render_script_args(player_info, session_info)
        command = [sys.executable, str(target.entry_path), *args]
        env = os.environ.copy()
        env["client_LAUNCH"] = "1"
        env["SCORPIONS_GAME_ID"] = target.game_id
        env["SCORPIONS_SESSION_ID"] = request.session_id
        env["SCORPIONS_PLAYER"] = str(player_info.get("username", "guest"))
        # Future subprocess games can write JSON here before exiting:
        # {
        #   "score": 4200,
        #   "outcome": "Win",
        #   "duration_seconds": 180,
        #   "metadata": {"level": 3}
        # }
        # The launcher reads it after the process exits and sends it to the
        # platform session-result pipeline.
        env["SCORPIONS_RESULT_PATH"] = str(result_path)

        try:
            # cwd is intentionally the game's own code/game folder. Many copied
            # games load assets with relative paths such as ../../graphics.
            completed = subprocess.run(command, cwd=target.entry_path.parent, env=env, check=False)
        except OSError as exc:
            return LaunchResult(False, f"Could not launch {game.title}: {exc}")

        if completed.returncode != 0:
            self._cleanup_result_path(result_path)
            return LaunchResult(False, f"{game.title} exited with code {completed.returncode}.")
        payload = self._read_result_payload(result_path)
        return LaunchResult(True, f"{game.title} returned control to Scorpions Arcade.", request.session_id, self.connection.host, self.connection.port, payload)

    def _load_run_game(self, target: GameLaunchTarget) -> Callable[..., Any] | None:
        with self._game_import_context(target.entry_path.parent):
            try:
                module_name = f"_scorpions_external_{target.game_id.replace('-', '_')}"
                spec = util.spec_from_file_location(module_name, target.entry_path)
                if spec is None or spec.loader is None:
                    return None
                module = util.module_from_spec(spec)
                spec.loader.exec_module(module)
            except Exception:
                return None
        run_game = getattr(module, target.function_name, None)
        return run_game if callable(run_game) else None

    @contextmanager
    def _game_import_context(self, entry_dir: Path) -> Iterator[None]:
        old_cwd = Path.cwd()
        entry_dir_str = str(entry_dir)
        sys.path.insert(0, entry_dir_str)
        os.chdir(entry_dir)
        try:
            yield
        finally:
            os.chdir(old_cwd)
            try:
                sys.path.remove(entry_dir_str)
            except ValueError:
                pass

    def _call_run_game(self, run_game: Callable[..., Any], player_info: dict[str, object], session_info: dict[str, object]) -> object:
        signature = inspect.signature(run_game)
        parameters = signature.parameters
        if any(param.kind == inspect.Parameter.VAR_KEYWORD for param in parameters.values()):
            return run_game(player_info=player_info, session_info=session_info)
        if "player_info" in parameters or "session_info" in parameters:
            kwargs: dict[str, object] = {}
            if "player_info" in parameters:
                kwargs["player_info"] = player_info
            if "session_info" in parameters:
                kwargs["session_info"] = session_info
            return run_game(**kwargs)
        if len(parameters) == 0:
            return run_game()
        return run_game(player_info)

    def _build_player_info(self, player: Player | None) -> dict[str, object]:
        if player is None:
            return {"username": "guest", "display_name": "Guest"}
        return {
            "username": player.username,
            "display_name": player.display_name,
            "level": player.level,
            "favorite_genre": player.favorite_genre,
        }

    def _build_session_info(self, request: LaunchRequest, result_path: Path | None = None) -> dict[str, object]:
        return {
            "game_id": request.game_id,
            "session_id": request.session_id,
            "server_host": self.connection.host,
            "server_port": self.connection.port,
            "requested_mode": request.requested_mode,
            "result_path": str(result_path) if result_path else "",
            # TODO(C++): Add player_token and authoritative session settings
            # after the C++ server creates/joins a real multiplayer session.
        }

    def _result_message(self, game: Game, result: object) -> str:
        if isinstance(result, dict):
            message = result.get("message")
            if isinstance(message, str) and message:
                return message
        return f"{game.title} returned control to Scorpions Arcade."

    def _prepare_result_path(self) -> Path:
        """Create a temp result path that future subprocess games can write."""

        handle = tempfile.NamedTemporaryFile(prefix="scorpions_result_", suffix=".json", delete=False)
        result_path = Path(handle.name)
        handle.close()
        # Leave only the path, not an empty file, so "file exists" means a game
        # actually attempted to report a result.
        result_path.unlink(missing_ok=True)
        return result_path

    def _extract_result_payload(self, result: object, request: LaunchRequest, game: Game) -> dict[str, Any] | None:
        """Extract a completed-session payload from a run_game(...) return value."""

        if not isinstance(result, dict):
            return None
        raw_payload = result.get("session_result", result)
        if not isinstance(raw_payload, dict):
            return None
        if not any(key in raw_payload for key in ("score", "outcome", "result", "duration_seconds", "duration")):
            return None
        payload = dict(raw_payload)
        payload.setdefault("game_id", game.game_id)
        payload.setdefault("player_id", request.username)
        payload.setdefault("session_id", request.session_id)
        return payload

    def _read_result_payload(self, result_path: Path) -> dict[str, Any] | None:
        """Read and remove a future subprocess result JSON file if it exists."""

        try:
            if not result_path.exists() or result_path.stat().st_size == 0:
                return None
            payload = json.loads(result_path.read_text(encoding="utf-8"))
            if isinstance(payload, dict):
                return payload
            return None
        except (OSError, json.JSONDecodeError):
            # TODO(RESULT VALIDATION): Surface malformed result files as a
            # structured warning in the final platform server API.
            return None
        finally:
            self._cleanup_result_path(result_path)

    def _cleanup_result_path(self, result_path: Path) -> None:
        try:
            result_path.unlink(missing_ok=True)
        except OSError:
            pass
