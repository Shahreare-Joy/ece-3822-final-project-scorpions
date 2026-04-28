from __future__ import annotations

from dataclasses import dataclass
import os
import socket
from time import time


ALLOWED_SERVER_PORTS = (50068, 50069, 50075, 50082)
DEFAULT_SERVER_HOST = "127.0.0.1"
DEFAULT_SERVER_PORT = 50068


def is_allowed_port(port: int) -> bool:
    """Return True when a port is one of the class-approved ports."""

    try:
        return int(port) in ALLOWED_SERVER_PORTS
    except (TypeError, ValueError):
        return False


def normalize_allowed_port(port: int) -> int:
    """Return an allowed class port, falling back to the project default."""

    try:
        parsed_port = int(port)
    except (TypeError, ValueError):
        return DEFAULT_SERVER_PORT
    return parsed_port if parsed_port in ALLOWED_SERVER_PORTS else DEFAULT_SERVER_PORT


def _env_host(role: str) -> str:
    """Read host from env, defaulting to localhost for SSH tunnels."""

    return (
        os.environ.get(f"SCORPIONS_{role}_HOST")
        or os.environ.get("SCORPIONS_SERVER_HOST")
        or DEFAULT_SERVER_HOST
    ).strip() or DEFAULT_SERVER_HOST


def _env_port(role: str) -> int:
    """Read an approved local forwarded port from env."""

    return normalize_allowed_port(
        os.environ.get(f"SCORPIONS_{role}_PORT")
        or os.environ.get("SCORPIONS_SERVER_PORT")
        or DEFAULT_SERVER_PORT
    )


@dataclass
class ServerConnectionInfo:
    """Connection settings for a locally forwarded server endpoint.

    For SSH tunneling, host normally stays localhost/127.0.0.1. The local SSH
    client listens on this port and forwards traffic to the real ECE machine.
    """

    # server host address
    host: str = DEFAULT_SERVER_HOST

    # server port number
    port: int = DEFAULT_SERVER_PORT

    # communication protocol (tcp/udp/etc.)
    protocol: str = "tcp"

    def __post_init__(self) -> None:
        self.port = normalize_allowed_port(int(self.port))

    @classmethod
    def from_environment(cls, role: str = "GAME") -> "ServerConnectionInfo":
        """Build connection settings from SCORPIONS_<ROLE>_* variables."""

        return cls(host=_env_host(role), port=_env_port(role))


class PlatformConnectionInfo(ServerConnectionInfo):
    """Platform API tunnel endpoint for login/search/leaderboards."""

    @classmethod
    def from_environment(cls) -> "PlatformConnectionInfo":
        return cls(host=_env_host("PLATFORM"), port=_env_port("PLATFORM"))


class GameServerConnectionInfo(ServerConnectionInfo):
    """Gameplay tunnel endpoint for live game state."""

    @classmethod
    def from_environment(cls) -> "GameServerConnectionInfo":
        return cls(host=_env_host("GAME"), port=_env_port("GAME"))


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
    """Small client-side hook for the future C++ multiplayer server.

    This class intentionally stays tiny. It can verify that a TCP server is
    reachable on one of the approved class ports, but the final gameplay
    protocol still belongs in the C++ server and game clients.
    """

    def __init__(self, connection: ServerConnectionInfo | None = None) -> None:
        # store connection settings
        self.connection = connection or GameServerConnectionInfo.from_environment()

        # track connection state
        self.connected = False

    def connect(self) -> None:
        '''try to connect to the C++ backend server'''

        try:
            with socket.create_connection((self.connection.host, self.connection.port), timeout=0.75):
                self.connected = True
        except OSError:
            # Safe fallback: games can still run offline/local, but the UI can
            # honestly report that the live C++ server is not reachable.
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

        # TODO(C++ LAUNCH): Replace this local session id with the
        # authoritative session_id/player_token returned by the C++ server.
        if not self.connected:
            self.connect()
        if not self.connected:
            return ServerSessionResponse(False, "C++ session server is not reachable on the selected class port.")

        safe_game = request.game_id.replace(" ", "-")
        safe_user = request.username.replace(" ", "-")
        session_id = f"{safe_game}-{safe_user}-{int(time())}"
        return ServerSessionResponse(
            True,
            "Connected to local C++ demo server.",
            session_id=session_id,
            server_host=self.connection.host,
            server_port=self.connection.port,
            player_token=f"local-token-{safe_user}",
        )

    def send_chat_message(self, channel: str, message: str) -> None:
        '''send chat message to backend'''

        # TODO(C++): Send chat/lobby messages through the real networking layer.

        # ignore inputs for now
        _ = (channel, message)

    def disconnect(self) -> None:
        """Clear client connection state after a session ends."""

        self.connected = False
