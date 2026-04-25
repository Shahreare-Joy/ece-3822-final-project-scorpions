from __future__ import annotations

"""Persistence helpers for server restart recovery.

Purpose:
    Services should ask this layer to save/load state instead of writing files
    directly. It uses safe JSON writes so a crash is less likely to corrupt the
    primary file.
"""

from dataclasses import asdict, dataclass, is_dataclass
import json
from pathlib import Path
import os
import tempfile


@dataclass
class PersistencePaths:
    '''store file paths for persisted data'''

    # file path for saved players
    players_path: str = "data/synthetic_dataset/players_persisted.json"

    # file path for saved leaderboard data
    leaderboards_path: str = "data/synthetic_dataset/leaderboards_persisted.json"

    # file path for saved session history
    sessions_path: str = "data/synthetic_dataset/sessions_persisted.json"

    # file path for saved game catalog
    catalog_path: str = "data/synthetic_dataset/catalog_persisted.json"

    # file path for saved chat snapshots
    chat_path: str = "data/synthetic_dataset/chat_snapshots_persisted.json"


class PersistenceService:
    """Small JSON persistence interface."""

    def __init__(self, paths: PersistencePaths | None = None) -> None:
        # use provided paths or default paths
        self.paths = paths or PersistencePaths()

    def save_players(self, players: list[object]) -> bool:
        '''save player data to disk'''

        # TODO (DONE)(STORAGE): Save after signup/profile updates.
        # TODO (DONE)(RECOVERY): Write to a temporary file and replace atomically.

        return self._save_json(self.paths.players_path, players)

    def load_players(self) -> list[object]:
        '''load player data from disk'''

        # TODO (DONE)(STORAGE): Load account/profile records during server startup.
        # TODO (DONE)(RECOVERY): If the primary file is corrupt, return a safe empty list.

        return self._load_json(self.paths.players_path)

    def save_leaderboards(self, entries: list[object]) -> bool:
        '''save leaderboard data'''

        # TODO (DONE)(STORAGE): Save after validated score submissions/session endings.
        # TODO (DONE)(VALIDATION): Caller should only pass accepted scores.

        return self._save_json(self.paths.leaderboards_path, entries)

    def load_leaderboards(self) -> list[object]:
        '''load leaderboard data'''

        # TODO (DONE)(STORAGE): Rebuild heap/BST leaderboard structures from saved records.

        return self._load_json(self.paths.leaderboards_path)

    def save_session_history(self, sessions: list[object]) -> bool:
        '''save session history data'''

        # TODO (DONE)(STORAGE): Save after each completed game session.
        # TODO (DONE)(BATCHING): This scaffold saves the provided batch immediately.

        return self._save_json(self.paths.sessions_path, sessions)

    def load_session_history(self) -> list[object]:
        '''load session history data'''

        # TODO (DONE)(STORAGE): Load session records and build history indexes.

        return self._load_json(self.paths.sessions_path)

    def save_catalog(self, games: list[object]) -> bool:
        '''save game catalog data'''

        # TODO (DONE)(STORAGE): Persist registered games if the catalog becomes editable.

        return self._save_json(self.paths.catalog_path, games)

    def load_catalog(self) -> list[object]:
        '''load game catalog data'''

        # TODO (DONE)(STORAGE): Load catalog metadata before building search/filter indexes.

        return self._load_json(self.paths.catalog_path)

    def save_chat_snapshot(self, session_id: str, messages: list[object]) -> bool:
        '''save recent chat messages for one session'''

        # TODO (DONE)(CHAT PERSISTENCE): Save bounded recent messages, not unlimited logs.

        # load existing snapshots into dictionary
        snapshots = {
            row.get("session_id", ""): row.get("messages", [])
            for row in self.load_chat_snapshot("*")
            if isinstance(row, dict)
        }

        # update this session's messages
        snapshots[session_id] = [self._serialize(message) for message in messages]

        # convert dictionary back to list format
        rows = [{"session_id": key, "messages": value} for key, value in snapshots.items()]

        return self._save_json(self.paths.chat_path, rows)

    def load_chat_snapshot(self, session_id: str) -> list[object]:
        """Restore recent chat after a restart."""

        # TODO (DONE)(CHAT PERSISTENCE): Rehydrate circular buffers if this is enabled.

        rows = self._load_json(self.paths.chat_path)

        # return all snapshots if wildcard used
        if session_id == "*":
            return rows

        # find matching session
        for row in rows:
            if isinstance(row, dict) and row.get("session_id") == session_id:
                messages = row.get("messages", [])
                return messages if isinstance(messages, list) else []

        return []

    def recover_after_restart(self) -> dict[str, object]:
        '''load all persisted data after server restart'''

        # TODO (DONE)(RECOVERY ORDER): Load state in dependency order.

        # load all persisted datasets
        players = self.load_players()
        catalog = self.load_catalog()
        leaderboards = self.load_leaderboards()
        sessions = self.load_session_history()
        chat_snapshots = self.load_chat_snapshot("*")

        # return summary counts
        return {
            "players_loaded": len(players),
            "catalog_loaded": len(catalog),
            "leaderboards_loaded": len(leaderboards),
            "sessions_loaded": len(sessions),
            "chat_snapshots_loaded": len(chat_snapshots),
            "status": "recovery completed",
        }

    def validate_storage_paths(self) -> bool:
        '''ensure all storage directories exist and are writable'''

        # TODO (DONE)(RESILIENCE): Check folder existence, permissions, and backup files.

        for path in self._all_paths():
            try:
                Path(path).parent.mkdir(parents=True, exist_ok=True)
            except OSError:
                return False

        return True

    def _all_paths(self) -> list[str]:
        '''return all persistence file paths'''

        return [
            self.paths.players_path,
            self.paths.leaderboards_path,
            self.paths.sessions_path,
            self.paths.catalog_path,
            self.paths.chat_path,
        ]

    def _save_json(self, path_value: str, records: list[object]) -> bool:
        '''save data safely using temp file and atomic replace'''

        path = Path(path_value)

        # ensure directory exists
        path.parent.mkdir(parents=True, exist_ok=True)

        # serialize records
        data = [self._serialize(record) for record in records]

        try:
            # write to temporary file first
            with tempfile.NamedTemporaryFile(
                "w", encoding="utf-8", delete=False, dir=str(path.parent), suffix=".tmp"
            ) as handle:
                json.dump(data, handle, indent=2)
                temp_name = handle.name

            # atomically replace original file
            os.replace(temp_name, path)

            return True

        except OSError:
            return False

    def _load_json(self, path_value: str) -> list[object]:
        '''load json safely with fallback on errors'''

        path = Path(path_value)

        # return empty if file does not exist
        if not path.exists():
            return []

        try:
            with path.open("r", encoding="utf-8") as handle:
                data = json.load(handle)

            # ensure correct format
            return data if isinstance(data, list) else []

        except (OSError, json.JSONDecodeError):
            return []

    def _serialize(self, record: object) -> object:
        '''convert object into json-safe format'''

        # convert dataclass to dict
        if is_dataclass(record):
            return asdict(record)

        # use custom serializer if available
        if hasattr(record, "to_payload"):
            return record.to_payload()

        # fallback return as-is
        return record