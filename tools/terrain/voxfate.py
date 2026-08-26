# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""voxfate (URDRVXS1) — CONDITION THE POPULATION, THEN ASK WHAT BROKE IT.

EVERY FATE DISTRIBUTION THIS ARC HAS PRODUCED WAS CONTAMINATED, and the contamination was not small.
`voxmicro` classified where the rasteriser loses a face — not generated, near-clipped, degenerate,
backfacing, off-screen, not covered, depth rejected — over the WHOLE residual, which mixes three
populations that have nothing to do with each other: real defects, samples sitting on a visibility
event surface, and rays entering through an edge or corner where the oracle is answering by its own
convention. A mechanism inferred from that mixture is a mechanism for an average of three unrelated
things.

`voxtie` separated them. 1137 disagreeing pixels, 378 STABLE — the oracle unchanged at the exact
sample, at a thousandth of a pixel either side in both screen directions, and under six single-axis
camera perturbations. Those are the pixels where a disagreement admits no appeal to ambiguity.

THIS MODULE ASKS THE FATE QUESTION OF THOSE 378 AND OF NOTHING ELSE, and the answer does not split:

    not_covered      318   84.1%     the oracle's face WAS rasterised and did not claim the pixel
    depth_rejected    58   15.3%     it claimed the pixel and lost the depth test
    phantom            2    0.5%     the rasteriser drew where the oracle finds nothing

and of the 80 stable pixels awarding an IMPOSSIBLE face — one sandwiched between two solid cells —
78 are `not_covered` and 2 are `depth_rejected`. The surviving defect is COVERAGE, and the next
experiment lives entirely inside the fill rule rather than in depth ordering, the projection, or the
tie convention.

THE SAMPLING BRANCH IS DISABLED HERE, AND THAT IS THE WHOLE METHODOLOGICAL POINT. `voxmicro` tests
first whether the rasteriser's answer at a pixel equals the oracle's answer at an integer NEIGHBOUR,
and subtracts those as explained by the measured <=1px offset. On this population that subtraction
would be circular: these pixels are already known stable under sub-pixel perturbation, so a
neighbour agreeing is not evidence that sampling explains anything. Run with the branch enabled, 269
of the 378 are absorbed into `sampling_shift` and the coverage signal disappears entirely.

AND THE TWO FACTS TOGETHER SAY SOMETHING NEITHER SAYS ALONE. Sub-pixel stable, yet the rasteriser's
answer equals the oracle's answer ONE WHOLE PIXEL OVER, at 269 of 378. That is not a sub-pixel
ambiguity being resolved differently. It is a whole-pixel coverage displacement: the fill rule is
effectively claiming pixels for a face that the ray through the integer coordinate does not meet.

AND THE MINIMAL COUNTEREXAMPLE IS THE PIXEL THIS WHOLE ARC STARTED FROM. Six rungs ago a face-culling
experiment disagreed with the reference at frame 4, pixel (10, 0), and tracing it produced an
unculled winner of voxel (2,1,10)'s INTERIOR top face beating voxel (2,1,11)'s own exposed face —
impossible, not merely surprising, and the reason an oracle had to exist at all. `voxray` then found
the oracle names a THIRD answer there, voxel (2,0,10), which neither arm had. That pixel is now the
first instance of the dominant class: the oracle's face IS rasterised, reaches the pixel loop, and
does not claim the pixel. The investigation returns to where it began with the mechanism named.

does_not_show: anything about performance. WHY the coverage displaces — this module localises the
class and does not explain it; the candidates are the half-open top-left convention, the bounding
box derivation, and the sample point the fill rule effectively uses, and choosing between them is
the next rung's binary experiment. That the split generalises past the declared trace. And nothing
is repaired: `voxref` is untouched here as in `voxcand` and `voxtie`, and the census stays frozen.

