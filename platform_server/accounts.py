from __future__ import annotations

"""Account/login/signup service.

Likely data structure: custom chained HashTable from datastructures/hash_table.py
for username -> account lookup.

TODO (DONE)(ACCOUNTS): Implement password handling, duplicate username checks,
profile creation, and dataset-backed account loading. This is still a class
project starter, not production authentication.
"""

from dataclasses import dataclass
import hashlib

from datastructures.hash_table import ChainedHashTable


@dataclass
class AccountRecord:
    username: str
    password_hash: str
    display_name: str


class AccountService:
    def __init__(self) -> None:
        # Main hash table storing username -> AccountRecord
        self._account_index = ChainedHashTable()  # Fast lookup for login/signup

    def signup(self, username: str, password: str, display_name: str) -> bool:
        # TODO (DONE)(RESILIENCE): Validate required fields, duplicate usernames, and bad input.
        # TODO (DONE)(PERSISTENCE): Return a success flag so server/persistence can save after insertion.
        # TODO (DONE)(HASH TABLE): Insert account into custom hash table.

        # Normalize username for consistent storage (case-insensitive login)
        normalized = self._normalize_username(username)

        # Basic validation: username exists, password length, display name not empty
        if not normalized or len(password) < 4 or not display_name.strip():
            return False

        # Prevent duplicate usernames
        if self._account_index.contains(normalized):
            return False

        # Store account with hashed password
        self._account_index.put(
            normalized,
            AccountRecord(
                normalized,
                self._hash_password(password),
                display_name.strip()
            )
        )
        return True

    def login(self, username: str, password: str) -> bool:
        # TODO (DONE)(RESILIENCE): Return a safe error for missing or malformed credentials.
        # TODO (DONE)(HASH TABLE): Lookup username in custom hash table, validate password.

        # Normalize username for lookup
        normalized = self._normalize_username(username)

        # Reject empty inputs
        if not normalized or not password:
            return False

        # Retrieve stored account
        account = self._account_index.get(normalized)

        # Validate type and compare hashed passwords
        return (
            isinstance(account, AccountRecord)
            and account.password_hash == self._hash_password(password)
        )

    def load_accounts(self, rows: list[dict[str, object]]) -> int:
        """Load account-like player rows from the dataset."""

        loaded = 0
        for row in rows:
            # Extract username and display name from dataset row
            username = str(row.get("username", ""))
            display_name = str(row.get("display_name", username))

            # Use default "demo" password for seeded accounts (NOT secure, demo only)
            if self.signup(username, "demo", display_name):
                loaded += 1
        return loaded

    def _normalize_username(self, username: str) -> str:
        # Trim spaces and force lowercase to avoid duplicates like "User" vs "user"
        return username.strip().lower()

    def _hash_password(self, password: str) -> str:
        # Class-project starter hash. A real account server should use a salted
        # password hashing function such as bcrypt/argon2.
        return hashlib.sha256(password.encode("utf-8")).hexdigest()