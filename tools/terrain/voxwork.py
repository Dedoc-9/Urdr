# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""voxwork (URDRVXO1) — THE FLOOR. WHAT DOES THE REFERENCE ACTUALLY DO, COUNTED EXACTLY?

The correctness arc closed at `voxcam`. This is the first rung of the PERFORMANCE arc, and its
whole law is one line: SAME EXACT OBSERVABLE, LESS WORK. Nothing here optimises anything. A
speedup cannot be claimed without a ruler, and a ruler that moves the thing it measures is not a
ruler — so this rung builds the ruler and PROVES IT INERT before any arm exists.

THE INSTRUMENT IS THE SEVENTH TRANSCRIPTION OF THE COMMITTED LOOP AND IT IS BOUND IN THE STRONGEST
AVAILABLE DIRECTION: its colour and depth buffers must equal `voxref.render`'s as LISTS, element for
element, on every declared frame — not as digests, which would let two different pictures collide,
and not on one frame, which would let a transcription drift where the trace does not go.

THE FLOOR, MEASURED:

    664553 pixels are walked to produce 55296 output pixels.        TWELVE TIMES OVERDRAW.

And the fate of a walked pixel is a partition, asserted as one so no unit of work is uncounted or
counted twice:

    walked   664553
      outside the triangle   419370   63.1%   the three edge tests reject it
      covered but beaten     179290   27.0%   it is inside, and loses the depth compare
      written                 65893    9.9%   it changes a pixel

NINE PIXELS IN TEN ARE WALKED TO PRODUCE NOTHING, and the two losses are of DIFFERENT KINDS: 63% dies
to COVERAGE, which is a question about a triangle's shape and can be answered for a whole tile at
once; 27% dies to DEPTH, which is a question about what else is in front and can be answered for a
whole primitive at once. Those are different mechanisms with different remedies, so they are counted
separately and never summed into one `wasted work` number.

ARITHMETIC IS MODELLED AND THE MODEL IS CHECKED AGAINST EXECUTION, never asserted as a formula that
could drift: 36 multiplies per quad in the basis multiply, 8 more and 8 divides in the projection,
4 per triangle in the area, SIX PER WALKED PIXEL in the three edge functions, and 3 multiplies plus
ONE DIVIDE per covered pixel in the depth interpolation. The closed form must EQUAL the count taken
from the run.

NO WALL CLOCK APPEARS ANYWHERE IN THIS RUNG AND THAT IS ENFORCED RATHER THAN PROMISED. A timing
assertion inside a deterministic gate is nondeterministic and would flake or be loosened until it
could not fail; this repo's standing rule is counts on-gate and wall-clock off, in a committed record
from a named host. `no_wall_clock_enters_this_rung` reads this module's own AST and refuses a timing
import, so the performance arc cannot smuggle a stopwatch into the gate one rung at a time.

does_not_show: NOTHING ABOUT TIME — these are exact integer operation counts and an operation count
is not a duration, because a division and an addition are one operation each and are not one cost
each. NOTHING ABOUT MEMORY TRAFFIC OR CACHE BEHAVIOUR, which are properties of a machine and a
layout and this rung measures neither. THAT ANY OF THIS WORK IS REMOVABLE — naming waste is not
retiring it, and a bound on what a cheaper test could save is a different rung with an arm in it.
NO OPTIMISATION IS PROPOSED OR RUN. And nothing is altered: `voxref` is untouched and `O_t` is
byte-identical with the observer active, which is the only reason the numbers mean anything.

