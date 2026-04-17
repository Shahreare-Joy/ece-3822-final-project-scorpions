from __future__ import annotations

"""Match history service.

Likely data structures:
- Hash table: username -> sessions
- Hash table: game_id -> sessions
- BST/time index: date range queries over 100,000+ sessions
- Sorting algorithms: date/score ordering for report comparisons

TODO(HISTORY): Do not scan every session in the final version. Build indexes
after dataset loading.
"""


class HistoryService:
    def __init__(self) -> None:
        self._player_sessions = None  # TODO: custom hash table index.
        self._game_sessions = None  # TODO: custom hash table index.
        self._date_index = None  # TODO: custom BST/time index.

    def by_player(self, username: str, limit: int = 50) -> list[object]:
        _ = (username, limit)
        raise NotImplementedError("Team must implement player history lookup.")

    def by_game(self, game_id: str, limit: int = 50) -> list[object]:
        _ = (game_id, limit)
        raise NotImplementedError("Team must implement game history lookup.")

    def by_date_range(self, start: str, end: str, limit: int = 100) -> list[object]:
        _ = (start, end, limit)
        raise NotImplementedError("Team must implement date range lookup.")

    def by_outcome(self, result: str, limit: int = 100) -> list[object]:
        _ = (result, limit)
        raise NotImplementedError("Team must implement outcome filtering.")
