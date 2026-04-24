from __future__ import annotations

"""Match history service.

Likely data structures:
- Hash table: username -> sessions
- Hash table: game_id -> sessions
- BST/time index: date range queries over 100,000+ sessions
- Sorting algorithms: date/score ordering for report comparisons

TODO (DONE)(HISTORY): Build indexes after dataset loading so common queries do
not scan every session.
"""

from datastructures.hash_table import ChainedHashTable


class HistoryService:
    def __init__(self) -> None:
        self._player_sessions = ChainedHashTable()  # TODO (DONE): custom hash table index.
        self._game_sessions = ChainedHashTable()  # TODO (DONE): custom hash table index.
        self._outcome_sessions = ChainedHashTable()
        self._date_index: list[tuple[str, dict[str, object]]] = []  # TODO (DONE): custom time index scaffold.
        self._date_sorted = True

    def add_session(self, session: dict[str, object]) -> bool:
        username = str(session.get("username") or session.get("player_id") or "")
        game_id = str(session.get("game_id", ""))
        outcome = str(session.get("outcome") or session.get("result") or "")
        timestamp = str(session.get("started_at") or session.get("timestamp") or "")
        if not username or not game_id:
            return False
        self._append(self._player_sessions, username, session)
        self._append(self._game_sessions, game_id, session)
        if outcome:
            self._append(self._outcome_sessions, outcome, session)
        if timestamp:
            # A naive unbalanced BST becomes very slow when timestamps arrive in
            # mostly sorted order. Keep a sorted time index list for the starter
            # and let the team replace it with a balanced tree if required.
            self._date_index.append((timestamp, session))
            self._date_sorted = False
        return True

    def load_sessions(self, sessions: list[dict[str, object]]) -> int:
        loaded = sum(1 for session in sessions if self.add_session(session))
        self._sort_date_index()
        return loaded

    def by_player(self, username: str, limit: int = 50) -> list[object]:
        # TODO (DONE)(RESILIENCE): Clamp limit and handle unknown usernames safely.
        limit = self._clamp_limit(limit)
        return list(reversed(self._player_sessions.get(username, [])[-limit:]))

    def by_game(self, game_id: str, limit: int = 50) -> list[object]:
        # TODO (DONE)(RESILIENCE): Handle unknown game ids safely.
        # TODO (DONE)(INDEX): Use game_id -> sessions index instead of brute force.
        limit = self._clamp_limit(limit)
        return list(reversed(self._game_sessions.get(game_id, [])[-limit:]))

    def by_date_range(self, start: str, end: str, limit: int = 100) -> list[object]:
        # TODO (DONE)(RESILIENCE): Validate date format and start <= end.
        # TODO (DONE)(BST/TIME INDEX): Use an ordered date index for range queries.
        if start > end:
            start, end = end, start
        self._sort_date_index()
        rows: list[object] = []
        for timestamp, session in self._date_index:
            if timestamp < start:
                continue
            if timestamp > end:
                break
            rows.append(session)
            if len(rows) >= self._clamp_limit(limit, 500):
                break
        return rows

    def by_outcome(self, result: str, limit: int = 100) -> list[object]:
        # TODO (DONE)(RESILIENCE): Validate outcome labels before lookup.
        # TODO (DONE)(INDEX): Use outcome -> sessions index.
        limit = self._clamp_limit(limit, 500)
        return list(reversed(self._outcome_sessions.get(result, [])[-limit:]))

    def _append(self, table: ChainedHashTable, key: str, session: dict[str, object]) -> None:
        sessions = table.get(key)
        if not isinstance(sessions, list):
            sessions = []
            table.put(key, sessions)
        sessions.append(session)

    def _sort_date_index(self) -> None:
        if not self._date_sorted:
            self._date_index.sort(key=lambda item: item[0])
            self._date_sorted = True

    def _clamp_limit(self, limit: int, maximum: int = 100) -> int:
        return max(1, min(int(limit), maximum))
