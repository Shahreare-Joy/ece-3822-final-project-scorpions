from __future__ import annotations

"""Small active-session tracker for the Python platform facade.

The current C++ game server owns its own TCP sockets. This manager handles the
Python-side lifecycle: which arcade sessions are considered active, when a
player last checked in, and when stale local/chat state can be safely removed.
"""

from dataclasses import dataclass
from time import time

from datastructures.hash_table import ChainedHashTable


DEFAULT_SESSION_TIMEOUT_SECONDS = 90.0


@dataclass
class ActiveSession:
    session_id: str
    username: str
    game_id: str
    started_at: float
    last_seen_at: float
    status: str = "active"


class SessionManager:
    """Track active sessions and remove stale entries.

    Beginner-friendly rule: every session must have a matching cleanup path.
    Call start_session when a game begins, heartbeat while it is running, and
    end_session from finally/quit paths. cleanup_stale_sessions is the safety
    net for crashed clients that never send an end event.
    """

    def __init__(self, timeout_seconds: float = DEFAULT_SESSION_TIMEOUT_SECONDS) -> None:
        self.timeout_seconds = timeout_seconds
        self._sessions = ChainedHashTable()

    def start_session(self, session_id: str, username: str, game_id: str) -> ActiveSession:
        now = time()
        session = ActiveSession(
            session_id=self._safe_session_id(session_id),
            username=(username or "guest").strip().lower(),
            game_id=(game_id or "unknown-game").strip(),
            started_at=now,
            last_seen_at=now,
        )
        self._sessions.put(session.session_id, session)
        return session

    def heartbeat(self, session_id: str) -> bool:
        session = self._get_session(session_id)
        if session is None:
            return False
        session.last_seen_at = time()
        return True

    def end_session(self, session_id: str, reason: str = "ended") -> bool:
        session = self._get_session(session_id)
        if session is None:
            return False
        session.status = reason
        return self._sessions.remove(session.session_id)

    def cleanup_stale_sessions(self) -> list[str]:
        now = time()
        removed: list[str] = []
        for session in list(self.active_sessions()):
            if now - session.last_seen_at > self.timeout_seconds:
                if self.end_session(session.session_id, "timeout"):
                    removed.append(session.session_id)
        return removed

    def shutdown(self) -> int:
        sessions = list(self.active_sessions())
        for session in sessions:
            self.end_session(session.session_id, "shutdown")
        return len(sessions)

    def active_sessions(self) -> list[ActiveSession]:
        sessions: list[ActiveSession] = []
        for _, session in self._sessions.items():
            if isinstance(session, ActiveSession):
                sessions.append(session)
        return sessions

    def _get_session(self, session_id: str) -> ActiveSession | None:
        session = self._sessions.get(self._safe_session_id(session_id))
        return session if isinstance(session, ActiveSession) else None

    @staticmethod
    def _safe_session_id(session_id: str) -> str:
        return (session_id or "local-demo-session").strip() or "local-demo-session"
