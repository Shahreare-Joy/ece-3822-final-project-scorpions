from __future__ import annotations

"""Python platform server entry point.

The arcade can use this module in two ways:

1. Local mode imports :class:`PlatformServer` directly as an in-process facade.
2. Server mode runs this file as a small TCP server that accepts one
   newline-delimited request per connection.

The socket wrapper intentionally stays thin. It reuses the same beginner-
friendly platform services for accounts, search, history, leaderboards, chat,
and completed result routing instead of creating a separate code path.
"""

import argparse
import json
import socketserver
import sys
from dataclasses import asdict, is_dataclass
from pathlib import Path
from typing import Any

if __package__ in {None, ""}:  # pragma: no cover - direct CLI convenience path
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

try:  # Supports both `python -m platform_server.server` and direct script runs.
    from .accounts import AccountService
    from .catalog import CatalogService
    from .chat import ChatService
    from .data_ingest import DataIngestService
    from .history import HistoryService
    from .leaderboard import LeaderboardService
    from .persistence import PersistenceService
    from .search import SearchService
    from .game_registry import all_registered_games
    from .session_manager import SessionManager
    from .session_results import SessionResult, SessionResultProcessor
except ImportError:  # pragma: no cover - direct CLI convenience path
    from platform_server.accounts import AccountService
    from platform_server.catalog import CatalogService
    from platform_server.chat import ChatService
    from platform_server.data_ingest import DataIngestService
    from platform_server.history import HistoryService
    from platform_server.leaderboard import LeaderboardService
    from platform_server.persistence import PersistenceService
    from platform_server.search import SearchService
    from platform_server.game_registry import all_registered_games
    from platform_server.session_manager import SessionManager
    from platform_server.session_results import SessionResult, SessionResultProcessor


