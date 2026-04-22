"""
time_travel.py - Time travel system

Copy your TimeTravel implementation from Lab 4 into this file.
Single-player mode uses this to rewind and replay player movement.

Lab: Lab 4 - Time Travel with Stacks
"""

from datastructures.stack import Stack

# TODO: Copy your GameState and TimeTravel classes from Lab 4 here.
#
# GameState must store: player_x, player_y, timestamp
#
# TimeTravel must support:
#   __init__(max_history=180, sample_rate=10)
#   record_state(player_x, player_y)
#   can_rewind()
#   can_replay()
#   rewind()     -> returns previous GameState or None
#   replay()     -> returns next GameState or None
#   get_history_size()
#   get_future_size()
#   clear()
