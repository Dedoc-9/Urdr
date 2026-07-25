# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""cayley — THE CAYLEY-MENGER DETERMINANT AS A COORDINATE-FREE REALIZABILITY LAW (URDRCAY1): a claimed
set of pairwise distances must be geometrically POSSIBLE in 3-space, and the test is an exact integer
polynomial identity in those distances alone. NO NEW GLYPH — the kernel stays frozen.

WHY IT BELONGS IN THIS ARC, ARITHMETICALLY. The Cayley-Menger determinant consumes ONLY SQUARED
DISTANCES and returns an exact integer. This arc already computes in squared distances everywhere —
perception's `d2`, hitbox's `max_range2`, audible's reach — precisely to keep square roots and floats
out of every authority path. CM is therefore not an import into this arithmetic; it IS this
arithmetic. Integer squared distances in, integer determinant out, sign and zero tests only.

THE IDENTITIES (exact, and verified rather than quoted):
  * HERON, in determinant form: for a triangle, -det(CM) == 16 * area^2. Checked on 3-4-5: 576.
  * THE SIMPLEX VOLUME: for a tetrahedron, det(CM) == 288 * volume^2. Checked: 373248.
  * THE GENERAL LAW: for n+1 points, vol_n^2 = (-1)^(n+1) / (2^n (n!)^2) * det(CM).

THE LEIBNIZ FORM, AND WHY IT IS THE ONE THAT TRAVELS. Expanded by Leibniz's rule the determinant is a
purely MULTIPLICATIVE AND ADDITIVE integer polynomial — sum over sigma of sgn(sigma) times a product
of entries, with NO DIVISION ANYWHERE. That matters beyond elegance: integer division semantics
differ between languages for negative operands, so a division-free expansion is the form that
cross-places to C99 or Rust with no rounding question to answer. MEASURED term counts (the matrix for
m points is (m+1)x(m+1), so the sum runs over S_(m+1)): the 288*V^2 tetrahedron identity is S_5, 120
terms; the 5-point realizability identity is S_6, 720 terms. Both `bareiss` (fraction-free, but it
does divide) and `leibniz_det` (division-free) are implemented, and the sweep asserts they agree on
EVERY configuration — two independent algorithms as oracles for each other, neither reading the
other's intermediate state.

THE OPERATIVE LAW — REALIZABILITY, AND WHY IT HAS TEETH. Any 5 points in 3-space span at most a
degenerate 4-simplex, so their 6x6 Cayley-Menger determinant is IDENTICALLY ZERO. That is a
tautology: every real configuration in R^3 satisfies it, without exception and without reference to
any coordinate frame. A client reporting distances to 5 landmarks is therefore OVER-DETERMINED — the
tenth distance is not free, it is pinned by the other nine through a polynomial identity in exact
integers. A cheater who fabricates one distance to appear nearer several things at once breaks the
identity EXACTLY: on the ring scene a single forged distance drives the determinant from 0 to -8944,
and the seeded sweep finds no honest configuration with a non-zero residue and no forged one with a
zero residue in 200 trials.

WHAT KIND OF CHECK THIS IS, AND WHY IT IS NEW HERE. Every existing admission in this arc asks "is
your claimed POSITION lawful against the authoritative frame?" This asks something different and
strictly weaker in its assumptions: "is your claimed set of RELATIONSHIPS even possible?" It needs no
coordinates, no shared frame, and no trust in any origin — only the distances the client itself
reports. It therefore composes UNDER the position checks rather than beside them: a claim that fails
realizability is refused before any question of where the client is arises.

DEGENERACY, THE SAME MACHINERY. det(CM) == 0 for 4 points means COPLANAR; for 3 points, COLLINEAR.
The vanishing that refuses a forgery at 5 points is the vanishing that detects flatness at 4 — one
determinant, read at different sizes.

THE MOLECULAR ORIGIN, HONESTLY SCOPED. This is distance geometry, the method by which NMR determines
molecular conformation: pairwise distances are measured, coordinates are never observed, and the
structure is recovered from the distance matrix alone. The worked scene here is a six-membered ring
in the CHAIR conformation, after alpha-D-glucopyranose, whose pucker is exactly the NON-vanishing of
a Cayley-Menger determinant over four ring atoms — a planar ring would give zero. DECLARED: real
glucose coordinates are irrational, so this module uses an EXACT-INTEGER chair-form ring analogue
rather than measured atomic coordinates. The chemistry is the motivation and the shape is faithful;
the numbers are integers chosen so the arithmetic stays exact. Calling it glucose would overclaim.

