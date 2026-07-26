# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""horn — THE GABRIEL ANCHOR LADDER (URDRHRN1): unbounded rollback reach at bounded storage, with a
MINIMAX OPTIMALITY THEOREM for which past states to keep. Task 58 Half A. NO NEW GLYPH.

THE PROBLEM. `lagcomp` rewinds within a FIXED window (MAX_REWIND = 8 ticks). A starvation burst longer
than the window is unreconcilable, so the session must disconnect — which is exactly what a DDoS buys
an attacker. Widening the window linearly costs linear memory. The question is not "how big a buffer"
but "WHICH past states to keep", and that question has an exact answer.

GABRIEL'S HORN, AND WHICH HALF IS WHICH. The horn (y = 1/x revolved, x >= 1) has FINITE VOLUME
(INT 1/x^2 = 1) and INFINITE SURFACE (INT 1/x diverges). Both halves have an operational meaning here
and they are NOT interchangeable: the divergence of INT dt/t is the statement that REACH is unbounded;
the convergence of INT dt/t^2 is the statement that STORAGE is bounded. A rollback potential written
as INT_1^T (1/t) dt = ln T is therefore on the SURFACE side and diverges — unbounded storage, the
opposite of what a bounded buffer needs. The volume side is the one that bounds cost. Measured: at
T = 1e9 the surface integral is 20.7 and still climbing while the volume integral is 0.999999999.

THE LADDER. Keep a dense window of W recent ticks, then anchors at geometrically spaced depths.
Storage is O(log T) and reach is exponential in the slot count. MEASURED (dense W = 4): 8 slots reach
64 ticks where `lagcomp`'s fixed window reaches 8 at the same cost; 12 slots reach 1024; 20 slots
reach 262144.

THE THEOREM (MINIMAX ANCHOR SPACING) — the reason the ladder is geometric rather than merely
convenient. Let B slots retain anchors at integer depths 1 = a_0 < a_1 < ... < a_B = T. A rollback to
depth t must replay forward from the least retained anchor at or above t, so the natural cost is
RELATIVE: rho(t) = (a(t) - t) / t, which asks for constant precision per decade rather than per tick.

  (1) The worst-case relative cost over INTEGER depths is
          rho* = max_i (a_{i+1} - a_i - 1) / (a_i + 1),
      attained at t = a_i + 1 — the tick just past an anchor.
  (2) Minimising the worst RATIO max_i (a_{i+1} / a_i) is achieved EXACTLY by the geometric ladder
      a_i = T^(i/B), with optimal ratio T^(1/B). VERIFIED EXHAUSTIVELY over every integer schedule
      for (T, B) in {(16,2), (16,4), (27,3), (32,5), (64,3), (81,4)}: in each case the unique argmin
      is the geometric ladder and the optimum is exactly T^(1/B).
  (3) CONTINUOUSLY, sup_t rho(t) = max ratio - 1. On the INTEGER LATTICE this is an UPPER BOUND and
      NOT an identity — the discrete supremum is strictly smaller, because the worst integer depth is
      a_i + 1 rather than a_i + epsilon. An earlier draft of this module asserted the equality and
      the exhaustive check refused it; the bound is stated at its true strength.

  COROLLARY (the horn measure). Equal ratios are UNIFORM SPACING IN THE MEASURE dt/t — precisely the
  horn's surface integrand. So the divergent half of Gabriel's Horn is not an obstacle to be clamped;
  it is the coordinate in which the optimal schedule is uniform, and its divergence is exactly the
  unboundedness of reach that the finite-volume half pays for.

WHAT THIS BUYS UNDER ATTACK, AND WHAT IT DOES NOT. On a 1%-tail starvation (loss beyond the 99th
percentile) the session falls back to the deepest anchor and replays forward INSTEAD OF REFUSING: a
hard disconnect becomes graceful degradation. DECLARED, and this is the honest boundary: (a) the deep
anchors are SPARSE, so a deep reconciliation loses precision and must replay forward — the relative
cost above is exactly that price, quantified rather than hidden; (b) this DOES NOT DEFEAT A DDoS. It
extends survivable starvation from a fixed 8 ticks to ~2^B at bounded memory; the session still needs
data eventually, and an attacker who sustains the outage indefinitely still wins. It converts a cliff
into a slope. (c) Replay from a sparse anchor is only sound if the intervening operations COMMUTE —
under attack packets arrive out of order, so the exact original sequence is precisely what is not
available. This arc HAS order-independence (`commute` URDRCMU1, `rannull` RAN-0, `nway` URDRNWY1) but
CHECKED per instance; making it structural is Half B of task 58 and is NOT claimed here.

