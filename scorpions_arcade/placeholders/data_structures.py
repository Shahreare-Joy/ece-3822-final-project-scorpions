from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from scorpions_arcade.models import Game, GameSession, LeaderboardEntry, Player


@dataclass
class QueryMetrics:
    """Future performance-analysis measurements.

    TODO(ANALYSIS): Fill this from real data-structure operations when your
    group benchmarks runtime, comparisons, and complexity.
    """

    operation_name: str
    input_size: int
    structure_name: str = "placeholder"
    elapsed_ms: float = 0.0
    comparisons: int = 0
    notes: str = "placeholder"


class PlayerIndexHook(Protocol):
    """Future efficient player lookup/search interface.

    Intended scale: 10,000+ players.

    Possible structures:
    - Hash table for exact username lookup.
    - Trie for prefix autocomplete.
    - BST if your design needs ordered username/rank traversal.

    TODO(TEAM): Implement this in your final data-structure module and benchmark
    it against a brute-force scan from SearchService.
    """

    def find_by_username(self, username: str) -> Player | None:
        raise NotImplementedError

    def search_players(self, query: str, limit: int) -> list[Player]:
        raise NotImplementedError

    def autocomplete_players(self, prefix: str, limit: int) -> list[Player]:
        raise NotImplementedError


class GameCatalogIndexHook(Protocol):
    """Future catalog/search interface.

    Intended scale: large catalog plus genre/creator/popularity browsing.

    Possible structures:
    - Hash table for exact game_id lookup.
    - Inverted index for title/tag/creator search.
    - BST or sorted arrays for popularity/release-year/ranked browsing.
    - Graph for recommendation links between players, games, and genres.
    """

    def get_game(self, game_id: str) -> Game | None:
        raise NotImplementedError

    def filter_by_genre(self, genre: str) -> list[Game]:
        raise NotImplementedError

    def search_games(self, query: str, limit: int) -> list[Game]:
        raise NotImplementedError

    def filter_by_creator(self, creator: str) -> list[Game]:
        raise NotImplementedError

    def sort_games(self, games: list[Game], sort_by: str) -> list[Game]:
        raise NotImplementedError


class LeaderboardIndexHook(Protocol):
    """Future leaderboard ranking/range-query interface.

    Intended scale: many scores per game, responsive top-N and rank lookup.

    Possible structures:
    - Heap / priority queue for top-N scores.
    - BST or balanced tree for score range queries and rank lookup.
    - Sorting algorithms for total score, win rate, play time, and report demos.
    """

    def get_top_scores(self, game_id: str, limit: int) -> list[LeaderboardEntry]:
        raise NotImplementedError

    def get_rank_for_player(self, game_id: str, username: str) -> int | None:
        raise NotImplementedError

    def score_range(self, game_id: str, low_score: int, high_score: int) -> list[LeaderboardEntry]:
        raise NotImplementedError

    def sort_by_metric(self, game_id: str, metric: str, limit: int) -> list[LeaderboardEntry]:
        raise NotImplementedError


class MatchHistoryIndexHook(Protocol):
    """Future session-history interface.

    Intended scale: 100,000+ sessions.

    Possible structures:
    - Hash table from username -> sessions for profile/history lookup.
    - Hash table from game_id -> sessions for game detail pages.
    - Time-indexed BST for date range queries.
    - Linked list or deque for recent chronological activity.
    """

    def recent_sessions(self, limit: int) -> list[GameSession]:
        raise NotImplementedError

    def sessions_for_player(self, username: str, limit: int) -> list[GameSession]:
        raise NotImplementedError

    def sessions_for_game(self, game_id: str, limit: int) -> list[GameSession]:
        raise NotImplementedError

    def sessions_by_date_range(self, start_date: str, end_date: str, limit: int) -> list[GameSession]:
        raise NotImplementedError

    def sessions_by_outcome(self, result: str, limit: int) -> list[GameSession]:
        raise NotImplementedError

    def sorted_by_date(self, sessions: list[GameSession], descending: bool = True) -> list[GameSession]:
        raise NotImplementedError


class ProfileStatsHook(Protocol):
    """Future profile aggregation interface.

    TODO(PROFILE): Compute games played, total play time, win rate, favorite
    games, score history, and recent performance from the final session index.
    """

    def aggregate_for_player(self, username: str) -> dict[str, object]:
        raise NotImplementedError


class ChatChannelIndexHook(Protocol):
    """Future session chat lookup interface.

    The current UI uses a bounded circular buffer per session. Keep that memory
    cap even after networking is added so long sessions do not store unlimited
    client-side chat messages.
    """

    def recent_messages(self, session_id: str, limit: int) -> list[object]:
        raise NotImplementedError

    def append_message(self, session_id: str, message: object) -> None:
        raise NotImplementedError


class RecommendationGraphHook(Protocol):
    """Graph placeholder for recommendations, friend links, and matchmaking."""

    def recommended_games(self, player: Player | None, limit: int) -> list[Game]:
        raise NotImplementedError
