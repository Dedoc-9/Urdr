# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""lod (URDR2LD1) — R2a of the v2 ladder: draw distance as a derived schedule, not a wish.

THE CLAIM THIS RUNG DECIDES: naive draw distance costs O(r^2) primitives and no budget
survives a vista. The cure is octave rings — stride doubling with distance — and on THIS
substrate the cure is unusually honest, because the terrain is DERIVED from layered seeded
noise: a far ring sampling only the coarse layers is not an approximation of the canon
invented by an artist, it is the canon's own octave prefix, and the error of dropping the
fine layers is BOUNDED BY THE AMPLITUDE TABLE — a derivation, not a tuning pass.

Three laws, each with the number derived before it is trusted:

  * THE ERROR BOUND — for a sampling stride s, the world-height error against the full canon
    is bounded by the scaled amplitudes of every layer finer than the stride can carry
    (cell < 2s). The bound is checked against a MEASURED maximum over a seeded sweep, in both
    directions: the measurement may not exceed the bound, and the bound may not be so slack
    the measurement cannot reach a fraction of it (a bound nothing approaches is decoration).
  * THE DERIVED SCHEDULE — a ring of stride s is admissible only past the distance where its
    error bound projects under the declared pixel budget: d_min(s) = e(s) * focal / budget.
    The ladder's inner radii are MAX(octave default, d_min) — the budget writes the schedule.
  * COVERAGE AND COST — the derived rings tile the square annulus out to the ladder's reach
    with at least one coarse tile of overlap at every seam (cracks are covered by paint-behind
    overlap, deterministically, before any stitching cleverness is attempted), and the vertex
    count of a pure octave ring is CONSTANT — so total vertex cost is exactly affine in ring
    count, which is logarithmic in reach. O(r^2) becomes O(log r) by arithmetic the gate
    re-derives on every run.

does_not_show: wall-clock cost (a count is not a millisecond; the host A/B on the committed
walk decides R2b, chord-style, when the demo carries rings); anything about non-terrain
content (structures, entities, impostors are their own rungs); planet curvature or the galaxy
far-field (R2c/R2d, designed in the README, not smuggled in here).

