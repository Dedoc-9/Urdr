# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""voxproj (URDRVXP1) — THE CANDIDATE LAW, PREDICTED BEFORE IT RAN, AND REFUSED ON EVIDENCE.

The diagnosis closed at `voxwin`: 374 coverage, 2 tie, 2 phantom. `voxslack` split the coverage
class by signed distance — 215 failing by exactly -1, which is the top-left convention, and 103
failing by a real but sub-pixel amount, which is the floored projected vertex. This rung takes the
second of those and proposes ONE change to the coordinate construction:

    control      the committed integer vertex quantisation — floor
    candidate    round-to-nearest, exact, at the same sub-pixel denominator

ONE VARIABLE. No fill-rule change, no convention change, no combination. Floor and round-to-nearest
differ by at most one sub-pixel unit and agree wherever the division is exact, which is what makes
this a single step rather than a different renderer.

THE PREDICTION WAS WRITTEN INTO THIS FILE BEFORE A FRAME WAS RENDERED, and it is pinned as DATA so
it cannot be retrofitted. Five statements, each with a verdict computed separately and each verdict
naming exactly one of them, so no prediction can be quietly dropped from the scoring.

    P1  the sub-pixel misses largely close, MORE THAN HALF            MISS   12 of 103
    P2  the on-surface misses do NOT close                            HIT     0 of 215
    P3  the winner-side misses fall in rough proportion               MISS   5.4% against 11.7%
    P4  no regression: the candidate gains more than it loses         MISS   +23 against -34
    P5  the ties and phantoms are not swallowed                       HIT    both unchanged

TWO HITS AND THREE MISSES, AND THE CANDIDATE IS REFUSED. Net agreement goes 45550 -> 45539: it is
ELEVEN PIXELS WORSE. Impossible faces move 152 -> 151. Twelve of the hundred and three sub-pixel
misses close and thirty-four pixels elsewhere break, and a repair that costs more than it buys is
not a repair however good its motivation.

AND THE MISS IS THE INFORMATIVE PART. Round-to-nearest halves the worst-case quantisation error and
removes its systematic direction, and NINETY-ONE OF THE HUNDRED AND THREE SURVIVE IT. So the
sub-pixel residue is NOT a rounding-direction defect. The vertex being floored rather than rounded
is not what puts those samples on the wrong side of the edge; something else about the coordinate
construction is, and this rung has eliminated the most obvious candidate for it by measurement
rather than by argument.

P2 IS THE HIT WORTH KEEPING. Not one of the 215 on-surface misses closed — exactly as predicted,
because they fail by the top-left convention and not by quantisation at all. A candidate that had
closed them would have been evidence the mechanism reading was wrong, and it did not.

does_not_show: anything about performance. THAT MORE PRECISION WOULD HELP — a finer sub-pixel
denominator is a DIFFERENT single variable and running it here would have made this two, so it is
named as the next rung and not attempted. Any mechanism for the surviving 91. And nothing is
adopted: `voxref` and `voxray` are untouched, the candidate is not promoted, the two ties are not
used to tune anything, and the two phantoms stay red rather than being folded into a carve-out.

falsifier: `every_prediction_has_a_verdict` requires all five declared predictions to be scored, so
a rung cannot report its hits and lose its misses; and `the_candidate_is_refused_on_evidence`
asserts the refusal AS THE MEASUREMENT — it reddens on the day the candidate starts winning, which
is the day this rung must be reopened rather than quietly kept.
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
import voxslack as VK                                        # noqa: E402
import voxwin as VW                                          # noqa: E402

MAGIC = b"URDRVXP1"

#: DECLARED — the two arms. `control` is the committed floor and is REQUIRED to reproduce
#: `voxtie.render_level` at BEST exactly; `candidate` moves the rounding and nothing else.
ARMS = ("control", "candidate")

