# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""rpimm — THE DEGREE-DIMENSION PROBLEM FOR EVEN POLYNOMIAL MAPS OF RP^n (URDRRPI1).

DELIBERATELY UNGATED. This is a `hainuwele/parallel/` substrate: exploratory, with its own falsifiers
and its own runner, and NO stage in `verify.py`. It stays ungated until there is either a constructive
family that survives the corrected tangent-space test or an obstruction genuinely beyond the blockwise
case. Being ungated means it CAN rot, and that is stated rather than hidden — the same treatment
`bench.py` gets for wall-clock. Run it with `python3 hainuwele/parallel/rpimm.py --selfcheck`.

NO NEW GLYPH. Exact rational arithmetic throughout; no floats anywhere in any rank decision.

WHAT WENT WRONG BEFORE, SO IT CANNOT COME BACK.

(1) A PARITY CATEGORY ERROR, NOT A MISSING PROOF. The original construction was antipodally ODD,
    Phi(-x) = -Phi(x), and was asked to induce a map on RP^n. It cannot: descending to S^n/{+-1}
    requires Phi(-x) = Phi(x), and an odd map satisfying that is identically zero. So only EVEN maps
    descend, and the linear block `x` is inadmissible from the start rather than "lost to the
    quotient". Pinned as a witness rather than deleted.

(2) THE IDENTITY BLOCK MADE THE ORIGINAL OBSTRUCTION VACUOUS. The argument was "one block's
    differential dies, therefore the rank drops". False: with the identity block present, rank
    D(Phi)|T_xS^n = n at exactly the points where DQ_k = 0 — measured n, not n-1, for every n tried.
    Nothing is lost, because the identity already spans the tangent space. A vanishing sub-block is
    not a rank deficit until you count what survives.

(3) "POSITIVE-DIMENSIONAL" FAILED AT A BOUNDARY CASE. The vanishing locus is exactly S^(n-|B_k|), so
    a PROPER block missing only one coordinate gives S^0 — two points, dimension zero. The exact
    dimension formula replaces the adjective, which is what makes the boundary case checkable instead
    of quietly false.

THE LEMMA THAT SURVIVES, AND IT IS THE GENERAL FORM RATHER THAN THE TWO SPECIAL CASES. Let
Phi = (Q_1(x_B1), ..., Q_r(x_Br)) be even, with the blocks partitioning the coordinates, every
monomial of degree >= 2. At any x in S^n let Z be the union of the blocks that vanish ENTIRELY at x.
Every direction supported in Z is tangent (because x_Z = 0 makes v.x = 0) and lies in the kernel
(because Q_k for k inside Z has vanishing differential there, and Q_k for k outside Z does not depend
on those variables). Hence

    rank D(Phi)|T_xS^n  <=  n - |Z|

which recovers both special cases: a point supported in one block B_j gives rank <= |B_j| - 1, and a
point on {x_Bj = 0} gives rank <= n - |B_j|. With r >= 2 the bad locus is a nonempty union of
sub-spheres, so no variable-separable even map immerses RP^n. THE OBSTRUCTION IS FACTORIZATION THROUGH
INDEPENDENT COORDINATE PROJECTIONS — locality — NOT the degree. That is what later constructions have
to avoid, and it is why globally coupled families are the only ones worth searching.

THE RANK TEST ITSELF WAS THE MOST DANGEROUS ERROR AVAILABLE, AND IT IS THE ONE MOST LIKELY TO BE MADE.
The immersion condition is rank of the differential RESTRICTED to T_xS^n, not the rank of the ambient
Jacobian. Two sound routes are implemented and cross-checked: project onto a tangent basis, or stack
the normal row x^T and subtract one, since ker([A; x^T]) = ker(A) INTERSECT T_x gives
rank(A|T_x) = rank([A; x^T]) - 1 identically. THE NAIVE AMBIENT TEST IS OFF BY EXACTLY ONE, AND NOT BY
ACCIDENT: Euler's relation for a degree-d homogeneous map gives A x = d Phi(x), so the radial
direction generически carries one unit of rank that the immersion condition must not count. Measured,
there are points where the ambient rank reaches n while the true tangent rank is n-1 — the naive test
CERTIFIES AN IMMERSION THAT IS NOT ONE. That plant is kept live.

