from __future__ import annotations

"""Minimal custom linked list.

This structure is intentionally small because it exists to support the graph
adjacency lists without falling back to Python's built-in list. It stores nodes
manually and provides only the operations the graph needs.
"""

from dataclasses import dataclass
from typing import Callable, Iterator, TypeVar


T = TypeVar("T")


@dataclass
class _LinkedNode:
    # value stored in node
    value: object

    # pointer to next node
    next: "_LinkedNode | None" = None

    # pointer to previous node (doubly linked)
    previous: "_LinkedNode | None" = None


class LinkedList:
    """Node-based list with append, removal, and forward/reverse iteration."""

    def __init__(self) -> None:
        # head of list (first node)
        self._head: _LinkedNode | None = None

        # tail of list (last node)
        self._tail: _LinkedNode | None = None

        # number of elements
        self._size = 0

    def __len__(self) -> int:
        '''return number of elements in list'''
        return self._size

    def append(self, value: T) -> None:
        '''append value to end of list'''
        """Add a value to the end of the linked list."""

        # create new node
        node = _LinkedNode(value)

        # if list is empty, set head and tail
        if self._tail is None:
            self._head = node
            self._tail = node
        else:
            # link new node to current tail
            node.previous = self._tail
            self._tail.next = node
            self._tail = node

        # increase size
        self._size += 1

    def remove_first_matching(self, predicate: Callable[[T], bool]) -> bool:
        '''remove first node that matches predicate'''
        """Remove the first node whose value matches predicate."""

        current = self._head

        while current is not None:
            value = current.value

            # check predicate condition
            if predicate(value):  # type: ignore[arg-type]
                self._unlink(current)
                return True

            current = current.next

        return False

    def __iter__(self) -> Iterator[T]:
        '''iterate forward through list'''

        current = self._head

        while current is not None:
            yield current.value  # type: ignore[misc]
            current = current.next

    def reversed_values(self) -> Iterator[T]:
        '''iterate backward through list'''

        current = self._tail

        while current is not None:
            yield current.value  # type: ignore[misc]
            current = current.previous

    def to_list(self) -> list[T]:
        '''convert linked list to python list (for debugging/tests only)'''
        """Return a Python list for tests/UI display only, not core storage."""

        return [value for value in self]

    def _unlink(self, node: _LinkedNode) -> None:
        '''remove node from linked list'''

        # get surrounding nodes
        before = node.previous
        after = node.next

        # update head if needed
        if before is None:
            self._head = after
        else:
            before.next = after

        # update tail if needed
        if after is None:
            self._tail = before
        else:
            after.previous = before

        # decrease size
        self._size -= 1