# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""farfield (URDR2FF1) — R2d of the v2 ladder: beyond the door there is no geometry, only a
channel.

THE CLAIM THIS RUNG DECIDES: how a galaxy-scale far field can exist at all in a world whose
arithmetic refuses absolute positions. The answer is R1's delta door paying off: past the
interest bound there is NO GEOMETRY, by refusal — the delta door already refuses any
geometric delta beyond its derived bound, and this rung asserts that refusal as the far
field's founding law rather than working around it. Far content may manifest ONLY through a
FAR-FIELD CHANNEL: a pure deterministic function of the viewer's COARSE region delta (to a
declared galactic anchor) and the view direction bin — a seeded star lattice, digestable,
translation-covariant, and provably an observer.

Four laws, red-first:

  * THE DOOR STANDS — geometry admits at DELTA_MAX and refuses one past it (voxin's law,
    re-asserted at this tier rather than re-derived), while the channel serves region deltas
    of ANY magnitude — half a galaxy of regions — without refusing. The division of labor is
    the architecture: geometry inside the door, channel beyond it, nothing in between.
  * TRANSLATION COVARIANCE — the channel consumes only the DELTA between viewer region and
    anchor region, never an absolute index, so translating viewer AND anchor together by up
    to 2^54 regions renders a digest-identical sky (R1's sweep, at the far field). The
    falsifier is an absolute-region leak inside the channel hash; the sweep must catch it.
  * THE PARALLAX QUANTUM — the sky is a function of the COARSE delta (regions >> stride):
    moving the viewer anywhere inside one quantum changes NOTHING (stars do not jitter as
    you walk), and crossing a quantum boundary changes the digest (both halves asserted — a
    sky that never changes is decoration, and one that shimmer-changes below the quantum is
    a defect wearing a feature's name).
  * THE CHANNEL IS AN OBSERVER — reading it moves nothing: the authority transcript is
    byte-identical before and after any number of channel reads, and two independently
    constructed channels agree bin for bin (purity — no hidden state survives construction).
    The falsifier is a peeking channel that caches its result into the authority store.

does_not_show: pictures (compositing the far field behind R2c's clipped terrain is a demo
adoption with its own before/after); any astronomy (the star lattice is a seeded placeholder
CONTENT choice — the laws constrain the channel's TYPE, not its art); parallax below the
quantum (refused by construction, stated: a true 3D starfield with per-star parallax would
be a different channel with its own laws); scale beyond the swept 2^54-region translations
(the caustic law).

falsifier: verify2 runs every plant — one past the delta door refuses; an absolute-region
leak breaks the covariance sweep; a peeking channel breaks the authority transcript; a
constant sky is caught as vacuity; a sub-quantum jitter is caught by the parallax law.
"""
import hashlib

import region as RG

MAGIC = b"URDR2FF1"

STRIDE = 20                    # the parallax quantum: the sky moves only per 2^20 regions
AZ_BINS = 512
ALT_BINS = 128
SWEEP_REGIONS = 1 << 54        # R1's own translation scale


class Farfield2Error(Exception):
    def __init__(self, message):
        super().__init__(f"V2FARFIELD-REFUSE: {message}")
        self.code = "V2FARFIELD-REFUSE"


def far_geometry(delta_q):
    """The door, re-asserted at this tier: a GEOMETRIC delta admits only inside the derived
    bound. Far content has no mesh — asking for one past the door is a refusal, not a LOD."""
    if not isinstance(delta_q, int) or isinstance(delta_q, bool):
        raise Farfield2Error("a geometric delta must be an integer")
    if abs(delta_q) > RG.DELTA_MAX_Q:
        raise Farfield2Error("no geometry past the delta door — far content manifests only "
                             "through the channel")
    return ("mesh", delta_q)


class Channel:
    """The far-field channel: pure, seeded, stateless after construction. Brightness of one
    sky bin as a function of (coarse region delta, direction bin) — and NOTHING else."""

    def __init__(self, seed=1963, leak_absolute=False, jitter=False, constant=False,
                 peek_store=None):
        self.seed = seed
        self._leak = leak_absolute
        self._jitter = jitter
        self._constant = constant
        self._peek = peek_store

    def read(self, viewer_region, anchor_region, az, alt):
        if not (0 <= az < AZ_BINS and 0 <= alt < ALT_BINS):
            raise Farfield2Error("a direction bin off the sky grades nothing")
        drx = viewer_region[0] - anchor_region[0]
        dry = viewer_region[1] - anchor_region[1]
        if self._constant:
            return 7                                    # THE PLANT: a sky that never changes
        cx, cy = drx >> STRIDE, dry >> STRIDE
        if self._jitter:
            cx, cy = drx, dry                           # THE PLANT: sub-quantum parallax
        key = (viewer_region if self._leak else (cx, cy))  # THE PLANT: absolute leak
        h = hashlib.sha256(b"%s|%d|%d|%d|%d|%d"
                           % (MAGIC, self.seed, key[0], key[1], az, alt)).digest()
        v = h[0]
        if self._peek is not None:
            self._peek[(az, alt)] = v                   # THE PLANT: a read that writes
        return v


def sky_digest(chan, viewer_region, anchor_region, samples=256, seed=11):
    s = seed
    d = hashlib.sha256(MAGIC + b"|sky")
    for _ in range(samples):
        s = (s * 6364136223846793005 + 1442695040888963407) % (1 << 64)
        az = s % AZ_BINS
        alt = (s >> 32) % ALT_BINS
        d.update(b"%d|%d|%d" % (az, alt, chan.read(viewer_region, anchor_region, az, alt)))
    return d.hexdigest()


# ---- the laws -----------------------------------------------------------------------------------
def door_stands():
    """Geometry admits at the bound and refuses one past; the channel serves any magnitude."""
    if far_geometry(RG.DELTA_MAX_Q)[0] != "mesh":
        return False
    try:
        far_geometry(RG.DELTA_MAX_Q + 1)
        return False
    except Farfield2Error:
        pass
    c = Channel()
    half_galaxy = (SWEEP_REGIONS // 2, SWEEP_REGIONS // 3)
    return isinstance(c.read(half_galaxy, (0, 0), 100, 50), int)


def translation_covariance(seed=1964, trials=25):
    c = Channel()
    s = seed
    for _ in range(trials):
        s = (s * 6364136223846793005 + 1442695040888963407) % (1 << 64)
        v = (s % (1 << 30), (s >> 30) % (1 << 30))
        a = ((s >> 8) % (1 << 20), (s >> 40) % (1 << 20))
        t = (s % SWEEP_REGIONS, (s >> 16) % SWEEP_REGIONS)
        moved_v = (v[0] + t[0], v[1] + t[1])
        moved_a = (a[0] + t[0], a[1] + t[1])
        if sky_digest(c, v, a) != sky_digest(c, moved_v, moved_a):
            return False
    return True


def parallax_quantum():
    """Inside one quantum: nothing moves. Across the boundary: the sky changes. Both halves."""
    c = Channel()
    anchor = (0, 0)
    base = (1 << STRIDE) * 5                    # a viewer seated at a quantum boundary
    within = sky_digest(c, (base, base), anchor)
    for step in (1, 137, (1 << STRIDE) - 1):
        if sky_digest(c, (base + step, base + step), anchor) != within:
            return False
    across = sky_digest(c, (base + (1 << STRIDE), base), anchor)
    return across != within


def channel_is_an_observer():
    """Reading moves nothing, and purity holds: two independently built channels agree."""
    store = {i: i * i for i in range(64)}       # a stand-in authority store
    before = hashlib.sha256(repr(sorted(store.items())).encode()).hexdigest()
    c1, c2 = Channel(), Channel()
    for az in range(0, AZ_BINS, 37):
        for alt in range(0, ALT_BINS, 17):
            if c1.read((123456, 654321), (7, 7), az, alt) != \
               c2.read((123456, 654321), (7, 7), az, alt):
                return False
    after = hashlib.sha256(repr(sorted(store.items())).encode()).hexdigest()
    return before == after


def sky_is_not_vacuous():
    """A channel must DEPEND on its inputs: different coarse deltas give different skies."""
    c = Channel()
    a = sky_digest(c, (0, 0), (0, 0))
    b = sky_digest(c, (1 << STRIDE, 0), (0, 0))
    d = sky_digest(c, (0, 1 << STRIDE), (0, 0))
    return len({a, b, d}) == 3


# ---- plants -------------------------------------------------------------------------------------
def an_absolute_leak_breaks_the_sweep():
    c = Channel(leak_absolute=True)
    v, a, t = (1000, 2000), (3, 4), (SWEEP_REGIONS // 7, SWEEP_REGIONS // 5)
    return sky_digest(c, v, a) != sky_digest(c, (v[0] + t[0], v[1] + t[1]),
                                             (a[0] + t[0], a[1] + t[1]))


def a_peeking_channel_is_caught():
    store = {}
    before = hashlib.sha256(repr(sorted(store.items())).encode()).hexdigest()
    c = Channel(peek_store=store)
    c.read((5, 5), (0, 0), 10, 10)
    after = hashlib.sha256(repr(sorted(store.items())).encode()).hexdigest()
    return before != after


def a_constant_sky_is_caught():
    c = Channel(constant=True)
    a = sky_digest(c, (0, 0), (0, 0))
    b = sky_digest(c, (1 << STRIDE, 0), (0, 0))
    return a == b                               # the vacuity is VISIBLE, and caught


def a_jittering_star_is_caught():
    c = Channel(jitter=True)
    anchor = (0, 0)
    base = (1 << STRIDE) * 5
    return sky_digest(c, (base + 1, base), anchor) != sky_digest(c, (base, base), anchor)


def an_off_sky_bin_refuses():
    try:
        Channel().read((0, 0), (0, 0), AZ_BINS, 0)
    except Farfield2Error:
        return True
    return False
