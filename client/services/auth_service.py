"""Client auth service adapter.

TODO(AUTH): Send login/signup requests to platform_server/accounts.py or a real
HTTP/socket API when the Python platform server is running.
"""


class ClientAuthService:
    def login(self, username: str, password: str) -> bool:
        # TODO(AUTH): Replace with request to platform_server.
        _ = (username, password)
        return False
