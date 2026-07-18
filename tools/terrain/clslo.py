# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""clslo — the per-CLASS worst-case latency SLO (T3.34, MMO Stage H, URDRLAT3): the priority-class follow-on the
composite `slo` named in its own does_not_show. `slo` stated ONE worst-case latency for the whole population — a
uniform promise ("everyone gets the same bound"). `clslo` refines it into a PER-CLASS promise ("premium gets X,
standard gets Y, free gets Z") and makes each tier's number accountable, so `priogov`'s weighted fairness stops
being a bare mechanism and becomes a certified guarantee.

THE LAW. `priogov` serves actors highest-base-priority first, exactly floor(budget / actor_cost) equal-cost
actors per tick, so each priority class occupies a CONTIGUOUS block of the service order. The LAST actor of the
class at priority p therefore finishes at tick ceil(N_ge_p / m), where N_ge_p is the number of actors at
priority >= p and m = floor(budget / actor_cost). That cumulative-population wait, plus the shared rollback
window H, is the class's worst-case latency:
    class_worst_case_latency(p) = ceil(N_ge_p / m) + H.
Two structural consequences, both certified:
  * REFINEMENT — a higher priority sees a SMALLER-or-equal cumulative population, so a tighter bound; the lowest
    class sees the whole population, so its bound is EXACTLY the composite `slo`'s uniform number. Priority buys
    a better latency, never a worse one; the uniform SLO is the floor, recovered as the one-class case.
  * PER-CLASS REFUSE — `class_slo_admit` ADMITS iff EVERY class meets its OWN target, else `CLSLO-REFUSE`
    naming the highest-priority class that misses. A tier whose promise cannot be kept is declined by name,
    never silently folded into an average.

THE SOUNDNESS. The per-class bound is not asserted, it is CHECKED against reality: the gate runs `priogov` over
a corpus of class configs and confirms ceil(N_ge_p / m) EQUALS the measured last-served tick of every class
(exact for equal-cost actors — the same soundness discipline that made the composite `slo` trustworthy, now
applied to the harder per-class quantity). A defect — an off-by-one cumulative, a wrong tie-break — moves the
measured tick away from the formula and reddens the row.

THE COMPOSITION. `priogov` (the per-class schedule + actor_cost), `horizon` (the shared window), and `slo` (the
one-class bound it reduces to) — no network, no chunking, all exact integer op-counts, so the table reproduces
bit-for-bit.

GRADE. The per-class bound, its REFINEMENT (monotone in priority; one class == `slo`), its SOUNDNESS against the
real `priogov` drain (exact for equal-cost), the by-name `CLSLO-REFUSE`, and determinism are MEASURED (exact,
reproducible, a defect diverges). `does_not_show`: WALL-CLOCK (ticks, not seconds — `bench.py` is
MEASURED-on-named-host); HETEROGENEOUS per-actor costs (this bounds the equal-cost class `priogov` schedules —
a non-fitting prefix that admits fewer than floor(budget/cost) is a follow-on); dynamic ARRIVALS mid-drain (the
bound is for a static population; aging bounds the wait either way, but the closed form is the static one);
pre-emption; and any guarantee under an adversarial OS scheduler."""
import hashlib
import os as _os
import sys as _sys

MAGIC = b"URDRLAT3"
_HERE = _os.path.dirname(_os.path.abspath(__file__))
if _HERE not in _sys.path:
    _sys.path.insert(0, _HERE)
import govern as _GV                                            # actor_cost + the drain priogov extends
import priogov as _PG                                           # the per-class schedule (soundness ground truth)
import horizon as _HZ                                           # the shared rollback window
import slo as _SL                                               # the one-class bound clslo reduces to
import opcost as _OC                                            # OPCOST-REFUSE (shared refuse family)


class ClsloError(Exception):
    def __init__(self, message, priority=None):
        super().__init__(f"CLSLO-REFUSE: {message}")
        self.code = "CLSLO-REFUSE"
        self.priority = priority


def _norm(classes):
    """Validate and return classes as a tuple of (priority, count) sorted by priority DESCENDING. Priorities
    must be distinct positive ints; counts positive ints — one class per priority."""
    if not classes:
        raise ClsloError("no classes given")
    seen = set()
    out = []
    for item in classes:
        if not (type(item) is tuple and len(item) == 2):
            raise ClsloError(f"class must be (priority, count), got {item!r}")
        pr, cnt = item
        if not (type(pr) is int and pr > 0 and type(cnt) is int and cnt > 0):
            raise ClsloError(f"class needs positive int priority and count, got {item!r}")
        if pr in seen:
            raise ClsloError(f"duplicate priority {pr} — classes are one per priority")
        seen.add(pr)
        out.append((pr, cnt))
    out.sort(key=lambda pc: -pc[0])
    return tuple(out)


def _per_tick(budget, actor_cost):
    if not (type(budget) is int and type(actor_cost) is int and actor_cost > 0):
        raise ClsloError(f"bad budget/actor_cost: {budget!r} / {actor_cost!r}")
    if actor_cost > budget:
        raise _OC.OpcostError(f"actor cost {actor_cost} > budget {budget} — cannot fit any tick")
    return budget // actor_cost


def population_at_least(classes, priority):
    """N_ge_p — the number of actors at priority >= p (the cumulative population a class waits behind)."""
    cs = _norm(classes)
    return sum(c for (pr, c) in cs if pr >= priority)


def class_admission_wait(classes, budget, actor_cost, priority):
    """The worst-case admission wait in TICKS for the class at `priority`: its last actor sits at cumulative
    position N_ge_p in the priority-sorted service order, so it drains at ceil(N_ge_p / floor(budget/cost)).
    An `OPCOST-REFUSE` if a single actor cannot fit the budget."""
    cs = _norm(classes)
    if priority not in {pr for pr, _ in cs}:
        raise ClsloError(f"no class at priority {priority}")
    m = _per_tick(budget, actor_cost)
    n_ge = sum(c for (pr, c) in cs if pr >= priority)
    return -(-n_ge // m)                                        # ceil division, integer-exact


def class_worst_case_latency(classes, budget, actor_cost, horizon, priority):
    """The class's composite worst-case end-to-end latency: its cumulative admission wait + the shared rollback
    window. One certified number per class."""
    return class_admission_wait(classes, budget, actor_cost, priority) + _HZ.worst_case_window(horizon)


def class_table(classes, budget, actor_cost, horizon):
    """The per-class worst-case latency table as a tuple of (priority, latency), HIGH priority first. The
    highest class carries the tightest bound; the lowest carries EXACTLY the composite slo's uniform number."""
    cs = _norm(classes)
    return tuple((pr, class_worst_case_latency(cs, budget, actor_cost, horizon, pr)) for (pr, _c) in cs)


def _targets_map(targets):
    tmap = {}
    for item in targets:
        if not (type(item) is tuple and len(item) == 2):
            raise ClsloError(f"target must be (priority, target_ticks), got {item!r}")
        pr, tg = item
        if not (type(pr) is int and type(tg) is int and tg >= 0):
            raise ClsloError(f"target needs int priority and non-negative ticks, got {item!r}")
        tmap[pr] = tg
    return tmap


def class_slo_admit(classes, budget, actor_cost, horizon, targets):
    """ADMIT the config iff EVERY class meets its OWN target latency, returning the class table; else
    `CLSLO-REFUSE` naming the highest-priority class that misses (checked high priority first). A promise made
    per tier is kept per tier, or the specific tier is declined by name — never averaged away."""
    cs = _norm(classes)
    tmap = _targets_map(targets)
    for (pr, _c) in cs:
        if pr not in tmap:
            raise ClsloError(f"no target for the class at priority {pr}", priority=pr)
    for (pr, _c) in cs:                                         # high priority first (cs is sorted desc)
        w = class_worst_case_latency(cs, budget, actor_cost, horizon, pr)
        if w > tmap[pr]:
            raise ClsloError(f"class p{pr} worst-case {w} ticks exceeds its target {tmap[pr]}", priority=pr)
    return class_table(cs, budget, actor_cost, horizon)


# ---- soundness ground truth (priogov) — used by the gate / tests, not by the pinned table ----
def class_actors(field, classes, cmds, max_step, sub):
    """Build priogov actors (start, priority) for `classes` on `field`, one distinct interior start per actor
    (equal cost on flat terrain), interleaved so the actor tuple is deliberately NOT pre-sorted by priority —
    the bound must hold for any arrival order, not just a convenient one."""
    cs = _norm(classes)
    cells = [(x, y) for x in range(2, 14) for y in range(2, 14)]
    pools = [[pr] * c for (pr, c) in cs]
    actors = []
    idx = 0
    while any(pools):
        for pool in pools:
            if pool:
                pr = pool.pop()
                actors.append((cells[idx], pr))
                idx += 1
    return tuple(actors)


def measured_class_ticks(field, actors, cmds, max_step, sub, budget, age_step):
    """Run `priogov.drain_prio` and return {priority: last served tick} — the REAL per-class latency the formula
    must match."""
    served = _PG.drain_prio(field, actors, cmds, max_step, sub, budget, age_step)
    by = {}
    for (_s, p), t in zip(actors, served):
        by[p] = max(by.get(p, 0), t)
    return by


def soundness_holds(field, classes, cmds, max_step, sub, budget, age_step):
    """True iff the per-class admission bound EQUALS priogov's real per-class last-served tick for every class
    (exact for equal-cost actors) — the guarantee is checked against the scheduler, not assumed."""
    cs = _norm(classes)
    actors = class_actors(field, cs, cmds, max_step, sub)
    ac = _GV.actor_cost(field, actors[0][0], cmds, max_step, sub)
    meas = measured_class_ticks(field, actors, cmds, max_step, sub, budget, age_step)
    for (pr, _c) in cs:
        if class_admission_wait(cs, budget, ac, pr) != meas[pr]:
            return False
    return True


def clslo_digest(name, classes, budget, actor_cost, horizon, table, verdict):
    """URDRLAT3 canon — SHA-256(MAGIC | name | classes | budget | actor_cost | horizon | table | verdict).
    Binds the whole per-class guarantee and its verdict, so any change to a class bound or a refuse moves it."""
    cs = _norm(classes)
    cstr = ",".join(f"p{pr}:{c}" for (pr, c) in cs)
    tstr = ",".join(f"p{pr}:{lat}" for (pr, lat) in table)
    hh = hashlib.sha256()
    hh.update(MAGIC)
    hh.update(f"|{name}|classes:{cstr}|b:{budget}|c:{actor_cost}|h:{horizon}|table:{tstr}|v:{verdict}".encode())
    return hh.hexdigest()


# ---- scenarios (pinned by the gate) -----------------------------------------------------
_MS, _SUB = 40, 4
_CMDS = "eeee"


def _flat16():
    return tuple(tuple(0 for _x in range(16)) for _y in range(16))


def _actor_cost():
    return _GV.actor_cost(_flat16(), (2, 8), _CMDS, _MS, _SUB)


# (classes, budget_mult, horizon, targets) — m = budget_mult equal-cost actors per tick.
_SCENES = {
    # premium(p3, 2) + standard(p2, 3) + free(p1, 4); m = 3, H = 2.
    #   premium: ceil(2/3)=1 +2 = 3 ; standard: ceil(5/3)=2 +2 = 4 ; free: ceil(9/3)=3 +2 = 5
    "tiered_admit":   (((3, 2), (2, 3), (1, 4)), 3, 2, ((3, 3), (2, 4), (1, 5))),   # every class meets -> ADMIT
    "premium_refuse": (((3, 2), (2, 3), (1, 4)), 3, 2, ((3, 2), (2, 4), (1, 5))),   # premium 3 > target 2 -> REFUSE p3
    "single_uniform": (((1, 6),),                3, 2, ((1, 5),)),                  # one class == slo: ceil(6/3)+2=4 <=5
}
SCENES = ("tiered_admit", "premium_refuse", "single_uniform")


def scene_case(name):
    """(table, verdict) for a named config — verdict is ADMIT or CLSLO-REFUSE:p<k> (the failing class)."""
    classes, bmult, hz, targets = _SCENES[name]
    c = _actor_cost()
    budget = bmult * c
    table = class_table(classes, budget, c, hz)
    try:
        class_slo_admit(classes, budget, c, hz, targets)
        verdict = "ADMIT"
    except ClsloError as exc:
        verdict = f"CLSLO-REFUSE:p{exc.priority}"
    return table, verdict


def scene_result(name):
    classes, bmult, hz, _targets = _SCENES[name]
    c = _actor_cost()
    table, verdict = scene_case(name)
    return clslo_digest(name, classes, bmult * c, c, hz, table, verdict)


def golden(name):
    with open(_os.path.join(_HERE, "conformance_clslo.txt"), encoding="utf-8") as fh:
        for ln in fh:
            ln = ln.strip()
            if ln and not ln.startswith("#"):
                nm, dig = ln.split()
                if nm == name:
                    return dig
    raise ClsloError(f"no golden named {name!r}")