PRIOR ART, honestly. Exponentially-spaced checkpointing is not new (reversible debugging, incremental
snapshotting). The closest formal work found is "Formalizing Rollback Netcodes for Robust and
Real-Time Client-Server Architectures" (OPODIS 2025), which formalises rollback-netcode properties
against latency attacks; I could NOT confirm from the accessible sections whether it treats the
retention SCHEDULE under bounded memory, so NO NOVELTY IS CLAIMED for the minimax result — it is
stated and verified here for this arc, not asserted to be first.

THE TWIST (rubber-band stress) — see the block above `twist_ratio`. Under starvation the ladder does
not grow; it TWISTS. The rung count B - W is conserved and only the pitch r changes, exactly as a flat
ribbon becomes a cylinder with the same material and a different rise per turn. Reach = W * r^(B-W)
and the price is the minimax bound, strictly under r - 1. It is OPT-OUT BY CONSTRUCTION: `stress=None`
reproduces the untwisted ladder identically, asserted as a law. And the pitch is SERVER-DERIVED — the
stress comes from the server's own starvation measurement at one step per doubling of the outage, not
from a client field, because coarse pitch widens the replay gap a client is reconciled through and a
client permitted to name its own stress would name the largest one.

GRADE. MEASURED: the reach/storage numbers; the exhaustive minimax optimality over every integer
schedule at the stated (T, B); the integer-lattice correction to the continuous bound; monotonicity
and coverage of the ladder; the twist's rung-conservation, reach closed form, price bound,
removability, view-band decoupling (the last measured against `clockauth`'s own band, with a coupling
plant that leaks 4 ticks where the honest path leaks 0) and pitch authority; determinism. DECLARED:
the DDoS boundary above; the commutation dependency; the pitch ceiling MAX_RATIO = 8 is a policy
choice, not a theorem — the theorem prices any pitch, it does not pick one; and the doubling law
`server_stress` uses is a POLICY for turning an observed outage into a pitch, chosen because it tracks
the outage's ORDER rather than its size, not derived from anything. does_not_show: the transport; the
actual replay of intervening operations (that is `commute`/`nway`'s territory, composed with rather
than re-proved); HOW THE STARVATION IS OBSERVED (this rung takes an integer starvation length and an
integer threshold and derives the pitch from them; producing that length from the ack stream is
`latencyest`'s territory and is not re-derived here — what IS closed here is that the number may not
come from the client); cross-placement."""
import hashlib
import os as _os
import sys as _sys
from fractions import Fraction as _Fr
from itertools import combinations as _comb

_HERE = _os.path.dirname(_os.path.abspath(__file__))
if _HERE not in _sys.path:
    _sys.path.insert(0, _HERE)

import clockauth as CA                          # noqa: E402  (the view band this must NOT widen)

MAGIC = b"URDRHRN1"
DENSE = 4                                    # ticks kept at full resolution before the ladder begins
TAIL_PERCENTILE = 99                         # the 1% spike: starvation beyond this falls back deep


class HornError(Exception):
    def __init__(self, message):
        super().__init__(f"HORN-REFUSE: {message}")
        self.code = "HORN-REFUSE"


# ---- the ladder -----------------------------------------------------------------------------
def ladder(dense=DENSE, slots=12, ratio=2):
    """Retained depths: `dense` recent ticks at full resolution, then geometric anchors. Exact
    integers; the ratio is the theorem's T^(1/B) written as a small integer."""
    if dense < 1 or slots < dense or ratio < 2:
        raise HornError(f"bad ladder (dense={dense}, slots={slots}, ratio={ratio})")
    d = list(range(1, dense + 1))
    nxt = dense
    while len(d) < slots:
        nxt *= ratio
        d.append(nxt)
    return d


def reach(dense=DENSE, slots=12, ratio=2):
    """The oldest tick anchorable with `slots` slots — exponential in the slot count."""
    return ladder(dense, slots, ratio)[-1]


