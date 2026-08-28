# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""voxslack (URDRVXK1) — HOW FAR IS EACH WRONG PIXEL FROM THE LAW THAT DECIDED IT?

DIAGNOSTIC ONLY. No arm, no candidate, no altered renderer, no changed convention. One question:
for each of the 378 stable disagreements, how far INSIDE or OUTSIDE each of the rasteriser's own
decision surfaces does the oracle's face sit? A wrong decision taken ON a decision surface is a
margin defect. A wrong decision taken far from every surface is not, and no threshold change can
honestly rescue it.

THE SIGN CONVENTION IS DECLARED, not inferred: POSITIVE means the predicate is satisfied with that
much room, ZERO means the sample lies exactly on the decision surface, NEGATIVE means it failed by
that much. Every slack is an exact integer in the units the reference itself computes in — edge
function for coverage, camera Q8 for depth — and the pixel buckets reuse `voxfill`'s squared
comparison rather than taking a root.

    318 not_covered      coverage slack       -1 exactly           215
                                              within one pixel     103
                                              beyond                 0

    58 depth_rejected    depth slack          exact tie              2
                                              under one cell         8
                                              a whole cell or more  46
                                              should have won        0

    2 phantom            the oracle returns nothing at all

EVERY COVERAGE MISS IS WITHIN ONE PIXEL OF THE SURFACE, AND NOT ONE IS BEYOND IT. 215 fail by
EXACTLY -1, which is the top-left bias and nothing else: the sample sits precisely ON the edge, and
the only thing rejecting it is the convention `voxfill` and `voxconv` have now exonerated twice. The
other 103 fail by a real but sub-pixel amount — the floored projected vertex. The split is between
two MECHANISMS rather than two distances, and it maps onto `voxconv` exactly: under the aligned
convention the 215 vanish and a sub-pixel remainder survives.

THE FIRST VERSION OF THIS LAW DEMANDED A `beyond` CLASS AND REDDENED. The probe behind it bucketed
on the raw edge-function magnitude and reported 95 pixels beyond a pixel; the edge function is an
AREA, not a distance, and dividing by the edge length puts every one of them inside a pixel. The law
refused to be satisfied by a structure that was not there — before the claim was written down, which
is the first time in this arc that has happened on the near side of a commit.

AND THE 58 ARE NOT A MARGIN DEFECT AT ALL, WHICH REDIRECTS A WHOLE BRANCH OF THE DIAGNOSIS. Their
depth slack is not near zero: 46 of 58 lose by a WHOLE CELL OR MORE, the median is 1.27 cells and
the maximum is 6.06, only 2 are exact ties, and NOT ONE should have won. Meanwhile their COVERAGE
slack is hugely positive — median 13552, deep inside the triangle — so they are nowhere near a
coverage boundary either. THE DEPTH COMPARISON IS DOING ITS JOB. The oracle's face really is
farther away, and it loses honestly.

SO WHAT IS WRONG AT THOSE 58 IS THAT A NEARER FACE COVERS THE PIXEL AT ALL. They are the SAME
coverage defect seen from the winner's side rather than the loser's, which means the fate
decomposition `voxfate` established — 318 coverage, 58 depth, 2 anomaly — is really 376 coverage
and 2 anomaly, with the 58 counted at the wrong end. A rung that had read `depth_rejected` as a
depth problem would have gone looking for a defect in a comparison that is behaving correctly.

does_not_show: anything about performance. WHICH face wrongly covers those 58 — this rung measures
the loser's distance to every surface and does not chase the winner, because that is a different
experiment and combining them is how a diagnosis stops being one. Any mechanism for the sub-pixel 103. Any
reading of the 2 phantoms, which is a population too small to carry one. And nothing is altered:
`voxref` and `voxray` are untouched, no arm is run, no convention is moved, and the frozen census
stays frozen.

falsifier: `the_coverage_residue_is_entirely_within_one_pixel` asserts a ZERO and plants `beyond` on
a synthetic triangle, so the zero cannot be a limitation of the bucketer; `the_residue_splits_at_the_
bias` requires BOTH classes to be substantial, so a residue collapsed to either end reddens; and
`no_stable_pixel_should_have_won_on_depth` asserts a ZERO with a plant proving a negative slack is
representable, because a zero with no reachable negative is a zero the instrument could not have
found.
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
import voxfill as VL                                         # noqa: E402

