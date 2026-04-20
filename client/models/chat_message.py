from __future__ import annotations

from dataclasses import dataclass


@dataclass
class ChatMessage:
    """Client-side chat message record.

    session_id identifies the game session chat log this message belongs to.
    TODO(C++): Replace/extend this with server message ids and player tokens.
    """

    channel: str
    sender: str
    text: str
    timestamp: str
    session_id: str = "global"
