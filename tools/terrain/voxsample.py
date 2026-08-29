# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""voxsample (URDRVXA1) — ARE THE RASTERISER AND THE ORACLE TALKING ABOUT THE SAME SAMPLE POINT?

DIAGNOSTIC ONLY. No arm, no candidate, no altered renderer, no moved convention, and the 2 exact
ties and 2 phantoms stay QUARANTINED — neither is a sample-construction question.

`voxproj` eliminated the rounding DIRECTION as the governing defect. The next question is not more
precision but whether the two programs are describing the same point at all. Three constructions
have to be checked against each other, exactly:

    coverage         the fill rule evaluates its edge functions at `(px*S, py*S)` — the screen
                     point (px, py) and nothing else
    interpolation    the depth barycentrics read the SAME three edge values, so the same point
    oracle           `voxray.ray_for_pixel` inverts (px, py) through the camera basis

AND THE ANSWER IS NO, ON THREE OF THE EIGHT DECLARED FRAMES. The integer camera basis is EXACTLY
orthonormal on five of them and NOT on the other three — frames 4, 5 and 6 carry non-zero
off-diagonal dot products and three different row norms — so `ray_for_pixel` is an APPROXIMATE
inverse there, not an exact one, and `voxray`'s own docstring calls it a derivation by inversion.
The departure is small and it is now measured rather than assumed: the worst round-trip offset over
the whole trace is 0.0038 px, about a quarter of one sub-pixel unit at S=64.

BUT THAT IS NOT THE SEAM, AND THE REAL ONE IS UPSTREAM OF EVERY RUNG SO FAR. Carry the basis
multiply at FULL PRECISION — no `>> 16` — and project the oracle's own face exactly:

    the oracle's face CONTAINS the sample at   316 of 318
    the winner's face EXCLUDES the sample at    56 of 56

The second agrees PIXEL FOR PIXEL with `voxwin`'s independent world-space ray/face test — two exact
computations, one in screen space and one in world space, reaching the same verdict on the same
pixels. THE GEOMETRY IS RIGHT. The projection is not lying about which face covers which pixel.

NOW PUT BACK THE ONE TRUNCATION `voxref._project` ACTUALLY PERFORMS — the `>> 16` that turns the
Q16 basis multiply into an integer camera coordinate, BEFORE any screen quantisation, BEFORE the
fill rule, and before anything this arc has examined:

    the oracle's face:  316 inside  ->   10 inside, 215 ON THE EDGE, 93 OUTSIDE
    the winner's face:   56 outside ->   25 inside,  28 on the edge,  3 outside

NINETY-ONE PIXELS ARE PUSHED OUT OF A FACE THAT GEOMETRICALLY CONTAINS THEM — 93 read `outside`
under the truncation against 2 that were already outside at full precision — AND FIFTY-THREE ARE
PULLED INTO A FACE THAT DOES NOT, BY A SINGLE SHIFT. That is the dominant term, and no rung has
looked at it: `voxcand` tested winding and weights, `voxfill` tested the fill rule, `voxconv` and
`voxgrid` tested the sample convention, `voxproj` tested the screen-space rounding direction. The
camera-space truncation was upstream of all of them.

AND IT EXPLAINS THE 215. Under the truncation they land EXACTLY ON THE EDGE — and they are exactly
the pixels `voxslack` measured at coverage slack -1, asserted here as SET EQUALITY rather than a
matching count. The top-left convention is not creating that class. The truncation puts the sample
precisely on the edge and the convention then rejects it, which makes the convention the last step
in a chain rather than the cause, and `voxfill` and `voxconv` were right to exonerate it twice.

does_not_show: anything about performance. ANY REPAIR — `_project` is untouched, no arm is run, and
naming a term is not fixing it. WHETHER REMOVING THE TRUNCATION IS AFFORDABLE OR EVEN COHERENT: the
reference is integer by contract and carrying full precision changes what the depth buffer holds, so
that is a design question and a separate rung. Any mechanism for the two exceptions at full
precision. And nothing is altered: `voxref` and `voxray` are untouched, the two ties and two
phantoms are quarantined, and the frozen census stays frozen.

falsifier: `the_screen_and_world_tests_agree` asserts SET EQUALITY between the pixels this rung
finds outside the winner's exact projected triangle and the pixels `voxwin` found the ray to miss in
world space — a matching count would pass while naming different pixels; and
`the_on_edge_class_is_made_by_the_truncation` asserts SET EQUALITY between the pixels the truncation
puts exactly on an edge and `voxslack`'s coverage-slack -1 class, so the explanation of the 215 is
checked against an independently computed population rather than asserted.
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
import voxslack as VK                                        # noqa: E402
import voxwin as VW                                          # noqa: E402

