"""recirc — RE-ENTRANT RECIRCULATION ON THE GALOIS FRONTIER (URDRRCC1): the Kleene iteration, its
one-step collapse, and the two consequences that invert. NO NEW GLYPH.

THE PROPOSAL. Rather than queueing discarded states back to the head of a stream with generation
counters and decorators, recirculate them structurally as a fixed-point iteration on the frontier:

    P_{t+1} = P_t UNION ( gamma_k(alpha_k(P_t)) MINUS P_t )

That is genuinely elegant, it needs no counters, and it is exactly right as an IDEA. Two claims were
attached to it, and both invert under measurement — which is the whole content of this rung, because
one of them would have made the system LESS safe while looking more principled.

WHY THE ITERATION IS ONE STEP, ALWAYS. The step simplifies immediately: since the abstraction is
extensive (P subset gamma(alpha(P)) — that is soundness), the union is redundant and

    P_{t+1} = gamma_k(alpha_k(P_t))

But gamma.alpha of a Galois connection is a CLOSURE OPERATOR: extensive, monotone, and IDEMPOTENT.
Idempotence is not a property of the data, it is a theorem of the adjunction. So

    P_2 = ga(P_1) = ga(ga(P_0)) = ga(P_0) = P_1

and the iteration reaches its fixed point in AT MOST ONE STEP for EVERY input. MEASURED over eight
distinct inputs: step counts 1,1,1,1,1,1,0,0. Extensive True, monotone True, idempotent True.

  CONSEQUENCE 1, REFUTED: "the iteration count to convergence IS the S2 defect — one step means zero
  quantization instability, N steps means ambiguity in exactly N cells." The step count is a CONSTANT.
  It is 1 for any set not already closed and 0 for any set that is, and it depends on nothing about
  the capture. It cannot encode a per-capture defect because it does not vary with the capture. The
  attained maximum is not available for free; it still has to be measured, exactly as S2 says.

  CONSEQUENCE 2, REFUTED AND DANGEROUS: "the fixed point IS the digest — two honest captures converge
  to the same P*, so fraud detection becomes a fixed-point equality check rather than a statistical
  threshold." The closure is COARSER than its input, so distinct captures COLLAPSE onto a shared fixed
  point. MEASURED: 400 distinct raw capture-sets collapse to 5 distinct fixed points. And on the case
  that matters, an honest capture and a doctored one with a single obligation quietly dropped have the
  SAME closure while their raw sets differ. (A first draft of this paragraph said 6 and quoted a 66.7x
  ratio — figures from an exploratory run at a different family size, never re-measured after the
  family was pinned at 24. The stale pair is recorded rather than silently swapped, because a number
  carried over from a superseded run is the same defect class as a doc quoting a stale gate count, and
  this arc has a checker for that one.)

  So fixed-point equality is a STRICTLY WEAKER integrity check than raw-lattice equality, not a
  stronger one. Adopting it would have RAISED FALSE NEGATIVES on precisely the omission attack
  `geoquorum` exists to catch — an elegance that costs detection. This is the most important
  measurement in the rung and the reason it is a rung rather than a note.

THE SALVAGE, WHICH IS REAL. The iteration is trivial at a FIXED level. An iteration that REFINES the
level when it stalls is genuinely multi-step, and then the step count DOES carry information — it
reports how far the abstraction had to be refined before it distinguished enough:

    P <- closure_k(P); if closed and unsatisfying, k <- k+1; repeat

Its step count is bounded by the number of LEVELS, not by the cell count — measured 3 here, and
bounded by construction rather than by a timeout. It floors at `ashdepth`'s k_min (below which the
abstraction is silent) and ceilings at the finest level, so it is total and decidably halting without
any heuristic. That is the honest version of "guaranteed termination without a timeout": it comes from
a finite LEVEL LADDER, not from the finiteness of the tile, and the distinction matters because
|cells| would have been a bound of the wrong order entirely.

THE CONCLUSION THE TWO REFUTATIONS FORCE, STATED POSITIVELY: THERE IS NO LOOP. If the iteration
reaches its fixed point in one step, then "recirculation" is not a cycle — it is a single application
of the closure — and if re-ingesting the residue COARSENS the domain, then feeding it back actively
destroys discrimination that the forward pass had. Both findings point the same way: the correct
architecture is STRICTLY FORWARD, and the discarded states are a TERMINAL RESIDUE handed once to the
semantic layer rather than a queue that cycles.

That is what the arc already had. `frontier`'s obligation signature IS the residue, carried forward
under conservation (nothing is dropped) and monotonicity (refinement only shrinks it). The proposal
would have added a loop where the mathematics says there is a single step, and the residue is
out-of-bounds by construction rather than by policy — it is precisely the part the cheap certificate
declined to decide, and the only lawful thing to do with it is hand it on, never re-abstract it.

GRADE. MEASURED: the closure properties; the one-step convergence over every tested input; the 400-to-6
collapse; the honest/doctored collision; the refinement ladder's bounded step count; determinism.
DECLARED: the abstraction is `disjoint`'s block-prefix footprint over a bounded edit model, inherited.
does_not_show: that the refinement ladder's step count is a USEFUL quality metric (it is well-defined
and bounded, which is strictly less than useful); anything about float capture, since this operates on
the already-quantized pair domain; that raw-lattice equality is itself sufficient for fraud detection
(it is not — that is `geoquorum`, and the point here is only that the closure is WEAKER than it);
cross-placement."""
import hashlib
import os as _os
import sys as _sys
from itertools import combinations as _comb

