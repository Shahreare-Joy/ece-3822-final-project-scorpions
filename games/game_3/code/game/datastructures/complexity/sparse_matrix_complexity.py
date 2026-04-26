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

Author: [Mykai Wade]
Date:   [4/12/26]
Lab:    Lab 6 - Sparse World Map
"""
import time
import random
import sys
import os
import tracemalloc
 
try:
    from scipy.sparse import csr_matrix
    import numpy as np
except ImportError:
    print('scipy/numpy not installed — run: pip install scipy numpy')
    sys.exit(1)
 
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from datastructures.sparse_matrix import SparseMatrix
 
 
# ------------------------------------------------------------------
# Helpers
# ------------------------------------------------------------------
 
def make_entries(N, NNZ, seed=42):
    """Generate NNZ random (row, col, value) entries for an NxN matrix."""
    random.seed(seed)
    return [
        (random.randint(0, N - 1), random.randint(0, N - 1), random.randint(1, 100))
        for _ in range(NNZ)
    ]
 
 
def build_sparse(entries, N):
    """Build a SparseMatrix from a list of (r, c, v) entries."""
    sm = SparseMatrix(rows=N, cols=N, default=0)
    for r, c, v in entries:
        sm.set(r, c, v)
    return sm
 
 
def build_scipy(entries, N):
    """Build a scipy CSR matrix from entries."""
    rows = [e[0] for e in entries]
    cols = [e[1] for e in entries]
    vals = [e[2] for e in entries]
    return csr_matrix((vals, (rows, cols)), shape=(N, N))
 
 
def build_dense(entries, N):
    """Build a numpy dense matrix from entries."""
    d = np.zeros((N, N))
    for r, c, v in entries:
        d[r, c] = v
    return d
 
 
def print_results(label, sizes, times):
    """Print benchmark results in a readable table."""
    print(f'\n{label}')
    print(f'{"Size":>10} {"Time (s)":>12}')
    print('-' * 25)
    for n, t in zip(sizes, times):
        print(f'{n:>10} {t:>12.7f}')
 
 
def print_comparison(label, sizes, nnzs, t_coo, t_sp, t_np):
    """Print a 3-way comparison table."""
    print(f'\n{label}')
    print(f'{"Size":>8} {"NNZ":>8} {"COO (s)":>12} {"scipy (s)":>12} {"numpy (s)":>12}')
    print('-' * 56)
    for i, (N, NNZ) in enumerate(zip(sizes, nnzs)):
        print(f'{N:>8} {NNZ:>8} {t_coo[i]:>12.6f} {t_sp[i]:>12.6f} {t_np[i]:>12.6f}')
 
 
# ------------------------------------------------------------------
# Benchmarks
# ------------------------------------------------------------------
 
def benchmark_set(size_pairs):
    """Measure time to build each matrix type. Expected: O(nnz) for COO."""
    t_coo, t_sp, t_np = [], [], []
    for N, NNZ in size_pairs:
        entries = make_entries(N, NNZ)
        t0 = time.perf_counter(); build_sparse(entries, N);  t_coo.append(time.perf_counter() - t0)
        t0 = time.perf_counter(); build_scipy(entries, N);   t_sp.append(time.perf_counter() - t0)
        t0 = time.perf_counter(); build_dense(entries, N);   t_np.append(time.perf_counter() - t0)
    return t_coo, t_sp, t_np
 
 
def benchmark_get(size_pairs):
    """Measure time for 100 random get() calls. Expected: O(nnz) for COO."""
    t_coo, t_sp, t_np = [], [], []
    for N, NNZ in size_pairs:
        entries = make_entries(N, NNZ)
        sm    = build_sparse(entries, N)
        sp    = build_scipy(entries, N)
        dense = build_dense(entries, N)
        keys  = [(random.randint(0, N-1), random.randint(0, N-1)) for _ in range(100)]
        t0 = time.perf_counter(); [sm.get(r, c)    for r, c in keys]; t_coo.append(time.perf_counter() - t0)
        t0 = time.perf_counter(); [sp[r, c]        for r, c in keys]; t_sp.append(time.perf_counter() - t0)
        t0 = time.perf_counter(); [dense[r, c]     for r, c in keys]; t_np.append(time.perf_counter() - t0)
    return t_coo, t_sp, t_np
 
 
def benchmark_items(size_pairs):
    """Measure time to iterate all entries. Expected: O(nnz) for COO."""
    t_coo, t_sp, t_np = [], [], []
    for N, NNZ in size_pairs:
        entries = make_entries(N, NNZ)
        sm    = build_sparse(entries, N)
        sp    = build_scipy(entries, N)
        dense = build_dense(entries, N)
        t0 = time.perf_counter(); list(sm.items()); t_coo.append(time.perf_counter() - t0)
        t0 = time.perf_counter()
        cx = sp.tocoo(); list(zip(cx.row, cx.col, cx.data))
        t_sp.append(time.perf_counter() - t0)
        t0 = time.perf_counter()
        for r in range(N):
            for c in range(N):
                _ = dense[r, c]
        t_np.append(time.perf_counter() - t0)
    return t_coo, t_sp, t_np
 
 
def benchmark_multiply(size_pairs):
    """Measure matrix multiply. Expected: O(nnz^2) for COO."""
    t_coo, t_sp, t_np = [], [], []
    for N, NNZ in size_pairs:
        entries = make_entries(N, NNZ)
        sm    = build_sparse(entries, N)
        sm2   = build_sparse(entries, N)
        sp    = build_scipy(entries, N)
        dense = build_dense(entries, N)
        t0 = time.perf_counter(); sm.multiply(sm2);     t_coo.append(time.perf_counter() - t0)
        t0 = time.perf_counter(); sp.dot(sp);           t_sp.append(time.perf_counter() - t0)
        t0 = time.perf_counter(); np.dot(dense, dense); t_np.append(time.perf_counter() - t0)
    return t_coo, t_sp, t_np
 
 
def benchmark_memory(size_pairs):
    """Measure peak memory usage for COO vs numpy dense."""
    print('\nbenchmark_memory - O(nnz) for COO, O(n^2) for dense')
    print(f'{"Size":>8} {"NNZ":>8} {"COO (bytes)":>14} {"numpy (bytes)":>14}')
    print('-' * 48)
    for N, NNZ in size_pairs:
        entries = make_entries(N, NNZ)
        tracemalloc.start()
        build_sparse(entries, N)
        _, peak_coo = tracemalloc.get_traced_memory()
        tracemalloc.stop()
        tracemalloc.start()
        build_dense(entries, N)
        _, peak_np = tracemalloc.get_traced_memory()
        tracemalloc.stop()
        print(f'{N:>8} {NNZ:>8} {peak_coo:>14} {peak_np:>14}')
 
 
# ------------------------------------------------------------------
# Main
# ------------------------------------------------------------------
 
def main():
    size_pairs      = [(100, 200), (500, 1000), (1000, 2000)]
    multiply_pairs  = [(100, 20),  (200, 40),   (300, 60)]
    sizes           = [p[0] for p in size_pairs]
    nnzs            = [p[1] for p in size_pairs]
    mul_sizes       = [p[0] for p in multiply_pairs]
    mul_nnzs        = [p[1] for p in multiply_pairs]
 
    print('=' * 56)
    print('Sparse Matrix Complexity Analysis')
    print('Comparing: COO SparseMatrix | scipy CSR | numpy dense')
    print('=' * 56)
 
    t_coo, t_sp, t_np = benchmark_set(size_pairs)
    print_comparison('benchmark_set() - O(nnz) for COO', sizes, nnzs, t_coo, t_sp, t_np)
 
    t_coo, t_sp, t_np = benchmark_get(size_pairs)
    print_comparison('benchmark_get() x100 - O(nnz) for COO', sizes, nnzs, t_coo, t_sp, t_np)
 
    t_coo, t_sp, t_np = benchmark_items(size_pairs)
    print_comparison('benchmark_items() - O(nnz) for COO', sizes, nnzs, t_coo, t_sp, t_np)
 
    t_coo, t_sp, t_np = benchmark_multiply(multiply_pairs)
    print_comparison('benchmark_multiply() - O(nnz^2) for COO', mul_sizes, mul_nnzs, t_coo, t_sp, t_np)
 
    benchmark_memory(size_pairs)
 
    print('\n' + '=' * 56)
    print('Analysis complete!')
    print('=' * 56)
 
 
if __name__ == '__main__':
    main()
 
