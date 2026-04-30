from __future__ import annotations

from dataclasses import dataclass

from client.integrations.cpp_server import (
    DEFAULT_SERVER_HOST,
    DEFAULT_SERVER_PORT,
    PlatformConnectionInfo,
    GameServerConnectionInfo,
    normalize_serializer,
)


@dataclass(frozen=True)
class RuntimeConfig:
    """Runtime mode selected by main.py command-line arguments."""

    mode: str = "local"
    server_host: str = DEFAULT_SERVER_HOST
    platform_port: int = DEFAULT_SERVER_PORT
    gameplay_port: int = DEFAULT_SERVER_PORT
    serializer: str = "json"
    allow_local_fallback: bool = True

    @property
    def is_server_mode(self) -> bool:
        return self.mode == "server"

    @classmethod
    def local(cls) -> "RuntimeConfig":
        return cls()

    @classmethod
    def server(cls, host: str, port: int, serializer: str = "json", gameplay_port: int | None = None) -> "RuntimeConfig":
        return cls(
            mode="server",
            server_host=(host or DEFAULT_SERVER_HOST).strip() or DEFAULT_SERVER_HOST,
            platform_port=_normalize_cli_port(port),
            gameplay_port=_normalize_cli_port(gameplay_port if gameplay_port is not None else port),
            serializer=normalize_serializer(serializer),
        )

    def platform_connection(self) -> PlatformConnectionInfo:
        return PlatformConnectionInfo(
            host=self.server_host,
            port=self.platform_port,
            serializer=self.serializer,
            enforce_allowed_ports=not self.is_server_mode,
        )

    def gameplay_connection(self) -> GameServerConnectionInfo:
        return GameServerConnectionInfo(
            host=self.server_host,
            port=self.gameplay_port,
            serializer=self.serializer,
            enforce_allowed_ports=not self.is_server_mode,
        )


def _normalize_cli_port(port: int | str | None) -> int:
    """Accept a normal TCP port from CLI while rejecting unusable values."""

    try:
        parsed = int(port if port is not None else DEFAULT_SERVER_PORT)
    except (TypeError, ValueError):
        return DEFAULT_SERVER_PORT
    return parsed if 1 <= parsed <= 65535 else DEFAULT_SERVER_PORT
