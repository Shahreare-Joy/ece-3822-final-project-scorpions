from __future__ import annotations

"""Indexed home-page personalization for recent and recommended games.

Recently Played:
    The service indexes session history once at startup using a custom chained
    hash table from username/player_id to a linked-list SessionHistory. Querying
    a player then walks only that player's linked list, collects unique game
    ids in newest-first order, and falls back to popular games when no history
    exists.

Recommended For You:
    Recommendations are deterministic, not random. The service counts the
    player's played genres/tags, follows a game co-play graph built from other
    players' histories, and adds small boosts for popularity/recent activity.
    Playable games receive a boost, but catalog-only games can still rank when
    they match the player's habits.
"""

from datetime import datetime
import re

from client.models import Game, GameSession, Player
from datastructures.graph import Graph
from datastructures.hash_table import ChainedHashTable
from datastructures.session_history import SessionHistory, SessionNode


class RecommendationService:
    """Build and query player history/recommendation indexes."""

    def __init__(self, games: dict[str, Game], sessions: list[GameSession]) -> None:
        self.games = games
        self._player_history = ChainedHashTable()
        self._player_game_counts = ChainedHashTable()
        self._player_recent_game_ids = ChainedHashTable()
        self._game_popularity = ChainedHashTable()
        self._game_recent_activity = ChainedHashTable()
        self._co_play_graph = Graph()
        self._popular_cache = self._sort_popular_games(list(games.values()))
        for session in sessions:
            self.add_session(session, refresh_popular=False)
        self._popular_cache = self._sort_popular_games(list(self.games.values()))

    def add_session(self, session: GameSession, refresh_popular: bool = True) -> None:
        """Add one completed/known session to the indexes.

        This runs both during startup and after a launched game returns, so
        Recently Played can update without rebuilding the full dataset index.
        """

        if session.game_id not in self.games or not session.username:
            return
        username = session.username.strip().lower()
        history = self._history_for(username)
        history.prepend(session.game_id, session.played_at, session.score, session.result)

        counts = self._counts_for(username)
        counts.put(session.game_id, int(counts.get(session.game_id, 0) or 0) + 1)

        self._game_popularity.put(session.game_id, int(self._game_popularity.get(session.game_id, 0) or 0) + 1)
        if self._is_recent(session.played_at):
            self._game_recent_activity.put(session.game_id, int(self._game_recent_activity.get(session.game_id, 0) or 0) + 1)

        recent_games = self._recent_games_for(username)
        seen: set[str] = set()
        for prior_game_id in recent_games[:11]:
            if prior_game_id == session.game_id or prior_game_id in seen:
                continue
            seen.add(prior_game_id)
            self._co_play_graph.add_edge(session.game_id, prior_game_id, 1.0)
            self._co_play_graph.add_edge(prior_game_id, session.game_id, 1.0)
        recent_games.insert(0, session.game_id)
        del recent_games[24:]
        self._player_recent_game_ids.put(username, recent_games)

        if refresh_popular:
            self._popular_cache = self._sort_popular_games(list(self.games.values()))

    def has_history(self, player: Player | None) -> bool:
        if player is None:
            return False
        history = self._player_history.get(player.username.strip().lower())
        return isinstance(history, SessionHistory) and not history.is_empty()

    def recently_played(self, player: Player | None, limit: int = 5) -> list[Game]:
        """Return unique recent games for a player, with popular fallback."""

        if player is None:
            return self.popular_games(limit)
        history = self._player_history.get(player.username.strip().lower())
        if not isinstance(history, SessionHistory) or history.is_empty():
            return self.popular_games(limit)

        rows: list[Game] = []
        seen: set[str] = set()
        nodes = sorted(history.get_all(), key=lambda item: self._timestamp_rank(str(item.timestamp)), reverse=True)
        for node in nodes:
            if node.game_id in seen:
                continue
            game = self.games.get(node.game_id)
            if game is None:
                continue
            rows.append(game)
            seen.add(node.game_id)
            if len(rows) >= limit:
                break
        return rows or self.popular_games(limit)

    def recommended(self, player: Player | None, limit: int = 5) -> list[Game]:
        """Return deterministic recommendations based on history patterns."""

        if player is None or not self.has_history(player):
            return self.popular_games(limit)

        username = player.username.strip().lower()
        history = self._player_history.get(username)
        played_nodes = history.get_all() if isinstance(history, SessionHistory) else []
        genre_scores = ChainedHashTable()
        tag_scores = ChainedHashTable()
        played_counts = self._player_game_counts.get(username, ChainedHashTable())
        played_games = {node.game_id for node in played_nodes}

        for node in played_nodes:
            game = self.games.get(node.game_id)
            if game is None:
                continue
            genre_scores.put(game.genre, int(genre_scores.get(game.genre, 0) or 0) + 1)
            for tag in game.tags:
                tag_scores.put(tag, int(tag_scores.get(tag, 0) or 0) + 1)

        co_play_scores = self._co_play_scores(played_nodes)
        scored: list[tuple[float, Game]] = []
        for game in self.games.values():
            score = 0.0
            score += float(genre_scores.get(game.genre, 0) or 0) * 12.0
            score += sum(float(tag_scores.get(tag, 0) or 0) * 3.0 for tag in game.tags)
            score += float(co_play_scores.get(game.game_id, 0) or 0) * 5.0
            score += min(game.players_now, 3000) / 3000.0
            score += min(int(self._game_recent_activity.get(game.game_id, 0) or 0), 200) / 40.0
            if game.playable:
                score += 7.5
            if game.game_id in played_games:
                score -= 18.0 + float(played_counts.get(game.game_id, 0) or 0)
            if score > 0:
                scored.append((score, game))

        scored.sort(key=lambda item: (item[0], item[1].playable, item[1].players_now, item[1].title), reverse=True)
        recommendations = [game for _, game in scored[:limit]]
        return recommendations or self.popular_games(limit)

    def popular_games(self, limit: int = 5) -> list[Game]:
        return self._popular_cache[:limit]

    def _history_for(self, username: str) -> SessionHistory:
        history = self._player_history.get(username)
        if not isinstance(history, SessionHistory):
            history = SessionHistory()
            self._player_history.put(username, history)
        return history

    def _counts_for(self, username: str) -> ChainedHashTable:
        counts = self._player_game_counts.get(username)
        if not isinstance(counts, ChainedHashTable):
            counts = ChainedHashTable()
            self._player_game_counts.put(username, counts)
        return counts

    def _recent_games_for(self, username: str) -> list[str]:
        recent_games = self._player_recent_game_ids.get(username)
        if not isinstance(recent_games, list):
            recent_games = []
            self._player_recent_game_ids.put(username, recent_games)
        return recent_games

    def _co_play_scores(self, played_nodes: list[SessionNode]) -> ChainedHashTable:
        scores = ChainedHashTable()
        seen_sources: set[str] = set()
        for node in played_nodes[:20]:
            if node.game_id in seen_sources:
                continue
            seen_sources.add(node.game_id)
            for edge in self._co_play_graph.neighbors(node.game_id):
                scores.put(edge.target, float(scores.get(edge.target, 0.0) or 0.0) + float(edge.weight))
        return scores

    def _sort_popular_games(self, games: list[Game]) -> list[Game]:
        return sorted(
            games,
            key=lambda game: (
                int(self._game_popularity.get(game.game_id, 0) or 0),
                game.players_now,
                game.total_plays,
                game.playable,
            ),
            reverse=True,
        )

    def _is_recent(self, timestamp: str) -> bool:
        return self._timestamp_rank(timestamp) >= self._timestamp_rank("2026-03-20T00:00:00")

    def _timestamp_rank(self, timestamp: str) -> float:
        timestamp = timestamp.strip()
        try:
            return datetime.fromisoformat(timestamp).timestamp()
        except ValueError:
            pass
        lowered = timestamp.lower()
        if lowered.startswith("today"):
            return datetime(2026, 4, 27, 23, 0, 0).timestamp()
        if lowered.startswith("yesterday"):
            return datetime(2026, 4, 26, 23, 0, 0).timestamp()
        match = re.match(r"(\d+)\s+days?\s+ago", lowered)
        if match:
            return datetime(2026, 4, 27).timestamp() - int(match.group(1)) * 86_400
        match = re.match(r"(\d+)\s+weeks?\s+ago", lowered)
        if match:
            return datetime(2026, 4, 27).timestamp() - int(match.group(1)) * 7 * 86_400
        if "last week" in lowered:
            return datetime(2026, 4, 20).timestamp()
        return 0.0
