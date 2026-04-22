from datastructures.stack import Stack

class GameState:
    def __init__(self, player_x, player_y, frame):
        self.player_x = player_x
        self.player_y = player_y
        self.frame = frame

class TimeTravel:

    """
    Manages game state history...
    """
    def __init__(self, max_history=180, sample_rate=10):
        """
        Initialize the time travel system.
        """
        # Create stacks
        self.history = Stack()
        self.future = Stack()

        # Store settings
        self.max_history = max_history
        self.sample_rate = sample_rate

        # Counters
        self.frame_counter = 0
        self.frames_since_last_record = 0

        # Rewinding flag
        self.rewinding = False


    def record_state(self, player_x, player_y):
        """
        Record the current game state (sampled based on sample_rate).
        """
        # Increment counters
        self.frames_since_last_record += 1

        # Only record every sample_rate frames
        if self.frames_since_last_record >= self.sample_rate:
            # Create snapshot
            state = GameState(player_x, player_y, self.frame_counter)

            # Push to history
            self.history.push(state)

            # If history too large, remove oldest (bottom of stack)
            if self.history.size() > self.max_history:
                temp_stack = Stack()

                # Reverse history into temp
                while not self.history.is_empty():
                    temp_stack.push(self.history.pop())

                # Remove oldest (top of temp)
                temp_stack.pop()

                # Restore back to history
                while not temp_stack.is_empty():
                    self.history.push(temp_stack.pop())

            # New action clears future (new timeline)
            self.future.clear()

            # Reset sampling counter
            self.frames_since_last_record = 0

        # Always increment frame counter
        self.frame_counter += 1


    def can_rewind(self):
        """
        Check if rewinding is possible.
        """
        return self.history.size() >= 2


    def can_replay(self):
        """
        Check if replaying forward is possible.
        """
        return not self.future.is_empty()


    def rewind(self):
        """
        Go back one frame in time.
        """
        if not self.can_rewind():
            return None

        # Pop current state
        current = self.history.pop()

        # Push into future
        self.future.push(current)

        # Return previous state
        return self.history.peek()


    def replay(self):
        """
        Go forward one frame in time (after rewinding).
        """
        if not self.can_replay():
            return None

        # Get next state
        state = self.future.pop()

        # Push back to history
        self.history.push(state)

        return state


    def get_history_size(self):
        """Get number of states in history"""
        return self.history.size()


    def get_future_size(self):
        """Get number of states in future (available for replay)"""
        return self.future.size()


    def clear(self):
        """
        Clear all history and future states.
        """
        self.history.clear()
        self.future.clear()
        self.frame_counter = 0
        self.frames_since_last_record = 0
