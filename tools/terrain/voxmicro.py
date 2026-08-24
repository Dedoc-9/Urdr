# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""voxmicro (URDRVXM1) — QUALIFYING THE ORACLE, AND ASKING THE RASTERISER WHERE IT LOST THE FACE.

`voxray` produced a number — 87.0% correspondence with the six face windings reversed — and was
careful to call the remaining 13% an UPPER BOUND on the reference's defect rather than a
measurement of it, because up to one pixel of ray/sample offset is folded into every comparison.
An upper bound on a residue is not a diagnosis. It is a place where three different things are
still stacked on top of each other:

    * a genuine defect in the rasteriser,
    * the ~1px sampling offset the projection-inversion law measured and pinned,
    * and the frames where the oracle was answering a DIFFERENT QUESTION entirely, because the eye
      began inside solid and one whole declared frame had to be excluded by derivation.

This module takes the stack apart. Three things it does, and each is separable from the others.

FIRST, THE ORIGIN SEMANTICS, DECIDED AGAINST A LAW RATHER THAN A PREFERENCE. With the eye inside
matter, `opaque` semantics return the containing voxel with no entry face — for every pixel, at
t = 0, regardless of direction. `the_opaque_origin_is_direction_blind` proves exactly that, and it
is the disqualifying property: an oracle whose answer does not depend on the ray cannot discriminate
between two renderers, so on such a frame it is not an oracle at all. `transparent` semantics treat
the eye's OWN cell — that one cell, not the connected run it belongs to — as free space, and the
answer becomes the first face bounding the free space the ray can actually reach. That restores
direction-dependence, which is the argument, and `the_two_origins_agree_off_solid` proves the choice
changes nothing anywhere else. It also happens to agree with what the reference does from inside
matter, and that agreement is NOT the reason: a semantics adopted because it matches the renderer
under test is the circularity this whole arc exists to avoid.

SECOND, AN ABSOLUTE DEFECT DETECTOR THAT OWES THE ORACLE NOTHING. Call a face INTERIOR when the
voxel across its outward normal is also solid. Such a face is sandwiched between two solid cells,
so from any eye outside the solid set every ray reaching it must pass through one of them first.
No exterior camera can see an interior face — ever, at any resolution, under any sampling. So a
rasteriser whose winning face at some pixel is an interior one is WRONG, full stop, and the count of
such pixels is immune to every caveat that weakens a correspondence figure: no ray/sample offset can
produce it, no oracle needs to be trusted for it, and it needs no exclusions. The reference reports
14032 of them as committed and STILL 2040 with the winding reversed, which is what turns "a second
defect is real and unexplained" from an inference into a measurement.

THIRD, "WHERE DID YOU LOSE ME?". For every pixel where the two disagree, the residue stops being a
mystery and becomes a named fate. The ~1px offset is SUBTRACTED FIRST — a disagreement counts as
`sampling_shift` when the rasteriser's answer at this pixel is the oracle's answer at one of the
eight neighbours, which is the whole content of the measured bound — and it is reported as an upper
bound on how much sampling could explain, which makes every other class a LOWER bound on real
defect. What survives is traced through the reference's own pipeline: was the face never generated,
near-clipped, degenerate, backfacing, off-screen, not covered at this pixel, or covered and beaten
on depth? `unknown` must be zero, and the selftest shows that a missing branch lands there.

AND THE LABELS BECOME CLAIMS. `voxray` recorded that two of `voxref`'s eight frame names described a
world that no longer existed. Renaming them fixes those two and prevents nothing. Here every label
carries ONE checkable claim evaluated against the world by the gate, so a label that stops being
true reddens a row instead of misleading a reader — and the claim for `wall_flat` turned out to be
false as originally written too, which is the third defect the rename alone would have missed.

does_not_show: anything about performance. Any assertion that the oracle is RIGHT — it is audited
by `voxray`'s invariants and qualified here against elementary scenes with hand-checkable answers,
which is a much weaker and much more honest claim than correctness. Nothing about whether the
reversed winding is the CORRECT repair: this module measures that it is still wrong and by how
much, and repairing it belongs to the rung that re-freezes the contract. And the micro-scenes are
not a substitute for the declared trace — they are elementary geometry, deliberately trivial, and a
reduction that is right on all of them can still be wrong on a real world.

falsifier: break any scene's declared expectation and `voxmicro-scenes` reddens; disable one branch
of the fate classifier and the pixels land in `unknown`, which `voxmicro-residue` requires to be
zero; restore either of the two corrected trace labels and `voxmicro-labels` reddens; and the
interior-face detector is shown to bite on a CONSTRUCTED scene whose reference render is known to
contain the impossible answer.
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

MAGIC = b"URDRVXM1"

Q = VR.Q
HALF = Q // 2
#: Keys at or above this belong to primitives that are not faces of a voxel — the declared
#: degenerate quad, and nothing else. `_unkey` is meaningless on them and is never called.
EXTRA_KEY_BASE = VR.N ** 3 * 6


class VoxmicroError(Exception):
    """VOXMICRO-REFUSE — a scene, a label or a record this module will not pretend to read."""


def _centre(cell):
    return tuple(c * Q + HALF for c in cell)


# ---- the scenes ------------------------------------------------------------------------------
#: DECLARED — elementary geometry, one question each, every answer hand-checkable from the cell
#: list and the camera without running anything. `cells` is a subset of the SAME 12^3 lattice the
#: frozen world lives in, so the oracle's bounds and the rasteriser's projection are unchanged and
#: the only thing that varies is occupancy. `expect` is the prediction, written before the scene
#: was ever run; where a prediction was wrong the scene records the geometric reason rather than
#: being quietly edited to match the output.
C = (5, 5, 5)
CC = _centre(C)
D = 5 * Q


def _scene(name, cells, eye, fwd, expect, extra=()):
    return {"name": name, "cells": None if cells is None else tuple(cells),
            "eye": eye, "fwd": fwd, "expect": tuple(expect), "extra": tuple(extra)}


#: A quad with four identical corners: zero area under any projection. Its only job is to make the
#: `degenerate` fate reachable, so that the class is a measured zero rather than an unreached one.
DEGENERATE_QUAD = (EXTRA_KEY_BASE, VR.PALETTE[0], ((CC[0], CC[1], CC[2]),) * 4)

