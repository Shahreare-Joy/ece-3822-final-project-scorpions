from __future__ import annotations

from client.models import GameSession


class HistoryService:
    """Temporary session-history service.

    Requirement target: query 100,000+ sessions by player, game, date range,
    outcome, and sorted recency. Current methods scan mock rows only.

    TODO(HISTORY INDEX): Replace scans with indexes such as username -> sessions,
    game_id -> sessions, date-indexed BST/tree, or a chronological structure.
    TODO(ANALYSIS): Benchmark indexed queries against the brute-force scan.
    """

    def __init__(self, sessions: list[GameSession]) -> None:
        self.sessions = sessions

    def get_sessions(self, username: str | None = None, game_id: str | None = None, limit: int = 8) -> list[GameSession]:
        # BRUTE-FORCE MOCK WARNING:
        # Filtering 100,000+ sessions this way will not be a strong final
        # design. Replace with player/game indexes.
        # TODO(HISTORY STRUCTURE): Replace scans with indexed history queries.
        sessions = self.sessions
        if username:
            sessions = [session for session in sessions if session.username == username]
        if game_id:
            sessions = [session for session in sessions if session.game_id == game_id]
        return sessions[:limit]

    def filter_sessions(self, username: str | None = None, game_id: str | None = None, result: str | None = None, limit: int = 25) -> list[GameSession]:
        # BRUTE-FORCE MOCK WARNING:
        # The final version should combine indexes rather than repeatedly
        # scanning the entire session list.
        # TODO(HISTORY INDEX): Add date range and outcome indexes for scale.
        sessions = self.sessions
        if username:
            sessions = [session for session in sessions if session.username == username]
        if game_id:
            sessions = [session for session in sessions if session.game_id == game_id]
        if result:
            sessions = [session for session in sessions if session.result.lower() == result.lower()]
        return sessions[:limit]

    def get_sessions_by_date_range(self, start_date: str, end_date: str, limit: int = 25) -> list[GameSession]:
        # BRUTE-FORCE MOCK WARNING:
        # Date range queries should use parsed dates and a time-indexed
        # structure when the project reaches 100,000+ records.
        # TODO(DATE RANGE QUERY): Replace string scan with parsed timestamps and
        # a time-indexed structure for 100,000+ rows.
        return [session for session in self.sessions if start_date <= session.played_at <= end_date][:limit]

    def sorted_by_date(self, sessions: list[GameSession], descending: bool = True) -> list[GameSession]:
        # TODO(SORTING): Route through placeholders/sorting_algorithms.py for
        # final algorithm demonstrations.
        return sorted(sessions, key=lambda session: session.played_at, reverse=descending)