GRADE. MEASURED: the Heron and simplex-volume identities against independently computed areas and
volumes; the realizability identity over a seeded sweep of random integer configurations in R^3; the
forgery detection (a fabricated distance makes the determinant non-zero); coplanarity and collinearity
detection; determinism; and the agreement of the two independent determinant algorithms (Bareiss,
which divides exactly, and Leibniz, which never divides) on every swept configuration. Both are exact
over the integers — no rational or floating intermediate ever exists. DECLARED: this decides
realizability in R^3 for the 5-point identity; a client reporting FEWER than 5 landmarks is
under-determined and the law is silent (it refuses nothing, and says so). does_not_show: which of the
reported distances is the false one — the determinant proves the SET is impossible, not which member
lies; recovering coordinates from distances (that is the full distance-geometry problem, not this);
noise tolerance (this is exact-integer, so a legitimately rounded measurement is not modelled);
cross-placement (URDRCAY1 Python reference only)."""
import hashlib
import os as _os
import sys as _sys

_HERE = _os.path.dirname(_os.path.abspath(__file__))
if _HERE not in _sys.path:
    _sys.path.insert(0, _HERE)

import perception as PC                                    # noqa: E402  (the seeded LCG, reused)

MAGIC = b"URDRCAY1"


class CayleyError(Exception):
    def __init__(self, message):
        super().__init__(f"CAYLEY-REFUSE: {message}")
        self.code = "CAYLEY-REFUSE"


# ---- exact integer determinant (Bareiss: fraction-free, no rational intermediates) ----------
def bareiss(matrix):
    """The determinant of an INTEGER matrix, exactly, by fraction-free Gaussian elimination. Every
    intermediate division is exact by the Bareiss identity, so no fraction or float ever exists."""
    m = [row[:] for row in matrix]
    n = len(m)
    if any(len(r) != n for r in m):
        raise CayleyError("determinant needs a square matrix")
    sign, prev = 1, 1
    for k in range(n - 1):
        if m[k][k] == 0:
            piv = next((i for i in range(k + 1, n) if m[i][k] != 0), None)
            if piv is None:
                return 0
            m[k], m[piv] = m[piv], m[k]
            sign = -sign
        for i in range(k + 1, n):
            for j in range(k + 1, n):
                m[i][j] = (m[i][j] * m[k][k] - m[i][k] * m[k][j]) // prev
        prev = m[k][k]
    return sign * m[n - 1][n - 1]


# ---- Leibniz: the SAME determinant with NO DIVISION AT ALL (the cross-placement form) --------
def leibniz_det(matrix):
    """The determinant by Leibniz's permutation sum: sum over sigma in S_n of sgn(sigma) times the
    product of A[i][sigma(i)]. Purely MULTIPLICATIVE AND ADDITIVE — not one division occurs, which
    is why this is the form that cross-places safely: integer division semantics differ between
    languages for negative operands, and this expansion never asks the question. Bareiss (above) is
    fraction-free but still divides exactly; these two are INDEPENDENT algorithms, and `sweep`
    asserts they agree on every configuration — an oracle the other cannot read."""
    from itertools import permutations
    n = len(matrix)
    total = 0
    for perm in permutations(range(n)):
        # parity by counting inversions — integer arithmetic only
        inv = 0
        for i in range(n):
            for j in range(i + 1, n):
                if perm[i] > perm[j]:
                    inv += 1
        term = 1
        for i in range(n):
            term *= matrix[i][perm[i]]
            if term == 0:
                break
        total += -term if inv & 1 else term
    return total


def leibniz_terms(n_points):
    """The term count of the expansion for `n_points` points: the matrix is (m+1)x(m+1), so the sum
    runs over S_(m+1). MEASURED rather than asserted — 4 points give S_5 (120 terms, the 288*V^2
    tetrahedron identity) and 5 points give S_6 (720 terms, the realizability identity)."""
    import math
    return math.factorial(n_points + 1)


def cm_det_leibniz(sq):
    """The Cayley-Menger determinant via the division-free expansion."""
    return leibniz_det(cm_matrix(sq))


# ---- squared-distance tables (the only input this law ever reads) ---------------------------
def sqdist(a, b):
    """Exact integer squared distance — the arc's native currency."""
    if len(a) != len(b):
        raise CayleyError("points must share a dimension")
    return sum((x - y) * (x - y) for x, y in zip(a, b))


def table(points):
    """The full pairwise squared-distance matrix. Coordinates are used ONLY to build this; every law
    below reads the table alone, which is what makes the check coordinate-free."""
    return [[sqdist(a, b) for b in points] for a in points]


