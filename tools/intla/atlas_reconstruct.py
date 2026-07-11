# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""Exact observer-atlas RECONSTRUCTION (inversion): recover the state from its
observations, or refuse.

The injectivity certificate (`atlas_injective.py`) proves an over-determined
atlas *can distinguish* states -- distinct states never share every chart's
observation. This is the constructive sibling: given an observation vector
`y = M x` of an unknown state `x` under an injective atlas (stacked matrix
`M`, Σk_i x n, full column rank n), it produces `x` itself -- exactly, as a
reduced rational (num/den) -- together with a cheap independent WITNESS.

Method (exact, division-free until the final rational, no float):
  1. `M` has full column rank n (injectivity), so some n of its rows form an
     invertible n x n submatrix `S`. Pick them deterministically: walk the rows
     in fixed order, keeping a row iff it raises the rank of those kept (frozen
     Bareiss `rank`). Full column rank guarantees n are found.
  2. Solve the square subsystem `S x = y_S` by Cramer's rule with the frozen
     `determinant`: `x_j = det(S with column j <- y_S) / det(S)`. So
     `x = N / D` with integer `N_j = det(S_j)`, `D = det(S) != 0`.
  3. CONSISTENCY on ALL rows -- the forgery detector: a genuine observation
     satisfies every chart, so check the exact integer identity `M N = D y`
     across all Σk_i rows, not just the n solved ones. The redundant
     (over-determined) rows are precisely what catches an observation that is
     not in the column space -- a forged / impossible view. If any row fails,
     `y` is not a real observation and reconstruction REFUSES.

The pair `(N, D)` (equivalently the reduced `(num, den)`) is the witness: anyone
can verify `M num = den y`, `den > 0` without redoing the solve -- the analogue
of the injectivity collision witness, for the recover direction.

Refusals (total, never a guess):
  * NOT_INJECTIVE  -- `rank(M) < n`: the state is not unique (the deficient
    atlas has a nullspace; see the injectivity collision witness). Cannot name
    THE state, so refuse.
  * INCONSISTENT   -- `M N != D y` on some row: `y` is not in the column space,
    i.e. not an observation of any state. Refuse (an impossible/forged view).
  * REFUSE         -- i64 overflow inside `determinant`: refuse, never wrap.

Consumes the frozen `urdr-math` v0.1 (`rank`, `determinant`); touches no core;
no new glyph."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import urdr_math as UM                                  # noqa: E402  frozen v0.1

OK = "OK"
NOT_INJECTIVE = "NOT_INJECTIVE"
INCONSISTENT = "INCONSISTENT"
REFUSE = "REFUSE"


def stack(charts):
    """Stack the chart matrices into one (Σk_i x n) observation matrix M."""
    rows = []
    for c in charts:
        rows.extend([list(r) for r in c])
    return rows


def matvec(a, v):
    """Exact integer A v (used to form observations and to check a witness)."""
    return [sum(a[i][j] * v[j] for j in range(len(v))) for i in range(len(a))]


def _gcd(a, b):
    a, b = abs(a), abs(b)
    while b:
        a, b = b, a % b
    return a


def _reduce(num_vec, den):
    """Canonicalize the rational state num_vec/den: den > 0, overall gcd 1."""
    if den < 0:
        num_vec = [-a for a in num_vec]
        den = -den
    g = den
    for a in num_vec:
        g = _gcd(g, a)
    if g > 1:
        num_vec = [a // g for a in num_vec]
        den //= g
    return num_vec, den


def independent_rows(m, n):
    """Deterministic greedy choice of n row indices of M forming an invertible
    n x n submatrix: walk rows in fixed order, keep a row iff the kept rows stay
    linearly independent (frozen Bareiss `rank`). Full column rank ⇒ n exist."""
    chosen, rows = [], []
    for i, row in enumerate(m):
        trial = rows + [list(row)]
        if UM.rank(trial) == len(trial):
            chosen.append(i)
            rows.append(list(row))
            if len(rows) == n:
                break
    return chosen


def solve(charts, y, n):
    """Full reconstruction verdict: (status, state).

    status is OK / NOT_INJECTIVE / INCONSISTENT / REFUSE. On OK, state is the
    exact reduced rational (num_vec, den) with M·num = den·y and den > 0; on any
    refusal, state is None. Deterministic and exact; i64 overflow -> REFUSE."""
    m = stack(charts)
    if len(y) != len(m):
        return (INCONSISTENT, None)                     # ill-shaped observation
    if UM.rank(m) != n:
        return (NOT_INJECTIVE, None)                    # state not unique -> refuse
    idx = independent_rows(m, n)
    if len(idx) != n:                                   # defensive; rank==n guarantees n
        return (NOT_INJECTIVE, None)
    s = [m[i] for i in idx]
    ys = [y[i] for i in idx]
    den = UM.determinant(s)
    if den == "REFUSE":
        return (REFUSE, None)
    if den == 0:                                        # unreachable: chosen rows independent
        return (NOT_INJECTIVE, None)
    num = []
    for j in range(n):
        sj = [list(s[r]) for r in range(n)]
        for r in range(n):
            sj[r][j] = ys[r]
        dj = UM.determinant(sj)
        if dj == "REFUSE":
            return (REFUSE, None)
        num.append(dj)
    # consistency on ALL rows: M·num == den·y (over-determination = forgery detector)
    mn = matvec(m, num)
    if any(mn[i] != den * y[i] for i in range(len(m))):
        return (INCONSISTENT, None)                     # y not in column space -> refuse
    return (OK, _reduce(num, den))


def reconstruct(charts, y, n):
    """The exact recovered state (num_vec, den) with M·num = den·y, or None if
    the atlas is not injective, y is not a genuine observation, or arithmetic
    overflowed. Convenience wrapper over `solve`."""
    status, state = solve(charts, y, n)
    return state if status == OK else None


def is_genuine_observation(charts, y, n):
    """True iff y is the observation of some (unique) state under an injective
    atlas -- i.e. reconstruction succeeds."""
    return solve(charts, y, n)[0] == OK


def verifies(charts, y, n, state):
    """Independent WITNESS check: does the claimed state (num_vec, den) satisfy
    M·num = den·y with den > 0? Cheap to run without redoing the solve."""
    if state is None:
        return False
    num, den = state
    if den <= 0:
        return False
    m = stack(charts)
    if len(y) != len(m) or len(num) != n:
        return False
    mn = matvec(m, num)
    return all(mn[i] == den * y[i] for i in range(len(m)))
