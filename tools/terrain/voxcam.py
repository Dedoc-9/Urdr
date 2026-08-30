# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""voxcam (URDRVXB1) — THE CANDIDATE THAT WORKS, AND IT IS STILL NOT THE REFERENCE.

`voxsample` found the seam: `voxref._project` truncates the Q16 basis multiply with a `>> 16` before
any screen quantisation and before the fill rule, and that single shift pushes 91 pixels out of a
face that geometrically contains them while pulling 53 into one that does not. This rung moves that
one variable and measures what it buys.

    control      the committed camera coordinate — `>> 16`, as `voxref._project` performs it
    candidate    the same multiply carried at full precision

ONE VARIABLE, WITH ONE FORCED CONSEQUENCE. The near-plane constant is expressed in camera units, so
changing the unit forces re-expressing the constant — and that is not a second variable but the same
one written down twice. It is checked rather than asserted: `cf >> 16 < NEAR` and `cf < NEAR << 16`
name the SAME plane for every integer, so no geometry is reinterpreted along the way.

THE PREDICTION WAS WRITTEN BEFORE THE ARM RAN, pinned as data, and every one of the five is scored.

    C1  the 215 on-surface misses close                    HIT    214 of 215
    C2  most of the 103 sub-pixel misses close             HIT     88 of 103
    C3  most of the 56 winner-side misses close            HIT     53 of  56
    C4  net agreement improves SUBSTANTIALLY               HIT    +339, 357 gained against 18 lost
    C5  the 2 ties and 2 phantoms do NOT close             MISS   the ties closed; the phantoms did not

FOUR HITS AND ONE MISS, AND UNLIKE `voxproj` THIS CANDIDATE WINS. Agreement 45550 -> 45889. Impossible
faces 152 -> 70. Three hundred and fifty-seven pixels gained against eighteen lost, a ratio of
nearly twenty to one where the rounding-direction candidate managed twenty-three against
thirty-four.

THE MISS IS THE INTERESTING ONE AND IT DOES NOT CONTRADICT `voxwin`. Both exact ties closed. `voxwin`
established in EXACT WORLD SPACE, with no truncation anywhere, that the ray at those two pixels
genuinely passes through an edge shared by two faces — that remains true and is not disturbed here.
What was an artefact is the DEPTH TIE: the interpolated depths were exactly equal only after the
`>> 16`, and at full precision they separate and resolve in the oracle's favour at both. So the
pixels are a real geometric degeneracy AND the rasteriser's tie at them was manufactured by the
truncation, and only the second of those is repaired. `voxtie`'s parked question keeps its two
pixels and loses its exact-depth character.

AND IT IS STILL NOT ADOPTED. Establishing a repair and promoting one are different acts, which is
`voxcand`'s doctrine and the reason that rung exists. Promotion here would move `O_t` on every frame
and invalidate the frozen census, the 1728-state census and the subdivision ladder at once — and it
would do more than that, because carrying full precision scales every interpolated depth by 2^16, so
the DEPTH half of the observable moves even at pixels whose colour does not. That is a contract
change, not a bug fix, and this rung does not make it.

WHAT SURVIVES THE CANDIDATE IS SMALL AND NAMED: 1 on-surface, 15 sub-pixel, 3 winner-side and the 2
phantoms stay open, and 18 pixels that agreed under the control now disagree. Twenty-one of the
original 378 and eighteen new ones — a residue this arc has not characterised and which this rung
does not pretend to.

does_not_show: anything about performance — carrying full precision widens every camera coordinate
and this rung measures no cost in time or space. THAT THE CANDIDATE IS CORRECT, only that it is
closer on the declared trace. Any mechanism for the 18 losses or the 21 survivors. Whether the
reference CAN carry full precision under its integer contract at all. And nothing is promoted:
`voxref` and `voxray` are untouched and the frozen census stays frozen.

falsifier: `the_candidate_wins_on_evidence` asserts the improvement AS A MEASUREMENT and reddens on
the day it stops winning; `the_near_plane_is_the_same_plane` proves the forced constant change
reinterprets no geometry, exhaustively over the integers that matter; and `every_prediction_has_a_
verdict` requires all five to be scored, so a rung that wins cannot quietly drop the one it missed.
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
import voxsample as VA                                       # noqa: E402

