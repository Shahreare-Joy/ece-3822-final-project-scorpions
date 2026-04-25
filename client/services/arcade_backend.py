from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from client.data import MOCK_CHAT, MOCK_GAMES, MOCK_LEADERBOARD, MOCK_PLAYERS, MOCK_SESSIONS, MOCK_STATS
from client.integrations import CppServerClient
from client.models import AuthResult, ChatMessage, Game, GameSession, HomeRows, LeaderboardEntry, Player, PlatformStats

from .account_store import DemoAccountStore
from .auth_service import AuthService
from .catalog_service import CatalogService
from .chat_service import ChatService
from .game_launch_service import GameLaunchService
from .history_service import HistoryService
from .leaderboard_service import LeaderboardService
from .profile_service import ProfileService
from .search_service import SearchService
from .session_result_service import SessionResultService


class MockArcadeBackend:
    """Facade used by screens while final backend logic remains unfinished.

    TODO(PROJECT): Keep this public API stable, but replace service internals
    with your dataset loader, custom structures, performance hooks, and C++
    networking as those pieces are implemented by the team.
    """

    def __init__(self) -> None:
        self.connected = True
        self.server_client = CppServerClient()
        self.account_store = DemoAccountStore()
        self.players = {player.username: player for player in MOCK_PLAYERS}
        self.players.update(self.account_store.load_players())
        self.synthetic_players_loaded = False
        self.games = {game.game_id: game for game in MOCK_GAMES}
        self.sessions = list(MOCK_SESSIONS)
        self.leaderboard_entries = list(MOCK_LEADERBOARD)
        self.chat_messages = list(MOCK_CHAT)
        self.stats = MOCK_STATS
        self.chat_storage_dir = Path(__file__).resolve().parents[2] / "data" / "runtime_chat"

        self.auth_service = AuthService(self.players, self.account_store)
        self.catalog_service = CatalogService(self.games, self.stats)
        self.profile_service = ProfileService(self.players)
        self.leaderboard_service = LeaderboardService(self.leaderboard_entries, self.players)
        self.history_service = HistoryService(self.sessions)
        self.search_service = SearchService(self.players)
        self.game_launch_service = GameLaunchService()
        self.chat_service = ChatService(self.chat_messages, storage_dir=self.chat_storage_dir)
        self.session_result_service = SessionResultService()

    def authenticate(self, username: str, password: str) -> AuthResult:
        result = self.auth_service.authenticate(username, password)
        if result.success:
            self._refresh_player_services()
        return result

    def create_account(self, username: str, display_name: str, password: str, confirm_password: str, country: str) -> AuthResult:
        result = self.auth_service.create_account(username, display_name, password, confirm_password, country)
        if result.success:
            self._refresh_player_services()
        return result

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

    def search_games(self, query: str, limit: int = 24) -> list[Game]:
        return self.catalog_service.search_games(query, limit)

    def get_leaderboard(self, game_id: str, limit: int = 8) -> list[LeaderboardEntry]:
        return self.leaderboard_service.get_leaderboard(game_id, limit)

    def get_sessions(self, username: str | None = None, game_id: str | None = None, limit: int = 8) -> list[GameSession]:
        return self.history_service.get_sessions(username, game_id, limit)

    def search_players(self, query: str, limit: int = 25) -> list[Player]:
        self.ensure_full_player_dataset_loaded()
        return self.search_service.search_players(query, limit)

    def get_chat_preview(self, session_id: str = "global", limit: int = 3) -> list[ChatMessage]:
        return self.chat_service.get_chat_preview(session_id, limit)

    def add_chat_message(self, session_id: str, sender: str, text: str) -> ChatMessage:
        return self.chat_service.add_message(session_id, sender, text)

    def launch_game(self, player: Player | None, game: Game) -> str:
        if not game.playable:
            # Not-connected catalog rows should never crash or try to import/run a
            # missing game. When a teammate's game is ready, update its catalog
            # row to playable=True and verify the registry entry points at the
            # correct top-level games/game_N/code/game/main.py file.
            return f"{game.title} is not connected yet. Its arcade page is ready, and the team can connect the game folder when it is available."
        result = self.game_launch_service.launch(player, game, self.session_id_for_game(game))
        if result.ok:
            result_report = self.session_result_service.handle_launch_result(player, game, result.session_result_payload)
            if result_report.processed:
                return f"{result.message} Result pipeline: {result_report.message}"
            return f"{result.message} {result_report.message}"
        player_name = player.display_name if player else "Guest"
        return f"{player_name}, {result.message}"

    def _refresh_player_services(self) -> None:
        self.profile_service = ProfileService(self.players)
        self.search_service = SearchService(self.players)

    def ensure_full_player_dataset_loaded(self) -> None:
        """Load the large generated player dataset only when search needs it.

        The launcher should feel quick on Welcome/Login/Home. Loading 10,000+
        records and building the search BST/hash indexes is useful for Search,
        but it does not need to block the first window from appearing.
        """

        if self.synthetic_players_loaded:
            return
        self.players.update(self._load_synthetic_players())
        self.players.update(self.account_store.load_players())
        self.synthetic_players_loaded = True
        self._refresh_player_services()

    def session_id_for_game(self, game: Game | None) -> str:
        if game is None:
            return "global"
        return f"local-{game.game_id}"

    def _load_synthetic_players(self) -> dict[str, Player]:
        """Load the generated dataset so player search uses the full platform.

        Demo login still comes from data/demo_accounts.json. Dataset players are
        searchable/profile-visible records and intentionally have blank local
        passwords until the real account server is connected.
        """

        path = Path(__file__).resolve().parents[2] / "data" / "synthetic_dataset" / "players.json"
        if not path.exists():
            return {}
        try:
            records = json.loads(path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            return {}
        if not isinstance(records, list):
            return {}

        players: dict[str, Player] = {}
        for record in records:
            if not isinstance(record, dict):
                continue
            player = self._synthetic_record_to_player(record)
            if player is not None:
                players[player.username] = player
        return players

    @staticmethod
    def _synthetic_record_to_player(record: dict[str, Any]) -> Player | None:
        username = str(record.get("username", "")).strip().lower()
        if not username:
            return None
        created_at = str(record.get("created_at", "2026"))
        try:
            joined_year = int(created_at[:4])
        except ValueError:
            joined_year = 2026
        wins = int(record.get("wins", 0) or 0)
        games_played = int(record.get("games_played", 0) or 0)
        return Player(
            username=username,
            display_name=str(record.get("display_name") or username),
            password="",
            country=str(record.get("country", "Unknown")),
            joined_year=joined_year,
            level=int(record.get("level", 1) or 1),
            favorite_genre=str(record.get("favorite_genre", "Arcade")),
            total_sessions=games_played,
            total_wins=wins,
            status="Online" if str(record.get("account_status", "active")) == "active" else "Offline",
            bio=f"Dataset player profile from the Scorpions Arcade platform records. Skill rating: {record.get('skill_rating', 'n/a')}.",
            avatar_id=str(record.get("avatar", "")),
        )