#: DECLARED BEFORE THE ARM RAN, and pinned as DATA so it cannot be retrofitted. Each entry is a
#: prediction about what the candidate quantisation will do, written from the mechanism `voxslack`
#: and `voxwin` established and committed to this file before a single frame was rendered.
PREDICTION = (
    ("P1", "the 103 sub-pixel `outside` coverage misses largely close — MORE THAN HALF of them — "
           "because they fail by about one quantisation unit and round-to-nearest halves the "
           "worst-case error while removing its systematic direction"),
    ("P2", "the 215 on-surface misses DO NOT close, because they fail by exactly -1 through the "
           "top-left convention and not through quantisation at all; a candidate that closed them "
           "would be evidence the mechanism reading is wrong"),
    ("P3", "the 56 one-pixel-over winners fall in rough proportion to the coverage misses that "
           "close, because `voxwin` showed them to be the same displacement from the other side"),
    ("P4", "no regression: over the whole framebuffer the candidate gains more agreement than it "
           "loses"),
    ("P5", "the 2 exact ties and the 2 phantoms remain separately classified and are NOT closed by "
           "this arm, because neither is a quantisation defect and a candidate that swallowed them "
           "would be claiming success on populations it did not address"),
)

#: DECLARED — the populations this rung scores against, each inherited from the rung that owns it.
POPULATIONS = ("on_surface", "sub_pixel", "winner_miss", "tie", "phantom")


class VoxprojError(Exception):
    """VOXPROJ-REFUSE — an arm, a population or a record this module will not pretend to read."""


def _level():
    return VT.level(VT.BEST)


# ---- the one variable ---------------------------------------------------------------------------------
def project(arm, c, S):
    """The projected vertex in sub-pixel units. THE ONLY DIFFERENCE BETWEEN THE ARMS.

    `control` floors, which is what the reference commits. `candidate` rounds to nearest, by exact
    integer arithmetic — `(2n + d) // (2d)` with the depth `d` strictly positive past the near
    plane, so no float is constructed and no tie-breaking rule is smuggled in beyond `half up`.
    """
    if arm not in ARMS:
        raise VoxprojError("VOXPROJ-REFUSE: no arm named %r" % (arm,))
    cx, cy = VR.W // 2, VR.H // 2
    nx = cx * S * c[1] + c[0] * VR.FOCAL * S
    ny = cy * S * c[1] - c[2] * VR.FOCAL * S
    d = c[1]
    if arm == "control":
        return nx // d, ny // d
    return (2 * nx + d) // (2 * d), (2 * ny + d) // (2 * d)


def the_quantisation_is_the_only_variable():
    """VALIDITY OF THE SINGLE STEP. The two arms must differ by AT MOST ONE sub-pixel unit and must
    AGREE wherever the division is exact — otherwise `round instead of floor` would be a different
    renderer rather than one variable moved. Checked on constructed camera points, both directions,
    rather than argued from the formula."""
    _n, _sym, S = _level()
    for cr in (-97, -1, 0, 1, 313):
        for cu in (-71, 0, 5, 257):
            for cf in (VR.NEAR, 129, 1000, 4097):
                a = project("control", (cr, cf, cu), S)
                b = project("candidate", (cr, cf, cu), S)
                if abs(a[0] - b[0]) > 1 or abs(a[1] - b[1]) > 1:
                    return False
    exact = (0, 1, 0)
    return project("control", exact, S) == project("candidate", exact, S)


# ---- the arms -----------------------------------------------------------------------------------------
def render_arm(arm, prims, eye, fwd):
    """The committed loop with the projection's rounding as the single parameter."""
    _n, _sym, S = _level()
    m = VR.basis(fwd)
    dep = [None] * (VR.W * VR.H)
    key = [-1] * (VR.W * VR.H)
    for pk, _col, quad in prims:
        cam = [VR._project(v, eye, m) for v in quad]
        if any(c[1] < VR.NEAR for c in cam):
            continue
        scr = [project(arm, c, S) + (c[1],) for c in cam]
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


def the_control_arm_matches_the_ladder():
    """The control must BE the committed renderer, or the candidate is measured against a stranger."""
    _n, sym, S = _level()
    prims = VX.primitives_with("reversed")
    for _nm, eye, fwd in VR.TRACE:
        if render_arm("control", prims, eye, fwd) != VT.render_level(prims, eye, fwd, sym, S):
            return False
    return True


