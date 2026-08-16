# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""planet (URDR2PL1) — R2c of the v2 ladder: the horizon is a door, and curvature is a view.

THE CLAIM THIS RUNG DECIDES: "planet-scale worlds make the vista problem intractable." On a
curved body the opposite is true, and this rung makes it arithmetic. Two laws:

  * THE HORIZON CLIP — the horizon distance derives EXACTLY from the declared radius and eye
    height (d_h = isqrt(h*(2R+h)), integer, no float anywhere), and an object of height H is
    visible past the horizon iff (d - d_h)^2 <= 2*R*H — an exact integer inequality, so the
    visibility bound is a VOXIN DOOR: distance bound admits, bound+1 refuses, in arithmetic
    the gate re-derives. Geometry beyond the bound is provably unrenderable, so a planet
    BOUNDS draw work where a flat map cannot: the clip table composes the derived bound with
    R2a's own ladder machinery (schedule and exact vertex counts, imported, not copied) and
    prints rings and vertices at the clipped reach per body. A flat map's reach is a CHOICE;
    a planet's is a DERIVATION — the vista problem gets easier, not harder.
  * THE CURVATURE DROP — authority stays a flat exact lattice (nothing in physics, netcode
    or the delta door changes), and curvature is a VIEW-layer vertical drop of far columns by
    the exact integer d*d/(2R) in camera space. Toggling curvature MUST change the view
    digest (a curvature that draws nothing is decoration) and MUST NOT move the authority
    digest — fidelity independent of integrity, the tree's cardinal invariant, at planetary
    scale. The two laws meet in one identity the gate checks: the drop AT the horizon
    distance equals the eye height (within exact floor remainders) — the same arithmetic seen
    from both sides.

THE MODEL, DECLARED: the drop is the parabolic sagitta d^2/2R, a declared approximation of
the sphere whose gap is d^4/8R^3 — and the gap is MEASURED, not waved at: sub-tile (zero,
in integer tiles) at every standard tier's full visibility bound, and printed honestly at
the one tier where it is not (an 8,848-tile peak seen from 340 km shows a measured
6-tile model gap at the extreme edge, stated, never hidden).

does_not_show: rendering a planet (this is the derivation layer; pictures are the demo's
R2b-style adoption with its own before/after); atmosphere, refraction, or occlusion by
terrain between eye and horizon (the bound is the geometric ceiling — real terrain occludes
MORE, never less, so the work bound stands); the sphere-vs-parabola gap beyond the swept
tiers (the caustic law); tile-to-metre scale (printed at one metre per tile, a declaration,
exactly as R2a prints its trade table).

