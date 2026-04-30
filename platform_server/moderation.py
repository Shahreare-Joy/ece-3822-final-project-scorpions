from __future__ import annotations

"""Chat moderation helpers for all game/session chat channels.

Purpose:
    This file defines moderation features that can be used for extra credit:
    basic rate limiting, blocked-word filtering, and mute state.

Where this connects:
    platform_server/chat.py calls ChatModerationService before accepting or
    broadcasting a chat message.
"""

from dataclasses import dataclass
import re
import time

from datastructures.circular_buffer import CircularBuffer
from datastructures.hash_table import ChainedHashTable


MAX_MESSAGE_LENGTH = 240
DEFAULT_RATE_LIMIT_WINDOW_SECONDS = 10
DEFAULT_RATE_LIMIT_MESSAGE_COUNT = 5


@dataclass
class ModerationResult:
    '''result returned after validating a message'''

    # whether message is allowed
    allowed: bool

    # reason for rejection (if any)
    reason: str = ""

    # cleaned version of message text
    cleaned_text: str = ""


@dataclass
class RateLimitRule:
    '''configuration for rate limiting'''

    # time window for rate limiting
    window_seconds: int = DEFAULT_RATE_LIMIT_WINDOW_SECONDS

    # max messages allowed in window
    max_messages: int = DEFAULT_RATE_LIMIT_MESSAGE_COUNT


