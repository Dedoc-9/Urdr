# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""voxevent (URDRVXE1) — DOES THE VISIBLE SURFACE GROW WITH THE GEOMETRY, OR WITH THE INCIDENCES?

THE QUESTION, AND WHY IT IS ASKED HERE RATHER THAN OF THE RENDERER. A rasteriser's cost scales with
primitives. The thing a camera can actually observe is a lower envelope, and Sharir's bound puts the
complexity of the lower envelope of n surface patches in three dimensions at O(n^(2+eps)) while the
arrangement of viewpoints above it is degree six or worse — tight at Theta(n^4 k^2) orthographic and
Theta(n^6 k^3) perspective for k convex polyhedra of total complexity n (Aronov, Broennimann,
Halperin and Schiffenbauer, 2001). The gap between those two is the only compression axis worth
building an architecture on, and nothing in this tree had measured where a real scene sits in it.

THIS MODULE READS THE ORACLE AND NEVER THE RASTERISER. That is not fastidiousness. `voxmicro`
measured 2040 pixels the reference still awards to faces no exterior camera can see, so a
compression law derived from the rasteriser today would be a compression law about a wrong answer.
`voxray.first_hit` is audited and qualified, takes an occupancy and a lattice as parameters, and
produces voxel/face/t — so every number below is a property of the WORLD and the CAMERA.

THE INSTRUMENT IS A SUBDIVISION LADDER, AND IT IS EXACT. Splitting every solid cell into s^3 cells
of the same material multiplies primitives by s^3 and moves NOT ONE WORLD POINT: the solid region is
the same set, so the first entry into it is the same entry, at the same parameter, through the same
face. `the_subdivision_moves_no_point` asserts exactly that across all four scales, and it is what
makes the ladder an instrument rather than four unrelated scenes. It also has a trap in it worth
writing down: `first_hit` returns an UNREDUCED rational whose representation depends on the cell
size, so two equal parameters compare unequal as tuples. Every comparison here is by cross
multiplication, and the first version of the probe was wrong in exactly that way.

WHAT IS PREDICTED, WRITTEN BEFORE THE LADDER WAS RUN:
    P1  the entry point, face and containing coarse cell are identical at every scale        (exact)
    P2  primitives(8) / primitives(1) == 512                                                 (exact)
    P3  visible faces grow like s^2 — the ratio at s = 8 lands in [30, 70]
    P4  merged regions grow by less than 10x while primitives grow by 512x
    P5  a run of k coplanar faces shows exactly 2(k+1) distinct projected corners
    P6  a voxel seen corner-on has a projected point where three visible faces meet
    P7  exact simultaneous plane crossings occur, and the oracle's tiebreak among them is
        UNDECLARED — it is whichever axis has the lowest index

P3 MISSED, AND THE REASON IS WORTH MORE THAN THE PREDICTION WAS. Visible faces grew 22.4x, not the
predicted 30-70, and the shortfall is not geometry: a frame has W*H rays and no more, so the number
of DISTINCT faces a census can observe is capped by the ray budget however fine the lattice becomes.
The hit count is identical at every scale — 46685 over the eight frames, the same rays finding the
same solid — while the share of hits landing on a distinct face climbs from 1.7% to 37.9%. The
ladder is therefore measuring the SAMPLER as much as the scene at its far end, which is the same
defect `sealframe-cost-surface` found when it held scene complexity still and varied only
resolution; this one holds resolution still and varies only complexity. The clean rung is the FIRST
one: eight times the primitives moved the merged visible regions by three per cent, measured where
the visible set still covers each face densely. That is the result. The 512x figure is reported and
is not the claim.

TWO MORE OF THE SEVEN MISSED, AND BOTH ARE RECORDED WHERE THEY HAPPENED RATHER THAN SMOOTHED AWAY. P5's
wall camera stood too close and clipped the wall the count was about, so the scene now carries the
visibility precondition it always assumed. P7 was asserted about the wrong thing entirely: a tie
decides which axis STEPS, not which face the eventual hit reports, and a ray that ties at every step
alternates until something stops it. The convention is only observable where the tie itself resolves
the hit, which is what the constructed pair now does — and doing it properly turned the convention
from a labelling question into a REACHABILITY one, because the losing candidate is not merely named
differently, it is never entered.