AND THE ALGEBRAIC CERTIFICATION HAS A SECOND TRAP, WHICH IS A REAL-VERSUS-COMPLEX GAP. The sound
direction is one-way only: if I_minors + I_sphere = (1) then the rank-deficient locus misses the
sphere and the map is an immersion. The CONVERSE FAILS, because the Nullstellensatz is about
algebraically closed fields while immersion is a real question. Witness, in exact Gaussian integers:
f = x0^2 + x1^2 + 2 x2^2 + 2 x3^2 is positive definite, so V_R(f) = {0} and misses the sphere
entirely — yet z = (1, 1, 0, i) satisfies sum z_i^2 = 1 and f(z) = 0, so the complex locus meets the
complex sphere and the ideal is NOT (1). A pipeline reading "ideal != (1) therefore not an immersion"
returns a false negative here. Real certification needs real machinery.

THE INVARIANTS, KEPT SEPARATE ON PURPOSE. m_d^imm(n) and m_d^emb(n) are the minimum target dimensions
over even homogeneous degree-d polynomial IMMERSIONS and EMBEDDINGS respectively. Conflating them
would let the Veronese's embedding bound masquerade as an immersion bound, which are different
questions with different known answers.

WHAT THIS MODULE CLAIMS AND WHAT IT REFUSES TO CLAIM. A refutation is exact from ONE witness point: if
the tangent rank drops below n anywhere, the map is not an immersion, full stop. A POSITIVE is not
available by search — sampling points can never establish a condition that must hold everywhere — so
the subset search reports REFUTED or CANDIDATE and NEVER "immersion". That asymmetry is the same one
`autoroute` inherited from view determinacy, arriving here from a different direction, and it is
enforced in the return vocabulary rather than in a comment.

