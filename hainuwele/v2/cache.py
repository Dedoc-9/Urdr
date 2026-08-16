# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""cache (URDR2CH1) — R4 of the v2 ladder: eviction may not change answers.

THE CLAIM THIS RUNG DECIDES: "a zero-allocation architecture cannot stream an open world."
The v1.9 demo made the question concrete: its resident grids are bounded by the ladder, but
the backing height cache grows without limit — seventy thousand entries on one committed walk
at mid reach, more forever after. The cure is a bounded cache with deterministic eviction,
and the law that makes it safe is the tree's cardinal invariant wearing a memory costume:
A CACHE OVER A PURE FUNCTION IS A VIEW, AND EVICTION IS A VIEW EVENT. Starve it, thrash it,
shrink it to nothing — the VALUES may never move, because a digest that shifts under memory
pressure is an authority leak wearing a performance costume.

Three laws, red-first:

  * REPLAY IDENTITY UNDER PRESSURE — one seeded access pattern (a drifting walk, the demo's
    shape) evaluated under capacities from starvation to unbounded produces IDENTICAL value
    sequences, compared by digest. The falsifier is a POISONED eviction (a victim's slot
    corrupts a neighbour on the way out) — the sweep must catch it.
  * DETERMINISTIC VICTIMS — the evicted entry is chosen by insertion-order clock, never by
    map iteration order, so two runs evict identically. The falsifier seeds a shuffled victim
    picker and the cross-capacity digest law must redden.
  * THE CAP TRADE TABLE — capacity against hit rate and recompute count, derived on the
    drift pattern, so the demo's R4 adoption picks its budget from a measured surface the
    way the reach default was picked, not from a feeling.

does_not_show: the demo's real hit rates (the drift pattern is synthetic; the adoption rung
replays the committed walk and measures its own); wall-clock cost of eviction (a count is not
a millisecond); anything about persistence or streaming from disk (this world derives from
seeds — the cache IS the storage tier, which is the point the critique missed).

falsifier: verify2 runs every plant — poisoned eviction caught by the identity sweep, a
shuffled victim picker caught by the cross-run digest, a cap of one still answers correctly
(the degenerate control: pure recompute), and the bound is asserted TIGHT (occupancy reaches
the cap and never passes it).
"""
import hashlib

MAGIC = b"URDR2CH1"


class Cache2Error(Exception):
    def __init__(self, message):
        super().__init__(f"V2CACHE-REFUSE: {message}")
        self.code = "V2CACHE-REFUSE"


def derive(key, seed=1958):
    """The pure backing function — a stand-in for the canon noise, deterministic and cheap
    enough to sweep. The cache may only ever memoize THIS; anything else it returns is a
    corruption by definition."""
    x, y = key
    h = hashlib.sha256(b"%s|%d|%d|%d" % (MAGIC, seed, x, y)).digest()
    return int.from_bytes(h[:4], "big")


class BoundedCache:
    """Insertion-order clock eviction over a fixed capacity. Deterministic by construction:
    the victim is the oldest slot by arrival, tracked in an explicit ring — never by map
    iteration order, which Python randomizes across runs unless the seed is pinned and Rust
    randomizes always."""

    def __init__(self, cap, fn=derive, poison=False, shuffled=None):
        if cap < 1:
            raise Cache2Error("a cache of capacity zero is a lie about having a cache")
        self.cap = cap
        self.fn = fn
        self.map = {}
        self.ring = []                 # insertion order; index 0 is the clock hand's victim
        self.hits = 0
        self.misses = 0
        self.evictions = 0
        self.high_water = 0
        self.victims = []              # the eviction ORDER — determinism's witness
        self._poison = poison
        self._shuffled = shuffled      # seeded LCG state for the defect picker, or None

    def _victim_index(self):
        if self._shuffled is not None:
            self._shuffled = (self._shuffled * 6364136223846793005
                              + 1442695040888963407) % (1 << 64)
            return self._shuffled % len(self.ring)
        return 0

    def get(self, key):
        if key in self.map:
            self.hits += 1
            return self.map[key]
        self.misses += 1
        v = self.fn(key)
        if len(self.map) >= self.cap:
            vi = self._victim_index()
            victim = self.ring.pop(vi)
            del self.map[victim]
            self.victims.append(victim)
            self.evictions += 1
            if self._poison and self.ring:
                # THE PLANT: corrupt a surviving neighbour on the way out — the exact shape
                # of an eviction bug (an index off by one into a compacted store)
                survivor = self.ring[0]
                self.map[survivor] = (self.map[survivor] + 1) & 0xFFFFFFFF
        self.map[key] = v
        self.ring.append(key)
        self.high_water = max(self.high_water, len(self.map))
        return v


def drift_pattern(steps=8000, seed=77):
    """A drifting walk over a tile lattice — revisits recent tiles heavily, abandons old
    ones, the demo's access shape. Seeded LCG, no wall clock, no hash order."""
    s = seed
    x, y = 0, 0
    out = []
    for i in range(steps):
        s = (s * 6364136223846793005 + 1442695040888963407) % (1 << 64)
        if s % 4 == 0:
            x += 1 if (s >> 8) % 2 == 0 else -1
        if s % 4 == 1:
            y += 1 if (s >> 9) % 2 == 0 else -1
        dx = (s >> 16) % 9 - 4
        dy = (s >> 24) % 9 - 4
        out.append((x + dx, y + dy))
    return out


