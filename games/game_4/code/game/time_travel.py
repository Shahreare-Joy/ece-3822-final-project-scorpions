"""
time_travel.py - Time travel system

Single-player mode uses this to rewind and replay player movement.

Author: Kevin Le
Date:   2026-04-27
Lab:    Lab 4 - Time Travel with Stacks
"""

import time
from datastructures.stack import Stack


class GameState:
    """Snapshot of the player's position at one moment in time."""

    def __init__(self, player_x, player_y, timestamp=None):
        """Store player position and creation time."""
        self.player_x = player_x
        self.player_y = player_y
        self.timestamp = time.time() if timestamp is None else timestamp

    def __repr__(self):
        """Return a debug representation."""
        return (
            f"GameState(player_x={self.player_x}, "
            f"player_y={self.player_y}, timestamp={self.timestamp})"
        )


class TimeTravel:
    """Manages rewind and replay history using two stacks."""

    def __init__(self, max_history=180, sample_rate=10):
        """Initialize history and future stacks."""
        self.max_history = max_history
        self.sample_rate = max(1, sample_rate)
        self.history = Stack(capacity=max_history)
        self.future = Stack(capacity=max_history)
        self._sample_counter = 0

    def _push_bounded(self, stack, state):
        """Push into a fixed custom stack, dropping oldest state if full."""
        if stack.is_full():
            stack.pop_oldest()
        try:
            stack.push(state)
        except OverflowError:
            # Final guard: gameplay should never crash if history storage fills.
            stack.pop_oldest()
            stack.push(state)

    def record_state(self, player_x, player_y):
        """Record a new state every sample_rate calls."""
        self._sample_counter += 1
        if self._sample_counter < self.sample_rate:
            return

        self._sample_counter = 0
        new_state = GameState(player_x, player_y)

        if not self.history.is_empty():
            latest = self.history.peek()
            if latest.player_x == player_x and latest.player_y == player_y:
                return

        self._push_bounded(self.history, new_state)
        self.future.clear()

    def can_rewind(self):
        """Return True if at least one earlier state exists."""
        return self.history.size() > 1

    def can_replay(self):
        """Return True if a future state is available."""
        return not self.future.is_empty()

    def rewind(self):
        """Step backward one recorded state."""
        if not self.can_rewind():
            return None

        current = self.history.pop()
        self._push_bounded(self.future, current)
        return self.history.peek()

    def replay(self):
        """Step forward one recorded state."""
        if not self.can_replay():
            return None

        state = self.future.pop()
        self._push_bounded(self.history, state)
        return state

    def get_history_size(self):
        """Return the number of recorded past states."""
        return self.history.size()

    def get_future_size(self):
        """Return the number of recorded future states."""
        return self.future.size()

    def clear(self):
        """Clear all recorded rewind/replay state."""
        self.history.clear()
        self.future.clear()
        self._sample_counter = 0