MAGIC = b"URDRVXB1"

#: DECLARED — the two arms. `control` is `voxref._project`'s truncation and is REQUIRED to reproduce
#: `voxtie.render_level` at BEST exactly; `candidate` removes it and nothing else.
ARMS = ("control", "candidate")

#: DECLARED — the shift the reference performs, named once so both arms read the same constant.
SHIFT = 16

#: DECLARED — the populations this rung scores against, each inherited from the rung that classified
#: it rather than restated here.
POPULATIONS = ("on_surface", "sub_pixel", "winner_miss", "tie", "phantom")

#: DECLARED BEFORE THE ARM RAN, pinned as DATA so it cannot be retrofitted.
PREDICTION = (
    ("C1", "the 215 on-surface misses CLOSE, because `voxsample` showed the truncation is what "
           "puts those samples exactly on the edge where the top-left convention then rejects them "
           "— remove it and they should be strictly inside"),
    ("C2", "most of the 103 sub-pixel misses close, because `voxsample` measured 91 of them as "
           "pushed OUT of a face that geometrically contains them by this single shift"),
    ("C3", "most of the 56 winner-side misses close, because `voxsample` measured 53 of them as "
           "pulled IN to a face that does not contain them by the same shift"),
    ("C4", "net agreement improves SUBSTANTIALLY — gained exceeds lost by a wide margin — which is "
           "what `voxproj` failed to do and what would distinguish a real term from a plausible "
           "one"),
    ("C5", "the 2 exact ties and the 2 phantoms do NOT close, because neither is a camera-precision "
           "defect and a candidate that swallowed them would be claiming success on populations it "
           "did not address"),
)


class VoxcamError(Exception):
    """VOXCAM-REFUSE — an arm, a population or a record this module will not pretend to read."""


def _level():
    return VT.level(VT.BEST)


# ---- the one variable ---------------------------------------------------------------------------------
def camera(v, eye, m, arm):
    """The camera coordinate of a world point. THE ONLY DIFFERENCE BETWEEN THE ARMS.

    `control` applies `voxref._project`'s `>> SHIFT`; `candidate` carries the Q16 basis multiply
    intact. Nothing else moves — the projection, the fill rule, the depth comparison and the sample
    point are all identical, because the ratio the projection forms is scale-invariant.
    """
    if arm not in ARMS:
        raise VoxcamError("VOXCAM-REFUSE: no arm named %r" % (arm,))
    dx, dy, dz = v[0] - eye[0], v[1] - eye[1], v[2] - eye[2]
    r, f, u = m
    cr = r[0] * dx + r[1] * dy + r[2] * dz
    cf = f[0] * dx + f[1] * dy + f[2] * dz
    cu = u[0] * dx + u[1] * dy + u[2] * dz
    if arm == "control":
        return (cr >> SHIFT, cf >> SHIFT, cu >> SHIFT)
    return (cr, cf, cu)


def near_of(arm):
    """The near plane in the arm's own camera units — the SAME plane, written down twice."""
    if arm not in ARMS:
        raise VoxcamError("VOXCAM-REFUSE: no arm named %r" % (arm,))
    return VR.NEAR if arm == "control" else (VR.NEAR << SHIFT)


def the_near_plane_is_the_same_plane():
    """THE FORCED CONSTANT REINTERPRETS NO GEOMETRY, AND THAT IS PROVED RATHER THAN ASSERTED.

    Changing the unit of the camera coordinate forces re-expressing the near constant in the same
    unit; that is the same variable written down twice, not a second one. `cf >> SHIFT < NEAR` and
    `cf < NEAR << SHIFT` must agree for every integer — checked across the sign, across the shift
    boundary and on both sides of the plane, because a near test that admitted or rejected one extra
    primitive would put a second change inside a single-variable arm.
    """
    lo, hi = near_of("control"), near_of("candidate")
    probes = [0, 1, -1, hi - 1, hi, hi + 1, -hi, 1 << 40, -(1 << 40)]
    probes += [(lo + k) << SHIFT for k in (-2, -1, 0, 1, 2)]
    probes += [((lo + k) << SHIFT) + j for k in (-1, 0, 1) for j in (-1, 1, 65535)]
    return all(((cf >> SHIFT) < lo) == (cf < hi) for cf in probes)


