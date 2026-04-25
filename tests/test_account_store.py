from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from client.models import Player
from client.services.account_store import DemoAccountStore
from client.services.auth_service import AuthService


class AccountPersistenceTests(unittest.TestCase):
    def test_created_account_persists_and_reloads(self) -> None:
        '''test that created account is saved and can be loaded again'''

        # create temporary folder for test account file
        with tempfile.TemporaryDirectory() as tmp:
            # create account store using temporary json path
            store = DemoAccountStore(Path(tmp) / "demo_accounts.json")

            # create empty player dictionary
            players: dict[str, Player] = {}

            # create auth service using account store
            auth = AuthService(players, store)

            # create new account
            result = auth.create_account("demo_user", "Demo User", "secret1", "secret1", "USA")

            # account creation should succeed
            self.assertTrue(result.success)

            # simulate app restart with fresh player dictionary and auth service
            reloaded_players: dict[str, Player] = {}
            reloaded_auth = AuthService(reloaded_players, store)

            # authenticate using persisted account
            login = reloaded_auth.authenticate("demo_user", "secret1")

            # login should succeed after reload
            self.assertTrue(login.success)
            self.assertEqual(login.player.display_name, "Demo User")

    def test_duplicate_username_is_rejected(self) -> None:
        '''test that duplicate username cannot be created'''

        # create temporary folder for test account file
        with tempfile.TemporaryDirectory() as tmp:
            # create account store using temporary json path
            store = DemoAccountStore(Path(tmp) / "demo_accounts.json")

            # create auth service
            auth = AuthService({}, store)

            # create first account
            first = auth.create_account("demo_user", "Demo User", "secret1", "secret1", "USA")

            # try creating duplicate account
            second = auth.create_account("demo_user", "Demo User 2", "secret2", "secret2", "USA")

            # first should succeed, second should fail
            self.assertTrue(first.success)
            self.assertFalse(second.success)
            self.assertIn("already exists", second.message)


if __name__ == "__main__":
    # run tests when file is executed directly
    unittest.main()