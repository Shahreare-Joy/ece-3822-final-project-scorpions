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

Author: [Mykai Wade]
Date:   [4/12/26]
Lab:    Lab 6 - Sparse World Map
"""

from datastructures.array import ArrayList

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
# Your implementation goes here.
# =============================================================================

class SparseMatrix(SparseMatrixBase):
    """COO sparse matrix backed by an ArrayList of (row, col, value) tuples."""
 
    def __init__(self, rows=None, cols=None, default=0):
        """Initialize empty matrix with given dimensions and default value."""
        super().__init__(rows, cols, default)
        self._data = ArrayList()
 
    def _find_index(self, row, col):
        """Return index of (row, col) in _data, or -1 if not found."""
        for i in range(len(self._data)):
            r, c, _ = self._data[i]
            if r == row and c == col:
                return i
        return -1
 
    def set(self, row, col, value):
        """Store value at (row, col). Removes entry if value == default."""
        idx = self._find_index(row, col)
        if value == self.default:
            if idx != -1:
                self._data.pop(idx)
        else:
            if idx != -1:
                self._data[idx] = (row, col, value)
            else:
                self._data.append((row, col, value))
 
    def get(self, row, col):
        """Return value at (row, col), or self.default if not found."""
        idx = self._find_index(row, col)
        if idx != -1:
            _, _, value = self._data[idx]
            return value
        return self.default
 
    def items(self):
        """Yield ((row, col), value) for each stored entry."""
        for i in range(len(self._data)):
            r, c, v = self._data[i]
            yield (r, c), v
 
    def __len__(self):
        """Return number of stored (non-default) entries."""
        return len(self._data)
 
    def multiply(self, other):
        """Return a new SparseMatrix equal to self * other."""
        result = SparseMatrix(default=self.default)
        for (i, k), v_self in self.items():
            for (k2, j), v_other in other.items():
                if k == k2:
                    current = result.get(i, j)
                    if current == result.default:
                        current = 0
                    result.set(i, j, current + v_self * v_other)
        return result
 
    def __str__(self):
        """Return a readable summary of the matrix and its stored entries."""
        rows_str = str(self.rows) if self.rows is not None else "?"
        cols_str = str(self.cols) if self.cols is not None else "?"
        lines = [f"SparseMatrix({rows_str}x{cols_str}, default={self.default}, nnz={len(self)})"]
        for (r, c), v in self.items():
            lines.append(f"  ({r}, {c}) -> {v}")
        return "\n".join(lines)
 
# end of file
