# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""urdr-criticality — a deterministic branching-diffusion (reactor-kinetics) field.

A population field on a 1D lattice, evolved on the FROZEN Q32.32 backend (`field.FixedPoint`),
in the urdr-field family (advection-diffusion / Marangoni / loop). Three coupled pieces, the
reactor-physics reading of "keff = 2.0 × Galton board + Doppler":

  * TRANSPORT (the Galton board). The binomial left/right peg step IS a discrete diffusion
    kernel. Implemented in EXACT-CONSERVATIVE FLUX FORM (D = 1/4): per interior edge,
    `f = 1/4·(n[i] − n[i+1])`, then `n[i] -= f; n[i+1] += f`. What leaves one cell enters its
    neighbour, so total population is conserved EXACTLY regardless of rounding (the urdr-field
    "flux form: mass conserved exactly" discipline). Vacuum boundaries LEAK (1/4 of the edge
    cell escapes) — leakage is part of criticality; reflecting boundaries conserve.

  * MULTIPLICATION (keff). Each generation multiplies the population by the effective
    multiplication factor `keff` (a rational). `keff > 1` is SUPERCRITICAL — it grows
    geometrically, and under the bounded substrate it RAISES `FIELD-REFUSE` at the i64 ceiling
    rather than wrapping. `keff = 1` is critical (stationary); `keff < 1` is subcritical (decays).

  * DOPPLER (the regulator). The reactor negative-temperature feedback: as local density
    ("temperature") rises, effective keff falls. Here `k_eff(cell) = k0 · n_ref/(n_ref + n)` —
    a rational feedback (EXACT), driving `k_eff → 1` as `n` rises, so a supercritical `k0`
    self-limits to a BOUNDED steady state `n* = (k0 − 1)·n_ref` per cell. This is why
    `keff = 2.0` does not explode when Doppler is on: the feedback IS the stability.

THE CLOSED FORM IS NOW CODE, AND UNTIL IT WAS, A DIGEST WAS STANDING IN FOR A LAW. `n* =
(k0 − 1)·n_ref` is what `k_eff(cell) = 1` solves to, and this file asserted it in the paragraph
above while the gate pinned a TRACE DIGEST of one supercritical scene. A digest is an IDENTITY: it
reproduces whatever the operator does and would reproduce a rest point that was the wrong number
for a right-looking reason. A law has a SHAPE — linear in `n_ref`, linear in `k0 − 1`, exact at
fractional `k0` — and one scene is one point on it, so the closed form is read across a PANEL of
five parameter pairs (`panel != scalar`). MEASURED: every member lands on the rational rest point
TO THE LAST BIT OF THE SUBSTRATE, three exactly and two one ulp low, never high, because `mul_k`
truncates — and the deficit is a FIXED POINT of the rounded operator rather than an unfinished
convergence, identical at 100 generations and at 800.

TWO THINGS FELL OUT OF WRITING IT DOWN.

  * DOPPLER MOVES THE CRITICAL POINT. `k0 = 1` is critical for the BARE multiplication operator —
    stationary, exactly. Through the regulator, `n* = (k0 − 1)·n_ref` is ZERO: `k_eff` is strictly
    under one at every positive density, so the field decays every generation and approaches zero
    without arriving. CRITICALITY REQUIRES `k0 > 1` ONCE DOPPLER IS ON. The prose above is SILENT
    on this rather than wrong — it gives the eigenvalue behaviour under `multiply` and the
    self-limiting behaviour under `doppler`, and never puts `k0 = 1` through the regulator.

  * THE EXCURSION IS DOWNWARD. The shipped scene seeds 1000 into one cell against `n_ref = 50`, so
    the feedback opens at roughly a tenth and the population CRASHES to under a third of its start
    by generation 2, turns exactly ONCE, and climbs to the rest point without ever passing it.
    There is no overshoot to bound: the maximum over the run IS the rest point.