def value_digest(cap, poison=False, shuffled=None, pattern=None):
    c = BoundedCache(cap, poison=poison, shuffled=shuffled)
    vals = [c.get(k) for k in (pattern or drift_pattern())]
    body = ",".join(str(v) for v in vals)
    return hashlib.sha256(MAGIC + b"|" + body.encode()).hexdigest(), c


CAPS = (1, 8, 64, 512, 10**9)


def identity_under_pressure():
    """The law: capacity changes COST, never VALUES."""
    digs = [value_digest(cap)[0] for cap in CAPS]
    return len(set(digs)) == 1


def bounds_are_tight():
    """Caps under the pattern's working set must FILL and EVICT (or the sweep proved
    nothing); a cap above it must settle at EXACTLY the working set with zero evictions —
    and no cap is ever exceeded. Both regimes asserted, because a law tested on one side of
    its own boundary is half a law."""
    ws = working_set()
    for cap in (8, 64):
        _d, c = value_digest(cap)
        if not (cap < ws and c.high_water == cap and c.evictions > 0):
            return False
    _d, c = value_digest(512)
    return 512 > ws and c.high_water == ws and c.evictions == 0


def working_set():
    _d, c = value_digest(10**9)
    return c.misses


def trade_table():
    out = []
    for cap in CAPS:
        _d, c = value_digest(cap)
        total = c.hits + c.misses
        out.append({"cap": cap, "hit_permille": c.hits * 1000 // total,
                    "recomputes": c.misses, "evictions": c.evictions})
    return out


# ---- plants -------------------------------------------------------------------------------------
def a_poisoned_eviction_is_caught():
    clean = value_digest(64)[0]
    dirty = value_digest(64, poison=True)[0]
    return clean != dirty


def _victim_digest(c):
    body = ";".join(f"{x},{y}" for (x, y) in c.victims)
    return hashlib.sha256(MAGIC + b"|victims|" + body.encode()).hexdigest()


def a_shuffled_victim_is_caught():
    """A nondeterministic-victim DEFECT still returns correct VALUES (the map never lies), so
    the identity law alone cannot see it. The determinism witness is the EVICTION ORDER: two
    clean runs produce one identical victim trace; two shuffled runs diverge in it. Both
    halves asserted — a witness that never agrees is as useless as one that never differs."""
    clean1 = _victim_digest(value_digest(64)[1])
    clean2 = _victim_digest(value_digest(64)[1])
    bad1 = _victim_digest(value_digest(64, shuffled=1)[1])
    bad2 = _victim_digest(value_digest(64, shuffled=2)[1])
    return clean1 == clean2 and bad1 != bad2


def a_cap_of_one_still_answers():
    """The degenerate control: pure recompute, values still exact."""
    return value_digest(1)[0] == value_digest(10**9)[0]


def a_zero_cap_refuses():
    try:
        BoundedCache(0)
    except Cache2Error:
        return True
    return False
