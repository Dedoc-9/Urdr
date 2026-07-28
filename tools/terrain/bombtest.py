# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""bombtest — INTERACTION-FREE TAMPER DETECTION (URDRBMB1): certifying that a recorded computation
contains an illegal step WITHOUT EVER RUNNING THE STEP. NO NEW GLYPH.

THE PROBLEM THIS IS FOR. The Dentatus Replay Court proves a published result is the untampered
consequence of its recorded inputs by RE-RUNNING the workflow bit-for-bit. That is the strongest
check available and it has one cost that is not a matter of engineering: it requires possessing the
inputs and executing the rules. A reviewer holding embargoed patient data, a proprietary model under
licence, or a climate run that costs a week of cluster time cannot pay it. Re-execution is the
detonation.

    THE ELITZUR-VAIDMAN QUESTION, TRANSPOSED: can a reviewer certify that a trail is tampered
    WITHOUT executing the tampered step?

THE STRUCTURE THAT TRANSFERS, AND IT IS NOT THE PHYSICS. Strip the interferometer and five things
remain: (a) a check that in the honest case CANCELS to a constant; (b) tampering breaks the
cancellation; (c) the firing certifies with NO false positives — one-sided; (d) silence is
INCONCLUSIVE, not innocence; (e) efficiency is improvable by adding arms, at a cost. All five are
classical and all five are implemented here. What does NOT transfer is the part that makes EV
remarkable: a real bomb's mere DISPOSITION to absorb alters the amplitude with no absorption
occurring, and there is no classical mechanism for that. Here "interaction-free" means one thing
only, and it is measured rather than asserted:

    the audit path invokes the rule EXACTLY ZERO times, instrumented as a call count

That is a claim about ACCESS AND COST, not about physics, and treating the analogy as more than
structural would be the inflation this repo exists to refuse.

THE DARK PORT IS A NEVER CLAIM. Holzmann's SPIN checks a property by composing the system with an
automaton that must NEVER accept; an accepting run IS the counterexample. That is precisely the dark
port — a detector wired so that in the honest case it cannot fire. Soundness here is therefore a
never-claim discharged by exhaustive exploration: over the FULL state space and every legal
transition, no conserved functional is ever broken: 4096 states, 13824 LEGAL transitions, 0
acceptances. (The first draft of this sentence said 24576, which is 4096 x 6 — every state times
every rule, counting the boundary-blocked moves that never fire. Writing down a product instead of
reading the counter is the same class of error as reporting a sample as a universal, and it is
corrected here rather than rounded to.) Without the never-claim the detector has false positives, and
a screen that condemns honest work is worse than no screen.

THE BLIND SPOT IS EXACTLY A KERNEL, COMPUTED AND NOT SAMPLED. A tamper is invisible precisely when
its delta lies in the kernel of every active invariant, so the dud class is a linear subspace and its
size is a closed form: with k of the 3 independent invariants active, the invisible tampers number
3^k * 9^(3-k), giving an exact detection ladder

    k = 1: 486/728      k = 2: 648/728      k = 3: 702/728

decided against enumeration with 0 exceptions. Adding invariants is the Zeno move — more arms, higher
efficiency — and its price is that EACH new invariant must itself discharge the never-claim or it
starts condemning honest trails.

THE CEILING, STATED PLAINLY. Detection efficiency is measured against a NON-ADAPTIVE tamperer. An
adversary who knows the invariants chooses a delta from the kernel and is caught with probability
EXACTLY ZERO, which is measured here rather than left as a caveat. That is the difference in kind
between this and a keyed MAC, and it is why the screen does not replace either the hash chain or the
court: the chain catches post-hoc edits but says nothing about whether a transition was LEGAL, the
screen catches illegal transitions at zero execution but is evadable by anyone who reads it, and the
court catches everything at the price of running the whole computation. Three tiers, disjoint
failure modes, and the cheap one is a SCREEN rather than a verdict.

