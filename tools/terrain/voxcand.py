# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""voxcand (URDRVXD1) — A REPAIR CANDIDATE, AND IT IS NOT THE REFERENCE.

WHAT THIS MODULE IS FOR, SAID FIRST BECAUSE EVERYTHING ELSE DEPENDS ON IT. `voxref` ships a renderer
this tree has PROVED defective: `voxmicro` counted 2040 pixels it awards to faces that are
sandwiched between two solid cells, which no exterior camera can see at any resolution under any
sampling. Two repairs have now been isolated. Neither is applied to `voxref`. They live here, as
declared arms of an experiment, because promoting a repair is a different act from establishing one
and this rung only does the second.

THE FROZEN CONTRACT DOES NOT MOVE IN THIS RUNG. `voxcoarse`'s 1728-state census and `voxevent`'s
subdivision ladder are both measurements OF the committed observable; landing a repair invalidates
them, and landing a PARTIAL repair would invalidate them twice. `the_committed_reference_is_
untouched` asserts that this module changed nothing about `voxref`, every gate run.

THE TWO FIXES, AS A 2x2 RATHER THAN A BUNDLE.

    winding   `as-committed` is the six face corner lists as `voxref` declares them; `reversed` is
              each list reversed. `voxray` established the defect: the screen-space Y inversion
              reverses projected orientation, so the `area <= 0` test discards the face pointing AT
              the camera and keeps the one pointing away.

    weights   `biased` is what `voxref` does — it adds the top-left bias to each edge value and then
              feeds those same values into the depth interpolation. `unbiased` adds the bias ONLY to
              the coverage test. THE BIAS IS A COVERAGE RULE: it decides which of two triangles owns
              a shared edge. It is not a barycentric coordinate, and using it as one displaces the
              interpolated depth by up to one edge unit, which at grazing incidence is enormous.

Crossing them is the point, and the cross refuted the prediction that motivated it. The obvious
expectation was that each fix helps alone. It is false: removing the bias while the winding is still
wrong makes the impossible population WORSE, 14032 to 14655, and moves not one agreeing pixel —
8399 either way. Correcting the barycentric coordinates of a renderer drawing the WRONG FACES does
not make it draw the right ones; it gives the wrong faces more accurate depths and more of them win.
The weight fix is CONDITIONAL on the winding fix, which a bundled before/after would have hidden
along with the interaction that found the second defect in the first place: with the bias still
present, interpolating 1/z improved the total while REGRESSING two frames, and that is what sent the
search from the interpolation to the weights.

PERSPECTIVE CORRECTION WAS TESTED AND IS REFUSED, which is a result and not an omission. Once the
weights are unbiased it changes NO WINNER at any pixel of any declared frame — the two arms are
identical, frame by frame — and on depth VALUES measured against the oracle's exact `t` it is a
statistical tie: 71.9% within one camera unit either way, mean absolute error 5.89 against 6.10. It
would cost an exact rational per pixel and buy nothing this tree can measure, so it is not in the
candidate. The measurement is pinned so the hypothesis cannot quietly return.

FACT THREE IS RED AND IS DESIGNED TO STAY VISIBLE. The four facts a repair must establish were
declared before this rung: projection correctness, face orientation correctness, visibility
correctness on the micro-scene suite, and preservation of the existing law chain. The candidate
passes three. It does NOT pass the third: 54 impossible pixels survive across three of the
twenty-three renderable micro-scenes, and 661 across the declared trace. `the_third_fact_is_still_
red` asserts that failure so it cannot be forgotten, and that law reddens on the day the defect is
finally closed — which is exactly when the census may be regenerated and not one rung before.

does_not_show: anything about performance. That the candidate is CORRECT — it is measurably closer
and measurably still wrong, and those are different claims. That the residual mechanism is known:
the leading hypothesis is the integer flooring of projected vertex positions, which would also
account for the mean depth error and the `not_covered` population, and it is a hypothesis with no
controlled experiment behind it yet. And nothing about the observable: this module deliberately
cannot produce an `O_t`, because its digests carry a different MAGIC and a candidate digest that
could be mistaken for a frozen one is the whole failure mode this rung exists to prevent.

