#!/usr/bin/env python3
# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""urdr-rigidity (consumer of urdr-math) -- infinitesimal rigidity, trivial motions, self-stress.

Reimplements NO linear algebra: it builds framework matrices and asks the frozen `urdr_math` API
for `rank`, `nullspace`, `transpose`. Composition, not reinvention.

  framework (G,p) --> rigidity matrix R --> urdr_math --> {rank verdict, internal flex, self-stress Ω}

Steps (of the rigidity ladder):
  1. trivial motions (d translations + C(d,2) rotations) always lie in ker(R); an INTERNAL flex is a
     kernel vector of R orthogonal to them -- ker([R ; T]).  rigid  <=>  no internal flex.
  2. a self-stress ω is a vector on edges with Rᵀ ω = 0 (nodal equilibrium); the stress matrix Ω is
     the symmetric matrix Ω_ij = -ω_ij (edge), Ω_ii = Σ ω_ij. This is Connelly's structural
     certificate. (PSD verification + superstability are steps 3-4, next -- also urdr-math consumers.)

i64-bounded (urdr-math refuses overflow). Run -> BATTERY: ALL OK.
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import urdr_math
from bareiss_rank import exact_rank


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


def trivial_motions(n, d, coords):
    """The d(d+1)/2 trivial infinitesimal motions: d translations + C(d,2) rotations."""
    mots = []
    for a in range(d):
        t = [0] * (d * n)
        for i in range(n):
            t[d * i + a] = 1
        mots.append(t)
    for a in range(d):
        for b in range(a + 1, d):
            r = [0] * (d * n)
            for i in range(n):
                r[d * i + a] = -coords[i][b]
                r[d * i + b] = coords[i][a]
            mots.append(r)
    return mots


def rigid_rank(n, d):
    return d * n - d * (d + 1) // 2


def is_infinitesimally_rigid(n, d, edges, coords):
    r = urdr_math.rank(rigidity_matrix(n, d, edges, coords))
    return "REFUSE" if r == "REFUSE" else (r == rigid_rank(n, d))


def internal_flex(n, d, edges, coords):
    """A kernel vector of R orthogonal to the trivial motions (a GENUINE internal deformation),
    or None if the framework is infinitesimally rigid. Uses urdr_math.nullspace on [R ; T]."""
    R = rigidity_matrix(n, d, edges, coords)
    T = trivial_motions(n, d, coords)
    return urdr_math.nullspace(R + T)


def self_stress(n, d, edges, coords):
    """A self-stress ω (Rᵀ ω = 0), or None if none exists. urdr_math.nullspace(transpose(R))."""
    R = rigidity_matrix(n, d, edges, coords)
    return urdr_math.nullspace(urdr_math.transpose(R))


def stress_matrix(n, edges, omega):
    Om = [[0] * n for _ in range(n)]
    for k, (i, j) in enumerate(edges):
        w = omega[k]
        Om[i][j] -= w
        Om[j][i] -= w
        Om[i][i] += w
        Om[j][j] += w
    return Om


def _matvec(M, v):
    return [sum(M[i][j] * v[j] for j in range(len(v))) for i in range(len(M))]


if __name__ == "__main__":
    bad = 0
    d = 2
    triangle = (3, [(0, 1), (1, 2), (0, 2)], [(0, 0), (2, 0), (1, 2)])
    square = (4, [(0, 1), (1, 2), (2, 3), (3, 0)], [(0, 0), (2, 0), (2, 2), (0, 2)])
    braced = (4, [(0, 1), (1, 2), (2, 3), (3, 0), (0, 2)], [(0, 0), (2, 0), (2, 2), (0, 2)])
    dbraced = (4, [(0, 1), (1, 2), (2, 3), (3, 0), (0, 2), (1, 3)], [(0, 0), (2, 0), (2, 2), (0, 2)])

    print("-- step 1: rigidity + internal flex (trivial motions separated) --")
    for name, (n, edges, coords), exp_rigid in [("triangle", triangle, True), ("square", square, False),
                                                ("braced square", braced, True)]:
        R = rigidity_matrix(n, d, edges, coords)
        # trivial motions really are in ker(R)
        for t in trivial_motions(n, d, coords):
            if any(x != 0 for x in _matvec(R, t)):
                bad += 1; print(f"    {name}: a trivial motion is NOT in ker(R)!")
        rigid = is_infinitesimally_rigid(n, d, edges, coords)
        flex = internal_flex(n, d, edges, coords)
        ok = (rigid == exp_rigid) and (urdr_math.rank(R) == exact_rank(R)) and ((flex is None) == rigid)
        print(f"  {name}: {'rigid' if rigid else 'flexible'}; internal_flex={'none' if flex is None else flex} [{'OK' if ok else 'FAIL'}]")
        if not ok:
            bad += 1
        if flex is not None and any(x != 0 for x in _matvec(R, flex)):
            bad += 1; print(f"    internal flex not in ker(R)!")

    print("-- step 2: self-stress + stress matrix Ω --")
    n, edges, coords = dbraced
    R = rigidity_matrix(n, d, edges, coords)
    w = self_stress(n, d, edges, coords)
    if w is None:
        bad += 1; print("  doubly-braced square: expected a self-stress, got none")
    else:
        Rt = urdr_math.transpose(R)
        equil = all(x == 0 for x in _matvec(Rt, w))          # Rᵀ ω = 0 (nodal equilibrium)
        Om = stress_matrix(n, edges, w)
        symmetric = all(Om[i][j] == Om[j][i] for i in range(n) for j in range(n))
        print(f"  doubly-braced square: self-stress ω={w}  equilibrium(Rᵀω=0)={equil}  Ω symmetric={symmetric}")
        print(f"    Ω = {Om}")
        if not (equil and symmetric):
            bad += 1
    print("BATTERY:", "ALL OK" if bad == 0 else f"{bad} FAIL")
    sys.exit(0 if bad == 0 else 1)