falsifier: the instrumented render must reproduce `voxtie`'s ladder winners exactly, so a third
transcription cannot quietly measure a fourth renderer; the conditioned population is required to
be a strict subset of the residual and to be exactly `voxtie`'s stable set, so a drifted
conditioning reddens; and the contamination is DEMONSTRATED rather than argued — the same
classifier is run over the same pixels with the sampling branch on, and the coverage class must
collapse, because a claim that conditioning matters is worth nothing without the unconditioned run
beside it.
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

MAGIC = b"URDRVXS1"

#: The class this module conditions on, declared rather than hardcoded at each use.
CONDITION = "stable"

#: DECLARED — the fates that can survive conditioning, in the order `voxmicro` declares them. Kept
#: as a subset name rather than a copy, so a change to the fate vocabulary reaches here.
FATES = VM.REJECTS


class VoxfateError(Exception):
    """VOXFATE-REFUSE — a population or a record this module will not pretend to read."""


# ---- the instrumented level ----------------------------------------------------------------------
def instrument_level(prims, eye, fwd, sym, S):
    """`voxtie.render_level` with `voxmicro`'s fate instrumentation. Returns (winner, stage, covered).

    A THIRD TRANSCRIPTION OF THE SAME LOOP, and therefore bound: `the_instrument_matches_the_ladder`
    requires this winner array to equal `voxtie.render_level`'s on every declared frame.
    """
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
        if sym:
            scr = [((cx * S * c[1] + c[0] * VR.FOCAL * S) // c[1],
                    (cy * S * c[1] - c[2] * VR.FOCAL * S) // c[1], c[1]) for c in cam]
        else:
            scr = [(cx * S + (c[0] * VR.FOCAL * S) // c[1],
                    cy * S - (c[2] * VR.FOCAL * S) // c[1], c[1]) for c in cam]
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
                    sx, sy = px * S, py * S
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


def the_instrument_matches_the_ladder():
    _n, sym, S = VT.level(VT.BEST)
    prims = VX.primitives_with("reversed")
    for _nm, eye, fwd in VR.TRACE:
        if instrument_level(prims, eye, fwd, sym, S)[0] != VT.render_level(prims, eye, fwd, sym, S):
            return False
    return True


# ---- the conditioned population --------------------------------------------------------------------
def conditioned():
    """`voxtie`'s classified residual, restricted to the class this module conditions on."""
    return [(f, px, py, imp) for f, px, py, cls, _xp, _yp, _mv, imp in VT.census()
            if cls == CONDITION]


def the_population_is_exactly_the_conditioned_class():
    """A DRIFTED CONDITIONING WOULD MAKE EVERY NUMBER BELOW ABOUT A DIFFERENT SET. The population
    must be a strict subset of the residual and exactly the rows `voxtie` calls stable."""
    all_rows = VT.census()
    mine = conditioned()
    want = sum(1 for r in all_rows if r[3] == CONDITION)
    return 0 < len(mine) == want < len(all_rows)


def fates(sampling=False):
    """The fate of every conditioned pixel. `sampling=True` leaves `voxmicro`'s sampling-shift
    branch enabled, which on THIS population is circular — see the module docstring — and exists
    only so the contamination can be demonstrated rather than asserted."""
    _n, sym, S = VT.level(VT.BEST)
    prims = VX.primitives_with("reversed")
    disable = () if sampling else ("sampling_shift",)
    by_frame = {}
    for f, px, py, imp in conditioned():
        by_frame.setdefault(f, []).append((px, py, imp))
    out = []
    for f in sorted(by_frame):
        _nm, eye, fwd = VR.TRACE[f]
        key, stage, covered = instrument_level(prims, eye, fwd, sym, S)
        ora = VM.oracle_frame(eye, fwd, VR.solid, VC.ORIGIN)
        keyed = {pk for pk, _c, _q in prims}
        for px, py, imp in by_frame[f]:
            i = py * VR.W + px
            r = VM.winner_answer(key[i])
            fate = VM._fate(px, py, i, r, ora[i], ora, keyed, stage, covered, disable)
            out.append((f, px, py, fate, imp))
    return out


def distribution(sampling=False):
    d = dict.fromkeys(FATES, 0)
    for _f, _px, _py, fate, _imp in fates(sampling):
        d[fate] += 1
    return d


def impossible_distribution():
    d = dict.fromkeys(FATES, 0)
    for _f, _px, _py, fate, imp in fates():
        if imp:
            d[fate] += 1
    return d


def dominant():
    d = distribution()
    return max(d, key=lambda k: d[k])


def the_answer_does_not_split():
    """THE RESULT: conditioning gives ONE dominant class, not a spread. If it had split, the honest
    move would have been to preserve the split rather than invent a single mechanism — so the law
    asserts dominance as measured rather than assuming it, and a spread would redden here."""
    d = distribution()
    tot = sum(d.values())
    top = d[dominant()]
    rest = sorted((v for k, v in d.items() if k != dominant()), reverse=True)
    return tot > 0 and top > 4 * (rest[0] if rest else 0)


def the_defect_is_coverage_not_depth():
    """The dominant class is `not_covered`, and it dominates among the IMPOSSIBLE-face pixels too —
    which matters, because those are the subset that needs no oracle to be called wrong."""
    return dominant() == "not_covered" and max(
        impossible_distribution(), key=lambda k: impossible_distribution()[k]) == "not_covered"


def the_contamination_is_demonstrated():
    """CONDITIONING IS SHOWN TO MATTER, not argued. Run the SAME classifier over the SAME pixels
    with the sampling branch enabled and the coverage class must collapse — because a neighbour
    agreeing is not evidence on a population already known stable under sub-pixel perturbation, and
    a claim that the conditioning matters is worth nothing without the unconditioned run beside it.
    """
    off = distribution(False)
    on = distribution(True)
    return on["sampling_shift"] > off["not_covered"] // 2 and on["not_covered"] < off["not_covered"]


# ---- the minimal counterexample ---------------------------------------------------------------------
def minimal_counterexample():
    """The first conditioned pixel of the dominant class in canonical order, with everything needed
    to reproduce it by hand: frame, pixel, the oracle's answer, the rasteriser's winner, and the
    covering state of the oracle's own face."""
    _n, sym, S = VT.level(VT.BEST)
    prims = VX.primitives_with("reversed")
    want = dominant()
    for f, px, py, fate, imp in fates():
        if fate != want:
            continue
        _nm, eye, fwd = VR.TRACE[f]
        key, stage, covered = instrument_level(prims, eye, fwd, sym, S)
        ora = VM.oracle_frame(eye, fwd, VR.solid, VC.ORIGIN)
        i = py * VR.W + px
        o = ora[i]
        k = (((o[0][0] * VR.N) + o[0][1]) * VR.N + o[0][2]) * 6 + o[1]
        return {"frame": f, "pixel": (px, py), "oracle": o,
                "winner": VM.winner_answer(key[i]), "impossible": bool(imp),
                "oracle_face_stage": VM.STAGES[stage.get(k, 0)],
                "oracle_face_covers": sorted(covered.get(k, ()))[:6],
                "covers_this_pixel": i in covered.get(k, ())}
    raise VoxfateError("VOXFATE-REFUSE: the dominant class has no instances")


def the_counterexample_is_minimal_and_real():
    """It must be an instance of the dominant class, and the oracle's face must have REACHED the
    pixel loop while not claiming the pixel — which is what `not_covered` means and what makes the
    next experiment a coverage experiment rather than a guess."""
    c = minimal_counterexample()
    return (c["oracle_face_stage"] == "rasterised" and not c["covers_this_pixel"]
            and c["oracle"] is not None)


# ---- the record ------------------------------------------------------------------------------------
RECORD = os.path.join("spec", "attest", "voxref-fate.txt")


def population_digest():
    body = "\n".join("%d %d %d %s %d" % r for r in fates())
    return hashlib.sha256(MAGIC + b"|fates|" + body.encode()).hexdigest()


def generate():
    off, on = distribution(False), distribution(True)
    imp = impossible_distribution()
    rows = ["# URDRVXS1 conditioned fate census — emitted by voxfate.generate(), committed as an",
            "# artifact, re-derived by the gate.",
            "# world %s" % VR.world_digest(),
            "# THE POPULATION IS CONDITIONED FIRST: only the pixels `voxtie` classifies as %s,"
            % CONDITION,
            "# where the oracle is unchanged at the exact sample, a thousandth of a pixel either",
            "# side in both screen directions, and under six single-axis camera perturbations.",
            "# Every earlier fate distribution in this arc mixed those with event-surface samples",
            "# and edge/corner degeneracies, and a mechanism read off that mixture is a mechanism",
            "# for an average of three unrelated things.",
            "#   fate    <fate> <conditioned> <with-sampling-branch> <impossible>",
            "#   pixel   <frame> <px> <py> <fate> <impossible>",
            "#   digest  <population digest>"]
    for f in FATES:
        rows.append("fate %s %d %d %d" % (f, off[f], on[f], imp[f]))
    for r in fates():
        rows.append("pixel %d %d %d %s %d" % r)
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
        if f[0] == "fate":
            if len(f) != 5 or f[1] not in FATES:
                raise VoxfateError("VOXFATE-REFUSE: a fate row in no declared class")
        elif f[0] == "pixel":
            if len(f) != 6 or f[4] not in FATES:
                raise VoxfateError("VOXFATE-REFUSE: a pixel row in no declared class")
        elif f[0] != "digest":
            raise VoxfateError("VOXFATE-REFUSE: a row of unknown kind %r" % (f[0],))
        rows.append(tuple(f))
    if world is None:
        raise VoxfateError("VOXFATE-REFUSE: the record names no world digest")
    if not rows:
        raise VoxfateError("VOXFATE-REFUSE: the record has no rows")
    return world, rows


def the_record_names_this_world():
    return parse()[0] == VR.world_digest()


def the_record_is_bound_to_the_live_code():
    _w, rows = parse()
    live = distribution(False)
    for r in rows:
        if r[0] == "fate" and int(r[2]) != live[r[1]]:
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
    except VoxfateError:
        return True
    return False


def told():
    off, on = distribution(False), distribution(True)
    imp = impossible_distribution()
    tot = sum(off.values())
    c = minimal_counterexample()
    return ("conditioned on the %d %s pixels — the ones no ambiguity excuses — the fate is %s "
            "%d (%.1f%%), %s; among the %d that award an IMPOSSIBLE face it is %s %d. The defect "
            "is COVERAGE. Leaving voxmicro's sampling branch enabled absorbs %d of them into "
            "`sampling_shift` and the signal disappears, which is why the conditioning comes "
            "first. Minimal counterexample: frame %d pixel %s, the oracle's face RASTERISED and "
            "did not claim the pixel"
            % (tot, CONDITION, dominant(), off[dominant()], 100.0 * off[dominant()] / tot,
               ", ".join("%s %d" % (k, v) for k, v in sorted(off.items())
                         if v and k != dominant()),
               sum(imp.values()), max(imp, key=lambda k: imp[k]), max(imp.values()),
               on["sampling_shift"], c["frame"], c["pixel"]))


def scene_case(name):
    if name == "conditioned":
        return repr((CONDITION, len(conditioned()), distribution(False), distribution(True),
                     impossible_distribution(), dominant(), population_digest()))
    if name == "counterexample":
        return repr(minimal_counterexample())
    raise VoxfateError("VOXFATE-REFUSE: no scene named %r" % name)


def scene_result(name):
    return hashlib.sha256(MAGIC + b"|" + name.encode() + b"|"
                          + scene_case(name).encode()).hexdigest()


SCENES = ("conditioned", "counterexample")


def golden(name):
    with open(os.path.join(_HERE, "conformance_voxfate.txt"), encoding="utf-8") as fh:
        for ln in fh:
            ln = ln.strip()
            if ln and not ln.startswith("#"):
                nm, dig = ln.split()
                if nm == name:
                    return dig
    raise VoxfateError("VOXFATE-REFUSE: no golden named %r" % name)
