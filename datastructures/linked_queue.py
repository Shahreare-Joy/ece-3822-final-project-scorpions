from __future__ import annotations

"""Minimal linked queue for BFS.

This avoids Python list pop(0), which is O(n), and gives graph traversal a
custom O(1) enqueue/dequeue queue.
"""

from dataclasses import dataclass
from typing import TypeVar


T = TypeVar("T")


@dataclass
class _QueueNode:
    # value stored in node
    value: object

    # pointer to next node
    next: "_QueueNode | None" = None


class LinkedQueue:
    def __init__(self) -> None:
        # front of queue (dequeue from here)
        self._front: _QueueNode | None = None

        # back of queue (enqueue here)
        self._back: _QueueNode | None = None

        # number of elements
        self._size = 0

    def __len__(self) -> int:
        '''return number of elements in queue'''
        return self._size

    def is_empty(self) -> bool:
        '''check if queue is empty'''
        return self._size == 0

    def enqueue(self, value: T) -> None:
        '''add value to back of queue'''

        # create new node
        node = _QueueNode(value)

        # if queue is empty, set front and back
        if self._back is None:
            self._front = node
            self._back = node
        else:
            # link new node to current back
            self._back.next = node
            self._back = node

        # increase size
        self._size += 1

    def dequeue(self) -> T:
        '''remove and return value from front of queue'''

        # error if queue is empty
        if self._front is None:
            raise IndexError("dequeue from empty queue")

        # get value from front node
        value = self._front.value

        # move front pointer forward
        self._front = self._front.next

        # if queue becomes empty, reset back pointer
        if self._front is None:
            self._back = None

        # decrease size
        self._size -= 1

        return value  # type: ignore[return-value]