MERGED REGIONS ARE MEASURED, NOT BUILT. The merge — coplanar, same material, edge-adjacent, taken
to connected components — is greedy meshing's own equivalence relation, and this module computes it
only to COUNT it. Letting the merged representation become the thing rendered is the reduction
redefining the observable, which is the circularity `voxref` was frozen to prevent. The relation is
defined on the VISIBLE SET alone and knows nothing about how the world was subdivided, so it cannot
be accused of finding the structure it was handed.

does_not_show: anything about performance — no renderer runs here at all. Any claim that a
measured growth rate is a BOUND: Zhang, Everett, Lazard, Weibel and Whitesides (2008) measured the
3D visibility skeleton at roughly C*k*sqrt(nk) against a proven tight worst case of Theta(n^2 k^2),
and observing sparsity in a scene family says nothing about the family you did not build. That is
why the degeneracy scenes exist and why they are the part of this rung with a novelty claim
attached; it is still a measurement and not a theorem. And nothing here is a certificate: counting
how few regions the visible surface has is not the same as producing a witness that proves the rest
invisible, which is the rung after the reference repair.

falsifier: break the subdivision map and `the_subdivision_moves_no_point` reddens; declare a
degeneracy scene's corner count wrong and `voxevent-degeneracy` reddens; and the merge relation is
shown to BITE by a control that merges nothing, because a relation that merged everything would
report one region for any scene at all.
"""
import hashlib
import os
import sys as _sys

_HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(_HERE))
if _HERE not in _sys.path:
    _sys.path.insert(0, _HERE)

import voxref as VR                                          # noqa: E402
import voxray as VX                                          # noqa: E402
import voxmicro as VM                                        # noqa: E402

MAGIC = b"URDRVXE1"

Q = VR.Q
HALF = Q // 2

#: DECLARED — the subdivision ladder. 8 is the last scale whose cell size stays an integer at
#: Q = 256 while leaving room for the lattice bounds, and 512x primitives is enough of a lever.
SCALES = (1, 2, 4, 8)

#: The origin semantics `voxmicro` decided against a law, referenced rather than re-chosen.
ORIGIN = VM.CORRESPONDENCE_ORIGIN

#: THE ORACLE'S UNDECLARED TIEBREAK, NAMED HERE. When a ray crosses two or three lattice planes at
#: exactly the same parameter — it enters through an edge or a corner rather than through a face —
#: `voxray.first_hit` compares with a strict `<` and therefore keeps the FIRST axis it examined.
#: That is a convention, not a derivation, and a different one would report a different face at
#: exactly those rays. It is asserted below and its population is counted, so the convention is
#: visible and its blast radius is a number.
TIE_RULE = "lowest axis index wins a simultaneous crossing"


class VoxeventError(Exception):
    """VOXEVENT-REFUSE — a scale, a scene or a record this module will not pretend to read."""


# ---- the subdivision ladder --------------------------------------------------------------------
def lattice(s):
    """(extent, cell size) at scale s. The world's physical extent is unchanged: N*Q == (N*s)*(Q/s)."""
    if s not in SCALES:
        raise VoxeventError("VOXEVENT-REFUSE: no declared scale %r" % (s,))
    if Q % s:
        raise VoxeventError("VOXEVENT-REFUSE: scale %d does not divide the cell size" % s)
    return VR.N * s, Q // s