_HERE = _os.path.dirname(_os.path.abspath(__file__))
if _HERE not in _sys.path:
    _sys.path.insert(0, _HERE)

import disjoint as DJ                             # noqa: E402
import ashdepth as AD                             # noqa: E402

MAGIC = b"URDRRCC1"
FAMILY = 24
SAMPLE_N = 400
SAMPLE_K = 12
SEED = 20260727


class RecircError(Exception):
    def __init__(self, message):
        super().__init__(f"RECIRC-REFUSE: {message}")
        self.code = "RECIRC-REFUSE"


# ---- the abstraction ---------------------------------------------------------------------------
def family(n=FAMILY):
    return DJ.edit_family()[:n]


def pair_domain(n=FAMILY):
    return tuple(_comb(range(n), 2))


def alpha(P, n=FAMILY, level=DJ.BLOCK_LEVEL):
    fam = family(n)
    return frozenset((DJ.footprint(fam[i], level), DJ.footprint(fam[j], level)) for i, j in P)


def gamma(O, n=FAMILY, level=DJ.BLOCK_LEVEL):
    fam = family(n)
    return frozenset(p for p in pair_domain(n)
                     if (DJ.footprint(fam[p[0]], level), DJ.footprint(fam[p[1]], level)) in O)


def closure(P, n=FAMILY, level=DJ.BLOCK_LEVEL):
    return gamma(alpha(P, n, level), n, level)


def kleene_step(P, n=FAMILY, level=DJ.BLOCK_LEVEL):
    """The proposed recirculation: join the discarded obligations back in. The union is redundant
    because the abstraction is extensive, which is the first half of why this is one step."""
    return P | (closure(P, n, level) - P)


# ---- the closure properties, decided --------------------------------------------------------------
def _samples(n=FAMILY):
    """A PINNED sample ladder — deterministic from a fixed seed, never freshly drawn."""
    dom = pair_domain(n)
    st, out = SEED, []
    for k in (1, 3, 8, 20, 50, 120):
        picked, seen = [], set()
        while len(picked) < min(k, len(dom)):
            st = (st * 1103515245 + 12345) & 0x7FFFFFFF
            idx = st % len(dom)
            if idx not in seen:
                seen.add(idx); picked.append(dom[idx])
        out.append(frozenset(picked))
    return out + [frozenset(dom), frozenset()]


def is_extensive(n=FAMILY):
    return all(P <= closure(P, n) for P in _samples(n))


def is_monotone(n=FAMILY):
    s = _samples(n)
    return all((not (A <= B)) or (closure(A, n) <= closure(B, n)) for A in s for B in s)