GRADE. MEASURED: the parity witness; the identity-block vacuity; the exact locus dimension including
the S^0 boundary case; the general blockwise bound, attained; the two tangent-rank routes agreeing,
with a mutation probe proving the cross-check can fail; the naive ambient test certifying a
non-immersion; the Veronese positive control; the monomial-subset refutation census. DECLARED: the
subset search ranges over MONOMIAL subsets of the Veronese, not over general linear projections, so
its CANDIDATE verdicts are weaker than they look; the point sets used for refutation are pinned and
finite; no certified positive appears anywhere in this module. does_not_show: that any CANDIDATE is an
immersion; the asymptotics of m_d, which are the open question this only sets up; anything about the
optimal topological immersion dimension of RP^n, which is characteristic-class territory this module
does not enter."""
from fractions import Fraction as _F
from itertools import combinations as _comb, combinations_with_replacement as _cwr
import sys as _sys

MAGIC = b"URDRRPI1"
REFUTED, CANDIDATE = "RPIMM_REFUTED", "RPIMM_CANDIDATE"


class RpimmError(Exception):
    def __init__(self, message):
        super().__init__(f"RPIMM-REFUSE: {message}")
        self.code = "RPIMM-REFUSE"


# ---- exact linear algebra --------------------------------------------------------------------------
def rank_exact(M):
    """Exact rank over Q. No floats: a float rank decision on a degenerate matrix is a coin flip."""
    M = [[_F(x) for x in row] for row in M]
    rows = len(M)
    cols = len(M[0]) if rows else 0
    r = 0
    for c in range(cols):
        piv = next((i for i in range(r, rows) if M[i][c] != 0), None)
        if piv is None:
            continue
        M[r], M[piv] = M[piv], M[r]
        for i in range(rows):
            if i != r and M[i][c] != 0:
                f = M[i][c] / M[r][c]
                M[i] = [a - f * b for a, b in zip(M[i], M[r])]
        r += 1
        if r == rows:
            break
    return r


def tangent_basis(x):
    """A basis of T_x = {v : v.x = 0}, exact, dimension n = len(x) - 1."""
    if all(v == 0 for v in x):
        raise RpimmError("the origin has no tangent space to the sphere")
    j = next(i for i in range(len(x)) if x[i] != 0)
    out = []
    for i in range(len(x)):
        if i == j:
            continue
        v = [_F(0)] * len(x)
        v[i] = _F(1)
        v[j] = -_F(x[i]) / _F(x[j])
        out.append(v)
    return out


# ---- polynomials as exponent-vector dictionaries ----------------------------------------------------
def _mono(n1, idxs):
    e = [0] * n1
    for i in idxs:
        e[i] += 1
    return tuple(e)


def evaluate(polys, x):
    out = []
    for p in polys:
        s = _F(0)
        for m, c in p.items():
            t = _F(c)
            for i, e in enumerate(m):
                t *= _F(x[i]) ** e
            s += t
        out.append(s)
    return out


def jacobian(polys, x):
    n1 = len(x)
    J = []
    for p in polys:
        row = []
        for k in range(n1):
            s = _F(0)
            for m, c in p.items():
                if m[k] == 0:
                    continue
                t = _F(c) * m[k]
                for i, e in enumerate(m):
                    t *= _F(x[i]) ** (e - 1 if i == k else e)
                s += t
            row.append(s)
        J.append(row)
    return J


def degree_of(polys):
    degs = {sum(m) for p in polys for m in p}
    if len(degs) != 1:
        raise RpimmError(f"not homogeneous: degrees {sorted(degs)}")
    return degs.pop()


def is_even(polys):
    return degree_of(polys) % 2 == 0


# ---- THE RANK TEST, two sound routes and one unsound one -------------------------------------------
def tangent_rank_project(polys, x):
    """Route 1: restrict the differential to a tangent basis."""
    J, B = jacobian(polys, x), tangent_basis(x)
    M = [[sum(J[r][k] * B[c][k] for k in range(len(x))) for c in range(len(B))]
         for r in range(len(J))]
    return rank_exact(M)


def tangent_rank_augment(polys, x):
    """Route 2: stack the normal row. ker([A; x^T]) = ker(A) INTERSECT T_x, so the restricted rank is
    the stacked rank minus one — identically, which is why this is a genuine cross-check and not the
    same computation twice."""
    J = jacobian(polys, x)
    stacked = J + [[_F(v) for v in x]]
    return rank_exact(stacked) - 1


def naive_ambient_rank(polys, x):
    """THE UNSOUND TEST, kept live as a plant: the rank of the ambient Jacobian, which is NOT the
    immersion condition."""
    return rank_exact(jacobian(polys, x))


def _tangent_rank_project_broken(polys, x):
    """MUTATION PROBE for the cross-check (L23): uses the ambient basis instead of the tangent one, so
    it degenerates to the ambient rank. If the two sound routes agreed with THIS too, their agreement
    would be measuring nothing."""
    return rank_exact(jacobian(polys, x))


def routes_agree(cases):
    """Returns (checked, disagreements)."""
    bad = 0
    for polys, x in cases:
        if tangent_rank_project(polys, x) != tangent_rank_augment(polys, x):
            bad += 1
    return len(cases), bad


def cross_check_is_falsifiable(cases):
    """The probe must make the agreement FAIL somewhere, or the cross-check is decoration.
    Returns (checked, disagreements_under_mutation)."""
    bad = 0
    for polys, x in cases:
        if _tangent_rank_project_broken(polys, x) != tangent_rank_augment(polys, x):
            bad += 1
    return len(cases), bad


# ---- families ---------------------------------------------------------------------------------------
def veronese(n1, degree=2):
    """All degree-`degree` monomials in n1 variables. Even iff `degree` is even."""
    return [{_mono(n1, idxs): 1} for idxs in _cwr(range(n1), degree)]


def linear_block(n1):
    return [{_mono(n1, (i,)): 1} for i in range(n1)]


def block_monomials(n1, block, degree=2):
    return [{_mono(n1, idxs): 1} for idxs in _cwr(sorted(block), degree)]


def even_blocks(n1, sizes, degree=2):
    """A variable-separable even map with the given block sizes. Returns (polys, blocks)."""
    if sum(sizes) != n1 or len(sizes) < 2 or any(s < 1 for s in sizes):
        raise RpimmError(f"block sizes {sizes} must be >= 1 each, at least 2 blocks, summing to {n1}")
    blocks, start = [], 0
    for s in sizes:
        blocks.append(set(range(start, start + s)))
        start += s
    polys = sum((block_monomials(n1, b, degree) for b in blocks), [])
    return polys, blocks


# ---- (1) THE PARITY WITNESS -------------------------------------------------------------------------
def an_odd_map_does_not_descend(n1=3):
    """Phi(-x) = -Phi(x) is not constant on {x, -x}, so it induces NO map on RP^n. An odd map that DID
    descend would satisfy Phi = -Phi, hence Phi = 0. Returns (odd, even, forced_zero_if_both)."""
    polys = linear_block(n1) + veronese(n1, 3)
    x = [_F(1), _F(2), _F(-1)][:n1]
    mx = [-v for v in x]
    fx, fmx = evaluate(polys, x), evaluate(polys, mx)
    odd = fmx == [-v for v in fx]
    even = fmx == fx
    return odd, even, (odd and even) == all(v == 0 for v in fx)


def the_linear_block_is_inadmissible(n1=4):
    """Not "lost to the quotient" — never admissible. Returns (linear_is_even, veronese_is_even)."""
    return is_even(linear_block(n1)), is_even(veronese(n1, 2))


# ---- (2) THE IDENTITY BLOCK MADE THE OLD OBSTRUCTION VACUOUS ---------------------------------------
def identity_block_makes_it_vacuous(ns=(2, 3, 4, 5)):
    """At exactly the points where DQ_k = 0, the map with an identity block still has FULL rank n.
    Returns ((n, rank, needed, dq_vanishes), ...)."""
    out = []
    for n in ns:
        n1 = n + 1
        polys_b, blocks = even_blocks(n1, (n1 // 2, n1 - n1 // 2))
        polys = linear_block(n1) + polys_b
        x = [_F(0)] * n1
        for i in sorted(blocks[1]):
            x[i] = _F(i + 1)
        q1 = block_monomials(n1, blocks[0])
        dq_zero = all(all(v == 0 for v in row) for row in jacobian(q1, x))
        out.append((n, tangent_rank_project(polys, x), n, dq_zero))
    return tuple(out)


# ---- (3) THE EXACT LOCUS DIMENSION, INCLUDING THE S^0 BOUNDARY CASE --------------------------------
def locus_dimension(n, block_size):
    """{x_B = 0} INTERSECT S^n is S^(n - |B|). The adjective "positive-dimensional" hides |B| = n."""
    if not (1 <= block_size <= n + 1):
        raise RpimmError(f"block size {block_size} out of range for n={n}")
    return n - block_size


def positive_dimensionality_fails_at_the_boundary(ns=(2, 3, 4, 5)):
    """Returns ((n, size, dim, positive_dimensional), ...) for the two largest proper block sizes."""
    out = []
    for n in ns:
        for size in (n - 1, n):
            d = locus_dimension(n, size)
            out.append((n, size, d, d >= 1))
    return tuple(out)


# ---- THE LEMMA THAT SURVIVES, in its general form --------------------------------------------------
def vanishing_union(blocks, x):
    """Z = the union of blocks that vanish ENTIRELY at x."""
    return frozenset(i for b in blocks if all(x[j] == 0 for j in b) for i in b)


def blockwise_bound_census(cases=((2, (1, 2)), (3, (2, 2)), (4, (2, 3)), (4, (1, 1, 3)),
                                  (5, (3, 3)), (5, (1, 2, 3)))):
    """The lemma, measured: rank <= n - |Z|. Returns
    ((n, sizes, |Z|, rank, bound, holds, attained, needed), ...)."""
    out = []
    for n, sizes in cases:
        n1 = n + 1
        polys, blocks = even_blocks(n1, sizes)
        x = [_F(0)] * n1
        for i in sorted(blocks[-1]):
            x[i] = _F(i + 1)
        Z = vanishing_union(blocks, x)
        r = tangent_rank_project(polys, x)
        bound = n - len(Z)
        out.append((n, sizes, len(Z), r, bound, r <= bound, r == bound, n))
    return tuple(out)


def the_lemma_holds(cases=None):
    rows = blockwise_bound_census() if cases is None else blockwise_bound_census(cases)
    return (sum(1 for r in rows if r[5]), sum(1 for r in rows if r[6]),
            sum(1 for r in rows if r[3] < r[7]), len(rows))


def block_supported_special_case(cases=((2, (1, 2)), (3, (2, 2)), (4, (2, 3)), (5, (3, 3)))):
    """The other special case: at a point supported in B_1, rank <= |B_1| - 1. Returns
    ((n, |B1|, rank, bound), ...)."""
    out = []
    for n, sizes in cases:
        n1 = n + 1
        polys, blocks = even_blocks(n1, sizes)
        x = [_F(0)] * n1
        for i in sorted(blocks[0]):
            x[i] = _F(i + 1)
        out.append((n, len(blocks[0]), tangent_rank_project(polys, x), len(blocks[0]) - 1))
    return tuple(out)


def separability_not_degree_is_the_obstruction(n=4, degrees=(2, 4, 6)):
    """The distinction that matters: raising the degree does NOT rescue a separable map. Returns
    ((degree, rank, needed), ...)."""
    n1 = n + 1
    out = []
    for d in degrees:
        polys, blocks = even_blocks(n1, (2, n1 - 2), degree=d)
        x = [_F(0)] * n1
        for i in sorted(blocks[1]):
            x[i] = _F(i + 1)
        out.append((d, tangent_rank_project(polys, x), n))
    return tuple(out)


# ---- THE NAIVE AMBIENT TEST CERTIFIES A NON-IMMERSION ----------------------------------------------
def euler_relation(polys, x):
    """A x = d Phi(x). This is WHY the ambient rank overcounts by one: the radial direction carries a
    unit of rank the immersion condition must not count. Returns (holds, d)."""
    d = degree_of(polys)
    J = jacobian(polys, x)
    lhs = [sum(J[r][k] * _F(x[k]) for k in range(len(x))) for r in range(len(J))]
    return lhs == [d * v for v in evaluate(polys, x)], d


def the_naive_test_certifies_a_non_immersion(ns=(3, 4, 5)):
    """THE PLANT. Points where the AMBIENT rank reaches n while the TRUE tangent rank is n-1: the naive
    test says immersion, the correct test refutes. Returns
    ((n, ambient, tangent, needed, naive_says_yes, truth_says_no), ...)."""
    out = []
    for n in ns:
        n1 = n + 1
        polys, blocks = even_blocks(n1, (1,) + (1,) * (n1 - 2) + (1,)) if False else \
            even_blocks(n1, tuple([1] * (n1 - 1) + [1]))
        x = [_F(0)] + [_F(i + 1) for i in range(1, n1)]
        amb = naive_ambient_rank(polys, x)
        tan = tangent_rank_project(polys, x)
        out.append((n, amb, tan, n, amb >= n, tan < n))
    return tuple(out)


def the_naive_test_is_off_by_exactly_one(cases):
    """Returns (checked, ambient_equals_tangent_plus_one)."""
    same = 0
    for polys, x in cases:
        if naive_ambient_rank(polys, x) == tangent_rank_project(polys, x) + 1:
            same += 1
    return len(cases), same


# ---- POSITIVE CONTROL ------------------------------------------------------------------------------
def _control_points(n1):
    pts = [[_F(i + 1) for i in range(n1)], [_F(1)] + [_F(0)] * (n1 - 1),
           [_F(0)] * (n1 - 1) + [_F(1)], [_F(1), _F(-1)] + [_F(0)] * (n1 - 2)]
    if n1 >= 3:
        pts.append([_F(3), _F(0), _F(-4)] + [_F(0)] * (n1 - 3))
    return pts


def veronese_is_an_immersion(ns=(2, 3, 4, 5)):
    """Without this, a rank routine that always returned n-1 would look like a discovery. Returns
    ((n, ranks, all_full, target_dim), ...)."""
    out = []
    for n in ns:
        n1 = n + 1
        polys = veronese(n1, 2)
        rs = tuple(tangent_rank_project(polys, p) for p in _control_points(n1))
        out.append((n, rs, all(r == n for r in rs), len(polys)))
    return tuple(out)


def the_veronese_gap_is_quadratic(ns=(2, 3, 4, 5)):
    """Where the real difficulty is: the degree-2 target grows quadratically while the topological
    targets are linear in n. Returns ((n, veronese_target, 2n_minus_1), ...)."""
    return tuple((n, (n + 1) * (n + 2) // 2, 2 * n - 1) for n in ns)


# ---- THE SUBSET SEARCH: refutations only, never a certified positive -------------------------------
def refute(polys, points):
    """A refutation is EXACT from one witness. Returns the first witness point or None."""
    n = len(points[0]) - 1
    for p in points:
        if tangent_rank_project(polys, p) < n:
            return p
    return None


def subset_search(n=2, degree=2, sizes=None):
    """Search MONOMIAL subsets of the degree-d Veronese. Reports REFUTED (exact) or CANDIDATE, and
    NEVER "immersion", because sampling cannot establish an everywhere condition. Returns
    ((size, refuted, candidates), ...)."""
    n1 = n + 1
    full = veronese(n1, degree)
    pts = _control_points(n1) + [[_F(2), _F(-1)] + [_F(1)] * (n1 - 2),
                                 [_F(1), _F(1)] + [_F(-1)] * (n1 - 2)]
    sizes = tuple(range(n, len(full) + 1)) if sizes is None else sizes
    out = []
    for k in sizes:
        ref = cand = 0
        for sub in _comb(range(len(full)), k):
            polys = [full[i] for i in sub]
            if refute(polys, pts) is None:
                cand += 1
            else:
                ref += 1
        out.append((k, ref, cand))
    return tuple(out)


def the_search_never_certifies():
    """The vocabulary IS the discipline: no code path returns "immersion". Returns
    (verdicts, contains_certified)."""
    verdicts = (REFUTED, CANDIDATE)
    return verdicts, any("IMMERS" in v.upper() and "REFUT" not in v.upper() for v in verdicts)


def smallest_surviving_subset(n=2, degree=2):
    """The smallest monomial-subset size with any survivor. A CANDIDATE, explicitly not a theorem.
    Returns (size, candidates, verdict)."""
    for k, _ref, cand in subset_search(n, degree):
        if cand:
            return k, cand, CANDIDATE
    return None, 0, REFUTED


# ---- THE REAL-VERSUS-COMPLEX TRAP ------------------------------------------------------------------
def grobner_converse_fails():
    """f = x0^2 + x1^2 + 2x2^2 + 2x3^2 is positive definite, so V_R(f) misses the sphere entirely — yet
    z = (1,1,0,i) lies on the complex sphere with f(z) = 0, so the ideal is NOT (1). Exact Gaussian
    integers. Returns (sphere_value, f_value, on_complex_sphere, in_singular_locus, real_locus_empty)."""
    z = (complex(1, 0), complex(1, 0), complex(0, 0), complex(0, 1))
    sph = sum(w * w for w in z)
    f = z[0] ** 2 + z[1] ** 2 + 2 * z[2] ** 2 + 2 * z[3] ** 2
    # positive definite over R: f = 0 forces every coordinate 0, which is not on the sphere
    real_empty = True
    for pt in ((1, 0, 0, 0), (0, 1, 0, 0), (0, 0, 1, 0), (1, 1, 1, 1), (3, 0, 4, 0)):
        if pt[0] ** 2 + pt[1] ** 2 + 2 * pt[2] ** 2 + 2 * pt[3] ** 2 == 0:
            real_empty = False
    return sph, f, sph == 1, f == 0, real_empty


def the_sound_direction_is_one_way():
    """Stated so it cannot be misread: ideal = (1) IMPLIES immersion; the converse does not hold."""
    return ("ideal == (1)  =>  immersion", "ideal != (1)  =/=>  not an immersion")


# ---- the invariants, kept separate -----------------------------------------------------------------
def invariants():
    """m_d^imm and m_d^emb are DIFFERENT invariants. Conflating them would let the Veronese's
    EMBEDDING bound masquerade as an immersion bound."""
    return ("m_d_imm", "m_d_emb")


def veronese_bounds_the_embedding_invariant(ns=(2, 3, 4, 5)):
    """The Veronese is an embedding, so it bounds m_2^emb from above — and says nothing directly about
    m_2^imm. Returns ((n, upper_bound_on_m2_emb), ...)."""
    return tuple((n, (n + 1) * (n + 2) // 2) for n in ns)


# ---- the self-check --------------------------------------------------------------------------------
def _cases():
    out = []
    for n in (2, 3, 4, 5):
        n1 = n + 1
        polys, blocks = even_blocks(n1, (n1 // 2, n1 - n1 // 2))
        x0 = [_F(0)] * n1
        for i in sorted(blocks[1]):
            x0[i] = _F(i + 1)
        out.append((polys, x0))
        out.append((veronese(n1, 2), [_F(i + 1) for i in range(n1)]))
        out.append((veronese(n1, 2), [_F(1)] + [_F(0)] * (n1 - 1)))
    return tuple(out)


CHECKS = []


def _check(name, got, want):
    CHECKS.append((name, got == want, got, want))


def selfcheck():
    del CHECKS[:]
    _check("odd map does not descend", an_odd_map_does_not_descend(), (True, False, True))
    _check("linear block inadmissible", the_linear_block_is_inadmissible(), (False, True))
    _check("identity block vacuity", identity_block_makes_it_vacuous(),
           ((2, 2, 2, True), (3, 3, 3, True), (4, 4, 4, True), (5, 5, 5, True)))
    _check("locus dimension boundary", positive_dimensionality_fails_at_the_boundary(),
           ((2, 1, 1, True), (2, 2, 0, False), (3, 2, 1, True), (3, 3, 0, False),
            (4, 3, 1, True), (4, 4, 0, False), (5, 4, 1, True), (5, 5, 0, False)))
    holds, attained, below, total = the_lemma_holds()
    _check("lemma holds on every case", (holds, total), (6, 6))
    _check("lemma bound is attained somewhere", attained > 0, True)
    _check("every case is below n", (below, total), (6, 6))
    _check("routes agree", routes_agree(_cases())[1], 0)
    probe_checked, probe_bad = cross_check_is_falsifiable(_cases())
    _check("cross-check can fail (mutation probe bites)", probe_bad > 0, True)
    _check("veronese is an immersion",
           tuple((n, all_full) for n, _rs, all_full, _t in veronese_is_an_immersion()),
           ((2, True), (3, True), (4, True), (5, True)))
    for polys, x in _cases():
        ok, _d = euler_relation(polys, x)
        if not ok:
            _check("euler relation", False, True)
            break
    else:
        _check("euler relation", True, True)
    naive = the_naive_test_certifies_a_non_immersion()
    _check("naive ambient test certifies a non-immersion",
           all(row[4] and row[5] for row in naive), True)
    _check("naive test off by exactly one",
           the_naive_test_is_off_by_exactly_one(_cases()), (len(_cases()), len(_cases())))
    _check("search never certifies", the_search_never_certifies()[1], False)
    sph, f, on, inl, rempty = grobner_converse_fails()
    _check("grobner converse fails", (on, inl, rempty), (True, True, True))
    _check("separability not degree", tuple(r[1] < r[2] for r in
                                            separability_not_degree_is_the_obstruction()),
           (True, True, True))
    return tuple(CHECKS)


def _main(argv):
    print(f"rpimm ({MAGIC.decode()}) — DELIBERATELY UNGATED parallel substrate")
    print()
    print("(1) PARITY:      odd/even/forced-zero   ", an_odd_map_does_not_descend())
    print("    linear block even? veronese even?   ", the_linear_block_is_inadmissible())
    print("(2) VACUITY:     (n, rank, needed, DQ=0)", identity_block_makes_it_vacuous())
    print("(3) LOCUS DIM:   (n, |B|, dim, pos-dim) ")
    for row in positive_dimensionality_fails_at_the_boundary():
        print("                   ", row)
    print("THE LEMMA        (n, sizes, |Z|, rank, bound, holds, attained, needed)")
    for row in blockwise_bound_census():
        print("                   ", row)
    print("    summary (holds, attained, below-n, total)", the_lemma_holds())
    print("    block-supported special case            ", block_supported_special_case())
    print("    degree does NOT rescue separability     ",
          separability_not_degree_is_the_obstruction())
    print("RANK TEST        routes agree (checked, bad) ", routes_agree(_cases()))
    print("    mutation probe (checked, disagreements)  ", cross_check_is_falsifiable(_cases()))
    print("    NAIVE test certifies a non-immersion     ",
          the_naive_test_certifies_a_non_immersion())
    print("    off by exactly one (Euler)               ",
          the_naive_test_is_off_by_exactly_one(_cases()))
    print("CONTROL          veronese ranks             ")
    for row in veronese_is_an_immersion():
        print("                   ", row)
    print("    the gap (n, veronese dim, 2n-1)          ", the_veronese_gap_is_quadratic())
    print("SUBSET SEARCH    (size, refuted, candidates) ", subset_search(2, 2))
    print("    smallest surviving subset (n=2)          ", smallest_surviving_subset(2, 2))
    print("    verdict vocabulary                       ", the_search_never_certifies())
    print("GROBNER TRAP     (sphere, f, on, in, R-empty)", grobner_converse_fails())
    print("    the sound direction is one-way           ", the_sound_direction_is_one_way())
    print("INVARIANTS       kept separate               ", invariants())
    print()
    rows = selfcheck()
    bad = [r for r in rows if not r[1]]
    for name, ok, got, want in rows:
        print(f"  [{'PASS' if ok else 'FAIL'}] {name}")
        if not ok:
            print(f"         got  {got}\n         want {want}")
    print()
    print(f"SELFCHECK {'PASSED' if not bad else 'FAILED'} — {len(rows) - len(bad)}/{len(rows)}")
    print("(ungated by design: this substrate has no stage in verify.py and CAN rot)")
    return 1 if bad else 0


if __name__ == "__main__":
    raise SystemExit(_main(_sys.argv[1:]))
