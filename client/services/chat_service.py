from __future__ import annotations

from datetime import datetime

from client.models import ChatMessage
from .session_chat import SessionChat


class ChatService:
    """Temporary per-session chat manager.

    Each session_id maps to its own SessionChat, and each SessionChat keeps a
    bounded message log. This is still a local UI/client scaffold.

    TODO(CHAT/C++): Connect add_message to the C++ multiplayer server so new
    messages are validated, sanitized, and broadcast to every player in the
    session. Add persistence only if the final design requires saved chat.

    Requirement target: one chat channel per active game session. Keep only the
    most recent N messages per session on the client so long-running matches do
    not grow memory forever.
    """

    def __init__(self, messages: list[ChatMessage], capacity: int = 50) -> None:
        self.capacity = capacity
        self.session_chats: dict[str, SessionChat] = {}
        for message in messages:
            self.get_or_create_session_chat(message.session_id).add_message(message)

    def get_or_create_session_chat(self, session_id: str) -> SessionChat:
        session_id = session_id.strip() or "global"
        if session_id not in self.session_chats:
            self.session_chats[session_id] = SessionChat(session_id, self.capacity)
        return self.session_chats[session_id]

    def add_message(self, session_id: str, sender: str, text: str, channel: str = "session", timestamp: str | None = None) -> ChatMessage:
        # TODO(CHAT): Sanitize/validate content before sending it to the server.
        cleaned_text = text.strip()[:240]
        when = timestamp or datetime.now().strftime("%H:%M")
        message = ChatMessage(channel, sender.strip() or "Guest", cleaned_text, when, session_id=session_id.strip() or "global")
        self.get_or_create_session_chat(message.session_id).add_message(message)
        # TODO(CHAT/C++): Broadcast this message to all players in the session.
        return message

    def get_recent_messages(self, session_id: str, limit: int | None = None) -> list[ChatMessage]:
        chat = self.get_or_create_session_chat(session_id)
        return chat.recent_messages(limit)

    def get_chat_preview(self, session_id: str = "global", limit: int = 3) -> list[ChatMessage]:
        return self.get_recent_messages(session_id, limit)
