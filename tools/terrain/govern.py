# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""govern — the per-tick work governor (T3.30, MMO Stage H, URDROPC2): the `opcost` envelope turned into LIVE
ENFORCEMENT. `opcost` certified the exact integer WORK of a tick and seeded a typed `OPCOST-REFUSE`; this module
makes the budget bind every tick, deterministically, with a bounded-latency guarantee — and needs no network,
no chunking, no external infrastructure. It is the self-contained sequel to the latency envelope.

THE LAW. Given a per-tick op-BUDGET, `admit_tick` admits a FIFO prefix of the actors whose CUMULATIVE work fits
the budget and DEFERS the rest to the next tick. Three properties, all exact and gate-certified:
  * NEVER-OVERRUN — an admitted tick's spent work is always <= budget. The wall-clock of a tick is therefore
    bounded by budget x (host per-op cost), the benched number. This is the live latency guarantee.
  * PROGRESS (no deadlock) — a single actor whose cost alone exceeds the budget is a hard `OPCOST-REFUSE` (it
    can never fit any tick — an impossible / adversarial request, refused outright, never left to starve a
    queue). With that filter every remaining actor costs <= budget, so the FIRST queued actor always fits and
    every tick admits >= 1 actor.
  * BOUNDED-WAIT (FIFO fairness) — because admission is in-order and every tick makes progress, `drain` serves
    N actors in <= N ticks; an actor at queue position p waits at most p ticks. No starvation.

So a deferred actor is not dropped and not smoothed — it is served on a later tick, within a certified bound,
while no tick ever runs over its work budget. Refuse-or-defer, never overrun; serve-in-order, never starve.

THE COMPOSITION. `actor_cost` = one actor's `opcost` contribution (glide micro-steps + admit sub-steps).
`admit_tick` is a greedy in-order bin fit; `drain` iterates it to completion. All exact integer op-counts, so
the whole governor is deterministic and reproduces bit-for-bit.

GRADE. The never-overrun bound, the single-over-budget REFUSE, the progress (>= 1 admitted per tick) and
bounded-wait (<= N ticks) properties, conservation (admitted + deferred = all actors, none lost or
duplicated), and determinism are MEASURED (exact, reproducible, a defect diverges). `does_not_show`: WALL-CLOCK
enforcement (this bounds the WORK per tick; the wall-clock bound follows only via the host-tagged `bench.py`
per-op cost, MEASURED-on-named-host); priority / weighted fairness (this is FIFO — a priority queue is a
follow-on); pre-emption mid-actor (an actor is admitted whole or deferred whole); and any guarantee under an
adversarial OS scheduler (the governor bounds the work a tick ISSUES, not the time the OS gives it)."""
import hashlib
import os as _os
import sys as _sys

MAGIC = b"URDROPC2"
_HERE = _os.path.dirname(_os.path.abspath(__file__))
if _HERE not in _sys.path:
    _sys.path.insert(0, _HERE)
import opcost as _OC                                            # the certified work envelope + OPCOST-REFUSE
import glide as _GL                                             # the mover (for per-actor cells)


def actor_cost(field, start, cmds, max_step, sub):
    """One actor's per-tick work: its glide micro-steps + its admit sub-steps (the `opcost` contribution).
    Exact and deterministic."""
    g = _GL.glide_cells(field, start, cmds, max_step, sub)
    cells = tuple((p[0] >> 32, p[1] >> 32) for p in g)
    return _OC.glide_micro_count(field, start, cmds, max_step, sub) + _OC.admit_substeps(cells)


def admit_tick(field, starts, cmds, max_step, sub, budget):
    """Admit a FIFO prefix of `starts` whose cumulative work fits `budget`; defer the rest. Returns
    (admitted, deferred, spent). A single actor with cost > budget is an `OPCOST-REFUSE` (it can never fit).
    GUARANTEE: spent <= budget, and (given the refuse filter) at least the first actor is admitted."""
    if not (type(budget) is int and budget >= 0):
        raise _OC.OpcostError(f"budget must be a non-negative int, got {budget!r}")
    admitted = []
    spent = 0
    for i, s in enumerate(starts):
        c = actor_cost(field, s, cmds, max_step, sub)
        if c > budget:
            raise _OC.OpcostError(f"actor {i} costs {c} > budget {budget} — cannot fit any tick")
        if spent + c > budget:
            return tuple(admitted), tuple(starts[i:]), spent
        admitted.append(s)
        spent += c
    return tuple(admitted), (), spent


def drain(field, starts, cmds, max_step, sub, budget):
    """Iterate `admit_tick` until every actor is served. Returns the tuple of per-tick admitted COUNTS.
    GUARANTEE: each tick's work <= budget; every tick admits >= 1 (progress); N actors drain in <= N ticks
    (bounded wait). Raises `OPCOST-REFUSE` if any single actor cannot fit the budget."""
    queue = tuple(starts)
    ticks = []
    guard = len(queue) + 1                                       # <= N ticks; a safety cap that must never bind
    while queue:
        admitted, deferred, _spent = admit_tick(field, queue, cmds, max_step, sub, budget)
        if not admitted:                                        # unreachable given the refuse filter — defensive
            raise _OC.OpcostError("no progress: a queued actor exceeds the budget")
        ticks.append(len(admitted))
        queue = deferred
        guard -= 1
        if guard < 0:                                           # pragma: no cover - the <= N bound guarantees this
            raise _OC.OpcostError("drain exceeded the N-tick bound")
    return tuple(ticks)


def wait_ticks(field, starts, cmds, max_step, sub, budget):
    """The tick on which each actor is served (its bounded wait): actor at index i is served on tick
    wait[i] (1-based). Certifies bounded-wait directly. Derived from `drain`'s per-tick counts."""
    counts = drain(field, starts, cmds, max_step, sub, budget)
    waits = []
    tick = 0
    for n in counts:
        tick += 1
        waits.extend([tick] * n)
    return tuple(waits)


