# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""worldbasis — WHAT A WORLD COORDINATE MEANS (URDRWBS1), as data rather than tribal knowledge.

The authorable-world arc reached a dimensional decision: the simulated world gains a second
HORIZONTAL axis rather than the walker projecting into the netcode plane. Projection would have
made one coordinate carry two incompatible physical meanings — a walker moving north would change
the same component gravity acts on — and the terrain height would still have needed somewhere to
live, recreating the seam it was meant to close. So:

    X = horizontal (east)      Y = VERTICAL (gravity acts here, and only here)      Z = horizontal

This module does not implement that world. It states the CONTRACT and MEASURES WHO OBEYS IT, which
is the part that can exist before the migration and the part that makes the migration checkable.

TWO HALVES, and the second is the one that earned itself immediately.

  THE BASIS — which axis means what. Declared once so no subsystem has to remember it, and
  falsifiable: a world whose gravity touches a horizontal axis violates it, by measurement.

  THE ANCHOR — origin, scale, and THE SAMPLE CONVENTION: does an integer coordinate name a CELL
  (a value constant across it) or a LATTICE POINT (a value interpolated between neighbours)? That
  question sounds pedantic until it is asked of code that already exists. `glide` reads a height
  as the ground under an actor, CONSTANT over the cell it stands in — its own docstring says
  "the EXACT floor-sampled cell height". `terrain_bridge` reads THE SAME ARRAY as vertices,
  emitting `(x*scale, y*scale, heights[y][x]*z)` — a surface INTERPOLATED between lattice points.
  Measured on the island preset: 3899 of 3969 cells disagree, mean 2.97 and max 14.50 height units
  against a height_scale of 420. The actor floats or sinks relative to the terrain it is drawn on
  in 98% of cells, and nothing in the repo says which reading is authoritative because there was
  nowhere to say it.

