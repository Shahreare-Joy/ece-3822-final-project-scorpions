from __future__ import annotations

from platform_server.server import PlatformServer

from .cpp_server import PlatformConnectionInfo, ServerAvailability


class BackendApiHook:
    """Local direct-call hook for the platform API."""

    def __init__(self, server: PlatformServer | None = None, connection: PlatformConnectionInfo | None = None) -> None:
        # Separate platform endpoint settings from live game-server settings.
        # The current facade is direct-call, but these values document and
        # preserve the tunnel configuration for the future socket/HTTP wrapper.
        self.connection = connection or PlatformConnectionInfo.from_environment()

        # use provided server or create a new one
        self.server = server or PlatformServer()

        # track whether backend has been started
        self._started = False

    def health_check(self) -> bool:
        '''ensure backend server is started and healthy'''

        # start server only once
        if not self._started:
            report = self.server.start()

            # mark as started only if storage ok and no dataset errors
            self._started = bool(report.get("storage_ok")) and not report.get("errors")

        return self._started

    def availability_status(self) -> ServerAvailability:
        """Report platform API availability without loading the full dataset.

        The platform layer is currently a Python direct-call facade instead of
        a long-running socket server. That is why this check does not open a
        TCP socket; it simply reports the configured tunnel endpoint and that
        the local platform object can be reached by the arcade client.
        """

        return ServerAvailability(
            name="Python Platform Server",
            role="platform",
            host=self.connection.host,
            port=self.connection.port,
            reachable=True,
            message="Python platform facade is available for login, search, profiles, catalog, chat metadata, and history.",
            protocol=self.connection.protocol,
            direct_call=True,
        )

    def fetch_player_profile(self, username: str) -> dict[str, object] | None:
        '''fetch player profile using search service'''

        # TODO (DONE)(PROJECT): Fetch a player profile through the local backend facade.

        # ensure backend is ready
        if not self.health_check():
            return None

        # search for player by username
        matches = self.server.search.search_players(username, limit=1)

        # return None if no match found
        if not matches:
            return None

        match = matches[0]

        # convert result to dictionary if possible
        return dict(match) if isinstance(match, dict) else getattr(match, "__dict__", None)