class ChatModerationService:
    """Moderation service shared by all session chats."""

    def __init__(self, rate_limit_rule: RateLimitRule | None = None) -> None:
        # store rate limit configuration
        self.rate_limit_rule = rate_limit_rule or RateLimitRule()

        # hash table maps player_id -> recent timestamps
        self._rate_limit_index = ChainedHashTable()  # TODO (DONE): custom hash table player_id -> send timestamps.

        # hash table stores muted players
        self._muted_players = ChainedHashTable()  # TODO (DONE): custom hash table or set-like structure.

        # hash table stores blocked words
        self._blocked_words = ChainedHashTable()  # TODO (DONE): trie/hash table of banned terms.

        # initialize default blocked words
        for word in ("spamword", "badword", "bitch", "fuck", "shit", "asshole"):
            self._blocked_words.put(word, True)

    def validate_message(self, session_id: str, player_id: str, text: str) -> ModerationResult:
        '''validate message using moderation rules'''

        # clean input text first
        cleaned_text = self.clean_text(text)

        # reject missing session or player
        if not session_id or not player_id:
            return ModerationResult(False, "Missing session or player.", cleaned_text)

        # reject empty messages
        if not cleaned_text:
            return ModerationResult(False, "Message is empty.", cleaned_text)

        # reject oversized messages
        if len(cleaned_text) > MAX_MESSAGE_LENGTH:
            return ModerationResult(False, "Message is too long.", cleaned_text[:MAX_MESSAGE_LENGTH])

        # reject muted players
        if self.is_muted(player_id, session_id):
            return ModerationResult(False, "Player is muted.", cleaned_text)

        # reject if player is rate limited
        if self.is_rate_limited(player_id):
            return ModerationResult(False, "Too many messages. Slow down.", cleaned_text)

        # filter blocked words if present
        if self.contains_blocked_word(cleaned_text):
            cleaned_text = self.filter_words(cleaned_text)

        # TODO (DONE)(MODERATION): Combine real rate-limit, mute, and content checks here.

        # record message attempt for rate limiting
        self.record_message_attempt(player_id)

        return ModerationResult(allowed=True, cleaned_text=cleaned_text)

    def mute_player(self, moderator_id: str, player_id: str, session_id: str | None = None) -> bool:
        '''mute player globally or for a session'''

        # TODO (DONE)(MODERATION): Validate moderator permissions and store mute state.

        # reject invalid input
        if not moderator_id or not player_id:
            return False

        # store mute flag in hash table
        self._muted_players.put(self._mute_key(player_id, session_id), True)
        return True

    def unmute_player(self, moderator_id: str, player_id: str, session_id: str | None = None) -> bool:
        '''remove mute from player'''

        # reject invalid input
        if not moderator_id or not player_id:
            return False

        # TODO (DONE)(MODERATION): Validate permissions and remove mute from final structure.

        # remove mute entry
        return self._muted_players.remove(self._mute_key(player_id, session_id))

    def is_muted(self, player_id: str, session_id: str | None = None) -> bool:
        '''check if player is muted globally or per session'''

        # TODO (DONE)(MUTES): Check global and per-session mute indexes.

        # check global mute and session-specific mute
        return (
            self._muted_players.contains(self._mute_key(player_id, None))
            or self._muted_players.contains(self._mute_key(player_id, session_id))
        )

    def is_rate_limited(self, player_id: str) -> bool:
        '''check if player exceeded rate limit'''

        # TODO (DONE)(RATE LIMIT): Compare send timestamps against a configurable limit.

        now = time.time()

        # get timestamp buffer for player
        timestamps = self._rate_limit_index.get(player_id)

        if not isinstance(timestamps, CircularBuffer):
            return False

        # get recent timestamps
        recent = [
            stamp
            for stamp in timestamps.recent(self.rate_limit_rule.max_messages)
            if isinstance(stamp, (int, float))
        ]

        # check if message count exceeded within window
        return (
            len(recent) >= self.rate_limit_rule.max_messages
            and now - recent[0] <= self.rate_limit_rule.window_seconds
        )

    def record_message_attempt(self, player_id: str, timestamp: float | None = None) -> None:
        '''record timestamp for rate limiting'''

        # TODO (DONE)(RATE LIMIT): Store timestamp in bounded per-player history.

        timestamps = self._rate_limit_index.get(player_id)

        # create buffer if not present
        if not isinstance(timestamps, CircularBuffer):
            timestamps = CircularBuffer(self.rate_limit_rule.max_messages)
            self._rate_limit_index.put(player_id, timestamps)

        # append new timestamp
        timestamps.append(timestamp if timestamp is not None else time.time())

    def contains_blocked_word(self, text: str) -> bool:
        '''check if message contains blocked words'''

        # TODO (DONE)(WORD FILTER): Tokenize and compare against the final blocked-word structure.

        return any(self._blocked_words.contains(token.lower()) for token in self._tokens(text))

    def clean_text(self, text: str) -> str:
        """Normalize whitespace and strip control characters."""

        # TODO (DONE)(SANITIZE): Normalize whitespace and strip control characters server-side.

        # remove non-printable characters
        cleaned = "".join(character for character in str(text) if character.isprintable())

        # normalize spaces
        return " ".join(cleaned.strip().split())

    def filter_words(self, text: str) -> str:
        '''replace blocked words with asterisks'''

        # TODO (DONE)(WORD FILTER): Implement final filtering or rejection policy.

        words = []

        for token in text.split():
            # strip punctuation for comparison
            bare = re.sub(r"[^A-Za-z0-9_]", "", token).lower()

            # replace blocked word with asterisks
            words.append("****" if self._blocked_words.contains(bare) else token)

        return " ".join(words)

    def toxicity_score(self, text: str) -> float:
        '''calculate simple toxicity score'''

        # TODO (DONE)(TOXICITY): Documented rule-based score; no external model.

        tokens = self._tokens(text)

        if not tokens:
            return 0.0

        # count blocked tokens
        blocked = sum(1 for token in tokens if self._blocked_words.contains(token))

        # return normalized score
        return min(1.0, blocked / len(tokens))

    def _tokens(self, text: str) -> list[str]:
        '''split text into lowercase tokens'''

        return [token.lower() for token in re.findall(r"[A-Za-z0-9_]+", text)]

    def _mute_key(self, player_id: str, session_id: str | None) -> str:
        '''build key for mute lookup'''

        # use "*" for global mute
        return f"{session_id or '*'}::{player_id}"