MAGIC = b"URDRVXA1"

#: DECLARED — the three constructions that must be compared, named for what evaluates them.
CONSTRUCTIONS = ("coverage", "interpolation", "oracle")

#: DECLARED — the two precisions. `committed` reproduces `voxref._project`'s `>> 16`; `full` carries
#: the Q16 basis multiply without it. Neither is adopted; both are instruments.
PRECISIONS = ("committed", "full")

#: DECLARED — where the exact sample falls relative to a face's exact projected quad.
PLACES = ("outside", "backface", "behind", "on_edge", "inside")

#: DECLARED BEFORE THE ARM RAN, pinned as DATA so it cannot be retrofitted.
PREDICTION = (
    ("Q4", "the three sample constructions COINCIDE EXACTLY — the coverage predicate, the "
           "barycentric interpolation and `voxray`'s inversion all name the screen point (px, py) "
           "and nothing else — so the sample location is NOT the seam"),
    ("Q5a", "every one of the 318 pixels whose face the oracle says the ray hits is INSIDE the "
            "EXACT projected triangle of that face, because the ray's screen position IS the "
            "sample point"),
    ("Q5b", "every one of the 56 winner-side pixels is OUTSIDE the exact projected triangle of the "
            "face the rasteriser awarded, agreeing pixel-for-pixel with `voxwin`'s exact "
            "WORLD-space ray/face test"),
    ("Q6", "the seam is therefore the OBJECT and not the POINT: the coverage predicate tests a "
           "quantised triangle while the oracle tests exact geometry, and the sample point is "
           "innocent"),
    ("Q7", "the two ties and the two phantoms are untouched and stay quarantined, since neither is "
           "a sample-construction question"),
)


class VoxsampleError(Exception):
    """VOXSAMPLE-REFUSE — a precision or a record this module will not pretend to read."""


# ---- the exact projection, at either precision ---------------------------------------------------------
def vertex(v, eye, m, precision):
    """The EXACT screen position of a world point as (x numerator, y numerator, denominator).

    `committed` applies `voxref._project`'s `>> 16` and so reproduces the reference's own camera
    coordinates; `full` carries the Q16 basis multiply intact. The factor cancels in the ratio, so
    the two differ ONLY by that truncation and by nothing else — which is what makes the pair a
    single-variable comparison rather than two projections.
    """
    if precision not in PRECISIONS:
        raise VoxsampleError("VOXSAMPLE-REFUSE: no precision named %r" % (precision,))
    cx, cy = VR.W // 2, VR.H // 2
    dx, dy, dz = v[0] - eye[0], v[1] - eye[1], v[2] - eye[2]
    r, f, u = m
    cr = r[0] * dx + r[1] * dy + r[2] * dz
    cf = f[0] * dx + f[1] * dy + f[2] * dz
    cu = u[0] * dx + u[1] * dy + u[2] * dz
    if precision == "committed":
        cr, cf, cu = cr >> 16, cf >> 16, cu >> 16
    return (cx * cf + cr * VR.FOCAL, cy * cf - cu * VR.FOCAL, cf)


def edge(A, B, px, py):
    """The edge function at the exact integer sample, as an exact integer whose SIGN is the test.

    The true value carries a positive denominator `da*da*db`, which cannot change a sign, so it is
    never formed. No float, no rational object, no epsilon.
    """
    ax, ay, da = A
    bx, by, db = B
    return (bx * da - ax * db) * (py * da - ay) - (by * da - ay * db) * (px * da - ax)


def area(A, B, C):
    ax, ay, da = A
    bx, by, db = B
    cx2, cy2, dc = C
    return ((bx * da - ax * db) * (cy2 * da - ay * dc)
            - (by * da - ay * db) * (cx2 * da - ax * dc))


def place(quad, eye, m, px, py, precision):
    """Where the exact sample falls relative to a face's exact projected quad, best of its two
    triangles — because a quad covered by either triangle is covered."""
    E = [vertex(v, eye, m, precision) for v in quad]
    if any(e[2] <= 0 for e in E):
        return "behind"
    best = None
    for a, b, c in ((E[0], E[1], E[2]), (E[0], E[2], E[3])):
        if area(a, b, c) <= 0:
            cand = "backface"
        else:
            e = (edge(a, b, px, py), edge(b, c, px, py), edge(c, a, px, py))
            cand = ("inside" if all(x > 0 for x in e)
                    else "on_edge" if all(x >= 0 for x in e) else "outside")
        if best is None or PLACES.index(cand) > PLACES.index(best):
            best = cand
    return best


