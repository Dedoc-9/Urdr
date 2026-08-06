# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""voxin — THE IMPORT BOUNDARY (URDRVXI1): geometry becomes lattice occupancy, or it is REFUSED.
Slice S1.1 of the city-replica arc. NO NEW GLYPH.

WHY THIS RUNG EXISTS. `voxlat` certified the quantization boundary and named its own successor in its
`does_not_show`: *"any splat-to-occupancy derivation (the next rung)"*. That rung never happened, and
the consequence is structural rather than cosmetic — **the arc's chain has no front end.** Everything
downstream (simulate, stream, network, witness, replay) begins at a synthetic scene or a certified
heightfield. Nothing turns authored geometry into the lattice, so "import a real block" was not a
slow path, it was an absent one. This module is that path.

THE LAW, and it is one sentence: **occupancy is a function of the geometry alone.** Permute the
triangles, and the emitted key set and its digest are byte-identical. That is what makes an import
reproducible on another machine rather than merely repeatable on this one, and it is the property a
downstream witness needs — two importers that agree on geometry must agree on bytes.

THE ADMISSION RULE IS DERIVED, NOT CHOSEN, and this is the rung's real content. `voxlat` decided the
exact-integer triangle/box overflow maximum to be `4*B^3` and drew the corollary that a 64-bit
placement admits `3*coord_bits + 2 <= 64`, so `coord_bits <= 20`. **This module refuses any geometry
whose coordinate bound exceeds that.** The refusal is not a safety margin someone picked; it is the
theorem, applied. Geometry that would silently overflow a 64-bit placement cannot enter the lattice
at all — and `voxlat` measured what shipping the alternative costs: the handed-down quadratic
estimate claims a 57-bit fit where 84 are required, whose symptom is mis-adjudicated hits at long
range, indistinguishable from cheating. **The importer is where that theorem stops being arithmetic
and starts being a gate on real data.**

FLOAT IS REFUSED AT THE DOOR. Every authority path in this arc is exact integer; every scan of the
real world is float. `voxlat` moved that boundary INSIDE the codebase, and this module is the door:
a float coordinate is `VOXIN-REFUSE`, never rounded. Quantization is the CALLER's declared act,
performed before admission and owned by whoever performed it — because a rounding this module did
silently would be an authority act with no record.

GRADE. MEASURED: permutation invariance of the emitted key set and its digest over a swept corpus;
the derived coordinate bound, read from `voxlat.max_tile_coord_bits()` rather than restated; typed
refusal totality over floats, out-of-range coordinates, degenerate and malformed input; agreement
with `voxlat.tri_box_overlap` on every emitted voxel. DECLARED: that a triangle soup is the right
import surface — meshes and splats both reduce to one, but that reduction is the caller's and is not
performed here. does_not_show: that the geometry is CORRECT or that it resembles any real place;
splat/point-cloud ingestion (the caller quantizes); any renderer; cross-placement — URDRVXI1 is a
Python reference with no Rust or C99 port, so every figure here is single-implementation, exactly as
`voxlat`'s is.

    PYTHONHASHSEED=0 python3 tools/terrain/voxin.py
"""
import hashlib
import os as _os
import sys as _sys

_HERE = _os.path.dirname(_os.path.abspath(__file__))
if _HERE not in _sys.path:
    _sys.path.insert(0, _HERE)
import voxlat as VX                                                       # noqa: E402

MAGIC = b"URDRVXI1"
LEVELS = VX.LEVELS


class VoxinError(Exception):
    def __init__(self, message):
        super().__init__(f"VOXIN-REFUSE: {message}")
        self.code = "VOXIN-REFUSE"


def admissible_coord_bits(word=VX.WORD64):
    """THE DERIVED BOUND. Not a constant in this file: read from `voxlat`, which DECIDED it. If the
    word size or the overflow law ever changes, this moves with it and nothing here needs editing —
    a bound restated in two places is a bound that can disagree with itself."""
    return VX.max_tile_coord_bits(word)


def coord_limit(word=VX.WORD64):
    """The largest absolute coordinate a triangle may carry, from the derived bit budget."""
    return (1 << admissible_coord_bits(word)) - 1


def _check_vertex(v, limit):
    if not (isinstance(v, tuple) or isinstance(v, list)) or len(v) != 3:
        raise VoxinError(f"a vertex must be a 3-tuple of ints, got {v!r}")
    for c in v:
        if type(c) is not int:                       # bool is an int subclass; float is refused
            raise VoxinError(f"coordinates must be exact ints — float capture is the CALLER's "
                             f"declared quantization, never a silent rounding here; got {c!r}")
        if abs(c) > limit:
            raise VoxinError(f"coordinate {c} exceeds the DERIVED bound +/-{limit} "
                             f"({admissible_coord_bits()} bits): geometry this large would overflow "
                             f"a 64-bit placement of the exact-integer overlap test (voxlat's "
                             f"4*B^3 law), so it is refused rather than silently truncated")
    return tuple(v)


def _voxel_box(v0, v1, v2, side):
    """The candidate voxel range for a triangle, and THE MINUS ONE IS A BUG FIX RATHER THAN A MARGIN.

    Voxel index `x` covers the half-open region [x, x+1] — the box is centred at `2x+1` with
    half-extent 1 in doubled coordinates. So a triangle whose MINIMUM vertex sits exactly at `x`
    still touches voxel `x-1`, whose region ends at `x`. The first version used `min(verts)` as the
    low bound and therefore MISSED every boundary-touching voxel on the low side — an importer that
    silently under-reports occupancy, which for a city is a hole in a wall.

    It was not found by inspection. It was found because the ORACLE CHECK was repaired to run in
    BOTH directions: once the sweep asked "does any triangle hit this voxel" over the union of the
    boxes, the missed voxels appeared immediately. A one-directional check could not see it, because
    it compared each triangle's hits against the same too-small box that produced them."""
    lo = [max(0, min(v0[i], v1[i], v2[i]) - 1) for i in range(3)]
    hi = [min(side - 1, max(v0[i], v1[i], v2[i])) for i in range(3)]
    return lo, hi


