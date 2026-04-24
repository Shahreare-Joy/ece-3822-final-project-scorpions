from __future__ import annotations

"""Session chat service.

Likely data structure: CircularBuffer from datastructures/circular_buffer.py.

Each active game session has its own bounded chat log. Only recent messages are
kept so memory does not grow forever.
"""

from dataclasses import dataclass
from datetime import datetime, timezone

from datastructures.circular_buffer import CircularBuffer
from datastructures.hash_table import ChainedHashTable

from .moderation import ChatModerationService


@dataclass
class ChatRecord:
    session_id: str
    sender: str
    text: str
    sent_at: str


class ChatService:
    def __init__(self, capacity: int = 100) -> None:
        self.capacity = capacity
        self._channels = ChainedHashTable()  # TODO (DONE): hash table session_id -> CircularBuffer.
        self._moderation = ChatModerationService()

    def add_message(self, session_id: str, sender: str, text: str) -> bool:
        # TODO (DONE)(RESILIENCE): Validate session_id, sender, and text before mutation.
        # TODO (DONE)(MODERATION): Call ChatModerationService and return a safe error if blocked.
        # TODO (DONE)(CHAT): Sanitize text, append to session circular buffer.
        # TODO(C++ RELAY): Broadcast accepted messages only to players in this session.
        if not session_id or not sender or not isinstance(text, str):
            return False
        result = self._moderation.validate_message(session_id, sender, text)
        if not result.allowed:
            return False
        channel = self._get_channel(session_id)
        channel.append(ChatRecord(session_id, sender, result.cleaned_text, datetime.now(timezone.utc).isoformat()))
        return True

    def recent_messages(self, session_id: str, limit: int = 50) -> list[ChatRecord]:
        # TODO (DONE)(RESILIENCE): Return [] for unknown sessions.
        # TODO (DONE)(CIRCULAR BUFFER): Return newest messages from session channel only.
        channel = self._channels.get(session_id)
        if not isinstance(channel, CircularBuffer):
            return []
        return channel.recent(max(1, min(int(limit), self.capacity)))

    def _get_channel(self, session_id: str) -> CircularBuffer:
        channel = self._channels.get(session_id)
        if not isinstance(channel, CircularBuffer):
            channel = CircularBuffer(self.capacity)
            self._channels.put(session_id, channel)
        return channel