def the_place_test_bites_in_every_direction():
    """PLANTED. A test answering one word everywhere would manufacture whatever this rung claims, so
    a sample squarely inside a face must read `inside`, one squarely outside must read `outside`,
    and the exact-zero case must be reachable — checked on a constructed triangle rather than
    trusted from the population."""
    A, B, C = (0, 0, 1), (10, 0, 1), (0, 10, 1)
    inside = (edge(A, B, 2, 2) > 0 and edge(B, C, 2, 2) > 0 and edge(C, A, 2, 2) > 0)
    outside = edge(A, B, 2, -3) < 0
    on = edge(A, B, 5, 0) == 0
    return inside and outside and on and area(A, B, C) > 0 and area(A, C, B) < 0


# ---- the camera basis --------------------------------------------------------------------------------
def basis_dots(frame):
    """The six exact dot products of the integer camera basis rows on one declared frame."""
    rows = VR.basis(VR.TRACE[frame][2])
    return tuple(sum(rows[i][k] * rows[j][k] for k in range(3))
                 for i in range(3) for j in range(i, 3))


def orthonormal_frames():
    """The frames whose integer basis is EXACTLY orthonormal — equal norms, zero off-diagonals."""
    out = []
    for f in range(len(VR.TRACE)):
        d = basis_dots(f)
        norms, offs = (d[0], d[3], d[5]), (d[1], d[2], d[4])
        if norms[0] == norms[1] == norms[2] and offs == (0, 0, 0):
            out.append(f)
    return tuple(out)


def round_trip_worst():
    """(numerator, denominator) of the worst round-trip offset in PIXELS, as an exact fraction.

    `ray_for_pixel` builds a direction from the basis rows and `_project` reads it back with the
    same rows; the two are exact inverses only when the basis is exactly orthonormal. Where it is
    not, this is how far the oracle's ray lands from the sample it was aimed at — kept as an exact
    rational and never as a float, because the quantity being bounded is smaller than a sub-pixel.
    """
    cx, cy = VR.W // 2, VR.H // 2
    best = (0, 1)
    for _nm, eye, fwd in VR.TRACE:
        r, ff, uu = VR.basis(fwd)
        for py in range(0, VR.H, 7):
            for px in range(0, VR.W, 7):
                a, b, c = px - cx, VR.FOCAL, cy - py
                d = tuple(r[j] * a + ff[j] * b + uu[j] * c for j in range(3))
                cf = sum(ff[j] * d[j] for j in range(3))
                if cf <= 0:
                    continue
                cr = sum(r[j] * d[j] for j in range(3))
                cu = sum(uu[j] * d[j] for j in range(3))
                for num in (abs(cr * VR.FOCAL - (px - cx) * cf),
                            abs(cu * VR.FOCAL - (cy - py) * cf)):
                    if num * best[1] > best[0] * cf:
                        best = (num, cf)
    return best


def the_basis_is_not_always_orthonormal():
    """MEASURED, NOT ASSUMED. Some declared frames carry an exactly orthonormal integer basis and
    some do not, so `ray_for_pixel` is an exact inverse on the first and an approximate one on the
    rest — and `voxray`'s docstring calls it a derivation by inversion without saying which."""
    o = orthonormal_frames()
    return 0 < len(o) < len(VR.TRACE)


def the_round_trip_departure_is_bounded():
    """AND THE DEPARTURE IS SMALL. The worst offset is under a quarter of one sub-pixel unit at the
    ladder's denominator — compared as an exact fraction, so the bound is arithmetic and not a
    reading off a float."""
    num, den = round_trip_worst()
    return num > 0 and num * 256 < den


# ---- the populations, inherited and quarantined ---------------------------------------------------------
def population(name):
    if name == "cover":
        return {(r[0], r[1], r[2]) for r in VK.census() if r[3] == "not_covered"}
    if name == "winner":
        return {(r[0], r[1], r[2]) for r in VW.census() if r[3] == "ray_misses_winner"}
    if name == "on_surface":
        return {(r[0], r[1], r[2]) for r in VK.census() if r[9] == "on_surface"}
    if name == "tie":
        return {(r[0], r[1], r[2]) for r in VW.census() if r[3] == "true_tie"}
    if name == "phantom":
        return {(r[0], r[1], r[2]) for r in VK.census() if r[3] == "phantom"}
    raise VoxsampleError("VOXSAMPLE-REFUSE: no population named %r" % (name,))


