from __future__ import annotations

from dataclasses import dataclass


@dataclass
class ServerConnectionInfo:
    """Future C++ backend connection settings.

    TODO(C++): Replace placeholders with local server config, environment
    variables, or a real config file once the C++ service exists.
    """

    host: str = "127.0.0.1"
    port: int = 3822
    protocol: str = "tcp"


@dataclass
class ServerLoginRequest:
    username: str
    password: str


@dataclass
class ServerLoginResponse:
    ok: bool
    message: str
    player_token: str = ""


@dataclass
class ServerSessionRequest:
    username: str
    game_id: str
    requested_mode: str = "matchmaking"


@dataclass
class ServerSessionResponse:
    ok: bool
    message: str
    session_id: str = ""
    server_host: str = ""
    server_port: int = 0
    player_token: str = ""


class CppServerClient:
    """Placeholder client for future C++ multiplayer/backend communication.

    TODO(C++): Implement these methods with the team-owned protocol. The UI and
    services should call this integration layer instead of opening sockets from
    screen files.
    """

    def __init__(self, connection: ServerConnectionInfo | None = None) -> None:
        self.connection = connection or ServerConnectionInfo()
        self.connected = False

    def connect(self) -> None:
        # TODO(C++): Implement socket connection to the C++ server.
        self.connected = False

    def login(self, request: ServerLoginRequest) -> ServerLoginResponse:
        # TODO(C++): Send login request to the real account backend.
        _ = request
        return ServerLoginResponse(False, "C++ login backend is not connected yet.")

    def request_live_scoreboard(self, game_id: str) -> None:
        # TODO(C++): Stream live scoreboard updates from the real server.
        _ = game_id

    def create_or_join_session(self, request: ServerSessionRequest) -> ServerSessionResponse:
        # TODO(C++ LAUNCH): Ask the C++ server to create/join a game session and
        # return authoritative session_id, server_host, server_port, and token.
        _ = request
        return ServerSessionResponse(False, "C++ session handoff is not connected yet.")

    def send_chat_message(self, channel: str, message: str) -> None:
        # TODO(C++): Send chat/lobby messages through the real networking layer.
        _ = (channel, message)
