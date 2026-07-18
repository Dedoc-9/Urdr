# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""priogov — the PRIORITY work governor (T3.31, MMO Stage H, URDROPC3): the weighted-fairness follow-on `govern`
named in its own does_not_show. `govern` admitted a FIFO prefix within the tick op-budget; `priogov` admits a
PRIORITY prefix — higher-priority actors first — while AGING keeps the lowest priority from ever starving.

THE LAW. Each actor carries a base priority. Per tick, the EFFECTIVE priority is `base + age_step * wait`, so a
deferred actor climbs the order the longer it waits; the tick admits the highest-effective-priority prefix that
fits the budget and defers the rest. Same three guarantees as `govern`, now priority-aware:
  * NEVER-OVERRUN — an admitted tick's work is always <= budget (the live latency guarantee is preserved).
  * PRIORITY-ORDER (fresh) — with no wait yet, admission order is exactly base priority (highest first); a
    single actor over budget is a hard `OPCOST-REFUSE`.
  * NO-STARVATION / BOUNDED-WAIT — because aging raises a waiter's effective priority without bound, every
    actor is eventually admitted, and (each tick admitting >= 1) `drain_prio` serves N actors in <= N ticks —
    so even the lowest base priority waits at most N ticks. Priority buys ORDER, never permanent exclusion.

So priority decides WHO goes first; aging guarantees EVERYONE goes. Refuse-or-defer, never overrun; prioritise,
never starve.

THE COMPOSITION. `actor_cost` is reused from `opcost` (via `govern`); the only new machinery is the effective-
priority sort and the aging counter. All exact integer op-counts, so the schedule reproduces bit-for-bit.

