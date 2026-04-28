from __future__ import annotations

import tempfile
import unittest

from client.services.chat_service import ChatService as ClientChatService
from platform_server.chat import ChatService as PlatformChatService
from platform_server.moderation import ChatModerationService


class ChatModerationTests(unittest.TestCase):
    def test_moderation_filters_bad_words_case_insensitively(self) -> None:
        moderation = ChatModerationService()

        result = moderation.validate_message("session-1", "joy", "This has BADWORD inside")

        self.assertTrue(result.allowed)
        self.assertEqual(result.cleaned_text, "This has ******* inside")

    def test_moderation_uses_whole_tokens_not_partial_words(self) -> None:
        moderation = ChatModerationService()

        result = moderation.validate_message("session-1", "joy", "badwording is not the same token")

        self.assertTrue(result.allowed)
        self.assertEqual(result.cleaned_text, "badwording is not the same token")

    def test_platform_chat_stores_cleaned_message(self) -> None:
        service = PlatformChatService(capacity=5)

        accepted = service.add_message("session-1", "joy", "please remove badword")
        messages = service.recent_messages("session-1", 5)

        self.assertTrue(accepted)
        self.assertEqual(messages[-1].text, "please remove *******")

    def test_client_chat_filters_before_file_backed_storage_and_display(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            writer = ClientChatService([], capacity=5, storage_dir=tmp)
            writer.add_message("session-1", "Joy", "client BADWORD test")

            reader = ClientChatService([], capacity=5, storage_dir=tmp)
            messages = reader.get_recent_messages("session-1", 5)

            self.assertEqual(messages[-1].text, "client ******* test")


if __name__ == "__main__":
    unittest.main()
