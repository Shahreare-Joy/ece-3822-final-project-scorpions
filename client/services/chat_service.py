from __future__ import annotations

from datetime import datetime
import json
import os
import re
import socket
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from client.models import ChatMessage
from .session_chat import SessionChat


BLOCKED_CHAT_WORDS = {"badword", "spamword", "bitch", "fuck", "shit", "asshole"}


@dataclass
class _ChatRequestResult:
    ok: bool
    message: str
    response: Any = None


class _PlatformChatConnection:
    """Tiny JSON socket client kept independent of the full arcade backend."""

    def __init__(self, host: str, port: int, timeout: float = 0.5) -> None:
        self.host = host
        self.port = int(port)
        self.timeout = timeout

    @property
    def endpoint(self) -> str:
        return f"{self.host}:{self.port}"

    def send_request(self, request: dict[str, Any]) -> _ChatRequestResult:
        try:
            with socket.create_connection((self.host, self.port), timeout=self.timeout) as sock:
                sock.settimeout(self.timeout)
                sock.sendall((json.dumps(request) + "\n").encode("utf-8"))
                chunks: list[bytes] = []
                while True:
                    chunk = sock.recv(4096)
                    if not chunk:
                        break
                    chunks.append(chunk)
                    if b"\n" in chunk:
                        break
        except OSError as exc:
            return _ChatRequestResult(False, f"Could not reach platform chat server at {self.endpoint}: {exc}")
        raw = b"".join(chunks).strip()
        if not raw:
            return _ChatRequestResult(False, "Platform chat server returned no response.")
        try:
            return _ChatRequestResult(True, "Platform chat response received.", json.loads(raw.decode("utf-8")))
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            return _ChatRequestResult(False, f"Invalid platform chat response: {exc}")


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
        self.remote_connection = self._build_remote_connection()
        self._remote_cache: dict[str, tuple[float, list[ChatMessage]]] = {}
        self.remote_poll_interval_seconds = 0.75
        self.polling_active = True
        self.remote_available = self.remote_connection is not None
        self.last_status = "Platform chat ready." if self.remote_available else "Local session chat ready."
        if self.remote_connection is not None:
            print(f"[CHAT] Platform chat sync enabled at {self.remote_connection.endpoint}.")
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
        if self.remote_connection is not None:
            result = self.remote_connection.send_request(
                {
                    "type": "chat_send",
                    "session_id": message.session_id,
                    "sender": message.sender,
                    "text": message.text,
                }
            )
            if result.ok and isinstance(result.response, dict) and result.response.get("ok"):
                print(f"[CHAT] Sent platform chat message for session {message.session_id}.")
                self.remote_available = True
                self.last_status = "Platform chat synced."
                self._remote_cache.pop(message.session_id, None)
            else:
                detail = result.message
                if isinstance(result.response, dict):
                    detail = str(result.response.get("message") or detail)
                print(f"[CHAT] Platform chat send failed; local overlay kept message. {detail}")
                self.remote_available = False
                self.last_status = "Chat server unavailable - local fallback."
        return message

    def get_recent_messages(self, session_id: str, limit: int | None = None) -> list[ChatMessage]:
        if self.remote_connection is not None and self.polling_active:
            remote_messages = self._fetch_remote_messages(session_id.strip() or "global", limit or self.capacity)
            if remote_messages is not None:
                return remote_messages
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

    def stop_polling(self) -> None:
        """Disable remote chat polling for hidden/destroyed overlays."""

        self.polling_active = False
        self._remote_cache.clear()
        self.last_status = "Chat polling stopped."

    def resume_polling(self) -> None:
        """Re-enable remote chat polling when the overlay becomes visible."""

        self.polling_active = True
        self.last_status = "Platform chat ready." if self.remote_connection is not None else "Local session chat ready."

    @property
    def remote_enabled(self) -> bool:
        return self.remote_connection is not None

    def _build_remote_connection(self) -> _PlatformChatConnection | None:
        if os.environ.get("SCORPIONS_PLATFORM_CHAT") != "1":
            return None
        host = (os.environ.get("SCORPIONS_PLATFORM_HOST") or "").strip()
        port_text = (os.environ.get("SCORPIONS_PLATFORM_PORT") or "").strip()
        if not host or not port_text:
            return None
        try:
            port = int(port_text)
        except ValueError:
            return None
        return _PlatformChatConnection(host, port, timeout=0.5)

    def _fetch_remote_messages(self, session_id: str, limit: int) -> list[ChatMessage] | None:
        if self.remote_connection is None:
            return None
        cached = self._remote_cache.get(session_id)
        now = time.monotonic()
        if cached is not None and now - cached[0] < self.remote_poll_interval_seconds:
            return cached[1][-limit:]
        result = self.remote_connection.send_request(
            {
                "type": "chat_recent",
                "session_id": session_id,
                "limit": max(1, min(int(limit), self.capacity)),
            }
        )
        if not result.ok or not isinstance(result.response, dict) or not result.response.get("ok"):
            print(f"[CHAT] Platform chat poll failed; using local cache. {result.message}")
            self.remote_available = False
            self.last_status = "Chat server unavailable - local fallback."
            return None
        self.remote_available = True
        self.last_status = "Platform chat synced."
        rows = result.response.get("messages", [])
        if not isinstance(rows, list):
            return []
        messages = [self._message_from_record(row, session_id) for row in rows if isinstance(row, dict)]
        chat = SessionChat(session_id, self.capacity)
        for message in messages:
            chat.add_message(message)
        self.session_chats[session_id] = chat
        recent = chat.recent_messages(limit)
        self._remote_cache[session_id] = (now, recent)
        return recent

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
            str(record.get("timestamp") or record.get("sent_at") or ""),
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
            return "****" if token.lower() in BLOCKED_CHAT_WORDS else token

        return re.sub(r"\b[A-Za-z0-9_]+\b", replace, text)
