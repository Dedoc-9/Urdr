# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""terrain_bridge — T2: the heightfield → URDROBJ2 bridge (the D14 admission rung).

Converts a URDRHF1 heightfield into an integer-snapped wireframe grid object under the
one identity law every front end shares (`URDROBJ2|v{n}|x,y,z|…|e{m}|a-b|…`, edges
min-first and lexically sorted). Height rides the z axis; x/y are sample coordinates
scaled exactly. Decimation is EXACT: the stride must divide (dim − 1) so the last
row/column is always included — a stride that leaves a remainder is `TERRAIN-REFUSE`,
never a silently dropped border.

D14 clause 2 requires the canon "through its OWN implementation": `own_canon` below
re-implements the URDROBJ2 string law without importing `canon_ref` — the gate and the
falsifiers then check `own_canon ≡ canon_ref.canon` on every pinned scene, which is the
agreement that makes convergence a checked property. D14 clause 5: provenance (seed,
params, template name) is carried alongside and NEVER hashed — two bridges of the same
field with different provenance are the same object.

Everything here is exact integer arithmetic on already-integer heights; no rounding
happens in this module at all. Grade: MEASURED (reference) once gated; the editor/world
consumption of the produced objects is the existing, already-measured machinery."""
# ---- WHAT THIS BRIDGE DOES NOT DO, and why nothing can yet --------------------------------
#
# This module converts a heightfield into a URDROBJ2 wireframe VIEW object. It is regularly
# mistaken — including by the author of this block, in the proposal that produced it — for the
# missing link between the terrain a walker crosses and the world the netcode spine simulates.
# It is not, and the reason is not that the link is unwritten. THE CORRESPONDENCE IS UNDEFINED.
#
# `worldstep`'s world is a 2D SIDE VIEW: `pos` has two components, `grav` acts along axis 1, and
# `floor`/`ceil` bound that axis. The terrain walker is a TOP-DOWN 2D GRID: `stance.DIRS` spends
# axis 1 on N/S movement, and height is a THIRD quantity sampled per cell. So axis 0 corresponds,
# axis 1 means VERTICAL in one world and HORIZONTAL in the other, and the netcode world has no
# third axis to hold a terrain height at all.
#
# THIS RETIRES A MEASUREMENT BEFORE IT WAS BUILT. The proposed first rung was a seam certificate —
# count where terrain ground height and netcode resting height disagree, reported as
# (disagree, overlap) per predicate, with the vacuity guard OVERLAP == 0. Its three outcome states
# were zero-overlap, agreement, and disagreement. It had NO STATE for the case that actually
# obtains: an overlap that is numerically non-empty and semantically meaningless, because the
# quantity on each side of the comparison names a different physical direction. That measurement
# would have produced counts, passed its own non-vacuity guard, and compared a map ROW INDEX
# against a height above a floor. The fifth defect of this arc — a confounded axis — arriving in
# the ARCHITECTURE rather than in an instrument.
#
# The three options on the table (terrain becomes statics / certify the seam / a heightfield
# collision primitive) all presuppose one coordinate space. A dimensional decision comes first:
# either the simulated world gains a second horizontal axis, or the walker projects into the
# netcode plane. Neither is a measurement, and neither is smuggled in here.
def axis_semantics():
    """READ FROM CODE, not restated: what each world spends its axes on.

    Imported function-locally on purpose — a module-scope edge from terrain to netcode is exactly
    the cross-subsystem dependency `lattice-depth` measures, and this is an audit, not a use."""
    import os as _o
    import sys as _s
    for _d in ("netcode", "physics"):
        _p = _o.path.join(_o.path.dirname(_o.path.dirname(_o.path.abspath(__file__))), _d)
        if _p not in _s.path:
            _s.path.insert(0, _p)
    import stance as _ST
    import worldstep as _WS
    w = _WS.arena_world()
    return {"netcode_axes": len(w["pos"][0]),
            "netcode_gravity_axes": tuple(i for i, g in enumerate(w["grav"]) if g),
            "netcode_bounded_axis1": ("floor" in w and "ceil" in w),
            "terrain_movement_axes": tuple(sorted({i for d in _ST.DIRS.values()
                                                   for i, c in enumerate(d) if c})),
            "terrain_has_separate_height": True}


def netcode_correspondence_is_undefined(sem=None):
    """TRUE while axis 1 means different things in the two worlds, or while the netcode world has
    no axis to hold a terrain height. A reason, not a verdict — see the block above."""
    s = sem or axis_semantics()
    axis1_is_vertical_in_netcode = 1 in s["netcode_gravity_axes"] and s["netcode_bounded_axis1"]
    axis1_is_horizontal_in_terrain = 1 in s["terrain_movement_axes"]
    no_room_for_height = s["netcode_axes"] < 3 and s["terrain_has_separate_height"]
    return (axis1_is_vertical_in_netcode and axis1_is_horizontal_in_terrain) or no_room_for_height


def correspondence_check_can_fail(sem=None):
    """NON-VACUITY. A checker that cannot say 'defined' would report the seam undefined forever,
    including after somebody defines it — which is the shape of law this arc has already retired
    once. On a synthetic world with a third axis and gravity off axis 1, this must return False."""
    s = dict(sem or axis_semantics())
    s.update(netcode_axes=3, netcode_gravity_axes=(2,), netcode_bounded_axis1=False)
    return not netcode_correspondence_is_undefined(s)


import hashlib

from heightfield import TerrainError, generate


def _refuse(message):
    raise TerrainError("TERRAIN-REFUSE", message)


def _is_int(v):
    return type(v) is int


def to_object(heights, stride, xy_scale, z_num=1, z_den=1):
    """The wireframe grid: verts (x·xy_scale, y·xy_scale, h·z_num // z_den) at every
    stride-th sample (last row/column exactly included), edges to the right and down
    neighbours. Returns (verts, edges) — plain integer tuples, URDROBJ2-ready."""
    if not (isinstance(heights, tuple) and len(heights) >= 2
            and all(isinstance(r, tuple) and len(r) == len(heights[0]) >= 2 for r in heights)):
        _refuse("heights must be a rectangular tuple grid (≥ 2×2)")
    h_dim, w_dim = len(heights), len(heights[0])
    for name, v in (("stride", stride), ("xy_scale", xy_scale),
                    ("z_num", z_num), ("z_den", z_den)):
        if not (_is_int(v) and v >= 1):
            _refuse(f"{name} must be a positive int, got {v!r}")
    if (w_dim - 1) % stride != 0 or (h_dim - 1) % stride != 0:
        _refuse(f"stride {stride} must divide both {w_dim - 1} and {h_dim - 1} exactly "
                "(the border is included, never dropped)")
    xs = list(range(0, w_dim, stride))
    ys = list(range(0, h_dim, stride))
    cols = len(xs)
    verts = []
    for y in ys:
        for x in xs:
            verts.append((x * xy_scale, y * xy_scale, heights[y][x] * z_num // z_den))
    edges = []
    for r in range(len(ys)):
        for c in range(cols):
            i = r * cols + c
            if c + 1 < cols:
                edges.append((i, i + 1))
            if r + 1 < len(ys):
                edges.append((i, i + cols))
    return tuple(verts), tuple(edges)


def own_canon(verts, edges):
    """The INDEPENDENT URDROBJ2 implementation (no import from canon_ref — that module
    is the referee, not a dependency): same string law, this module's own code."""
    parts = ["URDROBJ2", "v%d" % len(verts)]
    for (x, y, z) in verts:
        parts.append("%d,%d,%d" % (x, y, z))
    norm = sorted((a, b) if a <= b else (b, a) for (a, b) in edges)
    parts.append("e%d" % len(norm))
    for (a, b) in norm:
        parts.append("%d-%d" % (a, b))
    return hashlib.sha256("|".join(parts).encode("utf-8")).hexdigest()


def own_canon_defect(verts, edges):
    """THE DEFECT (non-vacuity): max-first edge normalization — a plausible one-line
    mistake in the canon law that MUST diverge from the golden on every grid."""
    parts = ["URDROBJ2", "v%d" % len(verts)]
    for (x, y, z) in verts:
        parts.append("%d,%d,%d" % (x, y, z))
    norm = sorted((b, a) if a <= b else (a, b) for (a, b) in edges)
    parts.append("e%d" % len(norm))
    for (a, b) in norm:
        parts.append("%d-%d" % (a, b))
    return hashlib.sha256("|".join(parts).encode("utf-8")).hexdigest()


def bridge_scene(params, stride, xy_scale, z_num=1, z_den=1, provenance=None):
    """Generate the field, bridge it, and return (verts, edges, digest, design).
    `provenance` is carried in the design dict and provably inert to the digest."""
    heights = generate(params["w"], params["h"], params["seed"], params["height_scale"],
                       params["sea_level"], params["layers"], params["falloff"],
                       params["falloff_width"])
    verts, edges = to_object(heights, stride, xy_scale, z_num, z_den)
    design = {"verts": [{"x": x, "y": y, "z": z} for (x, y, z) in verts],
              "edges": [list(e) for e in edges],
              "provenance": dict(provenance or {})}
    return verts, edges, own_canon(verts, edges), design


# The pinned bridge parameterizations (append-only rows in conformance_terrain.txt):
#   island_obj — island() at stride 9 (63/9 → 8×8 grid), xy_scale 8, z 1/1
#   blank_obj  — blank() at stride 5 (15/5 → 4×4 grid), xy_scale 32, z 1/1
BRIDGES = {
    "island_obj": ("island", 9, 8, 1, 1),
    "blank_obj": ("blank", 5, 32, 1, 1),
}
