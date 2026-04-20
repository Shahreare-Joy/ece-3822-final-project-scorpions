"""
sparse_matrix_complexity.py - Performance analysis for SparseMatrix

Compare your SparseMatrix implementation to:
  - scipy.sparse (CSR format)
  - numpy dense matrix (numpy.ndarray)

Measure and report wall-clock time for:
  1. Building the matrix (set() calls)
  2. Random get() accesses
  3. items() full iteration
  4. multiply()

Run with:
    cd code/game/datastructures/complexity
    python sparse_matrix_complexity.py

Install dependencies if needed:
    pip install scipy numpy

Author: Shahreare Joy
Date:   04/12/2026
Lab:    Lab 6 - Sparse World Map
"""

import time
import random
import sys
import os

try:
    from scipy.sparse import csr_matrix
    import numpy as np
    SCIPY_NUMPY_AVAILABLE = True
except ImportError:
    SCIPY_NUMPY_AVAILABLE = False

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from datastructures.sparse_matrix import SparseMatrix


def generate_positions(rows, cols, count):
    """Generate unique random (row, col) positions."""
    positions = set()
    while len(positions) < count:
        r = random.randint(0, rows - 1)
        c = random.randint(0, cols - 1)
        positions.add((r, c))
    return list(positions)


def benchmark_sparsematrix_build(rows, cols, positions):
    """Measure build time for custom SparseMatrix."""
    start = time.perf_counter()

    m = SparseMatrix(rows=rows, cols=cols, default=0)
    for i, (r, c) in enumerate(positions):
        m.set(r, c, i + 1)

    end = time.perf_counter()
    return m, end - start


def benchmark_sparsematrix_get(matrix, positions):
    """Measure random get() time for custom SparseMatrix."""
    start = time.perf_counter()

    for r, c in positions:
        matrix.get(r, c)

    end = time.perf_counter()
    return end - start


def benchmark_sparsematrix_items(matrix):
    """Measure full iteration time for custom SparseMatrix."""
    start = time.perf_counter()

    for _ in matrix.items():
        pass

    end = time.perf_counter()
    return end - start


def benchmark_sparsematrix_multiply(size, num_entries):
    """Measure multiply() time for custom SparseMatrix."""
    a = SparseMatrix(rows=size, cols=size, default=0)
    b = SparseMatrix(rows=size, cols=size, default=0)

    positions_a = generate_positions(size, size, num_entries)
    positions_b = generate_positions(size, size, num_entries)

    for i, (r, c) in enumerate(positions_a):
        a.set(r, c, (i % 9) + 1)

    for i, (r, c) in enumerate(positions_b):
        b.set(r, c, (i % 9) + 1)

    start = time.perf_counter()
    _ = a.multiply(b)
    end = time.perf_counter()

    return end - start


def benchmark_numpy_build(rows, cols, positions):
    """Measure build time for numpy dense array."""
    if not SCIPY_NUMPY_AVAILABLE:
        return None, None

    start = time.perf_counter()

    arr = np.zeros((rows, cols), dtype=int)
    for i, (r, c) in enumerate(positions):
        arr[r, c] = i + 1

    end = time.perf_counter()
    return arr, end - start


def benchmark_numpy_get(arr, positions):
    """Measure random access time for numpy dense array."""
    if not SCIPY_NUMPY_AVAILABLE:
        return None

    start = time.perf_counter()

    for r, c in positions:
        _ = arr[r, c]

    end = time.perf_counter()
    return end - start


def benchmark_numpy_items(arr):
    """Measure full iteration over nonzero entries in numpy dense array."""
    if not SCIPY_NUMPY_AVAILABLE:
        return None

    start = time.perf_counter()

    rows, cols = arr.shape
    for r in range(rows):
        for c in range(cols):
            if arr[r, c] != 0:
                pass

    end = time.perf_counter()
    return end - start


def benchmark_numpy_multiply(size, num_entries):
    """Measure matrix multiply for numpy dense array."""
    if not SCIPY_NUMPY_AVAILABLE:
        return None

    a = np.zeros((size, size), dtype=int)
    b = np.zeros((size, size), dtype=int)

    positions_a = generate_positions(size, size, num_entries)
    positions_b = generate_positions(size, size, num_entries)

    for i, (r, c) in enumerate(positions_a):
        a[r, c] = (i % 9) + 1

    for i, (r, c) in enumerate(positions_b):
        b[r, c] = (i % 9) + 1

    start = time.perf_counter()
    _ = a @ b
    end = time.perf_counter()

    return end - start