falsifier: verify2 runs every plant — one past the visibility door refuses; a poisoned
curvature (a view pass that writes its drop back into the terrain store) breaks the
authority digest; a drop-blind view (curvature that changes no pixel) is caught by the
non-vacuity comparison; and a near-infinite radius never clips (the flat-map degenerate
control: the clip is the planet's property, not the code's habit).
"""
import hashlib
from math import isqrt

import lod as LD

MAGIC = b"URDR2PL1"

TIERS = (
    ("asteroid", 1_000, 2, 20),
    ("moon", 1_737_400, 2, 100),
    ("earth", 6_371_000, 2, 100),
    ("earth-everest", 6_371_000, 2, 8_848),
)                                     # (name, radius_tiles, eye_h, peak_H) at 1 m per tile
PIX = 35                              # the working point the reach arc measured


class Planet2Error(Exception):
    def __init__(self, message):
        super().__init__(f"V2PLANET-REFUSE: {message}")
        self.code = "V2PLANET-REFUSE"


def horizon_tiles(radius, h):
    """The MODEL's horizon: the tangent point of the sight line grazing the parabola,
    exactly isqrt(2*R*h). (The sphere's secant form isqrt(h*(2R+h)) differs by the h^2
    cross-term — sub-tile at every tier here, and it belongs to the declared model gap;
    mixing the two formulas was this rung's own first red row, caught by the door law.)"""
    if radius < 1 or h < 0:
        raise Planet2Error("a horizon needs a positive radius and a non-negative eye")
    return isqrt(2 * radius * h)


def visible_bound(radius, h_eye, peak):
    """The exact ceiling: an object of height `peak` can be seen at most this far."""
    return horizon_tiles(radius, h_eye) + horizon_tiles(radius, peak)


def is_visible(radius, h_eye, peak, d):
    """EXACT integer visibility in the declared model: past the eye's horizon, the grazing
    sight line rises as (d - d_h)^2 / 2R, and the object clears it iff the inequality holds."""
    d_h = horizon_tiles(radius, h_eye)
    if d <= d_h:
        return True
    return (d - d_h) ** 2 <= 2 * radius * peak


def drop(d, radius):
    """The curvature drop: exact integer sagitta of the view model."""
    return d * d // (2 * radius)


def model_gap_tiles(d, radius):
    """Parabola-vs-sphere gap at distance d, in whole tiles: d^4 / 8R^3, floored."""
    return d ** 4 // (8 * radius ** 3)


def ladder_for_reach(pix, reach):
    """R2a's schedule, grown until it covers the reach, last ring clamped TO the reach —
    the clip is the point, so the ladder may not quietly overshoot it."""
    for k_max in range(1, 48):
        rings = LD.schedule(pix, k_max)
        if rings[-1]["outer"] >= reach:
            rings[-1] = dict(rings[-1], outer=reach)
            return rings
    raise Planet2Error(f"no ladder covers reach {reach} — the reach is not planetary")


# ---- the laws -----------------------------------------------------------------------------------
def horizon_door():
    """Voxin's law on the visibility ceiling: the bound admits, one past refuses — exact,
    both directions, every tier; and the horizon is monotonic in eye height."""
    for (_n, radius, h, peak) in TIERS:
        b = visible_bound(radius, h, peak)
        if not is_visible(radius, h, peak, b):
            return False
        if is_visible(radius, h, peak, b + 1):
            return False
        if not (horizon_tiles(radius, h) < horizon_tiles(radius, h + 1)
                <= horizon_tiles(radius, 4 * h)):
            return False
    return True


def beyond_is_dark(seed=1961):
    """Seeded soundness sweep: everything past the bound is invisible; something inside the
    last tile-width is visible (the ceiling is approached, not decoration)."""
    s = seed
    for (_n, radius, h, peak) in TIERS:
        b = visible_bound(radius, h, peak)
        for _ in range(200):
            s = (s * 6364136223846793005 + 1442695040888963407) % (1 << 64)
            if is_visible(radius, h, peak, b + 1 + s % (4 * b)):
                return False
        if not is_visible(radius, h, peak, b):
            return False
    return True


def clip_table():
    """THE DELIVERABLE: per body, the derived bound and what R2a's ladder costs to paint it."""
    out = []
    for (name, radius, h, peak) in TIERS:
        b = visible_bound(radius, h, peak)
        rings = ladder_for_reach(PIX, b)
        verts = sum(LD.ring_vertices(r) for r in rings)
        out.append({"name": name, "radius_km": radius // 1000,
                    "horizon_m": horizon_tiles(radius, h), "bound_m": b,
                    "rings": len(rings), "verts": verts,
                    "gap_tiles": model_gap_tiles(b, radius)})
    return out


def horizon_identity():
    """The two laws are one arithmetic: the drop AT the horizon distance is the eye height,
    within the exact floor remainders."""
    for (_n, radius, h, _peak) in TIERS:
        d_h = horizon_tiles(radius, h)
        got = drop(d_h, radius)
        if not (h - 1 <= got <= h + h * h // (2 * radius)):
            return False
    return True


def model_is_subtile():
    """The declared approximation, graded: zero whole tiles of sphere-gap at every standard
    tier's own bound; the everest extreme carries a measured, printed gap instead of a
    hidden one."""
    gaps = {row["name"]: row["gap_tiles"] for row in clip_table()}
    return (gaps["asteroid"] == 0 and gaps["moon"] == 0 and gaps["earth"] == 0
            and 0 < gaps["earth-everest"] <= 8)


# ---- the view/authority separation --------------------------------------------------------------
def _terrain(x, seed=1962):
    h = hashlib.sha256(b"%s|%d|%d" % (MAGIC, seed, x)).digest()
    return int.from_bytes(h[:2], "big") % 128


def render(radius, curved, poison=False, blind=False, columns=257, step=200):
    """A one-row skyline: column x at distance d = (x+1)*step, screen height = terrain minus
    the curvature drop. Returns (view_digest, authority_digest). The authority digest is
    taken AFTER the render, over the store the render read — a view that wrote would move it."""
    store = {x: _terrain(x) for x in range(columns)}
    view = hashlib.sha256(MAGIC + b"|view")
    for x in range(columns):
        d = (x + 1) * step
        fall = 0 if (not curved or blind) else drop(d, radius)
        y = store[x] - fall
        if poison and curved:
            store[x] = y                 # THE PLANT: the view writes its drop into authority
        view.update(b"%d|%d" % (x, y))
    auth = hashlib.sha256(MAGIC + b"|auth")
    for x in sorted(store):
        auth.update(b"%d|%d" % (x, store[x]))
    return view.hexdigest(), auth.hexdigest()


def curvature_is_a_view():
    """Toggling curvature changes the VIEW and never the AUTHORITY — both halves asserted,
    because a separation with a vacuous half is not a separation."""
    radius = 6_371_000
    v_flat, a_flat = render(radius, curved=False)
    v_curv, a_curv = render(radius, curved=True)
    return v_flat != v_curv and a_flat == a_curv


# ---- plants -------------------------------------------------------------------------------------
def a_poisoned_curvature_is_caught():
    radius = 6_371_000
    _v, a_clean = render(radius, curved=True)
    _v2, a_dirty = render(radius, curved=True, poison=True)
    return a_clean != a_dirty


def a_drop_blind_view_is_caught():
    radius = 6_371_000
    v_flat, _a = render(radius, curved=False)
    v_blind, _a2 = render(radius, curved=True, blind=True)
    return v_flat == v_blind             # the defect is VISIBLE as vacuity, and caught


def a_flat_earth_never_clips():
    """The degenerate control: a near-infinite radius yields a bound past any galaxy reach —
    the clip is the planet's property, not the code's habit."""
    return visible_bound(1 << 60, 2, 100) > 10 ** 9


def a_zero_radius_refuses():
    try:
        horizon_tiles(0, 2)
    except Planet2Error:
        return True
    return False
