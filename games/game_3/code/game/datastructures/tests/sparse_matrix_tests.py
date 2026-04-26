"""
sparse_matrix_tests.py - Tests for SparseMatrix

Write tests for ALL methods of your SparseMatrix implementation.
You may use AI to help generate edge cases, but make sure you understand
every test before submitting.

Run with:
    cd code/game/datastructures/tests
    python sparse_matrix_tests.py

Author: [Your Name]
Date:   [Date]
Lab:    Lab 6 - Sparse World Map
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from datastructures.sparse_matrix import SparseMatrix
from scipy.sparse import csr_matrix


def test_set_and_get():
    """set() stores a value and get() retrieves it."""
    m = SparseMatrix(default=-1)
    m.set(0, 0, 5)
    assert m.get(0, 0) == 5
    print("PASS test_set_and_get")
 
def test_default_value():
    """get() returns default for entries never set."""
    m = SparseMatrix(default=-1)
    assert m.get(10, 10) == -1
    print("PASS test_default_value")
 
def test_custom_default():
    """default value can be set to something other than -1."""
    m = SparseMatrix(default=0)
    assert m.get(5, 5) == 0
    print("PASS test_custom_default")
 
def test_len_empty():
    """Empty matrix has length 0."""
    m = SparseMatrix(default=-1)
    assert len(m) == 0
    print("PASS test_len_empty")
 
def test_len_after_set():
    """len() grows as entries are added."""
    m = SparseMatrix(default=-1)
    m.set(0, 0, 1)
    m.set(1, 1, 2)
    m.set(2, 2, 3)
    assert len(m) == 3
    print("PASS test_len_after_set")
 
def test_items():
    """items() should yield exactly the non-default entries."""
    m = SparseMatrix(default=-1)
    m.set(0, 1, 10)
    m.set(2, 3, 20)
    found = {pos: val for pos, val in m.items()}
    assert (0, 1) in found and found[(0, 1)] == 10
    assert (2, 3) in found and found[(2, 3)] == 20
    assert len(found) == 2
    print("PASS test_items")
 
def test_overwrite():
    """Setting a position twice keeps only the latest value."""
    m = SparseMatrix(default=-1)
    m.set(1, 1, 99)
    m.set(1, 1, 42)
    assert m.get(1, 1) == 42
    assert len(m) == 1
    print("PASS test_overwrite")
 
def test_set_to_default_removes_entry():
    """set(r, c, default) should remove the entry so len() decreases."""
    m = SparseMatrix(default=-1)
    m.set(3, 3, 7)
    m.set(3, 3, -1)
    assert len(m) == 0
    assert m.get(3, 3) == -1
    print("PASS test_set_to_default_removes_entry")
 
def test_large_sparse():
    """A 1000x1000 matrix with 10 entries should use minimal memory."""
    m = SparseMatrix(rows=1000, cols=1000, default=-1)
    entries = [(100, 200, 1), (500, 500, 2), (999, 999, 3),
               (0, 0, 4), (1, 999, 5), (999, 0, 6),
               (250, 750, 7), (333, 333, 8), (600, 100, 9), (700, 800, 10)]
    for r, c, v in entries:
        m.set(r, c, v)
    assert len(m) == 10
    for r, c, v in entries:
        assert m.get(r, c) == v
    assert m.get(400, 400) == -1
    print("PASS test_large_sparse")
 
def test_items_consistent_with_get():
    """Every (r, c) yielded by items() should match get(r, c)."""
    m = SparseMatrix(default=-1)
    m.set(0, 0, 5)
    m.set(1, 2, 8)
    m.set(3, 3, 12)
    for (r, c), v in m.items():
        assert m.get(r, c) == v
    print("PASS test_items_consistent_with_get")
 
def test_multiply_identity():
    """A * I == A for a 2x2 identity matrix."""
    a = SparseMatrix(default=0)
    a.set(0, 0, 2)
    a.set(1, 1, 3)
    identity = SparseMatrix(default=0)
    identity.set(0, 0, 1)
    identity.set(1, 1, 1)
    result = a.multiply(identity)
    assert result.get(0, 0) == 2
    assert result.get(1, 1) == 3
    assert result.get(0, 1) == 0
    print("PASS test_multiply_identity")
 
def test_multiply_basic():
    """Hand-computed 2x2 example."""
    a = SparseMatrix(default=0)
    a.set(0, 0, 1); a.set(0, 1, 2)
    a.set(1, 0, 3); a.set(1, 1, 4)
    b = SparseMatrix(default=0)
    b.set(0, 0, 5); b.set(0, 1, 6)
    b.set(1, 0, 7); b.set(1, 1, 8)
    # Expected: [[19, 22], [43, 50]]
    result = a.multiply(b)
    assert result.get(0, 0) == 19
    assert result.get(0, 1) == 22
    assert result.get(1, 0) == 43
    assert result.get(1, 1) == 50
    print("PASS test_multiply_basic")
 
def test_multiply_zero():
    """A * Z == all-zeros (empty sparse matrix)."""
    a = SparseMatrix(default=0)
    a.set(0, 0, 5)
    a.set(1, 1, 10)
    zero = SparseMatrix(default=0)
    result = a.multiply(zero)
    assert len(result) == 0
    assert result.get(0, 0) == 0
    print("PASS test_multiply_zero")
 
def test_str():
    """__str__ should return a non-empty string."""
    m = SparseMatrix(rows=5, cols=5, default=-1)
    m.set(0, 0, 1)
    m.set(4, 4, 9)
    s = str(m)
    assert len(s) > 0
    assert "SparseMatrix" in s
    print("PASS test_str")
 
# ==========================================================================
 
if __name__ == '__main__':
    test_set_and_get()
    test_default_value()
    test_custom_default()
    test_len_empty()
    test_len_after_set()
    test_items()
    test_overwrite()
    test_set_to_default_removes_entry()
    test_large_sparse()
    test_items_consistent_with_get()
    test_multiply_identity()
    test_multiply_basic()
    test_multiply_zero()
    test_str()
    print("All tests passed!")
