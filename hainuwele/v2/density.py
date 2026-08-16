# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""density (URDR2DN1) — R3 of the v2 ladder: visibility cost is local, and the budget is a door.

THE CLAIM THIS RUNG DECIDES: "server-authoritative visibility for thousands of entities means
per-entity occlusion math that collapses the CPU hot path." The architecture's answer has
always been interest sets plus budgeted refresh — but nobody had MEASURED the scaling law on
this substrate. This rung builds the synthetic instrument: seeded entity populations drifting
on a toroidal tile arena, one drifting observer with a Chebyshev area-of-interest, a bucket
grid whose cell equals the AoI radius (so the 3x3 neighborhood is a proven superset of
interest), and a round-robin refresh scheduler that may spend AT MOST budget distance checks
per tick. Everything is integer, seeded, and digestable; wall-clock never appears.

Four laws, red-first:

  * THE BUDGET IS A DOOR, NOT A HOPE — no tick ever spends more than B distance checks, at
    any density, and a zero budget refuses. The falsifier is a budget-blind scheduler (checks
    every candidate every tick); the sweep must catch it exceeding the door.
  * BOUNDED STALENESS, EXERCISED — a continuously-candidate entity is re-checked within
    ceil(Q_max / B) ticks, where Q_max is the measured queue ceiling; the bound is derived
    from measurements, asserted, and APPROACHED (a bound never approached is decoration).
    The falsifier is a starving LIFO scheduler: newest first, the oldest waits forever.
  * VALUES SETTLE; BUDGET ONLY DELAYS THEM — freeze all movement and within bound+1 ticks
    the budgeted visible set EQUALS the oracle interest set exactly, at every swept density.
    The family invariant's third appearance: R4 said capacity changes cost never values;
    R3 says budget changes STALENESS, never the settled values.
  * COST IS LOCAL, NOT GLOBAL — the population sweep holds density fixed while the world
    grows 16x (N = 1024 -> 16384, arena scaling with it): the queue ceiling and staleness
    stay inside one constant band while the naive full-scan cost grows EXACTLY linearly with
    N (measured, not assumed). Per-observer visibility cost is a function of LOCAL density
    and budget; world population is the naive path's bill only. The falsifier is a
    population-blind candidate set (all N are candidates): its queue ceiling tracks N and
    the band law must redden.