class PlatformServer:
    """Facade for platform features."""

    def __init__(self) -> None:
        # initialize all core platform services
        self.accounts = AccountService()
        self.catalog = CatalogService()
        self.chat = ChatService()
        self.data_ingest = DataIngestService()
        self.history = HistoryService()
        self.leaderboard = LeaderboardService()
        self.search = SearchService()
        self.sessions = SessionManager()

        # load static game registry
        self.game_registry = all_registered_games()

        # initialize persistence layer
        self.persistence = PersistenceService()

        # session result processor connects leaderboard, history, and persistence
        self.session_results = SessionResultProcessor(
            leaderboard_service=self.leaderboard,
            history_service=self.history,
            persistence_service=self.persistence,
        )
        self.records: dict[str, list[dict[str, Any]]] = {}

    def load_dataset(self) -> dict[str, object]:
        '''load dataset and build all service indexes'''

        # TODO (DONE)(DATASET): Call validate_all/load_all and pass records into
        # custom data structures before serving direct-call queries.

        # validate dataset structure and references
        errors = self.data_ingest.validate_all()

        # load all dataset records
        records = self.data_ingest.load_all()
        self.records = records

        # extract key datasets
        players = records.get("players", [])
        sessions = [
            row
            for row in records.get("sessions", [])
            if self._canonical_game_id(str(row.get("game_id", ""))) not in {
                "scorpions-arena",
                "sky-raiders",
                "turbo-sprint",
                "crystal-run",
            }
        ]
        games = records.get("game_catalog", [])

        # load accounts from player data
        self.accounts.load_accounts(players)
        self._load_demo_accounts()

        # build search indexes
        self.search.index_players(players)
        self.search.index_games(games)

        # build history indexes
        self.history.load_sessions(sessions)

        # build leaderboard from subset of sessions for performance
        self.leaderboard.load_from_sessions(sessions[:25_000])

        # return validation errors and dataset sizes
        return {
            "errors": errors,
            "counts": {key: len(value) for key, value in records.items()}
        }

    @staticmethod
    def _canonical_game_id(game_id: str) -> str:
        return {
            "game_1": "scorpions-arena",
            "game_2": "sky-raiders",
            "game_3": "turbo-sprint",
            "game_4": "crystal-run",
        }.get(game_id, game_id)

    def start(self) -> dict[str, object]:
        '''start platform server and initialize services'''

        # TODO (DONE)(SERVER): Replace this placeholder with a usable direct-call
        # startup path. A socket/HTTP wrapper can be added later.
        # TODO (DONE)(RESILIENCE): Return structured startup errors.
        # TODO (DONE)(API): Route message types through service methods documented
        # in docs/API_DOCUMENTATION.md.
        # TODO (DONE)(PERSISTENCE): Validate storage paths before accepting calls.
        # TODO (DONE)(RESULTS): Completed-session submissions route through
        # self.session_results.process_result(...).

        # check persistence storage paths
        storage_ok = self.persistence.validate_storage_paths()

        # load dataset and initialize indexes
        dataset_report = self.load_dataset()

        # return startup status and dataset report
        return {"storage_ok": storage_ok, **dataset_report}

    def shutdown(self) -> dict[str, object]:
        """Gracefully release Python-side active session state."""

        closed_sessions = self.sessions.shutdown()
        return {"closed_sessions": closed_sessions, "message": "Platform server facade shut down cleanly."}

    def handle_request(self, request: dict[str, Any]) -> dict[str, Any]:
        """Route one JSON-style platform request.

        This is the protocol used by the TCP wrapper. It is deliberately small
        and explicit so students can explain it during the demo:
        login/search/catalog/history/leaderboard/chat/result/session cleanup.
        """

        action = str(request.get("type") or request.get("action") or "").strip().lower()
        if action:
            print(f"[PLATFORM] request={action}")
        if action in {"health", "ping"}:
            return {"ok": True, "type": "health", "message": "Python platform server is online."}
        if action == "login":
            username = str(request.get("username", "")).strip().lower()
            password = str(request.get("password", ""))
            if not self.accounts.login(username, password):
                return {"ok": False, "message": "Invalid username or password."}
            return {"ok": True, "message": "Login accepted.", "player": self._player_payload(username)}
        if action == "search_players":
            query = str(request.get("query", ""))
            limit = self._safe_limit(request.get("limit", 25), 100)
            return {"ok": True, "players": [self._serialize(row) for row in self.search.search_players(query, limit)]}
        if action == "catalog":
            limit = self._safe_limit(request.get("limit", 120), 250)
            return {"ok": True, "games": self.records.get("game_catalog", [])[:limit]}
        if action == "history":
            username = str(request.get("username", "")).strip().lower()
            game_id = str(request.get("game_id", "")).strip()
            limit = self._safe_limit(request.get("limit", 25), 100)
            if username:
                rows = self.history.by_player(username, limit)
            elif game_id:
                rows = self.history.by_game(game_id, limit)
            else:
                rows = self.records.get("sessions", [])[-limit:]
            return {"ok": True, "sessions": [self._serialize(row) for row in rows]}
        if action == "leaderboard":
            game_id = str(request.get("game_id", "")).strip()
            limit = self._safe_limit(request.get("limit", 10), 100)
            rows = self.leaderboard.top_n(game_id, limit)
            return {"ok": True, "leaders": [self._serialize(row) for row in rows]}
        if action == "chat_send":
            ok = self.chat.add_message(
                str(request.get("session_id", "")),
                str(request.get("sender", "")),
                str(request.get("text", "")),
            )
            print(f"[CHAT] session={request.get('session_id', '')} sender={request.get('sender', '')} stored={ok}")
            return {"ok": ok, "message": "Message stored." if ok else "Message rejected by chat validation/moderation."}
        if action == "chat_recent":
            session_id = str(request.get("session_id", ""))
            limit = self._safe_limit(request.get("limit", 20), 100)
            return {"ok": True, "messages": [self._serialize(row) for row in self.chat.recent_messages(session_id, limit)]}
        if action == "session_start":
            session_id = self.sessions.start_session(
                str(request.get("session_id") or ""),
                str(request.get("player_id") or request.get("username") or "guest"),
                str(request.get("game_id") or "unknown"),
            )
            return {"ok": True, "session": self._serialize(session_id)}
        if action in {"session_end", "disconnect"}:
            session_id = str(request.get("session_id", ""))
            closed = self.sessions.end_session(session_id)
            # Keep bounded chat history available for Profile/History previews
            # after a game exits. Active session cleanup still happens above.
            return {"ok": closed, "message": "Session cleaned up." if closed else "Session was not active."}
        if action == "submit_result":
            payload = request.get("payload", request)
            if not isinstance(payload, dict):
                return {"ok": False, "message": "Result payload must be an object."}
            report = self.session_results.process_result(SessionResult.from_payload(payload))
            print(
                "[RESULT] "
                f"player={payload.get('player_id') or payload.get('username')} "
                f"game={payload.get('game_id')} score={payload.get('score')} "
                f"accepted={report.accepted}"
            )
            return {"ok": report.accepted, "message": report.message, "errors": report.validation_errors}
        return {"ok": False, "message": f"Unknown platform request: {action or '<empty>'}."}

    def _load_demo_accounts(self) -> int:
        """Load class demo accounts into the platform account hash table."""

        path = Path(__file__).resolve().parents[1] / "data" / "demo_accounts.json"
        if not path.exists():
            return 0
        try:
            rows = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return 0
        if not isinstance(rows, list):
            return 0
        loaded = 0
        for row in rows:
            if not isinstance(row, dict):
                continue
            if self.accounts.signup(str(row.get("username", "")), str(row.get("password", "")), str(row.get("display_name", ""))):
                loaded += 1
        return loaded

    def _player_payload(self, username: str) -> dict[str, Any]:
        for row in self.records.get("players", []):
            if str(row.get("username", "")).strip().lower() == username:
                return dict(row)
        path = Path(__file__).resolve().parents[1] / "data" / "demo_accounts.json"
        try:
            rows = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            rows = []
        for row in rows if isinstance(rows, list) else []:
            if isinstance(row, dict) and str(row.get("username", "")).strip().lower() == username:
                public = dict(row)
                public.pop("password", None)
                return public
        return {"username": username, "display_name": username.title()}

    @staticmethod
    def _safe_limit(value: Any, maximum: int) -> int:
        try:
            return max(1, min(int(value), maximum))
        except (TypeError, ValueError):
            return min(25, maximum)

    @staticmethod
    def _serialize(value: Any) -> Any:
        if is_dataclass(value):
            return asdict(value)
        if isinstance(value, dict):
            return dict(value)
        if hasattr(value, "__dict__"):
            return dict(value.__dict__)
        return value


