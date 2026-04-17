from __future__ import annotations

from scorpions_arcade.data import MOCK_CHAT, MOCK_GAMES, MOCK_LEADERBOARD, MOCK_PLAYERS, MOCK_SESSIONS, MOCK_STATS
from scorpions_arcade.integrations import CppServerClient
from scorpions_arcade.models import AuthResult, ChatMessage, Game, GameSession, HomeRows, LeaderboardEntry, Player, PlatformStats

from .auth_service import AuthService
from .catalog_service import CatalogService
from .chat_service import ChatService
from .game_launch_service import GameLaunchService
from .history_service import HistoryService
from .leaderboard_service import LeaderboardService
from .profile_service import ProfileService
from .search_service import SearchService


class MockArcadeBackend:
    """Facade used by screens while final backend logic remains unfinished.

    TODO(PROJECT): Keep this public API stable, but replace service internals
    with your dataset loader, custom structures, performance hooks, and C++
    networking as those pieces are implemented by the team.
    """

    def __init__(self) -> None:
        self.connected = True
        self.server_client = CppServerClient()
        self.players = {player.username: player for player in MOCK_PLAYERS}
        self.games = {game.game_id: game for game in MOCK_GAMES}
        self.sessions = list(MOCK_SESSIONS)
        self.leaderboard_entries = list(MOCK_LEADERBOARD)
        self.chat_messages = list(MOCK_CHAT)
        self.stats = MOCK_STATS

        self.auth_service = AuthService(self.players)
        self.catalog_service = CatalogService(self.games, self.stats)
        self.profile_service = ProfileService(self.players)
        self.leaderboard_service = LeaderboardService(self.leaderboard_entries, self.players)
        self.history_service = HistoryService(self.sessions)
        self.search_service = SearchService(self.players)
        self.game_launch_service = GameLaunchService()
        self.chat_service = ChatService(self.chat_messages)

    def authenticate(self, username: str, password: str) -> AuthResult:
        return self.auth_service.authenticate(username, password)

    def create_account(self, username: str, display_name: str, password: str, confirm_password: str, country: str) -> AuthResult:
        return self.auth_service.create_account(username, display_name, password, confirm_password, country)

    def get_platform_stats(self) -> PlatformStats:
        return self.catalog_service.get_platform_stats()

    def get_games(self) -> list[Game]:
        return self.catalog_service.get_games()

    def get_game(self, game_id: str) -> Game | None:
        return self.catalog_service.get_game(game_id)

    def get_player(self, username: str) -> Player | None:
        return self.profile_service.get_player(username)

    def get_home_rows(self, player: Player | None) -> HomeRows:
        return self.catalog_service.get_home_rows(player)

    def filter_games(self, genre: str) -> list[Game]:
        return self.catalog_service.filter_games(genre)

    def get_leaderboard(self, game_id: str, limit: int = 8) -> list[LeaderboardEntry]:
        return self.leaderboard_service.get_leaderboard(game_id, limit)

    def get_sessions(self, username: str | None = None, game_id: str | None = None, limit: int = 8) -> list[GameSession]:
        return self.history_service.get_sessions(username, game_id, limit)

    def search_players(self, query: str, limit: int = 8) -> list[Player]:
        return self.search_service.search_players(query, limit)

    def get_chat_preview(self, session_id: str = "global", limit: int = 3) -> list[ChatMessage]:
        return self.chat_service.get_chat_preview(session_id, limit)

    def add_chat_message(self, session_id: str, sender: str, text: str) -> ChatMessage:
        return self.chat_service.add_message(session_id, sender, text)

    def launch_game(self, player: Player | None, game: Game) -> str:
        result = self.game_launch_service.launch(player, game)
        if result.ok:
            return result.message
        player_name = player.display_name if player else "Guest"
        return f"{player_name}, {result.message}"