#: DERIVED from the world by a canonical scan and PINNED, so the record cannot move when the scan
#: changes: an empty cell with solid directly below and two clear cells ahead (standing on
#: something and able to look along it), and an empty cell with solid immediately ahead (a wall at
#: arm's length). Both are vantages the declared trace turned out not to contain — `wall_flat`
#: faces a wall three voxels away and NO frame stands on anything at all.
STANDING_PIN = (2, 2, 3)
WALLADJ_PIN = (2, 2, 7)


def derive_standing():
    for x in range(2, VR.N - 2):
        for y in range(2, VR.N - 2):
            for z in range(1, VR.N):
                if (not VR.solid(x, y, z) and VR.solid(x, y, z - 1)
                        and not VR.solid(x, y + 1, z) and not VR.solid(x, y + 2, z)):
                    return (x, y, z)
    raise VoxmicroError("VOXMICRO-REFUSE: the world contains nowhere to stand")


def derive_walladj():
    for x in range(2, VR.N - 2):
        for y in range(2, VR.N - 2):
            for z in range(1, VR.N):
                if (not VR.solid(x, y, z) and VR.solid(x + 1, y, z)
                        and not VR.solid(x, y, z + 1)):
                    return (x, y, z)
    raise VoxmicroError("VOXMICRO-REFUSE: the world contains no wall to stand beside")


def the_derived_vantages_match_their_pins():
    """The scan is DERIVED and the answer is PINNED, so a change to either is visible as a red row
    rather than as a record that silently moved."""
    return derive_standing() == STANDING_PIN and derive_walladj() == WALLADJ_PIN


MICRO = (
    # -- one voxel, one camera on each axis: the case that caught the winding defect ------------
    _scene("single_px", (C,), (CC[0] + D, CC[1], CC[2]), (-1, 0, 0),
           (("faces_exactly", (0,)), ("voxels_exactly", (C,)), ("nonempty",))),
    _scene("single_nx", (C,), (CC[0] - D, CC[1], CC[2]), (1, 0, 0),
           (("faces_exactly", (1,)), ("voxels_exactly", (C,)), ("nonempty",))),
    _scene("single_py", (C,), (CC[0], CC[1] + D, CC[2]), (0, -1, 0),
           (("faces_exactly", (2,)), ("voxels_exactly", (C,)), ("nonempty",))),
    _scene("single_ny", (C,), (CC[0], CC[1] - D, CC[2]), (0, 1, 0),
           (("faces_exactly", (3,)), ("voxels_exactly", (C,)), ("nonempty",))),
    #: THE CAMERA CANNOT LOOK ALONG ITS OWN UP AXIS. `voxref.basis` refuses a forward parallel to
    #: +z by construction, so the two z faces are never seen head-on ANYWHERE — not here and not
    #: in the declared trace. A refusal is an answer, and this scene exists so the limitation is
    #: recorded as a property of the camera model rather than discovered later as a gap.
    _scene("single_pz_refuses", (C,), (CC[0], CC[1], CC[2] + D), (0, 0, -1), (("refuses",),)),
    #: So the z faces get a near-vertical camera instead: the eye is directly above (below) the
    #: cell in x and y, tipped by one part in 64, which is inside the field of view and leaves the
    #: side faces geometrically invisible.
    _scene("single_pz", (C,), (CC[0], CC[1], CC[2] + 6 * Q), (1, 0, -64),
           (("faces_exactly", (4,)), ("voxels_exactly", (C,)), ("nonempty",))),
    _scene("single_nz", (C,), (CC[0], CC[1], CC[2] - 6 * Q), (1, 0, 64),
           (("faces_exactly", (5,)), ("voxels_exactly", (C,)), ("nonempty",))),
    # -- two voxels sharing a face on each axis: the coincident-face case ----------------------
    _scene("pair_x", (C, (6, 5, 5)), (_centre((6, 5, 5))[0] + D, CC[1], CC[2]), (-1, 0, 0),
           (("faces_exactly", (0,)), ("voxels_exactly", ((6, 5, 5),)), ("nonempty",))),
    _scene("pair_y", (C, (5, 6, 5)), (CC[0], _centre((5, 6, 5))[1] + D, CC[2]), (0, -1, 0),
           (("faces_exactly", (2,)), ("voxels_exactly", ((5, 6, 5),)), ("nonempty",))),
    _scene("pair_z", (C, (5, 5, 6)), (CC[0], CC[1], _centre((5, 5, 6))[2] + 6 * Q), (1, 0, -64),
           (("faces_exactly", (4,)), ("voxels_exactly", ((5, 5, 6),)), ("nonempty",))),
    #: The same adjacent pair seen from a general direction, where all three visible faces of the
    #: union are in play at once and the two coincident interior faces are in the middle of it.
    _scene("pair_oblique", (C, (6, 5, 5)), (CC[0] + 6 * Q, CC[1] + 6 * Q, CC[2] + 6 * Q),
           (-1, -1, -1), (("no_faces", (1, 3, 5)), ("nonempty",))),
    # -- occlusion, coplanarity, the degenerate angles -----------------------------------------
    _scene("occluder", (C, (8, 5, 5)), (_centre((8, 5, 5))[0] + D, CC[1], CC[2]), (-1, 0, 0),
           (("voxels_exactly", ((8, 5, 5),)), ("faces_exactly", (0,)), ("nonempty",))),
    _scene("coplanar", (C, (5, 6, 5)), (CC[0] + D, 6 * Q, CC[2]), (-1, 0, 0),
           (("voxels_exactly", (C, (5, 6, 5))), ("faces_exactly", (0,)), ("nonempty",))),
    #: EDGE-ON: the eye sits exactly in the plane of the cell's -z face. Neither z face can be
    #: entered from there — the +z face would need a ray descending from above it, and the -z face
    #: a ray rising from below a plane the eye is already on.
    _scene("edge_on", (C,), (CC[0] + D, CC[1], 5 * Q), (-1, 0, 0),
           (("no_faces", (4, 5)), ("nonempty",))),
    #: CORNER-ON: the body diagonal. Exactly three faces are turned towards the eye and all three
    #: must appear; a fourth would mean the oracle reported a face pointing away from the camera.
    _scene("corner_on", (C,), (CC[0] + D, CC[1] + D, CC[2] + D), (-1, -1, -1),
           (("faces_exactly", (0, 2, 4)), ("voxels_exactly", (C,)), ("nonempty",))),
    # -- a thin wall, and an aperture through it -----------------------------------------------
    _scene("thin_wall_edge_on", tuple((6, y, 5) for y in range(3, 9)),
           (6 * Q, 0 * Q + HALF, 5 * Q + HALF), (0, 1, 0),
           (("no_faces", (0, 1)), ("nonempty",))),
    _scene("aperture",
           tuple((6, y, z) for y in (4, 5, 6) for z in (4, 5, 6) if (y, z) != (5, 5))
           + ((8, 5, 5),),
           (_centre((6, 5, 5))[0] + 6 * Q, CC[1], CC[2]), (-1, 0, 0),
           (("voxels_exactly",
             tuple((6, y, z) for y in (4, 5, 6) for z in (4, 5, 6) if (y, z) != (5, 5))
             + ((8, 5, 5),)), ("nonempty",))),
    # -- the boundary cases --------------------------------------------------------------------
    #: THE EYE INSIDE MATTER, which is the whole reason the origin semantics had to be decided.
    #: TWO of them, because the case has two jobs. With the neighbour PRESSED AGAINST the eye its
    #: -x face is an interior one — solid on the far side, namely the eye's own cell — and it is
    #: the single declared exception to the interior-face theorem, so the exception is exercised
    #: rather than merely written down. With the neighbour THREE CELLS AWAY the transparent answer
    #: varies across the screen and misses at the edges, which is what makes the direction-
    #: blindness of the opaque semantics visible as a contrast rather than as an assertion.
    _scene("eye_inside_wall", (C, (6, 5, 5)), CC, (1, 0, 0),
           (("origin_split", (C, (6, 5, 5), 1)),)),
    _scene("eye_inside_open", (C, (8, 5, 5)), CC, (1, 0, 0),
           (("origin_split", (C, (8, 5, 5), 1)),)),
    #: THE EYE EXACTLY ON A CELL PLANE. Floor division puts it in the HIGHER cell, and the ray
    #: immediately crosses back out with a first step of length zero — so the question is whether
    #: that zero-length step creates a phantom crossing or swallows a real one. It does neither:
    #: the frame is identical to the frame from one unit BEFORE the plane, which is where the ray
    #: arrives at t = 0. WITH A CONTROL, because one unit in the other direction is NOT identical
    #: — it moves the eye further from the cell and the silhouette rounds differently, which is
    #: perspective and not the boundary. The first version of this expectation demanded equality
    #: on that side too and was simply wrong about what moving a ray ORIGIN does.
    _scene("eye_on_boundary", (C,), (10 * Q, CC[1], CC[2]), (-1, 0, 0),
           (("boundary_cell", (10, 5, 5)), ("nonempty",))),
    #: ZERO EXTENT: a quad whose four corners coincide. The reference must be byte-identical with
    #: and without it, and the fate classifier must call it `degenerate` rather than guess.
    _scene("zero_extent", (C,), (CC[0] + D, CC[1], CC[2]), (-1, 0, 0),
           (("degenerate_is_invisible",), ("nonempty",)), extra=(DEGENERATE_QUAD,)),
    _scene("empty_world", (), (CC[0] + D, CC[1], CC[2]), (-1, 0, 0), (("all_miss",),)),
    # -- the two vantages the frozen trace does not contain, taken from the REAL world ----------
    _scene("world_standing", None, _centre(STANDING_PIN), (0, 1, 0),
           (("supported",), ("nonempty",))),
    _scene("world_walladj", None, _centre(WALLADJ_PIN), (1, 0, 0),
           (("wall_ahead",), ("nonempty",))),
)