# ---- the populations, inherited ------------------------------------------------------------------------
def population(name):
    """The pixels of one declared population, from the rung that classified them."""
    if name not in POPULATIONS:
        raise VoxprojError("VOXPROJ-REFUSE: no population named %r" % (name,))
    if name == "on_surface":
        return {(r[0], r[1], r[2]) for r in VK.census() if r[9] == "on_surface"}
    if name == "sub_pixel":
        return {(r[0], r[1], r[2]) for r in VK.census() if r[9] == "within_one_pixel"}
    if name == "phantom":
        return {(r[0], r[1], r[2]) for r in VK.census() if r[3] == "phantom"}
    kind = "ray_misses_winner" if name == "winner_miss" else "true_tie"
    return {(r[0], r[1], r[2]) for r in VW.census() if r[3] == kind}


_READING = {}


def reading(arm):
    """(agree, impossible, gained, lost, changed, {population: closed})."""
    if arm not in ARMS:
        raise VoxprojError("VOXPROJ-REFUSE: no arm named %r" % (arm,))
    k = (VR.world_digest(), arm)
    if k in _READING:
        return _READING[k]
    prims = VX.primitives_with("reversed")
    pops = {p: population(p) for p in POPULATIONS}
    agree = imposs = gained = lost = changed = 0
    closed = dict.fromkeys(POPULATIONS, 0)
    for f, (_nm, eye, fwd) in enumerate(VR.TRACE):
        key = render_arm(arm, prims, eye, fwd)
        base = key if arm == "control" else render_arm("control", prims, eye, fwd)
        ora = VM.oracle_frame(eye, fwd, VR.solid, VC.ORIGIN)
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
            if now:
                px, py = i % VR.W, i // VR.W
                for p in POPULATIONS:
                    if (f, px, py) in pops[p]:
                        closed[p] += 1
    _READING[k] = (agree, imposs, gained, lost, changed, closed)
    return _READING[k]


# ---- the verdicts -------------------------------------------------------------------------------------
def verdicts():
    """{prediction id: (hit, what was measured)} — one entry per DECLARED prediction, computed from
    the arm and never from the prediction's own text."""
    c = reading("candidate")
    closed, pops = c[5], {p: len(population(p)) for p in POPULATIONS}
    sub, on = closed["sub_pixel"], closed["on_surface"]
    win = closed["winner_miss"]
    out = {}
    out["P1"] = (sub * 2 > pops["sub_pixel"], "%d of %d sub-pixel misses closed" % (sub, pops["sub_pixel"]))
    out["P2"] = (on == 0, "%d of %d on-surface misses closed" % (on, pops["on_surface"]))
    lo = sub * pops["winner_miss"]
    hi = win * pops["sub_pixel"]
    out["P3"] = (bool(lo) and bool(hi) and lo <= 2 * hi and hi <= 2 * lo,
                 "%d of %d winner-side against %d of %d coverage"
                 % (win, pops["winner_miss"], sub, pops["sub_pixel"]))
    out["P4"] = (c[2] > c[3], "+%d gained against -%d lost" % (c[2], c[3]))
    out["P5"] = (closed["tie"] == 0 and closed["phantom"] == 0,
                 "%d ties and %d phantoms closed" % (closed["tie"], closed["phantom"]))
    return out


def every_prediction_has_a_verdict():
    """THE ANTI-CHERRY-PICK LAW. Every declared prediction must be scored, so a rung cannot report
    its hits and lose its misses somewhere between the measurement and the record."""
    v = verdicts()
    return sorted(v) == sorted(p for p, _t in PREDICTION) and len(v) == len(PREDICTION)


def hits():
    return tuple(sorted(p for p, (ok, _w) in verdicts().items() if ok))


def misses():
    return tuple(sorted(p for p, (ok, _w) in verdicts().items() if not ok))


def the_prediction_was_mostly_wrong_and_that_is_recorded():
    """THE MISSES ARE THE RESULT, NOT AN EMBARRASSMENT TO BE TRIMMED. Three of five predictions
    failed, and the law asserts that the record carries misses at all — a rung whose every
    prediction landed would either be lucky or would have written its predictions after the fact."""
    return len(misses()) > 0 and len(hits()) > 0


