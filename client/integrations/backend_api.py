from __future__ import annotations


class BackendApiHook:
    """Placeholder for a future account/platform API.

    TODO(PROJECT): If your final architecture keeps account/catalog logic in a
    backend service instead of local files, place request/response methods here.
    """

    def health_check(self) -> bool:
        return False

    def fetch_player_profile(self, username: str) -> None:
        _ = username
        # TODO(PROJECT): Fetch a real player profile after the backend exists.

