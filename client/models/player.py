from __future__ import annotations

from dataclasses import dataclass


@dataclass
class ClientPlayer:
    """Client-side player view model.

    TODO(PROFILE): Populate this from platform_server responses instead of mock
    data once accounts/profile lookup are implemented.
    """

    username: str
    display_name: str
    avatar_id: str = ""
    status: str = "Offline"
