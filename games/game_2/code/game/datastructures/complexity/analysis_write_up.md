# Sparse Matrix Complexity Analysis

**Name:** Hamza Mughal  
**Date:** 4/11/2026  
**Implementation:** COO

---

## Overview

I chose **Option B: COO (Coordinate List)**, backed by my custom `ArrayList` from Lab 3.

The COO format stores only non-default entries as `(row, col, value)` tuples in an
ArrayList. For the tile-map use case, most tiles are empty (default value), so only
a small number of entries need to be stored — making COO a natural fit. A 40×30 tile
map has 1200 cells, but only a fraction are walls or objects, so COO wastes no memory
on empty tiles.

Compared to DOK (Option A), COO avoids needing a custom hash table. Compared to CSR
(Option C), COO is simpler to implement and easier to update (inserting/removing entries
does not require rebuilding row pointer arrays). The trade-off is that `get()` and `set()`
require a linear O(nnz) scan, whereas CSR achieves O(log nnz) per lookup via binary
search on sorted column indices.

---

## Time Complexity

| Operation | Your SparseMatrix | scipy sparse (CSR) | numpy dense |
|-----------|-------------------|--------------------|-------------|
| `set(r, c, v)` | O(nnz) | O(nnz) amortised | O(1) |
| `get(r, c)` | O(nnz) | O(log nnz) | O(1) |
| `items()` iteration | O(nnz) | O(nnz) | O(n²) |
| `multiply(other)` | O(nnz²) | O(nnz²/n) | O(n³) |

*nnz = number of non-zero entries, n = matrix dimension side length*

**Reasoning:**
- **set:** Each call scans the entire ArrayList to find an existing entry before
  inserting or updating — O(nnz) in the worst case.
- **get:** Same linear scan through all stored entries to find a matching (row, col) pair.
- **items():** Simply iterates once over all stored entries — O(nnz).
- **multiply():** For each entry in self (nnz entries), scans all entries in other (nnz
  entries) looking for matching column/row pairs — O(nnz²) in the worst case.

---

## Benchmark Results

```
============================================================
SparseMatrix Complexity Analysis
Matrix size: 500 x 500, Non-zeros: 1000, Gets: 1000
============================================================

[1] Your SparseMatrix (COO / ArrayList)
  build (set x 1000)                       186.2549 ms
  get x 1000                               349.6093 ms
  items() full iteration                   1.7783 ms
  multiply() (50-entry submatrix)          1.4115 ms

[2] scipy.sparse (CSR format)
  build (set x 1000)                       4.1941 ms
  get x 1000                               26.2505 ms
  items() full iteration                   0.6124 ms
  multiply() (50-entry submatrix)          1.1810 ms

[3] numpy dense matrix (ndarray)
  build (set x 1000)                       1.5178 ms
  get x 1000                               0.4007 ms
  items() full iteration                   1.6939 ms
  multiply() (50-entry submatrix)          179.2276 ms
```

---

## Space Complexity

| Representation | Space Used |
|----------------|------------|
| Dense n×n      | O(n²)      |
| Your sparse    | O(nnz)     |

**Break-even density analysis:**

A dense matrix stores n² entries. The COO sparse matrix stores 3·nnz values (row, col,
value per entry). The sparse matrix uses more memory than dense when:

```
3 · nnz > n²
nnz > n² / 3
density > 1/3 ≈ 33%
```

So once more than ~33% of the matrix cells are non-zero, a dense matrix is actually
more memory-efficient than COO. For a tile map where typically fewer than 10% of tiles
are walls or objects, COO is clearly the better choice.

---

## Observations

1. **Speed vs scipy:** My COO implementation is significantly slower than scipy for
   `build` (~44×) and `get` (~13×). This is because scipy is written in optimized C and
   uses sorted indices with binary search, while my implementation does Python-level
   linear scans through an ArrayList. For `items()` and `multiply()` on small submatrices,
   the difference is much smaller (under 3×).

2. **When sparse beats dense:** Sparse representations are faster than dense for
   `items()` iteration and `multiply()` when nnz << n². The numpy dense multiply took
   179 ms vs 1.4 ms for COO on the same 50-entry submatrix — a 127× speedup — because
   dense multiply processes all n³ = 125,000,000 operations while COO only processes
   non-zero pairs.

3. **Per-entry overhead:** Yes, the overhead was noticeable. Each ArrayList entry is a
   Python tuple object with significantly more overhead than a raw numpy array element.
   numpy stores integers as contiguous bytes in memory (cache-friendly), while my
   ArrayList stores Python object references, which require pointer chasing and are much
   slower to access.

---

## Conclusions

Sparse data structures provide significant memory savings for matrices where most values
are the same default (like a tile map), storing only the exceptions rather than every
cell. However, a pure Python COO implementation is considerably slower than optimized
library implementations like scipy due to interpreted linear scans versus compiled binary
search. For this game's tile map — which is small and read mostly at load time — the
COO implementation is fast enough in practice, even if it cannot match scipy's speed for
large-scale numerical work.

---

## References

- scipy.sparse documentation: https://docs.scipy.org/doc/scipy/reference/sparse.html
- Sparse matrix formats overview: https://en.wikipedia.org/wiki/Sparse_matrix
- Lab 6 course materials, ECE 3882
