# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""gf2 — exact linear algebra over 𝔽₂ (GF(2)), by mod-2 Gaussian elimination.

The exact-integer math spine (`urdr_math`) works over ℤ (Bareiss rank, integer nullspace); this
is a *different* exact substrate — the two-element field. It is the cleanest exact arithmetic in
the project: bits, no rounding, no overflow, no bound to refuse at. A matrix is a list of rows,
each row a list of 0/1 ints. Used by `toric.py` for 𝔽₂ homology (the toric-code detector)."""


def rank(rows, ncols):
    """Exact rank over 𝔽₂ of the matrix given as 0/1 rows with `ncols` columns."""
    rows = [r[:] for r in rows]
    r = 0
    for c in range(ncols):
        piv = next((i for i in range(r, len(rows)) if rows[i][c]), None)
        if piv is None:
            continue
        rows[r], rows[piv] = rows[piv], rows[r]
        for i in range(len(rows)):
            if i != r and rows[i][c]:
                rows[i] = [a ^ b for a, b in zip(rows[i], rows[r])]
        r += 1
    return r


def nullity(rows, ncols):
    """dim ker over 𝔽₂ = ncols − rank (rank–nullity, exact)."""
    return ncols - rank(rows, ncols)
