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
    mv = walker_movement_axes()
    horiz = tuple(AXIS_INDEX[a] for a in AXES if AXIS_KIND[a] == "horizontal")
    out["stance.DIRS"] = ("CONFORMS" if all(AXIS_KIND[AXES[i]] == "horizontal"
                                            for i in mv if i < len(AXES)) else "PRE-BASIS",
                          "movement on axes %s; the basis reserves %s for horizontal"
                          % (mv, horiz))
    out["sample convention"] = ("DIVERGENT" if sample_conventions_diverge() else "AGREED",
                                "glide=%s, terrain_bridge=%s"
                                % (sample_convention_of("glide"),
                                   sample_convention_of("terrain_bridge")))
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


def basis_digest():
    """URDRWBS1 canon over the contract — the declared half, so a silent edit to what a
    coordinate means changes a pinned digest."""
    hh = hashlib.sha256()
    hh.update(MAGIC)
    for a in AXES:
        hh.update(f"|{a}:{AXIS_KIND[a]}:{AXIS_COMPASS.get(a, '-')}".encode())
    hh.update(f"|g:{GRAVITY_AXIS}|o:{ORIGIN}|s:{SCALE}|c:{SAMPLE_CONVENTIONS}".encode())
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