class _ThreadingPlatformTcpServer(socketserver.ThreadingTCPServer):
    allow_reuse_address = True
    daemon_threads = True


def run_socket_server(host: str = "127.0.0.1", port: int = 50068, serializer: str = "json") -> None:
    """Start the TCP platform server until Ctrl+C.

    JSON mode expects one JSON object per line. Text mode accepts simple words
    like ``PING`` or ``HEALTH`` and replies with text/JSON text for easy manual
    testing with a socket client.
    """

    platform = PlatformServer()
    report = platform.start()

    class Handler(socketserver.StreamRequestHandler):
        def handle(self) -> None:
            raw = self.rfile.readline(1024 * 1024)
            if not raw:
                return
            response = _decode_and_handle(platform, raw, serializer)
            self.wfile.write(response)

    with _ThreadingPlatformTcpServer((host, int(port)), Handler) as tcp_server:
        print(f"Scorpions platform TCP server listening on {host}:{port} ({serializer}).")
        print(f"Storage paths ready: {report['storage_ok']}")
        print(f"Loaded counts: {report['counts']}")
        if report["errors"]:
            print(f"Dataset validation warnings: {len(report['errors'])}")
        try:
            tcp_server.serve_forever(poll_interval=0.5)
        except KeyboardInterrupt:
            print("Shutting down platform TCP server...")
        finally:
            platform.shutdown()


def _decode_and_handle(platform: PlatformServer, raw: bytes, serializer: str) -> bytes:
    text = raw.decode("utf-8", errors="replace").strip()
    if serializer == "json":
        try:
            request = json.loads(text)
        except json.JSONDecodeError:
            request = {"type": "", "error": "invalid_json"}
        if not isinstance(request, dict):
            request = {"type": "", "error": "request_must_be_object"}
        response = platform.handle_request(request)
        return (json.dumps(response) + "\n").encode("utf-8")
    command, _, rest = text.partition(" ")
    request: dict[str, Any] = {"type": command.lower()}
    if command.upper() == "LOGIN":
        parts = rest.split()
        if len(parts) >= 2:
            request["username"] = parts[0]
            request["password"] = parts[1]
    elif command.upper() == "SEARCH_PLAYERS":
        request["type"] = "search_players"
        request["query"] = rest
    if rest:
        request["query"] = rest
    response = platform.handle_request(request)
    if command.upper() in {"PING", "HEALTH"}:
        return (("OK " if response.get("ok") else "ERR ") + str(response.get("message", "")) + "\n").encode("utf-8")
    return (json.dumps(response) + "\n").encode("utf-8")


def main(argv: list[str] | None = None) -> None:
    '''entry point for running platform server'''

    parser = argparse.ArgumentParser(description="Run the Scorpions Python platform server.")
    parser.add_argument("--host", default="127.0.0.1", help="Host/interface to bind.")
    parser.add_argument("--port", type=int, default=50068, help="TCP platform port.")
    parser.add_argument("--serializer", choices=("json", "text"), default="json", help="Request/response wire format.")
    parser.add_argument("--check", action="store_true", help="Load the dataset and exit without opening a TCP listener.")
    args = parser.parse_args(argv)

    if not args.check:
        run_socket_server(args.host, args.port, args.serializer)
        return

    # create server instance
    server = PlatformServer()

    # start server and get report
    report = server.start()

    # print startup status
    print("Scorpions platform server facade ready.")
    print(f"Storage paths ready: {report['storage_ok']}")
    print(f"Loaded counts: {report['counts']}")

    # print dataset validation warnings if any
    if report["errors"]:
        print(f"Dataset validation warnings: {len(report['errors'])}")


if __name__ == "__main__":
    main()
