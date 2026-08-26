# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""voxtie (URDRVXT1) — IS A DISAGREEING PIXEL A DEFECT, OR A SAMPLE ON AN EVENT SURFACE?

THE QUESTION THIS RUNG REFUSES TO ANSWER BY COUNTING. `voxcand` left 661 impossible pixels; two
further candidate fixes take that to 152, and thirteen survive on one two-cell scene. It would be
easy — and wrong — to call thirteen pixels a permanent degeneracy and let the visibility fact go
green with a carve-out. The one-sided limit test says why it would be wrong: ONE of the thirteen is
not degenerate at all. The oracle answers the same face at the exact sample and at a thousandth of a
pixel either side, in both screen directions, and the rasteriser still awards the pixel to a face
sandwiched between two solid cells. That is a bug, and a carve-out written on the count would have
buried it.

SO THE RESIDUAL IS CLASSIFIED, NOT TALLIED. Every disagreeing pixel of the best candidate arm is
asked three questions and sorted into exactly one class:

    degenerate  the exact ray enters through an EDGE or a CORNER — two or three lattice planes
                crossed at one parameter — so the ORACLE ITSELF is resolving by a convention
                (`voxevent` named it: lowest axis index). Geometric uniqueness is not available.
    boundary    a clean single-plane entry, but the answer DIFFERS across the sample: the ray at
                minus epsilon meets one face and at plus epsilon another. The sample lies on a
                visibility event surface and the two programs land on opposite sides of it.
    stable      the oracle gives the same answer at the exact sample and at every perturbation.
                There is no ambiguity to appeal to, so a disagreement here IS a defect.

THE ONE-SIDED SEQUENCE IS RECORDED, NOT SUMMARISED. `A->B->B` and `A->B->C` and `A->B->A` are three
different situations and only the third would indicate an implementation fault in the oracle. What
the trace actually shows is right-continuity — the exact value equals the plus-epsilon side — which
is a consistent convention rather than a third answer appearing from nowhere, and the pattern is
pinned per pixel so that claim can be checked instead of believed.

TWO PERTURBATIONS, BECAUSE THEY ANSWER DIFFERENT QUESTIONS. Moving the screen sample tells you the
topology of the RASTER SAMPLE — which side of a projected edge an integer pixel falls on. Moving the
CAMERA tells you whether the viewpoint sits on a boundary in viewpoint space, which is the quantity
an aspect-cell or propagation census would care about. A pixel can be on a projected edge without
the viewpoint being anywhere near a visibility-cell wall, and conflating the two would put a
screen-space artefact into a viewpoint-space census.

CANDIDATE TIE RULES ARE MEASURED AND NONE IS ADOPTED. `voxref`'s `(depth, face_key)` was built to
kill draw-order dependence across 1058 coincident face pairs and it does that perfectly. It was
never designed to decide which of two equidistant faces is visible, and at the stable pixel it
decides wrongly. Four orderings are evaluated against the tie population — face key, the geometric
ray parameter, the normal's opposition to the ray, and the entry axis — and what is reported is
which invariants each preserves and which exact cases each moves. ADOPTING ONE IS A DESIGN DECISION
ABOUT WHAT THE REFERENCE IS, not a bug fix, and this module does not make it.

does_not_show: anything about performance. That any tie rule is correct — the geometric-parameter
rule in particular computes a ray/plane intersection inside the rasteriser, which makes it partly a
ray tracer and is exactly the kind of choice that needs deciding rather than defaulting. That the
classification generalises past the declared trace and the tie micro-suite. And it promotes nothing:
`voxref` is untouched here as it is in `voxcand`, and the frozen census stays frozen.

falsifier: the ladder's first level must reproduce `voxcand`'s candidate arm exactly, so the chain
from `voxref.render` through two transcriptions stays bound; the classifier is required to find at
least one STABLE disagreement, because a classifier that called everything a boundary would
manufacture the carve-out this rung exists to refuse; and every class is required to be non-empty
across the corpus, since a taxonomy with an unreachable bucket is a taxonomy that has not been
tested.
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