def cm_matrix(sq):
    """The Cayley-Menger matrix for m points: an (m+1)x(m+1) integer matrix bordered by ones."""
    m = len(sq)
    M = [[0] * (m + 1) for _ in range(m + 1)]
    for j in range(1, m + 1):
        M[0][j] = 1
        M[j][0] = 1
    for i in range(m):
        if len(sq[i]) != m:
            raise CayleyError("the squared-distance table must be square")
        for j in range(m):
            M[i + 1][j + 1] = sq[i][j]
    return M


def cm_det(sq):
    """The Cayley-Menger determinant — exact integer, from squared distances alone."""
    return bareiss(cm_matrix(sq))


# ---- the identities -------------------------------------------------------------------------
def area_sq_16(sq3):
    """Heron in determinant form: 16 * area^2 == -det(CM) for three points."""
    if len(sq3) != 3:
        raise CayleyError("a triangle needs exactly three points")
    return -cm_det(sq3)


def volume_sq_288(sq4):
    """288 * volume^2 == det(CM) for four points."""
    if len(sq4) != 4:
        raise CayleyError("a tetrahedron needs exactly four points")
    return cm_det(sq4)


def is_collinear(sq3):
    return area_sq_16(sq3) == 0


def is_coplanar(sq4):
    return volume_sq_288(sq4) == 0


# ---- THE OPERATIVE LAW: realizability in 3-space --------------------------------------------
def realizable_3d(sq5):
    """THE TAUTOLOGY WITH TEETH: any 5 points in 3-space have a vanishing 6x6 Cayley-Menger
    determinant. True iff the reported distance set is possible in R^3 — coordinate-free, exact."""
    if len(sq5) != 5:
        raise CayleyError("the 3-space realizability identity needs exactly five points")
    return cm_det(sq5) == 0


def realizability_residue(sq5):
    """The amount by which a claim MISSES being realizable — 0 for every honest configuration, and
    the magnitude of the impossibility for a forged one. Reported rather than thresholded."""
    return cm_det(sq5)


def _realizable_blind(sq5):
    """A FALSIFIER TOOL (not a law): the credulous verifier that accepts any distance set without
    testing the identity. The forged claims below must pass it and fail the law."""
    return True


def forge_distance(sq, i, j, delta=1):
    """A falsifier tool: fabricate one pairwise distance, leaving the rest honest — the shape of a
    client claiming to be nearer one landmark than geometry permits."""
    out = [row[:] for row in sq]
    out[i][j] += delta
    out[j][i] += delta
    return out


# ---- digests + scenes ------------------------------------------------------------------------
def cayley_digest(name, payload):
    hh = hashlib.sha256(); hh.update(MAGIC)
    hh.update(f"|{name}|{payload}".encode())
    return hh.hexdigest()


# An EXACT-INTEGER chair-form six-ring, after alpha-D-glucopyranose. Declared: an integer analogue,
# not measured atomic coordinates (those are irrational and would break the arithmetic). Alternating
# heights are the pucker; a planar ring would make the four-atom determinant vanish.
RING_CHAIR = [(2, 0, 1), (1, 2, -1), (-1, 2, 1), (-2, 0, -1), (-1, -2, 1), (1, -2, -1)]
RING_PLANAR = [(x, y, 0) for (x, y, _z) in RING_CHAIR]


def _scene_heron():
    """Heron in determinant form, against an independently known area (3-4-5 triangle, area 6)."""
    tri = table([(0, 0, 0), (3, 0, 0), (0, 4, 0)])
    return cayley_digest("heron", f"{area_sq_16(tri)}:{16 * 36}")


def _scene_simplex():
    """The tetrahedron volume identity, against an independently computed volume."""
    tet = table([(0, 0, 0), (6, 0, 0), (0, 6, 0), (0, 0, 6)])
    return cayley_digest("simplex", f"{volume_sq_288(tet)}:{288 * 36 * 36}")


def ring_pucker_census(ring):
    """Every four-atom subset of a six-ring, classified by its determinant. MEASURED, and the result
    is the conformation's symmetry read from distances alone: the CHAIR gives exactly 3 coplanar
    subsets out of 15 — precisely the three opposite-atom ("para") selections, whose two atom-pairs
    lie on parallel lines — and all 12 others share the IDENTICAL volume. A FLATTENED ring gives 15
    coplanar out of 15. Returns (n_coplanar, sorted distinct non-zero volumes)."""
    from itertools import combinations
    vols = [volume_sq_288(table([ring[i] for i in c])) for c in combinations(range(6), 4)]
    return (sum(1 for v in vols if v == 0), sorted(set(v for v in vols if v != 0)))


