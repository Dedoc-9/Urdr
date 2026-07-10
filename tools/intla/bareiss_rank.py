#!/usr/bin/env python3
# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""Verified reference for the exact integer MATRIX engine (intla Stage B): rank over ℤ by
fraction-free (Bareiss) Gaussian elimination.

Bareiss keeps every intermediate an exact integer via the Sylvester identity:

    M'[i][j] = ( M[p][p]*M[i][j] - M[i][p]*M[p][j] ) / prev        (prev = previous pivot, 1 at start)

the division is EXACT (a known multiple) -- computed here by the proven exact `floor_divmod`
(rung 1). This is the general kernel matrix engine: `rank` is the first witness; general-n atlas
injectivity (rank = n), rigidity/stress-matrix rank, scheduler dependency ranks, and graph
Laplacians all consume it. It is NOT "for Connelly" -- Connelly is one downstream theorem.

i64 discipline (honest bound): every product, difference, and quotient must fit i64
[-(2^63-1), 2^63-1]; any overflow is a REFUSAL, never a wrapped/approximate answer (D9 law).
The fraction-free entries are bounded by subdeterminants (Hadamard), so this engine is exact
for i64-sized problems -- small integer matrices. Larger exact problems need a bignum substrate
(a later, separate piece) without changing this algorithm. ASCII, no glyph.

Run -> BATTERY: ALL OK.
"""
from fractions import Fraction
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from intdiv_algorithm import floor_divmod

IMAX = (1 << 63) - 1


class _Refuse(Exception):
    pass


def _fit(x):
    if x < -IMAX or x > IMAX:
        raise _Refuse
    return x


def _mul(a, b):
    return _fit(a * b)          # i64 multiply; overflow -> refuse (mirrors the fixpoint mul law)


def _sub(a, b):
    return _fit(a - b)          # i64 subtract; overflow -> refuse


def _exact_div(a, b):
    q, r = floor_divmod(a, b)   # Bareiss guarantees r == 0 (exact multiple)
    if r != 0:
        raise _Refuse           # defensive: a non-exact division means the invariant broke
    return q


def bareiss_rank(matrix):
    """Exact rank of an integer matrix, or 'REFUSE' if any i64 intermediate overflows."""
    try:
        M = [[_fit(int(x)) for x in row] for row in matrix]
        rows = len(M)
        cols = len(M[0]) if rows else 0
        prev = 1
        rank = 0
        prow = 0
        for col in range(cols):
            if prow >= rows:
                break
            piv = -1
            for i in range(prow, rows):
                if M[i][col] != 0:
                    piv = i
                    break
            if piv < 0:
                continue                     # rank-deficient column: no pivot here
            if piv != prow:
                M[prow], M[piv] = M[piv], M[prow]
            for i in range(prow + 1, rows):
                for j in range(col + 1, cols):
                    num = _sub(_mul(M[prow][col], M[i][j]), _mul(M[i][col], M[prow][j]))
                    M[i][j] = _exact_div(num, prev)
                M[i][col] = 0
            prev = M[prow][col]
            prow += 1
            rank += 1
        return rank
    except _Refuse:
        return "REFUSE"


def exact_rank(matrix):
    """Oracle: exact rank via Fraction Gaussian elimination (unbounded, no i64 limit)."""
    A = [[Fraction(int(x)) for x in row] for row in matrix]
    rows = len(A)
    cols = len(A[0]) if rows else 0
    rank = 0
    prow = 0
    for col in range(cols):
        if prow >= rows:
            break
        piv = -1
        for i in range(prow, rows):
            if A[i][col] != 0:
                piv = i
                break
        if piv < 0:
            continue
        A[prow], A[piv] = A[piv], A[prow]
        for i in range(rows):
            if i != prow and A[i][col] != 0:
                f = A[i][col] / A[prow][col]
                for j in range(col, cols):
                    A[i][j] -= f * A[prow][j]
        prow += 1
        rank += 1
    return rank


if __name__ == "__main__":
    import random
    bad = 0
    checked = 0
    refusals = 0
    # curated cases
    curated = [
        [[1, 0, 0], [0, 1, 0], [0, 0, 1]],           # rank 3
        [[1, 2, 0], [2, 4, 0], [0, 0, 1]],           # rank 2 (row1 = 2*row0)
        [[1, 1, 0], [0, 1, 1], [1, 0, 1]],           # rank 3 (det=2)
        [[1, 2, 3], [4, 5, 6], [7, 8, 9]],           # rank 2 (singular)
        [[0, 0], [0, 0]],                            # rank 0
        [[2, -1, 0]],                                # rank 1 (a kernel row)
        [[1, 2], [3, 4], [5, 6]],                    # rank 2 (3x2)
    ]
    for M in curated:
        g = bareiss_rank(M)
        e = exact_rank(M)
        checked += 1
        if g != e:
            bad += 1
            print(f"  MISMATCH {M} got={g} exp={e}")
    # random small integer matrices with small entries (stay in i64)
    random.seed(9)
    for _ in range(40000):
        r = random.randint(1, 4)
        c = random.randint(1, 4)
        M = [[random.randint(-6, 6) for _ in range(c)] for _ in range(r)]
        g = bareiss_rank(M)
        e = exact_rank(M)
        checked += 1
        if g == "REFUSE":
            refusals += 1
            continue
        if g != e:
            bad += 1
            if bad <= 6:
                print(f"  MISMATCH {M} got={g} exp={e}")
    # deliberate overflow -> must REFUSE, not wrap
    big = [[10**10, 3, 1], [7, 10**10, 2], [1, 4, 10**10]]
    ov = bareiss_rank(big)
    print(f"  overflow case -> {ov} (i64 refuse expected)")
    print(f"checked={checked}  in-range refusals={refusals}  mismatches={bad}")
    print("BATTERY:", "ALL OK" if bad == 0 and ov == "REFUSE" else "FAIL")
