# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""persim — persistent homology: the barcode of a filtered simplicial complex, over F2.

A detector under D17. A filtered complex is a sequence of simplices, each with a filtration value,
where every face precedes its coface and has a filtration value no larger (monotonicity — the
domain check). The standard persistence algorithm reduces the F2 boundary matrix column by column:
a column reducing to empty is a creator (a homology class is born); a column with a surviving
lowest row is a destroyer (it kills the class born at that row). The (birth, death) pairs, read as
filtration values, are the barcode; unkilled creators are infinite bars. `b_d` = the count of
infinite bars in dimension d (the Betti number).

The invariant is the barcode. A different input gives a different barcode unless the filtered
complexes have the same persistence; reordering simplices within one filtration value gives the
same barcode; a non-monotone filtration is `PH-REFUSE`d. The barcode is exact over F2.

Scope: the equivalence checked is exact barcode equality. This detector does NOT claim metric
stability (that a small input perturbation moves the barcode a bounded amount in bottleneck
distance); that is a separate theorem, not computed here. It certifies the barcode of a given
complex; it is not wired into any tick loop and stores no per-frame reduction. Grade: MEASURED
(reference); cross-placement declared."""
import hashlib
import os as _os

MAGIC = b"URDRPH01"
_HERE = _os.path.dirname(_os.path.abspath(__file__))


class PersimError(Exception):
    def __init__(self, code, message):
        super().__init__(f"{code}: {message}")
        self.code = code


# ---- a filtered complex: a list of simplices `(dim, filt, [face indices earlier in the list])` --
def is_monotone(S):
    """Membership in Dom: every face precedes its coface and has filtration ≤ it (a valid filtration)."""
    for j, (d, f, faces) in enumerate(S):
        if len(faces) != d + 1 and d > 0:                   # a d-simplex has d+1 facets
            return False
        for i in faces:
            if i >= j or S[i][1] > f or S[i][0] != d - 1:
                return False
    return True


def _reduce(S, do_reduce=True):
    """The F2 boundary-matrix reduction. Returns (cols, low) where `cols[j]` is the reduced
    column (a set of row indices, mod 2) and `low[r] = j` records that column `j` owns lowest row
    `r`. `do_reduce=False` is THE DEFECT — it pairs by the RAW lowest row without reducing
    collisions, so colliding lows mispair (a wrong barcode)."""
    n = len(S)
    cols = [set(faces) for (_, _, faces) in S]
    low = {}
    for j in range(n):
        while cols[j]:
            r = max(cols[j])
            if r in low and do_reduce:
                cols[j] ^= cols[low[r]]
            else:
                low[r] = j
                break
    return cols, low


def persistence(S, do_reduce=True):
    """The persistence barcode of the filtered complex `S`: a sorted list of
    `(dim, birth_filt, death_filt | None)` intervals (`None` = an infinite bar). Refuses
    `PH-REFUSE` if `S` is not a valid monotone filtration."""
    if not is_monotone(S):
        raise PersimError("PH-REFUSE", "not a valid monotone filtration")
    cols, low = _reduce(S, do_reduce)
    killed = set(low.keys())                                # birth simplices later destroyed
    bars = []
    for r, j in low.items():                                # (birth simplex r, death column j)
        bars.append((S[r][0], S[r][1], S[j][1]))
    for j in range(len(S)):                                 # creators never killed → infinite bars
        if not cols[j] and j not in killed:
            bars.append((S[j][0], S[j][1], None))
    return sorted(bars, key=lambda x: (x[0], x[1], (x[2] is None, x[2] if x[2] is not None else 0)))


def persistence_defect(S):
    """THE DEFECT (D17 non-invariance): reduce nothing, so colliding lows mispair → a wrong barcode."""
    return persistence(S, do_reduce=False)


def betti(bars):
    """Betti numbers from the barcode: `b_d` = number of infinite bars in dimension `d`."""
    b = {}
    for (dim, _birth, death) in bars:
        if death is None:
            b[dim] = b.get(dim, 0) + 1
    return b


def barcode_digest(bars):
    """The witness digest — SHA-256 over the sorted barcode (independently recomputable from `S`)."""
    h = hashlib.sha256(); h.update(MAGIC)
    for (dim, b, d) in bars:
        h.update(bytes([dim]))
        h.update(str(b).encode()); h.update(b"|")
        h.update((str(d) if d is not None else "inf").encode()); h.update(b";")
    return h.hexdigest()


# ---- scenarios (pinned by the gate) -------------------------------------------------
def circle():
    """A 4-cycle: 4 vertices at t=0, 4 edges at t=1. Barcode: H₀ = one ∞ bar + three [0,1) bars;
    H₁ = one ∞ bar (the loop is never filled). The canonical persistence example."""
    S = [(0, 0, []) for _ in range(4)]
    for (a, b) in [(0, 1), (1, 2), (2, 3), (3, 0)]:
        S.append((1, 1, [a, b]))
    return S


def disk():
    """A filled triangle: 3 vertices (t=0), 3 edges (t=1), 1 triangle (t=2). The H₁ loop born at
    t=1 is KILLED at t=2 by the 2-cell → a FINITE H₁ bar [1,2). Distinguishes disk from circle."""
    S = [(0, 0, []) for _ in range(3)]
    e = {}
    for k, (a, b) in enumerate([(0, 1), (1, 2), (0, 2)]):
        e[(a, b)] = 3 + k; S.append((1, 1, [a, b]))
    S.append((2, 2, [e[(0, 1)], e[(1, 2)], e[(0, 2)]]))
    return S


def golden(name):
    with open(_os.path.join(_HERE, "conformance_persim.txt"), encoding="utf-8") as fh:
        for ln in fh:
            ln = ln.strip()
            if ln and not ln.startswith("#"):
                nm, dig = ln.split()
                if nm == name:
                    return dig
    raise PersimError("PH-REFUSE", f"no golden named {name!r}")
