from __future__ import annotations

from platform_server.server import PlatformServer

from .cpp_server import PlatformConnectionInfo


class BackendApiHook:
    """Local direct-call hook for the platform API."""

    def __init__(self, server: PlatformServer | None = None) -> None:
        # Separate platform endpoint settings from live game-server settings.
        # The current facade is direct-call, but these values document and
        # preserve the tunnel configuration for the future socket/HTTP wrapper.
        self.connection = PlatformConnectionInfo.from_environment()

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
