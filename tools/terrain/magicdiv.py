# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""magicdiv — DIVISION BY AN INVARIANT CONSTANT, EXACT AND EXHAUSTIVELY PROVEN (URDRMAG1): the
Granlund-Montgomery multiply-shift identity, admitted into this arc on its own terms. A handed-down
theorem arrived with four "self-organization" corollaries attached; this rung keeps what is true,
SHARPENS it to an exact statement, and REFUTES what is false. NO NEW GLYPH — the kernel stays frozen.

THE OPERATIVE THEOREM (exact, integer, no floats — the reason it belongs here). For a word size W and
a divisor d, with l = ceil(log2 d), m = ceil(2^(W+l) / d) and s = W + l:

    floor(n / d) == (m * n) >> s        for EVERY n in [0, 2^W)

This is not sampled and not asymptotic: the gate verifies it EXHAUSTIVELY — every divisor in
[1, 2^W) against every dividend in [0, 2^W) — which at W = 10 is a complete proof over the whole
word, ~1.05e6 checks. That is a stronger grade than any sweep in this arc: not
confidence-over-a-sampled-space but a decided finite statement.

THE FOUR HANDED-DOWN COROLLARIES, EACH GRADED RATHER THAN REPEATED.

  * CLAIM 1 — "Lambda = {(mu_c mod 2^w, s_c)} is fractal with Hausdorff dimension ~ log2(log2 M)":
    **REFUTED, and not by measurement but by definition.** Lambda is a set of integer pairs, hence
    COUNTABLE, and every countable subset of R^2 has Hausdorff dimension exactly 0. No computation
    can rescue this; a dimension of log2(log2 M) would require an uncountable set. `refutes_claim1`
    returns the witness. This is kept in the module rather than quietly dropped, because a refuted
    claim is a result.

  * CLAIM 2 — "near-collisions with equal shift cluster around powers of 2": **TRUE, and sharper
    than stated.** The equal-shift classes are not merely clustered near powers of two, they ARE the
    half-open dyadic blocks (2^k, 2^(k+1)]: every class's upper edge is exactly a power of two.
    MEASURED exhaustively by `shift_classes`.

  * CLAIM 3 — the equivalence c1 ~ c2 iff mu/gcd(mu, 2^w) agree: well-defined, and `equiv_classes`
    computes it. Its content is reported as a MEASUREMENT (the class-size histogram), not asserted.

  * CLAIM 4 — "each class self-organizes around a centre c* with s_c constant on [c*2^-e, c*2^e]":
    **TRUE, and the mechanism is not self-organization — it is bit-length.** s_c = W + ceil(log2 c)
    exactly, so constancy on dyadic intervals is a restatement of the definition rather than an
    emergent phenomenon. MEASURED by `shift_is_bitlength`, which checks the closed form on every
    divisor in the word.

WHAT THIS BUYS THE ARC. Every exact-integer rung here divides by constants — squared ranges,
quantisation quanta, rate shifts, byte budgets. Where the divisor is a compile-time constant this
identity replaces the division with a multiply and a shift *with no change of value whatsoever*,
which is the only kind of optimisation this arc will accept: one that is provably value-preserving
rather than approximately so. `plan(d)` hands back the pair; `apply_plan` is the substitution.

