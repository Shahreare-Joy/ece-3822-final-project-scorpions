from __future__ import annotations

"""Synthetic dataset ingestion scaffold.

This module loads the committed dataset from `data/synthetic_dataset/`, validates
basic required fields, and returns records for platform services.

Important:
    Loading/validation is okay here. Final backend work still belongs to the
    team:
    - cleaning noisy records
    - resolving duplicates
    - building custom Hash Table / BST / Heap / Graph / CircularBuffer indexes
    - benchmarking indexed logic against brute force

Expected committed files:
    - players.json: 10,000+ player records
    - sessions.json: 100,000+ game session records
    - chat_messages.json: 50,000+ chat message records
    - game_catalog.json: 100+ game catalog records
"""

import json
from pathlib import Path
from typing import Any


DATASET_FILES = {
    "players": "players.json",
    "sessions": "sessions.json",
    "chat_messages": "chat_messages.json",
    "game_catalog": "game_catalog.json",
}

REQUIRED_FIELDS = {
    "players": {"player_id", "username", "display_name", "created_at", "region", "favorite_genre"},
    "sessions": {"session_id", "player_id", "username", "game_id", "started_at", "duration_seconds", "score", "outcome"},
    "chat_messages": {"message_id", "session_id", "player_id", "game_id", "sent_at", "text"},
    "game_catalog": {"game_id", "title", "creator", "genre", "playable", "total_plays", "currently_playing"},
}

EXPECTED_MINIMUM_COUNTS = {
    "players": 10_000,
    "sessions": 100_000,
    "chat_messages": 50_000,
    "game_catalog": 100,
}


class DataIngestService:
    """Starter service for synthetic dataset loading.

    TODO(CLEANING):
        Add noisy-data cleaning rules here after the final generator supports
        optional bad records. Examples: duplicate usernames, invalid timestamps,
        negative scores, missing game ids, and empty chat messages.

    TODO(DATA STRUCTURES):
        After validation, pass records to the final custom structures:
        - players -> account/profile hash table and search structure
        - sessions -> history indexes and leaderboard builders
        - chat_messages -> bounded per-session circular buffers, if restored
        - game_catalog -> catalog hash table, genre index, recommendation graph
    """

    def __init__(self, dataset_root: Path | str = "data/synthetic_dataset") -> None:
        self.dataset_root = Path(dataset_root)

    def load_json_file(self, dataset_name: str) -> list[dict[str, Any]]:
        """Load one dataset file safely.

        Returns an empty list if the file is missing so the server scaffold can
        still start before the team generates the dataset.
        """

        file_name = DATASET_FILES[dataset_name]
        path = self.dataset_root / file_name
        if not path.exists():
            return []
        with path.open("r", encoding="utf-8") as file:
            data = json.load(file)
        if not isinstance(data, list):
            raise ValueError(f"{file_name} must contain a JSON list of records.")
        return [row for row in data if isinstance(row, dict)]

    def validate_records(self, dataset_name: str, rows: list[dict[str, Any]]) -> list[str]:
        """Return validation errors for missing fields and undersized datasets."""

        errors: list[str] = []
        required = REQUIRED_FIELDS[dataset_name]
        minimum = EXPECTED_MINIMUM_COUNTS[dataset_name]
        if rows and len(rows) < minimum:
            errors.append(f"{dataset_name} has {len(rows)} records; expected at least {minimum}.")
        for index, row in enumerate(rows[:100]):
            missing = required - set(row.keys())
            if missing:
                errors.append(f"{dataset_name}[{index}] missing fields: {sorted(missing)}")
        return errors

    def load_players(self) -> list[dict[str, Any]]:
        rows = self.load_json_file("players")
        # TODO(CLEANING): Normalize usernames and detect duplicates before indexing.
        return rows

    def load_games(self) -> list[dict[str, Any]]:
        rows = self.load_json_file("game_catalog")
        # TODO(CATALOG): Load these into the final game registry/catalog indexes.
        return rows

    def load_sessions(self) -> list[dict[str, Any]]:
        rows = self.load_json_file("sessions")
        # TODO(HISTORY): Build player/game/date/outcome indexes from these rows.
        return rows

    def load_leaderboards(self) -> list[dict[str, Any]]:
        # TODO(LEADERBOARD): Derive leaderboard entries from sessions or add a
        # committed leaderboard file if the final report needs one.
        return []

    def load_chat_messages(self) -> list[dict[str, Any]]:
        rows = self.load_json_file("chat_messages")
        # TODO(CHAT): Optionally restore recent messages into circular buffers.
        return rows

    def validate_all(self) -> list[str]:
        """Validate all committed dataset files."""

        errors: list[str] = []
        for dataset_name in DATASET_FILES:
            rows = self.load_json_file(dataset_name)
            if not rows:
                errors.append(f"{dataset_name} is missing or empty. Run data/generate_dataset.py.")
                continue
            errors.extend(self.validate_records(dataset_name, rows))
        return errors

    def load_all(self) -> dict[str, list[dict[str, Any]]]:
        """Load all datasets for platform-server startup.

        TODO(INTEGRATION): After cleaning, return model objects or index-ready
        records, then hand them to services in platform_server/server.py.
        """

        return {
            "players": self.load_players(),
            "sessions": self.load_sessions(),
            "chat_messages": self.load_chat_messages(),
            "game_catalog": self.load_games(),
        }
