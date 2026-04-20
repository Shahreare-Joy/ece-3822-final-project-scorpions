from __future__ import annotations

"""Completed game session result processing scaffold.

Purpose:
    This is the central platform-server place for "a game just ended" events.
    Games should not update leaderboards, history, profiles, or persistence
    directly. They should report a result payload, and this processor should
    validate and route that payload to the correct platform services.

Important:
    This file intentionally does not implement the final professor-required
    backend/data-structure logic. It defines the pipeline and TODO hooks so the
    team can finish those pieces without restructuring the project later.
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any


VALID_OUTCOMES = {"Win", "Loss", "Draw", "Finished", "DNF"}


@dataclass
class SessionResult:
    """Normalized completed-session result shared by platform services."""

    player_id: str
    game_id: str
    score: int
    outcome: str
    duration_seconds: int
    timestamp: str
    session_id: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_payload(cls, payload: dict[str, Any]) -> "SessionResult":
        """Build a result from a client/game payload.

        TODO(VALIDATION): In the final version, validate all fields before
        constructing this object. For now this accepts a small safe payload so
        the UI and launcher can exercise the flow.
        """

        return cls(
            player_id=str(payload.get("player_id") or payload.get("username") or "guest"),
            game_id=str(payload.get("game_id", "")),
            score=int(payload.get("score", 0)),
            outcome=str(payload.get("outcome") or payload.get("result") or "Finished"),
            duration_seconds=int(payload.get("duration_seconds") or payload.get("duration") or 0),
            timestamp=str(payload.get("timestamp") or datetime.now(timezone.utc).isoformat()),
            session_id=str(payload.get("session_id", "")),
            metadata=dict(payload.get("metadata", {})) if isinstance(payload.get("metadata", {}), dict) else {},
        )

    def to_payload(self) -> dict[str, Any]:
        """Return a serializable payload for API/file handoff."""

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


@dataclass
class SessionResultProcessingReport:
    """Summary returned after processing a completed game result."""

    accepted: bool
    message: str
    validation_errors: list[str] = field(default_factory=list)
    leaderboard_updated: bool = False
    history_recorded: bool = False
    profile_updated: bool = False
    persisted: bool = False


class SessionResultProcessor:
    """Central scaffold for completed-session platform updates.

    Expected final flow:
        validate result -> update leaderboard -> record match history ->
        update profile totals -> persist changes -> return a structured report.

    TODO(DATA STRUCTURES):
        - Leaderboards should route into the final heap/BST/ranking structures.
        - Match history should route into player/game/date indexes.
        - Profile stats should update aggregate player records.
        - Persistence should save accepted results for server restart recovery.
    """

    def __init__(
        self,
        leaderboard_service: object | None = None,
        history_service: object | None = None,
        profile_service: object | None = None,
        persistence_service: object | None = None,
    ) -> None:
        self.leaderboard_service = leaderboard_service
        self.history_service = history_service
        self.profile_service = profile_service
        self.persistence_service = persistence_service

    def process_result(self, result: SessionResult) -> SessionResultProcessingReport:
        """Validate and route a completed result.

        This method is deliberately scaffolded. It marks where final updates
        will happen, but avoids silently pretending the final backend is done.
        """

        errors = self.validate_result(result)
        if errors:
            return SessionResultProcessingReport(False, "Session result rejected.", errors)

        leaderboard_updated = self.update_leaderboard(result)
        history_recorded = self.record_match_history(result)
        profile_updated = self.update_player_profile(result)
        persisted = self.persist_result(result)

        return SessionResultProcessingReport(
            accepted=True,
            message="Session result accepted by scaffold processor. Final leaderboard/history/profile updates are TODO.",
            leaderboard_updated=leaderboard_updated,
            history_recorded=history_recorded,
            profile_updated=profile_updated,
            persisted=persisted,
        )

    def validate_result(self, result: SessionResult) -> list[str]:
        """Return validation errors for a completed result."""

        errors: list[str] = []
        if not result.player_id:
            errors.append("player_id is required")
        if not result.game_id:
            errors.append("game_id is required")
        if result.score < 0:
            errors.append("score must be non-negative")
        if result.duration_seconds < 0:
            errors.append("duration_seconds must be non-negative")
        if result.outcome not in VALID_OUTCOMES:
            errors.append(f"outcome must be one of {sorted(VALID_OUTCOMES)}")
        # TODO(ANTI-CHEAT): Validate score bounds per game before accepting.
        # TODO(AUTH): Verify the player token/session token came from the server.
        # TODO(REPLAY): Reject duplicate session_id submissions.
        return errors

    def update_leaderboard(self, result: SessionResult) -> bool:
        """Hook for leaderboard/ranking updates."""

        _ = result
        # TODO(LEADERBOARD): Insert/update this score in the final heap/BST
        # structures and support top-N, rank lookup, and score range queries.
        return False

    def record_match_history(self, result: SessionResult) -> bool:
        """Hook for storing completed session history."""

        _ = result
        # TODO(HISTORY): Append this result to session history and update
        # indexes by player_id, game_id, date/time, and outcome.
        return False

    def update_player_profile(self, result: SessionResult) -> bool:
        """Hook for player aggregate stats."""

        _ = result
        # TODO(PROFILE): Update games played, total score, win/loss counts,
        # favorite game/genre stats, and play-time totals.
        return False

    def persist_result(self, result: SessionResult) -> bool:
        """Hook for saving accepted results after processing."""

        _ = result
        # TODO(PERSISTENCE): Call PersistenceService.save_session_history(...)
        # and PersistenceService.save_leaderboards(...) after real structures
        # are updated. Use crash-safe writes in the final version.
        return False
