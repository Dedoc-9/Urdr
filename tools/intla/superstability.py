#!/usr/bin/env python3
# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""urdr-rigidity steps 3-4: exact PSD verification of the stress matrix Ω, and Connelly
superstability certification. Pure consumers of the frozen urdr-math (determinant, rank).

HONEST correction: PSD of a symmetric matrix is NOT Sylvester's leading-minor test (that proves
positive DEFINITE). Ω is always singular, so the leading-only test is wrong. The exact PSD test is
'ALL principal minors >= 0' (necessary and sufficient), computed by urdr_math.determinant on every
principal submatrix. Small n -> the 2^n-1 minors are cheap; exact; no floats.

Connelly superstability (sufficient for UNIVERSAL/global rigidity): a PROPER equilibrium stress ω
(the sign for which Ω >= 0) with
    (a) Ω >= 0,
    (b) rank(Ω) = n - d - 1,
    (c) no non-trivial affine flex  (no nonzero symmetric S with (p_i-p_j)^T S (p_i-p_j)=0 for all
        edges  <=>  the edge-quadratic-forms matrix has full column rank d(d+1)/2).
All three reduce to urdr-math det/rank. Run -> BATTERY: ALL OK.
"""
import sys, os
from itertools import combinations
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import urdr_math
from rigidity import rigidity_matrix, self_stress, stress_matrix


def is_psd(M):
    """PSD iff every principal minor >= 0 (exact). 'REFUSE' if a minor overflows i64."""
    n = len(M)
    for k in range(1, n + 1):
        for idx in combinations(range(n), k):
            sub = [[M[i][j] for j in idx] for i in idx]
            d = urdr_math.determinant(sub)
            if d == "REFUSE":
                return "REFUSE"
            if d < 0:
                return False
    return True


def proper_stress(n, d, edges, coords):
    """The self-stress ω (or -ω) whose stress matrix is PSD, with that Ω; None if none exists."""
    w = self_stress(n, d, edges, coords)
    if w is None:
        return None
    for sign in (1, -1):
        ws = [sign * x for x in w]
        Om = stress_matrix(n, edges, ws)
        if is_psd(Om) is True:
            return ws, Om
    return None


def affine_flex_rank(d, edges, coords):
    """(rank, full) of the edge-quadratic-forms matrix; no affine flex <=> rank == full = d(d+1)/2."""
    idx = [(a, b) for a in range(d) for b in range(a, d)]
    A = []
    for (i, j) in edges:
        diff = [coords[i][a] - coords[j][a] for a in range(d)]
        row = [(1 if a == b else 2) * diff[a] * diff[b] for (a, b) in idx]
        A.append(row)
    return urdr_math.rank(A), len(idx)


def superstable(n, d, edges, coords):
    """Connelly superstability certificate: (verdict, reason)."""
    ps = proper_stress(n, d, edges, coords)
    if ps is None:
        return (False, "no proper (PSD) equilibrium stress")
    _w, Om = ps
    rk = urdr_math.rank(Om)
    if rk != n - d - 1:
        return (False, f"rank(Ω)={rk} != n-d-1={n - d - 1}")
    ar, full = affine_flex_rank(d, edges, coords)
    if ar != full:
        return (False, f"non-trivial affine flex (edge-forms rank {ar} < {full})")
    return (True, f"superstable: Ω⪰0, rank(Ω)={rk}=n-d-1, no affine flex")


if __name__ == "__main__":
    bad = 0
    # --- step 3: PSD test correctness (the honest part) ---
    psd_cases = [
        ([[2, 0], [0, 3]], True),                 # PD -> PSD
        ([[1, 1, 1], [1, 1, 1], [1, 1, 1]], True),# rank-1 outer product, PSD (singular)
        ([[1, 0], [0, -1]], False),               # indefinite
        ([[-1, 0], [0, -1]], False),              # negative definite
        ([[0, 0], [0, 0]], True),                 # zero -> PSD
        ([[1, 2], [2, 1]], False),                # eigenvalues 3,-1 -> not PSD (leading minors 1,-3)
    ]
    for M, exp in psd_cases:
        if is_psd(M) != exp:
            bad += 1; print(f"  PSD MISMATCH {M} got={is_psd(M)} exp={exp}")
    print("  step 3 PSD test:", "ok" if bad == 0 else "FAIL")

    # --- step 4: superstability ---
    d = 2
    dbraced = (4, [(0, 1), (1, 2), (2, 3), (3, 0), (0, 2), (1, 3)], [(0, 0), (2, 0), (2, 2), (0, 2)])
    braced = (4, [(0, 1), (1, 2), (2, 3), (3, 0), (0, 2)], [(0, 0), (2, 0), (2, 2), (0, 2)])
    for name, (n, e, c), exp in [("doubly-braced square", dbraced, True), ("braced square (minimal)", braced, False)]:
        v, why = superstable(n, d, e, c)
        ok = (v == exp)
        print(f"  {name}: superstable={v} ({why}) [{'OK' if ok else 'FAIL'}]")
        if not ok:
            bad += 1
    print("BATTERY:", "ALL OK" if bad == 0 else f"{bad} FAIL")
    sys.exit(0 if bad == 0 else 1)
