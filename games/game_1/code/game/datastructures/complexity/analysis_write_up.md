# Sparse Matrix Complexity Analysis

**Name:** Shahreare Joy  
**Date:** 04/12/2026  
**Implementation:** COO

---

## Overview

I implemented the SparseMatrix using the COO (Coordinate List) representation. So, I store only the non-default entries as (row, col, value) triples in my custom ArrayList. This is appropriate for the tile-map use case because most tiles in the world map are empty or default values, so it is wasteful to store every position in a full dense matrix. COO saves memory by storing only the meaningful entries. Compared to the other options, COO is the simplest to implement and understand. However, its main trade-off is speed: operations like get() and set() require scanning through stored entries, so they are slower than DOK or CSR for large numbers of non-default values.

---

## Time Complexity

Fill in the `?` cells after analysing your implementation.

| Operation | Your SparseMatrix | scipy sparse (CSR) | numpy dense |
|-----------|-------------------|--------------------|-------------|
| `set(r, c, v)` | O(nnz) | O(nnz) amortised | O(1) |
| `get(r, c)` | O(nnz) | O(log nnz) | O(1) |
| `items()` iteration | O(nnz) | O(nnz) | O(n²) |
| `multiply(other)` | O(nnz²) | O(nnz²/n) | O(n³) |

*nnz = number of non-zero entries, n = matrix dimension side length*

Explain your reasoning for each `?` in a sentence or two.

- set(r, c, v) = O(nnz):
    - My COO implementation scans through the stored entries to check if the position already exists. If the value is changed to the default, it may also need to shift entries left after removal.

- get(r, c) = O(nnz):
    - The matrix searches linearly through stored entries until it finds the matching row and column, or returns the default value if none is found.

- items() iteration = O(nnz):
    - Since COO stores only the non-default values, iterating over items only visits those stored entries once.

- multiply(other) = O(nnz²)
    - My multiplication uses nested loops over the stored entries for both matrices. For each of stored entry in one matrix, it checks entries in the other matrix to find matching row-column pairs, so the running time grows roughly with the product of the number of non-default entries.


---

## Benchmark Results

Run `sparse_matrix_complexity.py` and paste the output here:

```
Sparse Matrix Complexity Analysis
==================================================
Matrix size: 1000 x 1000
Stored entries: 200

1. Building the matrix
SparseMatrix build             0.008610 sec
NumPy build                    0.000876 sec
SciPy CSR build                0.000840 sec

2. Random get() accesses
SparseMatrix get               0.002089 sec
NumPy get                      0.000030 sec
SciPy CSR get                  0.002932 sec

3. items() full iteration
SparseMatrix items             0.000111 sec
NumPy items                    0.250703 sec
SciPy CSR items                0.000363 sec

4. multiply()
SparseMatrix multiply          0.006517 sec
NumPy multiply                 0.001068 sec
SciPy CSR multiply             0.000232 sec
```

---

## Space Complexity

| Representation | Space Used |
|----------------|-----------|
| Dense n×n      | O(n²)     |
| Your sparse    | O(nnz)      |

At what density (percentage of non-zero entries) does your sparse matrix
use *more* memory than a dense matrix?  Show your reasoning.

- My sparse matrix uses O(nnz) space. There nnz is the number of non-zero (non-default) entries. This is because it only stores the values that are not equal to the default, instead of storing every position in the matrix. The dense matrix stores all n × n values, so it always uses O(n²) space. In my COO implementation, each stored entry keeps the row, column, and value. So each stored entry takes about 3 units of space. Dense matrix stores only value, 1 unit per cell. So, sparse uses more memory when: 3 × nnz > n². Solve for nnz: nnz > n² / 3. So the break-even point is around 33%. This means if more than about 33% of the matrix is filled with non-default values, the sparse matrix will actually use more memory than a dense matrix.

---

## Observations

1. How does your implementation compare to scipy in terms of speed?
- My implementation was slower than scipy for building and multiplication. This is because scipy is highly optimized. However, my get() performance was similar to scipy, and my items() was faster in this test.
2. When is a sparse representation faster than a dense one?
- A sparse representation is faster when the matrix has very few non-zero entries. In that case, it only works with the stored values instead of looping through the entire matrix like a dense structure.
3. Was the overhead per entry (your structure vs. numpy array) noticeable?
- Yes, it was noticeable. My implementation stores (row, col, value) for each entry, which adds extra overhead compared to numpy, which stores values more efficiently in memory

---

## Conclusions

In this complexity analysis, I learned that sparse data structures are very useful when most values in a matrix are empty. They save memory and can be faster for certain operations like iterating through stored values. On the other hand, they can be slower than optimized libraries like numpy and scipy for operations like multiplication, as seen in the benchmark result.

---

## References

List any resources (textbooks, websites, papers) you used.
- https://documentation.sas.com/doc/en/tmhpprcref/14.2/tmhpprcref_hptmine_sect024.htm
- https://scipy-lectures.org/advanced/scipy_sparse/coo_matrix.html