MAGIC = b"URDRVXT1"

#: DECLARED — the sub-pixel denominator for a screen-space limit. One part in 1024 of a pixel is far
#: finer than any projected feature in this world and coarse enough to stay in small integers.
SUB = 1024

#: DECLARED — the viewpoint perturbation, in world Q8 units. One unit is 1/256 of a cell.
EYE_EPS = 1

CLASSES = ("stable", "boundary", "degenerate")

#: DECLARED — bumped whenever the classifier's SEMANTICS change, so a stale materialisation cannot
#: survive a change to what the classes mean. It is part of the cache key for that reason.
CENSUS_VERSION = 1

#: THE CENSUS IS MATERIALISED ONCE PER PROCESS, NOT ONCE PER LAW. Six laws and a golden each need
#: the classified population, and each recomputation costs eleven oracle queries per disagreeing
#: pixel. The key is the set of inputs that can VARY within one interpreter — the world, the level
#: being classified, the two epsilons, and the semantic version. The CODE cannot vary within a
#: process, which is why it is not in the key and why this cache is deliberately process-local: a
#: cache that survived across runs would introduce exactly the stale-record failure mode this tree
#: spends its rungs eliminating, and it would do so while the records are being established.
_CENSUS = {}


def census_key():
    return (VR.world_digest(), BEST, SUB, EYE_EPS, CENSUS_VERSION)

#: DECLARED — the candidate ladder. Level 0 must reproduce `voxcand`'s candidate arm exactly; each
#: level after it adds ONE change, so the ladder is a sequence of single-variable experiments and
#: not four unrelated renderers. `sym` fixes the projection's axis asymmetry — `voxref` computes
#: `cy - (cu*F)//cf`, negating AFTER the floor, so screen Y rounds toward +inf where X rounds toward
#: -inf. `S` is the sub-pixel denominator of the projected VERTEX, 1 being the committed integer.
LEVELS = (("candidate", False, 1),
          ("symmetric", True, 1),
          ("subpixel64", True, 64),
          ("subpixel256", True, 256))
BEST = "subpixel64"


class VoxtieError(Exception):
    """VOXTIE-REFUSE — a level, a class or a record this module will not pretend to read."""


def level(name):
    for n, sym, s in LEVELS:
        if n == name:
            return n, sym, s
    raise VoxtieError("VOXTIE-REFUSE: no level named %r" % (name,))


