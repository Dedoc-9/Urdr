#!/usr/bin/env python3
# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""urdr-rigidity (first CONSUMER of urdr-math) -- infinitesimal rigidity of a bar framework.

This module does NOT implement linear algebra. It builds the rigidity matrix R of a framework
(G, p) with integer coordinates and asks the frozen `urdr_math` API for `rank(R)` and a kernel
vector `nullspace(R)`. Composition, not reimplementation:

    framework (G, p)  ->  rigidity matrix R  ->  urdr_math.rank / nullspace  ->  verdict + witness

Infinitesimal rigidity (non-degenerate framework in d dims, n vertices):
    rigid  <=>  rank(R) = d*n - d(d+1)/2      (the trivial motions: d translations + C(d,2) rotations)

A flexible framework has rank(R) below that; a kernel vector of R witnesses the deficiency (the
authority kernel certifies such a witness -- see examples/certify_kernel_witness.urdr). Full
distinction of nontrivial flexes from trivial motions, stress matrices, and Connelly superstability
are later urdr-rigidity milestones. i64-bounded (urdr-math refuses overflow). Run -> BATTERY: ALL OK.
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import urdr_math
from bareiss_rank import exact_rank              # independent oracle for cross-checking the composition


def rigidity_matrix(n, d, edges, coords):
    R = []
    for (i, j) in edges:
        row = [0] * (d * n)
        for a in range(d):
            diff = coords[i][a] - coords[j][a]
            row[d * i + a] = diff
            row[d * j + a] = -diff
        R.append(row)
    return R


def rigid_rank(n, d):
    return d * n - d * (d + 1) // 2              # dimension of the trivial-motion complement


def is_infinitesimally_rigid(n, d, edges, coords):
    R = rigidity_matrix(n, d, edges, coords)
    r = urdr_math.rank(R)                        # <-- consumes the frozen library API
    if r == "REFUSE":
        return "REFUSE"
    return r == rigid_rank(n, d)


def flex_witness(n, d, edges, coords):
    return urdr_math.nullspace(rigidity_matrix(n, d, edges, coords))   # <-- library API


def _matvec(M, v):
    return [sum(M[i][j] * v[j] for j in range(len(v))) for i in range(len(M))]


if __name__ == "__main__":
    bad = 0
    d = 2
    triangle = (3, [(0, 1), (1, 2), (0, 2)], [(0, 0), (2, 0), (1, 2)])          # rigid
    square = (4, [(0, 1), (1, 2), (2, 3), (3, 0)], [(0, 0), (2, 0), (2, 2), (0, 2)])   # flexible
    braced = (4, [(0, 1), (1, 2), (2, 3), (3, 0), (0, 2)],
              [(0, 0), (2, 0), (2, 2), (0, 2)])                                  # rigid (square + diagonal)

    cases = [("triangle", triangle, True), ("square", square, False), ("braced square", braced, True)]
    for name, (n, edges, coords), expect_rigid in cases:
        R = rigidity_matrix(n, d, edges, coords)
        r_lib = urdr_math.rank(R)
        r_oracle = exact_rank(R)                 # composition sanity: library rank == oracle rank
        rigid = is_infinitesimally_rigid(n, d, edges, coords)
        ok = (r_lib == r_oracle) and (rigid == expect_rigid)
        print(f"  {name}: rank(R)={r_lib} (rigid-rank {rigid_rank(n, d)}) -> "
              f"{'rigid' if rigid else 'flexible'} [{'OK' if ok else 'FAIL'}]")
        if not ok:
            bad += 1
        if not rigid:                            # a flex witness must lie in ker(R)
            v = flex_witness(n, d, edges, coords)
            if v is None or all(x == 0 for x in v) or any(x != 0 for x in _matvec(R, v)):
                bad += 1
                print(f"    flex witness invalid: {v}")
            else:
                print(f"    flex witness v={v}  (R·v = 0, certifiable by the authority kernel)")
    print("BATTERY:", "ALL OK" if bad == 0 else f"{bad} FAIL")
    sys.exit(0 if bad == 0 else 1)
