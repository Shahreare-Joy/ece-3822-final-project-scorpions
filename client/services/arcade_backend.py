from __future__ import annotations

import json
import os
import threading
import time
from datetime import datetime
from pathlib import Path
from typing import Any

from client.data import MOCK_CHAT, MOCK_GAMES, MOCK_LEADERBOARD, MOCK_PLAYERS, MOCK_SESSIONS, MOCK_STATS
from client.integrations import BackendApiHook, CppServerClient, ServerAvailability, ServerConnection
from client.models import AuthResult, ChatMessage, Game, GameSession, HomeRows, LeaderboardEntry, Player, PlatformStats
from client.runtime_config import RuntimeConfig

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

NEW_TEAM_GAME_IDS = {"scorpions-arena", "sky-raiders", "turbo-sprint", "crystal-run"}

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

    def __init__(self, config: RuntimeConfig | None = None) -> None:
        self.runtime_config = config or RuntimeConfig.local()
        self.local_fallback_active = False
        if self.runtime_config.is_server_mode:
            os.environ["SCORPIONS_PLATFORM_HOST"] = self.runtime_config.server_host
            os.environ["SCORPIONS_PLATFORM_PORT"] = str(self.runtime_config.platform_port)
            os.environ["SCORPIONS_PLATFORM_SERIALIZER"] = self.runtime_config.serializer
            os.environ["SCORPIONS_PLATFORM_CHAT"] = "1"
        platform_connection = self.runtime_config.platform_connection() if self.runtime_config.is_server_mode else None
        gameplay_connection = self.runtime_config.gameplay_connection() if self.runtime_config.is_server_mode else None
        self.server_connection = (
            ServerConnection(
                self.runtime_config.server_host,
                self.runtime_config.platform_port,
                serializer=self.runtime_config.serializer,
                name="Python Platform Server",
            )
            if self.runtime_config.is_server_mode
            else None
        )
        self.platform_api = BackendApiHook(connection=platform_connection)
        self.platform_status = self._initial_platform_status()
        self.connected = self.platform_status.reachable
        self.server_client = CppServerClient(gameplay_connection)
        self.gameplay_status = ServerAvailability(
            name="C++ Gameplay Server",
            role="gameplay",
            host=self.server_client.connection.host,
            port=self.server_client.connection.port,
            reachable=False,
            message="C++ gameplay server has not been checked yet.",
            protocol=self.server_client.connection.protocol,
        )
        self.account_store = DemoAccountStore()
        self.players = {player.username: player for player in MOCK_PLAYERS}
        self.players.update(self.account_store.load_players())
        self.synthetic_players_loaded = False
        self.synthetic_catalog_loaded = False
        self.synthetic_sessions_loaded = False
        self.games = {game.game_id: game for game in MOCK_GAMES}
        self.home_sessions = list(MOCK_SESSIONS)
        self.sessions = list(self.home_sessions)
        self.leaderboard_entries = [entry for entry in MOCK_LEADERBOARD if entry.game_id not in NEW_TEAM_GAME_IDS]
        self.chat_messages = list(MOCK_CHAT)
        self.stats = MOCK_STATS
        self.chat_storage_dir = Path(__file__).resolve().parents[2] / "data" / "runtime_chat"

        self.auth_service = AuthService(self.players, self.account_store)
        self.catalog_service = CatalogService(self.games, self.stats)
        self.profile_service = ProfileService(self.players)
        self.leaderboard_service = LeaderboardService(self.leaderboard_entries, self.players)
        self.history_service = HistoryService(self.sessions)
        self.recommendation_service = RecommendationService(self.games, self.sessions)
        self.home_recommendation_service = RecommendationService(self.games, self.home_sessions)
        self.search_service = SearchService(self.players)
        self.game_launch_service = GameLaunchService(gameplay_connection)
        self.chat_service = ChatService(self.chat_messages, storage_dir=self.chat_storage_dir)
        self.session_result_service = SessionResultService()
        self._preload_lock = threading.RLock()
        self._preload_thread: threading.Thread | None = None
        self._preload_username = ""
        self._preload_loading = False
        self._preload_cache: dict[str, Any] = {}
        self._preload_error = ""
        self._preload_generation = 0
        self._chat_preview_cache: dict[tuple[str, int], tuple[float, list[ChatMessage]]] = {}
        self.chat_preview_interval_seconds = 15.0

    @property
    def run_mode_label(self) -> str:
        if self.runtime_config.is_server_mode and self.local_fallback_active:
            return "Local Mode Fallback"
        return "Server Mode" if self.runtime_config.is_server_mode else "Local Mode"

    def _initial_platform_status(self) -> ServerAvailability:
        if not self.runtime_config.is_server_mode or self.server_connection is None:
            return self.platform_api.availability_status()
        status = self.server_connection.availability()
        if not status.reachable and self.runtime_config.allow_local_fallback:
            self.local_fallback_active = True
            return ServerAvailability(
                name="Python Platform Server",
                role="platform",
                host=status.host,
                port=status.port,
                reachable=True,
                message="Remote platform server is unavailable; using local dataset/accounts fallback.",
                protocol=status.protocol,
            )
        return status

    def get_platform_availability(self) -> ServerAvailability:
        """Return the current Python platform-server/facade status."""

        if self.runtime_config.is_server_mode and self.server_connection is not None and not self.local_fallback_active:
            self.platform_status = self.server_connection.availability()
            if not self.platform_status.reachable and self.runtime_config.allow_local_fallback:
                self.local_fallback_active = True
                self.platform_status = ServerAvailability(
                    name="Python Platform Server",
                    role="platform",
                    host=self.server_connection.host,
                    port=self.server_connection.port,
                    reachable=True,
                    message="Remote platform server is unavailable; using local dataset/accounts fallback.",
                    protocol="tcp",
                )
        else:
            self.platform_status = self.platform_api.availability_status() if not self.local_fallback_active else self.platform_status
        self.connected = self.platform_status.reachable
        return self.platform_status

    def get_gameplay_availability(self, refresh: bool = True) -> ServerAvailability:
        """Return C++ gameplay-server status, probing TCP only when requested."""

        if refresh:
            self.gameplay_status = self.server_client.check_availability()
        return self.gameplay_status

    def close(self) -> None:
        """Release any open networking resources before the app exits."""

        if self.server_connection is not None:
            self.server_connection.close()
        self.server_client.disconnect()

    def authenticate(self, username: str, password: str) -> AuthResult:
        if self.runtime_config.is_server_mode and self.server_connection is not None and not self.local_fallback_active:
            request: Any = (
                {"type": "login", "username": username, "password": password}
                if self.runtime_config.serializer == "json"
                else f"LOGIN {username} {password}"
            )
            remote = self.server_connection.send_request(request)
            if remote.ok:
                if isinstance(remote.response, dict):
                    if not remote.response.get("ok"):
                        return AuthResult(False, str(remote.response.get("message") or "Remote login failed."))
                    player = self._player_from_server_payload(remote.response.get("player"), username)
                    self.players[player.username] = player
                    self._refresh_player_services()
                    return AuthResult(True, str(remote.response.get("message") or f"Welcome back, {player.display_name}."), player)
                if isinstance(remote.response, str) and remote.response.upper().startswith("OK"):
                    result = self.auth_service.authenticate(username, password)
                    if result.success:
                        self._refresh_player_services()
                    return result
            if not self.runtime_config.allow_local_fallback:
                return AuthResult(False, remote.message)
            self.local_fallback_active = True
            self.platform_status = ServerAvailability(
                name=self.platform_status.name,
                role=self.platform_status.role,
                host=self.platform_status.host,
                port=self.platform_status.port,
                reachable=True,
                message=f"Remote login unavailable ({remote.message}); using local account file fallback.",
                protocol=self.platform_status.protocol,
                direct_call=self.platform_status.direct_call,
            )
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
        self.ensure_synthetic_catalog_loaded()
        return self.catalog_service.get_games()

    def get_game(self, game_id: str) -> Game | None:
        self.ensure_synthetic_catalog_loaded()
        return self.catalog_service.get_game(game_id)

    def get_player(self, username: str) -> Player | None:
        return self.profile_service.get_player(username)

    def get_home_rows(self, player: Player | None, load_personalization: bool = True) -> HomeRows:
        if load_personalization:
            cached_rows = self.get_cached_home_rows(player)
            if cached_rows is not None:
                return cached_rows
        if load_personalization and self.is_preload_loading(player):
            load_personalization = False
        if load_personalization:
            self.ensure_personalization_dataset_loaded()
        else:
            self.ensure_synthetic_catalog_loaded()
        return self.catalog_service.get_home_rows(player, self.recommendation_service)

    def get_home_sections(self, player: Player | None) -> list[tuple[str, list[Game]]]:
        """Build every Home shelf from one stable source.

        Home should look the same after login, after visiting another screen,
        and after returning from details. It uses the current catalog plus the
        current in-memory history/recommendation indexes, and it does not swap
        to a background preload cache when that worker finishes.
        """

        self.ensure_synthetic_catalog_loaded()
        rows = self.catalog_service.get_home_rows(player, self.home_recommendation_service)
        has_history = self.home_recommendation_service.has_history(player)
        sections: list[tuple[str, list[Game]]] = []

        if rows.continue_playing:
            sections.append(("Start Playing", rows.continue_playing))
        if has_history and rows.recently_played:
            sections.append(("Recently Played", rows.recently_played))
        sections.extend(
            [
                ("Popular Right Now", rows.popular_now),
                ("Recommended For You", rows.recommended),
                ("New / Featured", rows.featured),
            ]
        )
        if rows.coming_soon:
            sections.append(("Coming Soon", rows.coming_soon))
        return self._dedupe_home_sections(sections)

    def has_player_history(self, player: Player | None, load_personalization: bool = True) -> bool:
        if load_personalization:
            cached_has_history = self.get_cached_has_history(player)
            if cached_has_history is not None:
                return cached_has_history
        if load_personalization and self.is_preload_loading(player):
            load_personalization = False
        if load_personalization:
            self.ensure_personalization_dataset_loaded()
        return self.recommendation_service.has_history(player)

    def filter_games(self, genre: str) -> list[Game]:
        self.ensure_synthetic_catalog_loaded()
        return self.catalog_service.filter_games(genre)

    def search_games(self, query: str, limit: int = 24) -> list[Game]:
        self.ensure_synthetic_catalog_loaded()
        return self.catalog_service.search_games(query, limit)

    def get_leaderboard(self, game_id: str, limit: int = 8) -> list[LeaderboardEntry]:
        if self.runtime_config.is_server_mode and not self.local_fallback_active:
            response = self._platform_request({"type": "leaderboard", "game_id": game_id, "limit": limit})
            if response is not None and response.get("ok") and isinstance(response.get("leaders"), list):
                leaders = [
                    self._leaderboard_entry_from_server_payload(row, index + 1)
                    for index, row in enumerate(response["leaders"])
                    if isinstance(row, dict)
                ]
                return leaders
        return self.leaderboard_service.get_leaderboard(game_id, limit)

    def get_sessions(self, username: str | None = None, game_id: str | None = None, limit: int = 8) -> list[GameSession]:
        if self.runtime_config.is_server_mode and not self.local_fallback_active:
            response = self._platform_request(
                {
                    "type": "history",
                    "username": username or "",
                    "game_id": game_id or "",
                    "limit": limit,
                }
            )
            if response is not None and response.get("ok") and isinstance(response.get("sessions"), list):
                sessions = [
                    self._session_from_server_payload(row)
                    for row in response["sessions"]
                    if isinstance(row, dict)
                ]
                if sessions:
                    return sessions
        if username and game_id is None:
            cached_sessions = self.get_cached_player_sessions(username, limit)
            if cached_sessions is not None:
                return cached_sessions
        elif username is None and game_id is None:
            cached_history = self.get_cached_history_sessions(limit)
            if cached_history is not None:
                return cached_history
        self.ensure_personalization_dataset_loaded()
        return self.history_service.get_sessions(username, game_id, limit)

    def search_players(self, query: str, limit: int = 25) -> list[Player]:
        self.ensure_full_player_dataset_loaded()
        return self.search_service.search_players(query, limit)

    def get_chat_preview(self, session_id: str = "global", limit: int = 3) -> list[ChatMessage]:
        safe_session_id = (session_id or "").strip()
        if not safe_session_id:
            return []
        key = (safe_session_id, int(limit))
        now = time.monotonic()
        cached = self._chat_preview_cache.get(key)
        if cached is not None and now - cached[0] < self.chat_preview_interval_seconds:
            return list(cached[1])
        messages = self.chat_service.get_chat_preview(safe_session_id, limit)
        self._chat_preview_cache[key] = (now, list(messages))
        return messages

    def add_chat_message(self, session_id: str, sender: str, text: str) -> ChatMessage:
        message = self.chat_service.add_message(session_id, sender, text)
        self._invalidate_chat_preview_cache(message.session_id)
        return message

    def launch_game(self, player: Player | None, game: Game) -> str:
        if not game.playable:
            # Not-connected catalog rows should never crash or try to import/run a
            # missing game. When a teammate's game is ready, update its catalog
            # row to playable=True and verify the registry entry points at the
            # correct top-level games/game_N/code/game/main.py file.
            return f"{game.title} is not connected yet. Its arcade page is ready, and the team can connect the game folder when it is available."
        session_id = self.session_id_for_game(game)
        self._notify_platform_session_start(player, game, session_id)
        try:
            result = self.game_launch_service.launch(player, game, session_id)
            if result.ok:
                remote_result_message = self._submit_result_to_platform(result.session_result_payload)
                result_report = self.session_result_service.handle_launch_result(player, game, result.session_result_payload)
                self._record_completed_session(player, game, result.session_id, result.session_result_payload)
                if result_report.processed:
                    suffix = f" Result pipeline: {result_report.message}"
                    if remote_result_message:
                        suffix += f" Platform sync: {remote_result_message}"
                    return f"{result.message}{suffix}"
                if remote_result_message:
                    return f"{result.message} {result_report.message} Platform sync: {remote_result_message}"
                return f"{result.message} {result_report.message}"
            player_name = player.display_name if player else "Guest"
            return f"{player_name}, {result.message}"
        finally:
            self._notify_platform_session_end(session_id)
            # The local game subprocess has ended, so release the session chat
            # buffer/file used by the arcade bridge. A future C++ relay should
            # perform the matching network unsubscribe here.
            self.chat_service.close_session(session_id)
            self._invalidate_chat_preview_cache(session_id)

    def _invalidate_chat_preview_cache(self, session_id: str | None = None) -> None:
        if not session_id:
            self._chat_preview_cache.clear()
            return
        safe_session_id = session_id.strip()
        for key in list(self._chat_preview_cache):
            if key[0] == safe_session_id:
                self._chat_preview_cache.pop(key, None)

    def _platform_request(self, request: dict[str, Any]) -> dict[str, Any] | None:
        if not self.runtime_config.is_server_mode or self.server_connection is None or self.local_fallback_active:
            return None
        result = self.server_connection.send_request(request)
        if not result.ok:
            print(f"[PLATFORM] Request {request.get('type')} failed: {result.message}")
            return None
        if isinstance(result.response, dict):
            print(f"[PLATFORM] Request {request.get('type')} -> {result.response.get('message', 'ok')}")
            return result.response
        print(f"[PLATFORM] Request {request.get('type')} -> {result.response}")
        return None

    def _notify_platform_session_start(self, player: Player | None, game: Game, session_id: str) -> None:
        response = self._platform_request(
            {
                "type": "session_start",
                "session_id": session_id,
                "player_id": player.username if player else "guest",
                "game_id": game.game_id,
            }
        )
        if response is not None and response.get("ok"):
            print(f"[PLATFORM] Session started: {session_id}")

    def _notify_platform_session_end(self, session_id: str) -> None:
        response = self._platform_request({"type": "session_end", "session_id": session_id})
        if response is not None:
            print(f"[PLATFORM] Session end cleanup for {session_id}: {response.get('message', response.get('ok'))}")

    def _submit_result_to_platform(self, payload: dict[str, Any] | None) -> str:
        if payload is None:
            return ""
        response = self._platform_request({"type": "submit_result", "payload": payload})
        if response is None:
            return "not available"
        if response.get("ok"):
            print(f"[PLATFORM] Score submitted: player={payload.get('player_id')} game={payload.get('game_id')} score={payload.get('score')}")
            return str(response.get("message") or "score accepted")
        print(f"[PLATFORM] Score rejected: {response.get('message')} {response.get('errors', [])}")
        return str(response.get("message") or "score rejected")

    def _dedupe_home_sections(self, sections: list[tuple[str, list[Game]]]) -> list[tuple[str, list[Game]]]:
        """Drop empty shelves and avoid repeating the exact same game set."""

        deduped: list[tuple[str, list[Game]]] = []
        seen_sets: set[tuple[str, ...]] = set()
        for title, games in sections:
            unique_games: list[Game] = []
            seen_game_ids: set[str] = set()
            for game in games:
                if game.game_id in seen_game_ids:
                    continue
                unique_games.append(game)
                seen_game_ids.add(game.game_id)
            if not unique_games:
                continue
            game_set = tuple(game.game_id for game in unique_games)
            if game_set in seen_sets:
                continue
            seen_sets.add(game_set)
            deduped.append((title, unique_games))
        return deduped

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
        self.home_sessions.append(session)
        self.home_recommendation_service.add_session(session)
        if player is not None:
            player.total_sessions += 1
            if outcome.lower() == "win":
                player.total_wins += 1
            self.leaderboard_service.add_entry(
                LeaderboardEntry(
                    game_id=game.game_id,
                    username=player.username,
                    display_name=player.display_name,
                    score=score,
                    wins=player.total_wins,
                    rank=0,
                )
            )
            self.profile_service = ProfileService(self.players)
        self.invalidate_player_cache(username)
        if player is not None:
            self.start_post_login_preload(player)

    def start_post_login_preload(self, player: Player | None) -> None:
        """Warm common post-login data on a daemon thread.

        Login should navigate to Home immediately. This worker loads the larger
        catalog/session indexes after that first transition and stores the
        results in a small cache for Profile, History, Home, and quick previews.
        """

        if player is None:
            return
        username = player.username.strip().lower()
        with self._preload_lock:
            if self._preload_loading and self._preload_username == username:
                return
            self._preload_generation += 1
            generation = self._preload_generation
            self._preload_username = username
            self._preload_loading = True
            self._preload_error = ""
            self._preload_cache = {}
            self._preload_thread = threading.Thread(
                target=self._run_post_login_preload,
                args=(player, generation),
                name=f"ScorpionsPreload-{username}",
                daemon=True,
            )
            self._preload_thread.start()

    def _run_post_login_preload(self, player: Player, generation: int) -> None:
        username = player.username.strip().lower()
        try:
            self.ensure_synthetic_catalog_loaded()
            profile_summary = self.profile_service.aggregate_profile_stats(username)

            # This is the one heavier step. It builds the session/history and
            # recommendation indexes once in the background instead of doing it
            # during the first Profile or History draw call.
            self.ensure_personalization_dataset_loaded()

            player_sessions = self.history_service.get_sessions(username=username, limit=12)
            history_sessions = self.history_service.get_sessions(limit=80)
            home_rows = self.catalog_service.get_home_rows(player, self.recommendation_service)
            has_history = self.recommendation_service.has_history(player)
            recently_played = self.recommendation_service.recently_played(player, limit=5)
            recommended = self.recommendation_service.recommended(player, limit=5)
            catalog_rows = self.catalog_service.get_games()
            leaderboard_preview = {
                game.game_id: self.leaderboard_service.get_leaderboard(game.game_id, limit=5)
                for game in catalog_rows
                if game.playable
            }

            with self._preload_lock:
                if self._preload_username != username or self._preload_generation != generation:
                    return
                self._preload_cache = {
                    "profile_summary": profile_summary,
                    "player_sessions": player_sessions,
                    "history_sessions": history_sessions,
                    "home_rows": home_rows,
                    "has_history": has_history,
                    "recently_played": recently_played,
                    "recommended": recommended,
                    "leaderboard_preview": leaderboard_preview,
                    "catalog_rows": catalog_rows,
                }
                self._preload_loading = False
        except Exception as exc:  # pragma: no cover - defensive UI fallback
            with self._preload_lock:
                if self._preload_generation != generation:
                    return
                self._preload_error = str(exc)
                self._preload_loading = False

    def invalidate_player_cache(self, username: str | None = None) -> None:
        """Drop cached rows after a game changes history/stats/rank signals."""

        with self._preload_lock:
            if username is None or username.strip().lower() == self._preload_username:
                self._preload_generation += 1
                self._preload_loading = False
                self._preload_cache = {}
                self._preload_error = ""

    def is_preload_loading(self, player: Player | None = None) -> bool:
        with self._preload_lock:
            if player is not None and self._preload_username and self._preload_username != player.username.strip().lower():
                return False
            return self._preload_loading

    def preload_error(self) -> str:
        with self._preload_lock:
            return self._preload_error

    def get_cached_home_rows(self, player: Player | None) -> HomeRows | None:
        if player is None:
            return None
        with self._preload_lock:
            if self._preload_username != player.username.strip().lower():
                return None
            rows = self._preload_cache.get("home_rows")
            return rows if isinstance(rows, HomeRows) else None

    def get_cached_has_history(self, player: Player | None) -> bool | None:
        if player is None:
            return None
        with self._preload_lock:
            if self._preload_username != player.username.strip().lower() or "has_history" not in self._preload_cache:
                return None
            return bool(self._preload_cache["has_history"])

    def get_cached_profile_summary(self, player: Player | None) -> dict[str, object] | None:
        if player is None:
            return None
        with self._preload_lock:
            if self._preload_username != player.username.strip().lower():
                return None
            summary = self._preload_cache.get("profile_summary")
            return dict(summary) if isinstance(summary, dict) else None

    def get_cached_player_sessions(self, username: str, limit: int = 8) -> list[GameSession] | None:
        with self._preload_lock:
            if self._preload_username != username.strip().lower():
                return None
            sessions = self._preload_cache.get("player_sessions")
            if not isinstance(sessions, list):
                return None
            return [session for session in sessions[:limit] if isinstance(session, GameSession)]

    def get_cached_history_sessions(self, limit: int = 80) -> list[GameSession] | None:
        with self._preload_lock:
            sessions = self._preload_cache.get("history_sessions")
            if not isinstance(sessions, list):
                return None
            return [session for session in sessions[:limit] if isinstance(session, GameSession)]

    def get_cached_leaderboard_preview(self, game_id: str, limit: int = 5) -> list[LeaderboardEntry] | None:
        with self._preload_lock:
            previews = self._preload_cache.get("leaderboard_preview")
            if not isinstance(previews, dict):
                return None
            rows = previews.get(game_id)
            if not isinstance(rows, list):
                return None
            return [entry for entry in rows[:limit] if isinstance(entry, LeaderboardEntry)]

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

    def ensure_synthetic_catalog_loaded(self) -> None:
        """Load the large generated catalog only when Browse/Home need it.

        Login only needs accounts, so loading 100+ catalog rows during backend
        construction just delays the first screen. This rebuilds the catalog
        indexes once, then all future calls reuse them.
        """

        if self.synthetic_catalog_loaded:
            return
        self.games.update(self._load_synthetic_games())
        self.synthetic_catalog_loaded = True
        self.catalog_service = CatalogService(self.games, self.stats)
        self.recommendation_service = RecommendationService(self.games, self.sessions)
        self.home_recommendation_service = RecommendationService(self.games, self.home_sessions)

    def ensure_personalization_dataset_loaded(self) -> None:
        """Load full session history only when personalized rows/history need it.

        The 100,000-session file is useful for Recently Played, Recommended For
        You, and match history, but it should not block the login screen. The
        history and recommendation services build custom hash-table, linked-list,
        and graph indexes once after this lazy load.
        """

        if self.synthetic_sessions_loaded:
            return
        self.ensure_synthetic_catalog_loaded()
        self.sessions.extend(self._load_synthetic_sessions())
        self.synthetic_sessions_loaded = True
        self.history_service = HistoryService(self.sessions)
        self.recommendation_service = RecommendationService(self.games, self.sessions)

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

        This is lazy-loaded after login instead of during the first backend
        construction. The UI never scans this list per frame; `HistoryService`
        and `RecommendationService` build hash-table indexes once.
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

    @staticmethod
    def _player_from_server_payload(payload: Any, fallback_username: str) -> Player:
        record = payload if isinstance(payload, dict) else {}
        username = str(record.get("username") or fallback_username).strip().lower()
        display_name = str(record.get("display_name") or username.title())
        return Player(
            username=username,
            display_name=display_name,
            password="",
            country=str(record.get("country") or record.get("region") or "Unknown"),
            joined_year=int(str(record.get("joined_year") or record.get("created_at") or "2026")[:4] or 2026),
            level=int(record.get("level", 1) or 1),
            favorite_genre=str(record.get("favorite_genre") or "Arcade"),
            total_sessions=int(record.get("total_sessions") or record.get("games_played") or 0),
            total_wins=int(record.get("total_wins") or record.get("wins") or 0),
            status=str(record.get("status") or "Online"),
            bio=str(record.get("bio") or "Remote platform account."),
            avatar_id=str(record.get("avatar_id") or record.get("avatar") or ""),
        )

    @staticmethod
    def _leaderboard_entry_from_server_payload(payload: dict[str, Any], rank: int) -> LeaderboardEntry:
        username = str(payload.get("username") or payload.get("player_id") or "guest")
        return LeaderboardEntry(
            game_id=str(payload.get("game_id") or ""),
            username=username,
            display_name=str(payload.get("display_name") or username),
            score=int(payload.get("score", 0) or 0),
            wins=int(payload.get("wins", 0) or 0),
            rank=rank,
        )

    @staticmethod
    def _session_from_server_payload(payload: dict[str, Any]) -> GameSession:
        duration_seconds = int(payload.get("duration_seconds", payload.get("duration", 0)) or 0)
        return GameSession(
            session_id=str(payload.get("session_id") or ""),
            game_id=str(payload.get("game_id") or ""),
            username=str(payload.get("username") or payload.get("player_id") or "guest"),
            result=str(payload.get("outcome") or payload.get("result") or "Played"),
            score=int(payload.get("score", 0) or 0),
            duration_minutes=max(1, duration_seconds // 60) if duration_seconds else int(payload.get("duration_minutes", 1) or 1),
            played_at=str(payload.get("played_at") or payload.get("started_at") or payload.get("timestamp") or ""),
            status=str(payload.get("status") or "Complete"),
        )
