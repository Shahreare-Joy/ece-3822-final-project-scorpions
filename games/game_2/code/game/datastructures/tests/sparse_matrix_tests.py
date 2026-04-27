"""
sparse_matrix_tests.py - Tests for SparseMatrix

Author: Hamza Mughal
Date:   4/10/2026
Lab:    Lab 6 - Sparse World Map
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from datastructures.sparse_matrix import SparseMatrix

passed = 0
failed = 0

def check(test_name, condition):
    global passed, failed
    if condition:
        print(f"  PASS: {test_name}")
        passed += 1
    else:
        print(f"  FAIL: {test_name}")
        failed += 1


def test_default_value():
    """get on empty matrix returns default"""
    m = SparseMatrix(rows=10, cols=10, default=0)
    check("get on empty returns 0", m.get(0, 0) == 0)
    check("get anywhere returns default", m.get(5, 7) == 0)


def test_len_empty():
    """Empty matrix has length 0"""
    m = SparseMatrix(rows=10, cols=10, default=0)
    check("len of empty is 0", len(m) == 0)


def test_set_and_get():
    """set stores a value; get retrieves it"""
    m = SparseMatrix(rows=5, cols=5, default=0)
    m.set(1, 2, 42)
    check("get stored value", m.get(1, 2) == 42)
    check("get unstored cell returns default", m.get(0, 0) == 0)


def test_len_after_set():
    """len increases with each new entry"""
    m = SparseMatrix(default=0)
    m.set(0, 0, 1)
    check("len is 1 after one set", len(m) == 1)
    m.set(1, 1, 2)
    check("len is 2 after two sets", len(m) == 2)


def test_overwrite():
    """Setting a position twice keeps only the latest value"""
    m = SparseMatrix(default=0)
    m.set(3, 3, 10)
    m.set(3, 3, 99)
    check("overwrite updates value", m.get(3, 3) == 99)
    check("len still 1 after overwrite", len(m) == 1)


def test_set_to_default_removes_entry():
    """set(r, c, default) should remove the entry so len() decreases"""
    m = SparseMatrix(default=0)
    m.set(2, 2, 7)
    check("entry exists before removal", len(m) == 1)
    m.set(2, 2, 0)
    check("entry removed after set to default", len(m) == 0)
    check("get returns default after removal", m.get(2, 2) == 0)


def test_custom_default():
    """Non-zero default value works correctly"""
    m = SparseMatrix(default=-1)
    check("unstored returns -1", m.get(0, 0) == -1)
    m.set(0, 0, 5)
    check("stored value returns 5", m.get(0, 0) == 5)
    m.set(0, 0, -1)
    check("set to -1 removes entry", len(m) == 0)


def test_items():
    """items() should yield exactly the non-default entries"""
    m = SparseMatrix(default=0)
    m.set(0, 0, 1)
    m.set(1, 1, 2)
    m.set(2, 2, 3)
    all_items = list(m.items())
    check("items returns 3 entries", len(all_items) == 3)
    coords = [pos for pos, val in all_items]
    check("(0,0) in items", (0, 0) in coords)
    check("(1,1) in items", (1, 1) in coords)
    check("(2,2) in items", (2, 2) in coords)


def test_items_empty():
    """items() on empty matrix yields nothing"""
    m = SparseMatrix(default=0)
    check("items on empty yields nothing", list(m.items()) == [])


def test_items_consistent_with_get():
    """Every (r, c) yielded by items() should match get(r, c)"""
    m = SparseMatrix(default=0)
    m.set(0, 1, 10)
    m.set(3, 4, 20)
    m.set(7, 7, 30)
    for (r, c), v in m.items():
        check(f"items consistent with get at ({r},{c})", m.get(r, c) == v)


def test_str():
    """__str__ should return a non-empty string with key info"""
    m = SparseMatrix(rows=4, cols=4, default=0)
    m.set(0, 1, 9)
    s = str(m)
    check("str contains 'SparseMatrix'", "SparseMatrix" in s)
    check("str contains nnz=1", "nnz=1" in s)


def test_large_sparse():
    """A 1000x1000 matrix with 10 entries should work correctly"""
    m = SparseMatrix(rows=1000, cols=1000, default=0)
    entries = [(0,0,1),(100,200,2),(500,500,3),(999,999,4),
               (123,456,5),(321,654,6),(0,999,7),(999,0,8),
               (250,750,9),(750,250,10)]
    for r, c, v in entries:
        m.set(r, c, v)
    check("large matrix len is 10", len(m) == 10)
    check("large matrix get(500,500)==3", m.get(500, 500) == 3)
    check("large matrix get(999,999)==4", m.get(999, 999) == 4)
    check("large matrix unstored returns 0", m.get(1, 1) == 0)


def test_multiply_identity():
    """A * I == A for a 2x2 identity matrix"""
    I = SparseMatrix(rows=2, cols=2, default=0)
    I.set(0, 0, 1)
    I.set(1, 1, 1)

    A = SparseMatrix(rows=2, cols=2, default=0)
    A.set(0, 0, 3); A.set(0, 1, 4)
    A.set(1, 0, 5); A.set(1, 1, 6)

    result = A.multiply(I)
    check("A*I (0,0)==3", result.get(0, 0) == 3)
    check("A*I (0,1)==4", result.get(0, 1) == 4)
    check("A*I (1,0)==5", result.get(1, 0) == 5)
    check("A*I (1,1)==6", result.get(1, 1) == 6)


def test_multiply_zero():
    """A * Z == all-zeros (empty sparse matrix)"""
    A = SparseMatrix(rows=2, cols=2, default=0)
    A.set(0, 0, 3); A.set(0, 1, 4)
    A.set(1, 0, 5); A.set(1, 1, 6)

    Z = SparseMatrix(rows=2, cols=2, default=0)
    result = A.multiply(Z)
    check("A*Z (0,0)==0", result.get(0, 0) == 0)
    check("A*Z (1,1)==0", result.get(1, 1) == 0)
    check("A*Z len==0", len(result) == 0)


def test_multiply_basic():
    """Hand-computed 2x2: [[1,2],[3,4]] * [[5,6],[7,8]] = [[19,22],[43,50]]"""
    A = SparseMatrix(rows=2, cols=2, default=0)
    A.set(0, 0, 1); A.set(0, 1, 2)
    A.set(1, 0, 3); A.set(1, 1, 4)

    B = SparseMatrix(rows=2, cols=2, default=0)
    B.set(0, 0, 5); B.set(0, 1, 6)
    B.set(1, 0, 7); B.set(1, 1, 8)

    C = A.multiply(B)
    check("A*B (0,0)==19", C.get(0, 0) == 19)
    check("A*B (0,1)==22", C.get(0, 1) == 22)
    check("A*B (1,0)==43", C.get(1, 0) == 43)
    check("A*B (1,1)==50", C.get(1, 1) == 50)


def test_multiple_sets_and_removals():
    """Multiple sets then removals update len correctly"""
    m = SparseMatrix(default=0)
    for i in range(10):
        m.set(i, i, i + 1)
    check("len is 10 after 10 sets", len(m) == 10)
    for i in range(5):
        m.set(i, i, 0)
    check("len is 5 after 5 removals", len(m) == 5)
    check("removed entry returns default", m.get(0, 0) == 0)
    check("kept entry still correct", m.get(9, 9) == 10)


if __name__ == '__main__':
    print("=" * 50)
    print("SparseMatrix Tests")
    print("=" * 50)

    test_default_value()
    test_len_empty()
    test_set_and_get()
    test_len_after_set()
    test_overwrite()
    test_set_to_default_removes_entry()
    test_custom_default()
    test_items()
    test_items_empty()
    test_items_consistent_with_get()
    test_str()
    test_large_sparse()
    test_multiply_identity()
    test_multiply_zero()
    test_multiply_basic()
    test_multiple_sets_and_removals()

    print("\n" + "=" * 50)
    print(f"Results: {passed} passed, {failed} failed out of {passed+failed} tests")
    print("=" * 50)
    if failed == 0:
        print("All tests passed!")
    else:
        print("Some tests failed - check output above.")