def the_candidate_is_refused_on_evidence():
    """THE HEADLINE, ASSERTED AS THE MEASUREMENT. The candidate is not adopted because it is WORSE:
    it gains less than it loses and net agreement falls. This law REDDENS ON THE DAY THE CANDIDATE
    STARTS WINNING, which is the day this rung must be reopened rather than quietly kept."""
    ctl, can = reading("control"), reading("candidate")
    return can[0] < ctl[0] and can[3] > can[2]


def the_mechanism_reading_survives():
    """P2 IS THE HIT WORTH KEEPING. Not one on-surface miss closed, exactly as predicted, because
    they fail by the top-left convention and not by quantisation. A candidate that had closed them
    would have been evidence the mechanism reading was wrong."""
    return verdicts()["P2"][0] and reading("candidate")[5]["on_surface"] == 0


def the_rounding_direction_is_eliminated():
    """AND THE MISS IS THE INFORMATIVE PART. Round-to-nearest halves the worst-case quantisation
    error and removes its systematic direction, and most of the sub-pixel residue SURVIVES it — so
    the residue is not a rounding-direction defect, and the most obvious candidate for it is
    eliminated by measurement rather than by argument."""
    c = reading("candidate")
    return c[5]["sub_pixel"] * 2 < len(population("sub_pixel"))


def the_declared_populations_are_not_swallowed():
    """The 2 ties and the 2 phantoms are untouched by this arm. A candidate that closed them would
    be claiming success on populations it did not address."""
    c = reading("candidate")
    return c[5]["tie"] == 0 and c[5]["phantom"] == 0 and len(population("tie")) > 0


def nothing_is_adopted():
    """`voxref` and `voxray` are untouched, the candidate is not promoted, the ties are not used to
    tune anything, and the phantoms stay red."""
    return VC.the_committed_reference_is_untouched() and VW.nothing_is_altered()


# ---- the record ---------------------------------------------------------------------------------------
RECORD = os.path.join("spec", "attest", "voxref-projection.txt")


def population_digest():
    body = "\n".join("%s %s %s" % (p, v[0], v[1]) for p, v in sorted(verdicts().items()))
    body += "\n" + "\n".join("%s %d %d %d %d %d" % ((a,) + reading(a)[:5]) for a in ARMS)
    return hashlib.sha256(MAGIC + b"|proj|" + body.encode()).hexdigest()


def generate():
    rows = ["# URDRVXP1 projection candidate — emitted by voxproj.generate(), committed as an",
            "# artifact, re-derived by the gate.",
            "# world %s" % VR.world_digest(),
            "# ONE VARIABLE: the projected vertex is FLOORED in the control and ROUNDED TO NEAREST",
            "# in the candidate, by exact integer arithmetic, at the same sub-pixel denominator.",
            "# THE PREDICTION WAS WRITTEN INTO THE MODULE BEFORE A FRAME WAS RENDERED and is pinned",
            "# as data. Two of its five statements hit and three missed, and THE CANDIDATE IS",
            "# REFUSED: net agreement falls by eleven pixels.",
            "#   predict <id> <text>",
            "#   verdict <id> <HIT|MISS> <what was measured>",
            "#   arm     <arm> <agree> <impossible> <gained> <lost> <changed>",
            "#   closed  <arm> <population> <count>",
            "#   digest  <population digest>"]
    for pid, text in PREDICTION:
        rows.append("predict %s %s" % (pid, text))
    for pid, (ok, what) in sorted(verdicts().items()):
        rows.append("verdict %s %s %s" % (pid, "HIT" if ok else "MISS", what))
    for a in ARMS:
        rows.append("arm %s %d %d %d %d %d" % ((a,) + reading(a)[:5]))
        for p in POPULATIONS:
            rows.append("closed %s %s %d" % (a, p, reading(a)[5][p]))
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
            raise VoxprojError("VOXPROJ-REFUSE: a predict row naming no declared prediction")
        if f[0] == "verdict" and (len(f) < 4 or f[1] not in ids or f[2] not in ("HIT", "MISS")):
            raise VoxprojError("VOXPROJ-REFUSE: a verdict row naming no declared prediction")
        if f[0] == "arm" and (len(f) != 7 or f[1] not in ARMS):
            raise VoxprojError("VOXPROJ-REFUSE: an arm row naming no declared arm")
        if f[0] == "closed" and (len(f) != 4 or f[1] not in ARMS or f[2] not in POPULATIONS):
            raise VoxprojError("VOXPROJ-REFUSE: a closed row naming no declared population")
        if f[0] not in ("predict", "verdict", "arm", "closed", "digest"):
            raise VoxprojError("VOXPROJ-REFUSE: a row of unknown kind %r" % (f[0],))
        rows.append(tuple(f))
    if world is None:
        raise VoxprojError("VOXPROJ-REFUSE: the record names no world digest")
    if not rows:
        raise VoxprojError("VOXPROJ-REFUSE: the record has no rows")
    return world, rows


