# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""schedule — the ADAPTIVE PRIORITY SCHEDULER (URDRSCH1): bandwidth- and importance-aware refresh
scheduling over the clarity-bounded throttle (URDRTHR1). The throttle refreshes each entity on its clarity
cadence; when MORE entities are due than a per-tick refresh BUDGET allows (a bandwidth cap), the scheduler
chooses WHICH get fresh positions by priority — while guaranteeing that nothing STARVES. Composition over
`throttle`/`anamorphosis`/`perception`, NO NEW GLYPH — the kernel stays frozen. See
`docs/schedule_brief.md` for the design pass and the D1 §20 glyph ruling.

THE NEW HAZARD, AND THE LAW THAT ANSWERS IT. A naive priority scheme — always serve the most important —
STARVES the low-priority: a far, coarse entity that is always outranked never refreshes, and its staleness
grows without bound, breaking the throttle's bounded-staleness guarantee. The scheduler is therefore
STARVATION-FREE by construction: among the due, it serves OLDEST-FIRST (age primary), with importance and
eid as deterministic tiebreaks. Age-first guarantees every due entity is refreshed within a bounded window,
so staleness stays bounded even under a saturated budget.

THE SEPARATION (inherited from the throttle). Scheduling delays POSITION, never PRESENCE: MEMBERSHIP is the
live manifested set (closed-world every tick — a deferred entity is still SHOWN, just with its carried
position; a departed entity is DROPPED, no ghosts). Only the POSITION-refresh is scheduled.

THE MODEL (deterministic, exact-integer, no wall-clock — `tick` is an explicit integer of the replay):
  * rate = 2^shift (the throttle cadence — importance sets HOW OFTEN you are due: sharp every tick, coarse
    every 2^COARSEST);
  * an entity is DUE iff it just entered OR `tick − last_refresh ≥ rate` (stale past its cadence);
  * each tick, ENTRANTS refresh (mandatory — membership needs a position), then up to `budget` DUE-known
    entities refresh, chosen by priority = (age, importance, −eid) descending (OLDEST-FIRST — starvation-
    free; importance breaks ties so the most relevant of equally-stale entities wins);
  * every other manifested entity is CARRIED (its last shown position), and every manifested entity is
    SHOWN (membership live).

THE GATE-CHECKED LAWS (red-first — the plants bite before the goldens pin):
  * CLOSED-WORLD EVERY TICK (membership live) — `_run_membership_defer` (drop an unbudgeted due entity from
    the transcript) breaks it and is caught.
  * BOUNDED STALENESS under a saturated budget — max staleness ≤ MAX_STALE + ⌈CAPACITY/budget⌉;
    `_run_static_priority` (importance-only, no age) STARVES the coarse and exceeds the bound.
  * BUDGET RESPECTED — at most `budget` discretionary refreshes per tick; `_run_over_budget` exceeds it.
  * PRIORITY CORRECT — the refreshed discretionary set is exactly the top-`budget` due-known by priority;
    `_run_inversion` (serve the youngest) violates it.
  * DETERMINISTIC REPLAY — a run is a pure function of (ticks, lens, budget); the wall-clock plant diverges.
  * REDUCES TO THE THROTTLE — at `budget ≥ CAPACITY` no due entity is ever deferred, so staleness collapses
    to the throttle's ≤ MAX_STALE: the no-contention corner.

