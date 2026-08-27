# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""voxfill (URDRVXL1) — THE FILL RULE, ONE VARIABLE AT A TIME, AND THE ARM THAT WON WAS NOT ON THE LIST.

`voxfate` localised the surviving defect to COVERAGE: of the 378 stable disagreements, 318 are
`not_covered` — the oracle's face was rasterised, reached the pixel loop, and did not claim the
pixel. Three mechanisms could do that, and this rung varies each ALONE:

    inclusive   drop the top-left bias            edge ownership
    wide_bbox   pad the candidate box by a pixel  which pixels enter the loop
    centre      sample at px*S + S//2             where the fill rule reads the triangle

THE REJECTIONS ARE CLASSIFIED ALGEBRAICALLY FIRST, before any arm runs, by reading the three edge
functions at the exact sample point of the oracle's own face:

    bias_only   215   every rejecting edge has e == 0 — the sample is EXACTLY ON the edge and only
                      the top-left bias rejects it
    outside     100   some rejecting edge has e < 0 — genuinely outside the triangle
    bbox          3   the pixel never entered the candidate loop at all

THAT DISTRIBUTION PREDICTS THE ARMS BEFORE THEY RUN, and `wide_bbox` is eliminated by a stronger
statement than the one first written. The first law said the `bbox` class was EMPTY, so padding
could rescue nothing; the class is not empty, it is three. All three sit exactly ONE PIXEL right of
the box, padding admits all three, and all three still FAIL the edge test — so `wide_bbox` changes
not one pixel anywhere on screen. The box is not merely tight, it is a conservative superset of the
pixels the edge test accepts, and the arm is INERT rather than the class being absent. That
distinction is the difference between a check that bites and a check that is vacuously green.

AND THE 100 `outside` ARE OUTSIDE BY ALMOST NOTHING. 99 of them fall short by less than one pixel;
exactly ONE is beyond it. The typical shortfall is a single SUB-PIXEL UNIT at S=64 — the quantum of
the floor in the projection itself. Distances are compared as exact integers by squaring, never as
floats: `e^2 < S^2 * (dx^2 + dy^2)` is the perpendicular distance under one pixel, with no square
root taken and no rounding introduced by the measurement.

SO THE LEADING HYPOTHESIS WAS EDGE OWNERSHIP, WITH 215 OF 318 BEHIND IT, AND THE ALIGNMENT CONTROL
REFUTED IT. Under the committed convention `inclusive` looks like the answer: 204 of the 318
rescued, impossible faces 152 -> 59, agreement +58. But agreement +58 is a NET of +396 gained and
-338 lost, and 236 of those 338 losses are pixels the `(depth, face_key)` tiebreak — the rule
`voxtie` measured at ZERO of its own resolvable ceiling — only gets to decide because dropping the
bias turned the partition into a cover.

THE 2x2 THAT DECIDES IT VARIES THE ORACLE'S CONVENTION TOO, WHICH NO EARLIER RUNG HAS DONE. Every
rung of this arc has held the oracle fixed and asked what the rasteriser got wrong. But the oracle's
ray through pixel (px, py) is DERIVED from the rasteriser's own projection, so a convention error is
invisible to any experiment that varies only one side:

                        corner-ray oracle    centre-ray oracle
        corner sample         45550                41861
        centre sample         42744               *46567*

BOTH CONSISTENT PAIRINGS BEAT BOTH MIXED ONES, and the centre/centre pairing beats the committed
corner/corner pairing by 1017 pixels with impossible faces at 4 instead of 152. The reference's
projection FLOORS — it maps a screen position into a pixel REGION — while its sample point is that
region's CORNER. The two conventions are inconsistent by half a pixel, and the oracle inherited the
corner convention from the projection's algebra rather than from its rounding.

AND THAT REFUTES THIS RUNG'S OWN HEADLINE. Re-run `inclusive` with the conventions aligned and it is
WORSE, not better: 46560 against 46567, impossible 7 against 4. The 215 `bias_only` pixels were an
artefact of sampling a floored triangle at its corner, not evidence against the top-left rule. THE
TOP-LEFT RULE IS EXONERATED and the sample point is the defect — which is the arm that looked like
the weakest of the three when measured against the misaligned oracle, because it moves the whole
picture and the misaligned oracle scored that as 3739 losses.

THE STRONGEST NUMBER HERE NEEDS NO ORACLE AT ALL. `impossible` counts pixels awarded to a face
sandwiched between two solid cells; it is a property of the rasteriser alone, and no convention
choice can argue with it. It falls 152 -> 4 on the sample point ALONE.

does_not_show: anything about performance. WHY the one whole-pixel `outside` rejection survives.
That centre sampling is CORRECT — it is better on both metrics under the pairing that assumes it,
and choosing it changes what the ORACLE is, which reaches every record derived from `voxray` and is
a contract decision of exactly the kind `voxtie` refused to take by default. That the coverage
diagnosis survives the convention change: the population itself was selected under the corner
convention, so re-deriving it under the centre convention is the next rung and is not claimed here.
And nothing is repaired: `voxref` and `voxray` are untouched, and the frozen census stays frozen.

