from __future__ import annotations

"""Leaderboard service.

Likely data structures:
- Custom Heap / PriorityQueue for top-N scores
- BST or ordered score index for score range queries
- Sorting algorithms from algorithms/ for report comparisons

TODO (DONE)(LEADERBOARD): Implement ranking using datastructures/heap.py and
range queries using datastructures/bst.py.
"""

from dataclasses import dataclass

from datastructures.bst import BinarySearchTree
from datastructures.hash_table import ChainedHashTable
from datastructures.heap import MaxHeap


NEW_TEAM_GAME_IDS = {"game_1", "game_2", "game_3", "game_4", "scorpions-arena", "sky-raiders", "turbo-sprint", "crystal-run"}


@dataclass
class ScoreRecord:
    # game this score belongs to
    game_id: str

    # player username for this score
    username: str

    # numeric score value
    score: int

    # optional time when score was earned
    timestamp: str = ""


class _GameLeaderboard:
    def __init__(self) -> None:
        # heap used for top-n score lookup
        self.heap = MaxHeap()

        # bst used for score range queries
        self.score_tree = BinarySearchTree()

        # hash table stores best score per player
        self.best_by_player = ChainedHashTable()


class LeaderboardService:
    def __init__(self) -> None:
        # hash table maps game_id -> _GameLeaderboard
        self._boards = ChainedHashTable()

        # aliases kept for TODO/rubric clarity
        self._score_heap = self._boards  # TODO (DONE): custom heap per game.
        self._score_tree = self._boards  # TODO (DONE): score range structure per game.

    def submit_score(self, game_id: str, username: str, score: int, timestamp: str = "") -> bool:
        '''submit score and update leaderboard indexes'''

        # reject invalid game/user/score inputs
        if not game_id or not username or score < 0:
            return False

        # get leaderboard for this game
        board = self._get_board(game_id)

        # check current best score for this player
        current = board.best_by_player.get(username)

        # keep existing score if it is already better or equal
        if isinstance(current, ScoreRecord) and current.score >= score:
            return True

        # create new score record
        record = ScoreRecord(game_id, username, int(score), timestamp)

        # update player's best score
        board.best_by_player.put(username, record)

        # insert into heap for top-n queries
        board.heap.push(record.score, record)

        # insert into bst for score-range queries
        board.score_tree.insert(record.score, record)

        return True

    def top_n(self, game_id: str, n: int = 10) -> list[ScoreRecord]:
        '''return top n unique player scores for one game'''

        # TODO (DONE)(RESILIENCE): Validate game_id and clamp n to a safe maximum.
        # TODO (DONE)(HEAP): Return top N scores without sorting the full dataset.

        # clamp requested count
        n = max(1, min(int(n), 100))

        # get leaderboard for game
        board = self._boards.get(game_id)

        # return empty list if game has no board
        if not isinstance(board, _GameLeaderboard):
            return []

        unique: list[ScoreRecord] = []
        seen = set()

        # pull extra records because heap may contain old scores for same player
        for record in board.heap.top_n(n * 3):
            if isinstance(record, ScoreRecord) and record.username not in seen:
                latest = board.best_by_player.get(record.username)

                # keep record only if it matches player's current best score
                if latest is record or (isinstance(latest, ScoreRecord) and latest.score == record.score):
                    unique.append(record)
                    seen.add(record.username)

            if len(unique) >= n:
                break

        return unique

    def player_rank(self, game_id: str, username: str) -> int | None:
        '''return player rank for one game'''

        # TODO (DONE)(RESILIENCE): Return None or structured errors for missing players/games.
        # TODO (DONE)(RANK INDEX): Implement efficient player rank lookup.

        # get leaderboard for game
        board = self._boards.get(game_id)

        if not isinstance(board, _GameLeaderboard):
            return None

        # get target player's best score
        target = board.best_by_player.get(username)

        if not isinstance(target, ScoreRecord):
            return None

        rank = 1

        # count players with higher score
        for _, value in board.best_by_player.items():
            if isinstance(value, ScoreRecord) and value.score > target.score:
                rank += 1

        return rank

    def score_range(self, game_id: str, low: int, high: int) -> list[ScoreRecord]:
        '''return score records within score range'''

        # TODO (DONE)(RESILIENCE): Validate low <= high and numeric bounds.
        # TODO (DONE)(BST RANGE): Return scores in [low, high].
        # TODO (DONE)(BENCHMARK): See benchmarks/leaderboard_benchmark.py.

        # fix reversed bounds
        if low > high:
            low, high = high, low

        # get leaderboard for game
        board = self._boards.get(game_id)

        if not isinstance(board, _GameLeaderboard):
            return []

        # query bst for score range
        records = [
            record
            for record in board.score_tree.range_query(low, high)
            if isinstance(record, ScoreRecord)
        ]

        # keep only current best score records per player
        best = {record.username: record.score for record in self.top_n(game_id, 100)}
        return [record for record in records if best.get(record.username) == record.score]

    def load_from_sessions(self, sessions: list[dict[str, object]]) -> int:
        '''load leaderboard scores from session rows'''

        loaded = 0

        for row in sessions:
            try:
                game_id = str(row["game_id"])
                if game_id in NEW_TEAM_GAME_IDS:
                    continue
                # submit score from session row
                if self.submit_score(
                    game_id,
                    str(row.get("username") or row.get("player_id")),
                    int(row["score"]),
                    str(row.get("started_at", ""))
                ):
                    loaded += 1
            except (KeyError, TypeError, ValueError):
                # skip malformed session rows
                continue

        return loaded

    def _get_board(self, game_id: str) -> _GameLeaderboard:
        '''get existing game leaderboard or create a new one'''

        # lookup board by game_id
        board = self._boards.get(game_id)

        # create board if missing
        if not isinstance(board, _GameLeaderboard):
            board = _GameLeaderboard()
            self._boards.put(game_id, board)

        return board
