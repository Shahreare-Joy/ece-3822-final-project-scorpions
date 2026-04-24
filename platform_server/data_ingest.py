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

# Canonical field names match Task 5 dataset spec.
# sent_at/text/currently_playing are kept in the JSON for backward compat
# but timestamp/message/players_now are the required canonical names.
REQUIRED_FIELDS = {
    "players": {
        "player_id", "username", "display_name", "country", "created_at",
        "favorite_genre", "level", "total_score", "games_played", "wins", "losses",
    },
    "sessions": {
        "session_id", "player_id", "game_id", "started_at", "ended_at",
        "duration_seconds", "score", "outcome",
    },
    "chat_messages": {
        "message_id", "session_id", "player_id", "timestamp", "message",
    },
    "game_catalog": {
        "game_id", "title", "genre", "creator", "description", "playable",
        "total_plays", "players_now", "created_at", "last_updated",
    },
}

# Type expectations for basic validation: field -> expected Python type
FIELD_TYPES: dict[str, dict[str, type]] = {
    "players": {
        "total_score": int,
        "games_played": int,
        "wins": int,
        "losses": int,
        "level": int,
    },
    "sessions": {
        "score": int,
        "duration_seconds": int,
    },
    "chat_messages": {},
    "game_catalog": {
        "playable": bool,
        "total_plays": int,
        "players_now": int,
    },
}

# ID field for each dataset — used for duplicate detection
ID_FIELDS = {
    "players": "player_id",
    "sessions": "session_id",
    "chat_messages": "message_id",
    "game_catalog": "game_id",
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
        """Return validation errors for missing fields, wrong types, and undersized datasets."""
        errors: list[str] = []
        required = REQUIRED_FIELDS[dataset_name]
        type_checks = FIELD_TYPES.get(dataset_name, {})
        minimum = EXPECTED_MINIMUM_COUNTS[dataset_name]

        # Count check
        if rows and len(rows) < minimum:
            errors.append(
                f"{dataset_name} has {len(rows)} records; expected at least {minimum}."
            )

        # Field presence and type checks — sample first 100 records only
        for index, row in enumerate(rows[:100]):
            missing = required - set(row.keys())
            if missing:
                errors.append(
                    f"{dataset_name}[{index}] missing fields: {sorted(missing)}"
                )
            # Basic type validation
            for field, expected_type in type_checks.items():
                if field in row and not isinstance(row[field], expected_type):
                    errors.append(
                        f"{dataset_name}[{index}] field '{field}' expected "
                        f"{expected_type.__name__}, got {type(row[field]).__name__}"
                    )

        return errors

    def find_duplicates(self, dataset_name: str, rows: list[dict[str, Any]]) -> list[str]:
        """Return a list of duplicate ID warnings for the given dataset."""
        errors: list[str] = []
        id_field = ID_FIELDS.get(dataset_name)
        if not id_field:
            return errors

        seen: set[str] = set()
        for index, row in enumerate(rows):
            record_id = row.get(id_field)
            if record_id is None:
                errors.append(f"{dataset_name}[{index}] missing {id_field}")
            elif record_id in seen:
                errors.append(f"{dataset_name}: duplicate {id_field} '{record_id}' at index {index}")
            else:
                seen.add(record_id)

        return errors

    def load_players(self) -> list[dict[str, Any]]:
        rows = self.load_json_file("players")
        # TODO(CLEANING): Normalize usernames and detect duplicates before indexing.

        # Duplicate username detection — report but do not drop records yet.
        # TODO(DATA STRUCTURES): After deduplication, load into:
        #   - hash table keyed by player_id  for O(1) profile lookup
        #   - hash table keyed by username   for O(1) login/search lookup
        #   - search index (BST or Trie)     for prefix autocomplete
        usernames_seen: set[str] = set()
        for i, row in enumerate(rows):
            uname = row.get("username")
            if uname in usernames_seen:
                print(f"[data_ingest] WARNING: duplicate username '{uname}' at players[{i}]")
            else:
                usernames_seen.add(uname)

        return rows

    def load_games(self) -> list[dict[str, Any]]:
        rows = self.load_json_file("game_catalog")
        # TODO(CATALOG): Load these into the final game registry/catalog indexes.

        # TODO(DATA STRUCTURES): After loading, pass rows to:
        #   - hash table keyed by game_id    for O(1) catalog lookup
        #   - genre index                    for filtered browsing
        #   - recommendation graph           for related-games feature
        #   - mergesort / heapsort           for popularity/recency ordering
        return rows

    def load_sessions(self) -> list[dict[str, Any]]:
        rows = self.load_json_file("sessions")
        # TODO(HISTORY): Build player/game/date/outcome indexes from these rows.

        # TODO(DATA STRUCTURES): After loading, pass rows to:
        #   - hash table: player_id  -> list[session]  for history lookup
        #   - hash table: game_id    -> list[session]  for game history
        #   - BST / time index: started_at             for date range queries
        #   - mergesort: sort sessions by started_at or score for history display
        #   - heapsort / heap: derive leaderboard top-N per game
        return rows

    def load_leaderboards(self) -> list[dict[str, Any]]:
        # TODO(LEADERBOARD): Derive leaderboard entries from sessions or add a
        # committed leaderboard file if the final report needs one.

        # TODO(DATA STRUCTURES): Once sessions are loaded, pass to:
        #   - custom Heap keyed by score per game_id   for top_n() queries
        #   - BST keyed by score per game_id           for score_range() queries
        #   - heapsort from algorithms/heapsort.py     for full leaderboard sort
        return []

    def load_chat_messages(self) -> list[dict[str, Any]]:
        rows = self.load_json_file("chat_messages")
        # TODO(CHAT): Optionally restore recent messages into circular buffers.

        # TODO(DATA STRUCTURES): After loading, pass rows to:
        #   - circular buffer keyed by session_id      for recent chat display
        return rows

    def validate_all(self) -> list[str]:
        """Validate all committed dataset files — field presence, types, and duplicates."""
        errors: list[str] = []
        for dataset_name in DATASET_FILES:
            rows = self.load_json_file(dataset_name)
            if not rows:
                errors.append(
                    f"{dataset_name} is missing or empty. Run data/generate_dataset.py."
                )
                continue
            errors.extend(self.validate_records(dataset_name, rows))
            errors.extend(self.find_duplicates(dataset_name, rows))
        return errors

    def load_all(self) -> dict[str, list[dict[str, Any]]]:
        """Load all datasets for platform-server startup.

        TODO(INTEGRATION): After cleaning, return model objects or index-ready
        records, then hand them to services in platform_server/server.py.
        """
        return {
            "players":      self.load_players(),
            "sessions":     self.load_sessions(),
            "chat_messages": self.load_chat_messages(),
            "game_catalog": self.load_games(),
        }
