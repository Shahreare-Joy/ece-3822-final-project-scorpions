from __future__ import annotations

"""Client/UI scaffold for completed game session results.

This service sits between the active Pygame launcher and the future platform
server result processor. It keeps result handling out of screen files and out
of individual game folders.
"""

from dataclasses import dataclass, field
from typing import Any

from platform_server.session_results import SessionResult, SessionResultProcessor
from client.models import Game, Player


@dataclass
class ClientResultReport:
    """Small UI-friendly summary of result processing."""

    processed: bool
    message: str
    errors: list[str] = field(default_factory=list)


class SessionResultService:
    """Bridge from GameLaunchService results to platform_server/session_results.py."""

    def __init__(self, processor: SessionResultProcessor | None = None) -> None:
        self.processor = processor or SessionResultProcessor()

    def handle_launch_result(self, player: Player | None, game: Game, payload: dict[str, Any] | None) -> ClientResultReport:
        """Process a game result payload if the launched game provided one."""

        if payload is None:
            return ClientResultReport(
                False,
                "No score result was reported yet. Add result reporting inside the game when final scoring is ready.",
            )

        normalized = dict(payload)
        normalized.setdefault("player_id", player.username if player else "guest")
        normalized.setdefault("game_id", game.game_id)
        result = SessionResult.from_payload(normalized)
        report = self.processor.process_result(result)
        if not report.accepted:
            return ClientResultReport(False, "Session result was rejected by validation.", report.validation_errors)
        return ClientResultReport(True, report.message)
