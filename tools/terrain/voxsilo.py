# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""voxsilo (URDRVXH1) — THREE SILOS, EIGHT CELLS, AND THE FULL COMBINATION IS NOT THE BEST ONE.

`voxwork` built the ruler and proved it inert. This rung spends it. Three optimisation silos, each
answering ONE question and forbidden to answer any other, measured ALONE, PAIRWISE and TOGETHER — the
whole 2^3 lattice — under a single contract that no silo may negotiate:

    THE OBSERVABLE IS BYTE-IDENTICAL. Colour and depth, as LISTS, on every declared frame, in every
    one of the eight cells. A silo may change its implementation and may not change what is seen.

    G  primitive retirement   a whole triangle skipped when it provably cannot win anywhere
    T  tile retirement        a whole 8x8 tile skipped by testing three edges at two corners
    A  arithmetic reduction   the edge functions stepped incrementally, no multiply per pixel

THE CONTRACT CAUGHT AN UNSOUND OPTIMISATION ON ITS FIRST RUN, AND THAT IS THE FIRST RESULT.

Every hierarchical-Z scheme rests on one premise: interpolated depth is a CONVEX COMBINATION of the
vertex depths, so a triangle's nearest point is the nearest of its vertices, so a triangle whose
nearest vertex is behind everything already in its box cannot win anywhere and may be dropped
untested. THAT PREMISE IS FALSE FOR THIS RASTERISER, and not marginally:

    covered pixels                          245183
    pixels where d < min vertex depth       215300      87.8%
    worst shortfall                           5129      zmin 7783 -> d 2654

THE MECHANISM IS THE TOP-LEFT FILL RULE. The biased weights sum to `area + B` with B in -3..0, not
to `area` — and the depth divides by `area`. So the interpolation is scaled by (area+B)/area. On a
large triangle that is a rounding-level effect. On the witness, an area-3 sliver with B = -2, it is a
factor of one third. The naive cull is kept as a LIVE PLANT that must MOVE the observable, because a
refutation that stops being runnable stops being evidence. The corrected bound
`zmin + (zmin*B)//area` is checked against EVERY covered pixel of every walked triangle on every
frame and is never violated.

AND THE LATTICE SAYS THE OBVIOUS OPTIMISATION IS THE ONE THAT DOES NOT PAY.

Reported as a PANEL and never fused into one number, because a divide is not a multiply is not a
compare and summing them would invent a cost model nobody declared:

    cell        walked    multiplies
    -           664553       6633411
    T           569963       6493935
    G           267485       3810738
    GT          225384       3728136
    A           664553       3139347
    TA          569963       3810225
    GA          267485       2396172
    GTA         225384       2665590

GA IS THE BEST CELL ON MULTIPLIES AND GTA IS WORSE. Adding the tile arm to GA retires 42101 walked
pixels and spends 269418 extra multiplies to do it — SIX AND A HALF MULTIPLIES PER PIXEL RETIRED, at
a moment when arm A has already made a walked pixel cost ZERO multiplies. T is destructive wherever
A is present: A alone spends 3139347 multiplies and TA spends 3810225.

THE REASON IS A NUMBER `voxwork` ALREADY HELD: the mean bounding box of a walked triangle is 56
pixels and a tile is 64. THE AVERAGE TRIANGLE IS SMALLER THAN ONE TILE, so the per-tile setup is
amortised over almost nothing, and hierarchical rejection is the wrong instrument at this geometry.

Orthogonality on multiplies saved, as exact fractions and never as decimals:

    W(G,T) = 56874/139476       0.41   real overlap: both retire work
    W(G,A) = 2079498/2822673    0.82   highly redundant, and it was expected to be orthogonal
    W(T,A) = 810354/139476      5.81   GREATER THAN ONE — not redundancy, SUBTRACTION

THIS RUNG MAKES NO PREDICTION CLAIM, and says so as a law rather than in prose. `voxproj` and
`voxcam` pinned their predictions as data BEFORE their arms ran and were entitled to score them. The
arms here ran first, so pinning a prediction now would be back-dating one, which is the L64 class
exactly. `the_rung_makes_no_prediction_claim` asserts this module declares no PREDICTION, so a later
edit cannot quietly add one and inherit a discipline this rung did not pay for.