GRADE. Never-overrun, the fresh-tick priority order, the over-budget REFUSE, termination / bounded-wait (<= N),
no-starvation under aging, conservation (served exactly once), and determinism are MEASURED (exact,
reproducible, a defect diverges). `does_not_show`: WALL-CLOCK (bounds WORK per tick; the time bound is
`bench.py`'s, MEASURED-on-named-host); strict-priority WITHOUT aging (that CAN starve — this deliberately ages
to bound the wait); pre-emption mid-actor; a budget-filling (skip-and-continue) packing (this keeps the clean
priority PREFIX — a non-fitting actor stops the tick, it is not skipped for a lower one)."""
import hashlib
import os as _os
import sys as _sys

MAGIC = b"URDROPC3"
_HERE = _os.path.dirname(_os.path.abspath(__file__))
if _HERE not in _sys.path:
    _sys.path.insert(0, _HERE)
import govern as _GV                                            # actor_cost + the FIFO governor it extends
import opcost as _OC                                            # OPCOST-REFUSE


def _costs(field, actors, cmds, max_step, sub):
    costs = []
    for s, _p in actors:
        c = _GV.actor_cost(field, s, cmds, max_step, sub)
        costs.append(c)
    return costs


def admit_tick_prio(field, actors, cmds, max_step, sub, budget, waits=None):
    """One tick: admit the highest-EFFECTIVE-priority prefix that fits `budget`; defer the rest. `actors` is a
    tuple of (start, base_priority); `waits` (optional) is the per-actor wait so far (effective priority =
    base + wait). Returns (admitted_idx, deferred_idx, spent). A single actor over budget is `OPCOST-REFUSE`.
    GUARANTEE: spent <= budget, and the admitted set is a priority-ordered prefix (no lower jumps a deferred
    higher)."""
    if not (type(budget) is int and budget >= 0):
        raise _OC.OpcostError(f"budget must be a non-negative int, got {budget!r}")
    costs = _costs(field, actors, cmds, max_step, sub)
    for i, c in enumerate(costs):
        if c > budget:
            raise _OC.OpcostError(f"actor {i} costs {c} > budget {budget} — cannot fit any tick")
    w = waits if waits is not None else [0] * len(actors)
    order = sorted(range(len(actors)), key=lambda i: (-(actors[i][1] + w[i]), i))   # eff-prio desc, index asc
    admitted = []
    spent = 0
    for pos, i in enumerate(order):
        if spent + costs[i] > budget:
            deferred = tuple(sorted(order[pos:]))
            return tuple(sorted(admitted)), deferred, spent
        admitted.append(i)
        spent += costs[i]
    return tuple(sorted(admitted)), (), spent


def drain_prio(field, actors, cmds, max_step, sub, budget, age_step):
    """Iterate `admit_tick_prio` with AGING (effective priority = base + age_step * wait) until every actor is
    served. Returns the per-actor served tick (1-based). GUARANTEE: each tick's work <= budget; every tick
    admits >= 1; every actor served in <= N ticks (aging bounds the wait — no starvation)."""
    n = len(actors)
    if not (type(age_step) is int and age_step >= 0):
        raise _OC.OpcostError(f"age_step must be a non-negative int, got {age_step!r}")
    costs = _costs(field, actors, cmds, max_step, sub)
    for i, c in enumerate(costs):
        if c > budget:
            raise _OC.OpcostError(f"actor {i} costs {c} > budget {budget} — cannot fit any tick")
    served = {}
    wait = [0] * n
    remaining = set(range(n))
    tick = 0
    guard = n + 1
    while remaining:
        tick += 1
        order = sorted(remaining, key=lambda i: (-(actors[i][1] + age_step * wait[i]), i))
        spent = 0
        admitted = []
        for i in order:
            if spent + costs[i] > budget:
                break
            admitted.append(i)
            spent += costs[i]
        if not admitted:                                        # unreachable given the refuse filter
            raise _OC.OpcostError("no progress: a remaining actor exceeds the budget")
        for i in admitted:
            served[i] = tick
            remaining.discard(i)
        for i in remaining:
            wait[i] += 1
        guard -= 1
        if guard < 0:                                           # pragma: no cover - the <= N bound guarantees this
            raise _OC.OpcostError("drain_prio exceeded the N-tick bound")
    return tuple(served[i] for i in range(n))


def priogov_digest(name, field, actors, cmds, max_step, sub, budget, age_step):
    """URDROPC3 canon — SHA-256(MAGIC | name | budget | age_step | per-actor served ticks). Binds the priority
    schedule, so a changed priority, budget, aging rate, or governor defect moves it."""
    served = drain_prio(field, actors, cmds, max_step, sub, budget, age_step)
    hh = hashlib.sha256()
    hh.update(MAGIC)
    hh.update(f"|{name}|budget:{budget}|age:{age_step}|served:{','.join(str(t) for t in served)}".encode())
    return hh.hexdigest()


# ---- scenarios (pinned by the gate) -----------------------------------------------------
_MS, _SUB = 40, 4
_CMDS = "eeee"


def _flat16():
    return tuple(tuple(0 for _x in range(16)) for _y in range(16))


# 5 actors, priorities 1..5 given in REVERSE arrival order (actor 0 is LOWEST priority, actor 4 HIGHEST), so a
# priority governor must reorder them; per-actor cost 20 on this world.
_ACTORS = (((2, 4), 1), ((2, 6), 2), ((2, 8), 3), ((2, 10), 4), ((2, 12), 5))


def scene_served(name):
    fld = _flat16()
    a = _GV.actor_cost(fld, _ACTORS[0][0], _CMDS, _MS, _SUB)
    if name == "prio_two_per_tick":                             # budget fits 2/tick, age_step 1
        return drain_prio(fld, _ACTORS, _CMDS, _MS, _SUB, 2 * a, 1)
    if name == "prio_one_per_tick":                             # 1/tick: strict priority order 4,3,2,1,0 (by idx)
        return drain_prio(fld, _ACTORS, _CMDS, _MS, _SUB, a, 1)
    if name == "prio_no_aging":                                 # age_step 0: still terminates (>=1/tick)
        return drain_prio(fld, _ACTORS, _CMDS, _MS, _SUB, a, 0)
    raise _OC.OpcostError(f"no scene named {name!r}")


SCENES = ("prio_two_per_tick", "prio_one_per_tick", "prio_no_aging")


def scene_result(name):
    fld = _flat16()
    a = _GV.actor_cost(fld, _ACTORS[0][0], _CMDS, _MS, _SUB)
    cfg = {"prio_two_per_tick": (2 * a, 1), "prio_one_per_tick": (a, 1), "prio_no_aging": (a, 0)}[name]
    return priogov_digest(name, fld, _ACTORS, _CMDS, _MS, _SUB, cfg[0], cfg[1])


def golden(name):
    with open(_os.path.join(_HERE, "conformance_priogov.txt"), encoding="utf-8") as fh:
        for ln in fh:
            ln = ln.strip()
            if ln and not ln.startswith("#"):
                nm, dig = ln.split()
                if nm == name:
                    return dig
    raise _OC.OpcostError(f"no golden named {name!r}")
