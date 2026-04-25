"""Leaderboard tests.

TODO (DONE)(TESTS): Validate heap-based top-N, player rank lookup, and score
range queries.
"""

import unittest

from platform_server.leaderboard import LeaderboardService


class TestLeaderboard(unittest.TestCase):
    def test_top_rank_and_range(self) -> None:
        service = LeaderboardService()
        service.submit_score("fruit", "joy", 100)
        service.submit_score("fruit", "mykai", 200)
        service.submit_score("fruit", "hamza", 150)

        self.assertEqual([row.username for row in service.top_n("fruit", 2)], ["mykai", "hamza"])
        self.assertEqual(service.player_rank("fruit", "joy"), 3)
        self.assertEqual({row.username for row in service.score_range("fruit", 120, 210)}, {"mykai", "hamza"})


if __name__ == "__main__":
    unittest.main()
