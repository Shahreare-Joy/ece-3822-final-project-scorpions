from __future__ import annotations

"""Session chat service.

Likely data structure: CircularBuffer from datastructures/circular_buffer.py.

Each active game session should have its own bounded chat log. Keep only the
most recent N messages so memory does not grow forever.
"""


class ChatService:
    def __init__(self, capacity: int = 100) -> None:
        self.capacity = capacity
        self._channels = None  # TODO: hash table session_id -> CircularBuffer.

    def add_message(self, session_id: str, sender: str, text: str) -> None:
        # TODO(CHAT): Sanitize text, append to session circular buffer, relay to C++.
        _ = (session_id, sender, text)
        raise NotImplementedError("Team must implement bounded session chat.")

    def recent_messages(self, session_id: str, limit: int = 50) -> list[object]:
        # TODO(CIRCULAR BUFFER): Return newest messages from session channel.
        _ = (session_id, limit)
        raise NotImplementedError("Team must implement recent chat retrieval.")
