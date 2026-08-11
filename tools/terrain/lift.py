# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""lift — HOW MUCH OF A CERTIFIED IDENTITY SURVIVES BEING CARRIED INTO A RICHER REPRESENTATION
(URDRLFT1). A measurement family, deliberately with NO assumed functional form.

THE LIFT IS NOT `x = x` BECOMING `x_i = x_j`. Those are different propositions and conflating them
is the whole trap. `x = x` is a tautology; `x_i = x_j` is an additional assertion nobody made. What
actually lifts is:

    identity                x ≡ x                     (tautological, carries no information)
    representation          R_i(x)                    (a reading, with a declared convention)
    preservation claim      R_i(x) ≡ R_j(x)           (empirical, and can fail)

So the object measured here is a PRESERVATION CLAIM between two independently derived readings of
one substrate, under an EXPLICITLY DECLARED equivalence predicate. The default tolerance is ZERO,
because every reading in this repository is an exact integer and a tolerance nobody needed would be
a free parameter waiting to absorb a defect.

FIVE COUNTS, NEVER FUSED, and the third one is the reason this file exists.

    points          query points visited
    comparable      both readings DEFINED
    agree           comparable and equivalent
    disagree        comparable and not equivalent
    incomparable    exactly one reading defined — a DOMAIN mismatch, not a value mismatch

`incomparable` is zero at D=1 and D=2 and large at D=3, and that is not an artefact. Adding the
vertical coordinate gives a reading a way to REFUSE — an actor standing at the authority's ground is
INSIDE the terrain according to the view's ground — so the lift introduces a failure mode the lower
dimensions cannot express. Folding it into `disagree` would report a domain mismatch as a
disagreement about a value, and folding it into `points` would hide it entirely.

TPI IS AN OUTPUT, NOT A PREMISE. `tpi(counts)` returns `(agree, comparable)` — a pair — plus a
permille reading for a human. There is no closed form here and none is fitted. The proposed
`exp(-alpha*D*(1-g)/N)` is recorded as `PROPOSED_FORM`, a STRING, and is never evaluated.

AND THE PROPOSED FORM IS REFUTED AT ITS PREMISE RATHER THAN AT ITS FIT, which is a stronger result
and a cheaper one. It has no slot for the COARSENING ESTIMATOR. Two measurement cells sharing D, g
and N exactly, differing only in whether a block is summarised by its minimum or its mean, have
DIFFERENT preservation. So no function of (D, g, N) alone can reproduce the table, and a bad
curve-fit was never needed to say so. `does_not_show`: that no exponential in D exists once the
estimator is FIXED — that is a separate question this rung does not answer and does not foreclose.

(H, I) DOES NOT DETERMINE T, proved constructively rather than asserted, and NOT as a product.

    H   hypocrisy   declaration <-> behaviour
    I   integrity   behaviour <-> itself
    T   truth       behaviour <-> referent

Four systems are built over substrates that HAVE a referent, because T is measurable only where one
does. A and B share H = 0 and I = 1 exactly and differ in T. C declares one convention and
implements another, so H > 0; D's reading depends on a mutable counter, so I < 1 — without those two
the first pair would be a claim about a constant. `H x I != T` is deliberately NOT the form used:
the three are not quantities that have been shown to multiply, and the claim that survives is the
independence one.

AND PROJECTION ERROR IS NOT TRUTH ERROR. This is the sentence most worth being careful about, since
this repository has a measured 41-permille projection bound sitting nearby and it is tempting to
read it as a distance from reality. Two FINE fields that coarsen to the SAME coarse field have
IDENTICAL projection error by construction and DIFFERENT truth error — exhibited here in exact
integers. The projection certificate bounds drift BETWEEN REPRESENTATIONS; it says nothing about the
distance from either to the substrate, and on the live island there is no referent at all, so truth
there is NOT_MEASURED and is recorded as such.