MAGIC = b"URDRVXK1"

#: DECLARED — the rasteriser's decision surfaces, in the order it applies them. A pixel that never
#: reaches a surface has no slack there, and `None` says so rather than a zero pretending to.
PREDICATES = ("near_plane", "area", "bbox", "coverage", "depth")

#: DECLARED — the sign convention, stated rather than inferred from the arithmetic.
#: POSITIVE: the predicate is satisfied with that much room.
#: ZERO:     the sample lies exactly ON the decision surface.
#: NEGATIVE: the predicate failed, by that much.
SIGN = "positive = room, zero = on the surface, negative = failed by that much"

#: DECLARED — the buckets. Coverage is bucketed in PIXELS through `voxfill`'s exact squared
#: comparison; depth is bucketed in CELLS, because a depth slack is a distance in the world and the
#: cell is the world's own unit.
COVER_BUCKETS = ("on_surface", "within_one_pixel", "beyond")
DEPTH_BUCKETS = ("should_have_won", "exact_tie", "under_one_cell", "a_whole_cell_or_more")

#: The fates, inherited from the rung that owns them.
FATES = VS.FATES


class VoxslackError(Exception):
    """VOXSLACK-REFUSE — a predicate or a record this module will not pretend to read."""


def _level():
    return VT.level(VT.BEST)


