from __future__ import annotations

"""Python platform server entry point.

TODO(SERVER): Replace this local scaffold with the team's chosen API style
(HTTP, sockets, or direct module calls for the class demo). Keep real-time
gameplay in cpp_server/ and keep Pygame rendering in client/.
"""

from .accounts import AccountService
from .catalog import CatalogService
from .chat import ChatService
from .history import HistoryService
from .leaderboard import LeaderboardService
from .search import SearchService


class PlatformServer:
    """Facade for platform features.

    TODO(INTEGRATION): Wire this facade to loaded synthetic data and custom data
    structures after dataset ingestion is complete.
    """

    def __init__(self) -> None:
        self.accounts = AccountService()
        self.catalog = CatalogService()
        self.chat = ChatService()
        self.history = HistoryService()
        self.leaderboard = LeaderboardService()
        self.search = SearchService()


def main() -> None:
    server = PlatformServer()
    print("Scorpions platform server scaffold ready.")
    print("TODO: expose server.accounts/search/leaderboard/history/catalog/chat through an API.")
    _ = server


if __name__ == "__main__":
    main()