GRADE (honest, D5): MEASURED — the preservation counts over a swept fixture family, the
estimator-dependence refutation, the exact monotonicity verdicts, the four-system independence
construction, and the projection-is-not-truth construction, all exact integers and reproducible.
DECLARED: the preservation MATRIX's pending cells, which name work not done rather than results.
`does_not_show`: that coarse-graining ALWAYS biases (it does so here, under a named estimator, on a
named field — `sample != universal`); that measurement perturbs the measured (no such backreaction
is claimed or built, and `the_view_does_not_feed_back` is the standing law that it must not); that
the live repository's truth error is known (it is not — there is no referent); that these four
representations exhaust the readings of a heightfield."""
import hashlib

MAGIC = b"URDRLFT1"

#: RECORDED AS A HYPOTHESIS AND NEVER EVALUATED. Kept as text so a successor can see exactly what
#: was proposed and exactly which of its premises the table below refutes.
PROPOSED_FORM = "TPI(D) = exp(-alpha * D * (1 - g) / N)"
PROPOSED_FORM_STATUS = ("UNDERDETERMINED — refuted as a function of (D, g, N) because it has no "
                        "slot for the coarsening estimator, which moves the answer. Not refuted "
                        "as an exponential in D at a FIXED estimator; that is unmeasured here.")

#: The equivalence predicate, DECLARED rather than assumed. Zero by default: every reading here is
#: an exact integer, and a tolerance nobody needed is a free parameter waiting to absorb a defect.
DEFAULT_EPSILON = 0

CELL_CONSTANT = "CELL_CONSTANT"
LATTICE_POINT = "LATTICE_POINT"

DIMENSIONS = (1, 2, 3)
COARSENERS = ("block_min", "block_mean")


class LiftError(Exception):
    def __init__(self, message):
        super().__init__(f"LIFT-REFUSE: {message}")
        self.code = "LIFT-REFUSE"


def equivalent(a, b, eps=DEFAULT_EPSILON):
    """A ~e B iff their observable difference is within an EXPLICITLY DECLARED tolerance. Both
    readings are integers in a common scale, so this is exact at eps = 0."""
    if a is None or b is None:
        raise LiftError("equivalence asked of an undefined reading — an undefined reading is "
                        "INCOMPARABLE, which is a different count from disagreeing")
    return abs(a - b) <= eps


# ---- substrate and coarse-graining -------------------------------------------------------------
def _blocks(fine, k):
    n = len(fine)
    if n % k:
        raise LiftError(f"a {n}x{n} field does not partition into {k}x{k} blocks — an unequal "
                        f"partition would make the boundary placement part of the result")
    return n // k


def coarsen(fine, k, rule):
    """Summarise each k x k block. THE RULE IS A PARAMETER, not a default, because the whole
    finding below is that the answer depends on it."""
    if rule not in COARSENERS:
        raise LiftError(f"{rule!r} is not a declared coarsener ({', '.join(COARSENERS)})")
    m = _blocks(fine, k)
    out = []
    for cz in range(m):
        row = []
        for cx in range(m):
            vals = [fine[cz * k + dz][cx * k + dx] for dz in range(k) for dx in range(k)]
            row.append(min(vals) if rule == "block_min" else sum(vals) // len(vals))
        out.append(tuple(row))
    return tuple(out)


# ---- the two readings, each in units of 1/(k*k) so equality is exact ---------------------------
def read_cell(coarse, k, px, pz):
    """THE AUTHORITY CONVENTION: an integer coordinate names a CELL, constant across it. This is
    `glide`'s reading and `contact`'s, and `worldbasis` declares it the authority."""
    return coarse[pz // k][px // k] * k * k


def read_lattice(coarse, k, px, pz):
    """THE VIEW CONVENTION: an integer coordinate names a LATTICE POINT and the surface is
    interpolated between neighbours. This is `terrain_bridge`'s reading. Exact integer bilinear,
    in the same 1/(k*k) units, so no float and no rounding enters the comparison."""
    m = len(coarse)
    cx, fx = px // k, px % k
    cz, fz = pz // k, pz % k
    cx1, cz1 = min(cx + 1, m - 1), min(cz + 1, m - 1)
    return (coarse[cz][cx] * (k - fx) * (k - fz) + coarse[cz][cx1] * fx * (k - fz)
            + coarse[cz1][cx] * (k - fx) * fz + coarse[cz1][cx1] * fx * fz)


READINGS = {CELL_CONSTANT: read_cell, LATTICE_POINT: read_lattice}


def _defined_at(name, coarse, k, px, pz, D, y):
    """A reading, or None where this reading REFUSES.

    D = 1, 2 : the query names a place, and both readings answer.
    D = 3    : the query also names a HEIGHT, and a reading refuses a point BELOW its own ground —
               `contact`'s penetration refusal, which is not a contact state. The two grounds
               differ, so the third coordinate creates a DOMAIN mismatch the lower dimensions
               cannot express. That is the lift breaking preservation, not an artefact of it."""
    v = READINGS[name](coarse, k, px, pz)
    if D < 3:
        return v
    return None if y < v else v


# ---- the measurement -------------------------------------------------------------------------
def preservation(fine, k, rule, D, pair=(CELL_CONSTANT, LATTICE_POINT), eps=DEFAULT_EPSILON,
                 row=0):
    """FIVE COUNTS, NEVER FUSED. `row` fixes z for D = 1, where the query names x alone."""
    if D not in DIMENSIONS:
        raise LiftError(f"D={D!r} is not one of {DIMENSIONS}")
    coarse = coarsen(fine, k, rule)
    n = len(fine)
    a, b = pair
    points = comparable = agree = disagree = incomparable = 0
    zs = (row,) if D == 1 else range(n)
    for pz in zs:
        for px in range(n):
            points += 1
            y = read_cell(coarse, k, px, pz)          # the actor stands at the AUTHORITY's ground
            va = _defined_at(a, coarse, k, px, pz, D, y)
            vb = _defined_at(b, coarse, k, px, pz, D, y)
            if (va is None) != (vb is None):
                incomparable += 1
                continue
            if va is None:
                continue                              # neither reading answers: not a comparison
            comparable += 1
            if equivalent(va, vb, eps):
                agree += 1
            else:
                disagree += 1
    return {"points": points, "comparable": comparable, "agree": agree,
            "disagree": disagree, "incomparable": incomparable}


def tpi(counts):
    """A PAIR, NOT A NUMBER — `(agree, comparable)`, so the denominator travels with the result
    (L44). The permille reading is for a reader; nothing branches on it."""
    a, c = counts["agree"], counts["comparable"]
    if c == 0:
        raise LiftError("no comparable cases — a preservation index over an empty denominator is "
                        "the vacuity this discipline exists to refuse")
    return (a, c, a * 1000 // c)


# ---- the swept family --------------------------------------------------------------------------
def _field(n, seed):
    """A deterministic integer field with real structure at every scale, so coarsening has
    something to lose. No heightfield dependency: the substrate here must be controllable."""
    out = []
    s = seed
    for z in range(n):
        row = []
        for x in range(n):
            s = (s * 1103515245 + 12345) & 0x7FFFFFFF
            row.append((s >> 7) % 64 + ((x * 3 + z * 5) % 17))
        out.append(tuple(row))
    return tuple(out)


FIXTURES = ((16, 11), (32, 29))                        # (resolution, seed) — N varies with both
KS = (1, 2, 4)


def lift_table():
    """THE ARTIFACT. Every cell of the family, as data: (resolution, k, rule, D) -> counts. No
    functional form is assumed, fitted, or implied — the table IS the result."""
    out = {}
    for (n, seed) in FIXTURES:
        fine = _field(n, seed)
        for k in KS:
            for rule in COARSENERS:
                for D in DIMENSIONS:
                    out[(n, k, rule, D)] = preservation(fine, k, rule, D)
    return out


def segments(n, k):
    """N, the number of segments — recorded because the proposed form contains it, and varied
    independently of k by varying the resolution."""
    return (n // k) ** 2


# ---- the refutation ----------------------------------------------------------------------------
def the_preservation_is_not_a_function_of_D_g_N():
    """THE PROPOSED FORM IS REFUTED AT ITS PREMISE, WHICH IS CHEAPER AND STRONGER THAN A BAD FIT.

    `exp(-alpha*D*(1-g)/N)` has no slot for the coarsening ESTIMATOR. If two cells share D, the
    granularity k and the segment count N exactly, and differ only in whether a block is summarised
    by its MINIMUM or its MEAN, then any function of (D, g, N) alone must give them the same
    answer. Returns the witnesses where it does not — a non-empty list is the refutation."""
    t = lift_table()
    out = []
    for (n, k, rule, D), c in sorted(t.items()):
        if rule != COARSENERS[0]:
            continue
        other = t[(n, k, COARSENERS[1], D)]
        if tpi(c)[:2] != tpi(other)[:2] or c["incomparable"] != other["incomparable"]:
            out.append(((n, k, D, segments(n, k)), tpi(c)[:2], tpi(other)[:2]))
    return tuple(out)


def _cmp_ratio(p, q):
    """Compare two (num, den) ratios EXACTLY by cross-multiplication — no float, no rounding."""
    return (p[0] * q[1] > q[0] * p[1]) - (p[0] * q[1] < q[0] * p[1])


def monotonicity_report():
    """THE PROPOSED FORM'S QUALITATIVE PREDICTIONS, CHECKED EXACTLY AND BEFORE ANY FIT: preservation
    should FALL as D rises and RISE as granularity improves (k falls). Cross-multiplied integer
    comparisons, so the verdicts carry no tolerance. Returns {(n, rule): (in_D, in_g)} with each
    verdict in {"monotone", "violated"}."""
    t = lift_table()
    out = {}
    for (n, _seed) in FIXTURES:
        for rule in COARSENERS:
            dv = "monotone"
            for k in KS:
                seq = [tpi(t[(n, k, rule, D)])[:2] for D in DIMENSIONS]
                if any(_cmp_ratio(seq[i], seq[i + 1]) < 0 for i in range(len(seq) - 1)):
                    dv = "violated"
            gv = "monotone"
            for D in DIMENSIONS:
                seq = [tpi(t[(n, k, rule, D)])[:2] for k in KS]      # k rising = granularity worse
                if any(_cmp_ratio(seq[i], seq[i + 1]) < 0 for i in range(len(seq) - 1)):
                    gv = "violated"
            out[(n, rule)] = (dv, gv)
    return out


def the_family_is_non_vacuous():
    """L61 on the sweep itself. A family whose every cell reads 1.0 would certify nothing, and one
    whose every cell reads 0 would mean the fixture was broken rather than the claim. Both
    polarities must be present, and perfect granularity must be perfect."""
    t = lift_table()
    ratios = {tpi(c)[2] for c in t.values()}
    perfect = all(t[(n, 1, r, D)]["disagree"] == 0
                  for (n, _s) in FIXTURES for r in COARSENERS for D in DIMENSIONS)
    return (perfect and 1000 in ratios and any(r < 1000 for r in ratios)
            and any(c["incomparable"] > 0 for c in t.values())
            and all(t[(n, k, r, D)]["incomparable"] == 0
                    for (n, _s) in FIXTURES for k in KS for r in COARSENERS for D in (1, 2)))


# ---- (H, I) does not determine T ---------------------------------------------------------------
class _System:
    """A declaration, an implementation, a substrate, and — SEPARATELY — a REFERENT, which may be
    absent. Four things, deliberately not three: the substrate is what the system reads, and the
    referent is the finer thing it would have to be compared against for `truth` to mean anything.
    A system with no referent is not a system with truth zero; it is a system whose truth has no
    operand, and this class makes that a structural fact rather than a footnote."""

    def __init__(self, name, declares, impl, fine, k, referent=None, drifting=False):
        self.name, self.declares, self.impl = name, declares, impl
        self.fine, self.k, self.drifting = fine, k, drifting
        self.referent = referent
        self._coarse = coarsen(fine, k, "block_mean")
        self._calls = 0

    def read(self, px, pz):
        self._calls += 1
        v = READINGS[self.impl](self._coarse, self.k, px, pz)
        return v + (self._calls if self.drifting else 0)


def hypocrisy(sysm):
    """H — DECLARATION against BEHAVIOUR, as counts. A system declaring CELL_CONSTANT must read the
    SAME value everywhere inside a cell; one declaring LATTICE_POINT must not. Probed rather than
    trusted, so a system that declares one convention and implements another is caught."""
    n, k = len(sysm.fine), sysm.k
    probes = mismatch = 0
    for cz in range(0, n - k, k):
        for cx in range(0, n - k, k):
            probes += 1
            flat = all(sysm.read(cx, cz) == sysm.read(cx + d, cz) for d in range(k))
            if (sysm.declares == CELL_CONSTANT) != flat:
                mismatch += 1
    return (mismatch, probes)


def integrity(sysm, repeats=3):
    """I — BEHAVIOUR against ITSELF, as counts. Repeat every probe and count the repetitions that
    reproduce the first answer. Deterministic reading -> (0, probes)."""
    n, k = len(sysm.fine), sysm.k
    probes = differ = 0
    for pz in range(0, n, k):
        for px in range(0, n, k):
            probes += 1
            first = sysm.read(px, pz)
            if any(sysm.read(px, pz) != first for _ in range(repeats - 1)):
                differ += 1
    return (differ, probes)


def truth(sysm):
    """T — BEHAVIOUR against the REFERENT, as counts, AND IT REFUSES WITHOUT ONE.

    The refusal is the enforcement. A predicate that returned 'nothing wrong found' for a system
    with no referent would be the shape L23 forbids — a checker unable to fail — and would let a
    NOT_MEASURED quantity read as a perfect score. So the absence of a referent is a typed
    LIFT-REFUSE, and every truth number in this module comes from a substrate that was
    CONSTRUCTED so that one exists."""
    if sysm.referent is None:
        raise LiftError(f"{sysm.name!r} has no referent — truth is a comparison and there is "
                        f"nothing to compare against. NOT_MEASURED is the honest verdict, and it "
                        f"is not the same as zero error")
    n, k = len(sysm.fine), sysm.k
    probes = wrong = 0
    for pz in range(n):
        for px in range(n):
            probes += 1
            if sysm.read(px, pz) != sysm.referent[pz][px] * k * k:
                wrong += 1
    return (wrong, probes)


def _constant_extension(coarse, k):
    """The fine field for which the CELL reading is exactly right — each block constant."""
    return tuple(tuple(coarse[z // k][x // k] for x in range(len(coarse) * k))
                 for z in range(len(coarse) * k))


def _mean_preserving_ripple(coarse, k):
    """A DIFFERENT fine field with the SAME block means, so it coarsens to the same coarse field
    under `block_mean` — and the cell reading is therefore wrong about it. The block sums are held
    exactly equal by moving mass within each block, never across one."""
    m = len(coarse)
    out = [[0] * (m * k) for _ in range(m * k)]
    for cz in range(m):
        for cx in range(m):
            v = coarse[cz][cx]
            cells = [(cz * k + dz, cx * k + dx) for dz in range(k) for dx in range(k)]
            for i, (z, x) in enumerate(cells):
                out[z][x] = v + (1 if i % 2 == 0 else -1) * (k > 1)
    return tuple(tuple(r) for r in out)


def the_four_systems(k=2, m=8):
    """A and B share (H, I) EXACTLY and differ in T. C and D exist so that neither H nor I is a
    constant — without them the pair would be a claim about a number that never moves."""
    base = coarsen(_field(m * k, 7), k, "block_mean")
    f_const = _constant_extension(base, k)
    f_ripple = _mean_preserving_ripple(base, k)
    return (_System("A truthful", CELL_CONSTANT, CELL_CONSTANT, f_const, k, f_const),
            _System("B displaced", CELL_CONSTANT, CELL_CONSTANT, f_ripple, k, f_ripple),
            _System("C hypocrite", CELL_CONSTANT, LATTICE_POINT, f_const, k, f_const),
            _System("D drifting", CELL_CONSTANT, CELL_CONSTANT, f_const, k, f_const,
                    drifting=True))


def integrity_does_not_determine_truth():
    """(H, I) DOES NOT DETERMINE T — constructively, and NOT as a product. Returns the four
    triples; the claim is that A and B agree on (H, I) and differ on T, while C and D show that H
    and I can both move, so the agreement is a fact rather than a constant.

    A and B declare the same convention, implement the same reading, and are equally deterministic.
    They differ ONLY in what is underneath: A's substrate is the cell-constant extension its
    reading is exactly right about, B's is a mean-preserving ripple it is wrong about everywhere.
    Nothing observable from inside either system distinguishes them."""
    A, B, C, D = the_four_systems()
    rows = tuple((s.name, hypocrisy(s), integrity(s), truth(s)) for s in (A, B, C, D))
    (_na, ha, ia, ta), (_nb, hb, ib, tb), (_nc, hc, _ic, _tc), (_nd, _hd, idd, _td) = rows
    same_hi = (ha == hb == (0, ha[1])) and (ia == ib == (0, ia[1]))
    differ_t = ta[0] == 0 and tb[0] > 0
    h_moves, i_moves = hc[0] > 0, idd[0] > 0
    return rows, (same_hi and differ_t and h_moves and i_moves)


def projection_error_is_not_truth_error():
    """THE QUALIFICATION ON THE 41-PERMILLE FIGURE, MADE MECHANICAL.

    Two FINE fields that coarsen to the SAME coarse field have, by construction, IDENTICAL
    projection error — the cell/lattice disagreement is computed from the coarse field alone and
    cannot see which fine field produced it. Their TRUTH errors differ. So a projection certificate
    bounds drift BETWEEN REPRESENTATIONS and does not bound the distance from either to the
    substrate. Returns (projection_a, projection_b, truth_a, truth_b, holds)."""
    k, m = 2, 8
    base = coarsen(_field(m * k, 7), k, "block_mean")
    fa, fb = _constant_extension(base, k), _mean_preserving_ripple(base, k)
    if coarsen(fa, k, "block_mean") != coarsen(fb, k, "block_mean"):
        raise LiftError("the two fine fields do not coarsen alike — the construction is broken")
    pa = preservation(fa, k, "block_mean", 2)
    pb = preservation(fb, k, "block_mean", 2)
    ta = truth(_System("a", CELL_CONSTANT, CELL_CONSTANT, fa, k, fa))
    tb = truth(_System("b", CELL_CONSTANT, CELL_CONSTANT, fb, k, fb))
    holds = (pa == pb) and ta[0] == 0 and tb[0] > 0
    return (pa, pb, ta, tb, holds)


def the_live_field_has_no_referent():
    """AND ON THE LIVE FIELD THERE IS NONE. `heightfield.generate` IS the substrate — it is
    generated rather than sampled, so there is no finer thing it approximates and 'how far is the
    authority reading from the truth' has no operand. Recorded by CONSTRUCTING the live system
    with no referent and requiring `truth` to REFUSE it, which is the difference between a verdict
    of NOT_MEASURED and a score of zero error. Non-vacuous in both directions: the constructed
    fixture, whose referent exists, returns counts."""
    import os as _os
    import sys as _sys
    _sys.path.insert(0, _os.path.dirname(_os.path.abspath(__file__)))
    import heightfield as HF
    live = _System("live island", CELL_CONSTANT, CELL_CONSTANT,
                   HF.generate(**HF.island()), 1, referent=None)
    try:
        truth(live)
        return False                                   # a truth score for a referent-free system
    except LiftError as exc:
        refused = "NOT_MEASURED" in str(exc)
    A, _B, _C, _D = the_four_systems()
    return refused and truth(A)[1] > 0


def the_lift_reclassified_rather_than_preserved():
    """WHY THE FIVE COUNTS MAY NOT BE FUSED, stated as the sharpest thing this table says.

    Across the whole family, `agree` at D = 3 EQUALS `agree` at D = 2, and `disagree` at D = 2
    equals `disagree` + `incomparable` at D = 3. Not one additional point was preserved by adding
    the vertical coordinate. What the lift did was move value-disagreements into a DOMAIN
    mismatch — the authority's actor standing inside the view's terrain — and the ratio rose from
    324 to 515 permille purely because those cases left the denominator.

    The identity FOLLOWS from the domain rule, and saying so is the point rather than a weakness:
    the mechanism is what makes the ratio's rise legible. A single number could not have
    distinguished 'the lift preserved more' from 'the lift stopped counting the failures', and
    that is exactly the choice a reader of TPI alone would have to make blind."""
    t = lift_table()
    rose = False
    for (n, _s) in FIXTURES:
        for k in KS:
            for rule in COARSENERS:
                c2, c3 = t[(n, k, rule, 2)], t[(n, k, rule, 3)]
                if c2["agree"] != c3["agree"]:
                    return (False, None)
                if c2["disagree"] != c3["disagree"] + c3["incomparable"]:
                    return (False, None)
                if k > 1 and _cmp_ratio(tpi(c3)[:2], tpi(c2)[:2]) > 0:
                    rose = True
    return (rose, tuple((n, k, rule, tpi(t[(n, k, rule, 2)])[2], tpi(t[(n, k, rule, 3)])[2])
                        for (n, _s) in FIXTURES for k in KS for rule in COARSENERS if k > 1))


# ---- the lift preservation matrix --------------------------------------------------------------
#: WHAT SURVIVED THE 2D -> 3D LIFT THIS ARC JUST PERFORMED, as data. PRESERVED / TRANSFORMED / NEW
#: are results; PENDING names work not done. Each settled cell carries the callable that settles it,
#: so a claim here cannot drift away from the thing that proves it.
MATRIX = (
    ("horizontal admission", "checked", "checked", "PRESERVED", "contact.walk_contact_divergence"),
    ("MAX_STEP wall", "checked", "checked", "PRESERVED", "contact.walk_contact_divergence"),
    ("ground state", "implicit", "explicit", "TRANSFORMED", "contact.STATES"),
    ("gravity", "absent", "required", "NEW", "stride.advance"),
    ("support", "implicit", "certified", "TRANSFORMED", "contact.witness"),
    ("replay determinism", "checked", "checked", "PRESERVED", "stride.peers_agree"),
    ("sub-cell motion", "checked", "absent", "PENDING", ""),
    ("actor-actor collision", "checked", "absent", "PENDING", ""),
)
VERDICTS = ("PRESERVED", "TRANSFORMED", "NEW", "PENDING")


def matrix_verdicts():
    return {row[0]: row[3] for row in MATRIX}


def the_matrix_is_settled_where_it_claims_to_be():
    """Every non-PENDING cell names a live callable, every PENDING cell names none, every verdict is
    one of the declared four, and all four are POPULATED — a matrix reading PRESERVED throughout
    would be a table written to flatter the lift (L61)."""
    import importlib
    import os as _os
    import sys as _sys
    for d in ("terrain", "physics", "netcode"):
        p = _os.path.join(_os.path.dirname(_os.path.dirname(_os.path.abspath(__file__))), d)
        if p not in _sys.path:
            _sys.path.insert(0, p)
    seen = set()
    for name, d2, d3, verdict, cite in MATRIX:
        if verdict not in VERDICTS:
            return False
        seen.add(verdict)
        if verdict == "PENDING":
            if cite or d3 != "absent":
                return False
            continue
        if not cite:
            return False
        mod, attr = cite.split(".", 1)
        if not hasattr(importlib.import_module(mod), attr):
            return False
        if not (d2 and d3):
            return False
    return seen == set(VERDICTS)


def the_lift_broke_something(k=2):
    """THE MATRIX WOULD BE DECORATION IF NOTHING HAD MOVED. At least one law is TRANSFORMED or NEW
    rather than PRESERVED, and the sweep independently shows a lift that loses preservation: D = 3
    admits an incomparable class that D = 1 and D = 2 cannot express."""
    v = set(matrix_verdicts().values())
    t = lift_table()
    n = FIXTURES[0][0]
    return (bool(v & {"TRANSFORMED", "NEW"})
            and t[(n, k, "block_mean", 3)]["incomparable"] > 0
            and t[(n, k, "block_mean", 2)]["incomparable"] == 0)


# ---- scenes ------------------------------------------------------------------------------------
SCENES = ("table", "estimator", "monotonicity", "reclass", "independence", "matrix")


def scene_case(name):
    """The payload BEFORE it is digested — a golden nobody can read is a golden nobody checks."""
    if name == "table":
        t = lift_table()
        return "|".join("%d,%d,%s,%d:%d/%d/%d/%d/%d" % (
            n, k, r, D, c["points"], c["comparable"], c["agree"], c["disagree"], c["incomparable"])
            for (n, k, r, D), c in sorted(t.items()))
    if name == "estimator":
        return "|".join("%s %s %s" % w for w in the_preservation_is_not_a_function_of_D_g_N())
    if name == "monotonicity":
        return "|".join("%d,%s:%s/%s" % (n, r, a, b)
                        for (n, r), (a, b) in sorted(monotonicity_report().items()))
    if name == "reclass":
        rose, rows = the_lift_reclassified_rather_than_preserved()
        return "%s|%s" % (rose, rows)
    if name == "independence":
        rows, _ok = integrity_does_not_determine_truth()
        pa, pb, ta, tb, _h = projection_error_is_not_truth_error()
        return "|".join("%s H%s I%s T%s" % r for r in rows) + \
            "||proj %s==%s truth %s vs %s" % (tpi(pa)[:2], tpi(pb)[:2], ta, tb)
    if name == "matrix":
        return "|".join("%s:%s" % (r[0], r[3]) for r in MATRIX)
    raise LiftError(f"no scene named {name!r}")


def scene_result(name):
    return hashlib.sha256(MAGIC + b"|" + name.encode() + b"|"
                          + scene_case(name).encode()).hexdigest()


def lift_digest():
    return hashlib.sha256(MAGIC + b"|" + "|".join(scene_result(n)
                                                  for n in SCENES).encode()).hexdigest()


def golden(name):
    import os as _os
    with open(_os.path.join(_os.path.dirname(_os.path.abspath(__file__)),
                            "conformance_lift.txt"), encoding="utf-8") as fh:
        for ln in fh:
            ln = ln.strip()
            if ln and not ln.startswith("#"):
                nm, dig = ln.split()
                if nm == name:
                    return dig
    raise LiftError(f"no golden named {name!r}")


if __name__ == "__main__":
    t = lift_table()
    print("  n   k  rule        D   points comparable  agree disagree incomparable   TPI permille")
    for key in sorted(t):
        n, k, r, D = key
        c = t[key]
        print("%3d %3d  %-10s %2d %8d %10d %6d %8d %12d %8d"
              % (n, k, r, D, c["points"], c["comparable"], c["agree"], c["disagree"],
                 c["incomparable"], tpi(c)[2]))
    print()
    print("estimator witnesses:", len(the_preservation_is_not_a_function_of_D_g_N()))
    for w in the_preservation_is_not_a_function_of_D_g_N()[:4]:
        print("   ", w)
    print("monotonicity:", monotonicity_report())
    print("non-vacuous:", the_family_is_non_vacuous())
    rows, ok = integrity_does_not_determine_truth()
    for r in rows:
        print("   %-14s H=%s I=%s T=%s" % r)
    print("(H,I) does not determine T:", ok)
    print("projection != truth:", projection_error_is_not_truth_error()[4])
    print("reclassified:", the_lift_reclassified_rather_than_preserved()[0])
    print("matrix settled:", the_matrix_is_settled_where_it_claims_to_be(),
          "broke something:", the_lift_broke_something())
    print("no referent live:", the_live_field_has_no_referent())
    for n in SCENES:
        print(n, scene_result(n))
    print("lift", lift_digest())
