from __future__ import annotations

from scorpions_arcade.models import Genre, Player


# Temporary UI mock data only. TODO(DATASET): Replace with cleaned player records.
MOCK_PLAYERS: list[Player] = [
    # TODO(AVATAR): Replace avatar_id mock choices with account profile settings.
    Player("joy", "Joy", "123456", "USA", 2022, 42, Genre.ARCADE.value, 318, 94, "Online", "Platform founder, striker main, and leaderboard chaser.", "avatar_joy"),
    Player("maya", "MayaStorm", "mock", "USA", 2021, 37, Genre.STRATEGY.value, 241, 78, "In Match", "Prefers puzzle ladders and late-night co-op runs.", "avatar_maya"),
    Player("ren", "RenRunner", "mock", "Canada", 2020, 51, Genre.RACING.value, 402, 126, "Online", "Speedrun ghost data collector.", "avatar_ren"),
    Player("alex", "AlexByte", "mock", "USA", 2019, 29, Genre.ACTION.value, 176, 43, "Away", "Builds bots, breaks metas, writes notes.", "avatar_alex"),
    Player("nora", "NoraNova", "mock", "UK", 2023, 18, Genre.PLATFORMER.value, 88, 21, "Online", "New player climbing fast.", "avatar_nora"),
    Player("sam", "SamuraiSam", "mock", "USA", 2021, 33, Genre.ADVENTURE.value, 198, 56, "Offline", "Dungeon mapper and badge collector.", "avatar_sam"),
]