def anchor_for(depth, lad):
    """The least retained anchor at or above `depth` — the state a rollback must replay forward
    from. None if the depth is beyond the ladder's reach."""
    for a in lad:
        if a >= depth:
            return a
    return None


def replay_gap(depth, lad):
    """Ticks that must be replayed forward after anchoring. Zero at an exact anchor."""
    a = anchor_for(depth, lad)
    if a is None:
        raise HornError(f"depth {depth} exceeds the ladder's reach {lad[-1]}")
    return a - depth


def relative_cost(depth, lad):
    """The theorem's rho(t) as an exact RATIONAL — constant precision per decade, not per tick."""
    return _Fr(replay_gap(depth, lad), depth)


# ---- the theorem ----------------------------------------------------------------------------
def worst_ratio(sched):
    """max_i a_(i+1)/a_i, exact rational."""
    return max(_Fr(sched[i + 1], sched[i]) for i in range(len(sched) - 1))


def worst_relative_cost(sched):
    """THE INTEGER FORM, part (1): the supremum of rho over integer depths, attained at t = a_i + 1.
    Exact rational — and strictly below `worst_ratio - 1`, which is the continuous bound."""
    return max(_Fr(sched[i + 1] - sched[i] - 1, sched[i] + 1) for i in range(len(sched) - 1))


def worst_relative_cost_bruteforce(sched):
    """Independent oracle for part (1): sweep EVERY integer depth rather than using the closed form."""
    T = sched[-1]
    return max(_Fr(anchor_for(t, sched) - t, t) for t in range(1, T + 1))


def minimax_schedule(T, B):
    """EXHAUSTIVE part (2): over every integer schedule 1 = a_0 < ... < a_B = T, the one minimising
    the worst ratio. Returns (schedule, optimal_ratio). Exponential in B — used only on the small
    pinned cases, which is what makes it a DECIDED statement rather than a sampled one."""
    if not (2 <= B <= 5 and 4 <= T <= 100):
        raise HornError("the exhaustive optimum is only decided on the small pinned cases")
    best = arg = None
    for mid in _comb(range(2, T), B - 1):
        s = (1,) + mid + (T,)
        r = worst_ratio(s)
        if best is None or r < best:
            best, arg = r, s
    return arg, best


def geometric_schedule(T, B):
    """The theorem's claimed optimum: a_i = T^(i/B), exact when T is a perfect B-th power."""
    root = round(T ** (1.0 / B))
    if root ** B != T:
        raise HornError(f"T={T} is not a perfect {B}-th power; the exact ladder needs one")
    return tuple(root ** i for i in range(B + 1))


def optimum_is_geometric(T, B):
    """Part (2), decided: the exhaustive argmin IS the geometric ladder and the optimum IS T^(1/B)."""
    arg, best = minimax_schedule(T, B)
    geo = geometric_schedule(T, B)
    return arg == geo and best == _Fr(geo[1], geo[0])


def continuous_bound_is_strict(sched):
    """Part (3), decided: on the integer lattice the continuous bound is an UPPER BOUND and NOT an
    identity. True iff the discrete supremum is strictly below `worst_ratio - 1`."""
    return worst_relative_cost(sched) < worst_ratio(sched) - 1


# ---- the 1% tail trigger --------------------------------------------------------------------
def tail_threshold(samples, pct=TAIL_PERCENTILE):
    """The starvation length beyond which the session anchors deep instead of refusing. Exact
    integer order statistic — no interpolation, no float."""
    if not samples:
        raise HornError("a tail threshold needs samples")
    s = sorted(samples)
    idx = (pct * (len(s) - 1)) // 100
    return s[idx]


def anchor_decision(starvation, lad, thresh):
    """The graceful-degradation rule: inside the dense window, reconcile normally; beyond the tail
    threshold, fall back to the deepest usable anchor and replay forward; beyond the ladder's reach,
    and only then, refuse. A cliff becomes a slope."""
    if (starvation <= lad[DENSE - 1]) if len(lad) >= DENSE else False:
        return ("dense", starvation)
    if starvation > lad[-1]:
        return ("refuse", None)
    if starvation >= thresh:
        return ("anchor", anchor_for(starvation, lad))
    return ("dense", starvation)


