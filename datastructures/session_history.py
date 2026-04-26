from __future__ import annotations
 
"""Custom linked list for per-player match history.
 
This structure stores session records for each player without falling back
to Python's built-in list. It stores nodes manually and provides only the
operations the platform server needs for history queries and filters.
"""
 
 
class SessionNode:
    # game that was played
    game_id: str
 
    # when the session occurred
    timestamp: object
 
    # player score for this session
    score: int | float
 
    # result of the session
    outcome: str
 
    # pointer to next node
    next: "SessionNode | None"
 
    def __init__(
        self,
        game_id: str,
        timestamp: object,
        score: int | float,
        outcome: str = "unknown",
    ) -> None:
        self.game_id = game_id
        self.timestamp = timestamp
        self.score = score
        self.outcome = outcome
        self.next = None
 
    def __repr__(self) -> str:
        return (
            f"SessionNode(game_id={self.game_id!r}, timestamp={self.timestamp!r}, "
            f"score={self.score}, outcome={self.outcome!r})"
        )
 
 
class SessionHistory:
    """Singly linked list storing session records for a single player."""
 
    def __init__(self) -> None:
        # head of list (most recent session)
        self.head: SessionNode | None = None
 
        # number of sessions stored
        self._size: int = 0
 
    def __len__(self) -> int:
        '''return number of sessions in list'''
        return self._size
 
    def prepend(
        self,
        game_id: str,
        timestamp: object,
        score: int | float,
        outcome: str = "unknown",
    ) -> None:
        '''add new session to front of list'''
 
        # create new node
        node = SessionNode(game_id, timestamp, score, outcome)
 
        # link new node to current head
        node.next = self.head
        self.head = node
 
        # increase size
        self._size += 1
 
    def get_all(self) -> list:
        '''return all sessions most recent first'''
 
        results = []
        current = self.head
 
        # walk the list and collect all nodes
        while current is not None:
            results.append(current)
            current = current.next
 
        return results
 
    def filter_by_game(self, game_id: str) -> list:
        '''return only sessions matching game_id'''
 
        results = []
        current = self.head
 
        while current is not None:
            # check if game matches
            if current.game_id == game_id:
                results.append(current)
            current = current.next
 
        return results
 
    def filter_by_outcome(self, outcome: str) -> list:
        '''return only sessions matching outcome'''
 
        results = []
        current = self.head
 
        while current is not None:
            # check if outcome matches
            if current.outcome == outcome:
                results.append(current)
            current = current.next
 
        return results
 
    def filter_by_date_range(self, low: object, high: object) -> list:
        '''return sessions where low <= timestamp <= high'''
 
        results = []
        current = self.head
 
        while current is not None:
            # check if timestamp is within range
            if low <= current.timestamp <= high:
                results.append(current)
            current = current.next
 
        return results
 
    def filter(
        self,
        game_id: str | None = None,
        outcome: str | None = None,
        low_ts: object = None,
        high_ts: object = None,
    ) -> list:
        '''filter sessions by game, outcome, and date range in one pass'''
 
        results = []
        current = self.head
 
        while current is not None:
            # assume match until a filter fails
            match = True
 
            # check game filter
            if game_id is not None and current.game_id != game_id:
                match = False
 
            # check outcome filter
            if outcome is not None and current.outcome != outcome:
                match = False
 
            # check lower timestamp bound
            if low_ts is not None and current.timestamp < low_ts:
                match = False
 
            # check upper timestamp bound
            if high_ts is not None and current.timestamp > high_ts:
                match = False
 
            if match:
                results.append(current)
 
            current = current.next
 
        return results
 
    def delete(self, game_id: str, timestamp: object) -> bool:
        '''remove first session matching game_id and timestamp'''
 
        prev = None
        current = self.head
 
        while current is not None:
            # check if this node matches
            if current.game_id == game_id and current.timestamp == timestamp:
 
                # removing head
                if prev is None:
                    self.head = current.next
                else:
                    # bypass current node
                    prev.next = current.next
 
                # decrease size
                self._size -= 1
                return True
 
            prev = current
            current = current.next
 
        return False
 
    def is_empty(self) -> bool:
        '''return true if list has no sessions'''
        return self._size == 0
 
    def __repr__(self) -> str:
        return f"SessionHistory(size={self._size})"

 # end of file 
