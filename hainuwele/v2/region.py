# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""region (URDR2RG1) — R1 of the v2 ladder: the unbounded world in exact integers.

THE CLAIM THIS RUNG DECIDES: "fixed-point runs out of range on a large map, and origin
shifting inherently breaks exact arithmetic." The decision is arithmetic, not argument. A
position is (region index, local offset): region indices are plain i64 pairs, local offsets
are Q32.32 within a region of REGION_UNITS world units. An integer translation is exact, so
re-homing a position to a neighbouring region changes no represented value — normalize() is
a carry, not a rounding. And the LAW OF PRODUCTS: absolute coordinates never enter
arithmetic — only DELTAS do, and the delta door refuses one past its derived bound, so every
downstream product is bounded by the INTEREST RADIUS rather than by where in the world the
scene happens to sit. The world's extent then costs nothing: translating a scene by
half-a-galaxy of regions is digest-identical to rendering it at the origin, demonstrated
over a seeded sweep rather than asserted.

does_not_show: streaming or persistence at scale (R4's question); that any renderer consumes
these deltas yet (this is the coordinate substrate, proven translation-invariant before a
renderer is built on it — the v1 demo's delta-form camera is the existence proof that the
consumption side works); that region HANDOFF of moving authority is solved here (the v1 tree's
migrate/mesh laws own that seam and are cited, not reproven).

falsifier: every law here ships with a plant verify2.py runs red-first — a leaked absolute
coordinate breaks the translation sweep, a wrapped delta is refused not returned, a float
coordinate refuses at the door, and the boundary refusal fires exactly one past the derived
bound (voxin's law: a refusal one short means the enforced bound is not the derived one).
"""
import hashlib

FRAC = 32
ONE = 1 << FRAC                      # Q32.32
REGION_UNITS = 1 << 16               # world units per region side (65536 u)
REGION_Q = REGION_UNITS << FRAC      # region size in Q32.32
#: DECLARED — the interest radius bound on deltas, in world units. Every product downstream
#: of the door is bounded by this, never by absolute position. 2^20 units of reach is three
#: orders past the v1 demo's draw window; the door refuses one past it.
DELTA_MAX_UNITS = 1 << 20
DELTA_MAX_Q = DELTA_MAX_UNITS << FRAC


class Region2Error(Exception):
    def __init__(self, message):
        super().__init__(f"V2REGION-REFUSE: {message}")
        self.code = "V2REGION-REFUSE"


def make_pos(rx, ry, lx, ly):
    """A position: integer region indices and Q32.32 locals in [0, REGION_Q)."""
    for v in (rx, ry, lx, ly):
        if not isinstance(v, int):
            raise Region2Error(f"a {type(v).__name__} coordinate refuses — exact means integer")
    return normalize((rx, ry, lx, ly))


def normalize(pos):
    """Carry local overflow into the region index. A carry is EXACT: the represented point
    (rx * REGION_Q + lx) is identical before and after, by construction."""
    rx, ry, lx, ly = pos
    rx += lx // REGION_Q
    lx %= REGION_Q
    ry += ly // REGION_Q
    ly %= REGION_Q
    return (rx, ry, lx, ly)


def absolute_q(pos):
    """The represented absolute point, as unbounded Python ints — the ORACLE for the laws
    below, never an implementation datum (nothing downstream may consume this)."""
    rx, ry, lx, ly = pos
    return (rx * REGION_Q + lx, ry * REGION_Q + ly)


def translate(pos, drx, dry, dlx_q=0, dly_q=0):
    """Exact translation by whole regions plus an optional Q32.32 remainder."""
    rx, ry, lx, ly = pos
    return normalize((rx + drx, ry + dry, lx + dlx_q, ly + dly_q))


def delta_q(a, b):
    """THE ONLY DOOR ARITHMETIC MAY USE: b - a as Q32.32 i64-range deltas, refused past the
    derived interest bound. Absolute position dies here; everything downstream is bounded."""
    (arx, ary, alx, aly) = a
    (brx, bry, blx, bly) = b
    dx = (brx - arx) * REGION_Q + (blx - alx)
    dy = (bry - ary) * REGION_Q + (bly - aly)
    if abs(dx) > DELTA_MAX_Q or abs(dy) > DELTA_MAX_Q:
        raise Region2Error(
            f"delta exceeds the interest bound ({DELTA_MAX_UNITS} u) — a scene this wide is "
            f"not one scene, and admitting it would let absolute scale back into a product")
    return (dx, dy)


# ---- the derived envelope (the concern's arithmetic, printed rather than feared) ---------------
def envelope():
    """Every number here is DERIVED from the representation, not estimated. Units are world
    units; the metre reading assumes one unit is one metre, stated so the assumption travels
    with the number."""
    i64 = (1 << 63) - 1
    # v1 demo today: cam.px is Q8 in i64, and (wx*TILE)<<8 must not wrap
    v1_units = i64 >> 8
    # v2: region indices are i64; the reachable span is regions times region size
    v2_units = i64 * REGION_UNITS
    return {
        "delta_bound_units": DELTA_MAX_UNITS,
        "region_units": REGION_UNITS,
        "v1_absolute_ceiling_units": v1_units,
        "v1_absolute_ceiling_km_at_1m": v1_units // 1000,
        "v2_reachable_units": v2_units,
        "v2_over_v1_factor": v2_units // v1_units,
        "gta_v_map_km_for_scale": 81,
    }


# ---- the laws -----------------------------------------------------------------------------------
def _digest_scene(cam, points):
    """Render-substitute: the sorted delta set, digested. Any consumer (raster, physics,
    perception) sees the world only through delta_q, so this digest standing still under
    translation is exactly the property a renderer inherits."""
    ds = sorted(delta_q(cam, p) for p in points)
    return hashlib.sha256(repr(ds).encode()).hexdigest()


def _lcg(seed):
    s = seed & 0xFFFFFFFFFFFFFFFF
    while True:
        s = (s * 6364136223846793005 + 1442695040888963407) & 0xFFFFFFFFFFFFFFFF
        yield s


def translation_invariance(seed=1958, scenes=25, points=40):
    """A scene translated by up to half-a-galaxy of regions renders digest-identical to the
    same scene at the origin — over a seeded sweep of scenes and offsets, not one fixture."""
    rng = _lcg(seed)
    for _ in range(scenes):
        cam = make_pos(0, 0, next(rng) % REGION_Q, next(rng) % REGION_Q)
        pts = []
        for _ in range(points):
            ox = (next(rng) % (2 * DELTA_MAX_Q)) - DELTA_MAX_Q
            oy = (next(rng) % (2 * DELTA_MAX_Q)) - DELTA_MAX_Q
            pts.append(translate(cam, 0, 0, ox, oy))
        base = _digest_scene(cam, pts)
        drx = (next(rng) % (1 << 55)) - (1 << 54)
        dry = (next(rng) % (1 << 55)) - (1 << 54)
        moved_cam = translate(cam, drx, dry)
        moved_pts = [translate(p, drx, dry) for p in pts]
        if _digest_scene(moved_cam, moved_pts) != base:
            return False
    return True


def seam_walk_equality(seed=420, steps=400):
    """A walk that crosses region seams yields the SAME per-step deltas as the identical walk
    tracked in monolith (unbounded absolute) coordinates — the mesh==monolith law, at the
    coordinate layer."""
    rng = _lcg(seed)
    pos = make_pos(0, 0, REGION_Q - (200 << FRAC), REGION_Q - (200 << FRAC))
    abs_x, abs_y = absolute_q(pos)
    crossed = 0
    for _ in range(steps):
        sx = (next(rng) % (3 << FRAC)) - (1 << FRAC)
        sy = (next(rng) % (3 << FRAC)) - (1 << FRAC)
        old_region = (pos[0], pos[1])
        new_pos = translate(pos, 0, 0, sx, sy)
        if (new_pos[0], new_pos[1]) != old_region:
            crossed += 1
        nax, nay = abs_x + sx, abs_y + sy
        got = delta_q(pos, new_pos)
        if got != (nax - abs_x, nay - abs_y):
            return (False, crossed)
        if absolute_q(new_pos) != (nax, nay):
            return (False, crossed)
        pos, abs_x, abs_y = new_pos, nax, nay
    return (crossed > 0, crossed)     # a sweep that never crossed a seam proved nothing


def boundary_refusal():
    """DELTA_MAX admits; one past refuses — the enforced bound IS the derived one."""
    cam = make_pos(0, 0, 0, 0)
    at = translate(cam, 0, 0, DELTA_MAX_Q, 0)
    try:
        delta_q(cam, at)
    except Region2Error:
        return False                  # refused AT the bound: one short — voxin's law violated
    past = translate(cam, 0, 0, DELTA_MAX_Q + 1, 0)
    try:
        delta_q(cam, past)
    except Region2Error:
        return True
    return False


def carry_exactness(seed=77, trials=500):
    """normalize is a carry, not a rounding: the represented absolute point never moves."""
    rng = _lcg(seed)
    for _ in range(trials):
        raw = ((next(rng) % (1 << 40)) - (1 << 39), (next(rng) % (1 << 40)) - (1 << 39),
               (next(rng) % (1 << 62)) - (1 << 61), (next(rng) % (1 << 62)) - (1 << 61))
        rx, ry, lx, ly = raw
        want = (rx * REGION_Q + lx, ry * REGION_Q + ly)
        if absolute_q(normalize(raw)) != want:
            return False
        n = normalize(raw)
        if not (0 <= n[2] < REGION_Q and 0 <= n[3] < REGION_Q):
            return False
    return True


# ---- the plants (verify2 runs each red-first) ---------------------------------------------------
def a_float_coordinate_refuses():
    try:
        make_pos(0, 0, 1.5, 0)
    except Region2Error:
        return True
    return False


def an_absolute_leak_breaks_the_sweep():
    """The defect the sweep exists to catch: a consumer that folds ABSOLUTE position into its
    output is translation-VARIANT. Plant it and the invariance property must fail."""
    cam = make_pos(0, 0, 5 << FRAC, 5 << FRAC)
    pts = [translate(cam, 0, 0, 3 << FRAC, 4 << FRAC)]

    def leaky_digest(c, ps):
        ds = sorted(delta_q(c, p) for p in ps)
        return hashlib.sha256((repr(ds) + repr(c[0])).encode()).hexdigest()  # the leak: c[0]

    base = leaky_digest(cam, pts)
    moved = leaky_digest(translate(cam, 1000, 0), [translate(p, 1000, 0) for p in pts])
    return base != moved


def a_wrapped_delta_is_refused_not_returned():
    """Two positions farther apart than the bound: the door must REFUSE — returning any i64
    number here would be renderbound's silent-wrap defect at the world layer."""
    a = make_pos(0, 0, 0, 0)
    b = make_pos(1 << 30, 0, 0, 0)
    try:
        delta_q(a, b)
    except Region2Error:
        return True
    return False
