from __future__ import annotations

"""Lazy exports for client placeholder helpers.

The in-game chat overlay only needs `CircularChatBuffer`. Eagerly importing all
placeholder modules pulls in sorting/algorithm scaffolds, which can conflict
with self-contained game folders that also have a local `datastructures`
package. Lazy exports keep game-overlay imports isolated.
"""

from importlib import import_module
from typing import Any


__all__ = [
    "AnalysisHooks",
    "ChatChannelIndexHook",
    "CircularChatBuffer",
    "CleaningHooks",
    "GameCatalogIndexHook",
    "LeaderboardIndexHook",
    "MatchHistoryIndexHook",
    "PlayerIndexHook",
    "ProfileStatsHook",
    "QueryMetrics",
    "RecommendationGraphHook",
    "SortingHooks",
]


_EXPORTS: dict[str, tuple[str, str]] = {
    "AnalysisHooks": ("client.placeholders.analysis", "AnalysisHooks"),
    "CircularChatBuffer": ("client.placeholders.chat_buffer", "CircularChatBuffer"),
    "CleaningHooks": ("client.placeholders.dataset_cleaning", "CleaningHooks"),
    "ChatChannelIndexHook": ("client.placeholders.data_structures", "ChatChannelIndexHook"),
    "GameCatalogIndexHook": ("client.placeholders.data_structures", "GameCatalogIndexHook"),
    "LeaderboardIndexHook": ("client.placeholders.data_structures", "LeaderboardIndexHook"),
    "MatchHistoryIndexHook": ("client.placeholders.data_structures", "MatchHistoryIndexHook"),
    "PlayerIndexHook": ("client.placeholders.data_structures", "PlayerIndexHook"),
    "ProfileStatsHook": ("client.placeholders.data_structures", "ProfileStatsHook"),
    "QueryMetrics": ("client.placeholders.data_structures", "QueryMetrics"),
    "RecommendationGraphHook": ("client.placeholders.data_structures", "RecommendationGraphHook"),
    "SortingHooks": ("client.placeholders.sorting_algorithms", "SortingHooks"),
}


def __getattr__(name: str) -> Any:
    if name not in _EXPORTS:
        raise AttributeError(f"module 'client.placeholders' has no attribute {name!r}")
    module_name, attr_name = _EXPORTS[name]
    value = getattr(import_module(module_name), attr_name)
    globals()[name] = value
    return value