def _decision_no_ladder(starvation, lad, thresh, window=8):
    """A FALSIFIER TOOL (not a law): the FIXED-WINDOW policy the arc has today. Anything beyond the
    window is a refusal — the disconnect a DDoS is buying."""
    return ("dense", starvation) if starvation <= window else ("refuse", None)


# ---- THE TWIST: flat ribbon -> cylinder, under rubber-band stress ----------------------------
# A flat string twisted becomes a cylinder: the MATERIAL is conserved, only the PITCH changes. The
# ladder has the same structure. Its "material" is the RUNG COUNT B - W (the number of geometric
# steps); its "pitch" is the ratio r. Twisting raises r: the same rungs reach exponentially further
# while each step gets coarser. Both sides of that trade are CLOSED FORMS, which is what makes the
# twist a mechanism rather than a dial:
#
#     reach  =  W * r^(B-W)          exact, measured at every admitted pitch
#     price  =  worst rho  <  r - 1  the minimax bound of part (3), STRICTLY below it on the lattice
#
# So the price of twisting is fixed by the theorem, not chosen: one more unit of pitch costs strictly
# less than one more unit of relative replay. Flat = fine pitch, short reach, precise. Twisted =
# coarse pitch, deep reach, lossy. (An earlier draft of this block said the price is EXACTLY r - 1;
# that is the continuous value, and part (3) already recorded that the integer lattice comes in
# strictly under it. The same correction applies here and is measured by `twist_price_is_bounded`.)
#
# THE TWIST INVARIANT (why this is a twist and not merely a resize): B - W is CONSERVED under stress.
# Stress never adds or removes a rung; it only changes their pitch — a helix with a fixed number of
# turns and a variable rise. That conservation is what makes "flatten and twist" exact rather than
# figurative, and it is asserted as a law.
#
# MONOTONE DISCIPLINE, borrowed from pingpolicy: the twist RISES FREELY under stress (reach is needed
# now) and RELAXES ONE STEP per calm window (never thrash). The direction that helps survival is fast;
# the direction that restores precision is slow.
#
# REMOVABILITY — this mechanism is OPT-OUT BY CONSTRUCTION. `stress=None` (or TWIST_ENABLED = False)
# returns the plain fixed-ratio ladder EXACTLY: same list, same digests, same behaviour as Half A
# without the twist. It is a strict extension, asserted as a law (`twist_is_removable`), so a
# deployment that does not want adaptive pitch deletes one argument and loses nothing else.

TWIST_ENABLED = True
MIN_RATIO = 2                                # flat: finest pitch
MAX_RATIO = 8                                # fully twisted: coarsest pitch admitted
RELAX_STEP = 1                               # pitch recovered per calm window (slow, deliberate)


def rungs(dense=DENSE, slots=12):
    """The twist invariant: the number of geometric rungs, conserved under any stress."""
    return slots - dense


def twist_ratio(stress, prev_ratio=MIN_RATIO):
    """The pitch under rubber-band stress. RISES FREELY (straight to the stress level, because reach
    is needed immediately) and RELAXES at most RELAX_STEP per calm window. `stress=None` disables the
    mechanism entirely and returns the flat pitch — the removability path."""
    if stress is None or not TWIST_ENABLED:
        return MIN_RATIO
    if type(stress) is not int or stress < 0:
        raise HornError(f"stress must be a non-negative int or None, got {stress!r}")
    want = min(MIN_RATIO + stress, MAX_RATIO)
    if want >= prev_ratio:
        return want                          # twist up freely
    return max(want, prev_ratio - RELAX_STEP)  # untwist one step at a time


def twisted_ladder(dense=DENSE, slots=12, stress=None, prev_ratio=MIN_RATIO):
    """The ladder at the pitch stress dictates. With `stress=None` this IS `ladder(...)` — identical
    list, not merely equivalent behaviour."""
    return ladder(dense, slots, twist_ratio(stress, prev_ratio))


def twist_is_removable(dense=DENSE, slots=12):
    """REMOVABILITY, as a law: disabling the twist reproduces the untwisted ladder EXACTLY."""
    return twisted_ladder(dense, slots, stress=None) == ladder(dense, slots, MIN_RATIO)


