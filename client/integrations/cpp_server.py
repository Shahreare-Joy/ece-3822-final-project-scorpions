from __future__ import annotations

from dataclasses import dataclass


@dataclass
class ServerConnectionInfo:
    """Future C++ backend connection settings."""

    # server host address
    host: str = "127.0.0.1"

    # server port number
    port: int = 3822

    # communication protocol (tcp/udp/etc.)
    protocol: str = "tcp"


@dataclass
class ServerLoginRequest:
    '''store login request data'''

    # username for login
    username: str

    # password for login
    password: str


@dataclass
class ServerLoginResponse:
    '''store login response data'''

    # whether login succeeded
    ok: bool

    # response message
    message: str

    # token returned after login
    player_token: str = ""


@dataclass
class ServerSessionRequest:
    '''store session creation/join request'''

    # player username
    username: str

    # game being requested
    game_id: str

    # matchmaking or other mode
    requested_mode: str = "matchmaking"


@dataclass
class ServerSessionResponse:
    '''store session response from server'''

    # whether request succeeded
    ok: bool

    # response message
    message: str

    # assigned session id
    session_id: str = ""

    # server host for game
    server_host: str = ""

    # server port for game
    server_port: int = 0

    # player token for session
    player_token: str = ""


class CppServerClient:
    """Placeholder client for future C++ multiplayer/backend communication."""

    def __init__(self, connection: ServerConnectionInfo | None = None) -> None:
        # store connection settings
        self.connection = connection or ServerConnectionInfo()

        # track connection state
        self.connected = False

    def connect(self) -> None:
        '''connect to C++ backend server'''

        # TODO(C++): Implement socket connection to the C++ server.
        # This remains a safe no-network stub until the C++ protocol exists.

        # currently does nothing (stub)
        self.connected = False

    def login(self, request: ServerLoginRequest) -> ServerLoginResponse:
        '''send login request to backend'''

        # TODO(C++): Send login request to the real account backend.

        # ignore request for now
        _ = request

        # return placeholder response
        return ServerLoginResponse(False, "C++ login backend is not connected yet.")

    def request_live_scoreboard(self, game_id: str) -> None:
        '''request live scoreboard updates'''

        # TODO(C++): Stream live scoreboard updates from the real server.

        # ignore input for now
        _ = game_id

    def create_or_join_session(self, request: ServerSessionRequest) -> ServerSessionResponse:
        '''request session creation or join'''

        # TODO(C++ LAUNCH): Ask the C++ server to create/join a game session and
        # return authoritative session_id, server_host, server_port, and token.

        # ignore request for now
        _ = request

        # return placeholder response
        return ServerSessionResponse(False, "C++ session handoff is not connected yet.")

    def send_chat_message(self, channel: str, message: str) -> None:
        '''send chat message to backend'''

        # TODO(C++): Send chat/lobby messages through the real networking layer.

        # ignore inputs for now
        _ = (channel, message)