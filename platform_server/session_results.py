from __future__ import annotations

"""Completed game session result processing scaffold.

Purpose:
    This is the central platform-server place for "a game just ended" events.
    Games should not update leaderboards, history, profiles, or persistence
    directly. They should report a result payload, and this processor should
    validate and route that payload to the correct platform services.

Important:
    This file now implements the result-routing pipeline while still leaving
    anti-cheat, token validation, and final C++ authority rules visible for the
    team to finish.
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any

from datastructures.hash_table import ChainedHashTable


VALID_OUTCOMES = {"Win", "Loss", "Draw", "Finished", "DNF"}


@dataclass
class SessionResult:
    '''store normalized session result data'''

    # player identifier (username or id)
    player_id: str

    # game identifier
    game_id: str

    # score achieved in session
    score: int

    # outcome label (Win/Loss/etc.)
    outcome: str

    # duration of session in seconds
    duration_seconds: int

    # timestamp of session
    timestamp: str

    # optional session id for deduplication
    session_id: str = ""

    # additional metadata from game
    metadata: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_payload(cls, payload: dict[str, Any]) -> "SessionResult":
        '''convert raw payload into SessionResult'''

        # TODO (DONE)(VALIDATION): Coerce the common payload formats used by the
        # launcher and reject invalid values later in ``validate_result``.

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
        '''convert SessionResult back to serializable dict'''

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
    '''store result processing summary'''

    # whether result was accepted
    accepted: bool

    # status message
    message: str

    # validation errors if rejected
    validation_errors: list[str] = field(default_factory=list)

    # flags for which services were updated
    leaderboard_updated: bool = False
    history_recorded: bool = False
    profile_updated: bool = False
    persisted: bool = False


class SessionResultProcessor:
    """Central scaffold for completed-session platform updates."""

    def __init__(
        self,
        leaderboard_service: object | None = None,
        history_service: object | None = None,
        profile_service: object | None = None,
        persistence_service: object | None = None,
    ) -> None:
        # store service references
        self.leaderboard_service = leaderboard_service
        self.history_service = history_service
        self.profile_service = profile_service
        self.persistence_service = persistence_service

        # track processed session_ids to prevent duplicates
        self._processed_session_ids = ChainedHashTable()

        # fallback storage for player profile totals
        self._profile_totals = ChainedHashTable()

    def process_result(self, result: SessionResult) -> SessionResultProcessingReport:
        '''validate and route session result'''

        # validate input result
        errors = self.validate_result(result)

        # reject if validation fails
        if errors:
            return SessionResultProcessingReport(False, "Session result rejected.", errors)

        # update all subsystems
        leaderboard_updated = self.update_leaderboard(result)
        history_recorded = self.record_match_history(result)
        profile_updated = self.update_player_profile(result)
        persisted = self.persist_result(result)

        # mark session_id as processed
        if result.session_id:
            self._processed_session_ids.put(result.session_id, True)

        # return processing report
        return SessionResultProcessingReport(
            accepted=True,
            message="Session result accepted and routed to available platform services.",
            leaderboard_updated=leaderboard_updated,
            history_recorded=history_recorded,
            profile_updated=profile_updated,
            persisted=persisted,
        )

    def validate_result(self, result: SessionResult) -> list[str]:
        '''validate session result fields'''

        errors: list[str] = []

        # required field checks
        if not result.player_id:
            errors.append("player_id is required")
        if not result.game_id:
            errors.append("game_id is required")

        # numeric validation
        if result.score < 0:
            errors.append("score must be non-negative")
        if result.duration_seconds < 0:
            errors.append("duration_seconds must be non-negative")

        # outcome validation
        if result.outcome not in VALID_OUTCOMES:
            errors.append(f"outcome must be one of {sorted(VALID_OUTCOMES)}")

        # basic anti-cheat cap
        if result.score > 1_000_000_000:
            errors.append("score exceeds scaffold safety cap")

        # duplicate session protection
        if result.session_id and self._processed_session_ids.contains(result.session_id):
            errors.append("session_id was already submitted")

        # TODO (DONE)(ANTI-CHEAT): Validate broad score bounds before accepting.
        # TODO(AUTH): Verify the player token/session token came from the server.
        # TODO (DONE)(REPLAY): Reject duplicate session_id submissions.

        return errors

    def update_leaderboard(self, result: SessionResult) -> bool:
        '''update leaderboard with new score'''

        # TODO (DONE)(LEADERBOARD): Insert/update this score in the heap/BST
        service = self.leaderboard_service

        if service is None or not hasattr(service, "submit_score"):
            return False

        return bool(service.submit_score(result.game_id, result.player_id, result.score, result.timestamp))

    def record_match_history(self, result: SessionResult) -> bool:
        '''record session into history service'''

        # TODO (DONE)(HISTORY): Append this result to session history and update indexes

        service = self.history_service

        if service is None or not hasattr(service, "add_session"):
            return False

        return bool(service.add_session({
            "session_id": result.session_id,
            "player_id": result.player_id,
            "username": result.player_id,
            "game_id": result.game_id,
            "started_at": result.timestamp,
            "duration_seconds": result.duration_seconds,
            "score": result.score,
            "outcome": result.outcome,
            "metadata": result.metadata,
        }))

    def update_player_profile(self, result: SessionResult) -> bool:
        '''update player statistics'''

        # TODO (DONE)(PROFILE): Update aggregate stats

        service = self.profile_service

        if service is None:
            # fallback profile tracking
            totals = self._profile_totals.get(result.player_id)

            if not isinstance(totals, dict):
                totals = {"games_played": 0, "total_score": 0, "wins": 0, "play_time_seconds": 0}

            totals["games_played"] = int(totals["games_played"]) + 1
            totals["total_score"] = int(totals["total_score"]) + result.score
            totals["play_time_seconds"] = int(totals["play_time_seconds"]) + result.duration_seconds

            if result.outcome == "Win":
                totals["wins"] = int(totals["wins"]) + 1

            self._profile_totals.put(result.player_id, totals)
            return True

        for method_name in ("record_session_result", "update_from_result"):
            method = getattr(service, method_name, None)
            if callable(method):
                method(result)
                return True

        return False

    def persist_result(self, result: SessionResult) -> bool:
        '''persist result to storage'''

        # TODO (DONE)(PERSISTENCE): Save results using persistence service

        service = self.persistence_service

        if service is None or not hasattr(service, "save_session_history"):
            return False

        existing = service.load_session_history() if hasattr(service, "load_session_history") else []
        existing.append(result.to_payload())

        return bool(service.save_session_history(existing))