def govern_digest(name, field, starts, cmds, max_step, sub, budget):
    """URDROPC2 canon — SHA-256(MAGIC | name | budget | per-tick admitted counts | total spent). Binds the
    admission schedule, so a changed budget, a changed actor cost, or a defect in the governor moves it."""
    counts = drain(field, starts, cmds, max_step, sub, budget)
    spent = sum(actor_cost(field, s, cmds, max_step, sub) for s in starts)
    hh = hashlib.sha256()
    hh.update(MAGIC)
    hh.update(f"|{name}|budget:{budget}|counts:{','.join(str(c) for c in counts)}|spent:{spent}".encode())
    return hh.hexdigest()


# ---- scenarios (pinned by the gate) -----------------------------------------------------
_MS, _SUB = 40, 4


def _flat16():
    return tuple(tuple(0 for _x in range(16)) for _y in range(16))


_STARTS = ((2, 4), (2, 6), (2, 8), (2, 10), (2, 12))            # 5 actors, each an "eeee" glide on flat ground
_CMDS = "eeee"


def _actor_cost_flat():
    return actor_cost(_flat16(), _STARTS[0], _CMDS, _MS, _SUB)


def scene_schedule(name):
    """Run a named governor scenario -> its (per-tick admitted counts, spent). Deterministic."""
    fld = _flat16()
    a = _actor_cost_flat()                                       # one actor's cost on this world
    if name == "fits_one":                                       # a generous budget: all 5 in one tick
        return drain(fld, _STARTS, _CMDS, _MS, _SUB, 5 * a)
    if name == "split_two":                                      # room for 3 actors/tick -> counts (3, 2)
        return drain(fld, _STARTS, _CMDS, _MS, _SUB, 3 * a)
    if name == "one_each":                                       # exactly one actor/tick -> counts (1,1,1,1,1)
        return drain(fld, _STARTS, _CMDS, _MS, _SUB, a)
    raise _OC.OpcostError(f"no scene named {name!r}")


SCENES = ("fits_one", "split_two", "one_each")


def scene_result(name):
    fld = _flat16()
    a = _actor_cost_flat()
    budget = {"fits_one": 5 * a, "split_two": 3 * a, "one_each": a}[name]
    return govern_digest(name, fld, _STARTS, _CMDS, _MS, _SUB, budget)


def golden(name):
    with open(_os.path.join(_HERE, "conformance_govern.txt"), encoding="utf-8") as fh:
        for ln in fh:
            ln = ln.strip()
            if ln and not ln.startswith("#"):
                nm, dig = ln.split()
                if nm == name:
                    return dig
    raise _OC.OpcostError(f"no golden named {name!r}")
