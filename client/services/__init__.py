from __future__ import annotations

"""Service exports for the Pygame client.

This module intentionally uses lazy imports. Fruit Collection imports
`client.components.ChatOverlay`, and the overlay imports `client.services.chat_service`.
If this package eagerly imports every service, the game subprocess can pull in
the full platform backend and accidentally shadow project-level packages with
game-local folders. Lazy exports keep the chat overlay lightweight.
"""

from importlib import import_module
from typing import Any


__all__ = [
    "AuthService",
    "DEFAULT_ACCOUNT_PATH",
    "DemoAccountStore",
    "CatalogService",
    "ChatService",
    "GameLaunchService",
    "GAME_LAUNCH_TARGETS",
    "GameLaunchTarget",
    "HistoryService",
    "LaunchRequest",
    "LaunchResult",
    "LeaderboardService",
    "MockArcadeBackend",
    "ProfileService",
    "RecommendationService",
    "SearchService",
    "SessionChat",
    "ClientResultReport",
    "SessionResultService",
]


_EXPORTS: dict[str, tuple[str, str]] = {
    "AuthService": ("client.services.auth_service", "AuthService"),
    "DEFAULT_ACCOUNT_PATH": ("client.services.account_store", "DEFAULT_ACCOUNT_PATH"),
    "DemoAccountStore": ("client.services.account_store", "DemoAccountStore"),
    "CatalogService": ("client.services.catalog_service", "CatalogService"),
    "ChatService": ("client.services.chat_service", "ChatService"),
    "GameLaunchService": ("client.services.game_launch_service", "GameLaunchService"),
    "LaunchRequest": ("client.services.game_launch_service", "LaunchRequest"),
    "LaunchResult": ("client.services.game_launch_service", "LaunchResult"),
    "GAME_LAUNCH_TARGETS": ("client.services.game_launch_registry", "GAME_LAUNCH_TARGETS"),
    "GameLaunchTarget": ("client.services.game_launch_registry", "GameLaunchTarget"),
    "HistoryService": ("client.services.history_service", "HistoryService"),
    "LeaderboardService": ("client.services.leaderboard_service", "LeaderboardService"),
    "MockArcadeBackend": ("client.services.arcade_backend", "MockArcadeBackend"),
    "ProfileService": ("client.services.profile_service", "ProfileService"),
    "RecommendationService": ("client.services.recommendation_service", "RecommendationService"),
    "SearchService": ("client.services.search_service", "SearchService"),
    "SessionChat": ("client.services.session_chat", "SessionChat"),
    "ClientResultReport": ("client.services.session_result_service", "ClientResultReport"),
    "SessionResultService": ("client.services.session_result_service", "SessionResultService"),
}


def __getattr__(name: str) -> Any:
    if name not in _EXPORTS:
        raise AttributeError(f"module 'client.services' has no attribute {name!r}")
    module_name, attr_name = _EXPORTS[name]
    value = getattr(import_module(module_name), attr_name)
    globals()[name] = value
    return value