GRADE. MEASURED: the never-claim discharged over the full state space, 0 acceptances, with a planted
non-conserved functional producing violations; the detection ladder against enumeration, 0
exceptions; the kernel closed form; the zero-invocation property as an instrumented count against
the court's trail-length count; trail-independence of detection; three plants biting; determinism.
DECLARED: the workflow is a bounded integer lattice with pairwise-conserving rules — a MODEL of a
stoichiometric or accounting workload, chosen because its conserved functionals are exactly
computable, and a workload whose invariants are unknown or nonlinear inherits nothing from the
ladder; the tamper alphabet is single-state deltas in {-1,0,1}^6 kept in range. does_not_show: WHICH
value was correct — the screen localizes to a step and never recovers the true output; that silence
is innocence, which is the whole one-sidedness and is measured as a nonzero dud class; that the
science is right, since this is the integrity half only, exactly as Dentatus states — INTEGRITY IS
NOT TRUTH, and a bit-perfectly reproducible result can still be wrong."""
import hashlib
import os as _os
import sys as _sys
from itertools import product as _prod

_HERE = _os.path.dirname(_os.path.abspath(__file__))
if _HERE not in _sys.path:
    _sys.path.insert(0, _HERE)

MAGIC = b"URDRBMB1"
PAIRS = 3                        # three conserved pairs -> three independent invariants
COORDS = 2 * PAIRS
VMAX = 3                         # each coordinate lives in 0..VMAX
START = (1, 2, 1, 2, 1, 2)
TRAIL_LEN = 4
TRAIL_CAP = 24                   # trails are CAPPED and the cap is reported, never silent

_INVOCATIONS = {"apply_rule": 0}


class BombTestError(Exception):
    def __init__(self, message):
        super().__init__(f"BOMBTEST-REFUSE: {message}")
        self.code = "BOMBTEST-REFUSE"


class TamperDetected(Exception):
    """The dark port fired. A tamper reported as advisory is a tamper that gets published."""
    def __init__(self, message):
        super().__init__(f"BOMBTEST-TAMPERED: {message}")
        self.code = "BOMBTEST-TAMPERED"


# ---- the workflow ------------------------------------------------------------------------------------
def rules():
    """Each rule moves one unit within a conserved pair. The pair sums are the physical law; the
    direction of travel is the model."""
    out = []
    for p in range(PAIRS):
        i, j = 2 * p, 2 * p + 1
        out.append((i, j))
        out.append((j, i))
    return tuple(out)


RULES = rules()


def apply_rule(state, r):
    """THE ONLY FUNCTION THAT EXECUTES ANYTHING. Every call is counted, because the entire
    interaction-free claim is a statement about this counter."""
    _INVOCATIONS["apply_rule"] += 1
    src, dst = RULES[r]
    s = list(state)
    if s[src] < 1 or s[dst] >= VMAX:
        return None
    s[src] -= 1
    s[dst] += 1
    return tuple(s)


def invocations():
    return _INVOCATIONS["apply_rule"]


def reset_invocations():
    _INVOCATIONS["apply_rule"] = 0


# ---- the invariants (the arms of the interferometer) ---------------------------------------------------
def invariant(state, p):
    """The p-th conserved functional: the sum of a conserved pair. Reading it touches no rule."""
    return state[2 * p] + state[2 * p + 1]


def signature(state, k=PAIRS):
    """The k active arms, as a tuple. THIS IS THE WHOLE AUDIT INSTRUMENT."""
    return tuple(invariant(state, p) for p in range(k))


def in_range(state):
    return all(0 <= v <= VMAX for v in state)


# ---- the never claim (soundness: the dark port cannot fire on honest work) -------------------------------
def never_claim_census():
    """SPIN'S MOVE: an automaton wired so that ACCEPTANCE IS THE BUG. Here it accepts when a LEGAL
    transition breaks a conserved functional. Exhaustive over the full state space and every rule.
    Returns (transitions_checked, acceptances, states); acceptances must be 0 or the screen has FALSE
    POSITIVES, and a screen that condemns honest work is worse than no screen at all."""
    checked = accepted = states = 0
    for state in _prod(range(VMAX + 1), repeat=COORDS):
        states += 1
        for r in range(len(RULES)):
            nxt = apply_rule(state, r)
            if nxt is None:
                continue
            checked += 1
            if signature(nxt) != signature(state):
                accepted += 1
    return checked, accepted, states


def never_claim_is_discharged():
    checked, accepted, _s = never_claim_census()
    return accepted == 0 and checked > 0


def _unconserved_functional(state):
    """A FALSIFIER TOOL: a functional the rules do NOT preserve — a single coordinate. Wired in as an
    arm it would fire on honest trails, which is the failure mode that matters most."""
    return (state[0],)


def planted_functional_breaks_the_never_claim():
    """The plant BITES: with a non-conserved arm the never-claim ACCEPTS, so the exhaustive check is
    a live falsifier and not decoration. Returns (acceptances_with_plant, acceptances_honest)."""
    bad = 0
    for state in _prod(range(VMAX + 1), repeat=COORDS):
        for r in range(len(RULES)):
            nxt = apply_rule(state, r)
            if nxt is None:
                continue
            if _unconserved_functional(nxt) != _unconserved_functional(state):
                bad += 1
    return bad, never_claim_census()[1]


# ---- trails ---------------------------------------------------------------------------------------------
def trails(cap=TRAIL_CAP, length=TRAIL_LEN, start=START):
    """Legal rule sequences from `start`, in deterministic order, CAPPED at `cap`. The cap is a real
    bound on coverage and `trail_cap_is_reported` exists so it can never read as exhaustive."""
    out, frontier = [], [(start, (), (start,))]
    while frontier and len(out) < cap:
        state, seq, path = frontier.pop(0)
        if len(seq) == length:
            out.append(path)
            continue
        for r in range(len(RULES)):
            nxt = apply_rule(state, r)
            if nxt is not None:
                frontier.append((nxt, seq + (r,), path + (nxt,)))
    return tuple(out[:cap])


def trail_cap_is_reported(cap=TRAIL_CAP, length=TRAIL_LEN):
    """NO SILENT TRUNCATION: returns (kept, cap, was_capped)."""
    full, frontier = 0, [(START, ())]
    while frontier:
        state, seq = frontier.pop(0)
        if len(seq) == length:
            full += 1
            continue
        for r in range(len(RULES)):
            nxt = apply_rule(state, r)
            if nxt is not None:
                frontier.append((nxt, seq + (r,)))
    return len(trails(cap, length)), full, full > cap


def chain(path):
    """The content-addressed trail. Present so the screen and the chain can be compared rather than
    conflated — they catch DISJOINT things."""
    h = hashlib.sha256(); h.update(MAGIC)
    for s in path:
        h.update(b"|" + ",".join(str(v) for v in s).encode())
    return h.hexdigest()


# ---- THE AUDIT: zero invocations ---------------------------------------------------------------------------
def audit(path, k=PAIRS):
    """THE INTERACTION-FREE SCREEN. It reads the declared states and compares their signatures. It
    NEVER calls apply_rule — that is the whole claim, and `audit_invokes_nothing` measures it rather
    than trusting this sentence. Returns the index of the first broken adjacency, or None."""
    for i in range(len(path) - 1):
        if signature(path[i], k) != signature(path[i + 1], k):
            return i
    return None


def replay_court(path):
    """THE BASELINE, and it is not a plant — it is the stronger check. It re-executes every step and
    catches EVERYTHING, at a cost of one rule invocation per step per candidate rule. This is what a
    reviewer cannot always pay."""
    for i in range(len(path) - 1):
        if not any(apply_rule(path[i], r) == path[i + 1] for r in range(len(RULES))):
            return i
    return None


def audit_invokes_nothing(k=PAIRS):
    """THE OPERATIONAL MEANING OF 'INTERACTION-FREE', INSTRUMENTED. Returns
    (audit_invocations, court_invocations); the first must be exactly 0 and the second positive."""
    path = trails()[0]
    reset_invocations()
    audit(path, k)
    a = invocations()
    reset_invocations()
    replay_court(path)
    c = invocations()
    return a, c


# ---- the detection ladder, and the kernel that is its blind spot ---------------------------------------------
def _tamper_alphabet():
    return tuple(d for d in _prod((-1, 0, 1), repeat=COORDS) if any(d))


def kernel_size_closed_form(k):
    """THE BLIND SPOT AS A CLOSED FORM: a tamper is invisible exactly when its delta balances within
    every ACTIVE pair and is unconstrained on the rest, so the invisible deltas number
    3^k * 9^(PAIRS-k) counting the zero vector."""
    if not (0 <= k <= PAIRS):
        raise BombTestError("k must index the available invariants")
    return 3 ** k * 9 ** (PAIRS - k)


def detection_census(k):
    """DECIDED by enumeration over every tamper delta: how many the k active arms catch. Returns
    (detected, total)."""
    alpha = _tamper_alphabet()
    det = sum(1 for d in alpha
              if any(d[2 * p] + d[2 * p + 1] != 0 for p in range(k)))
    return det, len(alpha)


def detection_ladder():
    return tuple((k,) + detection_census(k) for k in range(1, PAIRS + 1))


def ladder_matches_the_closed_form():
    """The enumeration and the closed form must agree, and they are computed by different routes —
    one counts caught deltas, the other counts uncaught ones from a formula."""
    alpha = len(_tamper_alphabet())
    for k in range(1, PAIRS + 1):
        det, total = detection_census(k)
        if total != alpha or det != alpha + 1 - kernel_size_closed_form(k):
            return False
    return True


def detection_is_trail_independent(k=PAIRS):
    """A REAL FINDING, not a convenience: because every arm is LINEAR, whether a tamper is caught
    depends only on its DELTA — not on where in the trail it lands nor on which trail. Returns
    (agreements, exceptions) over every trail, position and delta that stays in range."""
    agree = exc = 0
    for path in trails():
        for pos in range(len(path)):
            for d in _tamper_alphabet():
                cand = tuple(a + b for a, b in zip(path[pos], d))
                if not in_range(cand):
                    continue
                tampered = path[:pos] + (cand,) + path[pos + 1:]
                caught = audit(tampered, k) is not None
                expect = any(d[2 * p] + d[2 * p + 1] != 0 for p in range(k))
                if caught == expect:
                    agree += 1
                else:
                    exc += 1
    return agree, exc


# ---- the ceiling: an adaptive tamperer is never caught ---------------------------------------------------------
def _tamper_from_the_kernel(k=PAIRS):
    """A FALSIFIER TOOL, and the honest ceiling: an adversary who has READ the invariants picks a
    delta that balances within every active pair."""
    for d in _tamper_alphabet():
        if all(d[2 * p] + d[2 * p + 1] == 0 for p in range(k)):
            return d
    raise BombTestError("no kernel delta exists")


def adaptive_tamperer_is_never_caught(k=PAIRS):
    """MEASURED, not caveated: over every trail and position, a kernel tamper is caught 0 times.
    Returns (caught, attempted); the first must be 0 and the second positive."""
    d = _tamper_from_the_kernel(k)
    caught = attempted = 0
    for path in trails():
        for pos in range(len(path)):
            cand = tuple(a + b for a, b in zip(path[pos], d))
            if not in_range(cand):
                continue
            attempted += 1
            if audit(path[:pos] + (cand,) + path[pos + 1:], k) is not None:
                caught += 1
    return caught, attempted


def the_court_catches_what_the_screen_misses(k=PAIRS):
    """THE THREE TIERS ARE COMPLEMENTARY, DECIDED. The kernel tamper the screen cannot see is caught
    by re-execution, and by the hash chain. Returns (screen_caught, court_caught, chain_changed)."""
    d = _tamper_from_the_kernel(k)
    for path in trails():
        for pos in range(len(path)):
            cand = tuple(a + b for a, b in zip(path[pos], d))
            if not in_range(cand):
                continue
            bad = path[:pos] + (cand,) + path[pos + 1:]
            return (audit(bad, k) is not None, replay_court(bad) is not None,
                    chain(bad) != chain(path))
    raise BombTestError("no in-range kernel tamper available")


def _silence_is_innocence(path, k=PAIRS):
    """A FALSIFIER TOOL, and it is THE Elitzur-Vaidman error: reading a quiet dark port as proof the
    bomb is a dud. The screen not firing is INCONCLUSIVE and nothing more."""
    return audit(path, k) is None


def silence_plant_bites(k=PAIRS):
    """The plant BITES on exactly the kernel: a tampered trail it declares clean."""
    d = _tamper_from_the_kernel(k)
    for path in trails():
        for pos in range(len(path)):
            cand = tuple(a + b for a, b in zip(path[pos], d))
            if not in_range(cand) or cand == path[pos]:
                continue
            bad = path[:pos] + (cand,) + path[pos + 1:]
            if _silence_is_innocence(bad, k) and replay_court(bad) is not None:
                return True
    return False


def _detect_by_chain_only(path, published_root):
    """A FALSIFIER TOOL: check only the content-addressed chain. It catches a post-hoc edit and is
    blind to a tamperer who RECOMPUTES the root — which is exactly the case a forensics court exists
    for, since the person who publishes the root is the person under audit."""
    return chain(path) != published_root


def chain_only_plant_bites(k=PAIRS):
    """The plant BITES: with the root recomputed over the tampered trail, the chain check goes quiet
    while the screen still fires. Returns (chain_caught, screen_caught)."""
    for path in trails():
        for pos in range(len(path)):
            for d in _tamper_alphabet():
                cand = tuple(a + b for a, b in zip(path[pos], d))
                if not in_range(cand) or cand == path[pos]:
                    continue
                bad = path[:pos] + (cand,) + path[pos + 1:]
                if audit(bad, k) is None:
                    continue
                return _detect_by_chain_only(bad, chain(bad)), audit(bad, k) is not None
    raise BombTestError("no detectable tamper available")


# ---- the refusal ------------------------------------------------------------------------------------------------
def adjudicate(path, k=PAIRS):
    """THE AUTHORITATIVE CALL. Fires as an exception; a screen that returns a warning is a screen
    whose output gets published anyway."""
    i = audit(path, k)
    if i is not None:
        raise TamperDetected(f"conserved functional broken between steps {i} and {i + 1}")
    return True


def refuses_a_detectable_tamper():
    path = trails()[0]
    bad = list(path)
    bad[1] = tuple(v + (1 if idx == 0 else 0) for idx, v in enumerate(bad[1]))
    if not in_range(bad[1]):
        raise BombTestError("fixture out of range")
    try:
        adjudicate(tuple(bad))
    except TamperDetected as exc:
        return exc.code == "BOMBTEST-TAMPERED"
    return False


def admits_an_honest_trail():
    return adjudicate(trails()[0]) is True


# ---- digests + scenes ---------------------------------------------------------------------------------------------
def bt_digest(name, payload):
    hh = hashlib.sha256(); hh.update(MAGIC)
    hh.update(f"|{name}|{payload}".encode())
    return hh.hexdigest()


def _scene_neverclaim():
    return bt_digest("neverclaim", f"{never_claim_census()}:{never_claim_is_discharged()}:"
                                   f"{planted_functional_breaks_the_never_claim()}")


def _scene_ladder():
    return bt_digest("ladder", f"{detection_ladder()}:{ladder_matches_the_closed_form()}:"
                               f"{[kernel_size_closed_form(k) for k in range(PAIRS + 1)]}:"
                               f"{detection_is_trail_independent()}")


def _scene_freeness():
    return bt_digest("freeness", f"{audit_invokes_nothing()}:{trail_cap_is_reported()}:"
                                 f"{adaptive_tamperer_is_never_caught()}:"
                                 f"{the_court_catches_what_the_screen_misses()}:"
                                 f"{silence_plant_bites()}:{chain_only_plant_bites()}")


_SCENES = {"neverclaim": _scene_neverclaim, "ladder": _scene_ladder, "freeness": _scene_freeness}
SCENES = ("neverclaim", "ladder", "freeness")


def scene_result(name):
    return _SCENES[name]()


def golden(name):
    with open(_os.path.join(_HERE, "conformance_bombtest.txt"), encoding="utf-8") as fh:
        for ln in fh:
            ln = ln.strip()
            if ln and not ln.startswith("#"):
                nm, dig = ln.split()
                if nm == name:
                    return dig
    raise BombTestError(f"no golden named {name!r}")


def _main(argv):
    for n in SCENES:
        print(n, scene_result(n))
    print(f"never claim (checked, accepted, states) {never_claim_census()} -> discharged "
          f"{never_claim_is_discharged()}")
    print(f"planted non-conserved arm (bad, honest) {planted_functional_breaks_the_never_claim()}")
    print(f"detection ladder (k, detected, total) {detection_ladder()}")
    print(f"kernel closed form {[kernel_size_closed_form(k) for k in range(PAIRS + 1)]} "
          f"| matches enumeration {ladder_matches_the_closed_form()}")
    print(f"trail-independence (agree, exceptions) {detection_is_trail_independent()}")
    print(f"INTERACTION-FREE (audit calls, court calls) {audit_invokes_nothing()}")
    print(f"trail cap (kept, full, capped) {trail_cap_is_reported()}")
    print(f"adaptive tamperer (caught, attempted) {adaptive_tamperer_is_never_caught()}")
    print(f"three tiers (screen, court, chain) {the_court_catches_what_the_screen_misses()}")
    print(f"plants: silence {silence_plant_bites()} | chain-only {chain_only_plant_bites()}")
    print(f"refuses tamper {refuses_a_detectable_tamper()} | admits honest {admits_an_honest_trail()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(_main(_sys.argv))
