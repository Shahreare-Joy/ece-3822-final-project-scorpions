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

Author: Hamza Mughal
Date:   4/11/2026
Lab:    Lab 6 - Sparse World Map
"""

import time
import random
import sys
import os

try:
    from scipy.sparse import csr_matrix, lil_matrix
    import numpy as np
    HAS_SCIPY = True
except ImportError:
    print("scipy/numpy not installed — run: pip install scipy numpy")
    HAS_SCIPY = False

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from datastructures.sparse_matrix import SparseMatrix

# --------------------------------------------------
# Configuration
# --------------------------------------------------
MATRIX_SIZE   = 500      # N x N matrix
NUM_ENTRIES   = 1000     # non-zero entries to insert
NUM_GETS      = 1000     # random get() accesses
RANDOM_SEED   = 42

random.seed(RANDOM_SEED)

def random_coords(n, count):
    """Generate `count` unique (row, col) pairs in an n x n matrix."""
    coords = set()
    while len(coords) < count:
        coords.add((random.randint(0, n-1), random.randint(0, n-1)))
    return list(coords)

def benchmark(label, fn):
    """Time a zero-argument callable and print the result."""
    start = time.perf_counter()
    result = fn()
    elapsed = time.perf_counter() - start
    print(f"  {label:<40} {elapsed*1000:.4f} ms")
    return result

# --------------------------------------------------
# Generate test data
# --------------------------------------------------
print("=" * 60)
print("SparseMatrix Complexity Analysis")
print(f"Matrix size: {MATRIX_SIZE} x {MATRIX_SIZE}, "
      f"Non-zeros: {NUM_ENTRIES}, Gets: {NUM_GETS}")
print("=" * 60)

insert_coords = random_coords(MATRIX_SIZE, NUM_ENTRIES)
insert_values = [random.randint(1, 100) for _ in range(NUM_ENTRIES)]
get_coords    = [(random.randint(0, MATRIX_SIZE-1),
                  random.randint(0, MATRIX_SIZE-1))
                 for _ in range(NUM_GETS)]

# --------------------------------------------------
# 1. Your COO SparseMatrix
# --------------------------------------------------
print("\n[1] Your SparseMatrix (COO / ArrayList)")

def build_mine():
    m = SparseMatrix(rows=MATRIX_SIZE, cols=MATRIX_SIZE, default=0)
    for (r, c), v in zip(insert_coords, insert_values):
        m.set(r, c, v)
    return m

my_matrix = benchmark("build (set x {})".format(NUM_ENTRIES), build_mine)

benchmark("get x {}".format(NUM_GETS),
          lambda: [my_matrix.get(r, c) for r, c in get_coords])

benchmark("items() full iteration",
          lambda: list(my_matrix.items()))

def multiply_mine():
    m2 = SparseMatrix(rows=MATRIX_SIZE, cols=MATRIX_SIZE, default=0)
    # small multiply — use only first 50 entries to keep it reasonable
    small = SparseMatrix(rows=MATRIX_SIZE, cols=MATRIX_SIZE, default=0)
    for (r, c), v in zip(insert_coords[:50], insert_values[:50]):
        small.set(r, c, v)
    return small.multiply(small)

benchmark("multiply() (50-entry submatrix)", multiply_mine)

# --------------------------------------------------
# 2. Scipy CSR
# --------------------------------------------------
if HAS_SCIPY:
    print("\n[2] scipy.sparse (CSR format)")

    def build_scipy():
        m = lil_matrix((MATRIX_SIZE, MATRIX_SIZE))
        for (r, c), v in zip(insert_coords, insert_values):
            m[r, c] = v
        return m.tocsr()

    sci = benchmark("build (set x {})".format(NUM_ENTRIES), build_scipy)

    benchmark("get x {}".format(NUM_GETS),
              lambda: [sci[r, c] for r, c in get_coords])

    benchmark("items() full iteration",
              lambda: list(zip(*sci.nonzero())))

    def multiply_scipy():
        small = lil_matrix((MATRIX_SIZE, MATRIX_SIZE))
        for (r, c), v in zip(insert_coords[:50], insert_values[:50]):
            small[r, c] = v
        s = small.tocsr()
        return s.dot(s)

    benchmark("multiply() (50-entry submatrix)", multiply_scipy)

    # --------------------------------------------------
    # 3. NumPy dense matrix
    # --------------------------------------------------
    print("\n[3] numpy dense matrix (ndarray)")

    def build_numpy():
        m = np.zeros((MATRIX_SIZE, MATRIX_SIZE), dtype=int)
        for (r, c), v in zip(insert_coords, insert_values):
            m[r, c] = v
        return m

    dense = benchmark("build (set x {})".format(NUM_ENTRIES), build_numpy)

    benchmark("get x {}".format(NUM_GETS),
              lambda: [dense[r, c] for r, c in get_coords])

    benchmark("items() full iteration",
              lambda: list(zip(*np.nonzero(dense))))

    def multiply_numpy():
        small = np.zeros((MATRIX_SIZE, MATRIX_SIZE), dtype=int)
        for (r, c), v in zip(insert_coords[:50], insert_values[:50]):
            small[r, c] = v
        return small @ small

    benchmark("multiply() (50-entry submatrix)", multiply_numpy)

print("\n" + "=" * 60)
print("Benchmarks complete.")
print("=" * 60)