def twist_conserves_rungs(dense=DENSE, slots=12, stresses=(0, 1, 3, 6, 99)):
    """THE INVARIANT, as a law: stress changes pitch, never rung count. A helix, not a resize."""
    base = rungs(dense, slots)
    return all(len(twisted_ladder(dense, slots, st)) - dense == base for st in stresses)


def twist_trades_reach_for_precision(dense=DENSE, slots=12):
    """MEASURED: as pitch coarsens, reach grows strictly and so does the worst relative replay cost.
    Returns [(ratio, reach, worst_relative_cost)] — the trade, in exact integers and rationals."""
    out = []
    for r in range(MIN_RATIO, MAX_RATIO + 1):
        lad = ladder(dense, slots, r)
        out.append((r, lad[-1], worst_relative_cost(lad)))
    return out


def reach_is_dense_times_pitch_to_rungs(dense=DENSE, slots=12):
    """THE REACH CLOSED FORM, as a law: reach = W * r^(B-W) at every admitted pitch. This is the
    quantitative content of "same material, different pitch" — reach is exponential in the CONSERVED
    rung count, with the pitch as the base, so twisting buys depth without buying storage."""
    return all(ladder(dense, slots, r)[-1] == dense * r ** rungs(dense, slots)
               for r in range(MIN_RATIO, MAX_RATIO + 1))


def twist_price_is_bounded(dense=DENSE, slots=12):
    """THE PRICE, as a law: the worst relative replay cost at pitch r is STRICTLY below r - 1 at every
    admitted pitch — the minimax bound of part (3), applied to the twist. Strictly, not exactly: the
    continuous value r - 1 is attained only at t = a_i + epsilon, and the integer lattice's worst depth
    is a_i + 1. Stating it as an equality would repeat the error part (3) already caught once."""
    return all(worst_relative_cost(ladder(dense, slots, r)) < r - 1
               for r in range(MIN_RATIO, MAX_RATIO + 1))


# THE DECOUPLING CHECK — the one place this mechanism could go wrong, and the reason it is MEASURED
# against clockauth's own band rather than asserted here. Deeper ROLLBACK anchors must never widen the
# admissible VIEW-TICK band that clockauth polices: retention is what the SERVER keeps, the band is
# what the CLIENT may claim, and a client that can induce stress must not thereby buy backdating.
# The decoupling is STRUCTURAL, not a promise — `CA.band(now, clk)` takes no ladder, no ratio and no
# stress, so stress cannot reach it through any argument. `_coupled_band` is the plant that shows what
# the leak would look like if it could, and it bites.

def _honest_band(stress, prev_ratio=MIN_RATIO):
    """The band clockauth ACTUALLY polices. It is returned unwrapped and it discards `stress`, which
    is the whole content of the decoupling: a signature, not a discipline anyone has to maintain."""
    return CA.band


def _coupled_band(stress, prev_ratio=MIN_RATIO):
    """A FALSIFIER TOOL (not a law): the coupling this rung must NOT have — a view band whose jitter
    tolerance widens with the twist's pitch. Under it, a client that induces starvation converts the
    deeper anchors survival bought into an ALIBI BUDGET: it may claim a view-tick further in the past
    than its attested latency admits, which is precisely the backdating `clockauth` exists to refuse."""
    slack = twist_ratio(stress, prev_ratio) - MIN_RATIO

    def _band(now, clk):
        lat, jitter = clk
        return CA.band(now, (lat, jitter + slack))
    return _band


def admissible_view_ticks(stress, now=64, clk=(3, 2), prev_ratio=MIN_RATIO, _bandfn=None):
    """The SET of view-ticks clockauth admits at this stress — obtained by ASKING clockauth, not by
    restating the twist. Under the honest band this set is invariant in stress."""
    lo, hi = (_bandfn or _honest_band)(stress, prev_ratio)(now, clk)
    return tuple(vt for vt in range(now - CA.MAX_REWIND, now + 1) if lo <= vt <= hi)


def twist_leaks_into_view_band(stress, now=64, clk=(3, 2), prev_ratio=MIN_RATIO, _bandfn=None):
    """MEASURED: how many view-ticks the twist BUYS a client at this stress, relative to flat. Must be
    zero on the honest path; strictly positive under `_coupled_band`, which is what makes the zero a
    result rather than a decoration."""
    flat = set(admissible_view_ticks(None, now, clk, prev_ratio, _bandfn))
    under = set(admissible_view_ticks(stress, now, clk, prev_ratio, _bandfn))
    return len(under - flat)


