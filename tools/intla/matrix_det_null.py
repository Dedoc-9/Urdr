#!/usr/bin/env python3
# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""Exact integer MATRIX foundation, part 2 (urdr-math, deterministic math library):
exact determinant (fraction-free) and an exact integer NULLSPACE witness. Companion to
bareiss_rank.py; same i64-overflow-as-refusal discipline. These are DETERMINISTIC algorithms
(same matrix -> same result), not search. Proven here as the reference; trusted in-system only
via cross-placement + grading, like urdr-core-rs.

- det: the fraction-free (Bareiss) determinant = final pivot x swap-sign; 0 if rank-deficient.
- nullspace_witness: a nonzero INTEGER vector v with M v = 0 (rank-deficient case), the exact
  witness the authority kernel certifies cheaply (matvec + != 0). None if the kernel is trivial.

Run -> BATTERY: ALL OK.
"""
from fractions import Fraction
from math import gcd
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from bareiss_rank import _fit, _mul, _sub, _exact_div, exact_rank, _Refuse, IMAX


def bareiss_det(matrix):
    """Exact determinant of a square integer matrix, or 'REFUSE' on i64 overflow."""
    n = len(matrix)
    if any(len(r) != n for r in matrix):
        raise ValueError("determinant needs a square matrix")
    try:
        M = [[_fit(int(x)) for x in row] for row in matrix]
        prev = 1
        sign = 1
        for k in range(n):
            if M[k][k] == 0:
                sw = next((i for i in range(k + 1, n) if M[i][k] != 0), None)
                if sw is None:
                    return 0                      # zero column at/after k -> singular
                M[k], M[sw] = M[sw], M[k]
                sign = -sign
            for i in range(k + 1, n):
                for j in range(k + 1, n):
                    num = _sub(_mul(M[k][k], M[i][j]), _mul(M[i][k], M[k][j]))
                    M[i][j] = _exact_div(num, prev)
                M[i][k] = 0
            prev = M[k][k]
        return _fit(sign * M[n - 1][n - 1])
    except _Refuse:
        return "REFUSE"


def det_oracle(matrix):
    """Exact determinant via Fraction elimination (unbounded)."""
    n = len(matrix)
    A = [[Fraction(int(x)) for x in row] for row in matrix]
    det = Fraction(1)
    for k in range(n):
        piv = next((i for i in range(k, n) if A[i][k] != 0), None)
        if piv is None:
            return 0
        if piv != k:
            A[k], A[piv] = A[piv], A[k]
            det = -det
        det *= A[k][k]
        for i in range(k + 1, n):
            f = A[i][k] / A[k][k]
            for j in range(k, n):
                A[i][j] -= f * A[k][j]
    return int(det)


def nullspace_witness(matrix):
    """A nonzero INTEGER vector v with matrix @ v = 0 (rank-deficient case), reduced by gcd;
    None if the matrix has trivial column kernel. Uses exact Fraction RREF (the compute side)."""
    A = [[Fraction(int(x)) for x in row] for row in matrix]
    rows = len(A)
    cols = len(A[0]) if rows else 0
    pivots = []
    prow = 0
    for col in range(cols):
        if prow >= rows:
            break
        piv = next((i for i in range(prow, rows) if A[i][col] != 0), None)
        if piv is None:
            continue
        A[prow], A[piv] = A[piv], A[prow]
        pv = A[prow][col]
        A[prow] = [x / pv for x in A[prow]]
        for i in range(rows):
            if i != prow and A[i][col] != 0:
                f = A[i][col]
                A[i] = [A[i][j] - f * A[prow][j] for j in range(cols)]
        pivots.append((prow, col))
        prow += 1
    pivot_cols = {c for _, c in pivots}
    free = [c for c in range(cols) if c not in pivot_cols]
    if not free:
        return None                                  # trivial kernel
    fc = free[0]
    v = [Fraction(0)] * cols
    v[fc] = Fraction(1)
    for (pr, pc) in pivots:
        v[pc] = -A[pr][fc]
    L = 1
    for x in v:
        L = L * x.denominator // gcd(L, x.denominator)
    vi = [int(x * L) for x in v]
    g = 0
    for x in vi:
        g = gcd(g, abs(x))
    if g > 1:
        vi = [x // g for x in vi]
    return vi


def _matvec(M, v):
    return [sum(M[i][j] * v[j] for j in range(len(v))) for i in range(len(M))]


if __name__ == "__main__":
    import random
    bad = 0
    # --- determinant ---
    dets = [[[1, 0, 0], [0, 1, 0], [0, 0, 1]], [[1, 1, 0], [0, 1, 1], [1, 0, 1]],
            [[1, 2, 3], [4, 5, 6], [7, 8, 9]], [[2, 5], [1, 3]], [[0]], [[7]]]
    for M in dets:
        g, e = bareiss_det(M), det_oracle(M)
        if g != e:
            bad += 1; print(f"  DET MISMATCH {M} got={g} exp={e}")
    random.seed(11)
    for _ in range(20000):
        n = random.randint(1, 4)
        M = [[random.randint(-6, 6) for _ in range(n)] for _ in range(n)]
        g = bareiss_det(M)
        if g == "REFUSE":
            continue
        if g != det_oracle(M):
            bad += 1
            if bad <= 6: print(f"  DET MISMATCH {M} got={g} exp={det_oracle(M)}")
    print("  det overflow ->", bareiss_det([[10**10, 1], [1, 10**10]]))

    # --- nullspace witness: M v = 0 exactly, v != 0, only for rank-deficient ---
    nbad = 0
    random.seed(13)
    tested = trivial = 0
    for _ in range(20000):
        r = random.randint(1, 4); c = random.randint(1, 4)
        M = [[random.randint(-5, 5) for _ in range(c)] for _ in range(r)]
        v = nullspace_witness(M)
        rank = exact_rank(M)
        if v is None:
            trivial += 1
            if rank != c:                            # None claimed but a kernel exists -> bug
                nbad += 1
            continue
        tested += 1
        if all(x == 0 for x in v) or any(x != 0 for x in _matvec(M, v)):
            nbad += 1
            if nbad <= 6: print(f"  NULL MISMATCH {M} v={v}")
    print(f"  nullspace: witnessed={tested} trivial={trivial} bad={nbad}")
    print("BATTERY:", "ALL OK" if bad == 0 and nbad == 0 else "FAIL")
