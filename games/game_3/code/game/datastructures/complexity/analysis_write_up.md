# Sparse Matrix Complexity Analysis

**Name:** [Mykai Wade]
**Date:** [4/12/26]
**Implementation:**   COO 

---

## Overview
I implemented a SparseMatrix using COO (Coordinate List) format with a custom ArrayList. It stores only non-default values (–1), making it efficient for tile maps where most entries are empty. For example, a 60×40 grid with ~2000 non-empty tiles stores only those values, saving memory.

The trade-off is performance: unlike DOK (O(1) lookup), COO requires a linear scan O(nnz) for get() and set(). Compared to CSR, it is easier to implement but less efficient for row-based access.
---

## Time Complexity

Fill in the `?` cells after analysing your implementation.

| Operation | Your SparseMatrix | scipy sparse (CSR) | numpy dense |
|-----------|-------------------|--------------------|-------------|
| `set(r, c, v)` | O(nnz) | O(nnz) amortised | O(1) |
| `get(r, c)` | O(nnz) | O(log nnz) | O(1) |
| `items()` iteration | O(nnz) | O(nnz) | O(n²) |
| `multiply(other)` | O(nnz^2) | O(nnz²/n) | O(n³) |

*nnz = number of non-zero entries, n = matrix dimension side length*

Explain your reasoning for each `?` in a sentence or two.
 O(nnz) due to linear search, O(nnz), faster than dense O(n²), and  O(nnz²), slower than optimized CSR
---

## Benchmark Results

Run `sparse_matrix_complexity.py` and paste the output here:

```
========================================================
Sparse Matrix Complexity Analysis
Comparing: COO SparseMatrix | scipy CSR | numpy dense
========================================================
benchmark_set() - O(nnz) for COO
    Size      NNZ      COO (s)    scipy (s)    numpy (s)
--------------------------------------------------------
     100      200     0.004469     0.000838     0.000140
     500     1000     0.098673     0.001064     0.001731
    1000     2000     0.328827     0.001687     0.003097

benchmark_get() x100 - O(nnz) for COO
    Size      NNZ      COO (s)    scipy (s)    numpy (s)
--------------------------------------------------------
     100      200     0.003117     0.002525     0.000037
     500     1000     0.016401     0.002383     0.000058
    1000     2000     0.033005     0.002435     0.000063

benchmark_items() - O(nnz) for COO
    Size      NNZ      COO (s)    scipy (s)    numpy (s)
--------------------------------------------------------
     100      200     0.000067     0.000220     0.002229
     500     1000     0.000500     0.000503     0.048199
    1000     2000     0.000919     0.000923     0.212345

benchmark_multiply() - O(nnz^2) for COO
    Size      NNZ      COO (s)    scipy (s)    numpy (s)
--------------------------------------------------------
     100       20     0.000285     0.000273     0.000307
     200       40     0.000605     0.000217     0.000457
     300       60     0.001336     0.000200     0.001174

benchmark_memory - O(nnz) for COO, O(n^2) for dense
    Size      NNZ    COO (bytes)  numpy (bytes)
------------------------------------------------
     100      200           4336          80144
     500     1000          15936        2000144
    1000     2000          84716        8000144
```

---

## Space Complexity

| Representation | Space Used |
|----------------|-----------|
| Dense n×n      | O(n²)     |
| Your sparse    | O(nnz)      |

COO uses far less memory (e.g., ~85 KB vs 8 MB at 1000×1000). It is more efficient when density is below ~6–7%.COO uses far less memory (e.g., ~85 KB vs 8 MB at 1000×1000). It is more efficient when density is below ~6–7%.
---

## Observations
COO is slower than scipy for access operations due to linear scans but much faster than dense matrices for iteration. The higher insertion cost is acceptable since tile maps are typically built once and reused.
---

## Conclusions
COO is ideal for sparse, write-once, iterate-often cases like tile maps. It provides major memory savings and fast iteration but is less suitable for frequent random access, where DOK or CSR would perform better.
---

## References
scipy.sparse documentation: https://docs.scipy.org/doc/scipy/reference/sparse.html
Wikipedia: Sparse matrix — https://en.wikipedia.org/wiki/Sparse_matrix
Course lecture notes, ECE 3822 Spring 2026