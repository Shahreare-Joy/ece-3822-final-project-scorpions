from __future__ import annotations

from dataclasses import dataclass


@dataclass
class ClientGame:
    """Client-side game card/detail model.

    TODO(CATALOG): Populate these fields from platform_server/catalog.py after
    the real game catalog index is built.
    """

    game_id: str
    title: str
    genre: str
    playable: bool = False
    status: str = "Placeholder"
