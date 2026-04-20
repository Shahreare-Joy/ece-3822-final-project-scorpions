from __future__ import annotations

"""Client-side completed session result model.

Games should eventually report a small payload with score/outcome/duration when
they exit. This model keeps that payload shape clear for the UI/client layer.
"""

from dataclasses import dataclass, field
from typing import Any


@dataclass
class ClientSessionResult:
    """Serializable game result sent from the client to the platform server."""

    player_id: str
    game_id: str
    score: int
    outcome: str
    duration_seconds: int
    timestamp: str
    session_id: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_payload(self) -> dict[str, Any]:
        """Return the wire/API payload for platform_server/session_results.py."""

        return {
            "player_id": self.player_id,
            "game_id": self.game_id,
            "score": self.score,
            "outcome": self.outcome,
            "duration_seconds": self.duration_seconds,
            "timestamp": self.timestamp,
            "session_id": self.session_id,
            "metadata": self.metadata,
        }

    @classmethod
    def from_game_return(cls, payload: dict[str, Any]) -> "ClientSessionResult":
        """Normalize a result dict returned by a future run_game(...) adapter."""

        return cls(
            player_id=str(payload.get("player_id") or payload.get("username") or "guest"),
            game_id=str(payload.get("game_id", "")),
            score=int(payload.get("score", 0)),
            outcome=str(payload.get("outcome") or payload.get("result") or "Finished"),
            duration_seconds=int(payload.get("duration_seconds") or payload.get("duration") or 0),
            timestamp=str(payload.get("timestamp", "")),
            session_id=str(payload.get("session_id", "")),
            metadata=dict(payload.get("metadata", {})) if isinstance(payload.get("metadata", {}), dict) else {},
        )
