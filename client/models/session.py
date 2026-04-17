from __future__ import annotations

from dataclasses import dataclass


@dataclass
class ClientSession:
    """Client-side match history row model.

    TODO(HISTORY): Load real session rows from platform_server/history.py and
    keep screen rendering separate from history filtering/index logic.
    """

    session_id: str
    game_id: str
    username: str
    score: int
    result: str