does_not_show: NOTHING ABOUT TIME, and no wall clock enters this rung — counts on-gate, wall-clock
off in a named-host record, the rule `voxwork` made structural. NOTHING ABOUT MEMORY TRAFFIC, CACHE
BEHAVIOUR OR SIMD, which is where a multiply-count stops predicting a duration and this rung has no
instrument for any of them. THAT GA IS THE FASTEST ARRANGEMENT — it is the cheapest in multiplies on
THIS trace at THIS resolution with THIS geometry, and the tile arm's verdict is explicitly a verdict
about 56-pixel triangles rather than about hierarchical culling. NO PROMOTION: `voxref` is untouched
and not one of the eight cells is adopted.

falsifier: `every_cell_reproduces_the_observable` compares both buffers as lists across all eight
cells and all eight frames and reddens if any silo ever changes what is seen; `the_naive_bound_is_
unsound` REQUIRES the refuted cull to still move the observable, so the refutation cannot rot into a
comment; and `the_best_cell_is_not_the_full_combination` reddens on the day stacking everything
starts winning, which is the day this lattice must be re-read rather than quoted.
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
import voxcand as VC                                         # noqa: E402
import voxwork as VO                                         # noqa: E402

MAGIC = b"URDRVXH1"

#: DECLARED — the three silos. Each answers ONE question and is forbidden to answer any other.
ARMS = ("G", "T", "A")

#: DECLARED — what each silo is allowed to attack, so a silo that started attacking something else
#: would be a different arm wearing this one's name.
QUESTION = {
    "G": "can a whole primitive be retired without examining any of its pixels?",
    "T": "can a whole tile be retired without examining any of its pixels?",
    "A": "can the same per-pixel answer be computed with fewer multiplies?",
}

#: DECLARED — the eight cells of the lattice, in a fixed order so the record is stable.
CELLS = ((), ("T",), ("G",), ("G", "T"), ("A",), ("T", "A"), ("G", "A"), ("G", "T", "A"))

#: DECLARED — the tile edge. 8x8, against a mean walked bounding box of 56 pixels.
TILE = 8

#: DECLARED — the arms' own costs, named once so no arm's overhead is left out of its own column.
MUL_PER_TILE = 12           #: 3 edges x 2 corners x 2 multiplies
MUL_PER_ROW = 6             #: arm A's per-row setup: 3 edge functions evaluated once, 2 each

#: DECLARED — the counters this rung reports. A PANEL. They are never summed into one number,
#: because a divide is not a multiply is not a compare and a sum would invent a cost model.
COLUMNS = ("walked", "covered", "written", "mul", "div", "tiles", "zscan", "cmp")


class VoxsiloError(Exception):
    """VOXSILO-REFUSE — an arm, a cell or a record this module will not pretend to read."""


def cell_name(cell):
    return "".join(cell) if cell else "-"


def _check(cell):
    if tuple(cell) not in CELLS:
        raise VoxsiloError("VOXSILO-REFUSE: no cell named %r" % (cell_name(tuple(cell)),))
    return tuple(cell)


# ---- the bound -----------------------------------------------------------------------------------------
def naive_bound(a, b, c, _area, _bias):
    """THE PREMISE EVERY HIERARCHICAL-Z SCHEME RESTS ON, AND IT IS FALSE HERE. Kept runnable as a
    plant rather than described in a comment, because a refutation that cannot be executed stops
    being evidence the day someone edits around it."""
    return min(a[2], b[2], c[2])


def corrected_bound(a, b, c, area, bias):
    """THE REPAIR, AND IT IS ONE LINE OF ALGEBRA RATHER THAN A FUDGE FACTOR.

    The interior test is `e + bias >= 0`, so the biased weights sum to `area + B` where B is the sum
    of the three biases and lies in -3..0 — but the depth divides by `area`. The interpolation is
    therefore scaled by (area+B)/area and is NOT a convex combination, so it can fall BELOW every
    vertex depth. With every weight non-negative the sum is at least `zmin * (area + B)`, which gives
    this bound, and it is checked exhaustively against every covered pixel rather than trusted.
    """
    zmin = min(a[2], b[2], c[2])
    return zmin + (zmin * bias) // area


BOUNDS = {"naive": naive_bound, "corrected": corrected_bound}


