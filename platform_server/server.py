from __future__ import annotations

"""Python platform server entry point.

TODO (DONE)(SERVER): Provide a local direct-call server facade. The team can
wrap this facade with HTTP or sockets later without changing the services.
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
from .session_manager import SessionManager
from .session_results import SessionResultProcessor


class PlatformServer:
    """Facade for platform features."""

    def __init__(self) -> None:
        # initialize all core platform services
        self.accounts = AccountService()
        self.catalog = CatalogService()
        self.chat = ChatService()
        self.data_ingest = DataIngestService()
        self.history = HistoryService()
        self.leaderboard = LeaderboardService()
        self.search = SearchService()
        self.sessions = SessionManager()

        # load static game registry
        self.game_registry = all_registered_games()

        # initialize persistence layer
        self.persistence = PersistenceService()

        # session result processor connects leaderboard, history, and persistence
        self.session_results = SessionResultProcessor(
            leaderboard_service=self.leaderboard,
            history_service=self.history,
            persistence_service=self.persistence,
        )

    def load_dataset(self) -> dict[str, object]:
        '''load dataset and build all service indexes'''

        # TODO (DONE)(DATASET): Call validate_all/load_all and pass records into
        # custom data structures before serving direct-call queries.

        # validate dataset structure and references
        errors = self.data_ingest.validate_all()

        # load all dataset records
        records = self.data_ingest.load_all()

        # extract key datasets
        players = records.get("players", [])
        sessions = records.get("sessions", [])
        games = records.get("game_catalog", [])

        # load accounts from player data
        self.accounts.load_accounts(players)

        # build search indexes
        self.search.index_players(players)
        self.search.index_games(games)

        # build history indexes
        self.history.load_sessions(sessions)

        # build leaderboard from subset of sessions for performance
        self.leaderboard.load_from_sessions(sessions[:25_000])

        # return validation errors and dataset sizes
        return {
            "errors": errors,
            "counts": {key: len(value) for key, value in records.items()}
        }

    def start(self) -> dict[str, object]:
        '''start platform server and initialize services'''

        # TODO (DONE)(SERVER): Replace this placeholder with a usable direct-call
        # startup path. A socket/HTTP wrapper can be added later.
        # TODO (DONE)(RESILIENCE): Return structured startup errors.
        # TODO (DONE)(API): Route message types through service methods documented
        # in docs/API_DOCUMENTATION.md.
        # TODO (DONE)(PERSISTENCE): Validate storage paths before accepting calls.
        # TODO (DONE)(RESULTS): Completed-session submissions route through
        # self.session_results.process_result(...).

        # check persistence storage paths
        storage_ok = self.persistence.validate_storage_paths()

        # load dataset and initialize indexes
        dataset_report = self.load_dataset()

        # return startup status and dataset report
        return {"storage_ok": storage_ok, **dataset_report}

    def shutdown(self) -> dict[str, object]:
        """Gracefully release Python-side active session state."""

        closed_sessions = self.sessions.shutdown()
        return {"closed_sessions": closed_sessions, "message": "Platform server facade shut down cleanly."}


def main() -> None:
    '''entry point for running platform server'''

    # create server instance
    server = PlatformServer()

    # start server and get report
    report = server.start()

    # print startup status
    print("Scorpions platform server facade ready.")
    print(f"Storage paths ready: {report['storage_ok']}")
    print(f"Loaded counts: {report['counts']}")

    # print dataset validation warnings if any
    if report["errors"]:
        print(f"Dataset validation warnings: {len(report['errors'])}")


if __name__ == "__main__":
    main()
