from __future__ import annotations

"""Binary Search Tree.

Use cases:
- ordered player/game search
- autocomplete or prefix range traversal if keys are strings
- score range queries
- date range queries for match history
"""

from dataclasses import dataclass, field
from typing import Any


@dataclass
class _Node:
    # store key and list of values for duplicate keys
    key: Any
    values: list[object] = field(default_factory=list)

    # left and right child pointers
    left: "_Node | None" = None
    right: "_Node | None" = None


class BinarySearchTree:
    """Simple iterative BST that supports duplicate keys."""

    def __init__(self) -> None:
        # initialize empty tree
        self.root: _Node | None = None
        self._size = 0

    def __len__(self) -> int:
        '''return total number of stored values'''
        return self._size

    def insert(self, key: object, value: object) -> None:
        '''insert key-value pair into BST'''

        # create root if tree is empty
        if self.root is None:
            self.root = _Node(key, [value])
            self._size += 1
            return

        current = self.root

        # iterate until correct position is found
        while True:
            if key == current.key:
                # append to existing node for duplicate key
                current.values.append(value)
                self._size += 1
                return

            if key < current.key:
                if current.left is None:
                    # insert new node on left
                    current.left = _Node(key, [value])
                    self._size += 1
                    return
                current = current.left
            else:
                if current.right is None:
                    # insert new node on right
                    current.right = _Node(key, [value])
                    self._size += 1
                    return
                current = current.right

    def search(self, key: object) -> object | None:
        '''return most recent value for key'''

        current = self.root

        # traverse tree until key is found or None reached
        while current is not None:
            if key == current.key:
                # return last inserted value for key
                return current.values[-1] if current.values else None

            # move left or right based on comparison
            current = current.left if key < current.key else current.right

        return None

    def search_all(self, key: object) -> list[object]:
        '''return all values stored under key'''

        current = self.root

        # traverse tree to find key
        while current is not None:
            if key == current.key:
                return list(current.values)

            current = current.left if key < current.key else current.right

        return []

    def delete(self, key: object) -> bool:
        '''delete node with key and all its values'''

        parent: _Node | None = None
        current = self.root

        # find node to delete
        while current is not None and current.key != key:
            parent = current
            current = current.left if key < current.key else current.right

        # key not found
        if current is None:
            return False

        # count values to adjust size later
        removed_count = len(current.values)

        # case: node has two children
        if current.left is not None and current.right is not None:
            successor_parent = current
            successor = current.right

            # find inorder successor (smallest in right subtree)
            while successor.left is not None:
                successor_parent = successor
                successor = successor.left

            # replace current node data with successor
            current.key = successor.key
            current.values = successor.values

            # now delete successor node
            current = successor
            parent = successor_parent

        # case: node has 0 or 1 child
        child = current.left if current.left is not None else current.right

        if parent is None:
            # deleting root node
            self.root = child
        elif parent.left is current:
            parent.left = child
        else:
            parent.right = child

        # update size based on removed values
        self._size -= removed_count
        return True

    def range_query(self, low: object, high: object) -> list[object]:
        '''return values where low <= key <= high'''

        # TODO (DONE)(BST RANGE): Return values with low <= key <= high.

        # reject invalid range
        if low > high:
            return []

        results: list[object] = []
        stack: list[_Node] = []
        current = self.root

        # iterative inorder traversal
        while stack or current is not None:
            while current is not None:
                stack.append(current)
                current = current.left

            current = stack.pop()

            # collect values within range
            if low <= current.key <= high:
                results.extend(current.values)

            # stop early if keys exceed upper bound
            if current.key > high:
                break

            current = current.right

        return results

    def inorder(self) -> list[object]:
        '''return all values in sorted order'''

        results: list[object] = []
        stack: list[_Node] = []
        current = self.root

        # iterative inorder traversal
        while stack or current is not None:
            while current is not None:
                stack.append(current)
                current = current.left

            current = stack.pop()
            results.extend(current.values)
            current = current.right

        return results

    def prefix_query(self, prefix: str, limit: int = 10) -> list[object]:
        '''return values whose keys start with prefix'''

        prefix = prefix.lower()

        # reject invalid prefix or limit
        if not prefix or limit <= 0:
            return []

        results: list[object] = []
        stack: list[_Node] = []
        current = self.root

        # inorder traversal with early stop at limit
        while (stack or current is not None) and len(results) < limit:
            while current is not None:
                stack.append(current)
                current = current.left

            current = stack.pop()

            # match prefix and collect values
            if str(current.key).lower().startswith(prefix):
                results.extend(current.values[: max(0, limit - len(results))])

            current = current.right

        return results[:limit]