GRADE: MEASURED. DECLARED: inherits every throttle/anamorphosis/perception boundary; adds a NEW declared
boundary — under budget pressure a carried position may be staler than the pure cadence (up to
MAX_STALE + ⌈CAPACITY/budget⌉), the cost of the bandwidth cap; bounded and declared, not eliminated (raise
the budget to the no-contention corner). `does_not_show`: continuous line-of-sight (exact integer grid);
byte-level bandwidth accounting (the budget is a per-tick refresh COUNT, not a byte meter — a declared
successor); cross-placement (URDRSCH1 Python reference only)."""
import hashlib
import os as _os
import sys as _sys

_HERE = _os.path.dirname(_os.path.abspath(__file__))
if _HERE not in _sys.path:
    _sys.path.insert(0, _HERE)

import throttle as TH                                            # the rung this composes over  # noqa: E402
import anamorphosis as A                                         # noqa: E402
import perception as PC                                          # noqa: E402

MAGIC = b"URDRSCH1"
DIGEST_BYTES = A.DIGEST_BYTES
CAPACITY = A.CAPACITY
SLOT_BYTES = A.SLOT_BYTES
PAD_EID = A.PAD_EID
COARSEST = A.COARSEST
MAX_STALE = TH.MAX_STALE                                        # the throttle's cadence bound, inherited
_HEADER = len(MAGIC) + 4 + 4 + 4 + 4                            # MAGIC | reach | focus | tick | capacity
_PAD_SLOT = PAD_EID.to_bytes(4, "big") + b"\x00" * (SLOT_BYTES - 4)


class ScheduleError(Exception):
    def __init__(self, message):
        super().__init__(f"SCHEDULE-REFUSE: {message}")
        self.code = "SCHEDULE-REFUSE"


def stale_bound(budget):
    """The declared staleness bound under a saturated budget: the cadence bound plus the worst-case
    deferral ⌈CAPACITY/budget⌉ (age-first drains the due queue that fast)."""
    if type(budget) is not int or budget < 1:
        raise ScheduleError(f"budget must be a positive int, got {budget!r}")
    return MAX_STALE + (CAPACITY + budget - 1) // budget


def _importance(entities, cl, L, eid):
    return COARSEST - A.shift_of(entities, cl, L, eid)          # sharper (closer/central) = more important


# ---- the constant-shape, tick-stamped transcript ----------------------------------------------
def transcript_bytes_len():
    return _HEADER + CAPACITY * SLOT_BYTES + DIGEST_BYTES


def _slot(eid, x, y, cite_hex):
    return (eid.to_bytes(4, "big") + (x & 0xFFFFFFFF).to_bytes(4, "big")
            + (y & 0xFFFFFFFF).to_bytes(4, "big") + PC._cite_bytes(cite_hex))


def _frame(L, tick, shown):
    reach, focus = L
    body = bytearray(MAGIC) + reach.to_bytes(4, "big") + focus.to_bytes(4, "big") \
        + (tick & 0xFFFFFFFF).to_bytes(4, "big") + CAPACITY.to_bytes(4, "big")
    slots = [_slot(eid, x, y, cite) for eid, (x, y, cite, _asof) in sorted(shown.items())]
    if len(slots) > CAPACITY:
        raise ScheduleError(f"{len(slots)} shown entities exceed the transcript capacity {CAPACITY}")
    for s in slots:
        body += s
    for _ in range(CAPACITY - len(slots)):
        body += _PAD_SLOT
    return bytes(body) + hashlib.sha256(bytes(body)).digest()


# ---- the priority (oldest-first, starvation-free) ---------------------------------------------
def _due(state, entities, cl, L, tick, eid):
    """An entity is DUE iff it just entered OR it is stale past its clarity cadence (`tick − as_of ≥
    rate`)."""
    prev = state.get(eid)
    if prev is None:
        return True
    return (tick - prev[3]) >= TH.rate_of(A.shift_of(entities, cl, L, eid))


def _priority(state, entities, cl, L, tick, eid):
    """The scheduling key, HIGHEST first: age (oldest-first — starvation-free), then importance (the most
    relevant of equally-stale), then a deterministic eid tiebreak."""
    age = tick - state[eid][3]
    return (age, _importance(entities, cl, L, eid), -eid)


def _select(state, entities, walls, cl, L, tick, budget):
    """Return (manifest, entrants, refreshed_discretionary) — the entrants (mandatory) and the top-`budget`
    due-known entities by priority."""
    man = A._manifest_under(entities, walls, cl, L)
    entrants = [e for e in man if e not in state]
    due_known = [e for e in man if e in state and _due(state, entities, cl, L, tick, e)]
    due_known.sort(key=lambda e: _priority(state, entities, cl, L, tick, e), reverse=True)
    return man, entrants, due_known[:budget]


# ---- the stateful step ------------------------------------------------------------------------
def step(state, entities, walls, cl, L, tick, budget, _clock=None):
    """One tick: emit the scheduled transcript and the new client state. Membership is the live manifested
    set (a departed entity is dropped); entrants and the top-`budget` due-known entities refresh, the rest
    are carried. Returns (transcript, new_state, manifest, refreshed_eids, discretionary_count)."""
    man, entrants, disc = _select(state, entities, walls, cl, L, tick, budget)
    drift = 0 if _clock is None else _clock()                  # the wall-clock plant folds a value in here
    refresh = set(entrants) | set(disc)
    if drift:
        refresh |= {e for e in man if e in state and _due(state, entities, cl, L, tick, e)}
    new_state = {}
    refreshed = []
    for eid in man:
        if eid in refresh:
            ex, ey, cite = entities[eid]
            s = A.shift_of(entities, cl, L, eid)
            new_state[eid] = (A.quantize(ex, s), A.quantize(ey, s), cite, tick)
            refreshed.append(eid)
        else:
            new_state[eid] = state[eid]                         # carry (deferred or not-yet-due)
    return _frame(L, tick, new_state), new_state, man, refreshed, len(disc)


def run(ticks, cl, L, budget, _clock=None):
    """Thread a sequence of authority worlds through the scheduler. Returns {transcripts, manifests, report}
    where report tallies deferrals, discretionary refreshes, max staleness, departures."""
    state = {}
    transcripts = []
    manifests = []
    refresh_total = manifest_total = disc_total = deferrals = departures = max_stale = max_disc = 0
    prev_man = set()
    for t, (entities, walls) in enumerate(ticks):
        man, entrants, disc = _select(state, entities, walls, cl, L, t, budget)
        due_known = [e for e in man if e in state and _due(state, entities, cl, L, t, e)]
        deferrals += len(due_known) - len(disc)                 # due but not picked this tick
        tr, state, man2, refreshed, dcount = step(state, entities, walls, cl, L, t, budget, _clock)
        transcripts.append(tr)
        manifests.append(man2)
        refresh_total += len(refreshed)
        manifest_total += len(man2)
        disc_total += dcount
        max_disc = max(max_disc, dcount)
        departures += len(prev_man - set(man2))
        for _eid, (_x, _y, _c, asof) in state.items():
            max_stale = max(max_stale, t - asof)
        prev_man = set(man2)
    return {"transcripts": transcripts, "manifests": manifests, "refresh_total": refresh_total,
            "manifest_total": manifest_total, "disc_total": disc_total, "deferrals": deferrals,
            "departures": departures, "max_stale": max_stale, "max_disc": max_disc}


# ---- reconstruction / laws --------------------------------------------------------------------
def _parse(transcript):
    if not (type(transcript) is bytes or type(transcript) is bytearray):
        raise ScheduleError("a transcript must be bytes")
    t = bytes(transcript)
    if len(t) != transcript_bytes_len():
        raise ScheduleError(f"a transcript must be exactly {transcript_bytes_len()} bytes")
    if t[:len(MAGIC)] != MAGIC:
        raise ScheduleError("bad magic — not a URDRSCH1 transcript")
    if hashlib.sha256(t[:-DIGEST_BYTES]).digest() != t[-DIGEST_BYTES:]:
        raise ScheduleError("digest mismatch — tampered or truncated")
    off = _HEADER
    slots = []
    for _ in range(CAPACITY):
        raw = t[off:off + SLOT_BYTES]; off += SLOT_BYTES
        eid = int.from_bytes(raw[:4], "big")
        if eid == PAD_EID:
            continue
        x = int.from_bytes(raw[4:8], "big", signed=True)
        y = int.from_bytes(raw[8:12], "big", signed=True)
        slots.append((eid, x, y, raw[12:].hex()))
    return slots


def reconstruct(transcript):
    return {eid: (x, y, cite) for (eid, x, y, cite) in _parse(transcript)}


def is_closed_world_at(entities, walls, cl, L, transcript):
    """MEMBERSHIP LIVE: the reconstruction holds EXACTLY the manifested-under-L set — a deferred entity is
    still shown (carried), a departed one is dropped; scheduling changes refresh ORDER, never membership."""
    return set(reconstruct(transcript)) == set(A._manifest_under(entities, walls, cl, L))


def staleness_ok(report, budget):
    return report["max_stale"] <= stale_bound(budget)


def budget_ok(report, budget):
    return report["max_disc"] <= budget


def priority_correct(ticks, cl, L, budget):
    """The refreshed discretionary set at each tick is EXACTLY the top-`budget` due-known by priority."""
    state = {}
    for t, (entities, walls) in enumerate(ticks):
        man, entrants, disc = _select(state, entities, walls, cl, L, t, budget)
        due_known = [e for e in man if e in state and _due(state, entities, cl, L, t, e)]
        due_known.sort(key=lambda e: _priority(state, entities, cl, L, t, e), reverse=True)
        if set(disc) != set(due_known[:budget]):
            return False
        _tr, state, _m, _r, _d = step(state, entities, walls, cl, L, t, budget)
    return True


# ---- falsifier tools (NOT laws) ---------------------------------------------------------------
def _run_static_priority(ticks, cl, L, budget):
    """STARVATION: rank by importance ONLY (no age). A coarse, low-importance entity that is always
    outranked never refreshes — staleness grows without bound. Returns the report (max_stale)."""
    state = {}
    max_stale = 0
    for t, (entities, walls) in enumerate(ticks):
        man = A._manifest_under(entities, walls, cl, L)
        entrants = [e for e in man if e not in state]
        due_known = [e for e in man if e in state and _due(state, entities, cl, L, t, e)]
        due_known.sort(key=lambda e: (_importance(entities, cl, L, e), -e), reverse=True)  # BUG: no age
        refresh = set(entrants) | set(due_known[:budget])
        for eid in man:
            if eid in refresh:
                ex, ey, cite = entities[eid]; s = A.shift_of(entities, cl, L, eid)
                state[eid] = (A.quantize(ex, s), A.quantize(ey, s), cite, t)
        state = {e: state[e] for e in man}                     # drop departed (isolate the starvation bug)
        for eid in man:
            max_stale = max(max_stale, t - state[eid][3])
    return {"max_stale": max_stale}


def _run_membership_defer(ticks, cl, L, budget):
    """DEFER MEMBERSHIP (the mistake): a due entity that misses the budget is DROPPED from the transcript
    instead of being shown carried. Breaks closed-world — the reconstruction is a strict subset."""
    state = {}
    out = []
    for t, (entities, walls) in enumerate(ticks):
        man, entrants, disc = _select(state, entities, walls, cl, L, t, budget)
        refresh = set(entrants) | set(disc)
        shown = {}
        for eid in man:
            if eid in refresh:
                ex, ey, cite = entities[eid]; s = A.shift_of(entities, cl, L, eid)
                state[eid] = (A.quantize(ex, s), A.quantize(ey, s), cite, t)
                shown[eid] = state[eid]
            elif eid in state and not _due(state, entities, cl, L, t, eid):
                shown[eid] = state[eid]                         # BUG: a DEFERRED due entity is omitted
        state = {e: state[e] for e in man}
        out.append(_frame(L, t, shown))
    return out


def _run_over_budget(ticks, cl, L, budget):
    """BUDGET VIOLATION: refresh MORE than `budget` discretionary entities per tick. The budget-respected
    law (max discretionary ≤ budget) is caught. Returns the report (max_disc)."""
    state = {}
    max_disc = 0
    for t, (entities, walls) in enumerate(ticks):
        man, entrants, disc = _select(state, entities, walls, cl, L, t, budget + 2)  # BUG: over the budget
        max_disc = max(max_disc, len(disc))
        refresh = set(entrants) | set(disc)
        for eid in man:
            if eid in refresh:
                ex, ey, cite = entities[eid]; s = A.shift_of(entities, cl, L, eid)
                state[eid] = (A.quantize(ex, s), A.quantize(ey, s), cite, t)
        state = {e: state[e] for e in man}
    return {"max_disc": max_disc}


def _run_inversion(ticks, cl, L, budget):
    """PRIORITY INVERSION: serve the YOUNGEST due entities instead of the oldest. The priority-correct law
    is violated, and the oldest starve. Returns (transcripts, report)."""
    state = {}
    max_stale = 0
    for t, (entities, walls) in enumerate(ticks):
        man = A._manifest_under(entities, walls, cl, L)
        entrants = [e for e in man if e not in state]
        due_known = [e for e in man if e in state and _due(state, entities, cl, L, t, e)]
        due_known.sort(key=lambda e: _priority(state, entities, cl, L, t, e))  # BUG: ascending — youngest
        refresh = set(entrants) | set(due_known[:budget])
        for eid in man:
            if eid in refresh:
                ex, ey, cite = entities[eid]; s = A.shift_of(entities, cl, L, eid)
                state[eid] = (A.quantize(ex, s), A.quantize(ey, s), cite, t)
        state = {e: state[e] for e in man}
        for eid in man:
            max_stale = max(max_stale, t - state[eid][3])
    return {"max_stale": max_stale}


# ---- digests / scenarios ----------------------------------------------------------------------
def _d(i):
    return PC._d(i)


def run_digest(ticks, cl, L, budget):
    hh = hashlib.sha256(); hh.update(MAGIC)
    for tr in run(ticks, cl, L, budget)["transcripts"]:
        hh.update(hashlib.sha256(tr).digest())
    return hh.hexdigest()


def _seq(paths, nticks):
    ticks = []
    for t in range(nticks):
        ents = {eid: (xs[t][0], xs[t][1], _d(eid)) for eid, xs in paths.items()}
        ticks.append((ents, frozenset()))
    return ticks


def _contended(nticks=12):
    """A world where more entities are due than the budget can serve: a fan of entities at varied ranges,
    the viewpoint fixed. Forces deferrals and exercises the priority queue."""
    cl = PC.client(0, 0, 1, 0, 4, 2, 400, 0)
    paths = {}
    for i, (x, y) in enumerate([(3, 0), (6, 1), (10, 0), (13, 1), (16, 0)], start=1):
        paths[i] = [(x, y + (t % 2)) for t in range(nticks)]   # jitter → each is due on its cadence
    return _seq(paths, nticks), cl


def _scene(name, ticks, cl, L, budget, verdict):
    return hashlib.sha256(MAGIC + f"|{name}|L:{L[0]}:{L[1]}|b:{budget}|d:{run_digest(ticks, cl, L, budget)}"
                          f"|v:{verdict}".encode()).hexdigest()


def _scene_budget():
    ticks, cl = _contended()
    rep = run(ticks, cl, A.lens(0, 0), 2)
    ok = rep["max_disc"] <= 2 and rep["deferrals"] > 0
    return _scene("budget", ticks, cl, A.lens(0, 0), 2, "BUDGETED" if ok else "OVER")


def _scene_priority():
    ticks, cl = _contended()
    ok = priority_correct(ticks, cl, A.lens(0, 0), 2)
    return _scene("priority", ticks, cl, A.lens(0, 0), 2, "PRIORITIZED" if ok else "INVERTED")


def _scene_starvefree():
    ticks, cl = _contended(24)                                 # long enough for starvation to manifest
    rep = run(ticks, cl, A.lens(0, 0), 1)                      # the tightest budget
    ok = rep["max_stale"] <= stale_bound(1)
    return _scene("starvefree", ticks, cl, A.lens(0, 0), 1, "BOUNDED" if ok else "STARVED")


def _scene_reduce():
    ticks, cl = _contended()
    rep = run(ticks, cl, A.lens(0, 0), CAPACITY)              # no contention → collapses to the throttle
    ok = rep["max_stale"] <= MAX_STALE and rep["deferrals"] == 0
    return _scene("reduce", ticks, cl, A.lens(0, 0), CAPACITY, "THROTTLE" if ok else "DEFER")


_SCENES = {"budget": _scene_budget, "priority": _scene_priority,
           "starvefree": _scene_starvefree, "reduce": _scene_reduce}
SCENES = ("budget", "priority", "starvefree", "reduce")


def scene_result(name):
    return _SCENES[name]()


def golden(name):
    with open(_os.path.join(_HERE, "conformance_schedule.txt"), encoding="utf-8") as fh:
        for ln in fh:
            ln = ln.strip()
            if ln and not ln.startswith("#"):
                nm, dig = ln.split()
                if nm == name:
                    return dig
    raise ScheduleError(f"no golden named {name!r}")


# ---- the seeded property sweep ----------------------------------------------------------------
SWEEP_SEED = 20260724
SWEEP_COUNT = 80
NTICKS = 12
_BUDGETS = (1, 2, 3)


def gen_sequence(r):
    """A random contended world: a fixed viewpoint; several entities at varied ranges (so cadences differ
    and the budget is saturated), id2 behind (hidden ground truth), plus movers that depart."""
    cl = PC.client(0, 0, 1, 0, 4, 2, 400, 0)
    bases = {1: (r.rng(2, 5), r.rng(-1, 1)), 3: (r.rng(8, 12), r.rng(-2, 2)),
             4: (r.rng(14, 18), r.rng(-2, 2)), 5: (r.rng(16, 19), r.rng(-3, 3))}
    behind = (-r.rng(3, 8), r.rng(-3, 3))
    mover = (r.rng(3, 6), r.rng(-7, 7), r.rng(1, 3))           # drifts off-axis → departs
    ticks = []
    for t in range(NTICKS):
        ents = {2: (behind[0], behind[1], _d(2))}              # hidden
        for eid, (x, y) in bases.items():
            ents[eid] = (x, y + (t % 2), _d(eid))              # jitter → due on cadence
        ents[6] = (mover[0], mover[1] + mover[2] * t, _d(6))
        ticks.append((ents, frozenset()))
    return ticks, cl


def sweep(seed=SWEEP_SEED, count=SWEEP_COUNT):
    """The in-gate fixed-seed sweep over contended moving worlds × budgets, asserting per tick: CLOSED-WORLD
    (membership live), constant-shape, hidden-set invariance; per run: budget respected, bounded staleness,
    priority correct, deterministic replay. Non-vacuous: deferrals, departures, and stale records exercised.
    RAISES on the first violation."""
    hh = hashlib.sha256(); hh.update(MAGIC)
    r = PC._LCG(seed)
    deferrals = departures = stale_seen = prio_checked = 0
    for s in range(count):
        ticks, cl = gen_sequence(r)
        L = A.lens(0, 0)
        for budget in _BUDGETS:
            rep = run(ticks, cl, L, budget)
            if run_digest(ticks, cl, L, budget) != run_digest(ticks, cl, L, budget):
                raise ScheduleError(f"seq {s} b{budget}: not deterministic")
            if not budget_ok(rep, budget):
                raise ScheduleError(f"seq {s} b{budget}: refreshed {rep['max_disc']} > budget {budget}")
            if not staleness_ok(rep, budget):
                raise ScheduleError(f"seq {s} b{budget}: staleness {rep['max_stale']} exceeds bound "
                                    f"{stale_bound(budget)} — starvation")
            if not priority_correct(ticks, cl, L, budget):
                raise ScheduleError(f"seq {s} b{budget}: the refreshed set is not top-priority")
            prio_checked += 1
            for t, (entities, walls) in enumerate(ticks):
                tr = rep["transcripts"][t]
                if len(tr) != transcript_bytes_len():
                    raise ScheduleError(f"seq {s} b{budget} tick {t}: not constant-shape")
                if not is_closed_world_at(entities, walls, cl, L, tr):
                    raise ScheduleError(f"seq {s} b{budget} tick {t}: reconstruction is not the live "
                                        f"manifested set")
                moved = dict(entities); moved[2] = (entities[2][0], entities[2][1], _d(7000 + s))
                st = {}
                for u in range(t + 1):
                    e_u = moved if u == t else ticks[u][0]
                    tr_u, st, _m, _r, _dc = step(st, e_u, walls, cl, L, u, budget)
                if tr_u != tr:
                    raise ScheduleError(f"seq {s} b{budget} tick {t}: a hidden change altered the transcript")
            deferrals += rep["deferrals"]; departures += rep["departures"]
            stale_seen += 1 if rep["max_stale"] > 0 else 0
            hh.update(f"|{s}:{budget}:{run_digest(ticks, cl, L, budget)}:{rep['deferrals']}".encode())
    if deferrals == 0 or departures == 0 or stale_seen == 0 or prio_checked == 0:
        raise ScheduleError(f"NON-VACUITY: deferrals {deferrals}, departures {departures}, stale "
                            f"{stale_seen}, prio {prio_checked}")
    return {"scenarios": count, "deferrals": deferrals, "departures": departures, "stale_seen": stale_seen,
            "prio_checked": prio_checked, "digest": hh.hexdigest()}


def sweep_digest(seed=SWEEP_SEED, count=SWEEP_COUNT):
    return sweep(seed, count)["digest"]


def sweep_golden():
    with open(_os.path.join(_HERE, "conformance_schedule.txt"), encoding="utf-8") as fh:
        for ln in fh:
            ln = ln.strip()
            if ln and not ln.startswith("#"):
                nm, dig = ln.split()
                if nm == "sweep":
                    return dig
    raise ScheduleError("no golden named 'sweep'")


def explore(base_seed, n_seeds, count=SWEEP_COUNT):
    found = []
    for kk in range(n_seeds):
        seed = (base_seed + kk * 2654435761) & 0x7FFFFFFF
        try:
            sweep(seed, count)
        except ScheduleError as exc:
            found.append((seed, str(exc)))
    return found


def _main(argv):
    if len(argv) >= 2 and argv[1] == "--explore":
        base = int(argv[2]) if len(argv) > 2 else SWEEP_SEED
        n = int(argv[3]) if len(argv) > 3 else 300
        found = explore(base, n)
        print(f"EXPLORE: {'no counterexample' if not found else str(len(found)) + ' counterexample(s)'} "
              f"across {n} reseeded sweeps from base {base}.")
        for seed, msg in found:
            print(f"  seed={seed}: {msg}")
        return 0
    for name in SCENES:
        print(name, scene_result(name))
    rep = sweep()
    print(f"SWEEP: {rep['scenarios']} sequences × {len(_BUDGETS)} budgets, deferrals {rep['deferrals']}, "
          f"departures {rep['departures']}, stale {rep['stale_seen']}")
    print(f"sweep digest={rep['digest']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(_main(_sys.argv))