_CENSUS = {}


def census():
    """(frame, px, py, which, place at full precision, place as committed)."""
    k = VR.world_digest()
    if k in _CENSUS:
        return _CENSUS[k]
    prims = VX.primitives_with("reversed")
    quad = {pk: q for pk, _c, q in prims}
    want = {}
    for w in ("cover", "winner"):
        for t in population(w):
            want.setdefault(t[0], []).append((t[1], t[2], w))
    rows = []
    for f in sorted(want):
        _nm, eye, fwd = VR.TRACE[f]
        m = VR.basis(fwd)
        ora = VM.oracle_frame(eye, fwd, VR.solid, VC.ORIGIN)
        key, _d, _c, _g, _s = VK.instrument(prims, eye, fwd)
        for px, py, w in want[f]:
            i = py * VR.W + px
            t = ora[i] if w == "cover" else VM.winner_answer(key[i])
            pk = (((t[0][0] * VR.N) + t[0][1]) * VR.N + t[0][2]) * 6 + t[1]
            rows.append((f, px, py, w,
                         place(quad[pk], eye, m, px, py, "full"),
                         place(quad[pk], eye, m, px, py, "committed")))
    _CENSUS[k] = rows
    return rows


def distribution(which, precision):
    if which not in ("cover", "winner"):
        raise VoxsampleError("VOXSAMPLE-REFUSE: no population named %r" % (which,))
    if precision not in PRECISIONS:
        raise VoxsampleError("VOXSAMPLE-REFUSE: no precision named %r" % (precision,))
    i = 4 if precision == "full" else 5
    d = dict.fromkeys(PLACES, 0)
    for r in census():
        if r[3] == which:
            d[r[i]] += 1
    return d


# ---- the laws -----------------------------------------------------------------------------------------
def the_geometry_is_right_at_full_precision():
    """THE PROJECTION IS NOT LYING ABOUT WHICH FACE COVERS WHICH PIXEL. Carried at full precision,
    the oracle's face contains almost every sample and the winner's face excludes every one."""
    c = distribution("cover", "full")
    w = distribution("winner", "full")
    return (c["inside"] * 50 > sum(c.values()) * 49
            and w["outside"] == sum(w.values()) > 0)


def the_screen_and_world_tests_agree():
    """SET EQUALITY BETWEEN TWO EXACT COMPUTATIONS IN DIFFERENT SPACES. The pixels this rung finds
    outside the winner's exact projected triangle must be EXACTLY the pixels `voxwin` found the ray
    to miss in world space — a matching count would pass while naming different pixels."""
    mine = {(r[0], r[1], r[2]) for r in census() if r[3] == "winner" and r[4] == "outside"}
    return bool(mine) and mine == population("winner")


def the_camera_truncation_is_the_dominant_term():
    """PUT BACK THE ONE SHIFT `_project` PERFORMS AND THE GEOMETRY BREAKS. Pixels a face
    geometrically contains are pushed OUT of it, and pixels it does not contain are pulled IN — by a
    truncation that happens before any screen quantisation, before the fill rule, and upstream of
    every rung this arc has run."""
    cf, cc = distribution("cover", "full"), distribution("cover", "committed")
    wf, wc = distribution("winner", "full"), distribution("winner", "committed")
    pushed_out = cc["outside"] - cf["outside"]
    pulled_in = wf["outside"] - wc["outside"]
    return pushed_out > 50 and pulled_in > 40


def the_on_edge_class_is_made_by_the_truncation():
    """AND IT EXPLAINS THE 215. Under the truncation they land EXACTLY ON THE EDGE, and they are
    exactly `voxslack`'s coverage-slack -1 class — SET EQUALITY against an independently computed
    population. The top-left convention is not creating that class; the truncation puts the sample
    precisely on the edge and the convention then rejects it, which makes the convention the last
    step in a chain rather than the cause."""
    mine = {(r[0], r[1], r[2]) for r in census() if r[3] == "cover" and r[5] == "on_edge"}
    return bool(mine) and mine == population("on_surface")


def the_ties_and_phantoms_are_quarantined():
    """Neither is a sample-construction question, and this rung does not touch either."""
    seen = {(r[0], r[1], r[2]) for r in census()}
    return (not (seen & population("tie")) and not (seen & population("phantom"))
            and len(population("tie")) > 0 and len(population("phantom")) > 0)


