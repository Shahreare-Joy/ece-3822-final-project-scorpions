from __future__ import annotations

from client.models import LeaderboardEntry


# Team games are new. Their leaderboards should start empty and fill only
# after real users finish sessions during the demo.
MOCK_LEADERBOARD: list[LeaderboardEntry] = []