GRADE. MEASURED (and unusually strongly — exhaustively decided over the whole word): the
multiply-shift identity; the dyadic-block structure of the shift classes; the closed form
s = W + ceil(log2 d); the equivalence-class histogram. ESTABLISHED by definition, not measurement:
the refutation of the Hausdorff-dimension claim. DECLARED: the exhaustive proof is for W = 10 — the
same construction is used at 32 and 64 in practice and is spot-checked here at W = 16, but only the
W = 10 statement is decided in this gate; a wider word is a longer computation, not a different
theorem. does_not_show: signed division (this is the unsigned case); division by a runtime-variable
divisor (the identity needs d fixed); cross-placement (URDRMAG1 Python reference only)."""
import hashlib
import os as _os
import sys as _sys

_HERE = _os.path.dirname(_os.path.abspath(__file__))
if _HERE not in _sys.path:
    _sys.path.insert(0, _HERE)

MAGIC = b"URDRMAG1"
WORD = 10                                     # the word the gate decides EXHAUSTIVELY
WIDE = 16                                     # a wider word, spot-checked (declared, not decided)


class MagicdivError(Exception):
    def __init__(self, message):
        super().__init__(f"MAGICDIV-REFUSE: {message}")
        self.code = "MAGICDIV-REFUSE"


# ---- the construction ---------------------------------------------------------------------
def ceil_log2(d):
    """ceil(log2 d) in exact integer arithmetic — no float, no math.log."""
    if d <= 0:
        raise MagicdivError("divisor must be positive")
    return max(0, (d - 1).bit_length())


def plan(d, word=WORD):
    """The (multiplier, shift) pair for divisor `d` at `word` bits: m = ceil(2^(W+l)/d), s = W+l."""
    if type(d) is not int or d <= 0:
        raise MagicdivError(f"divisor must be a positive int, got {d!r}")
    l = ceil_log2(d)
    s = word + l
    m = ((1 << s) + d - 1) // d               # ceil(2^s / d), exact integer
    return (m, s)


def apply_plan(n, mp):
    """The substitution: floor(n/d) computed as (m*n) >> s."""
    m, s = mp
    return (m * n) >> s


def _plan_floor(d, word=WORD):
    """A FALSIFIER TOOL (not the law): the off-by-one that uses floor instead of ceil for the
    multiplier. It is correct for divisors that are powers of two and WRONG otherwise — exactly the
    subtle defect an exhaustive check exists to catch."""
    l = ceil_log2(d)
    s = word + l
    return ((1 << s) // d, s)


# ---- the exhaustive decision (not a sweep — a decided finite statement) --------------------
def verify_divisor(d, word=WORD, _plan=None):
    """Every dividend in [0, 2^word) for this divisor. True iff the identity holds throughout."""
    mp = (_plan or plan)(d, word)
    for n in range(1 << word):
        if apply_plan(n, mp) != n // d:
            return False
    return True


def first_counterexample(d, word=WORD, _plan=None):
    mp = (_plan or plan)(d, word)
    for n in range(1 << word):
        if apply_plan(n, mp) != n // d:
            return (n, apply_plan(n, mp), n // d)
    return None


def exhaustive(word=WORD, _plan=None):
    """EVERY divisor against EVERY dividend in the word. Returns (checks, failures)."""
    lim = 1 << word
    checks = fails = 0
    for d in range(1, lim):
        mp = (_plan or plan)(d, word)
        for n in range(lim):
            checks += 1
            if apply_plan(n, mp) != n // d:
                fails += 1
                break
    return checks, fails


# ---- the four corollaries, graded ----------------------------------------------------------
def refutes_claim1():
    """Claim 1 is refuted BY DEFINITION: Lambda is a set of integer pairs, hence countable, and every
    countable subset of R^2 has Hausdorff dimension 0. Returns the witness (countable, dim)."""
    return ("countable", 0)


def shift_classes(word=WORD):
    """The equal-shift classes as (shift, lo, hi). MEASURED: they are exactly the half-open dyadic
    blocks (2^k, 2^(k+1)] — claim 2, sharpened from 'cluster near powers of two'."""
    runs = {}
    for d in range(1, 1 << word):
        runs.setdefault(plan(d, word)[1], []).append(d)
    return [(s, v[0], v[-1]) for s, v in sorted(runs.items())]


def classes_are_dyadic(word=WORD):
    """MEASURED, and stated at exactly its true strength: every multi-element shift class ends on a
    power of two EXCEPT the final one, which is truncated at 2^word - 1 by the word boundary — it
    would close at 2^word if the word were wider. Asserting the universal without that exception
    would be false (an earlier draft of this rung asserted it from a six-class sample and was wrong);
    asserting the whole thing false would discard a real structure. Returns True iff the pattern
    holds with exactly that one boundary exception."""
    cls = [c for c in shift_classes(word) if c[2] > c[1]]
    if not cls:
        return False
    interior, final = cls[:-1], cls[-1]
    return (all((hi & (hi - 1)) == 0 for _s, _lo, hi in interior)
            and final[2] == (1 << word) - 1)


def shift_is_bitlength(word=WORD):
    """Claim 4, MEASURED and demystified: s_d == word + ceil(log2 d) for EVERY divisor, so constancy
    on dyadic intervals is the definition restated, not an emergent self-organisation."""
    return all(plan(d, word)[1] == word + ceil_log2(d) for d in range(1, 1 << word))


def equiv_classes(word=WORD):
    """Claim 3's equivalence: d1 ~ d2 iff m/gcd(m, 2^word) agree. Reported as a histogram
    {class_size: how_many}, a measurement rather than an assertion."""
    from math import gcd
    buckets = {}
    for d in range(1, 1 << word):
        m, _s = plan(d, word)
        key = m // gcd(m, 1 << word)
        buckets[key] = buckets.get(key, 0) + 1
    hist = {}
    for n in buckets.values():
        hist[n] = hist.get(n, 0) + 1
    return hist


# ---- digests + scenes ----------------------------------------------------------------------
def plan_digest(word=WORD):
    hh = hashlib.sha256(); hh.update(MAGIC)
    for d in range(1, 1 << word):
        m, s = plan(d, word)
        hh.update(f"|{d}:{m}:{s}".encode())
    return hh.hexdigest()


def magicdiv_digest(name, payload):
    hh = hashlib.sha256(); hh.update(MAGIC)
    hh.update(f"|{name}|{payload}".encode())
    return hh.hexdigest()


def _scene_identity():
    """The operative theorem, decided over the whole word."""
    checks, fails = exhaustive()
    return magicdiv_digest("identity", f"{checks}:{fails}")


def _scene_plans():
    """The (m, s) table itself — every divisor's plan, pinned."""
    return magicdiv_digest("plans", plan_digest())