falsifier: verify2 runs each plant red-first — an over-dropped layer exceeds its stride's
bound, a ring seated below its derived d_min violates the pixel budget, a ladder built
without overlap exposes a seam point, and the stride-1 prefix must equal the canon exactly
at sample points (the degenerate control that proves the identity machinery itself).
"""
import os as _os
import sys as _sys

_HERE = _os.path.dirname(_os.path.abspath(__file__))
_ROOT = _os.path.dirname(_os.path.dirname(_HERE))
_sys.path.insert(0, _os.path.join(_ROOT, "tools", "terrain"))

import heightfield as HF                                     # the gated canon, imported not copied

# the shipped demo's world (fpsdemo v1.1+): mountains canon at view scale
SEED = 1958
HS = 420
LAYERS = ((48, 5), (12, 3), (6, 2), (3, 1))
RAWMAX = sum(a for (_c, a) in LAYERS) * HF.VMAX
H_SCALE = 16
TILE = 3                            # world units per tile
FOCAL = 1440                        # the demo's projection at 720p (h * 2)
R0 = 24                             # DECLARED: minimum ring-0 half-width in tiles
PIX_CANDIDATES = (4, 8, 16, 35)     # DECLARED: the budgets the trade surface is derived for —
                                    # 35 is roughly what v1 already accepts at its patch edge


class Lod2Error(Exception):
    def __init__(self, message):
        super().__init__(f"V2LOD-REFUSE: {message}")
        self.code = "V2LOD-REFUSE"


def _floordiv(n, d):
    return n // d


def height_full(x, y, cache):
    raw = 0
    for li, (cell, amp) in enumerate(LAYERS):
        raw += amp * HF.noise16(SEED, li, cell, x, y, cache)
    return _floordiv(_floordiv(raw * HS, RAWMAX), H_SCALE)


def kept_layers(stride):
    """The octave prefix for a stride: layers the stride can still carry (cell >= 2*stride
    keeps sub-stride structure representable; anything finer is dropped and bounded)."""
    kept = tuple((li, c, a) for li, (c, a) in enumerate(LAYERS) if c >= 2 * stride)
    if not kept:
        kept = ((0,) + LAYERS[0],)   # the coarsest layer always survives — a flat far ring
                                     # would erase the silhouette entirely
    return kept


def height_prefix(x, y, stride, cache, kept=None):
    raw = 0
    for (li, cell, amp) in (kept or kept_layers(stride)):
        raw += amp * HF.noise16(SEED, li, cell, x, y, cache)
    return _floordiv(_floordiv(raw * HS, RAWMAX), H_SCALE)


def error_bound_h(stride):
    """DERIVED: dropped raw amplitude, scaled to world height units, plus one for each of the
    two floor divisions the scaling applies."""
    kept_idx = {li for (li, _c, _a) in kept_layers(stride)}
    dropped_raw = sum(a * HF.VMAX for li, (_c, a) in enumerate(LAYERS) if li not in kept_idx)
    return _floordiv(_floordiv(dropped_raw * HS, RAWMAX), H_SCALE) + 2


def measured_error(stride, seed=9, span=64):
    """The MEASURED maximum |full - prefix| over a seeded patch of sample points."""
    cache = {}
    kept = kept_layers(stride)
    worst = 0
    base_x = 100003 * (seed + 1)
    base_y = 70001 * (seed + 3)
    for i in range(span):
        for j in range(span):
            x, y = base_x + i * stride, base_y + j * stride
            e = abs(height_full(x, y, cache) - height_prefix(x, y, stride, cache, kept))
            if e > worst:
                worst = e
    return worst


def d_min_tiles(stride, pix):
    """DERIVED: the nearest tile distance at which this stride's error bound projects at or
    under the pixel budget. e_h world units at distance d tiles: px = e_h*FOCAL/(d*TILE)."""
    e = error_bound_h(stride)
    return -(-e * FOCAL // (pix * TILE))                     # ceil division


def schedule(pix, k_max):
    """The ladder, derived FROM THE BUDGET: ring k's start is the larger of octave doubling
    and its stride's derived d_min, strictly increasing; each ring reaches to the next ring's
    start plus one coarse tile of overlap (paint-behind covers the seam, no stitching)."""
    starts = [0]
    for k in range(1, k_max + 1):
        stride = 1 << k
        prev = starts[k - 1]
        start = max(2 * prev if prev > 0 else R0, d_min_tiles(stride, pix))
        if start <= prev:
            start = 2 * prev                                  # keep the ladder strictly rising
        starts.append(start)
    rings = []
    for k in range(k_max + 1):
        stride = 1 << k
        outer = starts[k + 1] + stride if k < k_max else 2 * starts[k_max]
        inner = 0 if k == 0 else starts[k] - stride
        rings.append({"k": k, "stride": stride, "inner": inner, "outer": outer})
    return rings


def trade_table(k_max=10):
    """THE DELIVERABLE: for each declared pixel budget, the derived schedule's reach, ring
    count and exact vertex total — the surface R2b chooses a working point on, with pictures
    and a host A/B, instead of anyone arguing."""
    out = []
    for pix in PIX_CANDIDATES:
        rings = schedule(pix, k_max)
        verts = sum(ring_vertices(r) for r in rings)
        reach_tiles = rings[-1]["outer"]
        out.append({"pix": pix, "rings": len(rings), "verts": verts,
                    "reach_km_at_1m": reach_tiles * TILE // 1000,
                    "near_verts": ring_vertices(rings[0]) + ring_vertices(rings[1])})
    return out


def ring_vertices(ring):
    """EXACT lattice-point count of the square annulus [inner, outer] at the ring's stride."""
    s, inn, out = ring["stride"], max(ring["inner"], 0), ring["outer"]
    side_out = 2 * (out // s) + 1
    if inn == 0:
        return side_out * side_out
    side_in = max(2 * ((inn + s - 1) // s) - 1, 0)
    return side_out * side_out - side_in * side_in


def covered(rings, tx, ty):
    """How many rings claim tile (tx, ty)?"""
    m = max(abs(tx), abs(ty))
    return sum(1 for r in rings if r["inner"] <= m <= r["outer"])


def coverage_law(rings, seed=5, probes=4000):
    """Every probe tile inside the ladder's reach is covered; every OCTAVE SEAM tile is
    covered at least twice (paint-behind overlap is real, not asserted)."""
    reach = rings[-1]["outer"]
    rng_state = seed
    for _ in range(probes):
        rng_state = (rng_state * 6364136223846793005 + 1442695040888963407) % (1 << 64)
        tx = (rng_state >> 8) % (2 * reach + 1) - reach
        rng_state = (rng_state * 6364136223846793005 + 1442695040888963407) % (1 << 64)
        ty = (rng_state >> 8) % (2 * reach + 1) - reach
        if covered(rings, tx, ty) < 1:
            return (False, (tx, ty))
    for r in rings[1:]:
        seam = r["outer"]                                     # this ring's outer edge
        nxt = next((q for q in rings if q["k"] == r["k"] + 1), None)
        if nxt is not None and covered(rings, seam, 0) < 2:
            return (False, ("seam", seam))
    return (True, None)


def octave_cost_form(rings):
    """Past the saturation octave (only the coarsest layer survives, so d_min stops growing)
    every INTERIOR ring doubles both edges — their vertex counts are IDENTICAL, so cost is
    affine in ring count and logarithmic in reach. The first rings straddle their d_min
    boundaries and the final ring closes the ladder, so the law is asserted on the interior
    tail, which must be at least three rings long or the sweep proved nothing."""
    counts = [ring_vertices(r) for r in rings]
    interior = counts[3:-1]
    return (len(interior) >= 3 and len(set(interior)) == 1, tuple(counts))


# ---- plants -------------------------------------------------------------------------------------
def a_stride1_prefix_is_the_canon():
    cache = {}
    for i in range(40):
        x, y = 5000 + i * 17, 9000 + i * 13
        if height_full(x, y, cache) != height_prefix(x, y, 1, cache):
            return False
    return True


def an_overdropped_prefix_exceeds_its_bound():
    """Drop one layer MORE than stride 2's prefix allows and the stride-2 bound must break."""
    cache = {}
    kept = kept_layers(2)[:-1]                                # illegally drop the finest kept
    bound = error_bound_h(2)
    worst = 0
    for i in range(48):
        for j in range(48):
            x, y = 31337 + i * 2, 4242 + j * 2
            e = abs(height_full(x, y, cache) - height_prefix(x, y, 2, cache, kept))
            worst = max(worst, e)
    return worst > bound


def a_ring_below_dmin_violates_the_budget():
    """Seat a stride-16 ring nearer than its derived d_min: its projected error must exceed
    the pixel budget — the schedule law has teeth."""
    stride, pix = 16, 8
    e = error_bound_h(stride)
    too_near = max(d_min_tiles(stride, pix) // 2, 1)
    px = e * FOCAL // (too_near * TILE)
    return px > pix


def a_gapped_ladder_is_caught():
    rings = schedule(16, 5)
    rings[2]["inner"] += rings[2]["stride"] * 3               # tear the overlap open
    ok, _where = coverage_law(rings, probes=8000)
    return not ok