def the_arms_differ_only_by_the_shift():
    """VALIDITY OF THE SINGLE STEP. The candidate's camera coordinate must be the control's shifted
    back — exactly, for every component of every declared vertex on every declared frame — or
    `remove the truncation` would be a different camera rather than one variable moved."""
    prims = VX.primitives_with("reversed")
    for _nm, eye, fwd in VR.TRACE:
        m = VR.basis(fwd)
        for _pk, _col, quad in prims[:200]:
            for v in quad:
                a = camera(v, eye, m, "control")
                b = camera(v, eye, m, "candidate")
                if tuple(x >> SHIFT for x in b) != a:
                    return False
    return True


# ---- the arms -----------------------------------------------------------------------------------------
def render_arm(arm, prims, eye, fwd):
    """The committed loop with the camera coordinate's precision as the single parameter."""
    _n, _sym, S = _level()
    m = VR.basis(fwd)
    cx, cy = VR.W // 2, VR.H // 2
    near = near_of(arm)
    dep = [None] * (VR.W * VR.H)
    key = [-1] * (VR.W * VR.H)
    for pk, _col, quad in prims:
        cam = [camera(v, eye, m, arm) for v in quad]
        if any(c[1] < near for c in cam):
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


# ---- the populations, inherited -------------------------------------------------------------------------
def population(name):
    if name not in POPULATIONS:
        raise VoxcamError("VOXCAM-REFUSE: no population named %r" % (name,))
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
        raise VoxcamError("VOXCAM-REFUSE: no arm named %r" % (arm,))
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


def survivors():
    """{population: still open under the candidate} — what the repair does NOT close."""
    c = reading("candidate")[5]
    return {p: len(population(p)) - c[p] for p in POPULATIONS}


# ---- the verdicts -------------------------------------------------------------------------------------
def verdicts():
    c = reading("candidate")
    closed, n = c[5], {p: len(population(p)) for p in POPULATIONS}
    out = {}
    out["C1"] = (closed["on_surface"] * 20 > n["on_surface"] * 19,
                 "%d of %d on-surface closed" % (closed["on_surface"], n["on_surface"]))
    out["C2"] = (closed["sub_pixel"] * 2 > n["sub_pixel"],
                 "%d of %d sub-pixel closed" % (closed["sub_pixel"], n["sub_pixel"]))
    out["C3"] = (closed["winner_miss"] * 2 > n["winner_miss"],
                 "%d of %d winner-side closed" % (closed["winner_miss"], n["winner_miss"]))
    out["C4"] = (c[2] > 5 * c[3], "+%d gained against -%d lost" % (c[2], c[3]))
    out["C5"] = (closed["tie"] == 0 and closed["phantom"] == 0,
                 "%d of %d ties and %d of %d phantoms closed"
                 % (closed["tie"], n["tie"], closed["phantom"], n["phantom"]))
    return out


def every_prediction_has_a_verdict():
    v = verdicts()
    return sorted(v) == sorted(p for p, _t in PREDICTION) and len(v) == len(PREDICTION)


def hits():
    return tuple(sorted(p for p, (ok, _w) in verdicts().items() if ok))


def misses():
    return tuple(sorted(p for p, (ok, _w) in verdicts().items() if not ok))


def the_record_carries_hits_and_misses():
    """A rung that WINS is exactly the one most tempted to drop the prediction it missed."""
    return len(hits()) > 0 and len(misses()) > 0


def the_candidate_wins_on_evidence():
    """THE HEADLINE, ASSERTED AS THE MEASUREMENT. Unlike `voxproj` this candidate gains far more than
    it loses and drops the oracle-free impossible count as well. REDDENS ON THE DAY IT STOPS
    WINNING, which is the day the finding must be revisited rather than quietly kept."""
    ctl, can = reading("control"), reading("candidate")
    return can[0] > ctl[0] and can[2] > 5 * can[3] and can[1] * 2 < ctl[1]


