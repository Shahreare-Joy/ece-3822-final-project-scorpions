from __future__ import annotations

from scorpions_arcade.models import GameSession


# Temporary UI mock session history. TODO(HISTORY): Replace with custom history index.
MOCK_SESSIONS: list[GameSession] = [
    GameSession("S-89421", "scorpions-arena", "joy", "Win", 18420, 12, "Today 09:15", "Complete"),
    GameSession("S-89388", "sky-raiders", "joy", "Loss", 7400, 8, "Yesterday 21:42", "Complete"),
    GameSession("S-89310", "turbo-sprint", "joy", "Top 3", 12880, 6, "2 days ago", "Complete"),
    GameSession("S-89277", "block-arena", "maya", "Win", 22300, 18, "2 days ago", "Complete"),
    GameSession("S-89201", "neon-strikers", "ren", "Win", 31400, 9, "3 days ago", "Complete"),
    GameSession("S-89164", "crystal-run", "nora", "Checkpoint 7", 9800, 14, "4 days ago", "Saved"),
    GameSession("S-89012", "castle-quest", "sam", "Win", 15800, 27, "Last week", "Complete"),
    GameSession("S-88990", "logic-lab", "alex", "Solved", 7600, 5, "Last week", "Complete"),
    GameSession("S-88941", "metro-drift", "ren", "Best Lap", 22100, 7, "Last week", "Complete"),
    GameSession("S-88876", "pixel-patrol", "maya", "Wave 28", 36400, 16, "2 weeks ago", "Complete"),
    GameSession("S-88812", "cloud-courier", "nora", "Route Saved", 11200, 11, "2 weeks ago", "Saved"),
    GameSession("S-88780", "dragon-dock", "sam", "Raid Win", 27650, 24, "3 weeks ago", "Complete"),
]

