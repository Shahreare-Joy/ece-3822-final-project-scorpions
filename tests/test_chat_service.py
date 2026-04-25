from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from client.services.chat_service import ChatService


class ChatServiceBridgeTests(unittest.TestCase):
    def test_file_backed_session_chat_round_trip(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            storage = Path(tmp)
            writer = ChatService([], capacity=3, storage_dir=storage)
            writer.add_message("session-1", "Joy", "first")
            writer.add_message("session-1", "Mykai", "second")

            reader = ChatService([], capacity=3, storage_dir=storage)
            messages = reader.get_recent_messages("session-1", 5)

            self.assertEqual([message.text for message in messages], ["first", "second"])
            self.assertTrue((storage / "session-1.json").exists())

    def test_file_backed_chat_keeps_recent_capacity(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            service = ChatService([], capacity=2, storage_dir=tmp)
            service.add_message("session-2", "A", "one")
            service.add_message("session-2", "A", "two")
            service.add_message("session-2", "A", "three")

            reloaded = ChatService([], capacity=2, storage_dir=tmp)
            messages = reloaded.get_recent_messages("session-2", 5)

            self.assertEqual([message.text for message in messages], ["two", "three"])


if __name__ == "__main__":
    unittest.main()
