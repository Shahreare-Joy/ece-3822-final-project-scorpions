import sys
import os
sys.path.insert(0, os.path.dirname(__file__))
from array import ArrayList

"""
sparse_matrix.py - Sparse Matrix implementation

A sparse matrix stores only non-default entries, saving memory when most
cells share the same value (like -1 in a tile map).

Choose one of three backing representations:

  Option A — DOK (Dictionary of Keys): {(row, col): value}
    Requires implementing HashTable in hash_table.py.
    Do not use Python's built-in dict or set.

  Option B — COO (Coordinate List): list of (row, col, value) triples
    Use your ArrayList from Lab 3. Do not use Python's built-in list.

  Option C — CSR (Compressed Sparse Row): three parallel arrays
    row_ptr, col_idx, values. Most efficient for row-wise access.

All three options must satisfy the same interface.

Author: [Hamza Mughal]
Date:   [4/10/2026]
Lab:    Lab 6 - Sparse World Map
"""


# =============================================================================
# Do not modify SparseMatrixBase.
# =============================================================================

class SparseMatrixBase:
    """Interface definition. Your SparseMatrix must inherit from this."""

    def __init__(self, rows=None, cols=None, default=0):
        self.rows    = rows
        self.cols    = cols
        self.default = default

    def set(self, row, col, value):
        raise NotImplementedError

    def get(self, row, col):
        raise NotImplementedError

    def items(self):
        raise NotImplementedError

    def __len__(self):
        raise NotImplementedError

    def multiply(self, other):
        raise NotImplementedError

    def __str__(self):
        raise NotImplementedError


# =============================================================================
# Your implementation goes here. OPTION B
# =============================================================================

class SparseMatrix(SparseMatrixBase):
    """
    COO sparse matrix: stores only non-default entries as
    (row, col, value) triples in an ArrayList.
    """

    def __init__(self, rows=None, cols=None, default=0):
        super().__init__(rows, cols, default)
        # ArrayList of (row, col, value) tuples
        self._entries = ArrayList()

    def _find(self, row, col):
        """Return index of (row, col) entry in _entries, or -1 if not found."""
        for i in range(len(self._entries)):
            r, c, _ = self._entries[i]
            if r == row and c == col:
                return i
        return -1

    def set(self, row, col, value):
        """
        Store value at (row, col).
        If value == default, remove the entry to keep the matrix sparse.
        """
        idx = self._find(row, col)
        if value == self.default:
            # Remove entry if it exists
            if idx != -1:
                self._entries.pop(idx)
        else:
            if idx != -1:
                # Update existing entry
                self._entries[idx] = (row, col, value)
            else:
                # Add new entry
                self._entries.append((row, col, value))

    def get(self, row, col):
        """Return stored value at (row, col), or default if not stored."""
        idx = self._find(row, col)
        if idx == -1:
            return self.default
        _, _, value = self._entries[idx]
        return value

    def items(self):
        """Yield ((row, col), value) tuples for all stored entries."""
        for i in range(len(self._entries)):
            r, c, v = self._entries[i]
            yield (r, c), v

    def __len__(self):
        """Return number of stored (non-default) entries."""
        return len(self._entries)

    def multiply(self, other):
        """
        Return a new SparseMatrix = self * other.
        Standard matrix multiplication: result[i][j] = sum(self[i][k] * other[k][j])
        Only iterates over non-default entries for efficiency.
        """
        result = SparseMatrix(
            rows=self.rows,
            cols=other.cols,
            default=self.default
        )

        # For each non-zero in self, combine with non-zeros in other
        for i in range(len(self._entries)):
            r, k, v1 = self._entries[i]
            for j in range(len(other._entries)):
                kr, c, v2 = other._entries[j]
                if k == kr:
                    current = result.get(r, c)
                    result.set(r, c, current + v1 * v2)

        return result

    def __str__(self):
        """Human-readable summary of the sparse matrix."""
        return (f"SparseMatrix(rows={self.rows}, cols={self.cols}, "
                f"default={self.default}, nnz={len(self)})")