Honest scope: 1D, one-group, a RATIONAL Doppler law (the physical Doppler defect ∝ √T is
irrational and would itself live in the bounded/refuse regime — DECLARED, not modelled here).
GRADE (D5): MEASURED (reference), bounded regime B (rounds honestly, refuses on overflow, never
wraps), deterministic; cross-placement DECLARED; NOT frozen. The witnessed properties: exact
transport conservation, the eigenvalue behaviour (k=1 stationary / k<1 decays / k>1 refuses),
the Galton distribution golden, the Doppler-regulated steady-state golden, and the closed-form
panel — with the non-vacuity defect that removing Doppler makes the supercritical field explode
(FIELD-REFUSE), and the second one this rung adds: a regulator with the feedback density scaled by
two is still bounded, still steady and still never refuses, and rests on half the right number.

`does_not_show`: NOT that the Doppler law is PHYSICAL — it is the rational stand-in named above,
and a closed form reproduced to the last bit is a statement about this operator, never about a
reactor. NOT that the panel is the whole shape: five pairs read linearity in both arguments and one
fractional `k0`, and a law that departed from the closed form only outside their span is invisible
here. NOT that one ulp is a bound anyone derived — it is MEASURED over these five, and a member
whose deficit were two would be a finding rather than a failure of the substrate."""
import hashlib
import os as _os

from field import FixedPoint as FP, FieldError            # noqa: E402  frozen Q32.32 + FIELD-REFUSE

MAGIC = b"URDRKFF1"          # per-generation population-field digest
TRACE_MAGIC = b"URDRKFFT"    # whole-run trace digest
_HERE = _os.path.dirname(_os.path.abspath(__file__))


def _ser(a):
    return int(a).to_bytes(8, "big", signed=True)


def state_digest(n, gen):
    """SHA-256(MAGIC | W u32 BE | generation u32 BE | each cell as signed i64 BE)."""
    out = bytearray(MAGIC)
    out += len(n).to_bytes(4, "big")
    out += int(gen).to_bytes(4, "big")
    for x in n:
        out += _ser(x)
    return hashlib.sha256(bytes(out)).hexdigest()


def trace_digest(digests):
    """The whole-run witness = SHA-256 over the ordered per-generation digests."""
    h = hashlib.sha256()
    h.update(TRACE_MAGIC)
    for d in digests:
        h.update(d.encode())
    return h.hexdigest()


def total(n):
    """Exact total population (a running FixedPoint sum — the conserved quantity of transport)."""
    t = 0
    for x in n:
        t = FP.add(t, x)
    return t


# ---- the three coupled operators ----------------------------------------------------
def transport(n, reflect=False):
    """Exact-conservative Galton/diffusion step (flux form, D=1/4). Vacuum boundaries leak."""
    w = len(n)
    out = list(n)
    for i in range(w - 1):
        f = FP.mul_k(FP.sub(out[i], out[i + 1]), 1, 4)
        out[i] = FP.sub(out[i], f)
        out[i + 1] = FP.add(out[i + 1], f)
    if not reflect:
        out[0] = FP.sub(out[0], FP.mul_k(out[0], 1, 4))
        out[w - 1] = FP.sub(out[w - 1], FP.mul_k(out[w - 1], 1, 4))
    return out


def multiply(n, kn, kd):
    """Uniform multiplication by keff = kn/kd (production). Supercritical (>1) refuses at the bound."""
    return [FP.mul_k(x, kn, kd) for x in n]


def doppler(n, k0n, k0d, nref):
    """Doppler-regulated production: k_eff(cell) = (k0n/k0d)·nref/(nref + n), driving k_eff→1
    as density rises. `nref` is a Q32.32 word (the reference density)."""
    return [FP.mul_k(x, k0n * nref, k0d * (nref + x)) for x in n]


def step(n, k0n, k0d, reflect=False, doppler_on=False, nref=None):
    """One generation: transport, then production (Doppler-regulated or plain keff)."""
    n = transport(n, reflect)
    return doppler(n, k0n, k0d, nref) if doppler_on else multiply(n, k0n, k0d)


# ---- scenarios (pinned by the gate) -------------------------------------------------
def seed_field(w, value=1000, center=None):
    """A point source: `value` at the centre cell, zero elsewhere (the incident 'beam')."""
    n = [0] * w
    n[center if center is not None else w // 2] = FP.unit(value, 1)
    return n


def simulate(w, gens, k0n, k0d, reflect=False, doppler_on=False, nref=None, value=1000):
    """Run `gens` generations from a centred point source. Returns (states, digests) —
    `states` the per-generation population lists (display-only), `digests` the per-generation
    URDRKFF1 witnesses. Raises `FieldError('FIELD-REFUSE', …)` if the bounded substrate
    overflows (a supercritical excursion with no regulator)."""
    n = seed_field(w, value)
    states = [list(n)]
    digests = [state_digest(n, 0)]
    for g in range(1, gens + 1):
        n = step(n, k0n, k0d, reflect, doppler_on, nref)
        states.append(list(n))
        digests.append(state_digest(n, g))
    return states, digests


def galton_scene():
    """Pure transport (keff = 1) from a point source with vacuum leakage — the deterministic
    Galton board: an incident spike diffuses to the binomial spread, reproducibly."""
    return dict(w=21, gens=12, k0n=1, k0d=1, reflect=False, doppler_on=False, nref=None)


def regulated_scene():
    """Supercritical k0 = 2.0 with Doppler feedback (reflecting) — the self-limiting critical
    state: population converges to the bounded steady total and holds."""
    return dict(w=21, gens=120, k0n=2, k0d=1, reflect=True, doppler_on=True, nref=FP.unit(50, 1))


def unregulated_scene():
    """The DEFECT for the gate: the same supercritical k0 = 2.0 with NO Doppler — it explodes
    and RAISES FIELD-REFUSE at the i64 ceiling (Doppler is load-bearing)."""
    return dict(w=21, gens=120, k0n=2, k0d=1, reflect=True, doppler_on=False, nref=None)


def run_trace(scene):
    """The trace digest of a scenario dict (raises FieldError if the scene refuses)."""
    _states, digests = simulate(**scene)
    return trace_digest(digests)


# ---- the closed form, as CODE ---------------------------------------------------------
#: THE DOPPLER LAW IMPLIES A NUMBER AND THAT NUMBER LIVED ONLY IN A DOCSTRING. Setting
#: `k_eff(cell) = k0·nref/(nref + n) = 1` and solving gives `n = (k0 − 1)·nref` — the density at
#: which the feedback is exactly critical, so it is the density the field must come to rest at.
#: The module said so in prose and pinned a TRACE DIGEST of one supercritical scene. A digest is an
#: IDENTITY: it reproduces whatever the operator does, and would reproduce just as happily if the
#: rest point were the wrong number for the right-looking reason. What it cannot do is READ THE LAW,
#: because a law has a SHAPE — linear in `nref`, linear in `k0 − 1`, exact at fractional `k0` — and
#: one scene is one point on it. `panel != scalar`, applied to a closed form.
STEADY_PANEL = ((2, 1, 50), (2, 1, 100), (3, 1, 50), (3, 2, 50), (5, 1, 20))

#: Generations allowed for the panel runs. 200 is not a tuned number: the shipped 120-generation
#: scene is at its rest point by generation 51 and the slowest panel member settles well inside
#: this, so the bound is slack rather than fitted.
STEADY_GENS = 200


def steady_state(k0n, k0d, nref):
    """n* = (k0 − 1)·nref per cell — the closed form, DERIVED from the shipped `doppler` operator
    rather than restated from its docstring. `nref` is a Q32.32 word; the result is one too."""
    return FP.mul_k(nref, k0n - k0d, k0d)


#: THE DEFICIT IS ONE BIT AND ITS SIGN IS NOT FREE. `FP.mul_k` truncates, so the rounded operator's
#: fixed point sits AT the exact rational rest point or exactly ONE ULP BELOW it, never above. The
#: bound is a MEASUREMENT of the substrate, not a tolerance chosen to make a test pass: the wrong
#: regulator this rung plants misses by 107374182400 ulps, eleven orders of magnitude outside it.
DEFICIT_FLOOR = -1        # ulps — the last representable bit of Q32.32
DEFICIT_CEIL = 0          # ulps — never above the exact rational rest point


def steady_reading(k0n, k0d, nrefv, w=21, gens=STEADY_GENS, value=1000):
    """Run the regulated field to rest and report (measured centre cell, predicted, deficit in ulps).

    The CENTRE cell is read rather than the total because the closed form is a PER-CELL statement
    and a total would fold the cell count in with it — a reading that agreed for the wrong reason
    if `w` ever changed."""
    nref = FP.unit(nrefv, 1)
    states, _d = simulate(w=w, gens=gens, k0n=k0n, k0d=k0d, reflect=True,
                          doppler_on=True, nref=nref, value=value)
    got = states[-1][w // 2]
    want = steady_state(k0n, k0d, nref)
    return got, want, int(got) - int(want)


def the_steady_state_matches_the_closed_form():
    """FIVE PARAMETER PAIRS, NOT ONE SCENE. Doubling `nref` doubles the rest point; raising `k0`
    from 2 to 3 doubles it; a fractional `k0` lands on a fractional multiple of `nref`. Each is
    reproduced TO THE LAST BIT OF THE SUBSTRATE — three of the five exactly, two one ulp low, none
    high. Returns a row per member: (k0n, k0d, nref, deficit_in_ulps, within_the_bound)."""
    out = []
    for a, b, c in STEADY_PANEL:
        _g, _w, d = steady_reading(a, b, c)
        out.append((a, b, c, d, DEFICIT_FLOOR <= d <= DEFICIT_CEIL))
    return tuple(out)


def the_rest_point_is_a_fixed_point_of_the_ROUNDED_operator():
    """A DEFICIT THAT SHRANK WITH GENERATIONS WOULD BE A CONVERGENCE RATE, NOT A REST POINT, and
    the difference decides whether the bound above means anything. Run the same member four run
    lengths apart: the deficit is the SAME value at 100 generations and at 800, so the rounded
    operator has an exact fixed point one ulp under the rational one rather than creeping toward
    it. Returns (deficits_by_run_length, all_equal)."""
    ds = tuple(steady_reading(2, 1, 50, gens=g)[2] for g in (100, 200, 400, 800))
    return ds, len(set(ds)) == 1


def panel_digest():
    """The panel's own witness — the measured rest points and their ulp deficits, in panel order,
    content-addressed like every other claim in this tree so the READING is pinned and not only the
    assertion that it passed."""
    h = hashlib.sha256()
    h.update(MAGIC + b"|steady|")
    for a, b, c in STEADY_PANEL:
        got, want, d = steady_reading(a, b, c)
        h.update(("%d/%d@%d=%d:%d:%d;" % (a, b, c, int(got), int(want), d)).encode())
    return h.hexdigest()


def doppler_moves_the_critical_point(gens=STEADY_GENS, w=21, nrefv=50):
    """THE FINDING, AND IT FALLS OUT OF THE CLOSED FORM RATHER THAN OUT OF A NEW IDEA.

    `k0 = 1` is the critical point of the BARE multiplication operator: population stationary,
    exactly. Put the regulator in front of it and `n* = (k0 − 1)·nref` is ZERO — `k_eff` is
    strictly below one at every positive density, so the field decays at every generation and
    approaches zero without reaching it. CRITICALITY REQUIRES `k0 > 1` ONCE DOPPLER IS ON.

    The module's prose is SILENT here rather than wrong: it states the eigenvalue behaviour under
    `multiply` and the self-limiting behaviour under `doppler`, and never puts `k0 = 1` through the
    regulator. A trace digest of one supercritical scene cannot see the question.

    Returns (bare_is_stationary, regulated_strictly_decays, regulated_end, predicted_rest_point).
    """
    bare, _d = simulate(w=w, gens=40, k0n=1, k0d=1, reflect=True)
    bare_stationary = total(bare[-1]) == total(bare[0])
    reg, _d2 = simulate(w=w, gens=gens, k0n=1, k0d=1, reflect=True,
                        doppler_on=True, nref=FP.unit(nrefv, 1))
    tots = [total(s) for s in reg]
    decays = all(tots[i] > tots[i + 1] for i in range(len(tots) - 1))
    return bare_stationary, decays, tots[-1], steady_state(1, 1, FP.unit(nrefv, 1))


def the_approach_has_one_turning_point(scene=None):
    """THE EXCURSION IS DOWNWARD, WHICH IS THE OPPOSITE OF WHAT THE NAME 'REGULATOR' SUGGESTS.

    The shipped scene seeds 1000 into ONE cell against `nref = 50`, so the feedback meets a density
    twenty times its reference and `k_eff` opens at roughly a tenth: the population CRASHES before
    it grows. The total falls to under a third of its start by generation 2, turns exactly once, and
    rises to the rest point without ever exceeding it.

    That is why this rung carries no bound on a PEAK. There is no peak — measured, not assumed: the
    maximum over the whole run is the rest point itself, attained at the end and never passed.

    Returns (turning_points, trough_generation, trough, start, maximum, maximum_is_the_rest_point).
    """
    states, _d = simulate(**(scene or regulated_scene()))
    tots = [total(s) for s in states]
    turns = tuple(i for i in range(1, len(tots) - 1)
                  if (tots[i] - tots[i - 1]) * (tots[i + 1] - tots[i]) < 0)
    lo = min(tots)
    return (turns, tots.index(lo), lo, tots[0], max(tots), max(tots) == tots[-1])


def a_stronger_regulator_is_bounded_steady_AND_WRONG(damp=2, gens=STEADY_GENS, w=21,
                                                     k0n=2, k0d=1, nrefv=50):
    """THE PLANT THAT HAS TO BITE, AND IT IS BUILT FROM THE PROPERTIES THIS GATE ALREADY CHECKED.

    Scale the feedback density by `damp`: `k_eff = k0·nref/(nref + damp·n)`. It is still a negative
    feedback, still drives `k_eff` below one as density rises, still self-limits, still never
    reaches the substrate ceiling — so it is BOUNDED, it is STEADY, and it does NOT refuse. Every
    property the gate held before this rung is satisfied by a regulator whose rest point is wrong
    by a factor of `damp`.

    It is deliberately NOT reachable through `step`: a knob on the shipped operator would make the
    defect a supported mode. The plant runs the module's own `transport` under a local production
    rule, which is the smallest change that can express the defect.

    Returns (bounded, steady, never_refused, miss_in_ulps_against_the_shipped_closed_form).
    """
    nref = FP.unit(nrefv, 1)
    n = seed_field(w, 1000)
    tots, refused = [total(n)], False
    try:
        for _g in range(gens):
            n = transport(n, True)
            n = [FP.mul_k(x, k0n * nref, k0d * (nref + damp * x)) for x in n]
            tots.append(total(n))
    except FieldError:
        refused = True
    if refused:
        return False, False, False, None
    steady = len(set(tots[-6:])) == 1
    bounded = max(tots) <= FP.unit(1000 * w, 1)
    miss = int(n[w // 2]) - int(steady_state(k0n, k0d, nref))
    return bounded, steady, True, miss


def golden(name):
    path = _os.path.join(_HERE, "conformance_criticality.txt")
    with open(path, encoding="utf-8") as fh:
        for ln in fh:
            ln = ln.strip()
            if ln and not ln.startswith("#"):
                nm, dig = ln.split()
                if nm == name:
                    return dig
    raise FieldError("FIELD-REFUSE", f"no golden named {name!r}")
