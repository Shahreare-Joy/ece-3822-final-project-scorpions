from __future__ import annotations

import unittest

from platform_server.session_manager import SessionManager


class SessionManagerTests(unittest.TestCase):
    def test_start_heartbeat_end_and_shutdown(self) -> None:
        manager = SessionManager(timeout_seconds=30)
        session = manager.start_session("session-1", "Shahreare", "game_1")

        self.assertEqual(session.username, "shahreare")
        self.assertTrue(manager.heartbeat("session-1"))
        self.assertEqual(len(manager.active_sessions()), 1)
        self.assertTrue(manager.end_session("session-1"))
        self.assertEqual(manager.active_sessions(), [])

        manager.start_session("session-2", "Hamza", "game_2")
        manager.start_session("session-3", "Mykai", "game_3")
        self.assertEqual(manager.shutdown(), 2)
        self.assertEqual(manager.active_sessions(), [])

    def test_cleanup_stale_sessions(self) -> None:
        manager = SessionManager(timeout_seconds=0)
        manager.start_session("stale", "Kevin", "game_4")

        removed = manager.cleanup_stale_sessions()

        self.assertEqual(removed, ["stale"])
        self.assertEqual(manager.active_sessions(), [])


if __name__ == "__main__":
    unittest.main()