def verdicts():
    """{prediction id: (hit, what was measured)} — computed from the census, never from the text."""
    cf, cc = distribution("cover", "full"), distribution("cover", "committed")
    wf = distribution("winner", "full")
    o = orthonormal_frames()
    out = {}
    out["Q4"] = (len(o) == len(VR.TRACE),
                 "%d of %d frames carry an exactly orthonormal basis" % (len(o), len(VR.TRACE)))
    out["Q5a"] = (cf["inside"] == sum(cf.values()),
                  "%d of %d inside at full precision" % (cf["inside"], sum(cf.values())))
    out["Q5b"] = (the_screen_and_world_tests_agree(),
                  "%d of %d outside, set-equal to voxwin's" % (wf["outside"], sum(wf.values())))
    out["Q6"] = (the_camera_truncation_is_the_dominant_term(),
                 "the truncation pushes %d out and pulls %d in"
                 % (cc["outside"] - cf["outside"], sum(wf.values()) - distribution(
                     "winner", "committed")["outside"]))
    out["Q7"] = (the_ties_and_phantoms_are_quarantined(), "ties and phantoms untouched")
    return out


def every_prediction_has_a_verdict():
    v = verdicts()
    return sorted(v) == sorted(p for p, _t in PREDICTION) and len(v) == len(PREDICTION)


def hits():
    return tuple(sorted(p for p, (ok, _w) in verdicts().items() if ok))


def misses():
    return tuple(sorted(p for p, (ok, _w) in verdicts().items() if not ok))


def the_record_carries_hits_and_misses():
    """A rung whose every prediction landed would either be lucky or would have written them after
    the fact, and one that reported only its hits would be worse."""
    return len(hits()) > 0 and len(misses()) > 0


def nothing_is_altered():
    """`_project` is untouched, no arm is run, and naming a term is not fixing it."""
    return VC.the_committed_reference_is_untouched() and VW.nothing_is_altered()


# ---- the record ---------------------------------------------------------------------------------------
RECORD = os.path.join("spec", "attest", "voxref-sample.txt")


def population_digest():
    body = "\n".join("%d %d %d %s %s %s" % r for r in census())
    return hashlib.sha256(MAGIC + b"|sample|" + body.encode()).hexdigest()


def generate():
    rows = ["# URDRVXA1 sample-construction audit — emitted by voxsample.generate(), committed as",
            "# an artifact, re-derived by the gate.",
            "# world %s" % VR.world_digest(),
            "# DIAGNOSTIC ONLY. `_project` untouched, no arm, no candidate, ties and phantoms",
            "# quarantined.",
            "#   predict <id> <text>",
            "#   verdict <id> <HIT|MISS> <what was measured>",
            "#   basis   <frame> <six exact dot products>",
            "#   trip    <worst round-trip numerator> <denominator>",
            "#   place   <population> <precision> <place> <count>",
            "#   pixel   <frame> <px> <py> <population> <full> <committed>",
            "#   digest  <population digest>"]
    for pid, text in PREDICTION:
        rows.append("predict %s %s" % (pid, text))
    for pid, (ok, what) in sorted(verdicts().items()):
        rows.append("verdict %s %s %s" % (pid, "HIT" if ok else "MISS", what))
    for f in range(len(VR.TRACE)):
        rows.append("basis %d %s" % (f, " ".join(str(x) for x in basis_dots(f))))
    rows.append("trip %d %d" % round_trip_worst())
    for w in ("cover", "winner"):
        for p in PRECISIONS:
            for k in PLACES:
                rows.append("place %s %s %s %d" % (w, p, k, distribution(w, p)[k]))
    for r in census():
        rows.append("pixel %d %d %d %s %s %s" % r)
    rows.append("digest %s" % population_digest())
    return "\n".join(rows) + "\n"


def _read():
    with open(os.path.join(ROOT, RECORD), encoding="utf-8") as fh:
        return fh.read()


