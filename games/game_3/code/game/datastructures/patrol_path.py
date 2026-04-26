"""
patrol_path.py - Linked list implementation for NPC patrol paths

Implements different types of linked lists for NPC movement:
- Singly linked list (one-way patrol)
- Circular linked list (looping patrol)
- Doubly linked list (back-and-forth patrol)

Author: [Mykai Wade]
Date: [4/3/26]
Lab: Lab 5 - NPC Patrol Paths with Linked Lists
"""

from .waypoint import Waypoint

class PatrolPath:
    """
    A linked list of waypoints that defines how an NPC moves.

    Supports three patrol types:
    - "one_way": Walk through waypoints once, then stop
    - "circular": Loop through waypoints infinitely
    - "back_and_forth": Walk forward to end, then reverse back to start
    """

    def __init__(self, patrol_type="circular"):
        """
        Initialize an empty patrol path.

        Args:
            patrol_type (str): Type of patrol - "one_way", "circular", or "back_and_forth"
        """
        self.head = None             # first waypoint in the list
        self.tail = None             # last waypoint in the list
        self.current = None          # waypoint NPC is currently moving toward
        self.patrol_type = patrol_type  # "one_way", "circular", or "back_and_forth"
        self.size = 0                # number of waypoints
        self.direction = 1           # 1 = forward, -1 = backward (back_and_forth only)

    def add_waypoint(self, x, y, wait_time=0):
        """
        Add a waypoint to the end of the patrol path.

        Args:
            x (float): X coordinate
            y (float): Y coordinate
            wait_time (float): How long to wait at this waypoint
        """
        new_node = Waypoint(x, y, wait_time)  # create the new waypoint node

        if self.head is None:
            self.head = new_node     # first node becomes the head
            self.tail = new_node     # first node is also the tail
            self.current = new_node  # start patrolling from first node
        else:
            self.tail.next = new_node  # link new node after current tail

            if self.patrol_type in ("back_and_forth", "circular"):
                new_node.prev = self.tail  # set prev pointer for doubly linked types

            self.tail = new_node     # update tail to new node

        if self.patrol_type == "circular":
            self.tail.next = self.head  # close the loop: tail points back to head
            self.head.prev = self.tail  # head's prev points to tail

        self.size += 1  # increment count

    def get_next_waypoint(self):
        """
        Get the next waypoint in the patrol sequence.

        Returns:
            Waypoint: The next waypoint to move toward, or None if patrol is complete
        """
        if self.current is None:     # empty or finished patrol
            return None

        result = self.current        # save current waypoint to return

        if self.patrol_type == "one_way":
            self.current = self.current.next  # advance forward, hits None at end

        elif self.patrol_type == "circular":
            self.current = self.current.next  # wraps around because tail.next = head

        elif self.patrol_type == "back_and_forth":
            if self.direction == 1:                     # moving forward
                if self.current == self.tail:
                    self.direction = -1                 # hit the end, reverse direction
                    self.current = self.current.prev    # step backward
                else:
                    self.current = self.current.next    # keep going forward
            else:                                       # moving backward
                if self.current == self.head:
                    self.direction = 1                  # hit the start, reverse direction
                    self.current = self.current.next    # step forward
                else:
                    self.current = self.current.prev    # keep going backward

        return result  # return the waypoint NPC should move toward

    def reset(self):
        """Reset patrol to the beginning."""
        self.current = self.head
        self.direction = 1

    def __len__(self):
        return self.size

    def __iter__(self):
        self._iter_current = self.head
        return self

    def __next__(self):
        if self._iter_current is None:
            raise StopIteration
        result = self._iter_current
        if self._iter_current == self.tail:
            self._iter_current = None
        else:
            self._iter_current = self._iter_current.next
        return result

    def is_empty(self):
        return self.head is None

    def get_path_info(self):
        return {
            "type": self.patrol_type,
            "length": len(self),
            "current": str(self.current) if self.current else "None",
            "direction": self.direction if self.patrol_type == "back_and_forth" else "N/A"
        }
    # end of file 
