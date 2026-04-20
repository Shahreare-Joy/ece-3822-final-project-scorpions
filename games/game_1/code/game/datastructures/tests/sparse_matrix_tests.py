"""
sparse_matrix_tests.py - Tests for SparseMatrix

Write tests for ALL methods of your SparseMatrix implementation.
You may use AI to help generate edge cases, but make sure you understand
every test before submitting.

Run with:
    cd code/game/datastructures/tests
    python sparse_matrix_tests.py

Author: Shahreare Joy
Date:   04/12/2026
Lab:    Lab 6 - Sparse World Map
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from datastructures.sparse_matrix import SparseMatrix
#from scipy.sparse import csr_matrix


# ==========================================================================
# TODID: Write your tests below
#
# Suggested test ideas (each as a separate function):
#
def test_set_and_get():
    m = SparseMatrix(rows=3, cols=3, default=0)
    m.set(1, 2, 5)
    assert m.get(1, 2) == 5

def test_default_value():
    m = SparseMatrix(rows=3, cols=3, default=0)
    assert m.get(0, 0) == 0

def test_custom_default():
    m = SparseMatrix(rows=3, cols=3, default=-1)
    assert m.get(2, 2) == -1

def test_len_empty():
    m = SparseMatrix(rows=4, cols=4, default=0)
    assert len(m) == 0

def test_len_after_set():
    m = SparseMatrix(rows=4, cols=4, default=0)
    m.set(0, 1, 8)
    assert len(m) == 1

def test_items():
    """items() should yield exactly the non-default entries."""
    m = SparseMatrix(rows=4, cols=4, default=0)
    m.set(0, 1, 10)
    m.set(2, 3, 20)

    items = list(m.items())

    assert ((0, 1), 10) in items
    assert ((2, 3), 20) in items
    assert len(items) == 2

def test_overwrite():
    """Setting a position twice keeps only the latest value."""
    m = SparseMatrix(rows=3, cols=3, default=0)
    m.set(1, 1, 5)
    m.set(1, 1, 9)

    assert m.get(1, 1) == 9
    assert len(m) == 1

def test_set_to_default_removes_entry():
    """set(r, c, default) should remove the entry so len() decreases."""
    m = SparseMatrix(rows=3, cols=3, default=-1)
    m.set(0, 2, 7)
    assert len(m) == 1

    m.set(0, 2, -1)
    assert m.get(0, 2) == -1
    assert len(m) == 0

def test_large_sparse():
    """A 1000x1000 matrix with 10 entries should use minimal memory."""
    m = SparseMatrix(rows=1000, cols=1000, default=0)

    values = [
        (0, 0, 1),
        (10, 20, 2),
        (50, 50, 3),
        (99, 100, 4),
        (123, 456, 5),
        (250, 300, 6),
        (400, 700, 7),
        (600, 600, 8),
        (800, 900, 9),
        (999, 999, 10),
    ]
    for r, c, v in values:
        m.set(r, c, v)

    assert len(m) == 10

    for r, c, v in values:
        assert m.get(r, c) == v

    assert m.get(500, 500) == 0

def test_items_consistent_with_get():
    """Every (r, c) yielded by items() should match get(r, c)."""
    m = SparseMatrix(rows=5, cols=5, default=0)
    m.set(0, 0, 3)
    m.set(1, 2, 7)
    m.set(4, 4, 9)

    for (r, c), value in m.items():
        assert m.get(r, c) == value

def test_multiply_identity():
    """A * I == A  for a 2x2 identity matrix."""
    a = SparseMatrix(rows=2, cols=2, default=0)
    identity = SparseMatrix(rows=2, cols=2, default=0)

    a.set(0, 0, 4)
    a.set(0, 1, 7)
    a.set(1, 0, 2)
    a.set(1, 1, 6)

    identity.set(0, 0, 1)
    identity.set(1, 1, 1)

    result = a.multiply(identity)

    assert result.get(0, 0) == 4
    assert result.get(0, 1) == 7
    assert result.get(1, 0) == 2
    assert result.get(1, 1) == 6

def test_multiply_basic():
    """Hand-computed 2x2 example."""
    a = SparseMatrix(rows=2, cols=2, default=0)
    b = SparseMatrix(rows=2, cols=2, default=0)

    a.set(0, 0, 1)
    a.set(0, 1, 2)
    a.set(1, 0, 3)
    a.set(1, 1, 4)

    b.set(0, 0, 5)
    b.set(0, 1, 6)
    b.set(1, 0, 7)
    b.set(1, 1, 8)

    result = a.multiply(b)

    assert result.get(0, 0) == 19
    assert result.get(0, 1) == 22
    assert result.get(1, 0) == 43
    assert result.get(1, 1) == 50

def test_multiply_zero():
    """A * Z == all-zeros (empty sparse matrix)."""
    a = SparseMatrix(rows=2, cols=2, default=0)
    z = SparseMatrix(rows=2, cols=2, default=0)

    a.set(0, 0, 3)
    a.set(0, 1, 5)
    a.set(1, 0, 7)
    a.set(1, 1, 9)

    result = a.multiply(z)

    assert len(result) == 0
    assert result.get(0, 0) == 0
    assert result.get(0, 1) == 0
    assert result.get(1, 0) == 0
    assert result.get(1, 1) == 0

def test_str():
    """__str__ should return a non-empty string."""
    m = SparseMatrix(rows=5, cols=6, default=0)
    m.set(1, 2, 8)

    s = str(m)

    assert isinstance(s, str)
    assert len(s) > 0
# ==========================================================================


if __name__ == '__main__':
    # TODID: call your tests here
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
