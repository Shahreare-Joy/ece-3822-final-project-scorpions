from __future__ import annotations

"""Minimal linked stack for DFS.

The graph uses this instead of a Python list stack so traversal stays aligned
with the custom data-structure requirement.
"""

from dataclasses import dataclass
from typing import TypeVar


T = TypeVar("T")


@dataclass
class _StackNode:
    # value stored in node
    value: object

    # pointer to next node
    next: "_StackNode | None" = None


class LinkedStack:
    def __init__(self) -> None:
        # top of stack
        self._top: _StackNode | None = None

        # number of elements
        self._size = 0

    def __len__(self) -> int:
        '''return number of elements in stack'''
        return self._size

    def is_empty(self) -> bool:
        '''check if stack is empty'''
        return self._size == 0

    def push(self, value: T) -> None:
        '''push value onto stack'''

        # create new node and link to current top
        self._top = _StackNode(value, self._top)

        # increase size
        self._size += 1

    def pop(self) -> T:
        '''remove and return top value'''

        # error if stack is empty
        if self._top is None:
            raise IndexError("pop from empty stack")

        # get top value
        value = self._top.value

        # move top pointer down
        self._top = self._top.next

        # decrease size
        self._size -= 1

        return value  # type: ignore[return-value]