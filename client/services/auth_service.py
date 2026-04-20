from __future__ import annotations

from client.models import AuthResult, Player


class AuthService:
    """Temporary mock auth service.

    TODO(ACCOUNTS/C++): Replace internals with real server auth and token
    handling. Keep the method names stable so UI screens do not change.
    """

    def __init__(self, players: dict[str, Player]) -> None:
        self.players = players
        self.connected = True

    def authenticate(self, username: str, password: str) -> AuthResult:
        username = username.strip().lower()
        if not self.connected:
            return AuthResult(False, "Server unavailable. Please try again later.")
        if not username or not password:
            return AuthResult(False, "Please fill in all login fields.")
        player = self.players.get(username)
        if player is None or player.password != password:
            return AuthResult(False, "Invalid username or password.")
        return AuthResult(True, f"Welcome back, {player.display_name}.", player)

    def create_account(self, username: str, display_name: str, password: str, confirm_password: str, country: str) -> AuthResult:
        username = username.strip().lower()
        display_name = display_name.strip()
        country = country.strip() or "Unknown"
        if not username or not display_name or not password or not confirm_password:
            return AuthResult(False, "Please complete all required fields.")
        if len(username) < 3:
            return AuthResult(False, "Username must be at least 3 characters.")
        if len(password) < 6:
            return AuthResult(False, "Password must be at least 6 characters.")
        if password != confirm_password:
            return AuthResult(False, "Passwords do not match.")
        if username in self.players:
            return AuthResult(False, "Username already exists.")
        player = Player(username, display_name, password, country, 2026, 1, "Arcade", 0, 0, "Online", "New Scorpions Arcade player.")
        self.players[username] = player
        return AuthResult(True, "Account created. You can log in now.", player)