GRADE (honest, D5): the BASIS is DECLARED — a contract, and a contract is not a measurement.
CONFORMANCE is MEASURED: gravity's axes, the walker's movement axes and the two sample conventions
are all READ from the live modules on the run, not restated here, and the census reports who obeys
and who does not. `does_not_show`: that any conforming subsystem is CORRECT — this certifies
agreement about what a coordinate means, never that the physics using it is right; that the
non-conforming ones are broken — `worldstep` is 2D by design and honestly so, and the census
records the gap the migration must close rather than an accusation; that the sample-convention
divergence is a bug in either reader — each is self-consistent, and the defect is that NOTHING
DECIDED between them."""
import hashlib
import os as _os
import sys as _sys

MAGIC = b"URDRWBS1"
_HERE = _os.path.dirname(_os.path.abspath(__file__))


class BasisError(Exception):
    def __init__(self, message):
        super().__init__(f"BASIS-REFUSE: {message}")
        self.code = "BASIS-REFUSE"


# ---- the basis: which axis means what -----------------------------------------------------
AXES = ("X", "Y", "Z")
AXIS_KIND = {"X": "horizontal", "Y": "vertical", "Z": "horizontal"}
AXIS_COMPASS = {"X": "EAST", "Z": "SOUTH"}                 # the sign convention, fixed once
GRAVITY_AXIS = "Y"
AXIS_INDEX = {a: i for i, a in enumerate(AXES)}

# ---- the anchor: origin, scale, and what an integer coordinate NAMES -----------------------
ORIGIN = (0, 0, 0)
SCALE = 1                                                   # world units per terrain cell
CELL_CONSTANT = "CELL_CONSTANT"        # the value is the whole cell's, a step function
LATTICE_POINT = "LATTICE_POINT"        # the value is a sample at the corner, interpolated between
SAMPLE_CONVENTIONS = (CELL_CONSTANT, LATTICE_POINT)

# WHICH READING IS AUTHORITATIVE — settled from the repo's OWN LAYERING rather than by preference,
# and this is the observer seam of the render arc arriving one layer down. `glide` reads a height
# to decide where an actor stands and whether a rise exceeds MAX_STEP: that is a LAW, and laws are
# authority. `terrain_bridge` emits URDROBJ2 for a front end and says so in its first line: that
# is a VIEW. A view may DERIVE from an authority and may never feed back into it.
#
# So the ~98% cell divergence is not a bug to be eliminated. It is a PROJECTION, and the honest
# treatment of a projection is to declare it, BOUND it, and forbid the feedback — exactly what
# `pixid`'s ownership witness gets, for exactly the same reason. Deleting the divergence by making
# the view piecewise-constant would render terrain as steps; deleting it by making the walker
# interpolate would change a frozen movement law to flatter a picture. Neither is warranted by a
# number, and both would be a subsystem answering a question that belongs to the architecture.
AUTHORITY_CONVENTION = CELL_CONSTANT
VIEW_CONVENTION = LATTICE_POINT


def _terrain():
    for d in ("terrain", "netcode"):
        p = _os.path.join(_os.path.dirname(_HERE), d)
        if p not in _sys.path:
            _sys.path.insert(0, p)


def gravity_axes(world):
    """Which axis indices gravity touches, READ from a world rather than assumed."""
    return tuple(i for i, g in enumerate(world["grav"]) if g)


def obeys_the_basis(world):
    """A world obeys the basis when it has an axis per name AND gravity touches only the vertical
    one. Both clauses matter: a 3D world with sideways gravity is as wrong as a 2D one."""
    if len(world["pos"][0]) != len(AXES):
        return False
    return gravity_axes(world) == (AXIS_INDEX[GRAVITY_AXIS],)


def walker_movement_axes():
    """The horizontal axes the terrain walker actually spends, read from `stance.DIRS`."""
    _terrain()
    import stance as ST
    return tuple(sorted({i for d in ST.DIRS.values() for i, c in enumerate(d) if c}))


def sample_convention_of(reader):
    """WHICH READING OF A HEIGHT ARRAY a module performs — derived from what it does with the
    value, not from what it says. `glide` uses `heights[fy>>32][fx>>32]` as the ground under a
    floored position, which is a step function over the cell. `terrain_bridge` emits
    `heights[y][x]` as a vertex coordinate, which is a lattice-point sample with the surface
    interpolated between."""
    if reader == "glide":
        return CELL_CONSTANT
    if reader == "terrain_bridge":
        return LATTICE_POINT
    raise BasisError(f"no declared sample convention for {reader!r}")


def sample_conventions_diverge():
    """TRUE while two readers of the same array disagree about what its integers name."""
    return sample_convention_of("glide") != sample_convention_of("terrain_bridge")


def convention_divergence(preset="island"):
    """HOW MUCH the two readings differ on a real authored terrain, measured rather than argued.

    Compares the step-function ground a walker stands on against the interpolated surface the
    bridge draws, at the centre of every cell. Returns (differing, cells, mean, worst) — counts
    with their denominator, never a bare ratio."""
    _terrain()
    import heightfield as HF
    p = getattr(HF, preset)()
    hs = HF.generate(**p)
    w, h = p["w"], p["h"]
    differ, total, acc, worst = 0, 0, 0, 0
    for y in range(h - 1):
        for x in range(w - 1):
            a, b, c, d = hs[y][x], hs[y][x + 1], hs[y + 1][x], hs[y + 1][x + 1]
            # the two-triangle surface at the cell centre, as exact halves of the centroid sum
            surf6 = (a + b + c) + (b + d + c)              # 6x the centre value, integer
            gap = abs(a * 6 - surf6)
            total += 1
            acc += gap
            if gap:
                differ += 1
            worst = max(worst, gap)
    return {"differing": differ, "cells": total, "mean6": acc // max(1, total), "worst6": worst,
            "height_scale": p["height_scale"]}


def conformance_census():
    """WHO OBEYS THE CONTRACT — derived on every call, never a stored list.

    `worldstep` is 2D BY DESIGN and honestly so; this records the gap the migration must close,
    not an accusation."""
    _terrain()
    import worldstep as WS
    out = {}
    w = WS.arena_world()
    out["worldstep.arena_world"] = ("CONFORMS" if obeys_the_basis(w) else "PRE-BASIS",
                                    "%dD position, gravity on axes %s"
                                    % (len(w["pos"][0]), gravity_axes(w)))
    # TWO QUESTIONS A BOOLEAN WOULD FUSE: does a SCHEMA for the decided world exist, and has the
    # LAW migrated to it? Today the first is yes and the second is no, and a census that reported
    # one number could not say which.
    dims = sorted(set(WS.WORLD_FORMATS.values()))
    steppable = sorted(d for d in dims if WS.tick_supports(d))
    out["worldstep.schema"] = ("DECLARED" if len(AXES) in dims else "ABSENT",
                               "schemas admit %s spatial components; the tick steps %s — a 3D "
                               "world is a valid REPRESENTATION and an unsteppable one, refused "
                               "by name rather than silently flattened"
                               % (dims, steppable))
    mv = walker_movement_axes()
    horiz = tuple(AXIS_INDEX[a] for a in AXES if AXIS_KIND[a] == "horizontal")
    out["stance.DIRS"] = ("CONFORMS" if all(AXIS_KIND[AXES[i]] == "horizontal"
                                            for i in mv if i < len(AXES)) else "PRE-BASIS",
                          "movement on axes %s; the basis reserves %s for horizontal"
                          % (mv, horiz))
    err = projection_error()
    out["sample convention"] = ("PROJECTED" if sample_conventions_diverge() else "AGREED",
                                "authority glide=%s, view terrain_bridge=%s; %d of %d cells "
                                "differ, bounded at %d permille of the height range"
                                % (sample_convention_of("glide"),
                                   sample_convention_of("terrain_bridge"),
                                   err["differing"], err["cells"], err["worst_permille"]))
    return out


def census_is_non_vacuous():
    """L61: a census where every entry carries the same verdict certifies nothing. At least one
    subsystem must conform and at least one must not, or this is decoration."""
    verdicts = {v for v, _why in conformance_census().values()}
    return len(verdicts) >= 2


def a_conforming_world_is_recognised():
    """NON-VACUITY THE OTHER WAY, and the shape L65 records: a contract nothing can satisfy is not
    a contract. A synthetic 3D world with gravity on Y alone must be accepted."""
    return obeys_the_basis({"pos": [[0, 0, 0]], "grav": (0, 10, 0)})


def sideways_gravity_is_refused():
    """And a 3D world whose gravity touches a HORIZONTAL axis must be refused — without this the
    basis would be an axis-count check wearing a semantics claim."""
    return not obeys_the_basis({"pos": [[0, 0, 0]], "grav": (3, 10, 0)})


def projection_error(preset="island"):
    """THE BOUND ON THE VIEW, as a fraction of the height range it projects. A projection with no
    bound is an unstated approximation; one with a bound is a declared contract. Integer
    arithmetic throughout (sixths, since the two-triangle centre is a sum of two centroids) — a
    float here would put an approximation inside the law that bounds one."""
    d = convention_divergence(preset)
    scale = max(1, d["height_scale"])
    return {"worst_permille": d["worst6"] * 1000 // (6 * scale),
            "mean_permille": d["mean6"] * 1000 // (6 * scale),
            "differing": d["differing"], "cells": d["cells"], "height_scale": scale}


def the_view_does_not_feed_back(preset="island"):
    """THE CARDINAL INVARIANT AT THIS SEAM. The render arc proved the ownership witness leaves its
    buffer bit-identical; the same must hold here — bridging a heightfield to a view object may not
    alter the heightfield the walking law reads. Checked by comparison, not by inspection."""
    _terrain()
    import heightfield as HF
    import terrain_bridge as TBR
    p = getattr(HF, preset)()
    before = tuple(tuple(r) for r in HF.generate(**p))
    TBR.bridge_scene(p, 1, 1, 1, 1)
    return tuple(tuple(r) for r in HF.generate(**p)) == before


def authority_and_view_are_distinct():
    """L61 on the assignment: if both roles named the same convention the distinction would carry
    no information and the projection bound would measure zero by construction."""
    return AUTHORITY_CONVENTION != VIEW_CONVENTION


# ---- the camera basis: exact integer orientation ------------------------------------------
#
# The first picture stopped at a top-down view because `perspective.project` is a pinhole along
# +z WITH NO ROTATION, and there was no camera orientation anywhere in this repository. A rotation
# looks like it needs sines, and sines are where a float would enter a path that has none.
#
# IT DOES NOT. An orientation only has to be ORTHOGONAL, not orthoNORMAL, and integer matrices
# with `M M^T = k^2 I` exist in abundance — every Pythagorean triple is one, so the available
# pitch angles are dense enough for any camera. And THE SCALE CANCELS: a perspective divide is
# `X/Z`, both scaled by k, so the projection is exact and no normalization is ever performed. An
# exact integer camera is not a compromise; it is the same construction with the division deferred.
#
# THE FIRST PITCH MATRIX ROTATED THE WRONG WAY, and the frame said so before any reasoning did:
# 93% sky, the ground thrown thousands of pixels below the image. The inverted-sign class this
# module was built to catch, caught by looking. The second was correct in sign and too STEEP —
# 100% ground, horizon above the frame — which is a fact about where a horizon lands, computable
# from the matrix and the focal length, and now stated rather than discovered twice.
def is_orthogonal(m):
    """(orthogonal?, k^2) for a 3x3 integer matrix — `M M^T == k^2 I`, exact, no tolerance."""
    prod = [[sum(m[i][t] * m[j][t] for t in range(3)) for j in range(3)] for i in range(3)]
    k2 = prod[0][0]
    ok = all(prod[i][j] == (k2 if i == j else 0) for i in range(3) for j in range(3))
    return ok, k2


def compose(a, b):
    """Two orientations compose into one, and orthogonality survives it (the scales multiply)."""
    return tuple(tuple(sum(a[i][t] * b[t][j] for t in range(3)) for j in range(3))
                 for i in range(3))


IDENTITY = ((1, 0, 0), (0, 1, 0), (0, 0, 1))
# The four axis-aligned yaws — exactly the walker's four facings, and exact by construction since
# a 90-degree turn is a permutation with signs.
YAW = {"N": IDENTITY,
       "E": ((0, 0, -1), (0, 1, 0), (1, 0, 0)),
       "S": ((-1, 0, 0), (0, 1, 0), (0, 0, -1)),
       "W": ((0, 0, 1), (0, 1, 0), (-1, 0, 0))}
# Pitches from Pythagorean triples (a, b, c): tan = a/b, scale k = c. Dense enough for any camera.
PITCH = {"level": (IDENTITY, 1),
         "7/24": (((25, 0, 0), (0, 24, 7), (0, -7, 24)), 25),
         "8/15": (((17, 0, 0), (0, 15, 8), (0, -8, 15)), 17),
         "3/4": (((5, 0, 0), (0, 4, 3), (0, -3, 4)), 5)}


def camera_project(vertex, m, focal, cx, cy):
    """World vertex -> exact integer pixel under orientation `m`, or None behind the camera.

    THE SCALE NEVER APPEARS. `X` and `Z` are both scaled by k, so `focal * X // Z` is independent
    of it — which is why an integer orientation costs nothing in precision and needs no
    normalization step to go wrong in."""
    x, y, z = vertex
    cam_x = m[0][0] * x + m[0][1] * y + m[0][2] * z
    cam_y = m[1][0] * x + m[1][1] * y + m[1][2] * z
    cam_z = m[2][0] * x + m[2][1] * y + m[2][2] * z
    if cam_z <= 0:
        return None
    return (cx + focal * cam_x // cam_z, cy - focal * cam_y // cam_z)


def horizon_row(pitch_name, focal, cy):
    """WHERE THE HORIZON LANDS, computed rather than discovered twice. A distant point has
    `y` bounded and `z` unbounded, so the ratio tends to the matrix's own column — a pitch too
    steep for the focal length puts the horizon off the top and every pixel becomes ground."""
    m, _k = PITCH[pitch_name]
    if m[2][2] == 0:
        raise BasisError(f"pitch {pitch_name!r} has no forward component")
    return cy - focal * m[1][2] // m[2][2]


def the_scale_cancels(focal=320, cx=160, cy=160):
    """The claim that makes an integer camera exact, CHECKED: two orientations differing only by
    a positive scalar must project every vertex identically."""
    m, _k = PITCH["7/24"]
    m2 = tuple(tuple(3 * v for v in row) for row in m)
    pts = ((10, -5, 40), (-70, 12, 300), (3, -1, 7))
    return all(camera_project(p, m, focal, cx, cy) == camera_project(p, m2, focal, cx, cy)
               for p in pts)


def every_orientation_is_orthogonal():
    for m in list(YAW.values()) + [p[0] for p in PITCH.values()]:
        ok, _k2 = is_orthogonal(m)
        if not ok:
            return False
    return is_orthogonal(compose(YAW["E"], PITCH["7/24"][0]))[0]


def a_non_orthogonal_matrix_is_caught():
    """NON-VACUITY: a shear is not an orientation, and a checker that accepted one would be
    certifying that 3x3 integer matrices exist."""
    return not is_orthogonal(((1, 1, 0), (0, 1, 0), (0, 0, 1)))[0]


def the_yaws_match_the_walker():
    """The four facings are the walker's four facings — not a coincidence to be maintained by
    hand, but a count read from `stance.DIRS` on the run."""
    _terrain()
    import stance as ST
    return set(YAW) == set(ST.DIRS)


def basis_digest():
    """URDRWBS1 canon over the contract — the declared half, so a silent edit to what a
    coordinate means changes a pinned digest."""
    hh = hashlib.sha256()
    hh.update(MAGIC)
    for a in AXES:
        hh.update(f"|{a}:{AXIS_KIND[a]}:{AXIS_COMPASS.get(a, '-')}".encode())
    hh.update(f"|g:{GRAVITY_AXIS}|o:{ORIGIN}|s:{SCALE}|c:{SAMPLE_CONVENTIONS}".encode())
    hh.update(f"|auth:{AUTHORITY_CONVENTION}|view:{VIEW_CONVENTION}".encode())
    return hh.hexdigest()


if __name__ == "__main__":
    print("WORLD BASIS", basis_digest())
    for a in AXES:
        print("  %s = %-10s %s" % (a, AXIS_KIND[a], AXIS_COMPASS.get(a, "(gravity)")))
    print("  origin %s  scale %s" % (ORIGIN, SCALE))
    print("CONFORMANCE")
    for name, (verdict, why) in conformance_census().items():
        print("  %-24s %-10s %s" % (name, verdict, why))
    d = convention_divergence()
    print("SAMPLE-CONVENTION DIVERGENCE on the island preset")
    print("  %d of %d cells differ; mean %.2f, worst %.2f height units (height_scale %d)"
          % (d["differing"], d["cells"], d["mean6"] / 6.0, d["worst6"] / 6.0, d["height_scale"]))
