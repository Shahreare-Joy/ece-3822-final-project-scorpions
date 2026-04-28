from __future__ import annotations

from datetime import datetime
import json
import re
from pathlib import Path
from typing import Any

from client.models import ChatMessage
from .session_chat import SessionChat


BLOCKED_CHAT_WORDS = {"badword", "spamword"}


class ChatService:
    """Per-session chat manager used by the arcade and launched games.

    Each session_id maps to its own SessionChat, and each SessionChat keeps a
    bounded message log. When storage_dir is provided, messages are saved to a
    shared JSON file per session. That lets multiple local game/client processes
    using the same project folder see each other's messages without requiring
    the unfinished C++ socket server.

    TODO(CHAT/C++): Connect add_message to the C++ multiplayer server so new
    messages are validated, sanitized, and broadcast to every player in the
    session across different machines. The current file-backed bridge works for
    local/shared-folder play and keeps the overlay API stable for that upgrade.

    Requirement target: one chat channel per active game session. Keep only the
    most recent N messages per session on the client so long-running matches do
    not grow memory forever.
    """

    def __init__(self, messages: list[ChatMessage], capacity: int = 50, storage_dir: str | Path | None = None) -> None:
        self.capacity = capacity
        self.session_chats: dict[str, SessionChat] = {}
        self.storage_dir = Path(storage_dir) if storage_dir else None
        if self.storage_dir is not None:
            self.storage_dir.mkdir(parents=True, exist_ok=True)
        for message in messages:
            self.get_or_create_session_chat(message.session_id).add_message(message)

    def get_or_create_session_chat(self, session_id: str) -> SessionChat:
        session_id = session_id.strip() or "global"
        if session_id not in self.session_chats:
            self.session_chats[session_id] = SessionChat(session_id, self.capacity)
            self._load_session_from_disk(session_id)
        return self.session_chats[session_id]

    def add_message(self, session_id: str, sender: str, text: str, channel: str = "session", timestamp: str | None = None) -> ChatMessage:
        # Keep the working local/file-backed chat flow, but sanitize content
        # before it is stored or displayed. Avoid importing platform_server here
        # because launched game subprocesses depend on this lightweight path.
        cleaned_text = self._filter_blocked_words(self._clean_text(text))[:240]
        when = timestamp or datetime.now().strftime("%H:%M")
        message = ChatMessage(channel, sender.strip() or "Guest", cleaned_text, when, session_id=session_id.strip() or "global")
        self.get_or_create_session_chat(message.session_id).add_message(message)
        self._save_session_to_disk(message.session_id)
        # TODO(CHAT/C++): Broadcast this message to all players in the session.
        return message

    def get_recent_messages(self, session_id: str, limit: int | None = None) -> list[ChatMessage]:
        # Reload from disk before rendering so another launched game process can
        # add a message and this process will show it on the next draw.
        if self.storage_dir is not None:
            self._load_session_from_disk(session_id.strip() or "global")
        chat = self.get_or_create_session_chat(session_id)
        return chat.recent_messages(limit)

    def get_chat_preview(self, session_id: str = "global", limit: int = 3) -> list[ChatMessage]:
        return self.get_recent_messages(session_id, limit)

    def close_session(self, session_id: str, remove_disk_file: bool = True) -> None:
        """Drop local chat state when a player leaves a game session.

        The real C++ relay is still scaffolded, so this cleans the local
        per-session buffer and optional file-backed bridge used by subprocess
        games. It prevents abandoned local sessions from accumulating forever.
        """

        safe_id = session_id.strip() or "global"
        self.session_chats.pop(safe_id, None)
        if remove_disk_file:
            path = self._session_path(safe_id)
            if path is not None:
                try:
                    path.unlink(missing_ok=True)
                except OSError:
                    pass

    def _session_path(self, session_id: str) -> Path | None:
        if self.storage_dir is None:
            return None
        safe_id = re.sub(r"[^A-Za-z0-9_.-]+", "_", session_id.strip() or "global")
        return self.storage_dir / f"{safe_id}.json"

    def _load_session_from_disk(self, session_id: str) -> None:
        path = self._session_path(session_id)
        if path is None or not path.exists():
            return
        try:
            rows = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return
        if not isinstance(rows, list):
            return
        chat = SessionChat(session_id, self.capacity)
        for row in rows[-self.capacity :]:
            if isinstance(row, dict):
                chat.add_message(self._message_from_record(row, session_id))
        self.session_chats[session_id] = chat

    def _save_session_to_disk(self, session_id: str) -> None:
        path = self._session_path(session_id)
        if path is None:
            return
        chat = self.get_or_create_session_chat(session_id)
        records = [self._message_to_record(message) for message in chat.recent_messages(self.capacity)]
        temp_path = path.with_suffix(".tmp")
        try:
            temp_path.write_text(json.dumps(records, indent=2), encoding="utf-8")
            temp_path.replace(path)
        except OSError:
            pass

    @staticmethod
    def _message_to_record(message: ChatMessage) -> dict[str, str]:
        return {
            "channel": message.channel,
            "sender": message.sender,
            "text": message.text,
            "timestamp": message.timestamp,
            "session_id": message.session_id,
        }

    def _message_from_record(self, record: dict[str, Any], fallback_session_id: str) -> ChatMessage:
        return ChatMessage(
            str(record.get("channel", "session")),
            str(record.get("sender", "Guest")),
            self._filter_blocked_words(self._clean_text(str(record.get("text", ""))))[:240],
            str(record.get("timestamp", "")),
            session_id=str(record.get("session_id") or fallback_session_id),
        )

    @staticmethod
    def _clean_text(text: str) -> str:
        """Strip control characters and normalize whitespace."""

        printable = "".join(character for character in str(text) if character.isprintable())
        return " ".join(printable.strip().split())

    @staticmethod
    def _filter_blocked_words(text: str) -> str:
        """Replace whole-word blocked terms without changing normal words."""

        def replace(match: re.Match[str]) -> str:
            token = match.group(0)
            return "*" * len(token) if token.lower() in BLOCKED_CHAT_WORDS else token

        return re.sub(r"\b[A-Za-z0-9_]+\b", replace, text)