def the_record_names_this_world():
    return parse()[0] == VR.world_digest()


def the_record_is_bound_to_the_live_code():
    _w, rows = parse()
    v = verdicts()
    for r in rows:
        if r[0] == "verdict" and (r[2] == "HIT") != v[r[1]][0]:
            return False
        if r[0] == "arm" and tuple(int(x) for x in r[2:]) != reading(r[1])[:5]:
            return False
        if r[0] == "closed" and int(r[3]) != reading(r[1])[5][r[2]]:
            return False
    pinned = next(r[1] for r in rows if r[0] == "digest")
    return pinned == population_digest()


def the_record_carries_the_prediction_text():
    """The prediction is in the RECORD, not only in the code, so the committed artifact carries what
    was claimed as well as what was measured."""
    _w, rows = parse()
    said = {r[1] for r in rows if r[0] == "predict"}
    return said == {p for p, _t in PREDICTION}


def a_tampered_row_refuses():
    text = _read()
    for ln in text.split("\n"):
        if ln.startswith("verdict "):
            f = ln.split()
            f[2] = "MAYBE"
            text = text.replace(ln, " ".join(f), 1)
            break
    try:
        parse(text)
    except VoxprojError:
        return True
    return False


def told():
    ctl, can = reading("control"), reading("candidate")
    v = verdicts()
    return ("the prediction was written into the module before a frame was rendered, and %d of its "
            "%d statements HIT while %d MISSED: %s. THE CANDIDATE IS REFUSED — agreement %d against "
            "the control's %d, which is %d pixels WORSE, from +%d gained against -%d lost, with "
            "impossible faces %d against %d. AND THE MISS IS THE INFORMATIVE PART: round-to-nearest "
            "halves the worst-case quantisation error and removes its systematic direction, and %d "
            "of the %d sub-pixel misses SURVIVE it, so the residue is not a rounding-direction "
            "defect. P2 is the hit worth keeping — not one of the %d on-surface misses closed, "
            "exactly as predicted, because they fail by the top-left convention and not by "
            "quantisation at all"
            % (len(hits()), len(PREDICTION), len(misses()),
               ", ".join("%s %s (%s)" % (p, "HIT" if v[p][0] else "MISS", v[p][1])
                         for p in sorted(v)),
               can[0], ctl[0], ctl[0] - can[0], can[2], can[3], can[1], ctl[1],
               len(population("sub_pixel")) - can[5]["sub_pixel"], len(population("sub_pixel")),
               len(population("on_surface"))))


def scene_case(name):
    if name == "arms":
        return repr(tuple((a,) + reading(a)[:5] + (tuple(sorted(reading(a)[5].items())),)
                          for a in ARMS))
    if name == "verdicts":
        return repr(sorted(verdicts().items()))
    raise VoxprojError("VOXPROJ-REFUSE: no scene named %r" % name)


def scene_result(name):
    return hashlib.sha256(MAGIC + b"|" + name.encode() + b"|"
                          + scene_case(name).encode()).hexdigest()


SCENES = ("arms", "verdicts")


def golden(name):
    with open(os.path.join(_HERE, "conformance_voxproj.txt"), encoding="utf-8") as fh:
        for ln in fh:
            ln = ln.strip()
            if ln and not ln.startswith("#"):
                nm, dig = ln.split()
                if nm == name:
                    return dig
    raise VoxprojError("VOXPROJ-REFUSE: no golden named %r" % name)
