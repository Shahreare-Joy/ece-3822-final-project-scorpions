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
    # session this message belongs to
    session_id: str

    # player/user who sent the message
    sender: str

    # cleaned message text
    text: str

    # timestamp when message was accepted
    sent_at: str


class ChatService:
    def __init__(self, capacity: int = 100) -> None:
        # store max number of recent messages per session
        self.capacity = capacity

        # hash table maps session_id -> CircularBuffer
        self._channels = ChainedHashTable()  # TODO (DONE): hash table session_id -> CircularBuffer.

        # moderation service checks and cleans messages
        self._moderation = ChatModerationService()

    def add_message(self, session_id: str, sender: str, text: str) -> bool:
        '''validate, clean, and store chat message'''

        # TODO (DONE)(RESILIENCE): Validate session_id, sender, and text before mutation.
        # TODO (DONE)(MODERATION): Call ChatModerationService and return a safe error if blocked.
        # TODO (DONE)(CHAT): Sanitize text, append to session circular buffer.
        # TODO(C++ RELAY): Broadcast accepted messages only to players in this session.

        # reject missing session/sender or invalid text
        if not session_id or not sender or not isinstance(text, str):
            return False

        # check message through moderation service
        result = self._moderation.validate_message(session_id, sender, text)

        # reject blocked messages
        if not result.allowed:
            return False

        # get or create chat buffer for this session
        channel = self._get_channel(session_id)

        # append accepted chat record with UTC timestamp
        channel.append(ChatRecord(session_id, sender, result.cleaned_text, datetime.now(timezone.utc).isoformat()))
        return True

    def recent_messages(self, session_id: str, limit: int = 50) -> list[ChatRecord]:
        '''return recent messages for one session'''

        # TODO (DONE)(RESILIENCE): Return [] for unknown sessions.
        # TODO (DONE)(CIRCULAR BUFFER): Return newest messages from session channel only.

        # lookup chat channel by session id
        channel = self._channels.get(session_id)

        # unknown session has no messages
        if not isinstance(channel, CircularBuffer):
            return []

        # clamp limit and return recent records
        return channel.recent(max(1, min(int(limit), self.capacity)))

    def _get_channel(self, session_id: str) -> CircularBuffer:
        '''get existing channel or create a new one'''

        # lookup existing session channel
        channel = self._channels.get(session_id)

        # create new circular buffer if session does not have one yet
        if not isinstance(channel, CircularBuffer):
            channel = CircularBuffer(self.capacity)
            self._channels.put(session_id, channel)

        return channel