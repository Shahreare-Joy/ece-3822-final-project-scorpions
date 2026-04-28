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

Author: Kevin Le
Date:   4/12/2026
Lab:    Lab 6 - Sparse World Map
"""
from .arraylist import ArrayList

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

class MatrixEntry:
    def __init__(self, row, col, value):
        self.row = row
        self.col = col
        self.value = value


class SparseMatrix(SparseMatrixBase):

    def __init__(self, rows=None, cols=None, default=0):
        super().__init__(rows, cols, default)
        # TODO: initialize your backing data structure
        self.data = ArrayList()

    def set(self, row, col, value):
        found_index = -1
        for i in range(len(self.data)):
            entry = self.data[i] # Uses your __getitem__
            if entry.row == row and entry.col == col:
                found_index = i
                break

        if found_index != -1:
            if value == self.default:
                # Use your pop() method to remove and shift elements
                self.data.pop(found_index)
            else:
                # Update the value of the entry object directly
                self.data[found_index].value = value
        elif value != self.default:
            # Use your append() method
            self.data.append(MatrixEntry(row, col, value))

    def get(self, row, col):
        for entry in self.data:
            if entry.row == row and entry.col == col:
                return entry.value
        return self.default

    def items(self):
        for entry in self.data:
            yield (entry.row, entry.col, entry.value)

    def __len__(self):
        return len(self.data)

    def multiply(self, other):
        result = SparseMatrix(rows=self.rows, cols=other.cols, default=self.default)

        # Standard COO Multiplication algorithm
        for a_entry in self.data:
            for b_entry in other.data:
                if a_entry.col == b_entry.row:
                    # Get existing value or 0 if empty
                    current = result.get(a_entry.row, b_entry.col)
                    base = 0 if current == self.default else current
                    
                    product = a_entry.value * b_entry.value
                    result.set(a_entry.row, b_entry.col, base + product)
        return result

    def __str__(self):
        return f"SparseMatrix(rows={self.rows}, cols={self.cols}, default={self.default}, entries={len(self.data)})"