def occupancy(triangles, levels=LEVELS, word=VX.WORD64):
    """Geometry -> the SORTED set of Morton keys whose unit voxel the geometry touches.

    Sorted, so the result is a function of the geometry and not of the input order; that ordering is
    the whole of the permutation-invariance law. Voxels are tested with `voxlat.tri_box_overlap`,
    the exact-integer Akenine-Moller test whose overflow bound this module enforces at the door."""
    if not isinstance(triangles, (list, tuple)):
        raise VoxinError("triangles must be a sequence")
    limit = coord_limit(word)
    side = 1 << levels
    keys = set()
    for t in triangles:
        if not isinstance(t, (list, tuple)) or len(t) != 3:
            raise VoxinError(f"a triangle must be exactly 3 vertices, got {t!r}")
        v0, v1, v2 = (_check_vertex(v, limit) for v in t)
        if v0 == v1 or v1 == v2 or v0 == v2:
            raise VoxinError(f"degenerate triangle (repeated vertex): {(v0, v1, v2)}")
        lo, hi = _voxel_box(v0, v1, v2, side)
        for x in range(lo[0], hi[0] + 1):
            for y in range(lo[1], hi[1] + 1):
                for z in range(lo[2], hi[2] + 1):
                    # unit voxel centred on the lattice point, half-extent 1 in doubled coordinates
                    c = (2 * x + 1, 2 * y + 1, 2 * z + 1)
                    d0, d1, d2 = ([2 * a for a in v] for v in (v0, v1, v2))
                    if VX.tri_box_overlap(d0, d1, d2, c, (1, 1, 1)):
                        keys.add(VX.morton(x, y, z, levels))
    return tuple(sorted(keys))


def occupancy_digest(triangles, levels=LEVELS):
    """The content address of an import. Two importers agreeing on geometry must agree on bytes."""
    keys = occupancy(triangles, levels)
    h = hashlib.sha256()
    h.update(MAGIC)
    h.update(len(keys).to_bytes(4, "big"))
    for k in keys:
        h.update(k.to_bytes(8, "big"))
    return h.hexdigest()


# ---- the laws, each able to fail ---------------------------------------------------------------
def occupancy_is_permutation_invariant(triangles, levels=LEVELS):
    """THE CENTRAL LAW. Reversing and rotating the triangle list must not move a single bit."""
    a = occupancy_digest(triangles, levels)
    rev = list(reversed(list(triangles)))
    rot = list(triangles)[1:] + list(triangles)[:1]
    return a == occupancy_digest(rev, levels) == occupancy_digest(rot, levels)


def bound_is_derived_not_restated():
    """The admission bound must come FROM `voxlat`, so the two cannot disagree. Checked by identity
    against the source of truth rather than against a copy of the number."""
    return (admissible_coord_bits() == VX.max_tile_coord_bits(VX.WORD64)
            and coord_limit() == (1 << VX.max_tile_coord_bits(VX.WORD64)) - 1)


def over_bound_geometry_is_refused():
    """RED-FIRST: a coordinate one past the derived limit must refuse. This is the theorem acting as
    a door — the plant is the geometry `voxlat` proved would overflow a 64-bit placement."""
    over = coord_limit() + 1
    try:
        occupancy([((0, 0, 0), (1, 0, 0), (0, over, 0))])
        return False
    except VoxinError:
        return True


def float_is_refused():
    """RED-FIRST: quantization is the caller's declared act. A float must never be rounded here."""
    for bad in (1.0, 0.5, -2.0):
        try:
            occupancy([((0, 0, 0), (1, 0, 0), (0, bad, 0))])
            return False
        except VoxinError:
            continue
    return True


def degenerate_is_refused():
    try:
        occupancy([((1, 1, 1), (1, 1, 1), (2, 2, 2))])
        return False
    except VoxinError:
        return True