falsifier: `the_bbox_class_is_empty_and_the_arm_is_inert` states a prediction made from the
classification BEFORE the arm ran and reddens if padding the box moves any pixel; and
`the_ownership_rescue_is_an_artefact` requires the SAME single change to gain under one convention
and lose under the other, so a rung that had merely picked the biggest class would redden here.
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
import voxcand as VC                                         # noqa: E402
import voxtie as VT                                          # noqa: E402
import voxfate as VS                                         # noqa: E402

MAGIC = b"URDRVXL1"

#: DECLARED — the arms, each ONE change from `voxtie.BEST`. `committed` is the control and is
#: REQUIRED to reproduce `voxtie.render_level` exactly; the other three are single-variable.
ARMS = ("committed", "inclusive", "wide_bbox", "centre")

#: DECLARED — the sample/ray convention. `corner` is what the reference and the oracle both use
#: today; `centre` reads the pixel at the middle of the region the projection's floor implies.
CONVENTIONS = ("corner", "centre")

#: DECLARED — the algebraic classification of a coverage rejection, ordered FARTHEST FROM COVERING
#: to closest. A quad is two triangles and either may claim the pixel, so the face takes the CLOSEST
#: of its triangles' classes — which is why the order is a declared datum and not a set. `bbox` is
#: farthest because a pixel that never entered the loop was never rejected by an edge at all, and
#: `bias_only` is closer than `outside` because one is a convention away from covering and the other
#: is geometry away.
REJECTIONS = ("bbox", "outside", "bias_only", "covered")

#: The fate this rung conditions on, inherited from `voxfate` rather than restated.
FATE = "not_covered"


class VoxfillError(Exception):
    """VOXFILL-REFUSE — an arm, a convention or a record this module will not pretend to read."""


def _level():
    return VT.level(VT.BEST)