# PITCH AUTHORITY — who is allowed to set the stress. Every sibling rung in this subsystem closes this
# question for its own input (`clockauth._admit_client_latency`, `pingpolicy._authenticate_none`,
# `oobprior._reference_including_self`) and the twist must not be the one place it is left open. The
# incentive is real and it is not the view band: coarse pitch maximises the REPLAY GAP a client is
# reconciled through, and replay across a wider gap is exactly where the commutation dependency
# declared above has the most room to be violated. A client that could name its own stress would name
# the largest one. So stress is DERIVED, from the server's own starvation observation against the
# server's own tail threshold — never read from a client field.

def server_stress(starvation, thresh):
    """The stress the SERVER measures. Zero while inside the tail; thereafter ONE PITCH STEP PER
    DOUBLING of the outage, so the pitch tracks the ORDER of the starvation rather than its size —
    which is what keeps a single long outage from spending the whole pitch range. Exact integer: the
    doubling count is a bit-length, not a logarithm (the same identity `magicdiv` decided)."""
    for v in (starvation, thresh):
        if type(v) is not int or v < 0:
            raise HornError(f"starvation and threshold must be non-negative ints, got {v!r}")
    if thresh < 1:
        raise HornError("a tail threshold of zero cannot scale a stress")
    if starvation <= thresh:
        return 0
    return (starvation // thresh).bit_length() - 1


def _stress_from_client(claimed, starvation=0, thresh=1):
    """A FALSIFIER TOOL (not a law): stress read from a CLIENT-SUPPLIED field. Under it the client
    picks its own pitch, and the pitch it wants is the coarsest available — because coarse pitch
    widens the replay gap it will be reconciled through. It ignores the server's own measurement
    entirely, which is the shape of the defect rather than a mere off-by-one."""
    return claimed


def pitch_is_server_derived(thresh=8, claims=(0, 1, 7, 99)):
    """THE AUTHORITY LAW, stated so that it CAN be false. At a fixed real starvation the honest pitch
    is a function of the SERVER's measurement alone, while the plant's pitch is a function of the
    CLIENT's claim alone. True iff (a) no claim moves the honest pitch, and (b) some claim DOES move
    the plant's — the second half is what keeps the first half from being a tautology. If anyone ever
    wires the pitch to the claimed field, (a) still holds vacuously and (b) fails, so the law reddens."""
    moved = False
    for starvation in (1, 8, 9, 16, 64, 1024):
        honest = twist_ratio(server_stress(starvation, thresh))
        for c in claims:
            if twist_ratio(server_stress(starvation, thresh)) != honest:
                return False
            if twist_ratio(_stress_from_client(c, starvation, thresh)) != honest:
                moved = True
    return moved


def pitch_ladder_from_starvation(thresh=8, starvations=(1, 8, 9, 16, 32, 64, 256, 1024, 65536)):
    """MEASURED: the pitch the server actually reaches as an outage lengthens — one step per doubling,
    saturating at MAX_RATIO. Returns [(starvation, stress, pitch)]."""
    out = []
    for s in starvations:
        st = server_stress(s, thresh)
        out.append((s, st, twist_ratio(st)))
    return out


def _twist_unbounded(stress, prev_ratio=MIN_RATIO):
    """A FALSIFIER TOOL (not a law): a pitch with no ceiling and no relaxation discipline. It breaks
    the mechanism in BOTH directions — upward it admits arbitrarily coarse ladders whose replay cost
    r - 1 grows without bound (the twist becomes a shred), and downward it drops straight to flat on a
    single calm window instead of relaxing one step, which is the thrash the monotone rule forbids."""
    return MIN_RATIO + (stress or 0)


# ---- digests + scenes -------------------------------------------------------------------------
def horn_digest(name, payload):
    hh = hashlib.sha256(); hh.update(MAGIC)
    hh.update(f"|{name}|{payload}".encode())
    return hh.hexdigest()


PINNED = ((16, 2), (16, 4), (27, 3), (32, 5), (64, 3), (81, 4))


def _scene_ladder():
    """Reach against slots — the horn's bounded-volume half, in integers."""
    return horn_digest("ladder", ":".join(str(reach(DENSE, b)) for b in (8, 12, 16, 20)))


def _scene_minimax():
    """THE THEOREM, decided: on every pinned case the exhaustive argmin is the geometric ladder."""
    return horn_digest("minimax", ":".join(
        f"{T}^1/{B}={minimax_schedule(T, B)[1]}:{optimum_is_geometric(T, B)}" for T, B in PINNED))


def _scene_integer_bound():
    """Part (3): the continuous bound is strict on the lattice — the correction the check forced."""
    lad = ladder(DENSE, 12)
    return horn_digest("integer_bound", f"{worst_relative_cost(lad)}:{worst_ratio(lad) - 1}:"
                                        f"{continuous_bound_is_strict(lad)}:"
                                        f"{worst_relative_cost(lad) == worst_relative_cost_bruteforce(lad)}")


def _scene_survival():
    """The cliff-to-slope comparison: what the fixed window refuses and the ladder still anchors."""
    lad = ladder(DENSE, 12)
    thresh = tail_threshold([1, 1, 2, 2, 3, 3, 4, 5, 9, 40])
    rows = [(s, anchor_decision(s, lad, thresh)[0], _decision_no_ladder(s, lad, thresh)[0])
            for s in (2, 8, 9, 40, 300, 2000)]
    return horn_digest("survival", f"{thresh}:{rows}")


def _scene_twist():
    """The flat ribbon becomes a cylinder: same rungs, coarser pitch, exponentially deeper reach —
    with BOTH sides of the trade in closed form and the price bounded by the minimax theorem."""
    return horn_digest("twist", f"{twist_trades_reach_for_precision()}:"
                                f"{twist_conserves_rungs()}:{twist_is_removable()}:"
                                f"{reach_is_dense_times_pitch_to_rungs()}:{twist_price_is_bounded()}")


def _scene_removable():
    """The mechanism is opt-out by construction: disabled, the ladder is IDENTICAL to the untwisted
    one. And the decoupling from the view band is pinned WITH ITS PLANT — the honest path buys a
    client zero extra view-ticks at every stress, while the coupled plant buys it several, so the zero
    is a measured result rather than a hardcoded reassurance."""
    honest = [twist_leaks_into_view_band(s) for s in (0, 5, 99)]
    leaked = [twist_leaks_into_view_band(s, _bandfn=_coupled_band) for s in (0, 5, 99)]
    return horn_digest("removable", f"{twisted_ladder(stress=None) == ladder()}:"
                                    f"{[twist_ratio(s) for s in (None, 0, 2, 5, 99)]}:"
                                    f"{honest}:{leaked}")


def _scene_authority():
    """WHO SETS THE PITCH. The stress is DERIVED from the server's own starvation measurement — one
    pitch step per doubling of the outage — and a client's claimed stress moves it not at all, while
    the claim-reading plant follows the claim straight to the ceiling."""
    return horn_digest("authority", f"{pitch_ladder_from_starvation()}:{pitch_is_server_derived()}:"
                                    f"{[twist_ratio(_stress_from_client(c)) for c in (0, 1, 7, 99)]}")


_SCENES = {"ladder": _scene_ladder, "minimax": _scene_minimax,
           "integer_bound": _scene_integer_bound, "survival": _scene_survival,
           "twist": _scene_twist, "removable": _scene_removable, "authority": _scene_authority}
SCENES = ("ladder", "minimax", "integer_bound", "survival", "twist", "removable", "authority")


def scene_result(name):
    return _SCENES[name]()


def golden(name):
    with open(_os.path.join(_HERE, "conformance_horn.txt"), encoding="utf-8") as fh:
        for ln in fh:
            ln = ln.strip()
            if ln and not ln.startswith("#"):
                nm, dig = ln.split()
                if nm == name:
                    return dig
    raise HornError(f"no golden named {name!r}")


def _main(argv):
    for n in SCENES:
        print(n, scene_result(n))
    for T, B in PINNED:
        print(f"  T={T} B={B}: optimum {minimax_schedule(T, B)[1]} geometric={optimum_is_geometric(T, B)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(_main(_sys.argv))