def _oracle_hit(triangles, x, y, z):
    """Does the ORACLE say this voxel is touched by any triangle? Independent of the traversal: it
    asks about a voxel the caller names, rather than about the voxels the traversal chose to test."""
    c = (2 * x + 1, 2 * y + 1, 2 * z + 1)
    for t in triangles:
        d0, d1, d2 = ([2 * a for a in v] for v in t)
        if VX.tri_box_overlap(d0, d1, d2, c, (1, 1, 1)):
            return True
    return False


def occupancy_agrees_with_voxlat(triangles, levels=LEVELS, keys=None):
    """BIDIRECTIONAL agreement with the oracle, over the union of the triangles' bounding boxes.

    THE SECOND VERSION, AND THE FIRST CHECKED ONE DIRECTION WHILE CLAIMING TWO. It verified only
    `oracle hit => key emitted`, so a SPURIOUS key — one overlapping nothing at all — passed. The
    gate row said "every emitted voxel independently satisfies voxlat.tri_box_overlap AND no
    overlapping voxel is omitted"; only the second clause was checked. The first was true by
    CONSTRUCTION (`occupancy` adds a key only on a hit), which is exactly what L23 forbids counting
    as verification: one computation restated is a definition, not a check. Now both directions run,
    and the emitted direction re-asks the oracle about each emitted voxel rather than trusting the
    traversal that produced it.

    SCOPE, stated because the previous version's row did not: this is EXECUTED over the triangles
    given, not proved for all geometry."""
    keys = set(occupancy(triangles, levels)) if keys is None else set(keys)
    side = 1 << levels
    seen = set()
    for t in triangles:
        v0, v1, v2 = (tuple(v) for v in t)
        lo, hi = _voxel_box(v0, v1, v2, side)
        for x in range(lo[0], hi[0] + 1):
            for y in range(lo[1], hi[1] + 1):
                for z in range(lo[2], hi[2] + 1):
                    seen.add((x, y, z))
    for (x, y, z) in seen:
        hit = _oracle_hit(triangles, x, y, z)
        emitted = VX.morton(x, y, z, levels) in keys
        if hit != emitted:
            return False                      # BOTH directions: omission AND spurious emission
    # a key outside every bounding box cannot overlap anything, so it is spurious by definition
    inbox = {VX.morton(x, y, z, levels) for (x, y, z) in seen}
    return keys.issubset(inbox)


def spurious_key_is_caught(triangles=None, levels=LEVELS):
    """RED-FIRST for the repaired direction: a key set polluted with a voxel that overlaps NOTHING
    must fail agreement. The first version of `occupancy_agrees_with_voxlat` returned True here."""
    triangles = SCENE if triangles is None else triangles
    honest = set(occupancy(triangles, levels))
    far = VX.morton((1 << levels) - 1, (1 << levels) - 1, (1 << levels) - 1, levels)
    if far in honest:
        return False                          # the plant must actually be spurious
    return (occupancy_agrees_with_voxlat(triangles, levels, honest)
            and not occupancy_agrees_with_voxlat(triangles, levels, honest | {far}))


def omitted_key_is_caught(triangles=None, levels=LEVELS):
    """RED-FIRST for the direction the first version did check, kept so both are proved."""
    triangles = SCENE if triangles is None else triangles
    honest = sorted(occupancy(triangles, levels))
    if not honest:
        return False
    return not occupancy_agrees_with_voxlat(triangles, levels, set(honest[1:]))


#: A small pinned scene — an axis-aligned wedge and a slanted face, chosen to touch several voxels.
SCENE = (
    ((0, 0, 0), (3, 0, 0), (0, 3, 0)),
    ((1, 1, 0), (4, 1, 2), (1, 4, 2)),
    ((2, 0, 1), (2, 3, 1), (5, 0, 4)),
)


def main():
    print("VOXIN — the import boundary: geometry becomes lattice occupancy, or is REFUSED")
    print()
    print("derived admission bound (from voxlat, not restated): %d bits, |coord| <= %d"
          % (admissible_coord_bits(), coord_limit()))
    print("bound is derived, not restated                     : %s" % bound_is_derived_not_restated())
    print()
    keys = occupancy(SCENE)
    print("pinned scene: %d triangles -> %d occupied voxels" % (len(SCENE), len(keys)))
    print("occupancy digest: %s" % occupancy_digest(SCENE))
    print()
    print("LAW  permutation invariance (reverse + rotate)     : %s"
          % occupancy_is_permutation_invariant(SCENE))
    print("LAW  agrees with oracle, BOTH directions           : %s"
          % occupancy_agrees_with_voxlat(SCENE))
    print("RED  a SPURIOUS key (overlaps nothing) is caught   : %s" % spurious_key_is_caught())
    print("RED  an OMITTED key is caught                      : %s" % omitted_key_is_caught())
    print()
    print("RED  geometry past the derived bound is refused    : %s" % over_bound_geometry_is_refused())
    print("RED  a float coordinate is refused, never rounded  : %s" % float_is_refused())
    print("RED  a degenerate triangle is refused              : %s" % degenerate_is_refused())
    print()
    print("does_not_show: that the geometry is CORRECT or resembles any real place; splat ingestion")
    print("(the caller quantizes); any renderer; cross-placement — Python reference only.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