def arm_flags(arm):
    """(inclusive, pad, offset) — the ONE thing each arm changes, read from the arm name."""
    if arm not in ARMS:
        raise VoxfillError("VOXFILL-REFUSE: no arm named %r" % (arm,))
    _n, _sym, S = _level()
    return (arm == "inclusive", 1 if arm == "wide_bbox" else 0, S // 2 if arm == "centre" else 0)


# ---- the rasteriser under test ---------------------------------------------------------------------
def render_arm(arm, prims, eye, fwd):
    """`voxtie.render_level` at BEST with exactly one variable moved. Returns (winner, covered, ties).

    A FOURTH TRANSCRIPTION OF THE SAME LOOP, and therefore bound: `the_control_arm_matches_the_ladder`
    requires `committed` to equal `voxtie.render_level` on every declared frame.
    """
    inclusive, pad, off = arm_flags(arm)
    _n, _sym, S = _level()
    m = VR.basis(fwd)
    cx, cy = VR.W // 2, VR.H // 2
    dep = [None] * (VR.W * VR.H)
    key = [-1] * (VR.W * VR.H)
    covered, ties = {}, {}
    for pk, _col, quad in prims:
        cam = [VR._project(v, eye, m) for v in quad]
        if any(c[1] < VR.NEAR for c in cam):
            continue
        scr = [((cx * S * c[1] + c[0] * VR.FOCAL * S) // c[1],
                (cy * S * c[1] - c[2] * VR.FOCAL * S) // c[1], c[1]) for c in cam]
        for a, b, c2 in ((scr[0], scr[1], scr[2]), (scr[0], scr[2], scr[3])):
            area = (b[0] - a[0]) * (c2[1] - a[1]) - (b[1] - a[1]) * (c2[0] - a[0])
            if area <= 0:
                continue
            xl = max(min(a[0], b[0], c2[0]) // S - pad, 0)
            xh = min(max(a[0], b[0], c2[0]) // S + pad, VR.W - 1)
            yl = max(min(a[1], b[1], c2[1]) // S - pad, 0)
            yh = min(max(a[1], b[1], c2[1]) // S + pad, VR.H - 1)
            if xl > xh or yl > yh:
                continue
            if inclusive:
                b0 = b1 = b2 = 0
            else:
                b0 = VR._top_left_bias(a[0], a[1], b[0], b[1])
                b1 = VR._top_left_bias(b[0], b[1], c2[0], c2[1])
                b2 = VR._top_left_bias(c2[0], c2[1], a[0], a[1])
            for py in range(yl, yh + 1):
                for px in range(xl, xh + 1):
                    sx, sy = px * S + off, py * S + off
                    e0 = VR._edge(a[0], a[1], b[0], b[1], sx, sy)
                    e1 = VR._edge(b[0], b[1], c2[0], c2[1], sx, sy)
                    e2 = VR._edge(c2[0], c2[1], a[0], a[1], sx, sy)
                    if e0 + b0 < 0 or e1 + b1 < 0 or e2 + b2 < 0:
                        continue
                    d = (a[2] * e1 + b[2] * e2 + c2[2] * e0) // area
                    i = py * VR.W + px
                    covered.setdefault(pk, set()).add(i)
                    ties.setdefault(i, []).append(d)
                    if dep[i] is None or (d, pk) < (dep[i], key[i] if key[i] >= 0 else (1 << 62)):
                        dep[i] = d
                        key[i] = pk
    return key, covered, ties


def the_control_arm_matches_the_ladder():
    """A FOURTH transcription is a fourth chance to drift, so the control is pinned to the third."""
    _n, sym, S = _level()
    prims = VX.primitives_with("reversed")
    for _nm, eye, fwd in VR.TRACE:
        if render_arm("committed", prims, eye, fwd)[0] != VT.render_level(prims, eye, fwd, sym, S):
            return False
    return True


# ---- the oracle, at either convention ----------------------------------------------------------------
def ray_at(eye, fwd, px, py, convention):
    """The world ray through a pixel at the declared convention.

    `corner` is `voxray.ray_for_pixel` verbatim. `centre` is the same derivation at (px+1/2, py+1/2),
    carried in DOUBLED integers so the half is exact and no float or rounding enters the oracle.
    """
    if convention not in CONVENTIONS:
        raise VoxfillError("VOXFILL-REFUSE: no convention named %r" % (convention,))
    if convention == "corner":
        return VX.ray_for_pixel(eye, fwd, px, py)
    r, f, u = VR.basis(fwd)
    a = 2 * (px - VR.W // 2) + 1
    b = 2 * VR.FOCAL
    c = 2 * (VR.H // 2 - py) - 1
    return (r[0] * a + f[0] * b + u[0] * c,
            r[1] * a + f[1] * b + u[1] * c,
            r[2] * a + f[2] * b + u[2] * c)


def the_centre_ray_is_the_corner_ray_shifted_half_a_pixel():
    """VALIDITY OF THE CONTROL, not its outcome: the two rays must differ, and the centre ray must
    be the corner ray of the SAME derivation with a half-pixel added — checked by rebuilding the
    corner ray from doubled integers and requiring it to equal `voxray`'s."""
    eye, fwd = VR.TRACE[0][1], VR.TRACE[0][2]
    r, f, u = VR.basis(fwd)
    for px, py in ((0, 0), (10, 0), (48, 36), (95, 71)):
        a, b, c = 2 * (px - VR.W // 2), 2 * VR.FOCAL, 2 * (VR.H // 2 - py)
        doubled = tuple(r[j] * a + f[j] * b + u[j] * c for j in range(3))
        plain = VX.ray_for_pixel(eye, fwd, px, py)
        if doubled != tuple(2 * v for v in plain):
            return False
        if ray_at(eye, fwd, px, py, "centre") == ray_at(eye, fwd, px, py, "corner"):
            return False
    return True


_ORACLE = {}


def oracle_frame(frame, convention):
    """(voxel, face) or None per pixel, materialised once per (frame, convention) per process.

    Keyed on the world digest for the same reason `voxtie`'s census is: a materialisation that
    cannot be invalidated is worse than no materialisation at all.
    """
    k = (VR.world_digest(), frame, convention)
    if k not in _ORACLE:
        _nm, eye, fwd = VR.TRACE[frame]
        _ORACLE[k] = [
            (lambda h: None if h is None else (h[0], h[1]))(
                VX.first_hit(eye, ray_at(eye, fwd, i % VR.W, i // VR.W, convention),
                             VR.solid, VC.ORIGIN))
            for i in range(VR.W * VR.H)]
    return _ORACLE[k]


# ---- the population, and why each pixel was rejected --------------------------------------------------
def population():
    """`voxfate`'s conditioned pixels restricted to the coverage fate — the 318 this rung explains.

    THE DECOMPOSITION IS NOT RECOMBINED. `voxfate` split the 378 stable disagreements into 318
    `not_covered`, 58 `depth_rejected` and 2 `phantom`; those are three mechanisms and this rung
    speaks only for the first. Merging them into one `disagreement` count would be the averaging
    `voxfate` was built to undo.
    """
    return [(f, px, py, imp) for f, px, py, fate, imp in VS.fates() if fate == FATE]


def the_decomposition_is_not_recombined():
    whole = VS.fates()
    mine = population()
    return 0 < len(mine) == sum(1 for r in whole if r[3] == FATE) < len(whole)


def _triangles(prims, eye, fwd):
    """pk -> the rasterised triangles of that primitive, with their biases and candidate box."""
    _n, _sym, S = _level()
    m = VR.basis(fwd)
    cx, cy = VR.W // 2, VR.H // 2
    out = {}
    for pk, _col, quad in prims:
        cam = [VR._project(v, eye, m) for v in quad]
        if any(c[1] < VR.NEAR for c in cam):
            continue
        scr = [((cx * S * c[1] + c[0] * VR.FOCAL * S) // c[1],
                (cy * S * c[1] - c[2] * VR.FOCAL * S) // c[1], c[1]) for c in cam]
        tris = []
        for a, b, c2 in ((scr[0], scr[1], scr[2]), (scr[0], scr[2], scr[3])):
            area = (b[0] - a[0]) * (c2[1] - a[1]) - (b[1] - a[1]) * (c2[0] - a[0])
            if area <= 0:
                continue
            xl = max(min(a[0], b[0], c2[0]) // S, 0)
            xh = min(max(a[0], b[0], c2[0]) // S, VR.W - 1)
            yl = max(min(a[1], b[1], c2[1]) // S, 0)
            yh = min(max(a[1], b[1], c2[1]) // S, VR.H - 1)
            if xl > xh or yl > yh:
                continue
            tris.append((a, b, c2,
                         (VR._top_left_bias(a[0], a[1], b[0], b[1]),
                          VR._top_left_bias(b[0], b[1], c2[0], c2[1]),
                          VR._top_left_bias(c2[0], c2[1], a[0], a[1])),
                         (xl, xh, yl, yh)))
        if tris:
            out[pk] = tris
    return out


def _within_one_pixel(e, ax, ay, bx, by, S):
    """|e| / |edge| < 1 pixel, EXACTLY: square both sides so no root is taken and no float appears.

    The perpendicular distance from the sample to the edge is |e| divided by the edge's length in
    sub-pixel units; one pixel is S of those units. `e*e < S*S*(dx*dx + dy*dy)` is that comparison
    with both sides multiplied by the (positive) squared length.
    """
    dx, dy = bx - ax, by - ay
    return e * e < S * S * (dx * dx + dy * dy)


def rejection_of(tris, px, py):
    """(class, rejecting edge indices, near) for the oracle's face at one pixel.

    The CLOSEST class across the face's two triangles is taken, because a quad covered by either
    triangle is covered. `near` is true when every rejecting edge falls short by less than a pixel.
    A pixel outside the candidate box is `bbox` whatever its edge functions say — it was never
    tested, and calling it `outside` would attribute to geometry a rejection the loop never made.
    """
    _n, _sym, S = _level()
    best = None
    for a, b, c2, bb, (xl, xh, yl, yh) in tris:
        sx, sy = px * S, py * S
        e = (VR._edge(a[0], a[1], b[0], b[1], sx, sy),
             VR._edge(b[0], b[1], c2[0], c2[1], sx, sy),
             VR._edge(c2[0], c2[1], a[0], a[1], sx, sy))
        rej = tuple(j for j in range(3) if e[j] + bb[j] < 0)
        if not (xl <= px <= xh and yl <= py <= yh):
            cls, near = "bbox", True
        elif not rej:
            cls, near = "covered", True
        elif all(e[j] == 0 for j in rej):
            cls, near = "bias_only", True
        else:
            cls = "outside"
            pts = ((a, b), (b, c2), (c2, a))
            near = all(_within_one_pixel(e[j], pts[j][0][0], pts[j][0][1],
                                         pts[j][1][0], pts[j][1][1], S) for j in rej)
        if best is None or REJECTIONS.index(cls) > REJECTIONS.index(best[0]):
            best = (cls, rej, near)
    return best if best is not None else ("bbox", (), True)


_REJ = {}


def rejection_census():
    """(frame, px, py, class, edges, near, impossible) for every pixel of the population."""
    k = VR.world_digest()
    if k not in _REJ:
        prims = VX.primitives_with("reversed")
        by_frame = {}
        for f, px, py, imp in population():
            by_frame.setdefault(f, []).append((px, py, imp))
        rows = []
        for f in sorted(by_frame):
            _nm, eye, fwd = VR.TRACE[f]
            tris = _triangles(prims, eye, fwd)
            ora = oracle_frame(f, "corner")
            for px, py, imp in by_frame[f]:
                o = ora[py * VR.W + px]
                pk = (((o[0][0] * VR.N) + o[0][1]) * VR.N + o[0][2]) * 6 + o[1]
                cls, rej, near = rejection_of(tris.get(pk, []), px, py)
                rows.append((f, px, py, cls, rej, near, imp))
        _REJ[k] = rows
    return _REJ[k]


def rejection_distribution():
    d = dict.fromkeys(REJECTIONS, 0)
    for r in rejection_census():
        d[r[3]] += 1
    return d


def near_misses():
    """(within one pixel, beyond one pixel) among the `outside` rejections."""
    rows = [r for r in rejection_census() if r[3] == "outside"]
    near = sum(1 for r in rows if r[5])
    return near, len(rows) - near


def the_classification_is_exhaustive():
    return sum(rejection_distribution().values()) == len(population()) > 0


def the_rejections_are_not_a_covering_failure():
    """`covered` must be EMPTY: a pixel `voxfate` calls `not_covered` cannot be covered here, or the
    two modules are measuring different renderers."""
    return rejection_distribution()["covered"] == 0


def the_outside_rejections_are_sub_pixel():
    """THE SHORTFALL IS THE QUANTUM OF THE FLOOR, NOT A GEOMETRIC MISS. Nearly every `outside`
    rejection falls short by less than one pixel — measured by exact integer comparison, never by a
    square root — which is what makes the sample point a candidate at all."""
    near, far = near_misses()
    return near > 10 * far


# ---- the arms ----------------------------------------------------------------------------------------
_READING = {}


def arm_reading(arm, convention):
    """(agree, impossible, covered_rescued, won_rescued, gained, lost, changed) for one arm.

    `gained`/`lost` are counted over the WHOLE framebuffer against the control arm, because a
    rescue inside the conditioned population is not a repair if it costs more outside it — and a
    rung reporting only the rescue would be reporting the half of the ledger it chose.
    """
    if arm not in ARMS:
        raise VoxfillError("VOXFILL-REFUSE: no arm named %r" % (arm,))
    if convention not in CONVENTIONS:
        raise VoxfillError("VOXFILL-REFUSE: no convention named %r" % (convention,))
    k = (VR.world_digest(), arm, convention)
    if k in _READING:
        return _READING[k]
    prims = VX.primitives_with("reversed")
    pop = {}
    for f, px, py, _imp in population():
        pop.setdefault(f, []).append((px, py))
    agree = imposs = cov = won = gained = lost = changed = 0
    for f, (_nm, eye, fwd) in enumerate(VR.TRACE):
        key, covered, _ties = render_arm(arm, prims, eye, fwd)
        base = key if arm == "committed" else render_arm("committed", prims, eye, fwd)[0]
        ora = oracle_frame(f, convention)
        own = tuple(e // VR.Q for e in eye)
        for i in range(VR.W * VR.H):
            r, o = VM.winner_answer(key[i]), ora[i]
            now = r is not None and o is not None and r[0] != "extra" and r == o
            bw = VM.winner_answer(base[i])
            was = bw is not None and o is not None and bw[0] != "extra" and bw == o
            agree += 1 if now else 0
            gained += 1 if (now and not was) else 0
            lost += 1 if (was and not now) else 0
            changed += 1 if key[i] != base[i] else 0
            if r is not None and r[0] != "extra" and VM.impossible_winner(r[0], r[1], VR.solid, own):
                imposs += 1
        corner = oracle_frame(f, "corner")
        for px, py in pop.get(f, ()):
            i = py * VR.W + px
            o = corner[i]
            pk = (((o[0][0] * VR.N) + o[0][1]) * VR.N + o[0][2]) * 6 + o[1]
            cov += 1 if i in covered.get(pk, ()) else 0
            won += 1 if VM.winner_answer(key[i]) == o else 0
    _READING[k] = (agree, imposs, cov, won, gained, lost, changed)
    return _READING[k]


def bbox_admitted_by_padding():
    """(admitted, then covered) among the `bbox` class when the candidate box is padded by a pixel.

    WITHOUT THIS THE INERTNESS LAW WOULD BE VACUOUS. `wide_bbox` changing nothing is only evidence
    that the box is a conservative superset if the padding actually ADMITTED the excluded pixels;
    if it admitted none, the same green would mean the padding was too small to reach them.
    """
    prims = VX.primitives_with("reversed")
    _n, _sym, S = _level()
    admitted = covered = 0
    for f, px, py, cls, _rej, _near, _imp in rejection_census():
        if cls != "bbox":
            continue
        _nm, eye, fwd = VR.TRACE[f]
        o = oracle_frame(f, "corner")[py * VR.W + px]
        pk = (((o[0][0] * VR.N) + o[0][1]) * VR.N + o[0][2]) * 6 + o[1]
        got_in = passed = False
        for a, b, c2, bb, (xl, xh, yl, yh) in _triangles(prims, eye, fwd).get(pk, []):
            if not (xl - 1 <= px <= xh + 1 and yl - 1 <= py <= yh + 1):
                continue
            got_in = True
            e = (VR._edge(a[0], a[1], b[0], b[1], px * S, py * S),
                 VR._edge(b[0], b[1], c2[0], c2[1], px * S, py * S),
                 VR._edge(c2[0], c2[1], a[0], a[1], px * S, py * S))
            if all(e[j] + bb[j] >= 0 for j in range(3)):
                passed = True
        admitted += 1 if got_in else 0
        covered += 1 if passed else 0
    return admitted, covered


def the_bbox_excludes_only_what_the_edges_reject():
    """THE CANDIDATE BOX IS ELIMINATED, AND BY A STRONGER STATEMENT THAN THE ONE FIRST WRITTEN.

    The first version of this law asserted the `bbox` class was EMPTY. It is not: three pixels of
    the population never entered the loop, each exactly one pixel right of the box. Padding admits
    all three and all three still fail the edge test, so `wide_bbox` moves not one pixel ANYWHERE on
    screen — not merely inside the population. The box is a conservative superset of what the edges
    accept, which is what actually eliminates the mechanism; `the class is empty` would have been a
    claim the data refuses, and `the arm changed nothing` alone would have been vacuous.
    """
    admitted, covered = bbox_admitted_by_padding()
    d = rejection_distribution()
    return (d["bbox"] > 0 and admitted == d["bbox"] and covered == 0
            and arm_reading("wide_bbox", "corner")[6] == 0
            and arm_reading("wide_bbox", "corner")[:2] == arm_reading("committed", "corner")[:2])


def the_ownership_arm_pays_for_what_it_buys():
    """`inclusive` rescues most of the population and its net is a fraction of its gross, because
    dropping the bias turns the partition into a cover and hands the pixels it opens to the
    `(depth, face_key)` tiebreak `voxtie` measured at ZERO of its own ceiling."""
    a = arm_reading("inclusive", "corner")
    c = arm_reading("committed", "corner")
    return a[4] > 0 and a[5] > 0 and (a[0] - c[0]) < a[4] // 2 and a[3] > len(population()) // 2


def tie_losses():
    """Of `inclusive`'s losses against the control, how many the tiebreak decides at equal depth."""
    prims = VX.primitives_with("reversed")
    tie = other = 0
    for f, (_nm, eye, fwd) in enumerate(VR.TRACE):
        base = render_arm("committed", prims, eye, fwd)[0]
        key, _cov, ties = render_arm("inclusive", prims, eye, fwd)
        ora = oracle_frame(f, "corner")
        for i in range(VR.W * VR.H):
            o = ora[i]
            bw, nw = VM.winner_answer(base[i]), VM.winner_answer(key[i])
            was = bw is not None and o is not None and bw[0] != "extra" and bw == o
            now = nw is not None and o is not None and nw[0] != "extra" and nw == o
            if was and not now:
                cs = ties.get(i, [])
                if cs and cs.count(min(cs)) > 1:
                    tie += 1
                else:
                    other += 1
    return tie, other


def the_cost_lands_on_the_parked_tie_rule():
    """The coupling is MEASURED, NOT BUILT. Most of `inclusive`'s losses are pixels that become
    exact-depth ties, which is `voxtie`'s parked question arriving from the other side — and the
    combined arm is deliberately not run, because a two-variable change explains nothing."""
    tie, other = tie_losses()
    return tie > other


# ---- the convention control ---------------------------------------------------------------------------
def convention_table():
    """{(sample convention, ray convention): (agree, impossible)} — the 2x2 that decides the rung."""
    out = {}
    for arm, sample in (("committed", "corner"), ("centre", "centre")):
        for ray in CONVENTIONS:
            out[(sample, ray)] = arm_reading(arm, ray)[:2]
    return out


def the_conventions_must_agree():
    """BOTH CONSISTENT PAIRINGS BEAT BOTH MIXED ONES. That is the shape of a convention error and
    not of a renderer defect: neither side is wrong alone, and any experiment holding the oracle
    fixed sees only half of it."""
    t = convention_table()
    diag = (t[("corner", "corner")][0], t[("centre", "centre")][0])
    off = (t[("corner", "centre")][0], t[("centre", "corner")][0])
    return min(diag) > max(off)


def the_sample_point_is_the_defect():
    """THE ORACLE-FREE NUMBER. `impossible` counts pixels awarded to a face sandwiched between two
    solid cells; it involves no oracle and no convention can argue with it, and the sample point
    ALONE takes it down by more than an order of magnitude."""
    c = arm_reading("committed", "corner")[1]
    s = arm_reading("centre", "corner")[1]
    return c > 10 * s and s >= 0


def the_ownership_rescue_is_an_artefact():
    """THIS RUNG'S OWN LEADING HYPOTHESIS, REFUTED BY ITS OWN CONTROL. `inclusive` gains under the
    misaligned convention and LOSES under the aligned one — same single change, opposite sign — so
    the 215 `bias_only` pixels were an artefact of sampling a floored triangle at its corner and
    not evidence against the top-left rule. A rung that had adopted the biggest class would redden
    here."""
    corner = arm_reading("inclusive", "corner")[0] - arm_reading("committed", "corner")[0]
    centre = aligned_inclusive()[0] - arm_reading("centre", "centre")[0]
    return corner > 0 > centre


_ALIGNED = {}


def aligned_inclusive():
    """(agree, impossible) for centre sampling with the bias dropped, against the centre-ray oracle.

    THE ONLY THREE-VARIABLE POINT IN THIS MODULE, and it is a CONTROL ON THIS RUNG'S OWN CLAIM
    rather than an arm: without it `inclusive` would stand as the answer on the strength of the
    largest class, and the largest class is the artefact.
    """
    k = VR.world_digest()
    if k in _ALIGNED:
        return _ALIGNED[k]
    _n, _sym, S = _level()
    prims = VX.primitives_with("reversed")
    agree = imposs = 0
    for f, (_nm, eye, fwd) in enumerate(VR.TRACE):
        m = VR.basis(fwd)
        cx, cy = VR.W // 2, VR.H // 2
        dep = [None] * (VR.W * VR.H)
        key = [-1] * (VR.W * VR.H)
        for pk, _col, quad in prims:
            cam = [VR._project(v, eye, m) for v in quad]
            if any(c[1] < VR.NEAR for c in cam):
                continue
            scr = [((cx * S * c[1] + c[0] * VR.FOCAL * S) // c[1],
                    (cy * S * c[1] - c[2] * VR.FOCAL * S) // c[1], c[1]) for c in cam]
            for a, b, c2 in ((scr[0], scr[1], scr[2]), (scr[0], scr[2], scr[3])):
                area = (b[0] - a[0]) * (c2[1] - a[1]) - (b[1] - a[1]) * (c2[0] - a[0])
                if area <= 0:
                    continue
                xl = max(min(a[0], b[0], c2[0]) // S, 0)
                xh = min(max(a[0], b[0], c2[0]) // S, VR.W - 1)
                yl = max(min(a[1], b[1], c2[1]) // S, 0)
                yh = min(max(a[1], b[1], c2[1]) // S, VR.H - 1)
                if xl > xh or yl > yh:
                    continue
                for py in range(yl, yh + 1):
                    for px in range(xl, xh + 1):
                        sx, sy = px * S + S // 2, py * S + S // 2
                        e0 = VR._edge(a[0], a[1], b[0], b[1], sx, sy)
                        e1 = VR._edge(b[0], b[1], c2[0], c2[1], sx, sy)
                        e2 = VR._edge(c2[0], c2[1], a[0], a[1], sx, sy)
                        if e0 < 0 or e1 < 0 or e2 < 0:
                            continue
                        d = (a[2] * e1 + b[2] * e2 + c2[2] * e0) // area
                        i = py * VR.W + px
                        if dep[i] is None or (d, pk) < (dep[i],
                                                       key[i] if key[i] >= 0 else (1 << 62)):
                            dep[i] = d
                            key[i] = pk
        ora = oracle_frame(f, "centre")
        own = tuple(e // VR.Q for e in eye)
        for i in range(VR.W * VR.H):
            r, o = VM.winner_answer(key[i]), ora[i]
            if r is not None and o is not None and r[0] != "extra" and r == o:
                agree += 1
            if r is not None and r[0] != "extra" and VM.impossible_winner(r[0], r[1], VR.solid, own):
                imposs += 1
    _ALIGNED[k] = (agree, imposs)
    return _ALIGNED[k]


def every_arm_is_order_independent():
    """DRAW ORDER MUST STAY UNOBSERVABLE UNDER EVERY ARM, and the result corrects a belief this tree
    has carried since `voxref`: the top-left partition is NOT what deletes draw order — the
    `(depth, face_key)` tiebreak already does, on a written datum — so dropping the bias costs the
    cover its uniqueness without costing the picture its determinism."""
    prims = VX.primitives_with("reversed")
    rev = list(reversed(prims))
    for arm in ARMS:
        for _nm, eye, fwd in VR.TRACE:
            if render_arm(arm, prims, eye, fwd)[0] != render_arm(arm, rev, eye, fwd)[0]:
                return False
    return True


def no_convention_is_adopted():
    """`voxref` AND `voxray` are both untouched. This rung measures the convention; adopting it
    would change what the ORACLE is and reach every record derived from it."""
    return (VC.the_committed_reference_is_untouched()
            and VX.ray_for_pixel(VR.TRACE[0][1], VR.TRACE[0][2], 10, 0)
            == ray_at(VR.TRACE[0][1], VR.TRACE[0][2], 10, 0, "corner"))


# ---- the record ---------------------------------------------------------------------------------------
RECORD = os.path.join("spec", "attest", "voxref-fill.txt")


def population_digest():
    body = "\n".join("%d %d %d %s %s %d %d" % (f, px, py, cls, "".join(str(j) for j in rej),
                                               1 if near else 0, imp)
                     for f, px, py, cls, rej, near, imp in rejection_census())
    return hashlib.sha256(MAGIC + b"|reject|" + body.encode()).hexdigest()


def generate():
    d = rejection_distribution()
    near, far = near_misses()
    t = convention_table()
    rows = ["# URDRVXL1 fill-rule census — emitted by voxfill.generate(), committed as an artifact,",
            "# re-derived by the gate.",
            "# world %s" % VR.world_digest(),
            "# THE POPULATION IS `voxfate`'s %d stable %s pixels and nothing else. Each is"
            % (len(population()), FATE),
            "# classified by reading the three edge functions of the ORACLE'S OWN FACE at the exact",
            "# sample point, so the arms are predicted before they are run.",
            "#   reject  <class> <count>",
            "#   near    <within one pixel> <beyond one pixel>",
            "#   padded  <bbox-class pixels admitted by a one-pixel pad> <of those, then covered>",
            "#   arm     <arm> <ray convention> <agree> <impossible> <covered> <won> <gained>"
            " <lost> <changed>",
            "#   pair    <sample> <ray> <agree> <impossible>",
            "#   aligned <agree> <impossible>",
            "#   tie     <losses decided by an exact-depth tie> <decided outright>",
            "#   pixel   <frame> <px> <py> <class> <edges> <near> <impossible>",
            "#   digest  <population digest>"]
    for c in REJECTIONS:
        rows.append("reject %s %d" % (c, d[c]))
    rows.append("near %d %d" % (near, far))
    rows.append("padded %d %d" % bbox_admitted_by_padding())
    for arm in ARMS:
        for conv in CONVENTIONS:
            rows.append("arm %s %s %d %d %d %d %d %d %d" % ((arm, conv) + arm_reading(arm, conv)))
    for (s, r), v in sorted(t.items()):
        rows.append("pair %s %s %d %d" % (s, r, v[0], v[1]))
    rows.append("aligned %d %d" % aligned_inclusive())
    rows.append("tie %d %d" % tie_losses())
    for f, px, py, cls, rej, near_i, imp in rejection_census():
        rows.append("pixel %d %d %d %s %s %d %d"
                    % (f, px, py, cls, "".join(str(j) for j in rej) or "-", 1 if near_i else 0, imp))
    rows.append("digest %s" % population_digest())
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
        if f[0] == "reject":
            if len(f) != 3 or f[1] not in REJECTIONS:
                raise VoxfillError("VOXFILL-REFUSE: a reject row in no declared class")
        elif f[0] == "arm":
            if len(f) != 10 or f[1] not in ARMS or f[2] not in CONVENTIONS:
                raise VoxfillError("VOXFILL-REFUSE: an arm row naming no declared arm")
        elif f[0] == "pair":
            if len(f) != 5 or f[1] not in CONVENTIONS or f[2] not in CONVENTIONS:
                raise VoxfillError("VOXFILL-REFUSE: a pair row naming no declared convention")
        elif f[0] == "pixel":
            if len(f) != 8 or f[4] not in REJECTIONS:
                raise VoxfillError("VOXFILL-REFUSE: a pixel row in no declared class")
        elif f[0] not in ("near", "padded", "aligned", "tie", "digest"):
            raise VoxfillError("VOXFILL-REFUSE: a row of unknown kind %r" % (f[0],))
        rows.append(tuple(f))
    if world is None:
        raise VoxfillError("VOXFILL-REFUSE: the record names no world digest")
    if not rows:
        raise VoxfillError("VOXFILL-REFUSE: the record has no rows")
    return world, rows


def the_record_names_this_world():
    return parse()[0] == VR.world_digest()


def the_record_is_bound_to_the_live_code():
    _w, rows = parse()
    d = rejection_distribution()
    for r in rows:
        if r[0] == "reject" and int(r[2]) != d[r[1]]:
            return False
        if r[0] == "arm" and tuple(int(x) for x in r[3:]) != arm_reading(r[1], r[2]):
            return False
    pinned = next(r[1] for r in rows if r[0] == "digest")
    return pinned == population_digest()


def a_tampered_row_refuses():
    text = _read()
    for ln in text.split("\n"):
        if ln.startswith("pixel "):
            f = ln.split()
            f[4] = "elsewhere"
            text = text.replace(ln, " ".join(f), 1)
            break
    try:
        parse(text)
    except VoxfillError:
        return True
    return False


def told():
    d = rejection_distribution()
    near, far = near_misses()
    t = convention_table()
    ai = aligned_inclusive()
    inc = arm_reading("inclusive", "corner")
    com = arm_reading("committed", "corner")
    ctr = arm_reading("centre", "corner")
    tie, other = tie_losses()
    return ("of the %d stable %s pixels, %d are rejected ONLY by the top-left bias (the sample sits "
            "exactly on the edge), %d are outside by at least one edge — %d of those by less than a "
            "pixel — and %d never entered the candidate loop at all, though padding the box admits "
            "all of them and none then passes the edges, so `wide_bbox` moves not one pixel "
            "anywhere on screen. Dropping the bias rescues %d of the %d and nets only "
            "%+d, because %d of its %d losses become exact-depth ties. THE 2x2 DECIDES IT: "
            "corner/corner %d, corner/centre %d, centre/corner %d, centre/centre %d — both "
            "consistent pairings beat both mixed ones, and impossible faces fall %d -> %d on the "
            "SAMPLE POINT ALONE, which needs no oracle. And the leading hypothesis is refused by "
            "its own control: with the conventions aligned, dropping the bias scores %d against "
            "%d and raises impossible from %d to %d"
            % (len(population()), FATE, d["bias_only"], d["outside"], near, d["bbox"],
               inc[3], len(population()), inc[0] - com[0], tie, tie + other,
               t[("corner", "corner")][0], t[("corner", "centre")][0],
               t[("centre", "corner")][0], t[("centre", "centre")][0],
               com[1], ctr[1], ai[0], t[("centre", "centre")][0], t[("centre", "centre")][1],
               ai[1]))


def scene_case(name):
    if name == "rejections":
        return repr((rejection_distribution(), near_misses(), population_digest()))
    if name == "arms":
        return repr(tuple((a, c, arm_reading(a, c)) for a in ARMS for c in CONVENTIONS))
    if name == "conventions":
        return repr((sorted(convention_table().items()), aligned_inclusive(), tie_losses()))
    raise VoxfillError("VOXFILL-REFUSE: no scene named %r" % name)


def scene_result(name):
    return hashlib.sha256(MAGIC + b"|" + name.encode() + b"|"
                          + scene_case(name).encode()).hexdigest()


SCENES = ("rejections", "arms", "conventions")


def golden(name):
    with open(os.path.join(_HERE, "conformance_voxfill.txt"), encoding="utf-8") as fh:
        for ln in fh:
            ln = ln.strip()
            if ln and not ln.startswith("#"):
                nm, dig = ln.split()
                if nm == name:
                    return dig
    raise VoxfillError("VOXFILL-REFUSE: no golden named %r" % name)
