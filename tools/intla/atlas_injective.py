# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""General-n observer-atlas injectivity certificate (exact, rectangular).

An observer atlas is a family of linear CHARTS, each a matrix C_i (k_i x n) that
projects an n-dimensional state to a k_i-dimensional observation. The atlas
RECOVERS the state (is injective) iff no two distinct states share every chart's
observation -- i.e. iff the STACKED matrix M (Σk_i x n, one block per chart) has
trivial column kernel, i.e. FULL COLUMN RANK:

        injective(atlas)  <=>  rank(M) = n          (D10, general dimension)

The earlier linear-chart theorem only handled the SQUARE case via det != 0. This
lifts it to any rectangular (typically over-determined, Σk_i >= n) atlas using the
frozen fraction-free Bareiss `rank` -- exact over Z, no float, i64-overflow
refused. When the atlas is deficient, `urdr_math.nullspace` returns a nonzero
integer v with M v = 0: the states 0 and v are then INDISTINGUISHABLE under every
chart (M·0 = M·v) -- an exact certificate of NON-injectivity (a collision), not a
guess. Consumes the frozen `urdr-math` v0.1; touches no core; no new glyph."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import urdr_math as UM                                  # noqa: E402  frozen v0.1


def stack(charts):
    """Stack the chart matrices into one (Σk_i x n) observation matrix M."""
    rows = []
    for c in charts:
        rows.extend([list(r) for r in c])
    return rows


def matvec(a, v):
    """Exact integer M v (used to verify a collision witness / recover a state)."""
    return [sum(a[i][j] * v[j] for j in range(len(v))) for i in range(len(a))]


def rank(charts):
    """Exact rank of the stacked atlas (frozen Bareiss `rank`)."""
    return UM.rank(stack(charts))


def injective(charts, n):
    """The certificate: the atlas recovers an n-dim state iff rank(M) == n."""
    return rank(charts) == n


def collision_witness(charts, n):
    """A nonzero integer v with M v = 0 when the atlas is deficient (so 0 and v
    collide under every chart), or None when the atlas is injective (trivial
    kernel). This is `urdr_math.nullspace` of the stacked matrix -- exact."""
    return UM.nullspace(stack(charts))


def certifies_injective(charts, n):
    """Full verdict: (is_injective, witness). is_injective iff rank==n AND there
    is no nontrivial kernel; witness is the colliding v (or None). The two exact
    engines (rank, nullspace) agree by construction -- a disagreement would redden
    the gate."""
    r = rank(charts)
    w = collision_witness(charts, n)
    inj = (r == n)
    # exactness cross-check: rank==n  <=>  no nullspace witness
    if inj != (w is None):
        return (None, w)                               # inconsistent -> refuse the verdict
    return (inj, w)
