from __future__ import annotations

"""Python platform server entry point.

TODO(SERVER): Replace this local scaffold with the team's chosen API style
(HTTP, sockets, or direct module calls for the class demo). Keep real-time
gameplay in cpp_server/ and keep Pygame rendering in client/.
"""

from .accounts import AccountService
from .catalog import CatalogService
from .chat import ChatService
from .data_ingest import DataIngestService
from .history import HistoryService
from .leaderboard import LeaderboardService
from .persistence import PersistenceService
from .search import SearchService
from .game_registry import all_registered_games
from .session_results import SessionResultProcessor


class PlatformServer:
    """Facade for platform features.

    TODO(INTEGRATION): Wire this facade to loaded synthetic data and custom data
    structures after dataset ingestion is complete.
    """

    def __init__(self) -> None:
        self.accounts = AccountService()
        self.catalog = CatalogService()
        self.chat = ChatService()
        self.data_ingest = DataIngestService()
        self.history = HistoryService()
        self.leaderboard = LeaderboardService()
        self.search = SearchService()
        self.game_registry = all_registered_games()
        self.persistence = PersistenceService()
        self.session_results = SessionResultProcessor(
            leaderboard_service=self.leaderboard,
            history_service=self.history,
            persistence_service=self.persistence,
        )

    def start(self) -> None:
        """Future API server entry point.

        TODO(SERVER): Replace this placeholder with socket/HTTP handling.
        TODO(RESILIENCE): Parse requests safely and return structured errors.
        TODO(API): Route message types documented in docs/API_DOCUMENTATION.md.
        TODO(PERSISTENCE): Load saved state before accepting client requests.
        TODO(RESULTS): Route completed-session result submissions through
        self.session_results.process_result(...).
        TODO(DATASET): Call self.data_ingest.validate_all() and load_all(), then
        pass cleaned records into custom data structures before serving queries.
        """

        raise NotImplementedError("Team must implement the Python platform server API.")


def main() -> None:
    server = PlatformServer()
    print("Scorpions platform server scaffold ready.")
    print("TODO: expose server.accounts/search/leaderboard/history/catalog/chat through an API.")
    _ = server


if __name__ == "__main__":
    main()