falsifier: the committed arm of the 2x2 is required to reproduce `voxref.render` byte for byte, so
a drifted transcription reddens rather than quietly measuring a fourth renderer; the candidate is
required to DIFFER from the committed observable, so a repair that changed nothing reddens; and
every structural law `voxref` established — determinism, the coverage partition against its cover
control, order-permutation irrelevance, both digest witnesses — is re-run against the candidate,
because a repair that fixed visibility and broke the partition would be a worse renderer with a
better number.
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

MAGIC = b"URDRVXD1"

#: The two axes, and the two corners of the square that have names.
WINDINGS = VX.WINDINGS
WEIGHTS = ("biased", "unbiased")
ARMS = tuple((w, b) for w in WINDINGS for b in WEIGHTS)
COMMITTED = ("as-committed", "biased")
CANDIDATE = ("reversed", "unbiased")

ORIGIN = VM.CORRESPONDENCE_ORIGIN


class VoxcandError(Exception):
    """VOXCAND-REFUSE — an arm, a fact or a record this module will not pretend to read."""


# ---- the 2x2 ------------------------------------------------------------------------------------
def render_arm(prims, eye, fwd, weights, collect=None, bias=True):
    """`voxref.render`'s loop with the weight treatment as a parameter. Returns (colour, depth, key).

    `bias=False` drops the top-left bias from the COVERAGE test as well, and exists only so the
    partition control can be re-run against this arm the way `voxref` runs it against its own.
    """
    if weights not in WEIGHTS:
        raise VoxcandError("VOXCAND-REFUSE: no weight treatment named %r" % (weights,))
    m = VR.basis(fwd)
    cx, cy = VR.W // 2, VR.H // 2
    colour = [VR.BACKGROUND] * (VR.W * VR.H)
    depth = [VR.FAR] * (VR.W * VR.H)
    key = [-1] * (VR.W * VR.H)
    for pkey, col, quad in prims:
        cam = [VR._project(v, eye, m) for v in quad]
        if any(c[1] < VR.NEAR for c in cam):
            continue
        scr = [(cx + c[0] * VR.FOCAL // c[1], cy - c[2] * VR.FOCAL // c[1], c[1]) for c in cam]
        for a, b, c in ((scr[0], scr[1], scr[2]), (scr[0], scr[2], scr[3])):
            area = (b[0] - a[0]) * (c[1] - a[1]) - (b[1] - a[1]) * (c[0] - a[0])
            if area <= 0:
                continue
            x_lo = max(min(a[0], b[0], c[0]), 0)
            x_hi = min(max(a[0], b[0], c[0]), VR.W - 1)
            y_lo = max(min(a[1], b[1], c[1]), 0)
            y_hi = min(max(a[1], b[1], c[1]), VR.H - 1)
            if x_lo > x_hi or y_lo > y_hi:
                continue
            if bias:
                b0 = VR._top_left_bias(a[0], a[1], b[0], b[1])
                b1 = VR._top_left_bias(b[0], b[1], c[0], c[1])
                b2 = VR._top_left_bias(c[0], c[1], a[0], a[1])
            else:
                b0 = b1 = b2 = 0
            for py in range(y_lo, y_hi + 1):
                row = py * VR.W
                for px in range(x_lo, x_hi + 1):
                    e0 = VR._edge(a[0], a[1], b[0], b[1], px, py)
                    e1 = VR._edge(b[0], b[1], c[0], c[1], px, py)
                    e2 = VR._edge(c[0], c[1], a[0], a[1], px, py)
                    if e0 + b0 < 0 or e1 + b1 < 0 or e2 + b2 < 0:
                        continue
                    # THE ONE LINE THIS RUNG IS ABOUT. `biased` reproduces the committed reference,
                    # which uses the coverage rule's own values as barycentric coordinates.
                    if weights == "biased":
                        w0, w1, w2 = e0 + b0, e1 + b1, e2 + b2
                    else:
                        w0, w1, w2 = e0, e1, e2
                    d = (a[2] * w1 + b[2] * w2 + c[2] * w0) // area
                    i = row + px
                    if collect is not None:
                        collect[i] = collect.get(i, 0) + 1
                    if (d, pkey) < (depth[i], key[i] if key[i] >= 0 else (1 << 62)):
                        depth[i] = d
                        key[i] = pkey
                        colour[i] = col
    return colour, depth, key


def primitives_for(winding):
    return VX.primitives_with(winding)


def arm_frame(arm, frame, collect=None, bias=True):
    winding, weights = arm
    _n, eye, fwd = VR.TRACE[frame]
    return render_arm(primitives_for(winding), eye, fwd, weights, collect, bias)


def the_committed_arm_reproduces_the_reference():
    """THE TRANSCRIPTION IS BOUND, or every number below is about a fourth renderer nobody runs.

    This module's loop with the committed winding and the biased weights must produce `voxref`'s
    colour AND depth buffers byte for byte, on every declared frame.
    """
    prims = VR.primitives()
    for _n, eye, fwd in VR.TRACE:
        want_c, want_d = VR.render(prims, eye, fwd)
        got_c, got_d, _k = render_arm(primitives_for("as-committed"), eye, fwd, "biased")
        if got_c != want_c or got_d != want_d:
            return False
    return True


# ---- identity A: the candidate is not the reference ----------------------------------------------
def candidate_digest(colour, depth):
    """A digest in a DIFFERENT NAMESPACE from `voxref.observable`, on purpose.

    Even byte-identical buffers hash differently here, so a candidate figure can never be pasted
    into a place expecting a frozen `O_t` and go unnoticed. Substitution is the failure mode this
    rung exists to make impossible, and a shared hash prefix would be an open door to it.
    """
    cb = b"".join(c.to_bytes(4, "big") for c in colour)
    db = b"".join((d & 0xFFFFFFFF).to_bytes(4, "big") for d in depth)
    return (hashlib.sha256(MAGIC + b"|CAND-C|" + cb).hexdigest(),
            hashlib.sha256(MAGIC + b"|CAND-Z|" + db).hexdigest())


def the_candidate_digest_is_not_an_observable():
    """The same buffers, hashed both ways, must not collide — the namespaces are separate."""
    colour, depth = VR.render(VR.primitives(), *VR.TRACE[4][1:])
    return candidate_digest(colour, depth) != VR.observable(colour, depth)


def the_candidate_is_not_the_committed_reference():
    """THE REPAIR MUST ACTUALLY CHANGE THE PICTURE. A candidate whose observable equalled the
    committed one would be a repair that repaired nothing, and this row would be certifying it."""
    differed = 0
    for frame in range(len(VR.TRACE)):
        cc, cd, _k = arm_frame(COMMITTED, frame)
        rc, rd, _k2 = arm_frame(CANDIDATE, frame)
        if (cc, cd) != (rc, rd):
            differed += 1
    return differed == len(VR.TRACE)


def the_committed_reference_is_untouched():
    """THIS RUNG MOVED NOTHING. `voxref` still declares the committed winding and still reproduces
    its own pinned contract, so the 1728-state census and the subdivision ladder both remain
    measurements of the thing they were measured against."""
    if VR.primitives()[0] != primitives_for("as-committed")[0]:
        return False
    return VR.scene_result("contract") == VR.golden("contract")


# ---- identity B: what the candidate buys, measured -----------------------------------------------
def _oracle(frame):
    _n, eye, fwd = VR.TRACE[frame]
    return VM.oracle_frame(eye, fwd, VR.solid, ORIGIN)


def arm_reading(arm, frame, ora=None):
    """(agree, disagree, impossible, drawn) for one arm on one frame, against the oracle."""
    _n, eye, fwd = VR.TRACE[frame]
    _c, _d, key = arm_frame(arm, frame)
    if ora is None:
        ora = _oracle(frame)
    own = tuple(e // VR.Q for e in eye)
    agree = impossible = drawn = 0
    for i, k in enumerate(key):
        r = None if k < 0 else VX._unkey(k)
        if r is not None:
            drawn += 1
            if VM.impossible_winner(r[0], r[1], VR.solid, own):
                impossible += 1
        if r == ora[i]:
            agree += 1
    return {"agree": agree, "disagree": VR.W * VR.H - agree,
            "impossible": impossible, "drawn": drawn}


#: THE PERSPECTIVE-CORRECTION MEASUREMENT, PINNED SO THE HYPOTHESIS CANNOT QUIETLY RETURN. Measured
#: against the oracle's exact `t` over every pixel where the candidate and the oracle agree on the
#: face: (pixels compared, linear within one camera unit, perspective within one camera unit,
#: linear mean absolute error in thousandths, perspective mean absolute error in thousandths).
#: Perspective correction also changed NO winner at any pixel of any declared frame once the
#: weights were unbiased, which is why it is not in the candidate.
PERSPECTIVE_VERDICT = (42148, 30321, 30307, 6102, 5891)


def the_perspective_hypothesis_stays_refused():
    """It is refused on two independent grounds and both are recorded: it moves no winner, and it
    does not measurably improve the stored value. A tie that costs an exact rational per pixel is
    not an improvement, and the numbers are pinned rather than remembered."""
    compared, lin_exact, per_exact, lin_err, per_err = PERSPECTIVE_VERDICT
    return (compared > 0 and abs(lin_exact - per_exact) * 100 < compared
            and abs(lin_err - per_err) * 10 < lin_err)


# ---- identity C: preservation --------------------------------------------------------------------
def candidate_trace(order=None):
    prims = primitives_for(CANDIDATE[0])
    if order is not None:
        prims = [prims[i] for i in order]
    out = []
    for name, eye, fwd in VR.TRACE:
        colour, depth, _k = render_arm(prims, eye, fwd, CANDIDATE[1])
        out.append((name, candidate_digest(colour, depth)))
    return out


def the_candidate_is_deterministic():
    return candidate_trace() == candidate_trace()


def _claims(prims, eye, fwd, bias):
    got = {}
    render_arm(prims, eye, fwd, CANDIDATE[1], collect=got, bias=bias)
    return got


def _report(bias, quads=64):
    prims = primitives_for(CANDIDATE[0])
    step = max(1, len(prims) // quads)
    eye, fwd = VR.TRACE[5][1], VR.TRACE[5][2]
    doubled = single = 0
    for i in range(0, len(prims), step):
        for n in _claims([prims[i]], eye, fwd, bias).values():
            if n > 1:
                doubled += 1
            else:
                single += 1
    return doubled, single


def the_candidate_keeps_the_coverage_partition():
    """PRESERVATION, WITH ITS CONTROL. The bias still governs coverage under the candidate, so no
    pixel of a quad may be claimed twice — and dropping it must still double-claim, or the law
    would be a statement about a sample with no shared edges rather than about the rule."""
    return _report(True) == (0, _report(True)[1]) and _report(True)[1] > 0 and _report(False)[0] > 0


def the_candidate_keeps_order_irrelevance():
    """The scene-identity tiebreak is untouched by the repair, so draw order must still be
    observationally irrelevant — checked with the same declared permutations `voxref` uses."""
    n = len(primitives_for(CANDIDATE[0]))
    base = candidate_trace()
    for order in (list(range(n - 1, -1, -1)),
                  [i for r in range(7) for i in range(r, n, 7)]):
        if candidate_trace(order) != base:
            return False
    return True


def the_candidate_keeps_both_witnesses():
    """`voxref`'s two constructed witnesses establish that neither digest is a function of the
    other. A repair that collapsed them would have broken the observable's structure while
    improving its accuracy, so both are re-run through the candidate's own loop."""
    eye, fwd = (0, -8 * VR.Q, 0), (0, 1, 0)

    def quad(dist, half):
        y = dist - 8 * VR.Q
        return tuple((sx * half, y, sz * half)
                     for sx, sz in ((-1, 1), (1, 1), (1, -1), (-1, -1)))

    near = (10, VR.PALETTE[3], quad(8 * VR.Q, 1 * VR.Q))
    far = (11, VR.PALETTE[3], quad(12 * VR.Q, 3 * VR.Q // 2))
    bc, bd, _k = render_arm([near, far], eye, fwd, CANDIDATE[1])
    fc, fd, _k2 = render_arm([far], eye, fwd, CANDIDATE[1])
    if all(x == VR.BACKGROUND for x in bc):
        raise VoxcandError("VOXCAND-REFUSE: the depth witness rendered nothing; it proves nothing")
    both, only = candidate_digest(bc, bd), candidate_digest(fc, fd)
    if not (both[0] == only[0] and both[1] != only[1]):
        return False
    corners = ((-1, 1), (1, 1), (1, -1), (-1, -1))
    q = tuple((sx * VR.Q, 0, sz * VR.Q) for sx, sz in corners)
    ac, ad, _k3 = render_arm([(20, VR.PALETTE[0], q)], eye, fwd, CANDIDATE[1])
    bc2, bd2, _k4 = render_arm([(20, VR.PALETTE[2], q)], eye, fwd, CANDIDATE[1])
    if all(x == VR.BACKGROUND for x in ac):
        raise VoxcandError("VOXCAND-REFUSE: the colour witness rendered nothing; it proves nothing")
    a, b = candidate_digest(ac, ad), candidate_digest(bc2, bd2)
    return a[1] == b[1] and a[0] != b[0]


# ---- the micro-scene suite, and the fact that stays red ------------------------------------------
def micro_impossible():
    """(impossible pixels, agreeing pixels, total pixels, the scenes that are not clean)."""
    bad, imp, agree, tot = [], 0, 0, 0
    for sc in VM.MICRO:
        if ("refuses",) in sc["expect"]:
            continue
        eye, fwd, occ = sc["eye"], sc["fwd"], VM.micro_occ(sc)
        prims = VM.micro_prims(sc, CANDIDATE[0])
        _c, _d, key = render_arm(prims, eye, fwd, CANDIDATE[1])
        ora = VM.oracle_frame(eye, fwd, occ, ORIGIN)
        own = tuple(e // VR.Q for e in eye)
        here = 0
        for i, k in enumerate(key):
            r = VM.winner_answer(k)
            if r is not None and r[0] != "extra" and VM.impossible_winner(r[0], r[1], occ, own):
                here += 1
            if r == ora[i]:
                agree += 1
            tot += 1
        imp += here
        if here:
            bad.append((sc["name"], here))
    return imp, agree, tot, tuple(bad)


#: DECLARED BEFORE THE RUNG — the four facts a repair must establish before the frozen census may
#: be regenerated, and no sooner. Three pass. The third does not, and it is the gate.
FACTS = ("projection", "orientation", "visibility", "preservation")


def fact_verdicts():
    imp, _a, _t, _bad = micro_impossible()
    return {
        "projection": VX.the_rays_invert_the_projection_to_within_one_pixel()
        and VX.the_round_trip_is_mostly_exact(),
        "orientation": all(n[1] == 0 for n in _orientation_readings()),
        "visibility": imp == 0,
        "preservation": (the_candidate_is_deterministic()
                         and the_candidate_keeps_the_coverage_partition()
                         and the_candidate_keeps_order_irrelevance()
                         and the_candidate_keeps_both_witnesses()),
    }


def _orientation_readings():
    """The six single-voxel axis scenes under the candidate: (name, impossible pixels)."""
    out = []
    for sc in VM.MICRO:
        if not sc["name"].startswith("single_") or ("refuses",) in sc["expect"]:
            continue
        occ = VM.micro_occ(sc)
        _c, _d, key = render_arm(VM.micro_prims(sc, CANDIDATE[0]),
                                 sc["eye"], sc["fwd"], CANDIDATE[1])
        own = tuple(e // VR.Q for e in sc["eye"])
        out.append((sc["name"], sum(1 for k in key if k >= 0
                                    and VM.impossible_winner(*VX._unkey(k), occ, own))))
    return tuple(out)


def the_third_fact_is_still_red():
    """ASSERTED AS A FAILURE, WHICH IS THE POINT OF THE RUNG.

    The candidate does not achieve visibility correctness: impossible pixels survive on the
    micro-scene suite. This law asserts that they DO, so the red cannot be forgotten, mis-read or
    quietly rounded to zero — and it reddens on the day the residual is closed, which is the day
    the frozen census may be regenerated and not one rung before.
    """
    v = fact_verdicts()
    return v["visibility"] is False and all(v[f] for f in FACTS if f != "visibility")


def the_census_may_not_be_regenerated_yet():
    """The consequence, stated as a law rather than as a plan: while any fact is red, the frozen
    records stay exactly as they are, and `the_committed_reference_is_untouched` is what enforces
    it in this rung."""
    return not all(fact_verdicts().values()) and the_committed_reference_is_untouched()


# ---- the record ----------------------------------------------------------------------------------
RECORD = os.path.join("spec", "attest", "voxref-candidate.txt")
COLUMNS = ("agree", "disagree", "impossible", "drawn")


def grid():
    return [(w, b, i) for w in WINDINGS for b in WEIGHTS for i in range(len(VR.TRACE))]


def generate():
    rows = ["# URDRVXD1 repair candidate — one row per (winding, weights, frame), emitted by",
            "# voxcand.generate(), committed as an artifact, re-derived by the gate.",
            "# columns: winding weights frame name " + " ".join(COLUMNS),
            "# world %s" % VR.world_digest(),
            "# A CANDIDATE, NEVER THE REFERENCE. `voxref` is untouched by this rung and its frozen",
            "# contract still reproduces its pinned digest. These are measurements OF a proposed",
            "# repair, crossed as a 2x2 so each fix's contribution is separable: the winding",
            "# reversal voxray established, and the removal of the top-left bias from the",
            "# barycentric weights it was never a coordinate for. Fact three is RED at the bottom",
            "# of this table and the census stays frozen until it is not."]
    ora = {i: _oracle(i) for i in range(len(VR.TRACE))}
    for w, b, i in grid():
        c = arm_reading((w, b), i, ora[i])
        rows.append("%s %s %d %s %s"
                    % (w, b, i, VR.TRACE[i][0], " ".join(str(c[k]) for k in COLUMNS)))
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
        if len(f) != 4 + len(COLUMNS):
            raise VoxcandError("VOXCAND-REFUSE: a row with %d fields" % len(f))
        c = dict(zip(COLUMNS, (int(v) for v in f[4:])))
        if c["agree"] + c["disagree"] != VR.W * VR.H:
            raise VoxcandError("VOXCAND-REFUSE: a row that does not account for every pixel")
        if c["impossible"] > c["drawn"]:
            raise VoxcandError("VOXCAND-REFUSE: a row with more impossible pixels than drawn")
        rows.append((f[0], f[1], int(f[2]), f[3], c))
    if world is None:
        raise VoxcandError("VOXCAND-REFUSE: the record names no world digest")
    if not rows:
        raise VoxcandError("VOXCAND-REFUSE: the record has no rows")
    return world, rows


def totals(rows=None):
    if rows is None:
        _w, rows = parse()
    out = {}
    for w, b, _i, _n, c in rows:
        a = out.setdefault((w, b), dict.fromkeys(COLUMNS, 0))
        for k in COLUMNS:
            a[k] += c[k]
    return out


def the_record_is_exactly_the_derived_grid():
    _w, rows = parse()
    return [(w, b, i) for w, b, i, _n, _c in rows] == grid()


def the_record_names_this_world():
    return parse()[0] == VR.world_digest()


BIND = (CANDIDATE[0], CANDIDATE[1], 4)


def the_record_is_bound_to_the_live_code():
    _w, rows = parse()
    want = next(c for w, b, i, _n, c in rows if (w, b, i) == BIND)
    return arm_reading((BIND[0], BIND[1]), BIND[2]) == want


def the_fixes_are_not_independent():
    """THE 2x2 EARNED ITS SHAPE BY REFUTING THE PREDICTION THAT MOTIVATED IT.

    The obvious expectation was that each fix helps on its own and the pair helps most. It is
    false, and the falsehood is the finding. Removing the bias from the barycentric weights while
    the winding is still wrong makes the impossible population WORSE — 14032 to 14655 — and moves
    not one agreeing pixel, 8399 either way. It helps only once the winding is right, and then it
    helps a great deal: 2040 to 661.

    The mechanism is plain once seen. Correcting the barycentric coordinates of a renderer that is
    drawing the WRONG FACES does not make it draw the right ones; it gives the wrong faces more
    accurate depths, and more of them win. A bundled before/after would have reported "the repair
    helps" and hidden that one of its halves is actively harmful in isolation.
    """
    t = totals()
    base = t[COMMITTED]
    weights_only = t[("as-committed", "unbiased")]
    winding_only = t[("reversed", "biased")]
    return (weights_only["impossible"] > base["impossible"]
            and weights_only["agree"] == base["agree"]
            and winding_only["impossible"] < base["impossible"]
            and t[CANDIDATE]["impossible"] < winding_only["impossible"]
            and t[CANDIDATE]["agree"] > winding_only["agree"])


def a_tampered_row_refuses():
    text = _read()
    for ln in text.split("\n"):
        if ln and not ln.startswith("#"):
            f = ln.split()
            f[4] = str(int(f[4]) + 1)          # agree moves, disagree does not
            text = text.replace(ln, " ".join(f), 1)
            break
    try:
        parse(text)
    except VoxcandError:
        return True
    return False


def told():
    t = totals()
    px = len(VR.TRACE) * VR.W * VR.H
    imp, agree, tot, bad = micro_impossible()
    return ("CANDIDATE, NOT REFERENCE, AND FACT THREE IS RED. Impossible pixels %d committed -> %d "
            "winding only -> %d weights only -> %d candidate; oracle agreement %d -> %d of %d "
            "(%.1f%% -> %.1f%%). On the micro-scene suite the candidate leaves %d impossible pixels "
            "across %s of %d scenes, so the frozen census stays frozen"
            % (t[COMMITTED]["impossible"], t[("reversed", "biased")]["impossible"],
               t[("as-committed", "unbiased")]["impossible"], t[CANDIDATE]["impossible"],
               t[COMMITTED]["agree"], t[CANDIDATE]["agree"], px,
               100.0 * t[COMMITTED]["agree"] / px, 100.0 * t[CANDIDATE]["agree"] / px,
               imp, ", ".join("%s %d" % b for b in bad) or "none",
               sum(1 for s in VM.MICRO if ("refuses",) not in s["expect"])))


def scene_case(name):
    if name == "arms":
        _w, rows = parse()
        return repr((totals(rows), ARMS, COMMITTED, CANDIDATE, PERSPECTIVE_VERDICT))
    if name == "facts":
        return repr((FACTS, fact_verdicts(), _orientation_readings(), micro_impossible()))
    raise VoxcandError("VOXCAND-REFUSE: no scene named %r" % name)


def scene_result(name):
    return hashlib.sha256(MAGIC + b"|" + name.encode() + b"|"
                          + scene_case(name).encode()).hexdigest()


SCENES = ("arms", "facts")


def golden(name):
    with open(os.path.join(_HERE, "conformance_voxcand.txt"), encoding="utf-8") as fh:
        for ln in fh:
            ln = ln.strip()
            if ln and not ln.startswith("#"):
                nm, dig = ln.split()
                if nm == name:
                    return dig
    raise VoxcandError("VOXCAND-REFUSE: no golden named %r" % name)