def benchmark_csr_build(rows, cols, positions):
    """Measure build time for scipy csr_matrix."""
    if not SCIPY_NUMPY_AVAILABLE:
        return None, None

    start = time.perf_counter()

    data = []
    row_ind = []
    col_ind = []

    for i, (r, c) in enumerate(positions):
        data.append(i + 1)
        row_ind.append(r)
        col_ind.append(c)

    mat = csr_matrix((data, (row_ind, col_ind)), shape=(rows, cols))

    end = time.perf_counter()
    return mat, end - start


def benchmark_csr_get(mat, positions):
    """Measure random access time for scipy csr_matrix."""
    if not SCIPY_NUMPY_AVAILABLE:
        return None

    start = time.perf_counter()

    for r, c in positions:
        _ = mat[r, c]

    end = time.perf_counter()
    return end - start


def benchmark_csr_items(mat):
    """Measure iteration over stored entries in csr_matrix."""
    if not SCIPY_NUMPY_AVAILABLE:
        return None

    start = time.perf_counter()

    coo = mat.tocoo()
    for _ in zip(coo.row, coo.col, coo.data):
        pass

    end = time.perf_counter()
    return end - start


def benchmark_csr_multiply(size, num_entries):
    """Measure matrix multiply for scipy csr_matrix."""
    if not SCIPY_NUMPY_AVAILABLE:
        return None

    positions_a = generate_positions(size, size, num_entries)
    positions_b = generate_positions(size, size, num_entries)

    data_a, rows_a, cols_a = [], [], []
    data_b, rows_b, cols_b = [], [], []

    for i, (r, c) in enumerate(positions_a):
        data_a.append((i % 9) + 1)
        rows_a.append(r)
        cols_a.append(c)

    for i, (r, c) in enumerate(positions_b):
        data_b.append((i % 9) + 1)
        rows_b.append(r)
        cols_b.append(c)

    a = csr_matrix((data_a, (rows_a, cols_a)), shape=(size, size))
    b = csr_matrix((data_b, (rows_b, cols_b)), shape=(size, size))

    start = time.perf_counter()
    _ = a @ b
    end = time.perf_counter()

    return end - start


def print_result(label, value):
    """Print a formatted benchmark result."""
    if value is None:
        print(f"{label:<30} skipped")
    else:
        print(f"{label:<30} {value:.6f} sec")


def main():
    random.seed(42)

    rows = 1000
    cols = 1000
    num_entries = 200
    get_samples = 100
    mult_size = 100
    mult_entries = 100

    print("Sparse Matrix Complexity Analysis")
    print("=" * 50)
    print(f"Matrix size: {rows} x {cols}")
    print(f"Stored entries: {num_entries}")
    print()

    positions = generate_positions(rows, cols, num_entries)
    sample_positions = positions[:get_samples]

    print("1. Building the matrix")
    sm, sm_build = benchmark_sparsematrix_build(rows, cols, positions)
    np_mat, np_build = benchmark_numpy_build(rows, cols, positions)
    csr_mat, csr_build = benchmark_csr_build(rows, cols, positions)

    print_result("SparseMatrix build", sm_build)
    print_result("NumPy build", np_build)
    print_result("SciPy CSR build", csr_build)
    print()

    print("2. Random get() accesses")
    sm_get = benchmark_sparsematrix_get(sm, sample_positions)
    np_get = benchmark_numpy_get(np_mat, sample_positions)
    csr_get = benchmark_csr_get(csr_mat, sample_positions)

    print_result("SparseMatrix get", sm_get)
    print_result("NumPy get", np_get)
    print_result("SciPy CSR get", csr_get)
    print()

    print("3. items() full iteration")
    sm_items = benchmark_sparsematrix_items(sm)
    np_items = benchmark_numpy_items(np_mat)
    csr_items = benchmark_csr_items(csr_mat)

    print_result("SparseMatrix items", sm_items)
    print_result("NumPy items", np_items)
    print_result("SciPy CSR items", csr_items)
    print()

    print("4. multiply()")
    sm_mult = benchmark_sparsematrix_multiply(mult_size, mult_entries)
    np_mult = benchmark_numpy_multiply(mult_size, mult_entries)
    csr_mult = benchmark_csr_multiply(mult_size, mult_entries)

    print_result("SparseMatrix multiply", sm_mult)
    print_result("NumPy multiply", np_mult)
    print_result("SciPy CSR multiply", csr_mult)
    print()

    if not SCIPY_NUMPY_AVAILABLE:
        print("Note: NumPy/SciPy not installed, so comparison benchmarks were skipped.")


if __name__ == "__main__":
    main()