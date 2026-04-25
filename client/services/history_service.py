from __future__ import annotations

from client.models import GameSession
from client.placeholders.sorting_algorithms import SortingHooks
from datastructures.hash_table import ChainedHashTable


class HistoryService:
    """Indexed session-history service."""

    def __init__(self, sessions: list[GameSession]) -> None:
        self.sessions = sessions
        self.sorting = SortingHooks()
        self._by_player = ChainedHashTable()
        self._by_game = ChainedHashTable()
        self._by_result = ChainedHashTable()
        self._build_indexes()

    def _build_indexes(self) -> None:
        for session in self.sessions:
            self._append(self._by_player, session.username, session)
            self._append(self._by_game, session.game_id, session)
            self._append(self._by_result, session.result.lower(), session)

    def _append(self, table: ChainedHashTable, key: str, session: GameSession) -> None:
        rows = table.get(key)
        if not isinstance(rows, list):
            rows = []
            table.put(key, rows)
        rows.append(session)

    def get_sessions(self, username: str | None = None, game_id: str | None = None, limit: int = 8) -> list[GameSession]:
        # TODO (DONE)(HISTORY STRUCTURE): Replace scans with indexed history queries.
        if username:
            sessions = self._by_player.get(username, [])
        elif game_id:
            sessions = self._by_game.get(game_id, [])
        else:
            sessions = self.sessions
        if game_id and username:
            sessions = [session for session in sessions if session.game_id == game_id]
        return list(sessions)[:limit]

    def filter_sessions(self, username: str | None = None, game_id: str | None = None, result: str | None = None, limit: int = 25) -> list[GameSession]:
        # TODO (DONE)(HISTORY INDEX): Add date range and outcome indexes for scale.
        if result:
            sessions = list(self._by_result.get(result.lower(), []))
        elif username:
            sessions = list(self._by_player.get(username, []))
        elif game_id:
            sessions = list(self._by_game.get(game_id, []))
        else:
            sessions = list(self.sessions)
        if username:
            sessions = [session for session in sessions if session.username == username]
        if game_id:
            sessions = [session for session in sessions if session.game_id == game_id]
        return sessions[:limit]

    def get_sessions_by_date_range(self, start_date: str, end_date: str, limit: int = 25) -> list[GameSession]:
        # TODO (DONE)(DATE RANGE QUERY): Use sorted chronological traversal.
        if start_date > end_date:
            start_date, end_date = end_date, start_date
        return [session for session in self.sorted_by_date(self.sessions, descending=False) if start_date <= session.played_at <= end_date][:limit]

    def sorted_by_date(self, sessions: list[GameSession], descending: bool = True) -> list[GameSession]:
        # TODO (DONE)(SORTING): Route through placeholders/sorting_algorithms.py.
        return self.sorting.sort_match_history(sessions, "played_at") if descending else list(reversed(self.sorting.sort_match_history(sessions, "played_at")))