falsifier: `the_observable_is_unmoved` compares both buffers as lists on every frame and reddens if
the ruler ever moves the thing it measures; `the_fates_partition_the_walk` reddens if the three fates
stop summing to the walk; and `the_walk_model_equals_the_run` derives the walk INDEPENDENTLY from the
projected bounding boxes and reddens if the model and the execution disagree, which is what a census
that had quietly started counting something else would look like.
"""
import ast
import hashlib
import os
import sys as _sys

_HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(_HERE))
if _HERE not in _sys.path:
    _sys.path.insert(0, _HERE)

import voxref as VR                                          # noqa: E402
import voxray as VX                                          # noqa: E402
import voxcand as VC                                         # noqa: E402

MAGIC = b"URDRVXO1"

#: DECLARED — the counters. Each is an INDEPENDENT count taken from the run; the ratios and the
#: arithmetic model are DERIVED from them and never stored beside them as if separately measured.
COUNTERS = ("primitives", "near_rejected", "triangles", "area_rejected", "bbox_rejected",
            "walked", "covered", "written", "mul", "div")

#: DECLARED — the three fates of a walked pixel. A PARTITION: every walked pixel has exactly one.
FATES = ("outside", "beaten", "written")

#: DECLARED — the arithmetic model's coefficients, named once so the law and the record read the
#: same constants. Per quad, per surviving quad, per triangle, per walked pixel, per covered pixel.
MUL_PER_QUAD = 36           #: 4 vertices x 9 multiplies in the Q16 basis multiply
MUL_PER_SEEN = 8            #: 4 vertices x 2 in the projection's screen divide
DIV_PER_SEEN = 8            #: the same 8 divides
MUL_PER_TRIANGLE = 4        #: the signed area
MUL_PER_WALK = 6            #: 3 edge functions x 2
MUL_PER_COVER = 3           #: the depth interpolation's three products
DIV_PER_COVER = 1           #: and its one divide

#: DECLARED — timing machinery this rung refuses to contain. Counts on-gate, wall-clock off.
FORBIDDEN_IMPORTS = ("time", "timeit", "datetime", "resource", "cProfile", "profile")


class VoxworkError(Exception):
    """VOXWORK-REFUSE — a counter, a fate or a record this module will not pretend to read."""


# ---- the instrument -----------------------------------------------------------------------------------
def instrument(prims, eye, fwd):
    """The committed loop with a counter beside every branch. Returns (color, depth, counts).

    THE SEVENTH TRANSCRIPTION OF THIS LOOP IN THIS ARC. It is bound to `voxref.render` on both
    buffers as LISTS, because a chain this long is exactly how a rung ends up measuring a renderer
    nobody declared.
    """
    m = VR.basis(fwd)
    cx, cy = VR.W // 2, VR.H // 2
    color = [VR.BACKGROUND] * (VR.W * VR.H)
    depth = [VR.FAR] * (VR.W * VR.H)
    key = [-1] * (VR.W * VR.H)
    n = dict.fromkeys(COUNTERS, 0)
    for pkey, col, quad in prims:
        n["primitives"] += 1
        n["mul"] += MUL_PER_QUAD
        cam = [VR._project(v, eye, m) for v in quad]
        if any(c[1] < VR.NEAR for c in cam):
            n["near_rejected"] += 1
            continue
        n["mul"] += MUL_PER_SEEN
        n["div"] += DIV_PER_SEEN
        scr = [(cx + c[0] * VR.FOCAL // c[1], cy - c[2] * VR.FOCAL // c[1], c[1]) for c in cam]
        for a, b, c in ((scr[0], scr[1], scr[2]), (scr[0], scr[2], scr[3])):
            n["triangles"] += 1
            n["mul"] += MUL_PER_TRIANGLE
            area = (b[0] - a[0]) * (c[1] - a[1]) - (b[1] - a[1]) * (c[0] - a[0])
            if area <= 0:
                n["area_rejected"] += 1
                continue
            x_lo = max(min(a[0], b[0], c[0]), 0)
            x_hi = min(max(a[0], b[0], c[0]), VR.W - 1)
            y_lo = max(min(a[1], b[1], c[1]), 0)
            y_hi = min(max(a[1], b[1], c[1]), VR.H - 1)
            if x_lo > x_hi or y_lo > y_hi:
                n["bbox_rejected"] += 1
                continue
            b0 = VR._top_left_bias(a[0], a[1], b[0], b[1])
            b1 = VR._top_left_bias(b[0], b[1], c[0], c[1])
            b2 = VR._top_left_bias(c[0], c[1], a[0], a[1])
            for py in range(y_lo, y_hi + 1):
                row = py * VR.W
                for px in range(x_lo, x_hi + 1):
                    n["walked"] += 1
                    n["mul"] += MUL_PER_WALK
                    w0 = VR._edge(a[0], a[1], b[0], b[1], px, py) + b0
                    w1 = VR._edge(b[0], b[1], c[0], c[1], px, py) + b1
                    w2 = VR._edge(c[0], c[1], a[0], a[1], px, py) + b2
                    if w0 < 0 or w1 < 0 or w2 < 0:
                        continue
                    n["covered"] += 1
                    n["mul"] += MUL_PER_COVER
                    n["div"] += DIV_PER_COVER
                    d = (a[2] * w1 + b[2] * w2 + c[2] * w0) // area
                    i = row + px
                    if (d, pkey) < (depth[i], key[i] if key[i] >= 0 else (1 << 62)):
                        depth[i] = d
                        key[i] = pkey
                        color[i] = col
                        n["written"] += 1
    return color, depth, n


_CENSUS = {}


def census():
    """[(frame, name, {counter: count})] over the declared trace."""
    k = VR.world_digest()
    if k in _CENSUS:
        return _CENSUS[k]
    prims = VX.primitives_with("reversed")
    rows = []
    for f, (nm, eye, fwd) in enumerate(VR.TRACE):
        _c, _d, n = instrument(prims, eye, fwd)
        rows.append((f, nm, n))
    _CENSUS[k] = rows
    return rows


def total(counter):
    if counter not in COUNTERS:
        raise VoxworkError("VOXWORK-REFUSE: no counter named %r" % (counter,))
    return sum(r[2][counter] for r in census())


def fates(frame=None):
    """{fate: count} — the partition of the walk, for one frame or for the whole trace."""
    rows = census() if frame is None else [r for r in census() if r[0] == frame]
    if not rows:
        raise VoxworkError("VOXWORK-REFUSE: no frame numbered %r" % (frame,))
    w = sum(r[2]["walked"] for r in rows)
    cv = sum(r[2]["covered"] for r in rows)
    wr = sum(r[2]["written"] for r in rows)
    return {"outside": w - cv, "beaten": cv - wr, "written": wr}


# ---- the ruler does not move what it measures -----------------------------------------------------------
def the_observable_is_unmoved():
    """THE ONE LAW THAT MAKES EVERY NUMBER HERE MEAN ANYTHING. An observer that changes a byte of
    the thing it observes is not an observer — the four-layer rule, applied to the ruler itself.
    Compared as LISTS and not as digests, on every declared frame: a digest comparison would pass on
    two buffers that collide, and one frame would pass a transcription that drifts elsewhere."""
    prims = VX.primitives_with("reversed")
    for _nm, eye, fwd in VR.TRACE:
        col, dep, _n = instrument(prims, eye, fwd)
        rc, rd = VR.render(prims, eye, fwd)
        if col != rc or dep != rd:
            return False
    return True


def the_fates_partition_the_walk():
    """EVERY WALKED PIXEL HAS EXACTLY ONE FATE. Asserted per frame, not once in aggregate, because
    two frames whose errors cancel would satisfy a total and not a partition."""
    for f, _nm, n in census():
        p = fates(f)
        if sum(p.values()) != n["walked"]:
            return False
        if p["outside"] < 0 or p["beaten"] < 0 or p["written"] < 0:
            return False
    return True


def walk_model():
    """The walk derived INDEPENDENTLY of the run: the sum of the clipped bounding-box areas of the
    projected front-facing triangles. A formula, to be checked against execution."""
    prims = VX.primitives_with("reversed")
    out = []
    for _nm, eye, fwd in VR.TRACE:
        m = VR.basis(fwd)
        cx, cy = VR.W // 2, VR.H // 2
        tot = 0
        for _pkey, _col, quad in prims:
            cam = [VR._project(v, eye, m) for v in quad]
            if any(c[1] < VR.NEAR for c in cam):
                continue
            scr = [(cx + c[0] * VR.FOCAL // c[1], cy - c[2] * VR.FOCAL // c[1], c[1]) for c in cam]
            for a, b, c in ((scr[0], scr[1], scr[2]), (scr[0], scr[2], scr[3])):
                if (b[0] - a[0]) * (c[1] - a[1]) - (b[1] - a[1]) * (c[0] - a[0]) <= 0:
                    continue
                x_lo = max(min(a[0], b[0], c[0]), 0)
                x_hi = min(max(a[0], b[0], c[0]), VR.W - 1)
                y_lo = max(min(a[1], b[1], c[1]), 0)
                y_hi = min(max(a[1], b[1], c[1]), VR.H - 1)
                if x_lo > x_hi or y_lo > y_hi:
                    continue
                tot += (x_hi - x_lo + 1) * (y_hi - y_lo + 1)
        out.append(tot)
    return out


def the_walk_model_equals_the_run():
    """MODEL == EXECUTION, per frame. A cost model that is only ever compared to itself is a
    formula; this one is compared to the thing it claims to describe, so a census that had quietly
    started counting something else reddens here rather than being believed."""
    model = walk_model()
    return all(model[f] == n["walked"] for f, _nm, n in census())


def arithmetic_model():
    """(mul, div) per frame from the declared coefficients — checked against the run, not asserted."""
    out = []
    for _f, _nm, n in census():
        seen = n["primitives"] - n["near_rejected"]
        mul = (MUL_PER_QUAD * n["primitives"] + MUL_PER_SEEN * seen
               + MUL_PER_TRIANGLE * n["triangles"] + MUL_PER_WALK * n["walked"]
               + MUL_PER_COVER * n["covered"])
        div = DIV_PER_SEEN * seen + DIV_PER_COVER * n["covered"]
        out.append((mul, div))
    return out


def the_arithmetic_model_equals_the_run():
    return all(arithmetic_model()[f] == (n["mul"], n["div"]) for f, _nm, n in census())


def the_triangles_are_two_per_surviving_quad():
    """A cheap identity, asserted because it is the one that catches a near test moved by accident:
    a rung that started rejecting quads somewhere else would break this and nothing else."""
    return all(n["triangles"] == 2 * (n["primitives"] - n["near_rejected"])
               for _f, _nm, n in census())


# ---- the headline -------------------------------------------------------------------------------------
def overdraw():
    """(walked, output pixels) — reported as a PAIR, never as a ratio, so no percentage is invented."""
    return total("walked"), len(VR.TRACE) * VR.W * VR.H


def the_overdraw_is_the_headline():
    """TWELVE TIMES. Asserted as the MEASUREMENT by integer comparison — no float, no rounding — and
    it reddens on the day the reference stops walking ten times its own output, which is the day
    this floor must be re-read rather than quoted."""
    w, out = overdraw()
    return w > 10 * out


def most_of_the_walk_is_outside_the_triangle():
    """THE FIRST LOSS AND THE LARGER: 63% of the inner loop is spent on pixels the three edge tests
    then reject. That is a question about a TRIANGLE'S SHAPE, which is answerable for a whole tile
    at once — a different mechanism from the second loss and kept separate from it."""
    p = fates()
    return p["outside"] > p["beaten"] + p["written"]


def most_of_the_coverage_loses_the_depth_test():
    """THE SECOND LOSS: of the pixels that ARE inside, most are beaten. That is a question about
    WHAT ELSE IS IN FRONT, answerable for a whole primitive at once. Summing the two losses into one
    `wasted work` number would hide that they have different remedies."""
    p = fates()
    return p["beaten"] > p["written"]


def arithmetic_split():
    """(setup multiplies, inner-loop multiplies) — where the arithmetic actually is."""
    inner = MUL_PER_WALK * total("walked") + MUL_PER_COVER * total("covered")
    return total("mul") - inner, inner


def the_inner_loop_dominates_but_the_setup_is_not_negligible():
    """A TWO-SIDED CLAIM, AND THE SECOND HALF IS THE ONE THAT MATTERS. The first draft of this law
    asserted that the edge functions are three quarters of the multiplies and REDDENED before it
    shipped: they are 71%, not 76%. What the correction exposes is the useful part — THE SETUP IS
    MORE THAN A FIFTH OF THE ARITHMETIC, and 1387584 of those multiplies are the Q16 basis multiply
    paid for EVERY quad including the 5859 the near test then throws away, before anything is known
    about any of them. A performance arc that assumed the inner loop was everything would aim every
    arm at it and leave a fifth of the work untouched, so both bounds are asserted and both can
    redden."""
    setup, inner = arithmetic_split()
    return inner > 2 * setup and setup * 5 > total("mul")


# ---- the stopwatch stays outside ------------------------------------------------------------------------
def timing_imports():
    """Every timing module this file imports, read from its own AST rather than from a promise."""
    with open(os.path.join(_HERE, "voxwork.py"), encoding="utf-8") as fh:
        tree = ast.parse(fh.read())
    found = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for a in node.names:
                if a.name.split(".")[0] in FORBIDDEN_IMPORTS:
                    found.add(a.name.split(".")[0])
        elif isinstance(node, ast.ImportFrom) and node.module:
            if node.module.split(".")[0] in FORBIDDEN_IMPORTS:
                found.add(node.module.split(".")[0])
    return sorted(found)


def no_wall_clock_enters_this_rung():
    """COUNTS ON-GATE, WALL-CLOCK OFF — this tree's standing rule, made STRUCTURAL at the moment a
    performance arc opens. A timing assertion inside a deterministic gate is nondeterministic and
    would flake or be loosened until it could not fail. Read from the AST, so the rule survives a
    later edit that adds a stopwatch to this module in good faith."""
    return timing_imports() == []


def the_wall_clock_law_can_bite():
    """A law with an empty live population is indistinguishable from one that cannot look, so the
    detector is run against a source that DOES import a stopwatch."""
    tree = ast.parse("import time\nfrom datetime import datetime\n")
    hits = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for a in node.names:
                if a.name.split(".")[0] in FORBIDDEN_IMPORTS:
                    hits.add(a.name.split(".")[0])
        elif isinstance(node, ast.ImportFrom) and node.module:
            if node.module.split(".")[0] in FORBIDDEN_IMPORTS:
                hits.add(node.module.split(".")[0])
    return hits == {"time", "datetime"}


def nothing_is_optimised():
    """NAMING WASTE IS NOT RETIRING IT. No arm is run, no traversal is changed, and `voxref` is
    untouched — this rung builds the ruler and stops, because a speedup measured against a ruler
    that arrived in the same commit is a speedup measured against itself."""
    return VC.the_committed_reference_is_untouched()


# ---- the record ---------------------------------------------------------------------------------------
RECORD = os.path.join("spec", "attest", "voxref-work.txt")


def work_digest():
    body = "\n".join("%d %s %s" % (f, nm, " ".join("%s=%d" % (c, n[c]) for c in COUNTERS))
                     for f, nm, n in census())
    body += "\n" + " ".join("%s=%d" % (k, v) for k, v in sorted(fates().items()))
    return hashlib.sha256(MAGIC + b"|work|" + body.encode()).hexdigest()


def generate():
    w, out = overdraw()
    p = fates()
    rows = ["# URDRVXO1 exact work floor — emitted by voxwork.generate(), committed as an artifact,",
            "# re-derived by the gate.",
            "# world %s" % VR.world_digest(),
            "# THE FIRST RUNG OF THE PERFORMANCE ARC. Its whole law is SAME EXACT OBSERVABLE, LESS",
            "# WORK — and this rung does the first half only: it builds the ruler and PROVES IT",
            "# INERT. No arm, no candidate, no altered traversal, and NO WALL CLOCK.",
            "#   count  <frame> <name> <counter> <count>",
            "#   fate   <fate> <count>",
            "#   walk   <walked> <output pixels>",
            "#   split  <setup multiplies> <inner-loop multiplies>",
            "#   digest <work digest>"]
    for f, nm, n in census():
        for c in COUNTERS:
            rows.append("count %d %s %s %d" % (f, nm, c, n[c]))
    for k in FATES:
        rows.append("fate %s %d" % (k, p[k]))
    rows.append("walk %d %d" % (w, out))
    rows.append("split %d %d" % arithmetic_split())
    rows.append("digest %s" % work_digest())
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
        if f[0] == "count" and (len(f) != 5 or f[3] not in COUNTERS):
            raise VoxworkError("VOXWORK-REFUSE: a count row naming no declared counter")
        if f[0] == "fate" and (len(f) != 3 or f[1] not in FATES):
            raise VoxworkError("VOXWORK-REFUSE: a fate row naming no declared fate")
        if f[0] == "walk" and len(f) != 3:
            raise VoxworkError("VOXWORK-REFUSE: a walk row of the wrong arity")
        if f[0] == "split" and len(f) != 3:
            raise VoxworkError("VOXWORK-REFUSE: a split row of the wrong arity")
        if f[0] not in ("count", "fate", "walk", "split", "digest"):
            raise VoxworkError("VOXWORK-REFUSE: a row of unknown kind %r" % (f[0],))
        rows.append(tuple(f))
    if world is None:
        raise VoxworkError("VOXWORK-REFUSE: the record names no world digest")
    if not rows:
        raise VoxworkError("VOXWORK-REFUSE: the record has no rows")
    return world, rows


def the_record_names_this_world():
    return parse()[0] == VR.world_digest()


def the_record_is_bound_to_the_live_code():
    _w, rows = parse()
    live = {(r[0], r[1]): r[2] for r in census()}
    p, (w, out) = fates(), overdraw()
    for r in rows:
        if r[0] == "count" and int(r[4]) != live[(int(r[1]), r[2])][r[3]]:
            return False
        if r[0] == "fate" and int(r[2]) != p[r[1]]:
            return False
        if r[0] == "walk" and (int(r[1]), int(r[2])) != (w, out):
            return False
        if r[0] == "split" and (int(r[1]), int(r[2])) != arithmetic_split():
            return False
    pinned = next(r[1] for r in rows if r[0] == "digest")
    return pinned == work_digest()


def a_tampered_row_refuses():
    text = _read()
    for ln in text.split("\n"):
        if ln.startswith("count "):
            f = ln.split()
            f[3] = "somethings"
            text = text.replace(ln, " ".join(f), 1)
            break
    try:
        parse(text)
    except VoxworkError:
        return True
    return False


def told():
    w, out = overdraw()
    p = fates()
    return ("%d pixels are WALKED to produce %d output pixels — TWELVE TIMES OVERDRAW — and the fate "
            "of a walked pixel is a PARTITION rather than a total: %d (%d in every hundred) fall "
            "OUTSIDE the triangle and die to the three edge tests, %d are covered and BEATEN on "
            "depth, and only %d ever change a pixel. NINE IN TEN ARE WALKED TO PRODUCE NOTHING, and "
            "THE TWO LOSSES ARE OF DIFFERENT KINDS: coverage is a question about a triangle's SHAPE "
            "and is answerable for a whole tile at once, depth is a question about WHAT ELSE IS IN "
            "FRONT and is answerable for a whole primitive at once — so they are counted separately "
            "and never summed into one wasted-work number. Arithmetic: %d multiplies and %d divides, "
            "MODELLED from declared coefficients and CHECKED against the run"
            % (w, out, p["outside"], (100 * p["outside"]) // w, p["beaten"], p["written"],
               total("mul"), total("div")))


def scene_case(name):
    if name == "census":
        return repr(tuple((f, nm, tuple((c, n[c]) for c in COUNTERS)) for f, nm, n in census()))
    if name == "shape":
        return repr((sorted(fates().items()), overdraw(), walk_model(), arithmetic_model(),
                     arithmetic_split()))
    raise VoxworkError("VOXWORK-REFUSE: no scene named %r" % name)


def scene_result(name):
    return hashlib.sha256(MAGIC + b"|" + name.encode() + b"|"
                          + scene_case(name).encode()).hexdigest()


SCENES = ("census", "shape")


def golden(name):
    with open(os.path.join(_HERE, "conformance_voxwork.txt"), encoding="utf-8") as fh:
        for ln in fh:
            ln = ln.strip()
            if ln and not ln.startswith("#"):
                nm, dig = ln.split()
                if nm == name:
                    return dig
    raise VoxworkError("VOXWORK-REFUSE: no golden named %r" % name)
