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
    # store account username
    username: str

    # store hashed password instead of plain text
    password_hash: str

    # store display name shown in UI
    display_name: str


class AccountService:
    def __init__(self) -> None:
        # create hash table for username -> AccountRecord lookup
        self._account_index = ChainedHashTable()  # TODO (DONE): replace with ChainedHashTable.

    def signup(self, username: str, password: str, display_name: str) -> bool:
        '''create a new account if input is valid'''

        # TODO (DONE)(RESILIENCE): Validate required fields, duplicate usernames, and bad input.
        # TODO (DONE)(PERSISTENCE): Return a success flag so server/persistence can save after insertion.
        # TODO (DONE)(HASH TABLE): Insert account into custom hash table.

        # normalize username for consistent lookup
        normalized = self._normalize_username(username)

        # reject empty username, weak password, or empty display name
        if not normalized or len(password) < 4 or not display_name.strip():
            return False

        # reject duplicate username
        if self._account_index.contains(normalized):
            return False

        # store new account in custom hash table
        self._account_index.put(normalized, AccountRecord(normalized, self._hash_password(password), display_name.strip()))
        return True

    def login(self, username: str, password: str) -> bool:
        '''validate login credentials'''

        # TODO (DONE)(RESILIENCE): Return a safe error for missing or malformed credentials.
        # TODO (DONE)(HASH TABLE): Lookup username in custom hash table, validate password.

        # normalize username before lookup
        normalized = self._normalize_username(username)

        # reject missing username or password
        if not normalized or not password:
            return False

        # get account record from hash table
        account = self._account_index.get(normalized)

        # compare stored password hash with input password hash
        return isinstance(account, AccountRecord) and account.password_hash == self._hash_password(password)

    def load_accounts(self, rows: list[dict[str, object]]) -> int:
        """Load account-like player rows from the dataset."""

        loaded = 0

        for row in rows:
            # read username and display name from dataset row
            username = str(row.get("username", ""))
            display_name = str(row.get("display_name", username))

            # Dataset seed accounts use a deterministic starter password for
            # demos only. Replace this policy before any real deployment.
            if self.signup(username, "demo", display_name):
                loaded += 1

        return loaded

    def _normalize_username(self, username: str) -> str:
        '''normalize username for case-insensitive matching'''

        # trim spaces and convert to lowercase
        return username.strip().lower()

    def _hash_password(self, password: str) -> str:
        '''hash password for storage'''

        # Class-project starter hash. A real account server should use a salted
        # password hashing function such as bcrypt/argon2.
        return hashlib.sha256(password.encode("utf-8")).hexdigest()