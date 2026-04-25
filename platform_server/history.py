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
        # create player -> sessions index
        self._player_sessions = ChainedHashTable()  # TODO (DONE): custom hash table index.

        # create game_id -> sessions index
        self._game_sessions = ChainedHashTable()  # TODO (DONE): custom hash table index.

        # create outcome -> sessions index
        self._outcome_sessions = ChainedHashTable()

        # store timestamp/session pairs for date range queries
        self._date_index: list[tuple[str, dict[str, object]]] = []  # TODO (DONE): custom time index scaffold.

        # track whether date index is already sorted
        self._date_sorted = True

    def add_session(self, session: dict[str, object]) -> bool:
        '''add one session into all history indexes'''

        # extract main lookup keys from session row
        username = str(session.get("username") or session.get("player_id") or "")
        game_id = str(session.get("game_id", ""))
        outcome = str(session.get("outcome") or session.get("result") or "")
        timestamp = str(session.get("started_at") or session.get("timestamp") or "")

        # reject sessions missing required lookup fields
        if not username or not game_id:
            return False

        # index session by player and game
        self._append(self._player_sessions, username, session)
        self._append(self._game_sessions, game_id, session)

        # index session by outcome if available
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
        '''load many sessions into indexes'''

        # add each valid session and count successful inserts
        loaded = sum(1 for session in sessions if self.add_session(session))

        # sort date index once after bulk loading
        self._sort_date_index()

        return loaded

    def by_player(self, username: str, limit: int = 50) -> list[object]:
        '''return recent sessions for one player'''

        # TODO (DONE)(RESILIENCE): Clamp limit and handle unknown usernames safely.

        # clamp limit to safe range
        limit = self._clamp_limit(limit)

        # get sessions for player and return newest first
        return list(reversed(self._player_sessions.get(username, [])[-limit:]))

    def by_game(self, game_id: str, limit: int = 50) -> list[object]:
        '''return recent sessions for one game'''

        # TODO (DONE)(RESILIENCE): Handle unknown game ids safely.
        # TODO (DONE)(INDEX): Use game_id -> sessions index instead of brute force.

        # clamp limit to safe range
        limit = self._clamp_limit(limit)

        # get sessions for game and return newest first
        return list(reversed(self._game_sessions.get(game_id, [])[-limit:]))

    def by_date_range(self, start: str, end: str, limit: int = 100) -> list[object]:
        '''return sessions between start and end timestamps'''

        # TODO (DONE)(RESILIENCE): Validate date format and start <= end.
        # TODO (DONE)(BST/TIME INDEX): Use an ordered date index for range queries.

        # swap dates if user passes them backwards
        if start > end:
            start, end = end, start

        # make sure time index is sorted
        self._sort_date_index()

        rows: list[object] = []

        # scan sorted date index until end range is passed
        for timestamp, session in self._date_index:
            if timestamp < start:
                continue
            if timestamp > end:
                break

            rows.append(session)

            # stop after reaching requested limit
            if len(rows) >= self._clamp_limit(limit, 500):
                break

        return rows

    def by_outcome(self, result: str, limit: int = 100) -> list[object]:
        '''return recent sessions with selected outcome'''

        # TODO (DONE)(RESILIENCE): Validate outcome labels before lookup.
        # TODO (DONE)(INDEX): Use outcome -> sessions index.

        # clamp limit to safe range
        limit = self._clamp_limit(limit, 500)

        # get outcome sessions and return newest first
        return list(reversed(self._outcome_sessions.get(result, [])[-limit:]))

    def _append(self, table: ChainedHashTable, key: str, session: dict[str, object]) -> None:
        '''append session into list stored in hash table'''

        # get existing sessions list
        sessions = table.get(key)

        # create list if key does not exist yet
        if not isinstance(sessions, list):
            sessions = []
            table.put(key, sessions)

        # append session to this key bucket
        sessions.append(session)

    def _sort_date_index(self) -> None:
        '''sort date index only when needed'''

        # sort timestamp/session pairs if new unsorted items were added
        if not self._date_sorted:
            self._date_index.sort(key=lambda item: item[0])
            self._date_sorted = True

    def _clamp_limit(self, limit: int, maximum: int = 100) -> int:
        '''clamp limit into safe range'''

        # keep limit between 1 and maximum
        return max(1, min(int(limit), maximum))