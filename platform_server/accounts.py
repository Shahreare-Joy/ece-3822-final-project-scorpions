from __future__ import annotations

"""Account/login/signup service.

Likely data structure: custom chained HashTable from datastructures/hash_table.py
for username -> account lookup.

TODO(ACCOUNTS): Implement password handling, duplicate username checks, profile
creation, and dataset-backed account loading. Do not store final accounts in a
plain Python dict for the assignment.
"""


class AccountService:
    def __init__(self) -> None:
        self._account_index = None  # TODO: replace with ChainedHashTable.

    def signup(self, username: str, password: str, display_name: str) -> bool:
        # TODO(RESILIENCE): Validate required fields, duplicate usernames, and bad input.
        # TODO(PERSISTENCE): Save new accounts after successful insertion.
        # TODO(HASH TABLE): Insert account into custom hash table.
        _ = (username, password, display_name)
        raise NotImplementedError("Team must implement signup with custom hash table.")

    def login(self, username: str, password: str) -> bool:
        # TODO(RESILIENCE): Return a safe error for missing or malformed credentials.
        # TODO(HASH TABLE): Lookup username in custom hash table, validate password.
        _ = (username, password)
        raise NotImplementedError("Team must implement login with account index.")