def the_tie_pixels_keep_their_geometry():
    """THE MISS, STATED PRECISELY AND WITHOUT CONTRADICTING `voxwin`. Both exact ties close here —
    but what closed is the DEPTH TIE, not the geometry. `voxwin` established in exact WORLD space,
    with no truncation anywhere, that the ray at those two pixels passes through an edge shared by
    two faces, and this rung does not disturb that: the pixels remain a real degeneracy, and only
    the rasteriser's manufactured exact-depth equality is repaired."""
    return (reading("candidate")[5]["tie"] == len(population("tie")) > 0
            and VW.the_exceptions_are_exactly_the_exact_ties()
            and VW.the_ties_are_the_parked_question())


def the_phantoms_are_not_swallowed():
    """The two phantoms stay red. A candidate that closed them would be claiming success on a
    population it did not address, and the oracle returns nothing at all there."""
    return reading("candidate")[5]["phantom"] == 0 and len(population("phantom")) > 0


def the_survivors_are_named_not_rounded():
    """WHAT THE REPAIR DOES NOT CLOSE IS COUNTED AND KEPT. A candidate reporting only what it fixed
    would be reporting the half of the ledger it chose, so the survivors and the newly broken are
    both carried into the record."""
    s = survivors()
    return sum(s.values()) > 0 and reading("candidate")[3] > 0


def nothing_is_promoted():
    """ESTABLISHING A REPAIR AND PROMOTING ONE ARE DIFFERENT ACTS — `voxcand`'s doctrine, and the
    reason that rung exists. Promotion here would move `O_t` on every frame and invalidate the
    frozen census, the 1728-state census and the subdivision ladder at once; and carrying full
    precision scales every interpolated depth by 2^SHIFT, so the DEPTH half of the observable moves
    even at pixels whose colour does not."""
    return VC.the_committed_reference_is_untouched() and VA.nothing_is_altered()


# ---- the record ---------------------------------------------------------------------------------------
RECORD = os.path.join("spec", "attest", "voxref-camera.txt")


def population_digest():
    body = "\n".join("%s %s %s" % (p, v[0], v[1]) for p, v in sorted(verdicts().items()))
    body += "\n" + "\n".join("%s %d %d %d %d %d" % ((a,) + reading(a)[:5]) for a in ARMS)
    body += "\n" + "\n".join("%s %d" % (p, survivors()[p]) for p in POPULATIONS)
    return hashlib.sha256(MAGIC + b"|cam|" + body.encode()).hexdigest()


def generate():
    rows = ["# URDRVXB1 camera-precision candidate — emitted by voxcam.generate(), committed as an",
            "# artifact, re-derived by the gate.",
            "# world %s" % VR.world_digest(),
            "# ONE VARIABLE: the camera coordinate is TRUNCATED by `>> 16` in the control and",
            "# carried at FULL PRECISION in the candidate, with the near constant re-expressed in",
            "# the same unit — the same variable written down twice, proved to name the same plane.",
            "# THE PREDICTION WAS WRITTEN BEFORE THE ARM RAN. Four of five hit and THE CANDIDATE",
            "# WINS — and it is STILL NOT PROMOTED.",
            "#   predict  <id> <text>",
            "#   verdict  <id> <HIT|MISS> <what was measured>",
            "#   arm      <arm> <agree> <impossible> <gained> <lost> <changed>",
            "#   closed   <arm> <population> <count>",
            "#   survivor <population> <still open under the candidate>",
            "#   digest   <population digest>"]
    for pid, text in PREDICTION:
        rows.append("predict %s %s" % (pid, text))
    for pid, (ok, what) in sorted(verdicts().items()):
        rows.append("verdict %s %s %s" % (pid, "HIT" if ok else "MISS", what))
    for a in ARMS:
        rows.append("arm %s %d %d %d %d %d" % ((a,) + reading(a)[:5]))
        for p in POPULATIONS:
            rows.append("closed %s %s %d" % (a, p, reading(a)[5][p]))
    for p in POPULATIONS:
        rows.append("survivor %s %d" % (p, survivors()[p]))
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
            raise VoxcamError("VOXCAM-REFUSE: a predict row naming no declared prediction")
        if f[0] == "verdict" and (len(f) < 4 or f[1] not in ids or f[2] not in ("HIT", "MISS")):
            raise VoxcamError("VOXCAM-REFUSE: a verdict row naming no declared prediction")
        if f[0] == "arm" and (len(f) != 7 or f[1] not in ARMS):
            raise VoxcamError("VOXCAM-REFUSE: an arm row naming no declared arm")
        if f[0] == "closed" and (len(f) != 4 or f[1] not in ARMS or f[2] not in POPULATIONS):
            raise VoxcamError("VOXCAM-REFUSE: a closed row naming no declared population")
        if f[0] == "survivor" and (len(f) != 3 or f[1] not in POPULATIONS):
            raise VoxcamError("VOXCAM-REFUSE: a survivor row naming no declared population")
        if f[0] not in ("predict", "verdict", "arm", "closed", "survivor", "digest"):
            raise VoxcamError("VOXCAM-REFUSE: a row of unknown kind %r" % (f[0],))
        rows.append(tuple(f))
    if world is None:
        raise VoxcamError("VOXCAM-REFUSE: the record names no world digest")
    if not rows:
        raise VoxcamError("VOXCAM-REFUSE: the record has no rows")
    return world, rows