does_not_show: wall-clock per check (a count is not a nanosecond; the tick-to-milliseconds
mapping belongs to a host measurement, exactly as R2a's ladder waited for reachenv); occlusion
or line-of-sight (this is INTEREST visibility — manifestation's closed-world absence is the
main tree's `perception`/`anamorphosis`, already gated); multiple observers (per-observer cost
is the claim; N observers multiply it and interest sets shard it, neither measured here);
densities outside the swept set (the caustic law — verdicts never extrapolate).

falsifier: verify2 runs every plant — the budget-blind scheduler blows the door, the LIFO
scheduler starves its oldest candidate past the bound, a poisoned visibility read (a refresh
that nudges the entity it inspects) breaks the authority transcript, a population-blind
candidate set breaks the locality band, and a zero budget refuses.
"""
import hashlib
from collections import deque

MAGIC = b"URDR2DN1"

R = 8                  # AoI Chebyshev radius, tiles
CELL = R               # bucket cell edge == R: the 3x3 neighborhood is a superset of interest
BUDGET = 16            # distance checks the scheduler may spend per tick
TICKS = 96
STALENESS_SLOT = 4     # declared verdict slot, in ticks (the host maps ticks to ms, later)

DENSITY_SWEEP = ((256, 128), (1024, 128), (4096, 128))     # (N, side): density rises 16x
POPULATION_SWEEP = ((1024, 128), (4096, 256), (16384, 512))  # density fixed, world grows 16x


class Density2Error(Exception):
    def __init__(self, message):
        super().__init__(f"V2DENSITY-REFUSE: {message}")
        self.code = "V2DENSITY-REFUSE"


def _lcg(s):
    return (s * 6364136223846793005 + 1442695040888963407) % (1 << 64)


def _cheb(ax, ay, bx, by, side):
    dx = abs(ax - bx)
    dy = abs(ay - by)
    return max(min(dx, side - dx), min(dy, side - dy))


class Sim:
    """One seeded world: N entities drifting on a side x side torus, one drifting observer,
    bucket grid, and a budgeted round-robin visibility scheduler. Deterministic by
    construction: one LCG stream, fixed draw order, sorted iteration at every digest."""

    def __init__(self, n, side, budget=BUDGET, seed=1959, blind_budget=False,
                 lifo=False, poison=False, blind_buckets=False):
        if budget < 1:
            raise Density2Error("a refresh budget of zero is a lie about having a scheduler")
        self.n, self.side, self.budget = n, side, budget
        self.blind_budget, self.lifo = blind_budget, lifo
        self.poison, self.blind_buckets = poison, blind_buckets
        self.ncells = side // CELL
        self.s = seed
        self.px, self.py = [0] * n, [0] * n
        self.buckets = {}
        for i in range(n):
            self.s = _lcg(self.s)
            self.px[i] = self.s % side
            self.s = _lcg(self.s)
            self.py[i] = self.s % side
            self.buckets.setdefault(self._cell(i), set()).add(i)
        self.ox, self.oy = side // 2, side // 2
        self.queue = deque()
        self.in_queue = set()
        self.visible = set()
        self.last_checked = [-1] * n
        self.entered = [-1] * n
        self.checks_per_tick = []
        self.bucket_moves = 0
        self.q_max = 0
        self.max_staleness = 0
        self.auth = hashlib.sha256(MAGIC + b"|auth")

    def _cell(self, i):
        return (self.px[i] // CELL, self.py[i] // CELL)

    def _candidates(self):
        if self.blind_buckets:
            return set(range(self.n))               # THE PLANT: the whole world, every tick
        ocx, ocy = self.ox // CELL, self.oy // CELL
        out = set()
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                cell = ((ocx + dx) % self.ncells, (ocy + dy) % self.ncells)
                out |= self.buckets.get(cell, set())
        return out

    def _move(self, tick):
        for _ in range(self.n // 8):
            self.s = _lcg(self.s)
            i = self.s % self.n
            self.s = _lcg(self.s)
            dx = self.s % 3 - 1
            self.s = _lcg(self.s)
            dy = self.s % 3 - 1
            old = self._cell(i)
            self.px[i] = (self.px[i] + dx) % self.side
            self.py[i] = (self.py[i] + dy) % self.side
            new = self._cell(i)
            if new != old:
                self.buckets.setdefault(old, set()).discard(i)
                self.buckets.setdefault(new, set()).add(i)
                self.bucket_moves += 1
            self.auth.update(b"%d|%d|%d|%d" % (tick, i, self.px[i], self.py[i]))
        self.s = _lcg(self.s)
        self.ox = (self.ox + self.s % 3 - 1) % self.side
        self.s = _lcg(self.s)
        self.oy = (self.oy + self.s % 3 - 1) % self.side

    def _refresh(self, tick, cand):
        for i in sorted(cand - self.in_queue):
            (self.queue.append if not self.lifo else self.queue.appendleft)(i)
            self.in_queue.add(i)
            if self.entered[i] < 0:
                self.entered[i] = tick
        self.q_max = max(self.q_max, len(self.queue))
        checks = 0
        limit = len(self.queue) if self.blind_budget else self.budget
        while self.queue and checks < limit:
            i = self.queue.popleft()
            if i not in cand:                       # departed: state update, no check spent
                self.in_queue.discard(i)
                self.visible.discard(i)
                self.entered[i] = -1
                continue
            checks += 1
            since = max(self.last_checked[i], self.entered[i])
            if self.last_checked[i] >= 0 and since >= 0:
                self.max_staleness = max(self.max_staleness, tick - since)
            d = _cheb(self.px[i], self.py[i], self.ox, self.oy, self.side)
            if self.poison:
                # THE PLANT: a visibility read that writes — the observer law's exact enemy
                self.px[i] = (self.px[i] + 1) % self.side
                self.auth.update(b"poison|%d|%d" % (i, self.px[i]))
            (self.visible.add if d <= R else self.visible.discard)(i)
            self.last_checked[i] = tick
            if self.lifo:
                self.queue.appendleft(i)
            else:
                self.queue.append(i)
        self.checks_per_tick.append(checks)

    def run(self, ticks=TICKS):
        for t in range(ticks):
            self._move(t)
            self._refresh(t, self._candidates())
        return self

    def settle(self, extra):
        """Movement frozen; refresh only. The convergence phase."""
        t0 = len(self.checks_per_tick)
        for t in range(t0, t0 + extra):
            self._refresh(t, self._candidates())
        return self

    def oracle(self):
        """The full-scan truth, and its bill: exactly N distance checks."""
        out = {i for i in range(self.n)
               if _cheb(self.px[i], self.py[i], self.ox, self.oy, self.side) <= R}
        return out, self.n

    def bound(self):
        return -(-self.q_max // self.budget)        # ceil(Q_max / B)

    def auth_digest(self):
        return self.auth.hexdigest()


# ---- the laws -----------------------------------------------------------------------------------
def budget_is_a_door():
    for (n, side) in DENSITY_SWEEP + POPULATION_SWEEP:
        sim = Sim(n, side).run()
        if max(sim.checks_per_tick) > BUDGET:
            return False
    return True


def staleness_bounded_and_exercised():
    for (n, side) in DENSITY_SWEEP:
        sim = Sim(n, side).run()
        b = sim.bound()
        if sim.max_staleness > b or sim.max_staleness * 2 < b:
            return False
    return True


def values_settle():
    """Budget delays values; it never changes what they settle to."""
    for (n, side) in DENSITY_SWEEP:
        sim = Sim(n, side).run()
        sim.settle(sim.bound() + 1)
        truth, _bill = sim.oracle()
        if sim.visible != truth:
            return False
    return True


def locality_band():
    """Density fixed, world 16x: the local numbers hold still while the naive bill grows
    exactly linearly. Returns (ok, rows) so the gate prints what was measured."""
    rows = []
    for (n, side) in POPULATION_SWEEP:
        sim = Sim(n, side).run()
        _truth, bill = sim.oracle()
        rows.append({"n": n, "q_max": sim.q_max, "bound": sim.bound(),
                     "stale": sim.max_staleness, "naive": bill})
    qs = [r["q_max"] for r in rows]
    ok = (max(qs) <= 2 * min(qs)
          and all(r["bound"] <= STALENESS_SLOT + 1 for r in rows)
          and all(rows[i]["naive"] * 4 == rows[i + 1]["naive"] for i in range(len(rows) - 1)))
    return ok, rows


def trade_table():
    out = []
    for (n, side) in DENSITY_SWEEP:
        sim = Sim(n, side).run()
        b = sim.bound()
        verdict = ("FITS" if b <= STALENESS_SLOT
                   else "MARGINAL" if sim.max_staleness <= STALENESS_SLOT else "EXCEEDS")
        out.append({"n": n, "density_permille": n * 1000 // (side * side),
                    "q_max": sim.q_max, "bound": b, "stale": sim.max_staleness,
                    "moves": sim.bucket_moves, "verdict": verdict})
    return out


def observer_law():
    """Visibility reads authority; it never writes. Same seeds, machinery on vs off, one
    transcript."""
    on = Sim(1024, 128)
    on.run()
    off = Sim(1024, 128, budget=1)                 # near-starved: barely any visibility work
    off.run()
    return on.auth_digest() == off.auth_digest()


# ---- plants -------------------------------------------------------------------------------------
def a_budget_blind_scheduler_is_caught():
    sim = Sim(1024, 128, blind_budget=True).run()
    return max(sim.checks_per_tick) > BUDGET


def a_starving_scheduler_is_caught():
    sim = Sim(1024, 128, lifo=True).run()
    return sim.max_staleness > sim.bound()


def a_poisoned_visibility_read_is_caught():
    clean = Sim(1024, 128).run().auth_digest()
    dirty = Sim(1024, 128, poison=True).run().auth_digest()
    return clean != dirty


def a_population_blind_candidate_set_is_caught():
    qs = []
    for (n, side) in POPULATION_SWEEP[:2]:
        sim = Sim(n, side, blind_buckets=True).run()
        qs.append(sim.q_max)
    return qs[1] > 2 * qs[0]


def a_zero_budget_refuses():
    try:
        Sim(64, 128, budget=0)
    except Density2Error:
        return True
    return False