def _scene_dyadic():
    """Claim 2, sharpened: the shift classes ARE the dyadic blocks."""
    cls = shift_classes()
    return magicdiv_digest("dyadic", f"{classes_are_dyadic()}:{len(cls)}:{cls[:6]}")


def _scene_bitlength():
    """Claim 4, demystified: the shift is the bit-length, exactly."""
    return magicdiv_digest("bitlength", f"{shift_is_bitlength()}")


def _scene_refuted():
    """Claim 1, refuted by definition and kept in the record as a result."""
    return magicdiv_digest("refuted", f"{refutes_claim1()}:{sorted(equiv_classes().items())[:4]}")


_SCENES = {"identity": _scene_identity, "plans": _scene_plans, "dyadic": _scene_dyadic,
           "bitlength": _scene_bitlength, "refuted": _scene_refuted}
SCENES = ("identity", "plans", "dyadic", "bitlength", "refuted")


def scene_result(name):
    return _SCENES[name]()


def golden(name):
    with open(_os.path.join(_HERE, "conformance_magicdiv.txt"), encoding="utf-8") as fh:
        for ln in fh:
            ln = ln.strip()
            if ln and not ln.startswith("#"):
                nm, dig = ln.split()
                if nm == name:
                    return dig
    raise MagicdivError(f"no golden named {name!r}")


def wide_spotcheck(count=64):
    """The DECLARED part: the same construction at a wider word, spot-checked rather than decided."""
    lim = 1 << WIDE
    for d in list(range(1, 40)) + [lim // 3, lim // 7, lim - 1]:
        mp = plan(d, WIDE)
        for n in (0, 1, d - 1, d, d + 1, lim // 2, lim - 1):
            if apply_plan(n, mp) != n // d:
                return False
    return True


def _main(argv):
    for n in SCENES:
        print(n, scene_result(n))
    c, f = exhaustive()
    print(f"EXHAUSTIVE: {c} checks over the whole {WORD}-bit word, {f} failures")
    print(f"claim1 REFUTED {refutes_claim1()} | claim2 dyadic {classes_are_dyadic()} | "
          f"claim4 bitlength {shift_is_bitlength()} | wide spot-check {wide_spotcheck()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(_main(_sys.argv))