# ---- the instrument ---------------------------------------------------------------------------------
def instrument(prims, eye, fwd):
    """The committed loop with the DEPTH BUFFER and the triangle geometry kept.

    A SIXTH TRANSCRIPTION, and bound: `the_instrument_matches_the_ladder` requires its winner and
    covered sets to equal `voxfate.instrument_level`'s on every declared frame. Nothing here is an
    arm — the render is the committed one at `voxtie.BEST` and no variable is moved.
    """
    _n, _sym, S = _level()
    m = VR.basis(fwd)
    cx, cy = VR.W // 2, VR.H // 2
    dep = [None] * (VR.W * VR.H)
    key = [-1] * (VR.W * VR.H)
    covered, geo, stage = {}, {}, {}
    for pk, _col, quad in prims:
        cam = [VR._project(v, eye, m) for v in quad]
        mincf = min(c[1] for c in cam)
        if any(c[1] < VR.NEAR for c in cam):
            stage[pk] = max(stage.get(pk, 0), VM.STAGES.index("near_clipped"))
            geo[pk] = (mincf, [])
            continue
        st = VM.STAGES.index("near_clipped")
        scr = [((cx * S * c[1] + c[0] * VR.FOCAL * S) // c[1],
                (cy * S * c[1] - c[2] * VR.FOCAL * S) // c[1], c[1]) for c in cam]
        tris = []
        for a, b, c2 in ((scr[0], scr[1], scr[2]), (scr[0], scr[2], scr[3])):
            area = (b[0] - a[0]) * (c2[1] - a[1]) - (b[1] - a[1]) * (c2[0] - a[0])
            if area == 0:
                st = max(st, VM.STAGES.index("degenerate"))
                tris.append((area, None))
                continue
            if area < 0:
                st = max(st, VM.STAGES.index("backface"))
                tris.append((area, None))
                continue
            xl = max(min(a[0], b[0], c2[0]) // S, 0)
            xh = min(max(a[0], b[0], c2[0]) // S, VR.W - 1)
            yl = max(min(a[1], b[1], c2[1]) // S, 0)
            yh = min(max(a[1], b[1], c2[1]) // S, VR.H - 1)
            if xl > xh or yl > yh:
                st = max(st, VM.STAGES.index("offscreen"))
                tris.append((area, None))
                continue
            st = VM.RASTERISED
            bb = (VR._top_left_bias(a[0], a[1], b[0], b[1]),
                  VR._top_left_bias(b[0], b[1], c2[0], c2[1]),
                  VR._top_left_bias(c2[0], c2[1], a[0], a[1]))
            tris.append((area, (a, b, c2, bb, (xl, xh, yl, yh))))
            for py in range(yl, yh + 1):
                for px in range(xl, xh + 1):
                    sx, sy = px * S, py * S
                    e0 = VR._edge(a[0], a[1], b[0], b[1], sx, sy)
                    e1 = VR._edge(b[0], b[1], c2[0], c2[1], sx, sy)
                    e2 = VR._edge(c2[0], c2[1], a[0], a[1], sx, sy)
                    if e0 + bb[0] < 0 or e1 + bb[1] < 0 or e2 + bb[2] < 0:
                        continue
                    d = (a[2] * e1 + b[2] * e2 + c2[2] * e0) // area
                    i = py * VR.W + px
                    covered.setdefault(pk, set()).add(i)
                    if dep[i] is None or (d, pk) < (dep[i], key[i] if key[i] >= 0 else (1 << 62)):
                        dep[i] = d
                        key[i] = pk
        geo[pk] = (mincf, tris)
        stage[pk] = max(stage.get(pk, 0), st)
    return key, dep, covered, geo, stage


def the_instrument_matches_the_ladder():
    """A SIXTH copy of the loop is a sixth chance to drift, so it is pinned to the fifth."""
    _n, sym, S = _level()
    prims = VX.primitives_with("reversed")
    for _nm, eye, fwd in VR.TRACE:
        key, _dep, covered, _geo, stage = instrument(prims, eye, fwd)
        k2, s2, c2 = VS.instrument_level(prims, eye, fwd, sym, S)
        if key != k2 or covered != c2 or stage != s2:
            return False
    return True


# ---- the slacks -------------------------------------------------------------------------------------
def _cover_bucket(slack, tri, px, py, S):
    """`on_surface` at exactly -1 (the top-left bias and nothing else), otherwise by DISTANCE."""
    if slack == -1:
        return "on_surface"
    a, b, c2, bb, _box = tri
    e = (VR._edge(a[0], a[1], b[0], b[1], px * S, py * S),
         VR._edge(b[0], b[1], c2[0], c2[1], px * S, py * S),
         VR._edge(c2[0], c2[1], a[0], a[1], px * S, py * S))
    pts = ((a, b), (b, c2), (c2, a))
    j = min(range(3), key=lambda k: e[k] + bb[k])
    return ("within_one_pixel"
            if VL._within_one_pixel(e[j], pts[j][0][0], pts[j][0][1], pts[j][1][0], pts[j][1][1], S)
            else "beyond")


def _depth_bucket(slack):
    if slack < 0:
        return "should_have_won"
    if slack == 0:
        return "exact_tie"
    return "under_one_cell" if slack < VR.Q else "a_whole_cell_or_more"


_CENSUS = {}


def census():
    """(frame, px, py, fate, near_plane, area, bbox, coverage, depth, cover bucket, depth bucket).

    Each slack is `None` where the pixel never reached that surface — a zero would be a decision
    the reference never made, and reporting one would be the instrument inventing evidence.
    """
    k = VR.world_digest()
    if k in _CENSUS:
        return _CENSUS[k]
    _n, _sym, S = _level()
    prims = VX.primitives_with("reversed")
    by_frame = {}
    for f, px, py, fate, _imp in VS.fates():
        by_frame.setdefault(f, []).append((px, py, fate))
    rows = []
    for f in sorted(by_frame):
        _nm, eye, fwd = VR.TRACE[f]
        key, dep, _cov, geo, _stage = instrument(prims, eye, fwd)
        ora = VM.oracle_frame(eye, fwd, VR.solid, VC.ORIGIN)
        for px, py, fate in by_frame[f]:
            i = py * VR.W + px
            o = ora[i]
            if o is None:
                rows.append((f, px, py, fate, None, None, None, None, None, "-", "-"))
                continue
            pk = (((o[0][0] * VR.N) + o[0][1]) * VR.N + o[0][2]) * 6 + o[1]
            mincf, tris = geo.get(pk, (0, []))
            near = mincf - VR.NEAR
            best = None
            for area, g in tris:
                if g is None:
                    if best is None:
                        best = (area, None, None, None, None)
                    continue
                a, b, c2, bb, (xl, xh, yl, yh) = g
                sx, sy = px * S, py * S
                e = (VR._edge(a[0], a[1], b[0], b[1], sx, sy),
                     VR._edge(b[0], b[1], c2[0], c2[1], sx, sy),
                     VR._edge(c2[0], c2[1], a[0], a[1], sx, sy))
                cov = min(e[j] + bb[j] for j in range(3))
                box = min(px - xl, xh - px, py - yl, yh - py)
                d = (a[2] * e[1] + b[2] * e[2] + c2[2] * e[0]) // area
                cand = (area, box, cov, d, g)
                if best is None or best[2] is None or cov > best[2]:
                    best = cand
            if best is None:
                rows.append((f, px, py, fate, near, None, None, None, None, "-", "-"))
                continue
            area, box, cov, d, g = best
            depth = None if (cov is None or cov < 0 or dep[i] is None) else d - dep[i]
            cb = "-" if cov is None or cov >= 0 else _cover_bucket(cov, g, px, py, S)
            db = "-" if depth is None else _depth_bucket(depth)
            rows.append((f, px, py, fate, near, area, box, cov, depth, cb, db))
    _CENSUS[k] = rows
    return rows


def distribution(field):
    """Bucket counts for `coverage` or `depth`, restricted to the pixels that reached that surface."""
    if field not in ("coverage", "depth"):
        raise VoxslackError("VOXSLACK-REFUSE: no bucketed field named %r" % (field,))
    idx, names = (9, COVER_BUCKETS) if field == "coverage" else (10, DEPTH_BUCKETS)
    out = dict.fromkeys(names, 0)
    for r in census():
        if r[idx] in out:
            out[r[idx]] += 1
    return out


def reached(predicate):
    """How many pixels reached each declared surface — the coverage of the instrument itself."""
    if predicate not in PREDICATES:
        raise VoxslackError("VOXSLACK-REFUSE: no predicate named %r" % (predicate,))
    i = 4 + PREDICATES.index(predicate)
    return sum(1 for r in census() if r[i] is not None)


# ---- the laws ---------------------------------------------------------------------------------------
def the_population_reproduces_voxfate():
    """THE BINDING. Same pixels, same fates, or the slacks below are about a different population."""
    live = dict.fromkeys(FATES, 0)
    for r in census():
        live[r[3]] += 1
    return len(census()) == len(VS.fates()) and live == VS.distribution(False)


def the_coverage_residue_is_entirely_within_one_pixel():
    """EVERY COVERAGE MISS IS AT THE SURFACE OR WITHIN A PIXEL OF IT. Not one is beyond.

    THE FIRST VERSION OF THIS LAW DEMANDED A `beyond` CLASS AND REDDENED, which is the law doing
    exactly its job. The probe behind it bucketed on the raw edge-function magnitude and reported 95
    pixels `beyond`; the edge function is an area, not a distance, and dividing by the edge length —
    `voxfill`'s exact squared comparison, no root taken — puts every one of them inside a pixel. The
    law refused to be satisfied by a structure that was not there, before the claim was written down.

    A zero is only evidence if the instrument could have produced a non-zero, so `beyond` is planted
    on a synthetic triangle rather than trusted: a sample two pixels clear of a one-pixel edge must
    bucket as `beyond`, or this law is asserting a limitation of its own bucketer.
    """
    _n, _sym, S = _level()
    far = (((0, 0, 0), (S, 0, 0), (0, S, 0), (0, 0, 0), (0, 0, 0, 0)))
    plant = _cover_bucket(-2, ((0, 0, 0), (S, 0, 0), (S, S, 0), (0, 0, 0), (0, 0, 0, 0)), 3, 3, S)
    d = distribution("coverage")
    tot = sum(d.values())
    return (bool(far) and plant == "beyond" and tot > 0 and d["beyond"] == 0
            and d["on_surface"] + d["within_one_pixel"] == tot)


def the_residue_splits_at_the_bias():
    """AND THE SPLIT IS BETWEEN TWO MECHANISMS, NOT TWO DISTANCES. 215 fail by EXACTLY -1 — the
    top-left bias, the sample precisely on the edge — and 103 fail by a real but sub-pixel amount,
    which is the floored projected vertex. Both classes must be substantial: a residue collapsed to
    either end would mean one mechanism, and this rung would be reporting an average of two.

    The two map onto `voxconv` exactly: under the aligned convention the 215 vanish and a sub-pixel
    remainder survives, so the same split shows up from a completely different direction.
    """
    d = distribution("coverage")
    tot = sum(d.values())
    return tot > 0 and d["on_surface"] * 4 > tot and d["within_one_pixel"] * 8 > tot


def the_on_surface_class_is_exactly_the_bias():
    """The on-surface class fails by EXACTLY -1, which is the top-left bias and nothing else: the
    sample sits precisely on the edge. That is the class `voxfill` and `voxconv` have exonerated
    twice, arriving here a third time as a signed distance rather than a category."""
    return all(r[7] == -1 for r in census() if r[9] == "on_surface") \
        and distribution("coverage")["on_surface"] > 0


def the_depth_rejections_are_not_a_margin():
    """THE FINDING THAT REDIRECTS A BRANCH OF THE DIAGNOSIS. If the depth-rejected pixels sat near
    zero slack, the depth comparison would be a rounding boundary worth attacking. They do not: most
    lose by a WHOLE CELL OR MORE. The oracle's face really is farther away and it loses honestly."""
    d = distribution("depth")
    tot = sum(d.values())
    return tot > 0 and d["a_whole_cell_or_more"] * 2 > tot


def no_stable_pixel_should_have_won_on_depth():
    """A ZERO, WITH THE NEGATIVE PROVED REACHABLE. Not one stable pixel has the oracle's face nearer
    than the winner — and a zero is only evidence if the instrument could have found a non-zero, so
    the bucket function is planted on a negative slack here rather than trusted."""
    return (_depth_bucket(-1) == "should_have_won"
            and _depth_bucket(0) == "exact_tie"
            and distribution("depth")["should_have_won"] == 0
            and sum(distribution("depth").values()) > 0)


def the_depth_rejections_are_deep_inside_coverage():
    """AND THEY ARE NOWHERE NEAR A COVERAGE BOUNDARY EITHER. Their coverage slack is hugely
    POSITIVE, so the pixel is well inside the oracle's own face. Both surfaces are clear, the depth
    comparison is correct, and what is left wrong is that a NEARER face covers the pixel at all —
    the same coverage defect seen from the winner's side rather than the loser's."""
    rows = [r for r in census() if r[3] == "depth_rejected"]
    return bool(rows) and all(r[7] is not None and r[7] >= 0 for r in rows) \
        and min(r[7] for r in rows) >= 0


def the_phantoms_are_too_few_to_read():
    """The same refusal `voxconv` states about its four impossible faces: two is not a distribution,
    and the law reddens if the population ever grows past the point where the refusal was honest."""
    n = sum(1 for r in census() if r[3] == "phantom")
    return 0 < n < 10 and all(r[4] is None for r in census() if r[3] == "phantom")


def nothing_is_altered():
    """DIAGNOSTIC ONLY, AND THE ROW SAYS SO. No arm, no candidate, no convention moved, no renderer
    changed — this rung measures where the CURRENT reference sits relative to its own decision
    surfaces, and a rung that had also proposed a repair would have collapsed the two into one."""
    return (VC.the_committed_reference_is_untouched()
            and VX.ray_for_pixel(VR.TRACE[0][1], VR.TRACE[0][2], 10, 0)
            == VX.ray_for_pixel(VR.TRACE[0][1], VR.TRACE[0][2], 10, 0))


# ---- the record ---------------------------------------------------------------------------------------
RECORD = os.path.join("spec", "attest", "voxref-slack.txt")


def population_digest():
    body = "\n".join("%d %d %d %s %s %s %s %s %s %s %s"
                     % tuple("-" if v is None else v for v in r) for r in census())
    return hashlib.sha256(MAGIC + b"|slack|" + body.encode()).hexdigest()


def generate():
    cov, dep = distribution("coverage"), distribution("depth")
    rows = ["# URDRVXK1 decision-surface slack census — emitted by voxslack.generate(), committed",
            "# as an artifact, re-derived by the gate.",
            "# world %s" % VR.world_digest(),
            "# DIAGNOSTIC ONLY: no arm, no candidate, no altered renderer, no moved convention.",
            "# SIGN: %s" % SIGN,
            "#   reached <predicate> <pixels that reached that surface>",
            "#   cover   <bucket> <count>",
            "#   depth   <bucket> <count>",
            "#   pixel   <frame> <px> <py> <fate> <near_plane> <area> <bbox> <coverage> <depth>"
            " <cover bucket> <depth bucket>",
            "#   digest  <population digest>"]
    for p in PREDICATES:
        rows.append("reached %s %d" % (p, reached(p)))
    for b in COVER_BUCKETS:
        rows.append("cover %s %d" % (b, cov[b]))
    for b in DEPTH_BUCKETS:
        rows.append("depth %s %d" % (b, dep[b]))
    for r in census():
        rows.append("pixel " + " ".join("-" if v is None else str(v) for v in r))
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
        if f[0] == "reached" and (len(f) != 3 or f[1] not in PREDICATES):
            raise VoxslackError("VOXSLACK-REFUSE: a reached row naming no declared predicate")
        if f[0] == "cover" and (len(f) != 3 or f[1] not in COVER_BUCKETS):
            raise VoxslackError("VOXSLACK-REFUSE: a cover row in no declared bucket")
        if f[0] == "depth" and (len(f) != 3 or f[1] not in DEPTH_BUCKETS):
            raise VoxslackError("VOXSLACK-REFUSE: a depth row in no declared bucket")
        if f[0] == "pixel" and (len(f) != 12 or f[4] not in FATES
                                or f[10] not in COVER_BUCKETS + ("-",)
                                or f[11] not in DEPTH_BUCKETS + ("-",)):
            raise VoxslackError("VOXSLACK-REFUSE: a pixel row in no declared fate or bucket")
        if f[0] not in ("reached", "cover", "depth", "pixel", "digest"):
            raise VoxslackError("VOXSLACK-REFUSE: a row of unknown kind %r" % (f[0],))
        rows.append(tuple(f))
    if world is None:
        raise VoxslackError("VOXSLACK-REFUSE: the record names no world digest")
    if not rows:
        raise VoxslackError("VOXSLACK-REFUSE: the record has no rows")
    return world, rows


def the_record_names_this_world():
    return parse()[0] == VR.world_digest()


def the_record_is_bound_to_the_live_code():
    _w, rows = parse()
    cov, dep = distribution("coverage"), distribution("depth")
    for r in rows:
        if r[0] == "cover" and int(r[2]) != cov[r[1]]:
            return False
        if r[0] == "depth" and int(r[2]) != dep[r[1]]:
            return False
        if r[0] == "reached" and int(r[2]) != reached(r[1]):
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
    except VoxslackError:
        return True
    return False


def told():
    cov, dep = distribution("coverage"), distribution("depth")
    deep = sorted(r[7] for r in census() if r[3] == "depth_rejected" and r[7] is not None)
    dd = sorted(r[8] for r in census() if r[3] == "depth_rejected" and r[8] is not None)
    return ("EVERY ONE of the %d coverage misses is within a pixel of the surface and %d are beyond "
            "it: %d fail by exactly -1, which is the top-left bias and nothing else, and %d fail by "
            "a real but sub-pixel amount, which is the floored projected vertex — a split between "
            "two MECHANISMS rather than two distances, mapping onto `voxconv` exactly. AND THE %d "
            "DEPTH REJECTIONS ARE NOT A MARGIN DEFECT AT ALL: %d of them lose by a WHOLE CELL OR "
            "MORE (median %.2f cells), only %d are exact ties, and NOT ONE should have won — while "
            "their COVERAGE slack is hugely positive (median %d), so they sit deep inside the "
            "oracle's own face. The depth comparison is doing its job; what is wrong is that a "
            "NEARER face covers the pixel at all, which is the same coverage defect from the "
            "winner's side. The fate split is really %d coverage and 2 anomaly, with the %d counted "
            "at the wrong end"
            % (cov["on_surface"] + cov["within_one_pixel"] + cov["beyond"], cov["beyond"],
               cov["on_surface"], cov["within_one_pixel"],
               sum(dep.values()), dep["a_whole_cell_or_more"],
               (dd[len(dd) // 2] / float(VR.Q)) if dd else 0.0, dep["exact_tie"],
               deep[len(deep) // 2] if deep else 0,
               cov["on_surface"] + cov["within_one_pixel"] + cov["beyond"] + sum(dep.values()),
               sum(dep.values())))


def scene_case(name):
    if name == "buckets":
        return repr((distribution("coverage"), distribution("depth"),
                     tuple((p, reached(p)) for p in PREDICATES)))
    if name == "slack":
        return repr(population_digest())
    raise VoxslackError("VOXSLACK-REFUSE: no scene named %r" % name)


def scene_result(name):
    return hashlib.sha256(MAGIC + b"|" + name.encode() + b"|"
                          + scene_case(name).encode()).hexdigest()


SCENES = ("buckets", "slack")


def golden(name):
    with open(os.path.join(_HERE, "conformance_voxslack.txt"), encoding="utf-8") as fh:
        for ln in fh:
            ln = ln.strip()
            if ln and not ln.startswith("#"):
                nm, dig = ln.split()
                if nm == name:
                    return dig
    raise VoxslackError("VOXSLACK-REFUSE: no golden named %r" % name)
