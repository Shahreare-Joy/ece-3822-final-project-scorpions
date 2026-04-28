from __future__ import annotations

import json
from datetime import datetime
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
from .recommendation_service import RecommendationService
from .search_service import SearchService
from .session_result_service import SessionResultService


TEAM_GAME_ID_ALIASES = {
    "game_1": "scorpions-arena",
    "game_2": "sky-raiders",
    "game_3": "turbo-sprint",
    "game_4": "crystal-run",
    "game_5": "snake-test",
}

GENRE_COLORS = {
    "Action": (190, 82, 104),
    "Adventure": (78, 156, 208),
    "Racing": (66, 150, 178),
    "Strategy": (150, 136, 94),
    "Puzzle": (128, 134, 210),
    "Arcade": (210, 86, 98),
    "Co-op": (112, 178, 128),
    "Platformer": (198, 142, 88),
}


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
        self.games.update(self._load_synthetic_games())
        self.sessions = list(MOCK_SESSIONS)
        self.sessions.extend(self._load_synthetic_sessions())
        self.leaderboard_entries = list(MOCK_LEADERBOARD)
        self.chat_messages = list(MOCK_CHAT)
        self.stats = MOCK_STATS
        self.chat_storage_dir = Path(__file__).resolve().parents[2] / "data" / "runtime_chat"

        self.auth_service = AuthService(self.players, self.account_store)
        self.catalog_service = CatalogService(self.games, self.stats)
        self.profile_service = ProfileService(self.players)
        self.leaderboard_service = LeaderboardService(self.leaderboard_entries, self.players)
        self.history_service = HistoryService(self.sessions)
        self.recommendation_service = RecommendationService(self.games, self.sessions)
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
        return self.catalog_service.get_home_rows(player, self.recommendation_service)

    def has_player_history(self, player: Player | None) -> bool:
        return self.recommendation_service.has_history(player)

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
        session_id = self.session_id_for_game(game)
        try:
            result = self.game_launch_service.launch(player, game, session_id)
            if result.ok:
                result_report = self.session_result_service.handle_launch_result(player, game, result.session_result_payload)
                self._record_completed_session(player, game, result.session_id, result.session_result_payload)
                if result_report.processed:
                    return f"{result.message} Result pipeline: {result_report.message}"
                return f"{result.message} {result_report.message}"
            player_name = player.display_name if player else "Guest"
            return f"{player_name}, {result.message}"
        finally:
            # The local game subprocess has ended, so release the session chat
            # buffer/file used by the arcade bridge. A future C++ relay should
            # perform the matching network unsubscribe here.
            self.chat_service.close_session(session_id)

    def _record_completed_session(self, player: Player | None, game: Game, session_id: str, payload: dict[str, Any] | None) -> None:
        """Record a local finished game so recent/recommended rows refresh."""

        payload = payload or {}
        username = player.username if player else "guest"
        score = int(payload.get("score", 0) or 0)
        duration_seconds = int(payload.get("duration_seconds", payload.get("duration", 0)) or 0)
        outcome = str(payload.get("outcome") or payload.get("result") or "Played")
        session = GameSession(
            session_id=session_id or f"local-{game.game_id}-{datetime.now().timestamp():.0f}",
            game_id=game.game_id,
            username=username,
            result=outcome,
            score=score,
            duration_minutes=max(1, duration_seconds // 60) if duration_seconds else 1,
            played_at=datetime.now().isoformat(timespec="seconds"),
            status="Complete",
        )
        self.history_service.add_session(session)
        self.recommendation_service.add_session(session)

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

    def _load_synthetic_games(self) -> dict[str, Game]:
        """Load catalog-only synthetic games for browse/recommendation rows.

        Team-game ids from the dataset are mapped to the launcher-friendly ids
        already present in `MOCK_GAMES`, so playable launch paths stay stable.
        The remaining `catalog_game_*` records become normal catalog entries.
        """

        path = Path(__file__).resolve().parents[2] / "data" / "synthetic_dataset" / "game_catalog.json"
        if not path.exists():
            return {}
        try:
            records = json.loads(path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            return {}
        if not isinstance(records, list):
            return {}

        games: dict[str, Game] = {}
        for record in records:
            if not isinstance(record, dict):
                continue
            raw_game_id = str(record.get("game_id", "")).strip()
            game_id = TEAM_GAME_ID_ALIASES.get(raw_game_id, raw_game_id)
            if not game_id or game_id in self.games:
                continue
            genre = str(record.get("genre", "Arcade"))
            tags = record.get("tags", [])
            created_at = str(record.get("created_at", "2026"))
            try:
                release_year = int(created_at[:4])
            except ValueError:
                release_year = 2026
            games[game_id] = Game(
                game_id=game_id,
                title=str(record.get("title") or game_id),
                genre=genre,
                description=str(record.get("description") or "Synthetic catalog recommendation entry."),
                creator=str(record.get("creator") or "Synthetic Catalog"),
                players_now=int(record.get("players_now", record.get("currently_playing", 0)) or 0),
                total_plays=int(record.get("total_plays", 0) or 0),
                status=str(record.get("status") or "Catalog"),
                playable=False,
                color=GENRE_COLORS.get(genre, (96, 128, 180)),
                tags=[str(tag) for tag in tags] if isinstance(tags, list) else [genre.lower()],
                release_year=release_year,
                last_updated=str(record.get("last_updated") or "Updated recently"),
                activity_note=f"Synthetic {genre.lower()} catalog entry used for realistic recommendations.",
                team_game=False,
                thumbnail_path=str(record.get("thumbnail_path") or ""),
                screenshot_path="",
            )
        return games

    def _load_synthetic_sessions(self) -> list[GameSession]:
        """Load 100,000-session history into UI session rows.

        This builds startup indexes from realistic synthetic history. The UI
        never scans this list per frame; `HistoryService` and
        `RecommendationService` build hash-table indexes once.
        """

        path = Path(__file__).resolve().parents[2] / "data" / "synthetic_dataset" / "sessions.json"
        if not path.exists():
            return []
        try:
            records = json.loads(path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            return []
        if not isinstance(records, list):
            return []

        sessions: list[GameSession] = []
        for record in records:
            if not isinstance(record, dict):
                continue
            game_id = TEAM_GAME_ID_ALIASES.get(str(record.get("game_id", "")).strip(), str(record.get("game_id", "")).strip())
            if game_id not in self.games:
                continue
            duration_seconds = int(record.get("duration_seconds", 0) or 0)
            sessions.append(
                GameSession(
                    session_id=str(record.get("session_id") or ""),
                    game_id=game_id,
                    username=str(record.get("username") or record.get("player_id") or "").strip().lower(),
                    result=str(record.get("outcome") or "Played"),
                    score=int(record.get("score", 0) or 0),
                    duration_minutes=max(1, duration_seconds // 60),
                    played_at=str(record.get("ended_at") or record.get("started_at") or ""),
                    status="Complete",
                )
            )
        return sessions

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
