"""Client history service adapter.

TODO(HISTORY): Request filtered match history from platform_server/history.py.
Do not scan 100,000+ sessions in the Pygame UI.
"""


class ClientHistoryService:
    def recent_sessions(self, username: str, limit: int = 10) -> list[object]:
        _ = (username, limit)
        return []
