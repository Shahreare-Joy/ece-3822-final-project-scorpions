from __future__ import annotations

from algorithms.heapsort import heapsort
from algorithms.mergesort import mergesort


class SortingHooks:
    """Starter placeholder for required sorting algorithm work."""

    def sort_catalog(self, records: list[object], sort_by: str) -> list[object]:
        '''sort catalog records using merge sort'''

        # TODO (DONE)(SORTING): Dispatch catalog sorting to mergesort.

        # choose key based on selected sort field
        key = self._key_for(sort_by)

        # descending for popularity-style fields
        return mergesort(records, key=key, reverse=sort_by in {"players", "plays", "popularity", "total_plays"})

    def sort_leaderboard(self, records: list[object], sort_by: str) -> list[object]:
        '''sort leaderboard records using heap sort'''

        # TODO (DONE)(SORTING): Use heap sort for numeric leaderboard metrics.

        # default to score if no sort field is provided
        key = self._key_for(sort_by or "score")

        # sort highest numeric values first
        return heapsort(records, key=lambda row: int(key(row) or 0), reverse=True)

    def sort_match_history(self, records: list[object], sort_by: str) -> list[object]:
        '''sort match history records using merge sort'''

        # TODO (DONE)(SORTING): Use mergesort for chronological/session sorting.

        # default to timestamp if no sort field is provided
        key = self._key_for(sort_by or "timestamp")

        # newest records first
        return mergesort(records, key=key, reverse=True)

    def _key_for(self, field_name: str):
        '''return key function for selected field'''

        # map UI names to dataset field names
        aliases = {
            "players": "players_now",
            "plays": "total_plays",
            "popularity": "total_plays",
            "date": "timestamp",
            "started_at": "timestamp",
        }

        # use alias if available
        field = aliases.get(field_name, field_name)

        def key(record: object) -> object:
            '''read sort value from dict or object'''

            # support dictionary records
            if isinstance(record, dict):
                return record.get(field, record.get(field_name, ""))

            # support dataclass/object records
            return getattr(record, field, getattr(record, field_name, ""))

        return key