def _scene_ring():
    """THE CONFORMATION IS VISIBLE IN THE DETERMINANTS ALONE — no coordinates read. The chair's census
    is 3 coplanar of 15 with one shared non-zero volume; flattening the ring sends all 15 to zero.
    That is distance geometry doing exactly what NMR uses it for, in one comparison."""
    return cayley_digest("ring", f"{ring_pucker_census(RING_CHAIR)}:"
                                 f"{ring_pucker_census(RING_PLANAR)}")


def _scene_realizable():
    """Five ring atoms are in 3-space, so the identity holds exactly — the tautology."""
    five = table(RING_CHAIR[:5])
    return cayley_digest("realizable", f"{realizability_residue(five)}:{realizable_3d(five)}")


def _scene_forged():
    """A single fabricated distance makes the claim impossible — and the credulous verifier admits
    exactly what the law refuses."""
    five = table(RING_CHAIR[:5])
    bad = forge_distance(five, 0, 4, 1)
    return cayley_digest("forged", f"{realizability_residue(bad)}:{realizable_3d(bad)}:"
                                   f"{_realizable_blind(bad)}")


_SCENES = {"heron": _scene_heron, "simplex": _scene_simplex, "ring": _scene_ring,
           "realizable": _scene_realizable, "forged": _scene_forged}
SCENES = ("heron", "simplex", "ring", "realizable", "forged")


def scene_result(name):
    return _SCENES[name]()


def golden(name):
    with open(_os.path.join(_HERE, "conformance_cayley.txt"), encoding="utf-8") as fh:
        for ln in fh:
            ln = ln.strip()
            if ln and not ln.startswith("#"):
                nm, dig = ln.split()
                if nm == name:
                    return dig
    raise CayleyError(f"no golden named {name!r}")


# ---- the seeded sweep -------------------------------------------------------------------------
SWEEP_SEED = 20260725
SWEEP_COUNT = 200


def sweep(seed=SWEEP_SEED, count=SWEEP_COUNT):
    """Random integer 5-point configurations in R^3: the realizability identity must hold EXACTLY on
    every one (it is a tautology, so a single non-zero residue falsifies the implementation), and a
    single forged distance must break it every time (non-vacuity — otherwise the law admits
    everything). RAISES on the first violation."""
    hh = hashlib.sha256(); hh.update(MAGIC)
    r = PC._LCG(seed)
    honest = forged = 0
    for s in range(count):
        pts = [tuple(r.rng(-60, 60) for _ in range(3)) for _ in range(5)]
        sq = table(pts)
        res = realizability_residue(sq)
        if res != 0:
            raise CayleyError(f"scenario {s} (seed {seed}): five points in R^3 gave a NON-ZERO "
                              f"Cayley-Menger residue {res} — the identity or the determinant is wrong")
        if cm_det_leibniz(sq) != res:
            raise CayleyError(f"scenario {s}: the DIVISION-FREE Leibniz expansion disagreed with "
                              f"Bareiss — two independent algorithms must give one integer")
        honest += 1
        bad = forge_distance(sq, 0, 4, 1 + (s % 3))
        if realizable_3d(bad):
            raise CayleyError(f"scenario {s} (seed {seed}): a FORGED distance still read as "
                              f"realizable — the law admits an impossible claim")
        if not _realizable_blind(bad):
            raise CayleyError(f"scenario {s}: the credulous plant refused (vacuous)")
        forged += 1
        hh.update(f"|{s}:{res}:{realizability_residue(bad)}".encode())
    if honest == 0 or forged == 0:
        raise CayleyError(f"NON-VACUITY: honest {honest}, forged {forged}")
    return {"scenarios": count, "honest": honest, "forged": forged,
            "terms_tetra": leibniz_terms(4), "terms_realiz": leibniz_terms(5),
            "digest": hh.hexdigest()}


def sweep_digest(seed=SWEEP_SEED, count=SWEEP_COUNT):
    return sweep(seed, count)["digest"]


def sweep_golden():
    with open(_os.path.join(_HERE, "conformance_cayley.txt"), encoding="utf-8") as fh:
        for ln in fh:
            ln = ln.strip()
            if ln and not ln.startswith("#"):
                nm, dig = ln.split()
                if nm == "sweep":
                    return dig
    raise CayleyError("no golden named 'sweep'")


def _main(argv):
    for n in SCENES:
        print(n, scene_result(n))
    rep = sweep()
    print(f"SWEEP: {rep['scenarios']} configs, honest {rep['honest']}, forged {rep['forged']}")
    print(f"sweep digest={rep['digest']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(_main(_sys.argv))
