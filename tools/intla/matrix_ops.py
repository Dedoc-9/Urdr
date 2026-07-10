#!/usr/bin/env python3
# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""urdr-math matrix basics: transpose, multiplication. Deterministic; i64-overflow = REFUSE.
Run -> BATTERY: ALL OK."""
import sys, os, random
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
IMAX = (1 << 63) - 1


class _Refuse(Exception):
    pass


def _fit(x):
    if x < -IMAX or x > IMAX:
        raise _Refuse
    return x


def transpose(M):
    if not M:
        return []
    return [[M[i][j] for i in range(len(M))] for j in range(len(M[0]))]


def matmul(A, B):
    if len(A[0]) != len(B):
        raise ValueError("shape mismatch")
    try:
        n, k, m = len(A), len(B), len(B[0])
        C = []
        for i in range(n):
            row = []
            for j in range(m):
                s = 0
                for l in range(k):
                    s = _fit(s + _fit(A[i][l] * B[l][j]))
                row.append(s)
            C.append(row)
        return C
    except _Refuse:
        return "REFUSE"


def _battery():
    bad = 0
    # transpose involution
    random.seed(23)
    for _ in range(5000):
        r, c = random.randint(1, 4), random.randint(1, 4)
        M = [[random.randint(-9, 9) for _ in range(c)] for _ in range(r)]
        if transpose(transpose(M)) != M:
            bad += 1
    # matmul vs a direct oracle (unbounded ints)
    for _ in range(20000):
        n, k, m = random.randint(1, 4), random.randint(1, 4), random.randint(1, 4)
        A = [[random.randint(-9, 9) for _ in range(k)] for _ in range(n)]
        B = [[random.randint(-9, 9) for _ in range(m)] for _ in range(k)]
        got = matmul(A, B)
        exp = [[sum(A[i][l] * B[l][j] for l in range(k)) for j in range(m)] for i in range(n)]
        if got != "REFUSE" and got != exp:
            bad += 1
    ov = matmul([[10**10, 10**10]], [[10**10], [10**10]])
    print("matrix_ops: transpose/matmul", "ALL OK" if bad == 0 and ov == "REFUSE" else "FAIL")
    return bad == 0 and ov == "REFUSE"


if __name__ == "__main__":
    sys.exit(0 if _battery() else 1)
