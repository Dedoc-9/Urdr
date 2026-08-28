# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""voxconv (URDRVXN1) — RE-DERIVE THE POPULATION UNDER BOTH CONVENTIONS, BECAUSE MOST OF IT WAS THE
CONVENTION.

`voxfill` found that the reference's projection FLOORS — mapping a screen position into a pixel
REGION — while its sample point is that region's CORNER, and that the oracle inherited the corner
convention from the projection's algebra rather than from its rounding. It then wrote its own
boundary: every count in `voxtie`, `voxfate` and `voxfill` was measured with the corner sample, so
none of them could speak for the aligned convention. THIS RUNG PAYS THAT DEBT AND THE BILL IS LARGE.

                                    corner        centre
        disagreeing pixels            1137           104
        stable                         378            89
        boundary                       198             5
        degenerate                     561            10
        impossible faces               152             4

NINE TENTHS OF THE DISAGREEMENT WAS THE CONVENTION. And the class that collapses hardest is the one
no experiment could have argued with: DEGENERATE falls 561 -> 10. That class means the exact ray
crosses two or three lattice planes at one parameter, where the ORACLE itself answers by convention
and no limit can appeal past it — and it was never a property of the world. Integer screen
coordinates are exactly the rays that land on lattice-plane crossings; offset the sample by half a
pixel and they almost all stop being degenerate at THIS lattice.

AND THE FIRST VERSION OF THAT PARAGRAPH OVERSTATED IT, GREEN AND PUSHED. It said `voxevent` measured
20.1% of declared rays entering through an edge or corner and called it a property of the lattice,
and that it is a property of where the rays were aimed. The claim carried NO SCALE, and the answer
depends on the scale: `voxgrid` re-derived `voxevent`'s whole ladder and found the artefact share is
96% at the base lattice (1017 crossings become 40) and 50% at scale 8 (11119 become 5507), because
subdividing by s multiplies the plane density by s and a half-pixel offset that dodged the coarse
planes cannot dodge the fine ones. The census below is at the base lattice, where the collapse IS
nearly total — but the sentence generalised past it, and a claim with no scale attached is a claim
with room in it.

THE COVERAGE DIAGNOSIS SURVIVES, AND THAT IS THE POINT OF ASKING. Of the 89 surviving stable
disagreements the fates are `not_covered` 74, `depth_rejected` 12, `phantom` 3 — 83.1% coverage
against `voxfate`'s 84.1% on a population thirteen times larger. The share is preserved almost
exactly while the population collapses, which is what a real mechanism does and what an artefact
does not.

AND THE OWNERSHIP CLASS VANISHES ENTIRELY: `bias_only` 215 -> 0. `voxfill` refuted the top-left
hypothesis by re-scoring one arm under the aligned pairing; this rung refutes it a second time by a
completely different route, re-deriving the population from scratch and finding the class it
explained no longer exists. The 215 pixels were the corner sample landing on a projected edge. THE
TOP-LEFT RULE IS EXONERATED TWICE, INDEPENDENTLY.

WHAT IS LEFT IS ONE MECHANISM AND IT IS NOT ONE ANY ARM HAS TESTED. Every surviving `not_covered`
pixel is `outside` and every one of them by less than a pixel: the floored projected vertex, and
nothing else. That is a quantisation defect in the PROJECTION, not a rule in the fill.

AND THE IMPOSSIBLE POPULATION IS NOW TOO SMALL TO CARRY A CLAIM. Four pixels, of which three are
`depth_rejected` and one `not_covered` — an inversion of the corner reading's 78 and 2. Four is not
a distribution. `the_impossible_population_is_too_small_to_read` states that refusal as a law, so
that the day it is read off anyway the gate says so.

does_not_show: anything about performance. WHICH CONVENTION IS RIGHT — this rung measures what each
implies and decides nothing, because adopting one changes what the ORACLE is and reaches every
record derived from `voxray`. That the centre convention is free of defects: it has 104
disagreements and 4 impossible faces, which is better and is not zero. Any mechanism for the
surviving 74. And nothing is repaired: `voxref` and `voxray` are untouched, and the frozen census
stays frozen.

