"""
sparse_matrix.py - Sparse Matrix implementation

A sparse matrix stores only non-default entries, saving memory when most
cells share the same value (like -1 in a tile map).

Choose one of three backing representations:

  Option A — DOK (Dictionary of Keys): {(row, col): value}
    Requires implementing HashTable in hash_table.py.
    Do not use Python's built-in dict or set.

Choose:  Option B — COO (Coordinate List): list of (row, col, value) triples
    Use your ArrayList from Lab 3. Do not use Python's built-in list.

  Option C — CSR (Compressed Sparse Row): three parallel arrays
    row_ptr, col_idx, values. Most efficient for row-wise access.

All three options must satisfy the same interface.

Author: Shahreare Joy
Date:   04/12/2026
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

    def __init__(self, rows=None, cols=None, default=0):
        super().__init__(rows, cols, default)
        # TODID: initialize your backing data structure
        self.entries = ArrayList()

    def set(self, row, col, value):
        """
        Set the value at (row, col). Remove entry if value equals default.
        """
        # TODID
        found = False

        # search for existing entry
        for i in range(len(self.entries)):
            r, c, v = self.entries[i]

            if r == row and c == col:
                found = True

                if value == self.default:
                    # remove by shifting left
                    for j in range(i, len(self.entries) - 1):
                        self.entries[j] = self.entries[j + 1]

                    # reduce size manually
                    self.entries._size -= 1
                else:
                    self.entries[i] = (row, col, value)

                break
        
        # if not found, add new entry
        if not found and value != self.default:
            self.entries.append((row, col, value))

    def get(self, row, col):
        """
        Return the value at (row, col), or the default if not stored.
        """
        # TODID
        for i in range(len(self.entries)):
            r, c, v = self.entries[i]
            if r == row and c == col:
                return v
        return self.default

    def items(self):
        """
        Yield ((row, col), value) pairs for all stored entries.
        """
        # TODID
        for i in range(len(self.entries)):
            r, c, v = self.entries[i]
            yield ((r, c), v)

    def __len__(self):
        """
        Return the number of stored non-default entries.
        """
        # TODID
        return len(self.entries)

    def multiply(self, other):
        """
        Return a new SparseMatrix equal to self * other.
        """
        # TODID
        result = SparseMatrix(self.rows, other.cols, self.default)

        for i in range(len(self.entries)):
            r1, c1, v1 = self.entries[i]

            for j in range(len(other.entries)):
                r2, c2, v2 = other.entries[j]

                if c1 == r2:
                    current = result.get(r1, c2)
                    result.set(r1, c2, current + v1 * v2)

        return result

    def __str__(self):
        """
        Return a human-readable string summary of the matrix.
        """
        # TODID
        return f"SparseMatrix({self.rows}x{self.cols}, stored={len(self)})"