def parse(text=None):
    if text is None:
        text = _read()
    rows, world = [], None
    ids = {p for p, _t in PREDICTION}
    for ln in text.split("\n"):
        ln = ln.strip()
        if not ln:
            continue
        if ln.startswith("#"):
            if ln.startswith("# world "):
                world = ln.split()[2]
            continue
        f = ln.split()
        if f[0] == "predict" and (len(f) < 3 or f[1] not in ids):
            raise VoxsampleError("VOXSAMPLE-REFUSE: a predict row naming no declared prediction")
        if f[0] == "verdict" and (len(f) < 4 or f[1] not in ids or f[2] not in ("HIT", "MISS")):
            raise VoxsampleError("VOXSAMPLE-REFUSE: a verdict row naming no declared prediction")
        if f[0] == "place" and (len(f) != 5 or f[2] not in PRECISIONS or f[3] not in PLACES):
            raise VoxsampleError("VOXSAMPLE-REFUSE: a place row outside the declared vocabulary")
        if f[0] == "pixel" and (len(f) != 7 or f[5] not in PLACES or f[6] not in PLACES):
            raise VoxsampleError("VOXSAMPLE-REFUSE: a pixel row in no declared place")
        if f[0] not in ("predict", "verdict", "basis", "trip", "place", "pixel", "digest"):
            raise VoxsampleError("VOXSAMPLE-REFUSE: a row of unknown kind %r" % (f[0],))
        rows.append(tuple(f))
    if world is None:
        raise VoxsampleError("VOXSAMPLE-REFUSE: the record names no world digest")
    if not rows:
        raise VoxsampleError("VOXSAMPLE-REFUSE: the record has no rows")
    return world, rows


def the_record_names_this_world():
    return parse()[0] == VR.world_digest()


def the_record_is_bound_to_the_live_code():
    _w, rows = parse()
    v = verdicts()
    for r in rows:
        if r[0] == "verdict" and (r[2] == "HIT") != v[r[1]][0]:
            return False
        if r[0] == "place" and int(r[4]) != distribution(r[1], r[2])[r[3]]:
            return False
    pinned = next(r[1] for r in rows if r[0] == "digest")
    return pinned == population_digest()


def a_tampered_row_refuses():
    text = _read()
    for ln in text.split("\n"):
        if ln.startswith("pixel "):
            f = ln.split()
            f[5] = "elsewhere"
            text = text.replace(ln, " ".join(f), 1)
            break
    try:
        parse(text)
    except VoxsampleError:
        return True
    return False


def told():
    cf, cc = distribution("cover", "full"), distribution("cover", "committed")
    wf, wc = distribution("winner", "full"), distribution("winner", "committed")
    o = orthonormal_frames()
    num, den = round_trip_worst()
    return ("the three constructions do NOT all coincide: %d of %d frames carry an exactly "
            "orthonormal integer basis and the rest do not, so `ray_for_pixel` is an APPROXIMATE "
            "inverse there — bounded, and now measured, at under a quarter of one sub-pixel unit. "
            "BUT THE SEAM IS UPSTREAM OF EVERY RUNG SO FAR. At FULL precision the oracle's face "
            "contains the sample at %d of %d and the winner's face excludes it at %d of %d, the "
            "second SET-EQUAL to `voxwin`'s independent world-space test — the geometry is right. "
            "PUT BACK THE ONE `>> 16` THAT `_project` PERFORMS and %d pixels are pushed OUT of a "
            "face that contains them while %d are pulled IN to one that does not. AND IT EXPLAINS "
            "THE 215: under the truncation they land EXACTLY ON THE EDGE, set-equal to `voxslack`'s "
            "slack -1 class, so the top-left convention is the last step in a chain and not the "
            "cause"
            % (len(o), len(VR.TRACE), cf["inside"], sum(cf.values()),
               wf["outside"], sum(wf.values()),
               cc["outside"] - cf["outside"], wf["outside"] - wc["outside"]))


def scene_case(name):
    if name == "places":
        return repr(tuple((w, p, tuple(sorted(distribution(w, p).items())))
                          for w in ("cover", "winner") for p in PRECISIONS))
    if name == "basis":
        return repr((tuple(basis_dots(f) for f in range(len(VR.TRACE))),
                     orthonormal_frames(), round_trip_worst()))
    if name == "verdicts":
        return repr(sorted(verdicts().items()))
    raise VoxsampleError("VOXSAMPLE-REFUSE: no scene named %r" % name)


def scene_result(name):
    return hashlib.sha256(MAGIC + b"|" + name.encode() + b"|"
                          + scene_case(name).encode()).hexdigest()


SCENES = ("places", "basis", "verdicts")


def golden(name):
    with open(os.path.join(_HERE, "conformance_voxsample.txt"), encoding="utf-8") as fh:
        for ln in fh:
            ln = ln.strip()
            if ln and not ln.startswith("#"):
                nm, dig = ln.split()
                if nm == name:
                    return dig
    raise VoxsampleError("VOXSAMPLE-REFUSE: no golden named %r" % name)
