from __future__ import annotations
 
"""Binary Search Tree.
 
Use cases:
- ordered player/game search
- autocomplete or prefix range traversal if keys are strings
- score range queries
- date range queries for match history
 
Expected complexity:
- balanced tree: O(log n) insert/search
- unbalanced tree: O(n) worst case
 
NOTE: This is a plain (unbalanced) BST. If keys are inserted in sorted order
the tree degrades into a linked list. Shuffle records before bulk insertion
to mitigate this (see Risk #2 in the design doc).
"""
 
 
# ---------------------------------------------------------------------------
# Internal node
# ---------------------------------------------------------------------------
 
class _BSTNode:
    """A single node in the binary search tree.
 
    Attributes:
        key:   Comparable value used for ordering (string, int, float, etc.)
        value: Associated payload (any Python object).
        left:  Left child node (keys < this key), or None.
        right: Right child node (keys > this key), or None.
    """
 
    def __init__(self, key: object, value: object) -> None:
        self.key: object = key
        self.value: object = value
        self.left: _BSTNode | None = None
        self.right: _BSTNode | None = None
 
 
# ---------------------------------------------------------------------------
# Binary Search Tree
# ---------------------------------------------------------------------------
 
class BinarySearchTree:
    def __init__(self) -> None:
        self.root: _BSTNode | None = None
        self._size: int = 0
 
    def insert(self, key: object, value: object) -> None:
        self.root, inserted = self._insert(self.root, key, value)
        if inserted:
            self._size += 1
 
    def search(self, key: object) -> object | None:
        node = self._search(self.root, key)
        return node.value if node is not None else None
 
    def delete(self, key: object) -> bool:
        self.root, removed = self._delete(self.root, key)
        if removed:
            self._size -= 1
        return removed
 
    def range_query(self, low: object, high: object) -> list:
        results = []
        self._range_query(self.root, low, high, results)
        return results
 
    def inorder(self) -> list:
        results = []
        self._inorder(self.root, results)
        return results
 
    def prefix_search(self, prefix: str) -> list:
        results = []
        self._prefix_search(self.root, prefix, results)
        return results
 
    def __len__(self) -> int:
        """Return number of nodes in the tree. Time complexity: O(1)."""
        return self._size                                   # FIX: indentation
 
    def __repr__(self) -> str:
        return f"BinarySearchTree(size={self._size})"
 
    # Private recursive helpers
 
    def _insert(                                            # FIX: was "def_insert", outside class
        self, node: _BSTNode | None, key: object, value: object
    ) -> tuple[_BSTNode, bool]:
        """Recursively insert and return (updated_node, was_new_key)."""
        if node is None:
            return _BSTNode(key, value), True
        if key < node.key:
            node.left, inserted = self._insert(node.left, key, value)
            return node, inserted
        if key > node.key:
            node.right, inserted = self._insert(node.right, key, value)
            return node, inserted
        # key == node.key: update value, not a new insertion
        node.value = value
        return node, False
 
    def _search(self, node: _BSTNode | None, key: object) -> _BSTNode | None:
        """Recursively search and return the matching node or None."""
        if node is None:
            return None
        if key == node.key:
            return node
        if key < node.key:
            return self._search(node.left, key)
        return self._search(node.right, key)
 
    def _delete(
        self, node: _BSTNode | None, key: object
    ) -> tuple[_BSTNode | None, bool]:
        """Recursively delete *key* and return (updated_node, was_removed)."""
        if node is None:
            return None, False
        if key < node.key:
            node.left, removed = self._delete(node.left, key)
            return node, removed
        if key > node.key:
            node.right, removed = self._delete(node.right, key)
            return node, removed
        # Found the node to delete
        if node.left is None:
            return node.right, True      # replace with right child
        if node.right is None:
            return node.left, True       # replace with left child
        # Two children: replace with in-order successor (smallest in right subtree)
        successor = self._min_node(node.right)
        node.key = successor.key
        node.value = successor.value
        node.right, _ = self._delete(node.right, successor.key)
        return node, True
 
    def _min_node(self, node: _BSTNode) -> _BSTNode:
        """Return the leftmost (smallest key) node in a subtree."""
        current = node
        while current.left is not None:
            current = current.left
        return current
 
    def _inorder(self, node: _BSTNode | None, results: list) -> None:
        """Append values to *results* in ascending key order."""
        if node is None:
            return
        self._inorder(node.left, results)
        results.append(node.value)
        self._inorder(node.right, results)
 
    def _range_query(
        self, node: _BSTNode | None, low: object, high: object, results: list
    ) -> None:
        """Append values in [low, high] to *results*, pruning dead branches."""
        if node is None:
            return
        # Prune: if current key > high, no need to go right
        if node.key > high:
            self._range_query(node.left, low, high, results)
            return
        # Prune: if current key < low, no need to go left
        if node.key < low:
            self._range_query(node.right, low, high, results)
            return
        # Current key is in range: visit left, record self, visit right
        self._range_query(node.left, low, high, results)
        results.append(node.value)
        self._range_query(node.right, low, high, results)
 
    def _prefix_search(
        self, node: _BSTNode | None, prefix: str, results: list
    ) -> None:
        """Collect values whose string key starts with *prefix*."""
        if node is None:
            return
        key = node.key
        if key.startswith(prefix):
            # Key matches: check both subtrees (siblings may also match)
            self._prefix_search(node.left, prefix, results)
            results.append(node.value)
            self._prefix_search(node.right, prefix, results)
        elif key < prefix:
            # Current key is alphabetically before prefix: only go right
            self._prefix_search(node.right, prefix, results)
        else:
            # Current key is alphabetically after prefix: only go left
            self._prefix_search(node.left, prefix, results)
 
# end of file
 
