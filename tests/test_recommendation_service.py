from __future__ import annotations

import unittest

from client.models import Game, GameSession, Player
from client.services.recommendation_service import RecommendationService


def game(game_id: str, genre: str, tags: list[str], players_now: int = 10, playable: bool = False) -> Game:
    return Game(
        game_id=game_id,
        title=game_id.replace("-", " ").title(),
        genre=genre,
        description="test game",
        creator="tests",
        players_now=players_now,
        total_plays=players_now * 100,
        status="Live",
        playable=playable,
        color=(100, 120, 140),
        tags=tags,
        release_year=2026,
        last_updated="today",
        activity_note="test",
    )


class RecommendationServiceTests(unittest.TestCase):
    def setUp(self) -> None:
        self.games = {
            "fruit": game("fruit", "Arcade", ["collection", "action"], players_now=100, playable=True),
            "escape": game("escape", "Action", ["racing", "escape"], players_now=90, playable=True),
            "forgotten": game("forgotten", "Adventure", ["mystery", "action"], players_now=80, playable=True),
            "logic": game("logic", "Puzzle", ["logic"], players_now=300),
            "racer": game("racer", "Racing", ["racing", "speed"], players_now=120),
        }
        self.sessions = [
            GameSession("s1", "fruit", "shahreare", "Win", 100, 5, "2026-04-20T12:00:00", "Complete"),
            GameSession("s2", "escape", "shahreare", "Win", 120, 7, "2026-04-21T12:00:00", "Complete"),
            GameSession("s3", "forgotten", "similar", "Win", 200, 10, "2026-04-22T12:00:00", "Complete"),
            GameSession("s4", "fruit", "similar", "Win", 220, 11, "2026-04-23T12:00:00", "Complete"),
        ]
        self.service = RecommendationService(self.games, self.sessions)

    def test_recently_played_uses_player_history_newest_unique_games(self) -> None:
        player = Player("shahreare", "Shahreare", "", "USA", 2026, 1, "Arcade", 0, 0, "Online", "", "")

        recent = self.service.recently_played(player, limit=3)

        self.assertEqual([row.game_id for row in recent], ["escape", "fruit"])

    def test_new_player_gets_popular_fallback(self) -> None:
        player = Player("new", "New", "", "USA", 2026, 1, "Arcade", 0, 0, "Online", "", "")

        recent = self.service.recently_played(player, limit=2)

        self.assertEqual(len(recent), 2)
        self.assertIn(recent[0].game_id, self.games)

    def test_recommendations_use_tags_genres_and_coplay_not_random(self) -> None:
        player = Player("shahreare", "Shahreare", "", "USA", 2026, 1, "Arcade", 0, 0, "Online", "", "")

        recommendations = self.service.recommended(player, limit=3)
        ids = [row.game_id for row in recommendations]

        self.assertIn("forgotten", ids)
        self.assertTrue(any(row.genre in {"Adventure", "Racing"} or "racing" in row.tags for row in recommendations))


if __name__ == "__main__":
    unittest.main()