MICRO_NAMES = tuple(s["name"] for s in MICRO)


def micro(name):
    for s in MICRO:
        if s["name"] == name:
            return s
    raise VoxmicroError("VOXMICRO-REFUSE: no scene named %r" % name)


def micro_occ(sc):
    """A scene's occupancy. `cells=None` means the frozen world itself, unmodified."""
    if sc["cells"] is None:
        return VR.solid
    cells = set(sc["cells"])

    def occ(x, y, z):
        return (x, y, z) in cells
    return occ


def micro_cells(sc):
    if sc["cells"] is not None:
        return set(sc["cells"])
    return {(x, y, z) for x in range(VR.N) for y in range(VR.N) for z in range(VR.N)
            if VR.solid(x, y, z)}


def micro_prims(sc, winding):
    """The scene's faces, through the SAME two windings `voxray` declared. Every face of every
    solid cell, no culling — the reference's own primitive rule, applied to a smaller world."""
    if winding not in VX.WINDINGS:
        raise VoxmicroError("VOXMICRO-REFUSE: no winding named %r" % winding)
    out = []
    for x, y, z in sorted(micro_cells(sc)):
        for fi, (_n, corners) in enumerate(VR.FACES):
            if winding == "reversed":
                corners = tuple(reversed(corners))
            key = (((x * VR.N) + y) * VR.N + z) * 6 + fi
            out.append((key, VR.PALETTE[fi],
                        tuple(((x + a) * Q, (y + b) * Q, (z + c) * Q) for a, b, c in corners)))
    out.extend(sc["extra"])
    return out


# ---- the oracle, posed at every pixel ---------------------------------------------------------
def oracle_frame(eye, fwd, occ, origin):
    """(voxel, face) or None for every pixel, in row-major order."""
    out = []
    for py in range(VR.H):
        for px in range(VR.W):
            hit = VX.first_hit(eye, VX.ray_for_pixel(eye, fwd, px, py), occ, origin)
            out.append(None if hit is None else (hit[0], hit[1]))
    return out


def across(cell, face):
    n = VR.FACES[face][0]
    return (cell[0] + n[0], cell[1] + n[1], cell[2] + n[2])


def is_interior(cell, face, occ):
    """A face with solid on the far side of its own outward normal: sandwiched, and unseeable."""
    v = across(cell, face)
    return all(0 <= v[i] < VR.N for i in range(3)) and occ(*v)


