from __future__ import annotations

import json
from pathlib import Path

from client.placeholders.dataset_cleaning import CleaningHooks


class DatasetHook:
    """Synthetic dataset loading and cleaning helper."""

    def __init__(self, cleaner: CleaningHooks | None = None) -> None:
        # use provided cleaner or default cleaning hooks
        self.cleaner = cleaner or CleaningHooks()

    def load_raw_records(self, path: Path) -> list[dict[str, object]]:
        '''load raw json records from file'''

        # return empty if file does not exist
        if not path.exists():
            return []

        # load json data
        with path.open("r", encoding="utf-8") as file:
            data = json.load(file)

        # return only dictionary records
        return [row for row in data if isinstance(row, dict)] if isinstance(data, list) else []

    def clean_records(self, records: list[dict[str, object]]) -> list[dict[str, object]]:
        '''clean and normalize generic dataset records'''

        # TODO (DONE)(CLEANING): Normalize names, remove invalid records, parse scores,
        # validate timestamps, and document every rule for the report.

        cleaned: list[dict[str, object]] = []

        for record in records:
            # include record only if no rejection reason
            if self.cleaner.reject_reason(record) is None:
                cleaned.append(self.cleaner.normalize_record(record))

        return cleaned

    def load_players(self, path: Path) -> list[dict[str, object]]:
        '''load and clean player records'''

        # TODO (DONE)(DATASET): Load synthetic player rows through the cleaning pipeline.

        return [
            self.cleaner.normalize_player_record(row)
            for row in self.load_raw_records(path)
            if self.cleaner.reject_reason(row) is None
        ]

    def load_sessions(self, path: Path) -> list[dict[str, object]]:
        '''load and clean session records'''

        # TODO (DONE)(DATASET): Load session rows for later indexing.

        return [
            self.cleaner.normalize_session_record(row)
            for row in self.load_raw_records(path)
            if self.cleaner.reject_reason(row) is None
        ]

    def load_games(self, path: Path) -> list[dict[str, object]]:
        '''load and clean game catalog records'''

        # TODO (DONE)(DATASET): Load catalog rows for browse/search/discover views.

        return self.clean_records(self.load_raw_records(path))

    def load_chat_messages(self, path: Path) -> list[dict[str, object]]:
        '''load and clean chat message records'''

        # TODO (DONE)(DATASET): Load optional chat seed data while runtime chat stays bounded.

        return self.clean_records(self.load_raw_records(path))