falsifier: the corner arm is REQUIRED to reproduce `voxtie`'s classified census, `voxfate`'s
conditioned fates and `voxfill`'s rejection classification exactly — a re-derivation that cannot
reproduce the numbers it is re-deriving is measuring something else, and `the_corner_arm_reproduces_
the_committed_rungs` reddens on any drift.
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

MAGIC = b"URDRVXN1"

#: DECLARED — the two conventions, named by `voxfill` and re-derived here from scratch.
CONVENTIONS = VL.CONVENTIONS

#: The classes and fates, held as references to the modules that own them rather than copied, so a
#: change to either vocabulary reaches this rung instead of drifting past it.
CLASSES = VT.CLASSES
FATES = VS.FATES
REJECTIONS = VL.REJECTIONS


class VoxconvError(Exception):
    """VOXCONV-REFUSE — a convention or a record this module will not pretend to read."""


def offsets(convention):
    """(rasteriser sub-pixel offset, oracle SUB offset) for a convention.

    The two denominators differ — the ladder carries vertices at 1/64 of a pixel and the limit test
    perturbs at 1/1024 — so the half-pixel is expressed in each and never converted between them.
    """
    if convention not in CONVENTIONS:
        raise VoxconvError("VOXCONV-REFUSE: no convention named %r" % (convention,))
    _n, _sym, S = VT.level(VT.BEST)
    return (0, 0) if convention == "corner" else (S // 2, VT.SUB // 2)


def the_two_offsets_are_the_same_half_pixel():
    """VALIDITY OF THE PARAMETERISATION. Both offsets must be half of their own denominator, or the
    rasteriser and the oracle would be sampling two different points and every number below would
    be comparing a picture with a ray that never aimed at it."""
    _n, _sym, S = VT.level(VT.BEST)
    ro, oo = offsets("centre")
    return (offsets("corner") == (0, 0) and ro * 2 == S and oo * 2 == VT.SUB)


# ---- the instrumented renderer, parameterised by the sample point -------------------------------------
def instrument(prims, eye, fwd, off):
    """`voxfate.instrument_level` with the sample point moved. Returns (winner, stage, covered).

    A FIFTH TRANSCRIPTION OF THE SAME LOOP, and bound in BOTH directions: at `off == 0` its winner,
    stages and covered sets must equal `voxfate.instrument_level`'s, and at either offset its winner
    must equal `voxfill.render_arm`'s. A chain this long is exactly how a rung ends up measuring a
    renderer nobody declared, so the chain is checked rather than trusted.
    """
    _n, _sym, S = VT.level(VT.BEST)
    m = VR.basis(fwd)
    cx, cy = VR.W // 2, VR.H // 2
    dep = [None] * (VR.W * VR.H)
    key = [-1] * (VR.W * VR.H)
    stage, covered = {}, {}
    for pk, _col, quad in prims:
        cam = [VR._project(v, eye, m) for v in quad]
        if any(c[1] < VR.NEAR for c in cam):
            stage[pk] = max(stage.get(pk, 0), VM.STAGES.index("near_clipped"))
            continue
        st = VM.STAGES.index("near_clipped")
        scr = [((cx * S * c[1] + c[0] * VR.FOCAL * S) // c[1],
                (cy * S * c[1] - c[2] * VR.FOCAL * S) // c[1], c[1]) for c in cam]
        for a, b, c2 in ((scr[0], scr[1], scr[2]), (scr[0], scr[2], scr[3])):
            area = (b[0] - a[0]) * (c2[1] - a[1]) - (b[1] - a[1]) * (c2[0] - a[0])
            if area == 0:
                st = max(st, VM.STAGES.index("degenerate"))
                continue
            if area < 0:
                st = max(st, VM.STAGES.index("backface"))
                continue
            xl = max(min(a[0], b[0], c2[0]) // S, 0)
            xh = min(max(a[0], b[0], c2[0]) // S, VR.W - 1)
            yl = max(min(a[1], b[1], c2[1]) // S, 0)
            yh = min(max(a[1], b[1], c2[1]) // S, VR.H - 1)
            if xl > xh or yl > yh:
                st = max(st, VM.STAGES.index("offscreen"))
                continue
            st = VM.RASTERISED
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
                    if dep[i] is None or (d, pk) < (dep[i], key[i] if key[i] >= 0 else (1 << 62)):
                        dep[i] = d
                        key[i] = pk
        stage[pk] = max(stage.get(pk, 0), st)
    return key, stage, covered


def the_instrument_is_bound_in_both_directions():
    prims = VX.primitives_with("reversed")
    _n, sym, S = VT.level(VT.BEST)
    for f, (_nm, eye, fwd) in enumerate(VR.TRACE):
        mine = instrument(prims, eye, fwd, 0)
        if mine != VS.instrument_level(prims, eye, fwd, sym, S):
            return False
        for conv, arm in (("corner", "committed"), ("centre", "centre")):
            if (instrument(prims, eye, fwd, offsets(conv)[0])[0]
                    != VL.render_arm(arm, prims, eye, fwd)[0]):
                return False
    return True


# ---- the oracle and the classifier, parameterised the same way ----------------------------------------
def _ask(eye, fwd, sx, sy):
    h = VX.first_hit(eye, VT._ray(eye, fwd, sx, sy), VR.solid, VC.ORIGIN)
    return None if h is None else (h[0], h[1])


def classify(eye, fwd, px, py, oo):
    """`voxtie.classify` with the sample point moved. (class, x-pattern, y-pattern)."""
    sx, sy = px * VT.SUB + oo, py * VT.SUB + oo
    ex = _ask(eye, fwd, sx, sy)
    xp = VT._pattern(_ask(eye, fwd, sx - 1, sy), ex, _ask(eye, fwd, sx + 1, sy))
    yp = VT._pattern(_ask(eye, fwd, sx, sy - 1), ex, _ask(eye, fwd, sx, sy + 1))
    if VT.simultaneous_planes(eye, fwd, VR.solid, sx, sy) >= 2:
        return "degenerate", xp, yp
    if xp == "AAA" and yp == "AAA":
        return "stable", xp, yp
    return "boundary", xp, yp


_ORACLE = {}


def oracle(frame, convention):
    k = (VR.world_digest(), frame, convention)
    if k not in _ORACLE:
        _nm, eye, fwd = VR.TRACE[frame]
        oo = offsets(convention)[1]
        _ORACLE[k] = [_ask(eye, fwd, (i % VR.W) * VT.SUB + oo, (i // VR.W) * VT.SUB + oo)
                      for i in range(VR.W * VR.H)]
    return _ORACLE[k]


# ---- the census, re-derived from scratch under each convention ----------------------------------------
_CENSUS = {}


def census(convention):
    """(frame, px, py, class, fate, rejection, near, impossible) for every disagreeing pixel.

    RE-DERIVED FROM SCRATCH under the named convention — the render, the oracle, the classifier and
    the fate all move together. Nothing is inherited from the corner-convention rungs except the
    vocabularies, and the corner arm is required to reproduce their numbers exactly.
    """
    k = (VR.world_digest(), convention)
    if k in _CENSUS:
        return _CENSUS[k]
    ro, oo = offsets(convention)
    _n, _sym, S = VT.level(VT.BEST)
    prims = VX.primitives_with("reversed")
    keyed = {pk for pk, _c, _q in prims}
    rows = []
    for f, (_nm, eye, fwd) in enumerate(VR.TRACE):
        key, stage, covered = instrument(prims, eye, fwd, ro)
        ora = oracle(f, convention)
        own = tuple(e // VR.Q for e in eye)
        tris = VL._triangles(prims, eye, fwd)
        for i, kk in enumerate(key):
            r = VM.winner_answer(kk)
            if r == ora[i]:
                continue
            px, py = i % VR.W, i // VR.W
            cls, xp, yp = classify(eye, fwd, px, py, oo)
            imp = (r is not None and r[0] != "extra"
                   and VM.impossible_winner(r[0], r[1], VR.solid, own))
            fate = VM._fate(px, py, i, r, ora[i], ora, keyed, stage, covered, ("sampling_shift",))
            rej, near = "-", 1
            if cls == "stable" and fate == "not_covered" and ora[i] is not None:
                o = ora[i]
                pk = (((o[0][0] * VR.N) + o[0][1]) * VR.N + o[0][2]) * 6 + o[1]
                rej, near = _rejection(tris.get(pk, []), px, py, ro, S)
            rows.append((f, px, py, cls, fate, rej, 1 if near else 0, 1 if imp else 0,
                         xp, yp))
    _CENSUS[k] = rows
    return rows


def _rejection(tris, px, py, off, S):
    """`voxfill.rejection_of` at the moved sample, ranked by (class, near) as its correction fixed."""
    best = None
    for a, b, c2, bb, (xl, xh, yl, yh) in tris:
        sx, sy = px * S + off, py * S + off
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
            near = all(VL._within_one_pixel(e[j], pts[j][0][0], pts[j][0][1],
                                            pts[j][1][0], pts[j][1][1], S) for j in rej)
        rank = (REJECTIONS.index(cls), 1 if near else 0)
        if best is None or rank > best[0]:
            best = (rank, cls, near)
    return (best[1], best[2]) if best is not None else ("bbox", True)


def summary(convention):
    """(disagreeing, per class, per stable fate, per stable-not_covered rejection, impossible)."""
    rows = census(convention)
    cls = dict.fromkeys(CLASSES, 0)
    fate = dict.fromkeys(FATES, 0)
    rej = dict.fromkeys(REJECTIONS, 0)
    imp = 0
    for _f, _px, _py, c, ft, rj, _near, im, _xp, _yp in rows:
        cls[c] += 1
        imp += im
        if c == "stable":
            fate[ft] += 1
            if rj in rej:
                rej[rj] += 1
    return len(rows), cls, fate, rej, imp


# ---- the laws -------------------------------------------------------------------------------------
def the_corner_arm_reproduces_the_committed_rungs():
    """A RE-DERIVATION THAT CANNOT REPRODUCE THE NUMBERS IT RE-DERIVES IS MEASURING SOMETHING ELSE.

    The corner arm must land on `voxtie`'s classified census, `voxfate`'s conditioned fate
    distribution and `voxfill`'s rejection classification — all three, exactly.
    """
    n, cls, fate, rej, imp = summary("corner")
    if n != len(VT.census()):
        return False
    tie = dict.fromkeys(CLASSES, 0)
    for r in VT.census():
        tie[r[3]] += 1
    if cls != tie:
        return False
    if fate != VS.distribution(False):
        return False
    live = VL.rejection_distribution()
    return all(rej[c] == live[c] for c in REJECTIONS)


def the_population_was_mostly_the_convention():
    """NINE TENTHS OF THE DISAGREEMENT WAS THE SAMPLE POINT. Stated as a comparison between the two
    re-derivations and not as a fraction chosen to sound like the answer — `voxtie` was reddened
    once by exactly that mistake."""
    return summary("centre")[0] * 5 < summary("corner")[0]


def the_degeneracy_was_the_integer_sample():
    """THE CLASS NO EXPERIMENT COULD ARGUE WITH IS THE ONE THAT COLLAPSES HARDEST. `degenerate`
    means the exact ray crosses two or three lattice planes at one parameter, where the ORACLE is
    answering by convention — and integer screen coordinates are precisely the rays that land on
    those crossings. It is not a property of the world; it is a property of where the rays were
    aimed. `voxevent` measured a rate of edge and corner entries and read it as the lattice."""
    return summary("centre")[1]["degenerate"] * 10 < summary("corner")[1]["degenerate"]


def the_coverage_diagnosis_survives():
    """THE POINT OF ASKING. The population collapses thirteenfold and the coverage SHARE does not
    move — which is what a real mechanism does and what an artefact does not. The law compares
    shares by integer cross-multiplication so no float or percentage is invented for it."""
    _n0, _c0, f0, _r0, _i0 = summary("corner")
    _n1, _c1, f1, _r1, _i1 = summary("centre")
    t0, t1 = sum(f0.values()), sum(f1.values())
    if not (t0 and t1):
        return False
    if max(f1, key=lambda k: f1[k]) != "not_covered" != max(f0, key=lambda k: f0[k]):
        return False
    return abs(f0["not_covered"] * t1 - f1["not_covered"] * t0) * 20 < t0 * t1


def the_ownership_class_vanishes():
    """THE TOP-LEFT RULE IS EXONERATED A SECOND TIME, BY A DIFFERENT ROUTE. `voxfill` re-scored one
    arm under the aligned pairing; this rung re-derives the population from scratch and finds the
    class that arm was built to explain no longer exists at all."""
    return summary("corner")[3]["bias_only"] > 0 == summary("centre")[3]["bias_only"]


def the_residue_is_pure_quantisation():
    """WHAT SURVIVES IS ONE MECHANISM AND NO ARM HAS TESTED IT. Every surviving `not_covered` pixel
    is `outside` and every one by less than a pixel — the floored projected vertex and nothing
    else, which is a defect in the PROJECTION rather than a rule in the fill."""
    rows = [r for r in census("centre") if r[3] == "stable" and r[4] == "not_covered"]
    _n, _c, f, rej, _i = summary("centre")
    return (rows and rej["outside"] == len(rows) == f["not_covered"]
            and all(r[6] for r in rows) and rej["bbox"] == rej["bias_only"] == 0)


def the_impossible_population_is_too_small_to_read():
    """AN ANTI-INFLATION LAW. Under the aligned convention the impossible faces number four, and
    their fates invert the corner reading's. Four is not a distribution. This law states the refusal
    so that the day someone reads a mechanism off it, the gate says so — it reddens if the
    population ever grows past the point where the refusal was honest."""
    return 0 < summary("centre")[4] < 10


def the_oracle_is_still_a_function():
    """No `ABA` under EITHER convention: the exact value always equals one of the two sides. The
    property `voxtie` established for the corner sample is re-established rather than assumed."""
    for conv in CONVENTIONS:
        for r in census(conv):
            if "ABA" in (r[8], r[9]):
                return False
    return True


def nothing_is_adopted():
    """`voxref` AND `voxray` are untouched. This rung measures what each convention implies and
    decides nothing, because adopting one changes what the ORACLE is.

    The oracle check is a PROPORTIONALITY, not an equality: `voxtie._ray` carries the same direction
    at SUB times the magnitude, and asserting equality here was this module's first red — a law that
    compared two vectors of different scale and called the difference an adoption."""
    eye, fwd = VR.TRACE[0][1], VR.TRACE[0][2]
    plain = VX.ray_for_pixel(eye, fwd, 10, 0)
    scaled = VT._ray(eye, fwd, 10 * VT.SUB, 0)
    return (VC.the_committed_reference_is_untouched()
            and scaled == tuple(VT.SUB * v for v in plain)
            and offsets("corner") == (0, 0))


# ---- the record -------------------------------------------------------------------------------------
RECORD = os.path.join("spec", "attest", "voxref-convention.txt")


def population_digest():
    body = "\n".join("%s %d %d %d %s %s %s %d %d %s %s"
                     % ((c,) + r) for c in CONVENTIONS for r in census(c))
    return hashlib.sha256(MAGIC + b"|convention|" + body.encode()).hexdigest()


def generate():
    rows = ["# URDRVXN1 convention census — emitted by voxconv.generate(), committed as an artifact,",
            "# re-derived by the gate.",
            "# world %s" % VR.world_digest(),
            "# THE SAME POPULATION DERIVED TWICE, ONCE PER SAMPLE CONVENTION. `voxfill` found the",
            "# projection floors into a pixel REGION while the sample is that region's CORNER, and",
            "# wrote its own boundary: every count in `voxtie`, `voxfate` and `voxfill` was measured",
            "# with the corner sample. This is that debt paid, and nine tenths of the disagreement",
            "# was the convention.",
            "#   count   <convention> <disagreeing> <impossible>",
            "#   class   <convention> <class> <count>",
            "#   fate    <convention> <fate> <count among the stable>",
            "#   reject  <convention> <class> <count among the stable not_covered>",
            "#   pixel   <convention> <frame> <px> <py> <class> <fate> <rejection> <near>"
            " <impossible> <x-pattern> <y-pattern>",
            "#   digest  <population digest>"]
    for c in CONVENTIONS:
        n, cls, fate, rej, imp = summary(c)
        rows.append("count %s %d %d" % (c, n, imp))
        for k in CLASSES:
            rows.append("class %s %s %d" % (c, k, cls[k]))
        for k in FATES:
            rows.append("fate %s %s %d" % (c, k, fate[k]))
        for k in REJECTIONS:
            rows.append("reject %s %s %d" % (c, k, rej[k]))
    for c in CONVENTIONS:
        for r in census(c):
            rows.append("pixel %s %d %d %d %s %s %s %d %d %s %s" % ((c,) + r))
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
        if f[0] in ("count", "class", "fate", "reject", "pixel") and f[1] not in CONVENTIONS:
            raise VoxconvError("VOXCONV-REFUSE: a row naming no declared convention")
        if f[0] == "class" and (len(f) != 4 or f[2] not in CLASSES):
            raise VoxconvError("VOXCONV-REFUSE: a class row in no declared class")
        if f[0] == "fate" and (len(f) != 4 or f[2] not in FATES):
            raise VoxconvError("VOXCONV-REFUSE: a fate row in no declared fate")
        if f[0] == "reject" and (len(f) != 4 or f[2] not in REJECTIONS):
            raise VoxconvError("VOXCONV-REFUSE: a reject row in no declared class")
        if f[0] == "pixel" and (len(f) != 12 or f[5] not in CLASSES or f[6] not in FATES):
            raise VoxconvError("VOXCONV-REFUSE: a pixel row in no declared class or fate")
        if f[0] not in ("count", "class", "fate", "reject", "pixel", "digest"):
            raise VoxconvError("VOXCONV-REFUSE: a row of unknown kind %r" % (f[0],))
        rows.append(tuple(f))
    if world is None:
        raise VoxconvError("VOXCONV-REFUSE: the record names no world digest")
    if not rows:
        raise VoxconvError("VOXCONV-REFUSE: the record has no rows")
    return world, rows


def the_record_names_this_world():
    return parse()[0] == VR.world_digest()


def the_record_is_bound_to_the_live_code():
    _w, rows = parse()
    live = {c: summary(c) for c in CONVENTIONS}
    for r in rows:
        if r[0] == "count" and (int(r[2]), int(r[3])) != (live[r[1]][0], live[r[1]][4]):
            return False
        if r[0] == "class" and int(r[3]) != live[r[1]][1][r[2]]:
            return False
        if r[0] == "fate" and int(r[3]) != live[r[1]][2][r[2]]:
            return False
        if r[0] == "reject" and int(r[3]) != live[r[1]][3][r[2]]:
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
    except VoxconvError:
        return True
    return False


def told():
    n0, c0, f0, r0, i0 = summary("corner")
    n1, c1, f1, r1, i1 = summary("centre")
    return ("the same population derived twice: %d disagreeing pixels at the corner sample and %d "
            "at the centre, so nine tenths of it was the convention. Classes %d/%d/%d stable/"
            "boundary/degenerate become %d/%d/%d — the DEGENERATE class, where the oracle itself "
            "answers by convention, collapses %d to %d because integer screen coordinates are "
            "exactly the rays that land on lattice-plane crossings. THE COVERAGE DIAGNOSIS "
            "SURVIVES: not_covered %d of %d stable becomes %d of %d, the same share on a population "
            "thirteen times smaller. THE OWNERSHIP CLASS DOES NOT: bias_only %d becomes %d, so the "
            "top-left rule is exonerated a second time by a route `voxfill` did not take. What is "
            "left is one mechanism no arm has tested — every surviving not_covered pixel is "
            "`outside` and every one by less than a pixel, which is the floored projected vertex "
            "and nothing else. Impossible faces %d become %d, which is too few to read"
            % (n0, n1, c0["stable"], c0["boundary"], c0["degenerate"],
               c1["stable"], c1["boundary"], c1["degenerate"],
               c0["degenerate"], c1["degenerate"],
               f0["not_covered"], sum(f0.values()), f1["not_covered"], sum(f1.values()),
               r0["bias_only"], r1["bias_only"], i0, i1))


def scene_case(name):
    if name == "census":
        return repr(tuple((c,) + summary(c) for c in CONVENTIONS))
    if name == "population":
        return repr(population_digest())
    raise VoxconvError("VOXCONV-REFUSE: no scene named %r" % name)


def scene_result(name):
    return hashlib.sha256(MAGIC + b"|" + name.encode() + b"|"
                          + scene_case(name).encode()).hexdigest()


SCENES = ("census", "population")


def golden(name):
    with open(os.path.join(_HERE, "conformance_voxconv.txt"), encoding="utf-8") as fh:
        for ln in fh:
            ln = ln.strip()
            if ln and not ln.startswith("#"):
                nm, dig = ln.split()
                if nm == name:
                    return dig
    raise VoxconvError("VOXCONV-REFUSE: no golden named %r" % name)
