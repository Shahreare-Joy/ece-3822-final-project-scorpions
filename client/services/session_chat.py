from __future__ import annotations

from client.models import ChatMessage
from client.placeholders import CircularChatBuffer


class SessionChat:
    """Chat log for one game session.

    One SessionChat belongs to one session_id. It stores only the newest
    capacity messages so the UI cannot grow memory forever during long sessions.

    TODO(CHAT STRUCTURE): If circular buffer is one of the team's final required
    structures, add tests, complexity notes, and benchmark notes. If not, keep
    this API stable while replacing the internal storage with the chosen design.
    """

    def __init__(self, session_id: str, capacity: int = 50) -> None:
        self.session_id = session_id
        self.messages = CircularChatBuffer(capacity)

    def add_message(self, message: ChatMessage) -> None:
        self.messages.append(message)

    def recent_messages(self, limit: int | None = None) -> list[ChatMessage]:
        return self.messages.recent(limit)