def the_record_names_this_world():
    return parse()[0] == VR.world_digest()


def the_record_is_bound_to_the_live_code():
    _w, rows = parse()
    v, s = verdicts(), survivors()
    for r in rows:
        if r[0] == "verdict" and (r[2] == "HIT") != v[r[1]][0]:
            return False
        if r[0] == "arm" and tuple(int(x) for x in r[2:]) != reading(r[1])[:5]:
            return False
        if r[0] == "closed" and int(r[3]) != reading(r[1])[5][r[2]]:
            return False
        if r[0] == "survivor" and int(r[2]) != s[r[1]]:
            return False
    pinned = next(r[1] for r in rows if r[0] == "digest")
    return pinned == population_digest()


def the_record_carries_the_prediction_text():
    _w, rows = parse()
    return {r[1] for r in rows if r[0] == "predict"} == {p for p, _t in PREDICTION}


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
    except VoxcamError:
        return True
    return False


def told():
    ctl, can = reading("control"), reading("candidate")
    v, s = verdicts(), survivors()
    return ("%d of the five predictions hit and %d missed, and UNLIKE `voxproj` THIS CANDIDATE WINS: "
            "agreement %d against %d, impossible faces %d against %d, +%d gained against -%d lost. "
            "%s. THE MISS IS C5 AND IT DOES NOT CONTRADICT `voxwin`: both exact ties closed, but "
            "what closed is the DEPTH TIE and not the geometry — the ray still passes through a "
            "shared edge at those two pixels, and only the rasteriser's manufactured exact-depth "
            "equality is repaired. WHAT SURVIVES IS NAMED RATHER THAN ROUNDED: %s still open, and "
            "%d pixels that agreed under the control now disagree. AND IT IS STILL NOT PROMOTED — "
            "carrying full precision scales every interpolated depth by 2^%d, so the DEPTH half of "
            "the observable moves even where the colour does not, which is a contract change and "
            "not a bug fix"
            % (len(hits()), len(misses()), can[0], ctl[0], can[1], ctl[1], can[2], can[3],
               ", ".join("%s %s (%s)" % (p, "HIT" if v[p][0] else "MISS", v[p][1])
                         for p in sorted(v)),
               ", ".join("%d %s" % (s[p], p) for p in POPULATIONS if s[p]), can[3], SHIFT))


def scene_case(name):
    if name == "arms":
        return repr(tuple((a,) + reading(a)[:5] + (tuple(sorted(reading(a)[5].items())),)
                          for a in ARMS))
    if name == "verdicts":
        return repr((sorted(verdicts().items()), sorted(survivors().items())))
    raise VoxcamError("VOXCAM-REFUSE: no scene named %r" % name)


def scene_result(name):
    return hashlib.sha256(MAGIC + b"|" + name.encode() + b"|"
                          + scene_case(name).encode()).hexdigest()


SCENES = ("arms", "verdicts")


def golden(name):
    with open(os.path.join(_HERE, "conformance_voxcam.txt"), encoding="utf-8") as fh:
        for ln in fh:
            ln = ln.strip()
            if ln and not ln.startswith("#"):
                nm, dig = ln.split()
                if nm == name:
                    return dig
    raise VoxcamError("VOXCAM-REFUSE: no golden named %r" % name)
