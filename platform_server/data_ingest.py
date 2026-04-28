from __future__ import annotations

"""Synthetic dataset ingestion scaffold.

This module loads the committed dataset from `data/synthetic_dataset/`, validates
basic required fields, and returns records for platform services.
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
    "players": {"player_id", "username", "display_name", "region", "created_at", "favorite_genre", "skill_rating", "total_score", "games_played", "avatar", "account_status"},
    "sessions": {"session_id", "player_id", "username", "game_id", "game_title", "started_at", "duration_seconds", "score", "outcome", "platform", "server_region"},
    "chat_messages": {"message_id", "session_id", "player_id", "username", "game_id", "sent_at", "text", "moderation_status"},
    "game_catalog": {"game_id", "title", "creator", "genre", "playable", "launch_path", "thumbnail_path", "screenshot_paths", "created_at", "last_updated", "total_plays", "currently_playing", "min_players", "max_players", "supports_multiplayer", "status", "tags"},
}

EXPECTED_MINIMUM_COUNTS = {
    "players": 10_000,
    "sessions": 100_000,
    "chat_messages": 50_000,
    "game_catalog": 100,
}


class DataIngestService:
    """Starter service for synthetic dataset loading."""

    def __init__(self, dataset_root: Path | str = "data/synthetic_dataset") -> None:
        # store dataset root path
        self.dataset_root = Path(dataset_root)

    def load_json_file(self, dataset_name: str) -> list[dict[str, Any]]:
        '''load one dataset json file safely'''

        # get file name and build full path
        file_name = DATASET_FILES[dataset_name]
        path = self.dataset_root / file_name

        # return empty list if file does not exist
        if not path.exists():
            return []

        # load json file
        with path.open("r", encoding="utf-8") as file:
            data = json.load(file)

        # ensure file contains list of records
        if not isinstance(data, list):
            raise ValueError(f"{file_name} must contain a JSON list of records.")

        # return only dictionary rows
        return [row for row in data if isinstance(row, dict)]

    def validate_records(self, dataset_name: str, rows: list[dict[str, Any]]) -> list[str]:
        '''validate dataset records for missing fields and bad values'''

        errors: list[str] = []

        # get required fields and expected size
        required = REQUIRED_FIELDS[dataset_name]
        minimum = EXPECTED_MINIMUM_COUNTS[dataset_name]

        # check dataset size
        if rows and len(rows) < minimum:
            errors.append(f"{dataset_name} has {len(rows)} records; expected at least {minimum}.")

        seen_ids: set[str] = set()

        # determine id field based on dataset
        id_field = {
            "players": "player_id",
            "sessions": "session_id",
            "chat_messages": "message_id",
            "game_catalog": "game_id",
        }[dataset_name]

        for index, row in enumerate(rows):
            # check missing required fields
            missing = required - set(row.keys())
            if missing:
                errors.append(f"{dataset_name}[{index}] missing fields: {sorted(missing)}")

            # check id field
            record_id = str(row.get(id_field, "")).strip()
            if not record_id:
                errors.append(f"{dataset_name}[{index}] has empty {id_field}")
            elif record_id in seen_ids:
                errors.append(f"{dataset_name}[{index}] duplicates {id_field}: {record_id}")
            else:
                seen_ids.add(record_id)

            # additional checks for sessions
            if dataset_name == "sessions":
                if int(row.get("score", 0)) < 0:
                    errors.append(f"sessions[{index}] has negative score")
                if int(row.get("duration_seconds", 0)) < 0:
                    errors.append(f"sessions[{index}] has negative duration")

            # additional checks for chat messages
            if dataset_name == "chat_messages" and not str(row.get("text", "")).strip():
                errors.append(f"chat_messages[{index}] has empty text")

            # additional checks for catalog entries
            if dataset_name == "game_catalog":
                if int(row.get("min_players", 0) or 0) < 1:
                    errors.append(f"game_catalog[{index}] has invalid min_players")
                if int(row.get("max_players", 0) or 0) < int(row.get("min_players", 0) or 0):
                    errors.append(f"game_catalog[{index}] has max_players below min_players")

        return errors

    def load_players(self) -> list[dict[str, Any]]:
        '''load and deduplicate player records'''

        rows = self.load_json_file("players")

        # TODO (DONE)(CLEANING): Normalize usernames and detect duplicates before indexing.
        return self._dedupe_by_id(rows, "player_id")

    def load_games(self) -> list[dict[str, Any]]:
        '''load and deduplicate game catalog records'''

        rows = self.load_json_file("game_catalog")

        # TODO (DONE)(CATALOG): Load these into the final game registry/catalog indexes.
        return self._dedupe_by_id(rows, "game_id")

    def load_sessions(self) -> list[dict[str, Any]]:
        '''load and deduplicate session records'''

        rows = self.load_json_file("sessions")

        # TODO (DONE)(HISTORY): Build player/game/date/outcome indexes from these rows.
        return self._dedupe_by_id(rows, "session_id")

    def load_leaderboards(self) -> list[dict[str, Any]]:
        '''derive leaderboard entries from sessions'''

        best: dict[tuple[str, str], dict[str, Any]] = {}

        # iterate through all sessions
        for session in self.load_sessions():
            key = (str(session.get("game_id", "")), str(session.get("username") or session.get("player_id", "")))

            # skip invalid keys
            if not key[0] or not key[1]:
                continue

            current = best.get(key)

            # store best score per player per game
            if current is None or int(session.get("score", 0)) > int(current.get("score", 0)):
                best[key] = session

        return list(best.values())

    def load_chat_messages(self) -> list[dict[str, Any]]:
        '''load and deduplicate chat messages'''

        rows = self.load_json_file("chat_messages")

        # TODO (DONE)(CHAT): Optionally restore recent messages into circular buffers.
        return self._dedupe_by_id(rows, "message_id")

    def validate_all(self) -> list[str]:
        '''validate all datasets together'''

        errors: list[str] = []
        loaded_rows: dict[str, list[dict[str, Any]]] = {}

        # validate each dataset individually
        for dataset_name in DATASET_FILES:
            rows = self.load_json_file(dataset_name)
            loaded_rows[dataset_name] = rows

            if not rows:
                errors.append(f"{dataset_name} is missing or empty. Run data/generate_dataset.py.")
                continue

            errors.extend(self.validate_records(dataset_name, rows))

        # validate cross references between datasets
        errors.extend(self.validate_references(loaded_rows))
        return errors

    def validate_references(self, rows_by_dataset: dict[str, list[dict[str, Any]]]) -> list[str]:
        '''validate relationships between players, games, sessions, and chat'''

        errors: list[str] = []

        # collect all valid ids
        players = {str(row.get("player_id", "")).strip() for row in rows_by_dataset.get("players", [])}
        games = {str(row.get("game_id", "")).strip() for row in rows_by_dataset.get("game_catalog", [])}
        sessions = {str(row.get("session_id", "")).strip() for row in rows_by_dataset.get("sessions", [])}

        # validate session references
        for index, row in enumerate(rows_by_dataset.get("sessions", [])):
            player_id = str(row.get("player_id", "")).strip()
            game_id = str(row.get("game_id", "")).strip()

            if player_id and player_id not in players:
                errors.append(f"sessions[{index}] references missing player_id: {player_id}")
            if game_id and game_id not in games:
                errors.append(f"sessions[{index}] references missing game_id: {game_id}")

        # validate chat references
        for index, row in enumerate(rows_by_dataset.get("chat_messages", [])):
            session_id = str(row.get("session_id", "")).strip()
            player_id = str(row.get("player_id", "")).strip()
            game_id = str(row.get("game_id", "")).strip()

            if session_id and session_id not in sessions:
                errors.append(f"chat_messages[{index}] references missing session_id: {session_id}")
            if player_id and player_id not in players:
                errors.append(f"chat_messages[{index}] references missing player_id: {player_id}")
            if game_id and game_id not in games:
                errors.append(f"chat_messages[{index}] references missing game_id: {game_id}")

        return errors

    def load_all(self) -> dict[str, list[dict[str, Any]]]:
        '''load all datasets for server startup'''

        return {
            "players": self.load_players(),
            "sessions": self.load_sessions(),
            "chat_messages": self.load_chat_messages(),
            "game_catalog": self.load_games(),
        }

    def _dedupe_by_id(self, rows: list[dict[str, Any]], id_field: str) -> list[dict[str, Any]]:
        '''remove duplicates and normalize usernames'''

        cleaned: list[dict[str, Any]] = []
        seen: set[str] = set()

        for row in rows:
            record_id = str(row.get(id_field, "")).strip()

            # skip invalid or duplicate ids
            if not record_id or record_id in seen:
                continue

            seen.add(record_id)
            normalized = dict(row)

            # normalize usernames to lowercase
            if "username" in normalized:
                normalized["username"] = str(normalized["username"]).strip().lower()

            cleaned.append(normalized)

        return cleaned