# ---- the instrument ------------------------------------------------------------------------------------
def render_cell(prims, eye, fwd, cell, bound="corrected"):
    """The committed loop with the three silos as independent switches. Returns (color, depth, n)."""
    cell = _check(cell)
    if bound not in BOUNDS:
        raise VoxsiloError("VOXSILO-REFUSE: no bound named %r" % (bound,))
    g, t, a = "G" in cell, "T" in cell, "A" in cell
    m = VR.basis(fwd)
    cx, cy = VR.W // 2, VR.H // 2
    color = [VR.BACKGROUND] * (VR.W * VR.H)
    depth = [VR.FAR] * (VR.W * VR.H)
    key = [-1] * (VR.W * VR.H)
    n = dict.fromkeys(COLUMNS, 0)
    tw, th = (VR.W + TILE - 1) // TILE, (VR.H + TILE - 1) // TILE
    tz, dirty = [VR.FAR] * (tw * th), [False] * (tw * th)

    def zmax(tx, ty):
        i = ty * tw + tx
        if dirty[i]:
            mx = -1
            for y in range(ty * TILE, min(ty * TILE + TILE, VR.H)):
                row = y * VR.W
                for x in range(tx * TILE, min(tx * TILE + TILE, VR.W)):
                    n["zscan"] += 1
                    if depth[row + x] > mx:
                        mx = depth[row + x]
            tz[i], dirty[i] = mx, False
        return tz[i]

    tris = []
    for pkey, _col, quad in prims:
        n["mul"] += VO.MUL_PER_QUAD
        cam = [VR._project(v, eye, m) for v in quad]
        if any(cc[1] < VR.NEAR for cc in cam):
            continue
        n["mul"] += VO.MUL_PER_SEEN
        n["div"] += VO.DIV_PER_SEEN
        scr = [(cx + cc[0] * VR.FOCAL // cc[1], cy - cc[2] * VR.FOCAL // cc[1], cc[1]) for cc in cam]
        col = _col
        for p, q, r in ((scr[0], scr[1], scr[2]), (scr[0], scr[2], scr[3])):
            n["mul"] += VO.MUL_PER_TRIANGLE
            area = (q[0] - p[0]) * (r[1] - p[1]) - (q[1] - p[1]) * (r[0] - p[0])
            if area <= 0:
                continue
            x_lo = max(min(p[0], q[0], r[0]), 0)
            x_hi = min(max(p[0], q[0], r[0]), VR.W - 1)
            y_lo = max(min(p[1], q[1], r[1]), 0)
            y_hi = min(max(p[1], q[1], r[1]), VR.H - 1)
            if x_lo > x_hi or y_lo > y_hi:
                continue
            b0 = VR._top_left_bias(p[0], p[1], q[0], q[1])
            b1 = VR._top_left_bias(q[0], q[1], r[0], r[1])
            b2 = VR._top_left_bias(r[0], r[1], p[0], p[1])
            z = BOUNDS[bound](p, q, r, area, b0 + b1 + b2)
            tris.append((z, pkey, col, p, q, r, area, x_lo, x_hi, y_lo, y_hi, b0, b1, b2))

    if g:
        tris.sort(key=lambda x: (x[0], x[1]))
        k = len(tris)
        n["cmp"] += 0 if k < 2 else k * k.bit_length()

    for z, pkey, col, p, q, r, area, x_lo, x_hi, y_lo, y_hi, b0, b1, b2 in tris:
        if g:
            back = -1
            for ty in range(y_lo // TILE, y_hi // TILE + 1):
                for tx in range(x_lo // TILE, x_hi // TILE + 1):
                    v = zmax(tx, ty)
                    if v > back:
                        back = v
            if z > back:
                continue
        E = ((p[0], p[1], q[0], q[1], b0), (q[0], q[1], r[0], r[1], b1),
             (r[0], r[1], p[0], p[1], b2))
        STEP = tuple((ay - by, bx - ax) for ax, ay, bx, by, _b in E)

        def ev(i, px, py):
            ax, ay, bx, by, bi = E[i]
            return (bx - ax) * (py - ay) - (by - ay) * (px - ax) + bi

        if t:
            blocks = []
            for ty in range(y_lo // TILE, y_hi // TILE + 1):
                for tx in range(x_lo // TILE, x_hi // TILE + 1):
                    u0, u1 = max(tx * TILE, x_lo), min(tx * TILE + TILE - 1, x_hi)
                    v0, v1 = max(ty * TILE, y_lo), min(ty * TILE + TILE - 1, y_hi)
                    if u0 > u1 or v0 > v1:
                        continue
                    n["tiles"] += 1
                    n["mul"] += MUL_PER_TILE
                    out, allin = False, True
                    for i in range(3):
                        dx, dy = STEP[i]
                        if ev(i, u1 if dx > 0 else u0, v1 if dy > 0 else v0) < 0:
                            out = True
                            break
                        if ev(i, u0 if dx > 0 else u1, v0 if dy > 0 else v1) < 0:
                            allin = False
                    if not out:
                        blocks.append((u0, u1, v0, v1, allin))
        else:
            blocks = [(x_lo, x_hi, y_lo, y_hi, False)]

        for u0, u1, v0, v1, allin in blocks:
            for py in range(v0, v1 + 1):
                row = py * VR.W
                if a:
                    w = [ev(i, u0, py) for i in range(3)]
                    n["mul"] += MUL_PER_ROW
                for px in range(u0, u1 + 1):
                    n["walked"] += 1
                    if a:
                        w0, w1, w2 = w
                        w = [w[0] + STEP[0][0], w[1] + STEP[1][0], w[2] + STEP[2][0]]
                    else:
                        n["mul"] += VO.MUL_PER_WALK
                        w0, w1, w2 = ev(0, px, py), ev(1, px, py), ev(2, px, py)
                    if not allin and (w0 < 0 or w1 < 0 or w2 < 0):
                        continue
                    n["covered"] += 1
                    n["mul"] += VO.MUL_PER_COVER
                    n["div"] += VO.DIV_PER_COVER
                    d = (p[2] * w1 + q[2] * w2 + r[2] * w0) // area
                    i = row + px
                    if (d, pkey) < (depth[i], key[i] if key[i] >= 0 else (1 << 62)):
                        depth[i], key[i], color[i] = d, pkey, col
                        n["written"] += 1
                        if g:
                            dirty[(py // TILE) * tw + (px // TILE)] = True
    return color, depth, n


_PANEL = {}


def panel(cell):
    """{column: total over the declared trace} for one cell of the lattice."""
    cell = _check(cell)
    k = (VR.world_digest(), cell)
    if k in _PANEL:
        return _PANEL[k]
    prims = VX.primitives_with("reversed")
    tot = dict.fromkeys(COLUMNS, 0)
    for _nm, eye, fwd in VR.TRACE:
        _c, _d, n = render_cell(prims, eye, fwd, cell)
        for col in COLUMNS:
            tot[col] += n[col]
    _PANEL[k] = tot
    return tot


def column(name):
    if name not in COLUMNS:
        raise VoxsiloError("VOXSILO-REFUSE: no column named %r" % (name,))
    return {cell_name(c): panel(c)[name] for c in CELLS}


# ---- the contract --------------------------------------------------------------------------------------
def every_cell_reproduces_the_observable():
    """THE SILO BOUNDARY, MADE MECHANICAL. A silo may optimise its implementation and may NOT
    redefine the observable — so every cell's colour and depth buffers must equal `voxref.render`'s
    AS LISTS on every declared frame. This is the law the whole arc rests on, and it is what caught
    the naive cull before any number derived from it was believed."""
    prims = VX.primitives_with("reversed")
    for _nm, eye, fwd in VR.TRACE:
        rc, rd = VR.render(prims, eye, fwd)
        for cell in CELLS:
            col, dep, _n = render_cell(prims, eye, fwd, cell)
            if col != rc or dep != rd:
                return False
    return True


def the_naive_bound_is_unsound():
    """THE REFUTATION, KEPT RUNNABLE. The premise every hierarchical-Z scheme rests on is false for
    this rasteriser, and this law REQUIRES the refuted cull to still move the observable — so the
    finding cannot rot into a comment while the code around it changes."""
    prims = VX.primitives_with("reversed")
    for _nm, eye, fwd in VR.TRACE:
        rc, rd = VR.render(prims, eye, fwd)
        col, dep, _n = render_cell(prims, eye, fwd, ("G",), bound="naive")
        if col != rc or dep != rd:
            return True
    return False


def premise_census():
    """(covered, below the minimum vertex depth, worst shortfall) — the exact scale of the failure,
    and the exhaustive check that the corrected bound is never violated."""
    prims = VX.primitives_with("reversed")
    cov = bad = worst = 0
    for _nm, eye, fwd in VR.TRACE:
        m = VR.basis(fwd)
        cx, cy = VR.W // 2, VR.H // 2
        for _pkey, _col, quad in prims:
            cam = [VR._project(v, eye, m) for v in quad]
            if any(c[1] < VR.NEAR for c in cam):
                continue
            scr = [(cx + c[0] * VR.FOCAL // c[1], cy - c[2] * VR.FOCAL // c[1], c[1]) for c in cam]
            for p, q, r in ((scr[0], scr[1], scr[2]), (scr[0], scr[2], scr[3])):
                area = (q[0] - p[0]) * (r[1] - p[1]) - (q[1] - p[1]) * (r[0] - p[0])
                if area <= 0:
                    continue
                x_lo = max(min(p[0], q[0], r[0]), 0)
                x_hi = min(max(p[0], q[0], r[0]), VR.W - 1)
                y_lo = max(min(p[1], q[1], r[1]), 0)
                y_hi = min(max(p[1], q[1], r[1]), VR.H - 1)
                if x_lo > x_hi or y_lo > y_hi:
                    continue
                b0 = VR._top_left_bias(p[0], p[1], q[0], q[1])
                b1 = VR._top_left_bias(q[0], q[1], r[0], r[1])
                b2 = VR._top_left_bias(r[0], r[1], p[0], p[1])
                zmin = naive_bound(p, q, r, area, b0 + b1 + b2)
                lo = corrected_bound(p, q, r, area, b0 + b1 + b2)
                for py in range(y_lo, y_hi + 1):
                    for px in range(x_lo, x_hi + 1):
                        w0 = VR._edge(p[0], p[1], q[0], q[1], px, py) + b0
                        w1 = VR._edge(q[0], q[1], r[0], r[1], px, py) + b1
                        w2 = VR._edge(r[0], r[1], p[0], p[1], px, py) + b2
                        if w0 < 0 or w1 < 0 or w2 < 0:
                            continue
                        cov += 1
                        d = (p[2] * w1 + q[2] * w2 + r[2] * w0) // area
                        if d < lo:
                            return (cov, -1, -1)
                        if d < zmin:
                            bad += 1
                            if zmin - d > worst:
                                worst = zmin - d
    return (cov, bad, worst)


def the_corrected_bound_is_never_violated():
    """EXHAUSTIVE, over every covered pixel of every walked triangle on every declared frame. A
    conservative bound checked on a sample is a conjecture."""
    return premise_census()[1] >= 0


def the_premise_fails_on_most_pixels():
    """NOT A CORNER CASE. Asserted by integer comparison as the MEASUREMENT it is: the majority of
    covered pixels interpolate to a depth below every vertex of their own triangle."""
    cov, bad, worst = premise_census()
    return bad * 2 > cov and worst > 0


# ---- the lattice ---------------------------------------------------------------------------------------
def the_lattice_is_complete():
    """All eight cells, and the empty cell bound to `voxwork`'s floor — so the lattice is measured
    against the committed ruler rather than against a baseline this rung invented for itself."""
    if len(CELLS) != 2 ** len(ARMS) or len(set(CELLS)) != len(CELLS):
        return False
    base = panel(())
    return (base["walked"] == VO.total("walked") and base["covered"] == VO.total("covered")
            and base["mul"] == VO.total("mul") and base["div"] == VO.total("div")
            and base["written"] == VO.total("written"))


def best_cell(name="mul"):
    col = column(name)
    return min(sorted(col), key=lambda c: col[c])


def the_best_cell_is_not_the_full_combination():
    """THE HEADLINE, AND IT REDDENS ON THE DAY STACKING EVERYTHING STARTS WINNING — which is the day
    this lattice must be re-read rather than quoted. `GA` is cheapest in multiplies and `GTA` is
    dearer, so a rung reporting `all three, twice as fast` would have been reporting a combination
    beaten by two of its own parts."""
    return best_cell("mul") != cell_name(CELLS[-1])


def the_tile_arm_is_destructive_with_the_arithmetic_arm():
    """MEASURED IN BOTH PLACES IT OCCURS, because one instance is an anecdote. Arm T raises the
    multiply count both when added to A alone and when added to GA."""
    col = column("mul")
    return col["TA"] > col["A"] and col["GTA"] > col["GA"]


def the_tile_arm_still_retires_pixels():
    """AND THE VERDICT IS NOT THAT THE TILE TEST DOES NOT WORK. It retires exactly what it claims
    to; it is the EXCHANGE RATE that fails. Stating this keeps the finding about 56-pixel triangles
    rather than about hierarchical culling in general."""
    w = column("walked")
    return w["GTA"] < w["GA"] and w["TA"] < w["A"]


def exchange_rate():
    """(multiplies spent, walked pixels retired) by arm T on top of GA — reported as a PAIR so no
    rate is invented, against arm A's cost of ZERO multiplies per walked pixel."""
    m, w = column("mul"), column("walked")
    return m["GTA"] - m["GA"], w["GA"] - w["GTA"]


def mean_walked_box():
    """(walked pixels, triangles walked) — `voxwork`'s number, and the reason arm T cannot pay: the
    mean bounding box is smaller than one tile."""
    walked = VO.total("walked")
    tris = VO.total("triangles") - VO.total("area_rejected") - VO.total("bbox_rejected")
    return walked, tris


def the_average_triangle_is_smaller_than_a_tile():
    """THE MECHANISM, TAKEN FROM THE RULER RATHER THAN FROM THIS RUNG'S OWN ARITHMETIC. A per-tile
    setup amortised over less than one tile of pixels cannot pay, and that is a fact about the
    geometry rather than about the test."""
    walked, tris = mean_walked_box()
    return walked < tris * TILE * TILE


def orthogonality(x, y, name="mul"):
    """(numerator, denominator) of (S_x + S_y - S_xy) / min(S_x, S_y) on work SAVED, as an EXACT
    fraction. Never a decimal: the quantity decides whether two silos are redundant or destructive
    and a rounded one would be reporting its own rounding. Above 1 is not overlap — it is
    SUBTRACTION, two arms that together save less than the better of them alone."""
    if x not in ARMS or y not in ARMS or x == y:
        raise VoxsiloError("VOXSILO-REFUSE: no arm pair %r,%r" % (x, y))
    col = column(name)
    base = col["-"]
    sx, sy = base - col[x], base - col[y]
    pair = "".join(a for a in ARMS if a in (x, y))
    sxy = base - col[pair]
    den = min(sx, sy)
    if den <= 0:
        raise VoxsiloError("VOXSILO-REFUSE: an arm that saves nothing has no orthogonality")
    return (sx + sy - sxy, den)


def the_tile_and_arithmetic_arms_subtract():
    """Omega above 1: together they save LESS than arm A alone. The strongest statement in the
    lattice, and it is asserted by integer cross-multiplication so no decimal is constructed."""
    num, den = orthogonality("T", "A")
    return num > den


def the_arms_are_not_all_orthogonal():
    """Every pair overlaps. A lattice whose arms were independent would not need measuring, and a
    rung reporting the sum of three separately-measured savings would be reporting a number that
    does not exist."""
    return all(orthogonality(x, y)[0] > 0 for x, y in (("G", "T"), ("G", "A"), ("T", "A")))


# ---- what this rung does not claim ------------------------------------------------------------------------
def the_rung_makes_no_prediction_claim():
    """`voxproj` and `voxcam` pinned their predictions as DATA before their arms ran and were
    entitled to score them. THE ARMS HERE RAN FIRST, so pinning a prediction now would be
    back-dating one. This module declares no PREDICTION and this law holds it to that, so a later
    edit cannot quietly add one and inherit a discipline this rung did not pay for."""
    return not hasattr(_sys.modules[__name__], "PREDICTION")


def no_wall_clock_enters_this_rung():
    """`voxwork` made the rule structural; this rung is the first to inherit it. A performance arc
    is exactly where a stopwatch gets smuggled into a deterministic gate one rung at a time."""
    with open(os.path.join(_HERE, "voxsilo.py"), encoding="utf-8") as fh:
        src = fh.read()
    import ast
    for node in ast.walk(ast.parse(src)):
        if isinstance(node, ast.Import):
            if any(a.name.split(".")[0] in VO.FORBIDDEN_IMPORTS for a in node.names):
                return False
        elif isinstance(node, ast.ImportFrom) and node.module:
            if node.module.split(".")[0] in VO.FORBIDDEN_IMPORTS:
                return False
    return True


def nothing_is_promoted():
    """Not one of the eight cells is adopted. `voxref` is untouched and the frozen census stays
    frozen — measuring a cheaper arrangement and shipping one are different acts."""
    return VC.the_committed_reference_is_untouched() and VO.nothing_is_optimised()


# ---- the record ---------------------------------------------------------------------------------------
RECORD = os.path.join("spec", "attest", "voxref-silo.txt")


def lattice_digest():
    body = "\n".join("%s %s" % (cell_name(c), " ".join("%s=%d" % (k, panel(c)[k])
                                                       for k in COLUMNS)) for c in CELLS)
    body += "\n" + " ".join("%s%s=%d/%d" % ((x, y) + orthogonality(x, y))
                            for x, y in (("G", "T"), ("G", "A"), ("T", "A")))
    body += "\n" + "premise %d %d %d" % premise_census()
    return hashlib.sha256(MAGIC + b"|silo|" + body.encode()).hexdigest()


def generate():
    cov, bad, worst = premise_census()
    rows = ["# URDRVXH1 three silos, eight cells — emitted by voxsilo.generate(), committed as an",
            "# artifact, re-derived by the gate.",
            "# world %s" % VR.world_digest(),
            "# ONE CONTRACT NO SILO MAY NEGOTIATE: the observable is BYTE-IDENTICAL, colour and",
            "# depth as LISTS, on every declared frame, in every one of the eight cells.",
            "# THE CONTRACT CAUGHT AN UNSOUND OPTIMISATION ON ITS FIRST RUN, and the refuted cull is",
            "# kept RUNNABLE as a plant that must still move the observable.",
            "# THE FULL COMBINATION IS NOT THE BEST CELL.",
            "#   arm     <arm> <the one question it may answer>",
            "#   cell    <cell> <column> <count>",
            "#   omega   <pair> <numerator> <denominator>",
            "#   premise <covered> <below the minimum vertex depth> <worst shortfall>",
            "#   best    <cheapest cell in multiplies>",
            "#   digest  <lattice digest>"]
    for a in ARMS:
        rows.append("arm %s %s" % (a, QUESTION[a]))
    for c in CELLS:
        for k in COLUMNS:
            rows.append("cell %s %s %d" % (cell_name(c), k, panel(c)[k]))
    for x, y in (("G", "T"), ("G", "A"), ("T", "A")):
        rows.append("omega %s%s %d %d" % ((x, y) + orthogonality(x, y)))
    rows.append("premise %d %d %d" % (cov, bad, worst))
    rows.append("best %s" % best_cell("mul"))
    rows.append("digest %s" % lattice_digest())
    return "\n".join(rows) + "\n"


def _read():
    with open(os.path.join(ROOT, RECORD), encoding="utf-8") as fh:
        return fh.read()


def parse(text=None):
    if text is None:
        text = _read()
    rows, world = [], None
    names = {cell_name(c) for c in CELLS}
    pairs = {"GT", "GA", "TA"}
    for ln in text.split("\n"):
        ln = ln.strip()
        if not ln:
            continue
        if ln.startswith("#"):
            if ln.startswith("# world "):
                world = ln.split()[2]
            continue
        f = ln.split()
        if f[0] == "arm" and (len(f) < 3 or f[1] not in ARMS):
            raise VoxsiloError("VOXSILO-REFUSE: an arm row naming no declared arm")
        if f[0] == "cell" and (len(f) != 4 or f[1] not in names or f[2] not in COLUMNS):
            raise VoxsiloError("VOXSILO-REFUSE: a cell row naming no declared cell or column")
        if f[0] == "omega" and (len(f) != 4 or f[1] not in pairs):
            raise VoxsiloError("VOXSILO-REFUSE: an omega row naming no declared pair")
        if f[0] == "premise" and len(f) != 4:
            raise VoxsiloError("VOXSILO-REFUSE: a premise row of the wrong arity")
        if f[0] == "best" and (len(f) != 2 or f[1] not in names):
            raise VoxsiloError("VOXSILO-REFUSE: a best row naming no declared cell")
        if f[0] not in ("arm", "cell", "omega", "premise", "best", "digest"):
            raise VoxsiloError("VOXSILO-REFUSE: a row of unknown kind %r" % (f[0],))
        rows.append(tuple(f))
    if world is None:
        raise VoxsiloError("VOXSILO-REFUSE: the record names no world digest")
    if not rows:
        raise VoxsiloError("VOXSILO-REFUSE: the record has no rows")
    return world, rows


def the_record_names_this_world():
    return parse()[0] == VR.world_digest()


def the_record_is_bound_to_the_live_code():
    _w, rows = parse()
    live = {cell_name(c): panel(c) for c in CELLS}
    om = {"".join(p): orthogonality(*p) for p in (("G", "T"), ("G", "A"), ("T", "A"))}
    for r in rows:
        if r[0] == "cell" and int(r[3]) != live[r[1]][r[2]]:
            return False
        if r[0] == "omega" and (int(r[2]), int(r[3])) != om[r[1]]:
            return False
        if r[0] == "premise" and tuple(int(x) for x in r[1:]) != premise_census():
            return False
        if r[0] == "best" and r[1] != best_cell("mul"):
            return False
    pinned = next(r[1] for r in rows if r[0] == "digest")
    return pinned == lattice_digest()


def a_tampered_row_refuses():
    text = _read()
    for ln in text.split("\n"):
        if ln.startswith("cell "):
            f = ln.split()
            f[2] = "cycles"
            text = text.replace(ln, " ".join(f), 1)
            break
    try:
        parse(text)
    except VoxsiloError:
        return True
    return False


def told():
    m, w = column("mul"), column("walked")
    cov, bad, worst = premise_census()
    spent, saved = exchange_rate()
    walked, tris = mean_walked_box()
    return ("THE CONTRACT CAUGHT AN UNSOUND OPTIMISATION ON ITS FIRST RUN: the premise every "
            "hierarchical-Z scheme rests on — that interpolated depth is a CONVEX COMBINATION of "
            "the vertex depths — is FALSE here at %d of %d covered pixels (%d in every hundred), "
            "worst shortfall %d, because the top-left bias makes the weights sum to `area + B` "
            "while the depth still divides by `area`. AND THE FULL COMBINATION IS NOT THE BEST "
            "CELL: %s is cheapest in multiplies at %d against GTA's %d, so arm T spends %d extra "
            "multiplies to retire %d walked pixels — SIX AND A HALF PER PIXEL, at a moment when arm "
            "A has already made a walked pixel cost ZERO. Omega(T,A) = %d/%d, ABOVE ONE, which is "
            "not redundancy but SUBTRACTION. The mechanism is geometry and not the test: %d walked "
            "pixels across %d walked triangles is a mean bounding box of %d against a tile of %d"
            % (bad, cov, (100 * bad) // cov, worst, best_cell("mul"), m[best_cell("mul")], m["GTA"],
               spent, saved, orthogonality("T", "A")[0], orthogonality("T", "A")[1],
               walked, tris, walked // tris, TILE * TILE))


def scene_case(name):
    if name == "lattice":
        return repr(tuple((cell_name(c), tuple((k, panel(c)[k]) for k in COLUMNS)) for c in CELLS))
    if name == "premise":
        return repr((premise_census(),
                     tuple((x + y, orthogonality(x, y))
                           for x, y in (("G", "T"), ("G", "A"), ("T", "A"))),
                     best_cell("mul"), exchange_rate(), mean_walked_box()))
    raise VoxsiloError("VOXSILO-REFUSE: no scene named %r" % name)


def scene_result(name):
    return hashlib.sha256(MAGIC + b"|" + name.encode() + b"|"
                          + scene_case(name).encode()).hexdigest()


SCENES = ("lattice", "premise")


def golden(name):
    with open(os.path.join(_HERE, "conformance_voxsilo.txt"), encoding="utf-8") as fh:
        for ln in fh:
            ln = ln.strip()
            if ln and not ln.startswith("#"):
                nm, dig = ln.split()
                if nm == name:
                    return dig
    raise VoxsiloError("VOXSILO-REFUSE: no golden named %r" % name)