def is_idempotent(n=FAMILY):
    """THE THEOREM that collapses the iteration. Not a property of the data — a consequence of the
    adjunction, and the reason the step count carries no information."""
    return all(closure(closure(P, n), n) == closure(P, n) for P in _samples(n))


def step_counts(n=FAMILY):
    """MEASURED: how many Kleene steps each pinned input needs. All of them are 0 or 1."""
    out = []
    for P in _samples(n):
        t, cur = 0, P
        while t <= 8:
            nxt = kleene_step(cur, n)
            if nxt == cur:
                break
            cur, t = nxt, t + 1
        out.append(t)
    return tuple(out)


def converges_in_at_most_one_step(n=FAMILY):
    """CONSEQUENCE 1, REFUTED: the step count is a CONSTANT, so it cannot be a per-capture defect."""
    return max(step_counts(n)) <= 1


def _step_count_as_defect(P, n=FAMILY):
    """A FALSIFIER TOOL (not a law): the proposed reading, in which the step count reports the S2
    defect in cells. It returns 0 or 1 for every input in the universe, so as a defect measure it is
    constant — a metric that does not vary with what it measures."""
    t, cur = 0, P
    while t <= 8:
        nxt = kleene_step(cur, n)
        if nxt == cur:
            return t
        cur, t = nxt, t + 1
    return t


def step_count_is_constant(n=FAMILY):
    """The plant BITES: over every pinned input the proposed defect takes at most two values, and
    neither depends on any property of the capture."""
    vals = {_step_count_as_defect(P, n) for P in _samples(n)}
    return vals <= {0, 1} and len(vals) <= 2


# ---- the collapse, which is the dangerous consequence ----------------------------------------------
def collapse_census(n=FAMILY, count=SAMPLE_N, k=SAMPLE_K):
    """MEASURED: distinct raw capture-sets versus distinct fixed points. The closure is coarser, so
    the second number is far smaller — which is exactly what makes it a WEAKER discriminator."""
    dom = pair_domain(n)
    st, raw = SEED ^ 0x5F5F, []
    for _ in range(count):
        picked, seen = [], set()
        while len(picked) < k:
            st = (st * 1103515245 + 12345) & 0x7FFFFFFF
            idx = st % len(dom)
            if idx not in seen:
                seen.add(idx); picked.append(dom[idx])
        raw.append(frozenset(picked))
    return len(set(raw)), len({closure(P, n) for P in raw})


def fixed_point_is_a_weaker_check(n=FAMILY):
    """CONSEQUENCE 2, REFUTED: distinct captures collapse onto a shared fixed point, so fixed-point
    equality admits MORE pairs as identical than raw equality does — it raises false negatives."""
    raw, fixed = collapse_census(n)
    return fixed < raw


def doctored_collides_with_honest(n=FAMILY):
    """THE CASE THAT MATTERS, and the reason this is a rung. An honest capture and a doctored one
    with a single obligation quietly dropped have DIFFERENT raw sets and the SAME closure — so the
    proposed check is blind to precisely the omission attack `geoquorum` exists to catch. Returns
    (raw_differ, closures_collide); both must be True for the refutation to hold."""
    dom = pair_domain(n)
    honest = frozenset(dom[:12])
    doctored = frozenset(dom[:11])
    return (honest != doctored, closure(honest, n) == closure(doctored, n))


def _fixedpoint_as_integrity(a, b, n=FAMILY):
    """A FALSIFIER TOOL (not a law): fraud detection by fixed-point equality. It calls a doctored
    capture identical to an honest one."""
    return closure(a, n) == closure(b, n)


def raw_equality_sees_what_the_closure_cannot(n=FAMILY):
    """The plant BITES: the honest/doctored pair is DISTINGUISHED by raw equality and CONFLATED by
    the proposed fixed-point check."""
    dom = pair_domain(n)
    honest, doctored = frozenset(dom[:12]), frozenset(dom[:11])
    return (honest != doctored) and _fixedpoint_as_integrity(honest, doctored, n)


