# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""slo — the composite worst-case latency SLO (T3.33, MMO Stage H, URDRLAT2): the end-to-end latency guarantee
as ONE certified number, with a refuse when a config cannot meet its target. This is where the Stage-H arc
closes: `opcost` measured the work, `govern`/`priogov` enforced a per-tick budget, `horizon` bounded the
rollback window — `slo` composes them into a single worst-case latency and a `SLO-REFUSE` for a config that
would over-promise.

THE COMPOSITE. An actor's end-to-end latency, in ticks, has two bounded parts:
  * ADMISSION WAIT — from the work governor: under a per-tick op-budget B and per-actor cost c, each tick
    admits floor(B / c) actors, so N actors drain in ceil(N / floor(B / c)) ticks and no actor waits longer.
  * RECONCILE WINDOW — from the rollback horizon H: a client correction rolls back at most H boundaries.
`worst_case_latency = admission_wait + H`. This is an UPPER BOUND, and it is SOUND: the gate checks that the
governor's ACTUAL maximum drain-wait never exceeds the admission_wait formula, so the number is a real
guarantee, not an optimistic estimate.

THE REFUSE. `slo_admit(config, target_L)` ADMITS iff `worst_case_latency <= target_L`, else `SLO-REFUSE` — a
config that cannot meet the latency target is refused, never quietly accepted (a promise is kept or declined,
never broken). Reduce N, raise the budget, or shrink the horizon until it fits.

GRADE. The admission-wait formula, its SOUNDNESS against the governor's actual drain (the formula is a true
upper bound), the composite worst-case number, the `SLO-REFUSE` at the target, and determinism are MEASURED
(exact, reproducible, a defect diverges). `does_not_show`: WALL-CLOCK latency (this is in TICKS; wall-clock per
tick is `bench.py`, MEASURED-on-named-host — multiply to get seconds); jitter / variance (this is the
WORST-CASE bound, not a distribution); priority-class latency (uses the FIFO governor's uniform bound, not
`priogov`'s per-class one — a follow-on); and any guarantee under an adversarial OS scheduler."""
import hashlib
import os as _os
import sys as _sys

MAGIC = b"URDRLAT2"
_HERE = _os.path.dirname(_os.path.abspath(__file__))
if _HERE not in _sys.path:
    _sys.path.insert(0, _HERE)
import govern as _GV                                            # the FIFO governor (actual drain, for soundness)
import horizon as _HZ                                           # the rollback window
import opcost as _OC                                            # OPCOST-REFUSE (shared refuse family)


class SloError(Exception):
    def __init__(self, message):
        super().__init__(f"SLO-REFUSE: {message}")
        self.code = "SLO-REFUSE"


def admission_wait(n, budget, actor_cost):
    """The worst-case admission wait in TICKS for N equal-cost actors under a per-tick op-budget: each tick
    admits floor(budget / actor_cost) actors, so the queue drains in ceil(N / per_tick). An `OPCOST-REFUSE`
    if a single actor cannot fit the budget."""
    if not (type(n) is int and n >= 0 and type(budget) is int and type(actor_cost) is int and actor_cost > 0):
        raise SloError(f"bad config: n={n!r} budget={budget!r} actor_cost={actor_cost!r}")
    if actor_cost > budget:
        raise _OC.OpcostError(f"actor cost {actor_cost} > budget {budget} — cannot fit any tick")
    if n == 0:
        return 0
    per_tick = budget // actor_cost
    return -(-n // per_tick)                                     # ceil division, integer-exact


def worst_case_latency(n, budget, actor_cost, horizon):
    """The composite worst-case end-to-end latency in ticks: admission wait (governor) + reconcile window
    (rollback horizon). One certified number."""
    return admission_wait(n, budget, actor_cost) + _HZ.worst_case_window(horizon)


def slo_admit(n, budget, actor_cost, horizon, target_ticks):
    """ADMIT a config iff its worst-case latency <= `target_ticks`, returning that latency; else `SLO-REFUSE`
    — the config cannot promise the target and is declined rather than allowed to over-promise."""
    w = worst_case_latency(n, budget, actor_cost, horizon)
    if w > target_ticks:
        raise SloError(f"worst-case latency {w} ticks exceeds target {target_ticks}")
    return w


def slo_digest(name, n, budget, actor_cost, horizon, latency, verdict):
    """URDRLAT2 canon — SHA-256(MAGIC | name | n | budget | actor_cost | horizon | latency | verdict). Binds
    the whole config and its verdict, so any change to the guarantee moves it."""
    hh = hashlib.sha256()
    hh.update(MAGIC)
    hh.update(f"|{name}|n:{n}|b:{budget}|c:{actor_cost}|h:{horizon}|w:{latency}|v:{verdict}".encode())
    return hh.hexdigest()


# ---- scenarios (pinned by the gate) -----------------------------------------------------
_MS, _SUB = 40, 4
_CMDS = "eeee"


def _flat16():
    return tuple(tuple(0 for _x in range(16)) for _y in range(16))


def _actor_cost():
    return _GV.actor_cost(_flat16(), (2, 8), _CMDS, _MS, _SUB)


# config: N actors, budget = k * actor_cost, horizon H, target L (ticks)
_SCENES = {
    # (n, budget_mult, horizon, target) -> worst-case = ceil(n/budget_mult) + horizon
    "meets": (6, 3, 2, 5),        # admission ceil(6/3)=2 + H2 = 4 <= target 5 -> ADMIT
    "tight": (6, 2, 4, 7),        # ceil(6/2)=3 + H4 = 7 <= target 7 -> ADMIT (exactly at the target)
    "fails": (12, 2, 5, 8),       # ceil(12/2)=6 + H5 = 11 > target 8 -> SLO-REFUSE
}
SCENES = ("meets", "tight", "fails")


def scene_case(name):
    """(latency, verdict) for a named config."""
    n, bmult, hz, target = _SCENES[name]
    c = _actor_cost()
    budget = bmult * c
    lat = worst_case_latency(n, budget, c, hz)
    try:
        slo_admit(n, budget, c, hz, target)
        verdict = "ADMIT"
    except SloError:
        verdict = "SLO-REFUSE"
    return lat, verdict


def scene_result(name):
    n, bmult, hz, target = _SCENES[name]
    c = _actor_cost()
    lat, verdict = scene_case(name)
    return slo_digest(name, n, bmult * c, c, hz, lat, verdict)


def golden(name):
    with open(_os.path.join(_HERE, "conformance_slo.txt"), encoding="utf-8") as fh:
        for ln in fh:
            ln = ln.strip()
            if ln and not ln.startswith("#"):
                nm, dig = ln.split()
                if nm == name:
                    return dig
    raise SloError(f"no golden named {name!r}")