def impossible_winner(cell, face, occ, eye_cell):
    """AN INTERIOR FACE THE CAMERA COULD NOT POSSIBLY BE LOOKING AT, with the one exception.

    THE EXCEPTION IS ON THE FAR SIDE, NOT THE NEAR ONE, and the first version of this had it
    backwards — it excluded faces BELONGING to the eye's cell and counted faces FACING it. From
    inside cell A with solid neighbour B, A's face towards B is seen from behind and is never
    drawn; B's face towards A is exactly what the camera sees, and is interior only because A is
    solid, which for this ray it is declared not to be. Getting this the wrong way round reported
    a whole framebuffer of impossible pixels on `eye_inside_wall` — 6912 of them, all legitimate —
    and it was caught by reading the record rather than by any law, which is why the count is now
    checked against a constructed witness whose answer is known before it runs.
    """
    return is_interior(cell, face, occ) and across(cell, face) != eye_cell


def the_oracle_never_reports_an_interior_face():
    """A THEOREM THE ORACLE MUST OBEY, checked on every scene under both origin semantics.

    From an eye outside the solid set, a ray reaching an interior face has already passed through
    one of the two solid cells that sandwich it. The single legal exception is the transparent
    origin's OWN cell, which is declared free for that ray and therefore no longer sandwiching.
    """
    for sc in MICRO:
        if ("refuses",) in sc["expect"]:
            continue
        occ = micro_occ(sc)
        eye = sc["eye"]
        own = tuple(e // Q for e in eye)
        for origin in VX.ORIGINS:
            for cell, face in _hits(oracle_frame(eye, sc["fwd"], occ, origin)):
                if face is None:
                    continue
                if not is_interior(cell, face, occ):
                    continue
                if origin == "transparent" and across(cell, face) == own:
                    continue
                return False
    return True


def _hits(frame):
    return [h for h in frame if h is not None]


def the_opaque_origin_is_direction_blind():
    """WHY THE CORRESPONDENCE USES `transparent`, AS A LAW AND NOT AS A PARAGRAPH.

    On a frame whose eye is inside matter, `opaque` returns the same answer for every pixel: the
    containing voxel, no face, t = 0. An oracle whose output does not depend on the ray carries no
    information about the camera and cannot separate a correct renderer from a broken one, which
    disqualifies it for that frame — the exclusion `voxray` had to make by derivation.
    """
    sc = micro("eye_inside_open")
    occ = micro_occ(sc)
    frame = oracle_frame(sc["eye"], sc["fwd"], occ, "opaque")
    if len(set(frame)) != 1 or frame[0][1] is not None:
        return False
    live = oracle_frame(sc["eye"], sc["fwd"], occ, "transparent")
    return len(set(live)) > 1


def the_two_origins_agree_off_solid():
    """AND THE CHOICE MOVES NOTHING ELSE: wherever the eye is outside solid the two semantics are
    identical, pixel for pixel, on every scene and on every declared frame."""
    for sc in MICRO:
        if ("refuses",) in sc["expect"]:
            continue
        occ = micro_occ(sc)
        v = tuple(e // Q for e in sc["eye"])
        if all(0 <= v[i] < VR.N for i in range(3)) and occ(*v):
            continue
        a = oracle_frame(sc["eye"], sc["fwd"], occ, "opaque")
        if a != oracle_frame(sc["eye"], sc["fwd"], occ, "transparent"):
            return False
    for _n, eye, fwd in VR.TRACE:
        if VX.eye_is_inside_solid(eye):
            continue
        if (oracle_frame(eye, fwd, VR.solid, "opaque")
                != oracle_frame(eye, fwd, VR.solid, "transparent")):
            return False
    return True


#: The semantics the correspondence uses, declared once and referenced everywhere.
CORRESPONDENCE_ORIGIN = "transparent"


# ---- the reference, instrumented --------------------------------------------------------------
#: THE FATE LADDER, DECLARED. A face is classified by the FURTHEST stage any of its two triangles
#: reached, because a face with one backfacing triangle and one rasterised triangle was drawn. The
#: only arbitrary step is `backface` above `degenerate`: the reference rejects both in the single
#: test `area <= 0`, and when a face manages one of each the negative area is the informative half
#: — it is a statement about winding, where a zero area is a statement about rounding.
STAGES = ("not_generated", "near_clipped", "degenerate", "backface", "offscreen", "rasterised")
RASTERISED = STAGES.index("rasterised")


def instrument(prims, eye, fwd):
    """`voxref.render`'s inner loop with the fates recorded. Returns (winner, stage, covered).

    A THIRD transcription of the same loop is a drift risk, so it is bound in both directions:
    `the_instrument_agrees_with_the_reference` checks this winner array against `voxray`'s and
    against the colours `voxref.render` actually paints.
    """
    m = VR.basis(fwd)
    cx, cy = VR.W // 2, VR.H // 2
    dep = [VR.FAR] * (VR.W * VR.H)
    key = [-1] * (VR.W * VR.H)
    stage, covered = {}, {}
    for pk, _col, quad in prims:
        cam = [VR._project(v, eye, m) for v in quad]
        if any(c[1] < VR.NEAR for c in cam):
            stage[pk] = max(stage.get(pk, 0), STAGES.index("near_clipped"))
            continue
        st = STAGES.index("near_clipped")
        scr = [(cx + c[0] * VR.FOCAL // c[1], cy - c[2] * VR.FOCAL // c[1], c[1]) for c in cam]
        for a, b, c2 in ((scr[0], scr[1], scr[2]), (scr[0], scr[2], scr[3])):
            area = (b[0] - a[0]) * (c2[1] - a[1]) - (b[1] - a[1]) * (c2[0] - a[0])
            if area == 0:
                st = max(st, STAGES.index("degenerate"))
                continue
            if area < 0:
                st = max(st, STAGES.index("backface"))
                continue
            xl = max(min(a[0], b[0], c2[0]), 0)
            xh = min(max(a[0], b[0], c2[0]), VR.W - 1)
            yl = max(min(a[1], b[1], c2[1]), 0)
            yh = min(max(a[1], b[1], c2[1]), VR.H - 1)
            if xl > xh or yl > yh:
                st = max(st, STAGES.index("offscreen"))
                continue
            st = RASTERISED
            b0 = VR._top_left_bias(a[0], a[1], b[0], b[1])
            b1 = VR._top_left_bias(b[0], b[1], c2[0], c2[1])
            b2 = VR._top_left_bias(c2[0], c2[1], a[0], a[1])
            for py in range(yl, yh + 1):
                for px in range(xl, xh + 1):
                    w0 = VR._edge(a[0], a[1], b[0], b[1], px, py) + b0
                    w1 = VR._edge(b[0], b[1], c2[0], c2[1], px, py) + b1
                    w2 = VR._edge(c2[0], c2[1], a[0], a[1], px, py) + b2
                    if w0 < 0 or w1 < 0 or w2 < 0:
                        continue
                    d = (a[2] * w1 + b[2] * w2 + c2[2] * w0) // area
                    i = py * VR.W + px
                    covered.setdefault(pk, set()).add(i)
                    if (d, pk) < (dep[i], key[i] if key[i] >= 0 else (1 << 62)):
                        dep[i] = d
                        key[i] = pk
        stage[pk] = max(stage.get(pk, 0), st)
    return key, stage, covered


def the_instrument_agrees_with_the_reference():
    """The instrumented loop must be the SAME loop: same winners as `voxray`, same colours as
    `voxref`. A diagnostic that drifts from the thing it diagnoses is worse than none."""
    for nm in ("single_px", "corner_on", "aperture", "world_standing"):
        sc = micro(nm)
        for winding in VX.WINDINGS:
            prims = micro_prims(sc, winding)
            key, _stage, _cov = instrument(prims, sc["eye"], sc["fwd"])
            if key != VX.render_winners(prims, sc["eye"], sc["fwd"]):
                return False
            col, _dep = VR.render(prims, sc["eye"], sc["fwd"])
            for i, k in enumerate(key):
                want = VR.BACKGROUND if k < 0 else VR.PALETTE[
                    (k % 6) if k < EXTRA_KEY_BASE else 0]
                if col[i] != want:
                    return False
    _n, eye, fwd = VR.TRACE[VX.BIND_FRAME]
    prims = VX.primitives_with("reversed")
    return instrument(prims, eye, fwd)[0] == VX.render_winners(prims, eye, fwd)


def winner_answer(k):
    """The rasteriser's answer at a pixel, in the oracle's vocabulary."""
    if k < 0:
        return None
    if k >= EXTRA_KEY_BASE:
        return ("extra", k - EXTRA_KEY_BASE)
    return VX._unkey(k)


# ---- where did you lose me --------------------------------------------------------------------
#: The comparison classes, reused verbatim from `voxray` so the two records speak one language.
CLASSES = VX.CLASSES

#: THE FATES, DECLARED AND MUTUALLY EXCLUSIVE — one per disagreeing pixel, in this order.
REJECTS = ("sampling_shift", "not_generated", "near_clipped", "degenerate", "backface",
           "offscreen", "not_covered", "depth_rejected", "no_face_answer", "phantom", "unknown")

#: The candidate offsets for a sampling-explained disagreement: the 3x3 block minus its centre.
#: That is exactly the bound `voxray.the_rays_invert_the_projection_to_within_one_pixel` measured
#: and pinned — no wider, so the subtraction cannot quietly absorb a real defect two pixels away.
NEIGHBOURS = tuple((dx, dy) for dy in (-1, 0, 1) for dx in (-1, 0, 1) if (dx, dy) != (0, 0))


def _shift_explains(px, py, answer, ora):
    for dx, dy in NEIGHBOURS:
        qx, qy = px + dx, py + dy
        if 0 <= qx < VR.W and 0 <= qy < VR.H and ora[qy * VR.W + qx] == answer:
            return True
    return False


def classify(sc_or_frame, winding, origin=CORRESPONDENCE_ORIGIN, _disable=()):
    """Every pixel of one scene under one winding: the six comparison classes, the eleven fates,
    and the interior-face count. `_disable` removes a fate branch and exists only so the selftest
    can show the removed pixels arriving in `unknown`."""
    if isinstance(sc_or_frame, int):
        _name, eye, fwd = VR.TRACE[sc_or_frame]
        occ, prims = VR.solid, VX.primitives_with(winding)
    else:
        sc = sc_or_frame
        eye, fwd = sc["eye"], sc["fwd"]
        occ, prims = micro_occ(sc), micro_prims(sc, winding)
    winner, stage, covered = instrument(prims, eye, fwd)
    ora = oracle_frame(eye, fwd, occ, origin)
    keyed = {pk for pk, _c, _q in prims}
    own = tuple(e // Q for e in eye)
    out = dict.fromkeys(CLASSES + REJECTS, 0)
    out["interior_winner"] = 0
    for py in range(VR.H):
        for px in range(VR.W):
            i = py * VR.W + px
            r = winner_answer(winner[i])
            o = ora[i]
            if r is not None and r[0] != "extra" and impossible_winner(r[0], r[1], occ, own):
                out["interior_winner"] += 1
            if r is None:
                out["both_empty" if o is None else "ref_empty_oracle_hit"] += 1
            elif o is None:
                out["ref_drew_oracle_miss"] += 1
            elif r == o:
                out["agree"] += 1
            elif r[0] == o[0]:
                out["same_voxel_other_face"] += 1
            else:
                out["other_voxel"] += 1
            if r == o:
                continue
            out[_fate(px, py, i, r, o, ora, keyed, stage, covered, _disable)] += 1
    return out


def _fate(px, py, i, r, o, ora, keyed, stage, covered, disable):
    """One disagreeing pixel, one name. THE SAMPLING OFFSET IS SUBTRACTED FIRST, deliberately:
    it is a property of the COMPARISON rather than of the renderer, and leaving it mixed into the
    pipeline classes would inflate every one of them. It is an UPPER bound on what sampling can
    explain — a genuinely wrong winner may coincide with a neighbour's answer by luck — so every
    other class below is a LOWER bound on real defect."""
    if "sampling_shift" not in disable and _shift_explains(px, py, r, ora):
        return "sampling_shift"
    if o is None:
        return "phantom" if "phantom" not in disable else "unknown"
    if o[1] is None:
        return "no_face_answer" if "no_face_answer" not in disable else "unknown"
    k = (((o[0][0] * VR.N) + o[0][1]) * VR.N + o[0][2]) * 6 + o[1]
    if k not in keyed:
        return "not_generated" if "not_generated" not in disable else "unknown"
    st = STAGES[stage[k]]
    if st != "rasterised":
        return st if st not in disable else "unknown"
    if i not in covered.get(k, ()):
        return "not_covered" if "not_covered" not in disable else "unknown"
    if "depth_rejected" not in disable:
        return "depth_rejected"
    return "unknown"


# ---- the scenes' declared expectations ---------------------------------------------------------
def expectation_holds(sc, kind, arg=None):
    if kind == "refuses":
        try:
            VR.basis(sc["fwd"])
        except VR.VoxrefError:
            return True
        return False
    occ = micro_occ(sc)
    if kind == "origin_split":
        want_op, want_tr, want_face = arg
        op = oracle_frame(sc["eye"], sc["fwd"], occ, "opaque")
        tr = oracle_frame(sc["eye"], sc["fwd"], occ, "transparent")
        centre = (VR.H // 2) * VR.W + VR.W // 2
        return (op[centre] == (want_op, None) and tr[centre] == (want_tr, want_face))
    frame = oracle_frame(sc["eye"], sc["fwd"], occ, CORRESPONDENCE_ORIGIN)
    hits = _hits(frame)
    if kind == "nonempty":
        return len(hits) > 0
    if kind == "all_miss":
        return len(hits) == 0
    if kind == "faces_exactly":
        return {f for _v, f in hits} == set(arg)
    if kind == "no_faces":
        return not ({f for _v, f in hits} & set(arg))
    if kind == "voxels_exactly":
        return {v for v, _f in hits} == set(arg)
    if kind == "boundary_cell":
        if tuple(e // Q for e in sc["eye"]) != tuple(arg):
            return False
        back = (sc["eye"][0] - 1, sc["eye"][1], sc["eye"][2])
        fwd_ = (sc["eye"][0] + 1, sc["eye"][1], sc["eye"][2])
        return (frame == oracle_frame(back, sc["fwd"], occ, CORRESPONDENCE_ORIGIN)
                and frame != oracle_frame(fwd_, sc["fwd"], occ, CORRESPONDENCE_ORIGIN))
    if kind == "degenerate_is_invisible":
        for winding in VX.WINDINGS:
            prims = micro_prims(sc, winding)
            bare = [p for p in prims if p[0] < EXTRA_KEY_BASE]
            if len(bare) == len(prims):
                return False
            if VR.render(prims, sc["eye"], sc["fwd"]) != VR.render(bare, sc["eye"], sc["fwd"]):
                return False
            _k, stage, _c = instrument(prims, sc["eye"], sc["fwd"])
            if STAGES[stage[EXTRA_KEY_BASE]] != "degenerate":
                return False
        return True
    if kind == "supported":
        v = tuple(e // Q for e in sc["eye"])
        return not VR.solid(*v) and VR.solid(v[0], v[1], v[2] - 1)
    if kind == "wall_ahead":
        v = tuple(e // Q for e in sc["eye"])
        s = tuple(1 if c > 0 else -1 if c < 0 else 0 for c in sc["fwd"])
        return not VR.solid(*v) and VR.solid(v[0] + s[0], v[1] + s[1], v[2] + s[2])
    raise VoxmicroError("VOXMICRO-REFUSE: no expectation kind named %r" % kind)


def failing_expectations():
    """Every (scene, expectation) that does not hold — the list, not a boolean, so a red row can
    say WHICH elementary case the oracle got wrong."""
    bad = []
    for sc in MICRO:
        for exp in sc["expect"]:
            kind, arg = (exp[0], exp[1] if len(exp) > 1 else None)
            if not expectation_holds(sc, kind, arg):
                bad.append((sc["name"], kind))
    return bad


def every_scene_meets_its_expectation():
    return not failing_expectations()


def a_broken_expectation_is_caught():
    """THE PLANT: a scene whose declared faces are wrong must fail, or the suite proves nothing."""
    sc = dict(micro("single_px"))
    sc["expect"] = (("faces_exactly", (2,)),)
    return not expectation_holds(sc, "faces_exactly", (2,))


# ---- the labels, as claims ---------------------------------------------------------------------
#: EVERY FRAME NAME MAKES ONE CHECKABLE CLAIM, evaluated against the world by the gate. A label is
#: not a comment here: `voxray` found two of these describing a world that no longer existed, and
#: renaming them would have prevented exactly nothing. The claim is a NECESSARY condition the name
#: asserts, not a classification — two frames may satisfy each other's claims.
LABEL_CLAIMS = {
    "enclosed":   "inside the lattice, in free space, and no ray escapes",
    "buried":     "the eye is inside solid",
    "seam":       "some eye coordinate lies exactly on a section plane",
    "wall_flat":  "the centre ray enters a face whose normal is exactly the reverse of forward",
    "open_air":   "outside the lattice on two axes or more, and some ray escapes",
    "oblique":    "no forward component is zero",
    "corner":     "outside the lattice on all three axes",
    "edge_on":    "the eye's cell sits directly on the floor slab and forward is level",
}


def label_holds(name, eye, fwd):
    v = tuple(e // Q for e in eye)
    inside = all(0 <= v[i] < VR.N for i in range(3)) and VR.solid(*v)
    outax = sum(1 for i in range(3) if not (0 <= v[i] < VR.N))
    if name == "buried":
        return inside
    if name == "enclosed":
        if inside or outax:
            return False
        return all(VX.first_hit(eye, VX.ray_for_pixel(eye, fwd, px, py)) is not None
                   for py in range(0, VR.H, 5) for px in range(0, VR.W, 5))
    if name == "seam":
        return any(e % (VR.SECTION * Q) == 0 for e in eye)
    if name == "wall_flat":
        hit = VX.first_hit(eye, VX.ray_for_pixel(eye, fwd, VR.W // 2, VR.H // 2))
        if hit is None or hit[1] is None:
            return False
        n = VR.FACES[hit[1]][0]
        s = tuple(1 if c > 0 else -1 if c < 0 else 0 for c in fwd)
        return n == tuple(-c for c in s)
    if name == "open_air":
        return outax >= 2 and any(
            VX.first_hit(eye, VX.ray_for_pixel(eye, fwd, px, py)) is None
            for py in range(0, VR.H, 5) for px in range(0, VR.W, 5))
    if name == "oblique":
        return all(c != 0 for c in fwd)
    if name == "corner":
        return outax == 3
    if name == "edge_on":
        return v[2] == 1 and fwd[2] == 0
    raise VoxmicroError("VOXMICRO-REFUSE: no claim declared for label %r" % name)


def failing_labels():
    return [n for n, eye, fwd in VR.TRACE if not label_holds(n, eye, fwd)]


def every_label_is_true_of_the_world():
    """The corrected names, checked. Not one of them is taken on trust."""
    return (sorted(LABEL_CLAIMS) == sorted(n for n, _e, _f in VR.TRACE)
            and not failing_labels())


def the_old_labels_would_fail():
    """THE CONTROL. Restore the two names `voxray` found wrong and the check must redden, or the
    correction was cosmetic and the claims are not doing any work."""
    checked = 0
    for i, was, _now in VX.TRACE_LABEL_CORRECTION:
        if was not in LABEL_CLAIMS:
            continue                     # `floor_flat` is gone entirely; nothing left to claim
        _n, eye, fwd = VR.TRACE[i]
        if label_holds(was, eye, fwd):
            return False                 # the old name would still have been true: no correction
        checked += 1
    return checked > 0


#: WHAT THE CORPUS STILL DOES NOT CONTAIN, said plainly rather than left as an absence. No declared
#: frame stands on anything: every one of the eight has empty space or the lattice exterior
#: directly below it, so grazing incidence over a supported surface — the case a fill rule breaks
#: first — is covered only by `edge_on`, which floats one cell above the slab. The two `world_*`
#: micro-scenes supply the vantage; moving the frozen trace is the re-freeze rung's business.
def no_declared_frame_is_supported():
    for _n, eye, _f in VR.TRACE:
        v = tuple(e // Q for e in eye)
        if not all(0 <= v[i] < VR.N for i in range(3)) or v[2] < 1:
            continue
        if not VR.solid(*v) and VR.solid(v[0], v[1], v[2] - 1):
            return False
    return True


# ---- the record ---------------------------------------------------------------------------------
RECORD = os.path.join("spec", "attest", "voxref-micro.txt")
COLUMNS = CLASSES + REJECTS + ("interior_winner",)


def grid():
    """DERIVED: every renderable scene and every declared frame, both windings, both origins."""
    rows = []
    for sc in MICRO:
        if ("refuses",) in sc["expect"]:
            continue
        for winding in VX.WINDINGS:
            for origin in VX.ORIGINS:
                rows.append(("micro", sc["name"], winding, origin))
    for i, (name, _e, _f) in enumerate(VR.TRACE):
        for winding in VX.WINDINGS:
            for origin in VX.ORIGINS:
                rows.append(("frame", "%d:%s" % (i, name), winding, origin))
    return rows


def _target(kind, name):
    return int(name.split(":")[0]) if kind == "frame" else micro(name)


def generate():
    rows = ["# URDRVXM1 oracle qualification — one row per (kind, name, winding, origin),",
            "# emitted by voxmicro.generate(), committed as an artifact, re-derived by the gate.",
            "# columns: kind name winding origin " + " ".join(COLUMNS),
            "# world %s" % VR.world_digest(),
            "# The six leading columns are voxray's comparison classes and sum to the",
            "# framebuffer. The eleven that follow are the FATE of each disagreeing pixel and sum",
            "# to the disagreement. `sampling_shift` is subtracted FIRST and is an upper bound on",
            "# what the measured <=1px ray/sample offset can explain, so every other fate is a",
            "# LOWER bound on real defect. `interior_winner` counts pixels whose winning face has",
            "# solid on the far side of its own normal: impossible for any exterior camera at any",
            "# resolution, and therefore the one number here that owes the oracle nothing."]
    for kind, name, winding, origin in grid():
        c = classify(_target(kind, name), winding, origin)
        rows.append("%s %s %s %s %s"
                    % (kind, name, winding, origin, " ".join(str(c[k]) for k in COLUMNS)))
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
        if len(f) != 4 + len(COLUMNS):
            raise VoxmicroError("VOXMICRO-REFUSE: a row with %d fields" % len(f))
        c = dict(zip(COLUMNS, (int(v) for v in f[4:])))
        if sum(c[k] for k in CLASSES) != VR.W * VR.H:
            raise VoxmicroError("VOXMICRO-REFUSE: a row whose classes do not sum to the "
                                "framebuffer")
        if sum(c[k] for k in REJECTS) != VR.W * VR.H - c["agree"] - c["both_empty"]:
            raise VoxmicroError("VOXMICRO-REFUSE: a row whose fates do not sum to its "
                                "disagreement")
        rows.append((f[0], f[1], f[2], f[3], c))
    if world is None:
        raise VoxmicroError("VOXMICRO-REFUSE: the record names no world digest")
    if not rows:
        raise VoxmicroError("VOXMICRO-REFUSE: the record has no rows")
    return world, rows


def the_record_is_exactly_the_derived_grid():
    _w, rows = parse()
    return [r[:4] for r in rows] == grid()


def the_record_names_this_world():
    return parse()[0] == VR.world_digest()


#: What the gate recomputes in full every run: one micro-scene and one declared frame, both
#: windings, the correspondence origin.
BIND = (("micro", "aperture"), ("frame", "%d:%s" % (VX.BIND_FRAME, VR.TRACE[VX.BIND_FRAME][0])))


def the_record_is_bound_to_the_live_code():
    _w, rows = parse()
    for kind, name in BIND:
        for winding in VX.WINDINGS:
            want = next(c for k, n, w, o, c in rows
                        if (k, n, w, o) == (kind, name, winding, CORRESPONDENCE_ORIGIN))
            got = classify(_target(kind, name), winding, CORRESPONDENCE_ORIGIN)
            if {k: got[k] for k in COLUMNS} != want:
                return False
    return True


def no_disagreement_is_unclassified():
    """`unknown` is zero in every row, which is what makes the fate distribution a distribution."""
    _w, rows = parse()
    return all(c["unknown"] == 0 for _k, _n, _wd, _o, c in rows)


def a_missing_branch_lands_in_unknown():
    """THE PLANT FOR THE LAW ABOVE: remove one fate branch and its pixels must arrive in
    `unknown`, or a zero there would only mean the classifier never looks."""
    sc = micro("aperture")
    full = classify(sc, "reversed")
    if not full["depth_rejected"]:
        return False
    cut = classify(sc, "reversed", _disable=("depth_rejected",))
    return cut["unknown"] == full["depth_rejected"] and cut["depth_rejected"] == 0


# ---- the interior-face detector -----------------------------------------------------------------
def interior_witness():
    """A CONSTRUCTED scene where the reference is known to award pixels to a sandwiched face.

    Two adjacent solid cells seen obliquely: the shared plane carries one interior face from each,
    and with the committed winding the reference hands pixels to them. Built rather than sampled,
    so the detector is shown to bite on a case whose answer is known before it runs.
    """
    sc = micro("pair_oblique")
    bad = classify(sc, "as-committed")["interior_winner"]
    good = classify(sc, "reversed")["interior_winner"]
    return bad, good


def the_interior_detector_bites():
    return interior_witness()[0] > 0


def interior_totals(rows=None):
    """Impossible pixels per winding over the declared frames, at the correspondence origin."""
    if rows is None:
        _w, rows = parse()
    out = {}
    for kind, _n, winding, origin, c in rows:
        if kind != "frame" or origin != CORRESPONDENCE_ORIGIN:
            continue
        out[winding] = out.get(winding, 0) + c["interior_winner"]
    return out


def the_reference_still_reports_impossible_faces():
    """REPORTED AS A DEFECT THAT SURVIVES THE WINDING FIX, and scheduled for retirement.

    This row asserts that the reference is still wrong, which means the repair rung will redden it
    — that is the point, and it is the same retention-then-retirement shape `armpair` used. The
    number is not a correspondence and carries none of its caveats: an interior face cannot be the
    nearest surface along any ray from an exterior eye, so every one of these pixels is wrong
    independently of the oracle, of sampling, and of any excluded frame.
    """
    t = interior_totals()
    return t.get("reversed", 0) > 0 and t.get("as-committed", 0) > t["reversed"]


def residue_split(winding, rows=None):
    """The disagreement of the declared frames, decomposed. (total, sampling, by-fate dict)."""
    if rows is None:
        _w, rows = parse()
    tot, samp, fates = 0, 0, {}
    for kind, _n, w, origin, c in rows:
        if kind != "frame" or w != winding or origin != CORRESPONDENCE_ORIGIN:
            continue
        tot += VR.W * VR.H - c["agree"] - c["both_empty"]
        samp += c["sampling_shift"]
        for k in REJECTS:
            if k != "sampling_shift":
                fates[k] = fates.get(k, 0) + c[k]
    return tot, samp, fates


def a_tampered_row_refuses():
    text = _read()
    for ln in text.split("\n"):
        if ln and not ln.startswith("#"):
            text = text.replace(ln, ln + " 7", 1)
            break
    try:
        parse(text)
    except VoxmicroError:
        return True
    return False


def told():
    tot, samp, fates = residue_split("reversed")
    ranked = sorted(((v, k) for k, v in fates.items() if v), reverse=True)
    it = interior_totals()
    frames = len(VR.TRACE) * VR.W * VR.H
    return ("all %d declared frames now comparable; reversed-winding disagreement %d/%d "
            "(%.1f%%), of which at most %d (%.1f%% of it) is the measured <=1px sampling offset; "
            "the rest is %s; impossible interior-face pixels %d as committed and %d reversed"
            % (len(VR.TRACE), tot, frames, 100.0 * tot / frames, samp,
               100.0 * samp / (tot or 1),
               ", ".join("%s %d" % (k, v) for v, k in ranked[:4]) or "nothing",
               it.get("as-committed", 0), it.get("reversed", 0)))


#: THE PINNED CONFORMANCE SCENES, under the name the rest of the tree uses for them. It is NOT the
#: micro-scene register above, which was called `SCENES` in this module's first draft — and that
#: collision was not harmless: `specfreeze.lattice`'s coverage clause reads exactly the pair
#: (`scene_result`, `SCENES`) to decide which modules its partition must account for, so a module
#: whose `SCENES` means something else is read as declaring a conformance register it does not
#: have. See `the_sibling_modules_escape_the_coverage_clause`, which measures the other half of
#: that: `voxref`, `voxray` and `voxcoarse` all pin conformance scenes and none of them defines
#: `SCENES` at all, so the clause never sees them.
SCENES = ("scenes", "labels", "residue")


def the_sibling_modules_escape_the_coverage_clause():
    """A BLIND SPOT IN THE TREE'S OWN COVERAGE LAW, RECORDED AS A MEASUREMENT.

    `lattice`'s clause (e) requires every module with `scene_result` AND `SCENES` to be in its
    sealed partition or its post-seal register. The three modules of this arc that came before
    this one pin conformance scenes through `scene_result`/`golden` and name their register
    nothing at all, so the clause cannot see them — which is why this module is the first of the
    four the law ever asked about, and it asked because of an attribute NAME rather than because
    of anything it does. Asserted so the gap is a row instead of a paragraph. IT REDDENS WHEN THE
    GAP IS CLOSED, which is the point: fixing `lattice` to key on `golden` is a different rung.
    """
    import importlib
    for name in ("voxref", "voxray", "voxcoarse"):
        m = importlib.import_module(name)
        if not hasattr(m, "scene_result") or hasattr(m, "SCENES"):
            return False
    return True


def scene_case(name):
    if name == "scenes":
        return repr([(sc["name"], sc["eye"], sc["fwd"], sc["expect"],
                      sorted(micro_cells(sc))[:8] if sc["cells"] is not None else "world")
                     for sc in MICRO])
    if name == "labels":
        return repr((sorted(LABEL_CLAIMS.items()), [n for n, _e, _f in VR.TRACE],
                     failing_labels(), VX.TRACE_LABEL_CORRECTION,
                     STANDING_PIN, WALLADJ_PIN))
    if name == "residue":
        _w, rows = parse()
        return repr((residue_split("as-committed", rows), residue_split("reversed", rows),
                     interior_totals(rows), interior_witness()))
    raise VoxmicroError("VOXMICRO-REFUSE: no scene named %r" % name)


def scene_result(name):
    return hashlib.sha256(MAGIC + b"|" + name.encode() + b"|"
                          + scene_case(name).encode()).hexdigest()


def golden(name):
    with open(os.path.join(_HERE, "conformance_voxmicro.txt"), encoding="utf-8") as fh:
        for ln in fh:
            ln = ln.strip()
            if ln and not ln.startswith("#"):
                nm, dig = ln.split()
                if nm == name:
                    return dig
    raise VoxmicroError("VOXMICRO-REFUSE: no golden named %r" % name)