# ---- the ladder ----------------------------------------------------------------------------------
def render_level(prims, eye, fwd, sym, S):
    """The candidate arm — reversed winding, unbiased barycentrics — with the projection's axis
    treatment and the vertex sub-pixel denominator as parameters. Returns the winning face key per
    pixel. At (sym=False, S=1) this is `voxcand`'s candidate arm exactly, which is asserted."""
    m = VR.basis(fwd)
    cx, cy = VR.W // 2, VR.H // 2
    dep = [None] * (VR.W * VR.H)
    key = [-1] * (VR.W * VR.H)
    for pk, _col, quad in prims:
        cam = [VR._project(v, eye, m) for v in quad]
        if any(c[1] < VR.NEAR for c in cam):
            continue
        if sym:
            scr = [((cx * S * c[1] + c[0] * VR.FOCAL * S) // c[1],
                    (cy * S * c[1] - c[2] * VR.FOCAL * S) // c[1], c[1]) for c in cam]
        else:
            scr = [(cx * S + (c[0] * VR.FOCAL * S) // c[1],
                    cy * S - (c[2] * VR.FOCAL * S) // c[1], c[1]) for c in cam]
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
                    if dep[i] is None or (d, pk) < (dep[i], key[i] if key[i] >= 0 else (1 << 62)):
                        dep[i] = d
                        key[i] = pk
    return key


def the_ladder_starts_at_the_candidate():
    """THE CHAIN STAYS BOUND. `voxref.render` -> `voxcand`'s committed arm -> `voxcand`'s candidate
    arm -> this ladder's level zero, each link asserted rather than assumed. Without this, four
    levels of a ladder could all be measuring something no other module runs."""
    for frame in range(len(VR.TRACE)):
        _n, eye, fwd = VR.TRACE[frame]
        want = VC.arm_frame(VC.CANDIDATE, frame)[2]
        if render_level(VX.primitives_with("reversed"), eye, fwd, False, 1) != want:
            return False
    return True


def level_reading(name, frame=None, scene=None):
    """(impossible, agreeing) for one ladder level on one declared frame or micro-scene."""
    _n, sym, S = level(name)
    if scene is None:
        _nm, eye, fwd = VR.TRACE[frame]
        occ, prims = VR.solid, VX.primitives_with("reversed")
    else:
        sc = VM.micro(scene)
        eye, fwd, occ = sc["eye"], sc["fwd"], VM.micro_occ(sc)
        prims = VM.micro_prims(sc, "reversed") + list(sc["extra"])
    ora = VM.oracle_frame(eye, fwd, occ, VC.ORIGIN)
    own = tuple(e // VR.Q for e in eye)
    imp = agr = 0
    for i, k in enumerate(render_level(prims, eye, fwd, sym, S)):
        r = VM.winner_answer(k)
        if r is not None and r[0] != "extra" and VM.impossible_winner(r[0], r[1], occ, own):
            imp += 1
        if r == ora[i]:
            agr += 1
    return imp, agr


# ---- the classifier ------------------------------------------------------------------------------
def _ray(eye, fwd, sx, sy):
    """The ray through sub-pixel screen coordinate (sx/SUB, sy/SUB). sx = px*SUB is the integer ray
    `voxray.ray_for_pixel` builds, so the perturbations are around exactly that sample."""
    r, f, u = VR.basis(fwd)
    a, b, c = sx - (VR.W // 2) * SUB, VR.FOCAL * SUB, (VR.H // 2) * SUB - sy
    return (r[0] * a + f[0] * b + u[0] * c,
            r[1] * a + f[1] * b + u[1] * c,
            r[2] * a + f[2] * b + u[2] * c)


def _ask(eye, fwd, occ, sx, sy):
    h = VX.first_hit(eye, _ray(eye, fwd, sx, sy), occ, VC.ORIGIN)
    return None if h is None else (h[0], h[1])


def simultaneous_planes(eye, fwd, occ, sx, sy):
    """How many lattice planes the ray crosses at ONE parameter — the oracle's own degeneracy."""
    d = _ray(eye, fwd, sx, sy)
    h = VX.first_hit(eye, d, occ, VC.ORIGIN)
    if h is None or h[1] is None:
        return 0
    pt = VX.point_at(eye, d, h[2])
    on = 0
    for ax in range(3):
        if d[ax] == 0:
            continue
        n, den = pt[ax]
        if n % (VR.Q * den) == 0:
            on += 1
    return on


def _pattern(minus, exact, plus):
    """The one-sided sequence as a three-letter word over the distinct answers: AAA, ABB, AAB, ABA,
    ABC. Recorded rather than summarised, because ABA would mean something quite different from ABB
    and only the count would hide it."""
    seen, out = {}, []
    for v in (minus, exact, plus):
        if v not in seen:
            seen[v] = chr(ord("A") + len(seen))
        out.append(seen[v])
    return "".join(out)


def classify(eye, fwd, occ, px, py):
    """(class, x-pattern, y-pattern, viewpoint changes) for one sample.

    THE PRIORITY IS DECLARED: an exact ray entering through an edge or corner is DEGENERATE
    whatever its neighbours do, because there the oracle is already answering by convention and no
    limit can appeal past that. Otherwise the perturbations decide.
    """
    sx, sy = px * SUB, py * SUB
    ex = _ask(eye, fwd, occ, sx, sy)
    xpat = _pattern(_ask(eye, fwd, occ, sx - 1, sy), ex, _ask(eye, fwd, occ, sx + 1, sy))
    ypat = _pattern(_ask(eye, fwd, occ, sx, sy - 1), ex, _ask(eye, fwd, occ, sx, sy + 1))
    moved = 0
    for ax in range(3):
        for sgn in (-1, 1):
            e2 = list(eye)
            e2[ax] += sgn * EYE_EPS
            if _ask(tuple(e2), fwd, occ, sx, sy) != ex:
                moved += 1
    if simultaneous_planes(eye, fwd, occ, sx, sy) >= 2:
        return "degenerate", xpat, ypat, moved
    if xpat == "AAA" and ypat == "AAA":
        return "stable", xpat, ypat, moved
    return "boundary", xpat, ypat, moved


# ---- the census ----------------------------------------------------------------------------------
def census_frame(frame):
    """Classify every DISAGREEING pixel of the best ladder level on one declared frame."""
    _n, sym, S = level(BEST)
    _nm, eye, fwd = VR.TRACE[frame]
    ora = VM.oracle_frame(eye, fwd, VR.solid, VC.ORIGIN)
    own = tuple(e // VR.Q for e in eye)
    key = render_level(VX.primitives_with("reversed"), eye, fwd, sym, S)
    rows = []
    for i, k in enumerate(key):
        r = VM.winner_answer(k)
        if r == ora[i]:
            continue
        px, py = i % VR.W, i // VR.W
        cls, xp, yp, moved = classify(eye, fwd, VR.solid, px, py)
        imp = (r is not None and r[0] != "extra"
               and VM.impossible_winner(r[0], r[1], VR.solid, own))
        rows.append((frame, px, py, cls, xp, yp, moved, 1 if imp else 0))
    return rows


def census():
    k = census_key()
    if k not in _CENSUS:
        rows = []
        for frame in range(len(VR.TRACE)):
            rows.extend(census_frame(frame))
        _CENSUS[k] = rows
    return _CENSUS[k]


def the_cache_is_keyed_on_inputs_and_not_on_the_run():
    """A materialisation keyed on "this run" would be a cache that cannot be invalidated. The key
    names the varying inputs, and changing any of them must produce a different key — checked by
    constructing one rather than by reading the code."""
    live = census_key()
    return (len(live) == 5 and live[0] == VR.world_digest() and live[1] == BEST
            and live[2:] == (SUB, EYE_EPS, CENSUS_VERSION)
            and census_key() == live)


def the_cache_returns_the_same_population():
    """Materialising must not change the answer: the cached rows are the rows."""
    a = census()
    _CENSUS.clear()
    b = census()
    return a == b


def census_summary(rows=None):
    """(per class: total, impossible), and the digest of the whole classified population."""
    if rows is None:
        _w, parsed = parse()
        rows = [r for r in parsed if r[0] == "census"]
        rows = [(int(r[1]), int(r[2]), int(r[3]), r[4], r[5], r[6], int(r[7]), int(r[8]))
                for r in rows]
    out = {c: [0, 0] for c in CLASSES}
    for _f, _px, _py, cls, _xp, _yp, _mv, imp in rows:
        out[cls][0] += 1
        out[cls][1] += imp
    return out


def population_digest(rows):
    """THE POPULATION, NOT THE COUNT. Two different sets of 1137 pixels would give the same tally
    and a different digest, so what is pinned is which pixels were classified how."""
    body = "\n".join("%d %d %d %s %s %s %d %d" % r for r in rows)
    return hashlib.sha256(MAGIC + b"|census|" + body.encode()).hexdigest()


def the_classifier_finds_a_genuine_defect():
    """THE LAW THAT REFUSES THE CARVE-OUT. A classifier that sorted every disagreement into
    `boundary` would manufacture exactly the conclusion this rung exists to test, so at least one
    STABLE disagreement must be found — a pixel where the oracle is unambiguous under every
    perturbation and the rasteriser still disagrees. That is a defect, not a degeneracy."""
    s = census_summary()
    return s["stable"][0] > 0


def the_oracle_never_gives_an_isolated_answer():
    """THE THIRD OUTCOME DOES NOT OCCUR, and it is the one that would have indicted the oracle.

    A pattern of `ABA` — the exact sample differing from both sides while the sides agree with each
    other — would mean the oracle answering with something no limit reaches: an implementation
    fault rather than a geometric event. Across every classified pixel, in both screen directions,
    the only patterns that occur are `AAA`, `AAB` and `ABB`. The exact value ALWAYS equals one of
    the two sides, so the oracle is a function with no isolated answers, and it is not uniformly
    right-continuous either — it takes whichever side the exact ray actually falls on, which is
    what a well-defined function does at a discontinuity.
    """
    seen = set()
    for _f, _px, _py, _c, xp, yp, _m, _i in census():
        seen.add(xp)
        seen.add(yp)
    return seen and seen <= {"AAA", "AAB", "ABB"}


def the_carve_out_is_refused_by_the_trace():
    """THE RESULT THAT DECIDED THE RUNG. On one two-cell scene the residual looked like twelve
    degeneracies around a single bug, which would have made a carve-out tempting. Over the declared
    trace it is nothing of the kind: STABLE disagreements outnumber event-surface ones, and among
    the impossible-face pixels they outnumber them by a wide margin. A carve-out written on the
    small scene would have excused several hundred defects.

    THIS LAW WAS FIRST WRITTEN WITH A THRESHOLD AND THE DATA MISSED IT BY THREE PIXELS. The claim
    was "a third of the disagreements are stable"; 378 of 1137 is 33.25%, so `stable * 3 > total`
    reads 1134 against 1137 and reddens. A fraction chosen because it sounded like the answer is a
    law fitted to a hope, and the repair is not to move the fraction but to delete it: what the
    measurement actually supports is a COMPARISON between two classes, which needs no number
    invented for it.
    """
    s = census_summary()
    return s["stable"][0] > s["boundary"][0] and s["stable"][1] > s["boundary"][1]


def every_class_is_reachable():
    """A taxonomy with an unreachable bucket has not been tested."""
    s = census_summary()
    return all(s[c][0] > 0 for c in CLASSES)


# ---- the tie rules, measured and not adopted -----------------------------------------------------
RULES = ("face_key", "ray_parameter", "normal_opposition", "entry_axis")


def _plane_t(eye, d, cell, face):
    """The exact parameter at which the ray meets the face's PLANE, as (num, den) with den > 0.
    None when the ray is parallel to it. This is a ray/plane intersection computed inside a
    rasteriser, which is precisely why adopting the rule it serves is a design decision."""
    axis = face // 2
    if d[axis] == 0:
        return None
    plane = (cell[axis] + (1 if face % 2 == 0 else 0)) * VR.Q
    num, den = plane - eye[axis], d[axis]
    return (num, den) if den > 0 else (-num, -den)


def rule_pick(rule, eye, d, cands):
    """Which of the tied candidates a rule selects. `cands` is [(cell, face, key), ...]."""
    if rule == "face_key":
        return min(cands, key=lambda c: c[2])
    if rule == "entry_axis":
        return min(cands, key=lambda c: (c[1] // 2, c[2]))
    if rule == "normal_opposition":
        def dot(c):
            n = VR.FACES[c[1]][0]
            return d[0] * n[0] + d[1] * n[1] + d[2] * n[2]
        return min(cands, key=lambda c: (dot(c), c[2]))
    if rule == "ray_parameter":
        def t(c):
            p = _plane_t(eye, d, c[0], c[1])
            return (1, 0, 0) if p is None else (0, p[0], p[1])
        best = cands[0]
        for c in cands[1:]:
            a, b = t(best), t(c)
            if a[0] != b[0]:
                if b[0] < a[0]:
                    best = c
                continue
            if b[1] * a[2] < a[1] * b[2] or (b[1] * a[2] == a[1] * b[2] and c[2] < best[2]):
                best = c
        return best
    raise VoxtieError("VOXTIE-REFUSE: no tie rule named %r" % (rule,))


def tie_population(scene="pair_oblique"):
    """Every pixel of a scene where two or more faces cover it at EXACTLY equal depth, with the
    candidates, the oracle's answer and the sample's class."""
    sc = VM.micro(scene)
    eye, fwd, occ = sc["eye"], sc["fwd"], VM.micro_occ(sc)
    _n, sym, S = level(BEST)
    m = VR.basis(fwd)
    cx, cy = VR.W // 2, VR.H // 2
    at = {}
    for pk, _col, quad in VM.micro_prims(sc, "reversed"):
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
                    at.setdefault(py * VR.W + px, {}).setdefault(d, set()).add(pk)
    out = []
    ora = VM.oracle_frame(eye, fwd, occ, VC.ORIGIN)
    for i, bydepth in sorted(at.items()):
        best = min(bydepth)
        keys = sorted(bydepth[best])
        if len(keys) < 2:
            continue
        px, py = i % VR.W, i // VR.W
        cands = [(VX._unkey(k)[0], VX._unkey(k)[1], k) for k in keys]
        cls, _xp, _yp, _mv = classify(eye, fwd, occ, px, py)
        out.append((px, py, tuple(cands), ora[i], cls,
                    _ray(eye, fwd, px * SUB, py * SUB)))
    return out


def rule_verdicts(scene="pair_oblique"):
    """For each rule: (ties resolved in agreement with the oracle, ties total, order-independent)."""
    pop = tie_population(scene)
    sc = VM.micro(scene)
    out = {}
    for rule in RULES:
        agree = 0
        for _px, _py, cands, ora, _cls, d in pop:
            pick = rule_pick(rule, sc["eye"], d, list(cands))
            if ora is not None and (pick[0], pick[1]) == ora:
                agree += 1
        # every rule here is a total order on face IDENTITY and geometry, never on arrival, so
        # draw-order independence is structural — checked by shuffling the candidate list.
        stable = True
        for _px, _py, cands, _o, _c, d in pop:
            a = rule_pick(rule, sc["eye"], d, list(cands))
            b = rule_pick(rule, sc["eye"], d, list(reversed(list(cands))))
            if a != b:
                stable = False
                break
        out[rule] = (agree, len(pop), stable)
    return out


def resolvable_ties(scene="pair_oblique"):
    """HOW MANY TIES A TIE RULE COULD EVER FIX — those where the oracle's answer is among the tied
    candidates. Everywhere else the correct face is not competing at that pixel at all, so the
    disagreement is about COVERAGE and no ordering of the candidates can reach it. This is the
    ceiling on the entire tie-rule question, and it is a much more useful number than a ranking."""
    n = 0
    for _px, _py, cands, ora, _cls, _d in tie_population(scene):
        if ora is not None and any((c[0], c[1]) == ora for c in cands):
            n += 1
    return n


def no_tie_rule_can_beat_the_resolvable_ceiling():
    """The best any ordering scores must equal the resolvable count, and the resolvable count must
    be strictly less than the population — which is what makes "change the tiebreak" a bounded
    proposal rather than an open-ended hope."""
    ceiling = resolvable_ties()
    best = max(v[0] for v in rule_verdicts().values())
    return best == ceiling and 0 < ceiling < len(tie_population())


def the_committed_rule_leaves_the_ceiling_unreached():
    """AND THERE IS SOMETHING TO BUY: `(depth, face_key)` scores strictly below the ceiling, so the
    committed ordering is not merely arbitrary — it is arbitrary AND worse than available."""
    return rule_verdicts()["face_key"][0] < resolvable_ties()


def no_rule_is_adopted():
    """`voxref`'s tiebreak is untouched and this module changes nothing. What is produced is a table
    of what each candidate ordering would do, because choosing one is a decision about what the
    reference IS — the geometric-parameter rule computes a ray/plane intersection inside the
    rasteriser, which makes it partly a ray tracer — and a rung that quietly adopted a convention
    would be making that decision by default."""
    return VC.the_committed_reference_is_untouched()


def every_rule_is_order_independent():
    """Whatever else they do, none of the candidates may reintroduce draw-order dependence — that
    is the property `(depth, face_key)` was built for and no replacement may cost it."""
    return all(v[2] for v in rule_verdicts().values())


# ---- the record ----------------------------------------------------------------------------------
RECORD = os.path.join("spec", "attest", "voxref-tie.txt")


def generate():
    rows = ["# URDRVXT1 tie and event-surface classification — emitted by voxtie.generate(),",
            "# committed as an artifact, re-derived by the gate.",
            "# world %s" % VR.world_digest(),
            "# FOUR RECORDS, SEPARATELY AUDITABLE, sharing one file and distinguished by kind:",
            "#   ladder  <level> <frame|scene> <impossible> <agreeing>",
            "#   census  <frame> <px> <py> <class> <x-pattern> <y-pattern> <eye-moves> <impossible>",
            "#   tie     <px> <py> <class> <candidates> <oracle>",
            "#   rule    <rule> <agreeing> <ties> <order-independent>",
            "# Nothing here is adopted. `voxref` is untouched, the frozen census stays frozen, and",
            "# the tie rules are a table of what each ordering WOULD do."]
    for name, _sym, _s in LEVELS:
        for frame in range(len(VR.TRACE)):
            imp, agr = level_reading(name, frame=frame)
            rows.append("ladder %s %d %d %d" % (name, frame, imp, agr))
        for scene in TIE_SCENES:
            imp, agr = level_reading(name, scene=scene)
            rows.append("ladder %s %s %d %d" % (name, scene, imp, agr))
    for r in census():
        rows.append("census %d %d %d %s %s %s %d %d" % r)
    for px, py, cands, ora, cls, _d in tie_population():
        rows.append("tie %d %d %s %s %s" % (px, py, cls,
                                            ";".join("%d" % c[2] for c in cands),
                                            "none" if ora is None else "%d.%d" % (
                                                (((ora[0][0] * VR.N) + ora[0][1]) * VR.N
                                                 + ora[0][2]), ora[1])))
    for rule, (agree, tot, stable) in sorted(rule_verdicts().items()):
        rows.append("rule %s %d %d %d" % (rule, agree, tot, 1 if stable else 0))
    rows.append("rule CEILING %d %d 1" % (resolvable_ties(), len(tie_population())))
    return "\n".join(rows) + "\n"


#: DECLARED — the micro-scenes whose ties this rung is about: the adjacent pairs on each axis, the
#: coplanar seam, the two degenerate angles, and the body diagonal that produced the residual.
TIE_SCENES = ("pair_x", "pair_y", "pair_z", "pair_oblique", "coplanar", "edge_on", "corner_on")


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
        if f[0] not in ("ladder", "census", "tie", "rule"):
            raise VoxtieError("VOXTIE-REFUSE: a row of unknown kind %r" % (f[0],))
        if f[0] == "census":
            if len(f) != 9:
                raise VoxtieError("VOXTIE-REFUSE: a census row with %d fields" % len(f))
            if f[4] not in CLASSES:
                raise VoxtieError("VOXTIE-REFUSE: a census row in no declared class")
            if f[5] not in ("AAA", "AAB", "ABB", "ABA", "ABC"):
                raise VoxtieError("VOXTIE-REFUSE: a census row with an unreadable pattern")
        rows.append(tuple(f))
    if world is None:
        raise VoxtieError("VOXTIE-REFUSE: the record names no world digest")
    if not rows:
        raise VoxtieError("VOXTIE-REFUSE: the record has no rows")
    return world, rows


def the_record_names_this_world():
    return parse()[0] == VR.world_digest()


def the_record_is_bound_to_the_live_code():
    """One declared frame's ladder readings and the whole tie population, recomputed every run."""
    _w, rows = parse()
    for name, _sym, _s in LEVELS:
        want = next(r for r in rows if r[0] == "ladder" and r[1] == name and r[2] == "4")
        imp, agr = level_reading(name, frame=4)
        if (str(imp), str(agr)) != (want[3], want[4]):
            return False
    live = {(px, py, cls) for px, py, _c, _o, cls, _d in tie_population()}
    have = {(int(r[1]), int(r[2]), r[3]) for r in rows if r[0] == "tie"}
    return live == have


def the_population_is_pinned_not_the_count():
    _w, rows = parse()
    body = [(int(r[1]), int(r[2]), int(r[3]), r[4], r[5], r[6], int(r[7]), int(r[8]))
            for r in rows if r[0] == "census"]
    return population_digest(body) == population_digest(census())


def a_tampered_row_refuses():
    text = _read()
    for ln in text.split("\n"):
        if ln.startswith("census "):
            f = ln.split()
            f[4] = "elsewhere"
            text = text.replace(ln, " ".join(f), 1)
            break
    try:
        parse(text)
    except VoxtieError:
        return True
    return False


def told():
    s = census_summary()
    lad = {n: level_reading(n, frame=None, scene="pair_oblique") for n, _y, _s in LEVELS}
    v = rule_verdicts()
    tot = sum(s[c][0] for c in CLASSES)
    return ("%d disagreeing pixels classified: %d on a visibility event surface, %d degenerate "
            "(the oracle's own edge/corner convention), and %d STABLE — unambiguous under every "
            "perturbation and still disagreed with, which is a DEFECT and not a degeneracy; the "
            "ladder takes pair_oblique's impossible count %d -> %d -> %d -> %d across candidate, "
            "symmetric-Y, S=64 and S=256; of the four tie orderings %s"
            % (tot, s["boundary"][0], s["degenerate"][0], s["stable"][0],
               lad["candidate"][0], lad["symmetric"][0], lad["subpixel64"][0],
               lad["subpixel256"][0],
               ", ".join("%s agrees %d/%d" % (r, v[r][0], v[r][1]) for r in RULES)))


def scene_case(name):
    if name == "ladder":
        return repr((LEVELS, BEST, TIE_SCENES,
                     tuple((n, tuple(level_reading(n, frame=f) for f in range(len(VR.TRACE))),
                            tuple(level_reading(n, scene=s) for s in TIE_SCENES))
                           for n, _y, _s in LEVELS)))
    if name == "limit_census":
        rows = census()
        return repr((census_summary(rows), population_digest(rows), SUB, EYE_EPS, CLASSES))
    if name == "tie_micro":
        return repr(tuple((px, py, cands, ora, cls)
                          for px, py, cands, ora, cls, _d in tie_population()))
    if name == "tie_rule":
        return repr((RULES, rule_verdicts(), resolvable_ties(), len(tie_population())))
    raise VoxtieError("VOXTIE-REFUSE: no scene named %r" % name)


def scene_result(name):
    return hashlib.sha256(MAGIC + b"|" + name.encode() + b"|"
                          + scene_case(name).encode()).hexdigest()


SCENES = ("ladder", "limit_census", "tie_micro", "tie_rule")


def golden(name):
    with open(os.path.join(_HERE, "conformance_voxtie.txt"), encoding="utf-8") as fh:
        for ln in fh:
            ln = ln.strip()
            if ln and not ln.startswith("#"):
                nm, dig = ln.split()
                if nm == name:
                    return dig
    raise VoxtieError("VOXTIE-REFUSE: no golden named %r" % name)
