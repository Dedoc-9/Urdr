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
