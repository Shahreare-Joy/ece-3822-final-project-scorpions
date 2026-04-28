from __future__ import annotations

import os
import unittest

from client.integrations.cpp_server import GameServerConnectionInfo, PlatformConnectionInfo


class ConnectionConfigTests(unittest.TestCase):
    def setUp(self) -> None:
        self._old_env = dict(os.environ)

    def tearDown(self) -> None:
        os.environ.clear()
        os.environ.update(self._old_env)

    def test_platform_and_game_connections_use_separate_env_vars(self) -> None:
        os.environ["SCORPIONS_PLATFORM_HOST"] = "127.0.0.1"
        os.environ["SCORPIONS_PLATFORM_PORT"] = "50069"
        os.environ["SCORPIONS_GAME_HOST"] = "localhost"
        os.environ["SCORPIONS_GAME_PORT"] = "50082"

        platform = PlatformConnectionInfo.from_environment()
        game = GameServerConnectionInfo.from_environment()

        self.assertEqual((platform.host, platform.port), ("127.0.0.1", 50069))
        self.assertEqual((game.host, game.port), ("localhost", 50082))

    def test_invalid_env_port_falls_back_to_default_allowed_port(self) -> None:
        os.environ["SCORPIONS_GAME_PORT"] = "60000"

        game = GameServerConnectionInfo.from_environment()

        self.assertEqual(game.host, "127.0.0.1")
        self.assertEqual(game.port, 50068)


if __name__ == "__main__":
    unittest.main()