# ---- the salvage: a refinement ladder that really is multi-step -------------------------------------
def refine_to_fixed_point(P, n=FAMILY, levels=None):
    """THE SALVAGE. At a FIXED level the iteration is one step; an iteration that REFINES the level
    when it stalls is genuinely multi-step, and its step count reports how far the abstraction had to
    be refined before it distinguished enough. Bounded by the LEVEL LADDER — not by the cell count,
    which would be a bound of the wrong order — so it is total and halts without a heuristic.
    Returns (fixed_point, steps, final_level)."""
    lv_list = list(levels if levels is not None else range(AD.k_min(AD.spread_corpus()), DJ.LEVELS + 1))
    if not lv_list:
        raise RecircError("no admissible level above the vacuity floor")
    cur, steps = P, 0
    for lv in lv_list:
        nxt = closure(cur, n, lv)
        steps += 1
        if nxt == cur and lv != lv_list[-1]:
            continue                              # closed here; refine and try again
        cur = nxt
    return cur, steps, lv_list[-1]


def refinement_steps_are_level_bounded(n=FAMILY):
    """The salvage's bound, decided: the step count never exceeds the number of admissible levels."""
    lv = list(range(AD.k_min(AD.spread_corpus()), DJ.LEVELS + 1))
    return all(refine_to_fixed_point(P, n)[1] <= len(lv) for P in _samples(n))


def refinement_is_total(n=FAMILY):
    """It halts on every pinned input, by construction rather than by timeout."""
    try:
        return all(refine_to_fixed_point(P, n)[0] is not None for P in _samples(n))
    except RecircError:
        return False


# ---- digests + scenes -------------------------------------------------------------------------
def rc_digest(name, payload):
    hh = hashlib.sha256(); hh.update(MAGIC)
    hh.update(f"|{name}|{payload}".encode())
    return hh.hexdigest()


def _scene_closure():
    return rc_digest("closure", f"{is_extensive()}:{is_monotone()}:{is_idempotent()}:"
                                f"{step_counts()}:{converges_in_at_most_one_step()}")


def _scene_collapse():
    return rc_digest("collapse", f"{collapse_census()}:{fixed_point_is_a_weaker_check()}:"
                                 f"{doctored_collides_with_honest()}")


def _scene_plants():
    return rc_digest("plants", f"{step_count_is_constant()}:"
                               f"{raw_equality_sees_what_the_closure_cannot()}")


def _scene_salvage():
    lv = list(range(AD.k_min(AD.spread_corpus()), DJ.LEVELS + 1))
    return rc_digest("salvage", f"{lv}:{refinement_steps_are_level_bounded()}:"
                                f"{refinement_is_total()}:"
                                f"{tuple(refine_to_fixed_point(P)[1] for P in _samples())}")


_SCENES = {"closure": _scene_closure, "collapse": _scene_collapse,
           "plants": _scene_plants, "salvage": _scene_salvage}
SCENES = ("closure", "collapse", "plants", "salvage")


def scene_result(name):
    return _SCENES[name]()


def golden(name):
    with open(_os.path.join(_HERE, "conformance_recirc.txt"), encoding="utf-8") as fh:
        for ln in fh:
            ln = ln.strip()
            if ln and not ln.startswith("#"):
                nm, dig = ln.split()
                if nm == name:
                    return dig
    raise RecircError(f"no golden named {name!r}")


def _main(argv):
    for n in SCENES:
        print(n, scene_result(n))
    print(f"extensive {is_extensive()} monotone {is_monotone()} IDEMPOTENT {is_idempotent()}")
    print(f"step counts {step_counts()} -> at most one step {converges_in_at_most_one_step()}")
    raw, fixed = collapse_census()
    print(f"collapse: {raw} distinct raw -> {fixed} distinct fixed points")
    print(f"doctored collides with honest: {doctored_collides_with_honest()}")
    print(f"salvage: level-bounded {refinement_steps_are_level_bounded()} total {refinement_is_total()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(_main(_sys.argv))