def occupancy(s):
    """The SAME solid region on a finer lattice: a subcell is solid iff its parent is."""
    def occ(x, y, z):
        return VR.solid(x // s, y // s, z // s)
    return occ


def solid_cells(s):
    """DERIVED, never enumerated at scale 8 — 411136 cells is a count, not a list."""
    base = sum(1 for x in range(VR.N) for y in range(VR.N) for z in range(VR.N)
               if VR.solid(x, y, z))
    return base * s ** 3


def primitives(s):
    return solid_cells(s) * 6


def _teq(a, b):
    """Rational equality by cross multiplication. `first_hit` returns UNREDUCED pairs whose
    representation depends on the cell size, so tuple equality is the wrong test and was the
    first version of this check."""
    return a[0] * b[1] == b[0] * a[1]


#: A declared, strided ray sample — the ladder's invariant is checked on this rather than on every
#: pixel of every frame, because 4 scales x 8 frames x 6912 rays is a census and not a law.
def _ladder_rays():
    out = []
    for frame in (3, 4, 5, 7):
        _n, eye, fwd = VR.TRACE[frame]
        for py in range(0, VR.H, 5):
            for px in range(0, VR.W, 5):
                out.append((eye, VX.ray_for_pixel(eye, fwd, px, py)))
    return out


def the_subdivision_moves_no_point():
    """P1 — THE LADDER IS AN INSTRUMENT, PROVED BEFORE IT IS READ.

    Subdividing a solid cell into s^3 cells of the same material changes the primitive count and
    nothing else about the scene: the solid region is the same set of world points, so a ray's
    first entry into it is the same point, at the same parameter, through the same face, and the
    fine cell reporting it must be a subcell of the coarse one. Anything less and the four arms of
    the ladder would be four different scenes wearing one name.
    """
    for eye, d in _ladder_rays():
        base = VX.first_hit(eye, d, None, ORIGIN)
        for s in SCALES[1:]:
            n, q = lattice(s)
            hit = VX.first_hit(eye, d, occupancy(s), ORIGIN, n, q)
            if (base is None) != (hit is None):
                return False
            if base is None:
                continue
            if hit[1] != base[1] or not _teq(base[2], hit[2]):
                return False
            if tuple(c // s for c in hit[0]) != base[0]:
                return False
    return True


def a_shifted_subdivision_is_caught():
    """THE PLANT: an occupancy that subdivides WRONG — off by one cell — must break the invariant,
    or the law above would pass for any map at all."""
    def bad(x, y, z):
        return VR.solid((x + 1) // 2, y // 2, z // 2)
    n, q = lattice(2)
    for eye, d in _ladder_rays()[:200]:
        base = VX.first_hit(eye, d, None, ORIGIN)
        hit = VX.first_hit(eye, d, bad, ORIGIN, n, q)
        if (base is None) != (hit is None):
            return True
        if base is None:
            continue
        if hit[1] != base[1] or not _teq(base[2], hit[2]):
            return True
        if tuple(c // 2 for c in hit[0]) != base[0]:
            return True
    return False


# ---- what the camera can actually see ------------------------------------------------------------
def visible_set(eye, fwd, s, occ=None, n=None, q=None):
    """The distinct (cell, face) the oracle reports over a whole frame, and the ray census.

    Returns (faces, hits, simultaneous). A SIMULTANEOUS crossing is a hit whose entry point lies
    exactly on two or three lattice planes the ray is actually crossing — the edge and corner
    cases, derived from the point rather than read out of the traversal's internals.
    """
    if occ is None:
        occ, (n, q) = occupancy(s), lattice(s)
    faces, hits, sim = set(), 0, 0
    for py in range(VR.H):
        for px in range(VR.W):
            d = VX.ray_for_pixel(eye, fwd, px, py)
            hit = VX.first_hit(eye, d, occ, ORIGIN, n, q)
            if hit is None or hit[1] is None:
                continue
            hits += 1
            faces.add((hit[0], hit[1]))
            pt = VX.point_at(eye, d, hit[2])
            on = 0
            for axis in range(3):
                if d[axis] == 0:
                    continue
                num, den = pt[axis]
                if num % (q * den) == 0:
                    on += 1
            if on >= 2:
                sim += 1
    return faces, hits, sim


def merged_regions(faces):
    """MAXIMAL CONNECTED COPLANAR SAME-MATERIAL REGIONS of the visible surface, by union-find.

    Two visible faces merge iff they carry the same face index — which fixes the normal AND the
    palette entry, so material equality is structural rather than checked — and their cells are
    adjacent by one step along an axis lying IN that face's plane, which forces the shared plane.
    The relation reads only the visible set: it is given no knowledge of the subdivision, so it
    cannot recover a structure it was handed.
    """
    order = sorted(faces)
    idx = {f: i for i, f in enumerate(order)}
    parent = list(range(len(order)))

    def find(a):
        while parent[a] != a:
            parent[a] = parent[parent[a]]
            a = parent[a]
        return a

    for cell, fi in order:
        axis = fi // 2
        for other in range(3):
            if other == axis:
                continue
            nb = list(cell)
            nb[other] += 1
            key = (tuple(nb), fi)
            if key in idx:
                ra, rb = find(idx[(cell, fi)]), find(idx[key])
                if ra != rb:
                    parent[ra] = rb
    return len({find(i) for i in range(len(order))})


def a_relation_that_merges_nothing_is_not_this_one():
    """THE CONTROL. A merge relation that joined nothing would report one region per face and a
    relation that joined everything would report one region for any scene; the live relation must
    sit strictly between, on a frame known to contain a flat surface."""
    _n, eye, fwd = VR.TRACE[7]
    faces, _h, _s = visible_set(eye, fwd, 1)
    got = merged_regions(faces)
    return 1 < got < len(faces)


# ---- the incidence census -------------------------------------------------------------------------
def projected_corners(eye, fwd, faces, q):
    """(corner instances, distinct screen positions, maximum faces meeting at one position).

    Measured in the renderer's own screen space, using the declared camera and the declared
    projection, because a degeneracy is a fact about where things LAND. No coverage test, no depth
    buffer and no framebuffer is consulted — this counts incidences, not pixels.
    """
    m = VR.basis(fwd)
    cx, cy = VR.W // 2, VR.H // 2
    at = {}
    total = 0
    for cell, fi in faces:
        for a, b, c in VR.FACES[fi][1]:
            v = ((cell[0] + a) * q, (cell[1] + b) * q, (cell[2] + c) * q)
            cam = VR._project(v, eye, m)
            if cam[1] < VR.NEAR:
                continue
            total += 1
            p = (cx + cam[0] * VR.FOCAL // cam[1], cy - cam[2] * VR.FOCAL // cam[1])
            at.setdefault(p, set()).add((cell, fi))
    return total, len(at), max((len(v) for v in at.values()), default=0)


# ---- the degeneracy families ----------------------------------------------------------------------
C = (5, 5, 5)
CC = tuple(c * Q + HALF for c in C)
RUN_K = 5
WALL_K = 4


def _run_cells(k):
    return tuple((5, 5 + i, 5) for i in range(k))


def _wall_cells(k):
    return tuple((6, 4 + i, 4 + j) for i in range(k) for j in range(k))


#: DECLARED — four incidence-degenerate families, each isolating one way a supposedly sparse
#: geometric representation becomes dense, each with the count predicted before it ran.
DEGENERACIES = (
    #: COLLINEAR AND COINCIDENT PROJECTED VERTICES. k coplanar faces in a row share every interior
    #: corner with their neighbour, so 4k corner instances collapse onto 2(k+1) distinct screen
    #: positions — exactly, and independently of the projection, because the sharing is structural.
    {"name": "run", "cells": _run_cells(RUN_K),
     "eye": (6 * Q + 12 * Q, (5 + RUN_K // 2) * Q + HALF, CC[2]), "fwd": (-1, 0, 0),
     "expect": ("coplanar_corners", 0, 2 * (RUN_K + 1)), "visible_faces": RUN_K},
    #: MULTI-FACE SHARED PROJECTED EVENTS. A k x k coplanar wall has (k+1)^2 distinct corners for
    #: k^2 faces, and every INTERIOR corner is shared by four of them — the densest fan-in a single
    #: plane can produce.
    #: THE FIRST CAMERA FOR THIS SCENE WAS TOO CLOSE and the prediction read 20 against 25 — the
    #: wall subtended 96 pixels of a 72-pixel-high frame, so a whole row of faces never appeared in
    #: the visible set and five of its corners with them. The count is a statement about a wall the
    #: camera can SEE, so the scene carries the visibility precondition explicitly rather than the
    #: claim being relaxed to whatever the clipped view produced.
    {"name": "wall", "cells": _wall_cells(WALL_K),
     "eye": ((7 + 10) * Q, (4 + WALL_K // 2) * Q + HALF, (4 + WALL_K // 2) * Q + HALF),
     "fwd": (-1, 0, 0),
     "expect": ("coplanar_corners", 0, (WALL_K + 1) ** 2), "visible_faces": WALL_K ** 2},
    #: CONCURRENT PROJECTED EDGES. Seen down its body diagonal a cube shows three faces meeting at
    #: one corner, so three projected edges pass through a single screen point.
    {"name": "corner_fan", "cells": (C,),
     "eye": (CC[0] + 5 * Q, CC[1] + 5 * Q, CC[2] + 5 * Q), "fwd": (-1, -1, -1),
     "expect": ("fan_in", None, 3)},
    #: EXACT DEPTH TIES, which in the oracle's vocabulary are SIMULTANEOUS PLANE CROSSINGS. A block
    #: viewed along a lattice diagonal sends rays into edges and corners rather than into faces.
    {"name": "diagonal_block",
     "cells": tuple((5 + i, 5 + j, 5 + k) for i in range(2) for j in range(2) for k in range(2)),
     "eye": (CC[0] + 6 * Q, CC[1] + 6 * Q, CC[2] + 6 * Q), "fwd": (-1, -1, -1),
     "expect": ("simultaneous_at_least", None, 1)},
)

DEGENERACY_NAMES = tuple(d["name"] for d in DEGENERACIES)


def degeneracy(name):
    for d in DEGENERACIES:
        if d["name"] == name:
            return d
    raise VoxeventError("VOXEVENT-REFUSE: no degeneracy named %r" % name)


def _occ_of(cells):
    s = set(cells)
    return lambda x, y, z: (x, y, z) in s


def degeneracy_reading(d):
    """(faces, hits, simultaneous, corner instances, distinct corners, fan-in, coplanar distinct)."""
    occ = _occ_of(d["cells"])
    faces, hits, sim = visible_set(d["eye"], d["fwd"], 1, occ, VR.N, Q)
    total, distinct, fan = projected_corners(d["eye"], d["fwd"], faces, Q)
    axis_faces = {f for f in faces if f[1] == d["expect"][1]} if d["expect"][0] == \
        "coplanar_corners" else set()
    _t, coplanar_distinct, _f = projected_corners(d["eye"], d["fwd"], axis_faces, Q)
    return faces, hits, sim, total, distinct, fan, coplanar_distinct


def failing_degeneracies():
    bad = []
    for d in DEGENERACIES:
        kind, _arg, want = d["expect"]
        faces, _h, sim, _t, _dist, fan, coplanar = degeneracy_reading(d)
        if not faces:
            bad.append((d["name"], "renders nothing"))
            continue
        if "visible_faces" in d and len(faces) != d["visible_faces"]:
            bad.append((d["name"], "visible faces %d != %d" % (len(faces), d["visible_faces"])))
            continue
        if kind == "coplanar_corners" and coplanar != want:
            bad.append((d["name"], "coplanar corners %d != %d" % (coplanar, want)))
        elif kind == "fan_in" and fan < want:
            bad.append((d["name"], "fan-in %d < %d" % (fan, want)))
        elif kind == "simultaneous_at_least" and sim < want:
            bad.append((d["name"], "simultaneous %d < %d" % (sim, want)))
    return bad


def every_degeneracy_meets_its_prediction():
    return not failing_degeneracies()


def a_wrong_corner_count_is_caught():
    """THE PLANT: the run's prediction is structural, so a scene with one more face must not
    satisfy the count written for k."""
    d = dict(degeneracy("run"))
    d["cells"] = _run_cells(RUN_K + 1)
    _f, _h, _s, _t, _dist, _fan, coplanar = degeneracy_reading(d)
    return coplanar != d["expect"][2]


# ---- the oracle's tiebreak, named and counted -----------------------------------------------------
#: A CONSTRUCTED ray that ties on its FIRST step, which is the only place the convention is
#: observable. It starts exactly on the x = 0 and y = 0 planes and travels along their diagonal, so
#: `tmax` is equal on both axes; with BOTH candidate cells solid the axis the traversal picks is the
#: face it reports.
#:
#: THE FIRST VERSION OF THIS ASSERTED THE WRONG THING. It fired the same ray into the frozen world
#: and demanded an x face, and got a y face — correctly, because the tie decides which axis STEPS
#: first, not which axis is standing on the cell the ray eventually reaches. A ray that ties at
#: every step alternates, and by the time it reaches solid the reported face is whichever step
#: happened to land. The convention is only visible where the tie itself resolves the hit.
TIE_RAY = ((0, 0, 5 * Q + HALF), (1, 1, 0))
TIE_BOTH = ((1, 0, 5), (0, 1, 5))          #: both candidates solid: the tie decides
TIE_ONE = ((0, 1, 5),)                     #: only the y candidate: the tie cannot decide


def tie_ray_face(cells):
    hit = VX.first_hit(TIE_RAY[0], TIE_RAY[1], _occ_of(cells), ORIGIN)
    return None if hit is None else hit[1]


def the_tiebreak_is_the_declared_convention():
    """P7 — with both candidates solid the simultaneous crossing resolves on the LOWEST AXIS INDEX,
    so the ray enters through an x face (index 1, the -x face). Asserted so the convention is a row
    rather than an accident, and so changing `first_hit`'s comparison reddens here instead of
    moving a number quietly."""
    return tie_ray_face(TIE_BOTH) == 1 and TIE_RULE.startswith("lowest axis index")


def a_broken_tie_misses_the_other_candidate():
    """THE CONTROL, AND IT IS SHARPER THAN THE ONE THAT WAS PLANNED. Removing the x candidate was
    expected to leave the ray reporting the y face instead. It reports NOTHING: because the tie
    sends the traversal along x first, the ray leaves the x = 0 column immediately and never enters
    the y candidate at all.

    THAT RAISES THE STAKES OF THE CONVENTION RATHER THAN CONFIRMING IT. An undeclared tiebreak that
    only relabelled a face would cost a label; this one decides WHICH CELL IS REACHED, so the
    opposite convention makes a different voxel visible along the same ray. It is a convention with
    a geometric consequence, and it is now written down, exercised, and counted."""
    return VX.first_hit(TIE_RAY[0], TIE_RAY[1], _occ_of(TIE_ONE), ORIGIN) is None


# ---- the record --------------------------------------------------------------------------------
RECORD = os.path.join("spec", "attest", "voxref-incidence.txt")
COLUMNS = ("solid_cells", "primitives", "visible_faces", "merged_regions", "hits",
           "simultaneous", "corner_instances", "corners_distinct", "max_fan_in")


def grid():
    rows = [("frame", "%d:%s" % (i, n), s)
            for i, (n, _e, _f) in enumerate(VR.TRACE) for s in SCALES]
    rows += [("degeneracy", d["name"], 1) for d in DEGENERACIES]
    return rows


def reading(kind, name, s):
    if kind == "frame":
        _n, eye, fwd = VR.TRACE[int(name.split(":")[0])]
        n, q = lattice(s)
        faces, hits, sim = visible_set(eye, fwd, s)
        cells = solid_cells(s)
    else:
        d = degeneracy(name)
        eye, fwd, q = d["eye"], d["fwd"], Q
        faces, hits, sim = visible_set(eye, fwd, 1, _occ_of(d["cells"]), VR.N, Q)
        cells = len(d["cells"])
    total, distinct, fan = projected_corners(eye, fwd, faces, q)
    return {"solid_cells": cells, "primitives": cells * 6, "visible_faces": len(faces),
            "merged_regions": merged_regions(faces), "hits": hits, "simultaneous": sim,
            "corner_instances": total, "corners_distinct": distinct, "max_fan_in": fan}


def generate():
    rows = ["# URDRVXE1 incidence and visible-surface census — one row per (kind, name, scale),",
            "# emitted by voxevent.generate(), committed as an artifact, re-derived by the gate.",
            "# columns: kind name scale " + " ".join(COLUMNS),
            "# world %s" % VR.world_digest(),
            "# ORACLE-SIDE ONLY. No renderer runs here: every figure is a property of the world",
            "# and the camera, read through voxray.first_hit. The subdivision ladder multiplies",
            "# primitives by s^3 while moving no world point, so the four arms of a frame are the",
            "# same scene at four representations and the growth rates between them are the",
            "# measurement. Merged regions are COUNTED, never built."]
    for kind, name, s in grid():
        c = reading(kind, name, s)
        rows.append("%s %s %d %s" % (kind, name, s, " ".join(str(c[k]) for k in COLUMNS)))
    return "\n".join(rows) + "\n"


def _read():
    with open(os.path.join(ROOT, RECORD), encoding="utf-8") as fh:
        return fh.read()


def parse(text=None):
    if text is None:
        text = _read()
    rows, world = [], None
    for ln in text.split("\n"):
        ln = ln.strip()
        if not ln:
            continue
        if ln.startswith("#"):
            if ln.startswith("# world "):
                world = ln.split()[2]
            continue
        f = ln.split()
        if len(f) != 3 + len(COLUMNS):
            raise VoxeventError("VOXEVENT-REFUSE: a row with %d fields" % len(f))
        c = dict(zip(COLUMNS, (int(v) for v in f[3:])))
        if c["primitives"] != c["solid_cells"] * 6:
            raise VoxeventError("VOXEVENT-REFUSE: a row whose primitives do not count its cells")
        if c["merged_regions"] > c["visible_faces"]:
            raise VoxeventError("VOXEVENT-REFUSE: a row with more regions than faces")
        rows.append((f[0], f[1], int(f[2]), c))
    if world is None:
        raise VoxeventError("VOXEVENT-REFUSE: the record names no world digest")
    if not rows:
        raise VoxeventError("VOXEVENT-REFUSE: the record has no rows")
    return world, rows


def the_record_is_exactly_the_derived_grid():
    _w, rows = parse()
    return [r[:3] for r in rows] == grid()


def the_record_names_this_world():
    return parse()[0] == VR.world_digest()


#: What the gate recomputes in full every run — one frame at one scale, and every degeneracy.
BIND = ("frame", "%d:%s" % (4, VR.TRACE[4][0]), 2)


def the_record_is_bound_to_the_live_code():
    _w, rows = parse()
    want = next(c for k, n, s, c in rows if (k, n, s) == BIND)
    if reading(*BIND) != want:
        return False
    for d in DEGENERACIES:
        want = next(c for k, n, _s, c in rows if (k, n) == ("degeneracy", d["name"]))
        if reading("degeneracy", d["name"], 1) != want:
            return False
    return True


def ladder(rows=None):
    """The growth rates, per scale, summed over the declared frames."""
    if rows is None:
        _w, rows = parse()
    out = {}
    for kind, _n, s, c in rows:
        if kind != "frame":
            continue
        a = out.setdefault(s, dict.fromkeys(COLUMNS, 0))
        for k in COLUMNS:
            a[k] += c[k]
    return out


def growth(rows=None):
    """(primitive ratio, visible-face ratio, merged-region ratio) from scale 1 to the last scale."""
    lad = ladder(rows)
    lo, hi = lad[SCALES[0]], lad[SCALES[-1]]
    return (hi["primitives"] / lo["primitives"],
            hi["visible_faces"] / lo["visible_faces"],
            hi["merged_regions"] / lo["merged_regions"])


def the_primitive_ladder_is_exact():
    """P2 — 512x, by construction rather than by measurement, and checked because a ladder whose
    lever is not the declared size measures a different experiment."""
    return abs(growth()[0] - float(SCALES[-1] ** 3)) < 1e-9


def the_ordering_holds_at_every_scale():
    """THE ONE DIRECTIONAL CLAIM: merged regions grow slower than visible faces, which grow slower
    than primitives — at every rung of the ladder, not merely end to end. Nothing here says any of
    the three is a bound, and nothing says the behaviour continues past s = 8."""
    lad = ladder()
    lo = lad[SCALES[0]]
    for s in SCALES[1:]:
        hi = lad[s]
        m = hi["merged_regions"] / lo["merged_regions"]
        v = hi["visible_faces"] / lo["visible_faces"]
        p = hi["primitives"] / lo["primitives"]
        if not m < v < p:
            return False
    return True


def the_first_rung_is_flat():
    """THE CLEANEST DATA POINT IN THE LADDER, and deliberately the smallest one.

    From s = 1 to s = 2 the primitive count multiplies by EIGHT and the merged visible regions
    move by three per cent. That rung is the one where the sampler is least stressed — the visible
    set still covers each face densely — so it is the only place the merged count is measuring the
    SURFACE rather than the sampling of it. The wider 512x figure is reported and is NOT the claim.
    """
    lad = ladder()
    return lad[2]["merged_regions"] / lad[1]["merged_regions"] < 1.10


def the_census_is_censored_by_the_sampler():
    """THE CONFOUND, ASSERTED AS A ROW RATHER THAN LEFT AS A FOOTNOTE — and it is the same defect
    `sealframe-cost-surface` found one arc over, arriving from the other direction.

    A frame has W*H rays and no more, so a ray budget is a hard ceiling on how many distinct faces
    a census can ever observe. Refining the lattice therefore does not measure the surface past the
    point where the visible set stops covering it: the hit count is IDENTICAL at every scale (same
    geometry, same rays), while the fraction of hits landing on distinct faces climbs from 1.7% to
    37.9%. The ladder is measuring the sampler as much as the scene, the growth exponents are not
    clean geometry, and a compression claim taken from the far end of this ladder would be a claim
    about the framebuffer. THE SECOND AXIS — resolution — IS WHAT THIS RUNG DOES NOT HAVE, and
    raising W and H is not available here because they are part of the frozen contract.
    """
    lad = ladder()
    hits = {lad[s]["hits"] for s in SCALES}
    if len(hits) != 1:
        return False                          # the rays must be the same rays, or nothing compares
    lo = lad[SCALES[0]]["visible_faces"] / lad[SCALES[0]]["hits"]
    hi = lad[SCALES[-1]]["visible_faces"] / lad[SCALES[-1]]["hits"]
    return hi > 5.0 * lo


def a_tampered_row_refuses():
    text = _read()
    for ln in text.split("\n"):
        if ln and not ln.startswith("#"):
            f = ln.split()
            f[3] = str(int(f[3]) + 1)          # cells move, primitives do not
            text = text.replace(ln, " ".join(f), 1)
            break
    try:
        parse(text)
    except VoxeventError:
        return True
    return False


def told():
    prim, vis, merged = growth()
    lad = ladder()
    rays = len(VR.TRACE) * VR.W * VR.H
    return ("8x the primitives moves the merged visible regions by %.0f%% (%d -> %d) at the rung "
            "where the sampler is unstressed; across the whole ladder primitives multiply %.0fx "
            "(%d -> %d) while visible faces grow %.1fx and merged regions %.2fx, BUT the hit count "
            "is identical at every scale (%d) and the share of hits on a distinct face climbs "
            "%.1f%% -> %.1f%%, so the far end measures the sampler; %.1f%% of the %d rays enter "
            "through an edge or a corner, where an UNDECLARED tiebreak decides which cell is "
            "reached at all"
            % (100.0 * (lad[2]["merged_regions"] / lad[1]["merged_regions"] - 1.0),
               lad[1]["merged_regions"], lad[2]["merged_regions"],
               prim, lad[1]["primitives"], lad[8]["primitives"], vis, merged, lad[1]["hits"],
               100.0 * lad[1]["visible_faces"] / lad[1]["hits"],
               100.0 * lad[8]["visible_faces"] / lad[8]["hits"],
               100.0 * lad[8]["simultaneous"] / rays, rays))


def scene_case(name):
    if name == "ladder":
        _w, rows = parse()
        return repr((ladder(rows), growth(rows), SCALES, solid_cells(1)))
    if name == "degeneracy":
        return repr([(d["name"], d["cells"][:4], d["eye"], d["fwd"], d["expect"],
                      degeneracy_reading(d)[1:]) for d in DEGENERACIES])
    if name == "ties":
        return repr((TIE_RULE, TIE_RAY, TIE_BOTH, TIE_ONE, tie_ray_face(TIE_BOTH),
                     VX.first_hit(TIE_RAY[0], TIE_RAY[1], _occ_of(TIE_ONE), ORIGIN)))
    raise VoxeventError("VOXEVENT-REFUSE: no scene named %r" % name)


def scene_result(name):
    return hashlib.sha256(MAGIC + b"|" + name.encode() + b"|"
                          + scene_case(name).encode()).hexdigest()


SCENES = ("ladder", "degeneracy", "ties")


def golden(name):
    with open(os.path.join(_HERE, "conformance_voxevent.txt"), encoding="utf-8") as fh:
        for ln in fh:
            ln = ln.strip()
            if ln and not ln.startswith("#"):
                nm, dig = ln.split()
                if nm == name:
                    return dig
    raise VoxeventError("VOXEVENT-REFUSE: no golden named %r" % name)
