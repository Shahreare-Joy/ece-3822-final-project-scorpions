from __future__ import annotations

from client.models import LeaderboardEntry


# Temporary UI mock scores. TODO(LEADERBOARD): Replace with heap/BST/sorting logic.
MOCK_LEADERBOARD: list[LeaderboardEntry] = [
    LeaderboardEntry("scorpions-arena", "ren", "RenRunner", 48200, 126, 1),
    LeaderboardEntry("scorpions-arena", "joy", "Joy", 43100, 94, 2),
    LeaderboardEntry("scorpions-arena", "maya", "MayaStorm", 40750, 78, 3),
    LeaderboardEntry("scorpions-arena", "alex", "AlexByte", 36640, 43, 4),
    LeaderboardEntry("scorpions-arena", "nora", "NoraNova", 30120, 21, 5),
]

